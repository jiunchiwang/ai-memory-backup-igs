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


def login(page, acct, pw):
    page.goto(BASE + "Login.aspx", wait_until="domcontentloaded", timeout=20000)
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
            die(3, "captcha", hint="登入被要求驗證碼，請用 --headed 手動輸入一次")
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
    """開首頁驗證 session 是否有效；被導回 Login.aspx 即失效。"""
    page.goto(BASE + "Homepage.aspx", wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(800)
    return "login.aspx" not in page.url.lower()


def open_uof(p, cfg, headed=False, fresh_login=False):
    """啟瀏覽器並取得已登入的 page。回 (browser, context, page, session_mode)。

    session_mode: 'reused'=沿用 session.json（免登入、不觸發重複登入互踢）；
                  'new'=帳密登入並把 storage_state 回存 session.json（chmod 600）。
    """
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
    except SystemExit:
        raise
    except Exception as e:
        msg = str(e)
        if _is_net_error(msg):
            die(2, "unreachable", hint="連不到 http://uof，請確認已連上公司內網 / VPN", detail=msg)
        die(5, "login_error", detail=msg)

    os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)
    try:
        ctx.storage_state(path=SESSION_PATH)
        os.chmod(SESSION_PATH, 0o600)  # Windows 無此語意，失敗不致命
    except Exception:
        pass
    return browser, ctx, page, "new"
