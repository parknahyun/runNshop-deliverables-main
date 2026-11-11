# 인터페이스 명세 — Catalog 도메인

> 상위 문서: [readme.md](readme.md)
> **단계**: 상세설계 (S3) | **문서범위**: Bolt (Catalog) | **문서종류**: Design

---

## 1. POST /api/partner/v1/products — 상품 임시저장 (입점형)

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/partner/v1/products |
| 인증 | Bearer {vendorId} (필수) |
| 설명 | 입점형 상품 초안을 DRAFT 상태로 생성. `isDirectSourced`는 서버가 판매자 토큰 기준으로 false 고정 |

#### Request Body

```json
{
  "name": "러닝화 에어맥스",
  "summary": "에어쿠셔닝 러닝화",
  "categoryId": "cat-001",
  "brandId": "brand-010",
  "priceOriginal": 179000,
  "priceSale": 152000,
  "priceSupply": 98000,
  "releaseDate": null,
  "description": "<p>상품 설명</p>",
  "tags": "러닝화,에어쿠션,나이키"
}
```

> `priceSale`은 `cat_product` 컬럼이 아니라 등록 시점에 `cat_product_price_schedule`에
> `source_type=BASE`(무기한) 행으로 저장된다(§16 참조, DBA §1.7.2). `summary`(최대 200자)·
> `tags`(쉼표 구분, 최대 10개)는 선택 입력이다(DBA §1.3.1·§1.3.3·§1.3.4, 2026-11-09 소급 반영).

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "productId": "prod-001",
    "status": "DRAFT",
    "isDirectSourced": false
  }
}
```

#### Error Responses

| HTTP | code | message | 조건 | 대응 GWT |
|---|---|---|---|---|
| 400 | REQUIRED_FIELD_MISSING | 필수 항목을 입력해주세요 | name/categoryId/가격3종 누락 | AC-CAT-002 유사(직매입과 동일 검증 규칙) |
| 422 | PRICE_RULE_VIOLATION | 정가는 판매가 이상이어야 합니다 | price_original < price_sale 등 | AC-CAT-035 |
| 401 | UNAUTHORIZED | 로그인이 필요합니다 | 토큰 없음/만료 | — |

---

## 2. POST /api/partner/v1/products/{productId}/review-request — 심사 요청

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/partner/v1/products/{productId}/review-request |
| 인증 | Bearer {vendorId} (필수, 본인 상품만) |
| 설명 | DRAFT → REVIEW_REQUESTED 전환. 필수 필드(이미지 1장 이상 포함) 충족 시에만 허용 |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": { "productId": "prod-001", "status": "REVIEW_REQUESTED" }
}
```

#### Error Responses

| HTTP | code | message | 조건 | 대응 GWT |
|---|---|---|---|---|
| 422 | IMAGE_REQUIRED | 이미지를 1장 이상 등록해주세요 | 이미지 0장 | AC-CAT-005 |
| 409 | INVALID_STATUS | DRAFT 상태에서만 심사 요청이 가능합니다 | 상태 불일치 | — |
| 403 | FORBIDDEN | 본인 상품만 처리할 수 있습니다 | 타 판매자 소유 | — |

---

## 3. POST /api/admin/v1/products — 상품 등록 (직매입)

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/admin/v1/products |
| 인증 | Bearer {adminId}, Role: MD-DIRECT (필수) |
| 설명 | `isDirectSourced=true`로 생성, 심사 게이트 없이 즉시 ON_SALE 전환 |

#### Request Body

```json
{
  "name": "자사 PB 보충제",
  "summary": "국산 유청 단백질 보충제",
  "categoryId": "cat-020",
  "priceOriginal": 39000,
  "priceSale": 35000,
  "priceSupply": 20000,
  "releaseDate": "2026-10-15",
  "tags": "보충제,단백질,국산"
}
```

> `priceSale`은 §1과 동일하게 `cat_product_price_schedule`에 BASE 행으로 저장된다. `summary`·
> `tags`는 §1과 동일 규칙(선택 입력, 2026-11-09 소급 반영).

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "productId": "prod-002",
    "status": "ON_SALE",
    "isDirectSourced": true
  }
}
```

#### Error Responses

| HTTP | code | message | 조건 | 대응 GWT |
|---|---|---|---|---|
| 400 | REQUIRED_FIELD_MISSING | 필수 항목을 입력해주세요 | 필수 필드 누락 | AC-CAT-002 |
| 422 | PRICE_RULE_VIOLATION | 정가는 판매가 이상이어야 합니다 | 가격 구조 위반 | AC-CAT-035 |

---

## 4. POST /api/admin/v1/products/{productId}/review-start — 심사 착수

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/admin/v1/products/{productId}/review-start |
| 인증 | Bearer {adminId}, Role: MD-REVIEWER (필수) |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": { "productId": "prod-001", "status": "UNDER_REVIEW", "reviewerId": "admin-review-001" }
}
```

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 409 | INVALID_STATUS | REVIEW_REQUESTED 상태에서만 착수가 가능합니다 | 상태 불일치 |

---

## 5. POST /api/admin/v1/products/{productId}/approve — 심사 승인

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/admin/v1/products/{productId}/approve |
| 인증 | Bearer {adminId}, Role: MD-REVIEWER (필수) |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": { "productId": "prod-001", "status": "ON_SALE" }
}
```

#### Error Responses

| HTTP | code | message | 조건 | 대응 GWT |
|---|---|---|---|---|
| 409 | INVALID_STATUS | UNDER_REVIEW 상태에서만 승인이 가능합니다 | 상태 불일치 | AC-CAT-007 |

---

## 6. POST /api/admin/v1/products/{productId}/reject — 심사 반려

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/admin/v1/products/{productId}/reject |
| 인증 | Bearer {adminId}, Role: MD-REVIEWER (필수) |

#### Request Body

```json
{ "rejectReason": "필수 인증 서류 누락" }
```

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "productId": "prod-001",
    "status": "REJECTED",
    "rejectCount": 1,
    "rejectedAt": "2026-09-28T14:10:00Z",
    "resubmitDeadline": "2026-10-28T14:10:00Z",
    "escalated": false
  }
}
```

#### Error Responses

| HTTP | code | message | 조건 | 대응 GWT |
|---|---|---|---|---|
| 400 | REASON_REQUIRED | 반려 사유를 입력해주세요 | reject_reason 누락 | AC-CAT-009 |
| 409 | INVALID_STATUS | UNDER_REVIEW 상태에서만 반려가 가능합니다 | 상태 불일치 | — |

> `escalated=true`는 동일 사유 3회 이상 반복 반려 시 반환되며(AC-CAT-013), 입점 심사팀 에스컬레이션 목록에 추가된다.

---

## 7. POST /api/partner/v1/products/{productId}/resubmit — 반려 후 재제출

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/partner/v1/products/{productId}/resubmit |
| 인증 | Bearer {vendorId} (필수, 본인 상품만) |
| 설명 | REJECTED → DRAFT 전환. 반려일로부터 30일 이내만 허용 (초과 시 배치가 이미 자동 삭제했으므로 404) |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": { "productId": "prod-001", "status": "DRAFT" }
}
```

#### Error Responses

| HTTP | code | message | 조건 | 대응 GWT |
|---|---|---|---|---|
| 404 | PRODUCT_NOT_FOUND | 상품을 찾을 수 없습니다 | 30일 초과로 배치가 이미 삭제 | AC-CAT-012 |
| 409 | INVALID_STATUS | REJECTED 상태에서만 재제출이 가능합니다 | 상태 불일치 | — |

---

## 8. PATCH /api/partner/v1/products/{productId} — 상품 기본정보 수정

| 항목 | 내용 |
|---|---|
| Method | PATCH |
| Path | /api/partner/v1/products/{productId} |
| 인증 | Bearer {vendorId} (필수, 본인 상품만) / admin은 별도 `/api/admin/v1/products/{productId}` 동일 스펙 |
| 설명 | 이름·카테고리·가격·출시일 등 부분 수정. 전달된 필드만 갱신 |

> 가격(`priceSale`) 변경은 이 API가 아니라 §16 전용 API로 분리되어 있다 — 판매가는
> `cat_product_price_schedule`에 새 유효기간 행을 추가하는 별도 쓰기 경로가 필요하기 때문.

#### Request Body

```json
{
  "name": "러닝화 에어맥스 v2",
  "summary": "에어쿠셔닝 러닝화",
  "releaseDate": "2026-10-15",
  "description": "<p>수정된 설명</p>",
  "maxOrderQuantity": 5,
  "restockAlertThreshold": 5,
  "complianceInfo": { "material": "메쉬·합성섬유", "origin": "베트남", "afterSalesContact": "1588-0000" },
  "tags": "러닝화,에어쿠션,나이키",
  "isExposed": true,
  "isSearchExcluded": false
}
```

> `maxOrderQuantity`(DBA §1.8, nullable=무제한)·`restockAlertThreshold`(DBA §1.10, 기본값 5)·
> `complianceInfo`(DBA §1.3.8, 대분류별 가변 키-값, 법무 확인 전 참고용 — §6 Human Review #4)는
> 2026-11-06 신설 필드다. `summary`(최대 200자)·`tags`(쉼표 구분, 최대 10개)는 DBA §1.3.1·
> §1.3.3·§1.3.4 기존 정책의 2026-11-09 소급 반영 필드다. `isExposed`·`isSearchExcluded`는
> DBA §2.16(2026-11-09 신설) — 별도 전시 탭 없이 이 API로 통합 관리한다(SCR-A-C04-T6 폐지).
> 전달하지 않으면 기존 값을 유지한다. 길이·개수 제한 위반 시 각각 400
> `SUMMARY_LENGTH_EXCEEDED`·422 `TAG_LIMIT_EXCEEDED`(AC-CAT-105·106).

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": { "productId": "prod-001", "updatedFields": ["name", "summary", "releaseDate", "description", "maxOrderQuantity", "restockAlertThreshold", "complianceInfo", "tags", "isExposed", "isSearchExcluded"] }
}
```

#### Error Responses (요약·태그 관련, 2026-11-09 신설)

| HTTP | code | message | 조건 | 대응 GWT |
|---|---|---|---|---|
| 400 | SUMMARY_LENGTH_EXCEEDED | 상품 요약은 최대 200자까지 입력 가능합니다 | summary 길이 > 200 | AC-CAT-105 |
| 422 | TAG_LIMIT_EXCEEDED | 태그는 최대 10개까지 등록 가능합니다 | tags 개수 > 10 | AC-CAT-106 |

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 403 | FORBIDDEN | 본인 상품만 처리할 수 있습니다 | 타 판매자 소유 |

---

## 9. POST /api/partner/v1/products/{productId}/images — 이미지 등록

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/partner/v1/products/{productId}/images |
| 인증 | Bearer {vendorId} (필수, 본인 상품만) / admin은 별도 `/api/admin/v1/products/{productId}/images`(API-CAT-044, 2026-11-09 소급 반영) — 소유자 검증 생략 |
| Content-Type | multipart/form-data |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": { "imageId": "img-004", "imageUrl": "https://cdn.../img-004.jpg", "sortOrder": 4, "imageType": "DETAIL" }
}
```

#### Error Responses

| HTTP | code | message | 조건 | 대응 GWT |
|---|---|---|---|---|
| 422 | IMAGE_LIMIT_EXCEEDED | 이미지는 최대 10장까지 등록 가능합니다 | 이미 10장 보유 | AC-CAT-017 |

---

## 10. POST /api/partner/v1/products/{productId}/options — 옵션그룹·옵션값 설정

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/partner/v1/products/{productId}/options |
| 인증 | Bearer {vendorId} (필수, 본인 상품만) / admin은 별도 `/api/admin/v1/products/{productId}/options`(API-CAT-045, 2026-11-09 소급 반영) — 소유자 검증 생략 |
| 설명 | 옵션그룹·옵션값 조합으로 SKU 자동 생성 |

#### Request Body

```json
{
  "optionGroups": [
    { "name": "색상", "depth": 1, "values": ["Red", "Blue"] },
    { "name": "사이즈", "depth": 2, "values": ["260", "265", "270"] }
  ]
}
```

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "optionGroups": [ { "id": "optgrp-001", "name": "색상" }, { "id": "optgrp-002", "name": "사이즈" } ],
    "generatedSkus": 6
  }
}
```

#### Error Responses

| HTTP | code | message | 조건 | 대응 GWT |
|---|---|---|---|---|
| 422 | OPTION_DEPTH_EXCEEDED | 옵션은 최대 2단계까지 설정 가능합니다 | 3단계 이상 요청 | AC-CAT-019 |

---

## 11. POST /api/partner/v1/products/{productId}/discontinue — 상품 단종 처리

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/partner/v1/products/{productId}/discontinue |
| 인증 | Bearer {vendorId} 또는 Bearer {adminId} Role: MD-OPERATOR |
| 설명 | ON_SALE/SOLD_OUT → DISCONTINUED. 재고 수량과 무관한 수동 전환만 허용 |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": { "productId": "prod-001", "status": "DISCONTINUED" }
}
```

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 409 | INVALID_STATUS | ON_SALE/SOLD_OUT 상태에서만 단종 처리가 가능합니다 | DRAFT 등 다른 상태 |

---

## 12. 분류체계 관리 API 그룹

> 카테고리(표준/전시)·브랜드는 CRUD 패턴이 동일하여 하나의 섹션에 묶는다.

| Method | Path | 설명 |
|---|---|---|
| POST | /api/admin/v1/categories | 표준 카테고리 생성 |
| PATCH | /api/admin/v1/categories/{categoryId} | 표준 카테고리 수정 |
| DELETE | /api/admin/v1/categories/{categoryId} | 표준 카테고리 삭제 |
| POST | /api/admin/v1/display-categories | 전시 카테고리 생성 |
| PATCH | /api/admin/v1/display-categories/{categoryId} | 전시 카테고리 수정 |
| DELETE | /api/admin/v1/display-categories/{categoryId} | 전시 카테고리 삭제 |
| POST | /api/admin/v1/brands | 브랜드 등록 |
| PATCH | /api/admin/v1/brands/{brandId} | 브랜드 수정 |

#### Request Body 예시 (표준 카테고리 생성)

```json
{ "name": "러닝화", "sortOrder": 1 }
```

#### Response 200 (공통 패턴)

```json
{
  "code": "SUCCESS",
  "data": { "categoryId": "cat-021", "name": "러닝화" }
}
```

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 409 | DUPLICATE_CATEGORY_NAME | 동일한 이름의 카테고리가 이미 존재합니다 | 중복 생성 |

---

## 12-1. 분류체계 목록 조회 API 그룹

> **2026-10-26 보강**: §5 분류체계 관리 화면(admin)의 데이터 소스로 필요한 목록 조회 API가
> §12(쓰기 전용)에 빠져 있었다(DN-화면레이아웃 catalog-admin.md §5 `[TBD-API]` 해소).

| Method | Path | 설명 |
|---|---|---|
| GET | /api/admin/v1/categories?page=1&size=50&sort=sortOrder&direction=asc | 표준 카테고리 목록 조회 |
| GET | /api/admin/v1/display-categories?page=1&size=50 | 전시 카테고리 목록 조회 (트리 구조 반환) |
| GET | /api/admin/v1/brands?page=1&size=50&sort=name&direction=asc | 브랜드 목록 조회 |

#### Response 200 (표준 카테고리 목록)

```json
{
  "code": "SUCCESS",
  "data": {
    "categories": [
      { "categoryId": "cat-001", "name": "러닝화", "sortOrder": 1, "isActive": true },
      { "categoryId": "cat-020", "name": "보충제", "sortOrder": 2, "isActive": true }
    ],
    "pagination": { "page": 1, "size": 50, "totalCount": 18, "totalPages": 1 }
  }
}
```

#### Response 200 (전시 카테고리 목록)

```json
{
  "code": "SUCCESS",
  "data": {
    "displayCategories": [
      { "categoryId": "dcat-001", "parentId": null, "name": "신상품", "depth": 1 },
      { "categoryId": "dcat-002", "parentId": "dcat-001", "name": "이번주 신상", "depth": 2 }
    ]
  }
}
```

> 전시 카테고리는 트리 구조라 `pagination` 없이 전체를 반환한다(표준 카테고리는 단일계층이라
> 페이지네이션 대상, DBA §3.1).

#### Response 200 (브랜드 목록)

```json
{
  "code": "SUCCESS",
  "data": {
    "brands": [
      { "brandId": "brand-010", "name": "나이키", "logoUrl": "https://cdn.../nike.png", "isActive": true }
    ],
    "pagination": { "page": 1, "size": 50, "totalCount": 42, "totalPages": 1 }
  }
}
```

---

## 13. PATCH /api/partner/v1/skus/{skuId}/stock — SKU 재고 수량 변경

| 항목 | 내용 |
|---|---|
| Method | PATCH |
| Path | /api/partner/v1/skus/{skuId}/stock |
| 인증 | Bearer {vendorId} (필수, 본인 상품의 SKU만) |
| 설명 | 재고 신규 등록·조정. SOLD_OUT 상품은 재고 1 이상 복원 시 MD 확인 없이 자동 ON_SALE 전환(대안A) |

#### Request Body

```json
{ "stockQuantity": 15, "changeType": "RESTOCK_VENDOR" }
```

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "skuId": "sku-001",
    "stockQuantity": 15,
    "availableQuantity": 15,
    "productStatusChanged": true,
    "productStatus": "ON_SALE"
  }
}
```

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 400 | INVALID_QUANTITY | 재고 수량은 0 이상이어야 합니다 | 음수 입력 |
| 403 | FORBIDDEN | 본인 상품만 처리할 수 있습니다 | 타 판매자 소유 |

---

## 13-1. GET /api/partner/v1/skus — SKU 통합 조회 (재고 관리용)

> **2026-10-26 보강**: partner §12 재고 관리 화면의 데이터 소스. 상품 상세(§29)는 상품
> 1건의 SKU만 보여주는데, 재고 관리 화면은 판매자가 보유한 **모든 상품의 SKU를 한 화면에서**
> 조회·수정해야 하므로 상품 경계를 넘는 전용 목록 API가 필요하다(DN-화면레이아웃
> catalog-partner.md §12 `[TBD-API]` 해소).

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/partner/v1/skus?keyword=&status=&page=1&size=20&sort=updatedAt&direction=desc |
| 인증 | Bearer {vendorId} (필수) |
| 설명 | 본인(판매자) 소유 상품의 SKU를 상품명·SKU코드 키워드로 검색. `status=SOLD_OUT` 필터로 품절 SKU만 조회 가능 |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "skus": [
      {
        "skuId": "sku-001",
        "productId": "prod-001",
        "productName": "러닝화 에어맥스",
        "optionValues": { "색상": "Red", "사이즈": "260" },
        "stockQuantity": 10,
        "availableQuantity": 8,
        "productStatus": "ON_SALE"
      },
      {
        "skuId": "sku-002",
        "productId": "prod-001",
        "productName": "러닝화 에어맥스",
        "optionValues": { "색상": "Blue", "사이즈": "265" },
        "stockQuantity": 0,
        "availableQuantity": 0,
        "productStatus": "SOLD_OUT"
      }
    ],
    "pagination": { "page": 1, "size": 20, "totalCount": 36, "totalPages": 2 }
  }
}
```

---

## 14. POST /api/internal/v1/skus/{skuId}/reserve — 재고 차감 (Order 연동)

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/internal/v1/skus/{skuId}/reserve |
| 인증 | Service-to-Service (Order 도메인 전용, 내부망) |
| 설명 | 동기 PublicApi. REQ-CAT-023·045 |

#### Request Body

```json
{ "quantity": 2, "orderId": "ord-001" }
```

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": { "skuId": "sku-001", "availableQuantity": 8, "productStatusChanged": false }
}
```

#### Error Responses

| HTTP | code | message | 조건 | 대응 GWT |
|---|---|---|---|---|
| 409 | INSUFFICIENT_STOCK | 재고가 부족합니다 | available_quantity < 요청수량 | AC-CAT-030 |

---

## 15. GET /api/internal/v1/skus/availability — 재고 확인 (Order 연동)

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/internal/v1/skus/availability?skuIds=sku-001,sku-002 |
| 인증 | Service-to-Service (Order 도메인 전용) |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "skus": [
      { "skuId": "sku-001", "availableQuantity": 8 },
      { "skuId": "sku-002", "availableQuantity": 0 }
    ]
  }
}
```

---

## 16. PATCH /api/partner/v1/products/{productId}/price — 가격 설정·변경

| 항목 | 내용 |
|---|---|
| Method | PATCH |
| Path | /api/partner/v1/products/{productId}/price |
| 인증 | Bearer {vendorId} (필수, 본인 상품만) / admin은 별도 `/api/admin/v1/products/{productId}/price`(API-CAT-043, 2026-11-09 신설) — Role MD-OPERATOR, 소유자 검증 생략, `createdBy`=adminId |
| 설명 | `priceOriginal`·`priceSupply`는 `cat_product`에 즉시 반영, `priceSale`은 `cat_product_price_schedule`에 `source_type=BASE`(무기한) 행으로 추가하고 기존 BASE 행은 `end_at=now`로 종료(DBA §1.7.2). `created_by`는 vendor_id 또는 admin_id를 수용(DF-ERD 설계 그대로) |

#### Request Body

```json
{ "priceOriginal": 179000, "priceSale": 152000, "priceSupply": 98000 }
```

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "productId": "prod-001",
    "priceOriginal": 179000,
    "priceSale": 152000,
    "priceSupply": 98000,
    "discountRate": 15,
    "priceScheduleId": "pps-ulid-020"
  }
}
```

#### Error Responses

| HTTP | code | message | 조건 | 대응 GWT |
|---|---|---|---|---|
| 422 | PRICE_RULE_VIOLATION | 정가는 판매가 이상이어야 합니다 | price_original < price_sale 등 | AC-CAT-035 |

---

## 16-1. GET /api/partner/v1/products/{productId}/price-schedule — 판매가 스케줄 조회·예약

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/partner/v1/products/{productId}/price-schedule |
| 인증 | Bearer {vendorId} (필수, 본인 상품만) |
| 설명 | 과거·현재·미래 전체 가격 스케줄 이력 조회 (이력+예약 겸용 테이블을 그대로 노출) |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "schedules": [
      { "id": "pps-ulid-018", "price": 179000, "sourceType": "BASE", "startAt": "2026-08-01T00:00:00Z", "endAt": "2026-09-30T23:59:59Z" },
      { "id": "pps-ulid-019", "price": 69000, "sourceType": "PROMOTION_EVENT", "sourceEventId": "prm-event-ulid-010", "startAt": "2026-10-01T00:00:00Z", "endAt": "2026-10-07T23:59:59Z" },
      { "id": "pps-ulid-020", "price": 152000, "sourceType": "BASE", "startAt": "2026-09-28T14:00:00Z", "endAt": null }
    ]
  }
}
```

> 미래 시각으로 `startAt`이 설정된 행(위 예시의 `pps-ulid-019`)이 "예약된 가격"이다. 조회
> API는 판매자에게 현재·과거·예약 전체를 투명하게 보여준다(대안: MD/판매자 혼동 방지를
> 위해 `source_type=PROMOTION_EVENT` 행은 읽기 전용으로 표시).

---

## 17. GET /api/mobile/v1/products — 상품 목록 조회

> **2026-11-09 변경**: 쿼리 파라미터를 `categoryId`(표준 카테고리)에서 `displayCategoryId`
> (전시 카테고리)로 교체했다 — 고객이 보는 "카테고리" 메뉴는 전시 카테고리 기준이다
> (DBA §2.5.1). `cat_product.category_id`(표준 카테고리)는 더 이상 고객 조회 필터로 쓰지
> 않으며, 등록·수수료 등 내부 분류 용도로만 남는다.

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/mobile/v1/products?displayCategoryId={id}&page=1&size=20&sort=exposurePriority&direction=asc |
| 인증 | 불필요 (비로그인 허용) |
| 설명 | `cat_product_display_category`에 매핑된 상품 중 ON_SALE/SOLD_OUT만 반환, release_date 노출 게이트(C안)·`is_exposed=TRUE`(2026-11-09 신설, DBA §2.16) 선행 적용. `displayCategoryId` 지정 시 `is_pinned` DESC·`sort_order` ASC로 정렬(DBA §2.5.3), 미지정 시 `exposure_priority` 정렬(DBA §2.6) |

> `priceSale`은 응답 조립 시 `cat_product_price_schedule`에서 조회 시점(now) 기준 유효 행을
> join하여 채운다(DBA §1.7.2, DM-시퀀스 §11). `badges`(2026-11-06 신설, DBA §2.6)는
> `NEW`(release_date 14일 이내)·`BEST`(카테고리별 sales_rank 상위 10)·`SOLD_OUT_SOON`(재고
> 임박) 중 조건을 만족하는 값을 복수 포함할 수 있다. 로그인 고객이면 `isWished`(DBA §1.14)도
> 포함한다. `summary`(2026-11-09 소급 반영, DBA §1.3.3)는 상품명 아래 서브타이틀로 노출한다.

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "products": [
      {
        "productId": "prod-001",
        "name": "러닝화 에어맥스",
        "summary": "에어쿠셔닝 러닝화",
        "priceOriginal": 179000,
        "priceSale": 152000,
        "discountRate": 15,
        "status": "ON_SALE",
        "thumbnailUrl": "https://cdn.../thumb.jpg",
        "badges": ["BEST"],
        "isWished": false
      }
    ],
    "pagination": { "page": 1, "size": 20, "totalCount": 134, "totalPages": 7 }
  }
}
```

---

## 18. GET /api/mobile/v1/products/search — 상품 검색

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/mobile/v1/products/search?q={keyword}&displayCategoryId=&brandId=&priceMin=&priceMax=&page=1&size=20 |
| 인증 | 불필요 |
| 매칭 대상 | `q`는 `cat_product.name` OR `tags`(2026-11-09 소급 반영, DBA §1.3.4)를 대상으로 매칭한다. `summary`는 검색 매칭에는 사용하지 않고 응답 서브타이틀 노출에만 쓰인다 |
| 노출 게이트 | §17과 동일한 `is_exposed=TRUE`·release_date 게이트에 더해, `is_search_excluded=TRUE`인 상품은 이 API에서만 추가로 제외한다(목록·전시는 영향 없음, DBA §2.16, 2026-11-09 신설) |

#### Response 200

응답 구조는 §17과 동일 (`products[]` + `pagination`, `summary` 포함).

---

## 19. GET /api/mobile/v1/products/{productId} — 상품 상세 조회

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/mobile/v1/products/{productId} |
| 인증 | 불필요 (로그인 시 할인가 노출 그룹B 로그인 버전 적용) |
| 비고 | `priceSale`은 §17과 동일하게 조회 시점 유효 `cat_product_price_schedule` 행을 join하여 채운다 (DBA §1.7.2). `badges`·`isWished`는 §17과 동일 규칙(DBA §2.6·§1.14). `complianceInfo`는 상품정보제공고시(DBA §1.3.8, 법무 확인 전 참고용). `summary`는 2026-11-09 소급 반영(DBA §1.3.3). `optionGroups[].values[].imageUrl`은 옵션값 이미지(2026-11-09 신설, API-CAT-049·050) — depth=1(색상 등)만 값이 있고 depth=2는 항상 null. `is_exposed=FALSE`인 상품은 release_date 노출 게이트와 동일하게 딥링크 직접 접근도 차단되어 404(DBA §2.16, 2026-11-09 신설) |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "productId": "prod-001",
    "name": "러닝화 에어맥스",
    "summary": "에어쿠셔닝 러닝화",
    "description": "<p>...</p>",
    "priceOriginal": 179000,
    "priceSale": 152000,
    "maxOrderQuantity": 5,
    "badges": ["BEST"],
    "isWished": false,
    "images": [ { "imageUrl": "https://cdn.../1.jpg", "sortOrder": 1, "imageType": "MAIN" } ],
    "optionGroups": [
      { "name": "색상", "depth": 1, "values": [ { "value": "Red", "imageUrl": "https://cdn.../red.jpg" }, { "value": "Blue", "imageUrl": null } ] },
      { "name": "사이즈", "depth": 2, "values": [ { "value": "260", "imageUrl": null }, { "value": "265", "imageUrl": null } ] }
    ],
    "skus": [ { "skuId": "sku-001", "optionValues": { "색상": "Red" }, "availableQuantity": 8 } ],
    "discountExposure": {
      "group": "PRODUCT_DETAIL_LOGGED_IN",
      "items": ["ORIGINAL", "SALE", "COUPON_ALL", "MEMBER_GRADE", "COUPON_CONDITIONAL"]
    },
    "complianceInfo": { "material": "메쉬·합성섬유", "origin": "베트남", "afterSalesContact": "1588-0000" }
  }
}
```

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 404 | PRODUCT_NOT_FOUND | 상품을 찾을 수 없습니다 | 존재하지 않는 ID, 또는 release_date 노출게이트 미도달, 또는 `is_exposed=FALSE`(2026-11-09 신설) |

---

## 20. POST /api/mobile/v1/products/{productId}/restock-subscriptions — 재입고 알림 신청

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/mobile/v1/products/{productId}/restock-subscriptions |
| 인증 | Bearer {memberId} (필수) |

#### Request Body

```json
{ "skuId": "sku-003" }
```

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": { "subscriptionId": "restock-001", "status": "PENDING" }
}
```

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 409 | SKU_NOT_SOLD_OUT | 이미 구매 가능한 상품입니다 | SKU가 SOLD_OUT이 아님 |

---

## 21. PATCH /api/admin/v1/products/{productId}/exposure-override — 노출 우선순위 수동 설정

| 항목 | 내용 |
|---|---|
| Method | PATCH |
| Path | /api/admin/v1/products/{productId}/exposure-override |
| 인증 | Bearer {adminId}, Role: MD-OPERATOR (필수) |

#### Request Body

```json
{ "exposureMdOverride": 1 }
```

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": { "productId": "prod-001", "exposureMdOverride": 1 }
}
```

> `exposureMdOverride: null` 요청 시 수동 설정을 해제하고 AI 점수/default_order로 복귀한다.

---

## 22. 전시 페이지 관리 API 그룹

> **2026-11-09 변경**: DRAFT_EDIT·SCHEDULED 상태 제거에 맞춰 `edit-start`/`republish`/
> `schedule`을 없애고, 제목·섹션·전시기간(`displayStartAt`/`displayEndAt`)을 한 번에 다루는
> 일반 수정 API(`PATCH /{pageId}`)로 통합했다. 게시 예약은 `displayStartAt`을 미래 시각으로
> 넣어두는 것으로 대체된다(배치가 자동 게시).

| Method | Path | 설명 |
|---|---|---|
| POST | /api/admin/v1/display-pages | 전시 페이지 생성 (DRAFT) |
| PATCH | /api/admin/v1/display-pages/{pageId} | 제목·슬러그·섹션·전시기간 수정 (DRAFT·PUBLISHED 공통, 상태 전이 없음) |
| POST | /api/admin/v1/display-pages/{pageId}/publish | 즉시 게시 (DRAFT→PUBLISHED) |
| POST | /api/admin/v1/display-pages/{pageId}/close | 종료 처리 (PUBLISHED→CLOSED) |
| PATCH | /api/admin/v1/display-pages/{pageId}/exposure | 전시여부 긴급 회수·복원(`isExposed`, DBA §2.10) — 상태 전이 아님 |

#### Request Body 예시 (전시여부 토글)

```json
{ "isExposed": false }
```

> 상태(`status`)·전시기간(`displayStartAt`/`displayEndAt`)·홈 지정(`isHome`)은 변경하지
> 않는다. `isExposed=false`가 되면 노출 쿼리에서 즉시 제외되고, `true`로 되돌리면 재게시
> 절차 없이 즉시 재노출된다. `isHome=true`인 페이지가 `isExposed=false`가 되면 §32 홈 조회가
> `HOME_NOT_CONFIGURED`와 동일하게 응답한다.

#### Request Body 예시 (제목·섹션·전시기간 수정)

```json
{
  "title": "10월 신상품 예약",
  "displayStartAt": "2026.10.01 00:00:00",
  "displayEndAt": "2026.10.31 23:59:59",
  "sections": [ { "sectionType": "BANNER", "displayStyle": "BANNER" } ]
}
```

> `displayStartAt`/`displayEndAt`은 `yyyy.mm.dd hh:mi:ss` 형식 문자열로 주고받는다(Catalog의
> 모든 "시작일시·종료일시" 쌍 컬럼 공통 규칙, DBA §2.10 참조 — 전사 공통 API 날짜 컨벤션
> `C6-API설계컨벤션.md` §8.1과는 별도). `displayEndAt`을 지정하면 `displayStartAt`보다 이후인지
> 검증한다. PUBLISHED 상태에서 호출해도 상태는 바뀌지 않고 내용만 즉시 교체된다.

#### Response 200 (공통 패턴)

```json
{
  "code": "SUCCESS",
  "data": { "pageId": "page-001", "status": "PUBLISHED", "displayStartAt": "2026.10.01 00:00:00", "displayEndAt": "2026.10.31 23:59:59" }
}
```

#### Error Responses

| HTTP | code | message | 조건 | 대응 GWT |
|---|---|---|---|---|
| 400 | INVALID_DISPLAY_PERIOD | 종료일시는 시작일시보다 이후여야 합니다 | displayEndAt ≤ displayStartAt | AC-CAT-055 |
| 409 | INVALID_STATUS | 현재 상태에서는 처리할 수 없습니다 | 상태 전이 규칙 위반 | — |

---

## 23. GET /api/internal/v1/products/{productId} — 상품 정보 조회 (Order 연동)

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/internal/v1/products/{productId} |
| 인증 | Service-to-Service (Order 도메인 전용) |

> `priceSale`은 조회 시점 유효 `cat_product_price_schedule` 행에서 join하여 반환한다.

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": { "productId": "prod-001", "name": "러닝화 에어맥스", "priceSale": 152000, "status": "ON_SALE", "vendorId": "vendor-001" }
}
```

---

## 24. GET /api/internal/v1/products/{productId}/vendor-shipping — 판매자 단위 배송 속성 (Order 연동)

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/internal/v1/products/{productId}/vendor-shipping |
| 인증 | Service-to-Service (Order 도메인 전용) |
| 설명 | 묶음배송·배송비 계산은 Order가 수행, Catalog는 그룹핑 속성만 제공 |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": { "productId": "prod-001", "vendorId": "vendor-001" }
}
```

---

## 25. GET /api/internal/v1/products/{productId}/promotion-grouping — 상품-행사 그룹핑 속성 (Promotion 연동)

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/internal/v1/products/{productId}/promotion-grouping |
| 인증 | Service-to-Service (Promotion 도메인 전용) |
| 설명 | 수량할인 그룹 판정은 Promotion이 수행, Catalog는 속성값만 제공. `priceSale`은 조회 시점 유효 `cat_product_price_schedule` 행에서 join |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": { "productId": "prod-001", "vendorId": "vendor-001", "priceSale": 152000 }
}
```

---

## 26. POST /api/internal/v1/products/{productId}/price-schedule — 행사가 스케줄 등록·취소 (Promotion 연동)

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/internal/v1/products/{productId}/price-schedule |
| 인증 | Service-to-Service (Promotion 도메인 전용) |
| 설명 | **2026-10-26 재설계**: 기존 "행사가 반영·복원"(price_sale 직접 갱신)을 폐기하고, `cat_product_price_schedule`에 기간을 가진 행을 등록/취소하는 방식으로 변경했다(DBA §1.7.2·§1.7.4). 이벤트(`PROMOTION_PRICE_SCHEDULED`/`PROMOTION_PRICE_SCHEDULE_CANCELLED`) 수신 처리와 동일 로직을 동기 호출로도 제공 |

#### Request Body (등록)

```json
{
  "action": "SCHEDULE",
  "sourceType": "PROMOTION_EVENT",
  "sourceEventId": "prm-event-ulid-010",
  "price": 69000,
  "startAt": "2026-10-01T00:00:00Z",
  "endAt": "2026-10-07T23:59:59Z"
}
```

> `startAt`은 미래 시각으로 사전 등록 가능 — 해당 시각 도래 즉시 조회에 반영되며 별도
> 배치가 필요 없다. 기간이 겹치는 기존 스케줄이 있어도 현재는 거부하지 않는다(중복 처리
> 규칙은 Human Review 대상, §16-1 참조).

#### Request Body (취소)

```json
{ "action": "CANCEL", "sourceEventId": "prm-event-ulid-010" }
```

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": { "productId": "prod-001", "priceScheduleId": "pps-ulid-019", "status": "SCHEDULED" }
}
```

> 행사 "종료"는 이 API를 호출할 필요가 없다 — 등록 시 지정한 `endAt`이 도달하면 조회가
> 자동으로 다음 유효 행(BASE 등)을 선택한다. `action: "CANCEL"`은 행사를 조기에 중도
> 취소할 때만 사용한다.

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 404 | PRODUCT_NOT_FOUND | 상품을 찾을 수 없습니다 | 존재하지 않는 productId |
| 404 | PRICE_SCHEDULE_NOT_FOUND | 취소할 스케줄을 찾을 수 없습니다 | CANCEL 시 sourceEventId 불일치 |

---

## 27. GET /api/admin/v1/products — 상품 목록 조회 (admin 관리용)

> **2026-10-26 보강**: §2 심사 목록 화면(admin), §5 상품 상세·수정 화면(admin)의 진입점으로
> 필요한 관리용 목록 조회 API가 기존 26개에 누락돼 있었다(§17~19은 mobile 고객용으로 응답
> 필드·접근 범위가 다름). DK-세부유스케이스/catalog.md §3·§5 화면 흐름을 근거로 신설.

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/admin/v1/products?status=REVIEW_REQUESTED\&categoryId=\&vendorId=\&isDirectSourced=\&page=1\&size=20\&sort=createdAt\&direction=desc |
| 인증 | Bearer {adminId}, Role: MD-REVIEWER 또는 MD-OPERATOR (필수) |
| 설명 | 모든 판매자·모든 상태(DRAFT 제외 — 판매자 작성 중인 초안은 비노출)의 상품을 조회. `status=REVIEW_REQUESTED`로 필터링하면 심사 목록 화면(§2)의 데이터 소스가 된다. §17과 달리 `is_exposed`·`is_search_excluded` 값과 무관하게 전부 조회된다(admin은 관리 목적상 숨김 상품도 봐야 함, 2026-11-09 신설) |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "products": [
      {
        "productId": "prod-001",
        "name": "러닝화 에어맥스",
        "summary": "에어쿠셔닝 러닝화",
        "vendorId": "vendor-001",
        "vendorName": "런메이트코리아",
        "isDirectSourced": false,
        "categoryId": "cat-001",
        "status": "REVIEW_REQUESTED",
        "priceOriginal": 179000,
        "priceSale": 152000,
        "isExposed": true,
        "createdAt": "2026-09-27T10:00:00Z"
      }
    ],
    "pagination": { "page": 1, "size": 20, "totalCount": 48, "totalPages": 3 }
  }
}
```

> `priceSale`은 §17과 동일하게 조회 시점 유효 `cat_product_price_schedule` 행을 join한다.

---

## 28. GET /api/partner/v1/products — 상품 목록 조회 (partner 관리용)

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/partner/v1/products?status=\&page=1\&size=20\&sort=createdAt\&direction=desc |
| 인증 | Bearer {vendorId} (필수) |
| 설명 | 본인(판매자) 소유 상품만 조회. §10 상품 목록 화면(partner)의 데이터 소스. DRAFT를 포함한 전체 상태를 조회 가능(§27 admin용과 달리 자신의 초안은 봐야 함). §27과 동일하게 `is_exposed`·`is_search_excluded`와 무관하게 전부 조회됨(2026-11-09 신설) |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "products": [
      {
        "productId": "prod-001",
        "name": "러닝화 에어맥스",
        "summary": "에어쿠셔닝 러닝화",
        "status": "REVIEW_REQUESTED",
        "priceOriginal": 179000,
        "priceSale": 152000,
        "isExposed": true,
        "stockSummary": { "totalSku": 6, "soldOutSku": 1 },
        "updatedAt": "2026-09-27T10:00:00Z"
      }
    ],
    "pagination": { "page": 1, "size": 20, "totalCount": 12, "totalPages": 1 }
  }
}
```

---

## 29. GET /api/admin/v1/products/{productId} · /api/partner/v1/products/{productId} — 상품 상세 조회 (관리용)

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/admin/v1/products/{productId} (admin) 또는 /api/partner/v1/products/{productId} (partner, 본인 상품만) |
| 인증 | Bearer {adminId} 또는 Bearer {vendorId} |
| 설명 | §4·§11 상품 상세(관리) 화면의 데이터 소스. §19(mobile 고객용 상세)와 달리 `rejectReason`·`rejectCount`·`isDirectSourced`·`exposureMdOverride` 등 운영 전용 필드를 포함하며, `is_exposed=FALSE`여도 조회·수정 가능(관리 목적). `summary`·`tags`는 2026-11-09 소급 반영(DBA §1.3.1·§1.3.3·§1.3.4). `optionGroups[].values[].imageUrl`은 옵션값 이미지(2026-11-09 신설, API-CAT-049·050). `isExposed`·`isSearchExcluded`는 기본정보 탭에 통합된 전시 설정(2026-11-09 신설, DBA §2.16, SCR-A-C04-T6 폐지) |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "productId": "prod-001",
    "name": "러닝화 에어맥스",
    "summary": "에어쿠셔닝 러닝화",
    "tags": "러닝화,에어쿠션,나이키",
    "vendorId": "vendor-001",
    "isDirectSourced": false,
    "categoryId": "cat-001",
    "brandId": "brand-010",
    "status": "REJECTED",
    "rejectReason": "필수 인증 서류 누락",
    "rejectCount": 1,
    "rejectedAt": "2026-09-28T14:10:00Z",
    "resubmitDeadline": "2026-10-28T14:10:00Z",
    "priceOriginal": 179000,
    "priceSale": 152000,
    "priceSupply": 98000,
    "releaseDate": null,
    "exposureMdOverride": null,
    "isExposed": true,
    "isSearchExcluded": false,
    "images": [ { "imageId": "img-001", "imageUrl": "https://cdn.../1.jpg", "sortOrder": 1, "imageType": "MAIN" } ],
    "optionGroups": [ { "id": "optgrp-001", "name": "색상", "depth": 1, "values": [ { "id": "optval-001", "value": "Red", "imageUrl": "https://cdn.../red.jpg" }, { "id": "optval-002", "value": "Blue", "imageUrl": null } ] } ],
    "skus": [ { "skuId": "sku-001", "optionValues": { "색상": "Red" }, "stockQuantity": 10, "availableQuantity": 8 } ]
  }
}
```

> partner로 호출 시 본인 소유가 아니면 403 `FORBIDDEN`(§1·§8과 동일 규칙). admin 호출은
> 소유자 제약이 없다.

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 404 | PRODUCT_NOT_FOUND | 상품을 찾을 수 없습니다 | 존재하지 않는 ID |
| 403 | FORBIDDEN | 본인 상품만 조회할 수 있습니다 | partner 호출 시 타 판매자 소유 |

---

## 30. GET /api/admin/v1/display-pages — 전시 페이지 목록 조회

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/admin/v1/display-pages?status=\&page=1\&size=20\&sort=updatedAt\&direction=desc |
| 인증 | Bearer {adminId}, Role: MD-OPERATOR (필수) |
| 설명 | §7 전시 페이지 목록 화면의 데이터 소스. §22(전시 페이지 쓰기 API 그룹)에 대응하는 조회 API |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "pages": [
      { "pageId": "page-001", "title": "가을 러닝 기획전", "slug": "fall-running-2026", "status": "PUBLISHED", "publishedAt": "2026.09.20 00:00:00" },
      { "pageId": "page-002", "title": "10월 신상품 예약", "slug": "oct-new-arrival", "status": "DRAFT", "displayStartAt": "2026.10.01 00:00:00" }
    ],
    "pagination": { "page": 1, "size": 20, "totalCount": 9, "totalPages": 1 }
  }
}
```

---

## 30-1. GET /api/admin/v1/display-pages/{pageId} — 전시 페이지 단건 조회

> **2026-10-26 보강**: §7 전시 페이지 편집 화면(admin)의 데이터 소스. §30(목록)은 요약
> 필드만 반환하므로 편집 폼에는 섹션 구성까지 포함한 단건 조회가 필요하다
> (DN-화면레이아웃 catalog-admin.md §7 `[TBD-API]` 해소).

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/admin/v1/display-pages/{pageId} |
| 인증 | Bearer {adminId}, Role: MD-OPERATOR (필수) |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "pageId": "page-002",
    "title": "10월 신상품 예약",
    "slug": "oct-new-arrival",
    "status": "DRAFT",
    "templateId": "tmpl-001",
    "displayStartAt": "2026.10.01 00:00:00",
    "displayEndAt": "2026.10.31 23:59:59",
    "publishedAt": null,
    "closedAt": null,
    "isExposed": true,
    "sections": [
      { "sectionId": "sec-001", "sectionType": "BANNER", "displayStyle": "BANNER", "title": "10월 신상품", "sortOrder": 1 },
      { "sectionId": "sec-002", "sectionType": "PRODUCT_LIST", "displayStyle": "SCROLL", "title": "신상 20종", "sortOrder": 2, "contentJson": { "productIds": ["prod-010", "prod-011"] } }
    ]
  }
}
```

> `displayStyle`(전시유형, 2026-11-06 신설, DBA §2.3)은 `sectionType`(콘텐츠유형)별 허용
> 조합 안에서만 설정 가능하다 — BANNER→BANNER만, EVENT_LIST→BANNER·SCROLL, PRODUCT_LIST→
> LIST·SCROLL, RECOMMENDATION→SCROLL만, CATEGORY_GRID→LIST만.

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 404 | DISPLAY_PAGE_NOT_FOUND | 전시 페이지를 찾을 수 없습니다 | 존재하지 않는 pageId |
| 422 | DISPLAY_STYLE_NOT_ALLOWED | 해당 콘텐츠유형에는 지정한 전시유형을 사용할 수 없습니다 | sectionType×displayStyle 허용 매트릭스 위반 |

---

## 31. PATCH /api/admin/v1/display-pages/{pageId}/set-home — 홈 화면 지정 (2026-10-26 신설)

> DN-화면레이아웃/catalog-admin.md §7 전시 페이지 편집 화면에 "홈으로 설정" 액션으로
> 추가(별도 메뉴 신설 없음, 사용자 확인 2026-10-26).

| 항목 | 내용 |
|---|---|
| Method | PATCH |
| Path | /api/admin/v1/display-pages/{pageId}/set-home |
| 인증 | Bearer {adminId}, Role: MD-OPERATOR (필수) |
| 설명 | 해당 페이지를 홈(mobile "/")으로 지정. PUBLISHED 상태만 가능, 기존 홈 지정은 자동 해제 |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": { "pageId": "page-001", "isHome": true }
}
```

#### Error Responses

| HTTP | code | message | 조건 | 대응 GWT |
|---|---|---|---|---|
| 409 | INVALID_STATUS | PUBLISHED 상태의 페이지만 홈으로 지정할 수 있습니다 | 상태 불일치 | — |

---

## 32. GET /api/mobile/v1/home — 홈 화면 조회 (2026-10-26 신설)

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/mobile/v1/home |
| 인증 | 불필요 (비로그인 허용) |
| 설명 | `is_home=true`인 전시 페이지의 섹션을 종류별로 resolve하여 반환. PRODUCT_LIST는 §17과 동일한 상품 데이터 resolve, EVENT_LIST는 `cat_event_banner_schedule` 조회 시점 유효 배너, RECOMMENDATION은 §19와 동일한 외부 SaaS 실시간 호출 |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "pageId": "page-001",
    "sections": [
      { "sectionType": "BANNER", "title": "메인 배너", "bannerImageUrl": "https://cdn.../main.jpg", "linkTarget": "/category/running" },
      {
        "sectionType": "PRODUCT_LIST",
        "title": "이번주 추천 상품",
        "products": [
          { "productId": "prod-001", "name": "러닝화 에어맥스", "priceOriginal": 179000, "priceSale": 152000, "thumbnailUrl": "https://cdn.../thumb.jpg" }
        ]
      },
      {
        "sectionType": "EVENT_LIST",
        "title": "진행중인 기획전",
        "banners": [
          { "eventKey": "prm-exhibition-ulid-020", "bannerImageUrl": "https://cdn.../exhibition-020-banner.jpg", "title": "가을 러닝 기획전", "linkTarget": "prm-exhibition-ulid-020" }
        ]
      },
      {
        "sectionType": "RECOMMENDATION",
        "title": "당신을 위한 추천",
        "products": [ { "productId": "prod-010", "name": "요가매트 프로" } ]
      }
    ]
  }
}
```

> `EVENT_LIST`의 `banners[]`는 `content_json`에 등록된 eventKey 중 조회 시점에 유효한
> (`start_at≤now<end_at`) 것만 포함한다 — 동기화가 안 됐거나 기간이 지난 eventKey는
> 결과에서 조용히 제외된다(Human Review, DM-시퀀스 §16 Human Review #4 참조).

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 404 | HOME_NOT_CONFIGURED | 홈 화면이 아직 설정되지 않았습니다 | `is_home=true`인 PUBLISHED 페이지 없음 |

---

## 33. POST /api/partner/v1/products/{productId}/duplicate — 상품 복제 등록 (2026-11-06 신설)

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/partner/v1/products/{productId}/duplicate |
| 인증 | Bearer {vendorId} (필수, 본인 상품만) |
| 설명 | 가격·재고·판매자상품코드를 제외한 모든 항목을 복사해 DRAFT 신규 상품을 생성(DBA §1.5.3). 이미지는 원본 파일을 그대로 참조(재업로드 없음) |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": { "productId": "prod-099", "sourceProductId": "prod-001", "status": "DRAFT" }
}
```

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 403 | FORBIDDEN | 본인 상품만 복제할 수 있습니다 | 타 판매자 소유 |

---

## 34. POST /api/partner/v1/products/bulk-upload — 상품 대량등록 (2026-11-06 소급 반영)

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/partner/v1/products/bulk-upload |
| 인증 | Bearer {vendorId} (필수) |
| Content-Type | multipart/form-data (엑셀 파일) |
| 설명 | 기본정보(상품명·카테고리·가격 등) 및 옵션(SKU)을 행 단위로 일괄 생성. 부분 성공 허용(DBA §1.5.2) |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "successCount": 18,
    "failCount": 2,
    "failures": [
      { "row": 5, "reason": "REQUIRED_FIELD_MISSING: priceOriginal" },
      { "row": 12, "reason": "PRICE_RULE_VIOLATION" }
    ]
  }
}
```

---

## 35. 찜하기 등록·해제 API 그룹 (2026-11-06 신설)

| Method | Path | 설명 |
|---|---|---|
| POST | /api/mobile/v1/products/{productId}/wishlist | 찜 등록 |
| DELETE | /api/mobile/v1/products/{productId}/wishlist | 찜 해제 |

| 항목 | 내용 |
|---|---|
| 인증 | Bearer {memberId} (필수) |
| 설명 | `cat_product_wishlist`에 상품당 회원 1건만 유지(DBA §1.14) |

#### Response 200 (등록)

```json
{ "code": "SUCCESS", "data": { "productId": "prod-001", "isWished": true } }
```

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 401 | UNAUTHORIZED | 로그인이 필요합니다 | 비로그인 상태 |

---

## 36. GET /api/mobile/v1/me/wishlist — 찜한 상품 목록 조회 (2026-11-06 신설)

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/mobile/v1/me/wishlist?page=1&size=20 |
| 인증 | Bearer {memberId} (필수) |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "products": [
      { "productId": "prod-001", "name": "러닝화 에어맥스", "priceSale": 152000, "status": "ON_SALE", "thumbnailUrl": "https://cdn.../thumb.jpg" }
    ],
    "pagination": { "page": 1, "size": 20, "totalCount": 7, "totalPages": 1 }
  }
}
```

> 상품이 `SOLD_OUT`/`DISCONTINUED`로 전환되면 해당 행이 삭제되므로 이 목록에는 항상
> 노출 가능한 상품만 남는다(DBA §1.14, DK-세부유스케이스 §20).

---

## 37. SNS 공유 메타데이터 조회 API 그룹 (2026-11-06 신설)

| Method | Path | 설명 |
|---|---|---|
| GET | /api/mobile/v1/products/{productId}/share | 상품 상세 공유 메타데이터 |
| GET | /api/mobile/v1/display-pages/{pageId}/share | 전시 페이지 공유 메타데이터 |

| 항목 | 내용 |
|---|---|
| 인증 | 불필요 |
| 설명 | 리워드 없음, 기존 데이터 재사용(신규 필드 없음, DBA §1.16). 이벤트 페이지(Promotion 소유)는 Catalog 범위 밖 |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "shareUrl": "https://runnshop.com/products/prod-001",
    "title": "러닝화 에어맥스 - runNshop",
    "imageUrl": "https://cdn.../thumb.jpg",
    "description": "쿠션감 좋은 데일리 러닝화"
  }
}
```

---

## 38. GET /api/internal/v1/products/{productId}/max-order-quantity — 주문 수량 제한 값 조회 (Promotion 연동, 2026-11-06 신설)

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/internal/v1/products/{productId}/max-order-quantity |
| 인증 | Service-to-Service (Promotion 도메인 전용) |
| 설명 | Promotion이 수량조건(1+1 등) 대상 상품을 등록·조회할 때 조회. 실제 필터링(조건 미달 상품 제외)은 Promotion이 수행(DBA §1.8, §6 HR #34) |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": { "productId": "prod-001", "maxOrderQuantity": null }
}
```

> `null`은 무제한을 의미한다. Order가 주문 시점에 수행하는 검증(§14 재고 차감과 별개 규칙)과
> 동일한 값을 공유한다.

---

## 39. 전시카테고리 상품순서 관리 API 그룹 (2026-11-09 신설)

| Method | Path | 설명 |
|---|---|---|
| GET | /api/admin/v1/display-categories/{displayCategoryId}/products | 매핑 상품 목록 조회(현재 순서·고정여부 포함) |
| PUT | /api/admin/v1/display-categories/{displayCategoryId}/products/order | 상품 순서·고정여부 저장(리스트 전체 교체) |

| 항목 | 내용 |
|---|---|
| 인증 | Bearer {adminId}, Role: MD-OPERATOR (필수) |
| 설명 | `cat_product_display_category`(DBA §2.5.2)에 매핑된 상품만 대상. 페이지네이션 없음 — 드래그앤드랍 재배열이 한 화면 안에서 이뤄져야 하므로 전체 목록을 반환(DN-admin §8 참조) |

#### Response 200 (목록 조회)

```json
{
  "code": "SUCCESS",
  "data": {
    "displayCategoryId": "dcat-001",
    "products": [
      { "productId": "prod-001", "name": "러닝화 에어맥스", "isPinned": true, "sortOrder": 0 },
      { "productId": "prod-010", "name": "요가매트 프로", "isPinned": false, "sortOrder": 1 },
      { "productId": "prod-003", "name": "폼롤러 디럭스", "isPinned": false, "sortOrder": 2 }
    ]
  }
}
```

#### Request Body 예시 (순서·고정여부 저장)

```json
{
  "products": [
    { "productId": "prod-001", "isPinned": true },
    { "productId": "prod-010", "isPinned": false },
    { "productId": "prod-003", "isPinned": false }
  ]
}
```

> 배열에 담긴 순서를 그대로 `sortOrder`(0부터 1씩 증가)로 일괄 저장한다(전체 교체, 부분
> 수정 아님). 저장 후 목록을 다시 조회하면 `isPinned=true`인 상품이 `sortOrder`와 무관하게
> 맨 위로 재배치되어 반환된다(DBA §2.5.3).

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 404 | DISPLAY_CATEGORY_NOT_FOUND | 전시 카테고리를 찾을 수 없습니다 | 존재하지 않는 displayCategoryId |
| 400 | PRODUCT_NOT_MAPPED | 매핑되지 않은 상품이 포함되어 있습니다 | 요청 배열의 productId가 해당 전시 카테고리에 매핑돼 있지 않음 |

---

## 40. GET /api/mobile/v1/display-categories — 전시카테고리 목록 조회 (고객, 2026-11-09 신설)

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/mobile/v1/display-categories |
| 인증 | 불필요 (비로그인 허용) |
| 설명 | 카테고리 메뉴(mobile `/category`)를 구성하는 트리 데이터. `is_active=true`인 노드만 반환(§12-1 admin용과 달리 비활성 제외) |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "displayCategories": [
      { "categoryId": "dcat-001", "parentId": null, "name": "러닝화", "depth": 1 },
      { "categoryId": "dcat-010", "parentId": "dcat-001", "name": "로드러닝화", "depth": 2 }
    ]
  }
}
```

---

## 41. GET /api/mobile/v1/products/ranking — 상품 랭킹 조회 (실시간/일간/주간, 2026-11-09 신설)

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/mobile/v1/products/ranking?period=REALTIME\|DAILY\|WEEKLY&displayCategoryId={id}(선택) |
| 인증 | 불필요 (비로그인 허용) |
| 설명 | `cat_product_sales_hourly`(DBA §1.17) 집계값을 기준(period)별 시간 범위로 합산해 정렬 반환. `REALTIME`=최근 3시간, `DAILY`=오늘 00:00(Asia/Seoul)~현재, `WEEKLY`=최근 7일(DBA §2.13). `displayCategoryId` 지정 시 해당 전시 카테고리에 매핑된 상품만 대상 |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "period": "DAILY",
    "products": [
      { "rank": 1, "productId": "prod-001", "name": "러닝화 에어맥스", "priceSale": 152000, "thumbnailUrl": "https://cdn.../thumb.jpg", "salesQuantity": 48 },
      { "rank": 2, "productId": "prod-010", "name": "요가매트 프로", "priceSale": 39000, "thumbnailUrl": "https://cdn.../thumb2.jpg", "salesQuantity": 35 }
    ]
  }
}
```

> 최대 50건 반환, 페이지네이션 없음(DBA §2.13). 집계 데이터가 없으면(신규 오픈 등) `products`가
> 빈 배열로 반환된다. ON_SALE/SOLD_OUT 외 상태로 전환된 상품은 결과에서 제외한다.

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 400 | INVALID_PERIOD | period 값이 올바르지 않습니다 | REALTIME/DAILY/WEEKLY 외 값 |

---

## 42. GNB 메뉴 관리 API 그룹 (admin, 2026-11-09 신설)

| Method | Path | 설명 |
|---|---|---|
| POST | /api/admin/v1/gnb-menus | 메뉴 등록 |
| PATCH | /api/admin/v1/gnb-menus/{id} | 메뉴 수정 |
| DELETE | /api/admin/v1/gnb-menus/{id} | 메뉴 삭제 |
| PATCH | /api/admin/v1/gnb-menus/order | 순서 일괄 저장(전체 교체) |

| 항목 | 내용 |
|---|---|
| 인증 | Bearer {adminId}, Role: MD-OPERATOR (필수) |
| 설명 | 단일 계층(서브메뉴 없음). `linkType`이 DISPLAY_PAGE/DISPLAY_CATEGORY면 참조 대상 존재 검증, EVENT_PAGE/EXTERNAL_URL은 URL 문자열 그대로 저장(검증 없음, `cat_event_banner_schedule.link_target`과 동일 패턴) |

#### Request Body (등록·수정)

```json
{
  "name": "이번주 테마",
  "linkType": "DISPLAY_PAGE",
  "linkTarget": "weekly-theme-2026w45",
  "isExposed": true,
  "displayStartAt": "2026.11.10 00:00:00",
  "displayEndAt": "2026.11.16 23:59:59"
}
```

#### Request Body (순서 저장)

```json
{ "menuIds": ["gnb-003", "gnb-001", "gnb-002"] }
```

> 배열 순서를 그대로 `sortOrder`(0부터 1씩 증가)로 일괄 저장한다(전체 교체, §24 전시카테고리
> 상품순서와 동일 패턴).

#### Response 200 (등록·수정)

```json
{
  "code": "SUCCESS",
  "data": { "id": "gnb-004", "name": "이번주 테마", "linkType": "DISPLAY_PAGE", "linkTarget": "weekly-theme-2026w45", "sortOrder": 3, "isExposed": true }
}
```

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 404 | DISPLAY_PAGE_NOT_FOUND | 참조한 전시 페이지를 찾을 수 없습니다 | linkType=DISPLAY_PAGE인데 존재하지 않는 slug |
| 404 | DISPLAY_CATEGORY_NOT_FOUND | 참조한 전시 카테고리를 찾을 수 없습니다 | linkType=DISPLAY_CATEGORY인데 존재하지 않는 ID |

---

## 42-1. GET /api/admin/v1/gnb-menus — GNB 메뉴 목록 조회 (admin, 전체, 2026-11-09 신설)

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/admin/v1/gnb-menus |
| 인증 | Bearer {adminId}, Role: MD-OPERATOR (필수) |
| 설명 | `is_exposed` 여부·전시기간과 무관하게 전체 목록을 `sort_order` 순으로 반환(관리 화면용, 페이지네이션 없음) |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "menus": [
      { "id": "gnb-001", "name": "랭킹", "linkType": "RANKING", "linkTarget": "/ranking?period=DAILY", "sortOrder": 0, "isExposed": true, "displayStartAt": null, "displayEndAt": null },
      { "id": "gnb-002", "name": "11월 러닝화 기획전", "linkType": "DISPLAY_PAGE", "linkTarget": "nov-running-event", "sortOrder": 1, "isExposed": true, "displayStartAt": "2026.11.01 00:00:00", "displayEndAt": "2026.11.30 23:59:59" }
    ]
  }
}
```

---

## 43. GET /api/mobile/v1/gnb-menus — GNB 메뉴 조회 (고객, 2026-11-09 신설)

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/mobile/v1/gnb-menus |
| 인증 | 불필요 (비로그인 허용) |
| 설명 | 홈 화면 Header 하단 퀵메뉴 바 전용. `is_exposed=true`이고 조회 시점이 전시기간 이내인 메뉴만 `sort_order` 오름차순으로 반환 |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "menus": [
      { "id": "gnb-001", "name": "랭킹", "linkType": "RANKING", "linkTarget": "/ranking?period=DAILY" },
      { "id": "gnb-002", "name": "11월 러닝화 기획전", "linkType": "DISPLAY_PAGE", "linkTarget": "nov-running-event" }
    ]
  }
}
```

> 노출조건을 만족하는 메뉴가 0건이면 `menus: []` 반환 — 홈 화면은 이 경우 퀵메뉴 바
> 영역 자체를 생략한다(DBA §2.11 "빈 섹션 생략"과 동일 사상).

---

## 44. GET /api/mobile/v1/display-pages/{slug} — 비홈 전시 페이지 뷰어 조회 (2026-11-09 신설)

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/mobile/v1/display-pages/{slug} |
| 인증 | 불필요 (비로그인 허용) |
| 설명 | §32(홈 화면 조회)와 **완전히 동일한 섹션 resolve 로직**을 재사용한다 — 홈도 `is_home=true`인 페이지 1건을 조회하는 것일 뿐이라, 이 API는 "slug로 특정 1건을 조회"하는 변형이다(DBA §2.15). `status=PUBLISHED`이고 `is_exposed=true`인 경우만 반환, 그 외는 404 |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "title": "11월 러닝화 기획전",
    "slug": "nov-running-event",
    "sections": [
      { "sectionType": "BANNER", "bannerImageUrl": "https://cdn.../banner.jpg", "linkTarget": "/products/prod-001" },
      { "sectionType": "PRODUCT_LIST", "products": [ { "productId": "prod-001", "name": "러닝화 에어맥스" } ] }
    ]
  }
}
```

> 응답 구조는 §32(홈 화면 조회) `HomeResponse`의 `sections[]`와 동일하다(BANNER/PRODUCT_LIST/
> EVENT_LIST/RECOMMENDATION 종류별 resolve 방식 포함).

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 404 | DISPLAY_PAGE_NOT_FOUND | 전시 페이지를 찾을 수 없습니다 | slug 미존재, 또는 status≠PUBLISHED, 또는 is_exposed=false |

> 이 API가 추가되면서 §21(SNS 공유, API-CAT-037b)과 GNB(§42, linkType=DISPLAY_PAGE)가
> 가리키던 "이동할 화면 없음" 공백이 해소된다(DQ 미진항목 #9·#13).

---

## 45. POST /api/partner/v1/products/{productId}/option-values/{optionValueId}/image — 옵션값 이미지 등록 (2026-11-09 신설)

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/partner/v1/products/{productId}/option-values/{optionValueId}/image |
| 인증 | Bearer {vendorId} (필수, 본인 상품만, API-CAT-049) / admin은 별도 `/api/admin/v1/products/{productId}/option-values/{optionValueId}/image`(API-CAT-050) — 소유자 검증 생략 |
| Content-Type | multipart/form-data |
| 설명 | 색상 등 1단계(depth=1) 옵션값에 대표 스와치 이미지를 등록한다(DBA §1.4.1). 동일 옵션값에 재업로드 시 기존 이미지를 덮어쓴다(복수 불가). 파일 형식·용량·해상도는 §9(상품 이미지)와 동일, 비율(정방형) 제약은 없음 |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": { "optionValueId": "optval-001", "imageUrl": "https://cdn.../red.jpg" }
}
```

#### Error Responses

| HTTP | code | message | 조건 | 대응 GWT |
|---|---|---|---|---|
| 422 | OPTION_IMAGE_DEPTH_INVALID | 1단계 옵션값에만 이미지를 등록할 수 있습니다 | 대상 옵션값의 소속 옵션그룹 depth=2 | AC-CAT-108 |
| 403 | FORBIDDEN | 본인 상품만 처리할 수 있습니다 | 타 판매자 소유(partner 경로) |
| 404 | PRODUCT_NOT_FOUND | 상품을 찾을 수 없습니다 | 존재하지 않는 productId 또는 optionValueId |

---

## 공통 규칙 (C6 API설계컨벤션 준수)

> `DL-인터페이스명세/order.md` "공통 규칙"과 동일 기준을 따른다. 이하는 Catalog에서 참조하는
> 요약이며, 전체 Envelope·Pagination·Idempotency-Key 규칙은 원문을 참조한다.

### 1. 에러 응답 Envelope

```json
{
  "code": "PRICE_RULE_VIOLATION",
  "message": "정가는 판매가 이상이어야 합니다",
  "errors": [
    { "field": "priceSale", "code": "PRICE_ORDER_INVALID", "message": "판매가가 정가를 초과했습니다." }
  ],
  "traceId": "trc_01HXYZ..."
}
```

### 2. HTTP Status 코드 사용 기준

| HTTP | 적용 대상 | 본 문서 내 해당 코드 |
|---|---|---|
| 400 | 요청 자체의 유효성 검증 실패 | `REQUIRED_FIELD_MISSING`, `REASON_REQUIRED`, `INVALID_QUANTITY`, `SUMMARY_LENGTH_EXCEEDED`(2026-11-09 신설) |
| 403 | 권한 없음 (리소스 소유자 불일치) | `FORBIDDEN` |
| 404 | 리소스 없음 | `PRODUCT_NOT_FOUND`, `PRICE_SCHEDULE_NOT_FOUND`, `DISPLAY_PAGE_NOT_FOUND`, `HOME_NOT_CONFIGURED` |
| 409 | 리소스/상태 충돌 | `INVALID_STATUS`, `INSUFFICIENT_STOCK`, `DUPLICATE_CATEGORY_NAME`, `SCHEDULE_LIMIT_EXCEEDED`, `SKU_NOT_SOLD_OUT` |
| 422 | 비즈니스 규칙 위반 (한도·구조 위반) | `PRICE_RULE_VIOLATION`, `IMAGE_LIMIT_EXCEEDED`, `OPTION_DEPTH_EXCEEDED`, `IMAGE_REQUIRED`, `DISPLAY_STYLE_NOT_ALLOWED`, `TAG_LIMIT_EXCEEDED`·`OPTION_IMAGE_DEPTH_INVALID`(2026-11-09 신설) |

### 3. Pagination

목록 조회 API(§12-1·§13-1·§17·§18·§27·§28·§30·§36)는 `pagination` 객체(`page`/`size`/`totalCount`/
`totalPages`)를 포함한다(전시 카테고리는 트리 구조라 예외, §12-1 참조). §17·§18(mobile)은
`sort` 기본값 `exposurePriority`·`direction` 기본값 `desc`(노출 우선순위가 높은 순)를 쓰며,
§27·§28·§30(admin/partner 관리용)은 운영 목적상 최신 변경分을 먼저 보기 위해 `sort` 기본값
`createdAt`(§27·§28) 또는 `updatedAt`(§30·§13-1)·`direction` 기본값 `desc`를 쓴다.

### 4. Idempotency-Key

| API | 대상 이유 |
|---|---|
| §3 POST /api/admin/v1/products (직매입 등록) | 중복 등록·중복 ON_SALE 전환 방지 |
| §13 PATCH /api/partner/v1/skus/{skuId}/stock | 재고 중복 반영 방지 (네트워크 재시도 시 이중 가산) |

### 5. 내부 연동 API (`/api/internal/v1/*`)

§14·§15·§23·§24·§25·§26은 Service-to-Service 전용이며 Bearer 토큰이 아닌 내부망 mTLS 또는
서비스 토큰으로 인증한다(구체 방식은 D9-컴포넌트 배포 구조에서 확정). 외부(mobile/admin/partner)
트래픽에서 직접 호출할 수 없다.

---

## Human Review

| # | 항목 | 사유 |
|---|---|---|
| 1 | §16·§26 `cat_product_price_schedule` 기간 중복 처리 | DBA §1.7.2·DF Human Review #6과 동일 쟁점 — Promotion 정책 소관, 허용 시 할인율 높은 순 우선조회·불허 시 등록 시점 중복체크. 확정 전까지 §26은 중복 체크 없이 그대로 등록한다 |
| 2 | **[Promotion 관련]** §32 홈 화면 조회가 의존하는 이벤트 배너 동기화(§Human Review 전반)의 Promotion 측 실제 발행 여부 | 사용자 확인(2026-10-26) — `cat_event_banner_schedule`을 채우는 이벤트(DI-이벤트플로우 참조)를 Promotion이 실제로 발행하는지 work-scope(Catalog 한정)상 미확인. Promotion 담당자 확인 필요 |
| 3 | §27 admin 상품 목록의 권한 분리(MD-REVIEWER vs MD-OPERATOR) | 심사 목록(§2 화면)은 MD-REVIEWER가, 일반 상품 목록(§3 화면)은 MD-OPERATOR가 쓰는데 현재 동일 API를 `status` 쿼리 파라미터만으로 구분한다 — 두 화면의 접근 권한을 쿼리 레벨이 아니라 역할 기반으로 완전히 분리해야 할지 미확정 |
| 4 | §33 상품 복제등록의 이미지 참조 방식 | 원본 이미지 파일을 그대로 참조(재업로드 없음, DBA §1.5.3) — 원본 삭제 시 복제본 이미지도 깨지는지(CDN 파일 생명주기)는 구현 단계 확인 필요 |
| 5 | §37 SNS 공유 메타데이터의 OG 태그 적용 범위 | API 응답은 JSON 메타데이터만 제공 — 실제 OG 태그 렌더링(SSR/메타태그 삽입)은 프론트엔드·인프라 담당, 본 API는 데이터 소스 역할만 |
| 6 | ~~§39 전시카테고리 상품순서를 소비하는 고객 조회 API 부재~~ | **해소(2026-11-09)** — §17이 `displayCategoryId` 기준으로 재정의되면서 `isPinned`/`sortOrder`를 실제로 적용해 반환한다 |

---

## 근거

| 항목 | 출처 |
|---|---|
| Endpoint 도출 | `deliverables/S3-상세설계/DK-세부유스케이스/catalog.md` API 호출 행위 |
| 에러코드 도출 | `deliverables/S3-상세설계/DJ-GWT수용기준/catalog.md` 예외 시나리오 Then절 |
| Path Prefix | `deliverables/S3-상세설계/DL-인터페이스명세/order.md` 공통 규칙과 동일 기준 — mobile(고객), admin(관리자), partner(판매자), internal(서비스 간) |
| 응답 구조 | 코딩 표준 `{ "code": "SUCCESS", "data": {...} }`, `DL-인터페이스명세/order.md` 에러 Envelope |
| 응답 필드 | `deliverables/S2-구조설계/DF-도메인모델ERD/catalog.md` 컬럼 정의 |
| 판매가 기간별 스케줄 API (§16·§16-1·§26) | DBA §1.7.2·§1.7.4, DD REQ-CAT-026·049~051 — "마스터 속성과 변동 속성 분리" 사용자 피드백(2026-10-26) 반영 |
| 전시카테고리 상품순서 관리 API (§39) | DD REQ-CAT-071~072, DBA §2.5.3(2026-11-09 신설) |
| 고객 상품 목록·검색의 카테고리 기준 변경(§17·§18), 전시카테고리 목록 조회(§40) | DD REQ-CAT-029·031·073, DBA §2.5.1~§2.5.2(2026-11-09 재정의) |
| 홈 화면 지정·조회 API (§31·§32) | 사용자 확인(2026-10-26) — DE-메뉴구조도/mobile.md "홈" 메뉴 공백 해소. DD REQ-CAT-052~053, DBA §2.7.2·§2.9 |
| 내부 연동 구분 | `deliverables/S2-구조설계/DI-이벤트플로우/catalog.md` 동기 PublicApi 목록 |
| 관리용 조회 API 보강 (§27~30) | DN(화면레이아웃) 목차 설계 중 발견된 공백 — DK §2·§3·§5·§7·§10·§11 화면이 참조할 목록·상세 조회 API가 기존 26개(쓰기 API 중심)에 없었음. mobile용(§17~19)과 달리 운영 전용 필드(rejectReason 등)·권한 범위가 달라 별도 API로 분리 |
| 목록·단건 조회 API 2차 보강 (§12-1·§13-1·§30-1) | DN-화면레이아웃/catalog-admin.md §5·§7, catalog-partner.md §12에 남아있던 `[TBD-API]` 3건 해소 — 분류체계 목록, 판매자 SKU 통합 조회(상품 경계를 넘는 조회라 §29 상품상세로 대체 불가), 전시 페이지 단건(섹션 구성 포함) 조회 |
| 상품 복제등록(§33)·대량등록(§34) | DD REQ-CAT-056~057, DBA §1.5.3·§1.5.2(2026-11-06) |
| 찜하기 등록·해제·목록(§35·§36) | DD REQ-CAT-061~062, DBA §1.14(2026-11-06 신설) |
| SNS 공유 메타데이터(§37) | DD REQ-CAT-063, DBA §1.16(2026-11-06 신설) |
| 주문 수량 제한 값 조회(§38) | DD REQ-CAT-060, DBA §1.8(2026-11-06 신설) — 실제 필터링은 Promotion, §6 HR #34 |
| 전시여부 플래그(§22 그룹 보강) | DD REQ-CAT-068, DBA §2.10(2026-11-06 신설) |
| 전시 콘텐츠유형×전시유형 2축(`displayStyle`, §30-1 보강) | DD REQ-CAT-053, DBA §2.3(2026-11-06 신설) |
| 상품 뱃지·찜여부·상품정보제공고시·주문수량제한 필드(§8·§17·§19 보강) | DD REQ-CAT-059b·061~062·064~066·070, DBA §1.3.8·§1.8·§1.14·§2.6 |
| 상품 요약·태그(§1·§3·§8·§17~19·§27~29 보강) | DD REQ-CAT-079, DBA §1.3.1·§1.3.3·§1.3.4(기존 정책, 2026-11-09 소급 반영) — `cat_product.summary`·`tags` 컬럼이 DF에 없던 공백을 메움 |
| 옵션값 이미지 등록(§45 신설), §19·§29 옵션값 응답 구조 변경(문자열 배열→객체 배열) | DD REQ-CAT-080~081, DBA §1.4.1(2026-11-09 신설) — API-CAT-049(partner)·050(admin) |
| 상품 단위 전시여부·검색노출 제외(§8·§17~19·§27~29 보강) | DD REQ-CAT-082~083, DBA §2.16(2026-11-09 신설) — SCR-A-C04-T6(전시 탭) 폐지, §8(기본정보 수정) API로 통합. 신규 API-CAT 번호 없음(기존 endpoint 필드 보강) |

