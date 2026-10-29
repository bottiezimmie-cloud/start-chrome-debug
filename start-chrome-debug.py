#!/usr/bin/env python3
"""start-chrome-debug — launch Chrome with remote debugging, on any OS, in one command.

The thing you google every single time before CDP / Playwright / Puppeteer work:
the exact Chrome binary path + the right flags. This finds Chrome on Windows, macOS,
or Linux, launches it with a remote-debugging port AND a dedicated profile (so you're
not driving your personal one), and confirms the endpoint is actually up.

    python3 start-chrome-debug.py                 # port 9222, dedicated profile
    python3 start-chrome-debug.py --port 9333
    python3 start-chrome-debug.py --url https://example.com
    python3 start-chrome-debug.py --profile ~/my-automation-profile

No dependencies. stdlib only. MIT licensed.

Once it's up, drive it with any CDP client. (I build a tiny raw-CDP driver that doesn't
hang on a busy browser — see "cdpkit" on this profile.)
"""
import argparse, os, platform, shutil, subprocess, sys, time, urllib.request, json

WIN_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",  # Edge is Chromium too
]
MAC_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]
LINUX_NAMES = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge"]


def find_chrome():
    sysname = platform.system()
    if sysname == "Windows":
        for c in WIN_CANDIDATES:
            if c and os.path.exists(c):
                return c
    elif sysname == "Darwin":
        for c in MAC_CANDIDATES:
            if os.path.exists(c):
                return c
    else:  # Linux / other
        for n in LINUX_NAMES:
            path = shutil.which(n)
            if path:
                return path
    return None


def is_up(port, timeout=1.5):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=timeout) as r:
            return json.loads(r.read())
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser(description="Launch Chrome with remote debugging on any OS.")
    ap.add_argument("--port", type=int, default=9222)
    ap.add_argument("--profile", default=os.path.join(os.path.expanduser("~"), ".chrome-debug-profile"),
                    help="dedicated user-data-dir (default: ~/.chrome-debug-profile)")
    ap.add_argument("--url", default="about:blank")
    ap.add_argument("--chrome", default=None, help="path to Chrome/Chromium binary (auto-detected if omitted)")
    args = ap.parse_args()

    existing = is_up(args.port)
    if existing:
        print(f"✅ Chrome debugging already up on :{args.port} — {existing.get('Browser')}")
        print(f"   {existing.get('webSocketDebuggerUrl', '')}")
        return 0

    chrome = args.chrome or find_chrome()
    if not chrome:
        print("❌ Couldn't find Chrome/Chromium/Edge. Pass --chrome /path/to/chrome.", file=sys.stderr)
        return 2

    os.makedirs(args.profile, exist_ok=True)
    cmd = [chrome, f"--remote-debugging-port={args.port}", f"--user-data-dir={args.profile}",
           "--no-first-run", "--no-default-browser-check", args.url]
    print(f"▶ launching: {chrome}\n  port {args.port} · profile {args.profile}")
    kwargs = {}
    if platform.system() != "Windows":
        kwargs["start_new_session"] = True
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kwargs)

    for _ in range(20):
        time.sleep(0.5)
        info = is_up(args.port)
        if info:
            print(f"✅ up on :{args.port} — {info.get('Browser')}")
            print(f"   {info.get('webSocketDebuggerUrl', '')}")
            return 0
    print("⚠️ launched, but the debug endpoint didn't answer in 10s. Check for an existing Chrome "
          "using your profile, or try a fresh --profile.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
