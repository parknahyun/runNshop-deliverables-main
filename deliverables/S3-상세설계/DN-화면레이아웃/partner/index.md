# 화면 레이아웃 — 판매자 어드민 (partner) 목차

> 상위 문서: [../readme.md](../readme.md)
> **단계**: 상세설계 (S3) | **문서범위**: Bolt (Order + Payment, partner 채널) | **문서종류**: Design
> 화면 섹션 표준 구조·유효성 검증 규칙은 [../readme.md](../readme.md) §0 참조

화면 단위로 파일을 분리했습니다. (기존 `partner.md` 단일 파일 → 화면별 분리, 2026-10-29. 섹션 번호(§)는 기존과 동일합니다.)

| § | 화면 | 화면 ID | 파일 |
|---|---|---|---|
| 13 | 주문 목록 (OrderListPage) | SCR-P-001 | [order/SCR-P-001_list.md](order/SCR-P-001_list.md) |
| 13 | 주문 상세 (컨테이너) | SCR-P-002 | [order/SCR-P-002/SCR-P-002_detail.md](order/SCR-P-002/SCR-P-002_detail.md) |
| 13 | 주문 상세 — 주문상품 탭 | SCR-P-002-T1 | [order/SCR-P-002/SCR-P-002-T1_items.md](order/SCR-P-002/SCR-P-002-T1_items.md) |
| 13 | 주문 상세 — 배송정보 탭 | SCR-P-002-T2 | [order/SCR-P-002/SCR-P-002-T2_shipping.md](order/SCR-P-002/SCR-P-002-T2_shipping.md) |
| 13 | 주문 상세 — 클레임 탭 | SCR-P-002-T3 | [order/SCR-P-002/SCR-P-002-T3_claim.md](order/SCR-P-002/SCR-P-002-T3_claim.md) |
| 13 | 주문 상세 — 변경이력 탭 | SCR-P-002-T4 | [order/SCR-P-002/SCR-P-002-T4_log.md](order/SCR-P-002/SCR-P-002-T4_log.md) |
| 13-1 | 클레임 상세 (컨테이너) | SCR-P-003 | [claim/SCR-P-003/SCR-P-003_detail.md](claim/SCR-P-003/SCR-P-003_detail.md) |
| 13-1 | 클레임 상세 — 클레임상품 탭 | SCR-P-003-T1 | [claim/SCR-P-003/SCR-P-003-T1_item.md](claim/SCR-P-003/SCR-P-003-T1_item.md) |
| 13-1 | 클레임 상세 — 배송정보 탭 | SCR-P-003-T2 | [claim/SCR-P-003/SCR-P-003-T2_shipping.md](claim/SCR-P-003/SCR-P-003-T2_shipping.md) |
| 13-1 | 클레임 상세 — 변경이력 탭 | SCR-P-003-T3 | [claim/SCR-P-003/SCR-P-003-T3_log.md](claim/SCR-P-003/SCR-P-003-T3_log.md) |
| 14 | 배송 관리 (ShippingPage) | SCR-P-004 | [order/SCR-P-004_shipping.md](order/SCR-P-004_shipping.md) |
| 15 | 클레임 현황 (ClaimStatusPage) | SCR-P-005 | [claim/SCR-P-005_claim-status.md](claim/SCR-P-005_claim-status.md) |

> 화면 ID는 [DQ-프로그램목록/order.md](../../DQ-프로그램목록/order.md) §1 화면(SCR) 표와 대응한다. 용어는 2026-10-28 확정에 따라 판매자(VENDOR)로 통일한다(2026-10-29 일괄 반영, 앱 이름 `partner`는 유지).
> 구현 소스(주문·배송): `apps/runNshop-partner/src/order/`. 클레임은 본 문서(SCR-P-003·SCR-P-005)에 대응하는 구현이 없다(아래 구현 현황 참조).

> **구현 현황 (2026-10-29)**: 본 폴더의 partner 화면 문서는 **설계안**이며, 현 프로토타입은 구버전이다. 클레임 메뉴는 통합 현황(SCR-P-005)·클레임 상세 MDI(SCR-P-003)가 아니라 취소·반품·교환 목록 3개로 분리되어 있고(`AppShell.tsx:45-47`), 상세 탭은 기본정보/처리이력 2개다(`ReturnClaimDetail.tsx:84-85`). 구현된 partner API는 주문 목록·상세 GET 2개뿐이며(`OrderController.kt:111,130`) 배송 관리는 API 없이 Mock만 쓴다. 화면별 차이는 각 문서의 "구현 현황" 인용 블록에 적었다.

