# 화면 레이아웃 — admin 클레임 관리 (ClaimPage) 목차

> 상위 문서: [../index.md](../index.md) · [../../readme.md](../../readme.md)
> **단계**: 상세설계 (S3) | **문서범위**: Bolt (Order + Payment, admin 채널) | **문서종류**: Design

목록 화면과 상세 화면(MDI 탭)을 파일 단위로 분리했습니다. 상세 화면은 `SCR-A-004/` 폴더에 컨테이너 문서와 탭별 문서(클레임상품·환불정보·배송정보·변경이력)로 분리했습니다.

| § | 화면 | 화면 ID | 파일 |
|---|---|---|---|
| 12 | 클레임 관리 (목록) | SCR-A-003 | [SCR-A-003_list.md](SCR-A-003_list.md) |
| 12-1 | 클레임 상세 (컨테이너) | SCR-A-004 | [SCR-A-004/SCR-A-004_detail.md](SCR-A-004/SCR-A-004_detail.md) |
| 12-1 | 클레임 상세 — 클레임상품 탭 | SCR-A-004-T1 | [SCR-A-004/SCR-A-004-T1_item.md](SCR-A-004/SCR-A-004-T1_item.md) |
| 12-1 | 클레임 상세 — 환불정보 탭 | SCR-A-004-T2 | [SCR-A-004/SCR-A-004-T2_refund.md](SCR-A-004/SCR-A-004-T2_refund.md) |
| 12-1 | 클레임 상세 — 배송정보 탭 | SCR-A-004-T3 | [SCR-A-004/SCR-A-004-T3_shipping.md](SCR-A-004/SCR-A-004-T3_shipping.md) |
| 12-1 | 클레임 상세 — 변경이력 탭 | SCR-A-004-T4 | [SCR-A-004/SCR-A-004-T4_log.md](SCR-A-004/SCR-A-004-T4_log.md) |

> 화면 ID는 [DQ-프로그램목록/order.md](../../../DQ-프로그램목록/order.md) §1 화면(SCR) 표와 대응한다.
> 구현 소스: `apps/runNshop-admin/src/order/claim/`(`ClaimPage.tsx`=목록, `ClaimDetail.tsx`=상세)
