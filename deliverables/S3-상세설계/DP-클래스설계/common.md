# 클래스 설계 — 도메인 간 공용 계약 (PublicApi)

> 상위 문서: [readme.md](readme.md)
> **단계**: 상세설계 (S3) | **문서범위**: Bolt (Order + Payment 공통) | **문서종류**: Design
> Order 도메인 클래스는 [order.md](order.md), Payment 도메인 클래스는 [payment.md](payment.md) 참조

> **최종 수정: 2026-10-20 (실제 구현 반영 — PublicApi 네이밍 Port/Api로 간소화)**: 아래 §5 원안은
> "본개발(미래 설계)" 기준이며 그대로 보존한다. 실제 프로토타입 구현은 패키지/인터페이스 네이밍이
> `order.publicapi.XxxPublicApi` → **`order.port.XxxApi`**로 변경됐다(SKILL.md "타 도메인 PublicApi
> 호출" 네이밍 간소화 결정, 2026-10-20). 매핑: `PaymentPublicApi`→`PaymentApi`,
> `MemberPublicApi`→`MemberApi`, `PromotionPublicApi`→`PromotionApi`. `CatalogPublicApi`는 아직
> 구현되지 않았다(재고선점은 이번 범위에서 생략, TODO). `VendorPublicApi`(→`VendorApi`)는 이 문서
> 원안에 없던 완전 신규 인터페이스로, 판매자명 조회(`getVendorName`/`getVendorNames`)를 담당한다.
> 메서드 시그니처 차이는 각 하위 섹션의 보완 각주 참조.

---

## 5. 도메인 간 PublicApi (interface)

### CatalogPublicApi (Order가 호출)

```kotlin
interface CatalogPublicApi {
    fun getProductInfo(productId: String, skuId: String): ProductInfo
    fun getProductInfoBatch(productIds: List<String>): Map<String, ProductInfo>
    fun reserveStock(items: List<StockReserveItem>): StockReservationResult
    fun restoreStock(items: List<StockRestoreItem>)
}
```

> **(2026-10-20 구현 확인)** 아직 구현되지 않았다 — 재고선점/복원은 이번 프로토타입 범위에서 생략됐다
> (`OrderService.kt`에 TODO로 명시, 설계 근거: `.agents/tasks/order-create-mobile-api/design.md` §4-2).

### PaymentPublicApi (Order가 호출)

```kotlin
interface PaymentPublicApi {
    fun requestPayment(orderId: String, amount: Int, method: String): PaymentResult
}
```

> **(2026-10-20 구현 확인)** 실제 인터페이스명은 `com.runnshop.order.port.PaymentApi`(패키지 변경:
> `order.publicapi`→`order.port`, 이름 변경: `PaymentPublicApi`→`PaymentApi`). 메서드도 `requestPayment`
> 외에 `getPaymentInfo(orderId: String): PaymentInfo`(결제정보 조회, 2026-10-15 추가)가 실제로 존재한다
> — 원안에는 없던 메서드다. 구현체: `com.runnshop.payment.service.PaymentService`(Mock, PG 연동 없음).

> **(2026-10-23 구현 확인 — `requestPayment()` 파라미터 보강, `payment-persist-mobile-order` 작업)**
> `requestPayment(orderId, amount, method)` 원안에 `memberId: String` 파라미터가 추가됐다.
> `pay_payment.member_id`(ERD NOT NULL)를 저장하려면 결제 요청 시점에 회원 식별자가 필요한데, Payment
> 도메인은 `platformOrderId`만으로 Order 도메인에 역으로 질의하지 않는다(Port는 Order→Payment
> 단방향 — Payment가 Order를 호출하면 순환 의존). 호출자(`OrderService`)가 이미 보유한 `memberId`를
> 그대로 전달하는 방식을 택했다(타입은 이 프로젝트의 Port 식별자 관례대로 `String` — `MemberApi`/
> `VendorApi`/`PromotionApi`의 모든 식별자 파라미터와 동일). 또한 `orderId`에 실제로 담기는 값이
> `platformOrder.platformOrderNo`(표시용 문자열)에서 `platformOrder.id.toString()`(PK)로 바뀌어, 같은
> Port의 `getPaymentInfo(orderId)`가 이미 쓰던 의미(PK as String)와 통일됐다 — `pay_payment.
> platform_order_id`(FK, BIGINT)를 채우려면 PK가 필요했기 때문. 이제까지 `PaymentService`는
> 고정 Mock(`admin__GET_internal_payment_by_order.json`)만 반환했으나, 이 작업으로 `pay_payment` 테이블
> (실 DB)에 결제 1건을 저장하고 조회하도록 바뀌었다(`.agents/tasks/payment-persist-mobile-order/design.md`
> §1 결정 1-6).

### MemberPublicApi (Order가 호출)

```kotlin
interface MemberPublicApi {
    fun getAddresses(memberId: String): List<AddressInfo>
    fun getPointBalance(memberId: String): PointInfo
}
```

> **(2026-10-20 구현 확인)** 실제 인터페이스명은 `com.runnshop.order.port.MemberApi`. `getAddresses`는
> 구현되지 않았다 — 배송지는 별도 `OrderAddressMock`(Order 패키지 내부 헬퍼)이 기존 주문서 Mock의
> `addresses[]`를 조회해 처리하며, Member PublicApi를 호출하지 않는다(설계 근거: design.md §0 Finding 3).
> 대신 원안에 없던 메서드 2개가 추가됐다 — `getMemberName(memberId): String?`/
> `getMemberNames(memberIds: List<String>): Map<String, String>`(고객명 조회, 단건/배치, 2026-10-20
> 추가 — 고객명은 Member 도메인 소유 데이터라는 코딩표준에 따라 Order 자체 고정 Map에서 이전됨).
> 구현체: `com.runnshop.member.service.MemberService`(Mock, 포인트 잔액은 15000 고정).

### PromotionPublicApi (Order가 호출)

```kotlin
interface PromotionPublicApi {
    fun getAvailableCoupons(memberId: String, items: List<CouponCheckItem>): CouponListInfo
}
```

> **(2026-10-20 구현 확인)** 실제 인터페이스명은 `com.runnshop.order.port.PromotionApi`. `getAvailableCoupons`
> (적용 가능 쿠폰 "목록" 조회)는 구현되지 않았다 — 대신 `validateCoupon(memberId, couponId, items):
> CouponDiscountResult`(쿠폰 1건 검증+할인액 계산, 2026-10-19 신규)가 실제로 쓰인다. 목적이 달라
> 원안 메서드를 재사용하지 않고 신규 명명했다(design-03-publicapi.md §0). 구현체:
> `com.runnshop.promotion.service.PromotionService`(Mock).

### VendorApi (Order가 호출, 완전 신규 — 원안에 없음)

> **(2026-10-20 신규)** 이 문서 원안에 전혀 없던 인터페이스다. 판매자명은 Vendor 도메인 소유
> 데이터라는 코딩표준(SKILL.md "타 도메인 PublicApi 호출")에 따라, Order가 자체 보유하던 고정 Map을
> Vendor 도메인 PublicApi 호출로 전환하며 신규 생성했다.

```kotlin
package com.runnshop.order.port

interface VendorApi {
    fun getVendorName(vendorId: String): String?
    fun getVendorNames(vendorIds: List<String>): Map<String, String>
}
```

> 구현체: `com.runnshop.vendor.service.VendorService`(Mock, vendorId 1~8 고정 매핑).

---

---

## 근거

| 항목 | 출처 |
|---|---|
| 클래스 도출 | 시퀀스(DM) 참여 객체 |
| 메서드 시그니처 | 인터페이스 명세(DL) endpoint(Order 50절·Payment 6절, 2026-10-29 기준) |
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
