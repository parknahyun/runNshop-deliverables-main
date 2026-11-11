# 러닝 커머스 플랫폼 Bounded Context 정의서 — 15. 도메인 간 이벤트 흐름 요약

> 상위 문서: [runNshop_bounded_context_v1_0.md](../runNshop_bounded_context_v1_0.md)
> 문서 버전: v1.0 | 상태: 초안 (Draft)

---

## 시나리오 1 — 고객 주문·결제

```
[사전 확인 - 동기]
Order → Catalog API (재고 확인)
Order → Promotion API (쿠폰 조건)
Order → Member API (잔액·보유 확인)

[비동기 처리]
Order →(StockReserveRequested)→ Catalog
Catalog →(StockReserveCompleted)→ Order
Order →(CouponUseRequested)→ Member
Order →(PointUseRequested)→ Member
Member →(CouponUseCompleted)→ Order
Member →(PointUseCompleted)→ Order
Order →(PaymentRequested)→ Payment
Payment →(PaymentCompleted)→ Order
Order →(OrderConfirmed)→ Notification
Order →(PurchaseConfirmed)→ Member·Settlement·Notification
```

## 시나리오 2 — 입점사 상품 등록·심사

```
[동기]
Catalog → Config API (MD 권한 확인)
Catalog → Vendor API (입점사 유효성)

[비동기]
Catalog →(ProductApproved)→ Notification (취합 배치)
Catalog →(ProductApproved)→ Search
Catalog →(ProductQnaRequested)→ Community
```

## 시나리오 3 — 정산 처리

```
Order →(PurchaseConfirmed)→ Settlement
Order →(ReturnCompleted)→ Settlement (재정산)
Settlement → Order API (분담금 조회)
Settlement → Vendor API (계좌 조회)
Settlement →(SettlementConfirmed)→ Notification
Settlement →(SettlementPaid)→ Notification
```

## 시나리오 4 — 클레임·반품 처리

```
Order →(ClaimReceived)→ Notification (취합 배치)
Order →(PaymentCancelRequested)→ Payment
Payment →(PaymentCancelCompleted)→ Order
Order →(PointRestoreRequested)→ Member
Order →(CouponRestoreRequested)→ Member
Order →(StockRestoreRequested)→ Catalog
Order →(ReturnCompleted)→ Settlement
```

## 전체 이벤트 목록

| 이벤트 | 발행 | 수신 |
|--------|------|------|
| StockReserveRequested | Order | Catalog |
| StockReserveCompleted/Failed | Catalog | Order |
| CouponUseRequested | Order | Member |
| PointUseRequested | Order | Member |
| CouponUseCompleted | Member | Order |
| PointUseCompleted | Member | Order |
| PaymentRequested | Order | Payment |
| PaymentCompleted/Failed | Payment | Order |
| PaymentCancelRequested | Order | Payment |
| PaymentCancelCompleted | Payment | Order |
| OrderConfirmed | Order | Notification |
| PurchaseConfirmed | Order | Member·Settlement·Notification |
| ClaimReceived | Order | Notification (취합) |
| PointRestoreRequested | Order | Member |
| CouponRestoreRequested | Order | Member |
| StockRestoreRequested | Order | Catalog |
| ReturnCompleted | Order | Settlement |
| CancelCompleted | Order | Settlement |
| ExchangeCompleted | Order | Settlement |
| OrderMetricPublished | Order | Vendor |
| ShippingDeadlineExceeded | Order | Notification |
| OrderQnaRequested | Order | Community |
| ReviewCompleted | Community | Order |
| RatingUpdated | Community | Catalog |
| ActivityCompleted | Community | Member |
| ProductQnaRequested | Catalog | Community |
| ProductApproved | Catalog | Notification·Search |
| ProductRejected | Catalog | Notification |
| ProductSoldOut | Catalog | Search·Notification |
| ProductPriceChanged | Catalog | Search·Audit |
| ProductStatusChanged | Catalog | Search·Audit |
| CouponIssued | Promotion | Member |
| EventPriceSoldOut | Promotion | Search·Notification |
| ExhibitionPublished | Promotion | Search |
| SettlementConfirmed | Settlement | Notification |
| SettlementPaid | Settlement | Notification |
| VendorApproved/Rejected | Vendor | Notification |
| VendorGradeChanged | Vendor | Notification |
| VendorContractExpiring | Vendor | Notification |
| VendorSuspended | Vendor | Catalog·Notification |
| VendorTerminated | Vendor | Catalog·Settlement·Notification |
| GradeChanged | Member | Notification |
| PointExpiringSoon | Member | Notification |

---

*Confidential | 3TOP | Bounded Context v1.0 | 2026.06.22*

---

*Confidential | 3TOP | Bounded Context v1.0 | 2026.06.22*
