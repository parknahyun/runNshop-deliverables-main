# 이벤트 플로우 — Payment 도메인 (발행 이벤트)

> 상위 문서: [readme.md](readme.md)
> **단계**: 구조설계 | **문서범위**: Domain 간 (Payment가 발행하는 이벤트) | **문서종류**: Design
> **갱신일**: 2026-11-03 (readme.md v5 비동기 재설계 반영 — ADR-008·009, REQ-PAY-029~031)
> Order 발행 이벤트는 [order.md](order.md) 참조. Envelope 공통 구조·이벤트 카탈로그(발행/수신 관계)·흐름 다이어그램은 [readme.md](readme.md) 참조

> **2026-11-03 비동기 재설계 — 이 문서에 없는 상태·전이**: 아래 3종(`PAYMENT_APPROVED`·`PAYMENT_FAILED`·`PAYMENT_REFUNDED`) 외에 Payment 내부에서 새로 생긴 `CONFIRMING`(결제 확인 중, 3초 무응답 후 PG 거래 조회, REQ-PAY-005·029)과 `AMOUNT_MISMATCH` 거부(REQ-PAY-007)는 **도메인 간 발행 이벤트가 아니다** — Order는 동기 응답(승인 요청 결과) 또는 상태 조회로만 결과를 안다.
> **2026-11-04 결정**: `LATE_DEPOSIT` 자동환불을 포함한 환불 완료 공백은 `PAYMENT_REFUNDED` 신설로 해소했다(readme.md §구현 현행화(2026-11-03) Human Review 항목 반영, DP-클래스설계/payment.md `PaymentEventPublisher.publishPaymentRefunded`).

---

## 이벤트 스키마 (Payment 발행)

### PAYMENT_APPROVED

```json
{
  "eventId": "evt_01HXYZ001",
  "eventType": "PAYMENT_APPROVED",
  "eventVersion": 1,
  "occurredAt": "2026-08-11T10:00:00",
  "producer": "payment-service",
  "correlationId": "cor_01HXYZ001",
  "payload": {
    "paymentId": "pay_01HXYZ001",
    "orderId": "ord_01HXYZ001",
    "platformOrderId": "pord_01HXYZ001",
    "amount": 35000,
    "paymentMethod": "CARD",
    "pgTransactionId": "toss-tx-12345",
    "approvedAt": "2026-08-11T10:00:00"
  }
}
```

> **2026-11-03**: 현재 프로토타입 범위(가상계좌)에서는 이 이벤트의 트리거가 "PG 승인 응답"이 아니라 **가상계좌 입금 통보(금액 일치)** 이다 — `paymentMethod`는 `VIRTUAL_ACCOUNT`가 된다. 위 `CARD`/Toss 승인 예시는 카드 등 인증형 수단(안, 미구현)을 위해 남겨둔 것이다. 수신측(Order)은 `DEPOSIT_PENDING`(또는 결제인증대기, 안) 상태에서만 이 이벤트를 받아 `PAYMENT_COMPLETED`로 전환한다(AC-ORD-015). 취소가 이미 확정된 주문이면 이 이벤트 대신 `LATE_DEPOSIT` 자동환불 경로(ADR-009)로 간다 — §상위 문서 참조.

### PAYMENT_FAILED

```json
{
  "eventId": "evt_01HXYZ002",
  "eventType": "PAYMENT_FAILED",
  "eventVersion": 1,
  "occurredAt": "2026-08-11T10:00:30",
  "producer": "payment-service",
  "correlationId": "cor_01HXYZ001",
  "payload": {
    "paymentId": "pay_01HXYZ001",
    "orderId": "ord_01HXYZ001",
    "platformOrderId": "pord_01HXYZ001",
    "amount": 35000,
    "failReason": "CARD_DECLINED",
    "retryCount": 3
  }
}
```

> **2026-11-03**: `retryCount`는 최초 시도를 포함한 **총 시도 횟수**(최대 3)를 의미하며, 승인 실패 응답과 3초 무응답(`CONFIRMING` 조회 미승인 확정) 두 경로의 실패가 합산된 값이다(REQ-PAY-003·004·029, ADR-008). 수신측(Order)은 `STOCK_DEDUCTED` 상태에서 이 이벤트를 받아 `PAYMENT_FAILED`로 전환하고 차감된 재고를 복원한다 — 구 상태명 `PAYMENT_PENDING`에서 전이한다고 적힌 하위 산출물(DQ 프로그램목록 등)이 있다면 이 `STOCK_DEDUCTED` 기준으로 읽는다.

### PAYMENT_REFUNDED (신규, 2026-11-04)

> **도출 배경**: `LATE_DEPOSIT` 자동환불(REQ-PAY-030, ADR-009)이 확정됐지만 환불 완료를 다른 도메인에 알리는 이벤트가 없었다(2026-11-03 Human Review 공백, readme.md §구현 현행화 참조). 이번에 신설하며, `LATE_DEPOSIT` 전용이 아니라 **Payment가 수행하는 환불 4경로(전액·부분·수동·계좌이체 자동) 전체의 완료**를 알리는 공통 이벤트로 설계했다 — `PAYMENT_APPROVED`/`PAYMENT_FAILED`와 대칭되는 "결제 트랜잭션의 세 번째 종착 상태(환불)"를 알리는 역할이다. `refundReason`은 완전 신규 값이 아니라 DP-클래스설계/payment.md에 이미 정의된 `RefundReason` enum(`ORDER_CANCELLED`/`CLAIM_COMPLETED`/`LATE_DEPOSIT`/`MANUAL`)을 그대로 쓴다.

```json
{
  "eventId": "evt_01HXYZ020",
  "eventType": "PAYMENT_REFUNDED",
  "eventVersion": 1,
  "occurredAt": "2026-11-04T09:00:00",
  "producer": "payment-service",
  "correlationId": "cor_01HXYZ001",
  "payload": {
    "paymentId": "pay_01HXYZ001",
    "orderId": "ord_01HXYZ001",
    "platformOrderId": "pord_01HXYZ001",
    "memberId": "mbr_01HXYZ001",
    "refundAmount": 152000,
    "refundStatus": "REFUNDED",
    "refundMethod": "VIRTUAL_ACCOUNT_TRANSFER",
    "refundReason": "LATE_DEPOSIT",
    "claimId": null,
    "refundedAt": "2026-11-04T09:00:00"
  }
}
```

| 필드 | 설명 |
|---|---|
| `refundAmount` | 이번 환불 요청에서 실제로 돌려준 금액(부분 환불이면 그 부분 금액) |
| `refundStatus` | `pay_payment.status` 결과 — `REFUNDED`(전액/잔여분까지 완료) 또는 `PARTIAL_REFUNDED`(부분, 추가 환불 남음) |
| `refundMethod` | `PG_CANCEL`(카드·간편결제·계좌이체 PG 부분승인취소) / `VIRTUAL_ACCOUNT_TRANSFER`(저장된 환불계좌 입금) / `BANK_TRANSFER`(CS 수동 계좌이체) |
| `refundReason` | `RefundReason` enum 그대로: `ORDER_CANCELLED`(주문취소 자동) / `CLAIM_COMPLETED`(어드민 클레임 환불 처리, API-029) / `LATE_DEPOSIT`(취소 확정 후 입금 경합 자동환불) / `MANUAL`(CS 수동 재환불) |
| `claimId` | `refundReason=CLAIM_COMPLETED`일 때만 값이 있고, 그 외(주문취소·LATE_DEPOSIT·수동)는 `null` |

> **수신 도메인(현재 미구현, `*`)**: Notification(환불완료 고객 안내 — 반품 클레임 환불은 이미 Order가 `CLAIM_REFUNDED`로 안내하므로 **이 이벤트로 중복 안내하지 않고, `refundReason=LATE_DEPOSIT`/`ORDER_CANCELLED`/`MANUAL` 건만 이 이벤트로 안내**한다), Settlement는 수신 대상이 아니다(환불은 매출로 인식된 적 없는 금액의 반환이라 정산 차감 대상이 아님, 정책서 settlement 10.4.1과 같은 원칙).
> Order는 이 이벤트로 **상태를 바꾸지 않는다** — `ORDER_CANCELLED`/클레임 환불은 이미 Order 자신의 트랜잭션에서 상태가 확정되어 있고, `LATE_DEPOSIT`은 애초에 Order 쪽 상태 변경이 없는 사례이기 때문이다(순수 알림용 이벤트).
