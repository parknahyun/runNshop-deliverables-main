# 시퀀스 — Order 도메인

> 상위 문서: [readme.md](readme.md)
> **단계**: 상세설계 (S3) | **문서범위**: Bolt (Order) | **문서종류**: Design
> Payment 관련 시퀀스는 [DM-시퀀스/payment.md](payment.md) 참조

---

## 1. [API] POST /api/mobile/v1/my/cart/items — 장바구니 담기

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title POST /api/mobile/v1/my/cart/items — 장바구니 담기

actor 고객 as Client
participant "CustomerCartController" as CC
participant "CartService" as CS
participant "CatalogPublicApi" as CAT
participant "CartRepository" as CR
database "DB (ord_cart)" as DB

Client -> CC : POST /api/mobile/v1/my/cart/items\n{productId, skuId, quantity}
activate CC

CC -> CS : addToCart(memberId, request)
activate CS

CS -> CAT : getProductInfo(productId, skuId)
activate CAT
CAT --> CS : {name, price, status, stock}
deactivate CAT

alt 상품 판매중지 or 품절
  CS --> CC : PRODUCT_NOT_AVAILABLE
  CC --> Client : 409 에러 응답
else 정상

  CS -> CR : findByMemberAndSku(memberId, skuId)
  activate CR
  CR -> DB : SELECT
  DB --> CR : 기존 cartItem (nullable)
  CR --> CS : Optional<CartItem>
  deactivate CR

  alt 기존 존재 → 수량 합산
    CS -> CR : save(existingItem.addQuantity(quantity))
  else 신규 → 새 아이템
    CS -> CS : 장바구니 개수 검증 (50개 초과?)
    alt 50개 초과
      CS --> CC : CART_FULL
      CC --> Client : 422 에러 응답
    else
      CS -> CR : save(newCartItem)
    end
  end

  CR -> DB : INSERT/UPDATE
  DB --> CR : OK
  CS --> CC : CartItemResponse
  deactivate CS
  CC --> Client : 200 SUCCESS
  deactivate CC
end

@enduml
```


---

## 2. [API] GET /api/mobile/v1/my/cart — 장바구니 조회

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title GET /api/mobile/v1/my/cart — 장바구니 조회

actor 고객 as Client
participant "CustomerCartController" as CC
participant "CartService" as CS
participant "CartRepository" as CR
participant "CatalogPublicApi" as CAT
database "DB (ord_cart)" as DB

Client -> CC : GET /api/mobile/v1/my/cart
activate CC

CC -> CS : getCart(memberId)
activate CS

CS -> CR : findAllByMember(memberId)
activate CR
CR -> DB : SELECT WHERE member_id AND is_deleted=false
DB --> CR : List<CartItem>
CR --> CS : cartItems
deactivate CR

CS -> CAT : getProductInfoBatch(productIds)
activate CAT
CAT --> CS : Map<productId, ProductInfo>
deactivate CAT

CS -> CS : 판매자별 그룹핑 + summary 계산\n(할인, 배송비, 포인트잔액)

CS --> CC : CartResponse
deactivate CS
CC --> Client : 200 SUCCESS
deactivate CC

@enduml
```


---

## 3. [API] POST /api/mobile/v1/my/orders/sheet — 주문서 생성

> 최종 수정: 2026-10-19 (실제 구현 반영 — URL 정정 + 실제 구현 보조 다이어그램 추가)

> **(2026-10-19 구현 확인·보완)** 제목·다이어그램 URL을 구버전(`/api/v1/orders/sheet`)에서 실제 Controller 매핑(`/api/mobile/v1/my/orders/sheet`, `OrderController.kt`)으로 정정했다 — order-domain-api-migration 작업 때 DL-인터페이스명세는 갱신됐지만 이 시퀀스 문서는 갱신 대상에서 빠져 있던 것을 이번 작업으로 발견·추가 정정(참고: readme.md §1, DQ-프로그램목록/order.md §2-1도 동일 간극이 있어 함께 정정).

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title POST /api/mobile/v1/my/orders/sheet — 주문서 생성

actor 고객 as Client
participant "CustomerOrderController" as OC
participant "OrderSheetService" as OSS
participant "CartRepository" as CR
participant "MemberPublicApi" as MEM
participant "PromotionPublicApi" as PROMO
database "DB" as DB

Client -> OC : POST /api/mobile/v1/my/orders/sheet\n{cartItemIds}
activate OC

OC -> OSS : createSheet(memberId, cartItemIds)
activate OSS

OSS -> CR : findByIds(cartItemIds)
CR -> DB : SELECT
DB --> CR : cartItems
CR --> OSS : cartItems

OSS -> MEM : getAddresses(memberId)
MEM --> OSS : addresses

OSS -> MEM : getPointBalance(memberId)
MEM --> OSS : pointInfo

OSS -> PROMO : getAvailableCoupons(memberId, items)
PROMO --> OSS : coupons

OSS -> OSS : 판매자별 그룹 + 금액 계산\n(상품할인, 배송비, 결제수단)

OSS --> OC : OrderSheetResponse
deactivate OSS
OC --> Client : 200 SUCCESS
deactivate OC

@enduml
```

> **신규 (2026-10-19 프로토타입 구현, 2026-10-20 네이밍 갱신): 실제 호출 흐름은 위 다이어그램보다 훨씬 단순하다** — Cart 영속 계층이 없어 CartRepository/MemberApi/PromotionApi(옛 이름: MemberPublicApi/PromotionPublicApi)를 전혀 호출하지 않는다. `OrderController.createOrderSheet()` → `OrderService.createOrderSheet()`가 Mock 파일(`mobile__POST_my_orders_sheet.json`)을 로드해 `order_sheet_id`만 UUID로 덮어쓴 뒤 그대로 반환한다(design.md §1-1).

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title POST /api/mobile/v1/my/orders/sheet — 주문서 생성 (실제 구현)

actor 고객 as Client
participant "OrderController" as OC
participant "OrderService" as OS
participant "MockLoader" as ML

Client -> OC : POST /api/mobile/v1/my/orders/sheet\n{items} (선택 상품 — 임시주문으로 저장, 2026-10-26)
activate OC

OC -> OS : createOrderSheet()
activate OS

OS -> ML : load("order", "mobile__POST_my_orders_sheet.json")
ML --> OS : Map(data)

OS -> OS : 임시주문 저장(ord_platform_order, status=TEMP) + 이력 (신규)→TEMP\ndata.order_sheet_id = 임시주문의 platformOrderNo (2026-10-26, 기존 stateless UUID 폐기)

OS --> OC : Map
deactivate OS
OC --> Client : 200 SUCCESS
deactivate OC

@enduml
```

### 3-1. PUT /api/mobile/v1/my/orders/sheet/{orderSheetId}/discount — 주문서 쿠폰/포인트 적용 (2026-10-26 신설)

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title PUT /api/mobile/v1/my/orders/sheet/{orderSheetId}/discount — 쿠폰/포인트 적용 영속화

actor 고객 as Client
participant "OrderController" as OC
participant "OrderService" as OS
participant "PromotionApi" as PROMO
participant "MemberApi" as MEM
participant "PlatformOrderRepository" as POR

Client -> OC : PUT .../sheet/{id}/discount\n{couponId?, pointUsed?}
OC -> OS : applyOrderSheetDiscount()
OS -> POR : 임시주문 조회(TEMP, 본인 확인)
OS -> MEM : getPointBalance() — 잔액 검증(POINT_EXCEED)
OS -> PROMO : validateCoupon() — COUPON_NOT_APPLICABLE
OS -> OS : 할인 행(ord_platform_order_discount) 교체/삭제\ntotal_discount_amount/point_used_amount/payment_amount 갱신
OS -> POR : save
OS --> OC : 갱신된 주문서(price_summary, selected_coupon_id, point_used)
OC --> Client : 200 SUCCESS
@enduml
```

> 결제(§4)는 요청 바디의 `couponId`/`pointUsed`를 무시하고 이 단계에서 저장된 값을 재검증해 확정한다.

---

## 4. [API] POST /api/mobile/v1/my/orders/{orderSheetId}/pay — 결제 요청

> 최종 수정: 2026-10-29 (비동기 접수 기준으로 현행화 — 결제하기는 **접수만 동기**, 재고차감·PG 요청은 §4-1 컨슈머가 비동기 처리. 구 동기 재고 선점·`ORDER_RECEIVED`/`PAYMENT_PENDING` 다이어그램은 §4-2로 이동(폐기))

- **세부UC 참조**: [주문서 제출] 주문서 작성·제출 Bolt (DK §3)
- **상태전이**: `TEMP` → `STOCK_REQUESTED` (플랫폼주문·판매자 주문·주문상품 일괄). 이후 `STOCK_DEDUCTED`·`DEPOSIT_PENDING`·`STOCK_FAILED`는 §4-1
- **원칙**: ① 상품·쿠폰·포인트는 요청 바디가 아니라 주문서 진입 시 저장된 임시주문(DB)에서 읽어 서버가 재검증·재계산한다(요청 바디의 `items`/`couponId`/`pointUsed`는 무시). ② 재고차감 요청은 주문 상태 변경과 **같은 트랜잭션**으로 아웃박스에 적재한다. ③ PG 요청(가상계좌 발급)은 접수 응답 후 컨슈머가 처리한다(응답에 포함되지 않음)

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title POST /api/mobile/v1/my/orders/{orderSheetId}/pay — 결제하기 접수 (비동기 접수, 2026-10-29 현행)

actor 고객 as Client
participant "OrderController" as OC
participant "OrderService" as OS
participant "MemberApi" as MEM
participant "PromotionApi" as PROMO
participant "PlatformOrderRepository" as POR
participant "OutboxEventRepository" as OB
participant "OrderStatusHistoryService" as HIS
database "DB (ord_*)" as DB

Client -> OC : POST .../orders/{sheetId}/pay\n{addressId, paymentMethodType,\nrefundAccount(가상계좌 시, 미구현), termsAgreed}
activate OC
OC -> OS : placeOrder(memberId, sheetId, request)
activate OS

== ① validation ==
OS -> OS : validatePayRequest()\n(addressId·필수 약관 T001~T003·결제수단 허용값·CARD 차단·\n가상계좌면 refundAccount 필수·예금주=주문자 실명 확인(미구현))
alt 검증 실패
  OS --> OC : 400 ADDRESS_REQUIRED / TERMS_NOT_AGREED /\nINVALID_PAYMENT_METHOD / PAYMENT_METHOD_NOT_READY /\nREFUND_ACCOUNT_REQUIRED / REFUND_ACCOUNT_INVALID(미구현)
end

== ② execute — 임시주문 확정(동기) ==
OS -> POR : findByPlatformOrderNo(sheetId)
alt 없음 / 타인 / TEMP 아님
  OS --> OC : 404 ORDER_SHEET_NOT_FOUND / 403 ORDER_SHEET_FORBIDDEN /\n422 ORDER_SHEET_ALREADY_PROCESSED
end
OS -> MEM : getPointBalance(memberId)
OS -> PROMO : validateCoupon(저장된 couponCode, 임시주문 상품)
alt 포인트 초과 / 쿠폰 부적용
  OS --> OC : 422 POINT_EXCEED / COUPON_NOT_APPLICABLE
end
OS -> OS : 배송지 확정(OrderAddressMock.resolve) +\n금액 확정 (주문금액 = 상품금액 − 할인금액 + 배송비 − 배송비 할인금액,\n결제금액 = 주문금액 − 포인트)
OS -> POR : save — 플랫폼주문·판매자 주문·상품 status=STOCK_REQUESTED
POR -> DB : UPDATE ord_platform_order / ord_order / ord_order_item
OS -> OB : save(STOCK_DEDUCT_REQUESTED, payload=결제수단)\n(같은 트랜잭션)
OB -> DB : INSERT ord_outbox_event
OS -> HIS : record(TEMP → STOCK_REQUESTED, "주문 접수, 재고차감 요청")
HIS -> DB : INSERT ord_status_history

== ③ dto convert ==
OS --> OC : PayResponse(status=STOCK_REQUESTED, totalOrderAmount, totalPayment,\nmessage="주문이 접수되었습니다. 재고 확인 후 결제가 진행됩니다")
deactivate OS
OC --> Client : 200 SUCCESS — "접수 완료" 화면 이동
deactivate OC

note right of OB
  재고 차감(STOCK_DEDUCTED)과 PG 요청(DEPOSIT_PENDING)은 이 응답에 포함되지 않는다.
  컨슈머가 아웃박스를 폴링해 비동기로 처리한다 → §4-1
end note
@enduml
```

> **환불계좌 (REQ-PAY-031, 미구현)**: 가상계좌 결제는 요청 바디에 `refundAccount`(은행·계좌번호·예금주, 예금주=주문자 본인·실명 확인)를 받아 결제에 저장한다. 현행 프로토타입은 이 필드를 받지 않는다(DL §6). 카드·간편결제는 불필요하며 마이페이지 환불계좌 등록은 폐기됐다.

> **현행 동작 메모**: 접수 응답의 `status`는 `STOCK_REQUESTED`다(구 `PAYMENT_PENDING`·`DEPOSIT_PENDING` 아님). 카드는 아직 차단(`PAYMENT_METHOD_NOT_READY`)이고 가상계좌만 진행한다. PG 실패·입금 통보·입금기한 만료는 미구현이다(DH 구현 현행화). 접수 후 진행 상태(재고 확인 중 → 입금 대기)는 화면이 폴링하지 않아 고정 안내문만 보인다(DN `order-complete.md`, Bolt14 SC29-1).

### 4-1. 재고차감·PG 요청 비동기 처리 — 아웃박스 + 별도 컨슈머 앱 (2026-10-26 신설)

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title 결제하기 이후 비동기 처리 (컨슈머 앱: 이벤트 조회·상태관리 / 업무 처리: API 호출)

participant "OrderService(API)" as OS
database "ord_outbox_event" as OB
participant "OrderEventConsumer\n(runNshop-consumer, @Scheduled)" as CON
participant "OrderInternalController(API)\nPOST /api/internal/v1/order-events/process" as IC
participant "OrderEventHandler(API)" as H
participant "CatalogApi(StockService)" as CAT
participant "PaymentApi" as PAY

OS -> OS : 주문 STOCK_REQUESTED
OS -> OB : STOCK_DEDUCT_REQUESTED 적재 (같은 트랜잭션)
OS --> OS : 200 응답(status=STOCK_REQUESTED)

loop 폴링(1초)
  CON -> OB : PENDING 조회
  CON -> IC : 업무 처리 요청 {eventType, platformOrderId, payload}
  IC -> H : process()
  alt STOCK_DEDUCT_REQUESTED
    H -> CAT : deductStock(platformOrderNo, items)
    alt 전 SKU 차감 성공
      H -> H : 주문 STOCK_DEDUCTED + 이력
      IC --> CON : result=STOCK_DEDUCTED
      CON -> OB : PAYMENT_REQUESTED 적재 + 이벤트 DONE
    else 일부 SKU 재고 부족/미등록 (성공분은 유지)
      IC --> CON : result=STOCK_PARTIAL (주문 상태 불변)
      CON -> OB : retry_count+1, 백오프 후 PENDING (재시도 시 실패 SKU만 재차감)
    end
  else PAYMENT_REQUESTED
    H -> PAY : requestPayment()
    H -> H : 주문 DEPOSIT_PENDING + 이력
    IC --> CON : result=DEPOSIT_PENDING
    CON -> OB : 이벤트 DONE
  end
end
note over CON : 실패(호출 오류/STOCK_PARTIAL) 3회 도달 → 이벤트 FAILED\n+ give-up API(차감분 복원, 주문 STOCK_FAILED)
@enduml
```

> 컨슈머는 다중 인스턴스 실행 가능(이벤트 점유 `FOR UPDATE SKIP LOCKED` + PROCESSING, 임대 만료 시 PENDING 복귀). API 처리는 멱등(이미 처리된 주문은 현재 상태를 result로 반환, 재고 차감은 SKU 단위 멱등).


### 4-2. [폐기] 이전 설계·구현 이력 (2026-10-19 이전)

> **주의 — 아래 두 다이어그램은 현행과 다르다.** 첫째는 동기 재고 선점(`reserveStock`)과 `ORDER_RECEIVED`/`PAYMENT_PENDING`, PG 승인 큐(타임아웃 30초)를 쓰는 **원안**이고, 둘째는 요청 바디 `items`로 상품을 받아 PG 요청까지 동기로 끝내던 **2026-10-19 프로토타입 구현**이다. 현행은 위 §4와 §4-1이며, 구현·테스트는 현행을 기준으로 한다. PG 승인 대기시간은 정책서 확정(3초, 4.2.5)과 달라 Bolt5 착수 전 재작성한다. 이력 보존용으로만 남긴다.

> 최종 수정: 2026-10-19 (실제 구현 반영 — URL 정정 + 실제 구현 보조 다이어그램 추가)

> **(2026-10-19 구현 확인·보완)** 제목·다이어그램 URL을 구버전(`/api/v1/orders/{orderSheetId}/pay`)에서 실제 Controller 매핑(`/api/mobile/v1/my/orders/{orderSheetId}/pay`, `OrderController.kt`)으로 정정했다 — §3과 동일 사유로 이번 작업에서 발견·추가 정정.

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title POST /api/mobile/v1/my/orders/{orderSheetId}/pay — 결제 요청

actor 고객 as Client
participant "CustomerOrderController" as OC
participant "OrderService" as OS
participant "CatalogPublicApi" as CAT
participant "PaymentPublicApi" as PAY
participant "OrderRepository" as OR
database "DB (ord_*)" as DB

Client -> OC : POST /api/mobile/v1/my/orders/{sheetId}/pay\n{addressId, couponId, pointUsed, paymentMethod, termsAgreed}
activate OC

OC -> OS : placeOrder(memberId, sheetId, request)
activate OS

== 유효성 검증 ==
OS -> OS : 배송지·약관 검증
alt 검증 실패
  OS --> OC : ADDRESS_REQUIRED / TERMS_NOT_AGREED
  OC --> Client : 400 에러
end

== 주문 생성 ==
OS -> OR : save(platformOrder + orders)
OR -> DB : INSERT ord_platform_order, ord_order, ord_order_item
DB --> OR : OK

== 주문 접수 (동기) ==
OS -> OR : updateStatus(ORDER_RECEIVED)
OR -> DB : UPDATE status

== 재고 선점 (동기) ==
OS -> CAT : reserveStock(items)
activate CAT
alt 재고 부족
  CAT --> OS : STOCK_NOT_AVAILABLE
  OS -> OR : updateStatus(STOCK_FAILED)
  OS --> OC : 409 에러
  OC --> Client : 409 STOCK_NOT_AVAILABLE
else 재고 선점 성공
  CAT --> OS : 선점 성공
  deactivate CAT
  OS -> OR : updateStatus(PAYMENT_PENDING)

  == 결제 요청 접수 (동기 — PG 승인은 비동기) ==
  OS -> PAY : requestPayment(orderId, amount, method, cardHash)
  activate PAY
  PAY -> PAY : checkCardRestriction(cardHash)\n(REQ-PAY-018, pay_card_restriction 조회)
  alt 카드 당일 차단 상태
    PAY --> OS : CARD_RESTRICTED
    OS --> OC : CARD_RESTRICTED
    OC --> Client : 409 에러\n"카드가 당일 결제 제한 상태입니다"
  else 정상
    PAY -> PAY : PG 승인 요청 큐 등록\n(재시도 최대 3회, 타임아웃 30초 — Payment 내부 비동기 처리)
    PAY --> OS : 접수됨 (paymentId)
    deactivate PAY
    OS --> OC : 202 접수 (status=PAYMENT_PENDING)
    OC --> Client : 200 SUCCESS\n"결제 진행 중" 화면 즉시 이동
  end
end
deactivate OS
deactivate OC

note right of PAY
  PG 승인 성공/실패 결과는 이 응답에 포함되지 않는다.
  Payment가 비동기로 PAYMENT_APPROVED/PAYMENT_FAILED
  이벤트를 발행하면 §16에서 소비해 최종 상태를 확정한다.
  PG 콜백 처리 자체는 §4-1 참조.
end note

@enduml
```

> **(2026-10-19 구현 확인, 2026-10-20 네이밍 갱신)** 위 note가 설명하는 §16 컨슈머(PAYMENT_APPROVED/PAYMENT_FAILED)는 현재 호출되지 않는다 — `EventPublisher`/이벤트 발행 코드 자체가 `OrderService.placeOrder()`에 없다. 결제 확정은 `PaymentApi.requestPayment()`(옛 이름: PaymentPublicApi)의 동기 응답(`accepted=true` 고정)만으로 즉시 끝난다.

> **신규 (2026-10-19 프로토타입 구현): 실제 흐름은 재고선점·PG 비동기 승인을 생략하고 즉시 완결된다**(상세: `.agents/tasks/order-create-mobile-api/design.md` §4-2). Cart 영속 계층이 없어 결제 대상 상품은 요청 바디 `items[]`로 직접 받고(DL §6 보완 참조), `sheetId`는 로깅/추적 전용 stateless 값이라 이 메서드 어디서도 조회에 쓰이지 않는다. 참여자 이름은 2026-10-20 네이밍 갱신(`XxxPublicApi`→`XxxApi`)을 반영한다.

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title POST /api/mobile/v1/my/orders/{orderSheetId}/pay — 결제 요청 (실제 구현)

actor 고객 as Client
participant "OrderController" as OC
participant "OrderService" as OS
participant "MemberApi" as MEM
participant "PromotionApi" as PROMO
participant "PlatformOrderRepository" as POR
participant "PaymentApi" as PAY
database "DB (ord_*)" as DB

Client -> OC : POST .../orders/{sheetId}/pay\n{addressId, couponId, pointUsed, paymentMethodType, termsAgreed}
activate OC

OC -> OS : placeOrder(memberId=1L, sheetId, request)
activate OS

== ① validation ==
OS -> OS : validatePayRequest()\n(items/addressId/termsAgreed/paymentMethodType/수량·가격)
alt 검증 실패
  OS --> OC : 400 (CART_ITEMS_REQUIRED 등)
end

== ② execute ==
OS -> MEM : getPointBalance(memberId)
MEM --> OS : PointInfo(balance=15000)
opt pointUsed가 잔액 또는 할인후금액 초과
  OS --> OC : 422 POINT_EXCEED
end
opt couponId 있음
  OS -> PROMO : validateCoupon(memberId, couponId, items)
  PROMO --> OS : CouponDiscountResult
  alt applicable=false
    OS --> OC : 422 COUPON_NOT_APPLICABLE
  end
end
OS -> OS : OrderAddressMock.resolve(addressId)\n(Mock addresses[] 조회)
OS -> POR : save(platformOrder) [자식 없음, 1차 저장]
POR -> DB : INSERT ord_platform_order
DB --> POR : id 확보
OS -> OS : vendor별 Order/OrderItem\n(+쿠폰 시 PlatformOrderDiscount) 생성
OS -> POR : save(platformOrder) [cascade, 2차 저장]
POR -> DB : INSERT ord_order, ord_order_item, (ord_platform_order_discount)
OS -> PAY : requestPayment(platformOrderNo, paymentAmount, paymentMethodType)
PAY --> OS : PaymentResult(accepted=true)

== ③ dto convert ==
OS --> OC : PayResponse(status=DEPOSIT_PENDING, message="입금 대기중입니다")
deactivate OS
OC --> Client : 200 SUCCESS
deactivate OC

@enduml
```

---

## 5. [API] POST /api/mobile/v1/my/orders/{orderId}/cancel — 고객 주문 취소

> 최종 수정: 2026-10-29 (현행 결정 반영 — 입금대기 취소 추가, 입금 통보 경합 시 취소 우선, 취소 클레임 생성)

- **세부UC 참조**: [고객 단순 취소] 고객 주문 취소 Bolt (DK §5)
- **상태전이**: Order `DEPOSIT_PENDING`/`PAYMENT_COMPLETED` → `CANCELLED`. 취소 클레임(`claim_type=CANCEL`, channel=SELF): 입금대기는 `RECEIVED`→`COMPLETED`, 결제완료는 `RECEIVED`→`REFUNDED`→`COMPLETED`
- **원칙**: ① 고객 직접 취소는 **입금대기·결제완료**에서만 허용한다(REQ-ORD-018·080). `PREPARING`(송장 등록 전)은 시스템상 취소요청·승인 절차가 없고 고객센터 문의 → 어드민 CS 예외 취소(§11)이며, 배송중(송장 등록 후)은 취소·반품 모두 불가(배송완료 후 반품·교환). ② 취소는 주문 전체 단위(부분 취소 없음). ③ 입금대기 취소는 가상계좌 폐기 + 재고 복원만 하고 환불은 없다. ④ 취소 처리와 같은 트랜잭션에서 취소 클레임을 생성한다(REQ-ORD-082, 상태 흐름은 제안값). ⑤ 입금대기 취소·취소 클레임·입금 통보 경합은 **미구현**이다(현행은 결제완료 취소 경로 위주 설계안).

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title POST /api/mobile/v1/my/orders/{orderId}/cancel — 고객 주문 취소

actor 고객 as Client
participant "OrderController" as OC
participant "OrderService" as OS
participant "OrderRepository" as OR
participant "ClaimService" as CLM
participant "PaymentApi" as PAY
participant "CatalogApi" as CAT
database "DB (ord_*)" as DB

Client -> OC : POST /api/mobile/v1/my/orders/{orderId}/cancel\n{cancelReason}
activate OC

OC -> OS : cancelOrder(memberId, orderId, reason)
activate OS

OS -> OR : findById(orderId) (행 잠금)
OR -> DB : SELECT ... FOR UPDATE
DB --> OR : order
OR --> OS : order

alt 주문 상태 PREPARING (송장 등록 전)
  OS --> OC : 409 CANCEL_NOT_ALLOWED\n"출고 준비 중에는 직접 취소할 수 없습니다. 고객센터로 문의해주세요"
else 배송중(PREPARING + 송장 등록 후) 또는 DELIVERED 이후
  OS --> OC : 409 CANCEL_NOT_ALLOWED\n"배송 중에는 취소할 수 없습니다. 배송완료 후 반품을 이용해주세요"
else 취소 가능 (canCancel = DEPOSIT_PENDING, PAYMENT_COMPLETED)

  OS -> OR : updateStatus(CANCELLED, reason, changedBy=memberId)
  OR -> DB : UPDATE ord_* + INSERT ord_status_history

  alt DEPOSIT_PENDING (입금대기 — 입금 전)
    OS -> PAY : discardVirtualAccount(platformOrderNo) (안)\n발급 가상계좌 폐기 — 환불 없음
    OS -> CAT : restoreStock(items)
    OS -> CLM : createCancelClaim(order, channel=SELF, reason)
    CLM -> DB : INSERT ord_claim (CANCEL, RECEIVED → COMPLETED)
    OS --> OC : CancelResponse(status=CANCELLED, refundAmount=0, claimNo)
  else PAYMENT_COMPLETED (결제완료)
    OS -> CLM : createCancelClaim(order, channel=SELF, reason, refundAmount)
    CLM -> DB : INSERT ord_claim (CANCEL, RECEIVED)
    OS -> PAY : requestRefund(orderId, amount) [비동기 이벤트: ORDER_CANCELLED]
    OS -> CAT : restoreStock(items) [비동기 이벤트: ORDER_CANCELLED]
    note right of CLM : 환불 완료 시 REFUNDED → COMPLETED
    OS --> OC : CancelResponse(status=CANCELLED, refundAmount, claimNo)
  end
  deactivate OS
  OC --> Client : 200 SUCCESS
  deactivate OC
end

@enduml
```

### 5-1. 입금 통보와 취소 경합 — 취소 우선 (REQ-ORD-080, REQ-PAY-030, AC-ORD-092)

> 입금대기 주문에 고객 취소와 가상계좌 입금 통보가 동시에 도착하면 **취소가 우선**한다. 주문 행 잠금(또는 낙관적 락 `version`)으로 직렬화하며, 먼저 커밋된 쪽을 따른다. 취소가 확정된 뒤 도착한 입금 통보는 주문을 PAYMENT_COMPLETED로 바꾸지 않고 입금액을 환불 대상으로 기록해 **저장된 환불계좌로 운영자 승인 없이 자동 환불**한다(사유 `LATE_DEPOSIT`, 기준일=입금 통보 수신일, 기한 정책 8.1.3 3영업일). 입금 통보 처리 자체는 Payment 도메인 시퀀스([payment.md §4-3](payment.md))·DH를 따른다. **미구현**.

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title 입금 통보와 고객 취소 경합 — 취소 우선 (미구현)

actor 고객 as Client
participant "OrderService" as OS
participant "PaymentService" as PAY
participant "PG(가상계좌)" as PG
database "DB (ord_*, pay_*)" as DB

par 고객 취소
  Client -> OS : POST .../cancel
  OS -> DB : 주문 행 잠금 → DEPOSIT_PENDING 확인
  OS -> DB : CANCELLED 커밋 + 취소 클레임(CANCEL) + 재고 복원 + 가상계좌 폐기
else 입금 통보
  PG -> PAY : 입금 통보(가상계좌, 금액)
  PAY -> DB : 주문 행 잠금 요청 (취소 트랜잭션 대기)
end

alt 취소가 먼저 커밋 (취소 우선)
  PAY -> DB : 주문 상태 재확인 = CANCELLED
  PAY -> DB : 결제를 PAID로 바꾸지 않음, 입금액을 환불 대상으로 기록
  PAY -> PG : 저장된 환불계좌로 자동 환불 요청 (reason=LATE_DEPOSIT, 3영업일 기한)
  note right of PAY : 운영자 승인 없음 — AC-PAY-035
else 입금 통보가 먼저 커밋 (취소 전에 이미 PAID)
  PAY -> DB : 결제 PAID, 주문 PAYMENT_COMPLETED
  OS --> Client : 이후 취소 요청은 결제완료 취소(환불 경로)로 처리
end
@enduml
```


---

## 6. [API] POST /api/mobile/v1/my/orders/{orderId}/confirm — 구매확정

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title POST /api/mobile/v1/my/orders/{orderId}/confirm — 구매확정

actor 고객 as Client
participant "CustomerOrderController" as OC
participant "OrderService" as OS
participant "OrderRepository" as OR
participant "EventPublisher" as EP
database "DB (ord_*)" as DB

Client -> OC : POST /api/mobile/v1/my/orders/{orderId}/confirm
activate OC

OC -> OS : confirmOrder(memberId, orderId)
activate OS

OS -> OR : findById(orderId)
OR -> DB : SELECT
DB --> OR : order
OR --> OS : order

alt 주문 상태 != DELIVERED
  OS --> OC : CONFIRM_NOT_ALLOWED
  OC --> Client : 409 에러
else
  OS -> OR : updateStatus(CONFIRMED)
  OR -> DB : UPDATE + INSERT ord_status_history
  DB --> OR : OK

  OS -> EP : publish(ORDER_CONFIRMED)
  note right of EP: Settlement → 정산 등록\nMember → 포인트 적립

  OS --> OC : ConfirmResponse(pointEarned)
  deactivate OS
  OC --> Client : 200 SUCCESS
  deactivate OC
end

@enduml
```


---

## 7. [API] POST /api/mobile/v1/my/orders/{orderId}/claims — 반품/교환 신청

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title POST /api/mobile/v1/my/orders/{orderId}/claims — 반품/교환 신청

actor 고객 as Client
participant "CustomerClaimController" as CC
participant "ClaimService" as CS
participant "OrderRepository" as OR
participant "ClaimRepository" as CR
participant "EventPublisher" as EP
database "DB (ord_*)" as DB

Client -> CC : POST /api/mobile/v1/my/orders/{orderId}/claims\n{claimType, reason, detailReason, responsibility, images[], exchangeSkuId?}
activate CC

CC -> CS : createClaim(memberId, orderId, request)
activate CS

CS -> OR : findById(orderId)
OR -> DB : SELECT
DB --> OR : order
OR --> CS : order

CS -> CS : 유효성 검증
alt 주문 상태 != DELIVERED
  CS --> CC : CLAIM_NOT_ALLOWED
  CC --> Client : 409 에러\n(구매확정(CONFIRMED) 후면 "구매확정 후에는 고객센터로 문의해주세요" —\n고객 모바일 접수 불가, 어드민 접수만 가능: REQ-ORD-081)
else 사유별 기한 초과\n(단순변심: 배송완료 후 10일 /\n하자·오배송: 배송완료 후 3개월 또는 안 날부터 30일, 정책 7.2.2)
  CS --> CC : CLAIM_PERIOD_EXPIRED
  CC --> Client : 422 에러
else responsibility=VENDOR 인데 images가 빈 배열
  CS --> CC : CLAIM_PHOTO_REQUIRED (REQ-ORD-058)
  CC --> Client : 400 에러
else claimType=EXCHANGE 인데 exchangeSkuId의 productId가 원 주문 상품과 다름
  CS --> CC : EXCHANGE_SKU_MISMATCH (REQ-ORD-070)
  CC --> Client : 422 에러
else 정상
  CS -> CR : save(newClaim{status=RECEIVED, submitted_responsibility=request.responsibility})
  CR -> DB : INSERT ord_claim
  note right of CR: submitted_responsibility는 고객 자진신고값으로 보존(REQ-ORD-076)\nCS 귀책판정(§7-1)의 최종 responsibility와 별도 컬럼
  CS -> CR : saveImages(claimId, images, uploadedBy=CUSTOMER)
  CR -> DB : INSERT ord_claim_image (uploaded_by=CUSTOMER, 최대 3장, REQ-ORD-075)
  DB --> CR : OK

  CS -> EP : publish(CLAIM_RECEIVED)
  note right of EP: Notification* → 고객 알림톡+이메일\n("클레임 접수 완료")

  CS --> CC : ClaimResponse(claimId, status)
  deactivate CS
  CC --> Client : 201 CREATED
  deactivate CC
end

@enduml
```


---

## 7-1. [API] POST /api/admin/v1/claims/{claimId}/blame-decision — 귀책 판정

> 신규 (2026-08-21 바텀업 재검증): 인터페이스명세(DL) §19-1에는 있었지만 시퀀스가 없던 것을 보완. CUSTOMER/VENDOR 분기와 EXCHANGE 재고선점 실패(REQ-ORD-069)까지 포함한 전체 분기를 다룬다.

- **트리거**: CS 담당자가 클레임 접수 내용을 확인하고 귀책을 확정
- **상태전이**: Claim `RECEIVED` → `PAYMENT_PENDING`(CUSTOMER) / `RECEIVED` 유지 + shipment(PICKUP) 생성 → 이후 §12/§14 경유 `INSPECTING`(VENDOR)

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title POST /api/admin/v1/claims/{claimId}/blame-decision — 귀책 판정

actor "CS 담당자" as Admin
participant "AdminClaimController" as ACC
participant "ClaimService" as CS
participant "ClaimRepository" as CR
participant "CatalogPublicApi" as CAT
participant "ShipmentService" as Ship
participant "EventPublisher" as EP

Admin -> ACC : POST /api/admin/v1/claims/{claimId}/blame-decision\n{responsibility}
activate ACC

ACC -> CS : decideResponsibility(adminId, claimId, responsibility)
activate CS

CS -> CR : findById(claimId)
CR --> CS : claim(submitted_responsibility, claimType)

alt responsibility == CUSTOMER
  CS -> CR : updateResponsibility(responsibility)\nupdateStatus(PAYMENT_PENDING)
  note right of CR: submitted_responsibility는 그대로 유지(불변, REQ-ORD-076)\nresponsibility만 CS 확정값으로 갱신 — 고객 신고와 달라도 됨(REQ-ORD-066)
  CS -> EP : publish(CLAIM_SHIPPING_PAID 대기 알림)
else responsibility == VENDOR
  alt claimType == EXCHANGE
    CS -> CAT : reserveStock(exchangeSkuId)
    alt 재고 없음
      CAT --> CS : StockInsufficientException
      CS --> ACC : EXCHANGE_STOCK_UNAVAILABLE (REQ-ORD-069)
      ACC --> Admin : 409 에러\n"교환 가능한 재고가 없습니다"
    else 재고 확보
      CAT --> CS : success
      CS -> Ship : createShipment(refType=CLAIM, shipmentType=EXCHANGE_OUT)
      CS -> Ship : createShipment(refType=CLAIM, shipmentType=PICKUP)
      CS -> CR : updateResponsibility(responsibility)
      CS -> EP : publish(CLAIM_EXCHANGE_SHIPPED)
    end
  else claimType == RETURN/CANCEL
    CS -> Ship : createShipment(refType=CLAIM, shipmentType=PICKUP)
    CS -> CR : updateResponsibility(responsibility)
  end
end

CS --> ACC : ClaimResponse(responsibility, status)
deactivate CS
ACC --> Admin : 200 SUCCESS
deactivate ACC

@enduml
```


---

## 7-2. [API] POST /api/mobile/v1/my/claims/{claimId}/cancel — 고객 클레임 자진 취소

> 신규 (2026-08-21 바텀업 재검증): REQ-ORD-073/071 대응. RECEIVED/PAYMENT_PENDING 상태까지만 허용, INSPECTING 이후는 거부.

- **트리거**: 고객이 마이페이지 클레임상세에서 취소 요청
- **상태전이**: Claim `RECEIVED`/`PAYMENT_PENDING` → `REJECTED`(사유="고객 자진 철회")

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title POST /api/mobile/v1/my/claims/{claimId}/cancel — 고객 클레임 자진 취소

actor 고객 as Client
participant "CustomerClaimController" as CC
participant "ClaimService" as CS
participant "ClaimRepository" as CR
participant "NotificationPublicApi" as Noti

Client -> CC : POST /api/mobile/v1/my/claims/{claimId}/cancel
activate CC

CC -> CS : cancelClaim(memberId, claimId)
activate CS

CS -> CR : findById(claimId)
CR --> CS : claim(status)

alt status NOT IN [RECEIVED, PAYMENT_PENDING]
  CS --> CC : CLAIM_CANCEL_NOT_ALLOWED (REQ-ORD-071)
  CC --> Client : 409 에러\n"귀책 판정/수거 시작 이후에는 취소할 수 없습니다"
else 정상
  CS -> CR : updateStatus(REJECTED, reason="고객 자진 철회")
  CS -> Noti : sendKakaoAlimtalk("클레임 취소 완료")
  CS --> CC : ClaimResponse(status=REJECTED)
  deactivate CS
  CC --> Client : 200 SUCCESS
  deactivate CC
end

@enduml
```


---

## 8. [API] POST /api/partner/v1/orders/{orderId}/ship — 출고 처리

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title POST /api/partner/v1/orders/{orderId}/ship — 출고 처리

actor 판매자 as Partner
participant "PartnerOrderController" as POC
participant "ShippingService" as SS
participant "OrderRepository" as OR
participant "ShipmentRepository" as SR
database "DB (ord_*)" as DB

Partner -> POC : POST /api/partner/v1/orders/{orderId}/ship
activate POC

POC -> SS : shipOrder(vendorId, orderId)
activate SS

SS -> OR : findByIdAndVendor(orderId, vendorId)
OR -> DB : SELECT
DB --> OR : order
OR --> SS : order

alt 상태 != PAYMENT_COMPLETED
  SS --> POC : SHIP_NOT_ALLOWED
  POC --> Partner : 409 에러
else
  SS -> OR : updateStatus(PREPARING)
  OR -> DB : UPDATE + INSERT ord_status_history
  DB --> OR : OK

  SS -> SR : save(shipment{refType=ORDER, refId=orderId, type=OUTBOUND, status=PENDING})
  SR -> DB : INSERT ord_shipment
  DB --> SR : OK
  note right of SR: 배송 실행(운송장 등록·이동·완료)은\nord_shipment(v6, §3)가 전담.\n운송장 등록은 §9에서 PENDING→IN_TRANSIT 전이

  SS --> POC : ShipResponse(status=PREPARING)
  deactivate SS
  POC --> Partner : 200 SUCCESS
  deactivate POC
end

@enduml
```


---

## 9. [API] POST /api/partner/v1/shipping/{orderId} — 운송장 등록

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title POST /api/partner/v1/shipping/{orderId} — 운송장 등록

actor 판매자 as Partner
participant "PartnerShippingController" as SC
participant "ShippingService" as SS
participant "ShipmentRepository" as SR
participant "EventPublisher" as EP
database "DB (ord_*)" as DB

Partner -> SC : POST /api/partner/v1/shipping/{orderId}\n{deliveryCompany, trackingNo}
activate SC

SC -> SS : registerTracking(vendorId, orderId, request)
activate SS

alt 운송장번호 누락
  SS --> SC : TRACKING_NO_REQUIRED
  SC --> Partner : 400 에러
else
  SS -> SR : updateStatus(refType=ORDER, refId=orderId, type=OUTBOUND,\nstatus=IN_TRANSIT, carrier, trackingNumber, shippedAt)
  SR -> DB : UPDATE ord_shipment (PENDING → IN_TRANSIT)
  DB --> SR : OK
  note right of SR: 주문 자체(ord_order.status)는 변경 없음 — PREPARING 유지.\n"배송 중" 표시는 PREPARING + shipment(OUTBOUND).status=IN_TRANSIT\n조인으로 화면에서 계산(상태머신(DH) v6 참조). 배송완료 파생 전환은 §19 배치 참조.

  SS -> EP : publish(SHIPPING_STARTED)
  note right of EP: Notification* → 고객 알림톡\n("상품 발송, 송장번호")

  SS --> SC : TrackingResponse(shipmentStatus=IN_TRANSIT, shippedAt)
  deactivate SS
  SC --> Partner : 200 SUCCESS
  deactivate SC
end

@enduml
```


---

## 10. [배치] 클레임 자동완료 — REFUNDED/DISPOSED → COMPLETED

- **트리거**: 스케줄러 (매 시간 정각)
- **상태전이**: Claim `REFUNDED` → `COMPLETED`, Claim `DISPOSED` → `COMPLETED` (배치 자동 전환)
- **비고**: Claim 11상태 모델(DH)에는 어드민이 직접 호출하는 "클레임 완료" API가 없다. `PICKED_UP → REFUNDED`는 §13(환불 처리), `PICKUP_REJECTED → DISPOSED`는 §20(폐기 처리)에서 각각 어드민이 수행하고, `REFUNDED`/`DISPOSED`에 도달한 클레임은 본 배치가 주기적으로 스캔해 `COMPLETED`로 자동 전환한다. `RETURN_PAYMENT_PENDING → COMPLETED`(shipment(RETURN) DELIVERED 기준) 자동전환은 택배사 반송완료 확인과 같은 배치에서 처리하므로 §19를 참조. **`CLAIM_COMPLETED`는 정산·알림·재고복원·포인트 복원 이벤트**이며 Payment는 이 이벤트로 환불하지 않는다 — 클레임(반품) 환불은 어드민 [환불 처리](§13, API-029)만 트리거한다(2026-11-03 확정). 교환 클레임은 환불이 없어 이 배치 대상이 아니며, 맞교환 출고 shipment(EXCHANGE_OUT) 배송완료 시 `PICKED_UP → COMPLETED`로 전환된다(§19).

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title [배치] 클레임 자동완료 (REFUNDED/DISPOSED → COMPLETED)

participant "Scheduler\n(ClaimAutoCompleteBatch)" as Batch
participant "ClaimService" as CS
participant "ClaimRepository" as CR
participant "CatalogPublicApi" as CAT
participant "MemberPublicApi" as MEM
participant "EventPublisher" as EP
participant "NotificationPublicApi" as Noti
database "DB (ord_claim)" as DB

Batch -> CS : autoCompleteClaims()
activate CS

CS -> CR : findByStatusIn([REFUNDED, DISPOSED])
CR -> DB : SELECT
DB --> CR : List<Claim>
CR --> CS : claims

loop 각 클레임
  CS -> CR : updateStatus(COMPLETED)
  CR -> DB : UPDATE
  DB --> CR : OK

  CS -> EP : publish(CLAIM_COMPLETED)

  alt claimType == RETURN && 이전상태 == REFUNDED
    CS -> CAT : restoreStock(claimId, originalSkuItems)
    note right of CAT: RETURN: 원 SKU 재고 복원\n(EXCHANGE는 §14 검수합격 시점에 선반영됨)
  end
  CS -> MEM : restorePoints(claimId)\n(사용 포인트 복원, 해당 시)

  CS -> Noti : sendKakaoAlimtalk("클레임 완료 안내")
end

deactivate CS
@enduml
```


---

## 11. [API] POST /api/admin/v1/orders/{orderId}/force-cancel — CS 예외 취소

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title POST /api/admin/v1/orders/{orderId}/force-cancel — CS 예외 취소

actor "CS 담당자" as Admin
participant "AdminOrderController" as AOC
participant "OrderService" as OS
participant "OrderRepository" as OR
participant "EventPublisher" as EP
database "DB (ord_*)" as DB

Admin -> AOC : POST /api/admin/v1/orders/{orderId}/force-cancel\n{reason}
activate AOC

AOC -> OS : forceCancel(adminId, orderId, reason)
activate OS
note over OS : 취소 처리와 같은 트랜잭션에서\nclaim_type=CANCEL 클레임 생성(channel=CS, REQ-ORD-082, 2026-10-29)

OS -> OR : findById(orderId)
OR -> DB : SELECT
DB --> OR : order
OR --> OS : order

alt 주문이 PREPARING이 아니거나 출고 shipment(OUTBOUND)가 PENDING이 아님 (송장 등록 후)
  OS --> AOC : 409 CANCEL_NOT_ALLOWED
  AOC --> Admin : 409 (배송완료 후 반품 안내)
else PREPARING + 출고 shipment PENDING
  OS -> OR : updateStatus(CANCELLED, reason, changedBy=adminId)
OR -> DB : UPDATE + INSERT ord_status_history
DB --> OR : OK

OS -> EP : publish(ORDER_CANCELLED)
note right of EP
  Payment → 환불 요청
  Catalog → 재고 복원
end note
end

OS --> AOC : CancelResponse(status=CANCELLED, refundAmount)
deactivate OS
AOC --> Admin : 200 SUCCESS
deactivate AOC

@enduml
```


---

## 12. [API] POST /api/mobile/v1/my/claims/{claimId}/shipping-payment — 클레임 배송비 결제

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title POST /api/mobile/v1/my/claims/{claimId}/shipping-payment — 클레임 배송비 결제

actor 고객 as Client
participant "CustomerClaimPaymentController" as CPC
participant "ClaimService" as CS
participant "ClaimRepository" as CR
participant "ClaimPaymentRepository" as CPR
participant "ShipmentRepository" as SR
participant "PromotionPublicApi" as PROMO
participant "PaymentPublicApi" as PAY
participant "CatalogPublicApi" as CAT
participant "CourierApi\n(택배사 외부API)" as Courier
participant "EventPublisher" as EP
database "DB (ord_claim*)" as DB

Client -> CPC : POST /api/mobile/v1/my/claims/{claimId}/shipping-payment\n{paymentType, paymentMethodId, couponId}\n(금액은 클라이언트가 보내지 않음 — 서버 산정)
activate CPC

CPC -> CS : payShippingFee(memberId, claimId, request)
activate CS

CS -> CR : findById(claimId)
CR -> DB : SELECT
DB --> CR : claim
CR --> CS : claim

CS -> CS : 배송비 서버 산정 (단순변심 반품 = 편도 3,000원 + 초도 배송비 중 할인받은 금액,\n교환 왕복 6,000원, 반송 편도 3,000원 고정 — 정책 6.9.7, 환불에서 차감하지 않고 별도 결제)

alt 상태 not in (PAYMENT_PENDING, RETURN_PAYMENT_PENDING)
  CS --> CPC : INVALID_STATUS
  CPC --> Client : 409 에러
else 결제 기한 24시간 초과
  CS --> CPC : PAYMENT_EXPIRED
  CPC --> Client : 422 에러
else 정상

  alt 쿠폰 적용
    CS -> PROMO : applyCoupon(couponId, 산정 배송비)
    PROMO --> CS : discountedAmount (0원 가능)
  end

  alt 결제금액 > 0 (서버 산정 배송비 − 쿠폰 할인)
    CS -> PAY : requestPayment(claimId, 결제금액, method)
    activate PAY
    alt PG 실패
      PAY --> CS : PAYMENT_FAILED
      CS --> CPC : 400 에러
      CPC --> Client : 400 에러
    else 성공
      PAY --> CS : approved
      deactivate PAY
    end
  end

  CS -> CPR : save(claimPayment{status=PAID, paymentType})
  CPR -> DB : INSERT ord_claim_payment

  alt paymentType == PICKUP
    CS -> SR : save(shipment{refType=CLAIM, refId=claimId, type=PICKUP, status=PENDING})
    SR -> DB : INSERT ord_shipment
    DB --> SR : OK
    note right of CR: claim.status는 PAYMENT_PENDING 유지 (변경 없음).\n판매자 [입고 확인](§26, API-038) 시\nshipment(PICKUP) DELIVERED + claim INSPECTING으로 전환한다\n(배치는 입고 확인을 하지 않는다).

    CS -> EP : publish(CLAIM_SHIPPING_PAID)
    note right of EP: Notification* → 고객 알림톡+이메일\n("배송비 결제 완료, 수거 진행")

    alt claimType == EXCHANGE
      CS -> CAT : reserveExchangeStock(claimId, exchangeSkuItems)
      activate CAT
      CAT --> CS : success
      deactivate CAT

      CS -> Courier : requestReShipment(claimId, address)\n(교환상품 선출고 — 원상품 수취 이전, 맞교환 원칙)
      Courier --> CS : trackingRegistered

      CS -> SR : save(shipment{refType=CLAIM, refId=claimId, type=EXCHANGE_OUT, status=IN_TRANSIT, trackingNo})
      SR -> DB : INSERT ord_shipment
      DB --> SR : OK
      note right of SR: 귀책판정 완료 시점(본 케이스는 고객귀책+배송비결제 완료 시점)에\nshipment(EXCHANGE_OUT) 병렬 생성 — 맞교환 원칙(REQ-ORD-056).\nclaim.status에는 영향 없음(§10 배치 참조)

      CS -> EP : publish(CLAIM_EXCHANGE_SHIPPED)
      note right of EP: Notification* → 교환상품 발송 알림톡\n(원 SKU 재고 복원은 §14 검수합격 시점)
    end
  else paymentType == RETURN
    CS -> CR : recordReturnPaymentPaid(claimId)
    CR -> DB : UPDATE ord_claim (returnPaymentPaidAt)
    note right of CR: 상태는 RETURN_PAYMENT_PENDING 유지 (변경 없음)

    CS -> SR : save(shipment{refType=CLAIM, refId=claimId, type=RETURN, status=PENDING})
    SR -> DB : INSERT ord_shipment
    DB --> SR : OK
    note right of SR: 판매자 [반송운송장등록] 시 PENDING→IN_TRANSIT.\n택배사 반송완료 확인 시 §19 배치가 shipmentRepo.updateStatus(DELIVERED)\n호출 → 이어서 같은 배치가 claim을 COMPLETED로 자동전환

    CS -> EP : publish(CLAIM_RETURN_SHIPPING_PAID)
    note right of EP: Notification* → 고객 알림톡+이메일\n("반송 배송비 결제 완료")
  end

  CS --> CPC : PaymentResult
  deactivate CS
  CPC --> Client : 200 SUCCESS
  deactivate CPC
end

@enduml
```


---

## 13. [API] POST /api/admin/v1/claims/{claimId}/refund — 환불 처리

> **환불 기한(2026-11-03 확정)**: 환불 승인은 품질 합격 판정이다. 3영업일 기한은 합격 일시부터 세며, 어드민은 합격 후 3영업일 안에 이 API를 호출한다(정책서 8.1.2·8.1.3·8.8.1). 합격 전(회수 송장 집하 시점 등)에는 환불하지 않는다.

> **환불 트리거 단일화(2026-11-03 확정)**: 클레임(반품) 환불은 이 절의 어드민 [환불 처리](API-029) 동기 호출(`requestRefund`)만 트리거한다. 이후 §10 배치가 발행하는 `CLAIM_COMPLETED`는 정산·알림·재고복원·포인트 이벤트일 뿐 Payment는 이 이벤트로 환불하지 않는다(중복 환불 요청 없음). 주문 취소 환불은 `ORDER_CANCELLED`(자동), 입금 통보 경합(LATE_DEPOSIT)은 자동이다.
> 환불금액 = 상품주문금액 + 환불 대상 배송비(고객이 실제 낸 초도 배송비, 전체 취소·판매자 귀책 전체 반품만). 반품·교환 배송비는 별도 결제분이라 차감하지 않는다.

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title POST /api/admin/v1/claims/{claimId}/refund — 환불 처리

actor "CS 담당자" as Admin
participant "AdminClaimController" as ACC
participant "ClaimService" as CS
participant "ClaimRepository" as CR
participant "PaymentPublicApi" as PAY
participant "EventPublisher" as EP
database "DB (ord_claim)" as DB

Admin -> ACC : POST /api/admin/v1/claims/{claimId}/refund\n{refundMethod, bankAccount}
activate ACC

ACC -> CS : processRefund(adminId, claimId, request)
activate CS

CS -> CR : findById(claimId)
CR -> DB : SELECT
DB --> CR : claim
CR --> CS : claim

alt 상태 != PICKED_UP
  CS --> ACC : INVALID_STATUS (수거완료 상태만 환불 가능)
  ACC --> Admin : 409 에러
else 정상

  alt refundMethod == ORIGINAL
    CS -> PAY : requestRefund(orderId, amount)
    activate PAY
    PAY --> CS : refundSuccess
    deactivate PAY
  else refundMethod == BANK_TRANSFER
    CS -> CS : 입금정보 저장 (bankAccount)\n이체는 담당자 수동 진행
  end

  CS -> CR : updateStatus(REFUNDED)
  CR -> DB : UPDATE ord_claim

  CS -> EP : publish(CLAIM_REFUNDED)
  note right of EP: → Notification(환불완료 알림톡+이메일)

  CS --> ACC : RefundResult
  deactivate CS
  ACC --> Admin : 200 SUCCESS
  deactivate ACC
end

@enduml
```


---

## 14. [API] POST /api/partner/v1/claims/{claimId}/inspect-pass — 품질점검 합격

> **교환 종료(2026-11-03 확정)**: 교환은 환불이 없다. 교환 상품은 선출고하므로 합격(PICKED_UP) 판정과 선출고 shipment(EXCHANGE_OUT)의 배송완료(고객 수령)가 모두 충족되면(순서 무관) `PICKED_UP → COMPLETED`로 전환하고, `CLAIM_COMPLETED`는 그 COMPLETED 전환 시(§19) 발행한다 — 합격 시점에는 발행하지 않는다.

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title POST /api/partner/v1/claims/{claimId}/inspect-pass — 품질점검 합격

actor 판매자 as Partner
participant "PartnerClaimController" as PCC
participant "ClaimService" as CS
participant "ClaimRepository" as CR
participant "CatalogPublicApi" as CAT
participant "EventPublisher" as EP
database "DB (ord_claim)" as DB

Partner -> PCC : POST /api/partner/v1/claims/{claimId}/inspect-pass\n{memo}
activate PCC

PCC -> CS : inspectPass(vendorId, claimId, memo)
activate CS

CS -> CR : findById(claimId)
CR -> DB : SELECT
DB --> CR : claim
CR --> CS : claim

alt 상태 != INSPECTING
  CS --> PCC : INVALID_STATUS (품질점검 상태만 합격 가능)
  PCC --> Partner : 409 에러
else 정상
  note right of CS
    합격 판정 기준(DH v4)
    RETURN: 상품 상태 양호(훼손 없음)
    EXCHANGE: 택(TAG) 유지 여부
  end note

  CS -> CR : updateStatus(PICKED_UP, memo)
  CR -> DB : UPDATE ord_claim
  DB --> CR : OK

  alt claimType == EXCHANGE
    CS -> CAT : restoreStock(claimId, originalSkuItems)
    activate CAT
    CAT --> CS : success
    deactivate CAT
    note right of CAT: 원상품 재고 복원\n(교환 SKU는 §12 귀책판정 완료 시점에 shipment(EXCHANGE_OUT)으로\n이미 선출고·차감됨 — 맞교환 원칙)

    note right of CS
      claimType=EXCHANGE는 환불 대상이 아니므로 §13(환불) 없이,
      선출고한 shipment(EXCHANGE_OUT)가 배송완료(고객 수령)이고 합격 상태이면
      §19에서 PICKED_UP → COMPLETED 전환 + CLAIM_COMPLETED 발행
      (합격 시점에는 CLAIM_COMPLETED를 발행하지 않는다)
    end note
  else claimType == RETURN
    note right of CS: 원 SKU 재고복원은 어드민 환불(§13, PICKED_UP→REFUNDED) 이후\n§10 배치(REFUNDED→COMPLETED, CLAIM_COMPLETED 발행)에서 수행
  end

  CS --> PCC : InspectResult(status=PICKED_UP)
  deactivate CS
  PCC --> Partner : 200 SUCCESS
  deactivate PCC
end

@enduml
```


---

## 15. [API] POST /api/partner/v1/claims/{claimId}/inspect-reject — 품질점검 거부

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title POST /api/partner/v1/claims/{claimId}/inspect-reject — 품질점검 거부

actor 판매자 as Partner
participant "PartnerClaimController" as PCC
participant "ClaimService" as CS
participant "ClaimRepository" as CR
database "DB (ord_claim)" as DB

Partner -> PCC : POST /api/partner/v1/claims/{claimId}/inspect-reject\n{rejectReason}
activate PCC

PCC -> CS : inspectReject(vendorId, claimId, rejectReason)
activate CS

alt rejectReason 누락
  CS --> PCC : REASON_REQUIRED
  PCC --> Partner : 400 에러
else

  CS -> CR : findById(claimId)
  CR -> DB : SELECT
  DB --> CR : claim
  CR --> CS : claim

  alt 상태 != INSPECTING
    CS --> PCC : INVALID_STATUS
    PCC --> Partner : 409 에러
  else 정상
    CS -> CR : updateStatus(PICKUP_REJECTED, rejectReason)
    CR -> DB : UPDATE ord_claim
    DB --> CR : OK

    CS --> PCC : InspectResult(status=PICKUP_REJECTED)
    deactivate CS
    PCC --> Partner : 200 SUCCESS
    deactivate PCC
  end
end

@enduml
```


---

## 16. [컨슈머] PAYMENT_APPROVED/PAYMENT_FAILED 이벤트 수신 — 결제 완료·실패 후처리

> **(2026-10-29 개정)**: 현행 결제 접수 흐름은 §4·§4-1이다 — 재고는 접수 후 컨슈머가 차감하고(`STOCK_DEDUCTED`), 가상계좌 발급 후 주문은 **`DEPOSIT_PENDING`(입금대기)**이 된다. 이 절은 구 `PAYMENT_PENDING` 기준을 폐기하고 `DEPOSIT_PENDING`(가상계좌) 또는 결제 인증 대기 상태(안, DH 구현 현행화; 카드 등)를 입력 상태로 한다. 입금 통보·PG 승인 수신 처리, 결제 실패·입금기한(12시간) 만료 보상(§24)은 **미구현**이다(Bolt8 SC18-1, Bolt14 SC10-1·SC28-3).

- **트리거**: Payment 도메인 → `PAYMENT_APPROVED`(승인 또는 가상계좌 입금 통보) 또는 `PAYMENT_FAILED` 이벤트 발행
- **세부UC 참조**: [주문접수] UC-ORD-004 결제완료 후처리
- **상태전이**: Order `DEPOSIT_PENDING`(또는 결제 인증 대기) → `PAYMENT_COMPLETED`(승인·입금 통보, REQ-ORD-013) / `STOCK_DEDUCTED` → `PAYMENT_FAILED`(별도 종료 상태, 누적 실패 3회 도달, 재고 복원, REQ-ORD-014, DH). 결제 실패는 `CANCELLED`가 아니라 `PAYMENT_FAILED`다(2026-11-03 확정). **이미 `CANCELLED`인 주문에 입금 통보가 오면 PAID로 바꾸지 않는다**(취소 우선, §5-1)
- **재시도 기준**: PG 승인 실패 응답·3초 무응답(조회 미승인 확정)은 최초 시도 포함 총 3회(재시도 간격 3초 고정)이며 Payment 내부에서 처리한다. 3회 도달 시에만 `PAYMENT_FAILED`가 발행되어 이 컨슈머가 받는다.

```plantuml
@startuml
title [컨슈머] PAYMENT_APPROVED/PAYMENT_FAILED 수신 — 결제 완료·실패 후처리

participant "EventListener\n(OrderPaymentEventListener)" as Listener
participant "OrderService" as Service
participant "OrderRepository" as Repo
participant "CatalogApi" as Catalog
participant "EventPublisher" as Event
participant "NotificationApi" as Noti

alt PAYMENT_APPROVED 수신 (승인 또는 입금 통보)
    Listener -> Service : handlePaymentApproved(orderId, paymentId)
    activate Service
    Service -> Repo : findById(orderId) (행 잠금)
    Repo --> Service : Order(status)
    alt status == DEPOSIT_PENDING (또는 결제 인증 대기)
        Service -> Repo : updateStatus(PAYMENT_COMPLETED) + 이력
        Service -> Event : publish(ORDER_PAID)
        Service -> Noti : sendKakaoAlimtalk("주문확인")
        Service -> Noti : sendEmail("주문확인")
    else status == CANCELLED (취소가 먼저 확정된 뒤 입금 통보)
        note right of Service : 주문을 PAYMENT_COMPLETED로 바꾸지 않는다 (취소 우선, REQ-ORD-080)\n입금액은 Payment가 저장된 환불계좌로 자동 환불(LATE_DEPOSIT, AC-PAY-035) — §5-1
    end
    deactivate Service
else PAYMENT_FAILED 수신 (누적 실패 3회 도달 — 승인 실패 응답·무응답 합산)
    Listener -> Service : handlePaymentFailed(orderId, paymentId, reason)
    activate Service
    Service -> Repo : findById(orderId)
    Repo --> Service : Order(status=STOCK_DEDUCTED, PG 승인 시도 구간)
    Service -> Catalog : restoreStock(items)
    Service -> Repo : updateStatus(PAYMENT_FAILED) + 이력
    Service -> Noti : sendKakaoAlimtalk("결제 실패 안내")
    deactivate Service
end
@enduml
```


---

## 17. [배치] D+11 자동구매확정 — 배송완료 후 11일 경과

- **트리거**: 스케줄러 (매일 02:00)
- **세부UC 참조**: [구매확정] UC-ORD-006 자동구매확정
- **상태전이**: Order `DELIVERED` → `CONFIRMED` (Payment 상태는 변경 없음 — 정산은 Settlement 도메인이 `ORDER_CONFIRMED` 이벤트를 구독해 비동기 처리)
- **대상 조건**: 배송완료 후 11일이 지난 주문. **반품·교환 클레임이 진행 중인 건은 제외**한다(정책 5.6.2, AC-ORD-110) — 클레임이 반려·취소로 종료되면 다음 배치에서 대상이 된다.
- **실패 재처리**(정책 5.6.3, AC-ORD-111, 미구현): 처리 실패 건은 다음 실행에서 다시 시도하고, 같은 건이 3회 연속 실패하면 운영자 알림을 발송한다.

```plantuml
@startuml
title [배치] D+11 자동구매확정

participant "Scheduler\n(AutoConfirmBatch)" as Batch
participant "OrderService" as Service
participant "OrderRepository" as Repo
participant "EventPublisher" as Event
participant "NotificationPublicApi" as Noti

Batch -> Service : autoConfirmDelivered()
activate Service

Service -> Repo : findDeliveredBefore(now - 11days)\n+ 진행 중 반품·교환 클레임 없는 건만\n(NOT EXISTS 클레임 status NOT IN 종료상태)\n+ 이전 실패 건(재처리 대상) 포함
Repo --> Service : List<Order>

loop 각 주문
    alt 처리 성공
        Service -> Repo : updateStatus(CONFIRMED)
        Service -> Event : publish(ORDER_CONFIRMED)
        note right: → Settlement(정산 확정)\n→ Member(포인트 적립)
        Service -> Noti : sendKakaoAlimtalk("자동구매확정 안내")
    else 처리 실패 (예외)
        Service -> Repo : recordFailure(orderId, failCount+1) — 다음 배치에서 재처리
        opt failCount >= 3 (3회 연속 실패)
            Service -> Noti : sendAdminAlert("자동 구매확정 3회 연속 실패", orderId)
        end
    end
end

deactivate Service
@enduml
```


---

## 18. [배치] 배송비결제 24시간 만료 — 미결제 클레임 자동취소

- **트리거**: 스케줄러 (매 시간 정각)
- **세부UC 참조**: [클레임접수] UC-ORD-012 배송비 결제기한 만료
- **상태전이**: Claim `PAYMENT_PENDING` → `PAYMENT_EXPIRED` (수거 배송비), Claim `RETURN_PAYMENT_PENDING` → `PAYMENT_EXPIRED` (반송 배송비 24시간 미결제, DH, AC-ORD-113). 배송비 결제 12시간 경과 리마인드는 §23

```plantuml
@startuml
title [배치] 배송비결제 24시간 만료

participant "Scheduler\n(ShippingPaymentExpiryBatch)" as Batch
participant "ClaimService" as Service
participant "ClaimRepository" as Repo
participant "ClaimPaymentRepository" as PayRepo
participant "EventPublisher" as Event
participant "NotificationPublicApi" as Noti

Batch -> Service : expireUnpaidShippingFees()
activate Service

Service -> PayRepo : findPendingExpiredBefore(now)
PayRepo --> Service : List<ClaimPayment>(status=PENDING, expired_at < now)

loop 각 미결제 건
    Service -> Repo : updateClaimStatus(PAYMENT_EXPIRED)
    Service -> PayRepo : updatePaymentStatus(EXPIRED)
    Service -> Event : publish(CLAIM_PAYMENT_EXPIRED)
    Service -> Noti : sendKakaoAlimtalk("배송비 미결제로 클레임 취소")
end

deactivate Service
@enduml
```


---

## 18-1. [배치] RECEIVED 24시간 CS 미처리 리마인드

> 신규 (2026-08-21 바텀업 재검증): REQ-ORD-068 대응. 지금까지는 화면 대시보드 집계 표시만 있고 실제 발송 배치가 없었다.

- **트리거**: 스케줄러 (매 시간 정각)
- **세부UC 참조**: [클레임접수] CS 접수확인 SLA
- **상태전이**: 없음 (알림만 발송, claim.status는 RECEIVED 유지)

```plantuml
@startuml
title [배치] RECEIVED 24시간 CS 미처리 리마인드

participant "Scheduler\n(ClaimReceivedSlaBatch)" as Batch
participant "ClaimService" as Service
participant "ClaimRepository" as Repo
participant "NotificationPublicApi" as Noti

Batch -> Service : remindUnprocessedReceived()
activate Service

Service -> Repo : findByStatusAndCreatedBefore(RECEIVED, now - 24h)
Repo --> Service : List<Claim>

loop 각 미처리 클레임 (last_reminded_at이 24h 이상 지났거나 NULL인 건만)
    Service -> Noti : sendAdminAlert("접수 24시간 경과 미처리 클레임", claimId)
    Service -> Repo : updateLastRemindedAt(now)
    note right of Noti: CS 대시보드 "미처리임박" 집계(DN-화면레이아웃)의 실제 발송 트리거
end

deactivate Service
@enduml
```


---

## 19. [배치] 배송상태 갱신 — 택배사 API 조회 (60분 주기)

- **트리거**: 스케줄러 (매 60분)
- **세부UC 참조**: [배송관리] UC-ORD-008 배송상태 동기화
- **상태전이**: `ord_shipment.status` `IN_TRANSIT` → `DELIVERED`/`FAILED` (v6, 배송 실행 전용·order/claim 공용). 파생 전환: Order `PREPARING` → `DELIVERED`(shipment type=OUTBOUND 구독), Claim `RETURN_PAYMENT_PENDING` → `COMPLETED`(shipment type=RETURN 구독), Claim `PICKED_UP` → `COMPLETED`(교환, shipment type=EXCHANGE_OUT 구독). **수거(PICKUP) 입고 확인과 INSPECTING 전환은 이 배치가 아니라 판매자 [입고 확인](§26, API-038)이 수행한다**

```plantuml
@startuml
title [배치] 배송상태 갱신 (60분 주기, v6 — ord_shipment 전용)

participant "Scheduler\n(ShipmentStatusSyncBatch)" as Batch
participant "ShipmentService" as Service
participant "ShipmentRepository" as Repo
participant "CourierApi\n(택배사 외부API)" as Courier
participant "ClaimRepository" as ClaimRepo
participant "OrderRepository" as OrderRepo
participant "EventPublisher" as Event
participant "NotificationPublicApi" as Noti

Batch -> Service : syncShipmentStatus()
activate Service

Service -> Repo : findByStatus(IN_TRANSIT)
Repo --> Service : List<Shipment>(shipment_type IN [OUTBOUND, RETURN, EXCHANGE_OUT] — PICKUP은 판매자 [입고 확인](§26)이 처리하므로 배치 대상 아님)

loop 각 배송건
    Service -> Courier : getTrackingStatus(trackingNo)
    Courier --> Service : TrackingResult

    alt 배송완료
        Service -> Repo : updateStatus(DELIVERED)
        Repo -> Repo : (DB) UPDATE ord_shipment

        alt shipment_type == OUTBOUND
            Service -> Event : publish(SHIPMENT_DELIVERED, refType=ORDER, refId=orderId)
            note right of Event: order.status는 이 배치가 직접 갱신하지 않는다.\nOrderService가 이벤트를 구독해 파생 전환(아래 == 섹션 참조) — 2단계 분리
            Service -> Noti : sendKakaoAlimtalk("배송완료 안내")
        else shipment_type == PICKUP (조회 대상 아님 — 방어적 분기)
            note right of Service: 배치는 입고 확인을 하지 않는다(2026-11-03 확정) — 수거 shipment(PICKUP)의\nDELIVERED 전환과 claim INSPECTING 전환은 판매자 [입고 확인](§26)이 수행.\n택배사 배송완료 신호만으로 claim.status를 변경하지 않는다
        else shipment_type == RETURN
            note right of Service: claim.status는 변경하지 않음(RETURN_PAYMENT_PENDING 유지)\nCOMPLETED 자동전환은 아래 "클레임 자동완료" 섹션에서 별도 처리
            Service -> Noti : sendKakaoAlimtalk("반송 배송완료 안내")
        else shipment_type == EXCHANGE_OUT
            note right of Service: 교환상품 고객 수령 — 클레임이 PICKED_UP(합격)이면\n아래 "교환 클레임 종료" 섹션에서 COMPLETED 전환(맞교환 원칙 — §12/§14 참조)
            Service -> Noti : sendKakaoAlimtalk("교환상품 배송완료 안내")
        end
    else 배송실패/반송 신호
        Service -> Repo : updateStatus(FAILED)
        Repo -> Repo : (DB) UPDATE ord_shipment
        Service -> Noti : sendKakaoAlimtalk("배송 실패 안내, CS 확인 요청")
    else 상태변경 없음
        note right: skip
    end
end

== 주문 배송완료 파생 전환 (OrderService, SHIPMENT_DELIVERED 이벤트 구독) ==

Event -> OrderRepo : updateStatus(DELIVERED)\n(shipment type=OUTBOUND 구독분만, orderId 기준)
OrderRepo -> OrderRepo : (DB) UPDATE ord_order
note right of OrderRepo: D+11 자동확정 타이머 시작(§17), 고객 알림톡

== 클레임 자동완료 (RETURN_PAYMENT_PENDING → COMPLETED, shipment(RETURN) DELIVERED 기준 배치 자동전환) ==

Service -> ClaimRepo : findByStatusWithReturnShipmentDelivered(RETURN_PAYMENT_PENDING)
ClaimRepo --> Service : List<Claim>(연관 shipment(RETURN).status = DELIVERED)

loop 각 클레임 (CLAIM_REFUNDED류 알림톡 발행 패턴 참고)
    Service -> ClaimRepo : updateStatus(COMPLETED)
    Service -> Event : publish(CLAIM_COMPLETED)
    Service -> Noti : sendKakaoAlimtalk("클레임 완료 안내")
end

== 교환 클레임 종료 (PICKED_UP → COMPLETED, shipment(EXCHANGE_OUT) DELIVERED 기준) ==

Service -> ClaimRepo : findByStatusWithExchangeOutDelivered(PICKED_UP)
ClaimRepo --> Service : List<Claim>(claimType=EXCHANGE, 연관 shipment(EXCHANGE_OUT).status = DELIVERED)
note right of Service: 합격(PICKED_UP) 전에 배송완료된 건은 합격 판정 시점에 이미 충족 — 다음 주기에 전환.\n환불 없음(교환은 환불 대상 아님)

loop 각 교환 클레임
    Service -> ClaimRepo : updateStatus(COMPLETED)
    Service -> Event : publish(CLAIM_COMPLETED)
    note right of Event: 발행 시점 = COMPLETED 전환 시 (정산·알림·포인트 이벤트, Payment 환불 없음)
    Service -> Noti : sendKakaoAlimtalk("교환 완료 안내")
end

deactivate Service
@enduml
```


---

## 20. [API] POST /api/admin/v1/claims/{claimId}/dispose — 폐기 처리

- **트리거**: 어드민 수동 처리 (품질점검 불합격 건 중 반송 불가 판단)
- **상태전이**: Claim `PICKUP_REJECTED` → `DISPOSED`

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title POST /api/admin/v1/claims/{claimId}/dispose — 폐기 처리

actor "CS 담당자" as Admin
participant "AdminClaimController" as ACC
participant "ClaimService" as CS
participant "ClaimRepository" as CR
participant "EventPublisher" as EP
database "DB (ord_claim)" as DB

Admin -> ACC : POST /api/admin/v1/claims/{claimId}/dispose\n{reason}
activate ACC

ACC -> CS : disposeClaim(adminId, claimId, reason)
activate CS

CS -> CR : findById(claimId)
CR -> DB : SELECT
DB --> CR : claim
CR --> CS : claim

alt 상태 != PICKUP_REJECTED
  CS --> ACC : INVALID_STATUS (품질점검 거부 건만 폐기 가능)
  ACC --> Admin : 409 에러
else 정상
  CS -> CR : updateStatus(DISPOSED, reason)
  CR -> DB : UPDATE ord_claim

  CS -> EP : publish(CLAIM_DISPOSED)
  note right of EP: Notification* → 고객 알림톡\n("상품 폐기 처리됨")\nDISPOSED→COMPLETED 자동전환은 §10 배치 참조

  CS --> ACC : ClaimResponse(status=DISPOSED)
  deactivate CS
  ACC --> Admin : 200 SUCCESS
  deactivate ACC
end

@enduml
```


---

## 21. [API] POST /api/admin/v1/claims/{claimId}/request-return-payment — 반송 배송비 추가결제 요청

- **트리거**: 어드민 수동 처리 (품질점검 불합격 건 중 반송 가능 판단)
- **상태전이**: Claim `PICKUP_REJECTED` → `RETURN_PAYMENT_PENDING`
- **금액**: 반송 배송비는 품질점검 전체 불합격 시 편도 3,000원 고정(정책 6.9.7)이며, 환불에서 차감하지 않고 고객이 별도 결제한다. 필드명은 DL §35 `returnShippingFee`를 따른다.

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title POST /api/admin/v1/claims/{claimId}/request-return-payment — 반송 배송비 추가결제 요청

actor "CS 담당자" as Admin
participant "AdminClaimController" as ACC
participant "ClaimService" as CS
participant "ClaimRepository" as CR
participant "EventPublisher" as EP
database "DB (ord_claim)" as DB

Admin -> ACC : POST /api/admin/v1/claims/{claimId}/request-return-payment\n{returnShippingFee=3000 (생략 시 기본값, 다른 값은 거부)}
activate ACC

ACC -> CS : requestReturnPayment(adminId, claimId, returnShippingFee)
activate CS

CS -> CR : findById(claimId)
CR -> DB : SELECT
DB --> CR : claim
CR --> CS : claim

alt 상태 != PICKUP_REJECTED
  CS --> ACC : INVALID_STATUS (품질점검 거부 건만 반송 요청 가능)
  ACC --> Admin : 409 에러
else 정상
  CS -> CR : updateStatus(RETURN_PAYMENT_PENDING, returnShippingFee)
  CR -> DB : UPDATE ord_claim

  CS -> EP : publish(CLAIM_RETURN_PAYMENT_REQUESTED)
  note right of EP: Notification* → 고객 알림톡\n("반송 배송비 결제 필요")\n고객 결제는 §12(paymentType=RETURN)에서 처리\n24시간 미결제 시 §18 배치가 PAYMENT_EXPIRED로 자동취소

  CS --> ACC : ClaimResponse(status=RETURN_PAYMENT_PENDING)
  deactivate CS
  ACC --> Admin : 200 SUCCESS
  deactivate ACC
end

@enduml
```


---

## 22. [API] POST /api/partner/v1/shipping/{shipmentId}/reship — 배송 실패 재발송 처리 (신규)

> v6 후속 보완 (2026-08-21): REQ-ORD-062 대응. FAILED 상태의 shipment(어떤 shipment_type이든 공통)를 재발송 처리한다.

- **트리거**: 판매자 또는 CS 담당자 수동 처리 (§19 배치가 FAILED로 전환한 건)
- **상태전이**: `ord_shipment.status` `FAILED` → `PENDING` → (운송장 재등록 시) `IN_TRANSIT`

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title POST /api/partner/v1/shipping/{shipmentId}/reship — 배송 실패 재발송 처리

actor "판매자 / CS 담당자" as Actor
participant "PartnerShippingController" as SC
participant "ShipmentService" as Service
participant "ShipmentRepository" as Repo
database "DB (ord_shipment)" as DB

Actor -> SC : POST /api/partner/v1/shipping/{shipmentId}/reship\n{carrier, trackingNo}
activate SC

SC -> Service : reship(shipmentId, carrier, trackingNo)
activate Service

Service -> Repo : findById(shipmentId)
Repo --> Service : Shipment

alt 상태 != FAILED
  Service --> SC : RESHIP_NOT_ALLOWED (FAILED 상태만 재발송 가능)
  SC --> Actor : 409 에러
else 정상
  Service -> Repo : updateStatus(PENDING)
  Repo -> DB : UPDATE ord_shipment
  Service -> Repo : registerTracking(carrier, trackingNo)
  Repo -> DB : UPDATE ord_shipment (carrier, trackingNo)
  Service -> Repo : updateStatus(IN_TRANSIT)
  Repo -> DB : UPDATE ord_shipment
  note right: 이후 §19 배치가 다시 추적(60분 주기)

  Service --> SC : ShipmentResponse(status=IN_TRANSIT)
  deactivate Service
  SC --> Actor : 200 SUCCESS
  deactivate SC
end

@enduml
```


---

## 23. [배치] 클레임 배송비 결제 12시간 리마인드 (BAT-004)

> 신규 (2026-10-29): DQ-프로그램목록 BAT-004(UC-26 추가예정, 시퀀스 §23 추가 예정)의 시퀀스를 기존 계획 항목대로 추가한다. 프로그램 신설이 아니다. REQ-ORD-043, AC-ORD-045.

- **트리거**: 스케줄러 (매 시간 정각)
- **상태전이**: 없음 (알림만 발송). 24시간 만료는 §18
- **대상**: Claim `PAYMENT_PENDING`(수거 배송비) 또는 `RETURN_PAYMENT_PENDING`(반송 배송비) 상태로 결제 요청 후 12시간이 지났으나 아직 리마인드하지 않은 건

```plantuml
@startuml
title [배치] 클레임 배송비 결제 12시간 리마인드
participant "Scheduler\n(ShippingPaymentReminderBatch)" as Batch
participant "ClaimService" as Service
participant "ClaimPaymentRepository" as PayRepo
participant "NotificationApi" as Noti

Batch -> Service : remindUnpaidShippingFees()
activate Service
Service -> PayRepo : findPendingRequestedBefore(now - 12h, reminded=false)
PayRepo --> Service : List<ClaimPayment>(status=PENDING)
loop 각 미결제 건
    Service -> Noti : sendKakaoAlimtalk("배송비 미결제 리마인드(남은 시간 안내)")
    Service -> PayRepo : markReminded(claimPaymentId)
end
deactivate Service
@enduml
```


---

## 24. [배치] 입금기한 12시간 만료 + 재고 복원 (BAT-006)

> 신규 (2026-10-29): DQ-프로그램목록 BAT-006(계획, 입금기한 만료+재고 복원)의 시퀀스. 프로그램 신설이 아니라 기존 계획 항목의 시퀀스다. REQ-ORD-014, AC-ORD-016. **미구현**(Bolt14 SC28-3).

- **트리거**: 스케줄러 (주기 예: 매 시간, DQ BAT-006)
- **상태전이**: Order `DEPOSIT_PENDING` → `CANCELLED`(사유 입금기한 만료). 취소 클레임은 생성하지 않는다(REQ-ORD-082는 고객 직접 취소·어드민 예외 취소 한정)
- **경합**: 만료 처리와 입금 통보가 겹치면 취소 확정 후 도착한 입금 통보는 §5-1과 같이 자동 환불(LATE_DEPOSIT)한다. 주문 행 잠금으로 직렬화한다

```plantuml
@startuml
title [배치] 입금기한 12시간 만료 + 재고 복원
participant "Scheduler\n(DepositExpiryBatch)" as Batch
participant "내부 API\n(OrderInternalController)" as IC
participant "OrderService" as Service
participant "OrderRepository" as Repo
participant "PaymentApi" as PAY
participant "CatalogApi" as CAT

Batch -> IC : 입금기한 만료 처리 요청
IC -> Service : expireDepositPending(now)
activate Service
Service -> Repo : findByStatusAndDepositDueBefore(DEPOSIT_PENDING, now)
Repo --> Service : List<PlatformOrder> (입금기한 12시간 경과)
loop 각 주문 (행 잠금, 상태 재확인)
    alt 아직 DEPOSIT_PENDING
        Service -> PAY : discardVirtualAccount(platformOrderNo) (안)
        Service -> CAT : restoreStock(items)
        Service -> Repo : updateStatus(CANCELLED, reason=입금기한 만료) + 이력
    else 그사이 입금 통보로 PAYMENT_COMPLETED
        note right of Service : 건너뜀
    end
end
deactivate Service
@enduml
```


---

## 25. [배치] 임시주문(TEMP) 30분 TTL 정리 (BAT-005)

> 신규 (2026-10-29): DQ-프로그램목록 BAT-005(계획)의 시퀀스. 프로그램 신설이 아니다. DH `TEMP → CANCELLED`(30분 TTL 만료). **미구현**(Bolt14 SC28-4) — 현행은 이탈한 주문서가 TEMP로 누적된다.

- **트리거**: 스케줄러 (주기 예: 10분, DQ BAT-005)
- **상태전이**: Order(플랫폼주문·판매자 주문·상품) `TEMP` → `CANCELLED`. 재고는 접수 전이라 차감되지 않았으므로 복원하지 않는다

```plantuml
@startuml
title [배치] 임시주문(TEMP) TTL 정리
participant "Scheduler\n(TempOrderCleanupBatch)" as Batch
participant "내부 API\n(OrderInternalController)" as IC
participant "OrderService" as Service
participant "PlatformOrderRepository" as Repo

Batch -> IC : 임시주문 정리 요청
IC -> Service : cleanupExpiredTemp(now)
activate Service
Service -> Repo : findByStatusAndCreatedBefore(TEMP, now - 30min)
Repo --> Service : List<PlatformOrder>
loop 각 임시주문
    Service -> Repo : updateStatus(CANCELLED, reason=주문서 이탈(TTL 만료)) + 이력
end
deactivate Service
@enduml
```


---

## 26. [API] POST /api/partner/v1/claims/{claimId}/pickup-confirm — 입고 확인

> 신규 (2026-11-03): DQ API-038(DL §27, DK §21)의 시퀀스. 입고 확인 주체는 **판매자 [입고 확인] 액션**이며 배송추적 배치(§19)는 입고 확인을 하지 않는다. **미구현**(DL §27).

- **트리거**: 판매자 [입고 확인 → 품질점검 시작] 클릭
- **상태전이**: shipment(PICKUP) `IN_TRANSIT` → `DELIVERED`, Claim `PAYMENT_PENDING`(고객귀책, 배송비 결제 완료) 또는 `RECEIVED`(판매자귀책) → `INSPECTING` — 같은 트랜잭션

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title POST /api/partner/v1/claims/{claimId}/pickup-confirm — 입고 확인

actor 판매자 as Partner
participant "PartnerClaimController" as PCC
participant "ClaimService" as CS
participant "ClaimRepository" as CR
participant "ShipmentRepository" as SR
participant "NotificationPublicApi" as Noti
database "DB (ord_claim, ord_shipment)" as DB

Partner -> PCC : POST /api/partner/v1/claims/{claimId}/pickup-confirm
activate PCC

PCC -> CS : confirmPickup(vendorId, claimId)
activate CS

CS -> CR : findById(claimId)
CR -> DB : SELECT
DB --> CR : claim
CR --> CS : claim

alt 본인 판매자 클레임 아님
  CS --> PCC : FORBIDDEN
  PCC --> Partner : 403 에러
else 수거 shipment(PICKUP)가 IN_TRANSIT 아님 또는 클레임 상태 부적합
  CS --> PCC : INVALID_STATUS
  PCC --> Partner : 409 에러
else 정상
  CS -> SR : updateStatus(PICKUP shipment, DELIVERED)
  SR -> DB : UPDATE ord_shipment
  CS -> CR : updateStatus(INSPECTING)
  CR -> DB : UPDATE ord_claim + INSERT ord_status_history
  DB --> CR : OK

  CS -> Noti : sendKakaoAlimtalk("수거완료, 품질점검 진행 안내")

  CS --> PCC : PickupConfirmResult(claimId, pickupConfirmedAt)
  deactivate CS
  PCC --> Partner : 200 SUCCESS
  deactivate PCC
end

@enduml
```
