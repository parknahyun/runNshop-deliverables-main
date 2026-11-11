# EARS 기능요구사항 — Catalog

> **단계**: 구조설계
> **문서범위**: Domain
> **문서종류**: Spec
>
> **작성 목적**: 상위 유스케이스(⑥)를 기반으로, Catalog 도메인의 기능요구를 EARS 패턴으로 정형화한다.
> **흐름 내 위치**: ⑥ 상위 UC → ⑦ 메뉴구조도 → **⑧ EARS** → ⑨ ERD → ⑩ 상태머신
> **작성 주체**: 시니어 개발자 + AI 협업 (기획자·현업 검토·확인)

| 항목 | 내용 |
|---|---|
| ID | SPEC-EARS-CATALOG-001 |
| 상태 | **Draft** |
| 작성일 | 2026-08-21 |
| 갱신일 | 2026-11-06 |

> **2026-10-26 전면 재작성**: `DC-상위유스케이스/catalog.md`(9개 업무그룹 재편)·
> `DBA-도메인정책서/catalog.md`를 기준으로 전면 재작성했다. 기존 문서는 2026-08-21 작성 후
> 갱신되지 않아 직매입 경로·재고 자동전환(대안A)·출시일 노출 게이트(C안)·Promotion·Order
> 소유권 경계 등이 전혀 반영되지 않았고, REQ-CAT-030(Promotion→RatingUpdated)처럼 발신
> 도메인이 자기 모순인 오류 요구사항도 있었다. REQ 번호는 001부터 재부여했다. 업무그룹
> 순서는 DC와 동일하게 **상품등록·심사 / 상품정보관리 / 분류체계관리 / 재고관리 / 가격관리 /
> 고객조회 / 노출로직 / 화면관리(Display) / 연동지원** 9개를 따른다.
>
> **원칙**: 구조설계 단계 산출물은 AS-IS 정책서를 직접 인용하지 않는다. `DBA-도메인정책서/
> catalog.md`가 1차 근거이며, 범위정의 단계 산출물(DB 도메인정의서)은 계속 인용 가능하다.
>
> **2026-11-06 재동기화**: DBA가 2026-11-04에 Part I/II/III 구조로 번호를 전면 재정비했는데,
> 이 문서는 그 이전 번호(§2.1·§4.1·§6.1·§7.x 등)를 그대로 인용하고 있어 전부 갱신했다. 또한
> DBA에 그 사이 신설된 정책(복제등록·대량등록·재고임박알림·재입고알림 세부화·주문수량제한·
> 찜하기·SNS공유·상품뱃지·추천위젯 실패처리·전시여부 플래그·상품정보제공고시)을 신규
> REQ-CAT-056~070으로 추가했다. 기존 REQ 본문은 ID·내용을 유지하고 "도출 근거"만 교체했다
> (단, DBA 쪽에서 내용 자체가 보강된 REQ-CAT-010·015·029·032·033·036은 본문도 함께 갱신).

---

## 상품등록·심사

> 직매입/입점형 두 경로를 명확히 분리한다(DBA §1.5.1). 입점형은 심사 게이트를 거치고,
> 직매입은 심사 게이트를 생략한다.

| ID | 패턴 | 요구사항 | 상위UC | 도출 근거 |
|---|---|---|---|---|
| REQ-CAT-001 | Event-driven | WHEN 관리자(MD, 직매입 등록자)가 직매입 상품을 등록·완료하면, THE 시스템은 SHALL 심사 게이트 없이 즉시 상태를 DRAFT→ON_SALE로 전환한다. | [직매입] 상품 등록·즉시 판매 전환 | DBA §1.5.1 |
| REQ-CAT-002 | Event-driven | WHEN 판매자가 상품 초안을 작성하면, THE 시스템은 SHALL 상품을 DRAFT 상태로 생성한다. | [입점형] 상품 초안 작성 | DBA §1.5.1 |
| REQ-CAT-003 | Event-driven | WHEN 판매자가 심사 요청을 하면, THE 시스템은 SHALL 상품 상태를 DRAFT→REVIEW_REQUESTED로 전환한다. | [입점형] 심사 요청 | DBA §1.5.1 |
| REQ-CAT-004 | Event-driven | WHEN 관리자(MD, 심사자)가 심사를 착수하면, THE 시스템은 SHALL 상태를 REVIEW_REQUESTED→UNDER_REVIEW로 전환한다. | [입점형] 심사 착수 | DBA §1.6 |
| REQ-CAT-005 | Event-driven | WHEN 관리자(MD, 심사자)가 심사를 승인하면, THE 시스템은 SHALL 상태를 UNDER_REVIEW→ON_SALE로 전환하고 ProductApproved 이벤트를 발행한다. | [입점형] 심사 승인 | DBA §1.6 |
| REQ-CAT-006 | Event-driven | WHEN 관리자(MD, 심사자)가 심사를 반려하면, THE 시스템은 SHALL 상태를 UNDER_REVIEW→REJECTED로 전환하고 reject_reason을 판매자 BO에 기록·노출한다. | [입점형] 심사 반려 | DBA §1.6 |
| REQ-CAT-007 | Event-driven | WHEN 판매자가 반려된 상품을 수정하면, THE 시스템은 SHALL 상태를 REJECTED→DRAFT로 전환한다. | [입점형] 반려 후 재작성 | DBA §1.6 |
| REQ-CAT-008 | Ubiquitous | THE 시스템은 SHALL REJECTED 상태의 재제출 가능 기한을 반려일로부터 30일로 제한하며, 기한 초과 시 DRAFT 상태로 전환되지 않은 해당 상품을 자동 삭제한다. | [입점형] 반려 후 재작성 | DBA §1.6 — 재제출 기한 30일 |
| REQ-CAT-009 | Event-driven | WHEN 동일 상품이 동일 사유로 3회 이상 반복 반려되면, THE 시스템은 SHALL 입점 심사팀 에스컬레이션 대상으로 표시한다. | 동일 사유 반복 반려 에스컬레이션 | DBA §1.6 |
| REQ-CAT-056 | Event-driven | WHEN 판매자가 본인이 등록한 상품의 복제를 요청하면, THE 시스템은 SHALL 가격·재고·판매자 상품코드를 제외한 모든 항목(상품명·설명·이미지·카테고리·속성값·태그·옵션 구조)을 복사하여 `DRAFT` 상태의 신규 상품(신규 `productId`·`skuId`·상품번호·옵션번호 발급, 이미지는 원본 파일 참조)을 생성한다. | 상품 복제 등록 | DBA §1.5.3(2026-11-06 신설) |
| REQ-CAT-057 | Event-driven | WHEN 판매자가 엑셀 양식으로 상품 대량등록을 요청하면, THE 시스템은 SHALL 기본정보(상품명·카테고리·가격 등) 및 옵션(SKU)을 일괄 생성한다. | 상품 대량등록(Bulk) | DBA §1.5.2 — 기존 DBA 정책에 있었으나 EARS 미작성 상태로 남아있던 항목 소급 반영 |

---

## 상품정보관리

| ID | 패턴 | 요구사항 | 상위UC | 도출 근거 |
|---|---|---|---|---|
| REQ-CAT-010 | Event-driven | WHEN 판매자(본인 상품) 또는 관리자(MD)가 상품 기본정보(이름·요약·설명·이미지·카테고리·태그 등)를 수정하면, THE 시스템은 SHALL 별도 승인 절차 없이 변경 사항을 즉시 저장하고 ProductUpdated 이벤트를 발행한다. | 상품 기본정보 수정 | DBA §1.11 (요약·태그는 2026-11-09 명시 보강 — DBA §1.3.1·§1.3.3·§1.3.4 기존 정책의 EARS 소급 반영) |
| REQ-CAT-011 | Event-driven | WHEN 판매자가 상품 이미지를 등록하면, THE 시스템은 SHALL 이미지를 cat_product_image에 저장하고 sort_order를 부여한다. | 상품 이미지 등록·순서변경·삭제 | DBA §1.3.2 |
| REQ-CAT-012 | Ubiquitous | THE 시스템은 SHALL 상품당 이미지를 최대 10장까지, 파일당 최대 10MB(JPG/PNG/WebP, 정방형, 최소 800×800px)로 허용한다. | 상품 이미지 등록·순서변경·삭제 | DBA §1.3.2 |
| REQ-CAT-013 | Event-driven | WHEN 판매자가 옵션그룹·옵션값을 설정하면, THE 시스템은 SHALL 해당 조합으로 SKU를 자동 생성한다. | 옵션그룹·옵션값 설정 | DBA §1.4 |
| REQ-CAT-014 | Ubiquitous | THE 시스템은 SHALL 옵션 깊이를 최대 2단계(예: 색상·사이즈)로 제한한다. | 옵션그룹·옵션값 설정 | DBA §1.4 |
| REQ-CAT-015 | Event-driven | WHEN 판매자 또는 관리자(MD, 운영자)가 단종 처리하면, THE 시스템은 SHALL 상태를 ON_SALE/SOLD_OUT→DISCONTINUED로 전환하며, 이후 어떤 상태로도 복원(재판매)을 허용하지 않는다. | 상품 단종 처리 | DBA §1.9·§1.11 — 재고 수량과 무관한 별도 의사결정, 수동 전환만 허용, 재판매 금지 |
| REQ-CAT-070 | Event-driven | WHEN 고객이 상품 상세를 조회하면, THE 시스템은 SHALL 해당 상품 대분류의 법정 상품정보제공고시 항목을 이미지·설명과 구분된 별도 섹션으로 노출한다. | 상품정보제공고시 노출 | DBA §1.3.8(2026-11-06 신설) — **[Human Review] 법무 확인 전 참고용 항목 기준, DBA §6 HR #36과 동일 쟁점** |
| REQ-CAT-079 | Ubiquitous | THE 시스템은 SHALL 상품 요약을 최대 200자(평문, HTML 불허)로, 태그를 상품당 최대 10개(쉼표 구분, 특수문자·공백 제한)로 제한하며, 상품 목록·검색결과에서 상품명 아래 서브타이틀로 요약을 노출하고 태그는 검색 키워드 매칭에 사용한다. | 상품 요약·태그 입력 제한 | DBA §1.3.3·§1.3.4(기존 정책, 2026-11-09 EARS 소급 반영) |
| REQ-CAT-080 | Event-driven | WHEN 판매자(본인 상품) 또는 관리자(MD)가 옵션값에 이미지를 등록하면, THE 시스템은 SHALL 해당 이미지를 `cat_product_option_value.image_url`에 저장한다. | 옵션값 이미지 등록 | DBA §1.4.1(2026-11-09 신설) |
| REQ-CAT-081 | Ubiquitous | THE 시스템은 SHALL 옵션값 이미지 등록을 옵션그룹 1단계(depth=1)의 옵션값으로 한정하며, 2단계(depth=2) 옵션값에 대한 등록 요청은 거부한다. | 옵션값 이미지 등록 제한(1단계 전용) | DBA §1.4.1(2026-11-09 신설) |
| REQ-CAT-082 | Event-driven | WHEN 판매자(본인 상품) 또는 관리자(MD)가 상품의 전시여부(`is_exposed`)를 FALSE로 전환하면, THE 시스템은 SHALL 상태(status)·재고와 무관하게 해당 상품을 목록·검색·전시 영역·상세 페이지 딥링크에서 즉시 제외하며, TRUE로 되돌리면 즉시 복원한다. | 상품 단위 전시여부(수동 숨김) | DBA §2.16(2026-11-09 신설) |
| REQ-CAT-083 | Event-driven | WHEN 판매자(본인 상품) 또는 관리자(MD)가 상품의 검색노출 제외(`is_search_excluded`)를 TRUE로 설정하면, THE 시스템은 SHALL 해당 상품을 검색 결과에서만 제외하며 목록·카테고리·상세 노출은 그대로 유지한다. | 검색노출 제외(보조 플래그) | DBA §2.16(2026-11-09 신설) |

---

## 분류체계관리

| ID | 패턴 | 요구사항 | 상위UC | 도출 근거 |
|---|---|---|---|---|
| REQ-CAT-016 | Event-driven | WHEN 관리자(MD, 운영자)가 표준 카테고리를 생성·수정·삭제하면, THE 시스템은 SHALL cat_category 트리 구조(대분류-중분류-소분류 3단계)를 갱신한다. | 표준 카테고리 생성·수정·삭제 | DBA §1.2.1 |
| REQ-CAT-017 | Ubiquitous | THE 시스템은 SHALL 상품을 표준 카테고리 소분류 1개에만 귀속시키며 다중 카테고리를 허용하지 않는다. | 카테고리-상품 매핑 | DBA §1.2.1 |
| REQ-CAT-018 | Event-driven | WHEN 관리자(MD, 운영자)가 전시 카테고리를 생성·수정·삭제하면, THE 시스템은 SHALL cat_display_category 트리 구조(대분류-중분류-소분류 3단계)를 갱신한다. | 전시 카테고리 생성·수정·삭제 | DBA §2.5.1 |
| REQ-CAT-019 | Event-driven | WHEN 관리자(MD, 운영자)가 브랜드를 등록·수정하면, THE 시스템은 SHALL 브랜드 마스터 데이터를 갱신한다. | 브랜드 등록·수정 | **[Human Review]** 현재 DBA에는 전용 "브랜드 마스터" 섹션이 없고 §1.2.2의 카테고리별 필수속성 예시(브랜드)로만 흡수돼 있다 — 별도 브랜드 마스터 엔티티가 실제로 필요한지 DF ERD 작성 전 확인 필요 |
| REQ-CAT-071 | Event-driven | WHEN 관리자(MD, 운영자)가 전시 카테고리에 매핑된 상품 목록의 순서를 저장하면, THE 시스템은 SHALL 전달받은 상품 순서를 그대로 `cat_product_display_category.sort_order`에 0부터 일괄 반영하고, 각 상품의 상단고정(`is_pinned`) 여부를 함께 갱신한다. | 전시카테고리 상품순서 저장 | DBA §2.5.3(2026-11-09 신설) |

---

## 재고관리

> 재고 자동전환(대안A, DBA §1.10)을 명확히 반영한다 — **재고 복원의 발생 원인(주문취소·
> 반품교환확정·판매자재고신규등록)과 무관하게** MD 확인 없이 자동 전환한다. 판매종료
> (DISCONTINUED)는 재고 수량과 무관한 별도 의사결정이라 상품정보관리(REQ-CAT-015)에서
> 수동으로만 다룬다.

| ID | 패턴 | 요구사항 | 상위UC | 도출 근거 |
|---|---|---|---|---|
| REQ-CAT-020 | Event-driven | WHEN 판매자가 SKU 재고 수량을 변경하면, THE 시스템은 SHALL stock_quantity와 available_quantity를 갱신하고 cat_stock_history에 기록한다. | SKU 재고 수량 설정·변경 | DBA §1.10 |
| REQ-CAT-021 | Event-driven | WHEN SKU의 available_quantity가 0이 되면, THE 시스템은 SHALL 해당 상품 상태를 ON_SALE→SOLD_OUT으로 자동 전환한다. | 재고 부족 시 품절 자동 전환 | DBA §1.10 |
| REQ-CAT-022 | Event-driven | WHEN SOLD_OUT 상품의 available_quantity가 발생 원인(주문취소 복원·반품교환 확정·판매자 재고 신규등록)과 무관하게 1 이상으로 복원되면, THE 시스템은 SHALL 관리자(MD) 확인 없이 상태를 SOLD_OUT→ON_SALE로 자동 전환한다. | 재입고 시 판매 재개 자동 전환 | DBA §1.10(대안A) — 재고 변경 빈도가 높아 전량 승인은 운영 불가 |
| REQ-CAT-023 | Unwanted | IF Order 도메인의 재고 차감 요청 시 available_quantity < 요청 수량이면, THEN THE 시스템은 SHALL 차감을 거부하고 INSUFFICIENT_STOCK 응답을 반환한다. | PublicApi: 재고 차감 요청 (연동지원) | DBA §1.10 — 불변식: 가용 재고 ≥ 0 |
| REQ-CAT-024 | Ubiquitous | THE 시스템은 SHALL 모든 재고 변동(차감·복원·신규등록)을 cat_stock_history에 변동사유·수량·시점과 함께 기록한다. | 재고 선점·복원 (연동지원) | DBA §1.10 |
| REQ-CAT-025 | Event-driven | WHEN 재고 변동이 발생하면, THE 시스템은 SHALL StockChanged 이벤트를 발행한다. | 이벤트 발행 (연동지원) | DBA §1.10 |
| REQ-CAT-058 | Event-driven | WHEN 상품에 속한 SKU 중 하나라도 available_quantity가 해당 상품에 설정된 재고 임박 기준수량(기본값 5, 상품 단위 설정) 이하로 떨어지면, THE 시스템은 SHALL 담당자(입점형은 해당 입점사 담당자, 직매입은 공통 관리자 계정체계에 등록된 관리자)에게 상품 단위로 임박 알림을 발송한다. | 재고 품절 임박 알림 | DBA §1.10(2026-11-06 신설) |
| REQ-CAT-059 | Unwanted | WHILE 상품의 재고 임박 상태가 유지되는 동안, THE 시스템은 SHALL NOT 동일 상품에 대해 임박 알림을 중복 발송한다 (기준값 초과로 회복된 후 다시 떨어지면 재발송). | 재고 품절 임박 알림 중복 방지 | DBA §1.10(2026-11-06 신설) |
| REQ-CAT-074 | Event-driven | WHEN 재고 변동이 발생해 StockChanged 이벤트가 발행되면, THE 시스템은 SHALL `changeType`이 RESERVE(판매) 또는 RESTORE_ORDER_CANCEL(주문취소)인 경우에만 비동기로 `cat_product_sales_hourly`(상품·시간대별 판매량 버킷)를 갱신하고, RESTORE_RETURN_EXCHANGE(반품·교환확정)와 RESTOCK_VENDOR(판매자 재고 신규등록)는 집계에서 제외한다. | 상품 랭킹 집계 (비동기) | DBA §1.17(2026-11-09 신설) |

---

## 가격관리

> 가격 3단 구조(정가≥판매가≥공급가, DBA §1.7.1)의 불변식을 명시한다. 판매가는
> `cat_product` 컬럼이 아니라 `cat_product_price_schedule`(기간별 스케줄, DBA §1.7.2)에 저장된다
> — 마스터 속성(정가·공급가)과 변동 속성(판매가)을 분리했다. Promotion이 트리거하는 행사가
> 반영·복원도 이 스케줄 테이블에 행을 추가하는 방식으로 바뀌어 연동지원 그룹에서 다룬다
> (REQ-CAT-049~051).

| ID | 패턴 | 요구사항 | 상위UC | 도출 근거 |
|---|---|---|---|---|
| REQ-CAT-026 | Event-driven | WHEN 판매자 또는 관리자(MD, 운영자)가 정가·판매가·공급가를 설정·변경하면, THE 시스템은 SHALL 정가·공급가는 cat_product에 즉시 반영하고, 판매가는 cat_product_price_schedule에 `source_type=BASE`, `start_at=now`, `end_at=NULL`(무기한) 행으로 추가한다 (기존 BASE 행이 있으면 `end_at=now`로 종료 처리). `created_by`에는 실제 변경을 수행한 주체의 ID(vendor_id 또는 admin_id)가 기록되며, 관리자 경로는 소유자(판매자) 검증을 생략한다. | 판매가·공급가·정가 설정·변경 | DBA §1.7.1(결정 주체: 판매자 또는 플랫폼 MD)·§1.7.2 — 2026-11-09 본문 보강(admin 전용 가격변경 API 신설) |
| REQ-CAT-027 | Unwanted | IF 가격 설정 시 "정가 ≥ 판매가 ≥ 판매자 공급가" 순서를 위반하면, THEN THE 시스템은 SHALL 설정을 거부한다. | 판매가·공급가·정가 설정·변경 | DBA §1.7.1 — 가격 구조 불변식 |
| REQ-CAT-028 | Ubiquitous | THE 시스템은 SHALL 조회 시점에 유효한 판매가(now가 start_at~end_at 구간에 포함되는 cat_product_price_schedule 행)가 정가보다 낮으면 할인율을 함께 표시한다. | 판매가·공급가·정가 설정·변경 | DBA §1.7.1 |
| REQ-CAT-028b | Ubiquitous | THE 시스템은 SHALL 상품의 유효 판매가를 `WHERE product_id=? AND start_at<=now AND (end_at IS NULL OR end_at>now)` 조건으로 조회하며, 조회 시점에 유효 행이 2건 이상인 경우의 선택 규칙은 Human Review 대상이다. | 판매가·공급가·정가 설정·변경 | DBA §1.7.2 — 기간 중복 처리는 Promotion 정책 소관, Human Review #6 |
| REQ-CAT-059b | Ubiquitous | THE 시스템은 SHALL 상품 단위로 `max_order_quantity`(nullable, 기본 NULL=무제한) 값을 보유·제공하며, 값 자체의 검증(1회 주문 초과 거부)은 Order 도메인이 수행한다. | 주문 수량 제한 값 제공 (연동지원) | DBA §1.8(2026-11-06 신설) — 실제 검증 요구사항은 **Order EARS**에 작성 필요 |

---

## 고객조회

| ID | 패턴 | 요구사항 | 상위UC | 도출 근거 |
|---|---|---|---|---|
| REQ-CAT-029 | Event-driven | WHEN 고객이 전시 카테고리별 상품 목록을 조회하면, THE 시스템은 SHALL `cat_product_display_category`에 매핑된 ON_SALE/SOLD_OUT 상태 상품만 페이징하여 반환한다 (DRAFT/REVIEW_REQUESTED/UNDER_REVIEW/REJECTED/DISCONTINUED는 제외), 정렬은 REQ-CAT-072를 따른다. | 상품 목록 조회 | DBA §1.9·§2.5.2·§2.5.3(2026-11-09 재정의 — 표준 카테고리에서 전시 카테고리로 변경) |
| REQ-CAT-030 | Event-driven | WHEN 고객이 상품 상세를 조회하면, THE 시스템은 SHALL 상품 기본정보·이미지·옵션·SKU 가용재고를 반환한다. | 상품 상세 조회 | DBA §1.3 |
| REQ-CAT-031 | Event-driven | WHEN 고객이 키워드·필터로 상품을 검색하면, THE 시스템은 SHALL 전시 카테고리·가격·브랜드 필터를 적용하여 결과를 반환한다. | 상품 검색 | DBA §1.2.2·§2.5.2(2026-11-09 — 카테고리 필터를 전시 카테고리 기준으로 통일) |
| REQ-CAT-073 | Event-driven | WHEN 고객이 카테고리 메뉴에 진입하면, THE 시스템은 SHALL `is_active=TRUE`인 전시 카테고리 트리(대분류-중분류-소분류)를 반환한다. | 전시카테고리 목록 조회(고객) | DBA §2.5.1(2026-11-09 신설) |
| REQ-CAT-032 | Event-driven | WHEN 고객이 품절(SOLD_OUT) 상태인 SKU에 재입고 알림을 신청하면, THE 시스템은 SHALL `cat_restock_subscription`에 `PENDING` 건을 생성(SKU당 1건, 중복 신청 방지)하고, 해당 SKU가 SOLD_OUT→ON_SALE로 전환될 때(REQ-CAT-022) PENDING 건 전체를 `NOTIFIED`로 전환하며 일괄 발송한다. `ON_SALE` 상태 SKU는 신청 메뉴 자체를 노출하지 않는다. | 재입고 알림 신청 | DBA §1.10 |
| REQ-CAT-061 | Event-driven | WHEN 로그인 고객이 상품에 찜하기를 설정·해제하면, THE 시스템은 SHALL `cat_product_wishlist`에 상품당 1건만 유지되도록 등록·삭제하고, 상품이 노출되는 목록·상세 화면과 마이페이지 찜 목록에 반영한다. | 찜하기 등록·해제·목록 조회 | DBA §1.14(2026-11-06 신설) |
| REQ-CAT-062 | Event-driven | WHEN 상품 상태가 SOLD_OUT 또는 DISCONTINUED로 전환되면, THE 시스템은 SHALL 해당 상품의 모든 찜 데이터를 즉시 삭제한다 (재입고돼도 복원하지 않음). | 찜 데이터 자동 삭제 | DBA §1.14(2026-11-06 신설) |
| REQ-CAT-063 | Event-driven | WHEN 고객이 상품 상세 또는 전시 페이지에서 공유를 요청하면, THE 시스템은 SHALL 공유 URL(canonical)·제목·대표 이미지·요약 설명을 반환한다 (리워드 없음, 기존 데이터 재사용, 신규 필드 없음). | SNS 공유·URL 복사 메타데이터 제공 | DBA §1.16(2026-11-06 신설) — 이벤트 페이지는 Promotion 소유라 Catalog 범위 밖 |

---

## 노출로직

> 고객 조회 결과(고객조회 그룹)에 시스템이 적용하는 필터링·가공 로직. 출시일 노출 게이트
> (C안), 화면별 할인가 노출, 연관상품 추천, 노출 우선순위, 상품 뱃지를 다룬다.

| ID | 패턴 | 요구사항 | 상위UC | 도출 근거 |
|---|---|---|---|---|
| REQ-CAT-033 | Ubiquitous | THE 시스템은 SHALL ON_SALE 상품 중 `release_date`가 설정돼 있고 `release_date > now`인 상품을 상품 목록·검색·전시 조회 결과에서 제외하며, 해당 상품의 상세 페이지 직접 접근(딥링크)도 동일하게 차단한다 (상태 전이 없이 조회 쿼리 필터로만 처리). | 출시일 노출 필터링 | DBA §2.4(C안) |
| REQ-CAT-034 | Ubiquitous | THE 시스템은 SHALL `release_date`가 설정되지 않은 상품에는 출시일 노출 필터를 적용하지 않는다(즉시 노출). | 출시일 노출 필터링 | DBA §2.4(C안) — 하위 호환 |
| REQ-CAT-035 | Event-driven | WHEN 상품목록·상품상세(비로그인/로그인)·장바구니·주문서 화면이 할인가 노출을 요청하면, THE 시스템은 SHALL 화면 그룹별로 정의된 노출 항목(정가·행사가·전체대상쿠폰·회원등급할인·조건만족쿠폰·장바구니할인·포인트사용)만 반환한다. | 화면별 할인가 노출 | DBA §2.8.1 — Catalog가 1차 소유, Order 소유 화면(장바구니·주문서)과 기준 공유 |
| REQ-CAT-036 | Event-driven | WHEN 고객이 상품 목록·장바구니에서 연관상품 추천을 요청하면, THE 시스템은 SHALL 외부 상품추천 SaaS에 요청하고, 반환된 추천 상품을 자체 노출 기준(ON_SALE + 출시일 게이트)으로 재조회해 노출 불가 상품을 제외한 뒤 제공한다. 추천 상품에도 화면별 할인가 노출(REQ-CAT-035)을 동일 적용한다. | 연관상품 추천 위젯 제공 | DBA §2.9 — Catalog가 외부 SaaS 연동 전담, Order는 화면 배치만 |
| REQ-CAT-037 | Ubiquitous | THE 시스템은 SHALL 상품 목록 노출 순서를 `exposure_priority = COALESCE(md_override, sales_rank, default_order)` 규칙으로 산정하며, 관리자(MD) 수동 설정값을 항상 우선 적용한다. 전시 카테고리를 지정해 조회하는 경우에는 REQ-CAT-072(카테고리별 정렬)가 이 규칙보다 우선한다. | 노출 우선순위 수동 설정 (MD Override) | DBA §2.6 |
| REQ-CAT-072 | Ubiquitous | THE 시스템은 SHALL 전시 카테고리별 상품 목록을 조회할 때 `cat_product_display_category.is_pinned` 내림차순, `sort_order` 오름차순으로 정렬해 반환한다(상단고정 상품은 정렬순서와 무관하게 항상 먼저 노출). | 전시카테고리 상품순서 정렬 조회 | DBA §2.5.3(2026-11-09 신설) |
| REQ-CAT-053 | Event-driven | WHEN 고객이 홈 화면(mobile "/")을 조회하면, THE 시스템은 SHALL `is_home=TRUE`인 전시 페이지의 섹션을 콘텐츠유형별로 resolve하여 반환한다 — 상품목록은 상품코드로 자체 상품 데이터를 조회, 이벤트목록은 이벤트 key로 `cat_event_banner_schedule`에서 조회 시점(now) 유효 배너를 조회, 추천영역은 외부 추천 SaaS를 실시간 호출(REQ-CAT-036 재사용). | 홈 화면 섹션 콘텐츠 resolve | DBA §2.9 |
| REQ-CAT-064 | Ubiquitous | THE 시스템은 SHALL `release_date`(또는 등록일) 기준 14일 이내인 상품에 NEW 뱃지를 노출한다. | 상품 뱃지 — NEW | DBA §2.6(2026-11-06 신설) |
| REQ-CAT-065 | Ubiquitous | THE 시스템은 SHALL 카테고리별 판매량 순위(sales_rank) 상위 10위 이내인 상품에 BEST 뱃지를 노출한다. | 상품 뱃지 — BEST | DBA §2.6(2026-11-06 신설) |
| REQ-CAT-066 | Ubiquitous | THE 시스템은 SHALL SKU 재고가 재고 임박 기준수량(DBA §1.10) 이하인 상품에 품절임박 뱃지를 노출하며, 여러 뱃지 조건을 동시에 만족하면 모두 노출한다. | 상품 뱃지 — 품절임박 | DBA §2.6(2026-11-06 신설) |
| REQ-CAT-067 | Unwanted | IF 외부 추천 SaaS 응답이 지연되거나 실패하면, THEN THE 시스템은 SHALL 위젯을 숨기지 않고 판매량 순위(sales_rank) 상위 N개 상품(기본값 20, 노출 영역별 설정 가능)으로 대체 노출한다. | 연관상품 추천 실패 시 대체 노출 | DBA §2.9(2026-11-06 신설) |
| REQ-CAT-075 | Event-driven | WHEN 고객이 랭킹 화면에 진입하면, THE 시스템은 SHALL 선택한 기준(실시간=최근 3시간, 일간=오늘 00:00~현재, 주간=최근 7일)과 선택적 전시 카테고리 필터에 따라 `cat_product_sales_hourly`의 해당 범위 합산값을 내림차순 정렬해 상위 N개 상품을 반환한다. | 상품 랭킹 조회(실시간/일간/주간) | DBA §2.13(2026-11-09 신설) |

---

## 화면관리(Display)

> 전시 페이지(기획전·배너 등 콘텐츠) 생명주기. 노출 우선순위는 "노출로직" 그룹으로 분리됨.

| ID | 패턴 | 요구사항 | 상위UC | 도출 근거 |
|---|---|---|---|---|
| REQ-CAT-038 | Event-driven | WHEN 관리자(MD, 운영자)가 전시 페이지를 생성하면, THE 시스템은 SHALL 페이지를 DRAFT 상태로 생성한다. | 전시 페이지 생성·편집 | DBA §2.7.1 |
| REQ-CAT-039 | Event-driven | WHEN 관리자(MD, 운영자)가 전시 페이지를 게시하면, THE 시스템은 SHALL 상태를 PUBLISHED로 전환한다. | 전시 페이지 게시 | DBA §2.7.1 |
| REQ-CAT-040 | Event-driven | WHEN `display_start_at`이 설정된 DRAFT 페이지의 해당 시각이 도래하면, THE 시스템(배치 `BAT-CAT-002`)은 SHALL 상태를 PUBLISHED로 자동 전환한다. | 전시 페이지 게시 예약(display_start_at) | DBA §2.10(2026-11-09 재정의) |
| REQ-CAT-041 | Ubiquitous | THE 시스템은 SHALL PUBLISHED 상태의 전시 페이지도 제목·섹션 구성·전시기간을 상태 전이 없이 직접 수정할 수 있도록 허용한다(저장 즉시 반영, 별도 임시본 없음). | PUBLISHED 상태 직접 수정 | DBA §2.10(2026-11-09 재정의) |
| REQ-CAT-042 | Ubiquitous | THE 시스템은 SHALL 전시 페이지의 `display_end_at`을 설정하는 경우 `display_start_at`보다 이후 시각인지 검증한다. | 전시기간 값 검증 | DBA §2.10(2026-11-09 재정의) |
| REQ-CAT-043 | Event-driven | WHEN `display_end_at`이 설정된 PUBLISHED 페이지의 해당 시각이 도래하거나 관리자(MD, 운영자)가 종료 처리하면, THE 시스템은 SHALL 상태를 CLOSED로 전환한다 (종료 후 재활성화 불가). | 전시 페이지 종료(display_end_at 또는 수동) | DBA §2.7.1·§2.10(2026-11-09 재정의) |
| REQ-CAT-052 | Event-driven | WHEN 관리자(MD, 운영자)가 PUBLISHED 상태의 전시 페이지를 홈으로 지정하면, THE 시스템은 SHALL 기존 홈 지정(있다면)을 해제하고 해당 페이지의 `is_home`을 TRUE로 설정한다. | 홈 화면 지정 (mobile "/" 노출 대상) | DBA §2.7.2 |
| REQ-CAT-068 | Event-driven | WHEN 운영자가 전시 페이지의 전시여부(`is_exposed`)를 N으로 전환하면, THE 시스템은 SHALL 상태 전이·예약·홈 지정을 그대로 둔 채 해당 페이지를 노출 쿼리에서만 즉시 제외하며, Y로 되돌리면 즉시 복원한다. 홈 지정 페이지가 N이 되면 "홈 미지정"과 동일하게 처리해 기본 카테고리 화면으로 대체 노출한다. | 긴급 게시·회수 (전시여부 플래그) | DBA §2.10(2026-11-06 신설) |
| REQ-CAT-069 | Ubiquitous | THE 시스템은 SHALL 콘텐츠가 등록되지 않은 전시 섹션(빈 영역)을 노출 시 생략(skip)하며, 나머지 섹션은 정상 노출한다. | 빈 섹션 생략 노출 | DBA §2.11(2026-11-06 신설) |
| REQ-CAT-078 | Event-driven | WHEN 고객이 비홈 전시 페이지(slug 경로)에 접근하면, THE 시스템은 SHALL 해당 페이지가 `status=PUBLISHED`이고 `is_exposed=TRUE`인 경우에만 섹션을 홈 화면(REQ-CAT-053)과 동일한 방식으로 resolve하여 반환하며, 그 외 상태·비노출 페이지는 404를 반환한다. | 비홈 전시 페이지 뷰어 조회 | DBA §2.15(2026-11-09 신설) |
| REQ-CAT-076 | Event-driven | WHEN 관리자(MD, 운영자)가 GNB 메뉴를 등록·수정·삭제·순서변경하면, THE 시스템은 SHALL `cat_gnb_menu`에 메뉴명·링크유형(`link_type`)·링크대상(`link_target`)·정렬순서(`sort_order`)·전시여부(`is_exposed`)·전시기간(`display_start_at`/`display_end_at`)을 저장하며, 링크유형이 DISPLAY_PAGE 또는 DISPLAY_CATEGORY면 참조 대상의 존재 여부를 검증하고, EVENT_PAGE·EXTERNAL_URL이면 URL 문자열을 그대로 저장한다(검증 없음). | GNB 메뉴 관리 | DBA §2.14(2026-11-09 신설) |
| REQ-CAT-077 | Event-driven | WHEN 고객이 홈 화면(mobile "/")에 진입하면, THE 시스템은 SHALL `is_exposed=TRUE`이고 조회 시점이 전시기간(`display_start_at`~`display_end_at`) 이내인 GNB 메뉴만 `sort_order` 오름차순으로 반환한다 (전시기간 미설정 시 상시 노출). | GNB 메뉴 노출 조회(고객) | DBA §2.14(2026-11-09 신설) |

---

## 연동지원

> Order·Promotion 도메인과의 모든 연동(PublicApi·이벤트)을 모은 그룹 — 외부
> 도메인이 트리거하는 항목은 소유 그룹이 아니라 이곳에 둔다.

| ID | 패턴 | 요구사항 | 상위UC | 도출 근거 |
|---|---|---|---|---|
| REQ-CAT-044 | Event-driven | WHEN Order 도메인이 상품 정보를 요청하면, THE 시스템은 SHALL 상품 ID 기반으로 이름·가격·상태·판매자 정보를 반환한다. | PublicApi: 상품 정보 조회 | `DB-도메인정의서.md` §1 Order "의존" 행(← Catalog) |
| REQ-CAT-045 | Event-driven | WHEN Order 도메인이 재고 차감을 요청하면, THE 시스템은 SHALL 해당 SKU의 available_quantity를 요청 수량만큼 차감한다 (실패 조건은 REQ-CAT-023 참조). | PublicApi: 재고 차감 요청 | `DB-도메인정의서.md` §1 Order "의존" 행(← Catalog) |
| REQ-CAT-046 | Event-driven | WHEN Order 도메인이 복수 SKU의 가용 재고를 확인 요청하면, THE 시스템은 SHALL 각 SKU별 available_quantity를 반환한다. | PublicApi: 재고 확인 | DBA §1.10 |
| REQ-CAT-047 | Event-driven | WHEN Order 도메인으로부터 ORDER_CANCELLED 이벤트를 수신하면, THE 시스템은 SHALL 해당 SKU의 available_quantity를 복원하고 조건 충족 시 REQ-CAT-022에 따라 자동 ON_SALE 전환한다. | 이벤트 수신: ORDER_CANCELLED | DBA §1.10 |
| REQ-CAT-048 | Event-driven | WHEN Order 도메인이 판매자 단위 배송 속성(vendor_id 그룹핑)을 요청하면, THE 시스템은 SHALL 해당 상품의 판매자 정보를 반환한다. 묶음배송·배송비 계산은 Order가 수행한다. | PublicApi: 판매자 단위 배송 속성 제공 | DBA §1.13.1 |
| REQ-CAT-049 | Event-driven | WHEN Promotion 도메인이 상품-행사 그룹핑 속성(vendor_id·조회 시점 유효 판매가)을 요청하면, THE 시스템은 SHALL 해당 상품의 속성값을 반환한다. 수량할인 그룹 판정은 Promotion이 수행한다. | PublicApi: 상품-행사 그룹핑 속성 제공 | DBA §1.7.4 — Catalog는 속성값만 제공, 정책 소유는 Promotion |
| REQ-CAT-050 | Event-driven | WHEN Promotion 도메인으로부터 행사가 반영 요청(시작일시·종료일시·행사가)을 수신하면, THE 시스템은 SHALL cat_product_price_schedule에 `source_type=PROMOTION_EVENT`, 요청받은 start_at~end_at·source_event_id로 행을 추가한다. | [Promotion 연동] 행사가 반영 요청 수신 | DBA §1.7.4·§1.7.2 — 1차 정책 소유는 Promotion |
| REQ-CAT-051 | Event-driven | WHEN 행사 기간의 end_at이 도래하면, THE 시스템은 SHALL 별도 요청·배치 없이 조회 시점 판정으로 그 다음 유효 행(BASE 또는 다음 스케줄)을 자동 선택한다. | [Promotion 연동] 행사 종료 시 가격 자동 복원 | DBA §1.7.4·§1.7.2 — 출시일 노출 게이트(C안)와 동일한 조회시점판정 패턴 |
| REQ-CAT-054 | Event-driven | WHEN Promotion 도메인으로부터 기획전 배너 동기화 요청(이벤트 key·배너이미지·기간)을 수신하면, THE 시스템은 SHALL `cat_event_banner_schedule`에 해당 이벤트 key로 행을 upsert한다. | [Promotion 연동] 기획전 배너 동기화 수신 | DBA §2.8.2 — **[Human Review] Promotion 측 실제 이벤트 발행 여부 미확인** |
| REQ-CAT-055 | Event-driven | WHEN Promotion 도메인으로부터 기획전 배너 동기화 취소 요청을 수신하면, THE 시스템은 SHALL 해당 `cat_event_banner_schedule` 행을 `end_at=now`로 종료 처리한다 (물리 삭제 아님). | [Promotion 연동] 기획전 배너 동기화 취소 수신 | DBA §2.8.2 — **[Human Review] Promotion 측 실제 이벤트 발행 여부 미확인** |
| REQ-CAT-060 | Event-driven | WHEN Promotion 도메인이 수량조건(1+1 등 min=max 구간) 대상 상품을 조회·등록하면, THE 시스템은 SHALL 각 상품의 `max_order_quantity` 값을 제공하여, 조건을 만족할 수 없는 상품을 Promotion이 대상에서 제외할 수 있도록 한다. | PublicApi: 주문 수량 제한 값 제공 | DBA §1.8(2026-11-06 신설) — 실제 필터링 로직은 **Promotion EARS**에 작성 필요, DBA §6 HR #34 |

---

## Human Review

| # | 항목 | 사유 |
|---|---|---|
| 1 | ~~REQ-CAT-033 출시일 노출 게이트의 상세 페이지 딥링크 처리~~ | **해소(2026-11-06)** — DBA §2.4에서 상세 페이지 직접 접근도 목록·검색과 동일하게 차단하는 것으로 확정(DBA §6 HR #8과 동일 쟁점). REQ-CAT-033 본문에 반영 완료 |
| 2 | ~~REQ-CAT-036 연관상품 추천의 검증필터·프로모션연동·실패처리~~ | **해소(2026-11-06)** — DBA §2.9에서 3개 항목 모두 확정(DBA §6 HR #2). 검증필터·프로모션연동은 REQ-CAT-036 본문에, 실패처리는 REQ-CAT-067로 반영 완료 |
| 3 | ~~REQ-CAT-049~051과 REQ-CAT-035(화면별 할인노출)의 price_sale 반영 시점 관계~~ | **완화(2026-10-26)** — price_sale 직접 갱신 방식을 폐기하고 cat_product_price_schedule(기간 기록) 방식으로 바꾸면서, "갱신 시점과 읽는 시점의 캐시 지연" 문제 자체가 사라졌다(조회가 항상 now 기준으로 유효 행을 판정). 다만 신규 쟁점(#6)이 남는다 |
| 4 | REQ-CAT-017 카테고리별 필수 입력 속성 전체 매트릭스 | DBA §1.2.2가 예시(러닝화·보충제)만 확인 — 전체 대분류×속성 매트릭스는 DF ERD 작성 시 확정 |
| 5 | REQ-CAT-026 수수료율 구체 수치 | DBA §1.7.3이 "기본율−등급감면율" 구조만 확인 — 구체 수치는 DF ERD 작성 시 확정 |
| 6 | REQ-CAT-028b `cat_product_price_schedule` 기간 중복 처리 규칙 | 사용자 확인(2026-10-26) — 중복 처리는 Promotion 도메인 정책 소관. 허용 시 할인율 높은 순 우선조회, 불허 시 Promotion이 등록 시점에 중복체크. `DBA-도메인정책서/promotion.md` 확정 후 본 문서·DF(Human Review #6)·DI·DM·DL에 소급 반영 필요 |
| 7 | **[Promotion 관련]** REQ-CAT-054~055 기획전 배너 동기화 이벤트의 Promotion 측 발행 여부 | 사용자 확인(2026-11-06) — Promotion이 기획전 등록·수정 시 이벤트를 실제로 발행하는지 work-scope(Catalog 한정)상 이 세션에서 확인 불가. Promotion 담당자 확인 필요. 동일 쟁점이 DBA §6 Human Review #11~12, DF Human Review #7~8에도 기록됨 |
| 8 | REQ-CAT-019 브랜드 마스터 엔티티 필요 여부 | DBA에 더 이상 전용 "브랜드 마스터" 섹션이 없고 §1.2.2 카테고리별 필수속성 예시(브랜드)로만 흡수돼 있다 — 별도 브랜드 마스터 엔티티·관리 화면이 실제로 필요한지 DF ERD 작성 전 확인 필요 |
| 9 | REQ-CAT-070 상품정보제공고시 법정 항목 확정 | DBA §1.3.8·§6 HR #36과 동일 쟁점 — 의류·신발/건강기능식품 항목은 참고용(법무 검토 전)이므로 정확한 항목·표기 문구는 법무팀 확인 후 EARS에도 소급 반영 필요 |
| 10 | **[Member 관련]** REQ-CAT-062 찜 데이터와 회원 탈퇴 연동 | DBA §1.14·§6 HR #35와 동일 쟁점 — 회원 탈퇴 시 찜 데이터 정리가 Member의 탈퇴 이벤트 구독에 의존하는데, Member 쪽 실제 발행 여부는 work-scope상 확인 불가 |
| 11 | ~~REQ-CAT-072 전시카테고리별 상품 정렬을 소비하는 고객 화면 부재~~ | **해소(2026-11-09)** — REQ-CAT-029가 전시 카테고리 기준으로 재정의되면서 해소됨(DBA §6 HR #37과 동일) |
| 12 | REQ-CAT-075 랭킹 "실시간" 기준(최근 3시간)·"보존기간"(14일) 수치 | 사용자 확인(2026-11-09) — 대략적인 방향(캘린더 고정이 아닌 rolling window)만 합의됐고, 정확한 시간 수치는 운영 지표를 보며 조정 가능한 설정값으로 둔다. DBA §1.17·§2.13 Human Review와 동일 쟁점 |

---

## 근거

> **원칙**: 구조설계 단계(DC 이후) 산출물은 AS-IS 정책서를 직접 인용하지 않는다. DBA가 1차
> 근거이며, 범위정의 단계 산출물(DB 도메인정의서)은 계속 인용 가능하다.

| 항목 | 출처 |
|---|---|
| 유스케이스 도출 (업무그룹 9개 구조 동일 적용) | `deliverables/S2-구조설계/DC-상위유스케이스/catalog.md` |
| 상품등록·심사(직매입/입점형 분기, 상태, 심사정책, 복제·대량등록) | `deliverables/S2-구조설계/DBA-도메인정책서/catalog.md` §1.5·§1.6 |
| 상품정보관리(기본정보·이미지·단종·상품정보제공고시) | `deliverables/S2-구조설계/DBA-도메인정책서/catalog.md` §1.3·§1.9·§1.11 |
| 상품 요약·태그 입력 제한(REQ-CAT-079) | DBA §1.3.1·§1.3.3·§1.3.4 — 기존 정책이었으나 DD·DF에 EARS·ERD로 반영되지 않았던 공백을 2026-11-09 소급 반영 |
| 옵션값 이미지 등록·1단계 제한(REQ-CAT-080~081) | DBA §1.4.1(2026-11-09 신설) — 사용자 지시, 상품등록 전시 탭 설계 검토 과정에서 도출 |
| 상품 단위 전시여부·검색노출 제외(REQ-CAT-082~083) | DBA §2.16(2026-11-09 신설) — 사용자 지시, SCR-A-C04-T6(전시 탭) 설계 검토 중 탭 폐지·기본정보 탭 통합 결정으로 도출 |
| 재고관리(재고-상태 연동, 자동전환 대안A, 재고임박알림, 랭킹 집계) | `deliverables/S2-구조설계/DBA-도메인정책서/catalog.md` §1.10·§1.17(2026-11-09 신설) |
| 가격관리(가격 3단 구조, 판매가 기간별 스케줄 분리, 주문수량제한) | `deliverables/S2-구조설계/DBA-도메인정책서/catalog.md` §1.7.1·§1.7.2·§1.8 |
| 분류체계관리 | `deliverables/S2-구조설계/DBA-도메인정책서/catalog.md` §1.2·§2.5 |
| 전시카테고리 상품순서(저장·정렬) | DBA §2.5.3(2026-11-09 신설) |
| 고객 상품 목록·검색의 카테고리 기준(전시 카테고리로 변경), 전시카테고리 목록 조회 | DBA §2.5.1~§2.5.2(2026-11-09 재정의) |
| SKU·옵션 | `deliverables/S2-구조설계/DBA-도메인정책서/catalog.md` §1.4 |
| 고객조회(재입고알림·찜하기·SNS공유) | `deliverables/S2-구조설계/DBA-도메인정책서/catalog.md` §1.10·§1.14·§1.16 |
| 노출로직(출시일게이트 C안, 화면별할인노출, 연관상품추천, MD Override, 상품뱃지, 상품 랭킹 조회) | `deliverables/S2-구조설계/DBA-도메인정책서/catalog.md` §2.4·§2.6·§2.8.1·§2.9·§2.13(2026-11-09 신설) |
| 화면관리(전시 페이지 상태, 전시여부 플래그, 빈 섹션 생략, GNB 메뉴 관리, 비홈 전시 페이지 뷰어) | `deliverables/S2-구조설계/DBA-도메인정책서/catalog.md` §2.2·§2.7.1·§2.10·§2.11·§2.14~§2.15(2026-11-09 신설) |
| 연동지원(Order·Promotion 소유권 경계) | `deliverables/S2-구조설계/DBA-도메인정책서/catalog.md` §1.13.1·§1.7.4 |
| 홈 화면 지정·섹션 resolve·이벤트 배너 동기화 | `deliverables/S2-구조설계/DBA-도메인정책서/catalog.md` §2.7.2·§2.9·§2.8.2 |
| 재고 연동 (Order↔Catalog 의존 관계) | `deliverables/S1-범위정의/DB-도메인정의서.md` §1(Order)·§3(Catalog) "의존" 행 |
| 용어 "판매자" 통일 | C2 용어 3관점 협의 (업무=판매자 / 도메인=Vendor / 앱=partner) |

> **폐기한 기존 REQ**: 구버전 REQ-CAT-030("WHEN Promotion 도메인으로부터 RatingUpdated
> 이벤트를 수신하면... 도출 근거: 도메인정의서: Review→Catalog")은 발신 도메인(Promotion)과
> 근거(Review)가 자기 모순이며, 평점·리뷰는 Community 도메인 책임이라 Catalog EARS에 포함될
> 근거가 없어 전면 재작성 시 제외했다. 구버전 REQ-CAT-031(Redis 캐시)·REQ-CAT-032
> (DISPLAY_PRICE_CHANGED 수신)은 DF ERD·DI 이벤트플로우 작성 시 필요하면 해당 산출물에서
> 재검토한다(REQ-CAT-050·051과의 관계가 Human Review #3 대상이라 현재는 중복 포함하지 않음).
>
> **2026-11-06 번호 재동기화 메모**: 이 문서는 2026-10-26 전면 재작성 당시 DBA의 구 번호
> (§2.1·§4.1·§6.1·§7.x 등)를 인용했다. DBA가 2026-11-04에 Part I/II/III 구조로 재정비되면서
> 번호가 바뀌었고(매핑표는 `DBA-도메인정책서/catalog.md` §8 "구 번호 → 신 번호 매핑" 참조),
> 이 문서는 그 사실을 반영하지 못한 채 남아있었다. 이번에 전체 "도출 근거" 열을 현재 DBA
> 번호로 재동기화하고, 그 사이 DBA에 추가된 신규 정책(복제등록·대량등록·재고임박알림·
> 주문수량제한·찜하기·최근본상품·SNS공유·상품뱃지·추천위젯 실패처리·전시여부 플래그·
> 상품정보제공고시)에 대응하는 REQ-CAT-056~070을 추가했다. 최근 본 상품 정책(DBA §1.15)은
> 클라이언트 전용 기능(서버 저장·API 없음)이라 "THE 시스템은 SHALL" 주어가 성립하지 않아
> 별도 REQ를 두지 않았다 — 상품 상세 조회는 기존 REQ-CAT-030을 그대로 재사용한다.
