# 인터페이스 명세 — Order 도메인

> 상위 문서: [readme.md](readme.md)
> **단계**: 상세설계 (S3) | **문서범위**: Bolt (Order) | **문서종류**: Design
> Payment 관련 API는 [DL-인터페이스명세/payment.md](payment.md) 참조

> **금액 용어 (2026-10-29)**: 이 문서의 금액 필드는 [DBA order.md 3.7.5](../../S2-구조설계/DBA-도메인정책서/order.md)의 용어를 따른다 — 상품금액 − 할인금액 + 배송비 − 배송비 할인금액 = **주문금액** = 포인트 + **결제금액**(PG 결제분 = 주문금액 − 포인트). 필드명은 하위호환을 위해 유지한 것이 있다(`totalPayment`·`total_payment` = 결제금액, 장바구니 `summary.total_payment` = 주문 예상 금액). "결제 요청금액"·"실결제금액" 용어는 폐기했다.

> **신규 (2026-10-19 구현 확인)**: 이 문서의 모든 POST/PUT API(요청 바디가 있는 API)는 JSON 역직렬화 자체가 실패하면(필수 필드 타입 불일치 등) `400 INVALID_REQUEST_BODY`를 반환한다 — `com.runnshop.common.exception.GlobalExceptionHandler`(전 도메인 공용 파일)에 핸들러가 추가됐다. Order 도메인 문서 범위를 넘는 공용 처리이므로 개별 API의 Error Responses 표에는 반복 기재하지 않고 이 각주로 1회만 명시한다.

---

## 1. POST /api/mobile/v1/my/cart/items — 장바구니 담기

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음(`CustomerCartController`에 담기 endpoint 없음). 담기 본 구현은 Bolt13 SC01-1.

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/mobile/v1/my/cart/items |
| 인증 | Bearer {memberId} (필수) |
| 설명 | 상품을 장바구니에 추가. 동일 상품+옵션 존재 시 수량 합산 |

#### Request Body

```json
{
  "productId": "prod-001",
  "skuId": "sku-001",
  "quantity": 2
}
```

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "cartItemId": "cart-001",
    "productId": "prod-001",
    "skuId": "sku-001",
    "quantity": 2,
    "unitPrice": 152000,
    "totalCartCount": 5
  }
}
```

#### Error Responses

| HTTP | code | message | 조건 | 대응 GWT |
|---|---|---|---|---|
| 422 | CART_FULL | 장바구니가 가득 찼습니다 (최대 50개) | 50개 초과 | AC-ORD-005 |
| 409 | PRODUCT_NOT_AVAILABLE | 현재 구매할 수 없는 상품입니다 | 품절·판매중지 | AC-ORD-008 |
| 400 | INVALID_QUANTITY | 수량은 1~99 사이여야 합니다 | 수량 범위 초과 | — |
| 401 | UNAUTHORIZED | 로그인이 필요합니다 | 토큰 없음/만료 | — |

---

## 2. GET /api/mobile/v1/my/cart — 장바구니 조회

> **구현 현황 (2026-10-29)**: Mock — `CustomerCartController.getCart` → `CartService.getCart`가 `mock/order/mobile__GET_my_cart.json`을 그대로 반환한다. DB 저장·회원별 구분 없음(Bolt1 SC01-3에서 DB 전환 예정).

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/mobile/v1/my/cart |
| 인증 | Bearer {memberId} (필수) |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "total_count": 3,
    "vendors": [
      {
        "vendor_id": 10,
        "vendor_name": "나이키코리아",
        "shipping_fee": 3000,
        "free_threshold": 50000,
        "items": [
          {
            "cart_item_id": 1,
            "product_id": 101,
            "product_name": "나이키 페가수스 41",
            "image_url": "https://...",
            "color": "블랙",
            "size": "265",
            "price_original": 179000,
            "price_sale": 152000,
            "quantity": 1,
            "stock": 7,
            "status": "ON_SALE"
          }
        ]
      }
    ],
    "summary": {
      "total_product_price": 469000,
      "total_discount": -48000,
      "cart_discount": -3000,
      "total_shipping_fee": 0,
      "total_payment": 418000,
      "point_balance": 5200,
      "coupon_benefit_text": "사용 가능 쿠폰 2장"
    }
  }
}
```

---

## 3. PATCH /api/mobile/v1/my/cart/items/{cartItemId}/quantity — 수량 변경

> **구현 현황 (2026-10-29)**: Mock — `CustomerCartController.updateQuantity` → `CartService.updateQuantity`가 Mock 데이터셋으로 범위(`INVALID_QUANTITY`)·재고(`EXCEED_STOCK`)·존재(`CART_ITEM_NOT_FOUND`)를 검증·계산만 하고 저장하지 않는다. 응답은 `{cartItemId, quantity, subtotal}`.

| 항목 | 내용 |
|---|---|
| Method | PATCH |
| Path | /api/mobile/v1/my/cart/items/{cartItemId}/quantity |
| 인증 | Bearer {memberId} (필수) |

#### Request Body

```json
{ "quantity": 3 }
```

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": { "cartItemId": "cart-001", "quantity": 3, "subtotal": 456000 }
}
```

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 400 | INVALID_QUANTITY | 수량은 1~99 사이여야 합니다 | 범위 초과 |
| 409 | EXCEED_STOCK | 재고 수량을 초과합니다 | 재고 부족 |
| 404 | CART_ITEM_NOT_FOUND | 장바구니 항목을 찾을 수 없습니다 | 존재하지 않는 ID |

---

## 4. DELETE /api/mobile/v1/my/cart/items/{cartItemId} — 장바구니 삭제

> **구현 현황 (2026-10-29)**: Mock — `CustomerCartController.removeItem`이 항상 성공 Mock(`data: null`)을 반환한다. 존재 검증·실제 삭제 없음.

| 항목 | 내용 |
|---|---|
| Method | DELETE |
| Path | /api/mobile/v1/my/cart/items/{cartItemId} |
| 인증 | Bearer {memberId} (필수) |

#### Response 200

```json
{ "code": "SUCCESS", "data": null }
```

---

## 5. POST /api/mobile/v1/my/orders/sheet — 주문서 생성

> **구현 현황 (2026-10-29)**: 구현 — `OrderController.createOrderSheet`. 임시주문(TEMP)·판매자 주문·상품은 DB 저장, 배송지·쿠폰 목록·포인트 잔액·결제수단·약관은 Mock. `Idempotency-Key`는 처리하지 않는다.

> 최종 수정: 2026-10-26 (임시주문 생성 — 요청 바디 `items`, order_sheet_id=platformOrderNo, 조회 API 추가 / 쿠폰·포인트 적용 영속화 — `PUT .../sheet/{id}/discount` 신설)

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/mobile/v1/my/orders/sheet |
| 인증 | Bearer {memberId} (필수) |
| Header | `Idempotency-Key: {ULID}` (선택, 중복 생성 방지) |
| 설명 | 장바구니 선택 상품으로 주문서 생성. 배송지·쿠폰·포인트·결제수단 정보 반환 |

#### Request Body

```json
{ "items": [ { "vendorId": 10, "productId": 101, "skuId": 101, "productName": "나이키 페가수스 41", "priceOriginal": 179000, "priceSale": 152000, "quantity": 1, "color": "블랙", "size": "265" } ] }
```

> **신규 (2026-10-19 프로토타입 구현 반영)**: 당시 구현은 요청 바디를 받지 않았다(`cartItemIds` 미사용) — Cart 영속 계층이 코드베이스에 없어 서버가 조회할 대상이 없었기 때문이다(`.agents/tasks/order-create-mobile-api/design.md` §0 Finding 3). **(2026-10-26 변경 — 임시주문 생성·연결)** 요청 바디로 장바구니에서 선택한 `items`(`vendorId`/`productId`/`skuId`/`productName`/`priceOriginal`/`priceSale`/`quantity`/`color`/`size`)를 받는다(비어 있으면 400 `CART_ITEMS_REQUIRED`). 서버는 이 상품으로 임시주문(`ord_platform_order` `status=TEMP` + vendor별 `ord_order`/`ord_order_item` `TEMP`, 금액=상품합계, 배송지는 기본 배송지 placeholder)을 저장하고 주문상태 이력 `(신규) → TEMP`("주문서 진입, 임시주문 생성")를 기록한다. 응답의 `order_sheet_id`는 이 임시주문의 `platformOrderNo`(`PyyMMdd-NNNNN-00`)이며, §6의 `{orderSheetId}`로 전달되면 서버가 임시주문을 조회해 이어받는다(기존 stateless UUID 폐기). 호출마다 임시주문이 1건 생기므로 이탈한 임시주문 정리(만료 삭제)는 후속 과제이며, `TEMP`는 어드민/모바일 주문 목록·집계에서 제외된다. 응답의 `orders[]`/`price_summary`는 저장된 임시주문 값이고 나머지(배송지/쿠폰/포인트/결제수단/약관)는 Mock이다. **`GET /api/mobile/v1/my/orders/sheet/{orderSheetId}`**(2026-10-26 신설)는 저장된 임시주문으로 같은 응답을 다시 만들어 주며(새로고침·재진입, 404/403/422는 §6과 동일), 주문서 화면은 이 API로 그려진다(모바일 `/orders/new?sheet={order_sheet_id}`). `addresses[]`(이 Mock 응답 그대로, 고정 2건)는 §6 결제요청의 `addressId` 해석에 실제로 쓰인다. **(2026-10-26 변경 — 쿠폰·포인트 영속화)** 주문서에서 적용한 쿠폰/포인트는 임시주문에 저장된다. **`PUT /api/mobile/v1/my/orders/sheet/{orderSheetId}/discount`**(신설, 요청 `{ couponId: String?, pointUsed: Int? }` — `couponId=null`/`pointUsed=0`이면 해제)는 쿠폰(`PromotionApi.validateCoupon`)·포인트(잔액/결제금액 상한)를 검증한 뒤 `ord_platform_order_discount`(`ORDER_COUPON`, `coupon_code`, 할인액 — 기존 행은 교체, 해제 시 삭제)와 `ord_platform_order`의 `total_discount_amount`/`point_used_amount`/`payment_amount`를 갱신하고 갱신된 주문서(이 §5 응답과 동일 형태)를 반환한다. 오류는 `COUPON_NOT_APPLICABLE`(422)/`POINT_EXCEED`(422)/`INVALID_ITEM_PRICE`(400, 음수 포인트)/404/403/422(`ORDER_SHEET_*`)이며 검증 실패 시 기존 저장값은 유지된다. 이 §5 응답과 `GET .../sheet/{id}`의 `price_summary`(`coupon_discount`=-할인액, `point_used`, `total_payment`)는 저장값에서 만들어지고, 응답에 `selected_coupon_id`(미적용 시 빈 문자열)/`point_used`가 추가돼 재진입·새로고침 시 선택 상태를 복원한다.

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "order_sheet_id": "P261026-00001-00",
    "orderer": { "name": "홍길동", "phone": "010-****-5678", "email": "runner@runNshop.com" },
    "addresses": [ { "address_id": 1, "recipient": "홍길동", "phone": "010-****-5678", "zip_code": "06234", "address": "서울특별시 강남구 테헤란로 123", "address_detail": "런앤샵타워 5층", "is_default": true } ],
    "orders": [ { "vendor_id": 10, "vendor_name": "나이키코리아", "items": [...] } ],
    "coupons": { "available_count": 2, "items": [...] },
    "point": { "balance": 5200, "usable": 5200, "min_use": 1000 },
    "payment_methods": [ { "type": "CARD", "label": "신용카드" } ],
    "price_summary": { "total_product_price": 469000, "product_discount": -48000, "cart_discount": -3000, "coupon_discount": 0, "point_used": 0, "shipping_fee": 0, "order_amount": 418000, "total_payment": 418000 },
    "terms": [ { "term_id": "T001", "title": "구매조건 확인 및 결제 진행에 동의", "required": true, "content": "본 약관은 ... 내용을 포함합니다." } ]
  }
}
```

> **신규 (2026-10-23 프로토타입 구현 반영)**: `terms[]`에 `content`(string, 약관 전문 텍스트) 필드가 추가됐다 — 원래 이 §5에는 정의돼 있지 않던 필드다(`term_id`/`title`/`required` 3필드만 있었음). 약관 상세보기 모달(`TermDetailModal.tsx`, `mobile-order-ux-gaps` 작업)이 "보기" 버튼 클릭 시 약관 전문을 보여주기 위해 신규 추가했다. 근거: `.agents/tasks/mobile-order-ux-gaps/design.md` 결정 3.

---

## 5-1. GET /api/mobile/v1/my/orders/sheet/{orderSheetId} — 주문서 재조회 (API-051)

> **구현 현황 (2026-10-29)**: 구현 — `OrderController.getOrderSheet`.

> 신규 (2026-10-26 구현, 2026-10-29 절 분리 — 이전에는 §5 각주로만 서술)

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/mobile/v1/my/orders/sheet/{orderSheetId} |
| 인증 | Bearer {memberId} (필수) |
| 설명 | 주문서 진입 시 만든 임시주문(TEMP)을 다시 읽어 주문서 응답을 재구성한다. 새로고침·재진입 때 새 임시주문을 만들지 않고 **저장된 값**(상품·쿠폰·포인트·금액)을 그대로 그린다. |
| 호출원 | SCR-M-002 주문서 (`app/orders/new/page.tsx`) |

#### Path Parameter

| 이름 | 설명 |
|---|---|
| orderSheetId | 주문서 생성(§5) 응답의 `order_sheet_id` = 임시주문의 `platformOrderNo`(`PyyMMdd-NNNNN-00`) |

#### Response 200

§5 Response와 같은 구조다. 다음 값은 저장된 임시주문에서 채운다.

| 필드 | 출처 |
|---|---|
| `orders[]` | 임시주문의 판매자 주문·상품(스냅샷) |
| `selected_coupon_id` | 적용된 쿠폰 코드(`ord_platform_order_discount`), 미적용은 빈 문자열 |
| `point_used` | 저장된 포인트 사용액(`point_used_amount`) |
| `price_summary` | `total_product_price`(상품금액), `coupon_discount`(−할인금액), `point_used`, `shipping_fee`, `order_amount`(주문금액), `total_payment`(결제금액) — [DBA order.md 3.7.5](../../S2-구조설계/DBA-도메인정책서/order.md) |

> 배송지·쿠폰 목록·포인트 잔액·결제수단·약관·주문자는 해당 도메인(Member·Promotion) 영속화 전이라 주문서 Mock에서 가져온다(Port + Mock 원칙). 상품·금액·쿠폰 선택·포인트 사용액만 주문 도메인 DB 값이다.

#### 에러

| HTTP | code | message | 조건 |
|---|---|---|---|
| 404 | ORDER_SHEET_NOT_FOUND | 주문서를 찾을 수 없습니다 | `orderSheetId`에 해당하는 임시주문 없음 |
| 403 | ORDER_SHEET_FORBIDDEN | 본인의 주문서가 아닙니다 | 다른 회원의 주문서 |
| 422 | ORDER_SHEET_ALREADY_PROCESSED | 이미 결제가 진행된 주문서입니다 | 상태가 TEMP가 아님(결제하기 이후) |

---

## 5-2. PUT /api/mobile/v1/my/orders/sheet/{orderSheetId}/discount — 주문서 쿠폰·포인트 적용 (API-052)

> **구현 현황 (2026-10-29)**: 구현 — `OrderController.applyOrderSheetDiscount`. 쿠폰 검증·포인트 잔액은 Port Mock(`PromotionApi`·`MemberApi`).

> 신규 (2026-10-26 구현, 2026-10-29 절 분리 — 이전에는 §5 각주로만 서술). 시퀀스: [DM §3-1](../DM-시퀀스/order.md)

| 항목 | 내용 |
|---|---|
| Method | PUT |
| Path | /api/mobile/v1/my/orders/sheet/{orderSheetId}/discount |
| 인증 | Bearer {memberId} (필수) |
| 설명 | 주문서에서 선택한 쿠폰 1건(해제 포함)과 포인트 사용액을 임시주문에 **영속**하고 갱신된 주문서를 반환한다. 주문서 상태는 TEMP를 유지한다. 결제하기(§6)는 요청 바디의 쿠폰·포인트를 무시하고 여기서 저장한 값을 다시 검증해 확정한다. |
| 호출원 | SCR-M-002 주문서 — 쿠폰 선택·해제 즉시, 포인트 입력 400ms 후(저장 중에는 결제하기 차단) |

#### Request Body

```json
{ "couponId": "CPN-003", "pointUsed": 3000 }
```

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| couponId | string / null | 선택 | 적용할 쿠폰. `null`이면 쿠폰 해제(기존 할인 행 삭제) |
| pointUsed | int | 선택(기본 0) | 사용할 포인트. 0 이상, 사용 가능 잔액·할인 후 금액 이내 |

#### 처리

1. 임시주문 로드(본인·TEMP 확인) → 포인트 잔액 검증(`MemberApi`) → 쿠폰 검증(`PromotionApi.validateCoupon`) → 포인트 상한(할인 후 금액) 검증
2. `ord_platform_order_discount` 교체, 할인금액(`total_discount_amount`)·포인트(`point_used_amount`)·주문금액(`total_order_amount` = 상품금액 − 할인금액 + 배송비)·결제금액(`payment_amount` = 주문금액 − 포인트) 갱신
3. §5와 같은 구조의 주문서 응답 반환(`selected_coupon_id`, `point_used`, `price_summary` 갱신값)

#### 에러

| HTTP | code | message | 조건 |
|---|---|---|---|
| 400 | INVALID_ITEM_PRICE | 사용 포인트는 0 이상이어야 합니다 | `pointUsed` < 0 |
| 404 / 403 / 422 | ORDER_SHEET_NOT_FOUND / ORDER_SHEET_FORBIDDEN / ORDER_SHEET_ALREADY_PROCESSED | §5-1과 동일 | 임시주문 없음 / 타인 / TEMP 아님 |
| 422 | POINT_EXCEED | 사용 가능 포인트를 초과했습니다 | 포인트 잔액(Mock 15000) 초과 또는 할인 후 금액(상품금액 − 할인금액) 초과 |
| 422 | COUPON_NOT_APPLICABLE | 적용할 수 없는 쿠폰입니다 | 쿠폰 검증 실패(기간·상태·최소 상품금액·적용상품 불일치) 또는 할인액이 상품금액 초과 |

> 쿠폰 팝업·최적 조합 추천(API-008·009, §32-1·32-2)은 미구현이다. 포인트 최소 사용액(1,000P) 검증은 코드에 없다(Bolt4 SC16-1).

---

## 6. POST /api/mobile/v1/my/orders/{orderSheetId}/pay — 결제 요청

> **구현 현황 (2026-10-29)**: 구현(접수까지) — `OrderController.placeOrder`. 입금 통보·PG 승인 수신·실패/기한 만료 보상, `Idempotency-Key` 처리, `refundAccount`(`PayRequest`에 필드 없음)는 미구현.

> 최종 수정: 2026-10-20 (실제 구현 반영 — 요청/응답 필드, DEPOSIT_PENDING 상태, 에러코드 보강, PublicApi→Port 네이밍 갱신)

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/mobile/v1/my/orders/{orderSheetId}/pay |
| 인증 | Bearer {memberId} (필수) |
| Header | `Idempotency-Key: {ULID}` (필수 권장, 재고 이중 선점·이중 결제 방지) |
| 설명 | 주문서(임시주문, TEMP)에 저장된 상품·쿠폰·포인트를 다시 검증하고 배송지·필수 약관·결제수단을 확인해 주문을 **접수**(TEMP → STOCK_REQUESTED)하고, 재고차감 요청을 아웃박스에 같은 트랜잭션으로 적재한 뒤 즉시 응답한다(2026-10-29 비동기 접수 기준). 재고 차감(STOCK_DEDUCTED)과 PG 요청(가상계좌 발급, DEPOSIT_PENDING)은 이 응답에 포함되지 않고 컨슈머가 비동기로 처리한다(시퀀스 §4·§4-1). 입금 통보·PG 승인 수신(PAYMENT_COMPLETED)과 실패·입금기한 만료 보상은 미구현이다(REQ-ORD-013·014). |

> **(2026-10-26 변경 — 재고차감 비동기)** 결제하기는 이제 **동기 PG 호출을 하지 않는다.** 검증 후 주문 상태를 `STOCK_REQUESTED`로 전이하고 재고차감 요청(아웃박스 `ord_outbox_event` `STOCK_DEDUCT_REQUESTED`)을 같은 트랜잭션에 적재한 뒤 즉시 200을 반환한다(응답 `status=STOCK_REQUESTED`, `message="주문이 접수되었습니다. 재고 확인 후 결제가 진행됩니다"`). 이후 **별도 컨슈머 앱(`runNshop-consumer`)이 스케줄로 대기 이벤트를 조회해 내부 API `POST /api/internal/v1/order-events/process`(요청 `{eventType, platformOrderId, payload}`, 응답 `data.result`)를 호출**한다. 이벤트 조회·상태(DONE/재시도/FAILED)·후속 이벤트 적재는 컨슈머가, 업무 처리는 이 API가 맡는다. API가 ① 상품 API(`CatalogApi.deductStock`, `requestId`=platformOrderNo)로 재고를 **SKU 단위 독립 트랜잭션**으로 차감한다 — 전부 성공하면 주문 `STOCK_DEDUCTED`(`result=STOCK_DEDUCTED` → 컨슈머가 `PAYMENT_REQUESTED` 적재), 일부 SKU가 부족/미등록이면 성공한 SKU의 차감은 유지하고 주문 상태는 그대로 둔 채 `result=STOCK_PARTIAL`(실패 SKU 사유 포함)을 반환하며 컨슈머가 실패로 기록해 백오프 후 재시도하면 이미 차감한 SKU는 `cat_stock_deduction`(request_id+sku_id)으로 건너뛰고 **실패한 SKU만** 다시 차감한다(예: SKU 3개 중 2개 성공·1개 실패 → 재시도는 1개만) ② `PAYMENT_REQUESTED` 처리에서 PG 결제요청(`PaymentApi.requestPayment`) → 주문 `DEPOSIT_PENDING`. 이미 처리된 주문은 현재 상태를 `result`로 돌려주는 멱등 응답이다. 호출 실패·부분 실패 시 컨슈머가 재시도(최대 3회, 간격은 백오프)하고 소진하면 FAILED로 종결한 뒤 `POST /api/internal/v1/order-events/give-up`을 호출한다 — API는 부분 차감분을 되돌리고(`CatalogApi.restoreStock`) 재고차감 이벤트의 주문을 `STOCK_FAILED`로 전이한다. 컨슈머는 여러 인스턴스를 동시에 실행할 수 있다(이벤트 점유 `FOR UPDATE SKIP LOCKED`, 점유 후 임대 만료 시 재처리). 따라서 이 응답 시점에는 `pay_payment`가 아직 없고, 재고 부족은 응답이 아니라 이후 주문 상태(`STOCK_FAILED`, 변경이력 사유 "재고 차감 실패: ...")로 확인한다. 포인트·쿠폰은 주문서 단계 기록만 있어 실패 시 복원할 차감이 없다. 아래 2026-10-19 설명 중 "재고차감 호출 자체가 없고"/"그 자리에서 바로 200 확정"/`DEPOSIT_PENDING` 즉시 생성은 이 변경으로 대체됐다.

> **신규 (2026-10-19 프로토타입 구현 반영)**: 현재 구현은 위 설명(Catalog 동기 재고선점 → Payment 비동기 PG → PAYMENT_APPROVED 컨슈머)보다 훨씬 단순하다 — 배송지·약관·결제수단·가격 검증(아래 Error Responses 추가 행 참조) → 포인트 검증(`MemberApi.getPointBalance()`, Mock 고정 15000) → 쿠폰 검증(옵션, `PromotionApi.validateCoupon()`) → `PlatformOrder`/`Order`/`OrderItem`(쿠폰 시 `PlatformOrderDiscount`도) **신규 INSERT**(2단계 저장, `@Transactional`) → `PaymentApi.requestPayment()` 호출(Mock 항상 `accepted=true`) → **그 자리에서 바로 200 SUCCESS 확정**. 재고차감(Catalog) 호출 자체가 없고(TODO), PG 승인 비동기 컨슈머(§16)도 거치지 않는다 — "결제 진행중" 중간 상태 없이 결제요청=즉시 완료로 끝난다. `Idempotency-Key` 헤더는 현재 읽지도 검증하지도 않는다(중복 요청 방지 로직 미구현). 근거: `.agents/tasks/order-create-mobile-api/design.md` §4-2, `OrderService.kt.placeOrder()`.
>
> **(2026-10-19 구현 확인, 2026-10-20 네이밍 갱신)** 쿠폰 검증은 `PromotionApi.validateCoupon(memberId, couponId, items)`(완전 신규 메서드, `common.md`의 `getAvailableCoupons`와는 목적이 달라 재사용하지 않음), 포인트 조회는 `MemberApi.getPointBalance(memberId)`(`common.md` 원안 시그니처 그대로 재사용, Mock 고정 15000). `MemberApi.getAddresses()`는 호출하지 않는다 — 배송지는 §5 각주의 `OrderAddressMock`을 통해 별도로 해석한다. (패키지/이름 변경: `order.publicapi.XxxPublicApi` → `order.port.XxxApi`, SKILL.md 네이밍 간소화 결정)

#### Request Body

```json
{
  "addressId": 1,
  "couponId": "CPN-001",
  "pointUsed": 3000,
  "paymentMethodType": "VIRTUAL_ACCOUNT",
  "refundAccount": { "bankName": "국민은행", "accountNo": "123456-78-901234", "holderName": "홍길동" },
  "termsAgreed": ["T001", "T002", "T003"]
}
```

> **신규 (2026-10-29, 미구현) — `refundAccount`**: `paymentMethodType`=`VIRTUAL_ACCOUNT`이면 필수다(정책서 payment.md 8.7.1, REQ-PAY-031). 예금주는 주문자 본인이어야 하며 계좌번호는 암호화 저장한다. 카드·간편결제는 받지 않는다. 입금 후 취소·반품 환불과 입금 통보·취소 경합 환불(REQ-PAY-030)은 이 계좌로 지급한다.

> **신규 (2026-10-19 프로토타입 구현 반영) — 실제 요청 바디**: 실제 `PayRequest`가 받는 필드는 위 예시와 다르다. **(2026-10-26 변경) `items`는 더 이상 받지 않는다(무시) — 상품은 주문서 진입 시 저장된 임시주문(DB)에서 읽어 서버가 금액을 계산한다. `couponId`/`pointUsed`도 무시한다 — §5의 `PUT .../discount`로 임시주문에 저장된 쿠폰·포인트를 결제 시점에 재검증(`COUPON_NOT_APPLICABLE`/`POINT_EXCEED`)해 그대로 확정한다.** (이하 2026-10-19 당시 설명) `items`(필수, 결제 대상 상품 배열 — `vendorId`/`productId`/`skuId`/`productName`/`priceOriginal`/`priceSale`/`quantity`), `addressId`(Long?), `couponId`(String?, 옵션), `pointUsed`(Int?, 기본 0), `paymentMethodType`(필수, `CARD`/`EASY_PAY`/`POINT`/`VIRTUAL_ACCOUNT` — `VIRTUAL_ACCOUNT`는 2026-10-19 결제수단 노출 작업에서 허용값에 추가됨, mock `mobile__POST_my_orders_sheet.json`의 `payment_methods[]`도 가상계좌를 기본값으로 노출), `termsAgreed`(List<String>). 기존 DL §6 예시엔 `items`가 없고 §5의 `cartItemIds`도 받지 않는다 — "결제 대상 상품을 지정할 방법이 원안에 없었다"는 설계 간극(design.md §0 Finding 2)을 Cart 영속 계층 부재(§5 각주)와 같은 사유로 요청 바디에 `items`를 직접 받는 방식으로 메웠다. 실제 요청 예시:
> ```json
> {
>   "items": [
>     { "vendorId": 10, "productId": 101, "skuId": 1001, "productName": "나이키 페가수스 41", "priceOriginal": 179000, "priceSale": 152000, "quantity": 1 }
>   ],
>   "addressId": 1,
>   "couponId": "CPN-001",
>   "pointUsed": 3000,
>   "paymentMethodType": "CARD",
>   "termsAgreed": ["T001", "T002", "T003"]
> }
> ```

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "platformOrderId": "1",
    "platformOrderNo": "P261023-00001-00",
    "orderId": "1",
    "totalOrderAmount": 149000,
    "totalPayment": 149000,
    "status": "STOCK_REQUESTED",
    "message": "주문이 접수되었습니다. 재고 확인 후 결제가 진행됩니다"
  }
}
```

> 이 응답은 **접수 완료**(TEMP → STOCK_REQUESTED)일 뿐 재고 차감·PG 요청·입금을 의미하지 않는다(2026-10-29 비동기 접수 기준, `OrderService.placeOrder`). 이후 컨슈머가 `STOCK_DEDUCTED` → `DEPOSIT_PENDING`(가상계좌 발급)으로 전이하며 재고 부족은 `STOCK_FAILED`로 끝난다. 클라이언트는 주문 상세(§30 `GET /api/mobile/v1/my/orders/{orderId}`)의 `status`로 진행을 확인한다(접수 완료 화면의 상태 폴링은 미구현).

응답 필드(`PayResponse`):

- `platformOrderId`(Long→String): `PlatformOrder.id`. 이후 주문 상세 조회·"주문 상세 보기" 이동 등 후속 동작의 1차 식별자 — 조회(GET) 경로가 `PlatformOrder.id` 기준이라 결제하기 응답도 같은 식별자를 1차로 쓴다(`order-placeorder-design-gaps/design.md` §2).
- `platformOrderNo`(String, `"P"+yyMMdd+"-"+5자리+"-00"`): 화면의 "주문번호" 표시용. 목록·상세 API가 같은 포맷을 쓰므로 접수 완료 화면의 주문번호 표기가 일치한다.
- `orderId`(Long→String): 생성된 `Order`(판매자별 분할 주문) 중 대표 1건(최솟값 id)의 참고값 — "주문번호" 표시에는 쓰지 않는다. 판매자가 2곳 이상이면 나머지 id는 포함되지 않으며 전체는 `platformOrderId` 상세 조회로 확인한다.
- `totalOrderAmount`(BigDecimal, 2026-10-29 신설): **주문금액**(상품금액 − 할인금액 + 배송비 − 배송비 할인금액, 포인트 사용 전). 접수 완료 화면의 "주문금액".
- `totalPayment`(BigDecimal): **결제금액**(주문금액 − 포인트, PG 결제수단으로 지불하는 금액). 필드명은 하위호환으로 유지.
- `status`·`message`: 접수 시점 상태와 안내 문구. 위 예시가 현재 코드의 실제 값이다.

#### Error Responses

| HTTP | code | message | 조건 | 대응 GWT |
|---|---|---|---|---|
| 400 | ADDRESS_REQUIRED | 배송지를 선택해주세요 | 배송지 미선택 | AC-ORD-012 |
| 400 | TERMS_NOT_AGREED | 필수 약관에 동의해주세요 | 필수 약관 미동의 | — |
| 409 | STOCK_NOT_AVAILABLE | 재고가 부족합니다 | 재고 선점 실패. **구설계: 비동기 접수 응답으로는 발생하지 않음** — 접수는 항상 `STOCK_REQUESTED`이고 재고 부족은 컨슈머 처리 후 `STOCK_FAILED`로 반영된다(REQ-ORD-077~079) | — |
| 409 | CARD_RESTRICTED | 카드가 당일 결제 제한 상태입니다 | 동일 카드 3회 연속 결제 실패로 당일 차단됨 (Payment가 접수 단계에서 동기 반환). **구설계: 비동기 접수 응답으로는 발생하지 않음** | REQ-PAY-018(제한 규칙), REQ-PAY-023(카운터 저장·리셋 메커니즘) |
| 404 | ORDER_SHEET_NOT_FOUND | 주문서를 찾을 수 없습니다 | `{orderSheetId}`에 해당하는 임시주문 없음 (2026-10-26 신설) | — |
| 403 | ORDER_SHEET_FORBIDDEN | 본인의 주문서가 아닙니다 | 임시주문의 회원 ≠ 요청 회원 (2026-10-26 신설) | — |
| 422 | ORDER_SHEET_ALREADY_PROCESSED | 이미 결제가 진행된 주문서입니다 | 임시주문 상태가 `TEMP`가 아님(중복 결제 요청 방지, 2026-10-26 신설) | — |
| 400 | CART_ITEMS_REQUIRED | 주문할 상품이 없습니다 | `items`가 없음/빈 배열 | — |
| 400 | REFUND_ACCOUNT_REQUIRED | 가상계좌 결제는 환불계좌를 입력해주세요 | `paymentMethodType`=`VIRTUAL_ACCOUNT`인데 `refundAccount`가 없음 (2026-10-29 신설, 미구현) | AC-PAY-037 |
| 400 | REFUND_ACCOUNT_INVALID | 환불계좌를 확인해주세요 | 예금주가 주문자 본인과 다르거나 계좌 실명 확인 실패 — 실명 확인은 **결제 요청 시점**에 수행한다 (2026-10-29 신설·확정, 미구현) | AC-PAY-037 |
| 400 | PAYMENT_METHOD_NOT_READY | 카드 결제는 작업중입니다. 가상계좌로 결제해주세요 | `paymentMethodType`=`CARD` (2026-10-26 신설 — 현재 가상계좌만 진행) | — |
| 400 | INVALID_PAYMENT_METHOD | 지원하지 않는 결제수단입니다 | `paymentMethodType`이 `CARD`/`EASY_PAY`/`POINT`/`VIRTUAL_ACCOUNT` 외의 값 | — |
| 400 | INVALID_ITEM_PRICE | 상품 수량/가격이 올바르지 않습니다 | 저장된 임시주문 상품 중 `quantity<1` 또는 `priceOriginal<0`/`priceSale<0` | — |
| 400 | INVALID_ITEM_PRICE | 사용 포인트는 0 이상이어야 합니다 | 요청의 `pointUsed<0` (같은 코드, 메시지가 다름 — `validatePayRequest`) | — |
| 422 | POINT_EXCEED | 사용 가능 포인트를 초과했습니다 | `pointUsed`가 포인트 잔액(Mock 15000) 또는 할인 후 금액(상품금액 − 할인금액)을 초과 | — |
| 422 | COUPON_NOT_APPLICABLE | 적용할 수 없는 쿠폰입니다 | `couponId`가 있을 때 `PromotionApi.validateCoupon()` 검증 실패(DL §32-2 기존 식별자 재사용), 또는 `discountAmount`가 `totalItemAmount`를 초과 | — |

> **(2026-10-19 구현 확인)** 위 두 행(`STOCK_NOT_AVAILABLE`/`CARD_RESTRICTED`)은 현재 발생하지 않는다 — 재고선점/카드제한 로직 자체가 미구현(Mock은 항상 성공). 아래 추가된 4행(`CART_ITEMS_REQUIRED`/`INVALID_PAYMENT_METHOD`/`INVALID_ITEM_PRICE`/`POINT_EXCEED`)과 `COUPON_NOT_APPLICABLE`은 실제 `OrderService.kt.validatePayRequest()`/`validatePointUsage()`/`validatePointNotExceedingPayableAmount()`/`validateCouponIfPresent()`가 반환하는 에러다. `COUPON_NOT_APPLICABLE`은 `PromotionApi.validateCoupon()`의 `applicable=false` 판정과, `discountAmount`가 상품금액(`totalItemAmount`)을 초과하는 경우(order-placeorder-design-gaps/design.md §1) 두 조건 모두에서 발생한다.
>
> **(2026-10-19 결제수단 노출 작업 반영)** `paymentMethodType` 허용값은 최초 구현 시 `CARD`/`EASY_PAY`/`POINT` 3종이었으나, 이후 "가상계좌/신용카드 노출 + 가상계좌 기본값" 작업에서 `VIRTUAL_ACCOUNT`가 추가됐다(`OrderService.kt.validatePayRequest()`의 허용 Set, mock `mobile__POST_my_orders_sheet.json`의 `payment_methods[]`). 결제수단과 무관하게 접수 결과는 항상 `STOCK_REQUESTED`이고, 이후 컨슈머 처리가 끝나면 `DEPOSIT_PENDING`(입금대기)이 된다 — 가상계좌만 진행하며 `CARD` 요청은 `PAYMENT_METHOD_NOT_READY`로 거부되고, 결제수단별 상태 분기 로직은 미구현.

> PG 승인 실패(`PAYMENT_FAILED`)·타임아웃은 이 API의 동기 에러가 아니다. 재고 선점 성공 후에는 Payment 결제 요청 접수(큐 등록)까지만 동기로 확인하며, PG 승인 결과는 §16(컨슈머)에서 비동기로 반영된다. (**(2026-10-19 구현 확인)** 이 문단이 설명하는 비동기 PG 승인 흐름 자체가 현재는 호출되지 않는다 — 결제확정은 §4 보완 블록 참조.)

---

## 7. POST /api/mobile/v1/my/orders/{orderId}/cancel — 고객 주문 취소

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음.

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/mobile/v1/my/orders/{orderId}/cancel |
| 인증 | Bearer {memberId} (필수) |

#### Request Body

```json
{ "cancelReason": "CUSTOMER_REQUEST" }
```

> 취소 가능 상태는 `DEPOSIT_PENDING`(입금대기, 2026-10-29 허용 확정)과 `PAYMENT_COMPLETED`다. 입금대기 취소는 가상계좌 폐기·재고 복원만 하고 환불이 없어 `refundAmount`는 0이다(REQ-ORD-080, AC-ORD-091). 입금 통보와 경합하면 취소가 우선하며 이미 반영된 입금액은 별도로 환불한다(REQ-PAY-030, AC-ORD-092). 취소 시 같은 트랜잭션에서 `claim_type=CANCEL` 클레임이 생성되며 응답에 `claimNo`를 포함한다(REQ-ORD-082 확정, AC-ORD-098·099). 미구현.

#### Response 200

입금대기(`DEPOSIT_PENDING`) 취소 — 가상계좌 폐기·재고 복원만 하므로 환불이 없다(`refundAmount` 0). 취소 클레임은 `RECEIVED → COMPLETED`로 종결된다(REQ-ORD-082 확정, AC-ORD-098·100):

```json
{
  "code": "SUCCESS",
  "data": { "orderId": "1", "status": "CANCELLED", "refundAmount": 0, "claimNo": "CLM-20261029-001" }
}
```

결제완료(`PAYMENT_COMPLETED`) 취소 — 환불이 필요하며 취소 클레임은 `RECEIVED → REFUNDED → COMPLETED`로 진행된다(AC-ORD-099):

```json
{
  "code": "SUCCESS",
  "data": { "orderId": "1", "status": "CANCELLED", "refundAmount": 152000, "claimNo": "CLM-20261029-002" }
}
```

> `claimNo`(취소 클레임 번호)는 응답 필드로 확정이다(REQ-ORD-082). `cancel_type`은 취소 사유 구분용 컬럼이며 의미는 DF 기준(미정). 환불액은 상품주문금액 + 환불 대상 배송비(고객이 낸 초도 배송비)다.

#### Error Responses

| HTTP | code | message | 조건 | 대응 GWT |
|---|---|---|---|---|
| 409 | CANCEL_NOT_ALLOWED | 출고 준비 중에는 직접 취소할 수 없습니다. 고객센터로 문의해주세요 (배송 중이면: 배송 중에는 취소할 수 없습니다. 배송완료 후 반품을 이용해주세요) | `DEPOSIT_PENDING`·`PAYMENT_COMPLETED` 이외 상태 | AC-ORD-018·019 |
| 403 | FORBIDDEN | 본인 주문만 취소할 수 있습니다 | 타인 주문 | — |

---

## 8. POST /api/mobile/v1/my/orders/{orderId}/confirm — 구매확정

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음.

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/mobile/v1/my/orders/{orderId}/confirm |
| 인증 | Bearer {memberId} (필수) |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": { "orderId": "ord-001", "status": "CONFIRMED", "pointEarned": 1520 }
}
```

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 409 | CONFIRM_NOT_ALLOWED | 배송완료 상태에서만 구매확정이 가능합니다 | DELIVERED 아닌 상태 |

---

## 9. PUT /api/mobile/v1/my/orders/{orderId}/shipping-address — 배송지 변경

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음.

| 항목 | 내용 |
|---|---|
| Method | PUT |
| Path | /api/mobile/v1/my/orders/{orderId}/shipping-address |
| 인증 | Bearer {memberId} (필수) |

#### Request Body

```json
{
  "recipientName": "홍길동",
  "phone": "010-1234-5678",
  "zipCode": "06234",
  "address": "서울특별시 강남구 테헤란로 123",
  "addressDetail": "런앤샵타워 5층"
}
```

#### Response 200

```json
{ "code": "SUCCESS", "data": null }
```

#### Error Responses

| HTTP | code | message | 조건 | 대응 GWT |
|---|---|---|---|---|
| 409 | ADDRESS_CHANGE_NOT_ALLOWED | 출고 후에는 변경할 수 없습니다 | 출고 지시 후(PREPARING 이후). `DEPOSIT_PENDING`·`PAYMENT_COMPLETED`(출고 지시 전)는 고객 직접 변경 가능, 준비중은 고객센터(정책 6.12.2), 송장 후는 범위 제외(반품 후 재주문) | AC-ORD-025 |

---

## 10. POST /api/mobile/v1/my/orders/{orderId}/claims — 반품/교환 신청

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음.

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/mobile/v1/my/orders/{orderId}/claims |
| 인증 | Bearer {memberId} (필수) |
| 헤더 | `Idempotency-Key: {ULID}` (2026-11-03 추가 — 클레임 중복 접수 방지, readme §4) |

#### Request Body

```json
{
  "claimType": "RETURN",
  "items": [ { "orderItemId": "oi-001", "quantity": 1 } ],
  "reason": "단순 변심",
  "detailReason": "사이즈가 맞지 않습니다",
  "responsibility": "CUSTOMER",
  "images": []
}
```

> `items[]`(2026-11-03 추가·설계안): 접수 대상 주문상품과 수량. `orderItemId`는 대상 주문상품, `quantity`는 반품·교환할 수량(부분 반품 가능, REQ-ORD-074). 한 주문상품의 진행 중 클레임 수량을 뺀 재신청 가능 수량(AC-ORD-109)을 넘기면 `CLAIM_ALREADY_IN_PROGRESS`(409)로 거부한다. 아래 예시의 다른 요청 본문에도 같은 `items[]`를 함께 보낸다(생략 표기).

> `claimType=EXCHANGE` 예시 — 교환 대상 SKU(`exchangeSkuId`)를 함께 전달한다.

```json
{
  "claimType": "EXCHANGE",
  "reason": "사이즈 교환",
  "detailReason": "270 사이즈로 교환 원합니다",
  "exchangeSkuId": "sku-002",
  "responsibility": "CUSTOMER",
  "images": []
}
```

> `exchangeSkuId`: 교환 대상 SKU ID. `claimType=EXCHANGE`일 때 **필수** (Catalog 도메인 SKU 참조, 선출고 시 사용)

> `responsibility`: **고객 자진신고** 값이다 — `CUSTOMER`(단순변심 등) / `VENDOR`(상품불량 등). 서버는 이 값을 `ord_claim.submitted_responsibility`에 저장하고 최종 귀책 `ord_claim.responsibility`는 **비워 둔다**(판정 전, REQ-ORD-066). 최종 귀책은 어드민 귀책 판정(§19-1)이 확정한다. `images`: 첨부 이미지 URL 배열, 최대 3장. **`responsibility=VENDOR`일 때 최소 1장 필수**(REQ-ORD-058), CUSTOMER는 선택. 서버는 이 이미지를 `uploaded_by=CUSTOMER`로 저장하며, "최대 3장" 제한은 이후 품질점검 거부(#38)에서 판매자가 첨부하는 사진(`uploaded_by=VENDOR`)과 완전히 독립적으로 적용된다(REQ-ORD-075).

```json
{
  "claimType": "RETURN",
  "reason": "상품불량",
  "detailReason": "박음질이 뜯어져 있습니다",
  "responsibility": "VENDOR",
  "images": ["https://cdn.runnshop.com/claims/img-001.jpg"]
}
```

#### Response 201

```json
{
  "code": "SUCCESS",
  "data": { "claimId": "clm-001", "claimType": "RETURN", "status": "RECEIVED" }
}
```

> `claimType=EXCHANGE`인 경우 `data`에 `exchangeSkuId`가 함께 반환된다: `{ "claimId": "clm-002", "claimType": "EXCHANGE", "status": "RECEIVED", "exchangeSkuId": "sku-002" }`

#### Error Responses

| HTTP | code | message | 조건 | 대응 GWT |
|---|---|---|---|---|
| 422 | CLAIM_PERIOD_EXPIRED | 기한이 초과되었습니다 | 구매확정 전 접수: 단순변심은 배송완료 후 10일 초과, 하자·오배송(VENDOR)은 배송완료 후 3개월과 안 날부터 30일 모두 초과(운영자 승인 경로 안내, 7.2.3) | 단순변심 AC-ORD-032, 하자·오배송 AC-ORD-112·118 |
| 409 | CLAIM_NOT_ALLOWED | 배송완료 후에만 신청할 수 있습니다 (구매확정 후: 구매확정 후에는 고객센터로 문의해주세요) | 배송완료 전 상태(배송중 포함) 또는 구매확정 후(고객 모바일 접수 불가, 어드민에서만 접수 — REQ-ORD-081, AC-ORD-096) | AC-ORD-096 |
| 409 | CLAIM_ALREADY_IN_PROGRESS | 이미 진행 중인 클레임이 있습니다 | 대상 주문상품에 진행 중(RECEIVED~COMPLETED 전) 클레임이 있어 요청 수량이 재신청 가능 수량(구매수량 − 진행 중 클레임 수량)을 초과 (2026-11-03 신설·설계안). 같은 Idempotency-Key 재요청은 이 에러가 아니라 최초 응답을 그대로 반환 | AC-ORD-109 |
| 400 | INVALID_QUANTITY | 수량이 올바르지 않습니다 | `items`가 비어 있거나 `quantity<1` (2026-11-03 신설·설계안) | — |
| 404 | ORDER_NOT_FOUND | 주문을 찾을 수 없습니다 | 존재하지 않는 orderId 또는 타인 주문(타인 리소스는 존재 여부를 숨기기 위해 404, readme §2) | — |
| 400 | EXCHANGE_SKU_REQUIRED | 교환할 옵션(SKU)을 선택해주세요 | claimType=EXCHANGE인데 exchangeSkuId 누락 | REQ-ORD-056 |
| 422 | EXCHANGE_SKU_MISMATCH | 교환은 동일 상품 내 옵션 변경만 가능합니다 | claimType=EXCHANGE인데 exchangeSkuId의 productId가 원 주문 상품(productId)과 다름 | REQ-ORD-070 |
| 400 | CLAIM_PHOTO_REQUIRED | 상품 상태를 확인할 수 있는 사진을 1장 이상 첨부해주세요 | responsibility=VENDOR인데 images가 빈 배열 | REQ-ORD-058 |

---

## 10-1. POST /api/mobile/v1/my/claims/{claimId}/cancel — 클레임 자진 취소

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음.

> 신규 (시퀀스 §7-2 대응). 고객이 마이페이지 클레임상세에서 접수한 클레임을 스스로 취소한다. CS 귀책판정(#19-1) 또는 수거(PICKUP) 프로세스가 시작되기 전, 즉 `RECEIVED`/`PAYMENT_PENDING` 상태에서만 허용한다.

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/mobile/v1/my/claims/{claimId}/cancel |
| 인증 | Bearer {memberId} (필수) |
| 설명 | 클레임 상태가 `RECEIVED` 또는 `PAYMENT_PENDING`일 때만 자진 취소를 허용한다. 취소 시 상태 → `REJECTED`(사유="고객 자진 철회"), 고객에게 알림톡 발송. `INSPECTING` 등 CS 귀책판정 이후 상태에서는 거부한다(REQ-ORD-073, REQ-ORD-071). |

#### Request Body

없음 (Body 없이 호출)

#### Response 200

```json
{ "code": "SUCCESS", "data": { "claimId": "clm-001", "status": "REJECTED" } }
```

#### Error Responses

| HTTP | code | message | 조건 | 대응 GWT |
|---|---|---|---|---|
| 409 | CLAIM_CANCEL_NOT_ALLOWED | 귀책 판정/수거 시작 이후에는 취소할 수 없습니다 | claim.status가 `RECEIVED`/`PAYMENT_PENDING`이 아님 (예: `INSPECTING` 이후) | REQ-ORD-071 |
| 403 | FORBIDDEN | 본인 클레임만 취소할 수 있습니다 | 타인 클레임 | — |

---

## 11. GET /api/mobile/v1/my/orders — 내 주문 목록

> **구현 현황 (2026-10-29)**: 구현(제한) — DB. `OrderController.getMyOrders` → `OrderService.getMyOrders`. 쿼리 파라미터·`pagination`은 미적용.

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/mobile/v1/my/orders |
| 인증 | Bearer {memberId} (필수) |
| Query | (설계안) `?page=1&size=10&status=ALL&sort=orderDate&direction=desc` — **구현은 쿼리 파라미터를 받지 않는다**(`getMyOrders()`가 본인 주문 전체를 최신순으로 반환, 미적용) |

> 어드민 주문 목록(API-022)의 조회 규칙·검증 오류는 [§15](#api-022)로 옮겼다(2026-10-29 — 이전에는 이 절에 섞여 있었다). 내 주문 목록은 `ord_platform_order`에서 본인(`memberId`) 주문을 `ordered_at` 내림차순으로 가져와 `TEMP`(주문서 진입 임시주문)를 제외한다.

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "totalCount": 1,
    "orders": [
      { "orderId": "1", "platformOrderNo": "P261023-00001-00", "productName": "나이키 페가수스 41 외 1건", "imageUrl": "https://placehold.co/80x80/f5f5f5/333?text=...", "optionName": "블랙 / 265", "quantity": 1, "amount": 149000, "status": "DEPOSIT_PENDING", "statusLabel": "입금대기", "orderDate": "2026-10-23" }
    ]
  }
}
```

> 현재 구현 응답이다. `amount`는 **주문금액**(`total_order_amount`)이고 `statusLabel`은 서버가 내려주는 한글 라벨이다(재고확인중·재고차감완료·재고부족·입금대기·결제완료·상품준비중·배송중·배송완료·구매확정·취소). 설계안의 `pagination`(`page`/`size`/`totalCount`/`totalPages`)과 `status` 필터·`sort`·`direction`은 **미적용**이며 `data.totalCount`(전체 건수)만 있다.

---

<a id="api-022"></a>
## 15. GET /api/admin/v1/orders — 주문 검색 (어드민) (API-022)

> **구현 현황 (2026-10-29)**: 구현 — DB(MyBatis). `OrderController.getAdminOrders`. `sort`·`direction` 미적용, 표시 상태 파생 미적용.

> 최종 수정: 2026-10-27 (정책 확인 회신 반영 — 키워드·기간·summary·오류코드 확정) / 2026-10-20 (실제 구현 반영 — Mock→PostgreSQL 전환, customer/vendorName을 Member/Vendor Port 배치조회로 전환)

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/admin/v1/orders |
| 인증 | Admin Bearer (필수) |
| Query | `?keyword=&status=ALL&from=2026-06-01&to=2026-06-30&page=1&size=10&sort=orderDate&direction=desc` — `sort`·`direction`은 **미적용**(컨트롤러가 받지 않으며 `ordered_at` 내림차순·`id` 내림차순 고정) |

> **(2026-10-27 정책 확인 회신 반영 — 개발자 문의 8건)** 어드민 주문 목록의 조회 규칙을 다음과 같이 확정한다.
>
> | 항목 | 확정 규칙 |
> |---|---|
> | 조회 테이블 | 어드민은 `ord_platform_order`(플랫폼 오더) 기준. 판매자(partner)만 `ord_order` 사용 (확정) |
> | `platformOrderNo` | `PyyMMdd-NNNNN-00` (예: `P261026-00001-00`). 판매자 주문번호 `VyyMMdd-NNNNN-NN`(예: `V261026-00001-01`, 끝 2자리 = 해당 주문 내 판매자 순번)과 구분 — 구형 Mock의 `ORD-…` 표기는 폐기 대상 |
> | `keyword` | 주문번호(`platform_order_no`)·상품명·주문자명(고객명) 모두 **부분 일치**(ILIKE, 대소문자 무시). 판매자명 검색은 제외. 고객명 검색 소스는 주문 시점 `orderer_name` 스냅샷 컬럼(확정, 컬럼 추가 필요 — [[DF-도메인모델ERD/order]]) |
> | `from`/`to` | `ord_platform_order.ordered_at` 기준 날짜 범위(양끝 포함, `ordered_at::date`). `created_at` 미사용 (확정) |
> | `orderDate` 표시 | `ordered_at`을 `yyyy-MM-dd HH:mm` 형식으로 반환 |
> | `amount` | **주문금액** `total_order_amount` = 상품금액 − 할인금액 + 배송비 − 배송비 할인금액 (= 포인트 + 결제금액). 어드민 목록의 금액은 주문금액이다(DBA 3.7.4) |
> | `status` | 플랫폼 오더 상태(`ord_platform_order.status`)를 그대로 필터. 기본 `ALL`. `TEMP`(주문서 진입 임시주문)는 목록·집계에서 항상 제외 |
> | `page` / `size` | `page` ≥ 1, `size` 1~100 (기본 10). 화면 선택지는 10/20/50 |
> | `sort` / `direction` | 설계안: `sort=orderDate`(기본), `direction=desc`(기본). **구현은 받지 않고 고정 정렬**(미적용) |
> | `customer` | `orderer_name` 스냅샷을 마스킹해 반환 (Port 배치조회 폴백: 스냅샷 없으면 `MemberApi.getMemberNames()` → 그래도 없으면 `"비회원{memberId}"`) |
>
> **summary 규격**: 응답 `data.summary`는 `{ "all", "depositPending", "paymentCompleted", "cancelled" }` 4개 키. ① `status` 필터는 적용하지 않고 `keyword`+기간만 적용한 분포이며 ② 건수가 0인 상태도 키를 유지(0)하고 ③ `all`은 `TEMP`를 제외한 전체 합계다. 위 4개 키 밖의 상태(`STOCK_REQUESTED` 등)는 `all`에만 포함된다.

#### Error Responses (API-022 입력 검증)

| HTTP | code | message | 조건 |
|---|---|---|---|
| 400 | `INVALID_PAGE` | page는 1 이상이어야 합니다 | `page` < 1 |
| 400 | `INVALID_SIZE` | size는 1~100 사이여야 합니다 | `size` < 1 또는 > 100 |
| 400 | `INVALID_DATE_RANGE` | from은 to보다 늦을 수 없습니다 | `from` > `to` |

> **`status` 값 (2026-10-29 현행화)**: 목록·필터·배지의 `status`는 **플랫폼주문(`ord_platform_order.status`) 원시값을 그대로** 쓴다(`OrderMapper.xml` — `po.status = #{status}`). 값은 [DH-상태머신/order](../../S2-구조설계/DH-상태머신/order.md) 11상태 중 `TEMP`를 제외한 값이며, `TEMP`는 목록·집계에서 항상 제외한다. 화면 필터는 전체/재고확인중/재고차감완료/재고부족/입금대기/결제완료/취소를 쓴다.
>
> | status (API) | 한글 라벨 | 비고 |
> |---|---|---|
> | `STOCK_REQUESTED` | 재고확인중 | 접수 완료, 재고차감 대기 |
> | `STOCK_DEDUCTED` | 재고차감완료 | 결제 요청 대기 |
> | `STOCK_FAILED` | 재고부족 | 재고차감 3회 소진 |
> | `DEPOSIT_PENDING` | 입금대기 | 가상계좌 발급 완료 |
> | `PAYMENT_COMPLETED` | 결제완료 | |
> | `PREPARING` / `DELIVERED` / `CONFIRMED` | 상품준비중 / 배송완료 / 구매확정 | 전이 로직 미구현 — 필터 시 빈 결과 |
> | `CANCELLED` | 취소 | |
> | `PAYMENT_FAILED` | 결제 실패 | DH 상태. 전이 미구현 |
>
> **`IN_DELIVERY` 표시 상태 파생은 적용하지 않는다(미적용, 설계안).** 이전 설계는 `PREPARING` 구간을 운송장 등록 여부(`ord_shipment(OUTBOUND).status=IN_TRANSIT`)로 다시 나눠 `IN_DELIVERY`로 표시하는 것이었다. 구현은 `ord_shipment` 조인 없이 원시 상태를 그대로 반환하고, 배송 데이터 연동은 배송 Bolt 이후다. `ord_order.status`·`ord_shipment` 규칙 자체는 [DH-상태머신/order](../../S2-구조설계/DH-상태머신/order.md) §1·§3을 따른다. `ORDER_RECEIVED`·`PAYMENT_PENDING`은 폐기된 구 상태다.

> **(2026-10-15 구현 확인)** 이 API는 Mock JSON이 아니라 PostgreSQL `ord_order` 테이블을 MyBatis(slave 읽기전용 계정)로 실제 조회한다. `keyword`(주문번호/상품명 ILIKE)·`status`·`from/to`(날짜 범위) 필터와 `page/size` 페이징이 실제로 동작한다. `summary`는 `status`를 제외한 조건(keyword+dateRange)만으로 GROUP BY 집계한다 — "상태별 요약 카드는 검색조건과 무관하게 전체 상태 분포를 보여주고, 목록만 선택한 상태로 좁힌다"는 설계 의도가 실제로 구현됐다. 단, "표시 상태"(`ord_shipment` 조인으로 `IN_DELIVERY` 파생)는 **적용되지 않는다** — `ord_shipment` 테이블 자체가 이번 범위 밖(order-admin-erd-redesign.sql §8)이라 저장된 상태값을 그대로 반환한다(2026-10-26 이후 조회 기준은 플랫폼주문 `ord_platform_order`, 위 현행화 표 참조). 근거: `.agents/tasks/order-admin-erd-redesign/plan.md` §1.8, `OrderMapper.xml`.

> **(2026-10-20 구현 확인)** `customer`/`vendorName`은 `OrderMapper.xml`의 SQL CASE(1~8 고정 매핑)가 더 이상 채우지 않는다 — 고객명/판매자명은 Member/Vendor 도메인 소유 데이터라는 코딩표준에 따라, Mapper가 `memberId`/`vendorId` 원시값만 반환하고 `OrderService.getAdminOrders()`가 `MemberApi.getMemberNames()`/`VendorApi.getVendorNames()`(각각 Order가 소유한 Port 인터페이스, 배치 조회로 N+1 방지)를 호출해 채운다. 매핑표 밖의 ID는 `"비회원{memberId}"`/`"미등록{vendorId}"`처럼 원시 ID를 이어붙인 폴백 문자열을 반환한다(운영자가 매핑 공백을 추적할 수 있도록 함). Port 호출이 실패해도 목록 조회 전체를 막지 않고 같은 폴백으로 계속 진행한다(SKILL.md "제한적 서비스 가능(단순조회)" 유형).

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "orders": [
      { "orderId": "ord-001", "platformOrderNo": "P260626-00001-00", "productName": "나이키 페가수스 41", "customer": "홍*동", "vendorName": "나이키코리아", "status": "PAYMENT_COMPLETED", "amount": 152000, "orderDate": "2026-06-26 09:15" },
      { "orderId": "ord-003", "platformOrderNo": "P260625-00015-00", "productName": "호카 클리프턴 9", "customer": "이*미", "vendorName": "호카코리아", "status": "IN_DELIVERY", "amount": 169000, "orderDate": "2026-06-25 14:22" }
    ],
    "summary": { "all": 12, "depositPending": 3, "paymentCompleted": 5, "cancelled": 0 },
    "pagination": { "page": 1, "size": 10, "totalCount": 12, "totalPages": 2 }
  }
}
```

> `status: "IN_DELIVERY"`(ord-003) 예시는 설계안의 표시 상태 파생(`PREPARING` + 출고 shipment `IN_TRANSIT`)을 보인 것이며 **현재 구현은 이 값을 만들지 않는다**(미적용). 실제 응답의 `orderId`는 플랫폼주문 id 숫자 문자열(예: `"1"`)이다.

---

<a id="api-023"></a>
## 16. GET /api/admin/v1/orders/{orderId} — 주문 상세 (API-023)

> **구현 현황 (2026-10-29)**: 구현 — DB(JPA). `OrderController.getAdminOrderDetail`. `history`는 `ord_status_history`, `inquiries`·`logs`는 Mock.

> 최종 수정: 2026-10-20 (실제 구현 반영 — Mock→PostgreSQL 전환, Payment/Member/Vendor Port 연동, Error Responses 신설, PublicApi→Port 네이밍 갱신)

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/admin/v1/orders/{orderId} |
| 인증 | Admin Bearer (필수) |

> `status`는 플랫폼주문 상태 원시값이다(§15 현행화 표). 표시 상태 파생(`trackingNumber` 등록 시 `IN_DELIVERY`)은 **미적용**(설계안).

> **(2026-10-15/10-19 구현 확인, 2026-10-20 네이밍 갱신)** PostgreSQL `ord_order`(+연관 `ord_order_item`/`ord_delivery`/`ord_claim`)을 JPA(master 계정, `@EntityGraph`)로 실제 조회한다. `status`는 §15의 "표시 상태" 매핑이 적용되지 않고 `ord_order.status` 원시값을 그대로 반환한다(§15 보완 노트와 동일 사유 — `ord_shipment` 범위 밖). `payment` 블록은 `PaymentApi.getPaymentInfo()`(Payment 도메인 Port, 인터페이스 호출 — 이 코드는 Payment의 Mock 파일 경로를 모른다)로, `customer`/`vendorName`은 `MemberApi.getMemberName()`/`VendorApi.getVendorName()`으로 각 도메인에 조회한다(패키지/이름 변경: `order.publicapi.XxxPublicApi` → `order.port.XxxApi`). **(2026-10-26 변경)** `history`는 `ord_status_history`(주문/결제/배송/클레임 상태전이 이력, `OrderStatusHistoryService`)에서 최신순으로 조회한다 — 결제상태는 PG 요청(REQUESTED)·PG 수신(COMPLETED/FAILED)을 시각과 작업 내용(`reason`)만으로 기록한다(payload 미저장). 기록 단위는 결제완료까지 플랫폼주문, 이후 배송·클레임은 vendor 주문이다. 항목: `targetType`(ORDER/PAYMENT/DELIVERY/CLAIM)/`fromStatus`(최초 생성이면 null)/`toStatus`/`changedBy`/`reason`/`createdAt`. 변경이력 탭은 `logs`가 아니라 `history`를 사용한다. `inquiries`/`logs`는 여전히 Mock 파일(`mock/order/admin__GET_orders_{order_id}.json`)에서 가져온다 — ERD 범위 밖(`ord_platform_order` 등) 테이블 소관이기 때문(order-admin-erd-redesign plan.md §1.7). **(2026-10-29 정정)** `shipping.recipientName/phone/address`는 Mock이 아니라 `ord_platform_order`의 `receiver_*` 컬럼에서 읽는다(`OrderService.kt`의 배송 정보 구성부). 단 마스킹은 적용되지 않고 저장값이 그대로 반환된다 — 문서 기준은 마스킹이며 구현 갭이다(DN admin/order-history/tabs/shipping 구현 현황 참조).

> **(2026-10-27 복합결제)** `payment` 블록은 가장 최근 결제 시도(`pay_group_no`)의 `pay_payment` 행들을 합쳐 반환한다. 복합결제면 `method`는 `"복합결제 (가상계좌 + 포인트)"`처럼 수단을 `+`로 연결하고, `pgProvider`/`transactionId`/`paidAt`은 PG를 거치는 행(없으면 첫 행)의 값이다. 결제 행은 수단별 1행이며 결제번호는 `YyMMdd-NNNNN-NN`(DBA 결제 §4). 수단별 금액 내역 노출은 후속(현재 블록 필드 불변).

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "orderId": "1",
    "platformOrderNo": "P261023-00001-00",
    "status": "DEPOSIT_PENDING",
    "customer": "홍*동",
    "vendorName": "나이키코리아 외 1곳",
    "amount": 149000,
    "orderAmount": 149000,
    "paymentAmount": 146000,
    "productAmount": 152000,
    "shippingFee": 0,
    "productDiscount": 0,
    "cartDiscount": 3000,
    "pointUsedAmount": 3000,
    "orderDate": "2026-10-23 09:15",
    "items": [
      {
        "vendorName": "나이키코리아",
        "vendorStatus": "DEPOSIT_PENDING",
        "products": [ { "productName": "나이키 페가수스 41", "optionName": "블랙/265", "quantity": 1, "unitPrice": 152000, "subtotal": 152000 } ]
      }
    ],
    "payment": { "method": "복합결제 (가상계좌 + 포인트)", "pgProvider": "토스페이먼츠", "transactionId": "TXN-001", "paidAt": null },
    "shipping": {
      "recipientName": "홍*동", "phone": "010-****-5678", "address": "[06234] 서울 강남구 테헤란로 123 런앤샵타워 5층", "memo": "부재 시 문 앞에",
      "deliveries": [ { "vendorName": "나이키코리아", "carrier": null, "trackingNumber": null, "shippedAt": null, "status": "DEPOSIT_PENDING" } ]
    },
    "claims": [],
    "inquiries": [],
    "logs": [],
    "history": [ { "targetType": "ORDER", "fromStatus": "TEMP", "toStatus": "STOCK_REQUESTED", "changedBy": "CUSTOMER", "reason": "주문 접수, 재고차감 요청", "createdAt": "2026-10-23 09:15" } ]
  }
}
```

> 위 예시는 현재 구현 응답 구조다(`OrderService.getAdminOrderDetail`). 설계안과의 차이: ① `items[]`는 **판매자 그룹**(`vendorName`·`vendorStatus`·`products[]`)이며 상품 단위 배열이 아니다. ② `shipping`은 수령인 정보와 `memo`, 판매자별 `deliveries[]`(`vendorName`·`carrier`·`trackingNumber`·`shippedAt`·`status`)로 구성한다(단일 `carrier`/`trackingNumber` 아님). ③ 금액 필드 `productAmount`·`shippingFee`·`productDiscount`(현재 0 고정)·`cartDiscount`·`pointUsedAmount`가 추가됐다. ④ `cartDiscount`는 어드민에서 **양수**(할인금액 크기)로 내려가고 화면이 "-"를 붙인다(고객 주문 상세 §30은 음수). ⑤ `vendorName`은 판매자가 2곳 이상이면 "대표 외 N곳"이다. ⑥ `inquiries`·`logs`는 Mock이다. `shipping`·`customer` 마스킹은 문서 기준이며 구현은 적용하지 않는다(갭).

> **금액 필드 (2026-10-29)**: `amount`·`orderAmount` = 주문금액(`total_order_amount`), `paymentAmount` = 결제금액(주문금액 − 포인트), `productAmount` = 상품금액, `cartDiscount` = 할인금액(쿠폰 등 주문 단위 할인), `pointUsedAmount` = 포인트, `shippingFee` = 배송비. 고객 주문 상세(`GET /my/orders/{id}`)의 `payment`도 `orderAmount`·`pointUsedAmount`·`paymentAmount`를 내려주며 `totalAmount`는 하위호환용으로 `paymentAmount`와 같은 값이다.

> `trackingNumber` 등록 여부에 따른 `PREPARING` ↔ `IN_DELIVERY` 파생은 **미적용**이다 — `status`는 항상 플랫폼주문 상태 원시값이다(구 설계안: 미등록 `PREPARING`, 등록 `IN_DELIVERY`).

> **(2026-10-15 구현 확인) — 실제 claims[] 필드**: `claims[]`는 실제 `ord_claim` 조회 결과이며 필드는 `claimId`(실제로는 `claim.claimNo` 값이 매핑됨)·`claimType`·`status`·`refundAmount`·`extraShippingFee`·`receivedAt` 6개뿐이다 — Mock 시절 JSON에 있던 `extraShippingFeeStatus` 필드는 실제 구현(`OrderService.kt.buildClaimMap()`)에 없다. `inquiries`/`logs`는 §16 JSON 예시엔 원래 없었지만 하단 "admin/partner 주문상세 탭별 Sub-API 정책" 각주가 이미 포함을 요구했고, 실제 응답도 포함한다(값은 Mock 그대로 — 위 예시의 `inquiries: []`/`logs: []`).

#### Error Responses

| HTTP | code | message | 조건 | 대응 |
|---|---|---|---|---|
| 400 | INVALID_ORDER_ID | orderId는 숫자여야 합니다 | `orderId`가 숫자가 아님 | — |
| 404 | ORDER_NOT_FOUND | 주문을 찾을 수 없습니다 | 존재하지 않는 `orderId` | — |

> **(2026-10-15 구현 확인)** §16에는 원래 Error Responses 표가 없었다 — 실제 구현(`OrderService.kt.getAdminOrderDetail()`)이 반환하는 2개 에러를 신규 추가. 기존 404 패턴(`CLAIM_NOT_FOUND`/`PAYMENT_NOT_FOUND`/`SHIPMENT_NOT_FOUND`, readme.md §2)과 동일한 `_NOT_FOUND` 네이밍을 그대로 따름 — 신규 생성 시 중복 식별자 검색 결과 기존 코드 없음을 확인(work-scope 규칙 준수).

---

<a id="api-024"></a>
## 17. POST /api/admin/v1/orders/{orderId}/force-cancel — 예외 취소 (API-024)

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음.

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/admin/v1/orders/{orderId}/force-cancel |
| 인증 | Admin Bearer (필수) |

#### Request Body

```json
{ "reason": "고객 CS 요청에 의한 예외 취소" }
```

> **가드 (2026-10-29 확정)**: 주문이 `PREPARING`이고 출고 shipment(OUTBOUND)가 `PENDING`(송장 미등록)일 때만 허용한다. 송장 등록 후(IN_TRANSIT 이후)는 거부한다(REQ-ORD-017, AC-ORD-020·093). 취소 시 `claim_type=CANCEL` 클레임(channel=CS)을 같은 트랜잭션에서 생성하고 응답에 `claimNo`를 포함한다(REQ-ORD-082 확정, AC-ORD-100). 미구현.

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": { "orderId": "1", "status": "CANCELLED", "refundAmount": 152000, "claimNo": "CLM-20261029-003" }
}
```

#### Error Responses

| HTTP | code | message | 조건 | 대응 GWT |
|---|---|---|---|---|
| 409 | CANCEL_NOT_ALLOWED | 송장이 등록되어 취소할 수 없습니다. 배송완료 후 반품을 이용해주세요 | PREPARING이 아니거나 출고 shipment가 IN_TRANSIT 이후 | AC-ORD-093 |
| 404 | ORDER_NOT_FOUND | 주문을 찾을 수 없습니다 | 존재하지 않는 orderId | — |

---

## 17-1. POST /api/admin/v1/orders/{orderId}/claims — 어드민 클레임 접수 (API-058)

> **구현 현황 (2026-11-03)**: 미구현(설계안). 구매확정 후 하자·오배송과 기한 후 하자의 어드민 접수 경로다(REQ-ORD-081, WBS SC39-4, 정책서 7.2.1·7.2.3). 화면은 SCR-A-002-T4 [클레임 접수] 버튼이다.

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/admin/v1/orders/{orderId}/claims |
| 인증 | Admin Bearer (필수). 클레임 접수 권한이 없는 Admin은 403 `FORBIDDEN` |
| 헤더 | `Idempotency-Key: {ULID}` (2026-11-03 추가 — 중복 접수 방지, readme §4) |
| 설명 | 고객이 고객센터로 요청한 반품·교환을 CS 담당자가 대신 접수한다. 클레임은 `RECEIVED`(`channel=CS`)로 생성하고 주문상품 상태는 `CONFIRMED`를 유지한다. 접수 후 흐름(귀책 판정·수거·검수·환불)은 고객 접수 건과 같다 |

> **접수 가능 조건**
> - 배송완료 후여야 한다(배송중 이전은 거부, 정책서 7.2.1).
> - 구매확정 전 CS 대리 접수는 고객 모바일 접수와 같은 기한을 적용한다 — 단순변심은 배송완료 후 10일(배송완료 일시 + 10×24시간)을 넘기면 `CLAIM_PERIOD_EXPIRED`(422)로 거부한다(AC-ORD-032). 단순변심 기한 초과에는 운영자 승인 경로가 없다.
> - 구매확정 후에는 **하자·오배송(`VENDOR` 귀책)만** 접수한다. 단순변심은 구매확정 후 접수하지 않는다.
> - 기한은 정책서 7.2.2를 따른다(하자·오배송 = 배송완료 후 3개월 또는 안 날부터 30일). 기한을 넘긴 하자는 운영자 승인(7.2.3)이 있어야 하며, 이때 `periodExceptionApproved=true`와 `approvalReason`을 함께 보낸다.
> - 하자·오배송은 사진 증빙을 1장 이상 첨부한다(`images`).

#### Request Body

```json
{
  "claimType": "RETURN",
  "items": [ { "orderItemId": "oi-001", "quantity": 1 } ],
  "reason": "상품불량",
  "detailReason": "구매확정 후 박음질이 뜯어진 것을 발견",
  "responsibility": "VENDOR",
  "images": ["https://cdn.runnshop.com/claims/img-001.jpg"],
  "periodExceptionApproved": false,
  "approvalReason": null,
  "csMemo": "고객센터 접수(전화) 2026-11-03"
}
```

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| claimType | string | ✅ | `RETURN` / `EXCHANGE`. `EXCHANGE`는 `exchangeSkuId`가 필수(모바일 접수 §10과 같음) |
| items | object[] | ✅ | 접수 대상 주문상품 `{orderItemId, quantity}` (2026-11-03 추가·설계안, §10과 같음). 재신청 가능 수량(구매수량 − 진행 중 클레임 수량, AC-ORD-109) 초과 시 `CLAIM_ALREADY_IN_PROGRESS` |
| reason | string | ✅ | 사유 |
| detailReason | string | | 상세 사유 |
| responsibility | string | ✅ | 접수 시 신고 귀책. 구매확정 후에는 `VENDOR`만 허용 |
| images | string[] | 하자·오배송이면 ✅ | 증빙 이미지 URL, 최대 3장 |
| exchangeSkuId | string | EXCHANGE일 때 ✅ | 교환 대상 SKU(동일 상품 내 옵션) |
| periodExceptionApproved | boolean | | 기한(7.2.2)을 넘긴 하자를 운영자 승인으로 접수하면 `true` |
| approvalReason | string | periodExceptionApproved=true일 때 ✅ | 운영자 승인 사유 |
| csMemo | string | | CS 접수 메모(전화 접수 일시 등) |

> **승인자 기록**: `periodExceptionApproved=true` 접수의 승인자(`approvedBy`)는 요청 본문이 아니라 **Admin 토큰의 운영자 ID로 서버가 채운다**. 승인 사유(`approvalReason`)·승인 일시와 함께 클레임 이력에 남긴다. 클라이언트가 보낸 `approvedBy`는 무시한다(설계안).
>
> `responsibility`는 모바일 접수와 같이 `ord_claim.submitted_responsibility`에 저장하고 최종 귀책 `responsibility`는 비워 둔다. 최종 귀책은 어드민 귀책 판정(§19-1)이 확정한다. [확인 필요: 어드민 접수 시 VENDOR 귀책을 즉시 확정할지]

#### Response 201

```json
{
  "code": "SUCCESS",
  "data": {
    "claimId": "clm-010",
    "claimNo": "CLM-20261103-001",
    "claimType": "RETURN",
    "status": "RECEIVED",
    "channel": "CS",
    "orderStatus": "CONFIRMED"
  }
}
```

> 구매확정 후 접수된 건의 정산 차감(settlement 10.4.3)과 지급 포인트 회수(payment 8.6.4)는 이후 환불·완료 단계에서 처리하며 이 API의 응답 범위가 아니다.

#### Error Responses

| HTTP | code | message | 조건 | 대응 GWT |
|---|---|---|---|---|
| 409 | CLAIM_NOT_ALLOWED | 배송완료 후에만 접수할 수 있습니다 | 배송완료 전 상태(배송중 포함) | AC 없음(후속) — AC-ORD-096은 모바일 시나리오 |
| 422 | CLAIM_REASON_NOT_ALLOWED | 구매확정 후에는 하자·오배송(판매자 귀책)만 접수할 수 있습니다 | 구매확정 후 `responsibility=CUSTOMER`(단순변심 등) | AC-ORD-097 |
| 422 | CLAIM_PERIOD_EXPIRED | 기한이 초과되었습니다. 운영자 승인으로 접수해주세요 | (a) 구매확정 전 단순변심 10일 초과, (b) 하자·오배송 기한(3개월·30일 모두) 초과인데 `periodExceptionApproved`가 아님 | (a) AC-ORD-032, (b) AC 없음(후속) — 승인 필요 규칙은 AC-ORD-097 후단, AC-ORD-118은 모바일 시나리오 |
| 400 | APPROVAL_REASON_REQUIRED | 운영자 승인 사유를 입력해주세요 | `periodExceptionApproved=true`인데 `approvalReason` 없음 | AC 없음(후속) |
| 400 | CLAIM_PHOTO_REQUIRED | 상품 상태를 확인할 수 있는 사진을 1장 이상 첨부해주세요 | 하자·오배송(VENDOR)인데 images가 빈 배열 | REQ-ORD-058 |
| 400 | EXCHANGE_SKU_REQUIRED | 교환할 옵션(SKU)을 선택해주세요 | claimType=EXCHANGE인데 exchangeSkuId 누락 | REQ-ORD-056 |
| 422 | EXCHANGE_SKU_MISMATCH | 교환은 동일 상품 내 옵션 변경만 가능합니다 | exchangeSkuId의 productId가 원 주문 상품과 다름 | REQ-ORD-070 |
| 404 | ORDER_NOT_FOUND | 주문을 찾을 수 없습니다 | 존재하지 않는 orderId | — |
| 409 | CLAIM_ALREADY_IN_PROGRESS | 이미 진행 중인 클레임이 있습니다 | 대상 주문상품에 진행 중 클레임이 있어 요청 수량이 재신청 가능 수량을 초과 (2026-11-03 신설·설계안) | AC-ORD-109 |
| 403 | FORBIDDEN | 클레임 접수 권한이 없습니다 | 클레임 접수 권한이 없는 Admin 계정 (2026-11-03 신설·설계안) | AC 없음(후속) |

---

<a id="api-025"></a>

## 18. GET /api/admin/v1/claims — 클레임 목록 (API-025)

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음.

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/admin/v1/claims |
| 인증 | Admin Bearer (필수) |
| Query | `?keyword=&claimType=ALL&status=ALL&responsibility=ALL&from=&to=&page=1&size=10&sort=createdAt&direction=desc` |

> `responsibility` 필터는 전체 / 고객 귀책(`CUSTOMER`) / 판매자 귀책(`VENDOR`) / **판정 전**(responsibility가 비어 있는 건)이다. [확인 필요: 판정 전 필터의 Query 값(예: `UNDECIDED`)은 미정]

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "claims": [
      { "claimId": "clm-001", "claimNo": "CLM-20260626-001", "platformOrderNo": "P260626-00001-00", "claimType": "RETURN", "status": "RECEIVED", "responsibility": null, "submittedResponsibility": "CUSTOMER", "channel": "SELF", "refundAmount": 152000, "createdAt": "2026-06-26 10:30", "completedAt": null }
    ],
    "pagination": { "page": 1, "size": 10, "totalCount": 8, "totalPages": 1 }
  }
}
```

---

## 18-1. GET /api/admin/v1/claims/{claimId} — 클레임 상세 (어드민) (API-056)

> **구현 현황 (2026-10-29)**: 미구현(설계안) — 컨트롤러 매핑 없음.

> **신규 2026-10-29 — 미구현(설계안).** 화면레이아웃(DN) 어드민 클레임 상세(SCR-A-004)가 필요로 하는 단건 조회다. 아래 "admin/partner 주문상세 탭별 Sub-API 정책"과 같이 **탭별 sub-API를 두지 않고 단일 응답에 모든 탭 데이터를 포함**한다. DN이 적었던 `/refund`(GET)·`/shipping`·`/logs` 개별 endpoint는 이 응답의 섹션으로 대체한다.

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/admin/v1/claims/{claimId} |
| 인증 | Admin Bearer (필수) |
| 호출원 | SCR-A-004 (T1 클레임상품 / T2 환불정보 / T3 배송정보 / T4 변경이력) |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "claimId": "clm-001",
    "claimNo": "CLM-20260628-001",
    "claimType": "RETURN",
    "status": "RECEIVED",
    "platformOrderNo": "P260622-00008-00",
    "vendorOrderNo": "V260622-00008-01",
    "createdAt": "2026-06-28 10:30",
    "reason": "사이즈가 맞지 않습니다",
    "detailReason": "정사이즈보다 작게 나와서 반품으로 변경했습니다.",
    "responsibility": null,
    "submittedResponsibility": "CUSTOMER",
    "items": [
      { "orderItemId": "oi-001", "productName": "호카 클리프턴 9", "optionName": "오렌지 / 275", "quantity": 1, "productOrderAmount": 169000, "refundAmount": 169000, "attachments": [] }
    ],
    "refund": { "method": "VIRTUAL_ACCOUNT", "status": "PENDING", "refundAmount": 169000, "returnShippingFee": 6000, "bankAccount": null },
    "shipments": [
      { "shipmentId": "shp-001", "shipmentType": "PICKUP", "carrier": "CJ대한통운", "trackingNo": "9876543210", "status": "IN_TRANSIT", "requestedAt": "2026-06-29 09:00", "failReason": null }
    ],
    "history": [
      { "targetType": "CLAIM", "fromStatus": null, "toStatus": "RECEIVED", "changedBy": "고객", "reason": "반품 신청", "createdAt": "2026-06-28 10:30" }
    ]
  }
}
```

> `responsibility`는 귀책 판정(§19-1) 전에는 `null`이고 화면은 "판정 전"으로 표시하며, 고객 자진신고는 `submittedResponsibility`로 내려준다(판정 후 `responsibility`는 `CUSTOMER`/`VENDOR`). `status`는 DH 클레임 11상태 원시값이다. 화면의 4종 표시 상태(접수/처리중/완료/반려)는 DN이 매핑한다. `history`는 §16과 같이 `ord_status_history`에서 최신순으로 조회한다(`logs` 아님). `refund`는 GET으로만 제공하고 환불 실행은 §33 `POST .../refund`(API-029)가 맡는다. 금액 용어는 DBA order.md 3.7.5를 따른다(환불 기준 = 상품주문금액).

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 404 | CLAIM_NOT_FOUND | 클레임을 찾을 수 없습니다 | 존재하지 않는 claimId |

---

## 19. POST /api/admin/v1/claims/{claimId}/start — 클레임 처리 시작

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음. UI 전용 API-050(호출원 SCR-A-004-T1 [처리 시작]), claim.status는 `RECEIVED` 유지(아래 §19 비고).

> API-050 (프로그램목록DQ §2-2, 2026-08-24 신규 부여 — 이전에는 DL에만 존재하고 DQ에 대응 ID가 없었음).

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/admin/v1/claims/{claimId}/start |
| 인증 | Admin Bearer (필수) |

#### Response 200

```json
{ "code": "SUCCESS", "data": { "claimId": "clm-001", "status": "RECEIVED" } }
```

> 클레임 11상태 모델(DH)에는 별도의 `IN_PROGRESS` 상태가 없다. "처리 시작"은 CS가 클레임 상세를 열어 확인 중임을 표시하는 UI 동작일 뿐, 클레임 상태는 `RECEIVED`로 유지되며 이후 귀책 판정(§19-1 `blame-decision`)에서 `PAYMENT_PENDING`/`INSPECTING`으로 분기한다.

---

<a id="api-026"></a>
## 19-1. POST /api/admin/v1/claims/{claimId}/blame-decision — 귀책 판정 (API-026)

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음.

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/admin/v1/claims/{claimId}/blame-decision |
| 인증 | Admin Bearer (필수) |
| 설명 | 고객이 신청 시 제출한 `responsibility`를 CS가 최종 확정한다(고객 제출값과 달라도 CS 판정이 최종, 덮어쓰기 가능 — REQ-ORD-066). `CUSTOMER` 판정 시 상태 → `PAYMENT_PENDING`(수거 배송비 결제 대기). `VENDOR` 판정 시 상태 → `INSPECTING` + shipment(PICKUP) 자동생성. `claimType=EXCHANGE`이고 `VENDOR` 판정인 경우 교환 SKU 재고를 즉시 선점하고 shipment(EXCHANGE_OUT)를 병행 생성해 선출고한다(맞교환 원칙, REQ-ORD-056). |

#### Request Body

```json
{ "responsibility": "VENDOR" }
```

> `responsibility`: `CUSTOMER`(단순변심 등) | `VENDOR`(상품불량 등). 고객이 신청 시 제출한 값을 참고값으로만 쓰고 CS가 최종 확정한다(REQ-ORD-066).

#### Response 200

`CUSTOMER` 판정:
```json
{ "code": "SUCCESS", "data": { "claimId": "clm-001", "responsibility": "CUSTOMER", "status": "PAYMENT_PENDING" } }
```

`VENDOR` 판정 (`claimType=RETURN`):
```json
{ "code": "SUCCESS", "data": { "claimId": "clm-001", "responsibility": "VENDOR", "status": "INSPECTING", "shipment": { "shipmentType": "PICKUP", "status": "PENDING" } } }
```

`VENDOR` 판정 (`claimType=EXCHANGE`, 교환 SKU 즉시 선출고):
```json
{ "code": "SUCCESS", "data": { "claimId": "clm-002", "responsibility": "VENDOR", "status": "INSPECTING", "shipment": { "shipmentType": "PICKUP", "status": "PENDING" }, "exchangeShipment": { "shipmentType": "EXCHANGE_OUT", "status": "PENDING" } } }
```

#### Error Responses

| HTTP | code | message | 조건 | 대응 |
|---|---|---|---|---|
| 409 | CLAIM_ALREADY_DECIDED | 이미 귀책 판정이 완료된 클레임입니다 | claim.status ≠ RECEIVED | — |
| 409 | EXCHANGE_STOCK_UNAVAILABLE | 교환 가능한 재고가 없습니다 | `claimType=EXCHANGE`인 클레임의 귀책판정 시점에 `exchangeSkuId` 재고 선점 실패 (선출고 전 단계에서 판정 자체를 차단; 이전에는 39-1 exchange-ship 시점 에러로 잘못 배치돼 있었음) | REQ-ORD-069 |

> `EXCHANGE_STOCK_UNAVAILABLE`은 이 endpoint(귀책판정 시점)에서만 반환된다. 39-1(exchange-ship, 운송장 등록)은 이미 재고 선점이 끝난 뒤의 배송 등록 단계이므로 이 에러가 발생하지 않는다.

---

<a id="api-027"></a>
## 20. POST /api/admin/v1/claims/{claimId}/complete — 클레임 완료 (API-027)

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음.

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/admin/v1/claims/{claimId}/complete |
| 인증 | Admin Bearer (필수) |

#### Request Body

```json
{ "memo": "수거 확인 완료. 환불 처리 진행" }
```

#### Response 200

```json
{ "code": "SUCCESS", "data": { "claimId": "clm-001", "status": "COMPLETED" } }
```

---

<a id="api-028"></a>
## 21. POST /api/admin/v1/claims/{claimId}/reject — 클레임 반려 (API-028)

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음.

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/admin/v1/claims/{claimId}/reject |
| 인증 | Admin Bearer (필수) |

#### Request Body

```json
{ "rejectReason": "고객 귀책 사유에 해당하지 않음" }
```

#### Response 200

```json
{ "code": "SUCCESS", "data": { "claimId": "clm-001", "status": "REJECTED" } }
```

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 400 | REASON_REQUIRED | 반려 사유를 입력해주세요 | 사유 누락 |

---

## 22. GET /api/partner/v1/orders — 판매자 주문 목록

> **필드명 주의 (RD-24)**: 판매자 응답의 `platformOrderNo` 필드에는 설계상 **판매자 주문번호**(`V…`, 예 `V260626-00001-01`)가 담긴다(필드명은 하위호환으로 유지, 의미상 `vendorOrderNo`). 어드민·고객 응답의 `platformOrderNo`는 `P…` 플랫폼 주문번호다.

> **구현 현황 (2026-10-29)**: Mock — `OrderController.getPartnerOrders`가 `mock/order/partner__GET_orders.json`을 필터·페이징한다(판매자(vendor) 필터 미적용, `summary` 없음).

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/partner/v1/orders |
| 인증 | Partner Bearer (필수) |
| Query | `?status=ALL&from=&to=&keyword=&page=1&size=10&sort=orderDate&direction=desc` |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "orders": [
      { "orderId": "ord-001", "platformOrderNo": "V260626-00001-01", "productName": "나이키 페가수스 41", "customerName": "홍*동", "quantity": 1, "amount": 152000, "status": "PAYMENT_COMPLETED", "orderDate": "2026-06-26" }
    ],
    "pagination": { "page": 1, "size": 10, "totalCount": 10, "totalPages": 1 }
  }
}
```

---

## 23. GET /api/partner/v1/orders/{orderId} — 판매자 주문 상세

> **구현 현황 (2026-10-29)**: 구현(부분) — DB. `OrderController.getPartnerOrderDetail`(소유 검증 403). 응답은 `myItems`·`otherVendorItems`·`history`(Mock) 구성이며 아래 예시와 다르다. `platformOrderNo`에는 현재 구현이 판매자 주문번호(V…)가 아닌 플랫폼 주문번호(P…)를 담는다.

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/partner/v1/orders/{orderId} |
| 인증 | Partner Bearer (필수) |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "orderId": "ord-001",
    "platformOrderNo": "V260626-00001-01",
    "status": "PAYMENT_COMPLETED",
    "productName": "나이키 페가수스 41",
    "customerName": "홍*동",
    "quantity": 1,
    "amount": 152000,
    "orderDate": "2026-06-26",
    "history": [ { "at": "2026-06-26 09:15", "action": "주문 접수", "memo": "결제 완료" } ]
  }
}
```

---

## 24. POST /api/partner/v1/orders/{orderId}/ship — 출고 처리

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음.

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/partner/v1/orders/{orderId}/ship |
| 인증 | Partner Bearer (필수) |

#### Response 200

```json
{ "code": "SUCCESS", "data": { "orderId": "ord-001", "status": "PREPARING" } }
```

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 409 | SHIP_NOT_ALLOWED | 결제완료 상태에서만 출고 처리할 수 있습니다 | PAYMENT_COMPLETED 아닌 상태 |

---

## 25. GET /api/partner/v1/shipping — 배송 목록

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음.

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/partner/v1/shipping |
| 인증 | Partner Bearer (필수) |
| Query | `?status=ALL&keyword=&page=1&size=10&sort=shippedAt&direction=desc` |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "items": [
      { "orderId": "ord-001", "platformOrderNo": "V260626-00001-01", "productName": "나이키 페가수스 41", "customerName": "홍*동", "status": "PREPARING", "deliveryCompany": null, "trackingNo": null, "shippedAt": null }
    ],
    "pagination": { "page": 1, "size": 10, "totalCount": 5, "totalPages": 1 }
  }
}
```

---

## 26. POST /api/partner/v1/shipping/{orderId} — 운송장 등록

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음.

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/partner/v1/shipping/{orderId} |
| 인증 | Partner Bearer (필수) |

#### Request Body

```json
{ "deliveryCompany": "CJ대한통운", "trackingNo": "1234567890" }
```

#### Response 200

```json
{ "code": "SUCCESS", "data": { "orderId": "ord-001", "status": "PREPARING", "shipment": { "shipmentType": "OUTBOUND", "status": "IN_TRANSIT", "carrier": "CJ대한통운", "trackingNumber": "1234567890", "shippedAt": "2026-06-27 10:00" } } }
```

> v6: order.status는 `IN_DELIVERY`로 전환되지 않고 `PREPARING`을 유지한다. 배송 실행은 신규 `ord_shipment`(shipmentType=OUTBOUND)로 표현되며, "배송 중" 화면 표시는 `PREPARING + shipment.status=IN_TRANSIT` 조인으로 계산한다(REQ-ORD-059).

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 400 | TRACKING_NO_REQUIRED | 운송장번호를 입력해주세요 | 번호 누락 |

---

## 27. POST /api/partner/v1/claims/{claimId}/pickup-confirm — 입고 확인

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음.

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/partner/v1/claims/{claimId}/pickup-confirm |
| 인증 | Partner Bearer (필수) |

#### Response 200

```json
{ "code": "SUCCESS", "data": { "claimId": "clm-001", "pickupConfirmedAt": "2026-06-30 14:00" } }
```

---

## 30. GET /api/mobile/v1/my/orders/{orderId} — 내 주문 상세

> **구현 현황 (2026-10-29)**: 구현 — DB. `OrderController.getMyOrderDetail`. `history`는 Mock.

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/mobile/v1/my/orders/{orderId} |
| 인증 | Bearer {memberId} (필수) |
| 설명 | 본인 주문 상세 (판매자별 상품, 결제정보, 배송정보, 주문이력) |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "orderId": "1",
    "platformOrderNo": "P261023-00001-00",
    "status": "DEPOSIT_PENDING",
    "orderDate": "2026-10-23 09:15",
    "items": [
      {
        "vendorName": "나이키코리아",
        "vendorStatus": "DEPOSIT_PENDING",
        "products": [
          { "productName": "나이키 페가수스 41", "imageUrl": "https://placehold.co/80x80/f5f5f5/333?text=...", "optionName": "블랙/265", "quantity": 1, "amount": 152000, "claimableQuantity": 1 }
        ]
      }
    ],
    "payment": { "productAmount": 152000, "productDiscount": 0, "cartDiscount": -3000, "shippingFee": 0, "orderAmount": 149000, "pointUsedAmount": 3000, "paymentAmount": 146000, "totalAmount": 146000, "method": "복합결제 (가상계좌 + 포인트)", "paidAt": null },
    "shipping": { "recipientName": "홍*동", "phone": "010-****-5678", "address": "[06234] 서울 강남구 테헤란로 123 런앤샵타워 5층", "memo": "부재 시 문 앞에", "carrier": null, "trackingNumber": null, "deliveryStatus": "입금대기" },
    "history": [ { "at": "2026-10-23 09:15", "event": "주문 접수" } ]
  }
}
```

> 위 예시는 현재 구현 응답 구조다(`OrderService.getMyOrderDetail`, 본인 주문이 아니면 403). 이전 설계안과의 차이: `orders[]` → **`items[]`**(판매자 그룹), 그 안의 `items[]` → **`products[]`**, `orderQuantity` → `quantity`, `payment.totalProductPrice` → `productAmount`, `payment.totalPayment` → `totalAmount`(= `paymentAmount`), 배송 `carrier`·`trackingNumber`는 대표 판매자 주문 1건 기준이다. `claimInProgress`·`claimCompleted`는 **미구현**이며 `claimableQuantity`는 항상 `quantity`와 같다(클레임 수량 차감 미연동). `history`는 Mock이다. `phone` 마스킹은 구현에 적용되지 않는다(갭).

> `claimableQuantity`(재신청 가능 수량, **설계안**) = `orderQuantity` − 진행 중/완료된 클레임 수량. `REJECTED`(반려)·`PAYMENT_EXPIRED`(배송비 결제 만료)로 종료된 클레임은 차감 대상에서 제외하여 원래 구매수량 그대로 재신청 가능하도록 복원한다(REQ-ORD-067, REQ-ORD-074). 반품/교환 신청 화면(#10)은 이 값을 참조해 신청 가능 최대 수량을 노출한다.

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 400 | INVALID_ORDER_ID | orderId는 숫자여야 합니다 | `orderId`가 숫자가 아님 |
| 404 | ORDER_NOT_FOUND | 주문을 찾을 수 없습니다 | 존재하지 않는 `orderId` |
| 403 | FORBIDDEN | 본인 주문만 조회할 수 있습니다 | 타인 주문 |

---

## 31. POST /api/mobile/v1/my/claims/{claimId}/shipping-payment — 클레임 배송비 결제

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음.

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/mobile/v1/my/claims/{claimId}/shipping-payment |
| 인증 | Bearer {memberId} (필수) |
| Header | `Idempotency-Key: {ULID}` (필수 권장, 중복 결제 방지) |
| 설명 | 클레임 수거/반송 배송비 결제. PG SDK 인증 후 서버 확인. **배송비 쿠폰 사용 가능**(2026-11-03 확정) — 서버가 산정한 클레임 배송비에 쿠폰 할인을 적용한 금액이 결제 금액이다. 단순변심 수거 배송비는 서버가 산정한다 — 편도 반품 배송비 3,000원 + 초도 배송비 중 할인받은 금액(정책서 6.9.7, 2026-10-29) |

#### Request Body

```json
{
  "paymentType": "PICKUP",
  "paymentMethodId": "pm-001",
  "couponIds": ["CPN-003"]
}
```

> paymentType: `PICKUP`(수거 배송비) 또는 `RETURN`(반송 배송비)
>
> **금액은 요청에 없다(2026-10-29)** — 결제 배송비는 **서버가 산정**하며 클라이언트가 `amount`를 보내지 않는다(입력 금지). 정책 값(정책서 6.9.7): 단순변심 수거 = 편도 반품 배송비 3,000원 + 초도 배송비 중 할인받은 금액 → 유료배송 주문 3,000원, 무료배송 주문 6,000원, 배송비 쿠폰 50% 할인 주문 4,500원. 교환 수거 = 왕복 6,000원. 반송(품질점검 전체 불합격, `RETURN`) = 편도 3,000원 고정. `couponIds`(배열)가 있으면 서버 산정값에서 쿠폰 할인을 뺀 금액이 결제 금액이며, PG 인증 결제금액이 이 금액과 다르면 `AMOUNT_MISMATCH`로 거부한다(확정). `couponIds`는 고객이 보유한 **배송비 쿠폰**만 허용한다(Promotion 검증). 편도 배송비(반품 수거·반송)는 1장, **교환 왕복 배송비는 2장 이상 보유 시 최대 2장**까지 허용하며 초과하면 `COUPON_NOT_APPLICABLE`로 거부한다. [확인 필요: 할인받은 초도 배송비 부과액에도 적용되는지, 결제 만료·클레임 철회 시 쿠폰 복원]

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": { "claimId": "clm-001", "paymentType": "PICKUP", "paidAmount": 4500, "couponApplied": true, "couponDiscountAmount": 1500, "status": "INSPECTING" }
}
```

> v6: 수거 배송비 결제 완료 시 `status`는 `PICKUP`이 아니라 `INSPECTING`으로 전환된다(shipment(PICKUP)가 `ord_shipment`에 자동 생성되며 배송 실행은 그쪽에서 추적). `paymentType=RETURN`(반송 배송비 결제)인 경우 `status`는 변경 없이 `RETURN_PAYMENT_PENDING`을 유지한다.

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 422 | PAYMENT_EXPIRED | 결제 기한이 초과되었습니다 | 24시간 초과 → 자동취소 |
| 400 | PAYMENT_FAILED | 결제에 실패했습니다 | PG 승인 실패 |
| 422 | AMOUNT_MISMATCH | 결제 금액이 올바르지 않습니다 | PG 인증 결제금액이 서버 산정 배송비와 다름 (2026-10-29 확정) |
| 422 | COUPON_NOT_APPLICABLE | 사용할 수 없는 쿠폰입니다 | 배송비 쿠폰이 아니거나 이 클레임 배송비에 적용 불가 (AC-ORD-125) |
| 422 | COUPON_EXPIRED | 만료된 쿠폰입니다 | 지정한 쿠폰이 만료됨 (AC-ORD-125) |
| 409 | INVALID_STATUS | 배송비 결제 대기 상태가 아닙니다 | claim.status가 `PAYMENT_PENDING`/`RETURN_PAYMENT_PENDING`이 아님 |
| 404 | CLAIM_NOT_FOUND | 클레임을 찾을 수 없습니다 | 존재하지 않는 클레임 |

---

## 32. PUT /api/mobile/v1/my/cart/items/{cartItemId}/option — 장바구니 옵션 변경

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음.

| 항목 | 내용 |
|---|---|
| Method | PUT |
| Path | /api/mobile/v1/my/cart/items/{cartItemId}/option |
| 인증 | Bearer {memberId} (필수) |
| 설명 | 장바구니 상품의 옵션(색상/사이즈) 변경. 품절 = 실재고 − 장바구니 선점수량 ≤ 0 |

#### Request Body

```json
{ "skuId": "sku-002" }
```

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": { "cartItemId": "cart-001", "skuId": "sku-002", "color": "화이트", "size": "265", "stock": 5 }
}
```

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 409 | OPTION_SOLD_OUT | 해당 옵션은 품절입니다 | 잔여수량 ≤ 0 |
| 404 | CART_ITEM_NOT_FOUND | 장바구니 항목을 찾을 수 없습니다 | 존재하지 않는 ID |

---

## 32-1. GET /api/mobile/v1/my/orders/{orderSheetId}/coupon-combinations — 쿠폰 조합별 할인 계산

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음(API-008, Bolt13).

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/mobile/v1/my/orders/{orderSheetId}/coupon-combinations |
| 인증 | Bearer {memberId} (필수) |
| 설명 | 쿠폰 팝업 진입 시 호출. 적용 가능한 모든 쿠폰 조합별 할인 결과를 미리 계산하여 반환 (FE 캐시용). 가장 유리한 조합을 `recommended`로 표시 |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "currentDiscount": {
      "productDiscountType": "INSTANT",
      "productDiscount": -48000,
      "cartDiscountType": "CONDITION",
      "cartDiscount": -3000
    },
    "recommended": {
      "productCouponId": "CPN-002",
      "cartCouponId": "CPN-003",
      "shippingCouponId": null,
      "totalOrderAmount": 401300
    },
    "productCoupons": [
      { "couponId": "CPN-001", "name": "신규회원 10%", "discount": -41800, "diff": 6200, "favorable": false },
      { "couponId": "CPN-002", "name": "VIP 15%", "discount": -62700, "diff": -14700, "favorable": true }
    ],
    "cartCoupons": [
      { "couponId": "CPN-003", "name": "여름 러닝 5,000원", "discount": -5000, "diff": -2000, "favorable": true }
    ],
    "shippingCoupons": [
      { "couponId": "CPN-004", "name": "무료배송", "discount": -3000 }
    ],
    "combinations": [
      { "productCouponId": null, "cartCouponId": null, "shippingCouponId": null, "productDiscount": -48000, "cartDiscount": -3000, "shippingDiscount": 0, "totalOrderAmount": 418000 },
      { "productCouponId": "CPN-002", "cartCouponId": "CPN-003", "shippingCouponId": null, "productDiscount": -62700, "cartDiscount": -5000, "shippingDiscount": 0, "totalOrderAmount": 401300 }
    ]
  }
}
```

> `diff`: 현재 할인 대비 차이 (음수 = 추가 할인, 양수 = 할인 감소)
> `favorable`: true면 현재보다 유리
> `recommended`: 가장 유리한 조합 (FE에서 기본 선택 상태로 표시)

---

## 32-2. POST /api/mobile/v1/my/orders/{orderSheetId}/calculate — 쿠폰 확정 재계산 (Phase 2)

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음(API-009, Bolt13).

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/mobile/v1/my/orders/{orderSheetId}/calculate |
| 인증 | Bearer {memberId} (필수) |
| 설명 | 쿠폰 팝업 [적용하기] 클릭 시 호출. 선택된 쿠폰 조합으로 서버 재계산 (정합성 검증 + 최종 금액 확정) |

#### Request Body

```json
{
  "productCouponId": "CPN-002",
  "cartCouponId": "CPN-003",
  "shippingCouponId": null,
  "pointUsed": 3000
}
```

> couponId가 null이면 기본 할인(즉시/조건) 유지

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "productDiscountType": "COUPON",
    "productDiscount": -62700,
    "cartDiscountType": "COUPON",
    "cartDiscount": -5000,
    "shippingDiscount": 0,
    "pointDiscount": -3000,
    "totalPayment": 398300
  }
}
```

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 422 | COUPON_EXPIRED | 쿠폰이 만료되었습니다 | 팝업 열린 동안 쿠폰 만료 |
| 422 | COUPON_NOT_APPLICABLE | 적용 조건을 충족하지 않습니다 | 최소 상품금액(할인 후 상품금액 기준) 미달 등 |
| 422 | POINT_EXCEED | 사용 가능 포인트를 초과했습니다 | 잔액 부족 |

---

<a id="api-029"></a>
## 33. POST /api/admin/v1/claims/{claimId}/refund — 환불 처리 (수동) (API-029)

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음.

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/admin/v1/claims/{claimId}/refund |
| 인증 | Admin Bearer (필수) |
| 설명 | 품질점검 합격 후 환불 처리. 원결제수단 또는 계좌이체(수동). 환불 승인은 품질 합격 판정이며 3영업일 기한은 합격 일시부터 센다(정책서 8.1.2·8.1.3). 합격 전 호출은 거부한다(INVALID_STATUS) |

#### Request Body

```json
{
  "refundMethod": "ORIGINAL",
  "bankAccount": null
}
```

> refundMethod: `ORIGINAL`(원결제수단) 또는 `BANK_TRANSFER`(계좌이체)
> (2026-10-29) 가상계좌 결제분은 결제 시 저장된 환불계좌(§6 `refundAccount`)를 기본값으로 쓰며 `bankAccount`를 생략할 수 있다. bankAccount: refundMethod가 BANK_TRANSFER일 때 필수 `{ "bankName": "국민은행", "accountNo": "123-456-789", "holderName": "홍길동" }`

#### Response 200

```json
{ "code": "SUCCESS", "data": { "claimId": "clm-001", "status": "REFUNDED", "refundAmount": 169000 } }
```

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 409 | INVALID_STATUS | 품질점검 합격 상태에서만 환불할 수 있습니다 | claim.status ≠ `PICKED_UP` |
| 404 | CLAIM_NOT_FOUND | 클레임을 찾을 수 없습니다 | 존재하지 않는 클레임 |

---

<a id="api-030"></a>
## 34. POST /api/admin/v1/claims/{claimId}/dispose — 폐기 처리 (API-030)

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음.

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/admin/v1/claims/{claimId}/dispose |
| 인증 | Admin Bearer (필수) |
| 설명 | 수거거부(PICKUP_REJECTED) 건에 대해 폐기 결정 |

#### Request Body

```json
{ "reason": "상품 심각 훼손으로 반송 불가" }
```

#### Response 200

```json
{ "code": "SUCCESS", "data": { "claimId": "clm-001", "status": "DISPOSED" } }
```

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 409 | INVALID_STATUS | 품질점검 거부 건만 폐기 처리할 수 있습니다 | claim.status ≠ `PICKUP_REJECTED` |
| 404 | CLAIM_NOT_FOUND | 클레임을 찾을 수 없습니다 | 존재하지 않는 클레임 |

---

<a id="api-031"></a>
## 35. POST /api/admin/v1/claims/{claimId}/request-return-payment — 반송 배송비 추가결제 요청 (API-031)

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음.

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/admin/v1/claims/{claimId}/request-return-payment |
| 인증 | Admin Bearer (필수) |
| 설명 | 수거거부 건에 대해 고객에게 반송 배송비 추가결제 요청. 고객 알림톡 발송. 반송 배송비는 정책 값 편도 3,000원 고정이다(정책서 6.9.7, 2026-10-29) |

#### Request Body

```json
{ "returnShippingFee": 3000 }
```

> `returnShippingFee`는 정책 값 3,000원이다(2026-10-29 확정). 다른 값은 거부하거나 생략 시 3,000원을 기본값으로 쓴다.

#### Response 200

```json
{ "code": "SUCCESS", "data": { "claimId": "clm-001", "status": "RETURN_PAYMENT_PENDING", "paymentType": "RETURN" } }
```

> `status`는 `RETURN_PAYMENT_PENDING`(반송 배송비 결제대기)으로 전환된다. 수거 배송비 결제대기 상태인 `PAYMENT_PENDING`과는 구분되는 별도 상태이므로 혼동하지 않는다.

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 409 | INVALID_STATUS | 품질점검 거부 건만 반송 배송비를 요청할 수 있습니다 | claim.status ≠ `PICKUP_REJECTED` |
| 404 | CLAIM_NOT_FOUND | 클레임을 찾을 수 없습니다 | 존재하지 않는 클레임 |

---

## 36. POST /api/partner/v1/shipping/{claimId}/pickup — 수거 운송장 등록

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음.

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/partner/v1/shipping/{claimId}/pickup |
| 인증 | Partner Bearer (필수) |
| 설명 | 클레임 수거를 위한 택배사 + 운송장 등록 |

#### Request Body

```json
{ "deliveryCompany": "CJ대한통운", "trackingNo": "9876543210" }
```

#### Response 200

```json
{ "code": "SUCCESS", "data": { "claimId": "clm-001", "shipment": { "shipmentType": "PICKUP", "status": "IN_TRANSIT", "carrier": "CJ대한통운", "trackingNumber": "9876543210", "shippedAt": "2026-06-29 09:00" } } }
```

> v6: 이 endpoint는 `ord_shipment`(shipmentType=PICKUP)를 PENDING→IN_TRANSIT으로 전환할 뿐, claim.status는 변경하지 않는다(귀책판정 시점에 이미 INSPECTING 또는 PAYMENT_PENDING 상태).

---

## 37. POST /api/partner/v1/claims/{claimId}/inspect-pass — 품질점검 합격

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음.

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/partner/v1/claims/{claimId}/inspect-pass |
| 인증 | Partner Bearer (필수) |
| 설명 | 품질점검 합격 처리. 상태 → PICKED_UP(수거완료) |

#### Request Body

```json
{ "memo": "상품 상태 양호. 환불 가능", "tagIntact": true }
```

> `tagIntact`: 택(TAG) 부착 유지 여부. `claimType=EXCHANGE` 건의 판정 근거 (REQ-ORD-057). RETURN 건은 생략 가능

#### Response 200

```json
{ "code": "SUCCESS", "data": { "claimId": "clm-001", "status": "PICKED_UP", "tagIntact": true } }
```

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 409 | INVALID_STATUS | 품질점검 상태만 합격 처리할 수 있습니다 | claim.status ≠ `INSPECTING` |
| 404 | CLAIM_NOT_FOUND | 클레임을 찾을 수 없습니다 | 존재하지 않는 클레임 |

---

## 38. POST /api/partner/v1/claims/{claimId}/inspect-reject — 품질점검 거부

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음.

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/partner/v1/claims/{claimId}/inspect-reject |
| 인증 | Partner Bearer (필수) |
| 설명 | 품질점검 불합격. 상태 → PICKUP_REJECTED(수거거부). 사유 필수 |

#### Request Body

```json
{ "rejectReason": "상품 택 제거 및 사용 흔적으로 반품 불가", "tagIntact": false, "images": ["https://cdn.runnshop.com/claims/inspect-001.jpg"] }
```

> `tagIntact`: 택(TAG) 부착 유지 여부. `claimType=EXCHANGE` 건은 택 제거·훼손이 거부 사유인 경우 `false`로 전달 (REQ-ORD-057). RETURN 건은 생략 가능
> `images`: 상품 상태(훼손/택 제거 등)를 확인할 수 있는 증빙 사진 URL 배열. **`claimType=EXCHANGE` 건은 최소 1장 필수**(REQ-ORD-072, REQ-ORD-058 VENDOR귀책 사진 필수와 대칭). RETURN 건은 선택. 서버는 이 이미지를 `uploaded_by=VENDOR`로 저장하며, 고객 접수 시 첨부한 사진(`uploaded_by=CUSTOMER`, #10)과는 별도로 최대 3장 제한이 독립 적용된다(REQ-ORD-075).

#### Response 200

```json
{ "code": "SUCCESS", "data": { "claimId": "clm-001", "status": "PICKUP_REJECTED", "tagIntact": false } }
```

#### Error Responses

| HTTP | code | message | 조건 | 대응 |
|---|---|---|---|---|
| 400 | REASON_REQUIRED | 거부 사유를 입력해주세요 | 사유 누락 | — |
| 400 | INSPECT_PHOTO_REQUIRED | 상품 상태를 확인할 수 있는 사진을 1장 이상 첨부해주세요 | `claimType=EXCHANGE`인데 `images`가 빈 배열(0장) | REQ-ORD-072 |
| 409 | INVALID_STATUS | 품질점검 상태만 거부 처리할 수 있습니다 | claim.status ≠ `INSPECTING` | — |

---

## 39. POST /api/partner/v1/claims/{claimId}/return-ship — 반송 운송장 등록

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음.

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/partner/v1/claims/{claimId}/return-ship |
| 인증 | Partner Bearer (필수) |
| 설명 | 수거거부 후 반송 배송비 결제 완료된 건에 대해 반송 운송장 등록 |

#### Request Body

```json
{ "deliveryCompany": "CJ대한통운", "trackingNo": "1111222233" }
```

#### Response 200

```json
{ "code": "SUCCESS", "data": { "claimId": "clm-001", "status": "RETURN_PAYMENT_PENDING", "shipment": { "shipmentType": "RETURN", "status": "IN_TRANSIT", "carrier": "CJ대한통운", "trackingNumber": "1111222233" } } }
```

> v6: 이 endpoint는 `ord_shipment`(shipmentType=RETURN)를 PENDING→IN_TRANSIT으로 전환할 뿐, claim.status는 `RETURN_PAYMENT_PENDING`을 그대로 유지한다(반송 배송비 결제 완료 후 진입한 상태). shipment(RETURN)이 DELIVERED로 전환되어야 배치가 클레임을 COMPLETED로 자동전환한다(39-2. 참조).

---

## 39-1. POST /api/partner/v1/claims/{claimId}/exchange-ship — 교환상품 선출고 운송장 등록

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음.

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/partner/v1/claims/{claimId}/exchange-ship |
| 인증 | Partner Bearer (필수) |
| 설명 | `claimType=EXCHANGE` 건이 귀책판정되어 `INSPECTING` 상태로 전환될 때(또는 그 이전), 교환 대상 SKU(`exchange_sku_id`)를 원상품 수취 이전에 선출고하기 위한 택배사 + 운송장 등록 (REQ-ORD-056, 맞교환 원칙: 선출고 후 수취). 재고 선점은 이 endpoint 이전 §19-1(`blame-decision`)에서 이미 완료된 상태이므로 이 endpoint는 재고를 다시 확인하지 않는다. 반송 운송장 등록(39.)과 동일한 패턴 |

#### Request Body

```json
{ "deliveryCompany": "CJ대한통운", "trackingNo": "4444555566" }
```

#### Response 200

```json
{ "code": "SUCCESS", "data": { "claimId": "clm-001", "exchangeSkuId": "sku-002", "shipment": { "shipmentType": "EXCHANGE_OUT", "status": "IN_TRANSIT", "carrier": "CJ대한통운", "trackingNumber": "4444555566", "shippedAt": "2026-06-29 09:30" } } }
```

> v6: 이 endpoint는 `ord_shipment`(shipmentType=EXCHANGE_OUT)를 PENDING→IN_TRANSIT으로 전환할 뿐, claim.status는 변경하지 않는다. shipment(EXCHANGE_OUT)의 DELIVERED 전환은 이 endpoint가 아니라 배송 추적 배치(§19)가 처리하며, 클레임이 PICKED_UP(합격)이면 같은 배치 주기에 COMPLETED로 전환하고 CLAIM_COMPLETED를 발행한다(REQ-ORD-083, AC-ORD-116). 합격 전에 수령된 경우에는 합격 판정 후 다음 주기에 전환한다. 원상품 수취는 별도 shipment(PICKUP)로 추적한다.

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 400 | TRACKING_NO_REQUIRED | 운송장번호를 입력해주세요 | 번호 누락 |
| 409 | NOT_EXCHANGE_CLAIM | 교환 클레임이 아닙니다 | claimType≠EXCHANGE |

> `EXCHANGE_STOCK_UNAVAILABLE`(교환 재고 없음)은 이 endpoint의 에러가 아니다 — 재고 선점은 귀책판정(§19-1 `blame-decision`) 시점에 이미 끝났어야 하므로, 재고 부족은 그때 차단된다(REQ-ORD-069). 이 endpoint는 운송장 등록만 수행한다.

---

## 39-2. POST /api/admin/v1/claims/{claimId}/return-delivered — 반송 배송완료 확인

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음.

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/admin/v1/claims/{claimId}/return-delivered |
| 인증 | System/Admin Bearer (필수) — 택배사 배송완료 콜백 수신 또는 배송추적 배치가 호출 |
| 설명 | v6: `RETURN_SHIPPING`/`RETURN_DELIVERED`는 더 이상 claim.status가 아니다. 이 endpoint는 `ord_shipment`(shipmentType=RETURN, 즉 claim.status=RETURN_PAYMENT_PENDING 건에 연결된 shipment)가 IN_TRANSIT 상태일 때 택배사로부터 배송완료를 수신(또는 배치가 택배사 API 조회 결과 확인)하면 shipment.status를 DELIVERED로 전환한다. claim.status 자체는 이 시점에는 RETURN_PAYMENT_PENDING을 유지하며, 이후 별도 배치(shipment DELIVERED 이벤트 구독)가 클레임을 COMPLETED로 자동전환한다 |

#### Request Body

```json
{ "deliveryCompany": "CJ대한통운", "trackingNo": "1111222233", "deliveredAt": "2026-07-01 11:20", "source": "CARRIER_CALLBACK" }
```

> `source`: `CARRIER_CALLBACK`(택배사 콜백 수신) 또는 `BATCH_CHECK`(배송추적 배치의 상태 조회 결과)

#### Response 200

```json
{ "code": "SUCCESS", "data": { "claimId": "clm-001", "status": "RETURN_PAYMENT_PENDING", "shipment": { "shipmentType": "RETURN", "status": "DELIVERED", "deliveredAt": "2026-07-01 11:20" } } }
```

> v6: 응답의 `status`는 `RETURN_DELIVERED`가 아니라 여전히 `RETURN_PAYMENT_PENDING`이다(claim.status는 이 API로 전환되지 않음). 배송완료 확인은 `shipment.status=DELIVERED`로만 표현되며, 클레임 완료(COMPLETED) 전환은 이 이벤트를 구독하는 별도 배치가 수행한다.

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 409 | RETURN_DELIVER_NOT_ALLOWED | 반송 배송 중(이동중) 상태에서만 배송완료 처리할 수 있습니다 | shipment(RETURN).status가 IN_TRANSIT 아님 |
| 404 | CLAIM_NOT_FOUND | 클레임을 찾을 수 없습니다 | 존재하지 않는 claimId |

---

## 40. GET /api/partner/v1/claims — 클레임 현황 (통합)

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음.

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/partner/v1/claims |
| 인증 | Partner Bearer (필수) |
| Query | `?claimType=ALL&status=ALL&from=&to=&keyword=&page=1&size=10&sort=createdAt&direction=desc` |
| 설명 | 취소/반품/교환 통합 목록. 판매자 자기 건만 반환 |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "claims": [
      { "claimId": "clm-001", "claimNo": "CLM-20260628-001", "platformOrderNo": "V260622-00008-01", "claimType": "RETURN", "productName": "호카 클리프턴 9", "customerName": "이*미", "status": "INSPECTING", "shippingFee": 6000, "shippingFeeStatus": "PAID", "createdAt": "2026-06-28" }
    ],
    "pagination": { "page": 1, "size": 10, "totalCount": 8, "totalPages": 1 }
  }
}
```

---

## 40-1. GET /api/partner/v1/claims/{claimId} — 클레임 상세 (판매자) (API-057)

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음(설계안).

> **신규 2026-10-29 — 미구현(설계안).** 화면레이아웃(DN) 판매자 클레임 상세(SCR-P-003)의 단건 조회. §18-1과 같은 단일 응답 정책이다. DN이 적었던 `/claims/{id}/shipping`·`/claims/{id}/logs`는 이 응답의 섹션으로 대체한다. 본인 판매자(vendor)의 클레임만 조회한다.

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/partner/v1/claims/{claimId} |
| 인증 | Partner Bearer (필수) |
| 호출원 | SCR-P-003 (T1 클레임상품 / T2 배송정보 / T3 변경이력) |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "claimId": "clm-001",
    "claimNo": "CLM-20260628-001",
    "claimType": "RETURN",
    "status": "INSPECTING",
    "vendorOrderNo": "V260622-00008-01",
    "createdAt": "2026-06-28 10:30",
    "reason": "사이즈가 맞지 않습니다",
    "responsibility": "CUSTOMER",
    "items": [
      { "orderItemId": "oi-001", "productName": "호카 클리프턴 9", "optionName": "오렌지 / 275", "quantity": 1, "attachments": [] }
    ],
    "shipments": [
      { "shipmentId": "shp-001", "shipmentType": "PICKUP", "carrier": "CJ대한통운", "trackingNo": "9876543210", "status": "IN_TRANSIT", "requestedAt": "2026-06-29 09:00", "failReason": null }
    ],
    "history": [
      { "targetType": "CLAIM", "fromStatus": "RECEIVED", "toStatus": "INSPECTING", "changedBy": "CS", "reason": "귀책 판정", "createdAt": "2026-06-28 14:00" }
    ]
  }
}
```

> 판매자 응답에는 환불·결제 정보(`refund`)와 고객 연락처를 포함하지 않는다.

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 404 | CLAIM_NOT_FOUND | 클레임을 찾을 수 없습니다 | 존재하지 않거나 타 판매자 클레임 |

---

## 28. GET /api/mobile/v1/my/claims — 내 클레임 목록

> **구현 현황 (2026-10-29)**: Mock — `ClaimController.getMyClaims`가 `mock/order/mobile__GET_my_claims.json`을 반환한다(DB 미연동, 쿼리 파라미터·귀책 필드 없음).

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/mobile/v1/my/claims |
| 인증 | Bearer {memberId} (필수) |
| Query | `?status=ALL&page=1&size=10&sort=createdAt&direction=desc` |
| 설명 | 본인이 접수한 클레임(취소/반품/교환) 목록을 최신순으로 반환 |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "claims": [
      {
        "claimId": "clm-001",
        "claimNo": "CLM-20260628-001",
        "claimType": "RETURN",
        "claimTypeLabel": "반품",
        "status": "RECEIVED",
        "statusLabel": "접수됨",
        "orderId": "ord-003",
        "platformOrderNo": "P260622-00008-00",
        "productName": "호카 클리프턴 9",
        "imageUrl": "https://placehold.co/80x80/f5f5f5/333?text=Clifton9",
        "optionName": "오렌지 / 275",
        "quantity": 1,
        "refundAmount": 169000,
        "reason": "사이즈가 맞지 않습니다",
        "createdAt": "2026-06-28",
        "updatedAt": "2026-06-29"
      }
    ],
    "pagination": { "page": 1, "size": 10, "totalCount": 3, "totalPages": 1 }
  }
}
```

---

## 29. GET /api/mobile/v1/my/claims/{claimId} — 내 클레임 상세

> **구현 현황 (2026-10-29)**: Mock — `ClaimController.getMyClaimDetail`이 `mock/order/mobile__GET_my_claims_{claim_id}.json`을 반환한다. Mock에는 `pickup`·`IN_PROGRESS` 등 구상태 표현이 남아 있어 아래 설계안과 다르다.

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/mobile/v1/my/claims/{claimId} |
| 인증 | Bearer {memberId} (필수) |
| 설명 | 클레임 상세 정보 (상품정보, 사유, 수거정보, 환불정보, 처리 타임라인) |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "claimId": "clm-001",
    "claimNo": "CLM-20260628-001",
    "claimType": "RETURN",
    "claimTypeLabel": "반품",
    "status": "RECEIVED",
    "statusLabel": "접수됨",
    "orderId": "ord-003",
    "platformOrderNo": "P260622-00008-00",
    "productName": "호카 클리프턴 9",
    "imageUrl": "https://...",
    "optionName": "오렌지 / 275",
    "quantity": 1,
    "amount": 169000,
    "refundAmount": 169000,
    "reason": "사이즈가 맞지 않습니다",
    "detailReason": "정사이즈보다 작게 나와서 반품으로 변경했습니다.",
    "responsibility": null,
    "responsibilityLabel": "판정 전",
    "submittedResponsibility": "CUSTOMER",
    "returnShippingFee": 6000,
    "createdAt": "2026-06-28 10:30",
    "shipment": {
      "shipmentType": "PICKUP",
      "carrier": "CJ대한통운",
      "trackingNumber": "9876543210",
      "status": "IN_TRANSIT",
      "requestedAt": "2026-06-29 09:00"
    },
    "refund": {
      "method": "신용카드 (****-1234)",
      "status": "환불 대기",
      "expectedAt": "수거 확인 후 3~5영업일"
    },
    "timeline": [
      { "at": "2026-06-28 10:30", "event": "반품 신청", "description": "고객이 반품을 접수했습니다." },
      { "at": "2026-06-28 14:00", "event": "접수 확인", "description": "CS 담당자가 접수를 확인했습니다." },
      { "at": "2026-06-29 09:00", "event": "수거 요청", "description": "CJ대한통운 수거가 요청되었습니다." }
    ]
  }
}
```

> 귀책 라벨은 "고객 귀책"/"판매자 귀책"이며, 판정 전(위 예시)에는 `responsibility`가 `null`·`responsibilityLabel`이 "판정 전"이다(판정 후 예: `"responsibility": "CUSTOMER", "responsibilityLabel": "고객 귀책"`). `submittedResponsibility`는 고객이 접수 시 신고한 값이다.
>
> v6: 기존 `pickup` 객체를 `shipment` 객체로 대체(신규 `ord_shipment` 엔티티 반영). `shipmentType`은 클레임 유형에 따라 `PICKUP`/`RETURN`/`EXCHANGE_OUT`이며, `status`는 `PENDING`/`IN_TRANSIT`/`DELIVERED`/`FAILED`/`CANCELLED` 중 하나다.

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 404 | CLAIM_NOT_FOUND | 클레임을 찾을 수 없습니다 | 존재하지 않거나 타인 클레임 |

---

## admin/partner 주문상세 탭별 Sub-API 정책

> admin 주문상세(§11 InnerTabs) 및 partner 주문상세(§13)에서 사용하는 탭별 데이터는 **단일 상세 API 응답에 모두 포함**하여 반환한다.
> 별도 sub-API 호출 없이 프론트에서 탭 전환 시 캐싱된 데이터를 표시한다.
>
> | API | 응답 포함 데이터 |
> |---|---|
> | `GET /api/admin/v1/orders/{orderId}` | `items[]`(주문상품), `payment`(결제정보), `shipping`(배송정보), `claims[]`(CS·클레임), `inquiries[]`(주문문의), `history[]`(변경이력) |
> | `GET /api/partner/v1/orders/{orderId}` | `items[]`(주문상품), `shipping`(배송정보), `claims[]`(클레임), `history[]`(변경이력) |
> | `GET /api/admin/v1/claims/{claimId}` (API-056, 신규) | `items[]`(클레임상품), `refund`(환불정보), `shipments[]`(배송정보), `history[]`(변경이력) |
> | `GET /api/partner/v1/claims/{claimId}` (API-057, 신규) | `items[]`(클레임상품), `shipments[]`(배송정보), `history[]`(변경이력) |

---

## 44. POST /api/partner/v1/shipping/{shipmentId}/reship — 배송 실패 재발송 처리

> **구현 현황 (2026-10-29)**: 미구현 — 컨트롤러 매핑 없음.

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/partner/v1/shipping/{shipmentId}/reship |
| 인증 | Partner Bearer 또는 Admin Bearer (필수) |
| 설명 | `FAILED` 상태의 shipment(`shipment_type` 공용 — OUTBOUND/PICKUP/RETURN/EXCHANGE_OUT 모두 대상)를 재발송 처리한다. 배송상태 갱신 배치(BAT-003, 60분 주기)가 `FAILED`로 전환시킨 건을 판매자 또는 CS 담당자가 새 운송장으로 재등록한다 (REQ-ORD-062). |

#### Request Body

```json
{ "carrier": "CJ대한통운", "trackingNo": "5555666677" }
```

> 필드명 주석: 이 요청의 `carrier`는 §26·§36·§39·§39-1의 요청 필드 `deliveryCompany`와 같은 택배사 값이다(설계 당시 이름이 갈라졌고 공통 규칙은 readme 필드명 규칙 참조).

#### Response 200

```json
{ "code": "SUCCESS", "data": { "shipmentId": "shp-001", "status": "IN_TRANSIT", "carrier": "CJ대한통운", "trackingNumber": "5555666677" } }
```

> 상태전이: `ord_shipment.status` `FAILED` → `PENDING`(재발송 등록 접수) → `PENDING`에 운송장 등록 시 `IN_TRANSIT`. 재발송 이후에는 §19 배치가 다시 60분 주기로 추적한다. shipment_type이 무엇이든(출고/수거/반송/교환선출고) 동일 로직이 적용된다.

#### Error Responses

| HTTP | code | message | 조건 | 대응 |
|---|---|---|---|---|
| 409 | RESHIP_NOT_ALLOWED | FAILED 상태만 재발송 가능합니다 | shipment.status ≠ FAILED | 시퀀스(DM) §22 |
| 400 | TRACKING_NO_REQUIRED | 운송장번호를 입력해주세요 | 번호 누락 | — |
| 404 | SHIPMENT_NOT_FOUND | 배송 건을 찾을 수 없습니다 | 존재하지 않는 shipmentId | — |

---

