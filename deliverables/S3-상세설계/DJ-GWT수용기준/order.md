# GWT 수용기준 — Order 도메인

> 상위 문서: [readme.md](readme.md)
> **단계**: 상세설계 (S3) | **문서범위**: Bolt (Order) | **문서종류**: Spec
> Payment 관련 시나리오는 [payment.md](payment.md) 참조

---

## ID 규칙

```
AC-{DOMAIN}-{SEQ}
```
- AC: Acceptance Criteria
- DOMAIN: ORD(주문) / PAY(결제)
- SEQ: 3자리 순번

---

## 1. 장바구니 Bolt

| ID | 카테고리 | 대응 EARS | Given | When | Then |
|---|---|---|---|---|---|
| AC-ORD-001 | 정상 | REQ-ORD-001 | 고객이 로그인 상태이고, 상품A(SKU-001)가 판매중이다 | 고객이 상품A를 장바구니에 담는다 | 장바구니에 상품A·SKU-001·수량1이 저장된다 |
| AC-ORD-002 | 정상 | REQ-ORD-002 | 장바구니에 상품A·수량2가 있다 | 고객이 수량을 5로 변경한다 | 수량이 5로 갱신되고 소계가 재계산된다 |
| AC-ORD-003 | 정상 | REQ-ORD-003 | 장바구니에 상품A가 있다 | 고객이 상품A를 삭제한다 | 해당 항목이 is_deleted=true로 논리 삭제된다 |
| AC-ORD-004 | 경계값 | REQ-ORD-004 | 장바구니에 상품이 49개 있다 | 고객이 50번째 상품을 담는다 | 정상 추가된다 (최대 50개 허용) |
| AC-ORD-005 | 예외 | REQ-ORD-004 | 장바구니에 상품이 50개 있다 | 고객이 51번째 상품을 담는다 | "장바구니가 가득 찼습니다" 메시지 반환, 추가 거부 |
| AC-ORD-006 | 정상 | REQ-ORD-005 | 장바구니에 상품A(SKU-001)·수량2가 있다 | 고객이 같은 상품A(SKU-001)를 수량3으로 담는다 | 수량이 5로 합산된다 (중복 라인 미생성) |
| AC-ORD-007 | 정상 | REQ-ORD-006 | 비회원 장바구니에 상품A·수량3이 있고, 회원 장바구니에 상품A·수량5가 있다 | 비회원이 로그인한다 | 상품A 수량이 8로 합산 병합된다 |
| AC-ORD-008 | 예외 | REQ-ORD-001, REQ-ORD-063 | 상품B가 품절(SOLD_OUT) 상태이다 | 고객이 상품B를 장바구니에 담으려 한다 | "현재 구매할 수 없는 상품입니다" 반환, 추가 거부 |
| AC-ORD-065 | 경계값 | REQ-ORD-064 | 장바구니 상품 수량이 1이다 | 고객이 수량을 0으로 변경한다 | 변경이 거부된다, "수량은 1~99 사이로 입력해주세요" 반환 (1 유지) |
| AC-ORD-066 | 경계값 | REQ-ORD-064 | 장바구니 상품 수량이 99이다 | 고객이 수량을 100으로 변경한다 | 변경이 거부된다, 유효 범위 안내 (99 유지) |

---

## 2. 주문 생성·결제 요청 Bolt

> **비동기 접수 기준 (2026-10-29 현행화)**: 결제하기는 접수만 동기로 처리한다(TEMP→STOCK_REQUESTED + 아웃박스 적재). 재고차감(STOCK_DEDUCTED)과 PG 요청(DEPOSIT_PENDING)은 컨슈머가 비동기로 처리한다(DM §4, §4-1 · DH 구현 현행화). 구상태 `ORDER_RECEIVED`/`PAYMENT_PENDING`과 동기 재고 선점은 폐기했다.

| ID | 카테고리 | 대응 EARS | Given | When | Then |
|---|---|---|---|---|---|
| AC-ORD-009 | 정상 | REQ-ORD-008, REQ-ORD-012 | 고객이 선택한 상품 2개의 주문서(임시주문, TEMP)에서 배송지·결제수단(가상계좌)을 선택하고 필수 약관에 동의했다. 가상계좌이므로 환불계좌(은행·계좌번호·예금주, 예금주=주문자 본인·실명 확인)도 함께 입력했다(REQ-PAY-031, AC-PAY-036·037 — 미구현. 카드·간편결제는 환불계좌 불필요) | 고객이 [결제하기]를 누른다 | 저장된 임시주문을 재검증해 확정하고 플랫폼주문·판매자 주문·상품 상태가 TEMP→STOCK_REQUESTED로 전이, 재고차감 요청이 아웃박스(`STOCK_DEDUCT_REQUESTED`)에 같은 트랜잭션으로 적재되며 상태이력이 남는다. 응답 status=STOCK_REQUESTED("재고 확인 후 결제가 진행됩니다") — 재고차감·PG 요청은 비동기 |
| AC-ORD-010 | 정상 | REQ-ORD-009 | 주문서에서 쿠폰 5,000원, 포인트 3,000원을 적용해 서버에 저장했다(`PUT .../sheet/{id}/discount`) | 고객이 [결제하기]를 누른다 | 저장된 쿠폰·포인트를 결제 시점에 다시 검증하고(요청 바디 값은 무시), 쿠폰 할인내역(`ord_platform_order_discount`)·포인트가 주문에 확정 저장된다. 주문금액 = 상품금액 − 5,000원, 결제금액 = 주문금액 − 3,000원 |
| AC-ORD-011 | 정상 | REQ-ORD-011 | 장바구니에서 판매자A 상품 2개, 판매자B 상품 1개를 선택했다 | 고객이 [선택상품 주문하기]로 주문서를 생성한다 | 1개 platform_order(TEMP) + 2개 ord_order(판매자별, TEMP)로 분할 생성된다(주문서 생성 시점에 분할) |
| AC-ORD-012 | 예외 | REQ-ORD-010 | 고객이 배송지를 선택하지 않았다(주문서에서 직접 입력은 불가, 등록된 배송지에서 선택) | 고객이 [결제하기]를 누른다 | 400 `ADDRESS_REQUIRED` "배송지를 선택해주세요" 반환, 주문 상태는 TEMP 유지(접수 거부) |
| AC-ORD-013 | 정상 | REQ-ORD-078 | 주문이 STOCK_REQUESTED 상태이고 아웃박스에 `STOCK_DEDUCT_REQUESTED`가 적재되어 있다 | 컨슈머가 이벤트를 처리한다(내부 API 경유) | Catalog 재고를 SKU 단위로 차감하고(멱등), 전 SKU 성공 시 주문 상태→STOCK_DEDUCTED + 이력 기록, 아웃박스에 `PAYMENT_REQUESTED` 적재 (재고는 접수 응답 후 비동기로 차감) |
| AC-ORD-014 | 정상 | REQ-ORD-007 | 고객이 상품상세에서 "바로구매"를 선택했다 | 바로구매 주문서를 제출한다 | 장바구니 미경유, 즉시 주문 생성 |
| AC-ORD-086 | 정상 | REQ-ORD-077 | 주문이 STOCK_DEDUCTED 상태이고 아웃박스에 `PAYMENT_REQUESTED`가 적재되어 있다 | 컨슈머가 이벤트를 처리한다 | `PaymentApi.requestPayment`로 가상계좌를 발급(Mock PG)하고 주문 상태→DEPOSIT_PENDING + 이력 기록. 포인트 사용분은 같은 결제묶음의 POINT 행으로 저장된다 *(신규 2026-10-29, 현행 구현 반영)* |
| AC-ORD-087 | 예외 | REQ-ORD-079 | 주문한 SKU 중 일부만 재고가 부족하다 | 컨슈머가 재고 차감을 처리한다 | 성공한 SKU의 차감은 유지하고 실패한 SKU만 백오프 후 재시도한다. 주문 상태는 STOCK_REQUESTED로 유지된다 *(신규)* |
| AC-ORD-088 | 경계값 | REQ-ORD-079 | 재고 부족 SKU가 3회 재시도 후에도 차감되지 않았다 | 재시도가 소진되어 give-up이 호출된다 | 성공 SKU의 차감분을 복원(`restoreStock`)하고 주문 상태→STOCK_FAILED, 이벤트는 FAILED로 종결된다 *(신규, 재고부족 고객 알림은 미구현)* |
| AC-ORD-089 | 정상 | REQ-ORD-078 | 같은 재고차감 이벤트가 중복 처리된다(컨슈머 재시도·다중 인스턴스) | 내부 API가 다시 호출된다 | 이미 처리된 주문은 현재 상태를 결과로 반환하고 재고는 이중 차감되지 않는다(SKU 단위 멱등) *(신규)* |
| AC-ORD-090 | 예외 | REQ-ORD-008 | 이미 결제가 진행된 주문서(TEMP가 아님)이거나 타인의 주문서이거나 존재하지 않는 주문서이다 | 고객이 [결제하기]를 누른다 | 422 `ORDER_SHEET_ALREADY_PROCESSED` / 403 `ORDER_SHEET_FORBIDDEN` / 404 `ORDER_SHEET_NOT_FOUND` 반환, 주문 변화 없음 *(신규)* |
| AC-ORD-115 | 정상 | — | 임시주문(TEMP)이 생성 후 30분 동안 결제하기가 진행되지 않았다 | 임시주문 정리 배치가 실행된다 | 해당 주문은 CANCELLED로 정리된다(TTL 30분, DQ BAT-005) *(신규 2026-10-29, 미구현)* |

---

## 3. 결제 완료 처리 Bolt

> (Payment 도메인 관련 나머지 항목은 [payment.md](payment.md) 참조)

| ID | 카테고리 | 대응 EARS | Given | When | Then |
|---|---|---|---|---|---|
| AC-ORD-015 | 정상 | REQ-ORD-013 | 주문이 입금대기(DEPOSIT_PENDING, 가상계좌) 상태이다 — 인증형 수단(카드 등)은 결제 인증 대기 상태(안, DH 구현 현행화) | 입금 통보 또는 PAYMENT_APPROVED 이벤트를 수신한다 | 주문 상태가 PAYMENT_COMPLETED로 전환된다 *(현행 상태명 반영 2026-10-29 — 입금 통보 처리는 미구현, Bolt8 SC18-1)* |

---

## 4. 결제 실패 처리 Bolt

> (Payment 도메인 관련 나머지 항목은 [payment.md](payment.md) 참조)

| ID | 카테고리 | 대응 EARS | Given | When | Then |
|---|---|---|---|---|---|
| AC-ORD-016 | 정상 | REQ-ORD-014 | 주문이 입금대기(DEPOSIT_PENDING) 또는 결제 인증 대기 상태이다 | PAYMENT_FAILED 이벤트를 수신하거나 입금기한(12시간)이 만료된다 | 재고 복원, 주문 상태→PAYMENT_FAILED(결제 실패) / CANCELLED(입금기한 만료) *(현행 상태명 반영 2026-10-29 — 실패·만료 보상은 미구현, Bolt14 SC10-1·SC28-3)* |

---

## 5. 고객 취소 Bolt

| ID | 카테고리 | 대응 EARS | Given | When | Then |
|---|---|---|---|---|---|
| AC-ORD-017 | 정상 | REQ-ORD-018 | 주문이 PAYMENT_COMPLETED 상태이다 | 고객이 취소를 요청한다 | 주문 상태→CANCELLED, ORDER_CANCELLED 이벤트 발행 (환불·재고복원) |
| AC-ORD-091 | 정상 | REQ-ORD-018, REQ-ORD-080 | 주문이 DEPOSIT_PENDING(입금대기) 상태이고 입금 전이다 | 고객이 취소를 요청한다 | 주문 상태→CANCELLED, 발급 가상계좌 폐기, 재고 복원, 환불 요청은 발행하지 않는다(미구현) |
| AC-ORD-092 | 경계값 | REQ-ORD-080, REQ-PAY-030 | 주문이 DEPOSIT_PENDING 상태이고 고객 취소와 가상계좌 입금 통보가 동시에 도착한다 | 두 요청이 처리된다 | 취소가 우선하여 주문 상태→CANCELLED가 유지되고 결제완료로 전환되지 않으며, 입금 통보는 PAID로 반영하지 않고 입금액을 저장된 환불계좌로 운영자 승인 없이 자동 환불한다(사유 LATE_DEPOSIT, 기준일=입금 통보 수신일, 기한 3영업일 — AC-PAY-035) *(신규 2026-10-29, 미구현)* |
| AC-ORD-018 | 예외 | REQ-ORD-019 | 주문이 PREPARING 상태이고 송장이 등록되지 않았다 | 고객이 취소를 요청한다 | 직접 취소를 거부하고 "출고 준비 중에는 직접 취소할 수 없습니다. 고객센터로 문의해주세요" 반환 |
| AC-ORD-019 | 예외 | REQ-ORD-019 | 주문이 PREPARING 상태이고 shipment(OUTBOUND)가 IN_TRANSIT 상태이다 (배송 중) | 고객이 취소를 요청한다 | "배송 중에는 취소할 수 없습니다. 배송완료 후 반품을 이용해주세요" 반환 |
| AC-ORD-020 | 정상 | REQ-ORD-017 | 주문이 PREPARING 상태이고 출고 shipment(OUTBOUND)가 PENDING(송장 미등록)이다 (CS 예외 취소) | CS 담당자가 예외 취소를 요청한다 | 주문 상태→CANCELLED, 출고 shipment CANCELLED, 환불 요청 발행 |
| AC-ORD-093 | 예외 | REQ-ORD-017 | 주문이 PREPARING이지만 출고 shipment(OUTBOUND)가 IN_TRANSIT(송장 등록 후)이다 | CS 담당자가 예외 취소를 요청한다 | 409 `CANCEL_NOT_ALLOWED` — "송장이 등록되어 취소할 수 없습니다. 배송완료 후 반품을 이용해주세요" 반환, 주문 상태는 유지된다 *(신규 2026-10-29)* |
| AC-ORD-094 | 경계값 | REQ-ORD-017 | CS 예외 취소와 판매자 송장 등록이 동시에 도착한다 | 두 요청이 처리된다 | 먼저 커밋된 쪽을 따른다(정책 5.8.3). 송장이 먼저면 취소는 AC-ORD-093처럼 거부되고, 취소가 먼저면 송장 등록이 거부된다 *(신규 2026-10-29)* |

---

## 6. 출고·배송 Bolt

| ID | 카테고리 | 대응 EARS | Given | When | Then |
|---|---|---|---|---|---|
| AC-ORD-021 | 정상 | REQ-ORD-022 | 주문이 PAYMENT_COMPLETED 상태이다 | 판매자가 출고 처리를 요청한다 | 주문 상태→PREPARING |
| AC-ORD-022 | 정상 | REQ-ORD-023 | 주문이 PREPARING 상태이다 | 판매자가 운송장 번호를 등록한다 | shipment(OUTBOUND) 생성, 상태→IN_TRANSIT (주문 상태는 PREPARING 유지) |
| AC-ORD-104 | 정상 | REQ-ORD-059 | shipment(PICKUP/RETURN/EXCHANGE_OUT 포함 임의 유형)가 PENDING 상태이다 | 판매자가 운송장을 등록한다 | 해당 shipment 상태가 PENDING→IN_TRANSIT으로 전환된다 *(신규 2026-10-29)* |
| AC-ORD-023 | 정상 | REQ-ORD-024 | shipment(OUTBOUND)가 IN_TRANSIT 상태이다 | 택배사 API로부터 배송완료 신호를 수신한다 | shipment(OUTBOUND) 상태→DELIVERED, 이를 구독하여 주문 상태→DELIVERED로 파생 전환된다 |
| AC-ORD-105 | 정상 | REQ-ORD-027 | shipment(OUTBOUND)가 IN_TRANSIT 상태이다 | 배송상태 갱신 시각(60분 주기)이 도래한다 | 시스템이 택배사 API에 배송 상태를 조회한다(DQ BAT-003) *(신규 2026-10-29)* |
| AC-ORD-106 | 정상 | REQ-ORD-060 | shipment가 IN_TRANSIT 상태이다 | 택배사 API가 배송완료를 확인한다 | shipment 상태가 DELIVERED로 전환된다(유형별 파생 전환은 AC-ORD-023·057·058) *(신규 2026-10-29)* |
| AC-ORD-107 | 예외 | REQ-ORD-061 | shipment가 IN_TRANSIT 상태이다 | 택배사 API가 배송실패·반송 신호를 보낸다 | shipment 상태가 FAILED로 전환되고 CS 담당자에게 알림이 발송된다(재발송은 AC-ORD-076) *(신규 2026-10-29)* |
| AC-ORD-024 | 정상 | REQ-ORD-025 | 주문이 DEPOSIT_PENDING(입금대기) 또는 PAYMENT_COMPLETED(결제완료) 상태이다(출고 지시 전) | 고객이 배송지 변경을 요청한다 | 배송지 정보가 갱신된다 |
| AC-ORD-025 | 예외 | REQ-ORD-026 | 주문이 PREPARING 상태이다 | 고객이 배송지 변경을 요청한다 | "출고 후에는 변경할 수 없습니다" 반환 |

---

## 7. 구매확정 Bolt

| ID | 카테고리 | 대응 EARS | Given | When | Then |
|---|---|---|---|---|---|
| AC-ORD-026 | 정상 | REQ-ORD-015 | 주문이 DELIVERED 상태이고 11일이 경과했다 | 자동 구매확정 배치가 실행된다 | 주문 상태→CONFIRMED, 정산 등록 + 포인트 적립 이벤트 발행 |
| AC-ORD-027 | 정상 | REQ-ORD-016 | 주문이 DELIVERED 상태이고 3일 경과했다 | 고객이 수동 구매확정을 요청한다 | 주문 상태→CONFIRMED (11일 미경과도 가능) |
| AC-ORD-028 | 경계값 | REQ-ORD-015 | 주문이 DELIVERED 상태이고 배송완료 일시 + 11×24시간(264시간)이 지났다 | 다음 새벽 배치(02:00, DQ BAT-001)가 실행된다 | 자동 구매확정 처리됨. 10일째에 반품·교환을 접수한 건(AC-ORD-031)은 자동 구매확정에서 제외된다 |
| AC-ORD-102 | 정상 | REQ-ORD-020 | 주문이 CONFIRMED로 전환되었다(수동 또는 자동) | 구매확정이 처리된다 | Settlement 도메인에 정산 대상 등록 이벤트(`ORDER_CONFIRMED`)가 발행된다 *(신규 2026-10-29)* |
| AC-ORD-103 | 정상 | REQ-ORD-021 | 주문이 CONFIRMED로 전환되었다 | 구매확정이 처리된다 | Member 도메인에 포인트 적립 이벤트가 발행된다 *(신규 2026-10-29)* |
| AC-ORD-110 | 예외 | REQ-ORD-015 | 배송완료 후 11일이 지난 주문이나 반품·교환 클레임이 진행 중이다(RECEIVED~COMPLETED 전 단계, 정책 5.6.2) | 자동 구매확정 배치가 실행된다 | 해당 주문은 대상에서 제외되고 CONFIRMED로 전환되지 않는다. 클레임이 반려·취소로 종료되면 다음 배치에서 대상이 된다 *(신규 2026-10-29)* |
| AC-ORD-111 | 예외 | REQ-ORD-015 | 자동 구매확정 처리 중 일부 건이 실패했다(정책 5.6.3) | 배치가 실패 건을 재처리한다 | 실패 건은 다음 실행에서 다시 시도하고, 같은 건이 3회 연속 실패하면 운영자에게 알림을 발송한다 *(신규 2026-10-29, 미구현)* |

---

## 8. 클레임(반품·교환) Bolt

| ID | 카테고리 | 대응 EARS | Given | When | Then |
|---|---|---|---|---|---|
| AC-ORD-029 | 정상 | REQ-ORD-028 | 주문이 DELIVERED 상태, 배송완료 후 5일 경과 | 고객이 반품을 신청한다 | 클레임이 RECEIVED 상태(RETURN 유형)로 생성된다 |
| AC-ORD-030 | 정상 | REQ-ORD-029 | 주문이 DELIVERED 상태, 배송완료 후 3일 경과 | 고객이 교환을 신청한다 | 클레임이 RECEIVED 상태(EXCHANGE 유형)로 생성된다 |
| AC-ORD-072 | 예외 | REQ-ORD-070 | 원 주문 상품이 상품A(productId=P001)이다 | 고객이 교환 신청 시 exchangeSkuId를 다른 상품(productId=P002)의 SKU로 지정한다 | 신청이 거부된다 ("교환은 동일 상품 내 옵션 변경만 가능합니다") |
| AC-ORD-095 | 정상 | REQ-ORD-081 | 주문상품이 CONFIRMED이고 하자·오배송(VENDOR 귀책) 사유이며 배송완료 후 3개월 이내이다 | CS 담당자가 어드민에서 사진 1장 이상을 첨부해 클레임을 접수한다 | 클레임이 RECEIVED로 접수되고 주문상품은 CONFIRMED를 유지한다. 정산 차감·포인트 회수는 클레임 완료 시 처리 *(신규 2026-10-29, 미구현)* |
| AC-ORD-096 | 예외 | REQ-ORD-081 | 주문상품이 CONFIRMED이다 | 고객이 모바일에서 반품·교환을 신청한다(사유 무관) | "구매확정 후에는 고객센터로 문의해주세요"로 거부한다 *(신규 2026-10-29, 미구현)* |
| AC-ORD-097 | 예외 | REQ-ORD-081 | 주문상품이 CONFIRMED이고 단순변심 사유이다 | CS 담당자가 어드민에서 접수를 시도한다 | 접수를 거부한다(구매확정 후 단순변심은 접수하지 않음). 하자·오배송이 3개월·30일을 모두 넘긴 기한 후 하자도 같은 어드민 경로이며 운영자 승인(7.2.3)이 필요하다 *(신규 2026-10-29)* |
| AC-ORD-098 | 정상 | REQ-ORD-082, REQ-ORD-080 | 주문이 DEPOSIT_PENDING(입금대기) 상태이다 | 고객이 직접 취소한다 | 주문이 CANCELLED가 되고 같은 트랜잭션에서 claim_type=CANCEL 클레임(channel=SELF)이 생성되어 환불 없이 COMPLETED가 된다 *(신규 2026-10-29, 미구현)* |
| AC-ORD-099 | 정상 | REQ-ORD-082 | 주문이 PAYMENT_COMPLETED 상태이다 | 고객이 직접 취소한다 | 주문 CANCELLED + claim_type=CANCEL 클레임이 RECEIVED로 생성되고, 환불 요청 후 REFUNDED→COMPLETED로 종료된다 *(신규 2026-10-29, 미구현)* |
| AC-ORD-100 | 정상 | REQ-ORD-082, REQ-ORD-017 | 주문이 PREPARING이고 출고 shipment가 PENDING이다 | CS 담당자가 예외 취소한다 | 주문 CANCELLED + claim_type=CANCEL 클레임(channel=CS)이 생성되고 환불 후 COMPLETED로 종료된다 *(신규 2026-10-29, 미구현)* |
| AC-ORD-031 | 경계값 | REQ-ORD-030 | 배송완료 일시 + 정확히 10×24시간(240시간) 경과 | 고객이 반품을 신청한다 | 정상 접수 (10일 이내 허용) |
| AC-ORD-112 | 경계값 | REQ-ORD-030, REQ-ORD-081 | 하자·오배송(VENDOR 귀책) 사유이고 배송완료 후 11일이 지났으나 구매확정 전이며 3개월·안 날부터 30일 이내이다 | 고객이 반품·교환을 신청한다 | 사진 1장 이상 첨부 조건으로 정상 접수된다(7.2.2 사유별 기한). 3개월 또는 안 날부터 30일을 넘기면 "기한이 초과되었습니다"로 거부하고 고객센터 문의를 안내한다 *(신규 2026-10-29)* |
| AC-ORD-032 | 예외 | REQ-ORD-030 | 배송완료 일시 + 11×24시간 경과(구매확정 전)이고 사유가 단순변심이다 | 고객이 반품을 신청한다 | "기한이 초과되었습니다" 반환, 신청 거부 (단순변심 기한 10일). 하자·오배송은 AC-ORD-112, 구매확정 후는 고객 접수 불가(AC-ORD-096) — 어드민 접수(REQ-ORD-081) |
| AC-ORD-069 | 정상 | REQ-ORD-067 | 동일 주문 상품에 반려(REJECTED) 클레임 1건, 만료(PAYMENT_EXPIRED) 클레임 1건이 있다 | 고객이 재신청 가능 수량을 조회한다 | 반려·만료 건은 차감 대상에서 제외되어 원래 구매수량 그대로 재신청 가능 수량으로 반환된다 |
| AC-ORD-109 | 정상 | REQ-ORD-074 | 동일 주문 상품에 진행 중 반품 클레임 수량 2개, 반려 클레임 수량 1개가 있다(구매수량 5) | 고객이 재신청 가능 수량을 조회한다 | 응답 필드로 재신청 가능 수량 3(5−2)이 노출된다. 반려·만료 건은 제외된다 *(신규 2026-10-29)* |
| AC-ORD-033 | 정상 | REQ-ORD-040 | 클레임이 RECEIVED 상태이고 CS가 고객 귀책으로 판정했다 | 귀책판정이 확정된다 | 클레임 상태→PAYMENT_PENDING, 수거 배송비 결제 알림톡 발송 |
| AC-ORD-034 | 정상 | REQ-ORD-031 | 클레임이 RECEIVED 상태이고 CS가 판매자 귀책으로 판정했다 | 귀책판정이 확정된다 | shipment(PICKUP) 생성, 수거 즉시 시작 (배송비 없음). 클레임 상태는 RECEIVED 유지 (입고 확인 시 INSPECTING으로 전환, REQ-ORD-032) |
| AC-ORD-068 | 정상 | REQ-ORD-066, REQ-ORD-076 | 클레임이 RECEIVED 상태, 고객이 submitted_responsibility=CUSTOMER로 신청했다 | CS 담당자가 접수 확인 중 실제로는 판매자 귀책이라고 판단해 VENDOR로 판정한다 | 클레임 상태는 RECEIVED 유지, shipment(PICKUP) 생성 및 즉시 수거 시작 (CS 판정이 최종 — submitted_responsibility=CUSTOMER는 그대로 보존되고 responsibility만 VENDOR로 갱신됨. INSPECTING 전환은 입고확인 이후, AC-ORD-048 참조) |
| AC-ORD-064 | 예외 | REQ-ORD-058 | 고객이 판매자(VENDOR) 귀책 사유를 선택했고 첨부 사진이 0장이다 | 고객이 반품/교환 신청을 제출한다 | "상품 상태를 확인할 수 있는 사진을 1장 이상 첨부해주세요" 반환, 신청 거부 |
| AC-ORD-067 | 경계값 | REQ-ORD-065 | 클레임 신청 중 첨부 이미지가 3장 첨부되어 있다 | 고객이 4번째 이미지를 첨부하려 한다 | 추가 첨부가 거부된다 ("최대 3장까지 첨부 가능합니다") |
| AC-ORD-035 | 정상 | REQ-ORD-033 | 클레임이 RECEIVED 상태이다 | CS 담당자가 즉시 반려한다 | 클레임 상태→REJECTED, 사유 기록 |
| AC-ORD-070 | 정상 | REQ-ORD-068 | 클레임이 RECEIVED 상태로 24시간 이상 CS 미처리 상태이다 | 리마인드 배치가 실행된다 | CS 담당자에게 리마인드 알림이 발송된다 |
| AC-ORD-075 | 정상 | REQ-ORD-073 | 클레임이 RECEIVED 상태이다 (또는 PAYMENT_PENDING 상태, 귀책판정 이전) | 고객이 클레임 자진 취소를 요청한다 | 클레임 상태 → REJECTED로 전환되고 사유가 "고객 자진 철회"로 기록되며, 취소완료 알림톡이 발송된다 |
| AC-ORD-073 | 예외 | REQ-ORD-071 | 클레임이 INSPECTING 상태이다 | 고객이 클레임 자진 취소를 요청한다 | "귀책판정 이후에는 취소할 수 없습니다" 반환, 취소가 거부된다 |
| AC-ORD-036 | 정상 | REQ-ORD-035 | 클레임이 완료 처리되어 CLAIM_COMPLETED 이벤트가 발행된다 | 정산·알림·Catalog·Member가 각각 이벤트를 수신한다 | Settlement는 정산 차감, Notification은 완료 알림, Catalog는 재고복원, Member는 포인트복원을 수행한다. Payment는 이 이벤트로 환불하지 않는다(환불은 어드민 [환불 처리]만 트리거, AC-ORD-052) |

---

## 12. 주문 조회 Bolt

| ID | 카테고리 | 대응 EARS | Given | When | Then |
|---|---|---|---|---|---|
| AC-ORD-037 | 정상 | REQ-ORD-036 | 고객이 주문 3건을 보유하고 있다 | 주문 목록을 조회한다 | 본인 주문만 최신순으로 반환된다 |
| AC-ORD-038 | 정상 | REQ-ORD-037 | 판매자가 주문 5건을 수주했다 | 주문 목록을 조회한다 | 자기 매장 주문만 반환된다 |
| AC-ORD-039 | 정상 | REQ-ORD-038 | CS 담당자가 전체 주문을 조회한다 | 상태=CANCELLED, 기간=2026.06.01~06.30 필터를 적용한다 | 해당 조건의 주문만 반환된다 |
| AC-ORD-040 | 정상 | REQ-ORD-039 | 주문 상태가 PAYMENT_COMPLETED→PREPARING으로 변경되었다 | — | ord_status_history에 이력이 기록된다 |
| AC-ORD-079 | 정상 | REQ-ORD-038 | 주문번호 P261026-00001-00이 존재한다 | CS 담당자가 키워드에 `P261026-00001-00`을 입력해 조회한다 | 해당 주문 1건만 반환된다 (전체 번호를 입력하면 부분 일치로도 1건) |
| AC-ORD-080 | 경계값 | REQ-ORD-038 | 주문번호 P261026-00001-00 존재 | 키워드에 `P261026-0000`(일부)을 입력한다 | 주문번호 부분 일치로 해당 접두사를 가진 주문이 모두 반환된다 (대소문자 무시, 상품명·주문자명 일치 건 포함) |
| AC-ORD-081 | 정상 | REQ-ORD-038 | 주문자명 "홍길동"(주문 시점 orderer_name 스냅샷)인 주문이 있다 | 키워드에 "길동"을 입력한다 | 주문자명 부분 일치로 해당 주문이 반환된다 (이후 회원 개명과 무관) |
| AC-ORD-082 | 정상 | REQ-ORD-038 | 주문일시(ordered_at)가 2026-10-26 23:50인 주문이 있다 | 기간 from=to=2026-10-26으로 조회한다 | ordered_at 기준으로 해당 주문이 포함된다 |
| AC-ORD-083 | 정상 | REQ-ORD-038 | 키워드·기간 조건에 입금대기 3건·결제완료 5건이 일치한다 | status=PAYMENT_COMPLETED로 조회한다 | 목록은 5건이나 summary는 status와 무관하게 입금대기 3·결제완료 5·취소 0(키 유지)·전체 8로 반환된다 |
| AC-ORD-084 | 정상 | REQ-ORD-038 | 주문서 진입 임시주문(TEMP)이 존재한다 | 전체 조회한다 | TEMP는 목록·summary(all)에서 제외된다 |
| AC-ORD-085 | 예외 | REQ-ORD-038 | — | page=0, size=101, 또는 from>to로 조회한다 | 각각 400 INVALID_PAGE / INVALID_SIZE / INVALID_DATE_RANGE를 반환한다 |

---

## 13. 클레임 배송비 결제 Bolt

| ID | 카테고리 | 대응 EARS | Given | When | Then |
|---|---|---|---|---|---|
| AC-ORD-041 | 정상 | REQ-ORD-041 | 고객 귀책 클레임이 PAYMENT_PENDING 상태이다 | 고객이 서버가 산정한 수거 배송비(무료배송 주문 6,000원, 유료배송 주문 3,000원, 배송비 쿠폰 50% 할인 주문 4,500원 — 정책 6.9.7)를 결제한다 | 배송비 결제 완료, shipment(PICKUP) 생성 및 수거 프로세스 시작 (클레임 상태는 PAYMENT_PENDING 유지, INSPECTING 전환은 AC-ORD-048 참조) |
| AC-ORD-101 | 경계값 | REQ-ORD-040 | 초도 배송비 3,000원 중 배송비 쿠폰으로 1,500원이 할인된 주문이다 | 고객이 단순변심으로 전체 반품을 신청한다 | 수거 배송비가 편도 3,000원 + 할인받은 초도 배송비 1,500원 = 4,500원으로 산정되어 결제를 요청한다 *(신규 2026-10-29, 미구현)* |
| AC-ORD-042 | 정상 | REQ-ORD-041 | 배송비 쿠폰이 적용되어 결제금액 0원이다 | 고객이 [결제하기] 클릭한다 | 쿠폰으로 전액 충당, shipment(PICKUP) 생성 및 수거 즉시 시작 (클레임 상태는 PAYMENT_PENDING 유지) |
| AC-ORD-043 | 예외 | REQ-ORD-042 | 클레임 PAYMENT_PENDING 상태에서 24시간이 경과했다 | 배치가 실행된다 | 클레임 자동 취소 (PAYMENT_EXPIRED) + 알림톡 발송 |
| AC-ORD-113 | 예외 | REQ-ORD-050 | 클레임이 RETURN_PAYMENT_PENDING(반송 배송비 결제 대기)이고 24시간이 경과했다 | 만료 배치가 실행된다 | 반송 배송비 결제 요청이 만료 처리되고 알림톡이 발송된다(DH: RETURN_PAYMENT_PENDING→PAYMENT_EXPIRED). 반송 배송비는 편도 3,000원 고정이며 환불에서 차감하지 않고 별도 결제한다 *(신규 2026-10-29, 미구현)* |
| AC-ORD-044 | 경계값 | REQ-ORD-042 | 클레임 PAYMENT_PENDING 상태에서 23시간 59분 경과 | 고객이 배송비를 결제한다 | 정상 결제 완료 (기한 내) |
| AC-ORD-045 | 정상 | REQ-ORD-043 | 클레임 PAYMENT_PENDING 상태에서 12시간 경과 | 배치가 실행된다 | 미결제 리마인드 알림톡 발송 |

---

## 14. 판매자 수거·품질점검 Bolt

| ID | 카테고리 | 대응 EARS | Given | When | Then |
|---|---|---|---|---|---|
| AC-ORD-046 | 정상 | REQ-ORD-044 | 배송비 결제 완료 상태이다 (클레임: PAYMENT_PENDING, 또는 판매자귀책으로 RECEIVED 유지 중) | 판매자가 수거 운송장을 등록한다 | shipment(PICKUP) 상태 → IN_TRANSIT (클레임 상태는 PAYMENT_PENDING 또는 RECEIVED로 그대로 유지) |
| AC-ORD-047 | 예외 | — | 배송비가 미결제 상태이다 | 판매자가 수거 운송장을 등록하려 한다 | "배송비 결제 후 수거 가능" 거부 |
| AC-ORD-048 | 정상 | REQ-ORD-045, REQ-ORD-032 | shipment(PICKUP)가 IN_TRANSIT 상태이고 상품이 입고되었다 | 판매자가 [입고 확인] 클릭한다 | shipment(PICKUP) 상태 → DELIVERED, 클레임 상태 → INSPECTING (품질점검) 전환 |
| AC-ORD-049 | 정상 | REQ-ORD-046 | 클레임이 INSPECTING 상태, 상품 상태 양호 | 판매자가 [품질점검 합격] 클릭한다 | 클레임 상태 → PICKED_UP (수거완료) |
| AC-ORD-114 | 경계값 | REQ-ORD-050 | 품질점검 전체 불합격(PICKUP_REJECTED)으로 반송이 결정되었다 | 어드민이 반송 배송비 추가결제를 요청한다 | 반송 배송비는 반송 사유·주문 배송비와 무관하게 편도 3,000원 고정으로 요청된다(무료배송 주문도 동일) *(신규 2026-10-29)* |
| AC-ORD-050 | 정상 | REQ-ORD-047 | 클레임이 INSPECTING 상태, 상품 훼손 확인 | 판매자가 [품질점검 거부] + 사유 입력한다 | 클레임 상태 → PICKUP_REJECTED (수거거부) |
| AC-ORD-051 | 예외 | REQ-ORD-048 | 클레임이 INSPECTING 상태이다 | 판매자가 사유 없이 [품질점검 거부]를 클릭한다 | "거부 사유를 입력해주세요" 반환, 거부 불가 |
| AC-ORD-074 | 예외 | REQ-ORD-072 | 클레임 유형이 EXCHANGE이고 INSPECTING 상태이며, 판매자가 첨부 사진 없이 [품질점검 거부]를 시도한다 | 판매자가 거부 처리를 제출한다 | "사진을 첨부해주세요" 반환, 거부 처리가 거부된다 (사진 미첨부 시 처리 불가) |
| AC-ORD-078 | 정상 | REQ-ORD-075 | 고객이 클레임 접수 시 사진 3장(uploaded_by=CUSTOMER)을 첨부했다 | 이후 판매자가 같은 클레임의 품질점검거부 처리를 하며 별도로 사진 2장(uploaded_by=VENDOR)을 첨부한다 | 업로더(CUSTOMER/VENDOR)별로 "최대 3장" 제약이 독립 적용되어, 판매자의 첨부가 고객 첨부 수량과 합산되지 않고 정상 등록된다 |

---

## 15. 어드민 환불·폐기·반송 Bolt

> (Payment 도메인 관련 나머지 항목은 [payment.md](payment.md) 참조)

| ID | 카테고리 | 대응 EARS | Given | When | Then |
|---|---|---|---|---|---|
| AC-ORD-052 | 정상 | REQ-ORD-034 | 클레임이 PICKED_UP(수거완료) 상태이다 | 어드민이 [환불 처리] 클릭한다 | 클레임 상태 → REFUNDED, 어드민 [환불 처리](API-029)가 유일한 환불 트리거이며 PG 환불 진행 (환불금액 = 상품주문금액 + 환불 대상 배송비, 반품 배송비는 별도 결제라 차감하지 않음 — AC-PAY-039) |
| AC-ORD-108 | 정상 | REQ-ORD-034 | 클레임이 PICKED_UP 상태에서 어드민이 환불을 처리했다 | 클레임이 REFUNDED로 전환된다 | 환불 요청은 이 어드민 호출 한 경로로만 Payment에 전달된다(중복 요청 없음). Catalog 재고복원·Member 포인트복원은 클레임이 COMPLETED로 전환될 때 CLAIM_COMPLETED 이벤트로 수행된다(AC-ORD-036) *(신규 2026-10-29)* |
| AC-ORD-053 | 정상 | REQ-ORD-035 | 클레임이 REFUNDED 상태이다 | 환불 완료 배치가 실행된다 | 클레임 상태 → COMPLETED, 알림톡 발송 |
| AC-ORD-054 | 정상 | REQ-ORD-049 | 클레임이 PICKUP_REJECTED(수거거부) 상태이다 | 어드민이 [폐기 처리] 클릭한다 | 클레임 상태 → DISPOSED → COMPLETED |
| AC-ORD-055 | 정상 | REQ-ORD-050 | 클레임이 PICKUP_REJECTED 상태이다 | 어드민이 [반송 배송비 추가결제 요청] 클릭한다 | 고객에게 반송 배송비(편도 3,000원 고정, 별도 결제) 결제 알림톡 발송, 상태 → RETURN_PAYMENT_PENDING |
| AC-ORD-056 | 정상 | REQ-ORD-051 | 클레임이 RETURN_PAYMENT_PENDING 상태, 반송 배송비 결제 완료 | 판매자가 반송 운송장을 등록한다 | shipment(RETURN) 생성, 상태 → IN_TRANSIT (클레임 상태는 RETURN_PAYMENT_PENDING 유지) |
| AC-ORD-057 | 정상 | REQ-ORD-052 | shipment(RETURN)가 IN_TRANSIT 상태이다 | 택배사가 반송 배송완료를 확인한다(API) | shipment(RETURN) 상태 → DELIVERED (클레임 상태는 RETURN_PAYMENT_PENDING 유지, COMPLETED 전환은 배치가 수행 — AC-ORD-058 참조) |
| AC-ORD-058 | 정상 | REQ-ORD-053 | 클레임이 RETURN_PAYMENT_PENDING 상태이고 shipment(RETURN)가 DELIVERED 상태이다 | 배치가 실행된다 | 클레임 상태 → COMPLETED로 직접 전환 (RETURN_SHIPPING/RETURN_DELIVERED 경유 없음), 알림톡 발송 |
| AC-ORD-071 | 예외 | REQ-ORD-069 | 클레임 유형이 EXCHANGE이고 교환 요청 SKU(exchangeSkuId)의 재고가 0이다 | CS 담당자가 판매자(VENDOR) 귀책으로 귀책판정을 확정하려 한다 | "교환 가능한 재고가 없습니다" 반환, 귀책판정 자체가 거부된다 (선출고 전 단계에서 차단) |
| AC-ORD-062 | 정상 | REQ-ORD-056 | 클레임 유형이 EXCHANGE이고 귀책판정이 완료된다 (판매자귀책: 판정 즉시 / 고객귀책: 수거배송비 결제완료) | 시스템이 귀책판정 완료를 처리한다 | 교환 SKU 재고가 선점되고 shipment(EXCHANGE_OUT)가 생성되어 교환상품이 즉시 선출고된다 (원상품 수취 이전, 맞교환 원칙) |
| AC-ORD-063 | 정상 | REQ-ORD-057 | 클레임 유형이 EXCHANGE이고 INSPECTING 상태에서 회수 상품이 입고되었다 | 판매자가 택(TAG) 부착 상태를 확인한다 | 택이 유지되어 있으면 PICKED_UP(합격), 택이 제거·훼손되어 있으면 PICKUP_REJECTED(거부)로 판정된다 |
| AC-ORD-116 | 정상 | REQ-ORD-083 | 클레임 유형이 EXCHANGE이고 PICKED_UP(합격) 상태이며 선출고한 shipment(EXCHANGE_OUT)가 IN_TRANSIT이다(또는 이미 DELIVERED) | 교환상품 배송이 완료되어 고객이 수령한다(shipment DELIVERED, 이미 수령한 경우 다음 배치 주기) | 클레임 상태가 PICKED_UP → COMPLETED로 전환된다. 교환은 환불이 없어 어드민 [환불 처리]를 거치지 않는다 *(신규 2026-11-03)* |
| AC-ORD-117 | 정상 | REQ-ORD-083 | 클레임 유형이 EXCHANGE이고 품질점검에 합격했다(PICKED_UP) | 합격 처리가 완료된다 | 이 시점에는 CLAIM_COMPLETED가 발행되지 않는다. CLAIM_COMPLETED는 AC-ORD-116의 COMPLETED 전환 시 발행되며 정산·알림·포인트 이벤트로만 쓰인다(Payment 환불 없음). 원상품 재고는 합격 시점에 복원된다 *(신규 2026-11-03)* |
| AC-ORD-118 | 예외 | REQ-ORD-081 | 하자·오배송(VENDOR 귀책) 사유이고 3개월과 안 날부터 30일을 모두 넘겼다(구매확정 전·후 무관) | 고객이 모바일에서 반품·교환을 신청한다 | "기한이 초과되었습니다"(CLAIM_PERIOD_EXPIRED)로 거부하고 고객센터 문의를 안내한다. 접수는 어드민 운영자 승인 경로(7.2.3)로만 가능하다 *(신규 2026-11-03)* |
| AC-ORD-119 | 정상 | REQ-ORD-084 | 운영자가 부정 주문으로 확인한 계정이 있다 | 운영자가 사유와 제한 내용(대상·기간)을 입력해 이용 제한을 요청한다 | Member 도메인에 이용 제한 요청이 사유·내용과 함께 전달되고 요청자·일시가 이력에 남는다 *(신규 2026-11-03, 구현은 후속)* |
| AC-ORD-120 | 예외 | REQ-ORD-084 | Member 도메인에서 이용 제한 상태인 회원이다 | 주문서 진입·결제 요청·쿠폰 사용을 시도한다 | 요청이 거부되고 제한 사유와 이의 신청 방법이 안내된다(에러코드 미정) *(신규 2026-11-03, 구현은 후속)* |
| AC-ORD-121 | 정상 | REQ-ORD-085 | 회원이 탈퇴했거나 2025년 주문이 있고 현재 날짜가 2031-01-01이다 | 연 1회 마스킹 배치가 실행된다(탈퇴 회원 건은 1일 1회 배치) | 해당 주문·결제·배송의 수령인·연락처·주소·환불계좌·주문자명·가상계좌·카드 데이터가 마스킹되고 금액·상태·일시는 유지되며 이력은 삭제되지 않는다. 2025-01-01과 2025-12-31 주문은 동일하게 2031-01-01에 처리된다 *(신규 2026-11-03, 미구현)* |
| AC-ORD-122 | 정상 | REQ-ORD-085 | 보존 기간 안의 주문이 있다 | 고객·어드민·판매자 화면에서 주문을 조회한다 | 수령인·연락처·주소·환불계좌·주문자명·가상계좌·카드가 항상 마스킹되어 표시된다(저장 데이터는 보존 기간 초과 전까지 원본) *(신규 2026-11-03, 미구현)* |
| AC-ORD-123 | 예외 | REQ-ORD-057 | 클레임 유형이 EXCHANGE이고 교환상품이 이미 선출고되었으며 품질점검에서 택(TAG) 미유지로 불합격했다 | 판매자가 품질점검 거부를 처리한다 | 클레임은 불합격(PICKUP_REJECTED) 흐름을 따르고, 선출고된 교환상품에 대한 비용은 시스템이 자동 청구·환불하지 않으며 운영자가 수작업으로 청구한다(청구 항목·금액·기한은 확인 필요) *(신규 2026-11-03, 미구현)* |
| AC-ORD-124 | 정상 | REQ-ORD-086 | 단순변심 반품 클레임이 PAYMENT_PENDING이고 서버 산정 수거 배송비가 3,000원이며 고객이 배송비 쿠폰(예: 50% 할인)을 보유한다 | 고객이 쿠폰을 지정해 클레임 배송비를 결제한다 | 서버가 쿠폰 할인을 적용한 금액(1,500원)을 결제 금액으로 확정하고, PG 인증 금액이 같으면 결제가 완료되어 클레임이 INSPECTING으로 전환된다. 응답에 `couponApplied=true`와 할인액이 포함된다 *(신규 2026-11-03, 미구현)* |
| AC-ORD-125 | 예외 | REQ-ORD-086 | 클레임 배송비 결제 대기 상태이다 | 고객이 배송비 쿠폰이 아닌 쿠폰(또는 만료된 쿠폰)을 지정해 결제한다 | COUPON_NOT_APPLICABLE(만료는 COUPON_EXPIRED)로 거부되고 결제는 진행되지 않는다 *(신규 2026-11-03, 미구현)* |
| AC-ORD-126 | 정상 | REQ-ORD-086 | 교환 클레임이 PAYMENT_PENDING이고 서버 산정 왕복 배송비가 6,000원이며 고객이 배송비 쿠폰(50% 할인)을 2장 보유한다 | 고객이 쿠폰 2장을 지정해 클레임 배송비를 결제한다 | 구간별 1장씩 적용되어 결제 금액이 3,000원으로 확정되고 결제가 완료된다. 3장을 지정하거나 편도 배송비에 2장을 지정하면 COUPON_NOT_APPLICABLE로 거부된다 *(신규 2026-11-03, 미구현)* |
| AC-ORD-127 | 정상 | REQ-ORD-035 | 클레임이 COMPLETED로 전환되어 CLAIM_COMPLETED가 발행되었다 | Settlement가 이벤트를 수신한다 | 구매확정 후 접수된 반품·하자 클레임(`afterPurchaseConfirm=true`)만 정산에서 차감한다. 구매확정 전 취소·반품(`false`)과 교환(`claimType=EXCHANGE`)은 차감하지 않으며, 환불 완료로는 별도 차감 이벤트를 발행하지 않는다 *(신규 2026-11-03, 미구현)* |

---

## 16. 장바구니 옵션 변경 Bolt

| ID | 카테고리 | 대응 EARS | Given | When | Then |
|---|---|---|---|---|---|
| AC-ORD-059 | 정상 | REQ-ORD-054 | 장바구니에 상품A(SKU-001, 블랙/265)가 있다 | 고객이 옵션을 화이트/265(SKU-002)로 변경한다 | SKU가 변경되고 소계 재계산 |
| AC-ORD-060 | 예외 | REQ-ORD-055 | 화이트/275(SKU-003) 옵션의 잔여수량(실재고−장바구니 선점)이 0이다 | 고객이 해당 옵션을 선택한다 | "해당 옵션은 품절입니다" 선택 불가 |
| AC-ORD-061 | 정상 | — | 블랙/265(SKU-001) 잔여수량이 7개이다 | 고객이 옵션변경 팝업을 연다 | 잔여수량 "7개" 표시, 품절 옵션은 [×] 비활성화 |

---

## 18. 배송 재발송 Bolt

> 신규 (2026-08-21 바텀업 재검증): REQ-ORD-062 대응. shipment_type 공통(OUTBOUND/PICKUP/RETURN/EXCHANGE_OUT), DM-시퀀스/order §19 배치가 FAILED로 전환한 건을 판매자/CS가 수동 재처리한다.


| ID | 카테고리 | 대응 EARS | Given | When | Then |
|---|---|---|---|---|---|
| AC-ORD-076 | 정상 | REQ-ORD-062 | shipment(임의 유형)가 FAILED 상태이다 | 판매자 또는 CS 담당자가 새 운송장 정보로 재발송 처리를 요청한다 | shipment 상태가 FAILED→PENDING→IN_TRANSIT으로 전환되고 새 운송장이 등록된다 (이후 60분 주기 배치가 다시 추적) |
| AC-ORD-077 | 예외 | REQ-ORD-062 | shipment가 FAILED가 아닌 상태(예: IN_TRANSIT)이다 | 판매자 또는 CS 담당자가 재발송 처리를 요청한다 | "FAILED 상태만 재발송 가능합니다" 반환 (RESHIP_NOT_ALLOWED), 처리 거부 |

---

## 근거

| 항목 | 출처 |
|---|---|
| 시나리오 도출 | EARS(DD) REQ-ORD-001~086, REQ-PAY-001~031 → GWT 변환 (바텀업 재검증분 REQ-ORD-063~076, REQ-PAY-023~024 포함, 비동기 접수 개정분 REQ-ORD-077~079 — AC-ORD-086~090, 입금대기 취소 REQ-ORD-080 — AC-ORD-091·092, 구매확정 후 접수 REQ-ORD-081 — AC-ORD-095~097, 취소 클레임 REQ-ORD-082 — AC-ORD-098~100, 대응 AC가 없던 REQ-ORD-020·021·027·034·059·060·061·074와 확정 결정(자동 구매확정 제외·재처리, 사유별 기한, 반송 배송비 24시간 만료·3,000원 고정, TEMP TTL) — AC-ORD-102~115, 교환 종료·기한 후 하자 — AC-ORD-116~118) |
| 경계값 수치 | 정책서 (50개 장바구니, D+11 자동확정, 반품 10일, 총 3회 시도(승인 실패 응답, 정책 9.6.1), PG 승인 응답 대기 3초, 배송비결제 24시간) |
| 예외 시나리오 | EARS Unwanted/Optional 패턴 + 화면레이아웃(DN) 정책 미결 사항 |
| 상태 전이 | 상태머신(DH) v6 — Order 10상태(배송 실행은 ord_shipment로 분리; PREPARING에서 shipment(OUTBOUND) DELIVERED 이벤트 구독으로 DELIVERED 파생전환, IN_DELIVERY 상태 없음). Claim 11상태(RECEIVED→PAYMENT_PENDING(고객귀책) 또는 RECEIVED→INSPECTING(판매자귀책, shipment(PICKUP) 생성·DELIVERED 후 전환)→PICKED_UP/PICKUP_REJECTED→REFUNDED→COMPLETED/DISPOSED/RETURN_PAYMENT_PENDING→COMPLETED(shipment(RETURN) DELIVERED 후 배치가 직접 전환, RETURN_SHIPPING/RETURN_DELIVERED 경유 없음)). Claim은 CS "처리시작(IN_PROGRESS)" 단계 없이 RECEIVED에서 귀책판정으로 곧바로 분기한다. 신규 shipment.status(PENDING/IN_TRANSIT/DELIVERED/FAILED/CANCELLED, order/claim 공용, shipment_type=OUTBOUND/PICKUP/RETURN/EXCHANGE_OUT). responsibility는 CUSTOMER/VENDOR 2종 |
