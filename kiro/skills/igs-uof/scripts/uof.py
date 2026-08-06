#!/usr/bin/env python3
"""
igs-uof CLI 入口。查詢公司內網 UOF（U-Office Force）的個人差勤與辦公資訊。

用法：
  uof.py [全域flags] <子命令> [子命令flags] [<子命令> ...]
  uof.py                        # 無子命令 = hours 全查（向後相容 v1）
  uof.py hours --annual-leave
  uof.py todo attendance        # 一次多子命令 = 單次登入依序查
  uof.py --target 30            # 未冠子命令的 flags 歸 hours（向後相容 v1）

全域 flags：--headed（驗證碼手動過）、--fresh-login（忽略既有 session 強制重登）、
           --cdp（接管使用者自己開的瀏覽器，過人機驗證用）、--cdp-endpoint URL
           ⚠️ --cdp 模式下 --headed / --fresh-login 皆無作用（用的是使用者那個視窗
              的登入狀態，不碰 session.json）。
輸出單一 JSON 到 stdout。
離開碼：0 全成功；2 連不到內網；3 登入/憑證問題（含被人機驗證擋住 error=antibot、
查詢中途 session 失效——此時已完成子命令的結果仍會印出）；4 有子命令抓取失敗
（其餘子命令照常回）；5 其他（含 CDP 連不上）。
"""
import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import uof_client
from uof_client import ScrapeFailed, SessionExpired, die
# playwright 不在頂層 import：載入要 ~1.4s，而離線快照查詢（whois 走 run_offline）
# 根本不開瀏覽器。改在真的要上線時才載，離線路徑才稱得上秒回。
import cmd_hours
import cmd_attendance
import cmd_leave
import cmd_todo
import cmd_whois

# 子命令註冊表：新功能 = import + 加一行
MODS = {
    "hours": cmd_hours,
    "attendance": cmd_attendance,
    "leave": cmd_leave,
    "todo": cmd_todo,
    "whois": cmd_whois,
}


def _value_flags():
    """收集所有子命令「吃一個值」的 flags（--flag value 形式）。
    切段時其後緊接的 token 要視為值、不做子命令名比對——否則
    `whois --name todo` 的 todo 會被誤判成新子命令（store_true 的 nargs==0，不收）。"""
    flags = set()
    for mod in MODS.values():
        ap = argparse.ArgumentParser(add_help=False)
        mod.add_args(ap)
        for a in ap._actions:
            if a.option_strings and a.nargs != 0:
                flags.update(a.option_strings)
    return flags


def parse_segments(argv):
    """把 argv 切成 (全域flags, [(子命令, Namespace)…])。

    規則：--headed/--fresh-login/--cdp/--cdp-endpoint 任意位置皆收為全域；其餘 token
    依子命令名切段（吃值 flag 的下一個 token 視為值，不參與切段）；
    第一個 token 不是子命令名時整段歸 hours（向後相容 v1 直接下 flags 的用法）。
    """
    g = {"headed": False, "fresh_login": False, "cdp": None}
    toks = []
    i = 0
    while i < len(argv):
        t = argv[i]
        if t == "--headed":
            g["headed"] = True
        elif t == "--fresh-login":
            g["fresh_login"] = True
        elif t == "--cdp":
            g["cdp"] = uof_client.CDP_DEFAULT
        elif t == "--cdp-endpoint":
            # 全域吃值 flag：值必須在這裡吃掉，否則會被當成子命令名參與切段
            if i + 1 >= len(argv):
                die(5, "bad_args", hint="--cdp-endpoint 需要一個值，例如 --cdp-endpoint http://127.0.0.1:9222")
            g["cdp"] = argv[i + 1]
            i += 1
        else:
            toks.append(t)
        i += 1
    if not toks or toks[0] not in MODS:
        toks.insert(0, "hours")
    value_flags = _value_flags()
    segs = []
    expect_value = False
    for t in toks:
        if expect_value:
            segs[-1][1].append(t)
            expect_value = False
            continue
        if t in MODS:
            if any(c == t for c, _ in segs):
                die(5, "bad_args", hint=f"子命令 {t} 重複")
            segs.append((t, []))
        else:
            segs[-1][1].append(t)
            if t in value_flags:
                expect_value = True
    out = []
    for cmd, rest in segs:
        ap = argparse.ArgumentParser(prog=f"uof.py {cmd}", add_help=False)
        MODS[cmd].add_args(ap)
        try:
            ns = ap.parse_args(rest)
        except SystemExit:
            die(5, "bad_args", hint=f"{cmd} 的參數無法解析：{' '.join(rest)}（各子命令 flags 見 SKILL.md）")
        if hasattr(MODS[cmd], "validate"):
            MODS[cmd].validate(ns)  # 參數語意檢查（在開瀏覽器前 fail-fast）
        out.append((cmd, ns))
    return g, out


def run_segments(page, segs, cfg, result, attached=False):
    """依序執行各子命令，回 exit code。錯誤分級：
    - 三條例外分支（ScrapeFailed / Playwright 例外 / 保底 Exception）都**先問一次
      antibot**：中途被人機驗證重新挑戰時記為 `antibot`、停止後續（rc=3）——否則會
      誤報成「版型可能改變」把 agent 導去 recon（覆核 M2）
    - 非 antibot 的上述三類 → 記在該子命令鍵、續跑其他（rc=4）
    - SessionExpired → 記在該子命令鍵、停止後續（session 已死，續跑必然全失敗；rc=3）
    無論哪種，已完成子命令的結果都保留在 result、照常印出。
    attached：是否為 CDP 接管模式，決定 antibot hint 指向哪條出路（覆核 F1）。"""
    from playwright.sync_api import Error as PlaywrightError  # 頂層不 import，見檔頭說明

    rc = 0
    for cmd, ns in segs:
        try:
            out = MODS[cmd].run(page, ns, cfg)
        except ScrapeFailed as e:
            # 先問「是不是中途被人機驗證擋住」——否則會誤報成版型改變（覆核 M2）
            ab = uof_client.antibot_result(page, attached)
            if ab:
                result[cmd] = ab
                rc = 3
                break  # 後續子命令必然撞同一道牆
            result[cmd] = {"error": "scrape_failed", "page": e.page_name, "hint": e.hint}
            rc = 4
            continue
        except SessionExpired:
            result[cmd] = {"error": "session_expired",
                           "hint": "session 於查詢中途失效（可能被其他登入踢掉）；重新執行會自動重登，連續發生可加 --fresh-login"}
            rc = 3
            break
        except PlaywrightError as e:
            ab = uof_client.antibot_result(page, attached)  # goto 落到驗證頁 → selector 逾時，同 M2
            if ab:
                result[cmd] = ab
                rc = 3
                break
            result[cmd] = {"error": "scrape_failed", "page": cmd,
                           "hint": f"頁面操作逾時或異常（Playwright）：{str(e).splitlines()[0]}"}
            rc = 4
            continue
        except Exception as e:  # 保底：任何非預期例外都不可打破「輸出單一 JSON」契約
            ab = uof_client.antibot_result(page, attached)
            if ab:
                result[cmd] = ab
                rc = 3
                break
            result[cmd] = {"error": "unexpected_error", "page": cmd, "detail": str(e)}
            rc = 4
            continue
        if cmd == "hours":
            # hours 沿用 v1 輸出形狀：params 併入、overtime/annual_leave 直掛頂層（保回歸基準）
            result["params"].update(out.pop("params", {}))
            result.update(out)
        else:
            result[cmd] = out
    return rc


def run_offline_first(segs, cfg, result):
    """開瀏覽器**前**先讓有離線後端的子命令試著自己回答（目前只有 whois 查本地快照）。

    回 (仍需上線的 segs, rc)。子命令的 run_offline 回 None = 無法離線服務，照常上線。
    沒有 run_offline 屬性的模組（hours/attendance/leave/todo）一律原路徑，行為不變。
    這道短路是「秒回」的關鍵——open_uof 會啟瀏覽器並登入，只為查一支分機不划算。
    """
    remaining, rc = [], 0
    for cmd, ns in segs:
        off = getattr(MODS[cmd], "run_offline", None)
        if off is None:
            remaining.append((cmd, ns))
            continue
        try:
            out = off(ns, cfg)
        except Exception as e:  # 保底：離線路徑也不可打破「輸出單一 JSON」契約
            result[cmd] = {"error": "unexpected_error", "page": cmd, "detail": str(e)}
            rc = 4
            continue
        if out is None:
            remaining.append((cmd, ns))
            continue
        result[cmd] = out
        if "error" in out:
            rc = 4
    return remaining, rc


def main():
    g, segs = parse_segments(sys.argv[1:])
    cfg = uof_client.load_config()
    result = {"as_of": datetime.date.today().isoformat(), "params": {}}

    segs, rc = run_offline_first(segs, cfg, result)
    if not segs:  # 全部離線解決 → 完全不開瀏覽器
        result["params"]["session"] = "offline"
        print(json.dumps(result, ensure_ascii=False, indent=1))
        sys.exit(rc)

    from playwright.sync_api import sync_playwright  # 頂層不 import，見檔頭說明

    with sync_playwright() as p:
        browser, ctx, page, mode = uof_client.open_uof(
            p, cfg, headed=g["headed"], fresh_login=g["fresh_login"], cdp=g["cdp"])
        result["params"]["session"] = mode
        rc = run_segments(page, segs, cfg, result, attached=(mode == "cdp")) or rc
        uof_client.close_uof(browser, ctx, mode)  # mode=='cdp' 時不關（使用者的瀏覽器）

    print(json.dumps(result, ensure_ascii=False, indent=1))
    sys.exit(rc)


if __name__ == "__main__":
    main()
