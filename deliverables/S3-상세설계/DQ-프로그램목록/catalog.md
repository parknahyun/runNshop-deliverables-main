
# 프로그램 목록 — Catalog 도메인

> 상위 문서: [readme.md](readme.md)
> **단계**: 상세설계 (S3) | **문서범위**: Domain (Catalog) | **문서종류**: Design

---

## 1. 화면 (SCR)

| PGM-ID | 프로그램명 | 채널 | 화면레이아웃 참조 | 세부UC 참조 | 호출 API | 비고 |
|---|---|---|---|---|---|---|
| SCR-A-C01 | 직매입 상품 등록 | admin | DN-admin §1 ProductDirectCreatePage | DK §1 | API-CAT-003 | |
| SCR-A-C02 | 상품 심사 목록 | admin | DN-admin §2 ProductReviewListPage | DK §3 | API-CAT-027 | status=REVIEW_REQUESTED 필터 |
| SCR-A-C03 | 상품 목록 | admin | DN-admin §3 ProductListPage | DK §5 | API-CAT-027 | |
| SCR-A-C04 | 상품 상세 (컨테이너) | admin | DN-admin §4 ProductDetailPage | DK §3,5,6,9 | — | 감싸는 화면 |
| SCR-A-C04-T1 | 상품 상세 — 기본정보 탭 | admin | DN-admin §4 | DK §5 | API-CAT-008a, API-CAT-029a | 요약(summary)·태그(tags) 필드 2026-11-09 소급 반영(DBA §1.3.1·§1.3.3·§1.3.4). 전시여부(isExposed)·검색노출제외(isSearchExcluded) 체크박스 2026-11-09 신설(DBA §2.16) — SCR-A-C04-T6(전시 탭) 폐지로 통합, 미진항목 #3 해소 |
| SCR-A-C04-T2 | 상품 상세 — 이미지/옵션 탭 | admin | DN-admin §4 | DK §5 | API-CAT-044, API-CAT-045, API-CAT-050 | 2026-11-09 소급 반영 — 와이어프레임 설계 및 admin 전용 API 신설로 미진항목 #1 해소. API-CAT-050(옵션값 이미지, 2026-11-09 신설) 추가 |
| SCR-A-C04-T3 | 상품 상세 — 가격 탭 | admin | DN-admin §4 | DK §9 | API-CAT-043, API-CAT-016-1 | 2026-11-09 소급 반영 — admin 전용 가격변경 API 신설로 미진항목 #2 해소 |
| SCR-A-C04-T4 | 상품 상세 — 재고 탭 | admin | DN-admin §4 | DK §6 | API-CAT-011a, API-CAT-029a | 단종 처리 버튼 |
| SCR-A-C04-T5 | 상품 상세 — 심사 탭 | admin | DN-admin §4 | DK §3 | API-CAT-004, API-CAT-005, API-CAT-006 | |
| SCR-A-C05 | 분류체계 관리 (컨테이너) | admin | DN-admin §5 CategoryManagePage | DK §7 | — | 감싸는 화면(2026-11-09: 전시 카테고리 탭 제거, 2탭) |
| SCR-A-C05-T1 | 분류체계 관리 — 표준 카테고리 탭 | admin | DN-admin §5 | DK §7 | API-CAT-012a, API-CAT-012-1a | |
| SCR-A-C05-T3 | 분류체계 관리 — 브랜드 탭 | admin | DN-admin §5 | DK §7 | API-CAT-012c, API-CAT-012-1c | 2026-11-09 와이어프레임 추가 — 미진항목 #6 해소 |
| SCR-A-C10 | 전시카테고리 관리 | admin | DN-admin §8 DisplayCategoryManagePage | DK §7 | API-CAT-012b, API-CAT-012-1b | 2026-11-09 신설(SCR-A-C05-T2에서 분리) |
| SCR-A-C11 | GNB 메뉴 관리 | admin | DN-admin §10 GnbMenuManagePage | DK §27 | API-CAT-046, API-CAT-046-1 | 드래그앤드랍 순서조정(2026-11-09 신설) |
| SCR-A-C06 | 노출 우선순위 관리 | admin | DN-admin §6 ExposurePriorityPage | DK §12 | API-CAT-027, API-CAT-021 | |
| SCR-A-C07 | 전시 페이지 목록 | admin | DN-admin §7 DisplayPageListPage | DK §13 | API-CAT-030 | |
| SCR-A-C08 | 전시 페이지 편집 | admin | DN-admin §7 DisplayPageEditPage | DK §13, §15 | API-CAT-030-1, API-CAT-022a~d, API-CAT-031 | "홈으로 설정" 토글 포함 |
| SCR-A-C09 | 전시카테고리 상품순서 관리 | admin | DN-admin §9 DisplayCategoryProductOrderPage | DK §24 | API-CAT-039, API-CAT-040 | 드래그앤드랍 순서조정, 상단고정(2026-11-09 신설) |
| SCR-P-C01 | 상품 등록 | partner | DN-partner §8 ProductCreatePage | DK §2 | API-CAT-001, API-CAT-002 | |
| SCR-P-C02 | 반려 상품 재작성 | partner | DN-partner §9 ProductRejectedEditPage | DK §4 | API-CAT-029b, API-CAT-007 | |
| SCR-P-C03 | 상품 목록 | partner | DN-partner §10 ProductListPage | DK §5, §16 | API-CAT-028, API-CAT-033 | 행 액션에 "복제" 버튼 추가(2026-11-09 소급 반영) |
| SCR-P-C04 | 상품 상세·수정 | partner | DN-partner §11 ProductEditPage | DK §5, §6, §9, §19 | API-CAT-029b, API-CAT-008b, API-CAT-009, API-CAT-010, API-CAT-011b, API-CAT-016, API-CAT-016-1, API-CAT-049 | admin과 달리 탭 세분화 없이 단일 화면으로 설계됨(DN 서술 방식 차이, 기능상 동등). 최대 주문수량(maxOrderQuantity)·요약·태그·전시여부(isExposed)·검색노출제외(isSearchExcluded) 입력 필드 추가(2026-11-09 소급 반영·신설, API-CAT-008b 필드 확장). API-CAT-049(옵션값 이미지, 2026-11-09 신설) 추가 |
| SCR-P-C05 | 재고 관리 | partner | DN-partner §12 StockManagePage | DK §8 | API-CAT-013-1, API-CAT-013 | |
| SCR-P-C06 | 상품 대량등록 (Bulk Upload) | partner | DN-partner §13 BulkUploadPage | DK §17 | API-CAT-034 | 엑셀 업로드, 행 단위 부분 성공 허용(2026-11-09 소급 반영) |
| SCR-M-C01 | 상품 목록 | mobile | DN-mobile §13 ProductListPage | DK §10, §11, §20 | API-CAT-017, API-CAT-041, API-CAT-035 | 2026-11-09 카테고리 필터 전시카테고리로 변경, 찜 아이콘 추가(2026-11-09 소급 반영) |
| SCR-M-C02 | 상품 검색 | mobile | DN-mobile §14 ProductSearchPage | DK §10 | API-CAT-018, API-CAT-041 | 2026-11-09 카테고리 필터 전시카테고리로 변경 |
| SCR-M-C03 | 상품 상세 | mobile | DN-mobile §15 ProductDetailPage | DK §10, §11, §20, §21 | API-CAT-019, API-CAT-020, API-CAT-035, API-CAT-037a | 찜하기·공유 버튼 추가(2026-11-09 소급 반영) |
| SCR-M-C04 | 홈 | mobile | DN-mobile §17 HomePage | DK §15, §27 | API-CAT-032, API-CAT-047 | 2026-10-26 신설. GNB 퀵메뉴 바 추가(2026-11-09) |
| SCR-M-C05 | 찜한 상품 목록 (마이페이지) | mobile | DN-mobile §18 WishlistPage | DK §20 | API-CAT-036 | 2026-11-09 소급 반영 |
| SCR-M-C06 | 상품 랭킹 (실시간/일간/주간) | mobile | DN-mobile §19 RankingPage | DK §26 | API-CAT-042 | 홈 배너·카테고리 등에서 링크 진입, 전용 메뉴 없음(2026-11-09 신설) |
| SCR-M-C07 | 전시 페이지 뷰어 (비홈) | mobile | DN-mobile §20 DisplayPageViewPage | DK §28 | API-CAT-048 | GNB·공유 링크로만 진입, 전용 메뉴 없음(2026-11-09 신설, 미진항목 #9·#13 해소) |

> 재입고 알림 신청 완료(DN-mobile §16)는 SCR-M-C03 내 레이어 토스트라 별도 화면 ID 없음(Order의
> 알림 화면과 동일 처리 — SCR 제외).

---

## 2. API

### 2-1. 판매자 (partner) API

| PGM-ID | Method | Endpoint | 프로그램명 | 세부UC | 시퀀스 | 호출원 | 상태전이 |
|---|---|---|---|---|---|---|---|
| API-CAT-001 | POST | /api/partner/v1/products | 상품 임시저장 | DK §2 | §2 | SCR-P-C01 | — → DRAFT |
| API-CAT-002 | POST | /api/partner/v1/products/{id}/review-request | 심사 요청 | DK §2 | §2 | SCR-P-C01 | DRAFT→REVIEW_REQUESTED |
| API-CAT-007 | POST | /api/partner/v1/products/{id}/resubmit | 반려 후 재제출 | DK §4 | §4 | SCR-P-C02 | REJECTED→DRAFT |
| API-CAT-008b | PATCH | /api/partner/v1/products/{id} | 상품 기본정보 수정 (partner) | DK §5 | — | SCR-P-C04 | summary·tags·isExposed·isSearchExcluded 필드 2026-11-09 소급 반영·신설 |
| API-CAT-009 | POST | /api/partner/v1/products/{id}/images | 이미지 등록 | DK §5 | §5 | SCR-P-C04 | — |
| API-CAT-010 | POST | /api/partner/v1/products/{id}/options | 옵션그룹·옵션값 설정 | DK §5 | §5 | SCR-P-C04 | SKU 자동생성 |
| API-CAT-011b | POST | /api/partner/v1/products/{id}/discontinue | 상품 단종 처리 (partner) | DK §6 | §6(로직 공용) | SCR-P-C04 | ON_SALE/SOLD_OUT→DISCONTINUED |
| API-CAT-049 | POST | /api/partner/v1/products/{id}/option-values/{optionValueId}/image | 옵션값 이미지 등록 (partner) | DK §5 | §5(partner와 흐름 공유, 전용 다이어그램 없음) | SCR-P-C04 | depth=1 옵션값 전용, 2026-11-09 신설 |
| API-CAT-013 | PATCH | /api/partner/v1/skus/{skuId}/stock | SKU 재고 수량 변경 | DK §8 | §6 | SCR-P-C05 | 조건 충족 시 SOLD_OUT→ON_SALE(대안A) |
| API-CAT-013-1 | GET | /api/partner/v1/skus | SKU 통합 조회 | DK §8 | — | SCR-P-C05 | — |
| API-CAT-016 | PATCH | /api/partner/v1/products/{id}/price | 가격 설정·변경 | DK §9 | §9 | SCR-A-C04-T3(※미진항목 #2), SCR-P-C04 | priceSale은 cat_product_price_schedule 신규 BASE 행 |
| API-CAT-016-1 | GET | /api/partner/v1/products/{id}/price-schedule | 판매가 스케줄 조회 | DK §9 | — | SCR-A-C04-T3, SCR-P-C04 | — |
| API-CAT-028 | GET | /api/partner/v1/products | 상품 목록 조회 (partner) | DK §5 | — | SCR-P-C03 | summary 필드 2026-11-09 소급 반영 |
| API-CAT-029b | GET | /api/partner/v1/products/{id} | 상품 상세 조회 (partner) | DK §5 | — | SCR-P-C02, SCR-P-C04 | 본인 소유 아니면 403. summary·tags·옵션값 imageUrl 2026-11-09 소급 반영 |
| API-CAT-033 | POST | /api/partner/v1/products/{id}/duplicate | 상품 복제 등록 | DK §16 | §17 | SCR-P-C03 | — → DRAFT (가격·재고·판매자상품코드 제외 전체 복사, 2026-11-09 소급 반영) |
| API-CAT-034 | POST | /api/partner/v1/products/bulk-upload | 상품 대량등록(Bulk) | DK §17 | §18 | SCR-P-C06 | — → DRAFT (행 단위 생성, 부분 성공 허용, 2026-11-09 소급 반영) |

### 2-2. 어드민 (admin) API

| PGM-ID | Method | Endpoint | 프로그램명 | 세부UC | 시퀀스 | 호출원 | 상태전이 |
|---|---|---|---|---|---|---|---|
| API-CAT-003 | POST | /api/admin/v1/products | 상품 등록 (직매입) | DK §1 | §1 | SCR-A-C01 | DRAFT→ON_SALE (즉시) |
| API-CAT-004 | POST | /api/admin/v1/products/{id}/review-start | 심사 착수 | DK §3 | §3 | SCR-A-C04-T5 | REVIEW_REQUESTED→UNDER_REVIEW |
| API-CAT-005 | POST | /api/admin/v1/products/{id}/approve | 심사 승인 | DK §3 | §3 | SCR-A-C04-T5 | UNDER_REVIEW→ON_SALE |
| API-CAT-006 | POST | /api/admin/v1/products/{id}/reject | 심사 반려 | DK §3 | §3 | SCR-A-C04-T5 | UNDER_REVIEW→REJECTED |
| API-CAT-008a | PATCH | /api/admin/v1/products/{id} | 상품 기본정보 수정 (admin) | DK §5 | — | SCR-A-C04-T1 | summary·tags·isExposed·isSearchExcluded 필드 2026-11-09 소급 반영·신설 |
| API-CAT-050 | POST | /api/admin/v1/products/{id}/option-values/{optionValueId}/image | 옵션값 이미지 등록 (admin) | DK §5 | §5(partner와 흐름 공유, 전용 다이어그램 없음) | SCR-A-C04-T2 | depth=1 옵션값 전용, 소유자 검증 생략, 2026-11-09 신설 |
| API-CAT-011a | POST | /api/admin/v1/products/{id}/discontinue | 상품 단종 처리 (admin, Role MD-OPERATOR) | DK §6 | §6(로직 공용) | SCR-A-C04-T4 | ON_SALE/SOLD_OUT→DISCONTINUED |
| API-CAT-012a | POST/PATCH/DELETE | /api/admin/v1/categories(/{id}) | 표준 카테고리 CRUD | DK §7 | — | SCR-A-C05-T1 | 중복 이름 시 409 |
| API-CAT-012b | POST/PATCH/DELETE | /api/admin/v1/display-categories(/{id}) | 전시 카테고리 CRUD | DK §7 | — | SCR-A-C05-T2 | — |
| API-CAT-012c | POST/PATCH | /api/admin/v1/brands(/{id}) | 브랜드 등록·수정 | DK §7 | — | SCR-A-C05-T3 | — |
| API-CAT-012-1a | GET | /api/admin/v1/categories | 표준 카테고리 목록 조회 | DK §7 | — | SCR-A-C05-T1 | 2026-10-26 TBD-API 해소 |
| API-CAT-012-1b | GET | /api/admin/v1/display-categories | 전시 카테고리 목록 조회 | DK §7 | — | SCR-A-C05-T2 | 2026-10-26 TBD-API 해소 |
| API-CAT-012-1c | GET | /api/admin/v1/brands | 브랜드 목록 조회 | DK §7 | — | SCR-A-C05-T3 | 2026-10-26 TBD-API 해소 |
| API-CAT-021 | PATCH | /api/admin/v1/products/{id}/exposure-override | 노출 우선순위 수동 설정 | DK §12 | §12 | SCR-A-C06 | — |
| API-CAT-043 | PATCH | /api/admin/v1/products/{id}/price | 가격 설정·변경 (admin) | DK §9 | §9(partner와 흐름 공유, 전용 다이어그램 없음) | SCR-A-C04-T3 | priceSale은 cat_product_price_schedule 신규 BASE 행, createdBy=adminId. 소유자 검증 생략(2026-11-09 신설, 미진항목 #2 해소) |
| API-CAT-044 | POST | /api/admin/v1/products/{id}/images | 이미지 등록 (admin) | DK §5 | §5(partner와 흐름 공유, 전용 다이어그램 없음) | SCR-A-C04-T2 | 소유자 검증 생략(2026-11-09 소급 반영, 미진항목 #1 해소) |
| API-CAT-045 | POST | /api/admin/v1/products/{id}/options | 옵션그룹·옵션값 설정 (admin) | DK §5 | §5(partner와 흐름 공유, 전용 다이어그램 없음) | SCR-A-C04-T2 | SKU 자동생성, 소유자 검증 생략(2026-11-09 소급 반영, 미진항목 #1 해소) |
| API-CAT-046 | POST/PATCH/DELETE/PATCH | /api/admin/v1/gnb-menus(/{id})(/order) | GNB 메뉴 등록·수정·삭제·순서저장 | DK §27 | §24 | SCR-A-C11 | 2026-11-09 신설. DISPLAY_PAGE·DISPLAY_CATEGORY는 참조 검증, EVENT_PAGE·EXTERNAL_URL은 검증 없음 |
| API-CAT-046-1 | GET | /api/admin/v1/gnb-menus | GNB 메뉴 목록 조회 (admin, 전체) | DK §27 | — | SCR-A-C11 | 2026-11-09 신설 |
| API-CAT-022a | POST | /api/admin/v1/display-pages | 전시 페이지 생성 | DK §13 | §13 | SCR-A-C08 | — → DRAFT |
| API-CAT-022b | POST | /api/admin/v1/display-pages/{id}/publish | 즉시 게시 | DK §13 | §13 | SCR-A-C08 | DRAFT→PUBLISHED |
| API-CAT-022c | PATCH | /api/admin/v1/display-pages/{id} | 제목·섹션·전시기간 수정 (2026-11-09 변경, 舊 schedule/edit-start/republish 통합) | DK §13 | §13 | SCR-A-C08 | 상태 전이 없음 |
| API-CAT-022d | POST | /api/admin/v1/display-pages/{id}/close | 종료 처리 | DK §13 | §13 | SCR-A-C08 | PUBLISHED→CLOSED |
| API-CAT-027 | GET | /api/admin/v1/products | 상품 목록 조회 (admin) | DK §3, §5 | — | SCR-A-C02, SCR-A-C03, SCR-A-C06 | 2026-10-26 TBD-API 해소. summary 필드 2026-11-09 소급 반영 |
| API-CAT-029a | GET | /api/admin/v1/products/{id} | 상품 상세 조회 (admin) | DK §3, §5, §6, §9 | — | SCR-A-C04-T1, T4 | 2026-10-26 TBD-API 해소. summary·tags·옵션값 imageUrl 2026-11-09 소급 반영 |
| API-CAT-030 | GET | /api/admin/v1/display-pages | 전시 페이지 목록 조회 | DK §13 | §13(배치 부분) | SCR-A-C07 | 2026-10-26 TBD-API 해소 |
| API-CAT-030-1 | GET | /api/admin/v1/display-pages/{id} | 전시 페이지 단건 조회 | DK §13 | — | SCR-A-C08 | 2026-10-26 TBD-API 해소 |
| API-CAT-031 | PATCH | /api/admin/v1/display-pages/{id}/set-home | 홈 화면 지정 | DK §15 | §14 | SCR-A-C08 | 2026-10-26 신설. PUBLISHED만 가능 |
| API-CAT-039 | GET | /api/admin/v1/display-categories/{id}/products | 전시카테고리 매핑 상품 목록 조회 | DK §24 | — | SCR-A-C09 | 2026-11-09 신설 (전용 시퀀스 없음) |
| API-CAT-040 | PUT | /api/admin/v1/display-categories/{id}/products/order | 전시카테고리 상품 순서·고정여부 저장 | DK §24 | — | SCR-A-C09 | 2026-11-09 신설 (전용 시퀀스 없음) |

### 2-3. 고객웹 (mobile) API

| PGM-ID | Method | Endpoint | 프로그램명 | 세부UC | 시퀀스 | 호출원 | 상태전이 |
|---|---|---|---|---|---|---|---|
| API-CAT-017 | GET | /api/mobile/v1/products | 상품 목록 조회 | DK §10 | §11 | SCR-M-C01 | 2026-11-09 변경(categoryId→displayCategoryId) |
| API-CAT-018 | GET | /api/mobile/v1/products/search | 상품 검색 | DK §10 | — | SCR-M-C02 | 2026-11-09 변경(categoryId→displayCategoryId). name·tags 매칭(2026-11-09 소급 반영) |
| API-CAT-041 | GET | /api/mobile/v1/display-categories | 전시카테고리 목록 조회(카테고리 메뉴) | DK §10 | — | SCR-M-C01, SCR-M-C02 | 2026-11-09 신설 |
| API-CAT-019 | GET | /api/mobile/v1/products/{id} | 상품 상세 조회 | DK §10, §11 | §12 | SCR-M-C03 | summary·옵션값 imageUrl 2026-11-09 소급 반영 |
| API-CAT-020 | POST | /api/mobile/v1/products/{id}/restock-subscriptions | 재입고 알림 신청 | DK §10 | — | SCR-M-C03 | — → PENDING |
| API-CAT-032 | GET | /api/mobile/v1/home | 홈 화면 조회 | DK §15 | §16 | SCR-M-C04 | 2026-10-26 신설 |
| API-CAT-035 | POST/DELETE | /api/mobile/v1/products/{id}/wishlist | 찜 등록·해제 | DK §20 | §19 | SCR-M-C01, SCR-M-C03 | — (cat_product_wishlist 1건 등록/삭제, 2026-11-09 소급 반영) |
| API-CAT-036 | GET | /api/mobile/v1/me/wishlist | 찜한 상품 목록 조회 | DK §20 | — | SCR-M-C05 | 2026-11-09 소급 반영 (전용 시퀀스 없음) |
| API-CAT-037a | GET | /api/mobile/v1/products/{id}/share | 상품 공유 메타데이터 조회 | DK §21 | §20 | SCR-M-C03 | 2026-11-09 소급 반영 |
| API-CAT-037b | GET | /api/mobile/v1/display-pages/{id}/share | 전시 페이지 공유 메타데이터 조회 | DK §21 | §20 | SCR-M-C07 | 2026-11-09 소급 반영. 호출원 SCR-M-C07 확정(미진항목 #9 해소, 2026-11-09) |
| API-CAT-042 | GET | /api/mobile/v1/products/ranking | 상품 랭킹 조회 (실시간/일간/주간) | DK §26 | §23 | SCR-M-C06 | 2026-11-09 신설. 집계 쓰기는 §22(비동기, 내부 이벤트 재구독이라 별도 API-ID 없음) |
| API-CAT-047 | GET | /api/mobile/v1/gnb-menus | GNB 메뉴 조회 (고객, 홈 전용) | DK §27 | §25 | SCR-M-C04 | 2026-11-09 신설. is_exposed·전시기간 조건 만족 메뉴만 sortOrder ASC |
| API-CAT-048 | GET | /api/mobile/v1/display-pages/{slug} | 비홈 전시 페이지 뷰어 조회 | DK §28 | §26 | SCR-M-C07 | 2026-11-09 신설. §32(홈)와 섹션 resolve 로직 공유, PUBLISHED && is_exposed만 조회 가능 |

### 2-4. 내부 연동 (internal, Service-to-Service) API

| PGM-ID | Method | Endpoint | 프로그램명 | 세부UC | 시퀀스 | 호출원 | 상태전이 |
|---|---|---|---|---|---|---|---|
| API-CAT-014 | POST | /api/internal/v1/skus/{id}/reserve | 재고 차감 (Order 연동) | DK §14 | §7 | Order 도메인 | 조건 충족 시 ON_SALE→SOLD_OUT |
| API-CAT-015 | GET | /api/internal/v1/skus/availability | 재고 확인 (Order 연동) | DK §14 | — | Order 도메인 | — |
| API-CAT-023 | GET | /api/internal/v1/products/{id} | 상품 정보 조회 (Order 연동) | DK §14 | — | Order 도메인 | — |
| API-CAT-024 | GET | /api/internal/v1/products/{id}/vendor-shipping | 판매자 단위 배송 속성 (Order 연동) | DK §14 | — | Order 도메인 | — |
| API-CAT-025 | GET | /api/internal/v1/products/{id}/promotion-grouping | 상품-행사 그룹핑 속성 (Promotion 연동) | DK §14 | — | Promotion 도메인 | — |
| API-CAT-026 | POST | /api/internal/v1/products/{id}/price-schedule | 행사가 스케줄 등록·취소 (Promotion 연동, 동기) | DK §14 | — | Promotion 도메인 | — — 비동기 이벤트(§10)와 동일 로직의 동기 경로 |
| API-CAT-038 | GET | /api/internal/v1/products/{id}/max-order-quantity | 주문 수량 제한 값 조회 (Promotion 연동) | DK §19 | §21 | Promotion 도메인 | — (NULL=무제한, 실제 필터링은 Promotion 수행, 2026-11-09 소급 반영) |

---

## 3. 컨슈머 (CSM)

| PGM-ID | 프로그램명 | 트리거(이벤트) | 발행 도메인 | 수신 도메인 | 세부UC | 시퀀스 | 내부 호출 | 상태전이 |
|---|---|---|---|---|---|---|---|---|
| CSM-CAT-001 | 재고 복원 (주문취소) | ORDER_CANCELLED | Order | Catalog | DK §8 | §8 | StockService.restore | 조건 충족 시 SOLD_OUT→ON_SALE(대안A) |
| CSM-CAT-002 | 재고 복원 (반품·교환확정) | RETURN_EXCHANGE_CONFIRMED | Order | Catalog | DK §8 | §8 | StockService.restore | 조건 충족 시 SOLD_OUT→ON_SALE(대안A) |
| CSM-CAT-003 | 행사가 스케줄 등록 | PROMOTION_PRICE_SCHEDULED | Promotion | Catalog | DK §9 | §10 | PriceScheduleService.registerSchedule | — (cat_product_price_schedule INSERT) |
| CSM-CAT-004 | 행사가 스케줄 취소 | PROMOTION_PRICE_SCHEDULE_CANCELLED | Promotion | Catalog | DK §9 | §10 | PriceScheduleService.cancelSchedule | — (end_at=now) |
| CSM-CAT-005 | 이벤트 배너 동기화 | PROMOTION_EXHIBITION_BANNER_SYNCED | Promotion | Catalog | DK §15 | §15 | EventBannerScheduleService.upsertBanner | — (cat_event_banner_schedule UPSERT) — ⚠️ 미진항목 #4 |
| CSM-CAT-006 | 이벤트 배너 동기화 취소 | PROMOTION_EXHIBITION_BANNER_SYNC_CANCELLED | Promotion | Catalog | DK §15 | §15 | EventBannerScheduleService.cancelBanner | — (end_at=now) — ⚠️ 미진항목 #4 |
| CSM-CAT-007 | 상품 랭킹 집계 (내부 재구독, 2026-11-09 신설) | StockChanged | **Catalog** | Catalog | DK §25 | §22 | ProductSalesRankingListener.onStockChanged | — (cat_product_sales_hourly upsert). 발행 도메인=수신 도메인=Catalog인 유일한 행 — 외부 팀 구현 의존 없음(CSM-CAT-001~006과 달리 Human Review 대상 아님) |
| CSM-CAT-008 | 찜 데이터 정리 (회원 탈퇴, 2026-11-09 소급 반영) | MemberWithdrawn | Member | Catalog | DK §14 | §30(2026-11-09 신설) | MemberEventListener.onMemberWithdrawn → WishlistService.deleteAllByMember | — (cat_product_wishlist 해당 member_id 전체 삭제) — ⚠️ Member 실제 발행 여부 미확인(DBA §6 HR #35, DD HR #10, DI HR #6) |

---

## 4. 배치 (BAT)

| PGM-ID | 프로그램명 | 트리거(스케줄) | EARS 근거 | 세부UC | 시퀀스 | 내부 호출 | 상태전이 |
|---|---|---|---|---|---|---|---|
| BAT-CAT-001 | 재제출 기한 만료 자동 삭제 | 60분 주기 | REQ-CAT-008 | DK §4 | §4 | ProductService.expireOverdueRejectedProducts | REJECTED 상품 자동 삭제 (30일 초과) |
| BAT-CAT-002 | 전시 페이지 자동 게시 | 1분 주기 | REQ-CAT-040 | DK §13 | §13 | DisplayPageService.publishDuePages | DRAFT→PUBLISHED (display_start_at 도달) |
| BAT-CAT-003 | 전시 페이지 자동 종료 | 1분 주기 | REQ-CAT-043 | DK §13 | §13 | DisplayPageService.closeDuePages | PUBLISHED→CLOSED (display_end_at 도달) |

---

## 5. 집계

| 유형 | 건수 |
|---|---|
| 화면 (SCR, 탭 포함) | 31 |
| API | 66 (66건, internal 7건 포함) |
| 컨슈머 (CSM) | 8 |
| 배치 (BAT) | 3 |
| **합계** | **108** |

> 2026-11-09 소급 반영: 복제등록·대량등록·찜하기·SNS공유·주문수량제한 5개 기능(REQ-CAT-056·057·059b·061~063,
> 2026-11-06 DBA/DD 신설 당시 DK·DL에만 반영되고 DQ에는 등재되지 않았던 공백)을 API-CAT-033~038,
> SCR-P-C06·SCR-M-C05로 소급 등록했다. 기존 36건(API)·28건(SCR) 집계도 이번에 발견된 계산 오차
> (전시카테고리 관련 API-CAT-039~041 반영 누락, BAT-CAT-003 미반영)를 함께 정정했다.
>
> 2026-11-09 신설(같은 날 추가): 상품 랭킹(실시간/일간/주간) 기능 — API-CAT-042(조회),
> SCR-M-C06(화면) 추가. 집계 쓰기(StockChanged 내부 재구독, DK §25)는 화면·API가 없는
> 순수 비동기 처리라 SCR/API 집계에는 포함하지 않았다(아래 정합성 검증 #4 참조).
>
> 2026-11-09 신설(같은 날 추가, 상품등록 탭 항목 검토): 옵션값 이미지 등록 — API-CAT-049
> (partner)·050(admin, DL §45, §9·§10과 동일하게 1개 섹션에 admin·partner 2개 번호) 추가.
> 화면(SCR)은 기존 SCR-A-C04-T2·SCR-P-C04 탭 내 기능 추가라 신규 SCR을 만들지 않았다(API만
> +2). 상품 요약·태그(REQ-CAT-079)는 기존 API-CAT-008a/008b(기본정보 수정)·API-CAT-029a/029b
> (상세조회)·API-CAT-027/028(목록조회) 응답·요청 필드 보강이라 API-CAT 신규 번호 없음(건수
> 변화 없음).
>
> 2026-11-09 변경(같은 날 추가, 상품등록 탭 항목 검토 후속): **SCR-A-C04-T6(전시 탭) 폐지** —
> 전시여부·검색노출 제외 토글 2개만으로는 독립 탭을 구성할 근거가 부족하다고 판단(사용자
> 확인)해 탭 자체를 없애고 기본정보 탭(SCR-A-C04-T1)의 API-CAT-008a/008b 필드로 통합했다.
> 화면 수 32→31(-1). 미진항목 #3은 "설계 완료"가 아니라 "대상 자체를 없애는 결정"으로
> 해소됐다. API-CAT 신규 번호 없음(기존 008a/008b 필드 보강).

---

## 6. 정합성 검증 결과

| # | 점검 항목 | 결과 | 상세 |
|---|---|---|---|
| 1 | 인터페이스명세(DL) endpoint → API-CAT-* 대응 | ✅ 66/66 | DL §1~§45(하위번호 §8/§9/§10/§11/§16/§29의 admin·partner variant, §12/§12-1/§22/§35/§37/§42/§42-1 그룹 세분화 포함) 전수 매핑 — API-CAT-043~045(admin 가격변경·이미지·옵션)는 신규 섹션 없이 기존 §9·§10·§16에 병합. API-CAT-049(partner)·050(admin, 옵션값 이미지)은 §45 신설(1개 DL 섹션에 2개 API-CAT 번호, §8/§9/§10과 동일 병합 패턴) |
| 2 | 화면레이아웃(DN) 화면 → SCR-* 대응 | ✅ 31/31 | SCR-A-C04-T6(전시 탭)은 2026-11-09 폐지 결정(체크박스 2개만으로는 독립 탭 근거 부족 — 기본정보 탭에 통합, 미진항목 #3 해소)으로 전체 수에서 제외. SCR-A-C05 브랜드 탭은 와이어프레임 추가로 해소(미진항목 #6), SCR-A-C04-T2(이미지/옵션 탭)는 해소, SCR-A-C11·SCR-M-C07은 완전 설계로 신설 |
| 3 | 세부UC(DK) → 화면·API 역추적 | ✅ | DK §1~§21, §24~§28 전체가 최소 1개 이상의 SCR 또는 API에서 참조됨 |
| 4 | 시퀀스(DM) [API]/[컨슈머]/[배치] → PGM-* 대응 | ✅ 30/30 | DM §1~§30 전체가 PGM-ID로 매핑됨(§3은 API-CAT-004~006 3건, §8·§10·§15는 각 2개 이벤트로 CSM 2건씩, §19는 API-CAT-035 2개 메서드, §22는 CSM-CAT-007, §24는 API-CAT-046, §25는 API-CAT-047, §26은 API-CAT-048, §28은 API-CAT-039~040 2건). §22는 "발행 도메인=수신 도메인=Catalog"인 CSM 행으로 등록(CSM 분류 기준을 "도메인 간"이 아니라 "비동기 처리 여부"로 재정의, 2026-11-09). §27·28·29·30(API-CAT-026·039~040·036, CSM-CAT-008 전용 시퀀스)은 2026-11-09 신설(미진항목 #5·#8·#10 해소) |
| 5 | 모든 API → 호출원(SCR/도메인) 1건 이상 | ✅ 66/66 | API-CAT-026(내부, Promotion 동기 호출)은 DM §27 신설로 호출원이 "Promotion 도메인"으로 확정(2026-11-09, 미진항목 #5 해소) — API-CAT-037b는 SCR-M-C07 신설로 해소, API-CAT-049·050은 각각 SCR-P-C04·SCR-A-C04-T2로 호출원 확정 |
| 6 | 모든 SCR → 호출 API 매핑 존재 | ✅ | 컨테이너(SCR-A-C04, SCR-A-C05)는 자체 API 없음(정상) — 탭에서 호출 |
| 7 | CSM/BAT → 내부 호출(Service 메서드) 매핑 존재 | ✅ | `DP-클래스설계/catalog.md` Service 메서드와 1:1 대응 |
| 8 | Promotion 발행 전제 이벤트의 교차 확인 | ⚠️ 2건 | CSM-CAT-005·006(이벤트 배너 동기화)은 Promotion이 실제로 이벤트를 발행하는지 미확인 상태 — DBA/DF/DI/DM Human Review와 동일 쟁점(미진항목 #4) |

### 미진 항목 (후속 조치)

| # | 항목 | 조치 | 우선순위 |
|---|---|---|---|
| 1 | ~~SCR-A-C04-T2(이미지/옵션 탭) 전용 와이어프레임 미설계~~ | **해소(2026-11-09)** — partner §11(SCR-P-C04) 내용을 기준으로 DN-admin §4에 와이어프레임·화면구성·기능 추가. 동시에 API-CAT-009·010이 partner 경로뿐이고 admin 전용 경로가 없던 공백도 함께 발견해 API-CAT-044·045(admin 전용, 소유자 검증 생략)로 해소(가격 API와 동일한 패턴) | 해소 |
| 2 | ~~SCR-A-C04-T3(가격 탭)이 참조하는 API-CAT-016이 partner 전용 경로(`/api/partner/v1/...`)뿐이고 admin 전용 가격변경 경로가 없음~~ | **해소(2026-11-09)** — `PATCH /api/admin/v1/products/{id}/price`(API-CAT-043) 신설. `cat_product_price_schedule.created_by`가 이미 "vendor_id/admin_id 둘 다 수용"하도록 설계돼 있었던 점을 활용해, `PriceService.changePrice`를 `actorId`+`requireOwnership` 파라미터로 일반화(admin 경로는 소유자 검증 생략) | 해소 |
| 3 | ~~SCR-A-C04-T6(전시 탭) 전체 미설계~~ | **해소(2026-11-09, 탭 폐지)** — "이 상품이 포함된 전시 페이지 목록 역참조 조회" 없이 전시여부·검색노출 제외 토글 2개만 넣는 방안은 독립 탭을 구성할 근거가 부족하다고 판단(사용자 확인)해, 탭을 폐지하고 두 토글을 SCR-A-C04-T1(기본정보 탭)에 통합했다. 역참조 조회 기능은 설계 대상에서 제외 | 해소 |
| 4 | CSM-CAT-005·006(이벤트 배너 동기화)의 Promotion 측 실제 이벤트 발행 여부 | Promotion 담당자 확인 — 기존 Human Review(DF #7·8, DBA #11·12, DD #7, DI #4·5, DM #3, DL #2, ADR-C005) 전체가 이 1건으로 수렴 | 상 |
| 5 | ~~API-CAT-026(Promotion→Catalog 동기 가격스케줄 등록) 전용 시퀀스 부재~~ | **해소(2026-11-09)** — DM-시퀀스/catalog.md §27 신설. §10(비동기 이벤트 수신)과 동일한 `PriceScheduleService` 로직을 동기 호출로 재사용 | 해소 |
| 6 | ~~SCR-A-C05 브랜드 탭 와이어프레임 미설계~~ (전시카테고리 탭은 2026-11-09 SCR-A-C10으로 분리되며 해소) | **해소(2026-11-09)** — DN-화면레이아웃/catalog-admin.md §5에 브랜드 탭 와이어프레임(나이키/아디다스 예시, 로고 placeholder) 추가. API-CAT-012c·012-1c는 기존에 이미 설계돼 있어 추가 API 작업 없음 | 해소 |
| 7 | `cat_display_template` 관리 화면·메뉴 전체 미설계 (2026-10-26 사용자 확인, 보류) | 차후 진행 — DE-메뉴구조도/admin.md 근거 참조 | 보류(사용자 지정) |
| 8 | ~~API-CAT-039·040(전시카테고리 상품순서 저장) 전용 시퀀스 부재~~ (고객 조회 측 API-CAT-017은 2026-11-09 DM §11 갱신으로 해소) | **해소(2026-11-09)** — DM-시퀀스/catalog.md §28 신설(조회·저장 그룹 시퀀스 1건) | 해소 |
| 9 | ~~API-CAT-037b(전시 페이지 공유 메타데이터 조회)의 호출원이 될 고객용 전시 페이지 단건 뷰 화면이 설계돼 있지 않음~~ | **해소(2026-11-09)** — SCR-M-C07(DisplayPageViewPage), API-CAT-048(`GET /api/mobile/v1/display-pages/{slug}`) 신설. §17(홈)의 섹션 resolve 로직을 `HomeQueryService.resolveSections`로 추출해 재사용(DBA §2.15) | 해소 |
| 10 | ~~API-CAT-036(찜한 상품 목록 조회)·API-CAT-033/034(복제·대량등록) 전용 시퀀스 부재~~ | **해소(2026-11-09)** — API-CAT-033·034는 사실 이미 DM §17·§18에 전용 시퀀스가 있어 표기 오류였음(정정). API-CAT-036만 실제 공백이라 DM §29 신설로 메움. CSM-CAT-008 전용 다이어그램 부재도 §30 신설로 함께 해소 | 해소 |
| 11 | ~~DM §22(StockChanged 내부 재구독, 상품 랭킹 집계)에 대응하는 PGM-ID 부재~~ | **해소(2026-11-09)** — 새 카테고리를 만들지 않고, CSM의 정의를 "도메인 간"에서 "비동기 처리 여부"로 재정의해 CSM-CAT-007(발행 도메인=수신 도메인=Catalog)로 등록. CSM-CAT-001~006(외부 도메인 발행, Human Review 대상)과는 "발행 도메인" 컬럼 값으로 구분 — CSM 표를 "발행 도메인≠Catalog"로 필터링하면 기존처럼 외부 팀 확인이 필요한 목록만 그대로 추출됨 | 해소 |
| 12 | ~~CSM-CAT-008(찜 데이터 정리, MemberWithdrawn 수신) PGM-ID 부재~~ | **해소(2026-11-09 소급 반영, 전용 시퀀스도 해소)** — DI·DK §14에만 반영되고 DQ에 등재되지 않았던 공백을 CSM-CAT-008로 메움. 전용 시퀀스(DM)도 §30 신설로 §8·§10·§15와 동일하게 세분화됨(2026-11-09, #10과 함께 해소) | 해소 |
| 13 | ~~GNB 메뉴의 linkType=DISPLAY_PAGE를 클릭해도 이동할 고객 화면이 없음~~ | **해소(2026-11-09)** — #9와 동일 쟁점이라 #9 해소(SCR-M-C07 신설)로 함께 해소됨 | 해소 |

---

## 근거

| 항목 | 출처 |
|---|---|
| 화면 도출 | `deliverables/S3-상세설계/DN-화면레이아웃/catalog-admin.md`(§1~§10)·`catalog-partner.md`(§8~§13)·`catalog-mobile.md`(§13~§20) |
| API 도출 | `deliverables/S3-상세설계/DL-인터페이스명세/catalog.md` §1~§44(하위번호 포함) 전수 |
| 컨슈머 도출 | `deliverables/S2-구조설계/DI-이벤트플로우/catalog.md` 수신 이벤트 6건(도메인 간) + 내부 재구독 1건 |
| 배치 도출 | `deliverables/S2-구조설계/DD-EARS기능요구/catalog.md` REQ-CAT-008(재제출기한), REQ-CAT-040(자동게시), REQ-CAT-043(자동종료) 시간조건 |
| 세부UC 역추적 | `deliverables/S3-상세설계/DK-세부유스케이스/catalog.md` §1~§22, §24~§26 |
| 시퀀스 매핑 | `deliverables/S3-상세설계/DM-시퀀스/catalog.md` §1~§23 |
| 클래스·메서드 대응 | `deliverables/S3-상세설계/DP-클래스설계/catalog.md` |
| ADR 근거 | `deliverables/S3-상세설계/DO-ADR(Catalog).md` ADR-C001~C005 |
| 정합성 규칙 | 작성가이드 '프로그램 목록 정합성 체크리스트' 6항목, `DQ-프로그램목록/order.md`와 동일 패턴 |
| 미진항목 #2·#4 | 본 문서 작성 중 교차검증으로 신규 발견(2026-10-26) |
| 복제등록·대량등록·찜하기·SNS공유·주문수량제한 소급 등록(API-CAT-033~038, SCR-P-C06·SCR-M-C05) | 사용자 지시(2026-11-09) — REQ-CAT-056·057·059b·061~063는 2026-11-06 DBA/DD 신설 당시 DK·DL에만 반영되고 DQ·DJ·DM·DN·DP·DE에는 소급되지 않았던 공백을 메움 |
| 상품 랭킹(실시간/일간/주간) 신설(API-CAT-042, SCR-M-C06) | 사용자 지시(2026-11-09) — REQ-CAT-074~075, DBA §1.17·§2.13 |
| CSM 분류 기준 재정의("도메인 간" → "비동기 처리 여부") 및 CSM-CAT-007(상품 랭킹 집계) 등록 | 사용자 지시(2026-11-09) — 메커니즘(Outbox·`@EventListener`·`ProcessedEventRepository`)이 기존 CSM-CAT-001~006과 동일하므로 새 PGM 카테고리를 만들지 않고 CSM을 확장 |
| CSM-CAT-008(찜 데이터 정리, MemberWithdrawn 수신) 소급 등록 | 사용자 지시(2026-11-09) — DI-이벤트플로우·DK §14에만 반영되고 DQ에는 등재되지 않았던 공백을 메움. DD REQ-CAT-062, DBA §1.14·§6 HR #35 |
| API-CAT-043(admin 전용 가격변경) 신설, 미진항목 #2 해소 | 사용자 지시(2026-11-09) — `cat_product_price_schedule.created_by`가 이미 admin_id를 수용하도록 설계돼 있던 점을 활용, DD REQ-CAT-026 본문 보강 |
| SCR-A-C04-T2(이미지/옵션 탭) 와이어프레임 완성, API-CAT-044·045(admin 전용 이미지·옵션) 신설, 미진항목 #1 해소 | 사용자 지시(2026-11-09) — DN-partner §11 내용을 기준으로 DN-admin §4에 반영하면서, API-CAT-009·010이 partner 경로뿐이던 공백을 가격 API와 동일한 패턴으로 해소 |
| GNB 메뉴 관리 신설(API-CAT-046·046-1·047, SCR-A-C11) | 사용자 지시(2026-11-09) — REQ-CAT-076~077, DBA §2.14. 미진항목 #9(전시 페이지 뷰어 비홈) 논의에서 진입 경로 보완 필요성으로 도출, DISPLAY_PAGE 유형은 #9에 종속(미진항목 #13) |
| 비홈 전시 페이지 뷰어 신설(API-CAT-048, SCR-M-C07), 미진항목 #9·#13 해소 | 사용자 지시(2026-11-09) — REQ-CAT-078, DBA §2.15. §17(홈)과 섹션 resolve 로직 완전 재사용(사용자 확인: "템플릿으로 노출하는 전시페이지는 동일한 구조로 처리") |
| SCR-A-C05 브랜드 탭 와이어프레임 추가, 미진항목 #6 해소 | 사용자 지시(2026-11-09) — API-CAT-012c·012-1c는 기존 설계를 그대로 참조, 신규 API 없음. DN-화면레이아웃/catalog-admin.md §5 |
| 상품 요약(summary)·태그(tags) 소급 반영 (API-CAT-008a/008b·017·018·019·027·028·029a/029b 필드 보강) | 사용자 지시(2026-11-09, 상품등록 탭 항목 검토) — DBA §1.3.1·§1.3.3·§1.3.4에 이미 있던 정책이 DF ERD·DQ에 반영되지 않았던 공백. REQ-CAT-056·063이 이미 이 필드를 전제로 작성돼 있었음. DD REQ-CAT-079, AC-CAT-105~106 |
| 옵션값 이미지 등록 신설 (API-CAT-049 partner·050 admin, DL §45) | 사용자 지시(2026-11-09, 상품등록 탭 항목 검토) — 색상 등 1단계 옵션값에 스와치 이미지 지원. DD REQ-CAT-080~081, DBA §1.4.1(신설), AC-CAT-107~108 |
| SCR-A-C04-T6(전시 탭) 폐지, 전시여부(isExposed)·검색노출제외(isSearchExcluded)를 기본정보 탭(API-CAT-008a/008b)에 통합, 미진항목 #3 해소 | 사용자 지시(2026-11-09) — "역참조 조회 없이 토글 2개만 넣으면 탭 의미가 없다"는 사용자 판단에 동의해 탭 자체를 없애는 쪽으로 결정. DD REQ-CAT-082~083, DBA §2.16(신설), AC-CAT-109~110. 화면 수 32→31 |
| DM 전용 시퀀스 4건 신설(§27 API-CAT-026, §28 API-CAT-039~040, §29 API-CAT-036, §30 CSM-CAT-008), 미진항목 #5·#8·#10 해소 | 사용자 지시(2026-11-09) — 미진항목 #10 검토 중 API-CAT-033·034는 이미 DM §17·§18에 시퀀스가 있던 표기 오류였음을 함께 발견·정정. DM 정합성검증 행 4(26/26→30/30)·행 5(65/66→66/66 ✅) 갱신 |
