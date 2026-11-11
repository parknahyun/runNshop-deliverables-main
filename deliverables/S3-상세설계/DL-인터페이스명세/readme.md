# 인터페이스 명세

> **단계**: 상세설계 (S3)  
> **문서범위**: Bolt (Order + Payment + Catalog)  
> **문서종류**: Spec  
>
> **작성 목적**: GWT(DJ)의 예외를 에러코드로, 세부UC(DK)의 행위를 endpoint로 변환하여  
> API 계약(요청·응답·에러)을 확정한다. Frontend와 Backend 간의 명시적 계약 문서.
>
> **흐름 내 위치**:
> ```
> DJ GWT + DK 세부UC → DL 인터페이스 명세 → DM 시퀀스
> ```

---

도메인별 파일로 분리되어 있습니다.

| 구분 | 파일 |
|---|---|
| Order 도메인 (장바구니·주문·클레임·배송 API) | [order.md](order.md) |
| Payment 도메인 (결제수단·결제이력 API) | [payment.md](payment.md) |
| Catalog 도메인 (상품·재고·가격·전시·분류 API) | [catalog.md](catalog.md) |

---

## API 목록 요약

> **번호 읽는 법 (2026-10-29)**: `#`는 이 요약표의 연번(시퀀스·DQ 등 기존 참조 유지용)이고, **`본문 §`가 같은 endpoint의 order.md·payment.md 절 번호**다(두 번호는 일부 다르다). 하위 번호 행(5-1·5-2·23-1·40-1)은 2026-10-26·29에 신설된 절이다.
> **구현 현황**은 열로 두지 않고 order.md의 각 `## N.` 절 머리에 "구현 현황 (2026-10-29)" 한 줄(구현/Mock/DB/미구현 + 근거 컨트롤러)로 적었다. Payment 도메인 절([payment.md](payment.md))은 별도 담당 문서가 관리한다.

| # | 본문 § | Method | Path | 설명 | 채널 |
|---|---|---|---|---|---|
| 1 | §1 | POST | /api/mobile/v1/my/cart/items | 장바구니 담기 | mobile |
| 2 | §2 | GET | /api/mobile/v1/my/cart | 장바구니 조회 | mobile |
| 3 | §3 | PATCH | /api/mobile/v1/my/cart/items/{cartItemId}/quantity | 수량 변경 | mobile |
| 4 | §4 | DELETE | /api/mobile/v1/my/cart/items/{cartItemId} | 장바구니 삭제 | mobile |
| 5 | §5 | POST | /api/mobile/v1/my/orders/sheet | 주문서 생성 | mobile |
| 5-1 | §5-1 | GET | /api/mobile/v1/my/orders/sheet/{orderSheetId} | 주문서 재조회 (API-051, 신규 2026-10-26) | mobile |
| 5-2 | §5-2 | PUT | /api/mobile/v1/my/orders/sheet/{orderSheetId}/discount | 주문서 쿠폰·포인트 적용 (API-052, 신규 2026-10-26) | mobile |
| 6 | §6 | POST | /api/mobile/v1/my/orders/{orderSheetId}/pay | 결제 요청 | mobile |
| 7 | §7 | POST | /api/mobile/v1/my/orders/{orderId}/cancel | 고객 주문 취소 | mobile |
| 8 | §8 | POST | /api/mobile/v1/my/orders/{orderId}/confirm | 구매확정 | mobile |
| 9 | §9 | PUT | /api/mobile/v1/my/orders/{orderId}/shipping-address | 배송지 변경 | mobile |
| 10 | §10 | POST | /api/mobile/v1/my/orders/{orderId}/claims | 반품/교환 신청 | mobile |
| 10-1 | §10-1 | POST | /api/mobile/v1/my/claims/{claimId}/cancel | 클레임 자진 취소 (본문 §10-1, 시퀀스 §7-2) | mobile |
| 11 | §11 | GET | /api/mobile/v1/my/orders | 내 주문 목록 | mobile |
| 12 | §12 | GET | /api/mobile/v1/my/payment-methods | 결제수단 목록 | mobile |
| 13 | §13 | POST | /api/mobile/v1/my/payment-methods | 결제수단 등록 | mobile |
| 14 | §14 | DELETE | /api/mobile/v1/my/payment-methods/{methodId} | 결제수단 삭제 | mobile |
| 15 | §28 | GET | /api/mobile/v1/my/claims | 내 클레임 목록 | mobile |
| 16 | §29 | GET | /api/mobile/v1/my/claims/{claimId} | 내 클레임 상세 | mobile |
| 17 | §30 | GET | /api/mobile/v1/my/orders/{orderId} | 내 주문 상세 | mobile |
| 18 | §31 | POST | /api/mobile/v1/my/claims/{claimId}/shipping-payment | 클레임 배송비 결제 | mobile |
| 19 | §32 | PUT | /api/mobile/v1/my/cart/items/{cartItemId}/option | 장바구니 옵션 변경 | mobile |
| 19-1 | §32-1 | GET | /api/mobile/v1/my/orders/{orderSheetId}/coupon-combinations | 쿠폰 조합별 할인 계산 (캐시) | mobile |
| 19-2 | §32-2 | POST | /api/mobile/v1/my/orders/{orderSheetId}/calculate | 쿠폰 확정 재계산 (Phase 2) | mobile |
| 20 | §15 | GET | /api/admin/v1/orders | 주문 검색 (어드민) | admin |
| 21 | §16 | GET | /api/admin/v1/orders/{orderId} | 주문 상세 | admin |
| 22 | §17 | POST | /api/admin/v1/orders/{orderId}/force-cancel | 예외 취소 | admin |
| 22-1 | §17-1 | POST | /api/admin/v1/orders/{orderId}/claims | 어드민 클레임 접수 (API-058, 신규 2026-11-03·미구현) | admin |
| 23 | §18 | GET | /api/admin/v1/claims | 클레임 목록 | admin |
| 23-1 | §18-1 | GET | /api/admin/v1/claims/{claimId} | 클레임 상세 (어드민, API-056, 신규 2026-10-29·미구현) | admin |
| 24 | §19 | POST | /api/admin/v1/claims/{claimId}/start | 클레임 처리 시작 (API-050, 본문 §19) | admin |
| 24-1 | §19-1 | POST | /api/admin/v1/claims/{claimId}/blame-decision | 귀책 판정 (API-026, 본문 §19-1) | admin |
| 25 | §20 | POST | /api/admin/v1/claims/{claimId}/complete | 클레임 완료 (환불 진행) | admin |
| 26 | §21 | POST | /api/admin/v1/claims/{claimId}/reject | 클레임 반려 | admin |
| 27 | §33 | POST | /api/admin/v1/claims/{claimId}/refund | 환불 처리 (수동) | admin |
| 28 | §34 | POST | /api/admin/v1/claims/{claimId}/dispose | 폐기 처리 | admin |
| 29 | §35 | POST | /api/admin/v1/claims/{claimId}/request-return-payment | 반송 배송비 추가결제 요청 | admin |
| 30 | §22 | GET | /api/partner/v1/orders | 판매자 주문 목록 | partner |
| 31 | §23 | GET | /api/partner/v1/orders/{orderId} | 판매자 주문 상세 | partner |
| 32 | §24 | POST | /api/partner/v1/orders/{orderId}/ship | 출고 처리 | partner |
| 33 | §25 | GET | /api/partner/v1/shipping | 배송 관리 (출고+회수+재배송 통합) | partner |
| 34 | §26 | POST | /api/partner/v1/shipping/{orderId} | 출고/재배송 운송장 등록 | partner |
| 35 | §36 | POST | /api/partner/v1/shipping/{claimId}/pickup | 수거 운송장 등록 | partner |
| 36 | §27 | POST | /api/partner/v1/claims/{claimId}/pickup-confirm | 입고 확인 → 품질점검 시작 | partner |
| 37 | §37 | POST | /api/partner/v1/claims/{claimId}/inspect-pass | 품질점검 합격 (수거완료) | partner |
| 38 | §38 | POST | /api/partner/v1/claims/{claimId}/inspect-reject | 품질점검 거부 (수거거부) | partner |
| 39 | §39 | POST | /api/partner/v1/claims/{claimId}/return-ship | 반송 운송장 등록 | partner |
| 39-1 | §39-1 | POST | /api/partner/v1/claims/{claimId}/exchange-ship | 교환상품 선출고 운송장 등록 | partner |
| 39-2 | §39-2 | POST | /api/admin/v1/claims/{claimId}/return-delivered | 반송 배송완료 확인 (택배사 콜백/배치) | admin |
| 40 | §40 | GET | /api/partner/v1/claims | 클레임 현황 (통합) | partner |
| 40-1 | §40-1 | GET | /api/partner/v1/claims/{claimId} | 클레임 상세 (판매자, API-057, 신규 2026-10-29·미구현) | partner |
| 41 | §41 | GET | /api/mobile/v1/my/payments | 내 결제 이력 조회 | mobile |
| 42 | §42 | GET | /api/admin/v1/payments/search | CS 결제 검색 | admin |
| 43 | §43 | GET | /api/admin/v1/payments/{paymentId}/pg-logs | PG 거래 로그 조회 | admin |
| 44 | §44 | POST | /api/partner/v1/shipping/{shipmentId}/reship | 배송 실패 재발송 처리 | partner/admin |
| 45 | §45 | POST | /api/internal/v1/payments/mask-personal-data | 결제 개인정보 마스킹 (API-060, 신규 2026-11-03·미구현, 엔드포인트 "(안)") | internal |
| 46 | §46 | POST | /api/internal/v1/pg-webhooks/virtual-account/deposit | 가상계좌 입금 통보 웹훅 (API-059, 신규 2026-11-03·미구현, 엔드포인트 "(안)") | pg-webhook |

---

## 공통 규칙 (C6 API설계컨벤션 준수)

> 이하 개별 API의 에러 응답 테이블은 `code`/`message`/`조건`/`대응 GWT` 컬럼만 표기하여 가독성을 확보한다.
> **모든 에러 응답은 아래 Envelope을 따르며**, 개별 API 섹션에서 생략된 `errors[]`/`traceId`도 실제 응답에는 포함된다(C6 §6.3).

### 1. 에러 응답 Envelope (전체 형태)

```json
{
  "code": "STOCK_NOT_AVAILABLE",
  "message": "재고가 부족합니다",
  "errors": [
    { "field": "skuId", "code": "INSUFFICIENT_STOCK", "message": "요청 수량이 재고를 초과합니다." }
  ],
  "traceId": "trc_01HXYZ..."
}
```

- `errors[]`: 필드 단위 유효성 검증 실패 시에만 포함(예: `INVALID_QUANTITY`, `TERMS_NOT_AGREED`, `ADDRESS_REQUIRED` 등 입력값 문제). 단일 비즈니스 규칙 위반(예: `CLAIM_PERIOD_EXPIRED`)은 `errors[]` 없이 `code`+`message`만으로 충분.
- `traceId`: 운영 환경에서 항상 포함(로그 추적용). 프로토타입 Mock 응답에도 `trc_` 접두 ULID를 고정 포함한다.

### 2. HTTP Status 코드 사용 기준 (C6 §7)

| HTTP | 적용 대상 | 본 문서 내 해당 코드 |
|---|---|---|
| 400 | 요청 자체의 유효성 검증 실패 (필수값 누락·형식 오류) | `INVALID_QUANTITY`, `TRACKING_NO_REQUIRED`, `ADDRESS_REQUIRED`, `TERMS_NOT_AGREED`, `REASON_REQUIRED`, `EXCHANGE_SKU_REQUIRED`, `CLAIM_PHOTO_REQUIRED`, `INSPECT_PHOTO_REQUIRED`, `INVALID_DATE_RANGE`, `INVALID_PAGE`, `INVALID_SIZE`, `INVALID_ORDER_ID`, `CART_ITEMS_REQUIRED`, `INVALID_ITEM_PRICE`, `INVALID_PAYMENT_METHOD`, `PAYMENT_METHOD_NOT_READY`, `REFUND_ACCOUNT_REQUIRED`·`REFUND_ACCOUNT_INVALID`(2026-10-29, 미구현), `PAYMENT_FAILED`(PG 승인 거절). 역직렬화 실패는 공통 `INVALID_REQUEST_BODY`(order.md 머리말) |
| 409 | 리소스/상태 충돌 (재고 부족, 이미 처리된 상태, 중복 요청) | `STOCK_NOT_AVAILABLE`, `EXCEED_STOCK`, `OPTION_SOLD_OUT`, `PRODUCT_NOT_AVAILABLE`, `CANCEL_NOT_ALLOWED`, `CONFIRM_NOT_ALLOWED`, `ADDRESS_CHANGE_NOT_ALLOWED`, `SHIP_NOT_ALLOWED`, `CLAIM_NOT_ALLOWED`, `CLAIM_CANCEL_NOT_ALLOWED`, `CLAIM_ALREADY_DECIDED`, `EXCHANGE_STOCK_UNAVAILABLE`, `CARD_RESTRICTED`, `RESHIP_NOT_ALLOWED`, `RETURN_DELIVER_NOT_ALLOWED`, `NOT_EXCHANGE_CLAIM`(§39-1, 교환 클레임이 아님 — 이전 표는 400으로 잘못 분류), `INVALID_STATUS` |
| 422 | 비즈니스 규칙 위반 (기한 초과, 한도 초과, 조합 불일치) | `CLAIM_PERIOD_EXPIRED`, `PAYMENT_EXPIRED`, `CART_FULL`, `EXCHANGE_SKU_MISMATCH`, `COUPON_NOT_APPLICABLE`, `COUPON_EXPIRED`, `POINT_EXCEED`, `ORDER_SHEET_ALREADY_PROCESSED`, `AMOUNT_MISMATCH`(§31, 2026-10-29 확정) |
| 404 | 리소스 없음 | `CART_ITEM_NOT_FOUND`, `CLAIM_NOT_FOUND`, `PAYMENT_NOT_FOUND`, `SHIPMENT_NOT_FOUND`, `ORDER_NOT_FOUND`, `ORDER_SHEET_NOT_FOUND` |
| 403 | 소유권·권한 위반 | `FORBIDDEN`, `ORDER_SHEET_FORBIDDEN` |
| 401 | 인증 실패 | `UNAUTHORIZED` |

> 아래 개별 API 에러 테이블의 HTTP 컬럼은 위 기준에 따라 정정되어 있다. (예: 기존 400으로 뭉뚱그려졌던 재고부족/상태충돌류 → 409, 기한초과류 → 422)
>
> **2026-08-24 동기화**: 시퀀스(DM)가 이 정정을 반영하지 못하고 20건에서 옛 400을 그대로 쓰고 있던 것을 DL 기준으로 정정. 또한 시퀀스(DM) §12/§13/§14/§15/§20/§21이 실제로 분기하던 `INVALID_STATUS`(상태 충돌, 409)가 이 문서 §18/§33/§34/§35/§37/§38에 누락되어 있어 추가함 — 상태 충돌류이므로 위 409 분류를 따름.

### 3. Pagination (목록 API 공통, C6 §6.2)

목록 조회 API는 Query Parameter로 `sort`(필드명, camelCase)와 `direction`(`asc`|`desc`)을 추가로 지원하며,
Response는 `totalCount` 단일 필드 대신 `pagination` 객체를 포함한다.

```json
{
  "code": "SUCCESS",
  "data": {
    "orders": [ ... ],
    "pagination": { "page": 1, "size": 10, "totalCount": 12, "totalPages": 2 }
  }
}
```

> 배열 필드명은 도메인 가독성을 위해 `orders`/`claims`/`payments` 등 리소스명을 유지한다(C6 예시의 `items`는 범용 표기이며, 도메인 문서에서는 리소스명 사용을 허용).
> `sort` 기본값은 API별로 다르며 각 섹션의 Query 예시에 명시한다. `direction` 기본값은 `desc`.

### 4. Idempotency-Key (C6 §4)

금액이 오가거나 중복 실행 시 부작용이 있는 POST API는 `Idempotency-Key: {ULID}` 헤더를 지원한다(유효기간 24시간, 동일 Key 재요청 시 최초 처리 결과를 그대로 반환).

| API | 대상 이유 |
|---|---|
| #5 POST /api/mobile/v1/my/orders/sheet | 주문서 중복 생성 방지 (구현: 헤더 미처리) |
| #6 POST /api/mobile/v1/my/orders/{orderSheetId}/pay | 결제 요청 중복 접수 방지 (재고 이중 선점·이중 결제 방지) |
| #31 POST /api/mobile/v1/my/claims/{claimId}/shipping-payment | 배송비 결제 중복 접수 방지 |

---

## 근거

| 항목 | 출처 |
|---|---|
| Endpoint 도출 | 세부 유스케이스(DK) API 호출 행위 |
| 에러코드 도출 | GWT(DJ) 예외 시나리오 Then절 |
| Path Prefix | 컴포넌트(D9) 인증 규칙: v1(고객), admin/v1(관리자), partner/v1(판매자) |
| 응답 구조 | 코딩 표준 `{ "code": "SUCCESS", "data": {...} }` |
| 응답 필드 | 화면 레이아웃(DN) + mock JSON 데이터 |

---

## 필드명 규칙·주석 (2026-10-29)

| 항목 | 규칙·차이 |
|---|---|
| 택배사·운송장 | **요청**은 `deliveryCompany`·`trackingNo`(§26·36·39·39-1·39-2), **응답**은 `carrier`·`trackingNumber`(코드 `buildAdminDeliveryMap` 등 기준). §44 재발송 요청만 `carrier`를 쓴다 — 같은 의미이며 설계 당시 이름이 갈라졌다. §25 목록 응답의 `deliveryCompany`·`trackingNo`도 같은 사정이다. 필드명 통일은 FE·Mock 영향이 있어 하지 않았다 |
| 판매자 응답의 `platformOrderNo` | §22·§23(판매자 주문 목록·상세)의 `platformOrderNo`는 설계상 판매자 주문번호(`V…`)를 담는다(의미상 `vendorOrderNo`). 어드민·고객 응답은 플랫폼 주문번호(`P…`). 현재 구현 §23은 `P…`를 반환한다 |
| 금액 필드 | `amount`=주문금액, `totalPayment`/`paymentAmount`=결제금액(하위호환 필드명, order.md 머리말 금액 용어 참조) |
| 귀책 | 판정 전 `responsibility`=null(화면 "판정 전"), 고객 자진신고 `submittedResponsibility` |
