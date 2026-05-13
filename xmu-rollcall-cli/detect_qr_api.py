#!/usr/bin/env python3
"""
QR Code Rollcall API Detection Script
======================================
Uses multiple reverse-engineering strategies to discover QR code rollcall
API endpoints, payload formats, and response structures on Tronclass/XMU.

Strategies applied:
  1. Endpoint fuzzing         — brute-force common QR-related API paths
  2. Deep field inspection    — recursively scan all JSON fields in rollcall data
  3. Web page source analysis — fetch rollcall HTML/JS for embedded API refs
  4. Error message mining     — send malformed requests; parse errors for hints
  5. OpenAPI / docs discovery — look for swagger, openapi, graphql endpoints
  6. Mobile API fallback      — try mobile-app-oriented paths (Tronclass app)
  7. Response header analysis — inspect all headers for Link / X-* / Allow
  8. JS Bundle scraping       — extract & scan webpack/vite chunks for API routes
  9. Cookie & token audit     — check cookies & Authorization headers
 10. Number-code-style attack — fetch student_rollcalls, find codes, submit
 11. Cross-type diff analysis — compare QR/number/radar field sets
 12. Community knowledge      — known Tronclass QR patterns
 13. Course list probing      — enumerate courses for rollcall metadata
 14. CORS preflight analysis  — OPTIONS requests reveal allowed methods
 15. QR image URL extraction  — scrape rollcall pages for <img>/<canvas> QR refs
 16. Versioned API probing    — try /api/v1/, /api/v2/, /api/v3/ paths
 17. GraphQL introspection    — attempt GraphQL schema discovery
 18. Teacher-side API probe   — teacher endpoints may leak QR token generation
 19. Websocket endpoint check — QR may use WS for real-time token push
 20. Content negotiation      — vary Accept / Content-Type to trigger different responses

Usage:
    python detect_qr_api.py [--username USER] [--password PASS] [--rollcall-id ID]

If no credentials are given, the script reads from the existing config.
"""

import argparse
import json
import os
import re
import sys
import time
import uuid
from pprint import pprint
from urllib.parse import urljoin

import requests
from xmulogin import xmulogin

# ---------- config ----------
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
FUZZ_MAX_REQUESTS = 120  # hard cap for endpoint fuzzing

# ---------- helpers ----------

class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"
    BOLD = "\033[1m"
    ENDC = "\033[0m"


def cprint(color, *args, **kwargs):
    print(color + " ".join(str(a) for a in args) + Colors.ENDC, **kwargs)


def section(title):
    print(f"\n{'='*70}")
    cprint(Colors.BOLD + Colors.CYAN, f"  {title}")
    print(f"{'='*70}")


def sub(msg):
    cprint(Colors.GRAY, f"  [{msg}]")


def ok(msg):
    cprint(Colors.GREEN, f"  [✓] {msg}")


def warn(msg):
    cprint(Colors.YELLOW, f"  [!] {msg}")


def fail(msg):
    cprint(Colors.RED, f"  [✗] {msg}")


def info(msg):
    cprint(Colors.BLUE, f"  [i] {msg}")


def found(msg):
    cprint(Colors.MAGENTA + Colors.BOLD, f"  [>>> FOUND <<<] {msg}")


def skipped(msg):
    cprint(Colors.GRAY, f"  [–] SKIPPED: {msg}")


def safe_json(resp):
    """Try to parse response as JSON, return None on failure."""
    try:
        return resp.json()
    except Exception:
        return None


def deep_scan(obj, keywords, path="", results=None):
    """Recursively scan a JSON-like object for keys/values matching keywords."""
    if results is None:
        results = []

    if isinstance(obj, dict):
        for k, v in obj.items():
            current_path = f"{path}.{k}" if path else k
            for kw in keywords:
                if kw.lower() in k.lower():
                    results.append((current_path, k, v, "key_match"))
            if isinstance(v, str):
                for kw in keywords:
                    if kw.lower() in v.lower():
                        results.append((current_path, k, v, "value_match"))
            deep_scan(v, keywords, current_path, results)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            deep_scan(item, keywords, f"{path}[{i}]", results)

    return results


def try_request(session, method, url, **kwargs):
    """Make a request and return (status, json_data, headers, elapsed)."""
    hdrs = kwargs.pop("headers", HEADERS)
    try:
        resp = session.request(method, url, headers=hdrs, timeout=TIMEOUT, **kwargs)
        elapsed = resp.elapsed.total_seconds()
        data = safe_json(resp)
        return resp.status_code, data, dict(resp.headers), elapsed
    except requests.Timeout:
        return None, None, None, TIMEOUT
    except Exception as e:
        return None, str(e), None, 0


def requires_rollcall_id(func):
    """Decorator: skip strategy if rollcall_id is None."""
    def wrapper(session, rollcall_id, *args, **kwargs):
        if rollcall_id is None:
            skipped(f"{func.__name__} — no rollcall ID available")
            return []
        return func(session, rollcall_id, *args, **kwargs)
    return wrapper


# ============================================================
# STRATEGY 1: Endpoint fuzzing
# ============================================================
@requires_rollcall_id
def strategy_endpoint_fuzzing(session, rollcall_id):
    """Try many QR-related API endpoint patterns. Hard-capped at FUZZ_MAX_REQUESTS."""
    section("STRATEGY 1 — Endpoint Fuzzing")

    candidates = [
        f"/api/rollcall/{rollcall_id}/answer_qr_rollcall",
        f"/api/rollcall/{rollcall_id}/answer_qrcode_rollcall",
        f"/api/rollcall/{rollcall_id}/answer_qr",
        f"/api/rollcall/{rollcall_id}/qr_answer",
        f"/api/rollcall/{rollcall_id}/answer_qrcode",
        f"/api/rollcall/{rollcall_id}/qr_code",
        f"/api/rollcall/{rollcall_id}/qrcode",
        f"/api/rollcall/{rollcall_id}/qr",
        f"/api/rollcall/{rollcall_id}/code",
        f"/api/rollcall/{rollcall_id}/get_qr",
        f"/api/rollcall/{rollcall_id}/get_qrcode",
        f"/api/rollcall/{rollcall_id}/student_rollcalls",
        f"/api/rollcall/{rollcall_id}/student_rollcall",
        f"/api/rollcall/{rollcall_id}/scan",
        f"/api/rollcall/{rollcall_id}/scan_qr",
        f"/api/rollcall/{rollcall_id}/scan_qrcode",
        f"/api/rollcall/{rollcall_id}/answer",
        f"/api/rollcall/{rollcall_id}",
        f"/api/rollcall/{rollcall_id}/detail",
        f"/api/rollcall/{rollcall_id}/info",
        f"/api/m/rollcall/{rollcall_id}/answer_qr",
        f"/api/m/rollcall/{rollcall_id}/qrcode",
        f"/api/app/rollcall/{rollcall_id}/qr",
        f"/api/rollcall/{rollcall_id}/token",
        f"/api/rollcall/{rollcall_id}/qr_token",
        f"/api/attendance/{rollcall_id}/qr",
        f"/api/attendance/{rollcall_id}/answer",
    ]

    methods = ["GET", "POST", "PUT"]
    payloads_to_try = [
        None,
        {},
        {"deviceId": str(uuid.uuid4())},
        {"deviceId": str(uuid.uuid4()), "type": "qr"},
        {"deviceId": str(uuid.uuid4()), "rollcallType": "qrcode"},
        {"qrCode": ""},
        {"code": ""},
    ]

    interesting = []
    request_count = 0

    for endpoint in candidates:
        for method in methods:
            url = urljoin(BASE_URL, endpoint)
            for payload in payloads_to_try:
                if request_count >= FUZZ_MAX_REQUESTS:
                    warn(f"Fuzzing cap ({FUZZ_MAX_REQUESTS} requests) reached. Stopping.")
                    return interesting

                request_count += 1
                kwargs = {"json": payload} if payload is not None else {}
                status, data, headers, elapsed = try_request(session, method, url, **kwargs)

                if status is None:
                    continue

                if status not in (404, 405):
                    interesting.append({
                        "method": method, "url": url, "status": status,
                        "payload": payload, "data": data,
                        "headers": headers, "elapsed": elapsed,
                    })
                    cprint(Colors.MAGENTA, f"  {method:4s} {status} {url}  ({elapsed:.2f}s)")
                    if data:
                        data_str = json.dumps(data, ensure_ascii=False)[:300]
                        print(f"         Response: {data_str}")

    if not interesting:
        info("No non-404/405 responses found in fuzzing.")
    else:
        ok(f"Found {len(interesting)} potentially interesting responses.")

    return interesting


# ============================================================
# STRATEGY 2: Deep field inspection
# ============================================================
def strategy_deep_inspection(session, rollcall_id, rollcall_data):
    """Recursively scan all API responses for QR-related fields."""
    section("STRATEGY 2 — Deep Field Inspection")

    qr_keywords = [
        "qr", "qrcode", "qr_code", "QRCode", "QR",
        "scan", "scanned", "scanner",
        "code", "barcode",
        "token", "secret",
        "image", "img", "picture", "photo",
        "url", "link", "href",
        "uuid", "device",
        "answer", "submit", "checkin",
        "type", "method", "mode",
        "status", "state", "result",
    ]

    all_results = []

    sub("2a: Inspecting rollcalls list data")
    hits = deep_scan(rollcall_data, qr_keywords)
    if hits:
        for path, key, value, match_type in hits:
            info(f"  {match_type}: {path} = {repr(value)[:100]}")
        all_results.extend(hits)
    else:
        info("  No QR-related fields found in rollcalls list.")

    if rollcall_id:
        sub("2b: Fetching rollcall detail")
        detail_urls = [
            f"/api/rollcall/{rollcall_id}",
            f"/api/rollcall/{rollcall_id}/detail",
            f"/api/rollcall/{rollcall_id}/student_rollcalls",
        ]
        for du in detail_urls:
            url = urljoin(BASE_URL, du)
            status, data, headers, elapsed = try_request(session, "GET", url)
            if status == 200 and data:
                info(f"  GET {du} -> 200 ({elapsed:.2f}s)")
                hits = deep_scan(data, qr_keywords, f"GET {du}")
                for path, key, value, match_type in hits:
                    info(f"    {match_type}: {path} = {repr(value)[:120]}")
                all_results.extend(hits)
            elif status:
                info(f"  GET {du} -> {status}")
    else:
        skipped("detail endpoints — no rollcall ID")

    sub("2c: Checking profile API")
    url = urljoin(BASE_URL, "/api/profile")
    status, data, headers, elapsed = try_request(session, "GET", url)
    if status == 200 and data:
        hits = deep_scan(data, qr_keywords, "profile")
        for path, key, value, match_type in hits:
            info(f"    {match_type}: {path} = {repr(value)[:120]}")
        all_results.extend(hits)

    if not all_results:
        warn("No QR-related fields found in any deep inspection.")
    else:
        ok(f"Total matches from deep inspection: {len(all_results)}")

    return all_results


# ============================================================
# STRATEGY 3: Web page source analysis
# ============================================================
def strategy_web_source(session, rollcall_id):
    """Fetch Tronclass web pages and search for QR-related JS/API refs."""
    section("STRATEGY 3 — Web Page Source Analysis")

    pages_to_check = [
        "/student/courses",
        "/student",
        "/",
    ]
    if rollcall_id:
        pages_to_check = [
            f"/course/rollcall/{rollcall_id}",
            f"/student/rollcall/{rollcall_id}",
            f"/rollcall/{rollcall_id}",
            f"/mobile/rollcall/{rollcall_id}",
        ] + pages_to_check

    # Also try known JS bundle paths
    js_bundle_paths = [
        "/static/js/app.js",
        "/static/js/main.js",
        "/static/js/chunk-vendors.js",
        "/js/app.js",
        "/assets/index.js",
        "/dist/js/app.js",
        "/frontend/js/app.js",
    ]

    qr_patterns = [
        r'answer_qr', r'qrcode', r'qr_code', r'QRCode',
        r'/api/rollcall/.*?/answer', r'/api/rollcall/.*?/qr',
        r'scanQR', r'scanCode', r'handleScan',
        r'rollcallType.*qr', r'type.*qr',
        r'answerRollcall', r'submitRollcall',
        r'"qr"', r"'qr'", r'"qrcode"', r"'qrcode'",
        # New: QR image patterns
        r'qrImg', r'qr_image', r'qrImage', r'qrcodeImg',
        r'canvas.*qr', r'qr.*canvas',
        r'new QRCode\(', r'QRCode\.toCanvas',
        r'qrcodejs', r'qrcode\.min',
        # New: API route definitions
        r'baseURL.*rollcall', r'api.*rollcall',
        r'axios\.(get|post|put).*rollcall',
        r'fetch\(.*rollcall',
    ]

    found_refs = []

    for path in pages_to_check + js_bundle_paths:
        url = urljoin(BASE_URL, path)
        try:
            resp = session.get(url, headers={**HEADERS, "Accept": "text/html,*/*"}, timeout=TIMEOUT)
            if resp.status_code == 200:
                content_type = resp.headers.get("Content-Type", "")
                text = resp.text
                info(f"  GET {path} -> 200 ({len(text)} bytes, {content_type})")

                if "text/html" in content_type or "javascript" in content_type or "text/plain" in content_type:
                    for pattern in qr_patterns:
                        matches = re.findall(pattern, text, re.IGNORECASE)
                        for m in matches[:3]:
                            idx = text.find(str(m)) if isinstance(m, str) else 0
                            ctx_start = max(0, idx - 60)
                            ctx_end = min(len(text), idx + len(str(m)) + 60)
                            context = text[ctx_start:ctx_end].replace("\n", " ")
                            found_refs.append({
                                "page": path, "pattern": pattern,
                                "match": str(m)[:120], "context": context,
                            })
                            info(f"    Match: {str(m)[:80]}")
                            info(f"    Context: ...{context}...")
            elif resp.status_code != 404:
                info(f"  GET {path} -> {resp.status_code}")
        except Exception as e:
            pass

    if not found_refs:
        warn("No QR-related references found in web pages.")
    else:
        ok(f"Found {len(found_refs)} references in web sources.")

    return found_refs


# ============================================================
# STRATEGY 4: Error message mining
# ============================================================
@requires_rollcall_id
def strategy_error_mining(session, rollcall_id):
    """Send malformed requests; learn from error messages."""
    section("STRATEGY 4 — Error Message Mining")

    base_answer_url = urljoin(BASE_URL, f"/api/rollcall/{rollcall_id}/answer")

    payloads = [
        {"deviceId": str(uuid.uuid4()), "type": "qr"},
        {"deviceId": str(uuid.uuid4()), "type": "qrcode"},
        {"deviceId": str(uuid.uuid4()), "rollcallType": "qr"},
        {"deviceId": str(uuid.uuid4()), "rollcallType": "qrcode"},
        {"deviceId": str(uuid.uuid4()), "method": "qr"},
        {"deviceId": str(uuid.uuid4()), "mode": "scan"},
        {"deviceId": str(uuid.uuid4()), "qrCode": ""},
        {"deviceId": str(uuid.uuid4()), "qrCode": "test"},
        {"deviceId": str(uuid.uuid4()), "code": ""},
        {"deviceId": str(uuid.uuid4()), "scannedData": ""},
        {"deviceId": str(uuid.uuid4()), "answer": ""},
        {
            "accuracy": 35, "altitude": 0, "altitudeAccuracy": None,
            "deviceId": str(uuid.uuid4()), "heading": None,
            "latitude": 24.4, "longitude": 118.1, "speed": None,
            "type": "qr",
        },
        {},
        {"deviceId": str(uuid.uuid4())},
    ]

    results = []

    for payload in payloads:
        for method in ["PUT", "POST"]:
            status, data, headers, elapsed = try_request(
                session, method, base_answer_url, json=payload
            )
            if status:
                info(f"  {method} /api/rollcall/{rollcall_id}/answer")
                info(f"    payload: {json.dumps(payload, ensure_ascii=False)[:100]}")
                info(f"    -> {status} ({elapsed:.2f}s)")
                if data:
                    data_str = json.dumps(data, ensure_ascii=False)[:300]
                    info(f"    response: {data_str}")
                    results.append({"method": method, "payload": payload, "status": status, "data": data})
                if status not in (200, 400, 404, 405, 500):
                    found(f"Unusual status code: {status}")
            time.sleep(0.05)

    # OPTIONS preflight
    status, data, headers, elapsed = try_request(session, "OPTIONS", base_answer_url)
    if status == 200 and headers:
        allow = headers.get("Allow", headers.get("allow", ""))
        if allow:
            info(f"  OPTIONS -> Allow: {allow}")

    if not results:
        warn("No informative error messages received.")
    else:
        ok(f"Collected {len(results)} error/info responses.")

    return results


# ============================================================
# STRATEGY 5: OpenAPI / docs discovery
# ============================================================
def strategy_docs_discovery(session):
    """Look for API documentation endpoints."""
    section("STRATEGY 5 — API Documentation Discovery")

    doc_paths = [
        "/api/docs", "/api/swagger", "/api/openapi.json",
        "/api/swagger.json", "/api/swagger-ui.html",
        "/api/v1/docs", "/api/v2/docs",
        "/docs", "/swagger", "/openapi.json", "/swagger-ui.html",
        "/api/doc", "/api/redoc", "/api/schema",
        "/graphql", "/api/graphql",
        "/api/explorer", "/api/playground",
    ]

    found_docs = []

    for path in doc_paths:
        url = urljoin(BASE_URL, path)
        status, data, headers, elapsed = try_request(session, "GET", url)
        if status == 200:
            content_type = headers.get("Content-Type", "")
            info(f"  GET {path} -> 200 ({content_type})")
            found_docs.append({"path": path, "content_type": content_type, "data": data})
            if data is None:
                try:
                    resp = session.get(url, headers=HEADERS, timeout=TIMEOUT)
                    if "swagger" in resp.text.lower():
                        found(f"Swagger UI found at {path}")
                except Exception:
                    pass
        elif status and status != 404:
            info(f"  GET {path} -> {status}")

    if not found_docs:
        warn("No API documentation endpoints found.")
    else:
        ok(f"Found {len(found_docs)} documentation endpoints.")

    return found_docs


# ============================================================
# STRATEGY 6: Mobile API probing
# ============================================================
def strategy_mobile_api(session, rollcall_id):
    """Try mobile-app-specific API patterns."""
    section("STRATEGY 6 — Mobile API Probing")

    mobile_paths = [
        f"/api/m/rollcall/{rollcall_id}",
        f"/api/m/rollcall/{rollcall_id}/answer",
        f"/api/m/rollcall/{rollcall_id}/qr",
        f"/api/m/rollcall/{rollcall_id}/qrcode",
        f"/api/m/rollcall/{rollcall_id}/scan",
        f"/api/m/attendance/{rollcall_id}/qr",
        f"/api/app/rollcall/{rollcall_id}",
        f"/api/app/rollcall/{rollcall_id}/answer",
        f"/api/app/rollcall/{rollcall_id}/qr",
        f"/api/v1/rollcall/{rollcall_id}/answer_qr",
        f"/api/v2/rollcall/{rollcall_id}/answer_qr",
        f"/api/m/rollcall/{rollcall_id}/answer_number_rollcall",
        f"/api/m/rollcall/{rollcall_id}/student_rollcalls",
    ] if rollcall_id else [
        "/api/m/rollcall",
        "/api/app/rollcall",
        "/api/m/courses",
    ]

    results = []

    for path in mobile_paths:
        url = urljoin(BASE_URL, path)
        for method in ["GET", "POST", "PUT"]:
            status, data, headers, elapsed = try_request(session, method, url)
            if status and status not in (404, 405):
                results.append({
                    "method": method, "url": url, "status": status, "data": data
                })
                cprint(Colors.MAGENTA, f"  {method} {path} -> {status}")

    # Try with mobile User-Agent
    mobile_ua_list = [
        "TronClass/3.0 (iPhone; iOS 17.0; Scale/3.00)",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
        "TronClass/3.0 (Android 14; Pixel 8)",
        "okhttp/4.12.0",
    ]
    for ua in mobile_ua_list:
        mh = {**HEADERS, "User-Agent": ua}
        for path in ["/api/rollcall", "/api/m/rollcall", "/api/profile"]:
            url = urljoin(BASE_URL, path)
            try:
                resp = session.get(url, headers=mh, timeout=TIMEOUT)
                if resp.status_code == 200:
                    data = safe_json(resp)
                    keys = list(data.keys()) if isinstance(data, dict) else type(data).__name__
                    info(f"  GET {path} (UA: {ua[:30]}...) -> 200, keys: {keys}")
            except Exception:
                pass

    if not results:
        warn("No mobile-specific endpoints found.")
    else:
        ok(f"Found {len(results)} mobile endpoint responses.")

    return results


# ============================================================
# STRATEGY 7: Response header analysis
# ============================================================
def strategy_header_analysis(session, rollcall_id):
    """Analyze response headers across multiple endpoints for clues."""
    section("STRATEGY 7 — Response Header Analysis")

    endpoints = ["/api/radar/rollcalls", "/api/profile"]
    if rollcall_id:
        endpoints += [
            f"/api/rollcall/{rollcall_id}",
            f"/api/rollcall/{rollcall_id}/answer",
            f"/api/rollcall/{rollcall_id}/student_rollcalls",
        ]

    interesting_headers = []

    for ep in endpoints:
        url = urljoin(BASE_URL, ep)
        try:
            resp = session.get(url, headers=HEADERS, timeout=TIMEOUT)
            hdrs = dict(resp.headers)
            info(f"  GET {ep} -> {resp.status_code}")
            for hk, hv in hdrs.items():
                if any(kw in hk.lower() for kw in [
                    "x-", "api-", "server", "powered", "version",
                    "allow", "access-control", "link", "location",
                    "content-type", "set-cookie",
                ]):
                    interesting_headers.append({"endpoint": ep, "header": hk, "value": hv})
                    info(f"    {hk}: {hv}")
        except Exception as e:
            info(f"  {ep} -> Error: {e}")

    ok(f"Collected {len(interesting_headers)} interesting headers.")
    return interesting_headers


# ============================================================
# STRATEGY 8: JS Bundle scraping (frontend source)
# ============================================================
def strategy_js_bundle_scraping(session):
    """Try to find and analyze JS bundles for API route definitions."""
    section("STRATEGY 8 — JS Bundle Scraping")

    url = urljoin(BASE_URL, "/")
    js_urls = set()

    try:
        resp = session.get(url, headers={**HEADERS, "Accept": "text/html,*/*"}, timeout=TIMEOUT)
        if resp.status_code == 200:
            script_srcs = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', resp.text)
            imports = re.findall(r'import\s*\(?\s*["\']([^"\']+)["\']', resp.text)
            all_js = script_srcs + imports
            for js_path in all_js:
                if js_path.startswith("http"):
                    js_urls.add(js_path)
                elif js_path.startswith("/"):
                    js_urls.add(urljoin(BASE_URL, js_path))
                else:
                    js_urls.add(urljoin(BASE_URL + "/", js_path))
            info(f"  Found {len(js_urls)} JS references on main page.")
    except Exception as e:
        info(f"  Could not fetch main page: {e}")

    qr_js_patterns = [
        r'answer.*qr', r'qr.*rollcall', r'qrcode', r'QRCode',
        r'/api/rollcall/', r'answerQrRollcall', r'answerQR',
        r'scanQR', r'scanQrCode', r'handleQrScan',
        r'rollcallType.*=.*["\']qr["\']',
        r'type.*qr.*rollcall', r'rollcall.*type.*qr',
        # New: QR library usage
        r'new QRCode', r'qrcodejs', r'QRCode\.toCanvas',
        r'qrCodeReader', r'html5-qrcode', r'instascan',
        r'jsqr', r'qr-scanner',
    ]

    found_in_js = []

    for js_url in list(js_urls)[:20]:
        try:
            resp = session.get(js_url, headers={**HEADERS, "Accept": "*/*"}, timeout=TIMEOUT)
            if resp.status_code == 200 and len(resp.text) > 100:
                info(f"  Fetching: {js_url} ({len(resp.text)} bytes)")
                for pattern in qr_js_patterns:
                    matches = re.findall(pattern, resp.text, re.IGNORECASE)
                    for m in matches[:5]:
                        found_in_js.append({"url": js_url, "pattern": pattern, "match": str(m)})
                        info(f"    Match: {str(m)[:80]}")
        except Exception:
            pass

    if not found_in_js:
        warn("No QR-related references found in JS bundles.")
    else:
        ok(f"Found {len(found_in_js)} references in JS bundles.")

    return found_in_js


# ============================================================
# STRATEGY 9: Cookie & token audit
# ============================================================
def strategy_cookie_audit(session):
    """Audit cookies and look for QR-related tokens."""
    section("STRATEGY 9 — Cookie & Token Audit")

    cookies = session.cookies.get_dict()
    info(f"  Session cookies ({len(cookies)}):")

    qr_related = []
    for name, value in cookies.items():
        masked = value[:4] + "****" + value[-4:] if len(value) > 8 else "****"
        info(f"    {name} = {masked}")
        if any(kw in name.lower() for kw in ["qr", "rollcall", "scan", "token", "auth", "session", "jwt"]):
            qr_related.append((name, value))
            found(f"  Interesting cookie: {name}")

    if hasattr(session, 'headers'):
        auth_headers = {k: v for k, v in session.headers.items()
                        if k.lower() in ("authorization", "x-auth-token", "x-csrf-token",
                                         "x-xsrf-token", "cookie")}
        if auth_headers:
            for k, v in auth_headers.items():
                info(f"  Session header: {k} = {v[:20]}...")

    if not qr_related:
        info("  No QR-related cookies found.")

    return qr_related


# ============================================================
# STRATEGY 10: Number-code-style QR attempt
# ============================================================
@requires_rollcall_id
def strategy_number_code_style(session, rollcall_id):
    """Fetch student_rollcalls, look for any code/token field, then try submitting it."""
    section("STRATEGY 10 — Number-Code-Style QR Attempt")

    code_url = urljoin(BASE_URL, f"/api/rollcall/{rollcall_id}/student_rollcalls")
    status, data, headers, elapsed = try_request(session, "GET", code_url)
    if status != 200 or not data:
        warn(f"  GET student_rollcalls -> {status}")
        return []

    info(f"  GET student_rollcalls -> 200 ({elapsed:.2f}s)")
    info("  Full response structure:")
    pprint(data, indent=2, width=120, depth=5)

    code_fields = deep_scan(data, [
        "code", "number", "token", "secret", "key",
        "qr", "scan", "data", "value", "id",
        "string", "text", "content", "payload",
    ])

    findings = []
    for path, key, value, match_type in code_fields:
        if isinstance(value, (str, int)) and len(str(value)) > 2:
            info(f"  Potential code field: {path} = {repr(value)[:80]}")
            findings.append({"path": path, "key": key, "value": value})

    answer_endpoints = [
        f"/api/rollcall/{rollcall_id}/answer",
        f"/api/rollcall/{rollcall_id}/answer_qr_rollcall",
        f"/api/rollcall/{rollcall_id}/answer_number_rollcall",
    ]

    for finding in findings[:5]:
        code_value = finding["value"]
        for ae in answer_endpoints:
            url = urljoin(BASE_URL, ae)
            for payload in [
                {"deviceId": str(uuid.uuid4()), "code": str(code_value)},
                {"deviceId": str(uuid.uuid4()), "numberCode": str(code_value)},
                {"deviceId": str(uuid.uuid4()), "qrCode": str(code_value)},
                {"deviceId": str(uuid.uuid4()), "token": str(code_value)},
            ]:
                status, data, headers, elapsed = try_request(session, "PUT", url, json=payload)
                if status and status not in (400, 404, 405):
                    info(f"    PUT {ae} code={str(code_value)[:20]} -> {status}")
                    if status == 200:
                        found(f"SUCCESS with payload: {payload}")

    return findings


# ============================================================
# STRATEGY 11: Diff-based analysis
# ============================================================
def strategy_diff_analysis(session, rollcall_id):
    """Compare responses from different rollcall types to find QR-specific fields."""
    section("STRATEGY 11 — Cross-Type Diff Analysis")

    url = urljoin(BASE_URL, "/api/radar/rollcalls")
    status, data, headers, elapsed = try_request(session, "GET", url)
    if status != 200 or not data:
        warn("  Cannot fetch rollcalls list.")
        return {}

    rollcalls = data.get("rollcalls", [])
    if not rollcalls:
        warn("  No active rollcalls to compare.")
        return {}

    info(f"  Total rollcalls: {len(rollcalls)}")

    types = {"qr": [], "number": [], "radar": [], "other": []}
    for rc in rollcalls:
        if rc.get("is_radar"):
            types["radar"].append(rc)
        elif rc.get("is_number"):
            types["number"].append(rc)
        else:
            types["qr"].append(rc)

    for t, items in types.items():
        if items:
            info(f"  {t}: {len(items)} rollcall(s)")
            sample = items[0]
            info(f"    Fields: {list(sample.keys())}")
            for k, v in sample.items():
                if k not in ("course_title", "created_by_name", "department_name",
                             "rollcall_id", "is_expired", "is_number", "is_radar",
                             "rollcall_status", "scored", "status"):
                    info(f"    Extra field: {k} = {repr(v)[:100]}")

    if types["qr"] and types["number"]:
        qr_sample = types["qr"][0]
        num_sample = types["number"][0]
        qr_extra = set(qr_sample.keys()) - set(num_sample.keys())
        num_extra = set(num_sample.keys()) - set(qr_sample.keys())
        if qr_extra:
            info(f"  QR-unique fields: {qr_extra}")
        if num_extra:
            info(f"  Number-unique fields: {num_extra}")

    return types


# ============================================================
# STRATEGY 12: Community knowledge
# ============================================================
def strategy_community_knowledge():
    """Known Tronclass QR rollcall patterns from open-source projects."""
    section("STRATEGY 12 — Community Knowledge")

    known_patterns = {
        "Tronclass QR theory 1 — direct submit": {
            "flow": "GET /api/rollcall/{id}/student_rollcalls → extract qr_token → "
                    "PUT /api/rollcall/{id}/answer with {qrToken: <token>}",
            "evidence": "Number rollcall uses identical flow with number_code. "
                        "QR might use qr_code / qr_token analogously."
        },
        "Tronclass QR theory 2 — scan redirect": {
            "flow": "QR encodes URL https://lnt.xmu.edu.cn/student/check?rid={id}&token={t} → "
                    "browser opens → frontend JS parses params → calls answer API",
            "evidence": "Common pattern in classroom systems. Check page source for "
                        "URL parsing logic (URLSearchParams, query string extraction)."
        },
        "Tronclass QR theory 3 — WebSocket push": {
            "flow": "Teacher opens QR → server pushes token via WebSocket → "
                    "student scans and submits token to /api/rollcall/{id}/answer",
            "evidence": "Some Tronclass versions use Socket.IO. Check for "
                        "socket.io.js in page source or /socket.io/ endpoint."
        },
        "Tronclass QR theory 4 — image decode": {
            "flow": "QR code image is an <img> tag on rollcall detail page. "
                    "The image URL may contain the token. Decode QR from image "
                    "or extract token from the img src URL parameters.",
            "evidence": "If page contains /api/rollcall/{id}/qr_image or "
                        "similar endpoint returning a PNG, the QR can be decoded "
                        "with pyzbar/opencv."
        },
        "Tronclass QR theory 5 — mobile app sole": {
            "flow": "QR only works through the Tronclass mobile app. The app uses "
                    "native camera + proprietary API. Web fallback may not exist.",
            "evidence": "If no web endpoints work, QR may be mobile-only. "
                        "Try reverse-engineering the APK or intercepting mobile traffic "
                        "with mitmproxy."
        },
        "Fields to search for": {
            "in rollcall list": "qr_code, qr_token, qr_url, qr_image, code_url, scan_url",
            "in student_rollcalls": "number_code, qr_code, token, student_code",
            "in answer response": "message, error, success, data",
        },
    }

    for name, info_data in known_patterns.items():
        info(f"  {name}:")
        for k, v in info_data.items():
            info(f"    {k}: {v}")

    return known_patterns


# ============================================================
# STRATEGY 13: Course list probing
# ============================================================
def strategy_course_list(session):
    """Enumerate courses API for rollcall metadata and QR field hints."""
    section("STRATEGY 13 — Course List Probing")

    course_endpoints = [
        "/api/courses",
        "/api/student/courses",
        "/api/course",
        "/api/student/course",
        "/api/term/courses",
        "/api/semester/courses",
        "/api/course/list",
        "/api/my_courses",
    ]

    found_data = []

    for ep in course_endpoints:
        url = urljoin(BASE_URL, ep)
        status, data, headers, elapsed = try_request(session, "GET", url)
        if status == 200 and data:
            info(f"  GET {ep} -> 200 ({elapsed:.2f}s)")
            if isinstance(data, dict):
                info(f"    Top-level keys: {list(data.keys())}")
            elif isinstance(data, list):
                info(f"    Array of {len(data)} items")
                if data:
                    info(f"    First item keys: {list(data[0].keys()) if isinstance(data[0], dict) else type(data[0]).__name__}")

            # Deep scan for QR fields
            qr_hits = deep_scan(data, ["qr", "qrcode", "rollcall", "code", "token", "sign"])
            for path, key, value, match_type in qr_hits:
                info(f"    {match_type}: {path} = {repr(value)[:100]}")
            found_data.append({"endpoint": ep, "structure": str(list(data.keys())) if isinstance(data, dict) else f"list({len(data)})"})
        elif status and status != 404:
            info(f"  GET {ep} -> {status}")

    if not found_data:
        warn("No course endpoints returned data.")
    else:
        ok(f"Found {len(found_data)} course endpoints with data.")

    return found_data


# ============================================================
# STRATEGY 14: CORS preflight analysis
# ============================================================
def strategy_cors_analysis(session, rollcall_id):
    """OPTIONS preflight to discover allowed methods and headers."""
    section("STRATEGY 14 — CORS Preflight Analysis")

    targets = ["/api/rollcall", "/api/radar/rollcalls", "/api/profile"]
    if rollcall_id:
        targets += [
            f"/api/rollcall/{rollcall_id}",
            f"/api/rollcall/{rollcall_id}/answer",
            f"/api/rollcall/{rollcall_id}/student_rollcalls",
        ]

    results = []

    for path in targets:
        url = urljoin(BASE_URL, path)
        status, data, headers, elapsed = try_request(
            session, "OPTIONS", url,
            headers={
                **HEADERS,
                "Origin": BASE_URL,
                "Access-Control-Request-Method": "PUT",
                "Access-Control-Request-Headers": "content-type",
            }
        )
        if status == 200 and headers:
            cors_info = {
                "path": path,
                "allow_methods": headers.get("Access-Control-Allow-Methods", headers.get("allow", "")),
                "allow_headers": headers.get("Access-Control-Allow-Headers", ""),
                "allow_origin": headers.get("Access-Control-Allow-Origin", ""),
                "allow_credentials": headers.get("Access-Control-Allow-Credentials", ""),
            }
            results.append(cors_info)
            info(f"  OPTIONS {path} -> {status}")
            for k, v in cors_info.items():
                if v and k != "path":
                    info(f"    {k}: {v}")

    if not results:
        info("No CORS information returned (endpoints may not support OPTIONS).")
    else:
        ok(f"CORS info for {len(results)} endpoints.")

    return results


# ============================================================
# STRATEGY 15: QR image URL extraction
# ============================================================
def strategy_qr_image_extraction(session, rollcall_id):
    """Scrape rollcall pages for QR code image/canvas references."""
    section("STRATEGY 15 — QR Image URL Extraction")

    # Image patterns to search for
    img_patterns = [
        r'<img[^>]+src=["\']([^"\']*(?:qr|qrcode|code)[^"\']*)["\']',
        r'<canvas[^>]+id=["\']([^"\']*(?:qr|qrcode)[^"\']*)["\']',
        r'(?:qr|qrcode)[^"\']*\.(?:png|jpg|jpeg|gif|svg)',
        r'/api/[^"\']*(?:qr|qrcode)[^"\']*',
        r'qrCodeUrl\s*[:=]\s*["\']([^"\']+)["\']',
        r'qr_url\s*[:=]\s*["\']([^"\']+)["\']',
        r'qrcodeUrl\s*[:=]\s*["\']([^"\']+)["\']',
    ]

    pages_to_check = ["/", "/student", "/student/courses"]
    if rollcall_id:
        pages_to_check = [
            f"/course/rollcall/{rollcall_id}",
            f"/student/rollcall/{rollcall_id}",
            f"/mobile/rollcall/{rollcall_id}",
        ] + pages_to_check

    found_images = []

    for path in pages_to_check:
        url = urljoin(BASE_URL, path)
        try:
            resp = session.get(url, headers={**HEADERS, "Accept": "text/html,*/*"}, timeout=TIMEOUT)
            if resp.status_code == 200 and "text/html" in resp.headers.get("Content-Type", ""):
                info(f"  Scanning {path} ({len(resp.text)} bytes)")
                for pattern in img_patterns:
                    matches = re.findall(pattern, resp.text, re.IGNORECASE)
                    for m in matches[:5]:
                        found_images.append({"page": path, "pattern": pattern, "match": str(m)[:200]})
                        info(f"    {pattern[:50]}... → {str(m)[:120]}")
        except Exception:
            pass

    # Also try direct QR image endpoints
    if rollcall_id:
        qr_img_endpoints = [
            f"/api/rollcall/{rollcall_id}/qr_image",
            f"/api/rollcall/{rollcall_id}/qrcode.png",
            f"/api/rollcall/{rollcall_id}/qr.png",
            f"/api/rollcall/{rollcall_id}/qrcode.jpg",
            f"/api/rollcall/{rollcall_id}/qr",
        ]
        for ep in qr_img_endpoints:
            url = urljoin(BASE_URL, ep)
            try:
                resp = session.get(url, headers=HEADERS, timeout=TIMEOUT)
                ct = resp.headers.get("Content-Type", "")
                if resp.status_code == 200:
                    info(f"  GET {ep} -> 200 ({ct}, {len(resp.content)} bytes)")
                    if "image" in ct:
                        found(f"QR image endpoint: {ep} (Content-Type: {ct})")
                        found_images.append({"endpoint": ep, "content_type": ct, "size": len(resp.content)})
            except Exception:
                pass

    if not found_images:
        warn("No QR image references found.")
    else:
        ok(f"Found {len(found_images)} QR image references.")

    return found_images


# ============================================================
# STRATEGY 16: Versioned API probing
# ============================================================
def strategy_versioned_api(session, rollcall_id):
    """Try versioned API paths that may expose different QR implementations."""
    section("STRATEGY 16 — Versioned API Probing")

    versions = ["v1", "v2", "v3", "v4", "latest"]
    resources = ["rollcall", "rollcalls", "courses", "attendance"]
    if rollcall_id:
        resources.append(f"rollcall/{rollcall_id}")
        resources.append(f"rollcall/{rollcall_id}/answer")

    results = []

    for ver in versions:
        for resource in resources:
            path = f"/api/{ver}/{resource}"
            url = urljoin(BASE_URL, path)
            for method in ["GET", "POST"]:
                status, data, headers, elapsed = try_request(session, method, url)
                if status and status not in (404, 405):
                    results.append({
                        "version": ver, "resource": resource,
                        "method": method, "status": status, "data": data
                    })
                    cprint(Colors.MAGENTA, f"  {method} {path} -> {status}")

    if not results:
        info("No versioned API endpoints found.")
    else:
        ok(f"Found {len(results)} versioned API responses.")

    return results


# ============================================================
# STRATEGY 17: GraphQL introspection
# ============================================================
def strategy_graphql_introspection(session):
    """Attempt GraphQL schema introspection to discover QR mutations."""
    section("STRATEGY 17 — GraphQL Introspection")

    graphql_endpoints = [
        "/graphql", "/api/graphql", "/api/gql",
        "/graphql/v1", "/api/graphql/v1",
        "/query", "/api/query",
    ]

    # Standard introspection query
    intro_query = """
    {
      __schema {
        queryType { name fields { name } }
        mutationType { name fields { name } }
        types {
          name
          fields { name }
        }
      }
    }
    """

    found = []

    for ep in graphql_endpoints:
        url = urljoin(BASE_URL, ep)
        for payload in [
            {"query": intro_query},
            {"query": "{ __typename }"},
            {"query": "query { rollcalls { id } }"},
            {"query": "mutation { answerRollcall(id: 1) { success } }"},
        ]:
            status, data, headers, elapsed = try_request(
                session, "POST", url, json=payload,
                headers={**HEADERS, "Content-Type": "application/json"}
            )
            if status == 200 and data:
                info(f"  POST {ep} -> 200 ({elapsed:.2f}s)")
                info(f"    Response: {json.dumps(data, ensure_ascii=False)[:200]}")
                found.append({"endpoint": ep, "payload": str(payload)[:80], "data": data})
            elif status and status not in (404, 405):
                info(f"  POST {ep} -> {status}")

        if not found:
            # Also try GET
            status, data, headers, elapsed = try_request(session, "GET", url)
            if status == 200:
                info(f"  GET {ep} -> 200")
                found.append({"endpoint": ep, "method": "GET", "data": data})

    if not found:
        info("No GraphQL endpoints found.")
    else:
        ok(f"Found {len(found)} GraphQL-related responses.")

    return found


# ============================================================
# STRATEGY 18: Teacher-side API probe
# ============================================================
def strategy_teacher_api(session, rollcall_id):
    """Teacher endpoints may leak QR token generation logic."""
    section("STRATEGY 18 — Teacher-Side API Probe")

    teacher_endpoints = [
        "/api/teacher/rollcall",
        "/api/teacher/rollcalls",
        "/api/teacher/course",
        "/api/teacher/courses",
        "/api/rollcall/create",
        "/api/rollcall/generate_qr",
        "/api/rollcall/start",
        "/api/rollcall/open",
    ]
    if rollcall_id:
        teacher_endpoints += [
            f"/api/teacher/rollcall/{rollcall_id}",
            f"/api/teacher/rollcall/{rollcall_id}/qr",
            f"/api/teacher/rollcall/{rollcall_id}/qrcode",
            f"/api/rollcall/{rollcall_id}/qr_code_data",
            f"/api/rollcall/{rollcall_id}/generate_qr",
        ]

    results = []

    for ep in teacher_endpoints:
        url = urljoin(BASE_URL, ep)
        for method in ["GET", "POST"]:
            status, data, headers, elapsed = try_request(session, method, url)
            if status and status not in (404, 405, 403):
                results.append({
                    "method": method, "url": url, "status": status, "data": data
                })
                cprint(Colors.MAGENTA, f"  {method} {ep} -> {status}")
                if data:
                    info(f"    Response: {json.dumps(data, ensure_ascii=False)[:200]}")

    if not results:
        info("No teacher-side endpoints accessible (expected with student credentials).")
    else:
        ok(f"Found {len(results)} accessible teacher endpoints (unusual!).")

    return results


# ============================================================
# STRATEGY 19: WebSocket endpoint check
# ============================================================
def strategy_websocket_check(session, rollcall_id):
    """Check for WebSocket endpoints. QR may use WS for real-time token push."""
    section("STRATEGY 19 — WebSocket Endpoint Check")

    # We can't actually connect WebSocket easily, but we can:
    # 1. Check for socket.io.js in page source
    # 2. Look for ws:// or wss:// in JS
    # 3. Try HTTP upgrade requests

    ws_hints = []

    # Check page source for WebSocket references
    pages = ["/", "/student"]
    for path in pages:
        url = urljoin(BASE_URL, path)
        try:
            resp = session.get(url, headers={**HEADERS, "Accept": "text/html,*/*"}, timeout=TIMEOUT)
            if resp.status_code == 200:
                text = resp.text
                # socket.io
                sio = re.findall(r'socket\.io|io\.connect|socket\.io\.js', text, re.IGNORECASE)
                if sio:
                    ws_hints.append({"page": path, "type": "socket.io", "matches": sio})
                    info(f"  Socket.IO references in {path}: {sio}")
                # WebSocket URLs
                ws_urls = re.findall(r'(wss?://[^\s"\'<>]+)', text)
                if ws_urls:
                    ws_hints.append({"page": path, "type": "ws_url", "matches": ws_urls})
                    info(f"  WebSocket URLs in {path}: {ws_urls}")
                # new WebSocket(
                ws_new = re.findall(r'new\s+WebSocket\s*\(\s*["\']([^"\']+)["\']', text)
                if ws_new:
                    ws_hints.append({"page": path, "type": "WebSocket_ctor", "matches": ws_new})
                    info(f"  WebSocket constructors in {path}: {ws_new}")
        except Exception:
            pass

    # Try HTTP upgrade to common WS paths
    ws_paths = [
        "/socket.io/", "/ws", "/api/ws", "/ws/rollcall",
        "/signal", "/api/signal", "/stream",
    ]
    for wp in ws_paths:
        url = urljoin(BASE_URL, wp)
        try:
            resp = session.get(url, headers={
                **HEADERS,
                "Upgrade": "websocket",
                "Connection": "Upgrade",
                "Sec-WebSocket-Version": "13",
                "Sec-WebSocket-Key": "dGhlIHNhbXBsZSBub25jZQ==",
            }, timeout=5)
            if resp.status_code in (101, 426):
                info(f"  WS upgrade {wp} -> {resp.status_code}")
                ws_hints.append({"path": wp, "status": resp.status_code, "type": "upgrade_response"})
            elif resp.status_code != 400:
                info(f"  GET {wp} -> {resp.status_code}")
        except Exception:
            pass

    if not ws_hints:
        info("No WebSocket references found.")
    else:
        ok(f"Found {len(ws_hints)} WebSocket hints.")

    return ws_hints


# ============================================================
# STRATEGY 20: Content negotiation
# ============================================================
def strategy_content_negotiation(session, rollcall_id):
    """Vary Accept/Content-Type headers to trigger different response formats."""
    section("STRATEGY 20 — Content Negotiation")

    targets = ["/api/radar/rollcalls", "/api/profile"]
    if rollcall_id:
        targets += [f"/api/rollcall/{rollcall_id}", f"/api/rollcall/{rollcall_id}/student_rollcalls"]

    accept_headers = [
        "application/json",
        "text/html",
        "application/xml",
        "*/*",
        "application/vnd.api+json",
        "application/json, text/plain, */*",
    ]

    results = []

    for path in targets:
        url = urljoin(BASE_URL, path)
        for accept in accept_headers:
            hdrs = {**HEADERS, "Accept": accept}
            try:
                resp = session.get(url, headers=hdrs, timeout=TIMEOUT)
                ct = resp.headers.get("Content-Type", "")
                clen = len(resp.content)
                info(f"  GET {path} Accept={accept[:30]}... -> {resp.status_code} ({ct}, {clen}B)")
                results.append({
                    "path": path, "accept": accept,
                    "status": resp.status_code, "content_type": ct, "size": clen,
                })
                # Check if response differs significantly
                if "json" in accept and "html" in ct.lower():
                    info(f"    → Asked for JSON, got HTML! Possible redirect or error page.")
            except Exception:
                pass

    ok(f"Tested {len(results)} Accept-header combinations across {len(targets)} endpoints.")
    return results


# ============================================================
# MAIN
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="QR Code Rollcall API Detection Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python detect_qr_api.py
  python detect_qr_api.py --username 123456 --password mypass
  python detect_qr_api.py --rollcall-id 12345 --output results.json
        """
    )
    parser.add_argument("--username", "-u", help="XMU username (student ID)")
    parser.add_argument("--password", "-p", help="XMU password")
    parser.add_argument("--rollcall-id", "-r", help="Specific rollcall ID to analyze")
    parser.add_argument("--output", "-o", help="Output JSON file for results")
    args = parser.parse_args()

    print(f"\n{'='*70}")
    cprint(Colors.BOLD + Colors.CYAN, "  QR Code Rollcall API Detection Script")
    cprint(Colors.GRAY, "  Multi-strategy reverse-engineering for Tronclass/XMU")
    print(f"{'='*70}")

    # ---- Login ----
    section("INITIALIZATION — Login")

    if args.username and args.password:
        sub("Logging in with provided credentials...")
        session = xmulogin(type=3, username=args.username, password=args.password)
    else:
        sub("No credentials provided. Reading from config...")
        try:
            from xmu_rollcall.config import load_config, get_current_account, get_cookies_path
            from xmu_rollcall.utils import load_session, verify_session

            config = load_config()
            account = get_current_account(config)
            if not account:
                fail("No account configured. Run 'xmu config' first or provide --username/--password.")
                sys.exit(1)

            cookies_path = get_cookies_path(account.get("id"))
            session = requests.Session()

            if os.path.exists(cookies_path) and load_session(session, cookies_path):
                profile = verify_session(session)
                if profile:
                    ok(f"Session restored for {profile.get('name', 'unknown')}")
                else:
                    warn("Cached session expired, re-logging in...")
                    session = xmulogin(type=3, username=account["username"], password=account["password"])
            else:
                sub("No cached session, logging in...")
                session = xmulogin(type=3, username=account["username"], password=account["password"])
        except ImportError:
            fail("Cannot import config. Provide --username and --password.")
            sys.exit(1)

    if not session:
        fail("Login failed.")
        sys.exit(1)

    ok("Login successful.")

    # ---- Get rollcall ID ----
    section("FETCHING ROLLCALLS")

    rollcalls_url = urljoin(BASE_URL, "/api/radar/rollcalls")
    try:
        resp = session.get(rollcalls_url, headers=HEADERS, timeout=TIMEOUT)
        data = resp.json()
    except Exception as e:
        fail(f"Cannot fetch rollcalls: {e}")
        sys.exit(1)

    rollcalls = data.get("rollcalls", [])
    info(f"Active rollcalls: {len(rollcalls)}")

    if not rollcalls:
        if args.rollcall_id:
            target_rollcall_id = args.rollcall_id
            target_rollcall_data = {}
            warn(f"No active rollcalls, but using provided ID: {target_rollcall_id}")
        else:
            # ===== EARLY EXIT: nothing to analyze =====
            warn("No active rollcalls and no --rollcall-id provided.")
            fail("Nothing to analyze. Run this script when a rollcall is active,")
            fail("or provide a specific rollcall ID with --rollcall-id.")
            fail("Only ID-independent strategies will be skipped.")
            print()
            # Still run the ID-independent strategies for general reconnaissance
            info("Running ID-independent strategies for general reconnaissance...")
            target_rollcall_id = None
            target_rollcall_data = {}
    else:
        qr_rollcalls = [rc for rc in rollcalls
                        if not rc.get("is_radar") and not rc.get("is_number")]
        if args.rollcall_id:
            target = next((rc for rc in rollcalls
                          if str(rc.get("rollcall_id")) == str(args.rollcall_id)), None)
            if not target:
                fail(f"Rollcall ID {args.rollcall_id} not found in active list.")
                sys.exit(1)
            target_rollcall_id = target["rollcall_id"]
            target_rollcall_data = target
            info(f"Using specified rollcall: {target.get('course_title')} (ID: {target_rollcall_id})")
        elif qr_rollcalls:
            target = qr_rollcalls[0]
            target_rollcall_id = target["rollcall_id"]
            target_rollcall_data = target
            ok(f"Targeting QR rollcall: {target.get('course_title')} (ID: {target_rollcall_id})")
        else:
            target = rollcalls[0]
            target_rollcall_id = target["rollcall_id"]
            target_rollcall_data = target
            warn(f"No QR rollcall active. Using: {target.get('course_title')} "
                 f"(type: {'radar' if target.get('is_radar') else 'number'})")

    # Print rollcall summary
    for rc in rollcalls:
        rc_type = ("QR" if not rc.get("is_radar") and not rc.get("is_number")
                   else ("Radar" if rc.get("is_radar") else "Number"))
        marker = " <<< TARGET" if rc.get("rollcall_id") == target_rollcall_id else ""
        info(f"  [{rc_type}] {rc.get('course_title','?')} "
             f"by {rc.get('created_by_name','?')} "
             f"(status: {rc.get('status','?')}){marker}")

    # ---- Run all 20 strategies ----
    results = {}

    strategies = [
        # ID-dependent (auto-skipped when target_rollcall_id is None)
        ("01_endpoint_fuzzing",     lambda: strategy_endpoint_fuzzing(session, target_rollcall_id)),
        ("04_error_mining",         lambda: strategy_error_mining(session, target_rollcall_id)),
        ("10_number_code_style",    lambda: strategy_number_code_style(session, target_rollcall_id)),
        ("15_qr_image_extraction",  lambda: strategy_qr_image_extraction(session, target_rollcall_id)),
        # ID-optional (graceful degradation)
        ("02_deep_inspection",      lambda: strategy_deep_inspection(session, target_rollcall_id, data)),
        ("03_web_source",           lambda: strategy_web_source(session, target_rollcall_id)),
        ("06_mobile_api",           lambda: strategy_mobile_api(session, target_rollcall_id)),
        ("07_header_analysis",      lambda: strategy_header_analysis(session, target_rollcall_id)),
        ("11_diff_analysis",        lambda: strategy_diff_analysis(session, target_rollcall_id)),
        ("14_cors_analysis",        lambda: strategy_cors_analysis(session, target_rollcall_id)),
        ("16_versioned_api",        lambda: strategy_versioned_api(session, target_rollcall_id)),
        ("18_teacher_api",          lambda: strategy_teacher_api(session, target_rollcall_id)),
        ("19_websocket_check",      lambda: strategy_websocket_check(session, target_rollcall_id)),
        ("20_content_negotiation",  lambda: strategy_content_negotiation(session, target_rollcall_id)),
        # ID-independent (always run)
        ("05_docs_discovery",       lambda: strategy_docs_discovery(session)),
        ("08_js_bundle",            lambda: strategy_js_bundle_scraping(session)),
        ("09_cookie_audit",         lambda: strategy_cookie_audit(session)),
        ("12_community_knowledge",  strategy_community_knowledge),
        ("13_course_list",          lambda: strategy_course_list(session)),
        ("17_graphql_introspection", lambda: strategy_graphql_introspection(session)),
    ]

    for name, func in strategies:
        try:
            results[name] = func()
        except Exception as e:
            fail(f"Strategy '{name}' crashed: {e}")
            results[name] = {"error": str(e)}

    # ---- Summary ----
    section("SUMMARY")

    total_findings = 0
    for name, result in sorted(results.items()):
        if isinstance(result, list):
            count = len(result)
        elif isinstance(result, dict):
            count = sum(1 for v in result.values() if v)
        else:
            count = 0
        if count > 0:
            found(f"{name}: {count} finding(s)")
            total_findings += count

    if total_findings == 0:
        warn("No QR-related findings across all strategies.")
        warn("Possible reasons:")
        warn("  1. No QR rollcall is currently active — try during class time")
        warn("  2. Tronclass API structure has changed significantly")
        warn("  3. QR check-in uses a completely different mechanism (mobile-only, WebSocket)")
        warn("  4. Need to run mitmproxy/Charles to capture mobile app traffic")
    else:
        ok(f"Total findings across all strategies: {total_findings}")

    # ---- Output to file ----
    if args.output:
        serializable = {}
        for k, v in results.items():
            if isinstance(v, (list, dict, str, int, bool, type(None))):
                serializable[k] = v
            else:
                serializable[k] = str(v)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(serializable, f, indent=2, ensure_ascii=False)
        ok(f"Results saved to {args.output}")

    print()


if __name__ == "__main__":
    main()
