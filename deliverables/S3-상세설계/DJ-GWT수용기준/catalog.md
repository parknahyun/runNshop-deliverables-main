# GWT 수용기준 — Catalog 도메인

> 상위 문서: [readme.md](readme.md)
> **단계**: 상세설계 (S3) | **문서범위**: Bolt (Catalog) | **문서종류**: Spec

---

## ID 규칙

```
AC-{DOMAIN}-{SEQ}
```
- AC: Acceptance Criteria
- DOMAIN: CAT(상품)
- SEQ: 3자리 순번

---

## 1. 상품등록·심사 Bolt (직매입)

| ID | 카테고리 | 대응 EARS | Given | When | Then |
|---|---|---|---|---|---|
| AC-CAT-001 | 정상 | REQ-CAT-001 | 관리자(MD, 직매입등록자)가 상품 정보(name·category·price_original/sale/supply·이미지)를 모두 입력했다 | 등록 완료를 클릭한다 | `is_direct_sourced=TRUE`로 상품이 생성되고, 심사 게이트 없이 상태가 즉시 DRAFT→ON_SALE로 전환된다 |
| AC-CAT-002 | 예외 | REQ-CAT-001 | 관리자(MD, 직매입등록자)가 필수 필드(price_original 등) 중 하나를 비워뒀다 | 등록 완료를 클릭한다 | "필수 항목을 입력해주세요" 반환, ON_SALE 전환 거부 |

---

## 2. 상품등록·심사 Bolt (입점형)

| ID | 카테고리 | 대응 EARS | Given | When | Then |
|---|---|---|---|---|---|
| AC-CAT-003 | 정상 | REQ-CAT-002 | 판매자가 상품 정보를 입력 중이다 | 임시저장을 클릭한다 | `is_direct_sourced=FALSE` 상품이 DRAFT 상태로 생성된다 |
| AC-CAT-004 | 정상 | REQ-CAT-003 | 판매자의 상품이 DRAFT 상태이고 필수 필드(name·category_id·price_original/sale/supply·이미지 1장 이상)가 모두 채워졌다 | 판매자가 심사 요청을 클릭한다 | 상태가 DRAFT→REVIEW_REQUESTED로 전환되고 ProductCreated 이벤트가 발행된다 |
| AC-CAT-005 | 예외 | REQ-CAT-003 | 판매자의 상품이 DRAFT 상태이고 이미지가 0장이다 | 판매자가 심사 요청을 클릭한다 | "이미지를 1장 이상 등록해주세요" 반환, REVIEW_REQUESTED 전환 거부 |
| AC-CAT-006 | 정상 | REQ-CAT-004 | 상품이 REVIEW_REQUESTED 상태이다 | 관리자(MD, 심사자)가 심사 착수를 클릭한다 | 상태가 REVIEW_REQUESTED→UNDER_REVIEW로 전환되고 심사 담당자가 할당된다 |
| AC-CAT-007 | 정상 | REQ-CAT-005 | 상품이 UNDER_REVIEW 상태이고 적합 판정을 받았다 | 관리자(MD, 심사자)가 승인을 클릭한다 | 상태가 UNDER_REVIEW→ON_SALE로 전환되고 ProductApproved 이벤트가 발행된다 |
| AC-CAT-008 | 정상 | REQ-CAT-006 | 상품이 UNDER_REVIEW 상태이고 부적합 판정을 받았다 | 관리자(MD, 심사자)가 반려 사유를 입력하고 반려를 클릭한다 | 상태가 UNDER_REVIEW→REJECTED로 전환되고 reject_reason이 판매자 BO에 기록·노출된다 |
| AC-CAT-009 | 예외 | REQ-CAT-006 | 상품이 UNDER_REVIEW 상태이다 | 관리자(MD, 심사자)가 반려 사유 없이 반려를 클릭한다 | "반려 사유를 입력해주세요" 반환, REJECTED 전환 거부 |
| AC-CAT-010 | 정상 | REQ-CAT-007 | 상품이 REJECTED 상태이고 반려일로부터 10일이 경과했다 | 판매자가 상품을 수정하고 재제출한다 | 상태가 REJECTED→DRAFT로 전환된다 (30일 이내이므로 허용) |
| AC-CAT-011 | 경계값 | REQ-CAT-008 | 상품이 REJECTED 상태이고 반려일로부터 정확히 30일이 경과했다 | 배치가 재제출 기한을 점검한다 | 아직 DRAFT로 전환되지 않았다면 상품이 자동 삭제된다 (30일 경계 포함 처리) |
| AC-CAT-012 | 예외 | REQ-CAT-008 | 상품이 REJECTED 상태이고 반려일로부터 31일이 경과했으며 재제출되지 않았다 | 배치가 실행된다 | 해당 상품이 자동 삭제된다 |
| AC-CAT-013 | 정상 | REQ-CAT-009 | 동일 상품이 동일 사유로 2회 반려된 상태에서 판매자가 재제출했다 | 관리자(MD, 심사자)가 같은 사유로 3번째 반려를 확정한다 | reject_count=3이 되며 해당 상품이 입점 심사팀 에스컬레이션 대상으로 표시된다 |
| AC-CAT-069 | 정상 | REQ-CAT-056 | 판매자 A가 등록한 ON_SALE 상품 1건이 있다 | 판매자 A가 해당 상품의 복제를 요청한다 | 가격·재고·판매자상품코드를 제외한 전체 항목이 복사된 신규 DRAFT 상품(신규 productId·skuId 발급, 이미지는 원본 파일 참조)이 생성된다 (2026-11-09 소급 반영) |
| AC-CAT-070 | 예외 | REQ-CAT-056 | 상품이 판매자 B 소유다 | 판매자 A가 그 상품의 복제를 요청한다 | 403 FORBIDDEN이 반환되고 복제가 수행되지 않는다 (2026-11-09 소급 반영) |
| AC-CAT-071 | 정상 | REQ-CAT-057 | 판매자가 20행짜리 엑셀 양식(기본정보+옵션)을 업로드했고, 그중 18행은 유효하고 2행은 필수 필드가 누락됐다 | 대량등록을 요청한다 | 18건은 DRAFT 상품으로 생성되고, 2건은 실패 사유(행 번호 포함)와 함께 결과에 포함된다 (부분 성공 허용, 2026-11-09 소급 반영) |

---

## 3. 상품정보관리 Bolt

| ID | 카테고리 | 대응 EARS | Given | When | Then |
|---|---|---|---|---|---|
| AC-CAT-014 | 정상 | REQ-CAT-010 | 판매자의 상품이 존재한다 | 판매자가 이름·카테고리·가격·출시일 등 기본정보를 수정하고 저장한다 | 변경 사항이 저장되고 ProductUpdated 이벤트가 발행된다 |
| AC-CAT-015 | 정상 | REQ-CAT-011 | 상품에 이미지가 3장 등록돼 있다 | 판매자가 신규 이미지를 추가한다 | cat_product_image에 저장되고 sort_order가 부여되어 4번째로 추가된다 |
| AC-CAT-016 | 경계값 | REQ-CAT-012 | 상품에 이미지가 9장 등록돼 있다 | 판매자가 10번째 이미지를 추가한다 | 정상 추가된다 (최대 10장 허용) |
| AC-CAT-017 | 예외 | REQ-CAT-012 | 상품에 이미지가 10장 등록돼 있다 | 판매자가 11번째 이미지를 추가한다 | "이미지는 최대 10장까지 등록 가능합니다" 반환, 추가 거부 |
| AC-CAT-018 | 정상 | REQ-CAT-013 | 판매자가 옵션그룹(색상)·옵션값(Red, Blue)을 설정했다 | 옵션 조합을 저장한다 | 각 옵션값 조합별로 SKU가 자동 생성된다 |
| AC-CAT-019 | 경계값 | REQ-CAT-014 | 옵션그룹이 2단계(색상·사이즈)로 설정돼 있다 | 판매자가 3번째 옵션그룹(소재)을 추가하려 한다 | "옵션은 최대 2단계까지 설정 가능합니다" 반환, 추가 거부 |
| AC-CAT-020 | 정상 | REQ-CAT-015 | 상품이 ON_SALE 상태이다 (재고 보유 중) | 판매자가 단종 처리를 클릭한다 | 재고 수량과 무관하게 상태가 ON_SALE→DISCONTINUED로 전환된다 |
| AC-CAT-021 | 정상 | REQ-CAT-015 | 상품이 SOLD_OUT 상태이다 | 관리자(MD, 운영자)가 단종 처리를 클릭한다 | 상태가 SOLD_OUT→DISCONTINUED로 전환된다 |
| AC-CAT-085 | 정상 | REQ-CAT-070 | 상품이 "신발" 대분류에 속하고 상품 상세가 노출 중이다 | 고객이 상품 상세를 조회한다 | 해당 대분류의 법정 상품정보제공고시 항목이 이미지·설명과 구분된 별도 섹션으로 노출된다 (2026-11-09 소급 반영, 법무 확인 전 참고용 기준) |
| AC-CAT-105 | 예외 | REQ-CAT-079 | 판매자가 상품 요약을 201자로 입력했다 | 저장을 시도한다 | 400 SUMMARY_LENGTH_EXCEEDED가 반환되고 저장되지 않는다 (2026-11-09 신설) |
| AC-CAT-106 | 예외 | REQ-CAT-079 | 상품에 태그가 10개 등록돼 있다 | 판매자가 11번째 태그를 추가하고 저장한다 | 422 TAG_LIMIT_EXCEEDED가 반환되고 저장되지 않는다 (2026-11-09 신설) |
| AC-CAT-107 | 정상 | REQ-CAT-080 | 옵션그룹 "색상"(depth=1)에 옵션값 Red가 있다 | 판매자가 Red 옵션값에 이미지를 업로드한다 | `cat_product_option_value.image_url`에 저장되고, 상품 상세 조회 시 해당 옵션값에 imageUrl이 포함된다 (2026-11-09 신설) |
| AC-CAT-108 | 예외 | REQ-CAT-081 | 옵션그룹 "사이즈"(depth=2)에 옵션값 260이 있다 | 판매자가 260 옵션값에 이미지를 업로드한다 | 422 OPTION_IMAGE_DEPTH_INVALID가 반환되고 저장되지 않는다 (2026-11-09 신설) |
| AC-CAT-109 | 정상 | REQ-CAT-082 | 상품이 ON_SALE 상태이고 재고가 있다 | 관리자(MD)가 전시여부(is_exposed)를 FALSE로 전환한다 | 상태·재고는 그대로 유지되고, 고객용 목록·검색·전시 영역·상세 페이지 딥링크 전부에서 즉시 제외된다 (2026-11-09 신설) |
| AC-CAT-110 | 정상 | REQ-CAT-083 | 상품이 is_exposed=TRUE로 정상 노출 중이다 | 판매자가 검색노출 제외(is_search_excluded)를 TRUE로 설정한다 | 상품 목록·카테고리·상세는 그대로 노출되고 검색 결과에서만 제외된다 (2026-11-09 신설) |

---

## 4. 분류체계관리 Bolt

| ID | 카테고리 | 대응 EARS | Given | When | Then |
|---|---|---|---|---|---|
| AC-CAT-022 | 정상 | REQ-CAT-016 | 표준 카테고리 목록이 존재한다 | 관리자(MD, 운영자)가 신규 대분류를 생성한다 | cat_category에 신규 행이 추가된다 (단일계층, 상위 카테고리 없음) |
| AC-CAT-023 | 정상 | REQ-CAT-017 | 상품이 이미 카테고리A에 귀속돼 있다 | 판매자가 카테고리B로 변경을 시도한다 | 기존 카테고리A 귀속이 해제되고 카테고리B 1개로만 교체된다 (다중 카테고리 불가) |
| AC-CAT-024 | 정상 | REQ-CAT-018 | 전시 카테고리 목록이 존재한다 | 관리자(MD, 운영자)가 신규 전시 카테고리를 생성한다 | cat_display_category 트리에 신규 노드가 추가된다 |
| AC-CAT-025 | 정상 | REQ-CAT-019 | 브랜드 마스터가 존재한다 | 관리자(MD, 운영자)가 신규 브랜드를 등록한다 | cat_brand에 신규 행이 추가된다 |

---

## 5. 재고관리 Bolt

| ID | 카테고리 | 대응 EARS | Given | When | Then |
|---|---|---|---|---|---|
| AC-CAT-026 | 정상 | REQ-CAT-020 | SKU의 stock_quantity가 10이다 | 판매자가 수량을 15로 변경한다 | stock_quantity·available_quantity가 갱신되고 cat_stock_history에 기록된다 |
| AC-CAT-027 | 경계값 | REQ-CAT-021 | SKU의 available_quantity가 1이다 | 고객 주문으로 1개가 차감된다 | available_quantity가 0이 되고 상품 상태가 ON_SALE→SOLD_OUT으로 자동 전환된다 |
| AC-CAT-028 | 정상 | REQ-CAT-022 | SKU가 SOLD_OUT 상태이고 주문 취소로 재고가 1 복원된다 | 재고 복원 처리가 완료된다 | 발생 원인(주문취소) 무관하게 관리자(MD) 확인 없이 상태가 SOLD_OUT→ON_SALE로 자동 전환된다 |
| AC-CAT-029 | 정상 | REQ-CAT-022 | SKU가 SOLD_OUT 상태이고 판매자가 재고를 신규로 +5 등록한다 | 재고 등록이 완료된다 | MD 확인 없이 상태가 SOLD_OUT→ON_SALE로 자동 전환된다 (판매자 재고 신규등록도 동일 처리) |
| AC-CAT-030 | 예외 | REQ-CAT-023 | SKU의 available_quantity가 3이다 | Order 도메인이 5개 차감을 요청한다 | 차감이 거부되고 INSUFFICIENT_STOCK 응답이 반환된다 (재고 변동 없음) |
| AC-CAT-031 | 경계값 | REQ-CAT-023 | SKU의 available_quantity가 정확히 3이다 | Order 도메인이 3개 차감을 요청한다 | 차감이 성공하고 available_quantity가 0이 된다 (요청수량=가용재고는 허용) |
| AC-CAT-032 | 정상 | REQ-CAT-024 | SKU에 재고 변동이 발생한다 (차감이든 복원이든 신규등록이든) | 변동이 처리된다 | cat_stock_history에 변동사유(change_type)·수량·시점이 함께 기록된다 |
| AC-CAT-033 | 정상 | REQ-CAT-025 | SKU의 재고가 변동된다 | 변동이 커밋된다 | StockChanged 이벤트가 발행된다 |
| AC-CAT-078 | 정상 | REQ-CAT-074 | 상품 A의 재고가 주문 발생(RESERVE)으로 차감돼 StockChanged가 발행된다 | `ProductSalesRankingListener`가 이벤트를 비동기 수신한다 | 이벤트 처리 시각을 시간 단위로 truncate한 `cat_product_sales_hourly(productId, saleHour)` 행의 quantity가 증가한다 (2026-11-09 신설) |
| AC-CAT-079 | 정상 | REQ-CAT-074 | 상품 A가 조금 전 판매로 집계됐고, 같은 날 주문취소(RESTORE_ORDER_CANCEL)가 발생한다 | 리스너가 해당 StockChanged를 수신한다 | 이벤트 처리 시각 기준 시간 버킷의 quantity가 감소한다 (원 판매일이 아니라 취소가 발생한 시각의 버킷에서 차감, 2026-11-09 신설) |
| AC-CAT-080 | 예외 | REQ-CAT-074 | 반품(RESTORE_RETURN_EXCHANGE) 또는 판매자 재고 신규등록(RESTOCK_VENDOR)으로 StockChanged가 발행된다 | 리스너가 이벤트를 수신한다 | `cat_product_sales_hourly`에 아무 변화가 없다 (집계 제외, 2026-11-09 신설) |
| AC-CAT-081 | 경계값 | REQ-CAT-074 | 동일한 eventId의 StockChanged가 네트워크 재시도로 2번 전달된다 | 리스너가 두 번 모두 수신한다 | `ProcessedEventRepository` 멱등 검증으로 두 번째 수신은 무시되어 quantity가 1번만 반영된다 (2026-11-09 신설) |
| AC-CAT-086 | 정상 | REQ-CAT-058 | 상품에 속한 SKU 중 하나의 available_quantity가 재고 임박 기준수량(기본값 5) 이하로 떨어진다 | 재고 변동이 처리된다 | 담당자(입점형=해당 판매자, 직매입=공통 관리자)에게 상품 단위로 임박 알림이 발송된다 (2026-11-09 소급 반영) |
| AC-CAT-087 | 예외 | REQ-CAT-059 | 상품이 이미 재고 임박 상태이고 알림이 발송된 적 있다 | 같은 상품의 재고가 임박 기준 이하로 다시 변동된다(여전히 기준 이하 유지) | 중복 알림이 발송되지 않는다 (2026-11-09 소급 반영) |
| AC-CAT-088 | 경계값 | REQ-CAT-059 | 상품의 재고 임박 상태가 해소(기준수량 초과로 회복)된 뒤 다시 기준수량 이하로 떨어진다 | 재고가 재차 임박 상태가 된다 | 알림이 다시 발송된다 (최초 임박과 동일하게 처리, 2026-11-09 소급 반영) |

---

## 6. 가격관리 Bolt

| ID | 카테고리 | 대응 EARS | Given | When | Then |
|---|---|---|---|---|---|
| AC-CAT-034 | 정상 | REQ-CAT-026 | 상품의 가격 필드가 설정돼 있다 | 판매자가 판매가를 변경한다 | 변경 전후 가격이 cat_price_history에 기록된다 |
| AC-CAT-035 | 예외 | REQ-CAT-027 | 판매자가 price_original=10000, price_sale=12000으로 입력한다 (판매가가 정가보다 높음) | 저장을 시도한다 | "정가는 판매가 이상이어야 합니다" 반환, 설정이 거부된다 |
| AC-CAT-036 | 경계값 | REQ-CAT-027 | 판매자가 price_original=price_sale=price_supply=10000으로 입력한다 (3값이 모두 동일) | 저장을 시도한다 | 정상 저장된다 (≥ 조건은 등호 포함이므로 허용) |
| AC-CAT-037 | 정상 | REQ-CAT-028 | 상품의 price_original=10000, price_sale=8000이다 | 고객이 상품을 조회한다 | 20% 할인율이 함께 표시된다 |
| AC-CAT-076 | 정상 | REQ-CAT-059b | 판매자가 상품의 max_order_quantity를 5로 설정한다 | Promotion 도메인이 해당 상품의 주문 수량 제한 값을 조회한다 | 5가 반환된다 (1회 주문 초과 거부 검증 자체는 Order 도메인이 수행, 2026-11-09 소급 반영) |
| AC-CAT-077 | 정상 | REQ-CAT-059b | 상품의 max_order_quantity가 설정되지 않아 NULL이다 | Promotion/Order가 해당 값을 조회한다 | NULL(무제한)이 반환된다 (2026-11-09 소급 반영) |
| AC-CAT-096 | 정상 | REQ-CAT-026 | 판매자B가 등록한 상품이 있다 | 관리자(MD, 운영자)가 해당 상품의 가격을 수정한다 | 본인 소유 여부와 무관하게 정상 처리되고(소유자 검증 생략), `cat_product_price_schedule`에 `created_by=adminId`인 신규 BASE 행이 추가된다 (2026-11-09 신설, API-CAT-043) |

---

## 7. 고객조회 Bolt

| ID | 카테고리 | 대응 EARS | Given | When | Then |
|---|---|---|---|---|---|
| AC-CAT-038 | 정상 | REQ-CAT-029 | 전시 카테고리에 ON_SALE 상품 3건, DRAFT 상품 1건, DISCONTINUED 상품 1건이 매핑돼 있다 | 고객이 해당 전시 카테고리 목록을 조회한다 (2026-11-09 변경, 舊 표준 카테고리) | ON_SALE 3건만 반환된다 (DRAFT·DISCONTINUED는 제외) |
| AC-CAT-039 | 정상 | REQ-CAT-029 | 상품이 SOLD_OUT 상태이다 | 고객이 전시 카테고리 목록을 조회한다 | 해당 상품이 결과에 포함된다 (SOLD_OUT도 노출 대상) |
| AC-CAT-040 | 정상 | REQ-CAT-030 | 상품이 ON_SALE 상태이고 이미지 3장·옵션 2종·SKU 4개를 가진다 | 고객이 상품 상세를 조회한다 | 기본정보·이미지·옵션·SKU별 가용재고가 모두 반환된다 |
| AC-CAT-041 | 정상 | REQ-CAT-031 | 상품이 전시 카테고리A, 브랜드B, 가격대 5~10만원에 속한다 | 고객이 전시카테고리A+브랜드B+가격필터로 검색한다 | 조건을 모두 만족하는 상품만 반환된다 |
| AC-CAT-042 | 정상 | REQ-CAT-032 | 고객이 SOLD_OUT 상품에 재입고 알림을 신청했다 | 해당 SKU가 재고 복원으로 SOLD_OUT→ON_SALE 전환된다 | cat_restock_subscription의 PENDING 건이 NOTIFIED로 전환되며 알림이 발송된다 |
| AC-CAT-072 | 정상 | REQ-CAT-061 | 로그인한 고객이 ON_SALE 상품을 아직 찜하지 않았다 | 해당 상품에 찜하기를 클릭한다 | cat_product_wishlist에 (product_id, member_id) 1건이 생성되고, 상품 목록·상세·마이페이지 찜 목록에 반영된다 (2026-11-09 소급 반영) |
| AC-CAT-073 | 예외 | REQ-CAT-061 | 고객이 비로그인 상태다 | 상품 상세에서 찜하기를 클릭한다 | 401 UNAUTHORIZED가 반환되고 로그인 화면으로 유도된다 (2026-11-09 소급 반영) |
| AC-CAT-074 | 정상 | REQ-CAT-062 | 상품에 찜한 회원이 3명 있고 상품 상태가 ON_SALE이다 | 상품 상태가 SOLD_OUT 또는 DISCONTINUED로 전환된다 | 해당 product_id의 cat_product_wishlist 행 3건이 즉시 삭제되고, 이후 재입고돼도 복원되지 않는다 (2026-11-09 소급 반영) |
| AC-CAT-075 | 정상 | REQ-CAT-063 | 상품 상세 페이지가 노출 중이다 | 고객이 공유 버튼을 클릭한다 | canonical 공유 URL·제목·대표 이미지·요약 설명이 반환된다 (리워드 없음, 2026-11-09 소급 반영) |

---

## 8. 노출로직 Bolt

| ID | 카테고리 | 대응 EARS | Given | When | Then |
|---|---|---|---|---|---|
| AC-CAT-043 | 정상 | REQ-CAT-033 | 상품이 ON_SALE 상태이고 release_date가 내일(now보다 미래)로 설정돼 있다 | 고객이 상품 목록을 조회한다 | 해당 상품이 목록·검색·전시 결과에서 제외된다 |
| AC-CAT-044 | 경계값 | REQ-CAT-033 | 상품의 release_date가 정확히 현재 시각(now)과 같다 | 고객이 상품 목록을 조회한다 | 해당 상품이 노출 대상에 포함된다 (release_date > now만 제외, 등호는 노출) |
| AC-CAT-045 | 정상 | REQ-CAT-034 | 상품의 release_date가 NULL이다 | 고객이 상품 목록을 조회한다 | 즉시 노출된다 (출시일 필터 미적용, 하위호환) |
| AC-CAT-046 | 정상 | REQ-CAT-035 | 고객이 비로그인 상태로 상품상세를 조회한다 (그룹B) | 화면이 할인가 노출 정보를 요청한다 | 정가·행사가·전체대상쿠폰만 반환되고 회원등급할인·조건만족쿠폰은 제외된다 |
| AC-CAT-047 | 정상 | REQ-CAT-035 | 고객이 로그인 상태로 장바구니를 조회한다 (그룹C) | 화면이 할인가 노출 정보를 요청한다 | 정가·행사가·전체대상쿠폰·회원등급할인·조건만족쿠폰·장바구니할인까지 반환된다 (포인트사용만 제외) |
| AC-CAT-048 | 정상 | REQ-CAT-036 | 고객이 상품 목록에서 연관상품 추천 위젯을 조회한다 | 외부 추천 SaaS에 요청이 전달된다 | SaaS가 반환한 추천 상품이 위젯에 제공된다 |
| AC-CAT-049 | 정상 | REQ-CAT-037 | 상품A에 exposure_md_override=1이 설정되고, 상품B의 ai_score가 상품A보다 높다 | 상품 목록 노출 순서를 산정한다 | 상품A가 상품B보다 먼저 노출된다 (MD 수동 설정값이 AI 점수보다 항상 우선) |
| AC-CAT-050 | 정상 | REQ-CAT-037 | 상품C는 exposure_md_override·ai_score 모두 NULL이다 | 노출 순서를 산정한다 | default_order(예: 최신 등록순) 기준으로 노출된다 |
| AC-CAT-066 | 정상 | REQ-CAT-071 | 전시 카테고리에 상품 3건이 매핑돼 있다 | 관리자가 드래그앤드랍으로 순서를 [C, A, B]로 바꾸고 저장한다 | sort_order가 C=0, A=1, B=2로 저장된다 (2026-11-09 신설) |
| AC-CAT-067 | 정상 | REQ-CAT-072 | 전시 카테고리에 상단고정 상품 1건(sort_order=2)과 비고정 상품 2건(sort_order=0, 1)이 매핑돼 있다 | 해당 전시 카테고리의 상품 목록을 조회한다 | 고정 상품이 sort_order와 무관하게 맨 먼저 노출되고, 나머지는 sort_order 순으로 이어진다 (2026-11-09 신설) |
| AC-CAT-068 | 정상 | REQ-CAT-073 | 전시 카테고리 트리에 활성 노드 5건, 비활성 노드 1건이 있다 | 고객이 카테고리 메뉴에 진입한다 | 활성 노드 5건만 트리 구조로 반환된다 (2026-11-09 신설) |
| AC-CAT-082 | 정상 | REQ-CAT-075 | 상품 A가 오늘 00:00 이후 `cat_product_sales_hourly`에 여러 시간 버킷으로 집계돼 있다 | 고객이 "일간" 랭킹을 조회한다 | 오늘 00:00~현재까지의 버킷 합산값 기준으로 상품들이 내림차순 정렬돼 반환된다 (2026-11-09 신설) |
| AC-CAT-083 | 정상 | REQ-CAT-075 | 전시 카테고리 X에 매핑된 상품과 매핑되지 않은 상품이 모두 랭킹 집계 데이터를 가진다 | 고객이 전시 카테고리 X로 필터링해 랭킹을 조회한다 | 카테고리 X에 매핑된 상품만 랭킹 결과에 포함된다 (2026-11-09 신설) |
| AC-CAT-084 | 경계값 | REQ-CAT-075 | 신규 오픈한 상품이라 `cat_product_sales_hourly`에 해당 상품의 집계 행이 전혀 없다 | 고객이 랭킹을 조회한다 | 해당 상품은 랭킹 결과에 나타나지 않는다 (별도 신상품 보정 가중치 없음, 2026-11-09 신설) |
| AC-CAT-089 | 정상 | REQ-CAT-064 | 상품의 release_date(또는 등록일)가 10일 전이다 | 고객이 상품을 조회한다 | NEW 뱃지가 노출된다 (14일 이내, 2026-11-09 소급 반영) |
| AC-CAT-090 | 정상 | REQ-CAT-065 | 상품이 소속 카테고리에서 sales_rank 상위 10위 이내이다 | 고객이 상품을 조회한다 | BEST 뱃지가 노출된다 (2026-11-09 소급 반영) |
| AC-CAT-091 | 정상 | REQ-CAT-066 | 상품이 NEW 조건(14일 이내)과 품절임박 조건(재고≤기준수량)을 동시에 만족한다 | 고객이 상품을 조회한다 | NEW·품절임박 뱃지가 모두 노출된다 (복수 뱃지 동시 노출, 2026-11-09 소급 반영) |
| AC-CAT-092 | 예외 | REQ-CAT-067 | 외부 추천 SaaS 응답이 지연되거나 실패한다 | 고객이 연관상품 추천 위젯을 조회한다 | 위젯이 숨겨지지 않고 sales_rank 상위 20개 상품(기본값)으로 대체 노출된다 (2026-11-09 소급 반영) |

---

## 9. 화면관리(Display) Bolt

| ID | 카테고리 | 대응 EARS | Given | When | Then |
|---|---|---|---|---|---|
| AC-CAT-051 | 정상 | REQ-CAT-038 | 관리자(MD, 운영자)가 전시 페이지 작성을 시작한다 | 페이지를 생성한다 | 페이지가 DRAFT 상태로 생성된다 |
| AC-CAT-052 | 정상 | REQ-CAT-039 | 전시 페이지가 DRAFT 상태이고 섹션이 1개 이상 구성돼 있다 | 관리자(MD, 운영자)가 게시를 클릭한다 | 상태가 DRAFT→PUBLISHED로 전환되고 published_at이 기록된다 |
| AC-CAT-053 | 정상 | REQ-CAT-040 | 전시 페이지가 DRAFT 상태이고 display_start_at이 현재 시각에 도달했다 | 배치가 실행된다 | 상태가 DRAFT→PUBLISHED로 자동 전환되고 published_at이 기록된다 |
| AC-CAT-054 | 정상 | REQ-CAT-041 | 전시 페이지가 PUBLISHED 상태이다 | 관리자(MD, 운영자)가 섹션 구성을 수정하고 저장한다 | 상태 전이 없이 즉시 반영된다 (별도 임시본 없음) |
| AC-CAT-055 | 경계값 | REQ-CAT-042 | 관리자(MD, 운영자)가 display_end_at을 display_start_at보다 이전 시각으로 설정하려 한다 | 저장을 시도한다 | "종료일시는 시작일시보다 이후여야 합니다" 반환, 설정이 거부된다 |
| AC-CAT-056 | 정상 | REQ-CAT-043 | 전시 페이지가 PUBLISHED 상태이고 display_end_at이 현재 시각에 도달했다 | 배치가 실행된다 | 상태가 PUBLISHED→CLOSED로 전환된다 |
| AC-CAT-057 | 정상 | REQ-CAT-043 | 전시 페이지가 PUBLISHED 상태이다 | 관리자(MD, 운영자)가 종료 처리를 클릭한다 | 상태가 PUBLISHED→CLOSED로 전환된다 (수동 종료) |
| AC-CAT-093 | 정상 | REQ-CAT-068 | PUBLISHED 상태의 전시 페이지가 정상 노출 중이다 | 운영자가 전시여부(is_exposed)를 N으로 전환한다 | 상태 전이·예약·홈 지정은 그대로 두고, 해당 페이지가 노출 쿼리에서만 즉시 제외된다. Y로 되돌리면 즉시 복원된다 (2026-11-09 소급 반영) |
| AC-CAT-094 | 경계값 | REQ-CAT-068 | 홈으로 지정된(is_home=TRUE) 전시 페이지가 is_exposed=N으로 전환된다 | 고객이 홈 화면(mobile "/")에 진입한다 | "홈 미지정" 상태와 동일하게 처리되어 기본 카테고리 화면으로 대체 노출된다 (2026-11-09 소급 반영) |
| AC-CAT-095 | 정상 | REQ-CAT-069 | 전시 페이지에 섹션 3개가 구성돼 있고 그중 1개(PRODUCT_LIST)에 콘텐츠가 등록되지 않았다 | 고객이 해당 전시 페이지를 조회한다 | 콘텐츠 없는 섹션은 생략(skip)되고 나머지 2개 섹션만 정상 노출된다 (2026-11-09 소급 반영) |
| AC-CAT-097 | 정상 | REQ-CAT-076 | 존재하는 전시 페이지 slug가 있다 | 관리자가 linkType=DISPLAY_PAGE, linkTarget=해당 slug로 GNB 메뉴를 등록한다 | `cat_gnb_menu`에 신규 행이 저장된다 (2026-11-09 신설) |
| AC-CAT-098 | 예외 | REQ-CAT-076 | 존재하지 않는 slug다 | 관리자가 linkType=DISPLAY_PAGE로 GNB 메뉴를 등록한다 | 404 DISPLAY_PAGE_NOT_FOUND가 반환되고 저장이 거부된다 (2026-11-09 신설) |
| AC-CAT-099 | 정상 | REQ-CAT-076 | 관리자가 linkType=EVENT_PAGE 또는 EXTERNAL_URL로 GNB 메뉴를 등록한다 | 임의의 URL 문자열을 linkTarget에 입력한다 | 존재 여부 검증 없이 그대로 저장된다 (2026-11-09 신설) |
| AC-CAT-100 | 정상 | REQ-CAT-077 | GNB 메뉴 3건이 모두 is_exposed=true이고 전시기간 이내다 | 고객이 홈 화면에 진입한다 | 3건이 sort_order 오름차순으로 반환된다 (2026-11-09 신설) |
| AC-CAT-101 | 경계값 | REQ-CAT-077 | GNB 메뉴 중 1건은 전시기간이 지났고, 나머지는 노출조건을 만족하는 메뉴가 전혀 없다 | 고객이 홈 화면에 진입한다 | 전시기간이 지난 메뉴는 제외되고, 노출조건을 만족하는 메뉴가 0건이면 빈 배열이 반환된다 (2026-11-09 신설) |
| AC-CAT-102 | 정상 | REQ-CAT-078 | 전시 페이지가 status=PUBLISHED, is_exposed=true다 | 고객이 해당 페이지의 slug 경로로 접근한다 | 홈 화면과 동일한 섹션 resolve 로직으로 BANNER·PRODUCT_LIST 등 섹션이 반환된다 (2026-11-09 신설) |
| AC-CAT-103 | 예외 | REQ-CAT-078 | 전시 페이지가 status=DRAFT 또는 CLOSED 또는 CANCELLED다 | 고객이 해당 페이지의 slug 경로로 접근한다 | 404 DISPLAY_PAGE_NOT_FOUND가 반환된다 (2026-11-09 신설) |
| AC-CAT-104 | 예외 | REQ-CAT-078 | 전시 페이지가 status=PUBLISHED이지만 is_exposed=false다 | 고객이 해당 페이지의 slug 경로로 접근한다 | 404 DISPLAY_PAGE_NOT_FOUND가 반환된다 (2026-11-09 신설) |

---

## 10. 연동지원 Bolt (PublicApi·이벤트)

| ID | 카테고리 | 대응 EARS | Given | When | Then |
|---|---|---|---|---|---|
| AC-CAT-058 | 정상 | REQ-CAT-044 | 상품이 존재한다 | Order 도메인이 상품 ID로 정보를 요청한다 | 이름·가격·상태·판매자 정보가 반환된다 |
| AC-CAT-059 | 정상 | REQ-CAT-045 | SKU의 available_quantity가 충분하다 | Order 도메인이 재고 차감을 요청한다 | 요청 수량만큼 available_quantity가 차감된다 |
| AC-CAT-060 | 정상 | REQ-CAT-046 | 복수 SKU가 존재한다 | Order 도메인이 가용 재고 확인을 요청한다 | 각 SKU별 available_quantity가 반환된다 |
| AC-CAT-061 | 정상 | REQ-CAT-047 | SKU가 SOLD_OUT 상태이다 | ORDER_CANCELLED 이벤트를 수신한다 | available_quantity가 복원되고 조건 충족 시 자동 ON_SALE 전환된다 (REQ-CAT-022 적용) |
| AC-CAT-062 | 정상 | REQ-CAT-048 | 판매자A 소속 상품이 여러 건 존재한다 | Order 도메인이 판매자 단위 배송 속성을 요청한다 | 해당 상품들의 판매자 정보가 반환된다 (묶음배송·배송비 계산은 Order가 수행) |
| AC-CAT-063 | 정상 | REQ-CAT-049 | 상품에 vendor_id·price_sale이 설정돼 있다 | Promotion 도메인이 상품-행사 그룹핑 속성을 요청한다 | 해당 속성값이 반환된다 (그룹 판정은 Promotion이 수행) |
| AC-CAT-064 | 정상 | REQ-CAT-050 | 상품의 price_sale이 89000이다 | Promotion 도메인으로부터 행사가 반영 요청(69000)을 수신한다 | price_sale이 69000으로 갱신된다 |
| AC-CAT-065 | 정상 | REQ-CAT-051 | 상품의 price_sale이 행사가 69000으로 적용된 상태이고 행사 전 가격은 89000이었다 | Promotion 도메인으로부터 행사 종료 시 가격 복원 요청을 수신한다 | price_sale이 89000으로 복원된다 |

---

## 근거

> **원칙**: 상세설계 단계 산출물은 AS-IS 정책서를 직접 인용하지 않는다. `DD-EARS기능요구/
> catalog.md`가 1차 근거이며, `DBA-도메인정책서/catalog.md`로 정책 맥락을 보강한다.

| 항목 | 출처 |
|---|---|
| 시나리오 도출 | `deliverables/S2-구조설계/DD-EARS기능요구/catalog.md` REQ-CAT-001~051, REQ-CAT-056·057·059b·061~063·071~075 → GWT 변환 |
| 복제등록·대량등록·찜하기·SNS공유·주문수량제한 AC 소급 반영(AC-CAT-069~077) | 사용자 지시(2026-11-09) — REQ-CAT-056·057·059b·061~063는 2026-11-06 신설 당시 DK·DL에만 반영되고 AC-CAT가 누락돼 있던 공백을 메움 |
| 상품 랭킹(실시간/일간/주간) AC 신설(AC-CAT-078~084) | 사용자 지시(2026-11-09) — REQ-CAT-074~075, DBA §1.17·§2.13 |
| 재고품절임박알림·상품뱃지(NEW/BEST/품절임박)·추천실패대체·전시여부플래그·빈섹션생략 AC 소급 반영(AC-CAT-085~095) | 사용자 지시(2026-11-09) — REQ-CAT-058·059·064~070은 2026-11-06 DBA/DD 신설 당시 DK에만 반영되고 AC-CAT가 전무했던 공백을 메움 |
| admin 전용 가격변경(소유자 검증 생략) AC 신설(AC-CAT-096) | 사용자 지시(2026-11-09) — API-CAT-043, DQ 미진항목 #2 해소 |
| GNB 메뉴 관리 AC 신설(AC-CAT-097~101) | 사용자 지시(2026-11-09) — REQ-CAT-076~077, DBA §2.14 |
| 비홈 전시 페이지 뷰어 AC 신설(AC-CAT-102~104) | 사용자 지시(2026-11-09) — REQ-CAT-078, DBA §2.15, 미진항목 #9·#13 해소 |
| 상품 요약·태그 제한 AC 신설(AC-CAT-105~106) | 사용자 지시(2026-11-09) — REQ-CAT-079, DBA §1.3.3·§1.3.4(기존 정책 소급 반영) |
| 옵션값 이미지 AC 신설(AC-CAT-107~108) | 사용자 지시(2026-11-09) — REQ-CAT-080~081, DBA §1.4.1(신설), API-CAT-049·050 |
| 상품 단위 전시여부·검색노출 제외 AC 신설(AC-CAT-109~110) | 사용자 지시(2026-11-09) — REQ-CAT-082~083, DBA §2.16(신설). SCR-A-C04-T6(전시 탭) 폐지 결정에 따른 대체 |
| Bolt 구분 | `deliverables/S2-구조설계/DC-상위유스케이스/catalog.md` ⑤ Bolt 분할 후보 (9개 업무그룹과 1:1 대응, 상품등록·심사는 직매입/입점형 2개 Bolt로 분리) |
| 경계값 수치 | DBA §2.3(재제출 기한 30일, 반복반려 3회)·§2.6(release_date > now)·§5.1(옵션 최대 2단계)·§6.3(예약 1건) |
| 예외 시나리오 | EARS Unwanted/Optional 패턴 (REQ-CAT-023·027) |
| 상태 전이 | `deliverables/S2-구조설계/DH-상태머신/catalog.md` — cat_product 7상태(직매입/입점형 분기), cat_display_page 7상태 |
| 재고 자동전환(대안A) 검증 | DBA §2.4, DD REQ-CAT-022 — "발생원인 무관, MD 확인 불필요"를 Given-When-Then 양쪽 경로(AC-CAT-028·029)로 검증 |
| 노출 우선순위 COALESCE 규칙 | DBA §6.1, DD REQ-CAT-037 |
