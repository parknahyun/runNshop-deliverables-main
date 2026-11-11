# 화면 레이아웃 — [SCR-P-002-T1] partner 주문 상세 · 주문상품 탭 (OrderItemTab)

> 상위 문서: [SCR-P-002_detail.md](SCR-P-002_detail.md) · [주문 목록 SCR-P-001](../SCR-P-001_list.md) · 앱 목차: [../../index.md](../../index.md) · [../../../readme.md](../../../readme.md)
> **단계**: 상세설계 (S3) | **문서범위**: Bolt (Order + Payment, partner 채널) | **문서종류**: Design

---

## 13. partner — 주문 상세 · 주문상품 탭 (OrderItemTab)

### 메타블록

| 항목 | 내용 |
|---|---|
| 화면 ID | SCR-P-002-T1 |
| 앱 | partner |
| 접근 권한 | [SCR-P-002_detail.md](SCR-P-002_detail.md) 컨테이너(SCR-P-002)를 상속 — 판매자 담당자 (자기 매장 주문만, 권한 체크 미적용 — 프로토타입) |
| 진입 조건 | [SCR-P-002_detail.md](SCR-P-002_detail.md)(SCR-P-002) InnerTabs 활성 탭 = "주문상품" |
| 관련 세부UC | [[DK-세부유스케이스/order|UC-15 (조회), UC-7 (출고처리)]] |
| 호출 API | [[DL-인터페이스명세/order|API-033, API-034]] (`GET /api/partner/v1/orders/{orderId}`, 출고 처리 API-034) |

### 와이어프레임

```
── 행 클릭 시 MDI 탭 오픈 ──────────────────────────────────────────────
┌──────────────────────────────────────────────────────────────────────┐
│ V260626-00001-01  ⦿결제완료  홍*동  152,000원                       │ ← 탭 헤더
├──────────────────────────────────────────────────────────────────────┤
│ [●주문상품] [배송정보] [클레임] [변경이력]                           │ ← InnerTabs (배송정보·클레임 탭: 프로토타입 미구현)
├──────────────────────────────────────────────────────────────────────┤
│ 주문상품 탭                                                          │
│                                                                      │
│ 상태: ⦿결제완료    주문일시: 2026.06.26 09:15                       │
│ ※ 상품명·옵션은 주문 시점 스냅샷                                    │
│                                                                      │
│ 상품명              │ 옵션       │ 주문 │클레임│완료│ 단가      │ 소계 │
│                     │            │ 수량 │진행  │    │           │      │
│─────────────────────┼────────────┼──────┼──────┼────┼───────────┼──────│
│ 나이키 페가수스 41  │ 블랙/265  │  1   │  0   │ 0  │ 152,000원 │152,000│
│                                                                      │
│                                              [출고 처리]             │ ← PAYMENT_COMPLETED만 (API-034 미연동: 프로토타입)
└──────────────────────────────────────────────────────────────────────┘
```

### 화면 구성

| 영역 | 데이터 소스 (API) | 표시 내용 |
|---|---|---|
| 주문상품 (OrderItemTab) | GET /api/partner/v1/orders/{orderId} | 상태, 주문일시, 상품 테이블(상품명*/옵션*/주문수량/클레임진행/완료/단가/소계) + [출고 처리] 버튼(PAYMENT_COMPLETED만) |

> \* 상품명·옵션명은 주문(ord_order_item)의 스냅샷 속성

> 타 판매자 상품 참조: 주문상품(OrderItemTab)에는 자기 매장 상품(`myItems`: `productName`/`optionName`/`quantity`/`unitPrice`/`subtotal`)과 구분되는 별도 섹션으로, 같은 플랫폼주문에 속한 타 vendor 상품(`otherVendorItems`)을 상품명/수량/금액 3필드만 보여준다(액션 버튼 없음, "※ 다른 판매자 상품으로 귀 매장에서는 처리하지 않습니다" 안내문 포함). 근거 이력은 문서 하단 "변경 이력" 참조.

> 주문번호 바인딩: 현재 구현의 상세 API(`GET /api/partner/v1/orders/{orderId}`)는 플랫폼 주문번호(`platformOrderNo`)를 반환한다(`OrderService.kt:672`). 목록 mock의 `platformOrderNo` 값은 `V260626-00001-01`(P/V 번호 체계의 vendor 주문번호) 형식이다. DL 목록 응답(§22)도 `platformOrderNo` 필드에 V 형식 값을 담아 본 문서의 "orderNo(vendor 주문번호)" 표기와 필드명이 다르다. [확인 필요: partner 목록·상세 응답의 주문번호 필드명(`orderNo` vs `platformOrderNo`)을 DL과 함께 확정]

### 화면 전환

| 트리거 | 이동 화면 (SCR-ID) |
|---|---|
| 주문상품 탭 → [출고 처리] | API-034 호출 (PAYMENT_COMPLETED→PREPARING, 화면 전환 아님). 프로토타입은 API 미연동 |

### 유효성 검증

> [[DJ-GWT수용기준/order|GWT §6 출고·배송 Bolt]] · 에러코드는 DL 참조

| 대상 | 규칙 | 근거 |
|---|---|---|
| [출고 처리] | PAYMENT_COMPLETED 상태에서만 가능. 그 외 409 `SHIP_NOT_ALLOWED` | DL §24 (API-034) |

### 상태별 UI

| 상태 | 화면 표현 |
|---|---|
| 출고 처리 불가 (SHIP_NOT_ALLOWED) | "결제완료 상태에서만 출고 처리할 수 있습니다" 안내, [출고 처리] 비활성 |
| 상세 로딩 중 | 탭 영역에 "불러오는 중..." 표시 ([SCR-P-002_detail.md](SCR-P-002_detail.md) 참조) |

---

### 변경 이력

- 2026-10-19/20 (구현 확인): 주문상품 탭에 "타 vendor 상품 참조" 섹션 추가 확인. 근거: `apps/runNshop-partner/src/order/order-list/OrderDetail.tsx`(`order.myItems`/`order.otherVendorItems`), `mockData.ts`의 `Order.myItems?`/`Order.otherVendorItems?`(`{productName, quantity, amount}`), `OrderService.kt.getPartnerOrderDetail()`/`OrderRepository.findSiblingOrdersWithItems()`, `.agents/tasks/order-platform-order-channel-redesign/design.md` §3-6.
- 2026-10-23 (구현 확인): 상세 응답에 vendor 주문번호 전용 필드가 없고 `platformOrderNo`만 반환됨을 확인(당시 platform 번호는 PO- 포맷, 목록 mock 값은 ORD- 포맷으로 기록). 이후 2026-10-27 주문번호 체계(P/V) 개편으로 현재 값 형식은 위 "주문번호 바인딩" 문단이 최신이다.

---

*공통 작성 규칙·채널별 패턴 요약·근거는 [../../../readme.md](../../../readme.md)에 있습니다.*
