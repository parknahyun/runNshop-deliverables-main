# EARS 기능요구사항 — Order

> **단계**: 구조설계
> **문서범위**: Domain
> **문서종류**: Spec
>
> **작성 목적**: 상위 유스케이스(DC)를 기반으로, Order 도메인의 기능요구를 EARS 패턴으로 정형화한다.
> **흐름 내 위치**: DC 상위 UC → **DD EARS** → DE 메뉴구조도 → DF ERD → DG 비즈니스 프로세스 → DH 상태머신
> **작성 주체**: 시니어 개발자 + AI 협업 (기획자·현업 검토·확인)
> **갱신일**: 2026-10-29
---

## 장바구니·주문서

| ID | 패턴 | 요구사항 | 도출 근거 |
|---|---|---|---|
| REQ-ORD-001 | Event-driven | WHEN 고객이 상품을 장바구니에 담으면, THE 시스템은 SHALL 해당 상품·옵션·수량을 장바구니에 저장한다. | 상위UC: 장바구니 담기 |
| REQ-ORD-002 | Event-driven | WHEN 고객이 장바구니 상품의 수량을 변경하면, THE 시스템은 SHALL 변경된 수량으로 갱신하고 소계를 재계산한다. | 상위UC: 수량 변경 |
| REQ-ORD-003 | Event-driven | WHEN 고객이 장바구니 상품을 삭제하면, THE 시스템은 SHALL 해당 항목을 논리 삭제(is_deleted)한다. | 상위UC: 삭제 |
| REQ-ORD-004 | Unwanted | IF 장바구니 상품 수가 50개를 초과하면, THEN THE 시스템은 SHALL 추가를 거부하고 "장바구니가 가득 찼습니다" 메시지를 반환한다. | 정책: 최대 50개 |
| REQ-ORD-005 | Ubiquitous | THE 시스템은 SHALL 동일 상품+옵션 조합이 이미 장바구니에 존재하면 수량을 합산한다. | 정책: 중복 방지 |
| REQ-ORD-006 | Event-driven | WHEN 비회원이 로그인하면, THE 시스템은 SHALL 비회원 장바구니를 회원 장바구니에 병합한다. | 정책: 병합 규칙 |
| REQ-ORD-007 | Event-driven | WHEN 고객이 바로구매를 선택하면, THE 시스템은 SHALL 장바구니를 거치지 않고 즉시 주문서로 이동한다. | 상위UC: 바로구매 |
| REQ-ORD-008 | Event-driven | WHEN 고객이 결제하기를 요청하면, THE 시스템은 SHALL 주문서(임시주문)에 저장된 상품·쿠폰·포인트를 다시 검증하고 배송지·결제수단·필수 약관 동의를 확인한 뒤 주문을 접수(TEMP→STOCK_REQUESTED)한다. | 상위UC: 주문서 제출 (2026-10-29 비동기 접수 기준으로 개정) |
| REQ-ORD-009 | Ubiquitous | THE 시스템은 SHALL 주문서에서 적용해 저장한 할인·쿠폰·포인트 내역을 주문 접수 시점에 재검증한 뒤 주문에 스냅샷으로 확정 저장하고, 주문금액(상품금액 − 할인금액 + 배송비 − 배송비 할인금액)과 결제금액(주문금액 − 포인트)을 산출한다. | 정책: 주문 시점 가격 확정 (2026-10-29 개정) |
| REQ-ORD-010 | Unwanted | IF 결제하기 시 필수 정보(배송지, 결제수단, 필수 약관 동의)가 누락되면, THEN THE 시스템은 SHALL 주문 접수를 거부하고 누락 항목을 안내한다. 주문서가 이미 진행됐거나 타인의 것이거나 없으면 접수를 거부한다. | 유효성 검증 (2026-10-29 개정) |
| REQ-ORD-011 | Ubiquitous | THE 시스템은 SHALL 주문 생성 시 판매자별로 주문을 분할한다 (1 플랫폼주문 → N 판매자주문). | 정책: 판매자별 처리 단위 |

> **(2026-10-19/20 구현 확인/실제 구현 반영)**: REQ-ORD-008("배송지·결제수단·쿠폰 적용 여부를 검증")의 결제수단 허용값은 `CARD`/`EASY_PAY`/`POINT`/`VIRTUAL_ACCOUNT` 4종이다(`VIRTUAL_ACCOUNT`는 2026-10-19 결제수단 노출 작업에서 추가). 근거: `OrderService.kt.validatePayRequest()`의 허용 Set(`setOf("CARD", "EASY_PAY", "POINT", "VIRTUAL_ACCOUNT")`, 681행) — 재확인 시점 코드 일치.
>
> **(2026-10-23 실제 구현 반영)**: REQ-ORD-007(바로구매)·REQ-ORD-008(주문서 제출)이 다루는 "주문서로 이동"·"주문 생성" 대상 상품은 장바구니에서 고객이 선택한 상품으로 제한된다 — 장바구니(mobile `CartClient.tsx`)에서 상품별 체크박스로 선택한 `product_id` 집합만 주문서(`orders[]`)에 전달되고(미선택 상품은 주문서 화면에 표시되지 않음), 주문서 생성(`POST .../orders/sheet`) 이후의 결제하기(`POST .../pay`)는 주문서에 저장된 선택 상품(임시주문)만 대상으로 한다(2026-10-26부터 요청 바디 `items[]`는 무시). 기본값은 "품절이 아닌 상품 전체 선택"이라 아무것도 선택 해제하지 않으면 기존과 동일하게 전체 상품이 주문·결제된다(하위호환). 쿠폰/약관 상세보기(상세 조건·전문을 보여주는 모달 추가)는 기존 값을 추가로 보여주는 UI일 뿐 새로운 비즈니스 규칙이 아니라고 판단해 이 EARS 문서에는 반영하지 않는다. 근거: `.agents/tasks/mobile-order-ux-gaps/design.md` 결정 2.

---

## 주문결제·연동

| ID | 패턴 | 요구사항 | 도출 근거 |
|---|---|---|---|
| REQ-ORD-012 | Event-driven | WHEN 고객이 결제하기를 요청하면, THE 시스템은 SHALL 주문 접수와 같은 트랜잭션으로 재고차감 요청을 아웃박스에 적재하고 즉시 접수 응답(STOCK_REQUESTED)을 반환한다. 재고 차감과 PG 요청은 접수 응답에 포함되지 않고 비동기로 처리한다. | 상위UC: 결제 요청 (2026-10-29 비동기 접수 기준으로 개정 — 구 "재고 선점 후 결제 요청 전달"은 폐기) |
| REQ-ORD-013 | Event-driven | WHEN Payment 도메인으로부터 결제완료(PAYMENT_APPROVED) 이벤트 또는 가상계좌 입금 통보를 수신하면, THE 시스템은 SHALL 주문 상태를 입금대기(DEPOSIT_PENDING) 또는 결제 인증 대기에서 PAYMENT_COMPLETED로 전환한다. | 도메인정의서 §4: Payment→Order (2026-10-29 상태명 현행화 — 입금 통보 처리는 미구현). 프로토타입 결제수단은 가상계좌(DEPOSIT_PENDING 경로)뿐이며, 카드·간편결제(EASY_PAY)의 PAYMENT_APPROVED·결제 인증 대기 경로는 본개발 설계안이다(DH·DM에 상태 전이 미정의) |
| REQ-ORD-014 | Unwanted | IF Payment 도메인으로부터 결제실패(PAYMENT_FAILED) 이벤트를 수신하거나 가상계좌 입금기한(발급 후 12시간)이 만료되면, THEN THE 시스템은 SHALL 차감된 재고를 복원하고 주문을 PAYMENT_FAILED(결제 실패) 또는 CANCELLED(입금기한 만료)로 전환한다. | 도메인정의서 §4 + 정책 (2026-10-29 개정 — 보상·만료 처리는 미구현) |
| REQ-ORD-015 | Event-driven | WHEN 배송완료 후 11일(배송완료 일시 + 11×24시간)이 경과하면, THE 시스템은 SHALL 자동으로 구매확정(CONFIRMED) 처리한다. | 정책: D+11 자동 구매확정 (2026-10-29 개정: 구 7일 — 반품·교환 접수 10일(REQ-ORD-030)이 끝난 뒤 확정되도록 11일). 반품·교환 진행 중인 건은 제외(정책 5.6.2) |
| REQ-ORD-016 | Event-driven | WHEN 고객이 수동 구매확정을 요청하면, THE 시스템은 SHALL 즉시 구매확정 처리한다. | 상위UC: 구매확정(수동) |
| REQ-ORD-017 | Event-driven | WHEN CS 담당자가 예외 취소를 요청하면, THE 시스템은 SHALL 주문이 PREPARING이고 출고 shipment(OUTBOUND)가 PENDING(송장 미등록)인 경우에 한해 결제 상태와 무관하게 취소를 수행하고 환불을 요청하며, 송장이 등록된 뒤(IN_TRANSIT 이후)에는 취소를 거부한다. | 상위UC: 예외 취소 (CS 전용). 2026-10-29 확정: 송장 등록 전 한정(정책 7.3.3), 송장 등록과 취소가 경합하면 먼저 커밋된 쪽 우선(5.8.3) |
| REQ-ORD-018 | Event-driven | WHEN 고객이 단순 취소를 요청하면, THE 시스템은 SHALL 입금대기(DEPOSIT_PENDING) 또는 PAYMENT_COMPLETED 상태인 경우에만 취소를 허용한다(2026-10-29 입금대기 취소 허용 확정). | 정책 5.4.1: 결제완료까지 즉시취소, 출고 전 취소만 가능 |
| REQ-ORD-019 | Unwanted | IF 고객 취소 요청 시 주문 상태가 PREPARING 이후이면, THEN THE 시스템은 SHALL 취소를 거부하고, 준비중(송장 등록 전)이면 "고객센터로 문의해주세요", 배송중(송장 등록 후)이면 "배송완료 후 반품을 이용해주세요" 메시지를 반환한다. | 정책: 출고 후 취소 불가. 준비중 취소는 시스템 프로세스 없이 고객 유선 요청 → 어드민 접수(REQ-ORD-017, 2026-10-29 확정) |
| REQ-ORD-020 | Ubiquitous | THE 시스템은 SHALL 구매확정 시 Settlement 도메인에 정산 대상 등록 이벤트를 발행한다. | 도메인정의서: Order→Settlement |
| REQ-ORD-021 | Ubiquitous | THE 시스템은 SHALL 구매확정 시 Member 도메인에 포인트 적립 이벤트를 발행한다. | 도메인정의서: Order→Member |
| REQ-ORD-077 | Event-driven | WHEN 재고 차감이 완료되어 PG 결제요청 이벤트(`PAYMENT_REQUESTED`)가 처리되면, THE 시스템은 SHALL (현재 프로토타입 범위에서) Payment 도메인에 결제 요청을 전달해 가상계좌를 발급하고 주문 상태를 DEPOSIT_PENDING(입금대기)으로 전환한다. | 실제 구현 반영(2026-10-19/20), 2026-10-29 비동기 접수 기준으로 개정 — `OrderEventHandler`, `DM-시퀀스/order.md` §4-1 |
| REQ-ORD-078 | Event-driven | WHEN 컨슈머가 재고차감 요청(`STOCK_DEDUCT_REQUESTED`)을 처리하면, THE 시스템은 SHALL Catalog 상품 API로 SKU 단위로 재고를 멱등 차감하고, 전 SKU가 성공하면 주문 상태를 STOCK_DEDUCTED로 전환한 뒤 `PAYMENT_REQUESTED` 이벤트를 적재한다. 같은 이벤트를 중복 처리해도 재고는 이중 차감하지 않는다. | 신규(2026-10-29) — 구현 반영 `OrderEventHandler`, `CatalogApi.deductStock`, DM §4-1 |
| REQ-ORD-079 | Unwanted | IF 재고차감 처리에서 일부 SKU의 재고가 부족하면, THEN THE 시스템은 SHALL 성공한 SKU의 차감은 유지하고 실패한 SKU만 백오프 후 재시도하며, 재시도가 3회 소진되면 성공 SKU의 차감분을 복원하고 주문을 STOCK_FAILED로 전환한다. | 신규(2026-10-29) — 구현 반영 `give-up` 처리, DM §4-1 (재고부족 고객 알림은 미구현) |
| REQ-ORD-080 | Event-driven | WHEN 고객이 입금대기(DEPOSIT_PENDING) 주문을 취소하면, THE 시스템은 SHALL 발급된 가상계좌를 폐기하고 차감된 재고를 복원하며 주문을 CANCELLED로 전이한다. 입금 전 취소는 환불이 발생하지 않는다. | 2026-10-29 신규, 미구현(고객 취소 API 없음). 입금 통보와 취소가 경합하면 **취소 우선**(2026-10-29 확정) — 입금이 이미 반영됐더라도 취소를 유지하고 입금액을 환불한다(REQ-PAY-030) |
| REQ-ORD-081 | Event-driven | WHEN 주문상품이 구매확정(CONFIRMED)된 뒤 고객이 모바일에서 반품·교환을 신청하면, THE 시스템은 SHALL 신청을 거부하고 고객센터 문의를 안내한다. WHEN CS 담당자가 구매확정 후 하자·오배송(VENDOR 귀책) 건을 어드민에서 접수하면, THE 시스템은 SHALL 배송완료 후 3개월 또는 그 사실을 안 날부터 30일 이내인 경우 사진 증빙을 받아 클레임(RECEIVED)으로 접수하고 주문상품은 CONFIRMED를 유지한다. 단순변심은 구매확정 후 접수하지 않는다. | 신규(2026-10-29) — 정책서 7.2.1·7.2.3, 정산 차감 settlement 10.4.3·포인트 회수 payment 8.6.4 (미구현). 어드민 클레임 접수 API는 DL에 없음(확인 필요). 기한(3개월·30일)을 모두 넘긴 하자도 같은 어드민 경로(운영자 승인, 정책서 7.2.3)로 접수한다 |
| REQ-ORD-082 | Event-driven | WHEN 고객 직접 취소(입금대기·결제완료) 또는 어드민 예외 취소(REQ-ORD-017)가 처리되면, THE 시스템은 SHALL 같은 트랜잭션에서 claim_type=CANCEL 클레임을 생성한다(신청경로: 고객=SELF, 어드민=CS, 사유·환불금액 포함). 취소 클레임은 수거·검수·귀책 판정·배송비 결제를 거치지 않으며, 환불이 없는 입금대기 취소는 RECEIVED에서 바로 COMPLETED로, 환불이 필요한 취소는 RECEIVED→REFUNDED→COMPLETED로 종료한다. | 신규(2026-10-29) — 정책서 7.1.1, DF ord_claim, 클레임 목록·통계·정산 연계용 (미구현). 상태 흐름 확정(2026-11-03). 응답에 claimNo 포함 |

> **(2026-10-29 비동기 접수 기준 개정)**: 결제하기는 **접수만 동기**로 처리하고(REQ-ORD-008·012) 재고차감(REQ-ORD-078·079)과 PG 요청(REQ-ORD-077)은 컨슈머가 비동기로 처리한다. 주문 상태는 TEMP → STOCK_REQUESTED → STOCK_DEDUCTED → DEPOSIT_PENDING(재고 부족 시 STOCK_FAILED)이며, 옛 `ORDER_RECEIVED`/`PAYMENT_PENDING`과 "재고 선점 후 결제 요청 전달"은 폐기했다. REQ-ORD-013(입금 통보·PAYMENT_APPROVED 기반 결제완료)과 REQ-ORD-014(실패·입금기한 만료 보상)는 본개발 설계로 유지하며 현재 프로토타입에서는 미구현이다(Bolt8 SC18-1, Bolt14 SC10-1·SC28-3). 근거: `OrderService.placeOrder()`, `OrderEventHandler`, `DH-상태머신/order.md` 구현 현행화(2026-10-26), `DM-시퀀스/order.md` §4·§4-1, 정책서 payment.md 4.4.1(입금기한 12시간). 이전 개정 이력: REQ-ORD-077은 2026-10-19/20에 "결제 요청 성공 시 DEPOSIT_PENDING 생성"(동기 모델)으로 추가됐다.

---

## 배송관리

> v2 (2026-08-20 현행화): 배송 실행(택배사·운송장·집화/배송중/배송완료)을 `ord_shipment`로 분리(상태머신(DH) v6). 주문 상태(IN_DELIVERY 제거)는 더 이상 배송 진행을 직접 표현하지 않는다.

| ID | 패턴 | 요구사항 | 도출 근거 |
|---|---|---|---|
| REQ-ORD-022 | Event-driven | WHEN 판매자가 출고 처리를 요청하면, THE 시스템은 SHALL 주문 상태를 PREPARING으로 전환한다. | 상위UC: 출고 처리 |
| REQ-ORD-023 | Event-driven | WHEN 판매자가 운송장 번호를 등록하면, THE 시스템은 SHALL shipment(OUTBOUND)를 생성하고 상태를 IN_TRANSIT으로 전환한다 (주문 상태는 PREPARING 유지). | 상태머신: ord_shipment PENDING→IN_TRANSIT |
| REQ-ORD-024 | Event-driven | WHEN 택배사 API로부터 배송완료 신호를 수신하면, THE 시스템은 SHALL shipment(OUTBOUND) 상태를 DELIVERED로 전환하고, 이를 구독하여 주문 상태를 DELIVERED로 파생 전환한다. | 상태머신: ord_shipment IN_TRANSIT→DELIVERED → ord_order PREPARING→DELIVERED |
| REQ-ORD-025 | Event-driven | WHEN 고객이 배송지 변경을 요청하면, THE 시스템은 SHALL 입금대기(DEPOSIT_PENDING)·결제완료(PAYMENT_COMPLETED)(출고 지시 전) 상태에서만 변경을 허용한다. 준비중(PREPARING)은 고객센터 요청(정책서 6.12.2), 송장 등록 후는 변경 불가(반품 후 재주문). | 상위UC: 배송지 변경 (2026-11-03 허용 상태 확정) |
| REQ-ORD-026 | Unwanted | IF 고객이 모바일에서 배송지 변경을 요청했는데 주문 상태가 PREPARING 이후이면, THEN THE 시스템은 SHALL 변경을 거부하고, 준비중(송장 등록 전)이면 "고객센터로 문의해주세요"(어드민 수작업, 정책서 6.12.2), 송장 등록 후이면 "출고 후에는 변경할 수 없습니다(반품 후 재주문)" 메시지를 반환한다. | 정책: 준비중은 고객센터 문의, 송장 후 변경 불가 (2026-11-03 허용 상태 확정, REQ-ORD-025와 대응). CS 대행 변경 API는 미설계 |
| REQ-ORD-027 | State-driven | WHILE shipment(OUTBOUND)가 IN_TRANSIT 상태인 동안, THE 시스템은 SHALL 60분 주기로 택배사 API에 배송 상태를 조회한다. | 정책: 배치 주기 |

---

## 클레임처리

> v2 (2026-08-20 현행화): REQ-ORD-031/032/034가 폐기된 구모델(IN_PROGRESS 등)을 참조하고 있어 실제 귀책판정·환불 흐름(상태머신(DH))에 맞게 재정의. responsibility는 CUSTOMER/VENDOR 2종(PLATFORM 제거).

| ID | 패턴 | 요구사항 | 도출 근거 |
|---|---|---|---|
| REQ-ORD-028 | Event-driven | WHEN 고객이 반품을 신청하면, THE 시스템은 SHALL 클레임을 RECEIVED 상태로 생성한다. | 상위UC: 반품 신청 |
| REQ-ORD-029 | Event-driven | WHEN 고객이 교환을 신청하면, THE 시스템은 SHALL 클레임을 RECEIVED 상태(EXCHANGE 유형)로 생성한다. | 상위UC: 교환 신청 |
| REQ-ORD-030 | Unwanted | IF 단순변심 반품/교환 신청 시 배송완료 후 10일(배송완료 일시 + 10×24시간)이 초과되었으면, THEN THE 시스템은 SHALL 신청을 거부하고 "기한이 초과되었습니다" 메시지를 반환한다. | 정책: 단순변심 반품 기한 10일. 하자·오배송(VENDOR 귀책)은 배송완료 후 3개월 또는 안 날부터 30일(정책서 7.2.2, 기산 배송완료 일시 + N×24시간)로 별도 판정한다. 구매확정 후 접수는 REQ-ORD-081(어드민 접수만, 2026-10-29) |
| REQ-ORD-031 | Event-driven | WHEN CS 담당자가 접수 내용을 확인해 판매자(VENDOR) 귀책으로 판정하면, THE 시스템은 SHALL shipment(PICKUP)를 생성하고 수거를 즉시 시작한다(배송비 없음). | 상태머신: RECEIVED 유지, shipment(PICKUP) 생성(v6) |
| REQ-ORD-032 | Event-driven | WHEN shipment(PICKUP)가 판매자의 입고 확인으로 DELIVERED 상태가 되면, THE 시스템은 SHALL 클레임 상태를 INSPECTING(품질점검)으로 전환한다. | 상태머신: RECEIVED/PAYMENT_PENDING→INSPECTING(v6, 파생전환) |
| REQ-ORD-033 | Event-driven | WHEN CS 담당자가 클레임을 반려하면, THE 시스템은 SHALL 클레임 상태를 REJECTED로 전환하고 사유를 기록한다. | 상위UC: 반려확정 |
| REQ-ORD-034 | Event-driven | WHEN CS 담당자가 어드민 [환불 처리](API-029)를 수행하면, THE 시스템은 SHALL 클레임 상태를 REFUNDED로 전환하고 Payment에 환불을 요청한다(클레임 환불의 유일한 트리거). 재고복원은 Catalog 이벤트로 처리한다. | 상태머신: PICKED_UP→REFUNDED (2026-11-03 환불 트리거 단일화, REQ-PAY-009). 교환은 환불이 없다 |
| REQ-ORD-035 | Ubiquitous | THE 시스템은 SHALL 클레임이 COMPLETED로 전환될 때 CLAIM_COMPLETED 이벤트를 발행한다(정산·알림·Catalog 재고복원·Member 포인트복원 용도). CLAIM_COMPLETED는 환불 트리거가 아니며 Payment는 이 이벤트로 환불하지 않는다. | 도메인정의서: 이벤트 발행 (2026-11-03 정정). 교환은 맞교환 출고(EXCHANGE_OUT) 배송완료(고객 수령) 시 COMPLETED(REQ-ORD-083) |

---

## 주문 조회·관리

| ID | 패턴 | 요구사항 | 도출 근거 |
|---|---|---|---|
| REQ-ORD-036 | Event-driven | WHEN 고객이 주문 목록을 조회하면, THE 시스템은 SHALL 본인 주문만 최신순으로 반환한다. | 상위UC: 내 주문 조회 |
| REQ-ORD-037 | Event-driven | WHEN 판매자가 주문 목록을 조회하면, THE 시스템은 SHALL 자기 매장 주문만 반환한다. | 상위UC: 판매자 주문 조회 |
| REQ-ORD-038 | Event-driven | WHEN CS 담당자가 주문을 검색하면, THE 시스템은 SHALL 상태·기간(주문일시 `ordered_at` 기준)·키워드 필터를 지원한다. 키워드는 주문번호·상품명·주문자명(주문 시점 `orderer_name` 스냅샷) 모두 부분 일치(대소문자 무시)로 검색하며 판매자명 검색은 제외한다. | 상위UC: 전체 주문 검색 (2026-10-27 정책 확인 회신 반영) |
| REQ-ORD-039 | Ubiquitous | THE 시스템은 SHALL 모든 주문 상태 변경 시 이력(ord_status_history)을 기록한다. | 감사 추적 |

> **(2026-10-19/20 구현 확인/실제 구현 반영)**: REQ-ORD-036/037("본인/자기매장 주문만 반환")의 조회 집계 단위를 보완한다 — admin·mobile은 플랫폼주문(`ord_platform_order`) 1건을 1줄로 집계해 목록/상세를 보여주고, partner는 판매자주문(`ord_order`) 1건을 1줄로 유지하되 상세에서 같은 플랫폼주문에 속한 타 vendor 상품을 상품명/수량/금액만 참조로 노출한다(액션 버튼 없음). 근거: `.agents/tasks/order-platform-order-channel-redesign/design.md` §1(전체 결정 요약 표), §3-2/§3-4(admin·mobile `PlatformOrder` 기준 상세), §3-6(partner `myItems`/`otherVendorItems`).

---

## 클레임 확장 (배송비 결제·수거·품질점검·폐기·반송)

> v2 (2026-08-12 현행화): S3 상세설계에서 클레임 프로세스 확장에 따라 추가.
> v3 (2026-08-20 현행화): REQ-ORD-050 상태명 오기 수정(PAYMENT_PENDING(RETURN) → RETURN_PAYMENT_PENDING), 반송배송완료(RETURN_DELIVERED)·자동완료 전환 요구 신설(REQ-ORD-052/053), 장바구니 옵션변경 REQ 번호 이동(052/053 → 054/055).
> v6 (2026-08-20 현행화): 배송 실행(PICKUP/RETURN_SHIPPING/RETURN_DELIVERED 상태)을 `ord_shipment`로 분리 — REQ-ORD-041/044/045/051/052/053을 shipment 기준으로 재정의.

| ID | 패턴 | 요구사항 | 도출 근거 |
|---|---|---|---|
| REQ-ORD-040 | Event-driven | WHEN 고객 귀책 클레임이 접수되면, THE 시스템은 SHALL 클레임 상태를 PAYMENT_PENDING으로 전환하고 수거 배송비 결제를 요청한다. 단순변심 반품의 수거 배송비 = 편도 반품 배송비 3,000원 + 초도 배송비 중 할인받은 금액(무료배송 면제분·배송비 쿠폰 할인분, 정책서 6.9.7)이며 서버가 산정한다. | 정책: 고객 귀책 배송비 부담 (2026-10-29: 금액 산정 규칙 확정) |
| REQ-ORD-041 | Event-driven | WHEN 고객이 수거 배송비를 결제하면, THE 시스템은 SHALL shipment(PICKUP)를 생성하고 수거 프로세스를 시작한다(클레임 상태는 PAYMENT_PENDING 유지, INSPECTING 전환은 REQ-ORD-032 참조). | 상태머신: ord_shipment 생성(v6) |
| REQ-ORD-042 | Unwanted | IF 수거 배송비가 24시간 내 결제되지 않으면, THEN THE 시스템은 SHALL 클레임을 자동 취소(PAYMENT_EXPIRED)하고 고객에게 알림톡을 발송한다. | 정책: 결제 기한 24시간 |
| REQ-ORD-043 | Event-driven | WHEN 결제 대기 12시간이 경과하면, THE 시스템은 SHALL 미결제 리마인드 알림톡을 발송한다. | 정책: 신속 처리 유도 |
| REQ-ORD-044 | Event-driven | WHEN 판매자가 수거 운송장을 등록하면, THE 시스템은 SHALL shipment(PICKUP) 상태를 IN_TRANSIT으로 전환하고 수거 택배 추적을 시작한다. | 상태머신: ord_shipment PENDING→IN_TRANSIT |
| REQ-ORD-045 | Event-driven | WHEN 판매자가 [입고 확인](API-038)을 수행하면(배치가 아닌 판매자 액션), THE 시스템은 SHALL shipment(PICKUP) 상태를 DELIVERED로 전환한다(클레임 상태의 INSPECTING 전환은 REQ-ORD-032). | 상태머신: ord_shipment IN_TRANSIT→DELIVERED |
| REQ-ORD-046 | Event-driven | WHEN 판매자가 품질점검 합격을 판정하면, THE 시스템은 SHALL 클레임 상태를 PICKED_UP(수거완료)으로 전환한다. | 상태머신: INSPECTING→PICKED_UP |
| REQ-ORD-047 | Event-driven | WHEN 판매자가 품질점검 거부를 판정하면, THE 시스템은 SHALL 클레임 상태를 PICKUP_REJECTED(수거거부)로 전환하고 거부 사유를 기록한다. | 상태머신: INSPECTING→PICKUP_REJECTED |
| REQ-ORD-048 | Unwanted | IF 판매자가 거부 사유 없이 품질점검 거부를 시도하면, THEN THE 시스템은 SHALL 거부를 차단하고 사유 입력을 요구한다. | 정책: 사유 필수 |
| REQ-ORD-049 | Event-driven | WHEN 어드민이 수거거부 건에 대해 폐기를 결정하면, THE 시스템은 SHALL 클레임 상태를 DISPOSED로 전환한다. | CS 운영: 반송 불가 판단 |
| REQ-ORD-050 | Event-driven | WHEN 어드민이 수거거부 건에 대해 반송 배송비 추가결제를 요청하면, THE 시스템은 SHALL 고객에게 반송 배송비(편도 3,000원 고정, 정책서 6.9.7) 결제 알림톡을 발송하고 RETURN_PAYMENT_PENDING으로 전환한다. | CS 운영: 반송 결정 (2026-10-29 금액 확정) |
| REQ-ORD-051 | Event-driven | WHEN 반송 배송비 결제 완료 후 판매자가 반송 운송장을 등록하면, THE 시스템은 SHALL shipment(RETURN)를 생성하고 상태를 IN_TRANSIT으로 전환한다(클레임 상태는 RETURN_PAYMENT_PENDING 유지). | 상태머신: ord_shipment 생성·전환(v6) |
| REQ-ORD-052 | Event-driven | WHEN 택배사가 반송 배송완료를 확인하면, THE 시스템은 SHALL shipment(RETURN) 상태를 DELIVERED로 전환한다. | 상태머신: ord_shipment IN_TRANSIT→DELIVERED |
| REQ-ORD-053 | Event-driven | WHEN shipment(RETURN)가 DELIVERED 상태에서 배치가 실행되면, THE 시스템은 SHALL 클레임 상태를 COMPLETED로 자동 전환하고 고객에게 완료 알림톡을 발송한다. | 상태머신: RETURN_PAYMENT_PENDING→COMPLETED(v6, shipment 파생) |

---

## 장바구니 옵션 변경

| ID | 패턴 | 요구사항 | 도출 근거 |
|---|---|---|---|
| REQ-ORD-054 | Event-driven | WHEN 고객이 장바구니 상품의 옵션을 변경하면, THE 시스템은 SHALL 변경된 SKU로 갱신하고 소계를 재계산한다. | 상위UC: 옵션 변경 |
| REQ-ORD-055 | Unwanted | IF 변경하려는 옵션의 잔여수량(실재고−장바구니 선점수량)이 0 이하이면, THEN THE 시스템은 SHALL 변경을 거부하고 "해당 옵션은 품절입니다" 메시지를 반환한다. | 정책: 품절 판정 |

---

## 클레임 확장 — 교환(맞교환 원칙)

> v4 (2026-08-20 신설): 교환은 "맞교환"을 전제로 한다 — 선출고 후 수취 순서이며, 수취 시 품질점검 기준은 택(TAG) 유지 여부로 판단한다. REQ-ORD-046/047(품질점검 합격/거부)을 EXCHANGE 유형에 한해 아래 기준으로 특화한다.
> v6 (2026-08-20 현행화): REQ-ORD-056이 참조하던 PICKUP 상태가 ord_shipment로 이관됨에 따라 귀책판정 완료 시점 기준으로 재정의.

| ID | 패턴 | 요구사항 | 도출 근거 |
|---|---|---|---|
| REQ-ORD-056 | Event-driven | WHEN 클레임 유형이 EXCHANGE이고 귀책판정이 완료되면(고객귀책: 수거배송비 결제완료 / 판매자귀책: 판정 즉시), THE 시스템은 SHALL 교환 SKU 재고를 선점하고 shipment(EXCHANGE_OUT)를 생성해 교환상품을 즉시 선출고한다(원상품 수취 이전). | 정책: 맞교환 — 선출고 후 수취 |
| REQ-ORD-057 | Event-driven | WHEN 클레임 유형이 EXCHANGE이고 판매자가 회수 상품의 택(TAG) 부착 상태를 확인하면, THE 시스템은 SHALL 택이 유지된 경우 품질점검 합격(PICKED_UP)으로, 택이 제거·훼손된 경우 품질점검 거부(PICKUP_REJECTED)로 판정한다. | 상태머신: INSPECTING→PICKED_UP/PICKUP_REJECTED (EXCHANGE 특화 기준) |
| REQ-ORD-083 | Event-driven | WHEN 클레임 유형이 EXCHANGE이고 합격(PICKED_UP) 판정이 있으며 선출고한 교환 shipment(EXCHANGE_OUT)가 DELIVERED(고객 수령)인 상태가 되면(두 조건 중 늦게 충족되는 시점, 순서 무관), THE 시스템은 SHALL 클레임 상태를 COMPLETED로 전환하고 CLAIM_COMPLETED 이벤트를 발행한다. 교환은 환불이 없으므로 REFUNDED를 거치지 않는다. | 신규(2026-11-03) — 교환 종료 경로 확정, 상태머신 PICKED_UP→COMPLETED(EXCHANGE) |
| REQ-ORD-084 | Event-driven | WHEN 운영자가 부정·악용 주문 등으로 확인한 계정에 이용 제한을 요청하면, THE 시스템은 SHALL 제한 사유와 제한 내용(대상·기간)을 담아 Member 도메인에 이용 제한을 요청하고 요청자·일시를 접속·작업 이력에 남긴다. WHEN 이용 제한 회원이 주문서 진입·결제 요청·쿠폰 사용을 시도하면, THE 시스템은 SHALL Member 도메인의 이용 제한 상태를 조회해 요청을 거부한다. | 정책서 9.4.3·2.1.3, 2026-11-03 신규, 미구현. 제한 상태·사유·내용·이력의 소유는 Member 도메인. Port·에러코드·이의 신청 경로 미정. 정책서만 수용, 구현은 후속(WBS·DQ 미반영). EARS 유형 혼합: 앞 문장은 Event-driven(이용 제한 요청), 뒤 문장은 Unwanted(제한 회원 요청 거부)이며 하나의 REQ로 유지한다 |
| REQ-ORD-085 | Event-driven | WHEN 회원이 탈퇴하거나 주문 연도 기준 5년이 지나(주문 연도 + 6년 1월 1일 도래, 예: 2025년 주문은 2031-01-01) 마스킹 배치가 실행되면, THE 시스템은 SHALL 해당 주문·결제 이력을 삭제하지 않고 수령인·연락처·주소·환불계좌·주문자명·가상계좌·카드 데이터를 마스킹한다(결제 쪽 환불계좌·가상계좌·카드는 Payment에 요청, REQ-PAY-033). 금액·상태·일시는 유지한다. THE 시스템은 SHALL 화면 조회 시 위 항목을 보존 기간과 관계없이 항상 마스킹해 표시한다. | 정책서 11.3.4, 2026-11-03 신규, 미구현. 실행: 탈퇴 건 1일 1회 배치, 보존 기간 초과 건 연 1회 배치, 모두 익일 01:00(PG 로그는 저장 시 즉시 마스킹). 탈퇴 건 BAT-011·보존 기간 초과 건 BAT-012, Bolt16 WBS SC40-1·2. Payment 마스킹은 PaymentPublicApi API-060(SC40-4)으로 요청한다. EARS 유형 혼합: 배치 마스킹은 Event-driven, 화면 조회 시 항상 마스킹은 Ubiquitous이며 하나의 REQ로 유지한다 |
| REQ-ORD-086 | Event-driven | WHEN 고객이 클레임 배송비(수거·반송·교환 왕복)를 결제하면서 배송비 쿠폰을 지정하면(편도는 1장, 왕복 배송비는 2장 이상 보유 시 최대 2장), THE 시스템은 SHALL 서버가 산정한 클레임 배송비에 쿠폰 할인을 적용한 금액을 결제 금액으로 하고, PG 인증 결제금액이 이 금액과 다르면 AMOUNT_MISMATCH로 거부한다. 배송비 쿠폰이 아니거나 사용할 수 없는 쿠폰이면 COUPON_NOT_APPLICABLE(만료는 COUPON_EXPIRED, 지정 장수 초과도 COUPON_NOT_APPLICABLE)로 거부한다. | 정책서 6.9.7, 2026-11-03 신규, 미구현. 할인받은 초도 배송비 부과액에의 적용·쿠폰 복원은 확인 필요 |

> **확정(2026-11-03)**: 교환은 선출고다. 품질점검 불합격(택 미유지) 판정 시 이미 선출고된 교환상품에 대한 비용은 운영자가 **수작업으로 청구**한다(시스템 자동 청구·환불 없음, 정책서 7.5.5). [확인 필요: 청구 항목·금액 산정·청구 기한]

---

## 클레임 접수 — 증빙 사진

> v6 (2026-08-20 신설): 판매자(VENDOR) 귀책 사유(상품불량 등)로 신청 시 사진 증빙을 의무화. 고객(CUSTOMER) 귀책(단순변심 등)은 기존대로 선택.

| ID | 패턴 | 요구사항 | 도출 근거 |
|---|---|---|---|
| REQ-ORD-058 | Unwanted | IF 반품/교환 신청 시 사유가 판매자(VENDOR) 귀책(상품불량 등)인데 첨부 사진이 0장이면, THEN THE 시스템은 SHALL 신청을 거부하고 "상품 상태를 확인할 수 있는 사진을 1장 이상 첨부해주세요" 메시지를 반환한다. | CS 운영: 귀책사유 확인 증빙 |

---

## 배송 실행 (ord_shipment)

> v6 (2026-08-20 신설): 배송 실행(택배사 이동 구간)을 order/claim 공용 `ord_shipment`로 분리. 고객·판매자·CS가 판단하지 않는 순수 물류 구간을 담당한다.

| ID | 패턴 | 요구사항 | 도출 근거 |
|---|---|---|---|
| REQ-ORD-059 | Event-driven | WHEN 판매자가 운송장을 등록하면(출고/수거/반송/교환선출고 공통), THE 시스템은 SHALL 해당 shipment 상태를 PENDING에서 IN_TRANSIT으로 전환한다. | 상태머신: ord_shipment PENDING→IN_TRANSIT |
| REQ-ORD-060 | Event-driven | WHEN 택배사 API가 배송완료를 확인하면, THE 시스템은 SHALL shipment 상태를 DELIVERED로 전환한다. | 상태머신: ord_shipment IN_TRANSIT→DELIVERED |
| REQ-ORD-061 | Unwanted | IF 택배사 API가 배송실패·반송 신호를 보내면, THEN THE 시스템은 SHALL shipment 상태를 FAILED로 전환하고 CS 담당자에게 알림을 발송한다. | 정책: 배송 예외 처리 (기존 미모델링 구간 보완) |
| REQ-ORD-062 | Event-driven | WHEN 판매자 또는 CS 담당자가 FAILED 건에 대해 재발송 처리를 하면, THE 시스템은 SHALL shipment 상태를 PENDING으로 되돌리고 운송장을 재등록받는다. | 정책: 배송실패 재처리 |

---

## 바텀업 검토 보완 (2026-08-21 신설)

> S3 상세설계(화면레이아웃·인터페이스명세·GWT)를 역으로 검토해 발견한, S2에 근거 요구사항이 없던 항목을 보완한다.

| ID | 패턴 | 요구사항 | 도출 근거 |
|---|---|---|---|
| REQ-ORD-063 | Unwanted | IF 품절·판매중지 상품을 장바구니에 담으려 하면, THEN THE 시스템은 SHALL 담기를 거부하고 "현재 구매할 수 없는 상품입니다" 메시지를 반환한다. | 인터페이스명세 PRODUCT_NOT_AVAILABLE 역반영 |
| REQ-ORD-064 | Unwanted | IF 장바구니 수량이 1~99 범위를 벗어나면, THEN THE 시스템은 SHALL 변경을 거부하고 유효 범위를 안내한다. | 인터페이스명세 INVALID_QUANTITY 역반영 |
| REQ-ORD-065 | Unwanted | IF 클레임 첨부 이미지가 3장을 초과하면, THEN THE 시스템은 SHALL 추가 첨부를 거부한다. | ERD `ord_claim_image` "최대 3장" 역반영 |
| REQ-ORD-066 | Event-driven | WHEN CS 담당자가 귀책 판정을 확정하면, THE 시스템은 SHALL CS 판정 결과(CUSTOMER/VENDOR)를 `responsibility`에 기록한다. 고객이 신청 시 제출한 자진신고 값은 `submitted_responsibility`에 그대로 보존하며 덮어쓰지 않는다(REQ-ORD-076). 판정 전에는 `responsibility`를 비워 둔다(불일치 시 CS 판정이 최종). | CS 운영: 접수 심사 — 고객 자진신고는 참고값, CS 확정이 최종 (2026-10-29 정정 — 구 "덮어쓴다"는 REQ-ORD-076과 충돌) |
| REQ-ORD-067 | Ubiquitous | THE 시스템은 SHALL 반려(REJECTED)·만료(PAYMENT_EXPIRED)된 클레임의 수량을 "재신청 가능 수량" 계산에서 제외한다. | 상태머신(DH) "종료 상태(재신청 필요)" 주석 — 재신청 차단 방지 |
| REQ-ORD-068 | Unwanted | IF 클레임이 RECEIVED 상태로 24시간 이상 CS 미처리 상태이면, THEN THE 시스템은 SHALL CS 담당자에게 리마인드 알림을 발송한다. | 정책: PAYMENT_PENDING 12h 리마인드(REQ-ORD-043)와 동급 SLA |
| REQ-ORD-069 | Unwanted | IF 클레임 유형이 EXCHANGE이고 귀책판정 시점에 교환 SKU(exchangeSkuId) 재고가 없으면, THEN THE 시스템은 SHALL 귀책판정을 거부하고 "교환 가능한 재고가 없습니다" 메시지를 반환한다(선출고 전 단계에서 차단). | REQ-ORD-056 선행조건 — 재고선점 실패 시나리오 보완 |
| REQ-ORD-070 | Unwanted | IF 교환 신청 시 exchangeSkuId가 원 주문 상품(productId)과 다른 상품이면, THEN THE 시스템은 SHALL 신청을 거부한다. | 정책: 교환은 동일 상품 내 옵션(색상/사이즈) 변경만 허용 |
| REQ-ORD-071 | Unwanted | IF 클레임이 INSPECTING 상태 이후이면, THEN THE 시스템은 SHALL 고객의 자진 취소 요청을 거부한다(귀책판정·수거 시작 이후 취소 불가 — 주문 취소와 동일 원칙). | 상태머신(DH) PREPARING 이후 취소 불가 원칙과 대칭 |
| REQ-ORD-072 | Unwanted | IF 클레임 유형이 EXCHANGE이고 판매자가 품질점검 거부(택 미유지)를 판정하는데 사진이 0장이면, THEN THE 시스템은 SHALL 거부 처리를 차단하고 사진 첨부를 요구한다. | REQ-ORD-058(VENDOR귀책 사진 필수)과 대칭 — 판매자 판정도 증빙 필요 |

---

## 바텀업 재검증 보완 (2026-08-21 2차)

> 1차 보완(REQ-ORD-063~072)이 S3에 실제로 결선되는지 재검증한 결과, "요구사항은 있는데 대상 기능/필드/이력 자체가 없어 검증 불가"인 항목을 마저 보완한다.

| ID | 패턴 | 요구사항 | 도출 근거 |
|---|---|---|---|
| REQ-ORD-073 | Event-driven | WHEN 고객이 RECEIVED 또는 PAYMENT_PENDING 상태의 클레임을 자진 취소하면, THE 시스템은 SHALL 클레임 상태를 REJECTED로 전환하고 사유를 "고객 자진 철회"로 기록한다. | REQ-ORD-071(INSPECTING 이후 취소 거부)의 긍정 사례 — 취소 기능 자체가 없어 REQ-ORD-071을 검증할 대상이 없던 문제 해소 |
| REQ-ORD-074 | Ubiquitous | THE 시스템은 SHALL "재신청 가능 수량" 조회 시 반려(REJECTED)·만료(PAYMENT_EXPIRED) 클레임을 제외한 값을 API 응답 필드로 노출한다. | REQ-ORD-067 구체화 — 계산 로직이 필드로 실체화되지 않아 검증 불가였던 문제 해소 |
| REQ-ORD-075 | Ubiquitous | THE 시스템은 SHALL 클레임 첨부 이미지에 업로드 시점(고객 접수 시 / 판매자 품질점검 시)을 구분하는 값을 기록하며, "최대 3장" 제약은 접수 시점과 판정 시점에 각각 독립적으로 적용한다. | 접수 사진(REQ-ORD-058)과 판정 사진(REQ-ORD-072)이 같은 클레임에 공존할 때 서로를 침범하지 않도록 함 |
| REQ-ORD-076 | Ubiquitous | THE 시스템은 SHALL CS 귀책판정 확정 시 고객이 원래 제출한 responsibility 값을 덮어쓰지 않고 별도 이력으로 보존한다(`submitted_responsibility` vs 최종 `responsibility`). | REQ-ORD-066 구체화 — 단일 컬럼 덮어쓰기로 고객 자진신고 이력이 소실되던 문제 해소 |

---

## 근거

| 항목 | 출처 |
|---|---|
| 유스케이스 도출 | `../DC-상위유스케이스/order.md` |
| 정책 수치·규칙 | 자산 정책서 (장바구니 50개, D+11 자동확정, 반품 10일) |
| 도메인 간 연동 | `DB-도메인정의서.md` Order "의존·이벤트 발행" |
| 메뉴·화면 대응 | `DE-메뉴구조도/readme.md` Order 관련 화면 |
| 배송 실행 분리(ord_shipment) | 상태머신(DH) v6 — "판단·결정 지점만 order/claim status, 택배사 이동 구간은 shipment" 원칙 |
| 판매자귀책 사진 필수 | CS 운영 인터뷰 (귀책판정 증빙 필요) |
| 바텀업 검토 보완(REQ-ORD-063~072) | S3 상세설계(DL-인터페이스명세, DN-화면레이아웃, DF-ERD) 역검토 — 2026-08-21 |
| 바텀업 재검증 보완(REQ-ORD-073~076) | 2차 바텀업 재검증 — 기능/이력 실체 없이 요구사항만 있던 항목 보완, 2026-08-21 |
| 신규 REQ-ORD-077~082 | 077·078·079: 구현 반영(`OrderEventHandler`, DM §4-1) / 080 입금대기 취소·081 구매확정 후 어드민 접수·082 취소 클레임: 정책서 order.md 5.4·order-claim.md 7.1·7.2, 2026-10-29 결정 (DC·DF·DG·DH 반영: 상태머신(DH) §1·§2, DF `ord_claim.claim_type=CANCEL`, DG §1·§3) |
| 비동기 접수 개정(REQ-ORD-008·009·010·012·013·014·077, 신규 078·079) | 결제하기 접수만 동기, 재고차감·PG 요청 비동기 — 구현(`OrderService`·`OrderEventHandler`)·DH 구현 현행화·DM §4-1 기준, 2026-10-29 (개발 검토 F1·F4 후속) |
