# 클래스 설계 — Payment 도메인

> 상위 문서: [readme.md](readme.md)
> **단계**: 상세설계 (S3) | **문서범위**: Bolt (Payment) | **문서종류**: Design
> 도메인 간 공용 계약(PublicApi)은 [common.md](common.md) 참조

---

## 2. Payment 도메인 — 패키지 구조

```
com.runnshop.payment/
├── payment/
│   ├── controller/
│   │   └── PaymentInternalController.kt
│   ├── service/
│   │   └── PaymentService.kt
│   ├── repository/
│   │   ├── PaymentRepository.kt
│   │   └── PaymentLogRepository.kt
│   ├── domain/
│   │   ├── Payment.kt
│   │   └── PaymentLog.kt
│   └── dto/
│       ├── PaymentRequest.kt
│       └── PaymentResponse.kt
├── refund/
│   ├── service/
│   │   └── RefundService.kt
│   └── dto/
│       └── RefundRequest.kt
├── method/
│   ├── controller/
│   │   └── PaymentMethodController.kt
│   ├── service/
│   │   └── PaymentMethodService.kt
│   ├── repository/
│   │   ├── PaymentMethodRepository.kt
│   │   ├── CardRestrictionRepository.kt
│   │   └── CardFailCounterRepository.kt
│   ├── domain/
│   │   ├── PaymentMethod.kt
│   │   ├── CardRestriction.kt
│   │   └── CardFailCounter.kt       (v2 신규 — REQ-PAY-023)
│   └── dto/
│       ├── RegisterMethodRequest.kt
│       └── MethodListResponse.kt
├── pg/
│   ├── PgClient.kt                  (interface)
│   └── TossPaymentsClient.kt        (구현)
└── event/
    ├── PaymentEventPublisher.kt
    └── PaymentEventListener.kt
```

---
## 4. Payment 도메인 — 클래스 상세

### PaymentService

> (2026-08-21 배선 보완) `CardFailCounter`(REQ-PAY-023) 엔티티·리포지토리는 있었으나 `PaymentService`가 이를 호출하는 배선이 없었다. §16-4-1(Payment 내부 PG콜백 처리) 시퀀스에 맞춰 `handlePgCallback`을 구체화하고, 카드 당일제한 조회(`checkCardRestriction`)는 §16-4(결제 요청)의 위치대로 `requestPayment`에서 호출되도록 배선한다.

```kotlin
@Service
@Transactional
class PaymentService(
    private val paymentRepository: PaymentRepository,
    private val paymentLogRepository: PaymentLogRepository,
    private val cardFailCounterRepository: CardFailCounterRepository,
    private val paymentMethodService: PaymentMethodService,
    private val pgClient: PgClient,
    private val eventPublisher: PaymentEventPublisher
) {
    fun requestPayment(request: PaymentRequest): PaymentResponse
    // §16-4 — 최초 진입 시 paymentMethodService.checkCardRestriction(request.cardHash) 호출(REQ-PAY-018)
    //   true(당일 차단 상태) → CARD_RESTRICTED 응답, 이후 로직 미진행
    //   false → PG 승인 요청 (응답 대기 3초 — 초과 시 재시도 없이 CONFIRMING, PG 거래 조회로 확정(REQ-PAY-005·029). 결과는 handlePgCallback으로 비동기 수신. 실패 응답은 총 3회 시도(재시도 최대 2회) 후 CANCELLED(REQ-PAY-003·004, 정책 9.6.1))

    fun handlePgCallback(paymentId: String, result: PgResult)
    // §16-4-1 — PG 콜백(승인/실패 웹훅) 또는 재시도 소진 시 호출. cardHash는 paymentRepository.findById(paymentId)로 조회한 결제수단에서 얻는다.
    //   승인 성공: paymentRepository.updateStatus(PAID)
    //             → cardFailCounterRepository.resetFailCount(cardHash) (REQ-PAY-023 — 카운터 0 초기화)
    //             → eventPublisher.publishPaymentApproved(payment)
    //   승인 실패(총 3회 시도 모두 실패, REQ-PAY-004):
    //             → cardFailCounterRepository.incrementFailCount(cardHash) → consecutiveFailCount 반환
    //             → consecutiveFailCount >= 3이면 paymentMethodService.restrictCard(cardHash) 호출(REQ-PAY-018, pay_card_restriction 생성)
    //               후 cardFailCounterRepository.resetFailCount(cardHash)로 카운터 재초기화
    //             → eventPublisher.publishPaymentFailed(payment, reason)

    // ── 설계안 (2026-10-29, 미구현) — 시퀀스 DM payment §4-2~4-4 ──
    fun confirmByInquiry(paymentId: String)
    // REQ-PAY-029 — CONFIRMING(3초 무응답) 건을 pgClient.inquire(pgTransactionId)로 확정.
    //   승인 → PAID + publishPaymentApproved
    //   미승인 → 실패 1회 합산. 누적 실패 3회 미만이면 PENDING 복귀(같은 행·같은 멱등키·pay_group_no 불변) 후 3초 뒤 재요청,
    //            3회 도달(최초 시도 포함 총 3회 시도) 시 CANCELLED + publishPaymentFailed
    //   CONFIRMING 중 같은 주문 requestPayment는 거부(REQ-PAY-005)

    fun handleDepositNotice(notice: DepositNotice)
    // REQ-PAY-030 — 가상계좌 입금 통보. 입금대기면 금액 대조 후 PAID.
    //   주문이 이미 CANCELLED면 PAID로 바꾸지 않고 입금액을 환불 대상으로 기록(취소 우선) →
    //   refundService.refundToAccount(paymentId, amount, RefundReason.LATE_DEPOSIT)
    //   (저장된 refundAccount 사용, 운영자 승인 없음, 기준일=입금 통보 수신일, 기한 3영업일 8.1.3)

    fun validateRefundAccount(refundAccount: RefundAccount?, ordererName: String, method: String)
    // REQ-PAY-031 — method=VIRTUAL_ACCOUNT일 때만. 없으면 REFUND_ACCOUNT_REQUIRED,
    //   결제 요청 시점에 수행하며 예금주≠주문자·실명 확인 실패면 REFUND_ACCOUNT_INVALID. 통과 시 Payment.refundAccount에 저장(계좌번호 암호화).
    //   카드·간편결제는 호출하지 않는다.
}
```

### RefundService

```kotlin
@Service
@Transactional
class RefundService(
    private val paymentRepository: PaymentRepository,
    private val paymentLogRepository: PaymentLogRepository,
    private val pgClient: PgClient,
    private val eventPublisher: PaymentEventPublisher   // 2026-11-04 신규 — 환불 완료 시 PAYMENT_REFUNDED 발행
) {
    fun fullRefund(orderId: String, amount: Int)
    // 환불 성공 시 status→REFUNDED + eventPublisher.publishPaymentRefunded(payment, amount, RefundReason.ORDER_CANCELLED)
    fun partialRefund(orderId: String, amount: Int)   // 어드민 [환불 처리](API-029) 요청 시 호출(클레임 환불의 유일한 경로)
    // 환불 성공 시 status→REFUNDED/PARTIAL_REFUNDED + eventPublisher.publishPaymentRefunded(payment, amount, RefundReason.CLAIM_COMPLETED)
    //   (RefundReason.CLAIM_COMPLETED는 "클레임 환불"의 사유값이며, Payment가 CLAIM_COMPLETED 이벤트로 환불을 트리거하지는 않는다 — 2026-11-03 확정과 동일한 의미 구분)
    fun manualRefund(adminId: String, paymentId: String)
    // 수동 재환불 성공 시 eventPublisher.publishPaymentRefunded(payment, amount, RefundReason.MANUAL)
    fun refundToAccount(paymentId: String, amount: Int, reason: RefundReason)
    // 설계안(2026-10-29, 미구현) — 저장된 refundAccount으로 자동 환불(LATE_DEPOSIT 등). 계좌 오류 지급 거절은 환불실패+재등록 안내(8.7.2),
    //   PG 오류는 1시간 간격 최대 3회 재시도 후 운영자 이관(8.8.2, 정본. 현행 구현의 즉시 실패·보상 1회는 이력)
    //   환불 성공 시 eventPublisher.publishPaymentRefunded(payment, amount, reason)(= RefundReason.LATE_DEPOSIT) 발행 (2026-11-04 신규)
}
```

> **2026-11-04 신규 — `publishPaymentRefunded` 배선**: 이벤트플로우(DI payment.md) `PAYMENT_REFUNDED` 신설에 따른 보완이다. 4개 환불 경로(`fullRefund`/`partialRefund`/`manualRefund`/`refundToAccount`) 모두 **PG(또는 계좌이체) 환불이 실제로 성공한 뒤**에만 발행하며, 실패·재시도 중에는 발행하지 않는다(실패는 `pay_payment_log`에만 기록, 운영자 이관 시점까지 이벤트 없음). `RefundReason`은 기존 enum(`ORDER_CANCELLED`/`CLAIM_COMPLETED`/`LATE_DEPOSIT`/`MANUAL`, 본 문서 "도메인 엔티티" 절)을 그대로 이벤트 payload의 `refundReason`에 싣는다 — 새 식별자를 만들지 않고 기존 값을 재사용했다.

### PaymentMethodService

```kotlin
@Service
@Transactional
class PaymentMethodService(
    private val methodRepository: PaymentMethodRepository,
    private val cardRestrictionRepository: CardRestrictionRepository,
    private val pgClient: PgClient
) {
    fun registerMethod(memberId: String, request: RegisterMethodRequest): MethodResponse
    fun deleteMethod(memberId: String, methodId: String)
    fun getMyMethods(memberId: String): List<MethodResponse>
    fun checkCardRestriction(cardHash: String): Boolean
    // PaymentService.requestPayment()가 결제 요청 접수 시점에 호출 (REQ-PAY-018, §16-4)
    fun restrictCard(cardHash: String)
    // cardRestrictionRepository에 당일 제한 레코드 생성. PaymentService.handlePgCallback()이
    // 연속실패 3회 도달 시 호출 (REQ-PAY-018, §16-4-1)
    fun releaseExpiredRestrictions()  // 익일 00:00 배치
}
```

> v2 배선 정리(2026-08-21): incrementFailCount/resetFailCount(consecutiveFailCount 갱신)는
> PaymentService가 cardFailCounterRepository를 직접 호출하는 방식으로 이동(§16-4-1) — 중복 소유 방지.
> 본 서비스는 카드 제한(pay_card_restriction) 생성·조회만 담당한다.

### PaymentMethodController

```kotlin
@RestController
@RequestMapping("/api/mobile/v1/my/payment-methods")
class PaymentMethodController(private val paymentMethodService: PaymentMethodService) {

    @GetMapping
    fun getMyMethods(
        @RequestHeader("Authorization") bearer: String  // Bearer {memberId} — DL §12~14 기준, 서버가 memberId 해석
    ): ApiResponse<List<MethodResponse>>

    @PostMapping
    fun registerMethod(
        @RequestHeader("Authorization") bearer: String  // Bearer {memberId} — DL §12~14 기준, 서버가 memberId 해석,
        @RequestBody request: RegisterMethodRequest
    ): ApiResponse<MethodResponse>

    @DeleteMapping("/{methodId}")
    fun deleteMethod(
        @RequestHeader("Authorization") bearer: String  // Bearer {memberId} — DL §12~14 기준, 서버가 memberId 해석,
        @PathVariable methodId: String
    ): ApiResponse<Unit>
}
```

### CardFailCounter

> v2 신규 엔티티 (REQ-PAY-023). 카드별 연속 결제실패 횟수를 추적한다. `pay_card_fail_counter`(card_hash PK)는 카드당 1행을 upsert 방식으로 갱신하며, 결제 성공 시 0으로 리셋, 3회 연속 실패 시 `pay_card_restriction`(당일 제한) 레코드를 생성한다.

```kotlin
@Entity
@Table(name = "pay_card_fail_counter")
class CardFailCounter(
    @Id val cardHash: String,
    var consecutiveFailCount: Int = 0,
    var updatedAt: LocalDateTime
) {
    fun increment(): Int {
        this.consecutiveFailCount += 1
        this.updatedAt = LocalDateTime.now()
        return this.consecutiveFailCount
    }
    fun reset() {
        this.consecutiveFailCount = 0
        this.updatedAt = LocalDateTime.now()
    }
    fun hasReachedLimit(): Boolean = this.consecutiveFailCount >= 3
}
```

### CardFailCounterRepository

> `PaymentService.handlePgCallback()`(§16-4-1)이 직접 호출하는 upsert형 리포지토리. 카드당 1행을 갱신하며 호출부에서 별도 조회 없이 바로 증감시킨다.

```kotlin
interface CardFailCounterRepository {
    fun incrementFailCount(cardHash: String): Int
    // find-or-create(cardHash) → CardFailCounter.increment() → save → 갱신된 consecutiveFailCount 반환
    fun resetFailCount(cardHash: String)
    // find-or-create(cardHash) → CardFailCounter.reset() → save
}
```

### PgClient (도메인 경계 — 외부 시스템 계약)

```kotlin
interface PgClient {
    fun requestApproval(request: PgApprovalRequest): PgApprovalResponse
    fun requestRefund(request: PgRefundRequest): PgRefundResponse
    fun issueBillingKey(request: PgBillingRequest): PgBillingResponse
    fun revokeBillingKey(billingKey: String)
    // 설계안(2026-10-29, 미구현) — REQ-PAY-029·망취소(정책 4.6.2). PgGateway(아래 "결제 모듈 확장 구조")의 query·cancel과 같은 책임
    fun inquire(pgTransactionId: String): PgInquiryResponse   // 거래 조회: 승인 / 미승인
    fun cancelNetwork(pgTransactionId: String): PgCancelResponse   // 망취소 (배치 호출)
    fun verifyDepositNotice(signature: String, body: String): DepositNotice   // 입금 통보 서명 검증
}
```

> `PgClient`는 현재 단일 PG(Toss) 계약이고, "결제 모듈 확장 구조"의 `PgGateway`는 PG별 어댑터다. `inquire`·`cancelNetwork`·`verifyDepositNotice`는 `PgGateway`의 `query`·망취소·`verifyWebhook`에 1:1 대응하며, 어댑터 도입 시 `PgClient`가 `PgGateway`로 대체된다.

### PaymentEventPublisher

```kotlin
@Component
class PaymentEventPublisher(private val outboxRepository: OutboxRepository) {
    fun publishPaymentApproved(payment: Payment)
    fun publishPaymentFailed(payment: Payment, reason: String)
    fun publishPaymentRefunded(payment: Payment, refundAmount: Int, reason: RefundReason)
    // 2026-11-04 신규 — DI(이벤트플로우)/payment.md PAYMENT_REFUNDED 발행. RefundService의 4개 환불 경로(전액/부분/수동/계좌이체 자동)가
    //   PG(또는 계좌이체) 환불 성공 직후 호출한다. reason은 기존 RefundReason enum을 그대로 payload에 싣는다(신규 식별자 없음)
}
```

### PaymentEventListener

```kotlin
@Component
class PaymentEventListener(
    private val refundService: RefundService
) {
    @EventListener
    fun onOrderCancelled(event: OrderCancelledEvent)
    // 클레임 환불은 어드민 [환불 처리](API-029)가 RefundService.partialRefund를 호출한다. CLAIM_COMPLETED는 Payment가 환불에 쓰지 않는다.
}
```

---

## 도메인 엔티티 (핵심 속성)

### PaymentStatus · RefundAccount · RefundReason (설계안, 2026-10-29, 미구현)

```kotlin
enum class PaymentStatus {
    PENDING,            // 승인 요청 전·재요청 대기(자동 재시도 시 복귀)
    WAITING_DEPOSIT,    // 가상계좌 입금 대기(주문 DEPOSIT_PENDING)
    CONFIRMING,         // 결제 확인 중 — 승인 응답 3초 무응답, PG 거래 조회 확정 전(재결제 차단, REQ-PAY-005·029)
    PAID, CANCELLED, REFUNDED, PARTIAL_REFUNDED
}

// 값 객체 — 가상계좌 결제 시 입력·저장(REQ-PAY-031). 마이페이지 등록은 폐기
data class RefundAccount(
    val bankName: String,
    val accountNoEncrypted: String,   // 암호화 저장, 표시는 마스킹
    val holderName: String            // 예금주 = 주문자 본인, 실명 확인
)

enum class RefundReason { ORDER_CANCELLED, CLAIM_COMPLETED /* 어드민 환불 처리(API-029) 요청분 사유 */, LATE_DEPOSIT /* 취소 확정 주문의 입금 통보 자동 환불, REQ-PAY-030 */, MANUAL }
```

### Payment

```kotlin
@Entity
@Table(name = "pay_payment")
class Payment(
    @Id val id: String,
    val orderId: String,
    val platformOrderId: String,
    val memberId: String,
    val pgProvider: String = "TOSS",
    var pgToken: String? = null,
    val paymentMethod: String,
    val amount: Int,
    val pointAmount: Int = 0,
    var status: PaymentStatus,
    var refundAccount: RefundAccount? = null,   // 설계안(2026-10-29, 미구현): 가상계좌 결제만. 카드·간편결제는 null (REQ-PAY-031)
    var approvedAt: LocalDateTime? = null,
    var cancelledAt: LocalDateTime? = null,
    var refundedAt: LocalDateTime? = null,
    val createdAt: LocalDateTime,
    var updatedAt: LocalDateTime
) {
    fun approve(pgToken: String) { this.status = PaymentStatus.PAID; this.pgToken = pgToken; this.approvedAt = LocalDateTime.now() }
    fun cancel() { this.status = PaymentStatus.CANCELLED; this.cancelledAt = LocalDateTime.now() }
    fun refund() { this.status = PaymentStatus.REFUNDED; this.refundedAt = LocalDateTime.now() }
    fun partialRefund() { this.status = PaymentStatus.PARTIAL_REFUNDED }
}
```

> **(2026-10-23 실제 구현 반영 — `pay_payment` 1개 테이블, `payment-persist-mobile-order` 작업)**
> 위 `Payment`는 본개발(미래 설계) 기준이며 그대로 보존한다. 이번 라운드는 모바일 주문생성 시 결제를
> 실제로 `pay_payment` 테이블에 저장하고, 어드민/모바일 주문상세의 결제정보 블록이 그 저장값을 조회해
> 보여주도록 하는 범위만 다룬다(`pay_payment_cancel`/`pay_extra_payment`/`pay_payment_log`/`pay_fds_log`
> 4개 테이블, 실 PG 연동, 상태 전이(`approve`/`cancel`/`refund`/`partialRefund`)는 범위 밖 —
> `.agents/tasks/payment-persist-mobile-order/design.md` §0/§7).
>
> 실제 `Payment` Entity는 위 원안과 PK 타입·필드 구성이 다르다 — ERD(`runNshop_erd_v1_0.md` §9
> `pay_payment`, 1910-1939행) 리터럴을 1차 근거로 따른 정정이다(`Order`/`PlatformOrder`가 이미 겪은
> 동일한 ERD-vs-DP 충돌과 같은 해법, work-scope "1차 근거 기준 정정" 원칙 — design.md §1 결정 1):
>
> ```kotlin
> @Entity
> @Table(name = "pay_payment")
> class Payment(
>     @Id @GeneratedValue(strategy = GenerationType.IDENTITY) val id: Long = 0,  // String(ULID) 아님 — ERD BIGINT 그대로
>     val paymentNo: String,              // "PAY-yyyyMMdd-NNNNN", 당일 생성건수 채번(OrderService.nextPlatformOrderNo()와 동일 패턴)
>     val platformOrderId: Long,          // PlatformOrder에 대한 @ManyToOne 아님 — 평문 FK 컬럼(Payment가 Order Entity를 직접 참조하면 도메인 경계가 깨짐)
>     val memberId: Long,
>     val paymentAmount: BigDecimal,
>     val approvedAmount: BigDecimal?,
>     val paymentMethod: String,          // ERD 3값(CARD/POINT/MIXED)만 허용 — Order의 paymentMethodType 4종(CARD/EASY_PAY/POINT/VIRTUAL_ACCOUNT)을 근사 매핑(design.md §1 결정 2)
>     val pointAmount: Int = 0,
>     val cardAmount: BigDecimal = BigDecimal.ZERO,
>     val pgProvider: String?,            // 기본값 "TOSS" 아님 — 실 PG 미연동을 드러내는 "MOCK_PG" 고정(design.md §1 결정 3)
>     val pgTransactionId: String?,
>     val pgApprovalNo: String?,
>     val pgApprovedAt: LocalDateTime?,
>     val status: String,                 // 기본값 PENDING 아님 — 저장 시점에 "COMPLETED"로 고정(design.md §1 결정 4) — 단 2026-10-26부터 VIRTUAL_ACCOUNT는 "WAITING_DEPOSIT"(approvedAmount/pgApprovalNo/pgApprovedAt=null)로 저장, 입금통보 전이는 미구현
>     val failedReason: String? = null,
>     val retryCount: Int = 0,
>     val createdAt: LocalDateTime,
>     val updatedAt: LocalDateTime,
>     val isDeleted: Boolean = false,
>     val deletedAt: LocalDateTime? = null,
>     val deletedBy: String? = null
> )
> ```
>
> 원안의 `orderId`/`pgToken`/`cancelledAt`/`refundedAt`과 `approve()`/`cancel()`/`refund()`/
> `partialRefund()` 행위 메서드는 이번 구현에 없다 — 전부 이번 라운드 범위 밖(취소/환불 테이블,
> 상태 전이)에 속한 필드·메서드라 가져오지 않았다. `PaymentRepository`는 `findByPlatformOrderId()`
> (결제정보 실 조회)와 `countByCreatedAtBetween()`(채번용) 2개 메서드만 가진다 — DP 패키지트리의
> `PaymentLogRepository` 등 나머지는 범위 밖이라 아직 없다. `PaymentService`는 `PaymentApi`(Port)의
> `getPaymentInfo()`/`requestPayment()` 2개 메서드만 구현하며, `MockLoader` 의존은 제거됐다(이전엔
> 고정 Mock 파일 `admin__GET_internal_payment_by_order.json`을 반환했으나 이 파일은 삭제됨).

> **(2026-10-27 복합결제·결제번호 반영)**: ① `Payment`는 결제수단별 1행이다 — `pointAmount`/`cardAmount` 필드를 제거하고 `payGroupNo`(결제 시도 번호)를 추가했다. 포인트 사용분은 `paymentMethod=POINT` 행이다. ② `PaymentApi.requestPayment(orderId, platformOrderNo, memberId, amount, method, pointAmount)` — `amount`(PG 수단 금액, 0이면 생략)와 `pointAmount`(0이면 생략)를 각각 행으로 저장하고 같은 `payGroupNo`(기존 최대+1)를 부여한다. ③ 결제번호는 `formatPaymentNo(platformOrderNo, seq)` = `Y`+주문번호 본문+행 순번(01~99, 초과 시 거부). ④ `PaymentRepository`는 `findByPlatformOrderIdOrderByIdAsc()`만 가진다(`findByPlatformOrderId`·`countByCreatedAtBetween` 제거). ⑤ `getPaymentInfo()`는 가장 최근 `payGroupNo`의 행들을 모아 복합이면 `method`를 "복합결제 (가상계좌 + 포인트)"로 합치고 PG 정보는 PG 행(없으면 첫 행)에서 가져온다. ⑥ 상태이력(`ord_status_history`)은 행별로 REQUESTED→결과를 기록한다. 호출 측: `OrderEventHandler.requestPayment`가 `order.paymentAmount`(포인트 차감 후)와 `order.pointUsedAmount`를 넘긴다.

> **(2026-10-19 구현확인/실제 구현 반영)**: 위 `paymentMethod` 필드 설명의 "ERD 3값만 허용 — 근사
> 매핑" 부분은 더 이상 유효하지 않다. `payment_method` 컬럼은 `VARCHAR(20)`라 스키마 변경 없이 Order의
> `paymentMethodType` 4종(`CARD`/`EASY_PAY`/`POINT`/`VIRTUAL_ACCOUNT`)을 그대로 저장할 수 있었고,
> ERD(`runNshop_erd_v1_0.md` §9 `pay_payment`) enum 주석도 `CARD`/`EASY_PAY`/`POINT`/`VIRTUAL_ACCOUNT`/
> `MIXED` 5값으로 넓혔다 — 1차 근거(ERD)를 실제 저장값과 일치시킨 것이다(payment-method-fidelity-fix 작업).
> `PaymentService.requestPayment()`는 `method`를 그대로 `paymentMethod`에 저장하며, `cardAmount`는
> "`POINT`가 아니면 전액"으로 판단한다(`CARD`/`EASY_PAY`/`VIRTUAL_ACCOUNT`를 구분하는 별도 금액 컬럼이
> ERD에 없어 집계 의미는 그대로 유지). `PaymentMethodLabel`도 `EASY_PAY`→"간편결제", `VIRTUAL_ACCOUNT`→
> "가상계좌", `MIXED`→"복합결제" 라벨을 추가해, 어드민 결제정보탭이 모바일 주문완료 화면과 동일한
> 결제수단 표시를 보여준다. `MIXED`는 Order가 아직 복합결제를 보내지 않아 현재 생성되지 않는다(범위 밖).

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
| 메서드 시그니처 | 인터페이스 명세(DL payment) 6개 endpoint(§12~14·§41~43), 결제 요청은 DL order §6 |
| 패키지 구조 | 컴포넌트(D9) 도메인 모듈 구조 |
| 도메인 간 계약 | 도메인정의서(DB) 경계 규칙, 이벤트 플로우(DI) |
| 엔티티 속성 | ERD(DF) Order 10테이블(v6: ord_shipment 신설, ord_claim_image 포함), Payment 5테이블(v2: pay_card_fail_counter 신설 포함) |
| 이벤트 처리 | ADR-006 Outbox 패턴 |
| PG 추상화 | ADR-005 PG 토큰화 |
| confirmByInquiry·handleDepositNotice·validateRefundAccount·PaymentStatus(CONFIRMING)·RefundAccount·RefundReason(LATE_DEPOSIT) | 시퀀스(DM payment) §4-2~4-4, REQ-PAY-029·030·031, 정책서 payment.md 4.4.2·4.5.2·8.7.1 (설계안, 2026-10-29, 미구현) |
| PgClient.inquire·cancelNetwork | 시퀀스(DM payment) §4-2·§4-5, 정책서 payment.md 4.6.2 (망취소 배치 1시간 주기·3회 재시도) |
| PaymentEventPublisher.publishPaymentRefunded·RefundService 배선 | 이벤트플로우(DI payment.md) `PAYMENT_REFUNDED` 신설(2026-11-04) — readme.md §구현 현행화(2026-11-03) Human Review 공백 해소 |
| 클레임 첨부 이미지(ClaimImage) | ERD(DF) Order `ord_claim_image`, REQ-ORD-058 (VENDOR귀책 사진 1장 이상 필수) |
| 카드 연속실패 카운터(CardFailCounter) | ERD(DF) Payment `pay_card_fail_counter`, REQ-PAY-023 (바텀업 검토 보완, 2026-08-21) |
| CS 귀책판정 override(decideResponsibility) | REQ-ORD-066 (고객 자진신고를 CS가 덮어씀), 상태머신(DH) RECEIVED→PAYMENT_PENDING/INSPECTING 전이 (바텀업 검토 보완, 2026-08-21) |
| PaymentService ↔ CardFailCounter 배선(handlePgCallback/requestPayment) | 시퀀스(DM) §4(결제 요청)·§4-1(PG콜백 처리), REQ-PAY-018/023 — 엔티티만 있고 호출부가 없던 배선 결함 수정 (2026-08-21) |
| Claim.submittedResponsibility(불변) | 시퀀스(DM) §7(클레임 신청)·§7-1(귀책판정), REQ-ORD-076 — 고객 자진신고값과 CS 확정값(responsibility) 분리 보존 (2026-08-21) |
| ClaimImage.uploadedBy | 시퀀스(DM) §7 saveImages(uploadedBy=CUSTOMER) — 첨부 이미지의 등록 주체(CUSTOMER/VENDOR) 구분 (2026-08-21) |
| 클레임 자진취소(ClaimService.cancelClaim/Claim.cancel) | 시퀀스(DM) §7-2, REQ-ORD-071/073 — RECEIVED/PAYMENT_PENDING만 허용, 이후 상태는 ClaimCancelNotAllowedException (2026-08-21) |
| ShippingController(registerTracking/reship) | 시퀀스(DM) §9·§22, REQ-ORD-062 — ShipmentService.reship()은 기존에 있었으나 호출하는 컨트롤러 배선이 문서에 없던 결함 보완 (2026-08-21) |

---

## 결제 모듈 확장 구조 (2026-10-26 — 모듈 개발만으로 PG·결제수단 추가)

> 새 PG나 결제수단이 추가돼도 **모듈(어댑터) 개발만으로 확장**되고, **Order·Claim은 영향받지 않도록** 하는 구조 설계(안)이다. 구현은 WBS [payment.md](../../S2-구조설계/WBS-상세설계/payment.md)의 SC03 코어 Bolt(SPI·레지스트리·라우터·계약 테스트 킷)부터 시작한다.

```
Order / Claim ──▶ PaymentApi (안정 계약, 수단·PG 무관)            ← 변경 금지 경계
                    └ requestPayment(ref, amount, methodCode) / requestRefund(paymentRef, amount, reason)
                      getPaymentInfo(ref) / listAvailableMethods()
Payment 도메인
  PaymentService (오케스트레이션: 금액 분할, pay_payment 저장, 상태 정규화, 이력)
   ├ PaymentMethodRegistry ── PaymentMethodModule[] (수단별 모듈: Card, VirtualAccount, EasyPay, Transfer, PointMixed …)
   │     · supports(methodCode), flowType(SYNC / ASYNC_NOTIFY / REDIRECT), validate(), refundRule(), displayMeta()
   ├ PgRouter ── pay_pg_route(method, priority, enabled, 조건) → PgGateway 선택·장애 시 대체
   ├ PgGatewayRegistry ── PgGateway[] (PG별 어댑터: Mock, Toss …)
   │     · request/approve, cancel/refund, query, verifyWebhook, capabilities(지원 수단)
   └ WebhookController ── POST /api/payment-hooks/{pgCode} → 어댑터 서명 검증 → 정규화 이벤트(멱등)
```

| 확장 대상 | 추가하는 것 | 수정하지 않는 것 |
|---|---|---|
| 새 PG | `PgGateway` 구현 모듈 1개 + `pay_pg_route` 행 | Order·Claim, `PaymentApi`, 다른 PG·수단 모듈, FE |
| 새 결제수단 | `PaymentMethodModule` 구현 모듈 1개 + 방법 카탈로그 행(라벨·순서·활성) | Order·Claim, `PaymentApi`, 다른 모듈. FE는 서버가 내려주는 `payment_methods[]`로 표시(리다이렉트형 수단만 공통 리다이렉트 처리) |

- **정규화**: 모듈 안에서 PG·수단 고유 응답을 공통 결과(`ApprovalResult`, `RefundResult`, 공통 결제상태 `PENDING/WAITING_DEPOSIT/CONFIRMING/PAID/CANCELLED/REFUNDED/PARTIAL_REFUNDED`)로 변환한다. 수단 고유 데이터는 `pay_payment`의 확장 컬럼(JSON)·`pay_payment_log`에 둔다(스키마 변경 없음).
- **영향 0 검증**: 모듈 추가 변경이 `order`·`claim` 패키지를 수정하지 않는다(리뷰 체크), 모든 모듈은 계약 테스트 킷(승인 성공/실패/타임아웃/중복, 웹훅 서명·중복, 전액·부분 환불)을 통과, Order·Claim 회귀 시나리오 통과.
- **클레임**: 클레임 환불·배송비 결제·교환 추가결제도 같은 `PaymentApi`를 사용하며 수단별 분기를 갖지 않는다.
- **현재 위반 지점(제거 대상)**: `OrderService.validatePayRequest()`의 수단 허용 목록·카드 차단, `PaymentService`의 가상계좌 분기·수단/PG 라벨 맵, FE `OrderBottomBar`의 카드 차단.

### 인증·승인 2단계와 채널·PG 확장 (2026-10-26)

> 카드 결제는 **인증**(사용자 상호작용, 채널별 — PC 웹·모바일 웹·앱 — 이며 PG마다 방식이 다름)과 **승인**(서버 간 호출, PG별 API)이 다르다. 따라서 PG 모듈은 아래 부품 묶음으로 추가하고, 클라이언트·Order·Claim은 PG를 모른 채 정규화된 계약만 쓴다.

```
결제 세션 생성(PaymentApi.initiatePayment: orderRef, amount, methodCode, channel)
   → PaymentSession { sessionId, nextAction: AuthDescriptor | NONE | WAIT_DEPOSIT, expiresAt }
AuthDescriptor { type: POPUP | REDIRECT | APP_SCHEME | SDK, url, params, returnUrl }   ← PG·채널별 어댑터가 생성
클라이언트(채널별 공통 결제창 런처) → 인증 수행 → 복귀(returnUrl/콜백) → POST /api/.../payments/{sessionId}/auth-result
PaymentService → PgApproval.approve(authResult) → 승인 결과 정규화 → 주문 측에 정규화 상태/이벤트
```

| 부품 | 단위 | 책임 |
|---|---|---|
| `PgAuthProvider` | PG × 채널(PC_WEB / MOBILE_WEB / APP) | 인증 요청 기술(`AuthDescriptor`) 생성, 인증 복귀 결과 파싱·검증 |
| `PgGateway`(승인) | PG | 승인(`approve`), 취소·환불, 조회, 망취소, 웹훅 서명 검증, 지원 수단(`capabilities`) |
| `PaymentMethodModule`(카드) | 결제수단 | 흐름 유형 `AUTH_THEN_APPROVE`(카드·간편결제·계좌이체), `ASYNC_NOTIFY`(가상계좌), `NONE`(포인트 전액)을 선언하고 위 부품을 조합 |
| 결제창 런처 | 채널(클라이언트) | `AuthDescriptor`를 채널에 맞게 실행(팝업/리다이렉트/앱 스킴/SDK)하고 복귀 처리 — PG가 늘어도 변경 없음 |

- **채널 전달**: 클라이언트가 요청 헤더(`X-Channel: PC_WEB | MOBILE_WEB | APP`)로 채널을 알리고, 라우터가 (수단, 채널, 금액, 가용성)으로 PG·인증 어댑터를 선택한다.
- **PG 추가 = 모듈 1개**: {채널별 인증 어댑터 최대 3종, 승인, 취소·환불, 조회, 웹훅} + 라우팅 행. 모든 PG 모듈은 계약 테스트 킷(채널별 `AuthDescriptor` 생성·복귀 파싱, 승인 성공/실패/타임아웃/중복, 웹훅 서명·중복, 전액·부분 환불)을 통과한다.
- **비동기 주문 흐름에 미치는 영향(설계 결정 필요)**: 인증은 사용자 앞에서 진행되므로, 현재의 "접수 → 재고차감 → PG 요청(서버 단독)"에 **인증 대기 단계**가 생긴다 — 재고 차감 성공 후 `PAYMENT_REQUESTED`가 결제 세션을 만들면 카드 등은 주문이 **인증 대기(안: `PAYMENT_AUTH_PENDING`)** 로 머물고, 클라이언트가 주문 상태를 조회해 `nextAction`이 나오면 결제창 런처로 인증을 수행한다(주문완료 화면의 진행 상태 폴링 필수). 인증 만료·이탈 시 재고 복원 보상(WBS SC10)과 연결한다. 가상계좌는 현재처럼 서버 단독으로 계좌를 발급한다.
- **Order·Claim 영향 0**: Order·Claim은 `PaymentSession.nextAction`과 정규화된 결제상태만 사용하고 PG·채널별 분기를 갖지 않는다. 클라이언트의 채널별 차이는 결제창 런처가 흡수한다.

