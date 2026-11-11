# 화면 레이아웃 — [SCR-A-002] admin 주문 상세 (컨테이너)

> 상위 문서: [index.md](../index.md) · [../index.md](../../index.md) · [../../readme.md](../../../readme.md)
> **단계**: 상세설계 (S3) | **문서범위**: Bolt (Order + Payment, admin 채널) | **문서종류**: Design
> 화면 섹션 표준 구조·유효성 검증 규칙은 [../../readme.md](../../../readme.md) §0 참조

---

## 11. admin — 주문 상세 (OrderDetail MDI 탭 — 컨테이너)

> 목록 화면은 [SCR-A-001_list.md](../SCR-A-001_list.md) (SCR-A-001) 참조. 이 문서는 탭을 감싸는 컨테이너(헤더+탭바)만 다루며,
> 각 탭의 상세 내용은 [SCR-A-002/](./) 하위 파일로 분리되어 있다.

### 메타블록

| 항목 | 내용 |
|---|---|
| 화면 ID | SCR-A-002 (감싸는 화면, 호출 API 없음) |
| 앱 | admin |
| 접근 권한 | CS 담당자 (권한 체크 미적용 — 프로토타입) |
| 관련 세부UC | UC-6 (예외취소), UC-14 (조회) ([DK-세부유스케이스/order.md](../../../../DK-세부유스케이스/order.md)) |
| 호출 API | — (탭별 호출 API는 각 탭 문서 참조) |

> **구현 현황 (2026-10-29)**: 6개 탭은 `GET /api/admin/v1/orders/{orderId}` 1회 응답을 나눠 쓰는 현행 구현이다. CS·클레임 탭의 [클레임 접수]/[장바구니 담아주기]/[예외 취소]는 alert 스텁(**미구현**)이고, 주문문의 탭은 **Mock**이다. 예외취소 노출 조건은 PREPARING으로 확정(2026-10-29)됐고 현행 코드(PAYMENT_COMPLETED)와 다르다 — [SCR-A-002-T4_claim.md](SCR-A-002-T4_claim.md) 참조.

### 와이어프레임 — 탭 헤더 + InnerTabs

```
┌──────────────────────────────────────────────────────────────────────┐
│ P260626-00001-00  ⦿결제완료  나이키코리아 외 1곳  152,000원  2026-06-26 09:15 │ ← 탭 헤더
├──────────────────────────────────────────────────────────────────────┤
│ [●주문상품] [결제정보] [배송정보] [CS·클레임] [주문문의] [변경이력]    │ ← InnerTabs
├──────────────────────────────────────────────────────────────────────┤
│ (활성 탭 콘텐츠 — 탭별 상세는 SCR-A-002 폴더의 탭 파일 참조)                  │
└──────────────────────────────────────────────────────────────────────┘
```

### 화면 구성

| 영역 | 데이터 소스 (API) | 표시 내용 |
|---|---|---|
| 탭 헤더 | GET /api/admin/v1/orders/{orderId} | 주문번호(platformOrderNo), 플랫폼주문 상태 뱃지(`ORDER_STATUS_LABEL` — 재고확인중/재고차감완료/재고부족/입금대기/결제완료/취소), 판매자명, 주문금액, 주문일시. **표기 규칙**: 판매자명은 대표 vendor 1곳 + 복수일 때 "대표 vendor 외 N곳"(`formatRepresentative`), 목록의 상품명은 "대표 상품 외 N건"으로 표기한다. 주문일시는 와이어프레임에도 표시한다(`OrderDetail.tsx:179-184`) |
| InnerTabs (R0) | — (FE 상태) | 탭 전환, 현재 활성 탭 |

### 탭 목록 (R0-F1 탭 전환 → R0-S1 활성 탭)

| 탭 | 화면 ID | 데이터 소스 (API) | 파일 |
|---|---|---|---|
| 주문상품 (OrderItemsTab) | SCR-A-002-T1 | GET /api/admin/v1/orders/{orderId} | [SCR-A-002-T1_items.md](SCR-A-002-T1_items.md) |
| 결제정보 (PaymentInfoTab) | SCR-A-002-T2 | GET /api/admin/v1/orders/{orderId} (`payment`) | [SCR-A-002-T2_payment.md](SCR-A-002-T2_payment.md) |
| 배송정보 (ShippingInfoTab) | SCR-A-002-T3 | GET /api/admin/v1/orders/{orderId} (`shipping`) | [SCR-A-002-T3_shipping.md](SCR-A-002-T3_shipping.md) |
| CS·클레임 (ClaimTab) | SCR-A-002-T4 | GET /api/admin/v1/orders/{orderId} (`claims`) | [SCR-A-002-T4_claim.md](SCR-A-002-T4_claim.md) |
| 주문문의 (InquiryTab) | SCR-A-002-T5 | GET /api/admin/v1/orders/{orderId} (`inquiries`, 현재 Mock) | [SCR-A-002-T5_inquiry.md](SCR-A-002-T5_inquiry.md) |
| 변경이력 (ChangeLogTab) | SCR-A-002-T6 | GET /api/admin/v1/orders/{orderId} (`history`) | [SCR-A-002-T6_log.md](SCR-A-002-T6_log.md) |

> **(2026-10-19/20 구현 확인/실제 구현 반영)**: 이 상세는 플랫폼주문(`ord_platform_order`) 1건 기준이며(`orderId`가 가리키는 PK가 `Order.id`에서 `PlatformOrder.id`로 전환됨), 복수 vendor가 포함된 경우 주문상품 탭([SCR-A-002-T1_items.md](SCR-A-002-T1_items.md), `OrderItemGroup` 패턴)과 배송정보 탭(`SCR-A-002-T3_shipping.md`, `VendorDelivery` 패턴)이 각각 vendor별 섹션으로 나뉘어 표시된다. 근거: `OrderService.kt.getAdminOrderDetail()`(`platformOrderRepository.findDetailById()`), `buildAdminVendorGroup()`/`buildAdminDeliveryMap()`, `apps/runNshop-admin/src/order/order-history/mockData.ts`의 `OrderItemGroup`/`VendorDelivery` 타입, `.agents/tasks/order-platform-order-channel-redesign/design.md` §3-2-1/§3-2-2.

> **(2026-10-26 현행화 — 주문 상세 현재 구현)**
> - **단일 API**: 6개 탭은 모두 화면 진입 시 한 번 호출한 `GET /api/admin/v1/orders/{orderId}` 응답(`payment`/`items`/`shipping`/`claims`/`inquiries`/`history` 등)을 나눠 쓴다. 탭별 별도 호출 API는 없다. 주문번호는 `platformOrder.platformOrderNo`("P"+yyMMdd+"-"+5자리+"-00")다.
> - **상태 뱃지 2종**: 탭 헤더는 플랫폼주문 상태, 주문상품·배송정보 탭의 판매자 뱃지는 vendor 주문 상태(`vendorStatus`)다. 결제 확정 흐름에서는 vendor 주문 상태가 플랫폼과 함께 `STOCK_REQUESTED`→`STOCK_DEDUCTED`→`DEPOSIT_PENDING`(또는 `STOCK_FAILED`)로 전이하며, 이를 위해 vendor 상태 라벨에도 이 4종(재고확인중/재고차감완료/재고부족/입금대기)을 추가했다(이전에는 `DEPOSIT_PENDING` 라벨이 없어 뱃지가 비어 보였음).
> - **결제정보 탭**: 상품금액/배송비/상품할인/장바구니 할인(쿠폰)/포인트/결제금액(+ 주문금액)은 DB 저장값([SCR-A-002-T2_payment.md](SCR-A-002-T2_payment.md)). **변경이력 탭**: `ord_status_history` 기반 상태전이 이력([SCR-A-002-T6_log.md](SCR-A-002-T6_log.md)) — 재고차감·PG 요청 이력(`STOCK_REQUESTED`→`STOCK_DEDUCTED`→`DEPOSIT_PENDING`, 재시도 소진 시 "재고 차감 실패(재시도 초과, 차감분 복원)")이 사유와 함께 표시된다.
> - **CS·클레임 탭 액션**: [클레임 접수]/[장바구니 담아주기]/[예외 취소] 버튼은 alert 스텁이며, [예외 취소]는 현행 코드상 상태가 `PAYMENT_COMPLETED`일 때만 노출되나, 확정 기준은 `PREPARING`이다(구현 갭, [SCR-A-002-T4_claim.md](SCR-A-002-T4_claim.md) 참조). 주문문의 탭은 Mock 데이터다.

### 화면 전환

| 트리거 | 이동 화면 (SCR-ID) |
|---|---|
| [SCR-A-001_list.md](../SCR-A-001_list.md) 목록 행 클릭 → 진입 | SCR-A-002 (이 화면, 같은 화면 내 탭 오픈) |
| CS·클레임 탭 → 클레임번호 클릭 | [SCR-A-004 (클레임상세 MDI 탭, 같은 화면 내 탭 오픈)](../../claim/SCR-A-004/SCR-A-004_detail.md) |
| 주문문의 탭 → 문의번호 클릭 | 문의 상세/답변 모달 (화면 전환 아님, [SCR-A-002-T5_inquiry.md](SCR-A-002-T5_inquiry.md) 참조) |

### 유효성 검증

> [DJ-GWT수용기준/order.md](../../../../DJ-GWT수용기준/order.md) GWT §6 CS 예외취소 Bolt · 에러코드는 DL 참조 (예외취소는 CS·클레임 탭 소관, [SCR-A-002-T4_claim.md](SCR-A-002-T4_claim.md) 참조)

### 상태별 UI

| 상태 | 화면 표현 |
|---|---|
| 로딩 중 | "불러오는 중..." 메시지 |

---

*공통 작성 규칙·채널별 패턴 요약·근거는 [../../readme.md](../../../readme.md)에 있습니다.*
