# 화면 레이아웃 — 고객웹 (mobile) 목차

> 상위 문서: [../readme.md](../readme.md)
> **단계**: 상세설계 (S3) | **문서범위**: Bolt (Order + Payment, mobile 채널) | **문서종류**: Design
> 화면 섹션 표준 구조·유효성 검증 규칙은 [../readme.md](../readme.md) §0 참조

화면 단위로 파일을 분리했습니다. (기존 `mobile.md` 단일 파일 → 화면별 분리, 2026-10-29. 섹션 번호(§)는 기존과 동일합니다.)

| § | 화면 | 화면 ID | 파일 |
|---|---|---|---|
| 1 | 장바구니 (CartPage) | SCR-M-001 | [SCR-M-001_cart.md](order/SCR-M-001_cart.md) |
| 2 | 주문서 (OrderNewPage) | SCR-M-002 | [SCR-M-002_order-sheet.md](order/SCR-M-002_order-sheet.md) |
| 3 | 주문 접수 완료 (OrderCompletePage) | SCR-M-003 | [SCR-M-003_order-complete.md](order/SCR-M-003_order-complete.md) |
| 4 | 주문 접수 실패 (OrderFailedPage) | SCR-M-004 | [SCR-M-004_order-failed.md](order/SCR-M-004_order-failed.md) |
| 5 | 알림 문자/알림톡 (NotificationMessage) | 없음 (외부 채널 — DQ 프로그램목록에 SCR 미등록) | [notification.md](order/notification.md) |
| 6 | 주문 확인 이메일 (OrderConfirmationEmail) | 없음 (외부 채널 — DQ 프로그램목록에 SCR 미등록) | [order-email.md](order/order-email.md) |
| 7 | 마이페이지 (MyPage) | SCR-M-005 | [SCR-M-005_mypage.md](order/SCR-M-005_mypage.md) |
| 8 | 주문/배송 조회 (MyOrdersPage) | SCR-M-006 | [SCR-M-006_my-orders.md](order/SCR-M-006_my-orders.md) |
| 8-1 | 주문 상세 (OrderDetailPage) | SCR-M-007 | [SCR-M-007_order-detail.md](order/SCR-M-007_order-detail.md) |
| 8-2 | 반품/교환 신청 (ClaimRequestPage) | SCR-M-008 | [SCR-M-008_claim-request.md](claim/SCR-M-008_claim-request.md) |
| 8-3 | 반품/교환 신청 완료 (ClaimRequestCompletePage) | SCR-M-009 | [SCR-M-009_claim-request-complete.md](claim/SCR-M-009_claim-request-complete.md) |
| 8-4 | 클레임 접수 완료 알림 (ClaimReceivedNotification) | 없음 (외부 채널) | [claim-received-notification.md](claim/claim-received-notification.md) |
| 8-5 | 클레임 배송비 결제 완료 알림 (ClaimShippingPaymentNotification) | 없음 (외부 채널) | [claim-shipping-payment-notification.md](claim/claim-shipping-payment-notification.md) |
| 8-6 | 클레임 처리 완료 알림 (ClaimCompletedNotification) | 없음 (외부 채널) | [claim-completed-notification.md](claim/claim-completed-notification.md) |
| 9 | 클레임 목록 (MyClaimsPage) | SCR-M-010 | [SCR-M-010_my-claims.md](claim/SCR-M-010_my-claims.md) |
| 10 | 클레임 상세 (ClaimDetailPage) | SCR-M-011 | [SCR-M-011_claim-detail.md](claim/SCR-M-011_claim-detail.md) |

> 화면 ID는 [DQ-프로그램목록/order.md](../../DQ-프로그램목록/order.md) §1 화면(SCR) 표와 대응한다. 알림·이메일은 외부 채널이라 SCR-ID가 없다.
> 구현 소스: `apps/runNshop-mobile/app/cart`, `app/orders/*`, `app/my/*`, `components/cart/*`, `components/order/*`
