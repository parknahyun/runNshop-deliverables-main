# 도메인 모델 (ERD) — Catalog

> **단계**: 구조설계
> **문서범위**: Domain
> **문서종류**: Design
>
> **작성 목적**: EARS(⑧)에서 도출된 엔티티·속성·관계를 테이블 설계로 구체화한다.
> **흐름 내 위치**: ⑧ EARS → **⑨ 도메인 모델(ERD)** → ⑩ 상태머신
> **작성 주체**: 시니어 개발자 + AI 협업 (DBA/아키텍트 검토)

| 항목 | 내용 |
|---|---|
| ID | DESIGN-ERD-CATALOG-001 |
| 상태 | **Draft** |
| 작성일 | 2026-08-21 |
| 갱신일 | 2026-11-06 |

> **2026-10-26 전면 재작성**: `DD-EARS기능요구/catalog.md`(REQ-CAT-001~051, 2026-10-26
> 전면 재작성)·`DBA-도메인정책서/catalog.md`를 기준으로 전면 재작성했다. 구버전(2026-08-21)은
> 구버전 EARS(REQ-CAT-003·005·016 등 지금은 존재하지 않는 번호)를 근거로 작성돼 있었고,
> 폐기된 요구사항의 잔재 컬럼(`avg_rating`·`review_count`·`is_redis_target`)이 남아 있었으며,
> 핵심 신규 정책(출시일 노출 게이트, 직매입/입점형 분기, 재고 자동전환 대안A, 판매자 단위
> 배송, 연관상품 추천)을 반영할 엔티티·속성이 전혀 없었다.
>
> **2026-10-26 추가 수정 (판매가 구조 분리)**: `cat_product.price_sale`을 Promotion이 직접
> 덮어쓰는 구조는 "마스터 속성(거의 불변)"과 "수시로 변동하는 속성"을 같은 테이블에 섞는
> 문제가 있었다(사용자 피드백). `price_sale` 컬럼을 제거하고, 시작·종료 일시를 갖는 이력성
> 테이블 `cat_product_price_schedule`로 분리했다 — 출시일 노출 게이트(§2.6 C안)와 동일하게
> "조회 시점에 기간 조건으로 유효 가격을 판정"하는 방식이라, Promotion이 정시각에 정확히
> 반영하지 못하는 문제(배치 지연 등)도 함께 해소된다. 미래 가격도 미리 INSERT해두면 해당
> 시각 도래 즉시 조회에 반영된다.
>
> **2026-10-26 추가 수정 (홈 화면 설정·이벤트 배너 동기화)**: mobile 홈 화면(`/`)이 메뉴구조도
> (DE)에는 있었으나 실제로는 화면·API 설계가 빠져 있던 공백을 메운다(사용자 피드백). `cat_display_page`
> 중 하나를 "홈"으로 지정하는 `is_home` 플래그를 추가하고, 홈 화면의 "이벤트목록" 섹션이
> 가리키는 Promotion 기획전 배너를 캐시하는 `cat_event_banner_schedule`을 신설했다 — 기획전은
> 미리 등록해두고 기간이 되면 노출되는 특성이 있어, 판매가(§4.1-1)와 동일한 "이벤트 기반 동기화
> + 조회 시점 판정" 패턴을 재사용한다(최초 스냅샷만 복사하는 방식은 Promotion 쪽 변경 시
> 동기화가 끊기는 문제가 있어 폐기).
>
> **원칙**: 구조설계 단계 산출물은 AS-IS 정책서를 직접 인용하지 않는다. `DD-EARS기능요구/
> catalog.md`·`DBA-도메인정책서/catalog.md`가 1차 근거이며, 범위정의 단계 산출물(DB
> 도메인정의서)은 계속 인용 가능하다.
>
> **2026-11-06 재동기화**: DBA가 2026-11-04에 Part I/II/III 구조로 번호를 전면 재정비해 이
> 문서가 인용하던 옛 번호(§2.1·§4.1·§6.x·§7.x 등)를 전부 현재 번호로 교체했다. 또한 DBA가
> 그 사이 추가한 정책을 반영해 스키마를 보강했다 — ① `cat_sku.sold_quantity_total`(판매량
> 순위 `sales_rank` 산정 기준, 기존에 컬럼 자체가 없었던 결함) 신설, ② `cat_product.
> max_order_quantity`(주문 수량 제한)·`restock_alert_threshold`(재고 품절임박 기준수량)·
> `compliance_info_json`(상품정보제공고시) 신설, ③ `cat_display_page.is_exposed`(전시여부
> 플래그) 신설, ④ `cat_display_section.display_style`(전시유형 축) 신설, ⑤ `cat_product_wishlist`
> (찜하기) 테이블 신설. 최근 본 상품(DBA §1.15)·SNS 공유(DBA §1.16)는 클라이언트 전용이거나
> 신규 데이터가 없어 스키마 영향이 없다.

---

## 개념 구분: 직매입 vs 입점형 (경로 판별 방식)

> Promotion DF의 "할인 vs 쿠폰" 구분과 동일하게, Catalog도 등록 경로에 따라 상태 전이 경로가
> 달라진다. 다만 Promotion처럼 테이블을 분리하지 않고 **`cat_product` 단일 테이블 + `is_direct_sourced`
> 플래그**로 구분한다 — 직매입/입점형은 속성(가격구조·옵션 등)이 완전히 동일하고 "등록 주체·
> 심사 여부"만 다르기 때문이다(테이블 자체를 분리할 만큼 속성이 달라지는 Promotion의 할인
> 종류와는 성격이 다름).

| 구분 | `is_direct_sourced` | 심사 게이트 | 상태 전이 경로 | 등록 주체 |
|---|---|---|---|---|
| 직매입 | `TRUE` | 생략 | `DRAFT → ON_SALE` (즉시) | 관리자(MD, 직매입등록자) |
| 입점형 | `FALSE` | 필수 | `DRAFT → REVIEW_REQUESTED → UNDER_REVIEW → ON_SALE/REJECTED` | 판매자 |

→ DBA §1.5.1·§1.9, DD REQ-CAT-001~007

---

## 개념 구분: 판매가의 "마스터 값"과 "기간별 유효 가격" 분리

> **배경(2026-10-26)**: 판매가(price_sale)는 Promotion이 행사 시작·종료 시점마다 값을
> 바꾸는 속성이라, `cat_product`(이름·카테고리 등 거의 불변인 마스터 데이터)에 같은 컬럼으로
> 두면 두 가지 문제가 생긴다 — ① 마스터 수정 트랜잭션과 Promotion의 가격 갱신 트랜잭션이
> 같은 row를 두고 경합하고, ② "지금 가격이 원래 판매가인지 행사가인지"를 cat_product만
> 보고는 구분할 수 없다(cat_price_history를 역추적해야 함). 그래서 가격을 아래 2단으로
> 분리했다.

| 단 | 저장 위치 | 특징 |
|---|---|---|
| 1단: 상품 단위 할인 (행사가·수량할인) | **`cat_product_price_schedule`** (신규, 이력성) | 시작·종료 일시를 가진 행을 미리 INSERT, 조회 시점에 유효 행 1건을 판정 |
| 2단: 주문/고객 단위 할인 (쿠폰·회원등급할인·포인트) | 컬럼 없음, **조회·주문 시점에 동적 계산** | DBA §2.8.1 화면별 할인노출 표가 이 계산 범위를 정의 |

`cat_product_price_schedule`은 "미래 가격 예약 + 사후 변경 이력"을 겸한다 — `start_at`이
미래인 행을 미리 넣어두면 그 시각이 도래하는 순간부터 조회 쿼리가 자동으로 그 행을 고른다.
출시일 노출 게이트(§2.4 C안)와 동일한 "배치 없이 조회 시점 판정" 패턴이다.

---

## 개념 구분: 홈 화면 지정과 이벤트 배너 동기화

> **배경(2026-10-26)**: mobile 홈(`/`)에 노출할 콘텐츠(배너·상품·이벤트목록·추천목록)와
> 위치는 기존 `cat_display_page`+`cat_display_section` 구조로 충분히 커버되나(사용자 확인),
> 두 가지가 새로 필요하다 — ① 여러 전시 페이지 중 "지금 홈으로 쓸 1건"을 지정하는 플래그,
> ② 이벤트목록 섹션이 가리키는 Promotion 기획전의 배너를 Catalog가 최신 상태로 들고 있을
> 동기화 체계.

| 항목 | 방식 |
|---|---|
| 홈 지정 | `cat_display_page.is_home` 플래그. 동시에 1건만 TRUE, PUBLISHED 상태인 페이지만 지정 가능 |
| 섹션 콘텐츠·위치 | 기존 `cat_display_section`(BANNER/PRODUCT_LIST/CATEGORY_GRID/CUSTOM_HTML) 재사용 + `EVENT_LIST`/`RECOMMENDATION` 2종 추가 |
| 상품 섹션(PRODUCT_LIST) | `content_json`에 상품코드만 저장, 이미지·링크는 Catalog 자체 데이터(`cat_product_image`)에서 resolve (기존 구조 그대로) |
| 이벤트 섹션(EVENT_LIST) | `content_json`에 이벤트 key(Promotion `prm_exhibition.id`, 참조값)만 저장, 배너이미지는 **`cat_event_banner_schedule`에서 resolve** |
| 추천 섹션(RECOMMENDATION) | `content_json` 없음 — 조회 시점에 외부 추천 SaaS 호출(REQ-CAT-036 기존 로직 재사용), MD가 콘텐츠를 직접 큐레이션하지 않음 |

**이벤트 배너 동기화 — 판매가(§1.7.2)와 동일한 패턴**: Promotion이 기획전을 등록·수정할 때마다
이벤트를 발행하고, Catalog가 수신해 `cat_event_banner_schedule`에 upsert한다. 홈 화면 조회
시점에 `start_at ≤ now < end_at` 조건으로 유효 배너를 판정한다(배치 없음, 미래 기간 사전
등록 가능). "최초 등록 시점의 배너를 스냅샷으로 복사"하는 방식은 Promotion이 이후 배너를
바꾸면 Catalog가 갱신되지 않는 동기화 문제가 있어 폐기했다(사용자 피드백, 2026-10-26).

> **[Human Review]** 이 동기화가 실제로 동작하려면 **Promotion이 기획전 등록·수정 시
> 이벤트를 발행해야 한다** — Promotion 쪽에 그런 이벤트 발행 로직이 실제로 있는지는 이
> 세션에서 확인되지 않았다(work-scope상 Catalog만 작업 범위라 Promotion 문서를 수정할
> 수 없음). 상세는 §Human Review, DI-이벤트플로우/catalog.md Human Review 참조.

---

## 개념 구분: 전시 콘텐츠유형 × 전시유형 2축 체계 (2026-11-06 보강)

> **배경**: DBA §2.3이 "콘텐츠유형(노출 대상)"과 "전시유형(노출 방식)" 2축 코드 체계로
> 확정되면서, 기존 `cat_display_section.section_type` 1개 컬럼만으로는 "이 섹션을 목록형으로
> 보여줄지 배너형으로 보여줄지"를 표현할 수 없게 됐다. `display_style` 컬럼을 추가해 2축을
> 모두 저장한다. 두 축의 허용 조합(배너→배너형만, 이벤트목록→배너형·스크롤형 등)은 DBA §2.3
> 표를 그대로 애플리케이션 레벨 불변식으로 적용한다(아래 불변식 섹션 참조).

| 콘텐츠유형(`section_type`) | 허용 전시유형(`display_style`) |
|---|---|
| BANNER | BANNER만 |
| EVENT_LIST | BANNER, SCROLL |
| PRODUCT_LIST | LIST, SCROLL |
| RECOMMENDATION | SCROLL만 |
| CATEGORY_GRID | LIST만 |

> **[Human Review]** `CUSTOM_HTML`은 DBA §2.3의 콘텐츠유형 5종에 포함되지 않는 기존 값이다
> (2026-11-06 이전부터 존재). 실제로 쓰이는 값인지, 쓰인다면 `display_style` 허용 매트릭스에
> 어떤 전시유형을 매핑할지 DBA 쪽 확인이 필요하다 — 당장은 매트릭스 검증 예외로 둔다.

---

## 테이블 구조

```
cat_product (상품 마스터)
  ├── cat_product_image (상품 이미지)
  ├── cat_product_option_group (옵션그룹)
  │     └── cat_product_option_value (옵션값)
  ├── cat_sku (SKU: 재고 관리 단위)
  │     ├── cat_stock_history (재고 이력)
  │     └── cat_restock_subscription (재입고 알림 신청)
  ├── cat_product_price_schedule (판매가 기간별 스케줄 — 이력+예약 겸용)
  └── cat_product_wishlist (찜하기, member_id 참조)

cat_category (표준 카테고리, 단일계층)
cat_category_attribute (카테고리별 필수 입력 속성 정의)
cat_display_category (전시 카테고리, 트리)
cat_standard_display_category_mapping (표준-전시 카테고리 N:M 매핑, is_default)
cat_product_display_category (상품-전시 카테고리 N:M 매핑, sort_order·is_pinned로 카테고리별 정렬)
cat_brand (브랜드 마스터)

cat_display_page (전시 페이지, is_home 플래그로 홈 지정, is_exposed 플래그로 긴급 회수)
  └── cat_display_section (전시 섹션, section_type×display_style 2축, EVENT_LIST/RECOMMENDATION 포함)
cat_display_template (전시 템플릿)

cat_event_banner_schedule (이벤트 배너 동기화 캐시 — Promotion 기획전 참조, 기간별 스케줄)
```

---

## DBML

```dbml
Table cat_product {
  id varchar [pk, note: 'ULID']
  name varchar [not null, note: '상품명']
  vendor_id varchar [not null, note: '판매자 ID (업무 용어: 판매자 / 도메인 용어: Vendor)']
  is_direct_sourced boolean [not null, default: false, note: 'TRUE=직매입(심사 게이트 생략) / FALSE=입점형(심사 필수). DBA §1.5.1']
  category_id varchar [not null, note: 'cat_category.id 참조 (대분류 1개만, 다중 카테고리 미허용)']
  brand_id varchar [note: 'cat_brand.id 참조']
  status varchar [not null, note: 'DRAFT / REVIEW_REQUESTED / UNDER_REVIEW / ON_SALE / SOLD_OUT / DISCONTINUED / REJECTED. REVIEW_REQUESTED·UNDER_REVIEW·REJECTED는 is_direct_sourced=FALSE 전용']
  reject_reason text [note: '반려 사유 (REJECTED 시 필수, 판매자 BO에 노출)']
  reject_count int [not null, default: 0, note: '동일 사유 반복 반려 횟수 (3회 이상 시 에스컬레이션, REQ-CAT-009)']
  rejected_at timestamp [note: '최근 반려 시각 (재제출 기한 30일 산정 기준, DBA §1.6)']
  price_original int [not null, note: '정가 (price_original ≥ 유효판매가 ≥ price_supply). 판매자/MD가 설정하는 마스터 속성']
  price_supply int [not null, note: '판매자 공급가 (정산 계산 기준, 고객 미노출). 마스터 속성']
  release_date date [note: '출시일. NULL이면 즉시 노출(하위호환). 설정 시 release_date > now인 동안 목록·검색·전시·상세에서 제외 (DBA §2.4 C안, 상태 전이 없음). REQ-CAT-033~034']
  description text [note: '상품 상세 설명 (HTML/Markdown)']
  summary varchar(200) [note: '상품 요약 (평문, HTML 불허, 최대 200자). 목록 카드·검색결과에서 상품명 아래 서브타이틀로 노출. 선택 입력. DBA §1.3.1·§1.3.3(기존 정책 — 2026-11-09 DF 소급 반영, REQ-CAT-063 공유 메타데이터·REQ-CAT-056 복제등록이 이미 이 필드 존재를 전제로 작성돼 있었음)']
  tags varchar(255) [note: '검색 키워드 (쉼표 구분, 최대 10개, 특수문자·공백 제한). Search 도메인 색인 데이터로 제공되어 키워드 매칭에 사용. 선택 입력. DBA §1.3.1·§1.3.4(기존 정책 — 2026-11-09 DF 소급 반영, REQ-CAT-056 복제등록이 이미 이 필드 존재를 전제로 작성돼 있었음)']
  is_exposed boolean [not null, default: true, note: '상품 단위 전시여부(수동 숨김). FALSE면 상태·재고와 무관하게 목록·검색·전시 영역·상세 딥링크 전부에서 제외(cat_display_page.is_exposed·release_date 노출 게이트와 동일 패턴). 단종과 달리 가역적. DBA §2.16(2026-11-09 신설) — SCR-A-C04-T6(전시 탭) 폐지, 기본정보 탭에 통합']
  is_search_excluded boolean [not null, default: false, note: '검색노출 제외(보조 플래그). TRUE면 목록·카테고리·상세는 정상 노출하되 검색 결과(§18)에서만 제외. is_exposed=TRUE인 상품에만 의미가 있음. DBA §2.16(2026-11-09 신설)']
  exposure_md_override int [note: '관리자(MD) 수동 노출 순서 (NULL이면 미설정). exposure_priority = COALESCE(이 값, sales_rank 집계값, default_order) — DBA §2.6. 현재는 2단계 공식이며, AI 스코어링 배치 도입 시 md_override와 sales_rank 사이에 exposure_ai_score가 3단계로 삽입될 예정']
  exposure_ai_score decimal [note: 'AI 추천 점수 배치 결과 (2단계 운영 안정화 이후 도입 예정 — 현재 exposure_priority 공식에는 미포함, NULL 허용). DBA §2.6 3단계(확장 지점)']
  max_order_quantity int [note: '1회 주문 내 최대 수량(상품에 속한 전체 SKU 합산 기준). NULL=무제한. 실제 검증은 Order가 수행, Catalog는 값만 제공. DBA §1.8(2026-11-06 신설)']
  restock_alert_threshold int [not null, default: 5, note: '재고 품절임박 알림 기준수량(상품 단위, 소속 SKU 공통 적용). 판매자가 상품별로 변경 가능. DBA §1.10(2026-11-06 신설)']
  compliance_info_json text [note: '전자상거래법 상품정보제공고시 항목(대분류별 가변 키-값, 예: 소재·원산지·A/S책임자 또는 섭취방법·유통기한). DBA §1.3.8(2026-11-06 신설) — 정확한 키 목록은 법무 확인 전이라 §6 Human Review #10 대상']
  created_at timestamp [not null]
  updated_at timestamp [not null]
  is_deleted boolean [default: false]

  indexes {
    vendor_id [name: 'idx_product_vendor']
    category_id [name: 'idx_product_category']
    brand_id [name: 'idx_product_brand']
    (status, created_at) [name: 'idx_product_status_date']
    (status, release_date) [name: 'idx_product_status_release']
    name [name: 'idx_product_name']
    (status, is_exposed, release_date) [name: 'idx_product_exposure', note: '목록·검색·전시 조회의 3단 노출 게이트(status∈{ON_SALE,SOLD_OUT} AND is_exposed=TRUE AND release_date≤now) 공통 인덱스, 2026-11-09 신설']
  }

  note: '상품 마스터. REQ-CAT-001~010, REQ-CAT-015, REQ-CAT-026~027, REQ-CAT-033~034, REQ-CAT-037, REQ-CAT-056·058·059b·070. 판매가(price_sale)는 cat_product_price_schedule로 분리(마스터 속성 아님)'
}

Table cat_product_image {
  id varchar [pk, note: 'ULID']
  product_id varchar [not null, ref: > cat_product.id]
  image_url varchar [not null, note: 'CDN 경로']
  sort_order int [not null, default: 0, note: '정렬 순서']
  image_type varchar [not null, default: 'DETAIL', note: 'MAIN / DETAIL / THUMBNAIL']
  created_at timestamp [not null]

  indexes {
    product_id [name: 'idx_pimg_product']
    (product_id, sort_order) [name: 'idx_pimg_sort']
  }

  note: 'REQ-CAT-011~012: 상품 이미지 (최대 10장). 상품 복제등록(REQ-CAT-056) 시 원본 image_url을 그대로 참조하는 신규 row를 생성(파일 재업로드 없음)'
}

Table cat_product_option_group {
  id varchar [pk, note: 'ULID']
  product_id varchar [not null, ref: > cat_product.id]
  name varchar [not null, note: '옵션그룹명 (예: 색상, 사이즈)']
  depth int [not null, note: '1 또는 2 (옵션 깊이 최대 2단계)']
  sort_order int [not null, default: 0]
  created_at timestamp [not null]

  indexes {
    product_id [name: 'idx_optgrp_product']
  }

  note: '옵션그룹. REQ-CAT-013~014 (최대 2단계)'
}

Table cat_product_option_value {
  id varchar [pk, note: 'ULID']
  option_group_id varchar [not null, ref: > cat_product_option_group.id]
  value varchar [not null, note: '옵션값 (예: Red, XL)']
  sort_order int [not null, default: 0]
  image_url varchar [note: '옵션값 이미지(색상 스와치 등 CDN 경로). NULL 허용. 소속 옵션그룹의 depth=1인 옵션값에만 설정 가능 — depth=2(예: 사이즈)는 거부(OPTION_IMAGE_DEPTH_INVALID). DBA §1.4.1(2026-11-09 신설)']
  created_at timestamp [not null]

  indexes {
    option_group_id [name: 'idx_optval_group']
  }

  note: '옵션값. REQ-CAT-013, REQ-CAT-080~081(옵션값 이미지, 2026-11-09 신설)'
}

Table cat_sku {
  id varchar [pk, note: 'ULID']
  product_id varchar [not null, ref: > cat_product.id]
  option_values_json varchar [note: 'JSON: 선택된 옵션값 조합 (예: {"색상":"Red","사이즈":"XL"}). 옵션 없는 단일상품은 NULL']
  stock_quantity int [not null, default: 0, note: '총 재고 수량']
  available_quantity int [not null, default: 0, note: '가용 재고 (stock - 선점분). 불변식: 0 ≤ available ≤ stock']
  sold_quantity_total int [not null, default: 0, note: '누적 판매량 (2026-11-06 신설, 기존 모델링 공백). 주문발생(RESERVE) 시 +, 주문취소·반품확정(검수완료) 시 -, 판매자 재고 신규등록(RESTOCK_VENDOR)은 영향 없음. 상품 단위 sales_rank(DBA §2.6 추천순 2단계, §2.6 BEST 뱃지)는 소속 SKU 전체의 이 값을 합산해 산정 — 재고와 같은 변동성 테이블에 둠(마스터 테이블인 cat_product가 아님)']
  sku_code varchar [note: '외부 SKU 코드']
  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    product_id [name: 'idx_sku_product']
    (product_id, option_values_json) [unique, name: 'uq_sku_option']
    sold_quantity_total [name: 'idx_sku_sold_qty']
  }

  note: 'SKU: 재고 관리 단위. REQ-CAT-013, REQ-CAT-020~025, REQ-CAT-045~047, REQ-CAT-058~059(재고임박알림), REQ-CAT-065(BEST 뱃지)'
}

Table cat_stock_history {
  id varchar [pk, note: 'ULID']
  sku_id varchar [not null, ref: > cat_sku.id]
  change_type varchar [not null, note: 'RESERVE(선점/차감) / RESTORE_ORDER_CANCEL / RESTORE_RETURN_EXCHANGE / RESTOCK_VENDOR(판매자 신규등록) / MANUAL_ADJUST']
  change_quantity int [not null, note: '변동 수량 (+/-)']
  after_stock int [not null, note: '변동 후 총 재고']
  after_available int [not null, note: '변동 후 가용 재고']
  reason_ref varchar [note: '변동 근거 참조 (order_id 등)']
  created_at timestamp [not null]

  indexes {
    sku_id [name: 'idx_sthist_sku']
    (sku_id, created_at) [name: 'idx_sthist_sku_date']
  }

  note: 'REQ-CAT-024: 모든 재고 변동(차감·복원·신규등록)을 변동사유·수량·시점과 함께 기록. change_type이 DBA §1.10 "발생원인"과 1:1 대응'
}

Table cat_product_sales_hourly {
  product_id varchar [not null, ref: > cat_product.id]
  sale_hour timestamp [not null, note: '시간 단위 truncate (예: 2026-11-09 14:00:00, Asia/Seoul 기준)']
  quantity int [not null, default: 0, note: '해당 시간대 순 판매량. StockChanged 이벤트의 changeType=RESERVE 시 +, RESTORE_ORDER_CANCEL 시 -. RESTORE_RETURN_EXCHANGE·RESTOCK_VENDOR는 집계 제외(DBA §1.17, 2026-11-09 신설)']

  indexes {
    (product_id, sale_hour) [pk, name: 'pk_sales_hourly']
    (sale_hour, quantity) [name: 'idx_sales_hourly_rank']
  }

  note: 'REQ-CAT-074~075: 상품 랭킹(실시간/일간/주간) 집계 소스. sold_quantity_total(전체기간 누적, cat_sku 소유)과는 목적이 다른 별도 지표 — 쓰기는 StockChanged를 비동기로 구독해 처리(재고 트랜잭션과 분리). 보존기간 14일, 만료분은 저빈도 정리 배치로 삭제(DBA §1.17)'
}

Table cat_restock_subscription {
  id varchar [pk, note: 'ULID']
  sku_id varchar [not null, ref: > cat_sku.id]
  customer_id varchar [not null, note: '알림 신청 고객']
  status varchar [not null, default: 'PENDING', note: 'PENDING / NOTIFIED']
  created_at timestamp [not null]
  notified_at timestamp [note: '알림 발송 시각 (SOLD_OUT→ON_SALE 전환 시)']

  indexes {
    (sku_id, status) [unique, name: 'uq_restock_sku_pending', note: 'SKU당 유효(PENDING) 신청은 1건만 — DBA §1.10 중복 신청 방지']
    customer_id [name: 'idx_restock_customer']
  }

  note: 'REQ-CAT-032: 재입고 알림 신청. 재입고 자동전환(REQ-CAT-022) 발생 시 PENDING 건을 NOTIFIED로 전환하며 발송'
}

Table cat_product_wishlist {
  id varchar [pk, note: 'ULID']
  product_id varchar [not null, ref: > cat_product.id]
  member_id varchar [not null, note: '찜한 회원 ID. Catalog는 참조값으로만 저장(회원 자격·탈퇴 관리는 Member 소관)']
  created_at timestamp [not null]

  indexes {
    (product_id, member_id) [unique, name: 'uq_wishlist_product_member', note: '상품당 회원 1건, 중복 찜 불가']
    member_id [name: 'idx_wishlist_member', note: '마이페이지 "찜한 상품" 목록 조회용']
  }

  note: '찜하기(위시리스트). REQ-CAT-061~062(2026-11-06 신설) — 상품이 SOLD_OUT/DISCONTINUED로 전환되면 해당 product_id의 행을 전부 물리 삭제(재입고돼도 복원 안 함). DBA §1.14'
}

Table cat_product_price_schedule {
  id varchar [pk, note: 'ULID']
  product_id varchar [not null, ref: > cat_product.id]
  price int [not null, note: '해당 기간 동안의 유효 판매가']
  source_type varchar [not null, note: 'BASE(기본 판매가) / PROMOTION_EVENT(행사가) / QUANTITY_DISCOUNT(수량할인)']
  source_event_id varchar [note: 'Promotion 쪽 행사/할인 ID. source_type=BASE면 NULL']
  start_at timestamp [not null, note: '유효 시작 일시. 미래 시각으로 미리 INSERT 가능(예약) — 해당 시각 도래 즉시 조회에 반영, 별도 배치 불필요. yyyy.mm.dd hh:mi:ss 형식']
  end_at timestamp [note: '유효 종료 일시. NULL=무기한(기본 판매가 등). yyyy.mm.dd hh:mi:ss 형식']
  created_by varchar [not null, note: '등록자 ID (vendor_id/admin_id, Promotion 연동이면 SYSTEM_PROMOTION)']
  created_at timestamp [not null]

  indexes {
    (product_id, start_at, end_at) [name: 'idx_pps_product_period']
    source_event_id [name: 'idx_pps_source_event']
  }

  note: 'REQ-CAT-026: 판매가 기간별 스케줄(이력+예약 겸용). 유효 가격 조회: WHERE product_id=? AND start_at<=now AND (end_at IS NULL OR end_at>now), 중복 시 판정 규칙은 Human Review #6'
}

Table cat_category {
  id varchar [pk, note: 'ULID']
  name varchar [not null, note: '카테고리명 (대분류, 단일계층 — 중·소분류 없음)']
  sort_order int [not null, default: 0]
  is_active boolean [default: true]
  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    sort_order [name: 'idx_cat_sort']
  }

  note: '표준 카테고리 (단일 계층). REQ-CAT-016~017 — 상품은 대분류 1개에만 귀속, 다중 카테고리 미허용. DBA §1.2.1'
}

Table cat_category_attribute {
  id varchar [pk, note: 'ULID']
  category_id varchar [not null, ref: > cat_category.id]
  attribute_name varchar [not null, note: '필수 입력 속성명 (예: 브랜드, 사이즈, 드롭, 용량)']
  is_required boolean [not null, default: true]
  sort_order int [not null, default: 0]

  indexes {
    category_id [name: 'idx_cattr_category']
  }

  note: '카테고리별 필수 입력 속성 정의. DBA §1.2.2 — 전체 대분류×속성 매트릭스는 Human Review #4, 현재는 예시(러닝화·보충제) 수준만 확정'
}

Table cat_display_category {
  id varchar [pk, note: 'ULID']
  parent_id varchar [note: '상위 전시 카테고리 (NULL이면 루트)']
  name varchar [not null, note: '전시 카테고리명']
  depth int [not null, default: 1]
  sort_order int [not null, default: 0]
  is_active boolean [default: true]
  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    parent_id [name: 'idx_dcat_parent']
  }

  note: '전시 카테고리 (트리, 표준 카테고리와 별개 축). REQ-CAT-018, DBA §2.5.1'
}

Table cat_standard_display_category_mapping {
  id varchar [pk, note: 'ULID']
  category_id varchar [not null, ref: > cat_category.id, note: '표준 카테고리(소분류 — 현재 cat_category는 단일계층이라 대분류 자체를 가리킴)']
  display_category_id varchar [not null, ref: > cat_display_category.id]
  is_default boolean [not null, default: false, note: 'TRUE면 이 표준 카테고리로 등록되는 상품이 자동으로 해당 전시 카테고리에 매핑됨(cat_product_display_category 자동 생성 기준). 표준 카테고리 1건당 is_default=TRUE 매핑은 최대 1건']
  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    (category_id, display_category_id) [unique, name: 'uq_sdcm_pair']
    category_id [name: 'idx_sdcm_category', note: '상품 등록 시 is_default=TRUE 매핑 조회(자동 매핑 대상 판정)용']
  }

  note: '표준-전시 카테고리 N:M 매핑(2026-11-09 신설). DBA §2.5.2 — 전시 카테고리 1건에 여러 표준 카테고리가, 표준 카테고리 1건이 여러 전시 카테고리에 매핑 가능'
}

Table cat_product_display_category {
  id varchar [pk, note: 'ULID']
  product_id varchar [not null, ref: > cat_product.id]
  display_category_id varchar [not null, ref: > cat_display_category.id]
  is_auto_mapped boolean [not null, default: false, note: 'TRUE=cat_standard_display_category_mapping.is_default 매핑으로 자동 생성, FALSE=MD·판매자가 수동 추가']
  sort_order int [not null, default: 0, note: '전시 카테고리 내 노출 순서(낮을수록 먼저). 관리자가 드래그앤드랍으로 재배열한 리스트 순서를 그대로 0부터 저장. DBA §2.5.3(2026-11-09 신설)']
  is_pinned boolean [not null, default: false, note: '상단 고정 여부. TRUE인 행은 sort_order와 무관하게 항상 먼저 노출되고, 고정된 상품들 사이의 순서는 sort_order로 정렬. DBA §2.5.3(2026-11-09 신설)']
  created_at timestamp [not null]

  indexes {
    (product_id, display_category_id) [unique, name: 'uq_pdc_pair']
    (display_category_id, is_pinned, sort_order) [name: 'idx_pdc_display_order', note: '전시 카테고리별 상품 목록 정렬 조회용 — ORDER BY is_pinned DESC, sort_order ASC']
  }

  note: '상품-전시 카테고리 N:M 매핑. DBA §2.5.2 — 상품 등록 시 표준 카테고리의 기본 매핑(is_default)이 있으면 자동 생성, MD·판매자가 추가 전시 카테고리를 수동으로 더 매핑 가능. 카테고리별 정렬·고정은 DBA §2.5.3(2026-11-09 신설)'
}

Table cat_brand {
  id varchar [pk, note: 'ULID']
  name varchar [not null, note: '브랜드명']
  logo_url varchar [note: '브랜드 로고']
  is_active boolean [default: true]
  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    name [unique, name: 'uq_brand_name']
  }

  note: '브랜드 마스터. REQ-CAT-019 — DBA에는 더 이상 전용 섹션이 없고 §1.2.2 예시로만 흡수돼 있어, 이 테이블이 실제로 필요한지 Human Review 대상(DD HR #8과 동일 쟁점)'
}

Table cat_display_page {
  id varchar [pk, note: 'ULID']
  title varchar [not null, note: '페이지 제목']
  slug varchar [not null, note: 'URL 슬러그']
  status varchar [not null, note: 'DRAFT(대기) / PUBLISHED(진행) / CLOSED(종료) / CANCELLED(취소), 2026-11-09 4개로 단순화(舊 DRAFT_EDIT·SCHEDULED·RESERVED 제거). 전이 규칙은 DH-상태머신/catalog.md가 Single Source of Truth']
  is_exposed boolean [not null, default: true, note: '전시여부(긴급 게시·회수 플래그). 상태 전이와 별개 축 — 노출 조건은 status=PUBLISHED AND is_exposed=TRUE. 운영자가 즉시 FALSE로 전환해 노출을 끄고 TRUE로 되돌리면 즉시 복원(상태·전시기간·is_home 어느 것도 변경하지 않음). DBA §2.10']
  template_id varchar [ref: > cat_display_template.id]
  is_home boolean [not null, default: false, note: '홈(mobile "/") 화면으로 노출할 페이지 지정. 동시에 1건만 TRUE, PUBLISHED 상태에서만 TRUE 가능. is_exposed=FALSE가 되면 "홈 미지정"과 동일하게 처리해 기본 카테고리 화면으로 대체 노출(is_home 값 자체는 유지)']
  display_start_at timestamp [note: '전시 시작일시(2026-11-09 신설, 舊 scheduled_at). NULL이거나 이미 지난 시각이면 "즉시 게시"로 바로 PUBLISHED, 미래 시각이면 배치가 그 시각 도달 시 DRAFT→PUBLISHED로 자동 전환. yyyy.mm.dd hh:mi:ss 형식']
  display_end_at timestamp [note: '전시 종료일시(2026-11-09 신설). 설정 시 display_start_at보다 이후여야 하며, 그 시각 도달 시 배치가 PUBLISHED→CLOSED로 자동 전환. NULL이면 수동 종료만. yyyy.mm.dd hh:mi:ss 형식']
  published_at timestamp [note: '실제 게시 시각']
  closed_at timestamp [note: '종료 시각']
  created_by varchar [not null, note: '생성자 (admin_id)']
  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    status [name: 'idx_dpage_status']
    slug [unique, name: 'uq_dpage_slug']
    display_start_at [name: 'idx_dpage_display_start']
    display_end_at [name: 'idx_dpage_display_end']
    is_home [unique, name: 'uq_dpage_home', note: 'is_home=true인 행은 전체 테이블에서 최대 1건 (partial unique index)']
    (status, is_exposed) [name: 'idx_dpage_exposure', note: '노출 쿼리 필터(status=PUBLISHED AND is_exposed=TRUE)용']
  }

  note: '전시 페이지. REQ-CAT-038~043, REQ-CAT-052(홈 지정), REQ-CAT-068(전시여부 플래그)'
}

Table cat_display_section {
  id varchar [pk, note: 'ULID']
  page_id varchar [not null, ref: > cat_display_page.id]
  section_type varchar [not null, note: '콘텐츠유형(노출 대상). BANNER / EVENT_LIST / PRODUCT_LIST / RECOMMENDATION / CATEGORY_GRID(DBA §2.3 5종) + CUSTOM_HTML(레거시, DBA 5종에 없음 — Human Review #12)']
  display_style varchar [not null, note: '전시유형(노출 방식, 2026-11-06 신설). LIST(목록형) / SCROLL(스크롤형) / BANNER(배너형). section_type별 허용 조합은 상단 "전시 콘텐츠유형×전시유형" 표(DBA §2.3) 참조 — BANNER→BANNER만, EVENT_LIST→BANNER·SCROLL, PRODUCT_LIST→LIST·SCROLL, RECOMMENDATION→SCROLL만, CATEGORY_GRID→LIST만']
  title varchar [note: '섹션 제목']
  content_json text [note: '섹션 콘텐츠. PRODUCT_LIST={productIds:[]}(상품코드만, 이미지는 cat_product_image에서 resolve) / EVENT_LIST={eventKeys:[]}(Promotion 기획전 ID만, 배너는 cat_event_banner_schedule에서 resolve) / RECOMMENDATION=NULL(외부 SaaS 실시간 호출, REQ-CAT-036 재사용) / BANNER=자체 이미지URL+링크']
  sort_order int [not null, default: 0]
  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    page_id [name: 'idx_dsec_page']
    (page_id, sort_order) [name: 'idx_dsec_sort']
  }

  note: '전시 섹션. DBA §2.2 MD 수동 운영 영역·§2.3(콘텐츠유형·전시유형 2축), REQ-CAT-053(홈 화면 섹션 resolve), REQ-CAT-069(빈 섹션은 노출 시 생략)'
}

Table cat_event_banner_schedule {
  id varchar [pk, note: 'ULID']
  source_event_id varchar [not null, note: 'Promotion 기획전 ID(prm_exhibition.id) 참조값. Catalog는 FK 강제하지 않음(교차 도메인)']
  banner_image_url varchar [not null, note: '배너 이미지 URL']
  title varchar [note: '배너 타이틀(대체 텍스트 등)']
  link_target varchar [note: '클릭 시 이동 경로. 보통 source_event_id로 Promotion 기획전 상세를 구성']
  start_at timestamp [not null, note: '유효 시작 일시. 미래 시각 사전 등록 가능(예약) — cat_product_price_schedule과 동일 패턴. yyyy.mm.dd hh:mi:ss 형식']
  end_at timestamp [note: '유효 종료 일시. NULL이면 무기한. 중도 취소 시 end_at=now로 종료 처리(물리 삭제 아님). yyyy.mm.dd hh:mi:ss 형식']
  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    (source_event_id, start_at, end_at) [name: 'idx_ebs_event_period']
  }

  note: 'REQ-CAT-054~055: Promotion 기획전 배너 동기화 캐시(이벤트 수신 upsert). 유효 배너 조회: WHERE source_event_id=? AND start_at<=now AND (end_at IS NULL OR end_at>now). [Human Review] Promotion이 이 동기화용 이벤트를 실제로 발행하는지 미확인'
}

Table cat_display_template {
  id varchar [pk, note: 'ULID']
  name varchar [not null, note: '템플릿명']
  layout_json text [not null, note: '레이아웃 정의 (섹션 배치 규칙)']
  is_active boolean [default: true]
  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    name [unique, name: 'uq_template_name']
  }

  note: '전시 템플릿'
}

Table cat_gnb_menu {
  id varchar [pk, note: 'ULID']
  name varchar [not null, note: '메뉴명']
  link_type varchar [not null, note: 'DISPLAY_PAGE / DISPLAY_CATEGORY / RANKING / EVENT_PAGE / EXTERNAL_URL']
  link_target varchar [not null, note: 'link_type별 참조값. DISPLAY_PAGE=cat_display_page.slug, DISPLAY_CATEGORY=cat_display_category.id, RANKING=고정 경로(period 파라미터), EVENT_PAGE·EXTERNAL_URL=URL 문자열(검증 없음, cat_event_banner_schedule.link_target과 동일 패턴)']
  sort_order int [not null, default: 0, note: '오름차순 정렬. 상단고정 개념 없음(단순 정렬만)']
  is_exposed boolean [not null, default: true, note: '전시여부. cat_display_page.is_exposed와 동일 패턴 — 상태 전이 없이 조회 쿼리에서만 필터링']
  display_start_at timestamp [note: '전시 시작일시. NULL=즉시(하위호환). yyyy.mm.dd hh:mi:ss 형식']
  display_end_at timestamp [note: '전시 종료일시. NULL=무기한. yyyy.mm.dd hh:mi:ss 형식']
  created_by varchar [not null, note: '등록자 ID (admin_id)']
  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    sort_order [name: 'idx_gnb_sort']
  }

  note: 'REQ-CAT-076~077(2026-11-09 신설): 홈 화면(mobile) Header 하단 퀵메뉴 바. 단일 계층(서브메뉴 없음), 홈 화면 전용 노출(PC 채널 생기면 재검토). 유효 노출 조회: WHERE is_exposed=true AND (display_start_at IS NULL OR display_start_at<=now) AND (display_end_at IS NULL OR display_end_at>now) ORDER BY sort_order ASC'
}
```

---

## 불변식 (Invariants)

| 불변식 | 검증 시점 | 도출 근거 |
|---|---|---|
| `cat_sku.available_quantity ≥ 0` | 재고 차감 시 | REQ-CAT-023: 가용 재고 미만 차감 거부(INSUFFICIENT_STOCK) |
| `cat_sku.available_quantity ≤ cat_sku.stock_quantity` | 재고 변동 시 | 논리적 제약: 가용 ≤ 총재고 |
| `cat_sku.sold_quantity_total ≥ 0` | 재고 변동 시 | DBA §1.10·§2.6 — 누적 판매량은 음수가 될 수 없음(주문취소·반품 복원 시에도 원 주문 발생분을 초과해 차감하지 않음) |
| `cat_product.price_original ≥ cat_product_price_schedule.price(유효건) ≥ cat_product.price_supply` | 가격 설정·변경 시 | REQ-CAT-027: 가격 구조 불변식 위반 시 설정 거부 |
| `cat_product_price_schedule`은 동일 product_id 기준 조회 시점(now)에 유효 건이 정확히 1건으로 판정되어야 함 (중복 허용 시 우선순위 규칙 필요) | 조회·등록 시 | Human Review #6 — Promotion 중복 할인 정책 미확정 |
| `cat_product_image` 동일 product_id 건수 ≤ 10 | 이미지 등록 시 | REQ-CAT-012: 상품당 최대 10장 |
| `cat_product_option_group.depth` ∈ {1, 2} | 옵션그룹 생성 시 | REQ-CAT-014: 옵션 깊이 최대 2단계 |
| `cat_product_option_value.image_url`이 NOT NULL이면 소속 `cat_product_option_group.depth = 1` | 옵션값 이미지 등록 시 | REQ-CAT-081(2026-11-09 신설): 옵션값 이미지는 1단계(예: 색상)에만 허용, 2단계(예: 사이즈) 거부 |
| `cat_product.status = REJECTED`일 때 `reject_reason IS NOT NULL` | 상태 전이 시 | REQ-CAT-006: 반려 사유 판매자 BO 기록·노출 필수 |
| `cat_product.is_direct_sourced = TRUE`인 상품은 `status ∈ {REVIEW_REQUESTED, UNDER_REVIEW, REJECTED}`를 가질 수 없음 | 상태 전이 시 | REQ-CAT-001 — 직매입은 심사 게이트 생략, DBA §1.9 |
| `cat_product.status = DISCONTINUED`로의 전이는 수동 처리만 허용 (재고 수량 트리거 없음) | 상태 전이 시 | REQ-CAT-015 — 재고 수량과 무관한 별도 의사결정 |
| `cat_product.status`가 `SOLD_OUT` 또는 `DISCONTINUED`로 전환되면 해당 `product_id`의 `cat_product_wishlist` 행을 전부 삭제 | 상태 전이 시 | REQ-CAT-062, DBA §1.14 — `DH-상태머신/catalog.md` 전이 액션에도 동일하게 반영 필요 |
| `cat_product.max_order_quantity`는 NULL 또는 1 이상의 정수 | 설정 시 | DBA §1.8 — 0 이하 값은 의미 없음(무제한은 NULL로 표현) |
| 동일 카테고리에 상품은 1개 `category_id`만 가짐 (N:M 매핑 아님) | 카테고리 지정 시 | REQ-CAT-017: 다중 카테고리 미허용 |
| `cat_product_wishlist`은 동일 `(product_id, member_id)` 조합 중복 불가 | 찜 등록 시 | DBA §1.14 — 상품당 회원 1건 |
| `cat_restock_subscription`은 동일 `sku_id`에 `status=PENDING`인 행이 2건 이상 존재할 수 없음 | 신청 시 | DBA §1.10 — SKU당 중복 신청 방지 |
| `cat_display_section.display_style`은 `section_type`별 허용 전시유형(상단 매트릭스) 안에서만 설정 가능 | 섹션 등록·수정 시 | DBA §2.3 — `CUSTOM_HTML`은 매트릭스 검증 예외(Human Review #12) |
| `cat_standard_display_category_mapping`은 `category_id`당 `is_default=TRUE` 매핑 최대 1건 | 매핑 등록 시 | DBA §2.5.2 — 상품 자동 매핑 대상을 하나로 고정 |
| `cat_display_page.slug` 전역 유니크 | 페이지 생성 시 | URL 충돌 방지 |
| `cat_display_page.display_end_at`을 설정하는 경우 `display_start_at`보다 이후여야 함 | 생성·수정 시 | REQ-CAT-042(2026-11-09 재정의) |
| `cat_display_page.is_home=TRUE`인 행은 전체 테이블에서 최대 1건 | 홈 지정 시 | REQ-CAT-052 — 기존 홈 지정 해제 후 신규 지정 |
| `cat_display_page.is_home=TRUE`는 `status=PUBLISHED`에서만 허용 | 홈 지정 시 | REQ-CAT-052 — DRAFT/CLOSED 등 비공개 페이지는 홈 지정 불가 |
| `cat_event_banner_schedule`은 동일 `source_event_id` 기준 조회 시점(now)에 유효 건이 0~1건이어야 함 (중복 시 판정 규칙은 Human Review) | 조회·동기화 시 | DF Human Review(신설) — price_schedule Human Review #6과 동일 쟁점 |

---

## Soft Delete 정책

| 테이블 | 정책 | 사유 |
|---|---|---|
| cat_product | `is_deleted = true` | 주문 이력 참조 유지 (물리 삭제 불가) |
| cat_product_image | 물리 삭제 허용 | CDN 파일 별도 관리 |
| cat_sku | `is_deleted` 컬럼 없음 — 상위 product와 생명주기 동일 | 재고 이력 참조는 product soft delete로 충분 |
| cat_stock_history | 물리 삭제 없음, 영구 보존 | 감사 이력 (REQ-CAT-024) |
| cat_product_price_schedule | 물리 삭제 없음, 영구 보존 (이력+예약 겸용) | 과거 기간 행은 가격 변경 감사 이력, 미래 기간 행은 예약된 가격 — 둘 다 삭제 불가 |
| cat_product_wishlist | 물리 삭제 허용 (해제·품절·단종 시 즉시) | 개인화 데이터, 감사 이력 불필요. DBA §1.14 |
| cat_category / cat_display_category | `is_active = false` | 기존 매핑·상품 참조 보존 |
| cat_standard_display_category_mapping / cat_product_display_category | 물리 삭제 허용 | 단순 매핑 테이블, 감사 이력 불필요 — 매핑 해제 시 즉시 삭제 |
| cat_brand | `is_active = false` | 기존 상품 참조 보존 |
| cat_display_page | 물리 삭제 없음 | 게시 이력 보존 (CLOSED/CANCELLED로 종료) |
| cat_event_banner_schedule | 물리 삭제 없음, 중도 취소 시 `end_at=now`로 종료 처리 | cat_product_price_schedule과 동일 정책 — 과거 동기화 이력 추적 |

---

## 폐기한 기존 컬럼 (구버전 2026-08-21 → 전면 재작성 시 제거)

> `DD-EARS기능요구/catalog.md`가 전면 재작성되며 근거를 잃은 컬럼들이다. 제거 사유를 남겨
> 향후 "왜 없어졌는지" 재질문이 나왔을 때 추적할 수 있게 한다.

| 폐기 컬럼 | 소속 테이블 | 폐기 사유 |
|---|---|---|
| `avg_rating`, `review_count` | cat_product | 구버전 REQ-CAT-030(Promotion→RatingUpdated 수신)이 발신 도메인·근거 자기모순으로 폐기됨(DD "폐기한 기존 REQ" 참조). 평점·리뷰는 Community 도메인 책임이라 Catalog가 보유할 근거가 없음(이후 리뷰가 Catalog Part III로 소유권 이전됐으나, 집계값은 리뷰 엔티티 쪽에 두는 것으로 유지) |
| `display_sale_price`, `display_discount_rate`, `active_event_id` | cat_product | DBA §1.7.4에서 Promotion 연동 방식을 "`price_sale` 필드 직접 갱신"(REQ-CAT-050~051)으로 확정 — 별도 노출용 가격·할인율·행사ID 필드를 두지 않고 `price_sale` 단일 필드로 통일했으나, 아래 `price_sale` 자체도 재분리됨 |
| `is_redis_target` | cat_sku | 구버전 REQ-CAT-031(Redis 캐시 대상 표시)이 재작성 시 제외됨 — 캐싱 전략은 구조설계가 아닌 구현 단계에서 결정 (DD "폐기한 기존 REQ" 참조) |
| `category_id`(cat_category의 `parent_id`·`depth`) | cat_category | DBA §1.2.1 확정: 표준 카테고리는 "단일 계층(대분류만)" — 트리 구조 불필요. 트리 구조는 `cat_display_category`(전시 카테고리)에만 유지 |
| `price_sale` (2026-10-26 2차 폐기) | cat_product | 사용자 피드백: "수시로 변동하는 Promotion 갱신값을 마스터 테이블 컬럼으로 두는 것은 부적절" — `cat_product_price_schedule`(이력+예약 겸용 테이블)로 분리. 동시에 `cat_price_history`(단순 변경로그)도 역할이 중복되어 함께 폐기, price_schedule이 이력 기능을 겸함 |

---

## Human Review

| # | 항목 | 사유 |
|---|---|---|
| 1 | ~~`cat_product.release_date` 노출 게이트의 딥링크(상세 페이지 직접 접근) 처리~~ | **해소(2026-11-06)** — DBA §2.4에서 상세 페이지 직접 접근도 목록·검색과 동일하게 차단하는 것으로 확정. 위 `release_date` 컬럼 note에 반영 완료 |
| 2 | `cat_category_attribute` 전체 매트릭스 | DBA §1.2.2·DD Human Review #4 — 예시(러닝화·보충제)만 확정, 전체 대분류×속성 조합은 미확정 |
| 3 | 수수료율 테이블 부재 | DBA §1.7.3·DD Human Review #5 — "기본율−등급감면율" 구조만 확정, 구체 수치 테이블 설계는 수치 확정 후 별도 엔티티(`cat_commission_rate` 등) 추가 검토 |
| 4 | 연관상품 추천(REQ-CAT-036) 결과를 Catalog DB에 저장할지 여부 | 외부 SaaS 응답을 매 요청마다 실시간 조회만 할지, 캐시 테이블을 둘지 미확정 — DBA §2.9는 검증필터·프로모션연동·실패처리를 확정했지만 "응답을 저장할지"는 다루지 않음 |
| 5 | 판매자 단위 배송 속성(REQ-CAT-048) 전용 테이블 필요 여부 | 현재는 `cat_product.vendor_id`로 Order가 그룹핑하는 구조로 충분해 보이나, 판매자별 배송 정책(무료배송 기준 등)이 Catalog에 저장될지 Vendor 도메인에 저장될지 소유권 미확정 |
| 6 | `cat_product_price_schedule` 기간 중복 시 판정 규칙 | 사용자 확인(2026-10-26): 중복 처리 규칙은 **Promotion 도메인 정책**이 1차 소유 — 중복을 허용한다면 "할인율이 높은 순"으로 조회 시 1건을 고르고, 허용하지 않는다면 Promotion이 행사 등록 시점에 기간 중복을 체크해 차단한다. 어느 쪽으로 할지, 그리고 Catalog 조회 쿼리가 "허용+우선순위" 방식을 어떻게 구현할지(예: `ORDER BY discount_rate DESC LIMIT 1`)는 Promotion DBA 정책 확정 후 재작성 필요 |
| 7 | **[Promotion 관련]** `cat_event_banner_schedule` 동기화 이벤트의 Promotion 측 발행 여부 미확인 | 사용자 확인(2026-10-26) — 홈 화면의 이벤트목록 섹션은 Promotion이 기획전 등록·수정 시 이벤트를 발행해야 동기화되는 구조(DI-이벤트플로우/catalog.md 신설 이벤트 참조)인데, Promotion이 실제로 그런 이벤트를 발행하는지는 work-scope(Catalog 한정)상 이 세션에서 확인·수정할 수 없었다. Promotion 담당자 확인 필요 |
| 8 | **[Promotion 관련]** `cat_event_banner_schedule.source_event_id`가 가리키는 Promotion 엔티티 확정 | `prm_exhibition.id`로 가정했으나(DF-도메인모델ERD/promotion.md 열람 기준), Promotion 쪽에서 "이벤트"를 다른 엔티티로 취급하거나 별도 ID 체계를 쓸 가능성 — Promotion 담당자 확인 필요 |
| 9 | `cat_event_banner_schedule` 기간 중복 시 판정 규칙 | Human Review #6(가격 스케줄)과 동일한 쟁점 — 동일 source_event_id에 겹치는 기간이 등록되면 어떤 걸 고를지 미확정 |
| 10 | `cat_product.compliance_info_json` 정확한 키 목록 | DBA §1.3.8·§6 HR #36과 동일 쟁점 — 법무 검토 전 참고용 기준으로 작성됐다. JSON 컬럼(가변 스키마)으로 둔 것이 적절한지, 카테고리별 정규화 테이블(`cat_product_compliance`)이 더 나은지도 법무 확인 후 재검토 |
| 11 | `cat_sku.sold_quantity_total` 상품 단위 집계 성능 | 현재는 SKU 테이블에만 저장하고 상품 단위 `sales_rank`는 조회 시점에 소속 SKU 합산으로 계산한다(DBA §1.10 의도 그대로). SKU가 많은 상품의 목록 정렬 시 매번 집계 서브쿼리가 필요한데, 트래픽이 커지면 `cat_product`에 캐시 컬럼을 두고 트랜잭션마다 갱신하는 방식으로 전환할지 검토 필요 |
| 12 | `cat_display_section.section_type`의 `CUSTOM_HTML` 값 | DBA §2.3의 콘텐츠유형 5종 체계에 포함되지 않는 기존 값 — 실제 사용 여부, 사용한다면 `display_style` 허용 매트릭스에 어떻게 포함시킬지 DBA 쪽 확인 필요 |
| 13 | `cat_brand` 테이블 존속 여부 | DBA에 더 이상 전용 "브랜드 마스터" 섹션이 없고 §1.2.2 카테고리별 필수속성 예시로만 흡수돼 있다 — 이 테이블을 유지할지, `cat_category_attribute` 값으로 흡수할지 DD Human Review #8과 함께 확인 필요 |
| 14 | `cat_product_sales_hourly`의 "실시간=최근 3시간"·보존기간(14일) 구체 수치 | DBA §1.17·§6 HR #38과 동일 쟁점 — 설정값으로 두고 운영 데이터를 보며 조정. 인기상품에 동시에 여러 트랜잭션이 같은 (product_id, sale_hour) 행에 증분 upsert를 시도하는 쓰기 경합(hot row)은 DB 레벨 원자적 upsert(`INSERT ... ON CONFLICT DO UPDATE`)로 처리한다는 전제이며, 실제 부하 테스트는 구현 단계 확인 필요 |
| 15 | `cat_gnb_menu.link_target`이 DISPLAY_PAGE/DISPLAY_CATEGORY를 참조할 때, 참조 대상(전시 페이지·전시 카테고리)이 삭제되면 GNB 메뉴를 어떻게 처리할지 | FK 강제를 두지 않아(참조값만 저장) 삭제돼도 자동 감지·비활성화되지 않음 — 관리자가 수동으로 확인·정리해야 하는 운영 부담이 있다. 삭제 시 참조 중인 GNB 메뉴를 경고하는 기능은 범위 밖으로 보류(사용자 지시 없음) |

---

## 근거

> **원칙**: 구조설계 단계(DF) 산출물은 AS-IS 정책서를 직접 인용하지 않는다. `DD-EARS기능요구/
> catalog.md`가 1차 근거이며, `DBA-도메인정책서/catalog.md`로 정책 맥락을 보강한다.

| 항목 | 출처 |
|---|---|
| 엔티티 도출 | `deliverables/S2-구조설계/DD-EARS기능요구/catalog.md` 주어/목적어 명사 추출 (REQ-CAT-001~070) |
| 테이블 접두사 `cat_` | `deliverables/S1-범위정의/DB-도메인정의서.md` 스키마 그룹핑 |
| 직매입/입점형 분기 (`is_direct_sourced`) | DD REQ-CAT-001~007, DBA §1.5.1·§1.9 |
| 재고 불변식·변동 이력·판매량 집계(`sold_quantity_total`) | DD REQ-CAT-020~025·058~059, DBA §1.10·§2.6 |
| 가격 구조 불변식 | DD REQ-CAT-026~028, DBA §1.7.1 |
| 판매가 기간별 스케줄 분리 (`cat_product_price_schedule`) | 사용자 피드백(2026-10-26) — 마스터 속성과 변동 속성 분리, 출시일 노출 게이트(C안)와 동일한 "조회 시점 기간 판정" 패턴 적용. 중복 판정 규칙은 Human Review #6 |
| 이미지 제한·상품 복제등록 | DD REQ-CAT-011~012·056, DBA §1.3.2·§1.5.3 |
| 옵션 깊이 제한 | DD REQ-CAT-013~014, DBA §1.4 |
| 출시일 노출 게이트 (`release_date`) | DD REQ-CAT-033~034, DBA §2.4(C안) |
| 노출 우선순위 (`exposure_md_override`·`exposure_ai_score`)·상품 뱃지 | DD REQ-CAT-037·064~066, DBA §2.6 |
| 재입고 알림 (`cat_restock_subscription`) | DD REQ-CAT-032 |
| 찜하기 (`cat_product_wishlist`) | DD REQ-CAT-061~062, DBA §1.14(2026-11-06 신설) |
| 상품 랭킹 집계·조회 (`cat_product_sales_hourly`) | DD REQ-CAT-074~075, DBA §1.17·§2.13(2026-11-09 신설) — `sold_quantity_total`과 별도 지표, StockChanged 비동기 구독으로 집계 |
| GNB 메뉴 관리 (`cat_gnb_menu`) | DD REQ-CAT-076~077, DBA §2.14(2026-11-09 신설) |
| 주문 수량 제한(`max_order_quantity`) | DD REQ-CAT-059b, DBA §1.8(2026-11-06 신설) |
| 재고 품절임박 알림(`restock_alert_threshold`) | DD REQ-CAT-058~059, DBA §1.10(2026-11-06 신설) |
| 상품정보제공고시(`compliance_info_json`) | DD REQ-CAT-070, DBA §1.3.8(2026-11-06 신설) — 법무 확인 전, Human Review #10 |
| 전시여부 플래그(`is_exposed`) | DD REQ-CAT-068, DBA §2.10(2026-11-06 신설) |
| 전시 콘텐츠유형×전시유형 2축(`display_style`) | DD REQ-CAT-053, DBA §2.3(2026-11-06 신설) |
| 카테고리 단일계층·필수속성 | DD REQ-CAT-016~017·019, DBA §1.2.1~1.2.2 |
| 전시 페이지 상태값 | DD REQ-CAT-038~043, `DH-상태머신/catalog.md` (상호 참조) |
| Promotion 연동(가격 갱신 방식) | DD REQ-CAT-049~051, DBA §1.7.4 |
| 홈 화면 지정(`is_home`)·이벤트 배너 동기화(`cat_event_banner_schedule`) | 사용자 확인(2026-11-06) — DE-메뉴구조도/mobile.md "홈" 메뉴 공백 해소. DD REQ-CAT-052~055, DBA §2.7.2·§2.8.2(신설) |
| 상품 요약(`summary`)·태그(`tags`) 신설 | 사용자 지시(2026-11-09) — DBA §1.3.1·§1.3.3·§1.3.4에는 이미 "상품 요약"·"태그" 정책이 존재했으나 DF에 컬럼이 없던 소급 반영 공백. DD REQ-CAT-056(복제등록)·REQ-CAT-063(SNS 공유)이 이미 이 필드 존재를 전제로 작성돼 있었음. DD REQ-CAT-079(길이·개수 제한) 추가 |
| 옵션값 이미지(`cat_product_option_value.image_url`) 신설 | 사용자 지시(2026-11-09) — DD REQ-CAT-080~081, DBA §1.4.1(신설). depth=1 옵션값에만 허용(색상 스와치 용도) |
| 상품 단위 전시여부·검색노출 제외(`is_exposed`·`is_search_excluded`) 신설 | 사용자 지시(2026-11-09) — DD REQ-CAT-082~083, DBA §2.16(신설). SCR-A-C04-T6(전시 탭) 폐지 결정에 따라 기본정보 탭으로 통합 |
| 폐기 컬럼 사유 | `deliverables/S2-구조설계/DD-EARS기능요구/catalog.md` "폐기한 기존 REQ" 섹션 |
