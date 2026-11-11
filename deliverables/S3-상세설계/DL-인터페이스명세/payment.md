# 인터페이스 명세 — Payment 도메인

> 상위 문서: [readme.md](readme.md)
> **단계**: 상세설계 (S3) | **문서범위**: Bolt (Payment) | **문서종류**: Design
> Order 관련 API는 [DL-인터페이스명세/order.md](order.md) 참조

---

## 12. GET /api/mobile/v1/my/payment-methods — 결제수단 목록

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/mobile/v1/my/payment-methods |
| 인증 | Bearer {memberId} (필수) |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": [
    { "methodId": "pm-001", "methodType": "CARD", "displayName": "****-1234", "cardCompany": "신한카드", "isDefault": true }
  ]
}
```

---

## 13. POST /api/mobile/v1/my/payment-methods — 결제수단 등록

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/mobile/v1/my/payment-methods |
| 인증 | Bearer {memberId} (필수) |
| 설명 | PG 토큰 발급 후 저장 (카드번호 서버 미저장) |

#### Request Body

```json
{ "pgBillingKey": "pg-token-abc123", "methodType": "CARD", "displayName": "****-1234", "cardCompany": "신한카드" }
```

#### Response 201

```json
{
  "code": "SUCCESS",
  "data": { "methodId": "pm-002", "displayName": "****-1234" }
}
```

---

## 14. DELETE /api/mobile/v1/my/payment-methods/{methodId} — 결제수단 삭제

| 항목 | 내용 |
|---|---|
| Method | DELETE |
| Path | /api/mobile/v1/my/payment-methods/{methodId} |
| 인증 | Bearer {memberId} (필수) |

#### Response 200

```json
{ "code": "SUCCESS", "data": null }
```

---

## 41. GET /api/mobile/v1/my/payments — 내 결제 이력 조회

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/mobile/v1/my/payments |
| 인증 | Bearer {memberId} (필수) |
| Query | `?from=&to=&page=1&size=10&sort=paidAt&direction=desc` |
| 설명 | 본인 결제 건만 최신순으로 반환 (REQ-PAY-020) |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "payments": [
      { "paymentId": "pay-001", "platformOrderNo": "P260626-00001-00", "amount": 152000, "paymentMethod": "신용카드 (****-1234)", "status": "PAID", "paidAt": "2026-06-26 09:14" }
    ],
    "pagination": { "page": 1, "size": 10, "totalCount": 3, "totalPages": 1 }
  }
}
```

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 401 | UNAUTHORIZED | 인증이 필요합니다 | 토큰 누락/만료 |

---

## 42. GET /api/admin/v1/payments/search — CS 결제 검색

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/admin/v1/payments/search |
| 인증 | Admin Bearer (필수) |
| Query | `?status=ALL&platformOrderNo=&pgTransactionNo=&from=&to=&page=1&size=10&sort=paidAt&direction=desc` |
| 설명 | 상태·기간·주문번호·PG거래번호 필터로 결제 건 검색 (REQ-PAY-021) |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "payments": [
      { "paymentId": "pay-001", "platformOrderNo": "P260626-00001-00", "customerName": "홍*동", "amount": 152000, "pgTransactionNo": "PG-20260626-99001", "status": "PAID", "paidAt": "2026-06-26 09:14" }
    ],
    "pagination": { "page": 1, "size": 10, "totalCount": 1, "totalPages": 1 }
  }
}
```

> `pgTransactionNo`는 `pay_payment_log.pg_transaction_id`에서 조인해 채운다(`pay_payment` 자체 컬럼이 아님).

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 400 | INVALID_DATE_RANGE | 조회 기간이 올바르지 않습니다 (from > to) | from > to |

---

## 43. GET /api/admin/v1/payments/{paymentId}/pg-logs — PG 거래 로그 조회

| 항목 | 내용 |
|---|---|
| Method | GET |
| Path | /api/admin/v1/payments/{paymentId}/pg-logs |
| 인증 | Admin Bearer (필수) |
| 설명 | 해당 결제 건의 PG 요청·응답 이력 조회. 응답은 마스킹된 응답 문자열 자체, 요청은 작업 이력(원문 없음). PII 마스킹 처리 (REQ-PAY-022, 2026-10-29) |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "paymentId": "pay-001",
    "logs": [
      { "at": "2026-06-26 09:14:01", "direction": "REQUEST", "pgTransactionNo": "PG-20260626-99001", "amount": 152000, "reason": "승인 요청" },
      { "at": "2026-06-26 09:14:02", "direction": "RESPONSE", "pgTransactionNo": "PG-20260626-99001", "responseCode": "0000", "rawResponse": "{\"resultCode\":\"0000\",\"approvalNo\":\"12****78\"}", "reason": "승인 성공" }
    ]
  }
}
```

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 404 | PAYMENT_NOT_FOUND | 결제 건을 찾을 수 없습니다 | 존재하지 않는 paymentId |

---

## 45. POST /api/internal/v1/payments/mask-personal-data — 결제 개인정보 마스킹 (API-060)

> **구현 현황 (2026-11-03)**: 미구현(설계안). BAT-011(탈퇴 회원 주문·결제 데이터 마스킹)·BAT-012(보존 기간 초과 마스킹)가 호출하며, WBS SC40-4(Bolt16)다. 엔드포인트는 "(안)"이다.

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/internal/v1/payments/mask-personal-data (안) |
| 인증 | 내부 호출 전용(서비스 간 인증, 외부 비공개 — 방식 미정). 고객·어드민·판매자 토큰으로는 호출할 수 없다 |
| 설명 | 호출 측(Order 배치)이 넘긴 주문들의 결제 개인정보를 마스킹한다. 대상은 `pay_payment`의 환불계좌(`refund_bank_name`·`refund_account_no`·`refund_holder_name`)와 가상계좌(`virtual_account_no`·`virtual_account_bank`), 카드 토큰(`pg_token`)이며, 탈퇴 사유일 때는 해당 회원의 등록 결제수단(`pay_payment_method`)도 포함한다. 금액·상태·일시는 유지하고 이력은 삭제하지 않는다. 같은 요청을 다시 보내도 결과가 같다(멱등). (REQ-ORD-085, 정책서 11.3.4, 2026-11-03) |

> 대상 선정(탈퇴 회원·주문 연도 기준)은 주문 정보를 가진 Order가 한다. Payment는 받은 목록만 처리하며 Order 기준을 알지 못한다. PG 로그(`raw_response`)는 저장 시점에 이미 마스킹되어 이 API의 대상이 아니다.

#### Request Body

```json
{
  "reason": "MEMBER_WITHDRAWN",
  "memberId": "mem-001",
  "orderIds": ["ord-001", "ord-002"]
}
```

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| reason | string | ✅ | `MEMBER_WITHDRAWN`(BAT-011) / `RETENTION_EXPIRED`(BAT-012) |
| memberId | string | reason=MEMBER_WITHDRAWN일 때 ✅ | 탈퇴 회원. 이 값이 있으면 `pay_payment_method`(등록 결제수단)도 마스킹한다. RETENTION_EXPIRED에서는 보내지 않는다 |
| orderIds | string[] | ✅ | 마스킹할 주문 ID. 1~500건. 호출 측이 나누어 여러 번 호출한다 |

#### Response 200

```json
{
  "code": "SUCCESS",
  "data": {
    "requestedCount": 2,
    "maskedCount": 1,
    "alreadyMaskedCount": 0,
    "skipped": [
      { "orderId": "ord-002", "reason": "PAYMENT_IN_PROGRESS" }
    ],
    "notFoundOrderIds": []
  }
}
```

| 필드 | 설명 |
|---|---|
| requestedCount | 요청한 주문 수 |
| maskedCount | 이번 호출에서 마스킹한 주문 수 |
| alreadyMaskedCount | 이미 마스킹되어 건너뛴 주문 수(멱등) |
| skipped | 마스킹하지 않은 주문과 사유. `PAYMENT_IN_PROGRESS`는 결제가 진행 중(PENDING·CONFIRMING·WAITING_DEPOSIT)이거나 환불 처리 중이라 건너뛴 경우이며, 호출 측이 다음 실행에서 다시 보낸다 |
| notFoundOrderIds | 결제 건이 없는 주문 ID(결제 전 취소 주문 등). 오류가 아니다 |

#### 마스킹 규칙 (제안)

| 컬럼 | 마스킹 결과 |
|---|---|
| `refund_account_no`, `virtual_account_no` | 마지막 4자리만 남기고 `*` |
| `refund_holder_name` | 첫 글자만 남기고 `*` |
| `refund_bank_name`, `virtual_account_bank` | 비움(NULL) |
| `pg_token`, `pay_payment_method.pg_billing_key` | 고정값 `MASKED` |
| `pay_payment_method.display_name` | 이미 `****-1234` 형식이라 유지 |

> [확인 필요: 마스킹 형식(남기는 자릿수·NULL/고정값)은 제안이다. 확정 전 보안 담당과 맞춘다.]

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 400 | INVALID_MASK_REASON | 마스킹 사유가 올바르지 않습니다 | reason이 정의된 값이 아님 |
| 400 | MEMBER_ID_REQUIRED | 탈퇴 회원 ID가 필요합니다 | reason=MEMBER_WITHDRAWN인데 memberId 없음 |
| 400 | ORDER_IDS_REQUIRED | 마스킹할 주문 ID가 필요합니다 | orderIds가 비었거나 500건 초과 |
| 401 | UNAUTHORIZED | 인증이 필요합니다 | 내부 인증 실패 |
| 403 | FORBIDDEN | 호출 권한이 없습니다 | 내부 호출 주체가 아님 |

---

## 46. POST /api/internal/v1/pg-webhooks/virtual-account/deposit — 가상계좌 입금 통보 웹훅 (API-059)

> **구현 현황 (2026-11-03)**: 미구현(설계안). 입금 확인과 취소 우선·`LATE_DEPOSIT` 자동 환불의 입구다(REQ-PAY-029·030, WBS SC18-1, DM payment §4-3). **엔드포인트는 "(안)"이며** PG 연동 사양(토스페이먼츠 가상계좌 웹훅)이 확정되면 필드명·인증 방식을 맞춘다.

| 항목 | 내용 |
|---|---|
| Method | POST |
| Path | /api/internal/v1/pg-webhooks/virtual-account/deposit (안) |
| 인증 | 사용자 토큰 없음. **PG 서명 검증**(통보에 포함된 서명 또는 secret 값 대조)과 PG 발신 IP 허용 목록으로 검증한다. 검증 실패는 처리하지 않는다 |
| 설명 | PG가 가상계좌 입금을 통보하면 금액을 대조해 결제완료로 바꾼다. 이미 취소가 확정된 주문이면 결제완료로 바꾸지 않고 입금액을 환불 대상으로 기록해 결제 시 저장된 환불계좌로 운영자 승인 없이 자동 환불한다(사유 `LATE_DEPOSIT`, 기준일 = 입금 통보 수신일, 8.1.3) |

#### Request Body (PG → 시스템)

```json
{
  "pgTransactionNo": "PG-20261103-77001",
  "virtualAccountNo": "1234567890123",
  "depositAmount": 152000,
  "depositedAt": "2026-11-03 14:20:11",
  "depositorName": "홍*동",
  "signature": "pg-provided-secret-or-signature"
}
```

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| pgTransactionNo | string | ✅ | PG 거래번호. 중복 통보를 가르는 멱등 키 |
| virtualAccountNo | string | ✅ | 입금된 가상계좌 번호 |
| depositAmount | int | ✅ | 입금액 |
| depositedAt | string | ✅ | 입금 일시 |
| depositorName | string | | 입금자명(PG 제공 시) |
| signature | string | ✅ | PG 서명 또는 secret. 방식은 PG 사양 확정 후 정함 |

> 입금 통보 본문은 로그에 남길 때 개인정보(입금자명·계좌번호)를 마스킹한다(정책서 11.3.4, PG 로그 규칙).

#### Response 200

PG가 재시도하지 않도록 정상 수신과 처리 결과를 모두 200으로 응답한다.

```json
{
  "code": "SUCCESS",
  "data": { "result": "PAID" }
}
```

| result | 의미 |
|---|---|
| `PAID` | 입금액이 결제 금액과 같아 결제완료로 바꾸고 PAYMENT_APPROVED 이벤트를 발행함 |
| `LATE_DEPOSIT_REFUND_REQUESTED` | 이미 취소된 주문이라 결제완료로 바꾸지 않고 입금액 자동 환불을 요청함(취소 우선) |
| `AMOUNT_MISMATCH_REJECTED` | 입금액이 결제 금액과 달라 입금을 거절함(PG 설정)·로그만 기록 |
| `DUPLICATE_IGNORED` | 같은 `pgTransactionNo`를 이미 처리해 무시함(멱등) |

#### Error Responses

| HTTP | code | message | 조건 |
|---|---|---|---|
| 400 | INVALID_DEPOSIT_NOTICE | 입금 통보 형식이 올바르지 않습니다 | 필수 필드 누락·형식 오류 |
| 401 | INVALID_SIGNATURE | 서명 검증에 실패했습니다 | PG 서명·secret 불일치, 허용 IP 아님 |
| 404 | PAYMENT_NOT_FOUND | 결제 건을 찾을 수 없습니다 | `virtualAccountNo`에 해당하는 결제가 없음(로그 기록 후 운영자 확인) |

> 환불 실행 중의 계좌 오류·PG 실패는 이 API의 응답이 아니라 환불 처리 규칙(8.7.2·8.8.2, BAT-010)을 따른다.

---
