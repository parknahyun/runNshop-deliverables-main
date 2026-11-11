# 세부 유스케이스 — Order 도메인

> 상위 문서: [readme.md](readme.md)
> **단계**: 상세설계 (S3) | **문서범위**: Bolt (Order) | **문서종류**: Design
> Payment 관련 시나리오는 [DK-세부유스케이스/payment.md](payment.md) 참조

---

## 1. [장바구니 담기] 장바구니 담기 Bolt

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title §1 [장바구니 담기] 장바구니 담기

|고객|
start
:상품상세에서 옵션(색상/사이즈) 선택;
:수량 입력 (기본 1);
:"장바구니 담기" 클릭;

|시스템|
:POST /api/mobile/v1/my/cart/items;

if (동일 상품+옵션 존재?) then (예)
  :수량 합산;
else (아니오)
  if (장바구니 50개 초과?) then (예)
    :"장바구니가 가득 찼습니다" 토스트;
    stop
  else (아니오)
    :신규 아이템 추가;
  endif
endif

:뱃지 수량 갱신 + 성공 토스트;

|고객|
:장바구니 이동 or 쇼핑 계속;
stop
@enduml
```

### 기본 흐름

| Step | 액터 | 행위 | 시스템 응답 | 비고 |
|---|---|---|---|---|
| 1 | 고객 | 상품상세 화면에서 옵션(색상/사이즈) 선택 | 선택된 옵션 표시, 가격 갱신 | |
| 2 | 고객 | 수량 입력 (기본 1) | 수량 × 단가 소계 표시 | |
| 3 | 고객 | "장바구니 담기" 버튼 클릭 | API: POST /api/mobile/v1/my/cart/items | |
| 4 | 시스템 | — | 성공 응답 + 장바구니 뱃지 수량 갱신 | |
| 5 | 고객 | "장바구니 바로가기" 또는 쇼핑 계속 | 장바구니 화면 이동 or 현재 유지 | |

### 대안 흐름

| 조건 | Step 변경 | 결과 |
|---|---|---|
| 이미 동일 상품+옵션이 장바구니에 있음 | Step 4에서 수량 합산 | 기존 수량 + 새 수량 |
| 장바구니 50개 초과 | Step 4에서 거부 | "장바구니가 가득 찼습니다" 토스트 |
| 품절 상품 | Step 3 전에 버튼 비활성화 | "품절" 표시, 담기 불가 |

---

## 2. [장바구니 담기] 장바구니 조회·관리 Bolt

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title §2 [장바구니 담기] 장바구니 조회·관리

|고객|
start
:장바구니 화면 진입;

|시스템|
:GET /api/mobile/v1/my/cart;

if (장바구니 비어있음?) then (예)
  :빈 상태 + "쇼핑하러 가기" 버튼 표시;
  stop
else (아니오)
  :판매자별 그룹 표시;
endif

|고객|
:수량 +/- 버튼 클릭;

|시스템|
:PATCH /api/mobile/v1/my/cart/items/{cartItemId}/quantity
→ 소계 갱신;

|고객|
if (삭제?) then (예)
  |시스템|
  :DELETE /api/mobile/v1/my/cart/items/{cartItemId}
  → 목록 갱신;
else (아니오)
endif

|고객|
:"선택상품 주문하기" 클릭;

|시스템|
:주문서 화면(/orders/new)으로 이동;
stop
@enduml
```

### 기본 흐름

| Step | 액터 | 행위 | 시스템 응답 | 비고 |
|---|---|---|---|---|
| 1 | 고객 | 장바구니 화면 진입 | API: GET /api/mobile/v1/my/cart → 판매자별 그룹 표시 | |
| 2 | 고객 | 수량 +/- 버튼 클릭 | API: PATCH /api/mobile/v1/my/cart/items/{cartItemId}/quantity → 소계 갱신 | |
| 3 | 고객 | 삭제 버튼 클릭 | API: DELETE /api/mobile/v1/my/cart/items/{cartItemId} → 목록 갱신 | |
| 4 | 고객 | "선택상품 주문하기" 버튼 클릭 | 주문서 화면(/orders/new)으로 이동 | |

### 대안 흐름

| 조건 | Step 변경 | 결과 |
|---|---|---|
| 장바구니 비어있음 | Step 1에서 빈 상태 표시 | "쇼핑하러 가기" 버튼 노출 |
| 품절 상품 포함 | Step 1에서 비활성화 표시 | "품절" 배지, 주문 시 제외 안내 |

> **(2026-10-23 실제 구현 반영)**: "품절" 배지와 비활성화 표시는 `VendorGroup.tsx`에 구현 완료됐다(커밋 813a6e1). "주문 시 제외 안내"는 별도 텍스트로 구현하지 않고 기존 비활성 체크박스 + 기본 선택 제외 로직(`CartClient.tsx`)으로 동작상 충족하기로 결정했다 — 상세 근거는 `DN-화면레이아웃/mobile.md` 144행 각주, `.agents/tasks/mobile-cart-soldout-badge/review.md` 참조.

---

## 3. [주문서 제출] 주문서 작성·제출 Bolt

> v3 (2026-10-29 비동기 접수 기준 현행화): 결제하기는 **접수만 동기**(STOCK_REQUESTED)이고 재고차감·PG 요청은 컨슈머가 비동기로 처리한다(DM-시퀀스 §4/§4-1, REQ-ORD-008·012·077~079). 옛 "재고 선점(동기) 후 PAYMENT_PENDING 응답", 접수 시 재고 부족·CARD_RESTRICTED 즉시 실패 흐름은 폐기했다. 주문서의 쿠폰·포인트는 변경 즉시 서버에 저장(API-052)하고 결제하기는 저장값을 재검증한다. (v2 2026-08-21: 동기 확인 모델 정정)

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title §3 [주문서 제출] 주문서 작성·제출 (비동기 접수)

|고객|
start
:장바구니 "선택상품 주문하기";

|시스템|
:POST /api/mobile/v1/my/orders/sheet
→ 임시주문(TEMP) 생성, 주문서 표시;

|고객|
:배송지 확인(등록된 배송지에서 선택);
:쿠폰 적용 → PUT .../discount 저장 → 금액 재계산;
:포인트 입력 → PUT .../discount 저장 → 금액 재계산;
:결제수단 선택(가상계좌);
:환불계좌 입력(가상계좌 선택 시)
은행·계좌번호·예금주(=주문자 본인) 실명 확인
[미구현];
:약관 동의 체크;

if (필수 약관 전체 동의?) then (아니오)
  :결제 버튼 비활성화;
  stop
else (예)
endif

:"결제하기" 클릭;

|시스템|
:POST /api/mobile/v1/my/orders/{orderSheetId}/pay
저장된 값 재검증 → 접수(STOCK_REQUESTED)
+ 재고차감 요청 아웃박스 적재;

if (검증 통과?) then (아니오)
  :"주문 접수 실패" 화면\n(배송지·약관·쿠폰·포인트·결제수단 오류);
  stop
else (예)
  :200 응답 → "주문 접수 완료" 화면\n(status=STOCK_REQUESTED);
endif

|시스템(비동기, 컨슈머)|
if (재고 차감?) then (전 SKU 성공)
  :STOCK_DEDUCTED → PG 요청(가상계좌 발급)\n→ DEPOSIT_PENDING(입금대기);
else (일부 부족, 3회 재시도 소진)
  :STOCK_FAILED + 차감분 복원;
endif
stop
@enduml
```

### 기본 흐름

| Step | 액터 | 행위 | 시스템 응답 | 비고 |
|---|---|---|---|---|
| 1 | 고객 | 장바구니에서 "선택상품 주문하기" → 주문서 화면 진입 | API: POST /api/mobile/v1/my/orders/sheet → 임시주문(TEMP) 생성, 상품·배송지·쿠폰·포인트·결제수단·금액 표시. 새로고침은 GET .../sheet/{orderSheetId}(API-051) | 판매자별로 주문 분할 |
| 2 | 고객 | 배송지 확인 | 등록된 배송지에서 선택(주문서에서 직접 입력 불가). 현재 기본 배송지 고정 | 선택 기능은 Bolt1 SC37-5 |
| 3 | 고객 | 쿠폰 적용 | 사용 가능 쿠폰에서 선택 → API: PUT .../sheet/{orderSheetId}/discount(API-052) 저장 후 금액 재계산 | 저장 중 결제하기 차단 |
| 4 | 고객 | 포인트 입력 | 사용 가능 범위 내 입력 → API-052 저장(입력 400ms 후) 후 금액 재계산 | 최소 1,000P 검증은 미구현(Bolt4) |
| 5 | 고객 | 결제수단 선택 | 가상계좌(기본). 카드는 "작업중" 안내·차단 | 카드·간편결제 Bolt5·6 |
| 5-1 | 고객 | 환불계좌 입력(가상계좌 선택 시) | 은행·계좌번호·예금주 입력, 예금주는 주문자 본인이어야 하며 실명 확인 후 결제에 저장(REQ-PAY-031). 카드·간편결제는 입력 없음. 마이페이지 환불계좌 등록은 폐기 | **미구현** — 현행 프로토타입은 환불계좌 입력·검증이 없다(DL §6 `refundAccount`, 에러 `REFUND_ACCOUNT_REQUIRED`/`REFUND_ACCOUNT_INVALID`) |
| 6 | 고객 | 약관 동의 체크 | 필수 약관(T001~T003) 전체 동의 시 결제 버튼 활성화 | |
| 7 | 고객 | "결제하기" 버튼 클릭 | API: POST /api/mobile/v1/my/orders/{orderSheetId}/pay → 저장된 상품·쿠폰·포인트 재검증, 주문 접수(STOCK_REQUESTED), 재고차감 요청 적재 후 즉시 응답 | 요청 바디의 상품·쿠폰·포인트는 무시 |
| 8 | 시스템 | — | "주문 접수 완료" 화면으로 즉시 이동(status=STOCK_REQUESTED, "재고 확인 후 결제가 진행됩니다"). 재고 차감·PG 요청 결과는 이 응답에 없음 | |
| 9 | 시스템(비동기) | — | 컨슈머가 재고 차감 → 성공 시 STOCK_DEDUCTED → PG 요청(가상계좌 발급) → DEPOSIT_PENDING (DM-시퀀스 §4-1) | 입금 통보 → PAYMENT_COMPLETED 와 알림톡·이메일 발송은 미구현(REQ-ORD-013) |

### 대안 흐름

| 조건 | Step 변경 | 결과 |
|---|---|---|
| 필수 약관 미동의 | Step 7에서 버튼 비활성화 | 결제 불가 |
| 가상계좌 선택 후 환불계좌 누락·예금주 불일치 | Step 7에서 검증 실패 | 400 `REFUND_ACCOUNT_REQUIRED` / `REFUND_ACCOUNT_INVALID` → 접수 실패 화면 (**미구현**, AC-PAY-037) |
| 배송지 미선택 | Step 7에서 검증 실패 | 400 `ADDRESS_REQUIRED` "배송지를 선택해주세요" → 접수 실패 화면 |
| 쿠폰·포인트 부적합(적용 후 상태 변경 등) | Step 7 재검증 실패 | 422 `COUPON_NOT_APPLICABLE` / `POINT_EXCEED` → 접수 실패 화면 |
| 결제수단 카드 선택 | Step 7 | 400 `PAYMENT_METHOD_NOT_READY` "카드 결제는 작업중입니다" (카드 일일 결제 제한 `CARD_RESTRICTED`(REQ-PAY-018)는 카드 구현 시 적용) |
| 이미 진행된 주문서·타인 주문서 | Step 7 | 422 `ORDER_SHEET_ALREADY_PROCESSED` / 403 `ORDER_SHEET_FORBIDDEN` |
| 재고 부족(일부 SKU) | Step 9(비동기) | 성공 SKU는 유지, 실패 SKU만 백오프 재시도. 3회 소진 시 STOCK_FAILED + 차감분 복원(주문 상세에서 확인, 고객 알림은 미구현) |
| PG 승인 실패·입금기한(12시간) 만료 | 이후(비동기) | PAYMENT_FAILED/CANCELLED + 재고 복원 — **미구현**(Bolt14 SC10-1·SC28-3) |

---

## 4. [바로구매] 바로구매 Bolt

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title §4 [바로구매] 바로구매

|고객|
start
:상품상세에서 "바로구매" 클릭;

|시스템|
:장바구니 미경유\n즉시 주문서 화면 이동;

|고객|
:주문서 작성·제출\n(§3 Step 1~8 동일);
stop
@enduml
```

### 기본 흐름

| Step | 액터 | 행위 | 시스템 응답 | 비고 |
|---|---|---|---|---|
| 1 | 고객 | 상품상세에서 "바로구매" 버튼 클릭 | 장바구니 미경유, 즉시 주문서 화면 이동 | |
| 2~8 | — | (주문서 작성·제출 Bolt Step 1~8 동일) | — | |

---

## 5. [고객 단순 취소] 고객 주문 취소 Bolt

> v2 (2026-10-29 현행화): 고객 직접 취소는 **입금대기(DEPOSIT_PENDING)·결제완료(PAYMENT_COMPLETED)** 두 상태에서 가능하다(REQ-ORD-018·080). 상품준비중(송장 등록 전)은 시스템상 취소요청·승인 절차가 없고 **고객센터 문의 → 어드민 CS 예외 취소**(§6)로 처리하며, 배송중(송장 등록 후)은 취소·반품 모두 불가하다(배송완료 후 반품·교환 접수). 취소는 주문 전체 단위만 가능하다(부분 취소 없음). 취소 시 같은 트랜잭션에서 `claim_type=CANCEL` 클레임(channel=SELF)이 생성된다(REQ-ORD-082).

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title §5 [고객 단순 취소] 고객 주문 취소

|고객|
start
:주문상세 화면 진입;

if (주문 상태?) then (입금대기 / 결제완료)
  :"취소" 버튼 노출·클릭;
elseif (상품준비중) then
  :취소 버튼 비노출\n"출고 준비 중에는 직접 취소할 수 없습니다.\n고객센터로 문의해주세요" 안내;
  stop
else (배송중 이후)
  :취소 버튼 비노출\n"배송완료 후 반품을 이용해주세요" 안내;
  stop
endif

:취소 사유 선택;
:"취소 요청" 버튼 클릭;

|시스템|
:POST /api/mobile/v1/my/orders/{orderId}/cancel;
if (입금대기?) then (예)
  :가상계좌 폐기 + 재고 복원\n환불 없음 / 취소 클레임 RECEIVED→COMPLETED;
else (결제완료)
  :주문 취소 + 환불 요청 + 재고 복원\n취소 클레임 RECEIVED→REFUNDED→COMPLETED;
endif
:주문 취소 완료 안내;
stop
@enduml
```

### 기본 흐름

| Step | 액터 | 행위 | 시스템 응답 | 비고 |
|---|---|---|---|---|
| 1 | 고객 | 주문상세 화면에서 "취소" 버튼 클릭 | 취소 사유 선택 UI 표시 | 입금대기·결제완료 주문만 버튼 노출 |
| 2 | 고객 | 취소 사유 선택 | — | |
| 3 | 고객 | "취소 요청" 버튼 클릭 | API: POST /api/mobile/v1/my/orders/{orderId}/cancel | |
| 4 | 시스템 | — | 주문 CANCELLED + 취소 클레임(CANCEL, channel=SELF) 생성. 결제완료: 환불 요청·재고 복원. 입금대기: 발급 가상계좌 폐기·재고 복원, 환불 없음 | 입금대기 취소·취소 클레임은 **미구현**(REQ-ORD-080·082) |
| 5 | 시스템 | — | 주문 취소 완료 + (결제완료인 경우) 환불 안내 | |

### 대안 흐름

| 조건 | Step 변경 | 결과 |
|---|---|---|
| 입금대기 취소와 가상계좌 입금 통보가 동시에 도착 | Step 4 | **취소 우선** — 주문은 CANCELLED 유지, 입금액은 저장된 환불계좌로 자동 환불(LATE_DEPOSIT, AC-ORD-092·AC-PAY-035) |
| 주문이 상품준비중(PREPARING, 송장 등록 전) | Step 1에서 취소 버튼 비노출 | "출고 준비 중에는 직접 취소할 수 없습니다. 고객센터로 문의해주세요" 안내 → 어드민 CS 예외 취소(§6) |
| 주문이 배송중(송장 등록 후, PREPARING + shipment IN_TRANSIT) 또는 배송완료 이후 | Step 1에서 취소 버튼 비노출 | "배송 중에는 취소할 수 없습니다. 배송완료 후 반품을 이용해주세요" 안내 (취소·반품 모두 불가, 배송완료 후 반품·교환 접수) |

---

## 6. [예외 취소] CS 예외 취소 Bolt (admin)

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title §6 [예외 취소] CS 예외 취소

|CS 담당자|
start
:주문상세 > CS·클레임 탭 진입;

if (PREPARING이 아니거나 출고 shipment가 송장 등록 후(IN_TRANSIT 이후)?) then (예)
  :"예외 취소" 버튼 비활성화\n"배송완료 후 반품으로 처리해주세요" 안내;
  stop
else (아니오 — PREPARING + 송장 등록 전)
  :"예외 취소" 버튼 클릭;
endif

:취소 확인 다이얼로그 → 확인 클릭;

|시스템|
:POST /api/admin/v1/orders/{orderId}/force-cancel;
:주문 취소 + 환불 요청 + 상태 갱신;
stop
@enduml
```

### 기본 흐름

| Step | 액터 | 행위 | 시스템 응답 | 비고 |
|---|---|---|---|---|
| 1 | CS 담당자 | 주문상세 > CS·클레임 탭 진입 | 주문 정보 + CS 액션 버튼 표시 | PREPARING이고 송장 등록 전일 때만 버튼 활성화 |
| 2 | CS 담당자 | "예외 취소" 버튼 클릭 | 취소 확인 다이얼로그 | |
| 3 | CS 담당자 | 확인 클릭 | API: POST /api/admin/v1/orders/{orderId}/force-cancel | |
| 4 | 시스템 | — | 주문 취소 + 환불 요청 + 상태 갱신. 같은 트랜잭션에서 취소 클레임(CANCEL, channel=CS) 생성(REQ-ORD-082, 환불 후 COMPLETED, **미구현**). 고객에게는 별도 취소요청·승인 절차 없이 고객센터 유선 요청으로 접수(REQ-ORD-017) | |

### 대안 흐름

| 조건 | Step 변경 | 결과 |
|---|---|---|
| 송장 등록 후(배송중, PREPARING + shipment IN_TRANSIT) 또는 DELIVERED 이후 상태 | Step 1에서 "예외 취소" 버튼 비활성화(서버도 409 `CANCEL_NOT_ALLOWED`) | "배송 시작 후에는 취소할 수 없습니다. 배송완료 후 반품으로 처리해주세요" 안내 (상태머신(DH): CS 예외취소는 PREPARING·송장 등록 전까지만 허용, 2026-10-29 확정) |

---

## 7. [출고·운송장 등록] 판매자 출고·배송 Bolt (partner)

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title §7 [출고·운송장 등록] 판매자 출고·배송

|판매자|
start
:주문 목록에서 PAYMENT_COMPLETED 주문 선택;
:"출고 처리" 버튼 클릭;

|시스템|
:POST /api/partner/v1/orders/{orderId}/ship;
:주문 상태→PREPARING\n+ shipment(OUTBOUND) 생성;

|판매자|
:배송관리에서 해당 건 선택;
:택배사 선택 + 운송장번호 입력;

if (운송장번호 입력?) then (미입력)
  :"운송장번호를 입력해주세요" 알림;
  stop
else (입력 완료)
  :"배송정보 입력" 클릭;
endif

|시스템|
:POST /api/partner/v1/shipping/{orderId};
:shipment(OUTBOUND) 상태→IN_TRANSIT\n배송 추적 시작;
stop
@enduml
```

### 기본 흐름

| Step | 액터 | 행위 | 시스템 응답 | 비고 |
|---|---|---|---|---|
| 1 | 판매자 | 주문 목록에서 PAYMENT_COMPLETED 주문 선택 | 주문상세 탭 오픈 | |
| 2 | 판매자 | "출고 처리" 버튼 클릭 | API: POST /api/partner/v1/orders/{orderId}/ship | |
| 3 | 시스템 | — | 주문 상태→PREPARING (+ shipment(OUTBOUND) 생성) | |
| 4 | 판매자 | 배송관리에서 해당 건 선택 | 배송정보 입력 모달 표시 | |
| 5 | 판매자 | 택배사 선택 + 운송장번호 입력 | — | |
| 6 | 판매자 | "배송정보 입력" 버튼 클릭 | API: POST /api/partner/v1/shipping/{orderId} | |
| 7 | 시스템 | — | shipment(OUTBOUND) 상태→IN_TRANSIT (주문 상태는 PREPARING 유지), 배송 추적 시작 | |

### 대안 흐름

| 조건 | Step 변경 | 결과 |
|---|---|---|
| 운송장번호 미입력 | Step 6에서 검증 실패 | "운송장번호를 입력해주세요" 알림 |

---

## 8. [배송지 변경] 배송지 변경 Bolt

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title §8 [배송지 변경] 배송지 변경

|고객|
start
:주문상세 진입;

if (DEPOSIT_PENDING 또는 PAYMENT_COMPLETED 상태\n(출고 지시 전)?) then (아니오)
  :"출고 후에는 변경할 수 없습니다"\n버튼 비노출;
  stop
else (예)
  :"배송지 변경" 클릭;
endif

:새 배송지 입력;
:"변경" 버튼 클릭;

|시스템|
:PUT /api/mobile/v1/my/orders/{orderId}/shipping-address;
:배송지 갱신 완료;
stop
@enduml
```

### 기본 흐름

| Step | 액터 | 행위 | 시스템 응답 | 비고 |
|---|---|---|---|---|
| 1 | 고객 | 주문상세에서 "배송지 변경" 클릭 | 배송지 입력 UI 표시 | 입금대기(DEPOSIT_PENDING)·결제완료(PAYMENT_COMPLETED), 출고 지시 전만 |
| 2 | 고객 | 새 배송지 입력 | — | |
| 3 | 고객 | "변경" 버튼 클릭 | API: PUT /api/mobile/v1/my/orders/{orderId}/shipping-address | |
| 4 | 시스템 | — | 배송지 갱신 완료 | |

### 대안 흐름

| 조건 | Step 변경 | 결과 |
|---|---|---|
| 주문이 PREPARING 이후 | Step 1에서 버튼 비노출 | "출고 후에는 변경할 수 없습니다" (준비중은 고객센터 요청 → 어드민 처리, 정책 6.12.2. 송장 등록 후는 범위 제외 — 반품 후 재주문) |

---

## 9. [구매확정] 고객 구매확정 Bolt

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title §9 [구매확정] 고객 구매확정

|고객|
start
:주문상세에서 "구매확정" 버튼 클릭\n(DELIVERED 상태만 노출);
:확인 다이얼로그 → 확인 클릭;

|시스템|
:POST /api/mobile/v1/my/orders/{orderId}/confirm;
:주문 상태→CONFIRMED\n정산등록 + 포인트적립 이벤트;
stop
@enduml
```

### 기본 흐름

| Step | 액터 | 행위 | 시스템 응답 | 비고 |
|---|---|---|---|---|
| 1 | 고객 | 주문상세에서 "구매확정" 버튼 클릭 | 확인 다이얼로그 표시 | DELIVERED 상태만 |
| 2 | 고객 | 확인 클릭 | API: POST /api/mobile/v1/my/orders/{orderId}/confirm | |
| 3 | 시스템 | — | 주문 상태→CONFIRMED, 정산등록+포인트적립 이벤트 | |

---

## 10. [반품/교환 신청] 고객 반품·교환 신청 Bolt

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title §10 [반품/교환 신청] 고객 반품·교환 신청

|고객|
start
:주문상세에서 "반품 신청" 또는 "교환 신청" 클릭;

if (구매확정 후?) then (예)
  :고객 접수 불가\n"구매확정 후에는 고객센터로 문의해주세요" 안내\n(어드민에서만 접수, REQ-ORD-081);
  stop
elseif (사유별 기한 초과?\n단순변심 10일 / 하자·오배송 3개월·안 날부터 30일) then (예)
  :"기한이 초과되었습니다" 안내\n버튼 비노출;
  stop
else (아니오)
  :신청 폼 표시;
endif

:사유 선택 + 상세 입력;

if (판매자 귀책 + 사진 미첨부?) then (예)
  :"사진을 1장 이상 첨부해주세요" 안내;
  stop
else (아니오)
  :"신청" 버튼 클릭;
endif

|시스템|
:POST /api/mobile/v1/my/orders/{orderId}/claims;
:클레임 RECEIVED 상태 생성\n접수 안내;
stop
@enduml
```

### 기본 흐름

| Step | 액터 | 행위 | 시스템 응답 | 비고 |
|---|---|---|---|---|
| 1 | 고객 | 주문상세에서 "반품 신청" 또는 "교환 신청" 클릭 | 신청 폼 표시 (사유 선택, 상세 입력) | DELIVERED 상태(구매확정 전) + 사유별 기한 이내(단순변심 배송완료 후 10일, 하자·오배송 3개월·안 날부터 30일 — 정책 7.2.2) |
| 2 | 고객 | 사유 선택 + 상세 입력 | — | |
| 3 | 고객 | "신청" 버튼 클릭 | API: POST /api/mobile/v1/my/orders/{orderId}/claims | |
| 4 | 시스템 | — | 클레임 RECEIVED 상태 생성, 접수 안내 | |

### 대안 흐름

| 조건 | Step 변경 | 결과 |
|---|---|---|
| 단순변심 사유로 배송완료 후 10일 초과 | Step 1에서 버튼 비노출 | "기한이 초과되었습니다" 안내 |
| 하자·오배송(VENDOR 귀책)으로 배송완료 후 3개월 초과이거나 그 사실을 안 날부터 30일 초과 | Step 3에서 검증 실패 | "기한이 초과되었습니다" 안내, 고객센터 문의 (배송완료 후 11일이 지나도 3개월·30일 이내면 접수 가능, AC-ORD-112) |
| 주문상품이 구매확정(CONFIRMED) 이후 | Step 1에서 버튼 비노출(서버도 거부) | "구매확정 후에는 고객센터로 문의해주세요" — 고객 모바일 접수 불가, 하자·오배송(VENDOR 귀책)은 CS가 어드민에서 접수(REQ-ORD-081, 단순변심은 접수 안 함, **미구현**) |
| VENDOR(판매자) 귀책 사유 선택 시 사진 미첨부 | Step 3에서 검증 실패 | "상품 상태를 확인할 수 있는 사진을 1장 이상 첨부해주세요" 안내, 신청 거부 (사진 최소 1장 첨부 필수, REQ-ORD-058) |

---

## 11. [클레임 접수/반려] CS 클레임 접수 확인·반려·귀책판정 Bolt (admin)

> **역할 경계**: §11은 클레임 접수 단계(RECEIVED→REJECTED)만 담당.
> 수거완료 후 환불/폐기/반송 판정은 §22에서 처리.
> v2 (2026-08-21 바텀업 재검증): Step 3a에 "CS가 고객 자진신고와 다르게 판정할 수 있다"는 REQ-ORD-066을 명시하고, 실제 호출 API(blame-decision)를 표기. EXCHANGE 재고부족 거부(REQ-ORD-069) 대안흐름 추가.

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title §11 [클레임 접수/반려] CS 클레임 접수 확인·반려·귀책판정

|CS 담당자|
start
:클레임 관리 목록에서 RECEIVED 건 선택;
:접수 내용·사유·첨부사진 확인;

if (접수 승인?) then (반려)
  if (반려 사유 입력?) then (미입력)
    :"반려 사유를 입력해주세요";
    stop
  else (입력)
    :POST /api/admin/v1/claims/{claimId}/reject;
  endif
  |시스템|
  :클레임 상태→REJECTED\n고객 알림톡;
  stop
else (귀책 판정)
  :귀책 판정 확정\n(고객 신고값과 무관하게 최종 결정);
  :POST /api/admin/v1/claims/{claimId}/blame-decision;
endif

|시스템|
if (고객 귀책?) then (예)
  :상태→PAYMENT_PENDING\n(배송비 결제 요청);
else (판매자 귀책)
  :shipment(PICKUP) 자동 생성\n(즉시 수거 시작 → §21);
endif

if (claimType=EXCHANGE?) then (예)
  |판매자|
  :교환상품 선출고 운송장 등록\nPOST /api/partner/v1/claims/{claimId}/exchange-ship;
else (아니오)
endif
stop
@enduml
```

### 기본 흐름

| Step | 액터 | 행위 | 시스템 응답 | 비고 |
|---|---|---|---|---|
| 1 | CS 담당자 | 클레임 관리 목록에서 RECEIVED 건 선택 | 클레임상세 MDI 탭 오픈 — API: GET /api/admin/v1/claims/{claimId}(API-056)의 단일 응답으로 접수내용·귀책·첨부·결제·배송·이력을 한 번에 표시 | 고객이 신청 시 자진신고한 `submitted_responsibility`가 참고값으로 표시됨 |
| 2 | CS 담당자 | 접수 내용·사유·첨부사진(고객 업로드분) 확인 | — | |
| 3a | CS 담당자 | 귀책 판정 확정 (고객 신고값과 무관하게 최종 결정, REQ-ORD-066) | API: POST /api/admin/v1/claims/{claimId}/blame-decision {responsibility} → 고객 귀책: 상태→PAYMENT_PENDING (배송비 결제 요청) / 판매자 귀책: 클레임 상태 유지, shipment(PICKUP) 자동 생성 (즉시 수거 시작, §21로 이어짐) | CS가 고객이 제출한 값(`submitted_responsibility`)과 다르게 확정해도 `responsibility` 컬럼만 갱신되고 원신고값은 보존됨 |
| 3a-1 | 판매자 | (EXCHANGE + 판매자 귀책인 경우) 귀책판정 즉시 교환상품 선출고 운송장 등록 | API: POST /api/partner/v1/claims/{claimId}/exchange-ship (REQ-ORD-056, 맞교환 원칙) | 고객 귀책 건은 §20 Step 6에서 동일하게 트리거 |
| 3b | CS 담당자 | "반려" 클릭 + 사유 입력 | API: POST /api/admin/v1/claims/{claimId}/reject | |
| 4b | 시스템 | — | 클레임 상태→REJECTED, 고객 알림톡 | |

### 대안 흐름

| 조건 | Step 변경 | 결과 |
|---|---|---|
| 반려 시 사유 미입력 | Step 3b에서 거부 | "반려 사유를 입력해주세요" |
| claimType=EXCHANGE (귀책 무관) | Step 3a 직후 3a-1(또는 §20 Step 6) 트리거 | 원상품 수취 전 교환상품 선출고 완료 — §12에서 "이미 선출고됨"으로 조회됨 |
| claimType=EXCHANGE + 판매자 귀책 판정 시 exchangeSkuId 재고 없음 | Step 3a에서 판정 자체가 거부됨 | "교환 가능한 재고가 없습니다" 안내, 판정 보류(REQ-ORD-069) — 선출고 이전 단계에서 차단 |
| RECEIVED로 접수 후 24시간 경과, Step 1~4 미처리 | 배치가 CS에게 리마인드 알림 발송(DM-시퀀스 §18-1) | REQ-ORD-068 |

---

## 12. [클레임 접수/반려] 판매자 클레임 조회 Bolt (partner)

> 접수·처리 판정은 어드민 담당. 판매자는 클레임 현황 조회 + 클레임상세 MDI에서 수거·품질점검 수행 (§21 참조). 교환상품은 이미 선출고됨(맞교환 원칙) — 원상품 회수만 진행.

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title §12 [클레임 접수/반려] 판매자 클레임 조회

|판매자|
start
:클레임 현황 화면에서 필터 설정 + 조회;

|시스템|
:GET /api/partner/v1/claims → 통합 목록;

|판매자|
:클레임번호 클릭;
:클레임상세 MDI 탭 오픈;
:수거·품질점검 수행 (§21 참조);
stop
@enduml
```

### 기본 흐름

| Step | 액터 | 행위 | 시스템 응답 | 비고 |
|---|---|---|---|---|
| 1 | 판매자 | 클레임 현황 화면에서 필터 설정 + 조회 | API: GET /api/partner/v1/claims → 통합 목록 | 유형(취소/반품/교환) + 상태 필터 |
| 2 | 판매자 | 클레임번호 클릭 | 클레임상세 MDI 탭 오픈 — API: GET /api/partner/v1/claims/{claimId}(API-057) 단일 응답 | |
| 3 | 판매자 | 클레임상세에서 수거·품질점검 수행 | (§21 참조) | 교환상품은 이미 선출고됨(맞교환 원칙) — 원상품 회수만 진행 |

---

## 14. [전체 주문 검색] 주문 조회 Bolt (admin — 주문 현황)

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title §14 [전체 주문 검색] 주문 조회 (admin)

|CS 담당자|
start
:주문 현황 화면 진입;
:필터 설정 (키워드·상태·기간) + "조회" 클릭;

|시스템|
:GET /api/admin/v1/orders → 테이블 표시;

|CS 담당자|
:테이블 행 클릭;
:주문상세 MDI 탭 오픈;
:탭 전환\n(주문상품/결제정보/배송정보/CS·클레임/변경이력)\n— 추가 호출 없이 이미 받은 응답을 탭별로 표시;
stop
@enduml
```

### 기본 흐름

| Step | 액터 | 행위 | 시스템 응답 | 비고 |
|---|---|---|---|---|
| 1 | CS 담당자 | 주문 현황 화면 진입 | 빈 목록 + 필터바 표시 | |
| 2 | CS 담당자 | 필터 설정 (키워드·상태·기간) + "조회" 클릭 | API: GET /api/admin/v1/orders → 테이블 표시 | |
| 3 | CS 담당자 | 테이블 행 클릭 | 주문상세 MDI 탭 오픈 — API: GET /api/admin/v1/orders/{orderId}(API-023) **1회 호출**로 전 탭 데이터를 단일 응답으로 수신 | 탭별 sub-API 없음(DL "탭별 Sub-API 정책") |
| 4 | CS 담당자 | 탭(주문상품/결제정보/배송정보/CS·클레임/변경이력) 전환 | 이미 받은 단일 응답에서 해당 탭 데이터를 표시(추가 호출 없음) | 클레임 건은 클레임상세(§11, API-056)에서 별도 조회 |

---

## 15. [판매자 주문 조회] 주문 조회 Bolt (partner — 주문 목록)

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title §15 [판매자 주문 조회] 주문 조회 (partner)

|판매자|
start
:주문 목록 화면 진입 + 조회;

|시스템|
:GET /api/partner/v1/orders\n→ 자기 매장 주문 표시;

|판매자|
:테이블 행 클릭;
:주문상세 MDI 탭 오픈\n(주문정보/처리이력);
stop
@enduml
```

### 기본 흐름

| Step | 액터 | 행위 | 시스템 응답 | 비고 |
|---|---|---|---|---|
| 1 | 판매자 | 주문 목록 화면 진입 + 조회 | API: GET /api/partner/v1/orders → 자기 매장 주문 표시 | |
| 2 | 판매자 | 테이블 행 클릭 | 주문상세 MDI 탭 오픈 (주문정보/처리이력) | |

---

## 16. [반품/교환 신청] 고객 클레임 목록 조회 Bolt (mobile — 마이페이지)

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title §16 [반품/교환 신청] 고객 클레임 목록 조회

|고객|
start
:마이페이지 > "취소/반품/교환 내역" 클릭;

|시스템|
:GET /api/mobile/v1/my/claims;

if (클레임 있음?) then (아니오)
  :"접수된 클레임이 없습니다." 안내;
  stop
else (예)
  :상태 요약 + 목록 표시;
endif

|고객|
:클레임 카드 클릭;

|시스템|
:클레임 상세 화면(/my/claims/{claimId}) 이동;
stop
@enduml
```

### 기본 흐름

| Step | 액터 | 행위 | 시스템 응답 | 비고 |
|---|---|---|---|---|
| 1 | 고객 | 마이페이지 > "취소/반품/교환 내역" 클릭 | 클레임 목록 화면(/my/claims) 이동 | |
| 2 | 시스템 | — | API: GET /api/mobile/v1/my/claims → 상태 요약(접수/처리중/완료/반려) + 목록 표시 | |
| 3 | 고객 | 클레임 카드 클릭 | 클레임 상세 화면(/my/claims/{claimId}) 이동 | |

### 대안 흐름

| 조건 | Step 변경 | 결과 |
|---|---|---|
| 클레임 없음 | Step 2에서 빈 상태 표시 | "접수된 클레임이 없습니다." 안내 |

---

## 17. [반품/교환 신청] 고객 클레임 상세 조회 Bolt (mobile — 마이페이지)

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title §17 [반품/교환 신청] 고객 클레임 상세 조회

|고객|
start
:클레임 목록에서 카드 클릭;

|시스템|
:GET /api/mobile/v1/my/claims/{claimId};

if (취소 건?) then (예)
  :수거 정보 비노출\n환불 정보만 표시;
else (아니오)
  if (교환 건?) then (예)
    :환불 정보 비노출\n교환 상품 정보 표시;
  else (반품 건)
    :상품정보·사유·수거정보·환불정보 전체 표시;
  endif
endif

:처리 타임라인 표시\n(최신 이벤트 강조);

|고객|
:진행 상태 확인;
stop
@enduml
```

### 기본 흐름

| Step | 액터 | 행위 | 시스템 응답 | 비고 |
|---|---|---|---|---|
| 1 | 고객 | 클레임 목록에서 카드 클릭 | 상세 화면(/my/claims/{claimId}) 이동 | |
| 2 | 시스템 | — | API: GET /api/mobile/v1/my/claims/{claimId} → 상품정보, 사유, 수거정보, 환불정보, 처리 타임라인 표시 | |
| 3 | 고객 | 타임라인에서 진행 상태 확인 | 최신 이벤트 강조 표시 | |

### 대안 흐름

| 조건 | Step 변경 | 결과 |
|---|---|---|
| 취소 건 (수거 없음) | Step 2에서 수거 정보 섹션 비노출 | 환불 정보만 표시 |
| 교환 건 (환불 없음) | Step 2에서 환불 정보 섹션 비노출 | 교환 상품 정보 표시 |

---

## 18. [내 주문 조회] 고객 주문 상세 조회 Bolt (mobile)

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title §18 [내 주문 조회] 고객 주문 상세 조회

|고객|
start
:주문/배송 조회 목록에서 주문번호 클릭;

|시스템|
:GET /api/mobile/v1/my/orders/{orderId};
:판매자별 상품·결제·배송·이력 표시;

|고객|
if (상태?) then (DELIVERED)
  :구매확정/반품교환/배송조회 버튼 노출;
  :판매자별 액션 버튼 클릭;
elseif (STOCK_REQUESTED / STOCK_DEDUCTED) then
  :"재고 확인 중" 안내 표시\n(액션 없음);
elseif (DEPOSIT_PENDING 입금대기) then
  :가상계좌·입금기한 안내 표시\n"취소" 버튼 노출 → §5\n배송지 변경 노출 → §8;
elseif (PAYMENT_COMPLETED 결제완료) then
  :"취소" 버튼 노출 → §5\n배송지 변경 노출 → §8;
elseif (STOCK_FAILED) then
  :"재고 부족으로 주문이 접수되지 않았습니다" 안내;
else (취소/결제실패)
  :취소 사유 + 환불 상태 추가 표시;
endif
stop
@enduml
```

### 기본 흐름

| Step | 액터 | 행위 | 시스템 응답 | 비고 |
|---|---|---|---|---|
| 1 | 고객 | 주문/배송 조회 목록에서 주문번호 클릭 | 주문 상세 화면(/my/orders/{orderId}) 이동 | |
| 2 | 시스템 | — | API: GET /api/mobile/v1/my/orders/{orderId} → 판매자별 상품·결제·배송·이력 표시 | |
| 3 | 고객 | 판매자별 액션 버튼 클릭 | 상태에 따라 구매확정/반품교환/배송조회 수행 | 상품 단위 구매확정, 판매자 단위 반품/교환 |

### 대안 흐름

| 조건 | Step 변경 | 결과 |
|---|---|---|
| 재고 확인 중(STOCK_REQUESTED·STOCK_DEDUCTED) | 액션 없음 | "재고 확인 후 결제가 진행됩니다" 안내 표시(구 ORDER_RECEIVED·PAYMENT_PENDING 폐기) |
| 입금대기(DEPOSIT_PENDING) | 취소·배송지 변경 진입점 노출 | 가상계좌·입금기한 안내 + "취소" 버튼(§5, 입금대기 취소는 환불 없음, **미구현**). 입금기한(12시간) 만료 시 CANCELLED |
| 결제완료(PAYMENT_COMPLETED, 출고 지시 전) | 취소·배송지 변경 진입점 노출 | "취소" 버튼(§5), "배송지 변경"(§8) |
| 재고 부족 확정(STOCK_FAILED) | 액션 없음 | 재고 부족 안내(재고 복원 완료, 고객 알림은 미구현) |
| 취소/결제실패 | 결제 정보에 취소 사유 + 환불 상태 추가 표시 | |

---

## 19. [반품/교환 신청] 고객 클레임 신청 Bolt (mobile — 반품/교환 신청 상세)

> 주문상세(§18) 또는 주문/배송 조회(§8)에서 [반품/교환] 클릭 시 진입.
> 반품/교환은 **판매자 단위**로 진행. 복수 아이템 선택 가능(주문상세에서만).

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title §19 [반품/교환 신청] 고객 클레임 신청 상세

|고객|
start
:신청 유형 선택 (반품/교환);
:신청 상품 선택 + 수량 지정;
:사유 선택;

if (고객 귀책 사유?) then (예)
  :"수거 배송비 발생" 안내 노출;
else (아니오)
endif

:상세 사유 입력 (선택);
:사진 첨부 (최대 3장)\n판매자 귀책 사유는 1장 이상 필수;
:회수지 확인/변경;

if (아이템/사유 미선택?) then (예)
  :[신청하기] 비활성화;
  stop
else (아니오)
  :"신청하기" 클릭;
endif

|시스템|
:POST /api/mobile/v1/my/orders/{orderId}/claims;
:신청 완료 화면 이동\n(고객귀책 시 배송비 결제 유도);
stop
@enduml
```

### 기본 흐름

| Step | 액터 | 행위 | 시스템 응답 | 비고 |
|---|---|---|---|---|
| 1 | 고객 | 신청 유형 선택 (반품/교환) | — | 라디오 |
| 2 | 고객 | 신청 상품 선택 + 수량 지정 | 클레임 가능 수량 범위 내 | 체크박스 + 수량 Select |
| 3 | 고객 | 사유 선택 (단순변심/사이즈/불량/오배송/기타) | 고객귀책 사유 시 배송비 안내 문구 노출 | |
| 4 | 고객 | 상세 사유 입력 (선택) | — | |
| 5 | 고객 | 사진 첨부 (최대 3장) | — | 판매자(VENDOR) 귀책 사유(불량·오배송)는 **1장 이상 필수**(REQ-ORD-058), 고객 귀책 사유는 선택 |
| 6 | 고객 | 회수지 확인/변경 | 기본: 주문 배송지. [변경] → 배송지 팝업 | |
| 7 | 고객 | "신청하기" 클릭 | API: POST /api/mobile/v1/my/orders/{orderId}/claims | |
| 8 | 시스템 | — | 신청 완료 화면 이동 (고객귀책 시 배송비 결제 유도) | |

### 대안 흐름

| 조건 | Step 변경 | 결과 |
|---|---|---|
| 클레임 가능 아이템 없음 | Step 2에서 "반품/교환 가능한 상품이 없습니다" | 신청 불가 |
| 사유 미선택 / 아이템 미선택 | Step 7에서 [신청하기] 비활성화 | |
| 고객 귀책 사유 선택 | Step 3에서 안내 노출 | "수거 배송비 발생 + 품질점검 불합격 시 반송 배송비 추가 가능" |

---

## 20. [반품/교환 신청] 고객 클레임 배송비 결제 Bolt (mobile)

> 클레임 신청 완료 화면(§8-3) 또는 클레임 상세(§10)에서 진행.
> 결제 기한 24시간. 미결제 시 클레임 자동 취소. 12시간 경과 시 리마인드 알림톡(DM §23, BAT-004).
> **배송비는 서버가 산정**한다(클라이언트가 금액을 보내지 않음). 반품·교환 배송비는 **환불금액에서 차감하지 않고 수거 전에 별도 결제**한다. 단순변심 반품: 편도 3,000원 + 초도 배송비 중 할인받은 금액(유료배송 3,000, 무료배송 6,000, 배송비 쿠폰 50% 4,500), 교환: 왕복 6,000원(정책 6.9.7). 판매자 귀책은 고객 배송비 없음.

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title §20 [반품/교환 신청] 고객 클레임 배송비 결제

|고객|
start
:클레임 상세에서 [배송비 결제하기] 클릭;

if (결제 기한 24시간 초과?) then (예)
  :버튼 비활성화\n클레임 자동 취소 + 알림톡;
  stop
else (아니오)
  :배송비 결제 레이어 팝업 오픈;
endif

if (배송비 쿠폰 전액 적용?) then (예)
  :결제 0원, 즉시 수거 진행;
else (아니오)
  :결제수단 선택;
  :[결제하기] 클릭 → PG SDK 인증;
  if (PG 결제 성공?) then (실패)
    :팝업 내 에러 표시\n재시도 안내;
    stop
  else (성공)
  endif
endif

|시스템|
:POST /api/mobile/v1/my/claims/{claimId}/shipping-payment;
:shipment(PICKUP) 자동 생성\n수거 프로세스 시작 + 알림톡;

if (claimType=EXCHANGE?) then (예)
  |판매자|
  :교환상품 선출고 운송장 등록;
else (아니오)
endif
stop
@enduml
```

### 기본 흐름

| Step | 액터 | 행위 | 시스템 응답 | 비고 |
|---|---|---|---|---|
| 1 | 고객 | [배송비 결제하기] 버튼 클릭 | 배송비 결제 레이어 팝업 오픈 — 서버가 산정한 배송비 표시 | 환불에서 차감하지 않고 별도 결제 |
| 2 | 고객 | 쿠폰 적용 (선택) | 배송비 쿠폰 있으면 적용 → 결제금액 0원 가능 | |
| 3 | 고객 | 결제수단 선택 (쿠폰 미적용 시) | 기등록 결제수단 선택 | |
| 4 | 고객 | [결제하기] 클릭 | PG SDK 호출 → 인증 | |
| 5 | 시스템 | PG 결제 완료 콜백 | 팝업 닫힘 → 클레임 상세 화면에서 결제완료 상태 반영 | API: POST /api/mobile/v1/my/claims/{claimId}/shipping-payment |
| 6 | 시스템 | — | shipment(PICKUP) 자동 생성 (클레임 상태는 PAYMENT_PENDING 유지), 수거 프로세스 시작 + 알림톡 발송. **claimType=EXCHANGE면 이 시점에 판매자가 교환상품 선출고 운송장 등록**(§11 Step 3a-1과 동일 트리거, REQ-ORD-056) | |

### 대안 흐름

| 조건 | Step 변경 | 결과 |
|---|---|---|
| 결제 기한 24시간 초과 | [배송비 결제하기] 비활성화 | 클레임 자동 취소 + 알림톡 |
| PG 결제 실패 | Step 5에서 팝업 내 에러 표시 | 재시도 안내 |
| 배송비 쿠폰 전액 적용 | Step 3~4 생략 | 결제 0원, 즉시 수거 진행 |

---

## 21. [수거·재고복구] 판매자 수거·품질점검 Bolt (partner)

> 배송관리에서 회수 건 처리 또는 클레임상세 MDI에서 수행.

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title §21 [수거·재고복구] 판매자 수거·품질점검

|판매자|
start
:배송관리에서 회수 건(수거대기) 선택;

if (배송비 결제 완료?) then (미결제)
  :"배송비 결제 후 수거 가능" 안내;
  stop
else (결제완료)
  :택배사 + 운송장번호 입력;
  :[수거정보 입력] 클릭;
endif

|시스템|
:POST /api/partner/v1/shipping/{claimId}/pickup;
:shipment(PICKUP) 상태→IN_TRANSIT;

|판매자|
:상품 도착 후\n[입고 확인 → 품질점검 시작] 클릭;

|시스템|
:POST /api/partner/v1/claims/{claimId}/pickup-confirm;
:클레임 상태→INSPECTING\nshipment(PICKUP)→DELIVERED;

|판매자|
if (품질점검 결과?) then (합격)
  :POST /api/partner/v1/claims/{claimId}/inspect-pass;
  |시스템|
  :클레임 상태→PICKED_UP\n어드민 환불 처리 대기;
else (거부)
  if (거부 사유 입력?) then (미입력)
    :"거부 사유를 입력해주세요";
    stop
  else (입력)
    :POST /api/partner/v1/claims/{claimId}/inspect-reject;
  endif
  |시스템|
  :클레임 상태→PICKUP_REJECTED\n+ 사유 기록 → 어드민 판정 대기;
endif
stop
@enduml
```

### 기본 흐름

| Step | 액터 | 행위 | 시스템 응답 | 비고 |
|---|---|---|---|---|
| 1 | 판매자 | 배송관리에서 회수 건(수거대기) 선택 | 수거정보 입력 모달 표시 | 배송비 ⦿결제완료 확인 후 |
| 2 | 판매자 | 택배사 + 운송장번호 입력 | — | |
| 3 | 판매자 | [수거정보 입력] 클릭 | API: POST /api/partner/v1/shipping/{claimId}/pickup | |
| 4 | 시스템 | — | shipment(PICKUP) 상태 → IN_TRANSIT (수거중) | |
| 5 | 판매자 | 상품 도착 후 [입고 확인 → 품질점검 시작] 클릭 | API: POST /api/partner/v1/claims/{claimId}/pickup-confirm | 입고 확인 주체는 판매자 액션(API-038, DM §26, DL §27)이며 배송추적 배치는 입고 확인을 하지 않는다(2026-11-03 확정) |
| 6 | 시스템 | — | 클레임 상태 → INSPECTING (품질점검), shipment(PICKUP) 상태 → DELIVERED (동시 전환) | |
| 7 | 판매자 | 품질 확인 후 [합격] 또는 [거부] 클릭 | API: POST /api/partner/v1/claims/{claimId}/inspect-pass 또는 /inspect-reject | 판정 기준: **RETURN 유형**은 상품 상태(훼손 여부), **EXCHANGE 유형**은 택(TAG) 유지 여부 |
| 8a | 시스템 (합격) | — | 클레임 상태 → PICKED_UP (수거완료) → RETURN: 어드민 환불 처리 대기 / EXCHANGE: 선출고한 shipment 배송완료(고객 수령)가 합격과 함께 충족되면 COMPLETED(환불 없음). 불합격 시 선출고 비용은 운영자가 수작업 청구 | |
| 8b | 시스템 (거부) | — | 클레임 상태 → PICKUP_REJECTED (수거거부) + 사유 기록 → 어드민 판정 대기 | |

### 대안 흐름

| 조건 | Step 변경 | 결과 |
|---|---|---|
| 배송비 미결제 | Step 1에서 [수거정보 입력] 비활성화 | "배송비 결제 후 수거 가능" 안내 |
| 거부 시 사유 미입력 | Step 7에서 거부 불가 | "거부 사유를 입력해주세요" |
| RETURN 유형 품질점검 | Step 7에서 상품 훼손 여부로 합격/거부 판정 | 훼손 시 [거부] |
| EXCHANGE 유형 품질점검 | Step 7에서 택(TAG) 유지 여부로 합격/거부 판정 | 택 제거·훼손 시 [거부] |

---

## 22. [수거·재고복구] 어드민 환불/폐기/반송결제 판정 Bolt (admin)

> 수거완료(PICKED_UP) 또는 수거거부(PICKUP_REJECTED) 상태에서 어드민이 후속 처리.

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title §22 [수거·재고복구] 어드민 환불/폐기/반송결제 판정

|CS 담당자|
start

if (클레임 상태?) then (PICKED_UP — 수거완료)
  :클레임상세 > 환불정보 탭 진입;
  :[환불 처리] 클릭;
  |시스템|
  :POST /api/admin/v1/claims/{claimId}/refund;
  :클레임 상태→REFUNDED→COMPLETED\n고객 알림톡 발송;
  stop
else (PICKUP_REJECTED — 수거거부)
  :거부 사유 조회;
  if (반송 가능?) then (불가)
    :[폐기 처리] 클릭;
    |시스템|
    :POST /api/admin/v1/claims/{claimId}/dispose;
    :상태→DISPOSED→COMPLETED;
    stop
  else (가능)
    :[반송 배송비 추가결제 요청] 클릭;
    |시스템|
    :POST /api/admin/v1/claims/{claimId}/request-return-payment;
    :고객에게 결제 알림톡 발송;
  endif
endif

|고객|
:반송 배송비 결제 (§20, paymentType=RETURN);

|판매자|
:반송 운송장 등록;
:POST /api/partner/v1/claims/{claimId}/return-ship;

|시스템|
:shipment(RETURN)→IN_TRANSIT→DELIVERED;
:배치 자동전환 → COMPLETED\n고객 알림톡 발송;
stop
@enduml
```

### 기본 흐름 (수거완료 → 환불)

| Step | 액터 | 행위 | 시스템 응답 | 비고 |
|---|---|---|---|---|
| 1 | CS 담당자 | 클레임상세 > 환불정보 탭 진입 | 환불금액·수단 표시 | |
| 2 | CS 담당자 | [환불 처리] 클릭 | API: POST /api/admin/v1/claims/{claimId}/refund | 원결제수단 또는 계좌이체. 환불금액 = 상품주문금액 + 환불 대상 배송비(반품 배송비는 별도 결제라 차감 없음). 클레임(반품) 환불의 유일한 트리거이며, CLAIM_COMPLETED는 정산·알림·재고복원·포인트 이벤트로 Payment 환불을 일으키지 않는다(2026-11-03 확정) |
| 3 | 시스템 | — | 클레임 상태 → REFUNDED → (배치) COMPLETED | 고객 알림톡 발송 |

### 대안 흐름 (수거거부 → 폐기 또는 반송)

| Step | 액터 | 행위 | 시스템 응답 | 비고 |
|---|---|---|---|---|
| 1 | CS 담당자 | 클레임상세에서 PICKUP_REJECTED 건 확인 | 거부 사유 조회 | |
| 2a | CS 담당자 | [폐기 처리] 클릭 | API: POST /api/admin/v1/claims/{claimId}/dispose | 상품 반송 불가 판단 시 |
| 2b | CS 담당자 | [반송 배송비 추가결제 요청] 클릭 | API: POST /api/admin/v1/claims/{claimId}/request-return-payment | 고객에게 결제 알림톡 발송. 반송 배송비는 편도 3,000원 고정, 환불에서 차감하지 않고 별도 결제, 24시간 미결제 시 만료(DH RETURN_PAYMENT_PENDING→PAYMENT_EXPIRED) |
| 3b | 고객 | 알림톡 수신 → 클레임상세에서 반송 배송비 결제 | §20 배송비 결제 Bolt (paymentType=RETURN) | |
| 4b | 판매자 | 반송 운송장 등록 | API: POST /api/partner/v1/claims/{claimId}/return-ship | shipment(RETURN) 생성, 상태 → IN_TRANSIT (클레임 상태는 RETURN_PAYMENT_PENDING 유지) |
| 5b | 시스템 | 반송 배송완료 확인 (택배사 API) | shipment(RETURN) 상태 → DELIVERED | |
| 6b | 시스템 | 배치 자동전환 | 배치가 클레임 상태를 COMPLETED로 자동 전환 | 고객 알림톡 발송. |
| 6c | 시스템 | 교환 클레임 종료 (배치, DM §19) | 합격(PICKED_UP)한 교환 클레임의 선출고 shipment(EXCHANGE_OUT)가 배송완료(고객 수령)이면(수령이 먼저여도 다음 주기에) PICKED_UP → COMPLETED 전환 | CLAIM_COMPLETED는 COMPLETED 전환 시 발행(2026-11-03 확정). 교환은 환불 없음 |

---

## 23. [장바구니 담기] 장바구니 옵션 변경 Bolt (mobile)

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title §23 [장바구니 담기] 장바구니 옵션 변경

|고객|
start
:장바구니에서 [옵션변경] 클릭;
:옵션 변경 레이어 팝업 오픈;

if (선택한 옵션 품절?) then (예)
  :해당 옵션 [×] 표시, 선택 불가;
  stop
else (아니오)
  :색상/사이즈 선택;
  :[변경 완료] 클릭;
endif

|시스템|
:PUT /api/mobile/v1/my/cart/items/{cartItemId}/option;
:옵션 갱신 + 소계 재계산;
stop
@enduml
```

### 기본 흐름

| Step | 액터 | 행위 | 시스템 응답 | 비고 |
|---|---|---|---|---|
| 1 | 고객 | 장바구니에서 [옵션변경] 클릭 | 옵션 변경 레이어 팝업 오픈 | |
| 2 | 고객 | 색상/사이즈 선택 | 품절 옵션(실재고−장바구니 선점 ≤ 0) 비활성화 | |
| 3 | 고객 | [변경 완료] 클릭 | API: PUT /api/mobile/v1/my/cart/items/{cartItemId}/option | |
| 4 | 시스템 | — | 옵션 갱신 + 소계 재계산 | |

### 대안 흐름

| 조건 | Step 변경 | 결과 |
|---|---|---|
| 선택한 옵션 품절 | Step 2에서 선택 불가 | 해당 옵션 [×] 표시 |

---

## 24. [반품/교환 신청] 고객 클레임 자진 취소 Bolt (mobile — 신규)

> 신규 (2026-08-21 바텀업 재검증): REQ-ORD-073/071 대응. RECEIVED/PAYMENT_PENDING 상태에서만 가능, 귀책판정(INSPECTING 진입) 이후는 불가.

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title §24 [반품/교환 신청] 고객 클레임 자진 취소

|고객|
start
:내 클레임 상세 진입;

if (INSPECTING 이후 상태?) then (예)
  :"취소" 버튼 비노출\n"귀책 판정/수거 시작 이후에는\n취소할 수 없습니다" 안내;
  stop
else (RECEIVED/PAYMENT_PENDING)
  :"취소" 버튼 클릭;
  :취소 확인 다이얼로그 → 확인 클릭;
endif

|시스템|
:POST /api/mobile/v1/my/claims/{claimId}/cancel;
:클레임 상태→REJECTED\n(사유="고객 자진 철회")\n취소완료 알림톡;
stop
@enduml
```

### 기본 흐름

| Step | 액터 | 행위 | 시스템 응답 | 비고 |
|---|---|---|---|---|
| 1 | 고객 | 내 클레임 상세에서 "취소" 버튼 클릭 | 취소 확인 다이얼로그 | RECEIVED/PAYMENT_PENDING 상태만 버튼 노출 |
| 2 | 고객 | 확인 클릭 | API: POST /api/mobile/v1/my/claims/{claimId}/cancel | |
| 3 | 시스템 | — | 클레임 상태→REJECTED(사유="고객 자진 철회"), 취소완료 알림톡 | |

### 대안 흐름

| 조건 | Step 변경 | 결과 |
|---|---|---|
| 클레임이 INSPECTING 이후 상태 | Step 1에서 "취소" 버튼 비노출 | "귀책 판정/수거 시작 이후에는 취소할 수 없습니다" 안내(REQ-ORD-071) |

---

## 25. [배송실패 재발송] 판매자·CS 배송 재발송 처리 Bolt (partner/admin — 신규)

> 신규 (2026-08-21 바텀업 재검증): REQ-ORD-062 대응. shipment_type 공통(OUTBOUND/PICKUP/RETURN/EXCHANGE_OUT).

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title §25 [배송실패 재발송] 판매자·CS 배송 재발송 처리

|판매자 또는 CS 담당자|
start
:배송관리에서 FAILED 상태 건 선택;

if (shipment 상태 = FAILED?) then (아니오)
  :"FAILED 상태만 재발송 가능합니다"\n(RESHIP_NOT_ALLOWED);
  stop
else (예)
  :재발송 처리 모달 표시;
  :택배사 + 새 운송장번호 입력;
endif

if (운송장번호 입력?) then (미입력)
  :"운송장번호를 입력해주세요";
  stop
else (입력 완료)
  :[재발송 처리] 클릭;
endif

|시스템|
:POST /api/partner/v1/shipping/{shipmentId}/reship;
:shipment 상태 FAILED→PENDING→IN_TRANSIT\n추적 재시작;
stop
@enduml
```

### 기본 흐름

| Step | 액터 | 행위 | 시스템 응답 | 비고 |
|---|---|---|---|---|
| 1 | 판매자 또는 CS 담당자 | 배송관리에서 FAILED 상태 건 선택 | 재발송 처리 모달 표시 | 배송실패 뱃지 노출 건만 (DM-시퀀스 §19 배치가 FAILED로 전환) |
| 2 | 판매자/CS | 택배사 + 새 운송장번호 입력 | — | |
| 3 | 판매자/CS | [재발송 처리] 클릭 | API: POST /api/partner/v1/shipping/{shipmentId}/reship | 인증: Partner 또는 Admin Bearer |
| 4 | 시스템 | — | shipment 상태 FAILED→PENDING→IN_TRANSIT, 추적 재시작 | 이후 DM-시퀀스 §19 배치가 다시 추적 |

### 대안 흐름

| 조건 | Step 변경 | 결과 |
|---|---|---|
| shipment 상태가 FAILED가 아님 | Step 3에서 거부 | "FAILED 상태만 재발송 가능합니다" (RESHIP_NOT_ALLOWED) |
| 운송장번호 미입력 | Step 3에서 검증 실패 | "운송장번호를 입력해주세요" |

