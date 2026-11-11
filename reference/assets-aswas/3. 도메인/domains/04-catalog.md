# 러닝 커머스 플랫폼 Bounded Context 정의서 — 4. Catalog

> 상위 문서: [runNshop_bounded_context_v1_0.md](../runNshop_bounded_context_v1_0.md)
> 문서 버전: v1.0 | 상태: 초안 (Draft)

---

## 핵심 책임

> 상품 정보의 전체 생명주기와 가격·재고를 관리한다.

## 소유 데이터

| 엔티티 | 설명 |
|--------|------|
| `Product` | 상품 (이름·카테고리·상태·출시일) |
| `SKU` | 옵션 (색상·사이즈·재고·상태) |
| `Category` | 카테고리 (대분류·수수료율) |
| `Brand` | 브랜드 (이름·인증여부) |
| `ProductPrice` | 가격 이력 (정가·판매가·공급가·변경시각·변경자) |
| `ProductExposure` | 노출 설정 (MD 노출순서·ai_score·노출여부) |

## 상품 상태 전이

```
DRAFT → REVIEW_REQUESTED → UNDER_REVIEW → ON_SALE
                                        ↓
                                    REJECTED → DRAFT (재심사)

ON_SALE   → SOLD_OUT  : 재고 0 자동
SOLD_OUT  → ON_SALE   : 주문취소 재고 복구 자동
SOLD_OUT  → ON_SALE   : 담당자 수동 (반품·교환 후)
ON_SALE / SOLD_OUT → DISCONTINUED : 수동
```

## 재고-상태 연동 규칙

| 이벤트 | 재고 변화 | 상태 변화 | 처리 |
|--------|---------|---------|------|
| 주문 발생 | -1 | 재고=0 → SOLD_OUT 자동 | 시스템 |
| 주문 취소 | +1 | SOLD_OUT → ON_SALE 자동 | 시스템 |
| 반품 확정 | +1 | 상태 유지 (SOLD_OUT) | 시스템(재고) + 수작업(상태) |
| 교환 확정 | ±0 | 상태 유지 | 시스템 |
| 담당자 수동 | 무관 | SOLD_OUT → ON_SALE | 담당자 |

## 도메인 경계

**Catalog가 하는 것**
- 상품 등록·수정·상태 관리
- SKU·재고·가격 관리
- 가격 변경 이력 관리
- 카테고리·브랜드 관리
- 노출 순서 관리 (MD 설정)
- 재고 존재 여부 API 제공
- 평점 캐시 보유 (Community 이벤트 수신)

**Catalog가 하지 않는 것**
- 리뷰·평점·QnA 관리 → Community
- 행사가·쿠폰·수량 할인 → Promotion
- 검색 인덱스 관리 → Search
- 심사 권한 확인 → Config

## 제공 API

| API | 설명 | 호출 도메인 |
|-----|------|-----------|
| `GET /catalog/products/{id}/stock` | 재고 존재 여부 | Order |
| `GET /catalog/products/{id}/price` | 상품 가격 조회 | Order·프론트 |
| `GET /catalog/categories/{id}/fee-rate` | 수수료율 조회 | Vendor |
| `GET /catalog/products/{id}/rating` | 평점 캐시 조회 | 프론트 |

## 발행 이벤트

| 이벤트 | 수신 도메인 | 시점 |
|--------|-----------|------|
| `StockReserveCompleted` | Order | 재고 선점 성공 |
| `StockReserveFailed` | Order | 재고 선점 실패 |
| `ProductApproved` | Notification·Search | 심사 승인 (취합 배치) |
| `ProductRejected` | Notification | 심사 반려 (취합 배치) |
| `ProductSoldOut` | Search·Notification | 품절 전환 |
| `ProductPriceChanged` | Search·Audit | 가격 변경 |
| `ProductStatusChanged` | Search·Audit | 상태 변경 |
| `ProductQnaRequested` | Community | 상품 QnA 요청 |

## 수신 이벤트

| 이벤트 | 발행 도메인 | 처리 내용 |
|--------|-----------|---------|
| `StockReserveRequested` | Order | 재고 선점 처리 |
| `StockRestoreRequested` | Order | 재고 복구 처리 |
| `RatingUpdated` | Community | 평점 캐시 업데이트 |
| `VendorSuspended` | Vendor | 입점사 상품 노출 중지 |

## Catalog 배치 목록

| 배치명 | 실행 주기 | 처리 내용 |
|--------|---------|---------| 
| DisplayPageScheduleBatch | 매 5분 | 예약 전시 페이지 자동 전환 (SCHEDULED→PUBLISHED) |
| ProductIndexSyncBatch | 매일 03:00 | ES 상품 인덱스 전체 동기화 |

## 동기 API 호출

| 호출 대상 | 목적 | 시점 |
|---------|------|------|
| Config API | MD 롤·권한 확인 | 심사 처리 시 |
| Vendor API | 입점사 계약·운영 상태 확인 | 심사 시점 |

---

*Confidential | 3TOP | Bounded Context v1.0 | 2026.06.22*
