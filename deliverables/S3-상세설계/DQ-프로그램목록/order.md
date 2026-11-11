
# 프로그램 목록 — Order 도메인

> 상위 문서: [readme.md](readme.md)
> **단계**: 상세설계 (S3) | **문서범위**: Domain (Order) | **문서종류**: Design

---

## 1. 화면 (SCR)

| PGM-ID | 프로그램명 | 채널 | 화면레이아웃 참조 | 세부UC 참조 | 호출 API | 비고 |
|---|---|---|---|---|---|---|
| SCR-M-001 | 장바구니 | mobile | §1 CartPage | UC-1, UC-2, UC-23 | API-001, API-002, API-003, API-004, API-005, API-006 | 선택상품 주문하기(CTA)가 API-006 주문서 생성(임시주문)을 호출 |
| SCR-M-002 | 주문서 | mobile | §2 OrderNewPage | UC-3, UC-4 | API-006, API-007, API-008, API-009, API-051, API-052 | 쿠폰 선택 포함 (API-008/009는 미구현, 현재는 API-052로 인라인 선택 1건 저장) |
| SCR-M-003 | 주문 접수 완료 | mobile | §3 OrderCompletePage | UC-3 | — | 결과 표시만 |
| SCR-M-004 | 주문 접수 실패 | mobile | §4 OrderFailedPage | UC-3 | — | 결과 표시만 |
| SCR-M-005 | 마이페이지 | mobile | §7 MyPage | — | API-014, API-016 | 주문/클레임 진입점 |
| SCR-M-006 | 주문/배송 조회 목록 | mobile | §8 MyOrdersPage | UC-18 | API-014 | |
| SCR-M-007 | 주문 상세 | mobile | §8-1 OrderDetailPage | UC-18 | API-015, API-010, API-011, API-012 | 취소/확정/배송지변경 |
| SCR-M-008 | 반품/교환 신청 | mobile | §8-2 ClaimRequestPage | UC-10, UC-19 | API-013, API-015 | API-015(주문 상세)로 신청 가능 수량·상품 정보 조회 |
| SCR-M-009 | 반품/교환 신청 완료 | mobile | §8-3 ClaimRequestCompletePage | UC-19 | — | 결과 표시만 |
| SCR-M-010 | 클레임 목록 | mobile | §9 MyClaimsPage | UC-16 | API-016 | |
| SCR-M-011 | 클레임 상세 | mobile | §10 ClaimDetailPage | UC-17, UC-20 | API-017, API-018, API-049 | 배송비 결제 포함, 자진취소 버튼(API-049, 추가예정) |
| SCR-A-001 | 주문 현황 (목록) | admin | §11 OrderHistory | UC-14 | API-022 | DataGrid+필터 |
| SCR-A-002 | 주문 상세 (컨테이너) | admin | §11 OrderDetail MDI탭 | UC-6, UC-14 | — | 감싸는 화면 |
| SCR-A-002-T1 | 주문 상세 — 주문상품 탭 | admin | §11 OrderItemsTab | UC-14 | API-023 | |
| SCR-A-002-T2 | 주문 상세 — 결제정보 탭 | admin | §11 PaymentInfoTab | UC-14 | API-023 | payment 섹션 |
| SCR-A-002-T3 | 주문 상세 — 배송정보 탭 | admin | §11 ShippingInfoTab | UC-14 | API-023 | shipping 섹션 |
| SCR-A-002-T4 | 주문 상세 — CS·클레임 탭 | admin | §11 ClaimTab | UC-6, UC-11 | API-023, API-024 | 예외취소 버튼 포함 |
| SCR-A-002-T5 | 주문 상세 — 주문문의 탭 | admin | §11 InquiryTab | UC-14 | API-023 | inquiries 섹션 |
| SCR-A-002-T6 | 주문 상세 — 변경이력 탭 | admin | §11 ChangeLogTab | UC-14 | API-023 | history 섹션 (응답의 `logs`는 Mock 잔재) |
| SCR-A-003 | 클레임 관리 (목록) | admin | §12 ClaimPage | UC-11 | API-025 | DataGrid+필터 |
| SCR-A-004 | 클레임 상세 (컨테이너) | admin | §12 ClaimDetail MDI탭 | UC-11, UC-22 | — | 감싸는 화면 |
| SCR-A-004-T1 | 클레임 상세 — 클레임상품 탭 | admin | §12 ClaimItemTab | UC-11, UC-22 | API-056, API-026, API-027, API-028, API-050 | 귀책판정/완료(수동)/반려/처리시작 |
| SCR-A-004-T2 | 클레임 상세 — 환불정보 탭 | admin | §12 RefundTab | UC-22 | API-056, API-029 | 환불처리 (환불정보는 API-056 refund 섹션) |
| SCR-A-004-T3 | 클레임 상세 — 배송정보 탭 | admin | §12 ShippingTab | UC-22 | API-056, API-030, API-031, API-048 | 폐기/반송결제요청/재발송 (shipments 섹션) |
| SCR-A-004-T4 | 클레임 상세 — 변경이력 탭 | admin | §12 LogTab | UC-11 | API-056 | history 섹션 |
| API-058 | POST | /api/admin/v1/orders/{orderId}/claims | 어드민 클레임 접수 (구매확정 후 하자·오배송 등 CS 대리 접수, REQ-ORD-081, 신규 2026-11-03 추가예정, DL §17-1) | UC-11 | — | SCR-A-002-T4 ([클레임 접수] 버튼, SC39-4) | — (claim.status RECEIVED 생성, 주문상품은 CONFIRMED 유지) |
| SCR-P-001 | 판매자 주문 목록 (목록) | partner | §13 OrderListPage | UC-15 | API-032 | DataGrid |
| SCR-P-002 | 판매자 주문 상세 (컨테이너) | partner | §13 OrderDetail MDI탭 | UC-7, UC-15 | — | 감싸는 화면 |
| SCR-P-002-T1 | 판매자 주문 상세 — 주문상품 탭 | partner | §13 OrderItemTab | UC-7 | API-033, API-034 | 출고처리 버튼 |
| SCR-P-002-T2 | 판매자 주문 상세 — 배송정보 탭 | partner | §13 ShippingTab | UC-7 | API-033, API-036 | 운송장 등록 |
| SCR-P-002-T3 | 판매자 주문 상세 — 클레임 탭 | partner | §13 ClaimTab | UC-12 | API-033 | 클레임 목록 |
| SCR-P-002-T4 | 판매자 주문 상세 — 변경이력 탭 | partner | §13 LogTab | UC-15 | API-033 | logs 섹션 |
| SCR-P-003 | 판매자 클레임 상세 (컨테이너) | partner | §13-1 ClaimDetail MDI탭 | UC-12, UC-21 | — | 감싸는 화면 |
| SCR-P-003-T1 | 판매자 클레임 상세 — 클레임상품 탭 | partner | §13-1 ClaimItemTab | UC-21 | API-057, API-037, API-038, API-039, API-040 | 수거확인/품질점검 |
| SCR-P-003-T2 | 판매자 클레임 상세 — 배송정보 탭 | partner | §13-1 ShippingTab | UC-21 | API-057, API-037, API-041, API-043 | 수거/반송/교환선출고 운송장 (shipments 섹션) |
| SCR-P-003-T3 | 판매자 클레임 상세 — 변경이력 탭 | partner | §13-1 LogTab | UC-21 | API-057 | history 섹션 |
| SCR-P-004 | 배송 관리 (출고+회수+재배송) | partner | §14 ShippingPage | UC-7 | API-035, API-036, API-037, API-038, API-039, API-040, API-041, API-043, API-048 | 배경색 구분. 목록은 API-035, 나머지는 모달 액션(수거·점검·반송·교환출고·재발송) |
| SCR-P-005 | 클레임 현황 | partner | §15 ClaimStatusPage | UC-12, UC-21 | API-042 | 취소/반품/교환 통합 |

---

## 2. API

### 2-1. 고객웹 (mobile) API

> **(2026-10-19 구현 확인·보완)** 아래 mobile 행 Endpoint 열은 원래 `/api/v1/...` 구버전으로 적혀 있었다(admin/partner 행은 이미 `/api/admin/v1/...`·`/api/partner/v1/...`로 올바르게 반영돼 있었음) — order-domain-api-migration 작업이 Controller/DL은 `/api/mobile/v1/my/...`로 바꿨지만 이 표는 갱신 대상에서 빠져 있던 것을 이번 작업으로 발견·정정했다(API-ID는 변경하지 않음, 순수 URL 표기 정정).

| PGM-ID | Method | Endpoint | 프로그램명 | 세부UC | 시퀀스 | 호출원 | 상태전이 |
|---|---|---|---|---|---|---|---|
| API-001 | POST | /api/mobile/v1/my/cart/items | 장바구니 담기 | UC-1 | §1 | SCR-M-001 | — |
| API-002 | GET | /api/mobile/v1/my/cart | 장바구니 조회 | UC-2 | §2 | SCR-M-001 | — |
| API-003 | PATCH | /api/mobile/v1/my/cart/items/{cartItemId}/quantity | 수량 변경 | UC-2 | — | SCR-M-001 | — |
| API-004 | DELETE | /api/mobile/v1/my/cart/items/{cartItemId} | 장바구니 삭제 | UC-2 | — | SCR-M-001 | — |
| API-005 | PUT | /api/mobile/v1/my/cart/items/{cartItemId}/option | 장바구니 옵션 변경 | UC-23 | — | SCR-M-001 | — |
| API-006 | POST | /api/mobile/v1/my/orders/sheet | 주문서 생성 | UC-3 | §3 | SCR-M-002 | — |
| API-007 | POST | /api/mobile/v1/my/orders/{orderSheetId}/pay | 결제 요청 | UC-3 | §4, §4-1 | SCR-M-002 | TEMP→STOCK_REQUESTED (이후 STOCK_DEDUCTED→DEPOSIT_PENDING은 CSM-005/006이 비동기 전이, 2026-10-26 구현 기준. 원안 PAYMENT_PENDING) |
| API-008 | GET | /api/mobile/v1/my/orders/{orderSheetId}/coupon-combinations | 쿠폰 조합별 할인 계산 | UC-3 | — | SCR-M-002 | — |
| API-009 | POST | /api/mobile/v1/my/orders/{orderSheetId}/calculate | 쿠폰 확정 재계산 | UC-3 | — | SCR-M-002 | — |
| API-051 | GET | /api/mobile/v1/my/orders/sheet/{orderSheetId} | 주문서 재조회 (임시주문, 신규 2026-10-26) | UC-3 | §3 | SCR-M-002 | — |
| API-052 | PUT | /api/mobile/v1/my/orders/sheet/{orderSheetId}/discount | 주문서 쿠폰·포인트 적용 (신규 2026-10-26) | UC-3 | §3-1 | SCR-M-002 | — (TEMP 유지) |
| API-010 | POST | /api/mobile/v1/my/orders/{orderId}/cancel | 고객 주문 취소 | UC-5 | §5 | SCR-M-007 | CANCELLED |
| API-011 | POST | /api/mobile/v1/my/orders/{orderId}/confirm | 구매확정 | UC-9 | §6 | SCR-M-007 | CONFIRMED |
| API-012 | PUT | /api/mobile/v1/my/orders/{orderId}/shipping-address | 배송지 변경 (입금대기·결제완료, 출고 지시 전) | UC-8 | — | SCR-M-007 | — |
| API-013 | POST | /api/mobile/v1/my/orders/{orderId}/claims | 반품/교환 신청 | UC-10, UC-19 | §7 | SCR-M-008 | RECEIVED (VENDOR귀책 시 사진 1장 이상 필수, REQ-ORD-058) |
| API-014 | GET | /api/mobile/v1/my/orders | 내 주문 목록 | UC-18 | — | SCR-M-005, SCR-M-006 | — |
| API-015 | GET | /api/mobile/v1/my/orders/{orderId} | 내 주문 상세 | UC-18 | — | SCR-M-007 | — |
| API-016 | GET | /api/mobile/v1/my/claims | 내 클레임 목록 | UC-16 | — | SCR-M-005, SCR-M-010 | — |
| API-017 | GET | /api/mobile/v1/my/claims/{claimId} | 내 클레임 상세 | UC-17 | — | SCR-M-011 | — |
| API-018 | POST | /api/mobile/v1/my/claims/{claimId}/shipping-payment | 클레임 배송비 결제 | UC-20 | §12 | SCR-M-011 | 수거 배송비(`PICKUP`) 결제 완료: PAYMENT_PENDING→INSPECTING + shipment(PICKUP) 생성(PENDING) (DL §31·DH v6과 동일) / 반송 배송비(`RETURN`) 결제 완료: claim.status는 RETURN_PAYMENT_PENDING 유지. 결제금액은 서버 산정(단순변심 수거 3,000~6,000원, 반송 3,000원 고정) |
| API-049 | POST | /api/mobile/v1/my/claims/{claimId}/cancel | 클레임 자진취소 (신규) | UC-32(추가예정) | §7-2 | SCR-M-011 (취소 버튼 추가예정) | RECEIVED/PAYMENT_PENDING→REJECTED |

### 2-2. 어드민 (admin) API

| PGM-ID | Method | Endpoint | 프로그램명 | 세부UC | 시퀀스 | 호출원 | 상태전이 |
|---|---|---|---|---|---|---|---|
| API-022 | GET | /api/admin/v1/orders | 주문 검색 | UC-14 | — | SCR-A-001 | — |
| API-023 | GET | /api/admin/v1/orders/{orderId} | 주문 상세 | UC-14 | — | SCR-A-002-T1~T6 | — |
| API-024 | POST | /api/admin/v1/orders/{orderId}/force-cancel | CS 예외 취소 | UC-6 | §11 | SCR-A-002-T4 | PREPARING(출고 shipment 송장 미등록)→CANCELLED, 송장 등록 후 409 |
| API-025 | GET | /api/admin/v1/claims | 클레임 목록 | UC-11 | — | SCR-A-003 | — |
| API-026 | POST | /api/admin/v1/claims/{claimId}/blame-decision | 귀책 판정 (고객/판매자) | UC-11 | — | SCR-A-004-T1 | RECEIVED→PAYMENT_PENDING(고객귀책) / RECEIVED→INSPECTING(판매자귀책, shipment(PICKUP) 자동생성 + EXCHANGE 유형 시 shipment(EXCHANGE_OUT) 병행생성, REQ-ORD-056); 고객 자진신고 responsibility를 CS가 최종 확정(덮어쓰기 가능, REQ-ORD-066) |
| API-027 | POST | /api/admin/v1/claims/{claimId}/complete | 클레임 완료 (수동, 배치 선반영) | UC-11 | §10 | SCR-A-004-T1 | REFUNDED/RETURN_PAYMENT_PENDING(shipment(RETURN) DELIVERED 확인 후)/DISPOSED→COMPLETED (배치와 동일 로직을 CS가 즉시 트리거; PICKED_UP→REFUNDED 전이 자체는 API-029에서 수행) |
| API-028 | POST | /api/admin/v1/claims/{claimId}/reject | 클레임 반려 | UC-11 | — | SCR-A-004-T1 | REJECTED |
| API-029 | POST | /api/admin/v1/claims/{claimId}/refund | 환불 처리 (수동) | UC-22 | §13 | SCR-A-004-T2 | PICKED_UP→REFUNDED |
| API-030 | POST | /api/admin/v1/claims/{claimId}/dispose | 폐기 처리 | UC-22 | — | SCR-A-004-T3 | DISPOSED |
| API-031 | POST | /api/admin/v1/claims/{claimId}/request-return-payment | 반송 배송비 추가결제 요청 | UC-22 | — | SCR-A-004-T3 | — |
| API-050 | POST | /api/admin/v1/claims/{claimId}/start | 클레임 처리 시작 (UI전용 — 인터페이스명세(DL) §19에는 있었으나 API-* ID 누락, 2026-08-24 신규 부여) | UC-11 | — | SCR-A-004-T1 ([처리 시작] 버튼, 2026-10-29 호출원 지정) | — (claim.status는 `RECEIVED` 유지, 11상태 모델에 별도 IN_PROGRESS 없음) |
| API-056 | GET | /api/admin/v1/claims/{claimId} | 클레임 상세 (어드민, 신규 2026-10-29 — 미구현. 탭별 sub-API 없이 단일 응답) | UC-11, UC-22 | — | SCR-A-004-T1~T4 | — |
| API-047 | POST | /api/admin/v1/claims/{claimId}/return-delivered | 반송 배송완료 확인 (택배사 콜백 또는 배송추적 배치 호출) | UC-22 | §19 | BAT-003 (배송상태 갱신 배치가 RETURN 유형 shipment 배송완료 확인 시 호출) | shipment(RETURN) IN_TRANSIT→DELIVERED (claim.status는 이후 배치가 RETURN_PAYMENT_PENDING→COMPLETED로 전환) |

### 2-3. 판매자 (partner) API

| PGM-ID | Method | Endpoint | 프로그램명 | 세부UC | 시퀀스 | 호출원 | 상태전이 |
|---|---|---|---|---|---|---|---|
| API-032 | GET | /api/partner/v1/orders | 판매자 주문 목록 | UC-15 | — | SCR-P-001 | — |
| API-033 | GET | /api/partner/v1/orders/{orderId} | 판매자 주문 상세 | UC-15 | — | SCR-P-002-T1~T4 | — |
| API-034 | POST | /api/partner/v1/orders/{orderId}/ship | 출고 처리 | UC-7 | §8 | SCR-P-002-T1 | PAYMENT_COMPLETED→PREPARING (REQ-ORD-022; shipment(OUTBOUND) PENDING 생성, 운송장 등록에 의한 IN_TRANSIT 전환은 API-036) |
| API-035 | GET | /api/partner/v1/shipping | 배송 관리 목록 | UC-7 | — | SCR-P-004 | — |
| API-036 | POST | /api/partner/v1/shipping/{orderId} | 출고/재배송 운송장 등록 | UC-7 | §9 | SCR-P-002-T2, SCR-P-004 | — (order.status는 PREPARING 유지) / shipment(OUTBOUND) PENDING→IN_TRANSIT |
| API-037 | POST | /api/partner/v1/shipping/{claimId}/pickup | 수거 운송장 등록 | UC-21 | — | SCR-P-003-T1, SCR-P-003-T2, SCR-P-004 | — (claim.status 변경없음, 귀책유형에 따라 PAYMENT_PENDING 또는 INSPECTING 유지) / shipment(PICKUP) PENDING→IN_TRANSIT (수거 택배 추적 시작, REQ-ORD-044) |
| API-038 | POST | /api/partner/v1/claims/{claimId}/pickup-confirm | 입고 확인 → 품질점검 시작 (판매자 액션, 배치 아님) | UC-21 | §26 | SCR-P-003-T1, SCR-P-004 | shipment(PICKUP) DELIVERED + claim INSPECTING |
| API-039 | POST | /api/partner/v1/claims/{claimId}/inspect-pass | 품질점검 합격 (판정기준: RETURN=상품상태 양호 / EXCHANGE=택(TAG) 유지, REQ-ORD-057) | UC-21 | §14 | SCR-P-003-T1, SCR-P-004 | PICKED_UP |
| API-040 | POST | /api/partner/v1/claims/{claimId}/inspect-reject | 품질점검 거부 (판정기준: RETURN=상품 훼손 / EXCHANGE=택 제거·훼손, REQ-ORD-057, 사유 필수) | UC-21 | §15 | SCR-P-003-T1, SCR-P-004 | PICKUP_REJECTED |
| API-041 | POST | /api/partner/v1/claims/{claimId}/return-ship | 반송 운송장 등록 | UC-21 | — | SCR-P-003-T2, SCR-P-004 | — (claim.status는 RETURN_PAYMENT_PENDING 유지) / shipment(RETURN) PENDING→IN_TRANSIT |
| API-042 | GET | /api/partner/v1/claims | 클레임 현황 (통합) | UC-12 | — | SCR-P-005 | — |
| API-043 | POST | /api/partner/v1/claims/{claimId}/exchange-ship | 교환상품 발송 운송장 등록 (선출고, EXCHANGE 전용) | UC-21 | §24(추가예정) | SCR-P-003-T2, SCR-P-004 | — (claim.status 변경없음) / shipment(EXCHANGE_OUT) PENDING→IN_TRANSIT (귀책판정 시점=INSPECTING 진입 시 병행 생성, REQ-ORD-056 맞교환 원칙) |
| API-057 | GET | /api/partner/v1/claims/{claimId} | 클레임 상세 (판매자, 신규 2026-10-29 — 미구현. 단일 응답) | UC-21 | — | SCR-P-003-T1~T3 | — |
| API-048 | POST | /api/partner/v1/shipping/{shipmentId}/reship | 배송 실패 재발송 처리 (신규, REQ-ORD-062) | UC-31(추가예정) | §22 | SCR-P-004, SCR-A-004-T3 | shipment(전체 유형 공통) FAILED→PENDING→(운송장 재등록 시)IN_TRANSIT / 비고: admin 클레임관리 화면에도 재발송 UI 추가 예정(DN-화면레이아웃 반영 중) — 2026-10-29 호출원에 SCR-A-004-T3 추가 |

---

## 3. 컨슈머 (CSM)

> Payment가 발행하는 이벤트를 Order가 수신·구현하는 컨슈머. (Order가 발행하는 이벤트를
> Payment가 수신하는 컨슈머는 [payment.md](payment.md) §3 참조)

| PGM-ID | 프로그램명 | 트리거(이벤트) | 발행 도메인 | 수신 도메인 | 세부UC | 시퀀스 | 내부 호출 | 상태전이 |
|---|---|---|---|---|---|---|---|---|
| CSM-001 | 결제완료 후처리 (주문확정 — 재고는 CSM-005에서 이미 차감됨) | PAYMENT_APPROVED(또는 가상계좌 입금 통보) | Payment | Order | UC-24(추가예정) | §16 | — (추가 재고 호출 없음, 2026-11-03 정정: 구 `reserveStock`은 비동기 재설계 전 "재고 선점" 모델의 잔재) | DEPOSIT_PENDING(또는 결제인증대기, 안)→PAYMENT_COMPLETED (2026-11-03 정정: 구 상태명 `PAYMENT_PENDING`은 DH v7에서 폐기됨, AC-ORD-015 근거) |
| CSM-002 | 결제실패 후처리 (재고복원·주문실패) | PAYMENT_FAILED | Payment | Order | UC-24(추가예정) | §20(추가예정) | CatalogPublicApi.restoreStock | STOCK_DEDUCTED→PAYMENT_FAILED (2026-11-03 정정: 구 상태명 `PAYMENT_PENDING`은 DH v7에서 폐기됨 — 결제요청 단계의 선행 상태는 `STOCK_DEDUCTED`다) |
| CSM-005 | 재고 차감 처리 (신규 2026-10-26, 구현) | 아웃박스 `STOCK_DEDUCT_REQUESTED` (스케줄 폴링) | Order | Order(별도 컨슈머 앱) | UC-3 | §4-1 | API-053 → CatalogApi.deductStock (SKU 단위 부분 재시도·소진 시 restoreStock) | STOCK_REQUESTED→STOCK_DEDUCTED / STOCK_FAILED |
| CSM-006 | PG 결제요청 처리 (신규 2026-10-26, 구현) | 아웃박스 `PAYMENT_REQUESTED` (CSM-005 성공 후 적재) | Order | Order(별도 컨슈머 앱) | UC-3 | §4-1 | API-053 → PaymentApi.requestPayment | STOCK_DEDUCTED→DEPOSIT_PENDING |

---

## 4. 배치 (BAT)

| PGM-ID | 프로그램명 | 트리거(스케줄) | EARS 근거 | 세부UC | 시퀀스 | 내부 호출 | 상태전이 |
|---|---|---|---|---|---|---|---|
| BAT-001 | D+11 자동구매확정 | 매일 02:00 | REQ-ORD-015 | UC-25(추가예정) | §17 | PaymentPublicApi.settle | DELIVERED→CONFIRMED (배송완료 일시 + 11×24시간. **반품·교환 진행 중인 클레임이 있는 건은 제외**, 정책서 5.6.2) |
| BAT-002 | 배송비결제 24시간 만료 | 매 시간 정각 | REQ-ORD-042 | UC-26(추가예정) | §18 | — | PAYMENT_PENDING→PAYMENT_EXPIRED |
| BAT-003 | 배송상태 갱신 (택배사 API) | 매 60분 | REQ-ORD-027 | UC-27(추가예정) | §19 | CourierApi.getTrackingStatus, API-047(반송 배송완료 확인) | shipment(OUTBOUND·RETURN·EXCHANGE_OUT) IN_TRANSIT→DELIVERED (파생: OUTBOUND→order는 PREPARING 유지 상태에서 DELIVERED로 파생 표시, RETURN→claim RETURN_PAYMENT_PENDING→COMPLETED, EXCHANGE_OUT→교환 claim PICKED_UP→COMPLETED + CLAIM_COMPLETED 발행). **PICKUP(수거)은 배치 대상이 아니다** — 입고 확인은 판매자 [입고 확인](API-038)이 수행 |
| BAT-004 | 배송비 결제 12시간 리마인드 | 매 시간 정각 | REQ-ORD-043 | UC-26(추가예정) | §23(추가예정) | NotificationPublicApi.sendAlimtalk | — (알림만) |
| BAT-005 | 임시주문 정리 (신규 2026-10-26, 계획) | 주기(예: 10분) | DH-상태머신 TEMP TTL 30분 | UC-3 | (추가예정) | 내부 API(추가예정) | TEMP→CANCELLED |
| BAT-006 | 입금기한 만료 + 재고 복원 (신규 2026-10-26, 계획) | 주기(예: 매 시간) | (EARS 추가예정) | UC-3 | (추가예정) | 내부 API → CatalogApi.restoreStock | DEPOSIT_PENDING→CANCELLED(만료) |
| BAT-007 | 처리 완료 이벤트 정리 (신규 2026-10-26, 계획) | 매일 | — | — | — | ord_outbox_event DONE 보관기간 경과 삭제 | — |
| BAT-011 | 탈퇴 회원 주문·결제 데이터 개인정보 마스킹 (신규 2026-11-03, Bolt16·WBS SC40-1, 추가예정) | 1일 1회, 익일 01:00 | REQ-ORD-085, 정책서 11.3.4 | — | (추가예정) | Member 탈퇴 상태 조회(Port 추가예정), 주문·배송(`ord_*`) 개인정보 컬럼 직접 마스킹, 결제(`pay_payment`)는 PaymentPublicApi 마스킹 요청(API-060, 도메인 경계 유지) | — (거래 이력은 유지, 수령인·연락처·주소·환불계좌·주문자명·가상계좌·카드만 마스킹) |
| BAT-012 | 보존 기간 초과 주문·결제 데이터 개인정보 마스킹 (신규 2026-11-03, Bolt16·WBS SC40-2, 추가예정) | 연 1회, 1월 1일 01:00 (주문 연도 + 6년) | REQ-ORD-085, 정책서 11.3.4 | — | (추가예정) | 주문·배송(`ord_*`) 직접 마스킹, 결제(`pay_payment`)는 PaymentPublicApi 마스킹 요청(API-060) | — (같은 대상, 삭제 없음) |
| BAT-013 | 주문 데이터 기준 부정 주문·어뷰징 탐지 (신규 2026-11-03, Bolt16·WBS SC40-3, 추가예정) | 매시 정각 | 정책서 9.4.1·9.4.2 (도입 검토, 규칙 추후 정리) | — | (추가예정) | Order 데이터(주문·클레임) 조회, 쿠폰 사용 이력은 Promotion 조회 Port(추가예정), 탐지 결과를 운영자에게 전달(이용 제한 요청은 정책서 9.4.3, Member 도메인) | — |

---

## 근거

집계·정합성 검증·전체 근거는 [readme.md](readme.md) 참조.

---

## 구현 현행화 (2026-10-26) — 내부(시스템 간) API 및 컨슈머 앱

> 외부 채널 API 목록과 별개로, 아래 내부 API와 별도 앱이 구현돼 있다(화면 없음, Gateway 외부 노출 금지 — Prefix `/api/internal/v1`).

| 구분 | 프로그램 | 설명 |
|---|---|---|
| 내부 API **API-053** | `POST /api/internal/v1/order-events/process` | 컨슈머가 호출 — 재고차감 요청/PG 요청 이벤트의 업무 처리(`OrderEventHandler.process`), 응답 `result`(STOCK_DEDUCTED/STOCK_PARTIAL/STOCK_FAILED/DEPOSIT_PENDING/SKIPPED) |
| 내부 API **API-054** | `POST /api/internal/v1/order-events/give-up` | 컨슈머가 재시도 소진 시 호출 — 차감분 복원 + 주문 `STOCK_FAILED` |
| 모바일 API (API-052) | `PUT /api/mobile/v1/my/orders/sheet/{orderSheetId}/discount` | 주문서 쿠폰/포인트 적용 영속화 (DL §5-2) |
| 모바일 API (API-051) | `GET /api/mobile/v1/my/orders/sheet/{orderSheetId}` | 임시주문 주문서 재조회 (DL §5-1) |
| 별도 앱 | `api/runNshop-consumer` (`OrderEventConsumer`) = CSM-005/006 | 아웃박스 스케줄 컨슈머(이벤트 점유·상태 관리), 다중 인스턴스 실행 가능. 배치 앱(BAT-005~007)도 동일 구조 예정 |
| 내부 API (계획) **API-055** | `POST /api/internal/v1/order-events/{eventId}/retry` | FAILED 이벤트 수동 재처리(운영용, Bolt #21) — 미구현 |
| DDL | `order-stock-outbox.sql` | `ord_outbox_event`, `cat_sku_stock`, `cat_stock_deduction` |

---

## 7. Bolt별 프로그램·기능 구현 현황 (2026-10-26 도출)

> 구조설계(S2) WBS([WBS-상세설계/order.md](../../S2-구조설계/WBS-상세설계/order.md))의 Bolt 번호 기준으로 이 도메인의 프로그램(PGM-ID)과 기능을 묶는다. 대상: 모바일 장바구니·주문서·주문 접수 완료, 어드민 주문 목록·상세, 컨슈머. 구현 상태는 `구현`(프로토타입 동작)/`미구현`. 권장 순서는 미구현 항목의 작업 순서(1~10, 아래 7-2).

### 7-1. 기능 단위 현황 (Bolt → PGM-ID → 기능)

| Bolt | 화면/영역 | PGM-ID | 기능 | 상태 | 비고 | 권장 순서 |
|---|---|---|---|---|---|---|
| #0 | 어드민 주문 목록 | SCR-A-001 / API-022 | 조회·키워드/상태/기간 필터·페이징 (DB 조회) | 구현 |  | — |
| #0 | 어드민 주문 목록 | SCR-A-001 / API-022 | 상태 필터 6종, 요약 카드 4개 | 구현 | 재고 상태는 '전체'에만 포함 | — |
| #0 | 어드민 주문 목록 | SCR-A-001 | 행 클릭 시 상세 탭 열기 | 구현 |  | — |
| #0 | 어드민 주문 목록 | SCR-A-001 | 재고 관련 상태 요약 카드·뱃지 색상 | 미구현 |  | 6 |
| #0 | 어드민 주문 목록 | SCR-A-001 | 엑셀 다운로드 | 미구현 | 현재 알림창만 표시 | 6 |
| #0 | 어드민 주문 목록 | SCR-A-001 | 화면 진입 시 자동 조회 | 미구현 |  | 6 |
| #0 | 어드민 주문 상세 | SCR-A-002 | 헤더 (주문번호·상태·판매자·금액) | 구현 |  | — |
| #0 | 어드민 주문 상세 | SCR-A-002-T1 | 주문상품 탭 (판매자별) | 구현 | vendor 상태 라벨 누락 버그 수정함 | — |
| #0 | 어드민 주문 상세 | SCR-A-002-T2 | 결제정보 탭 (상품금액·쿠폰·주문금액·포인트·결제금액) | 구현 | DB 저장값 | — |
| #0 | 어드민 주문 상세 | SCR-A-002-T2 | 결제상태(pay_payment.status) 표시 | 미구현 | 현재 주문상태 라벨 표시 | 6 |
| #0 | 어드민 주문 상세 | SCR-A-002-T2 | PG 실데이터·할인 항목 명세 툴팁 | 미구현 |  | 6 |
| #0 | 어드민 주문 상세 | SCR-A-002-T5 | 주문문의 탭 | 미구현 | Mock | 9 |
| #1 | 모바일 장바구니 | SCR-M-001 / API-002 | 장바구니 조회, 판매자별 상품 그룹 | 구현 | GET /my/cart (Mock 데이터) | — |
| #1 | 모바일 장바구니 | SCR-M-001 | 상품 체크박스(품절 선택 불가), 품절 배지·음영 | 구현 |  | — |
| #1 | 모바일 장바구니 | API-003 | 수량 +/- (PATCH 호출) | 구현 | 서버는 Mock 계산, DB 저장 없음 | — |
| #1 | 모바일 장바구니 | API-004 | 삭제 (DELETE 호출 후 목록 갱신) | 구현 | 서버는 Mock 응답, 화면 로컬 상태로 반영 | — |
| #1 | 모바일 장바구니 | SCR-M-001 | 선택 상품 기준 금액 요약·하단 버튼 | 구현 | 조건부 할인은 미반영 | — |
| #1 | 모바일 장바구니 | SCR-M-001 | 뒤로가기 버튼 | 구현 |  | — |
| #1 | 모바일 장바구니 | API-005 | 옵션 변경 (버튼·팝업) | 미구현 | 화면정의서 설계안만 존재 | 8 |
| #1 | 모바일 장바구니 | SCR-M-001 | '사용 가능 쿠폰 N장' 쿠폰 목록 팝업 | 미구현 | 현재는 안내 문구 한 줄 | 8 |
| #1 | 모바일 장바구니 | SCR-M-001 | 장바구니 할인 행사 영역·조건부 할인 반영 | 미구현 |  | 8 |
| #1 | 모바일 장바구니 | API-001~004 | 장바구니 DB 저장 (조회·수량·삭제 영속화) | 미구현 | 현재 전부 Mock 기반. Order 소유라 DB 기준 — Bolt1 SC01-3에서 전환(2026-10-29) | Bolt1 |
| #1 | 모바일 장바구니 | API-002 | 실재고 연동 (재고·품절 표시) | 미구현 | 재고 테이블은 있으나 장바구니는 Mock 재고 | 8 |
| #1 | 모바일 장바구니 | SCR-M-001 | 선택 상품 기준 배송비 재계산 | 미구현 | 현재 Mock 값 복사 | 8 |
| #2 | 모바일 장바구니 | API-006 | 선택상품 주문하기 → 임시주문 생성 후 주문서 이동 | 구현 | POST /my/orders/sheet | — |
| #2 | 모바일 주문서 | API-051 | 임시주문 저장·재조회 (새로고침 유지) | 구현 | GET /my/orders/sheet/{id} | — |
| #2 | 모바일 주문서 | SCR-M-002 / API-051 | 주문 상품 표시 (DB 저장값) | 구현 |  | — |
| #2 | 모바일 주문서 | SCR-M-002 | 금액 요약 (저장값 기준) | 구현 | 상품할인·장바구니할인은 0이라 미표시 | — |
| #2 | 모바일 주문서 | SCR-M-002 | 배송지 변경 팝업·실제 배송지 연동 | 미구현 | 현재 기본 배송지 고정 Mock | 7 |
| #2 | 모바일 주문서 | API-006 / API-052 | 상품할인·장바구니할인·배송비 계산 | 미구현 |  | 7 |
| #3 | 모바일 주문서 | SCR-M-002 / API-007 | 결제수단 선택 (가상계좌만 진행) | 구현 | 카드는 '작업중' 안내·차단 | — |
| #3 | 모바일 주문서 | SCR-M-002 | 약관 동의·약관 전문 모달 | 구현 |  | — |
| #3 | 모바일 주문서 | API-007 / SCR-M-004 | 결제하기 (서버 재검증 후 접수), 접수 실패 화면 | 구현 | 접수 후 재고차감→PG 요청은 비동기(CSM-005/006) | — |
| #3 | 모바일 주문서 | API-007 | 카드·간편결제 | 미구현 |  | 7 |
| #3 | 모바일 주문서 | SCR-M-002 / API-007 | 결제 중 로딩 표시·중복 클릭 방지·멱등키 | 미구현 |  | 7 |
| #3 | 모바일 주문 접수 완료 | SCR-M-003 | 접수 결과 표시 (주문번호·금액·결제수단·접수일시·배송지) | 구현 | sessionStorage 의존 | — |
| #3 | 모바일 주문 접수 완료 | SCR-M-003 | 안내문, 주문 상세·쇼핑 계속하기 이동 | 구현 |  | — |
| #3 | 모바일 주문 접수 완료 | SCR-M-003 / API-015 | 진행 상태 실시간 반영 (폴링) | 미구현 | 현재 고정 안내 문구 | 3 |
| #3 | 모바일 주문 접수 완료 | SCR-M-003 / API-015 | 새로고침 시 데이터 유지 | 미구현 | 주문 상세 조회 API 기반으로 전환 필요 | 3 |
| #4 | 컨슈머 | CSM-001 | 입금 통보 이벤트 처리 (→ 결제완료 전이) | 미구현 |  | 4 |
| #5 | 모바일 주문 접수 완료 | SCR-M-003 | 재고 부족 확정 시 고객 알림 (알림톡·푸시·이메일) | 미구현 |  | 3 |
| #5 | 컨슈머 | CSM-002 | PG 실패·입금기한 만료 시 재고 복원 보상 | 미구현 |  | 1 |
| #7~#10 | 어드민 주문 목록 | API-022 | 준비중·배송중·배송완료·구매확정 상태 | 미구현 | 전이 로직 없어 필터 시 항상 빈 결과 | 9 |
| #8 | 어드민 주문 상세 | SCR-A-002-T3 | 배송정보 탭 (수령인·배송지) | 구현 | 운송장 등은 비어 있음 | — |
| #8 | 어드민 주문 상세 | SCR-A-002-T3 | 운송장 등록 등 실제 배송 데이터 | 미구현 |  | 9 |
| #11~#15 | 어드민 주문 상세 | SCR-A-002-T4 / API-024 | 클레임 탭 기능 (클레임 접수·장바구니 담아주기·예외 취소) | 미구현 | 현재 알림창 스텁 | 9 |
| #16 | 모바일 주문서 | API-052 | 쿠폰 선택·해제 후 서버 저장 | 구현 | PUT .../sheet/{id}/discount, 실패 시 복원 | — |
| #16 | 모바일 주문서 | API-052 | 포인트 입력 후 서버 저장 (400ms 지연) | 구현 | 저장 중 결제하기 차단 | — |
| #16 | 모바일 주문서 | API-008 / API-009 | 쿠폰 팝업·최적 조합 자동 추천·상품/장바구니/배송비 쿠폰 | 미구현 | 현재 인라인 선택 1건 | 7 |
| #16 | 모바일 주문서 | API-052 | 쿠폰·포인트 실데이터 연동 (프로모션·회원) | 미구현 | 현재 Mock | 7 |
| #16 | 모바일 주문서 | API-052 | 포인트 최소 사용액(1,000P) 검증 | 미구현 | 문서에는 있으나 코드 미확인 | 7 |
| #17 | 컨슈머 | CSM-005 | 재고차감 요청 처리 (아웃박스 점유·다중 인스턴스·SKIP LOCKED) | 구현 | api/runNshop-consumer | — |
| #17 | 컨슈머 | CSM-005 / CSM-006 | 점유 만료(60초) 재처리, 재시도 백오프, 3회 소진 시 FAILED·포기 처리 | 구현 |  | — |
| #17 | 컨슈머 | API-053 / API-054 | 업무 처리는 API 내부 API 호출로만 수행 | 구현 | /api/internal/v1/order-events/* | — |
| #17 | 컨슈머 | CSM-005 | 영구 실패(미등록 SKU) 즉시 종결 구분 | 미구현 | 현재도 재시도 후 실패 | 2 |
| #17, #5 | 컨슈머 | CSM-005 / API-054 | SKU 단위 부분 재시도, 재시도 소진 시 차감분 복원 | 구현 |  | — |
| #18 | 모바일 주문 접수 완료 | SCR-M-003 | 가상계좌 번호·입금기한 안내 | 미구현 |  | 3 |
| #18 | 어드민 주문 상세 | API-007 / API-023 | 포인트 사용액의 pay_payment 반영 | 구현(2026-10-27) | 복합결제: 포인트 사용분을 `POINT` 행(같은 pay_group_no)으로 저장, 상세 payment 블록은 "복합결제 (가상계좌 + 포인트)"로 표기 | 1 |
| #18 | 컨슈머 | CSM-006 | 재고 차감 후 PG 결제요청 비동기 처리 | 구현 |  | — |
| #19 | 모바일 주문서 | BAT-005 | 임시주문 만료·정리 (이탈 주문서 누적) | 미구현 | 배치 앱에서 처리 | 5 |
| #19, #22, #21 | 컨슈머 | BAT-005 / BAT-006 / BAT-007 | 배치 앱 (임시주문 정리·입금기한 만료·처리 완료 이벤트 정리) | 미구현 | 컨슈머와 동일 구조 | 5 |
| #20 | 어드민 주문 상세 | SCR-A-002-T6 | 변경이력 탭 (주문·결제 상태전이, 재고차감 이력) | 구현 | ord_status_history | — |
| #21 | 컨슈머 | API-055 | FAILED 이벤트 수동 재처리·운영 알림 | 미구현 |  | 2 |
| #21 | 컨슈머 | API-053 / API-054 | 내부 API 접근 통제 (Gateway 차단·인증) | 미구현 |  | 2 |
| 횡단 | 컨슈머 | (전체) | 자동화 테스트 코드 | 미구현 | 1~5단계 병행 권장 | 10 |
| 횡단 | 컨슈머 | (전체) | 배포 구성 | 미구현 |  | 10 |

### 7-2. 미구현 항목 권장 작업 순서

| 순서 | 단계 | 대상 | 작업 내용 | 추천 이유 |
|---|---|---|---|---|
| 1 | 정합성 결함 보완 | 컨슈머·어드민 상세 | 포인트 사용액을 pay_payment에 반영, PG 실패·입금기한 만료 시 재고 복원 보상 | 재고 차감 후 PG 단계 실패 시 재고가 새고, 데이터 불일치는 나중에 고치기 어렵다 |
| 2 | 컨슈머 운영 기반 | 컨슈머 | FAILED 이벤트 수동 재처리·알림, 내부 API 접근 통제, 영구 실패 즉시 종결 구분 | 실패를 사람이 볼 수 있어야 운영이 되고, 내부 API가 열려 있으면 위험하다 |
| 3 | 주문 완료 이후 고객 경험 | 모바일 주문 접수 완료 | 상태 폴링, 가상계좌·입금기한 안내, 재고 부족 알림, 새로고침 유지 | 비동기로 바뀌어 고객이 결과를 알 방법이 없는 것이 가장 큰 사용자 영향 |
| 4 | 입금 통보·결제완료 전이 | 컨슈머·주문 | 입금 통보(Mock 가능) 수신 → PAYMENT_COMPLETED, 입금기한 만료 처리 | 주문이 입금대기에서 끝나 이후 배송·클레임 흐름의 선행 조건 |
| 5 | 배치 앱 구성 | 컨슈머(배치) | 임시주문 TTL 정리, 입금기한 만료, 처리 완료 이벤트 정리 (스케줄 + API 호출) | 4단계 만료 처리와 임시주문 누적 문제를 같은 앱에서 해결 |
| 6 | 어드민 보강 | 어드민 주문 목록·상세 | 결제상태 표시, 재고 상태 뱃지·요약 카드, 할인 명세 툴팁, PG 실데이터, 엑셀 다운로드, 자동 조회 | — |
| 7 | 주문서 기능 확장 | 모바일 주문서 | 배송지 변경(회원 연동), 쿠폰 팝업·자동 추천, 쿠폰·포인트 실데이터, 카드 결제, 중복 클릭 방지·멱등키, 할인·배송비 계산, 포인트 최소 검증 | — |
| 8 | 장바구니 영속화 | 모바일 장바구니 | 장바구니 DB 저장, 옵션 변경, 쿠폰 팝업, 할인 행사, 실재고·배송비 연동 | 변경 범위가 커서 결제 흐름이 안정된 뒤에 하는 것이 안전 → **2026-10-29 변경**: 조회·수량·삭제 DB 저장은 Order 소유이므로 Bolt1(SC01-3)로 이동, 옵션 변경·쿠폰 팝업·할인 행사·실재고·배송비 연동은 이 순서 유지 |
| 9 | 클레임·문의·배송 탭 | 어드민 주문 상세·목록 | 클레임·주문문의·운송장 기능, 배송 이후 상태(준비중~구매확정) | 배송·클레임 정책 확정 후 구현 |
| 10 | 테스트·배포 구성 | 전체 | 자동화 테스트, 배포 구성 | 최소 1~5단계는 개발과 병행해 테스트 작성 권장 |

> 기능 목록 워크시트: `weekly-report/tmp/주문화면_기능목록_작업순서.xlsx` (Bolt·PGM-ID 열 포함). 구현 진행에 따라 이 표와 WBS를 함께 갱신한다.

### 7-3. Bolt 기준 구성·작업시간 산정 (2026-10-26 현재 기준)

> Bolt는 **Bolt1~Bolt16**(작업순, [WBS order.md §0 매트릭스](../../S2-구조설계/WBS-상세설계/order.md))이며 Bolt 하나는 여러 화면·기능을 가로지르는 흐름 단위다(Bolt1 주문 신청 = 장바구니 → 주문서 → 주문완료·목록·상세 기본 흐름). Bolt별 작업 항목·상태·실적은 WBS §2가 원본이고, 이 표는 프로그램 목록 관점의 요약이다. Bolt는 9단계(1 설계 패키지 → 2 설계 확인(휴먼) → 3 설계 확인 → 4 구현 → 5 AI 점검 → 6·7 휴먼 소스확인+기능점검(반복) → 8 현행화 → 9 검토(휴먼))로 진행한다. **결제수단은 모듈별**(카드·가상계좌·간편결제·계좌이체·포인트/복합)로 처리하며 Payment 작업 항목은 [WBS payment.md](../../S2-구조설계/WBS-상세설계/payment.md)가 원본이다.

**산정 가정**: 단계별 최소 시간 AI 0.5h·휴먼 1.0h, 6·7은 같이 진행해도 휴먼 2단계(회당 2h), 반복·AI 보정 최소 2회. Bolt 휴먼 = 6h + 3h × (작업 항목 수 − 1), 연동 성격 Bolt(Bolt4·5·6·7·9·10·11·12·16) ×1.25 올림. AI = 항목별 AI 시간 합. 수식은 워크시트 '산정모델'·'Bolt1-16'.

| Bolt | 주요 기능 | 작업 항목 수 | 계획(휴먼/AI, h) | 상태 |
|---|---|---|---|---|
| Bolt1<br>주문 신청 | 장바구니(선택·수량·삭제, DB 저장) → 주문서(가상계좌 Mock, 쿠폰·포인트 저장 Port+Mock) → 주문완료·목록·상세(조회) | 9 | 30/22.5 | 부분 |
| Bolt2<br>배송기본 | 출고, 운송장 입력, 수동 확정 | 6 | 21/30 | 미착수 |
| Bolt3<br>클레임 신청 | 입금대기 취소, 신청, 귀책, 상태 전이 | 7 | 24/29 | 부분 |
| Bolt4<br>주문 가격 | 재고 판정·행사가(장바구니), 프로모션·포인트 실연동(주문서) | 8 | 34/54 | 미착수 |
| Bolt5<br>주문 결제(카드) | 카드 결제(PC웹·모바일웹·앱 인증 → PG별 승인) + 결제 공통 기반(PG 포트·Mock, 모듈 SPI·레지스트리, PG·웹훅 라우터, 세션·인증 계약, 계약 테스트 킷, Order·Claim 결제 의존 격리, 인증 대기·결제창 런처) | 12 | 49/72 | 미착수 |
| Bolt6<br>주문 결제(가상계좌·간편·이체) | 가상계좌(발급 실연동 → 입금 통보 웹훅 → 결제완료), 간편결제(리다이렉트·승인), 실시간 계좌이체 | 3 | 15/21 | 미착수 |
| Bolt7<br>주문 결제(포인트·복합·관리) | 포인트 전액·복합 결제, 결제수단 관리, 결제이력 조회·CS 결제검색·PG 로그, 어드민 결제상태·PG 표시 | 4 | 19/25 | 미착수 |
| Bolt8<br>주문 연동 | 접수 → 재고차감 → PG 요청 | 6 | 21/18 | 부분 |
| Bolt9<br>배송연동 | 택배사 연동 및 추적 API, D+11 자동 확정, 보류 | 4 | 19/22 | 미착수 |
| Bolt10<br>클레임 결제(취소) | 결제완료 취소(환불·재고·쿠폰 복원) + 수단별 환불 모듈(카드·가상계좌·간편결제·계좌이체·포인트/복합) | 8 | 34/54 | 미착수 |
| Bolt11<br>클레임 결제(반품 환불·수거) | 반품 환불 연동, 수거·반송(택배) 연동 | 4 | 19/28 | 미착수 |
| Bolt12<br>클레임 결제(교환) | 교환 SKU 재고 선점·복원 | 2 | 12/14 | 미착수 |
| Bolt13<br>주문 고도화 | 장바구니 담기·옵션 변경, 쿠폰 조합 추천·중복 방지·장애·재시도 | 9 | 30/46.5 | 미착수 |
| Bolt14<br>주문 예외 | 보상, 알림, 운영, 실패·재발송 | 11 | 36/53 | 부분 |
| Bolt15<br>배송.클레임 예외 | 배송 후 취소, 환불 실패 재처리, 품질점검, 폐기, 기한 예외 | 9 | 30/48 | 미착수 |
| Bolt16<br>매출정산 | 대사, 매출연계, 정산연계, 개인정보 마스킹·부정 주문 탐지 배치 | 8 | 34/48.5 | 미착수 |
| **합계** | | **110** | **427/585.5** | |

> 합계에는 WBS와 같이 "이번 범위 제외"로 표기한 3건(SC26-3·SC32-1·SC32-2, AI 16.5h)이 포함된다(2026-11-03 확정, WBS §1 참조).

- 일정(8h/일): 휴먼 약 51일, AI 약 70일, 병행 시 약 51~58일(휴먼 병목).
- 사용자 정의 12열 중 `주문 결제`는 Bolt5~7, `클레임 결제`는 Bolt10~12로 업무 시나리오 기준 분리했다(WBS §1, 기술 기반·환불 모듈 위치는 제안 배치).
- 범위: 모바일 마이페이지는 Member 도메인에서 관리(제외). 매트릭스에 없던 항목(기존 8개 + 누락 보완 [추가] 16개 = 24개, 판매자 화면 포함)은 제안 위치에 배치(확정 필요). 기존 8개: 입금 확인·주문완료 가상계좌 안내 → Bolt8, 결제수단 관리·결제이력 조회·어드민 결제상태 → Bolt7, 카드 제한/해제 → Bolt14, 어드민 목록·상세 고도화 → Bolt13.
- 제외: 상대 모듈 설계 확정 대기, PG 실연동·택배사 연동 일정, Notification 모듈 쪽 작업, 구현 완료 항목의 설계 패키지 역작성(1~3단계), 휴먼 일정 지연.
- 변경 이력: 시나리오 35개·Bolt 88개 구성(중간 산출, WBS 부록 B) → 사용자 정의 **Bolt 매트릭스 12열**로 재구성(작업 항목 105개). 2026-10-29: Bolt1 데이터 구현 원칙(주문·결제는 DB 기준, 타 도메인은 Mock 기본·DB 샘플 유지)에 따라 장바구니 DB 저장(SC01-3)을 Bolt1에 추가해 106개로 갱신(Bolt1 9개 30/22.5, Bolt13 SC01-1 축소 30/46.5).
