# 비즈니스 프로세스 — Order

> **단계**: 구조설계
> **문서범위**: Domain
> **문서종류**: Design
>
> **작성 목적**: 상태머신(DH)의 전이를 액티비티 흐름으로 확장하여, "누가 어떤 순서로 업무를 수행하는가"를 시각화한다.
> **흐름 내 위치**: DF ERD → **DG 비즈니스 프로세스** → DH 상태머신 → DI 이벤트 플로우
> **작성 주체**: 시니어 개발자 + AI 협업 (기획자·현업 검토·확인)
> **갱신일**: 2026-10-29
---

## 1. 주문결제 프로세스

> v3 (2026-10-29 현행화): 비동기 접수 모델로 교체 — 결제하기는 접수만 동기(TEMP→STOCK_REQUESTED + 아웃박스 같은 트랜잭션), 재고차감·결제요청은 컨슈머가 비동기 처리, 가상계좌 발급 후 입금대기(DEPOSIT_PENDING)에서 입금 통보·12시간 만료·고객 취소(취소 우선)로 분기. 상태머신(DH) v7·REQ-ORD-008·012·013·014·077~080 기준.

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title 주문결제 비즈니스 프로세스 (비동기 접수)

|고객|
start
:주문서 화면 진입\n(TEMP 임시주문 생성);
:주문서 작성\n(배송지·쿠폰·포인트·결제수단 선택,\n가상계좌는 환불계좌 입력);
:결제하기;

|시스템(Order)|
:접수 (동기, 한 트랜잭션)\nTEMP → STOCK_REQUESTED\n+ 아웃박스 STOCK_DEDUCT_REQUESTED 적재;
:접수 응답 즉시 반환;

|시스템(컨슈머)|
:재고 차감 (SKU 단위 멱등)\n→ Catalog 상품 API;

if (전 SKU 성공?) then (yes)
  :주문 상태 → STOCK_DEDUCTED\n+ 아웃박스 PAYMENT_REQUESTED 적재;
else (일부 SKU 부족)
  :성공 SKU 차감 유지,\n실패 SKU만 백오프 후 재시도;
  if (3회 소진?) then (yes)
    :성공 SKU 차감분 복원\n주문 상태 → STOCK_FAILED;
    :고객 알림 (미구현);
    stop
  else (no)
    :재시도 후 위 판정으로 복귀;
  endif
endif

|시스템(Payment)|
:결제 요청 처리\n(PAYMENT_REQUESTED)\n가상계좌 발급;
note right
  PG 승인 응답 대기 3초.
  승인 실패 응답 / 3초 무응답(→ 결제 확인 중
  → PG 거래 조회 미승인) = 실패 1회로 합산.
  누적 실패 3회 미만이면 PENDING 복귀·재요청
  (총 3회 시도 = 최초 + 재시도 2회, 간격 3초).
end note

if (누적 실패 3회 도달?) then (yes)
  :PAYMENT_FAILED 이벤트 발행;
  |시스템(Order)|
  :재고 복원;
  :주문 상태 → PAYMENT_FAILED;
  :고객 알림톡 발송;
  stop
else (no — 발급 성공)
endif

|시스템(Order)|
:주문 상태 → DEPOSIT_PENDING\n(입금대기, 입금기한 12시간);

|고객|
if (입금대기 중 취소?) then (yes — 입금 통보보다 취소 우선)
  :취소 요청 (REQ-ORD-080);
  |시스템(Order)|
  :가상계좌 폐기 + 재고 복원\n환불 없음\n주문 상태 → CANCELLED\n(취소 클레임 생성, REQ-ORD-082);
  stop
else (no)
endif

|시스템(Payment)|
if (12시간 내 입금 통보?) then (yes)
  :입금 통보 수신 (금액 일치);
else (no — 입금기한 만료)
  |시스템(Order)|
  :재고 복원\n주문 상태 → CANCELLED (입금기한 만료);
  stop
endif

|시스템(Order)|
:주문 상태 → PAYMENT_COMPLETED;
:판매자별 주문 분할;
:ORDER_PAID 이벤트 발행;
note right: → Settlement(정산 대기)\n→ Notification(주문확인 알림톡+이메일)

stop
@enduml
```

> 취소 확정된 주문에 입금 통보가 뒤늦게 도착하면 PAYMENT_COMPLETED로 바꾸지 않고 입금액을 저장된 환불계좌로 자동 환불한다(LATE_DEPOSIT, REQ-PAY-030). 카드·간편결제 등 인증형 수단의 PAYMENT_AUTH_PENDING 흐름은 안(DH 참조)이며 이 다이어그램은 가상계좌(프로토타입 범위) 기준이다. 입금 통보·만료·고객 취소·PAYMENT_FAILED 처리는 프로토타입 미구현.

### [폐기] 이력 — 동기 접수 모델 (2026-10-29 이전)

> 아래 구 모델은 폐기됐다: `TEMP→ORDER_RECEIVED→PAYMENT_PENDING`, 결제하기 중 Catalog 동기 재고 선점 호출, 재고 부족 시 즉시 `STOCK_FAILED`, 승인 실패 1회에 즉시 `PAYMENT_FAILED`. 현행은 위 다이어그램(DH v7)을 따른다.

---

## 2. 배송·구매확정 프로세스

> v2 (2026-08-20 현행화): 배송 실행(IN_DELIVERY)을 `ord_shipment`(OUTBOUND)로 분리 — 상태머신(DH) v6

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title 배송·구매확정 비즈니스 프로세스

|판매자|
start
:출고 준비 확인;
:PREPARING;
:운송장 등록\n→ shipment(OUTBOUND) 생성;

|시스템(Order)|
:shipment(OUTBOUND) → IN_TRANSIT;
:배송상태 갱신 (배치 60분, 택배사 API 조회);

if (배송완료?) then (yes)
  :shipment(OUTBOUND) → DELIVERED;
  :주문 상태 → DELIVERED\n(shipment 이벤트 구독, 파생 전환);
else (no)
  :계속 추적;
  stop
endif

|고객|
if (수동 구매확정?) then (yes)
  :구매확정 요청;
else (D+11 경과)
  |시스템(배치)|
  if (진행 중 반품·교환 클레임 없음?\n(정책 5.6.2)) then (yes)
    :자동 구매확정;
  else (no — 클레임 진행 중)
    :자동 구매확정 제외\n(클레임 종결 후 재판정);
    stop
  endif
endif

|시스템(Order)|
:CONFIRMED;
:ORDER_CONFIRMED 이벤트 발행;
note right: → Settlement(정산 등록)\n→ Member(포인트 적립)
stop

@enduml
```

---

## 3. 취소 프로세스

> v2 (2026-08-20 현행화): CS 예외취소가 PREPARING까지만 가능함을 명시(송장 등록 후·배송 시작 이후는 CS도 취소 불가, 상태머신(DH) 금지전이)

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title 주문 취소 비즈니스 프로세스

|고객 / CS|
start
:취소 요청;

|시스템(Order)|
if (PAYMENT_COMPLETED 또는 DEPOSIT_PENDING(입금대기) 상태?) then (yes)
  :고객 단순 취소 허용;
  note right: 입금대기는 가상계좌 폐기 + 재고 복원, 환불 없음
  :CANCELLED\n(취소 클레임 생성, REQ-ORD-082);
  :ORDER_CANCELLED 이벤트 발행;
  note right: → Payment(환불)\n→ Catalog(재고 복원)\n→ Member(포인트 복원)
  stop
else (PREPARING 상태?) then (yes)
  if (CS 예외 취소 + 출고 shipment 송장 미등록?) then (yes)
    :CS 예외 취소 처리;
    :CANCELLED\n(취소 클레임 생성, channel=CS, REQ-ORD-082);
    :ORDER_CANCELLED 이벤트 발행;
    note right: → Payment(환불)\n→ Catalog(재고 복원)
    stop
  else (no)
    :취소 거부\n고객: "고객센터로 문의해주세요"\n송장 등록 후: "배송완료 후 반품을 이용해주세요";
    stop
  endif
else (DELIVERED 이후 — 배송 시작됨)
  :취소 거부(CS도 불가)\n"배송 시작 후에는 취소할 수 없습니다.\n반품 신청으로 처리해주세요";
  stop
endif

@enduml
```

---

## 4. 클레임(반품/교환) 프로세스

> v2 (2026-08-12 현행화): 12상태 확장 반영 (배송비 결제→수거→품질점검→합격/거부→환불/폐기/반송)
> v3 (2026-08-20 현행화): 14상태 반영 — 반송 배송비결제 대기(RETURN_PAYMENT_PENDING)·반송배송완료(RETURN_DELIVERED) 상태 보강
> v4 (2026-08-20 현행화): 교환(EXCHANGE) "맞교환" 원칙 반영 — PICKUP 진입 시 교환상품 선출고, 품질점검 판정 기준을 EXCHANGE는 택(TAG) 유지 여부로 명시
> v6 (2026-10-29 현행화): INSPECTING 진입 시점을 "수거 shipment(PICKUP) 입고 확인 시"로 명시(REQ-ORD-031·032, 귀책 판정 직후 아님), 고객 자진 철회(REQ-ORD-073)·INSPECTING 이후 취소 거부(REQ-ORD-071) 분기 추가.
> v5 (2026-08-20 현행화): 배송 실행(PICKUP/RETURN_SHIPPING/RETURN_DELIVERED)을 `ord_shipment`로 분리(상태머신(DH) v6) — 11상태로 축소. 수거·반송 배송은 shipment 하위 흐름으로 표시. VENDOR귀책 신청 시 사진 1장 필수(REQ-ORD-058) 반영.

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title 클레임 비즈니스 프로세스 (확장)

|고객|
start
:반품/교환 신청\n(주문상세에서 아이템 선택, 사유·회수지 입력\nVENDOR귀책 사유 선택 시 사진 1장 이상 필수 — REQ-ORD-058);

|시스템(Order)|
if (배송완료 후 10일 이내?) then (yes)
  :클레임 생성 (RECEIVED);
else (no)
  :신청 거부\n"기한이 초과되었습니다";
  stop
endif

note right
  고객 자진 철회 (REQ-ORD-073):
  RECEIVED·PAYMENT_PENDING 상태에서
  → REJECTED (사유 "고객 자진 철회")
  INSPECTING 이후(귀책판정·수거 시작 후)는
  취소 거부 (REQ-ORD-071)
end note

|어드민|
if (접수 승인?) then (yes)
  :귀책사유 확인·귀책 판정;
  if (고객(CUSTOMER) 귀책?) then (yes)
    :배송비 결제 요청 (PAYMENT_PENDING)\n알림톡 발송;
    |고객|
    if (24시간 내 결제?) then (yes)
      :수거 배송비 결제 완료\n(쿠폰 적용 가능)\n→ shipment(PICKUP) 생성;
    else (no)
      :자동 취소 (PAYMENT_EXPIRED)\n알림톡 발송;
      stop
    endif
  else (판매자(VENDOR) 귀책)
    :배송비 불필요\n→ shipment(PICKUP) 즉시 생성;
  endif
else (no)
  :반려 (REJECTED)\n알림톡 발송;
  stop
endif

note right
  EXCHANGE(교환) 유형: 귀책판정 완료 시점에
  shipment(EXCHANGE_OUT) 병렬 생성 →
  교환상품 선출고 (맞교환 원칙,
  선출고 후 수취 — REQ-ORD-056)
end note

|판매자|
:수거 운송장 등록\n→ shipment(PICKUP) IN_TRANSIT;
:판매자 [입고 확인](API-038)\n→ shipment(PICKUP) DELIVERED, 클레임 상태 → INSPECTING;
:품질점검;
note right
  판정 기준:
  RETURN → 상품 상태(훼손 여부)
  EXCHANGE → 택(TAG) 유지 여부
  (REQ-ORD-057)
end note

if (합격?) then (yes)
  :수거완료 (PICKED_UP);
  if (교환(EXCHANGE)?) then (yes)
    |시스템(Order)|
    :선출고한 shipment(EXCHANGE_OUT)\n배송완료(고객 수령) 확인 (합격 후 또는 이미 수령)\n→ 클레임완료 (COMPLETED)\n환불 없음, CLAIM_COMPLETED 발행, 알림톡;
    stop
  endif
else (no)
  :수거거부 (PICKUP_REJECTED)\n사유 등록;

  |어드민|
  if (반송 가능?) then (yes)
    :반송 배송비 추가결제 요청 (RETURN_PAYMENT_PENDING)\n고객 알림톡;
    |고객|
    :반송 배송비 결제 완료;
    |판매자|
    :반송 운송장 등록\n→ shipment(RETURN) IN_TRANSIT;
    |시스템(Order)|
    :반송 배송완료 확인(택배사 API)\n→ shipment(RETURN) DELIVERED;
    :클레임완료 (COMPLETED)\n(배치 자동전환, 알림톡);
    stop
  else (no)
    :폐기 처리 (DISPOSED)\n→ 클레임완료 (COMPLETED);
    stop
  endif
endif

|어드민|
:환불 처리 [환불 처리](API-029)\n→ Payment에 환불 요청;
note right
  원결제수단 PG 환불
  또는 계좌이체(수동)
  - 입금정보 시스템 등록
  - 이체 행위 휴먼 진행
  - 환불완료 처리
end note
:환불완료 (REFUNDED);

|시스템(Order)|
:클레임완료 (COMPLETED)\n알림톡+이메일 발송;
note right: CLAIM_COMPLETED 발행 (환불 트리거 아님)\n→ 정산·알림\n→ Catalog(재고 복원)\n→ Member(포인트 복원)
stop

@enduml
```

---

## 근거

| 항목 | 출처 |
|---|---|
| 상태 전이 | `../DH-상태머신/order.md` |
| 액터·업무 흐름 | `../DC-상위유스케이스/order.md` |
| 도메인 간 호출 | `DB-도메인정의서.md` §4 관계도 |
| 업무 규칙 | REQ-ORD-015 (D+11), REQ-ORD-019 (취소 제한), REQ-ORD-030 (반품 10일), REQ-ORD-058 (VENDOR귀책 사진 필수) |
| 배송 실행 분리(ord_shipment) | REQ-ORD-059~062 |
| 비동기 접수·재고차감·가상계좌 발급·입금대기 | REQ-ORD-008·012·013·014·077·078·079 |
| 입금대기 취소·구매확정 후 어드민 접수·취소 클레임 | REQ-ORD-080·081·082 |
| 클레임 자진 철회·INSPECTING 진입 시점 | REQ-ORD-071·073, REQ-ORD-031·032 |
| 자동 구매확정 제외(진행 중 클레임) | 정책서 5.6.2 |
