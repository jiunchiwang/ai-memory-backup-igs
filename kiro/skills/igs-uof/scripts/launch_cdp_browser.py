#!/usr/bin/env python3
"""開一個「非自動化啟動」的瀏覽器並打開 CDP port，供 uof.py --cdp 接管。

為什麼需要這支：UOF 在登入成功之後會跳 Cloudflare Turnstile 人機驗證頁
（AntiBotCheck.aspx）。2026-08-06 實測，Playwright 用 launch() 開出來的瀏覽器
過不了這關——內建 Chromium 與 channel=msedge 的真 Edge 兩臂皆敗（headed 等 241 秒
未過）。分野不在瀏覽器廠牌、也不在無痕模式，而在瀏覽器是否由自動化啟動。
∴ 這支只負責「用一般方式啟動瀏覽器 + 開 CDP port」，驗證交給真人點擊，
不做任何 stealth 參數或指紋偽裝。

用法：
  python launch_cdp_browser.py                 # 開瀏覽器 + UOF 登入頁
  python launch_cdp_browser.py --port 9333
  python launch_cdp_browser.py --browser chrome

接著在那個視窗自己登入、點過「驗證您是人類」，保持視窗開著，再跑：
  python uof.py --cdp hours
  python uof.py --cdp-endpoint http://127.0.0.1:9333 hours attendance

離開碼：0 成功；5 找不到瀏覽器或 CDP 沒起來。
"""
import argparse, json, os, subprocess, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uof_client import BASE, die  # 順帶拿到 stdout UTF-8 reconfigure

# 偏好 Edge（公司 Windows 一定有）→ Chrome
CANDIDATES = {
    "win32": {
        "edge": [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                 r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"],
        # 第三條是使用者層安裝（Chrome 常見安裝法，不在 Program Files）
        "chrome": [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                   r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                   os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Google\Chrome\Application\chrome.exe")],
    },
    "darwin": {
        "edge": ["/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"],
        "chrome": ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"],
    },
    "linux": {
        "edge": ["/usr/bin/microsoft-edge", "/usr/bin/microsoft-edge-stable"],
        "chrome": ["/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser"],
    },
}


def find_browser(prefer):
    """依偏好找瀏覽器。明確指定 edge/chrome 時**不** fallback 到另一家——
    否則 `--browser chrome` 可能靜默開了 Edge，使用者以為在測 Chrome。"""
    table = CANDIDATES.get(sys.platform) or CANDIDATES["linux"]
    order = ["edge", "chrome"] if prefer in (None, "auto") else [prefer]
    for name in order:
        for path in table.get(name, []):
            if path and os.path.exists(path):
                return name, path
    return None, None


def cdp_probe(port, timeout_s=1.5):
    """單次探 /json/version；有回應回版本 dict，否則 None。"""
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=timeout_s) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        return None


def cdp_ready(port, timeout_s):
    """輪詢 /json/version 直到 CDP 起來；回版本 dict 或 None。"""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        ver = cdp_probe(port)
        if ver:
            return ver
        time.sleep(0.5)
    return None


def main():
    ap = argparse.ArgumentParser(description="開瀏覽器 + CDP port 供 uof.py --cdp 接管")
    ap.add_argument("--port", type=int, default=9222, help="CDP port（預設 9222）")
    ap.add_argument("--browser", choices=["auto", "edge", "chrome"], default="auto")
    ap.add_argument("--profile", default=None,
                    help="user-data-dir（預設 ~/.config/uof/cdp-profile）。"
                         "刻意用獨立 profile：既有瀏覽器已在跑時，--remote-debugging-port 會被忽略")
    ap.add_argument("--url", default=None, help="開啟的網址（預設 UOF 登入頁）")
    args = ap.parse_args()

    # 先探 port：已被占用時，後面的輪詢會打到**別人的**瀏覽器並回報假成功
    # （這台機器有其他帶 CDP 的瀏覽器工具，情境真實）。占用就直接停，別讓使用者
    # 在新視窗過完驗證卻發現 uof.py 接到另一個瀏覽器。
    occupied = cdp_probe(args.port)
    if occupied:
        die(5, "cdp_port_in_use", port=args.port, existing_browser=occupied.get("Browser", ""),
            hint=f"port {args.port} 已經有帶 CDP 的瀏覽器在用。若那正是你要接管的視窗，"
                 f"直接跑 uof.py --cdp-endpoint http://127.0.0.1:{args.port}；"
                 f"否則換 --port（例如 --port 9333）或先關掉那個瀏覽器。")

    name, path = find_browser(args.browser)
    if not path:
        die(5, "browser_not_found", requested=args.browser,
            hint="找不到指定的瀏覽器；請改 --browser 或自行手動啟動："
                 f"<瀏覽器> --remote-debugging-port={args.port} --user-data-dir=<獨立目錄>"
                 "（⚠️ 用獨立目錄，不要用日常 profile）")

    profile = args.profile or os.path.expanduser("~/.config/uof/cdp-profile")
    os.makedirs(profile, exist_ok=True)
    url = args.url or (BASE + "Login.aspx")
    cmd = [path, f"--remote-debugging-port={args.port}", f"--user-data-dir={profile}",
           "--no-first-run", "--no-default-browser-check", url]
    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        die(5, "browser_launch_failed", detail=str(e)[:300])

    ver = cdp_ready(args.port, 20)
    if not ver:
        die(5, "cdp_not_ready", port=args.port,
            hint="瀏覽器起來了但 CDP port 沒開；若該 profile 的瀏覽器已在跑，"
                 "請先關掉它或換 --profile / --port 再試")

    print(json.dumps({
        "browser": name,
        "executable": path,
        "endpoint": f"http://127.0.0.1:{args.port}",
        "profile": profile,
        "url": url,
        "cdp_version": ver.get("Browser"),
        "next": ["在開起來的視窗登入 UOF 並點過「驗證您是人類」",
                 "保持視窗開著",
                 f"再跑：python uof.py --cdp-endpoint http://127.0.0.1:{args.port} hours"],
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
