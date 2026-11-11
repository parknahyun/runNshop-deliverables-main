# 러닝 커머스 플랫폼 Bounded Context 정의서 — 3. Order

> 상위 문서: [runNshop_bounded_context_v1_0.md](../runNshop_bounded_context_v1_0.md)
> 문서 버전: v1.0 | 상태: 초안 (Draft)

---

## 핵심 책임

> 고객 주문의 전체 생명주기를 오케스트레이션한다.

## 소유 데이터

| 엔티티 | 설명 |
|--------|------|
| `Order` | 주문 헤더 (고객·주문금액·상태·클레임잠금) |
| `OrderItem` | 주문 상품 (판매가·수수료율스냅샷·분담금) |
| `OrderDiscount` | 주문 단위 할인·분담금 |
| `Delivery` | 배송 정보 (운송장·배송사·상태) |
| `Claim` | 클레임 (유형·귀책·사진·상담원·추가배송비·접수채널) |
| `OrderBatch` | 배치 실행 이력 |

## 도메인 경계

**Order가 하는 것**
- 주문 생성·상태 관리 (TEMP → PAYMENT_COMPLETED → ... → CONFIRMED)
- 환불금 계산 (상품별 공급가 비중 안분)
- 클레임 접수·잠금 관리 (claim_lock)
- 배송 처리 (운송장 등록·추적)
- 구매확정 (7일 자동·수동)
- 추가 배송비 결제 요청 (고객 귀책 클레임)
- 주문 QnA 작성 요청
- 배송지 변경 처리
  - PAYMENT_COMPLETED: 고객 직접 변경
  - PREPARING: CS(어드민) 직접 변경 + 입점사 알림
  - IN_DELIVERY 이후: 변경 불가
- 운송장 수정: IN_DELIVERY 이전만 가능 (이후 CS 협의)
- 교환 조건: 동일 상품 내 옵션 변경만 가능 (색상·사이즈)
  - 재고 없는 경우 교환 불가 → 반품 후 재구매 안내
  - 타 상품으로의 교환 불가

**Order가 하지 않는 것**
- 재고 직접 관리 → Catalog
- 결제 처리 → Payment
- 포인트·쿠폰 처리 → Member
- 알림 발송 → Notification
- 정산 계산 → Settlement

## 주문 상태 전이

```
TEMP (임시 주문, 30분 타임아웃)
    ├─ PG 인증 완료 후 재고 선점 + PG 결제 요청
    ├─ 결제 성공 → PAYMENT_COMPLETED
    ├─ 비동기 주문 생성: PROCESSING (3분 타임아웃)
    │   └─ 성공 → PAYMENT_COMPLETED 유지
    └─ 실패·타임아웃 → CANCELLED (재고·포인트·쿠폰 복원)

PAYMENT_COMPLETED → PREPARING → IN_DELIVERY → DELIVERED
    ├─ 고객 확정 or 7일 경과 → CONFIRMED
    ├─ 반품 신청 (10일 이내)
    │   → RETURN_REQUESTED → RETURNING → RETURNED
    │   └─ 수거 전 철회 → RETURN_WITHDRAWN → DELIVERED 복귀
    └─ 교환 신청 (10일 이내)
        → EXCHANGE_REQUESTED → EXCHANGING → EXCHANGED
        └─ 수거 전 철회 → EXCHANGE_WITHDRAWN → DELIVERED 복귀
```

## 취소 유형

| 유형 | 시점 | 처리 방식 |
|------|------|---------|
| 단순 취소 | PAYMENT_COMPLETED | 전액 즉시 환불·재고 자동 복구·재주문 가능 |
| 반품 | PREPARING 이후 | 실물 회수·환불금 계산·재고 수작업 |
| 예외 취소 | PREPARING 이후 | 상담원 + 입점사·물류담당자 협의 후 상태 복원 → 단순 취소 |

## 클레임 정책

- 동일 주문 동시 클레임 불가 (claim_lock)
- 클레임은 고객 직접 또는 상담원 대리 진행 가능
- 고객 귀책 배송비: 프론트 추가 결제 수납 (정산 차감 아님)
- 재고 복구: 반품·교환(기존상품)은 수작업, 단순취소만 자동

## Order 배치 목록

| 배치명 | 실행 주기 | 처리 내용 |
|--------|---------|---------|
| TempOrderTimeoutBatch | 1분마다 | TEMP 30분 초과 → CANCELLED + 보상 |
| ProcessingTimeoutBatch | 1분마다 | PROCESSING 3분 초과 → CANCELLED + 보상 |
| ShippingDeadlineBatch | 매일 09:00 | 출고 기한 초과 → Notification + Vendor 지표 |
| AutoConfirmBatch | 매일 02:00 | 배송완료 7일 경과 → 구매확정 이벤트 |
| ClaimExpireBatch | 매일 02:00 | 배송완료 10일 경과 → 클레임 불가 전환 |

## 제공 API

| API | 설명 | 호출 도메인 |
|-----|------|-----------|
| `GET /orders/{id}/discount` | 주문 분담금 조회 | Settlement |
| `GET /orders/{id}/delivery-fee` | 배송비·귀책 조회 | Settlement |

## 발행 이벤트

| 이벤트 | 수신 도메인 | 시점 |
|--------|-----------|------|
| `StockReserveRequested` | Catalog | TEMP 생성 후 |
| `CouponUseRequested` | Member | 재고 선점 완료 후 |
| `PointUseRequested` | Member | 재고 선점 완료 후 |
| `PaymentRequested` | Payment | 쿠폰·포인트 사용 완료 후 |
| `OrderConfirmed` | Notification | 결제 완료 후 |
| `PurchaseConfirmed` | Member·Settlement·Notification | 구매확정 시 (비동기) |
| `ClaimReceived` | Notification | 클레임 접수 시 (취합 배치) |
| `PaymentCancelRequested` | Payment | 클레임 취소 시 |
| `PointRestoreRequested` | Member | 결제 취소 완료 후 |
| `CouponRestoreRequested` | Member | 결제 취소 완료 후 |
| `StockRestoreRequested` | Catalog | 취소 완료 후 |
| `ReturnCompleted` | Settlement | 반품 완료 후 (비동기) |
| `ExchangeCompleted` | Settlement | 교환 완료 후 (비동기) |
| `CancelCompleted` | Settlement | 취소 완료 후 (비동기) |
| `OrderQnaRequested` | Community | 주문 QnA 작성 요청 |
| `OrderMetricPublished` | Vendor | 거래액·이행률·클레임율 지표 |
| `ShippingDeadlineExceeded` | Notification | 출고 기한 초과 |

## 수신 이벤트

| 이벤트 | 발행 도메인 | 처리 내용 |
|--------|-----------|---------|
| `StockReserveCompleted` | Catalog | 쿠폰·포인트 사용 진행 |
| `StockReserveFailed` | Catalog | CANCELLED 처리 |
| `CouponUseCompleted` | Member | 결제 진행 |
| `PointUseCompleted` | Member | 결제 진행 |
| `PaymentCompleted` | Payment | PAYMENT_COMPLETED 전환 |
| `PaymentFailed` | Payment | 보상 트랜잭션 |
| `PaymentCancelCompleted` | Payment | 포인트·쿠폰 복원 진행 |
| `ReviewCompleted` | Community | 리뷰 포인트 지급 요청 |

## 동기 API 호출

| 호출 대상 | 목적 | 시점 |
|---------|------|------|
| Catalog API | 재고 존재 여부 사전 확인 | 주문 요청 시 |
| Promotion API | 쿠폰 조건 유효성 확인 | 주문 요청 시 |
| Member API | 쿠폰 보유·포인트 잔액 확인 | 주문 요청 시 |
| Config API | 상담원 CS 롤 권한 확인 | 클레임 상담 처리 시 |
| Payment API | 추가 배송비 결제 요청 | 고객 귀책 클레임 시 |

---

*Confidential | 3TOP | Bounded Context v1.0 | 2026.06.22*
