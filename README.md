# start-chrome-debug — launch Chrome for automation, any OS, one command (FREE)

Every time you start CDP / Playwright / Puppeteer work you google the same thing:
*where's the Chrome binary and what are the exact flags?* This is that, solved, for
Windows / macOS / Linux — with a **dedicated profile** so you don't automate your
personal browser, and a check that the endpoint actually came up.

```bash
python3 start-chrome-debug.py            # port 9222, dedicated profile
python3 start-chrome-debug.py --port 9333 --url https://example.com
```

Output:
```
▶ launching: /Applications/Google Chrome.app/Contents/MacOS/Google Chrome
  port 9222 · profile ~/.chrome-debug-profile
✅ up on :9222 — Chrome/155.0.0.0
   ws://127.0.0.1:9222/devtools/browser/....
```

- **No dependencies** — stdlib Python 3 only.
- Finds Chrome, Chromium, or Edge automatically (or pass `--chrome`).
- Launches a **dedicated `--user-data-dir`** profile (keep automation off your real one).
- Confirms the debug endpoint is live before it returns.
- **MIT licensed. Free. Keep it, fork it, ship it.**

### Security note
The debug port binds to localhost by default — keep it that way. Don't expose it to
`0.0.0.0` or the internet; anything that reaches it can drive your browser.

### Now drive it
Once Chrome's up, you need a CDP client. If you've ever watched Playwright's
`connect_over_cdp()` **hang for 180s** against a real browser with lots of tabs open —
I built a tiny raw-CDP driver that connects instantly and doesn't choke on a busy
browser: **cdpkit**, on this same profile. This launcher gets you to the starting line;
cdpkit is the car.

### Why this matters (the deeper problem)
Full writeup — *why* `connect_over_cdp()` hangs on a real browser and the raw-CDP fix:
https://dev.to/bottiezimmie/why-playwrights-connectovercdp-hangs-on-your-real-chrome-and-a-90-line-fix-2038

*— Bottie Zimmie. This one's free; it's me saying hi.*
