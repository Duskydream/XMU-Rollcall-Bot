 [i]     key_match: GET /api/rollcall/372654/student_rollcalls.student_rollcalls[163].department.code = '103048'
  [i]     key_match: GET /api/rollcall/372654/student_rollcalls.student_rollcalls[163].klass.code = None
  [i]     key_match: GET /api/rollcall/372654/student_rollcalls.student_rollcalls[163].rollcall_status = 'absent'
  [i]     key_match: GET /api/rollcall/372654/student_rollcalls.student_rollcalls[163].status = 'absent'
  [i]     key_match: GET /api/rollcall/372654/student_rollcalls.student_rollcalls[163].status_detail = ''
  [i]     key_match: GET /api/rollcall/372654/student_rollcalls.student_rollcalls[164].department.code = '103031'
  [i]     key_match: GET /api/rollcall/372654/student_rollcalls.student_rollcalls[164].klass.code = None
  [i]     key_match: GET /api/rollcall/372654/student_rollcalls.student_rollcalls[164].rollcall_status = 'absent'
  [i]     key_match: GET /api/rollcall/372654/student_rollcalls.student_rollcalls[164].status = 'absent'
  [i]     key_match: GET /api/rollcall/372654/student_rollcalls.student_rollcalls[164].status_detail = ''
  [i]     key_match: GET /api/rollcall/372654/student_rollcalls.type = 'qr_rollcall'
  [i]     value_match: GET /api/rollcall/372654/student_rollcalls.type = 'qr_rollcall'
  [i]     value_match: GET /api/rollcall/372654/student_rollcalls.type = 'qr_rollcall'
  [2c: Checking profile API]
  [i]     key_match: profile.audit.status = None
  [i]     key_match: profile.avatar_big_url = ''
  [i]     key_match: profile.avatar_small_url = ''
  [i]     key_match: profile.created_by.avatar_big_url = 'https://lnt.xmu.edu.cn:443/api/uploads/5232822/modified-image?thumbnail=200x200&crop_box=0,0,150,150'
  [i]     value_match: profile.created_by.avatar_big_url = 'https://lnt.xmu.edu.cn:443/api/uploads/5232822/modified-image?thumbnail=200x200&crop_box=0,0,150,150'
  [i]     key_match: profile.created_by.avatar_small_url = 'https://lnt.xmu.edu.cn:443/api/uploads/5232822/modified-image?thumbnail=32x32&crop_box=0,0,150,150'
  [i]     value_match: profile.created_by.avatar_small_url = 'https://lnt.xmu.edu.cn:443/api/uploads/5232822/modified-image?thumbnail=32x32&crop_box=0,0,150,150'
  [i]     key_match: profile.department.code = '103048'
  [i]     key_match: profile.org.code = 'xmu'
  [i]     key_match: profile.org.type = 'university'
  [i]     key_match: profile.program.code = None
  [i]     key_match: profile.program.discipline.code = None
  [i]     key_match: profile.program.status = None
  [i]     key_match: profile.updated_by.avatar_big_url = None
  [i]     key_match: profile.updated_by.avatar_small_url = None
  [i]     key_match: profile.user_attributes.job_type = None
  [i]     key_match: profile.user_attributes.occupation_type = 'none'
  [i]     key_match: profile.user_attributes.portfolio_url = None
  [i]     key_match: profile.user_personas.data.area_code_for_company_phone = None
  [i]     key_match: profile.user_personas.data.area_code_for_fax_number = None
  [i]     key_match: profile.user_personas.data.country_code = None
  [i]     key_match: profile.user_personas.data.country_code_for_company_phone = None
  [i]     key_match: profile.user_personas.data.country_code_for_fax_number = None
  [i]     key_match: profile.user_personas.data.upload_url = None
  [✓] Total matches from deep inspection: 862

======================================================================
  STRATEGY 3 — Web Page Source Analysis
======================================================================
  [i]   GET / -> 200 (958425 bytes, text/html; charset=utf-8)
  [i]     Match: QRCode
  [i]     Context: ...ass="second-level">                         <div class="app-QRCode ng-cloak" ng-class="{'app-zju': 'XMU' == 'ZJU' }"          ...
  [i]     Match: qrcode
  [i]     Context: ...e'; locale = 'zh-CN'">                                     <qrcode class="QRCode" size="110" version="6" data="https://lnt.xmu...
  [i]     Match: QRCode
  [i]     Context: ...ass="second-level">                         <div class="app-QRCode ng-cloak" ng-class="{'app-zju': 'XMU' == 'ZJU' }"          ...
  [i]     Match: QRCode
  [i]     Context: ...ass="second-level">                         <div class="app-QRCode ng-cloak" ng-class="{'app-zju': 'XMU' == 'ZJU' }"          ...
  [i]     Match: qrcode
  [i]     Context: ...e'; locale = 'zh-CN'">                                     <qrcode class="QRCode" size="110" version="6" data="https://lnt.xmu...
  [i]     Match: QRCode
  [i]     Context: ...ass="second-level">                         <div class="app-QRCode ng-cloak" ng-class="{'app-zju': 'XMU' == 'ZJU' }"          ...
  [i]     Match: "QRCode"
  [i]     Context: ...'zh-CN'">                                     <qrcode class="QRCode" size="110" version="6" data="https://lnt.xmu.edu.cn:443/mob...
  [✓] Found 7 references in web sources.

======================================================================
  STRATEGY 6 — Mobile API Probing
======================================================================
  [i]   GET /api/profile (UA: TronClass/3.0 (iPhone; iOS 17....) -> 200, keys: ['active', 'active_at', 'audit', 'avatar_big_url', 'avatar_small_url', 'comment', 'created_at', 'created_by', 'department', 'education', 'email', 'end_at', 'grade', 'has_ai_ability', 'id', 'imported_from', 'is_imported_data', 'klass', 'mobile_phone', 'name', 'nickname', 'org', 'program', 'program_id', 'remarks', 'require_verification', 'role', 'roles', 'storage_assigned', 'storage_used', 'total_course', 'total_forum', 'total_homework', 'updated_at', 'updated_by', 'user_addresses', 'user_attributes', 'user_auth_externals', 'user_no', 'user_personas', 'webex_auth']
  [i]   GET /api/profile (UA: Mozilla/5.0 (iPhone; CPU iPhon...) -> 200, keys: ['active', 'active_at', 'audit', 'avatar_big_url', 'avatar_small_url', 'comment', 'created_at', 'created_by', 'department', 'education', 'email', 'end_at', 'grade', 'has_ai_ability', 'id', 'imported_from', 'is_imported_data', 'klass', 'mobile_phone', 'name', 'nickname', 'org', 'program', 'program_id', 'remarks', 'require_verification', 'role', 'roles', 'storage_assigned', 'storage_used', 'total_course', 'total_forum', 'total_homework', 'updated_at', 'updated_by', 'user_addresses', 'user_attributes', 'user_auth_externals', 'user_no', 'user_personas', 'webex_auth']
  [i]   GET /api/profile (UA: TronClass/3.0 (Android 14; Pix...) -> 200, keys: ['active', 'active_at', 'audit', 'avatar_big_url', 'avatar_small_url', 'comment', 'created_at', 'created_by', 'department', 'education', 'email', 'end_at', 'grade', 'has_ai_ability', 'id', 'imported_from', 'is_imported_data', 'klass', 'mobile_phone', 'name', 'nickname', 'org', 'program', 'program_id', 'remarks', 'require_verification', 'role', 'roles', 'storage_assigned', 'storage_used', 'total_course', 'total_forum', 'total_homework', 'updated_at', 'updated_by', 'user_addresses', 'user_attributes', 'user_auth_externals', 'user_no', 'user_personas', 'webex_auth']
  [i]   GET /api/profile (UA: okhttp/4.12.0...) -> 200, keys: ['active', 'active_at', 'audit', 'avatar_big_url', 'avatar_small_url', 'comment', 'created_at', 'created_by', 'department', 'education', 'email', 'end_at', 'grade', 'has_ai_ability', 'id', 'imported_from', 'is_imported_data', 'klass', 'mobile_phone', 'name', 'nickname', 'org', 'program', 'program_id', 'remarks', 'require_verification', 'role', 'roles', 'storage_assigned', 'storage_used', 'total_course', 'total_forum', 'total_homework', 'updated_at', 'updated_by', 'user_addresses', 'user_attributes', 'user_auth_externals', 'user_no', 'user_personas', 'webex_auth']
  [!] No mobile-specific endpoints found.

======================================================================
  STRATEGY 7 — Response Header Analysis
======================================================================
  [i]   GET /api/radar/rollcalls -> 200
  [i]     Server: none
  [i]     Content-Type: application/json
  [i]     access-control-expose-headers: X-SESSION-ID
  [i]     set-cookie: session=V2-1-301cadda-3770-4cc9-8675-b9d6e27be339.MjQxNzg1.1778719722617.nAKc9PtEw_e0R4COi_Vp4nT0Sc8; Secure; HttpOnly; Path=/
  [i]     x-session-id: V2-1-301cadda-3770-4cc9-8675-b9d6e27be339.MjQxNzg1.1778719722617.nAKc9PtEw_e0R4COi_Vp4nT0Sc8
  [i]     access-control-allow-headers: Authorization,DNT,X-SESSION-ID,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range, DNT,X-SESSION-ID,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range
  [i]     x-content-type-options: nosniff, nosniff
  [i]     x-frame-options: ALLOW-FROM https://c-rms.xmu.edu.cn
  [i]     access-control-allow-origin: *
  [i]   GET /api/profile -> 200
  [i]     Server: none
  [i]     Content-Type: application/json
  [i]     access-control-expose-headers: X-SESSION-ID
  [i]     set-cookie: session=V2-1-301cadda-3770-4cc9-8675-b9d6e27be339.MjQxNzg1.1778719722816.rm_2fbsn-88jSmSAmKe_TIxv38k; Secure; HttpOnly; Path=/
  [i]     x-session-id: V2-1-301cadda-3770-4cc9-8675-b9d6e27be339.MjQxNzg1.1778719722816.rm_2fbsn-88jSmSAmKe_TIxv38k
  [i]     access-control-allow-headers: Authorization,DNT,X-SESSION-ID,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range, DNT,X-SESSION-ID,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range
  [i]     x-content-type-options: nosniff, nosniff
  [i]     x-frame-options: ALLOW-FROM https://c-rms.xmu.edu.cn
  [i]     access-control-allow-origin: *
  [i]   GET /api/rollcall/372654 -> 500
  [i]     Server: none
  [i]     Content-Type: text/html
  [i]   GET /api/rollcall/372654/answer -> 500
  [i]     Server: none
  [i]     Content-Type: text/html
  [i]   GET /api/rollcall/372654/student_rollcalls -> 200
  [i]     Server: none
  [i]     Content-Type: application/json
  [i]     access-control-expose-headers: X-SESSION-ID
  [i]     set-cookie: session=V2-1-301cadda-3770-4cc9-8675-b9d6e27be339.MjQxNzg1.1778719723224.Ro-M52-wiaBFw6Z0aoxDtZTOvZU; Secure; HttpOnly; Path=/
  [i]     x-session-id: V2-1-301cadda-3770-4cc9-8675-b9d6e27be339.MjQxNzg1.1778719723224.Ro-M52-wiaBFw6Z0aoxDtZTOvZU
  [i]     access-control-allow-headers: Authorization,DNT,X-SESSION-ID,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range, DNT,X-SESSION-ID,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range
  [i]     x-content-type-options: nosniff, nosniff
  [i]     x-frame-options: ALLOW-FROM https://c-rms.xmu.edu.cn
  [i]     access-control-allow-origin: *
  [✓] Collected 31 interesting headers.

======================================================================
  STRATEGY 11 — Cross-Type Diff Analysis
======================================================================
  [i]   Total rollcalls: 1
  [i]   qr: 1 rollcall(s)
  [i]     Fields: ['avatar_big_url', 'class_name', 'course_id', 'course_title', 'created_by', 'created_by_name', 'department_name', 'grade_name', 'group_set_id', 'is_expired', 'is_number', 'is_radar', 'published_at', 'rollcall_id', 'rollcall_status', 'rollcall_time', 'scored', 'source', 'status', 'student_rollcall_id', 'title', 'type']
  [i]     Extra field: avatar_big_url = ''
  [i]     Extra field: class_name = ''
  [i]     Extra field: course_id = 89759
  [i]     Extra field: created_by = 20384
  [i]     Extra field: grade_name = ''
  [i]     Extra field: group_set_id = 0
  [i]     Extra field: published_at = None
  [i]     Extra field: rollcall_time = '2026-05-13T00:47:23Z'
  [i]     Extra field: source = 'qr'
  [i]     Extra field: student_rollcall_id = 0
  [i]     Extra field: title = '2026.05.13 08:47'
  [i]     Extra field: type = 'qr_rollcall'

======================================================================
  STRATEGY 14 — CORS Preflight Analysis
======================================================================
  [i]   OPTIONS /api/radar/rollcalls -> 200
  [i]     allow_methods: GET, OPTIONS, POST, HEAD
  [i]   OPTIONS /api/profile -> 200
  [i]     allow_methods: GET, OPTIONS, HEAD
  [i]   OPTIONS /api/rollcall/372654 -> 200
  [i]     allow_methods: DELETE, PATCH, OPTIONS, PUT
  [i]   OPTIONS /api/rollcall/372654/answer -> 200
  [i]     allow_methods: OPTIONS, PUT, PATCH
  [i]   OPTIONS /api/rollcall/372654/student_rollcalls -> 200
  [i]     allow_methods: GET, OPTIONS, HEAD
  [✓] CORS info for 5 endpoints.

======================================================================
  STRATEGY 16 — Versioned API Probing
======================================================================
  [i] No versioned API endpoints found.

======================================================================
  STRATEGY 18 — Teacher-Side API Probe
======================================================================
  [i] No teacher-side endpoints accessible (expected with student credentials).

======================================================================
  STRATEGY 19 — WebSocket Endpoint Check
======================================================================
  [i]   WS upgrade /socket.io/ -> 101
  [i]   GET /ws -> 404
  [i]   GET /api/ws -> 404
  [i]   GET /ws/rollcall -> 404
  [i]   GET /signal -> 404
  [i]   GET /api/signal -> 404
  [i]   GET /stream -> 404
  [✓] Found 1 WebSocket hints.

======================================================================
  STRATEGY 20 — Content Negotiation
======================================================================
  [i]   GET /api/radar/rollcalls Accept=application/json... -> 200 (application/json, 537B)
  [i]   GET /api/radar/rollcalls Accept=text/html... -> 200 (application/json, 537B)
  [i]   GET /api/radar/rollcalls Accept=application/xml... -> 200 (application/json, 537B)
  [i]   GET /api/radar/rollcalls Accept=*/*... -> 200 (application/json, 537B)
  [i]   GET /api/radar/rollcalls Accept=application/vnd.api+json... -> 200 (application/json, 537B)
  [i]   GET /api/radar/rollcalls Accept=application/json, text/plain, ... -> 200 (application/json, 537B)
  [i]   GET /api/profile Accept=application/json... -> 200 (application/json, 3333B)
  [i]   GET /api/profile Accept=text/html... -> 200 (application/json, 3333B)
  [i]   GET /api/profile Accept=application/xml... -> 200 (application/json, 3333B)
  [i]   GET /api/profile Accept=*/*... -> 200 (application/json, 3333B)
  [i]   GET /api/profile Accept=application/vnd.api+json... -> 200 (application/json, 3333B)
  [i]   GET /api/profile Accept=application/json, text/plain, ... -> 200 (application/json, 3333B)
  [i]   GET /api/rollcall/372654 Accept=application/json... -> 500 (text/html, 1686B)
  [i]     → Asked for JSON, got HTML! Possible redirect or error page.
  [i]   GET /api/rollcall/372654 Accept=text/html... -> 500 (text/html, 1686B)
  [i]   GET /api/rollcall/372654 Accept=application/xml... -> 500 (text/html, 1686B)
  [i]   GET /api/rollcall/372654 Accept=*/*... -> 500 (text/html, 1686B)
  [i]   GET /api/rollcall/372654 Accept=application/vnd.api+json... -> 500 (text/html, 1686B)
  [i]     → Asked for JSON, got HTML! Possible redirect or error page.
  [i]   GET /api/rollcall/372654 Accept=application/json, text/plain, ... -> 500 (text/html, 1686B)
  [i]     → Asked for JSON, got HTML! Possible redirect or error page.
  [i]   GET /api/rollcall/372654/student_rollcalls Accept=application/json... -> 200 (application/json, 61600B)
  [i]   GET /api/rollcall/372654/student_rollcalls Accept=text/html... -> 200 (application/json, 61600B)
  [i]   GET /api/rollcall/372654/student_rollcalls Accept=application/xml... -> 200 (application/json, 61600B)
  [i]   GET /api/rollcall/372654/student_rollcalls Accept=*/*... -> 200 (application/json, 61600B)
  [i]   GET /api/rollcall/372654/student_rollcalls Accept=application/vnd.api+json... -> 200 (application/json, 61600B)
  [i]   GET /api/rollcall/372654/student_rollcalls Accept=application/json, text/plain, ... -> 200 (application/json, 61607B)
  [✓] Tested 24 Accept-header combinations across 4 endpoints.

======================================================================
  STRATEGY 5 — API Documentation Discovery
======================================================================
  [!] No API documentation endpoints found.

======================================================================
  STRATEGY 8 — JS Bundle Scraping
======================================================================
  [i]   Found 78 JS references on main page.
  [i]   Fetching: https://lnt.xmu.edu.cn/static/25996-369ed60a.js (27613 bytes)
  [i]   Fetching: https://lnt.xmu.edu.cn/static/95093-78347e93.js (61229 bytes)
  [i]   Fetching: https://lnt.xmu.edu.cn/static/91962-91463afb.js (31449 bytes)
  [i]     Match: /api/rollcall/
  [i]     Match: /api/rollcall/
  [i]     Match: /api/rollcall/
  [i]     Match: /api/rollcall/
  [i]     Match: /api/rollcall/
  [i]   Fetching: https://lnt.xmu.edu.cn/static/65238-c67ee9fb.js (25211 bytes)
  [i]   Fetching: https://lnt.xmu.edu.cn/static/30803-7b1f840f.js (1055054 bytes)
  [i]   Fetching: https://lnt.xmu.edu.cn/static/98133-ef5ebb8f.js (33806 bytes)
  [i]   Fetching: https://lnt.xmu.edu.cn/static/61409-cf835457.js (786275 bytes)
  [i]   Fetching: https://lnt.xmu.edu.cn/static/96431-8c3957af.js (53388 bytes)
  [i]   Fetching: https://lnt.xmu.edu.cn/static/83920-78334aed.js (36496 bytes)
  [i]   Fetching: https://lnt.xmu.edu.cn/static/68924-a30f5597.js (283118 bytes)
  [i]   Fetching: https://lnt.xmu.edu.cn/static/47959-8670e637.js (95031 bytes)
  [i]   Fetching: https://lnt.xmu.edu.cn/static/93110-634bbef4.js (31006 bytes)
  [i]   Fetching: https://lnt.xmu.edu.cn/static/49123-8cda630f.js (62590 bytes)
  [i]   Fetching: https://lnt.xmu.edu.cn/static/6485-9ef9b8a8.js (42718 bytes)
  [i]   Fetching: https://lnt.xmu.edu.cn/static/54964-7faa4ec3.js (43293 bytes)
  [i]   Fetching: https://lnt.xmu.edu.cn/static/13958-91152030.js (108701 bytes)
  [i]   Fetching: https://lnt.xmu.edu.cn/static/55054-b3dcb926.js (3257117 bytes)
  [i]     Match: answers_field":"請在題目中插入填空格","role_name_duplicated":"角色名稱重複","save_success":"儲存成功
  [i]     Match: QR Code的方式加入TronClass營運人員微信獲取幫助。","no_org_submit_tip":"您的資訊不存在，請檢查後重新輸入或聯繫您所在學校T
  [i]     Match: qrcode
  [i]     Match: qrcode
  [i]     Match: qrcode
  [i]     Match: QrCode
  [i]     Match: qrCode
  [i]     Match: qrcode
  [i]     Match: qrcode
  [i]     Match: qrcode
  [i]     Match: QrCode
  [i]     Match: qrCode
  [i]     Match: rollcallType":{"merged":"合併生成","newCapec":"新開普","manual":"手動點名","selfRegistratio
  [i]     Match: tyPeriod":"有效期","1day":"1天","7days":"7天","30days":"30天","365days":"365天","perman
  [i]     Match: Rollcall":"課程各項計分學習活動成績、影片觀看完成度成績，與課程總成績","questionUnit":"個問題"},"stat":{"departm
  [i]   Fetching: https://lnt.xmu.edu.cn/static/56662-68e56a01.js (33355 bytes)
  [i]   Fetching: https://lnt.xmu.edu.cn/static/13067-3b42e012.js (36494 bytes)
  [i]   Fetching: https://lnt.xmu.edu.cn/static/42789-f3817b0b.js (153110 bytes)
  [i]     Match: qrcode
  [i]     Match: qrcode
  [i]     Match: qrcode
  [i]     Match: qrcode
  [i]     Match: qrcode
  [i]     Match: qrcode
  [i]     Match: qrcode
  [i]     Match: qrcode
  [i]     Match: qrcode
  [i]     Match: qrcode
  [✓] Found 30 references in JS bundles.

======================================================================
  STRATEGY 9 — Cookie & Token Audit
======================================================================
  [i]   Session cookies (13):
  [i]     platformMultilingual = ****
  [i]     CLIENT_URL = ****
  [i]     AUTH_SESSION_ID = 7d21****2485
  [>>> FOUND <<<]   Interesting cookie: AUTH_SESSION_ID
  [i]     AUTH_SESSION_ID_LEGACY = 7d21****2485
  [>>> FOUND <<<]   Interesting cookie: AUTH_SESSION_ID_LEGACY
  [i]     KEYCLOAK_IDENTITY = eyJh****9tUc
  [i]     KEYCLOAK_IDENTITY_LEGACY = eyJh****9tUc
  [i]     KEYCLOAK_SESSION = xmu/****5215
  [>>> FOUND <<<]   Interesting cookie: KEYCLOAK_SESSION
  [i]     KEYCLOAK_SESSION_LEGACY = xmu/****5215
  [>>> FOUND <<<]   Interesting cookie: KEYCLOAK_SESSION_LEGACY
  [i]     happyVoyage = q3Yd****pqI=
  [i]     CASTGC = TGT-****main
  [i]     JSESSIONID = 9742****3AA4
  [>>> FOUND <<<]   Interesting cookie: JSESSIONID
  [i]     route = 9756****b1ba
  [i]     session = V2-1****Rj2o
  [>>> FOUND <<<]   Interesting cookie: session

======================================================================
  STRATEGY 12 — Community Knowledge
======================================================================
  [i]   Tronclass QR theory 1 — direct submit:
  [i]     flow: GET /api/rollcall/{id}/student_rollcalls → extract qr_token → PUT /api/rollcall/{id}/answer with {qrToken: <token>}
  [i]     evidence: Number rollcall uses identical flow with number_code. QR might use qr_code / qr_token analogously.
  [i]   Tronclass QR theory 2 — scan redirect:
  [i]     flow: QR encodes URL https://lnt.xmu.edu.cn/student/check?rid={id}&token={t} → browser opens → frontend JS parses params → calls answer API
  [i]     evidence: Common pattern in classroom systems. Check page source for URL parsing logic (URLSearchParams, query string extraction).
  [i]   Tronclass QR theory 3 — WebSocket push:
  [i]     flow: Teacher opens QR → server pushes token via WebSocket → student scans and submits token to /api/rollcall/{id}/answer
  [i]     evidence: Some Tronclass versions use Socket.IO. Check for socket.io.js in page source or /socket.io/ endpoint.
  [i]   Tronclass QR theory 4 — image decode:
  [i]     flow: QR code image is an <img> tag on rollcall detail page. The image URL may contain the token. Decode QR from image or extract token from the img src URL parameters.
  [i]     evidence: If page contains /api/rollcall/{id}/qr_image or similar endpoint returning a PNG, the QR can be decoded with pyzbar/opencv.
  [i]   Tronclass QR theory 5 — mobile app sole:
  [i]     flow: QR only works through the Tronclass mobile app. The app uses native camera + proprietary API. Web fallback may not exist.
  [i]     evidence: If no web endpoints work, QR may be mobile-only. Try reverse-engineering the APK or intercepting mobile traffic with mitmproxy.
  [i]   Fields to search for:
  [i]     in rollcall list: qr_code, qr_token, qr_url, qr_image, code_url, scan_url
  [i]     in student_rollcalls: number_code, qr_code, token, student_code
  [i]     in answer response: message, error, success, data

======================================================================
  STRATEGY 13 — Course List Probing
======================================================================
  [i]   GET /api/courses -> 403
  [i]   GET /api/course -> 500
  [!] No course endpoints returned data.

======================================================================
  STRATEGY 17 — GraphQL Introspection
======================================================================
  [i] No GraphQL endpoints found.

======================================================================
  SUMMARY
======================================================================
  [>>> FOUND <<<] 01_endpoint_fuzzing: 21 finding(s)
  [>>> FOUND <<<] 02_deep_inspection: 862 finding(s)
  [>>> FOUND <<<] 03_web_source: 7 finding(s)
  [>>> FOUND <<<] 04_error_mining: 14 finding(s)
  [>>> FOUND <<<] 07_header_analysis: 31 finding(s)
  [>>> FOUND <<<] 08_js_bundle: 30 finding(s)
  [>>> FOUND <<<] 09_cookie_audit: 6 finding(s)
  [>>> FOUND <<<] 10_number_code_style: 331 finding(s)
  [>>> FOUND <<<] 11_diff_analysis: 1 finding(s)
  [>>> FOUND <<<] 12_community_knowledge: 6 finding(s)
  [>>> FOUND <<<] 14_cors_analysis: 5 finding(s)
  [>>> FOUND <<<] 19_websocket_check: 1 finding(s)
  [>>> FOUND <<<] 20_content_negotiation: 24 finding(s)
  [✓] Total findings across all strategies: 1339