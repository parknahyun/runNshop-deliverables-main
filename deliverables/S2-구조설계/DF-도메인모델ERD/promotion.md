# 도메인 모델 (ERD) — Promotion

> **단계**: 구조설계
> **문서범위**: Domain
> **문서종류**: Design
>
> **작성 목적**: EARS(⑧)에서 도출된 엔티티·속성·관계를 테이블 설계로 구체화한다.
> **흐름 내 위치**: ⑧ EARS → **⑨ 도메인 모델(ERD)** → ⑩ 상태머신
> **작성 주체**: 시니어 개발자 + AI 협업 (DBA/아키텍트 검토)

| 항목 | 내용 |
|---|---|
| ID | DESIGN-ERD-PROMOTION-001 |
| 상태 | **Draft** |
| 작성일 | 2026-07-08 |
| 갱신일 | 2026-07-08 |

---

## 개념 구분: 할인 vs 쿠폰 (종류 판별 방식)

> Promotion에는 이름이 유사해 혼동하기 쉬운 "장바구니 할인"과 "장바구니 쿠폰"이 별개로 존재한다. **할인과 쿠폰은 종류를 구분하는 방식 자체가 다르다.**

### 1) 할인 — **테이블 자체로 종류를 구분** (type 컬럼 없음)

할인은 종류마다 고유 속성이 크게 달라(선착순 수량/구간 tier/총액 조건) 별도 테이블로 분리한다. 상품할인/장바구니할인의 실질 판별점은 **대상 상품 자식 테이블(`_product`)의 유무**다.

| 할인 종류 | 테이블 | 대상 지정 | 적용 레벨 |
|---|---|---|---|
| 행사가 (구 "즉시할인") | `prm_discount_event` | `prm_discount_event_product` (대상 상품) | 상품 단위 |
| 수량구간 할인 | `prm_quantity_discount` | `prm_quantity_discount_product` (대상 상품) | 상품 단위 |
| 장바구니 할인 | `prm_cart_discount` | **대상 상품 테이블 없음** (`condition_amount` 총액 조건) | 주문 단위 (자동 적용) |

→ **상품할인** = `_product` 자식 테이블 보유 / **장바구니할인** = 자식 테이블 없이 주문 총액 조건으로 자동 적용

### 2) 쿠폰 — **단일 테이블 + `coupon_type` 컬럼으로 구분**

쿠폰은 발급·사용·유효기간 등 공통 속성이 대부분이라 하나의 `prm_coupon` 테이블에 두고 컬럼으로 종류·대상을 구분한다.

| 축 | 컬럼 | 값 | 의미 |
|---|---|---|---|
| 쿠폰 성격 | `coupon_type` | PRODUCT / CART | 상품쿠폰 / 장바구니쿠폰 (적용 레벨) |
| 대상 범위 | `product_target_type` | ALL / MANUAL / CATEGORY | 상품쿠폰의 대상 (전체/특정상품/카테고리) |
| 대상 명세 | `prm_coupon_target_product` | product_id / category_code | MANUAL→product_id, CATEGORY→category_code |

→ 상품 단위 쿠폰 = `coupon_type=PRODUCT` + `product_target_type=MANUAL` / 카테고리 단위 = `+CATEGORY` / 주문 단위 = `coupon_type=CART`

### 3) 요약 — "장바구니 할인" ≠ "장바구니 쿠폰"

| | 장바구니 **할인** (`prm_cart_discount`) | 장바구니 **쿠폰** (`prm_coupon.coupon_type=CART`) |
|---|---|---|
| 성격 | 할인 정책 | 쿠폰의 한 종류 |
| 적용 | 총액 조건 충족 시 **자동** (누구나) | 회원이 **발급받아 보유·선택** |
| 발급/보유 | 없음 | 있음 (`prm_coupon_issue`) |
| 근거 | 정책서 §9.2 | 정책서 §9.1 |
| 중복 규칙 | 동시 1건 ACTIVE (REQ-PRM-032) | 동시 1건 적용 (REQ-PRM-048) |

---

## 테이블 구조

```
prm_discount_event (행사가·즉시할인)
  └── prm_discount_event_product (행사 대상 상품)

prm_quantity_discount (수량구간 할인)
  └── prm_quantity_discount_tier (구간별 조건)
  └── prm_quantity_discount_product (대상 상품)

prm_cart_discount (장바구니 가격할인)

prm_coupon (쿠폰 정의)
  └── prm_coupon_target_member (회원 타겟팅)
  └── prm_coupon_target_product (상품 타겟팅)
  └── prm_coupon_issue (발급 이력)

prm_exhibition (기획전)
  └── prm_exhibition_product (기획전 상품)
  └── prm_exhibition_promotion (기획전 소속 프로모션)
```

---

## DBML

```dbml
Table prm_discount_event {
  id varchar [pk, note: 'ULID']
  name varchar [not null, note: '행사명']
  discount_type varchar [not null, note: 'RATE / AMOUNT (정률/정액)']
  discount_value int [not null, note: '할인율(%) 또는 할인금액(원)']
  limit_type varchar [not null, default: 'PERIOD', note: '종료방식: PERIOD(기간형) / QUANTITY(선착순형)']
  limit_quantity int [note: '선착순 제한 수량 (limit_type=QUANTITY일 때만, 그 외 null)']
  remaining_quantity int [note: '선착순 잔여 수량, Redis 동기화 (limit_type=QUANTITY일 때만). 상품 재고(Catalog SKU stock)와 별개']
  status varchar [not null, note: 'DRAFT / SCHEDULED(등록·시작대기) / ACTIVE(start_at 배치 자동 전환) / ENDED — 정책서 §3.7 예약 활성화, 즉시 활성화 금지']
  start_at timestamp [not null, note: '행사 시작일 (기간형·선착순형 공통 필수). 등록은 start_at 1영업일 전까지 (정책서 §3.7)']
  end_at timestamp [not null, note: '행사 종료일 (기간형·선착순형 공통 필수)']
  created_by varchar [not null, note: 'MD 사용자 ID']
  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    status [name: 'idx_devent_status']
    (status, end_at) [name: 'idx_devent_status_end']
  }

  note: 'REQ-PRM-010~013: 행사가 정책 (종료방식 PERIOD/QUANTITY). 기존 "즉시할인" = 행사가'
}

Table prm_discount_event_product {
  id varchar [pk, note: 'ULID']
  discount_event_id varchar [not null, ref: > prm_discount_event.id]
  product_id varchar [not null, note: 'Catalog product_id (논리적 FK)']
  original_price int [not null, note: '행사 적용 전 판매가 (복원용)']
  created_at timestamp [not null]

  indexes {
    discount_event_id [name: 'idx_dep_event']
    product_id [name: 'idx_dep_product']
    (discount_event_id, product_id) [unique, name: 'uq_dep_event_product']
  }

  note: '행사 대상 상품 매핑'
}

Table prm_quantity_discount {
  id varchar [pk, note: 'ULID']
  name varchar [not null, note: '수량할인명']
  vendor_id varchar [not null, note: '판매자 ID']
  status varchar [not null, note: 'DRAFT / SCHEDULED(등록·시작대기) / ACTIVE(start_at 배치 자동 전환) / ENDED — 정책서 §3.7 예약 활성화. 선착순 종료 없음']
  start_at timestamp [not null, note: '등록은 start_at 1영업일 전까지 (정책서 §3.7)']
  end_at timestamp [not null]
  created_by varchar [not null]
  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    (vendor_id, status) [name: 'idx_qd_vendor_status']
  }

  note: 'REQ-PRM-020~021: 수량구간 할인 정책'
}

Table prm_quantity_discount_tier {
  id varchar [pk, note: 'ULID']
  quantity_discount_id varchar [not null, ref: > prm_quantity_discount.id]
  min_quantity int [not null, note: '최소 수량']
  max_quantity int [note: 'null = 상한 없음']
  discount_rate int [not null, note: '할인율 (%)']
  sort_order int [not null, default: 0]

  indexes {
    quantity_discount_id [name: 'idx_qdt_discount']
  }

  note: '수량구간 할인 조건 테이블'
}

Table prm_quantity_discount_product {
  id varchar [pk, note: 'ULID']
  quantity_discount_id varchar [not null, ref: > prm_quantity_discount.id]
  product_id varchar [not null]
  created_at timestamp [not null]

  indexes {
    (quantity_discount_id, product_id) [unique, name: 'uq_qdp_discount_product']
  }

  note: '수량할인 대상 상품'
}

Table prm_cart_discount {
  id varchar [pk, note: 'ULID']
  name varchar [not null, note: '장바구니 할인명']
  condition_amount int [not null, note: '조건 금액 (이상). 비교 기준은 정가 총액이 아니라 상품 단위 할인(행사가/수량구간+상품쿠폰) 적용 후 주문 총액 — "상품 먼저, 플랫폼 나중" (REQ-PRM-002, 프로모션-할인유형-적용순서 §4)']
  discount_amount int [not null, note: '할인 금액']
  status varchar [not null, note: 'DRAFT / SCHEDULED(등록·시작대기) / ACTIVE(start_at 배치 자동 전환, 동시 1건 제약) / ENDED — 정책서 §3.7 예약 활성화']
  start_at timestamp [not null, note: '등록은 start_at 1영업일 전까지 (정책서 §3.7)']
  end_at timestamp [not null]
  created_by varchar [not null, note: '플랫폼 운영자 ID']
  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    status [name: 'idx_cd_status']
  }

  note: 'REQ-PRM-030~032: 장바구니 가격할인 (동시 1건만 ACTIVE)'
}

Table prm_coupon {
  id varchar [pk, note: 'ULID']
  name varchar [not null, note: '쿠폰명']
  coupon_type varchar [not null, note: 'PRODUCT / CART (상품쿠폰/장바구니쿠폰)']
  discount_type varchar [not null, note: 'RATE / AMOUNT']
  discount_value int [not null, note: '할인율(%) 또는 할인금액(원)']
  max_discount_amount int [note: '최대 할인 한도 (정률 시)']
  min_order_amount int [default: 0, note: '최소 상품금액 — 할인 후 상품금액 기준으로 판단(DBA order.md 3.5.1, 2026-10-29). 컬럼명은 유지']
  issue_limit int [not null, note: '총 발급 한도']
  issued_count int [default: 0, note: '현재 발급 수']
  issue_limit_per_member int [default: 1, note: '1인당 발급 한도 (다운로드/임의발행 단계 제한, 사용 검증과 무관)']
  vendor_id varchar [note: '벤더 발행 시 판매자 ID (플랫폼 발행이면 null). ⚠️ 판매자 발행은 partner 채널 협의 대기']
  member_target_type varchar [not null, note: 'ALL / GRADE / MANUAL (전체/등급/임의지정)']
  product_target_type varchar [not null, note: 'ALL / MANUAL / CATEGORY']
  status varchar [not null, note: 'PENDING_APPROVAL / ACTIVE / REJECTED / EXPIRED. ⚠️ PENDING_APPROVAL/REJECTED는 입점형(partner) 흐름 — 협의 대기']
  reject_reason varchar [note: '반려 사유']
  valid_from timestamp [not null]
  valid_to timestamp [not null]
  created_by varchar [not null]
  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    status [name: 'idx_coupon_status']
    vendor_id [name: 'idx_coupon_vendor']
    (status, valid_to) [name: 'idx_coupon_status_valid']
  }

  note: 'REQ-PRM-040~048: 쿠폰 정의'
}

Table prm_coupon_target_member {
  id varchar [pk, note: 'ULID']
  coupon_id varchar [not null, ref: > prm_coupon.id]
  member_id varchar [note: 'MANUAL 타겟 시']
  grade varchar [note: 'GRADE 타겟 시']
  created_at timestamp [not null]

  indexes {
    coupon_id [name: 'idx_ctm_coupon']
  }

  note: '쿠폰 회원 타겟팅 (REQ-PRM-043)'
}

Table prm_coupon_target_product {
  id varchar [pk, note: 'ULID']
  coupon_id varchar [not null, ref: > prm_coupon.id]
  product_id varchar [note: 'MANUAL 타겟 시']
  category_code varchar [note: 'CATEGORY 타겟 시']
  created_at timestamp [not null]

  indexes {
    coupon_id [name: 'idx_ctp_coupon']
  }

  note: '쿠폰 상품 타겟팅 (REQ-PRM-043)'
}

Table prm_coupon_issue {
  id varchar [pk, note: 'ULID']
  coupon_id varchar [not null, ref: > prm_coupon.id]
  member_id varchar [not null]
  status varchar [not null, note: 'AVAILABLE / USED / EXPIRED. 사용 가능 판정은 status 단독이 아니라 status=AVAILABLE AND now<=prm_coupon.valid_to 조합 (상태머신 §3)']
  used_order_id varchar [note: '사용된 주문 ID']
  issued_at timestamp [not null]
  used_at timestamp
  expired_at timestamp [note: '만료 "처리된" 시각 기록용 (배치 EXPIRED 전환 시각). 유효기한 아님 — 유효기한은 부모 prm_coupon.valid_to 참조. 만료 판정 가드로 사용 금지']

  indexes {
    (coupon_id, member_id) [name: 'idx_ci_coupon_member']
    (member_id, status) [name: 'idx_ci_member_status']
  }

  note: '쿠폰 발급 이력 (REQ-PRM-044~047). 유효기간(valid_from/valid_to)은 부모 prm_coupon에서 상속 (발급 건별 별도 기간 미보유). 사용 검증 시 coupon join하여 valid_to 확인'
}

Table prm_exhibition {
  id varchar [pk, note: 'ULID']
  name varchar [not null, note: '기획전명']
  description text [note: '기획전 설명']
  status varchar [not null, note: 'DRAFT / SCHEDULED(등록·시작대기) / ACTIVE(start_at 배치 자동 전환) / ENDED — 정책서 §3.7 예약 활성화']
  start_at timestamp [not null, note: '등록은 start_at 1영업일 전까지 (정책서 §3.7)']
  end_at timestamp [not null]
  created_by varchar [not null]
  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    status [name: 'idx_exhibition_status']
  }

  note: '기획전 (프로모션 컨테이너)'
}

Table prm_exhibition_product {
  id varchar [pk, note: 'ULID']
  exhibition_id varchar [not null, ref: > prm_exhibition.id]
  product_id varchar [not null]
  sort_order int [default: 0]
  created_at timestamp [not null]

  indexes {
    (exhibition_id, product_id) [unique, name: 'uq_ep_exhibition_product']
  }

  note: '기획전 대상 상품'
}

Table prm_exhibition_promotion {
  id varchar [pk, note: 'ULID']
  exhibition_id varchar [not null, ref: > prm_exhibition.id]
  promotion_type varchar [not null, note: 'DISCOUNT_EVENT / QUANTITY_DISCOUNT / CART_DISCOUNT / COUPON']
  promotion_id varchar [not null, note: '각 프로모션 테이블의 ID']
  created_at timestamp [not null]

  indexes {
    exhibition_id [name: 'idx_epromo_exhibition']
  }

  note: '기획전 소속 프로모션 번들링'
}
```

---

## 불변식 (Invariants)

| 불변식 | 검증 시점 | 도출 근거 |
|---|---|---|
| 동일 product_id에 ACTIVE 상품 가격할인(행사가·수량할인)은 최대 1건 (행사가끼리도, 행사가↔수량할인도 택1) | 가격할인 활성화 시 | REQ-PRM-007, REQ-PRM-021 |
| prm_discount_event.limit_type=QUANTITY일 때만 limit_quantity·remaining_quantity 값 존재 (PERIOD는 null) | 행사 등록 시 | REQ-PRM-010, 종료방식 |
| prm_discount_event.remaining_quantity ≥ 0 (선착순형만) | 수량 차감 시 | REQ-PRM-012 |
| prm_cart_discount에 status=ACTIVE인 행은 최대 1건 | 장바구니 할인 활성화 시 | REQ-PRM-032 |
| prm_coupon_issue 사용 가능 = `status=AVAILABLE AND now≤valid_to` (상태 단독 판정 금지 — 유효기간 조합 필수, 만료 배치 지연 구간 오판 방지) | 쿠폰 사용 시 | REQ-PRM-003·004, 상태머신 §3 판정식 |
| prm_coupon.issued_count ≤ issue_limit | 쿠폰 발급 시 | REQ-PRM-046 |
| 환불 시 쿠폰 USED → AVAILABLE 복원은 `now ≤ prm_coupon.valid_to`인 경우만 (유효기간 지난 쿠폰은 EXPIRED 유지, 복원 안 함) | 환불 이벤트 수신 시 | 정산 정책 + 상태머신 §3 |
| vendor.is_platform_direct=TRUE인 쿠폰은 PENDING_APPROVAL 상태 생략 | 쿠폰 생성 시 | REQ-PRM-039, 정책서 §9.0 |
| vendor.is_platform_direct=TRUE인 쿠폰은 PENDING_APPROVAL 상태 생략 | 쿠폰 생성 시 | REQ-PRM-039, 정책서 §9.0 |

---

## Soft Delete 정책

| 테이블 | 정책 | 사유 |
|---|---|---|
| prm_discount_event | 물리 삭제 없음, ENDED 상태 보존 | 행사 이력 추적 |
| prm_quantity_discount | 물리 삭제 없음, ENDED 상태 보존 | 할인 이력 추적 |
| prm_cart_discount | 물리 삭제 없음, ENDED 상태 보존 | 정산 기준 |
| prm_coupon | 물리 삭제 없음 | 쿠폰 발급·사용 이력 법적 보관 |
| prm_coupon_issue | 물리 삭제 없음 | 사용 이력 법적 보관 |
| prm_exhibition | 물리 삭제 없음, ENDED 상태 보존 | 기획전 이력 |

---

## 근거

| 항목 | 출처 |
|---|---|
| 엔티티 도출 | `DD-EARS기능요구(Promotion).md` 주어/목적어 명사 추출 |
| 테이블 접두사 `prm_` | `DB-도메인정의서.md` 스키마 그룹핑 |
| 택1 규칙 | REQ-PRM-007, REQ-PRM-021 |
| 장바구니 1건 제한 | REQ-PRM-032 |
| 쿠폰 승인 워크플로우 | REQ-PRM-040~042 |
| 기획전 번들링 구조 | 도메인기능표 코드 기반 보완 (PromotionsTab) |
