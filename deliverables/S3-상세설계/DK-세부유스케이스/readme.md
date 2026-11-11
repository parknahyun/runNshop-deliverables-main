# 세부 유스케이스

> **단계**: 상세설계 (S3)
> **문서범위**: Bolt (Order + Payment + Catalog)
> **문서종류**: Design
>
> **작성 목적**: 상위 유스케이스(DC)를 버튼·화면 단위 행위로 분해한다.
> "사용자가 화면에서 어떤 순서로 무엇을 하는가"를 UI 흐름 수준으로 기술하여,
> 인터페이스 명세(DL)의 endpoint 도출 근거가 된다.
>
> **흐름 내 위치**:
> ```
> Bolt 분할 → DJ GWT → DK 세부 유스케이스 → DL 인터페이스 명세
> ```

---

도메인별 파일로 분리되어 있습니다.

| 구분 | 파일 |
|---|---|
| Order 도메인 | [order.md](order.md) |
| Payment 도메인 | [payment.md](payment.md) |
| Catalog 도메인 | [catalog.md](catalog.md) |

---

## 기본 흐름 전체 시각화

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title 세부 유스케이스 기본 흐름 — 주문·결제 도메인 (고객 여정 중심)

|고객 (mobile)|
start
:상품상세에서 옵션 선택;
:§1 **장바구니 담기**
POST /api/mobile/v1/my/cart/items;

:§2 장바구니 조회·관리
GET /api/mobile/v1/my/cart;

if (바로구매?) then (예)
  :§4 상품상세에서 바로구매;
else (아니오)
  :장바구니에서 [주문하기];
endif

:§3 **주문서 작성·제출**
POST /api/mobile/v1/my/orders/sheet
→ 임시주문(TEMP);
:배송지·쿠폰·포인트·결제수단 설정
(가상계좌는 환불계좌 입력, 미구현);
:약관 동의 → [결제하기]
POST /api/mobile/v1/my/orders/{sheetId}/pay
→ STOCK_REQUESTED (접수만 동기);

|시스템 (비동기 컨슈머)|
:재고차감 → STOCK_DEDUCTED;

if (재고 확보?) then (성공)
  :PG 요청(가상계좌 발급)
  → DEPOSIT_PENDING (입금대기);
  if (입금?) then (입금 통보)
    :→ PAYMENT_COMPLETED
    (입금 통보 처리 미구현);
  else (취소 또는 입금기한 12시간 만료)
    :§5 고객 취소(입금대기 취소)
    또는 만료 → CANCELLED
    + 재고 복원;
    stop
  endif
else (3회 재시도 소진)
  :STOCK_FAILED
  차감분 복원;
  stop
endif

|판매자 (partner)|
:§7 **출고 처리**
POST /api/partner/v1/orders/{id}/ship
→ PREPARING;
:운송장 등록
POST /api/partner/v1/shipping/{id}
→ shipment(OUTBOUND) IN_TRANSIT
(주문 상태는 PREPARING 유지);

|시스템 (배치)|
:§19 배송상태 갱신 (60분)
택배사 API 조회;
:배송완료 → DELIVERED;

|고객 (mobile)|
if (구매확정?) then (수동/D+11자동, 진행 중 클레임 건은 자동 제외)
  :§9 **구매확정**
  POST /api/mobile/v1/my/orders/{id}/confirm
  → CONFIRMED;
  stop
else (클레임 신청)
endif

:§10 **반품/교환 신청**
POST /api/mobile/v1/my/orders/{id}/claims
→ RECEIVED;

|어드민 (admin)|
:§11 **귀책 판정**
POST /api/admin/v1/claims/{id}/blame-decision;

if (고객 귀책?) then (예)
  |고객 (mobile)|
  :§20 **배송비 결제**
  POST /api/mobile/v1/my/claims/{id}/shipping-payment;
else (판매자 귀책)
  :배송비 면제, 즉시 수거;
endif

|판매자 (partner)|
:§21 **수거·품질점검**;
:수거 운송장 등록
→ PICKUP → INSPECTING;

if (품질점검?) then (합격)
  :→ PICKED_UP;
  |어드민 (admin)|
  :§22 **환불 처리**
  POST /api/admin/v1/claims/{id}/refund
  → REFUNDED → COMPLETED;
  stop
else (거부)
  :→ PICKUP_REJECTED;
  |어드민 (admin)|
  if (반송 가능?) then (예)
    :반송 배송비 추가결제 요청;
    |고객 (mobile)|
    :§20 반송 배송비 결제
    → RETURN_PAYMENT_PENDING;
    |판매자 (partner)|
    :반송 운송장 등록
    → shipment(RETURN) IN_TRANSIT → DELIVERED
    → 클레임 COMPLETED (배치);
    stop
  else (불가)
    :§22 **폐기 처리**
    → DISPOSED → COMPLETED;
    stop
  endif
endif

@enduml
```

---

## 근거

| 항목 | 출처 |
|---|---|
| 기본 흐름 | 상위 유스케이스(DC) Order·Payment 업무그룹 |
| 대안 흐름 | GWT(DJ) 예외·경계값 시나리오 |
| UI 행위 | 메뉴구조도(DE) + 화면 레이아웃(DN) |
| API 호출 지점 | 인터페이스 명세(DL) endpoint 도출 근거 |
