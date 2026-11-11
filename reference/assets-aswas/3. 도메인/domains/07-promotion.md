# 러닝 커머스 플랫폼 Bounded Context 정의서 — 7. Promotion

> 상위 문서: [runNshop_bounded_context_v1_0.md](../runNshop_bounded_context_v1_0.md)
> 문서 버전: v1.0 | 상태: 초안 (Draft)

---

## 핵심 책임

> 쿠폰·행사가·수량 할인·기획전 등 혜택 정책을 정의하고 관리한다.

## 소유 데이터

| 엔티티 | 설명 |
|--------|------|
| `Coupon` | 쿠폰 (발행기준·적용조건·할인액·유효기간) |
| `EventPrice` | 행사가 (상품ID·행사가·기간·수량제한·잔여수량) |
| `QuantityDiscount` | 수량 할인 (입점사·상품목록·구간·할인율) |
| `CartDiscount` | 장바구니 할인 (금액구간·할인액) |
| `Exhibition` | 기획전 (상품목록·기간·배너) |

## 쿠폰 정책

| 항목 | 기준 |
|------|------|
| 중복 사용 | 플랫폼 쿠폰 + 입점사 쿠폰 중복 가능 |
| 동일 주체 중복 | 1장만 적용 |
| 유효기간 | 발행일 기준 최대 90일 |
| 비용 부담 | 플랫폼 쿠폰: 플랫폼 / 입점사 쿠폰: 입점사 / 공동: 계약 비율 |

## 수량 할인 적용 조건

- MD가 수량 할인 행사로 설정한 상품
- 동일 입점사 (`vendor_id` 동일)
- 동일 판매가 (`price_sale` 동일)
- 3가지 모두 충족 시에만 적용

## 행사가 수량 관리

```
Redis DECR event:quantity:{event_id}  ← 주문 시 차감
Redis INCR event:quantity:{event_id}  ← 취소 시 복구 (행사 기간 내)
```

## 제공 API

| API | 설명 | 호출 도메인 |
|-----|------|-----------|
| `GET /promotions/coupons/validate/{coupon_id}` | 쿠폰 조건 유효성 | Order |
| `GET /promotions/price/{product_id}` | 행사가 조회 | 프론트·Order |
| `GET /promotions/coupons/public` | 전체 대상 쿠폰 | 프론트 |
| `GET /promotions/coupons/available/{product_id}` | 상품별 적용 가능 쿠폰 | 프론트 |
| `GET /promotions/quantity-discount/{vendor_id}` | 수량 할인 그룹 조회 | 프론트·Order |
| `GET /promotions/cart-discount` | 장바구니 할인 조건 | 프론트 |

## 발행 이벤트

| 이벤트 | 수신 도메인 | 시점 |
|--------|-----------|------|
| `CouponIssued` | Member | 쿠폰 발급 시 |
| `EventPriceSoldOut` | Search·Notification | 행사 수량 소진 |
| `EventPriceEnded` | Search | 행사 종료 |
| `ExhibitionPublished` | Search | 기획전 게시 |

---

*Confidential | 3TOP | Bounded Context v1.0 | 2026.06.22*
