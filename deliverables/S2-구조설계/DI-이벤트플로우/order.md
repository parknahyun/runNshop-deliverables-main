# 이벤트 플로우 — Order 도메인 (발행 이벤트)

> 상위 문서: [readme.md](readme.md)
> **단계**: 구조설계 | **문서범위**: Domain 간 (Order가 발행하는 이벤트) | **문서종류**: Design
> **갱신일**: 2026-11-03 (readme.md v5 비동기 재설계 반영 — ADR-007·008·009, REQ-ORD-080~086)
> Payment 발행 이벤트는 [payment.md](payment.md) 참조. Envelope 공통 구조·이벤트 카탈로그(발행/수신 관계)·흐름 다이어그램은 [readme.md](readme.md) 참조

> **2026-11-03 비동기 재설계**: 아래 스키마 중 `ORDER_CANCELLED`·`CLAIM_RECEIVED`·`CLAIM_REFUNDED`·`CLAIM_COMPLETED`는 비동기 재설계(ADR-007·009) 이후 새로 생기는 사례(취소 클레임 `claim_type=CANCEL`, 구매확정 후 어드민 대리 접수, 교환 종료)에도 **같은 스키마를 그대로 사용**한다(신규 이벤트를 만들지 않음 — readme.md §구현 현행화(2026-11-03) 참조). `STOCK_REQUESTED`→`STOCK_DEDUCTED`→`DEPOSIT_PENDING` 구간의 아웃박스 이벤트(`STOCK_DEDUCT_REQUESTED`/`PAYMENT_REQUESTED`)는 Order 내부 처리용이라 이 문서(도메인 간 발행 이벤트)의 스키마 대상이 아니다.

---

## 이벤트 스키마 (Order 발행)

### ORDER_CANCELLED

```json
{
  "eventId": "evt_01HXYZ003",
  "eventType": "ORDER_CANCELLED",
  "eventVersion": 1,
  "occurredAt": "2026-08-11T11:00:00",
  "producer": "order-service",
  "correlationId": "cor_01HXYZ001",
  "payload": {
    "orderId": "ord_01HXYZ001",
    "platformOrderId": "pord_01HXYZ001",
    "memberId": "mbr_01HXYZ001",
    "vendorId": "vnd_01HXYZ001",
    "cancelReason": "CUSTOMER_REQUEST",
    "totalAmount": 35000,
    "items": [
      { "productId": "prod_01HXYZ001", "skuId": "sku_01HXYZ001", "quantity": 2 }
    ]
  }
}
```

> **2026-11-03**: `DEPOSIT_PENDING` 상태의 입금대기 취소(REQ-ORD-080)·`PAYMENT_COMPLETED` 상태의 고객 즉시취소·CS 예외취소(REQ-ORD-017)가 모두 이 이벤트를 발행한다. 세 경우 모두 같은 트랜잭션에서 `claim_type=CANCEL` 취소 클레임이 생성되며(REQ-ORD-082), 그 접수·완료는 아래 `CLAIM_RECEIVED`/`CLAIM_REFUNDED`/`CLAIM_COMPLETED`로 뒤따라 발행된다. 입금대기 취소는 환불이 없으므로 `cancelReason`은 같지만 Payment 쪽 환불 요청은 발생하지 않는다(가상계좌 폐기만).

### ORDER_CONFIRMED

```json
{
  "eventId": "evt_01HXYZ004",
  "eventType": "ORDER_CONFIRMED",
  "eventVersion": 1,
  "occurredAt": "2026-08-18T00:00:00",
  "producer": "order-service",
  "correlationId": "cor_01HXYZ001",
  "payload": {
    "orderId": "ord_01HXYZ001",
    "platformOrderId": "pord_01HXYZ001",
    "memberId": "mbr_01HXYZ001",
    "vendorId": "vnd_01HXYZ001",
    "totalAmount": 35000,
    "confirmedAt": "2026-08-18T00:00:00",
    "items": [
      { "productId": "prod_01HXYZ001", "skuId": "sku_01HXYZ001", "quantity": 2, "amount": 35000 }
    ]
  }
}
```

### CLAIM_COMPLETED

```json
{
  "eventId": "evt_01HXYZ005",
  "eventType": "CLAIM_COMPLETED",
  "eventVersion": 1,
  "occurredAt": "2026-08-20T15:00:00",
  "producer": "order-service",
  "correlationId": "cor_01HXYZ002",
  "payload": {
    "claimId": "clm_01HXYZ001",
    "orderId": "ord_01HXYZ001",
    "claimType": "RETURN",
    "refundAmount": 17500,
    "afterPurchaseConfirm": true,
    "items": [
      { "productId": "prod_01HXYZ001", "skuId": "sku_01HXYZ001", "quantity": 1 }
    ]
  }
}
```

> `afterPurchaseConfirm`(제안): 구매확정 후 접수된 클레임이면 `true`. Settlement는 `claimType`과 이 값으로 차감 대상(구매확정 후 클레임, 교환 제외)을 판정한다(정책서 settlement 10.4.1, 2026-11-03).

### ORDER_PAID

```json
{
  "eventId": "evt_01HXYZ010",
  "eventType": "ORDER_PAID",
  "eventVersion": 1,
  "occurredAt": "2026-08-11T10:00:00",
  "producer": "order-service",
  "correlationId": "cor_01HXYZ001",
  "payload": {
    "orderId": "ord_01HXYZ001",
    "platformOrderId": "pord_01HXYZ001",
    "memberId": "mbr_01HXYZ001",
    "vendorId": "vnd_01HXYZ001",
    "totalAmount": 418000,
    "paymentMethod": "CARD",
    "paidAt": "2026-08-11T10:00:00",
    "items": [
      { "productId": "prod_01HXYZ001", "skuId": "sku_01HXYZ001", "quantity": 1, "amount": 152000 }
    ]
  }
}
```

### STOCK_FAILED

```json
{
  "eventId": "evt_01HXYZ011",
  "eventType": "STOCK_FAILED",
  "eventVersion": 1,
  "occurredAt": "2026-08-11T10:00:05",
  "producer": "order-service",
  "correlationId": "cor_01HXYZ001",
  "payload": {
    "orderId": "ord_01HXYZ001",
    "platformOrderId": "pord_01HXYZ001",
    "memberId": "mbr_01HXYZ001",
    "failedItems": [
      { "productId": "prod_01HXYZ001", "skuId": "sku_01HXYZ001", "requestedQuantity": 2, "availableStock": 0 }
    ]
  }
}
```

### SHIPPING_STARTED

```json
{
  "eventId": "evt_01HXYZ012",
  "eventType": "SHIPPING_STARTED",
  "eventVersion": 1,
  "occurredAt": "2026-08-12T10:00:00",
  "producer": "order-service",
  "correlationId": "cor_01HXYZ001",
  "payload": {
    "orderId": "ord_01HXYZ001",
    "platformOrderId": "pord_01HXYZ001",
    "memberId": "mbr_01HXYZ001",
    "vendorId": "vnd_01HXYZ001",
    "carrier": "CJ대한통운",
    "trackingNo": "1234567890",
    "shippedAt": "2026-08-12T10:00:00"
  }
}
```

### SHIPMENT_DELIVERED

> v4 (2026-08-24): `DELIVERY_COMPLETED`에서 이름 변경. `ord_shipment`(v6) 도입 이후 실제 트리거는 shipment 상태 전이이므로 `shipmentId`·`shipmentType`·`refType`/`refId`를 추가했다.

```json
{
  "eventId": "evt_01HXYZ013",
  "eventType": "SHIPMENT_DELIVERED",
  "eventVersion": 1,
  "occurredAt": "2026-08-14T14:00:00",
  "producer": "order-service",
  "correlationId": "cor_01HXYZ001",
  "payload": {
    "shipmentId": "shp_01HXYZ001",
    "shipmentType": "OUTBOUND",
    "refType": "ORDER",
    "refId": "ord_01HXYZ001",
    "platformOrderId": "pord_01HXYZ001",
    "memberId": "mbr_01HXYZ001",
    "vendorId": "vnd_01HXYZ001",
    "deliveredAt": "2026-08-14T14:00:00"
  }
}
```

### CLAIM_PAYMENT_EXPIRED

```json
{
  "eventId": "evt_01HXYZ018",
  "eventType": "CLAIM_PAYMENT_EXPIRED",
  "eventVersion": 1,
  "occurredAt": "2026-08-21T09:00:00",
  "producer": "order-service",
  "correlationId": "cor_01HXYZ002",
  "payload": {
    "claimId": "clm_01HXYZ001",
    "memberId": "mbr_01HXYZ001",
    "paymentType": "PICKUP",
    "amount": 5000,
    "expiredAt": "2026-08-21T09:00:00"
  }
}
```

### CLAIM_RECEIVED

```json
{
  "eventId": "evt_01HXYZ014",
  "eventType": "CLAIM_RECEIVED",
  "eventVersion": 1,
  "occurredAt": "2026-08-15T10:30:00",
  "producer": "order-service",
  "correlationId": "cor_01HXYZ002",
  "payload": {
    "claimId": "clm_01HXYZ001",
    "orderId": "ord_01HXYZ001",
    "memberId": "mbr_01HXYZ001",
    "claimType": "RETURN",
    "reason": "사이즈가 맞지 않습니다",
    "responsibility": "CUSTOMER",
    "items": [
      { "productId": "prod_01HXYZ001", "skuId": "sku_01HXYZ001", "quantity": 1 }
    ]
  }
}
```

> **2026-11-03**: `claimType`은 `RETURN`/`EXCHANGE` 외에 **`CANCEL`**(주문 취소와 같은 트랜잭션에서 생성, REQ-ORD-082)도 값으로 가진다. `CANCEL`일 때는 `reason`에 취소 사유, `responsibility`는 비워 둔다(귀책 판정이 없음). 구매확정(CONFIRMED) 후 하자·오배송 건을 CS가 어드민에서 대리 접수할 때(REQ-ORD-081)도 같은 스키마를 쓰되 `channel=CS`가 추가된다(아래 예시의 `channel` 필드는 생략돼 있었으나 실제로는 `SELF`/`CS` 중 하나를 포함한다).

### CLAIM_SHIPPING_PAID

```json
{
  "eventId": "evt_01HXYZ015",
  "eventType": "CLAIM_SHIPPING_PAID",
  "eventVersion": 1,
  "occurredAt": "2026-08-15T11:00:00",
  "producer": "order-service",
  "correlationId": "cor_01HXYZ002",
  "payload": {
    "claimId": "clm_01HXYZ001",
    "memberId": "mbr_01HXYZ001",
    "paymentType": "PICKUP",
    "amount": 5000,
    "couponApplied": false,
    "paidAt": "2026-08-15T11:00:00"
  }
}
```

### CLAIM_RETURN_SHIPPING_PAID

```json
{
  "eventId": "evt_01HXYZ016",
  "eventType": "CLAIM_RETURN_SHIPPING_PAID",
  "eventVersion": 1,
  "occurredAt": "2026-08-20T09:00:00",
  "producer": "order-service",
  "correlationId": "cor_01HXYZ002",
  "payload": {
    "claimId": "clm_01HXYZ001",
    "memberId": "mbr_01HXYZ001",
    "paymentType": "RETURN",
    "amount": 5000,
    "couponApplied": false,
    "paidAt": "2026-08-20T09:00:00"
  }
}
```

### CLAIM_REFUNDED

```json
{
  "eventId": "evt_01HXYZ017",
  "eventType": "CLAIM_REFUNDED",
  "eventVersion": 1,
  "occurredAt": "2026-08-18T15:00:00",
  "producer": "order-service",
  "correlationId": "cor_01HXYZ002",
  "payload": {
    "claimId": "clm_01HXYZ001",
    "orderId": "ord_01HXYZ001",
    "memberId": "mbr_01HXYZ001",
    "refundAmount": 169000,
    "refundMethod": "CARD",
    "refundedAt": "2026-08-18T15:00:00"
  }
}
```

> **2026-11-03**: 반품 클레임 환불(어드민 [환불 처리] API-029 트리거) 외에, **결제완료 상태의 취소 클레임**(`claim_type=CANCEL`, RECEIVED→REFUNDED→COMPLETED) 환불 완료도 이 이벤트를 쓴다 — 이때 `refundMethod`는 원결제수단(가상계좌면 저장된 환불계좌 입금)이다. 입금대기 취소(환불 없음, RECEIVED→COMPLETED 직행)는 환불이 없으므로 이 이벤트를 발행하지 않는다.
