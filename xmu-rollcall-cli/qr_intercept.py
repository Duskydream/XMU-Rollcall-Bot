#!/usr/bin/env python3
"""
QR Rollcall Intercept Script
=============================
Monitors for QR rollcalls and intercepts token/API traffic for reverse-engineering.

When a QR rollcall is detected, this script:
  1. Extracts the full QR URL from the page HTML (<qrcode data="...">)
  2. Parses the QR URL for token/rollcall parameters
  3. Connects to Socket.IO to listen for real-time token push events
  4. Polls rollcall status — detects when the user manually signs in
  5. Attempts to replay the captured token via PUT /api/rollcall/{id}/answer
  6. Logs EVERYTHING to qr_intercept_log.json

Usage:
    python qr_intercept.py

    Run this script, then manually scan the QR code with your phone
    (TronClass app or WeChat) to sign in. The script captures the token
    and any WebSocket traffic during the process.
"""

import argparse
import json
import os
import re
import sys
import threading
import time
import uuid
from datetime import datetime
from urllib.parse import urljoin, urlparse, parse_qs, unquote

import requests

# ====== config ======
BASE_URL = "https://lnt.xmu.edu.cn"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}
TIMEOUT = 10
POLL_INTERVAL = 1.5  # seconds between rollcall list polls
LOG_FILE = "qr_intercept_log.json"

# ====== colors ======
class C:
    R = "\033[91m"
    G = "\033[92m"
    Y = "\033[93m"
    B = "\033[94m"
    M = "\033[95m"
    C = "\033[96m"
    W = "\033[90m"
    BD = "\033[1m"
    E = "\033[0m"


def cprint(color, *args, **kwargs):
    print(color + " ".join(str(a) for a in args) + C.E, **kwargs)


def hr(title):
    print(f"\n{'='*60}")
    cprint(C.BD + C.C, f"  {title}")
    print(f"{'='*60}")


def ok(msg):
    cprint(C.G, f"  [OK] {msg}")


def warn(msg):
    cprint(C.Y, f"  [!] {msg}")


def info(msg):
    cprint(C.C, f"  [*] {msg}")


def fail(msg):
    cprint(C.R, f"  [X] {msg}")


# ====== log ======
_log_entries = []


def log_entry(stage, data):
    entry = {"timestamp": datetime.now().isoformat(), "stage": stage, "data": data}
    _log_entries.append(entry)
    return entry


def flush_log():
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump({"intercept_log": _log_entries}, f, indent=2, ensure_ascii=False)
    ok(f"Log saved to {LOG_FILE} ({len(_log_entries)} entries)")


# ====== helpers ======
def safe_json(resp):
    try:
        return resp.json()
    except Exception:
        return None


def try_get(session, url, **kwargs):
    """GET request, return (status, json|text, headers)."""
    hdrs = kwargs.pop("headers", HEADERS)
    try:
        resp = session.get(url, headers=hdrs, timeout=TIMEOUT, **kwargs)
        ct = resp.headers.get("Content-Type", "")
        data = safe_json(resp) if "json" in ct else resp.text
        return resp.status_code, data, dict(resp.headers)
    except Exception as e:
        return None, str(e), {}


# ====== phase 1: extract QR URL from HTML ======
def extract_qr_url(html_text):
    """Extract QR data URL from <qrcode> tag or JS variables."""
    patterns = [
        # <qrcode ... data="URL">
        r'<qrcode\b[^>]*\bdata\s*=\s*"([^"]+)"',
        r"<qrcode\b[^>]*\bdata\s*=\s*'([^']+)'",
        # JS: qrCodeUrl = "URL"
        r'qrCodeUrl\s*[:=]\s*"([^"]+)"',
        r"qrCodeUrl\s*[:=]\s*'([^']+)'",
        # JS: qr_url = "URL"
        r'qr_url\s*[:=]\s*"([^"]+)"',
        r"qr_url\s*[:=]\s*'([^']+)'",
        # JS: qrcodeUrl = "URL"
        r'qrcodeUrl\s*[:=]\s*"([^"]+)"',
        # Any QR data in angular/ng attributes
        r'data\s*=\s*"(https?://[^"]*qrcode[^"]*)"',
        r"data\s*=\s*'(https?://[^']*qrcode[^']*)'",
        # Generic URL in qrcode context
        r'<qrcode\b[^>]*\bdata\s*=\s*"([^"]+)"',
        # Mobile URL pattern
        r'"(https?://lnt\.xmu\.edu\.cn[^"]*(?:mobile|m/)[^"]*(?:rollcall|check|qr)[^"]*)"',
    ]
    for pattern in patterns:
        match = re.search(pattern, html_text, re.IGNORECASE)
        if match:
            url = match.group(1)
            url = url.replace("&amp;", "&")  # unescape HTML entities
            log_entry("qr_url_extracted", {"pattern": pattern, "url": url})
            return url
    return None


def fetch_and_extract_qr(session, rollcall_id):
    """Fetch relevant pages and extract QR URL."""
    hr("PHASE 1 — QR URL Extraction")

    pages_to_try = [
        "/",
        "/student",
        "/student/courses",
        f"/course/rollcall/{rollcall_id}",
        f"/student/rollcall/{rollcall_id}",
        f"/mobile/rollcall/{rollcall_id}",
    ]

    for path in pages_to_try:
        url = urljoin(BASE_URL, path)
        status, html, headers = try_get(session, url)
        if status == 200 and isinstance(html, str):
            info(f"Fetched {path} ({len(html)} bytes)")
            qr_url = extract_qr_url(html)
            if qr_url:
                ok(f"QR URL found in {path}:")
                cprint(C.BD + C.M, f"    {qr_url}")
                return qr_url
            else:
                info(f"  No QR URL in {path}")
        elif status:
            info(f"  {path} -> {status}")

    warn("QR URL not found in any page. Is a QR rollcall active?")
    return None


# ====== phase 2: parse QR URL ======
def parse_qr_url(qr_url):
    """Parse the QR URL for parameters like token, rollcall_id, etc."""
    hr("PHASE 2 — QR URL Analysis")

    parsed = urlparse(qr_url)
    info(f"Scheme:   {parsed.scheme}")
    info(f"Host:     {parsed.hostname}")
    info(f"Port:     {parsed.port}")
    info(f"Path:     {parsed.path}")
    info(f"Query:    {parsed.query}")
    info(f"Fragment: {parsed.fragment}")

    params = parse_qs(parsed.query)
    tokens_found = {}

    token_keywords = ["token", "code", "qr_code", "qr_token", "key", "secret", "t", "c", "rid", "id"]
    for k, v in params.items():
        info(f"  param: {k} = {v}")
        if any(kw in k.lower() for kw in token_keywords):
            tokens_found[k] = v
            cprint(C.BD + C.M, f"  >>> POTENTIAL TOKEN: {k} = {v}")

    # Also check path segments
    path_parts = [p for p in parsed.path.split("/") if p]
    info(f"Path segments: {path_parts}")
    for part in path_parts:
        if part and len(part) > 4:
            info(f"  path segment: {part}")

    result = {"url": qr_url, "params": {k: v[0] if len(v) == 1 else v for k, v in params.items()},
              "path_parts": path_parts, "tokens": tokens_found, "parsed": parsed._asdict()}
    log_entry("qr_url_parsed", result)
    return result


# ====== phase 3: Socket.IO monitoring ======
def start_socketio_monitor(session, captured_events):
    """Try to connect to Socket.IO and listen for rollcall events."""
    hr("PHASE 3 — Socket.IO Monitoring")

    try:
        import socketio
    except ImportError:
        warn("python-socketio not installed. Skipping WebSocket monitoring.")
        warn("Install: pip install python-socketio[client]")
        return None

    sio = socketio.Client(logger=False, engineio_logger=False)

    # Common Tronclass event names to listen for
    watch_events = [
        "rollcall", "rollcall_update", "rollcall_start", "rollcall_stop",
        "qr_update", "qr_token", "qr_code", "qr",
        "token", "new_token", "refresh_token",
        "notification", "message", "event",
        "attendance", "checkin",
    ]

    @sio.on("connect")
    def on_connect():
        msg = "Socket.IO connected"
        ok(msg)
        captured_events.append({"event": "connect", "timestamp": datetime.now().isoformat()})

    @sio.on("disconnect")
    def on_disconnect():
        msg = "Socket.IO disconnected"
        warn(msg)
        captured_events.append({"event": "disconnect", "timestamp": datetime.now().isoformat()})

    @sio.on("*")
    def on_any(event, data):
        msg = f"Event: {event}, data: {str(data)[:300]}"
        info(msg)
        captured_events.append({
            "event": event,
            "data": str(data)[:1000],
            "timestamp": datetime.now().isoformat()
        })

    # Extract cookies for Socket.IO auth
    cookies_dict = requests.utils.dict_from_cookiejar(session.cookies)
    cookie_str = "; ".join(f"{k}={v}" for k, v in cookies_dict.items())

    try:
        sio.connect(
            BASE_URL,
            headers={"Cookie": cookie_str, **HEADERS},
            transports=["websocket", "polling"],
            wait_timeout=8,
        )
        ok("Socket.IO connection established. Listening for events...")
        return sio
    except Exception as e:
        warn(f"Socket.IO connection failed: {e}")
        return None


# ====== phase 4: poll for status change (manual sign-in detection) ======
def monitor_status_change(session, rollcall_id, initial_status, timeout=120):
    """Poll rollcall status until it changes (user manually signed in)."""
    hr("PHASE 4 — Status Change Monitor")
    info(f"Waiting for status change from '{initial_status}'...")
    info("Scan the QR code with your phone NOW to sign in.")
    info(f"Timeout: {timeout}s")

    # Also watch student_rollcalls for personal status
    student_url = urljoin(BASE_URL, f"/api/rollcall/{rollcall_id}/student_rollcalls")
    radar_url = urljoin(BASE_URL, f"/api/radar/rollcalls")

    # Get profile to know our own user ID
    profile_status, profile_data, _ = try_get(session, urljoin(BASE_URL, "/api/profile"))
    my_id = None
    if profile_status == 200 and isinstance(profile_data, dict):
        my_id = profile_data.get("id")
        info(f"My user ID: {my_id}")

    start_time = time.time()
    last_status = initial_status
    snapshots = []

    while time.time() - start_time < timeout:
        # Check radar rollcalls for overall status
        st, data, _ = try_get(session, radar_url)
        if st == 200 and data:
            rollcalls = data.get("rollcalls", [])
            for rc in rollcalls:
                if str(rc.get("rollcall_id")) == str(rollcall_id):
                    current_status = rc.get("status", "unknown")
                    current_rc_status = rc.get("rollcall_status", "unknown")
                    if current_status != last_status or current_rc_status != "absent":
                        info(f"Overall status changed: {last_status} -> {current_status}")
                        info(f"Rollcall status: {current_rc_status}")
                        snapshots.append({"time": time.time() - start_time, "status": current_status,
                                          "rollcall_status": current_rc_status, "data": rc})
                        last_status = current_status

        # Check student_rollcalls for personal status
        st2, sdata, _ = try_get(session, student_url)
        if st2 == 200 and sdata and my_id:
            students = sdata.get("student_rollcalls", [])
            for s in students:
                if s.get("user_id") == my_id or s.get("student_id") == my_id:
                    my_status = s.get("status", "unknown")
                    my_rc_status = s.get("rollcall_status", "unknown")
                    info(f"My status: {my_status}, rollcall_status: {my_rc_status}")
                    if my_status != "absent" or my_rc_status != "absent":
                        ok(f"DETECTED status change! {my_status} / {my_rc_status}")
                        snapshots.append({"time": time.time() - start_time, "my_status": my_status,
                                          "rollcall_status": my_rc_status, "student_data": s})
                        log_entry("status_changed", snapshots)
                        return snapshots

        time.sleep(1.5)

    warn(f"No status change detected within {timeout}s.")
    log_entry("status_timeout", {"timeout": timeout, "snapshots": snapshots})
    return snapshots


# ====== phase 5: attempt answer with captured token ======
def attempt_answer(session, rollcall_id, token_candidates):
    """Try various payload formats with the captured token."""
    hr("PHASE 5 — Answer Attempt")

    answer_url = urljoin(BASE_URL, f"/api/rollcall/{rollcall_id}/answer")
    device_id = str(uuid.uuid4())

    # Build payload variants from token candidates
    payloads = [{"deviceId": device_id}]

    for name, value in token_candidates.items():
        val = value[0] if isinstance(value, list) else value
        payloads.extend([
            {"deviceId": device_id, "qrCode": val},
            {"deviceId": device_id, "qrToken": val},
            {"deviceId": device_id, "token": val},
            {"deviceId": device_id, "code": val},
            {"deviceId": device_id, "qr_code": val},
            {"deviceId": device_id, "qr_token": val},
            {"deviceId": device_id, name: val},
        ])

    results = []
    for i, payload in enumerate(payloads):
        try:
            resp = session.put(answer_url, json=payload, headers=HEADERS, timeout=TIMEOUT)
            status = resp.status_code
            data = safe_json(resp)
            info(f"  [{i+1}/{len(payloads)}] PUT answer — {status}")
            if data:
                info(f"    Response: {json.dumps(data, ensure_ascii=False)[:200]}")
            results.append({"payload": payload, "status": status, "response": data})
            if status == 200:
                ok(f"SUCCESS! Payload: {json.dumps(payload)}")
                break
            time.sleep(0.3)
        except Exception as e:
            results.append({"payload": payload, "error": str(e)})

    log_entry("answer_attempts", results)
    return results


# ====== phase 6: JS bundle deep scan ======
def scan_js_for_qr(session):
    """Download and scan JS bundles for QR answer logic."""
    hr("PHASE 6 — JS Bundle Scan")

    # Fetch main page to get JS bundle URLs
    status, html, _ = try_get(session, urljoin(BASE_URL, "/"))
    if status != 200 or not isinstance(html, str):
        warn("Cannot fetch main page for JS scan.")
        return []

    js_urls = set()
    for m in re.finditer(r'<script[^>]+src=["\']([^"\']+\.js[^"\']*)["\']', html):
        src = m.group(1)
        if src.startswith("/static/") or "static" in src:
            js_urls.add(urljoin(BASE_URL, src) if not src.startswith("http") else src)

    info(f"Found {len(js_urls)} JS bundles. Scanning for QR patterns...")

    qr_api_patterns = [
        r"(?:PUT|POST|put|post)\s*\(\s*[\"'][^\"']*rollcall[^\"']*answer[^\"']*[\"']",
        r"(?:PUT|POST|put|post)\s*\(\s*[\"'][^\"']*qr[^\"']*[\"']",
        r"answerQrRollcall|answerQr|answer_qr_rollcall|answerQR",
        r"qrCode\s*:\s*\w+|qrToken\s*:\s*\w+|qr_code\s*:\s*\w+",
        r"deviceId\s*:\s*\w+.*qr",
        r"rollcallType.*qr|type.*qr_rollcall",
        r"\.put\(\s*[^)]*rollcall[^)]*\)",
        r"\.post\(\s*[^)]*rollcall[^)]*\)",
        r'fetch\(\s*["\'].*rollcall.*answer',
        r'axios\.(?:put|post)\s*\(\s*[^)]*rollcall',
    ]

    findings = []
    for js_url in sorted(js_urls)[:30]:
        try:
            st, text, _ = try_get(session, js_url)
            if st == 200 and isinstance(text, str) and len(text) > 500:
                for pattern in qr_api_patterns:
                    for m in re.finditer(pattern, text, re.IGNORECASE):
                        ctx_start = max(0, m.start() - 100)
                        ctx_end = min(len(text), m.end() + 100)
                        finding = {
                            "file": js_url.split("/")[-1],
                            "url": js_url,
                            "match": m.group(0),
                            "context": text[ctx_start:ctx_end].replace("\n", " "),
                        }
                        findings.append(finding)
                        info(f"  {finding['file']}: {finding['match'][:80]}")
        except Exception:
            pass

    log_entry("js_scan", findings)
    ok(f"Found {len(findings)} QR-related patterns in JS bundles.")
    return findings


# ====== main ======
def main():
    parser = argparse.ArgumentParser(description="QR Rollcall Intercept Script")
    parser.add_argument("--username", "-u", help="XMU username")
    parser.add_argument("--password", "-p", help="XMU password")
    parser.add_argument("--timeout", "-t", type=int, default=120,
                        help="Seconds to wait for manual sign-in (default: 120)")
    parser.add_argument("--no-ws", action="store_true", help="Skip WebSocket monitoring")
    parser.add_argument("--no-js", action="store_true", help="Skip JS bundle scanning")
    args = parser.parse_args()

    print()
    cprint(C.BD + C.C, "  ╔══════════════════════════════════════════════╗")
    cprint(C.BD + C.C, "  ║     QR Rollcall Intercept Script v1.0        ║")
    cprint(C.BD + C.C, "  ║   Reverse-engineering QR check-in for XMU    ║")
    cprint(C.BD + C.C, "  ╚══════════════════════════════════════════════╝")
    print()

    # ---- Login ----
    hr("INIT — Login")

    if args.username and args.password:
        from xmulogin import xmulogin
        session = xmulogin(type=3, username=args.username, password=args.password)
    else:
        try:
            from xmu_rollcall.config import load_config, get_current_account, get_cookies_path
            from xmu_rollcall.utils import load_session, verify_session

            config = load_config()
            account = get_current_account(config)
            if not account:
                fail("No account configured. Use --username/--password or run 'xmu config' first.")
                sys.exit(1)

            cookies_path = get_cookies_path(account.get("id"))
            session = requests.Session()
            if os.path.exists(cookies_path) and load_session(session, cookies_path):
                if verify_session(session):
                    ok(f"Session restored for {account.get('name', 'unknown')}")
                else:
                    from xmulogin import xmulogin
                    session = xmulogin(type=3, username=account["username"], password=account["password"])
            else:
                from xmulogin import xmulogin
                session = xmulogin(type=3, username=account["username"], password=account["password"])
        except ImportError:
            fail("Cannot import config. Provide --username and --password.")
            sys.exit(1)

    if not session:
        fail("Login failed.")
        sys.exit(1)
    ok("Login successful.")

    # ---- Detect QR rollcall ----
    hr("DETECT — Finding QR Rollcall")

    radar_url = urljoin(BASE_URL, "/api/radar/rollcalls")

    target_rollcall = None
    target_id = None

    # Poll until a QR rollcall appears
    info("Polling for QR rollcalls... (Ctrl+C to skip wait)")
    try:
        for attempt in range(60):
            st, data, _ = try_get(session, radar_url)
            if st == 200 and data:
                rollcalls = data.get("rollcalls", [])
                for rc in rollcalls:
                    is_qr = not rc.get("is_radar") and not rc.get("is_number")
                    if is_qr:
                        target_rollcall = rc
                        target_id = rc["rollcall_id"]
                        break
                if target_rollcall:
                    break
            time.sleep(1)
    except KeyboardInterrupt:
        pass

    if not target_rollcall:
        fail("No QR rollcall detected. Start a QR check-in on Tronclass and re-run.")
        flush_log()
        sys.exit(1)

    ok(f"QR rollcall found: {target_rollcall.get('course_title')} (ID: {target_id})")
    info(f"  Type: {target_rollcall.get('type')}")
    info(f"  Status: {target_rollcall.get('status')}")
    info(f"  Rollcall status: {target_rollcall.get('rollcall_status')}")
    log_entry("rollcall_detected", target_rollcall)

    # ---- Phase 1: Extract QR URL ----
    qr_url = fetch_and_extract_qr(session, target_id)

    # ---- Phase 2: Parse QR URL ----
    parsed_qr = None
    token_candidates = {}
    if qr_url:
        parsed_qr = parse_qr_url(qr_url)
        token_candidates = parsed_qr.get("tokens", {})

    # ---- Phase 3: Socket.IO ----
    sio = None
    ws_events = []
    if not args.no_ws:
        sio = start_socketio_monitor(session, ws_events)
    else:
        info("WebSocket monitoring skipped (--no-ws).")

    # ---- Phase 4: Wait for manual sign-in ----
    initial_status = target_rollcall.get("status", "absent")
    status_changes = monitor_status_change(session, target_id, initial_status, args.timeout)

    # ---- Phase 5: Attempt answer ----
    if token_candidates:
        attempt_answer(session, target_id, token_candidates)
    else:
        warn("No token candidates to try.")

    # ---- Phase 6: JS scan ----
    if not args.no_js:
        scan_js_for_qr(session)

    # ---- Cleanup ----
    if sio:
        try:
            sio.disconnect()
        except Exception:
            pass
        info("Socket.IO disconnected.")

    # ---- Summary ----
    hr("SUMMARY")
    ok(f"QR URL captured: {'YES' if qr_url else 'NO'}")
    if qr_url:
        cprint(C.BD + C.M, f"  {qr_url}")
    ok(f"Token candidates: {len(token_candidates)}")
    for k, v in token_candidates.items():
        info(f"  {k} = {v}")
    ok(f"WebSocket events: {len(ws_events)}")
    ok(f"Status changes: {len(status_changes)}")
    ok(f"Log entries: {len(_log_entries)}")

    flush_log()
    print()
    info("Done. Check qr_intercept_log.json for full details.")
    print()


if __name__ == "__main__":
    main()
