#!/usr/bin/env python3
"""
工作日提供者：算出某區間內 IGS 的實際上班天數（扣週末 / 國定假 / 旅遊假）。

三層來源，依序：
  1. 內建年份資料 BAKED（如 2026，已從行事曆解析驗證）——跨平台、免檔案，最可靠。
  2. Downloads 內當年度 IGS 行事曆 .xls（檔名含民國年）——供未內建的年份（如明年）。
  3. 估算：僅計平日(週一~五)，若區間含七月則扣 5 天旅遊假（IGS 慣例）——最後手段，會標註。

行事曆顏色（實測 IGS 115）：白/無填色=上班、粉紅(255,153,204)=放假、淺黃(255,255,204)=旅遊假。
"""
import os, glob, re, datetime

# ── 內建年份資料：只記「平日卻放假」與「週末卻補班」兩種例外，其餘照週一~五 ──
BAKED = {
    2026: {
        "weekday_off": [
            "2026-01-01", "2026-02-16", "2026-02-17", "2026-02-18", "2026-02-19",
            "2026-02-20", "2026-02-27", "2026-04-03", "2026-04-06", "2026-05-01",
            "2026-06-19", "2026-07-20", "2026-07-21", "2026-07-22", "2026-07-23",
            "2026-07-24", "2026-09-25", "2026-09-28", "2026-10-09", "2026-10-26",
            "2026-12-25",
        ],
        "weekend_work": [],  # 補班的週六/日；2026 無
    },
}

CN_NUM = {"正":1,"一":1,"二":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9,
          "十":10,"十一":11,"十二":12}
WEEK_HEAD = ["日","一","二","三","四","五","六"]


def _daterange(start, end):
    d = start
    while d <= end:
        yield d
        d += datetime.timedelta(days=1)


# ── 來源 1：內建 ──────────────────────────────────────────────
def _count_baked(exc, start, end):
    woff = set(exc["weekday_off"]); wwork = set(exc["weekend_work"])
    n = 0
    for d in _daterange(start, end):
        iso = d.isoformat(); wd = d.weekday()  # 0=Mon..6=Sun
        if (wd < 5 and iso not in woff) or (wd >= 5 and iso in wwork):
            n += 1
    return n


# ── 來源 2：行事曆 .xls ───────────────────────────────────────
def find_calendar_file(year, downloads=None):
    """Downloads 找當年度 IGS 行事曆（檔名須含民國年 = 西元-1911）。找不到回 None。"""
    downloads = downloads or os.path.expanduser("~/Downloads")
    roc = str(year - 1911)
    matched = []
    for p in glob.glob(os.path.join(downloads, "*.xls")) + glob.glob(os.path.join(downloads, "*.xlsx")):
        base = os.path.basename(p)
        if roc in base and ("行事曆" in base or "IGS" in base.upper()):
            matched.append((os.path.getmtime(p), p))
    if not matched:
        return None
    matched.sort(reverse=True)
    return matched[0][1]


def _month_from_text(txt):
    m = re.search(r'(正|十[一二]?|[一二三四五六七八九])月', txt)
    return CN_NUM.get(m.group(1)) if m else None


def load_workday_map(path, year):
    """解析行事曆回 {date: 'work'|'off'|'travel'}；版型異常丟 ValueError。"""
    import xlrd
    b = xlrd.open_workbook(path, formatting_info=True)
    s = b.sheet_by_index(0); cm = b.colour_map

    def color(r, c):
        try:
            return cm.get(b.xf_list[s.cell_xf_index(r, c)].background.pattern_colour_index)
        except Exception:
            return None

    def cls(rgb):
        if rgb is None or rgb == (255, 255, 255): return "work"
        if rgb == (255, 153, 204): return "off"
        if rgb == (255, 255, 204): return "travel"
        return "off"  # 其他色保守當放假

    def cell(r, c):
        try: return s.cell_value(r, c)
        except Exception: return ""

    header_rows = []
    for r in range(s.nrows):
        row = [str(cell(r, c)).strip() for c in range(s.ncols)]
        if any(row[c0:c0 + 7] == WEEK_HEAD for c0 in range(0, max(0, s.ncols - 6))):
            header_rows.append(r)
    if not header_rows:
        raise ValueError("找不到星期表頭列，版型可能改了")

    dmap = {}; offsets = {}
    for hi, h in enumerate(header_rows):
        row = [str(cell(h, c)).strip() for c in range(s.ncols)]
        groups = []; c0 = 0
        while c0 <= s.ncols - 7:
            if row[c0:c0 + 7] == WEEK_HEAD:
                groups.append(c0); c0 += 7
            else:
                c0 += 1
        for gc in groups:
            month = None
            for rr in (h - 2, h - 1):
                if rr >= 0:
                    month = month or _month_from_text("".join(str(cell(rr, c)) for c in range(gc, gc + 7)))
            if not month:
                continue
            r_end = header_rows[hi + 1] if hi + 1 < len(header_rows) else s.nrows
            for r in range(h + 1, r_end):
                for off in range(7):
                    v = cell(r, gc + off)
                    if isinstance(v, float) and v == int(v) and 1 <= v <= 31:
                        try:
                            dt = datetime.date(year, month, int(v))
                        except ValueError:
                            continue
                        dmap[dt] = cls(color(r, gc + off)); offsets[dt] = off
    if len(dmap) < 300:
        raise ValueError(f"解析天數過少({len(dmap)})，版型可能改了")
    bad = sum(1 for dt, off in offsets.items() if dt.isoweekday() % 7 != off)
    if bad:
        raise ValueError(f"星期對位驗證失敗({bad} 天)，版型可能改了")
    return dmap


# ── 來源 3：估算 ─────────────────────────────────────────────
def _count_estimate(start, end):
    weekdays = sum(1 for d in _daterange(start, end) if d.weekday() < 5)
    # 七月旅遊假 5 天（IGS 慣例）：扣掉區間與七月重疊部分的平日，最多 5
    jul_start = datetime.date(start.year, 7, 1); jul_end = datetime.date(start.year, 7, 31)
    lo = max(start, jul_start); hi = min(end, jul_end)
    note = "估算：僅計平日，未扣國定假（可能偏高），建議下載當年度行事曆"
    if lo <= hi:
        jul_weekdays = sum(1 for d in _daterange(lo, hi) if d.weekday() < 5)
        weekdays -= min(5, jul_weekdays)
        note = "估算：平日扣七月旅遊假5天，未扣其他國定假（可能略高），建議下載當年度行事曆"
    return max(weekdays, 0), note


# ── 統一入口 ─────────────────────────────────────────────────
def count_workdays(year, start, end):
    """回傳 (上班天數, source, note)。source: 'baked:<year>' / 'calendar:<檔名>' / 'estimate'。"""
    if year in BAKED:
        return _count_baked(BAKED[year], start, end), f"baked:{year}", None
    path = find_calendar_file(year)
    if path:
        try:
            dmap = load_workday_map(path, year)
            n = sum(1 for d in _daterange(start, end) if dmap.get(d) == "work")
            return n, f"calendar:{os.path.basename(path)}", None
        except Exception as e:
            n, note = _count_estimate(start, end)
            return n, "estimate", f"{note}（行事曆解析失敗：{e}）"
    n, note = _count_estimate(start, end)
    return n, "estimate", note
