#!/usr/bin/env python3
"""
igs-uof 共用 client：設定/帳密解析、UOF 登入、session 持久化、錯誤處理。
被 uof.py 與各 cmd_*.py 引用，本身不直接執行。
"""
import subprocess, sys, os, json

# 強制 stdout/stderr 為 UTF-8：Windows subprocess pipe 預設 cp950(Big5)，
# 輸出含中文(錯誤 hint / workday_note / 行事曆檔名)會亂碼或 UnicodeEncodeError。
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE = "http://uof/UOF/"
KEYCHAIN_SERVICE = "uof-hr"
CDP_DEFAULT = "http://127.0.0.1:9222"
ANTIBOT_MARK = "antibotcheck"  # AntiBotCheck.aspx = Cloudflare Turnstile 人機驗證頁
CONFIG_PATH = os.environ.get("UOF_CONFIG") or os.path.expanduser("~/.config/uof/config.json")
SESSION_PATH = os.environ.get("UOF_SESSION") or os.path.expanduser("~/.config/uof/session.json")

SETUP_HINT = {
    "config": f"請建立設定檔 {CONFIG_PATH}，內容範例見 skill 目錄的 config.example.json："
              '{"account":"你的UOF帳號","password":"你的密碼","monthly_target":20}',
    "mac_keychain": '（macOS 也可改用 Keychain：security add-generic-password -s uof-hr -a <帳號> -U -w）',
}


class ScrapeFailed(Exception):
    """功能級錯誤：單一子命令抓取失敗。uof.py 會把它收進該子命令的結果鍵，不中斷其他子命令。"""

    def __init__(self, page_name, hint):
        super().__init__(hint)
        self.page_name = page_name
        self.hint = hint


class SessionExpired(Exception):
    """查詢中途 session 失效（多半是被其他登入踢掉）。
    uof.py 會把錯誤記在當前子命令鍵、停止後續子命令（session 已死，續跑必然全失敗），
    但仍印出已完成子命令的結果——不像全域 die() 把整包丟棄。"""


def die(code, err, **extra):
    """全域錯誤：印單一 JSON 後以指定碼離開（整體中止）。"""
    print(json.dumps({"error": err, **extra}, ensure_ascii=False))
    sys.exit(code)


def _keychain_get(field):
    """僅 macOS：讀 Keychain service uof-hr。取不到回 None。"""
    if sys.platform != "darwin":
        return None
    try:
        if field == "acct":
            r = subprocess.run(["security", "find-generic-password", "-s", KEYCHAIN_SERVICE],
                               capture_output=True, text=True)
            if r.returncode != 0:
                return None
            for line in r.stdout.splitlines():
                if '"acct"' in line:
                    return line.split('="', 1)[1].rstrip('"') or None
            return None
        r = subprocess.run(["security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-w"],
                           capture_output=True, text=True)
        return r.stdout.strip() or None if r.returncode == 0 else None
    except Exception:
        return None


def load_config():
    """讀設定檔（跨 Mac/Windows）；不存在回 {}。"""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            die(5, "bad_config", hint=f"設定檔 {CONFIG_PATH} 解析失敗：{e}")
    return {}


def resolve_credentials(cfg):
    """帳密優先序：環境變數 > 設定檔 > (macOS)Keychain。取不到給跨平台設定教學。"""
    acct = os.environ.get("UOF_ACCOUNT") or cfg.get("account") or _keychain_get("acct")
    pw = os.environ.get("UOF_PASSWORD") or cfg.get("password") or _keychain_get("pwd")
    if not acct or not pw:
        die(3, "no_credential",
            config_path=CONFIG_PATH,
            hint=SETUP_HINT["config"] + (SETUP_HINT["mac_keychain"] if sys.platform == "darwin" else ""))
    return acct, pw


def fnum(x):
    x = (x or "").strip()
    return float(x) if x else 0.0


def _safe_visible(page, sel):
    """導頁中呼叫 selector 會拋 context destroyed，統一吞掉當作不可見。"""
    try:
        el = page.query_selector(sel)
        return bool(el and el.is_visible())
    except Exception:
        return False


def login(page, acct, pw, attached=False):
    """帳密登入。attached=True 表示操作的是使用者自己的瀏覽器（CDP 模式），
    此時驗證碼的處置是「請他在那個視窗自己輸入」，`--headed` 在該模式無作用。"""
    page.goto(BASE + "Login.aspx", wait_until="domcontentloaded", timeout=60000)
    page.fill("#txtAccount", acct)
    page.fill("#txtPwd", pw)
    page.click("#btnSubmit")
    # 等：登入成功離開 Login / 出現重複登入 / 驗證碼
    for _ in range(40):  # 最多約 20s
        page.wait_for_timeout(500)
        try:
            url = page.url
        except Exception:
            continue  # 導頁進行中
        if "login.aspx" not in url.lower():
            page.wait_for_timeout(500)
            return
        if _safe_visible(page, "#btnRemoveRepeatLogin"):
            try:
                page.click("#btnRemoveRepeatLogin")  # 踢掉另一 session 才能登入
                page.wait_for_timeout(3000)
            except Exception:
                pass
            continue
        if _safe_visible(page, "#captchaImage"):
            die(3, "captcha",
                hint="登入被要求驗證碼，請在接管的那個視窗手動輸入後重跑（--headed 在 CDP 模式無作用）"
                     if attached else "登入被要求驗證碼，請用 --headed 手動輸入一次")
    try:
        final = page.url.lower()
    except Exception:
        final = "login.aspx"
    if "login.aspx" in final:
        die(3, "login_failed", hint="登入未成功（帳密可能有誤，或被要求驗證碼）")


def _is_net_error(msg):
    # "net::ERR_" 前綴涵蓋整類 Chromium 網路層錯誤（ERR_INTERNET_DISCONNECTED、
    # ERR_NETWORK_CHANGED、ERR_PROXY_CONNECTION_FAILED…），不逐個窮舉；
    # 舊清單保留以防訊息格式無 net:: 前綴的邊緣情況
    return ("net::ERR_" in msg or "Timeout" in msg
            or "ERR_NAME_NOT_RESOLVED" in msg or "ERR_CONNECTION" in msg
            or "ERR_ADDRESS_UNREACHABLE" in msg)


def _goto_home_ok(page):
    """開首頁驗證 session 是否有效；被導回 Login.aspx 即失效。

    ⚠️ 被導到 AntiBotCheck.aspx（Cloudflare 人機驗證）時這裡回 True——URL 不含
    login.aspx。所以「回 True」只代表 session 沒過期，不代表真的進到系統；
    呼叫端必須接一個 _die_if_antibot()，否則失敗會延後到查詢頁才炸成
    scrape_failed / Page.goto Timeout（2026-08-06 前的實際行為，曾被誤讀成連不到內網）。
    """
    page.goto(BASE + "Homepage.aspx", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(800)
    return "login.aspx" not in page.url.lower()


def _is_antibot(page):
    """是否停在 Cloudflare 人機驗證頁（登入成功之後才會跳）。"""
    try:
        return ANTIBOT_MARK in (page.url or "").lower()
    except Exception:
        return False


# 兩個 hint 分開：已經在 CDP 模式的人不該再被叫去跑 launch_cdp_browser.py（他已經做了）
ANTIBOT_HINT_LAUNCH = ("UOF 前面有 Cloudflare 人機驗證（AntiBotCheck.aspx），自動化啟動的瀏覽器過不了。"
                       "請跑 launch_cdp_browser.py 開一個瀏覽器，自己登入並點過「驗證您是人類」，"
                       "再加 --cdp 讓本工具接管那個視窗。")
ANTIBOT_HINT_ATTACHED = ("接管的視窗停在 Cloudflare 人機驗證頁。請在那個視窗點過「驗證您是人類」"
                         "（不必重開瀏覽器），確認進到 UOF 首頁後重跑本命令。")


def _die_if_antibot(page, attached=False):
    """被人機驗證擋住就中止，並給出唯一已知可行的走法。

    2026-08-06 實測：Playwright launch() 出來的瀏覽器過不了這關——內建 Chromium
    與 channel=msedge 的真 Edge 兩臂皆敗（headed 等 241s 未過）。分野不在瀏覽器
    廠牌也不在無痕模式，而在瀏覽器是否由自動化啟動。∴ 唯一路徑是接管使用者
    自己開的瀏覽器（--cdp），驗證由真人點擊完成，不做指紋偽裝。
    """
    if not _is_antibot(page):
        return
    die(3, "antibot", url=getattr(page, "url", ""),
        hint=ANTIBOT_HINT_ATTACHED if attached else ANTIBOT_HINT_LAUNCH)


def antibot_result(page, attached=False):
    """查詢**中途**被重新挑戰時用：回功能級錯誤 dict，沒被擋則回 None。

    attached 必須照實傳（CDP 模式才是 True）。否則非 CDP 模式會叫使用者去點一個
    不存在的視窗、並「重跑本命令」——而重跑必然再敗，與 SKILL.md 的「別重試同一條
    命令」自相矛盾（第二輪覆核 F1：修 M2 時把 L1 剛修掉的同型錯誤又埋回來）。

    為什麼需要：`_die_if_antibot` 只護住 session 建立點。clearance 中途失效時
    頁面會落到 AntiBotCheck，各 cmd 模組的 selector 隨即逾時 → 原本會回報
    `scrape_failed`「頁面版型可能改變」，uof_form 甚至回報「表單版型變了」——
    正是這次要修掉的誤診模式在 mid-session 復發（Fable5 覆核 M2，2026-08-06）。
    """
    if not _is_antibot(page):
        return None
    return {"error": "antibot", "url": getattr(page, "url", ""),
            "hint": ANTIBOT_HINT_ATTACHED if attached else ANTIBOT_HINT_LAUNCH}


def _save_session(ctx):
    """把 storage_state 存回 session.json（權限 600；Windows 無此語意，失敗不致命）。

    ⚠️ 只在**自己開的** context 上呼叫。CDP 接管的 context 不可存——storage_state
    匯出的是該 context 全部 origin 的 cookies，會把使用者無關網站的 cookies 落地成
    明文（2026-08-06 實測：乾淨 profile 都會混進 .msn.com/.bing.com；且 chmod 600
    在 Windows 是 no-op，實測 mode 666）。見 attach_uof。
    """
    try:
        os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)
        ctx.storage_state(path=SESSION_PATH)
        os.chmod(SESSION_PATH, 0o600)
    except Exception:
        pass


def _pick_uof_page(browser):
    """從既有瀏覽器的**所有** context 挑出停在 UOF 的分頁。回 (ctx, page) 或 (None, None)。

    不只看 contexts[0]：使用者可能在被接管的瀏覽器開了無痕視窗（獨立 context）。
    """
    for ctx in browser.contexts:
        try:
            pages = ctx.pages
        except Exception:
            continue
        for pg in pages:
            try:
                if "/uof/" in (pg.url or "").lower():
                    return ctx, pg
            except Exception:
                continue
    return None, None


def attach_uof(p, cfg, endpoint=CDP_DEFAULT):
    """接管使用者自己啟動、已手動過人機驗證的瀏覽器（CDP）。回 (browser, ctx, page, 'cdp')。

    ⚠️ 呼叫端一律用 close_uof() 收尾——這個瀏覽器是使用者的，直接 close()
    會把他的視窗關掉、害他重過一次人機驗證。
    """
    try:
        browser = p.chromium.connect_over_cdp(endpoint)
    except Exception as e:
        die(5, "cdp_connect_failed", endpoint=endpoint, detail=str(e)[:300],
            hint=f"連不到 CDP {endpoint}；請先跑 launch_cdp_browser.py 並保持該視窗開著")
    if not browser.contexts:
        die(5, "cdp_connect_failed", endpoint=endpoint,
            hint="CDP 連上了但瀏覽器沒有任何 context（視窗可能已關）")
    ctx, page = _pick_uof_page(browser)
    if page is None:
        die(3, "cdp_no_uof_page", endpoint=endpoint,
            hint=f"接管的瀏覽器裡沒有 UOF 分頁；請在那個視窗開 {BASE}Login.aspx 登入後再試")
    try:
        page.bring_to_front()
    except Exception:
        pass
    _die_if_antibot(page, attached=True)
    if "login.aspx" in (page.url or "").lower():
        acct, pw = resolve_credentials(cfg)
        login(page, acct, pw, attached=True)
        _die_if_antibot(page, attached=True)  # 登入成功後才跳驗證，所以這裡要再檢一次
    # 刻意不存 session：這是使用者的 context，storage_state 會把他全部網站的 cookies
    # 落地成明文（見 _save_session 的警告）。CDP 模式的登入狀態本來就在他自己的
    # 瀏覽器裡，存下來對後續 headless 也沒用（clearance cookie 綁 UA/指紋，未驗證可攜）。
    return browser, ctx, page, "cdp"


def close_uof(browser, ctx, session_mode):
    """統一收尾。session_mode=='cdp' 時什麼都不做（那是使用者的瀏覽器）。"""
    if session_mode == "cdp":
        return
    for obj in (ctx, browser):
        try:
            obj.close()
        except Exception:
            pass


def open_uof(p, cfg, headed=False, fresh_login=False, cdp=None):
    """啟瀏覽器並取得已登入的 page。回 (browser, context, page, session_mode)。

    session_mode: 'reused'=沿用 session.json（免登入、不觸發重複登入互踢）；
                  'new'=帳密登入並把 storage_state 回存 session.json（chmod 600）；
                  'cdp'=接管使用者自己開的瀏覽器（cdp 非 None 時；見 attach_uof）。
    收尾一律走 close_uof(browser, ctx, session_mode)——'cdp' 不可 close。
    """
    if cdp:
        return attach_uof(p, cfg, cdp if isinstance(cdp, str) else CDP_DEFAULT)
    acct, pw = resolve_credentials(cfg)
    try:
        browser = p.chromium.launch(headless=not headed)
    except Exception as e:
        die(5, "browser_launch_failed", detail=str(e))
    ctx_opts = {"locale": "zh-TW", "viewport": {"width": 1500, "height": 1400}}

    if not fresh_login and os.path.exists(SESSION_PATH):
        ctx = None
        try:
            ctx = browser.new_context(storage_state=SESSION_PATH, **ctx_opts)
            page = ctx.new_page()
            if _goto_home_ok(page):
                _die_if_antibot(page)  # session 沒過期，但被人機驗證擋在系統外
                return browser, ctx, page, "reused"
        except SystemExit:
            raise
        except Exception as e:
            msg = str(e)
            if _is_net_error(msg):  # 連線類錯誤重登也會撞一樣的，直接報
                die(2, "unreachable", hint="連不到 http://uof，請確認已連上公司內網 / VPN", detail=msg)
        # session 失效或檔案壞掉 → 落回帳密登入
        try:
            if ctx:
                ctx.close()
        except Exception:
            pass

    try:
        ctx = browser.new_context(**ctx_opts)
        page = ctx.new_page()
        login(page, acct, pw)
        _die_if_antibot(page)  # login() 只確認離開 Login.aspx，AntiBotCheck 也算「離開」
    except SystemExit:
        raise
    except Exception as e:
        msg = str(e)
        if _is_net_error(msg):
            die(2, "unreachable", hint="連不到 http://uof，請確認已連上公司內網 / VPN", detail=msg)
        die(5, "login_error", detail=msg)

    _save_session(ctx)
    return browser, ctx, page, "new"
