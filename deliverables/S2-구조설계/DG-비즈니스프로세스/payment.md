# 비즈니스 프로세스 — Payment

> **단계**: 구조설계
> **문서범위**: Domain
> **문서종류**: Design
>
> **작성 목적**: 상태머신(DH)의 전이를 액티비티 흐름으로 확장하여, "누가 어떤 순서로 업무를 수행하는가"를 시각화한다.
> **흐름 내 위치**: DF ERD → **DG 비즈니스 프로세스** → DH 상태머신 → DI 이벤트 플로우
> **작성 주체**: 시니어 개발자 + AI 협업 (기획자·현업 검토·확인)

| 항목 | 내용 |
|---|---|
| ID | DESIGN-BP-PAYMENT-001 |
| 상태 | **Finalized** |
| 작성일 | 2026-08-11 |
| 갱신일 | 2026-10-29 |

---

## 1. 결제 승인 프로세스

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title 결제 승인 비즈니스 프로세스

|시스템(Order)|
start
:결제 요청 전달\n(order_id, amount, method);

|시스템(Payment)|
:결제 생성 (PENDING);
:금액 검증\n(요청 금액 == 주문금액 total_order_amount − 포인트?);

if (금액 일치?) then (yes)
  :PG(토스페이먼츠) 승인 요청\n(응답 대기 3초);
else (no)
  :금액 불일치 오류;
  :PAYMENT_FAILED 이벤트 발행;
  stop
endif

if (3초 내 응답?) then (no — 타임아웃)
  :결제 확인 중 (CONFIRMING)\n재결제 차단;
  :PG 거래 조회로 승인 여부 확정\npay_payment_log 기록 (TIMEOUT);
  if (조회 결과 승인?) then (yes)
    :PAID;
    :PAYMENT_APPROVED 이벤트 발행 → Order;
    stop
  else (no — 미승인, 실패 +1)
    if (누적 실패 < 3?) then (yes)
      :PENDING 복귀 → 승인 재요청;
      note right: 위 분기로 복귀
    else (no — 3회 도달)
      :CANCELLED;
      :PAYMENT_FAILED 이벤트 발행 → Order;
    endif
    stop
  endif
elseif (PG 승인 성공?) then (yes)
  :PAID;
  :pay_payment_log 기록 (APPROVE);
  :PAYMENT_APPROVED 이벤트 발행 → Order;
  stop
else (no — 승인 실패 응답)
  if (누적 실패 < 3? (이번 실패 포함)) then (yes)
    :재시도 (실패 횟수 +1, 멱등키 동일)\n승인 재요청;
    note right: 재요청 후 위 분기로 복귀
  else (no — 총 3회 시도 모두 실패)
    :CANCELLED;
    :pay_payment_log 기록 (FAIL, final);
    :PAYMENT_FAILED 이벤트 발행 → Order;
    stop
  endif
  stop
endif

@enduml
```

> **타임아웃(2026-10-29 개정)**: 승인 응답이 3초 안에 오지 않으면 즉시 재요청하지 않고 "결제 확인 중"으로 두고 PG 거래 조회로 확정한다(정책서 4.5.2). 확인 전 재결제는 차단한다. 조회 결과 미승인이면 **실패 1회로 계산**하고, 실패 응답과 합산한 누적 실패가 3회 미만이면 재요청, 3회면 CANCELLED다.
> **승인 실패 응답 재시도**: 승인 실패 응답은 최초 시도 포함 총 3회 시도(재시도 최대 2회) 후 CANCELLED로 **확정**했다(2026-10-29, REQ-PAY-003·004, 정책서 9.6.1 정정). 재시도 간격은 **3초 고정**이다(2026-10-29 확정, 옛 지수 백오프 1초→2초→4초는 폐기). 3초 무응답은 조회로 미승인이 확정된 뒤에 같은 간격으로 재요청한다.

---

## 2. 환불 프로세스

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title 환불 비즈니스 프로세스

|시스템(Order)|
start
:환불 요청\n(ORDER_CANCELLED 이벤트 또는\n어드민 환불 처리 API-029);

|시스템(Payment)|
:환불 유형 판별;

if (전액 환불?) then (yes)
  :PG 전액 환불 요청;
else (부분 환불)
  :PG 부분 환불 요청\n(환불 금액 계산);
endif

if (PG 환불 성공?) then (yes)
  if (전액?) then (yes)
    :REFUNDED;
  else (부분)
    :PARTIAL_REFUNDED;
  endif
  :pay_payment_log 기록 (REFUND/PARTIAL_REFUND);
  :PAYMENT_REFUNDED 이벤트 발행\n(refundReason=ORDER_CANCELLED 또는 CLAIM_COMPLETED, 2026-11-04 신설);
  stop
else (실패)
  :pay_payment_log 기록 (REFUND_FAIL);
  :1시간 간격 최대 3회 자동 재시도\n(정책서 8.8.2);
  if (재시도 성공?) then (yes)
    :REFUNDED / PARTIAL_REFUNDED;
    :PAYMENT_REFUNDED 이벤트 발행\n(2026-11-04 신설);
    stop
  else (3회 모두 실패)
    :CS 알림 발송\n(운영자 이관, 수동 환불 필요);
    stop
  endif
endif

@enduml
```

> **환불 트리거·실패 처리(2026-11-03 확정)**: 환불은 ① 주문 취소(ORDER_CANCELLED 수신 시 자동) ② 클레임(반품) 환불(**어드민 [환불 처리](API-029)만** 트리거) ③ LATE_DEPOSIT(자동)으로만 시작한다. CLAIM_COMPLETED는 정산·알림·재고복원·포인트 이벤트일 뿐 Payment가 이 이벤트로 환불하지 않는다(REQ-PAY-009). 환불 실패는 정책서 8.8.2(1시간 간격 최대 3회 자동 재시도 후 운영자 이관)가 정본(설계안)이며, 현행 구현은 즉시 실패·보상 1회·운영팀 이관(정책서 8.1.4, 구현 이력)이다.
> **PAYMENT_REFUNDED 발행(2026-11-04 신설)**: 환불이 실제로 성공(최초 성공 또는 재시도 성공)했을 때만 발행하고, 3회 재시도 후 운영자 이관되는 실패 건은 발행하지 않는다(수동 환불로 최종 성공한 시점에 발행, §3 수동 환불 프로세스 참조). 상세 스키마는 이벤트플로우(DI payment.md) `PAYMENT_REFUNDED`.

---

## 3. 수동 환불 프로세스

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title 수동 환불 비즈니스 프로세스

|CS 담당자|
start
:환불 실패 건 확인;

if (PG 재환불 가능?) then (yes)
  :수동 PG 재환불 요청;
  |시스템(Payment)|
  :PG 재환불 요청;
  if (성공?) then (yes)
    :상태 갱신 (REFUNDED/PARTIAL_REFUNDED);
    :pay_payment_log 기록;
    :PAYMENT_REFUNDED 이벤트 발행\n(refundReason=MANUAL, 2026-11-04 신설);
    stop
  else (실패)
    :에스컬레이션\n(PG 관리자 직접 처리);
    stop
  endif
else (원결제수단 환불 불가)
  |CS 담당자|
  if (결제수단?) then (가상계좌)
    :결제 시 저장된 환불계좌 사용\n(refund_bank_name·refund_account_no·refund_holder_name);
  else (카드·간편결제 — 예외)
    :고객에게 입금정보 요청;
    :입금정보 시스템 등록\n(은행/계좌번호/예금주);
  endif
  :직접 계좌이체 수행\n(수동);
  :환불완료 처리 클릭;
  |시스템(Payment)|
  :상태 갱신 (REFUNDED);
  :pay_payment_log 기록 (BANK_TRANSFER);
  :PAYMENT_REFUNDED 이벤트 발행\n(refundReason=MANUAL, 2026-11-04 신설);
  stop
endif

@enduml
```

---

## 3-1. 입금 통보·취소 경합 자동 환불 프로세스 (LATE_DEPOSIT, 2026-10-29)

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title LATE_DEPOSIT 자동 환불 프로세스

|PG|
start
:가상계좌 입금 통보 전달;

|시스템(Payment)|
:pay_payment_log 기록 (DEPOSIT);
if (주문 취소 확정?) then (yes — 취소 우선)
  :결제를 PAID로 바꾸지 않음;
  :입금액을 환불 대상으로 기록\n(refund_reason=LATE_DEPOSIT, 기준일=입금 통보 수신일);
  :저장된 환불계좌로 자동 환불 요청\n(운영자 승인 없음, 기한 8.1.3 3영업일);
  if (환불 성공?) then (yes)
    :pay_payment_log 기록 (REFUND);
    :PAYMENT_REFUNDED 이벤트 발행\n(refundReason=LATE_DEPOSIT, 2026-11-04 신설 — Notification 고객 안내);
  else (no — 계좌 오류·PG 실패)
    :pay_payment_log 기록 (REFUND_FAIL);
    :CS 알림 → 수동 환불 (정책서 8.7.2·8.8.2);
  endif
else (no)
  :금액 대조 후 PAID\nPAYMENT_APPROVED 이벤트 발행 → Order;
endif
stop

@enduml
```

---

## 4. 카드 제한·해제 프로세스

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title 카드 제한·해제 프로세스

|시스템(Payment)|
start
:결제 실패 감지;
:동일 카드 실패 횟수 조회;

if (3회 연속 실패?) then (yes)
  :카드 당일 제한 등록\n(pay_card_restriction);
  :고객 안내 메시지;
else (no)
  :pay_card_fail_counter.consecutive_fail_count 증가;
endif
stop

|시스템(배치)|
start
:익일 00:00 배치 실행;
:전일 제한 카드 조회;
:released_at 갱신 (제한 해제);
stop

@enduml
```

---

## 근거

| 항목 | 출처 |
|---|---|
| 상태 전이 | `../DH-상태머신/payment.md` |
| 결제 흐름 | `../DC-상위유스케이스/payment.md` 결제 실행 업무그룹 |
| 재시도 규칙 | REQ-PAY-003 (총 3회 시도), REQ-PAY-005·029 (승인 응답 대기 3초, 결제 확인 중) |
| 금액 검증 | REQ-PAY-007 |
| 카드 제한 | REQ-PAY-018, REQ-PAY-019 |
| 환불 정책 | REQ-PAY-008~013 |
| 신규 REQ-PAY-023~031 추적 | 023 카드 연속 실패 카운터(§4), 024 환불 산식(§2), 025~028 복합결제·주문금액 검증(§1), 029 결제 확인 중(§1), 030 LATE_DEPOSIT 자동 환불(§3-1), 031 환불계좌(§3 가상계좌 수동 환불) |
| PAYMENT_REFUNDED 발행 지점(2026-11-04 신설) | 이벤트플로우(DI payment.md·readme.md), DP-클래스설계/payment.md `PaymentEventPublisher.publishPaymentRefunded` — §2·§3·§3-1의 환불 성공 분기에 발행 단계 추가 |
