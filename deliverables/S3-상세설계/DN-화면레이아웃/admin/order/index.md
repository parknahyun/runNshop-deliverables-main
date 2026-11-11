# 화면 레이아웃 — admin 주문 현황 (OrderHistory) 목차

> 상위 문서: [../index.md](../index.md) · [../../readme.md](../../readme.md)
> **단계**: 상세설계 (S3) | **문서범위**: Bolt (Order + Payment, admin 채널) | **문서종류**: Design
> 화면 섹션 표준 구조·유효성 검증 규칙은 [../../readme.md](../../readme.md) §0 참조

목록 화면과 상세 화면(MDI 탭)을 파일 단위로 분리했습니다. 상세 화면은 InnerTabs 탭마다 별도 파일로 더 분리했습니다. (2026-10-08)

| § | 화면 | 화면 ID | 파일 |
|---|---|---|---|
| 11 | 주문 현황 (목록) | SCR-A-001 | [SCR-A-001_list.md](SCR-A-001_list.md) |
| 11 | 주문 상세 (컨테이너) | SCR-A-002 | [SCR-A-002_detail.md](SCR-A-002/SCR-A-002_detail.md) |
| 11 | 주문 상세 — 주문상품 탭 | SCR-A-002-T1 | [tabs/SCR-A-002-T1_items.md](SCR-A-002/SCR-A-002-T1_items.md) |
| 11 | 주문 상세 — 결제정보 탭 | SCR-A-002-T2 | [tabs/SCR-A-002-T2_payment.md](SCR-A-002/SCR-A-002-T2_payment.md) |
| 11 | 주문 상세 — 배송정보 탭 | SCR-A-002-T3 | [tabs/SCR-A-002-T3_shipping.md](SCR-A-002/SCR-A-002-T3_shipping.md) |
| 11 | 주문 상세 — CS·클레임 탭 | SCR-A-002-T4 | [tabs/SCR-A-002-T4_claim.md](SCR-A-002/SCR-A-002-T4_claim.md) |
| 11 | 주문 상세 — 주문문의 탭 | SCR-A-002-T5 | [tabs/SCR-A-002-T5_inquiry.md](SCR-A-002/SCR-A-002-T5_inquiry.md) |
| 11 | 주문 상세 — 변경이력 탭 | SCR-A-002-T6 | [tabs/SCR-A-002-T6_log.md](SCR-A-002/SCR-A-002-T6_log.md) |

> 화면 ID·탭 구성은 [DQ-프로그램목록/order.md](../../../DQ-프로그램목록/order.md) §1 화면(SCR) 표와 1:1 대응한다.
> 구현 소스: `apps/runNshop-admin/src/order/order-history/`(`OrderHistory.tsx`=목록, `OrderDetail.tsx`=컨테이너, `tabs/*.tsx`=각 탭)

공통 작성 규칙·채널별 패턴 요약·근거는 [../../readme.md](../../readme.md)에 있습니다.
