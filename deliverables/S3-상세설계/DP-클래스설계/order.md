# 클래스 설계 — Order 도메인

> 상위 문서: [readme.md](readme.md)
> **단계**: 상세설계 (S3) | **문서범위**: Bolt (Order) | **문서종류**: Design
> 도메인 간 공용 계약(PublicApi)은 [common.md](common.md) 참조

---

## 1. Order 도메인 — 패키지 구조

```
com.runnshop.order/
├── cart/
│   ├── controller/
│   │   └── CartController.kt
│   ├── service/
│   │   └── CartService.kt
│   ├── repository/
│   │   └── CartRepository.kt
│   ├── domain/
│   │   └── CartItem.kt
│   └── dto/
│       ├── AddToCartRequest.kt
│       ├── UpdateQuantityRequest.kt
│       └── CartResponse.kt
├── order/
│   ├── controller/
│   │   └── OrderController.kt        (v3: 앱별 Controller 통합 — getMyOrders/getAdminOrders/getPartnerOrders/createOrderSheet 등 메서드로 구분, DM-시퀀스/readme.md §1 v3 참조)
│   ├── service/
│   │   ├── OrderService.kt
│   │   └── OrderSheetService.kt
│   ├── repository/
│   │   ├── PlatformOrderRepository.kt
│   │   ├── OrderRepository.kt
│   │   └── OrderHistoryRepository.kt
│   ├── domain/
│   │   ├── PlatformOrder.kt
│   │   ├── Order.kt
│   │   ├── OrderItem.kt
│   │   └── OrderHistory.kt
│   └── dto/
│       ├── OrderSheetRequest.kt
│       ├── OrderSheetResponse.kt
│       ├── PayRequest.kt
│       ├── CancelRequest.kt
│       └── OrderListResponse.kt
├── shipping/
│   ├── controller/
│   │   └── ShippingController.kt
│   ├── service/
│   │   └── ShipmentService.kt
│   ├── repository/
│   │   └── ShipmentRepository.kt
│   ├── domain/
│   │   └── Shipment.kt              (ORDER/CLAIM 공용 — ord_shipment)
│   └── dto/
│       ├── RegisterTrackingRequest.kt
│       ├── ReshipRequest.kt         (v6 후속 — REQ-ORD-062)
│       └── ShipmentResponse.kt
├── claim/
│   ├── controller/
│   │   └── ClaimController.kt        (v3: 앱별 Controller 통합 — getMyClaims/getAdminClaims/getPartnerClaims 등 메서드로 구분, DM-시퀀스/readme.md §1 v3 참조)
│   ├── service/
│   │   └── ClaimService.kt
│   ├── repository/
│   │   └── ClaimRepository.kt
│   ├── domain/
│   │   └── Claim.kt
│   └── dto/
│       ├── CreateClaimRequest.kt
│       ├── ClaimProcessRequest.kt
│       └── ClaimResponse.kt
├── publicapi/
│   ├── CatalogPublicApi.kt          (interface)
│   ├── PaymentPublicApi.kt          (interface)
│   ├── MemberPublicApi.kt           (interface)
│   └── PromotionPublicApi.kt        (interface)
└── event/
    ├── OrderEventPublisher.kt
    └── OrderEventListener.kt
```

> **신규 (2026-10 프로토타입 구현 반영)**: 실제 코드는 위 `cart/order/shipping/claim` 하위 서브패키지 분리를 아직 적용하지 않고, `com.runnshop.order` 바로 아래에 `controller/service/domain/dto/repository/publicapi` + **`mapper/`(신규, 위 트리에 없음 — admin 목록 MyBatis 전용)**를 평탄하게 둔다(DM-시퀀스/readme.md가 2026-10에 확정한 "Order는 단일 OrderController로 통합" 결정과 같은 축의 단순화). 실제 파일: `controller/{OrderController,ClaimController,CustomerCartController}.kt`, `service/{OrderService,OrderAddressMock}.kt`, `domain/{Order,OrderItem,PlatformOrder,PlatformOrderDiscount,Delivery,Claim}.kt`, `repository/{OrderRepository,PlatformOrderRepository}.kt`, `mapper/OrderMapper.kt`, `publicapi/{PaymentPublicApi,MemberPublicApi,PromotionPublicApi}.kt`. `OrderSheetService`/`OrderHistoryRepository`/`CartItem`/`CartRepository`/`Shipment`/`ShipmentRepository`/`OrderEventPublisher`/`OrderEventListener`는 아직 코드가 없다(미착수, 위 트리는 미래 설계 그대로 유지).

---
## 3. Order 도메인 — 클래스 상세

> **경로·인증·시간 타입 기준 (2026-10-29 현행화)**: 이 절의 코드는 **설계안**이며 인터페이스 명세(DL)와 다음처럼 다르다. 구현은 DL을 기준으로 한다. ① **경로**: Order 컨트롤러는 DL의 `/api/mobile/v1/my/...`(고객), `/api/admin/v1/...`, `/api/partner/v1/...`를 쓴다(원안 `/api/v1/...` 폐기 — 아래 코드의 `@RequestMapping`은 DL 기준으로 정정했다). ② **인증**: 원안의 `X-Member-Id`·`X-Vendor-Id` 헤더 파라미터는 폐기됐다 — DL은 `Bearer {memberId}`(고객)·Partner/Admin Bearer 인증이며 memberId·vendorId는 인증 컨텍스트에서 주입한다(현행 프로토타입은 고정값 placeholder, 실 인증 연동 전). 아래 시그니처의 `@RequestHeader("X-...")`는 "인증 컨텍스트에서 주입되는 값"으로 읽는다. ③ **시간 타입**: 시간은 `LocalDateTime`으로 통일한다(원안 `Instant`는 폐기 — 아래 코드는 정정했다). 구현 현황과의 차이는 각 클래스의 "프로토타입 구현 반영" 블록을 따른다.

### CartController

```kotlin
@RestController
@RequestMapping("/api/mobile/v1/my/cart")
class CartController(private val cartService: CartService) {

    @PostMapping("/items")
    fun addToCart(
        @RequestHeader("X-Member-Id") memberId: String,
        @RequestBody request: AddToCartRequest
    ): ApiResponse<CartItemResponse>

    @GetMapping
    fun getCart(
        @RequestHeader("X-Member-Id") memberId: String
    ): ApiResponse<CartResponse>

    @PatchMapping("/items/{cartItemId}/quantity")
    fun updateQuantity(
        @PathVariable cartItemId: String,
        @RequestBody request: UpdateQuantityRequest
    ): ApiResponse<CartItemResponse>

    @DeleteMapping("/items/{cartItemId}")
    fun removeItem(
        @PathVariable cartItemId: String
    ): ApiResponse<Unit>
}
```

### CartService

```kotlin
@Service
@Transactional
class CartService(
    private val cartRepository: CartRepository,
    private val catalogPublicApi: CatalogPublicApi
) {
    fun addToCart(memberId: String, request: AddToCartRequest): CartItemResponse
    fun getCart(memberId: String): CartResponse
    fun updateQuantity(cartItemId: String, quantity: Int): CartItemResponse
    fun removeItem(cartItemId: String)
    fun mergeCarts(guestId: String, memberId: String)
}
```

### OrderController

```kotlin
@RestController
@RequestMapping("/api/mobile/v1/my/orders")
class OrderController(
    private val orderSheetService: OrderSheetService,
    private val orderService: OrderService
) {
    @PostMapping("/sheet")
    fun createSheet(
        @RequestHeader("X-Member-Id") memberId: String,
        @RequestBody request: OrderSheetRequest
    ): ApiResponse<OrderSheetResponse>

    @PostMapping("/{orderSheetId}/pay")
    fun placeOrder(
        @RequestHeader("X-Member-Id") memberId: String,
        @PathVariable orderSheetId: String,
        @RequestBody request: PayRequest
    ): ApiResponse<PayResponse>

    @PostMapping("/{orderId}/cancel")
    fun cancelOrder(
        @RequestHeader("X-Member-Id") memberId: String,
        @PathVariable orderId: String,
        @RequestBody request: CancelRequest
    ): ApiResponse<CancelResponse>

    @PostMapping("/{orderId}/confirm")
    fun confirmOrder(
        @RequestHeader("X-Member-Id") memberId: String,
        @PathVariable orderId: String
    ): ApiResponse<ConfirmResponse>

    @PutMapping("/{orderId}/shipping-address")
    fun changeShippingAddress(
        @PathVariable orderId: String,
        @RequestBody request: ChangeAddressRequest
    ): ApiResponse<Unit>

    @GetMapping
    fun getMyOrders(
        @RequestHeader("X-Member-Id") memberId: String,
        @RequestParam page: Int,
        @RequestParam size: Int,
        @RequestParam status: String?
    ): ApiResponse<OrderListResponse>
}
```

> **(2026-10 프로토타입 구현 반영)**: 실제 `OrderController`는 클래스 레벨 `@RequestMapping` 없이(DP 원안과 다름) 메서드별 전체 경로를 쓰고, `// ── 회원(mobile) ──`/`// ── 관리자(admin) ──`/`// ── 파트너(partner) ──` 3개 채널 섹션(kotlin-guide.md 규칙)으로 구성된다. 실제 메서드 8개: `createOrderSheet()`, `placeOrder(orderSheetId, request)`(DP엔 없던 메서드, 2026-10-19 신규), `getMyOrders()`, `getMyOrderDetail(orderId)`, `getAdminOrders(filter...)`, `getAdminOrderDetail(orderId)`, `getPartnerOrders(filter...)`, `getPartnerOrderDetail(orderId)`. DP 원안의 `cancelOrder`/`confirmOrder`/`changeShippingAddress`는 아직 미구현. `placeOrder()`의 `memberId`는 `@RequestHeader`가 아니라 `val memberId = 1L`(실 인증 연동 전 placeholder, 코드 내 고정값)이다.

### OrderService

```kotlin
@Service
@Transactional
class OrderService(
    private val platformOrderRepository: PlatformOrderRepository,
    private val orderRepository: OrderRepository,
    private val orderHistoryRepository: OrderHistoryRepository,
    private val catalogPublicApi: CatalogPublicApi,
    private val paymentPublicApi: PaymentPublicApi,
    private val eventPublisher: OrderEventPublisher
) {
    fun placeOrder(memberId: String, sheetId: String, request: PayRequest): PayResponse
    fun cancelOrder(memberId: String, orderId: String, reason: String): CancelResponse
    // canCancel()=DEPOSIT_PENDING/PAYMENT_COMPLETED만 허용. DEPOSIT_PENDING: 가상계좌 폐기 + 재고 복원, 환불 없음(refundAmount=0).
    // 같은 트랜잭션에서 claim_type=CANCEL 클레임 생성(channel=SELF, REQ-ORD-082 — 입금대기 RECEIVED→COMPLETED / 결제완료 RECEIVED→REFUNDED→COMPLETED).
    // 입금 통보와 경합하면 취소 우선(DM §5-1). 미구현
    fun forceCancel(adminId: String, orderId: String, reason: String): CancelResponse
    // PREPARING + 출고 shipment(OUTBOUND) PENDING(송장 미등록)만 허용, 그 외 409 CANCEL_NOT_ALLOWED. 취소 클레임 생성(channel=CS, REQ-ORD-082)
    fun confirmOrder(memberId: String, orderId: String): ConfirmResponse
    fun autoConfirmBatch(): Int  // D+11 자동구매확정 배치 — 진행 중 반품·교환 클레임 건 제외(정책 5.6.2), 실패 재처리·3회 연속 실패 운영자 알림(5.6.3). DM §17
    fun changeShippingAddress(orderId: String, request: ChangeAddressRequest)
    fun getMyOrders(memberId: String, page: Int, size: Int, status: String?): OrderListResponse
    fun getAdminOrders(filter: AdminOrderFilter): OrderListResponse
    fun getPartnerOrders(vendorId: String, filter: PartnerOrderFilter): OrderListResponse
}
```

> **(2026-10-27 정책 확인 회신 반영 — `getAdminOrders`)**: ① 조회 테이블은 `ord_platform_order`, 날짜 필터·정렬·표시는 `ordered_at`. ② 키워드는 주문번호·상품명(EXISTS `ord_order_item`)·주문자명(`orderer_name`) ILIKE 부분 일치. ③ 입력 검증 `INVALID_PAGE`/`INVALID_SIZE`(1~100)/`INVALID_DATE_RANGE`는 `BadRequestException`. ④ summary는 `status` 제외 조건만 GROUP BY(`TEMP` 제외, `all`+3개 상태 키, 0건 유지). ⑤ 고객명은 `orderer_name` 스냅샷(마스킹) — 컬럼 추가·주문 접수 시 적재는 **미구현(후속)**.

> **(2026-10 프로토타입 구현 반영)**: 실제 생성자 의존성 7개 — `mockLoader, orderMapper, orderRepository, paymentPublicApi, platformOrderRepository, promotionPublicApi, memberPublicApi`. DP 원안의 `orderHistoryRepository`/`catalogPublicApi`/`eventPublisher`는 주입되지 않는다(재고차감·이벤트발행 미구현). 실제 메서드: `getAdminOrders`, `getPartnerOrders`, `getMyOrders`, `createOrderSheet`, `placeOrder(memberId: Long, sheetId: String, request: PayRequest): PayResponse`(**타입만 String→Long, 인자 개수는 DP 원안과 동일**), `getAdminOrderDetail`, `getPartnerOrderDetail`, `getMyOrderDetail`. DP 원안의 `cancelOrder`/`forceCancel`/`confirmOrder`/`autoConfirmBatch`/`changeShippingAddress`는 미구현.

### ShipmentService

> v6 리팩토링: 배송 실행 상태를 `order.status`/`claim.status`에서 분리하여 `ord_shipment`(Shipment)로 일원화.
> Order(OUTBOUND)와 Claim(PICKUP/RETURN/EXCHANGE_OUT) 양쪽의 배송 실행을 공통으로 처리한다.

```kotlin
@Service
@Transactional
class ShipmentService(
    private val shipmentRepository: ShipmentRepository,
    private val orderRepository: OrderRepository,
    private val orderHistoryRepository: OrderHistoryRepository
) {
    fun createShipment(refType: ShipmentRefType, refId: String, shipmentType: ShipmentType): Shipment
    // Shipment 생성 → status: PENDING
    // Order 발송: refType=ORDER, shipmentType=OUTBOUND (기존 shipOrder 대체)
    // Claim 수거/반송: refType=CLAIM, shipmentType=PICKUP/RETURN/EXCHANGE_OUT

    fun registerTracking(shipmentId: String, carrier: String, trackingNo: String): Shipment
    // PENDING → IN_TRANSIT (운송장 등록)

    fun confirmDelivered(shipmentId: String): Shipment
    // IN_TRANSIT → DELIVERED

    fun markFailed(shipmentId: String): Shipment
    // IN_TRANSIT → FAILED (배송 실패/미배달)

    fun reship(shipmentId: String, carrier: String, trackingNo: String): Shipment
    // FAILED → PENDING → IN_TRANSIT (재발송, 신규 운송장으로 즉시 재등록)

    fun getShippingList(vendorId: String, filter: ShippingFilter): ShippingListResponse
    fun getShipments(refType: ShipmentRefType, refId: String): List<ShipmentResponse>
}
```

### ShippingController

> (2026-08-21 배선 확인·보완) `ShipmentService.reship()`는 이미 존재했으나 이를 호출하는 컨트롤러 계층이 문서에 없었다. §16-22 시퀀스에 맞춰 보완.

```kotlin
@RestController
@RequestMapping("/api/partner/v1/shipping")
class ShippingController(private val shipmentService: ShipmentService) {

    @PostMapping("/{orderId}")
    fun registerTracking(
        @RequestHeader("X-Vendor-Id") vendorId: String,
        @PathVariable orderId: String,
        @RequestBody request: RegisterTrackingRequest
    ): ApiResponse<ShipmentResponse>
    // §16-9 — orderId로 shipment(refType=ORDER, shipmentType=OUTBOUND) 조회 후
    // shipmentService.registerTracking(shipmentId, request.deliveryCompany, request.trackingNo) 호출 (PENDING→IN_TRANSIT)

    @PostMapping("/{shipmentId}/reship")
    fun reship(
        @RequestHeader("X-Vendor-Id") vendorId: String,
        @PathVariable shipmentId: String,
        @RequestBody request: ReshipRequest
    ): ApiResponse<ShipmentResponse>
    // §16-22 (REQ-ORD-062) — shipmentService.reship(shipmentId, request.carrier, request.trackingNo) 호출
    // FAILED 상태만 허용, 그 외 상태는 RESHIP_NOT_ALLOWED
}
```

### ClaimService

```kotlin
@Service
@Transactional
class ClaimService(
    private val orderRepository: OrderRepository,
    private val claimRepository: ClaimRepository,
    private val shipmentService: ShipmentService,
    private val paymentPublicApi: PaymentPublicApi,
    private val eventPublisher: OrderEventPublisher
) {
    fun createClaim(memberId: String, orderId: String, request: CreateClaimRequest): ClaimResponse
    // 사유별 기한: 단순변심 배송완료 후 10일, 하자·오배송 3개월/안 날부터 30일(정책 7.2.2). 구매확정(CONFIRMED) 후는 고객 접수 거부(고객센터 안내) — 어드민 접수만 가능(REQ-ORD-081, 어드민 접수 API는 DL에 없음)

    // ── Customer (자진취소) ──
    fun cancelClaim(memberId: String, claimId: String): ClaimResponse
    // POST /api/mobile/v1/my/claims/{claimId}/cancel — 고객 클레임 자진취소 (§16-7-2, REQ-ORD-071/073)
    // claim.status가 RECEIVED/PAYMENT_PENDING이 아니면 ClaimCancelNotAllowedException 발생
    //   (귀책판정/수거 시작 이후 — INSPECTING 이상은 취소 불가)
    // 정상 시 claim.cancel() 호출 → status: REJECTED, reason="고객 자진 철회"

    // ── Admin (#23~#29) ──
    fun getAdminClaims(filter: AdminClaimFilter): ClaimListResponse                                    // #23 GET /api/admin/v1/claims
    // [폐기] fun startProcessing(adminId: String, claimId: String)  // POST .../start — CS 처리시작(IN_PROGRESS) 상태 전이는 DH v6에서 삭제됨. RECEIVED에서 귀책판정으로 곧바로 분기한다. 단 DL §19·DQ API-050 `/start`는 UI 전용(claim.status는 RECEIVED 유지)으로 남아 있다
    fun decideResponsibility(adminId: String, claimId: String, responsibility: ClaimResponsibility): ClaimResponse
    // (신규 — 인터페이스명세 미정의, 후속 추가 필요) CS 귀책판정(override). 고객 자진신고를 CS가 덮어씀 (REQ-ORD-066)
    // claim.decideResponsibility(responsibility) 호출
    //   CUSTOMER → claim.status: RECEIVED→PAYMENT_PENDING (수거배송비 결제 알림톡 발송)
    //   VENDOR   → claim.status 변경 없음(RECEIVED 유지) + shipmentService.createShipment(CLAIM, claimId, PICKUP) 생성
    //              이후 registerPickupTracking(#35)에서 운송장 등록, confirmPickup(#36)에서 INSPECTING 전환
    fun completeClaim(adminId: String, claimId: String, memo: String)                                  // #25 POST .../complete (환불 진행)
    fun rejectClaim(adminId: String, claimId: String, reason: String)                                  // #26 POST .../reject
    fun refundClaim(adminId: String, claimId: String, refundMethod: String, bankAccount: BankAccountInfo?): ClaimResponse
    // #27 POST .../refund — refundMethod: ORIGINAL(원결제수단) / BANK_TRANSFER(계좌이체, bankAccount 필수). PG 환불 실행은 Payment 도메인(RefundService)에 위임. 클레임(반품) 환불의 유일한 트리거 — CLAIM_COMPLETED 이벤트는 정산·알림·재고복원·포인트 이벤트일 뿐 Payment 환불을 일으키지 않는다(2026-11-03 확정)
    fun dispose(adminId: String, claimId: String, reason: String): ClaimResponse                       // #28 POST .../dispose — PICKUP_REJECTED 건 폐기 결정
    fun requestReturnPayment(adminId: String, claimId: String, returnShippingFee: Int): ClaimResponse   // #29 POST .../request-return-payment — 수거거부 건 반송배송비 추가결제 요청(알림톡)

    // ── Partner (#35~#40) ──
    // v6: 수거/반송 배송 실행은 Shipment(ord_shipment)로 이관. Claim.status는 더 이상 PICKUP/RETURN_SHIPPING/RETURN_DELIVERED를 갖지 않는다.
    fun registerPickupTracking(vendorId: String, claimId: String, deliveryCompany: String, trackingNo: String): ClaimResponse
    // #35 POST /api/partner/v1/shipping/{claimId}/pickup
    // shipmentService.createShipment(CLAIM, claimId, PICKUP) 후 registerTracking(shipmentId, deliveryCompany, trackingNo) → shipment: PENDING→IN_TRANSIT
    // (claim.status는 변경하지 않음 — RECEIVED/PAYMENT_PENDING 등 결제 흐름 상태 유지)
    fun confirmPickup(vendorId: String, claimId: String): ClaimResponse
    // #36 POST .../pickup-confirm — 입고 확인 (주체: 판매자 [입고 확인] 액션, API-038 — 배송추적 배치는 입고 확인을 하지 않음. 인자는 claimId로 통일, 2026-11-03 확정)
    // shipmentService.confirmDelivered(shipmentId)로 PICKUP shipment를 DELIVERED 처리한 뒤,
    // claim.startInspecting()으로 클레임 상태를 INSPECTING 전환 (shipment 배송완료와 클레임 상태전이를 분리된 메서드로 처리)
    fun inspectPass(vendorId: String, claimId: String, tagIntact: Boolean?, memo: String): ClaimResponse
    // #37 POST .../inspect-pass — 품질점검 합격 → PICKED_UP
    // tagIntact: 판정 근거(택 부착 여부). claimType=EXCHANGE 전용 기준, claimType=RETURN이면 null(사용감·파손 등은 memo로 기술)
    fun inspectReject(vendorId: String, claimId: String, tagIntact: Boolean?, rejectReason: String): ClaimResponse
    // #38 POST .../inspect-reject — 품질점검 거부 → PICKUP_REJECTED (rejectReason 필수)
    // tagIntact: inspectPass와 동일한 EXCHANGE 전용/RETURN=null 규칙
    fun returnShip(vendorId: String, claimId: String, deliveryCompany: String, trackingNo: String): ClaimResponse
    // #39 POST .../return-ship — 반송 운송장 등록 (반송배송비 결제 완료 건 대상)
    // shipmentService.createShipment(CLAIM, claimId, RETURN) 후 registerTracking(shipmentId, deliveryCompany, trackingNo) → shipment: PENDING→IN_TRANSIT
    // (claim.status는 RETURN_PAYMENT_PENDING에서 변경하지 않음 — 반송 배송 진행상태는 Shipment.status로 추적)
    fun getPartnerClaims(vendorId: String, claimType: String, filter: PartnerClaimFilter): ClaimListResponse  // #40 GET /api/partner/v1/claims
}
```

### OrderEventPublisher

```kotlin
@Component
class OrderEventPublisher(private val outboxRepository: OutboxRepository) {
    fun publishOrderCancelled(order: Order)
    fun publishOrderConfirmed(order: Order)
    fun publishClaimCompleted(claim: Claim)
}
```

### OrderEventListener

```kotlin
@Component
class OrderEventListener(private val orderService: OrderService) {
    @EventListener
    fun onPaymentApproved(event: PaymentApprovedEvent)
    @EventListener
    fun onPaymentFailed(event: PaymentFailedEvent)
}
```

---

## 도메인 엔티티 (핵심 속성)

### CartItem

```kotlin
@Entity
@Table(name = "ord_cart")
class CartItem(
    @Id val id: String,
    val memberId: String,
    val productId: String,
    val skuId: String,
    val vendorId: String,
    var quantity: Int,
    val addedAt: LocalDateTime,
    var isDeleted: Boolean = false
) {
    fun addQuantity(amount: Int) { this.quantity += amount }
    fun updateQuantity(newQuantity: Int) { this.quantity = newQuantity }
    fun softDelete() { this.isDeleted = true }
}
```

### Order

```kotlin
@Entity
@Table(name = "ord_order")
class Order(
    @Id val id: String,
    val platformOrderId: String,
    val vendorId: String,
    var status: OrderStatus,
    val totalAmount: Int,
    val shippingFee: Int,
    var cancelReason: String? = null,
    var confirmedAt: LocalDateTime? = null,
    val createdAt: LocalDateTime,
    var updatedAt: LocalDateTime
) {
    fun cancel(reason: String) { this.status = OrderStatus.CANCELLED; this.cancelReason = reason }
    fun confirm() { this.status = OrderStatus.CONFIRMED; this.confirmedAt = LocalDateTime.now() }
    fun canCancel(): Boolean = this.status in setOf(OrderStatus.DEPOSIT_PENDING, OrderStatus.PAYMENT_COMPLETED)  // 고객 직접 취소: 입금대기·결제완료 (REQ-ORD-018·080). PREPARING은 고객센터 문의 → 어드민 CS 예외 취소(forceCancel)
    fun canConfirm(): Boolean = this.status == OrderStatus.DELIVERED
}
```

> **(2026-10-15 ERD 기반 DB 전환 반영)**: 실제 `Order` Entity는 위와 전혀 다른 구조다 — `@Id val id: Long`(`GenerationType.IDENTITY`, **String ULID 아님**, ERD §8 리터럴을 그대로 따른 의도적 정정, `order-admin-erd-redesign/plan.md` §1.6), `platformOrder: PlatformOrder`(`@ManyToOne`, 2026-10-19 추가 — 처음엔 평문 `platformOrderId: Long`이었다가 `PlatformOrder` Entity 신설로 FK 연관관계로 교체됨), `vendorId: Long`, `itemAmount/discountAmount/shippingFee/paymentAmount: BigDecimal`(Int 아님), `shippingFeePayer: String`, `claimLock: Boolean`, `shippingDeadline/confirmedAt: LocalDateTime?`, `isDeleted/deletedAt/deletedBy`(soft delete, DP 원안엔 없음), 연관관계 `items: List<OrderItem>`/`delivery: Delivery?`/`claims: List<Claim>`. `cancelReason`/`confirm()`/`cancel()`/`canCancel()`/`canConfirm()` 등 DP 원안의 행위(Rich Domain Model) 메서드는 아직 없다 — 현재는 데이터만 담는 구조.

#### PlatformOrder (완전 신규, 2026-10-19)

> ERD(`runNshop_erd_v1_0.md` §8)·실 코드(`.../order/domain/PlatformOrder.kt`) 기준, DP/DL에 이 상세 정의가 없던 완전 신규 — work-scope 규칙에 따라 신규 생성 사실을 명시.

ERD §8 `ord_platform_order` 25개 컬럼을 그대로 옮긴 애그리거트 루트 Entity. `orders`/`discounts`는 `cascade=ALL`이며, `OrderService.placeOrder()`가 1차 저장(자식 없이 save, id 확보)→2차 저장(자식 포함 save)의 "2단계 저장" 패턴으로 쓴다(`OrderItem.platformOrderId` 비정규화 컬럼이 실제 id를 필요로 하기 때문).

```kotlin
@Entity
@Table(name = "ord_platform_order")
class PlatformOrder(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) val id: Long = 0,
    val platformOrderNo: String,
    val memberId: Long,
    var status: String,                       // DEPOSIT_PENDING 등 — enum 아님, 자유 문자열
    val totalItemAmount: BigDecimal,
    val totalDiscountAmount: BigDecimal,
    val totalShippingAmount: BigDecimal,
    val pointUsedAmount: Int,
    val paymentAmount: BigDecimal,
    val receiverName: String,
    val receiverPhone: String,
    val zipcode: String,
    val address1: String,
    val address2: String?,
    val deliveryMemo: String?,
    val orderedAt: LocalDateTime,
    val createdAt: LocalDateTime,
    val updatedAt: LocalDateTime,
    val cartedAt: LocalDateTime,               // 이번 라운드는 카트 담은 시각 추적 없어 orderedAt과 동일 값(TODO)
    val lastValidatedAt: LocalDateTime? = null, // 동기 사전검증 로직 범위 밖, 항상 null(TODO)
    val priceSnapshot: BigDecimal? = null,      // 범위 밖, 항상 null(TODO)
    val eventPriceId: Long? = null,             // 행사가 미연동, 항상 null(TODO)
    val isDeleted: Boolean = false,
    val deletedAt: LocalDateTime? = null,
    val deletedBy: String? = null,
    @OneToMany(mappedBy = "platformOrder", cascade = [CascadeType.ALL], orphanRemoval = true)
    val orders: MutableList<Order> = mutableListOf(),
    @OneToMany(mappedBy = "platformOrder", cascade = [CascadeType.ALL], orphanRemoval = true)
    val discounts: MutableList<PlatformOrderDiscount> = mutableListOf()
)
```

#### PlatformOrderDiscount (완전 신규, 2026-10-19)

> ERD(`runNshop_erd_v1_0.md` §8)·실 코드(`.../order/domain/PlatformOrderDiscount.kt`) 기준, DP/DL에 이 상세 정의가 없던 완전 신규 — work-scope 규칙에 따라 신규 생성 사실을 명시.

쿠폰 적용 시에만 1건 생성(옵션 처리) — 쿠폰 미적용이면 이 Entity 자체를 생성하지 않는다. ERD §8 14개 컬럼 + 비정규화 `couponCode` 1개 = 15개 컬럼. `promotionId`(ERD `Long?`)와 요청 바디 쿠폰코드(`String`, 예: `"CPN-001"`)의 타입이 달라(비정규화 사유), `promotionId`는 항상 `null`(TODO)로 두고 `couponCode`(ERD 범위 밖 추가 컬럼)에 쿠폰 코드 원문을 보관한다.

```kotlin
@Entity
@Table(name = "ord_platform_order_discount")
class PlatformOrderDiscount(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) val id: Long = 0,
    @ManyToOne val platformOrder: PlatformOrder,
    val discountType: String,                  // 'ORDER_COUPON' 고정(이번 라운드는 쿠폰만)
    val promotionId: Long? = null,              // request.couponId(String)와 타입 불일치, 항상 null(TODO)
    val couponCode: String? = null,             // ⚠ ERD 범위 밖 비정규화 컬럼 — 쿠폰 코드 원문 보관
    val discountAmount: BigDecimal,
    val platformShare: BigDecimal = BigDecimal.ZERO,  // 분담 비율 미연동, 0(TODO)
    val vendorShare: BigDecimal = BigDecimal.ZERO,    // 동일 사유, 0(TODO)
    val partialCancelPolicy: String = "KEEP",
    val isRevoked: Boolean = false,
    val createdAt: LocalDateTime,
    val updatedAt: LocalDateTime,
    val isDeleted: Boolean = false,
    val deletedAt: LocalDateTime? = null,
    val deletedBy: String? = null
)
```

#### OrderItem (완전 신규 상세 — 패키지 트리엔 파일명만 있었음)

> ERD(`runNshop_erd_v1_0.md` §8)·실 코드(`.../order/domain/OrderItem.kt`) 기준, DP에 파일명(`OrderItem.kt`)만 있고 필드 상세 정의가 없던 완전 신규 — work-scope 규칙에 따라 신규 생성 사실을 명시.

ERD §8 `ord_order_item` 원문 컬럼 그대로. `Order`에 종속된 소유 관계(`cascade=ALL`, `orphanRemoval=true`)라 자체 Repository를 두지 않는다(Order 애그리거트를 통해서만 접근). `platformOrderId`는 `ord_order.id`와 동일 값의 비정규화 컬럼(ERD 원문 그대로 유지).

```kotlin
@Entity
@Table(name = "ord_order_item")
class OrderItem(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) val id: Long = 0,
    val platformOrderId: Long,                  // ord_order.id와 동일 값의 비정규화 컬럼
    @ManyToOne val order: Order,
    val productId: Long,
    val skuId: Long,
    val productName: String,
    val option1Type: String?,
    val option1Value: String?,
    val option2Type: String?,
    val option2Value: String?,
    val quantity: Int,
    val priceOriginal: BigDecimal,
    val priceSale: BigDecimal,
    val priceSupply: BigDecimal,                // 공급가 — 이번 라운드는 priceSale과 동일값으로 단순화
    val feeRate: BigDecimal,                    // 수수료율 미연동, 0으로 고정
    var status: String,
    val reviewWritten: Boolean,
    val createdAt: LocalDateTime,
    val updatedAt: LocalDateTime,
    val isDeleted: Boolean,
    val deletedAt: LocalDateTime?,
    val deletedBy: String?
)
```

### Shipment

> v6 리팩토링 신규 엔티티. 배송 실행(운송장/배송상태)을 `order.status`/`claim.status`에서 분리하여 일원화한 테이블.
> `refType`/`refId`로 Order(OUTBOUND)와 Claim(PICKUP/RETURN/EXCHANGE_OUT)을 모두 참조한다.

```kotlin
@Entity
@Table(name = "ord_shipment")
class Shipment(
    @Id val id: String,
    val refType: ShipmentRefType,   // ORDER / CLAIM
    val refId: String,              // orderId 또는 claimId
    val shipmentType: ShipmentType,
    var status: ShipmentStatus,
    var carrier: String? = null,
    var trackingNumber: String? = null,
    var shippedAt: LocalDateTime? = null,
    var deliveredAt: LocalDateTime? = null,
    val createdAt: LocalDateTime,
    var updatedAt: LocalDateTime
) {
    fun registerTracking(carrier: String, trackingNumber: String) {
        this.carrier = carrier
        this.trackingNumber = trackingNumber
        this.status = ShipmentStatus.IN_TRANSIT
        this.shippedAt = LocalDateTime.now()
    }
    fun confirmDelivered() { this.status = ShipmentStatus.DELIVERED; this.deliveredAt = LocalDateTime.now() }
    fun markFailed() { this.status = ShipmentStatus.FAILED }
    fun reship(carrier: String, trackingNumber: String) {
        this.status = ShipmentStatus.PENDING
        this.carrier = carrier
        this.trackingNumber = trackingNumber
        this.status = ShipmentStatus.IN_TRANSIT
        this.shippedAt = LocalDateTime.now()
    }
    fun canRegisterTracking(): Boolean = this.status == ShipmentStatus.PENDING
    fun canReship(): Boolean = this.status == ShipmentStatus.FAILED
}

enum class ShipmentRefType { ORDER, CLAIM }
enum class ShipmentType { OUTBOUND, PICKUP, RETURN, EXCHANGE_OUT }
enum class ShipmentStatus { PENDING, IN_TRANSIT, DELIVERED, FAILED, CANCELLED }
```

### OrderStatusHistory / OrderStatusHistoryService (완전 신규, 2026-10-26)

> 주문/결제/배송/클레임 **상태전이 이력**(`ord_status_history`, append-only). DP 원안의 `OrderHistoryRepository`를 대체하는 실제 구현이다. 상태를 바꾸는 모든 경로는 상태 변경과 같은 트랜잭션에서 `record()`를 호출한다(from==to는 미기록). **기록 단위**: 결제완료까지(주문 생성·결제)는 플랫폼주문 단위(`orderId=null`, ORDER `targetId`=platformOrder.id), 이후 배송·클레임 전이는 vendor 주문 단위(`orderId`=ord_order.id)로 기록한다. 현재 호출부는 `OrderService.placeOrder`(플랫폼주문 ORDER 최초상태)와 `PaymentService.requestPayment`(결제상태: `null→REQUESTED`(PG 요청) → `REQUESTED→COMPLETED`(PG 승인 수신, 카드 등) 또는 `REQUESTED→WAITING_DEPOSIT`(가상계좌 발급 수신, 입금 대기), 모두 플랫폼 단위, `targetId`=pay_payment.id, `reason`에 작업 내용 요약만 기록하며 PG 요청/응답 payload는 저장하지 않음)뿐이며, DELIVERY/CLAIM 전이 기능이 구현되면 같은 방식으로 연결한다(현재는 시드 데이터만 존재). 주문서 진입 시 `OrderService.createOrderSheet(memberId, OrderSheetRequest{items})`가 임시주문(`PlatformOrder.status=TEMP` + vendor별 `Order`/`OrderItem` TEMP)을 저장하고(`getOrderSheet`로 재조회),  `(신규)→TEMP`를 기록하며, 주문서의 쿠폰/포인트 적용은 `OrderService.applyOrderSheetDiscount(memberId, sheetId, OrderSheetDiscountRequest{couponId, pointUsed})`가 검증 후 임시주문에 영속한다(`PlatformOrderDiscount` 교체/삭제 + `totalDiscountAmount`/`pointUsedAmount`/`paymentAmount` 갱신, `PUT .../sheet/{id}/discount`). `placeOrder`는 요청 바디가 아니라 이 임시주문의 상품과 저장된 쿠폰/포인트로 금액을 계산·재검증하고 주문/상품 상태를 갱신하며 `TEMP→DEPOSIT_PENDING`("결제 요청")을 기록한다(2026-10-26, 이후 재고차감/결제완료 상태 확장 예정). **(2026-10-26 재고차감 비동기)** `placeOrder`는 결제 시 상태를 `STOCK_REQUESTED`로 바꾸고 `OutboxEvent(STOCK_DEDUCT_REQUESTED)`를 같은 트랜잭션에 저장만 한다(동기 PG 호출 제거, API는 이벤트를 조회하지 않는다). 후속 처리는 **별도 컨슈머 앱 `runNshop-consumer`**(`OrderEventConsumer` `@Scheduled`(다중 인스턴스 가능), `OrderEventRepository`(JDBC — `FOR UPDATE SKIP LOCKED` 점유·임대 만료 복귀·백오프 재시도·상태 변경·후속 이벤트 적재), `OrderEventApiClient`(RestClient))가 이벤트를 조회해 API 내부 API `OrderInternalController`(`POST /api/internal/v1/order-events/process`, `.../give-up`)를 호출하면, `OrderEventHandler`(`@Transactional`, 요청 1건=트랜잭션 1개, 멱등)가 `CatalogApi.deductStock`(Port, 구현 `catalog.service.StockService` — SKU마다 `SkuStockDeductor`가 독립 트랜잭션(`REQUIRES_NEW`)으로 `cat_sku_stock` 조건부 UPDATE + `cat_stock_deduction`(request_id+sku_id) 기록, 이미 차감한 SKU는 건너뜀)으로 차감해 전부 성공이면 `STOCK_DEDUCTED`, 일부 실패면 주문 상태 불변 + `result=STOCK_PARTIAL`(재시도 시 실패 SKU만 재차감)로 응답하고, 재시도 소진 시 `giveUp`이 `CatalogApi.restoreStock`으로 차감분을 복원하며 `STOCK_FAILED`로 전이하고, `PAYMENT_REQUESTED`에서 `PaymentApi.requestPayment`로 `DEPOSIT_PENDING`으로 전이한다. 엔티티 `OutboxEvent`(적재 전용)/`SkuStock`/`StockDeduction`, DTO `OrderEventProcessRequest`/`OrderEventProcessResult`/`OrderEventGiveUpRequest`. `PlatformOrder`의 금액/배송지 필드는 이를 위해 `var`다. `getAdminOrderDetail`의 `history`가 `findByPlatformOrderId()`를 사용한다. 이력은 **등록=JPA(`OrderStatusHistoryRepository`, INSERT만)**, **목록 조회=MyBatis(`OrderStatusHistoryMapper`/`OrderStatusHistoryMapper.xml`, slave)**로 나눈다(단건·등록은 JPA, 다건·통계는 Mapper 규칙).

```kotlin
enum class StatusTargetType { ORDER, PAYMENT, DELIVERY, CLAIM }

@Entity @Table(name = "ord_status_history")
class OrderStatusHistory(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) val id: Long = 0,
    val platformOrderId: Long, val orderId: Long?,
    val targetType: String, val targetId: Long?,
    val fromStatus: String?, val toStatus: String,
    val changedBy: String, val reason: String?, val createdAt: LocalDateTime
)

@Service @Transactional
class OrderStatusHistoryService(
    private val repository: OrderStatusHistoryRepository, // 등록: JPA(master)
    private val mapper: OrderStatusHistoryMapper          // 목록 조회: MyBatis(slave)
) {
    fun record(platformOrderId: Long, targetType: StatusTargetType, fromStatus: String?, toStatus: String,
               orderId: Long? = null, targetId: Long? = null, changedBy: String = "SYSTEM",
               reason: String? = null, at: LocalDateTime = LocalDateTime.now())
    fun findByPlatformOrderId(platformOrderId: Long): List<StatusHistoryRow>  // 최신순(Mapper)
}
```

### Delivery (완전 신규 — Shipment와 다른 개념)

> ERD §8의 `ord_delivery`(배송 주소/송장 1:1)를 그대로 옮긴 Entity. **`Shipment`(ord_shipment, 위 섹션의 미래 설계)와는 다른 개념**이다 — `Shipment`는 아직 테이블/코드가 없고(ERD §8 `ord_shipment`는 order-admin-erd-redesign 범위 밖), `Delivery`는 지금 admin 상세(§16)의 `shipping.carrier/trackingNumber` 소스로 실제 쓰인다(`shipping.recipientName/phone/address`는 여전히 Mock, DL §16 결정). 신규 생성 사실 명시(DP/DL에 `Delivery`라는 이름 자체가 없었음, `Shipment`와 혼용하지 않도록 테이블명 그대로 명명) — `order-admin-erd-redesign/plan.md` §1.3/§0 근거.

```kotlin
@Entity
@Table(name = "ord_delivery")
class Delivery(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY) val id: Long = 0,
    @OneToOne @JoinColumn(name = "order_id") val order: Order,
    val deliveryCompanyId: Long?,     // cfg_delivery_company FK — Config 도메인 범위 밖이라 물리 FK 없이 값만 저장
    val trackingNo: String?,
    val shippingFee: BigDecimal,
    val shippingFeePayer: String,
    var status: String,
    val shippedAt: LocalDateTime?,
    val deliveredAt: LocalDateTime?,
    val returnTrackingNo: String?,
    val createdAt: LocalDateTime,
    val updatedAt: LocalDateTime,
    val isDeleted: Boolean,
    val deletedAt: LocalDateTime?,
    val deletedBy: String?
)
```

### Claim

```kotlin
@Entity
@Table(name = "ord_claim")
class Claim(
    @Id val id: String,
    val orderId: String,
    val claimType: ClaimType,
    var status: ClaimStatus,
    val reason: String,
    val detailReason: String? = null,
    val submittedResponsibility: ClaimResponsibility,  // 고객이 신청 시 자진신고한 귀책값. 생성 시 설정, 이후 불변(REQ-ORD-076)
    var responsibility: ClaimResponsibility? = null,   // CS 확정 귀책값. decideResponsibility()로만 갱신되며 submittedResponsibility와 달라질 수 있음(REQ-ORD-066)
    val channel: ClaimChannel = ClaimChannel.SELF,
    var pickupAddressId: String? = null,
    val exchangeSkuId: String? = null,       // 교환 대상 SKU (Catalog 도메인 FK, claimType=EXCHANGE 전용, 선출고 시 사용)
    var tagIntact: Boolean? = null,          // 품질점검 판정 근거 — 택(TAG) 부착 여부 (claimType=EXCHANGE 전용, RETURN이면 null)
    val createdAt: LocalDateTime,
    var updatedAt: LocalDateTime
) {
    val images: List<ClaimImage> = emptyList()
    // ord_claim_image 1:N (최대 3장). responsibility=VENDOR 신청 시 최소 1장 필수, CUSTOMER는 선택 (REQ-ORD-058)

    // v6: 수거중/반송중 상태는 Shipment(ord_shipment)로 이관 — registerPickupTracking/startReturnShipping/completeReturnDelivery 제거.
    fun decideResponsibility(responsibility: ClaimResponsibility) {
        this.responsibility = responsibility
        if (responsibility == ClaimResponsibility.CUSTOMER) this.status = ClaimStatus.PAYMENT_PENDING
        // VENDOR: status는 RECEIVED 그대로 유지 — shipment(PICKUP) 생성은 ClaimService에서 별도 처리, INSPECTING 전환은 confirmPickup()에서 수행
        // 주의: 이 메서드는 responsibility만 갱신한다. submittedResponsibility는 절대 건드리지 않음 —
        // 고객 자진신고값은 생성 시점 값 그대로 보존되며(불변, REQ-ORD-076), CS 확정값(responsibility)과 별도 컬럼으로 공존한다.
    }
    // CS 귀책판정(override) — 고객이 신청 시 제출한 responsibility 값을 CS 판정으로 덮어씀 (REQ-ORD-066)

    // startInspecting()은 shipment(PICKUP)가 DELIVERED됐을 때 ClaimService.confirmPickup()에서 호출되는 별도 메서드로 유지.
    fun startInspecting() { this.status = ClaimStatus.INSPECTING }
    fun passInspection(tagIntact: Boolean?) { this.status = ClaimStatus.PICKED_UP; this.tagIntact = tagIntact }
    fun rejectInspection(tagIntact: Boolean?) { this.status = ClaimStatus.PICKUP_REJECTED; this.tagIntact = tagIntact }
    fun requestReturnPayment() { this.status = ClaimStatus.RETURN_PAYMENT_PENDING }
    fun refund() { this.status = ClaimStatus.REFUNDED }
    fun dispose() { this.status = ClaimStatus.DISPOSED }
    fun complete() { this.status = ClaimStatus.COMPLETED }
    fun reject(reason: String) { this.status = ClaimStatus.REJECTED }
    fun cancel() { this.reject("고객 자진 철회") }
    // 고객 자진취소(§16-7-2, REQ-ORD-071/073). RECEIVED/PAYMENT_PENDING 상태에서만 호출 가능 —
    // 상태 검증은 ClaimService.cancelClaim()이 선행 수행하며, 위반 시 ClaimCancelNotAllowedException을 던진다.
    fun canDispose(): Boolean = this.status == ClaimStatus.PICKUP_REJECTED
    fun canCancel(): Boolean = this.status == ClaimStatus.RECEIVED || this.status == ClaimStatus.PAYMENT_PENDING
}

enum class ClaimType { CANCEL, RETURN, EXCHANGE }

enum class ClaimStatus {
    RECEIVED,               // 접수
    PAYMENT_PENDING,        // 수거 배송비 결제대기
    PAYMENT_EXPIRED,        // 배송비 결제 만료 (접수 후 24시간)
    INSPECTING,             // 입고 확인 → 품질점검중
    PICKED_UP,              // 품질점검 합격 (수거완료)
    PICKUP_REJECTED,        // 품질점검 거부 (수거거부)
    REFUNDED,               // 환불완료
    RETURN_PAYMENT_PENDING, // 반송 배송비 추가결제 대기
    DISPOSED,               // 폐기
    COMPLETED,              // 클레임 완료
    REJECTED                // 클레임 반려
}
// v6: PICKUP/RETURN_SHIPPING/RETURN_DELIVERED 제거(11상태) — 수거/반송 배송 진행상태는 Shipment.status로 추적

enum class ClaimResponsibility { CUSTOMER, VENDOR }
// v6: PLATFORM 제거 — 귀책은 CUSTOMER/VENDOR 2종만

enum class ClaimChannel { SELF, CS }
```

> **(2026-10-15 ERD 기반 DB 전환 반영)**: 실제 `Claim` Entity는 위 11상태 모델(`ClaimStatus` enum, `submittedResponsibility`/`responsibility` 분리, `decideResponsibility()`/`passInspection()` 등 행위 메서드)을 구현하지 않는다 — ERD §8 원문 컬럼만 그대로 옮긴 **읽기 전용 스냅샷**이다: `@Id val id: Long`(IDENTITY), `order: Order`(FK), `claimNo/claimType/cancelType/status: String`(enum 아님, 자유 문자열), `blameType/blameEvidenceUrls(jsonb)/reason/channel/counselorId/counselorMemo/refundAmount/extraDeliveryFee/extraPaymentId/extraPaymentStatus/completedAt`. admin 주문상세(§16)에서 **조회만** 되고(`buildClaimMap()`), 클레임 생성/상태전이 API(§7/§19-1 등)는 이 Entity와 아직 연결되지 않았다(여전히 Mock 응답, `ClaimController.kt` 참고).

### ClaimPayment

```kotlin
@Entity
@Table(name = "ord_claim_payment")
class ClaimPayment(
    @Id val id: String,
    val claimId: String,
    val paymentType: ClaimPaymentType,  // PICKUP(수거배송비) / RETURN(반송배송비)
    val amount: Int,
    val couponId: String? = null,
    val couponDiscount: Int = 0,
    val paidAmount: Int,
    var status: ClaimPaymentStatus,
    var pgTransactionId: String? = null,
    var paidAt: LocalDateTime? = null,
    var expiredAt: LocalDateTime? = null,      // 결제 만료 시각 (접수 후 24시간)
    val createdAt: LocalDateTime
) {
    fun pay(pgTransactionId: String) { this.status = ClaimPaymentStatus.PAID; this.pgTransactionId = pgTransactionId; this.paidAt = LocalDateTime.now() }
    fun expire() { this.status = ClaimPaymentStatus.EXPIRED; this.expiredAt = LocalDateTime.now() }
}

enum class ClaimPaymentType { PICKUP, RETURN }
enum class ClaimPaymentStatus { PENDING, PAID, EXPIRED }
```

### ClaimImage

```kotlin
@Entity
@Table(name = "ord_claim_image")
class ClaimImage(
    @Id val id: String,
    val claimId: String,
    val imageUrl: String,
    val uploadedBy: Uploader,       // CUSTOMER(접수 시 첨부, §16-7) / VENDOR(품질점검 등 판매자 첨부 근거)
    val sortOrder: Int = 0,
    val createdAt: LocalDateTime
)
// 클레임 첨부 이미지. 최대 3장. responsibility=VENDOR(상품불량 등) 신청 시 최소 1장 필수(REQ-ORD-058), CUSTOMER 귀책은 선택

enum class Uploader { CUSTOMER, VENDOR }
```

---

---

## 작성 규칙

| 규칙 | 설명 |
|---|---|
| 시퀀스 참여자 = 클래스 | 1:1 대응 |
| Controller는 로직 없음 | 요청 수신·응답 반환만 (Thin Controller) |
| Service에 비즈니스 로직 | 검증·조합·트랜잭션 관리 |
| PublicApi = interface | 도메인 간 계약, 구현은 제공 도메인에서 |
| Entity는 행위를 가짐 | `order.cancel(reason)` — Rich Domain Model |
| PgClient = interface | 외부 시스템(PG) 경계, 구현은 인프라 레이어 |

---

---

## 근거

| 항목 | 출처 |
|---|---|
| 클래스 도출 | 시퀀스(DM) 참여 객체 |
| 메서드 시그니처 | 인터페이스 명세(DL) Order endpoint (DQ API 목록 기준, 건수는 DQ-프로그램목록/order.md 참조) |
| 패키지 구조 | 컴포넌트(D9) 도메인 모듈 구조 |
| 도메인 간 계약 | 도메인정의서(DB) 경계 규칙, 이벤트 플로우(DI) |
| 엔티티 속성 | ERD(DF) Order 10테이블(v6: ord_shipment 신설, ord_claim_image 포함), Payment 5테이블(v2: pay_card_fail_counter 신설 포함) |
| 이벤트 처리 | ADR-006 Outbox 패턴 |
| PG 추상화 | ADR-005 PG 토큰화 |
| 클레임 첨부 이미지(ClaimImage) | ERD(DF) Order `ord_claim_image`, REQ-ORD-058 (VENDOR귀책 사진 1장 이상 필수) |
| 카드 연속실패 카운터(CardFailCounter) | ERD(DF) Payment `pay_card_fail_counter`, REQ-PAY-023 (바텀업 검토 보완, 2026-08-21) |
| CS 귀책판정 override(decideResponsibility) | REQ-ORD-066 (고객 자진신고를 CS가 덮어씀), 상태머신(DH) RECEIVED→PAYMENT_PENDING/INSPECTING 전이 (바텀업 검토 보완, 2026-08-21) |
| PaymentService ↔ CardFailCounter 배선(handlePgCallback/requestPayment) | 시퀀스(DM) §4(결제 요청)·§4-1(PG콜백 처리), REQ-PAY-018/023 — 엔티티만 있고 호출부가 없던 배선 결함 수정 (2026-08-21) |
| Claim.submittedResponsibility(불변) | 시퀀스(DM) §7(클레임 신청)·§7-1(귀책판정), REQ-ORD-076 — 고객 자진신고값과 CS 확정값(responsibility) 분리 보존 (2026-08-21) |
| ClaimImage.uploadedBy | 시퀀스(DM) §7 saveImages(uploadedBy=CUSTOMER) — 첨부 이미지의 등록 주체(CUSTOMER/VENDOR) 구분 (2026-08-21) |
| 클레임 자진취소(ClaimService.cancelClaim/Claim.cancel) | 시퀀스(DM) §7-2, REQ-ORD-071/073 — RECEIVED/PAYMENT_PENDING만 허용, 이후 상태는 ClaimCancelNotAllowedException (2026-08-21) |
| ShippingController(registerTracking/reship) | 시퀀스(DM) §9·§22, REQ-ORD-062 — ShipmentService.reship()은 기존에 있었으나 호출하는 컨트롤러 배선이 문서에 없던 결함 보완 (2026-08-21) |
| admin 주문현황/상세 ERD 기반 DB 전환(Order/OrderItem/Delivery/Claim 실 Entity, OrderMapper) | `.agents/tasks/order-admin-erd-redesign/plan.md`, 실제 코드(`order/domain/*.kt`, `order/mapper/OrderMapper.kt`) (2026-10-15) |
| 주문 상태전이 이력 영속화(OrderStatusHistory/Service, ord_status_history) | `.agents/tasks/order-status-history-persist/`, 실제 코드(`order/domain/OrderStatusHistory.kt`, `order/service/OrderStatusHistoryService.kt`) (2026-10-26) |
| mobile 주문생성(결제확정) 2단계 저장(PlatformOrder/PlatformOrderDiscount 신설, OrderService.placeOrder) | `.agents/tasks/order-create-mobile-api/design.md`·`plan.md`, 실제 코드(`OrderService.kt`, `order/domain/PlatformOrder*.kt`) (2026-10-19) |
