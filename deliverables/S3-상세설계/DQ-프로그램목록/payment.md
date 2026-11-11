
# 프로그램 목록 — Payment 도메인

> 상위 문서: [readme.md](readme.md)
> **단계**: 상세설계 (S3) | **문서범위**: Domain (Payment) | **문서종류**: Design

---

## 1. 화면 (SCR)

| PGM-ID | 프로그램명 | 채널 | 화면레이아웃 참조 | 세부UC 참조 | 호출 API | 비고 |
|---|---|---|---|---|---|---|
| SCR-M-012 | 결제수단 관리 | mobile | — | UC-13 | API-019, API-020, API-021 | 마이페이지 하위 |

---

## 2. API

### 2-1. 고객웹 (mobile) API

| PGM-ID | Method | Endpoint | 프로그램명 | 세부UC | 시퀀스 | 호출원 | 상태전이 |
|---|---|---|---|---|---|---|---|
| API-019 | GET | /api/mobile/v1/my/payment-methods | 결제수단 목록 | UC-13 | — | SCR-M-012 | — |
| API-020 | POST | /api/mobile/v1/my/payment-methods | 결제수단 등록 | UC-13 | — | SCR-M-012 | — |
| API-021 | DELETE | /api/mobile/v1/my/payment-methods/{methodId} | 결제수단 삭제 | UC-13 | — | SCR-M-012 | — |
| API-044 | GET | /api/mobile/v1/my/payments | 결제 이력 조회 (REQ-PAY-020, 본인 결제 건만 최신순) | UC-28(추가예정) | §25(추가예정) | — (신규 SCR 필요, 추가예정) | — |

### 2-2. 어드민 (admin) API

| PGM-ID | Method | Endpoint | 프로그램명 | 세부UC | 시퀀스 | 호출원 | 상태전이 |
|---|---|---|---|---|---|---|---|
| API-045 | GET | /api/admin/v1/payments/search | 결제 검색 (CS, REQ-PAY-021: 상태·기간·주문번호·PG거래번호 필터) | UC-29(추가예정) | §26(추가예정) | — (신규 SCR 필요, 추가예정) | — |
| API-046 | GET | /api/admin/v1/payments/{paymentId}/pg-logs | PG 거래 로그 조회 (REQ-PAY-022: 요청 이력 + 마스킹된 응답 문자열, 요청 원문 미저장) | UC-30(추가예정) | §27(추가예정) | — (신규 SCR 필요, 추가예정) | — |

---

### 2-3. 외부·내부 (PG 웹훅) API

| PGM-ID | Method | Endpoint | 프로그램명 | 세부UC | 시퀀스 | 호출원 | 상태전이 |
|---|---|---|---|---|---|---|---|
| API-059 | POST | /api/internal/v1/pg-webhooks/virtual-account/deposit (안) | 가상계좌 입금 통보 웹훅 — 입금 확인, 취소 확정 주문 입금 통보 시 LATE_DEPOSIT 자동 환불(REQ-PAY-029·030, 신규 2026-11-03 추가예정, DL §46) | UC-3 | DM payment §4-3 | PG(외부 콜백, SC18-1) | WAITING_DEPOSIT→PAID (취소 확정 주문: PAID 아님, 입금액 자동 환불) |
| API-060 | POST | /api/internal/v1/payments/mask-personal-data (안) | 결제 개인정보 마스킹 — BAT-011·012가 넘긴 주문(결제) 목록의 환불계좌·가상계좌·카드 정보를 마스킹, 멱등(REQ-ORD-085, 신규 2026-11-03 Bolt16·WBS SC40-4, 추가예정, DL §45) | — | (추가예정) | BAT-011, BAT-012 (PaymentPublicApi) | — (금액·상태·일시 유지, 삭제 없음) |

## 3. 컨슈머 (CSM)

> Order가 발행하는 이벤트를 Payment가 수신·구현하는 컨슈머. (Payment가 발행하는 이벤트를
> Order가 수신하는 컨슈머는 [order.md](order.md) §3 참조)

| PGM-ID | 프로그램명 | 트리거(이벤트) | 발행 도메인 | 수신 도메인 | 세부UC | 시퀀스 | 내부 호출 | 상태전이 |
|---|---|---|---|---|---|---|---|---|
| CSM-003 | 주문취소 PG 환불 요청 | ORDER_CANCELLED | Order | Payment | — | §21(추가예정) | PGApi.refund | PAID→REFUNDED |
| CSM-004 | 클레임 부분/전체 환불 (어드민 환불 처리 API-029 호출, CLAIM_COMPLETED 수신으로 환불하지 않음) | API-029 요청 | Order(어드민) | Payment | — | §22(추가예정) | PGApi.partialRefund | PAID→PARTIAL_REFUNDED/REFUNDED |

---

## 4. 배치 (BAT)

| PGM-ID | 프로그램명 | 트리거(스케줄) | EARS 근거 | 세부UC | 시퀀스 | 내부 호출 | 상태전이 |
|---|---|---|---|---|---|---|---|
| BAT-008 | PG 거래 조회 확정 (결제 확인 중 건, 신규 2026-11-03 추가예정) | 주기(예: 수 초~1분, 3초 무응답 건 조회) | REQ-PAY-005·029 | — | DM payment §4-2 | PgClient.inquire | CONFIRMING→PAID / PENDING(누적 실패 3회 미만, 재요청) / CANCELLED(3회 도달) |
| BAT-009 | 망취소 배치 (신규 2026-11-03 추가예정) | 매 시간 | 정책서 4.6.2 | — | DM payment §4-5 | PgClient.cancelNetwork | 망취소 대상 기록→취소 완료 (3회 재시도 후 수작업 이관) |
| BAT-010 | 환불 실패 재처리 (신규 2026-11-03 추가예정) | 1시간 간격 | 정책서 8.8.2 | — | DM payment §4-4 | PgClient.refund | 환불실패→환불요청 재시도(최대 3회 후 운영자 이관) |

> 배송·주문 관련 배치는 [order.md](order.md) §4 참조.

---

## 근거

집계·정합성 검증·전체 근거는 [readme.md](readme.md) 참조.
