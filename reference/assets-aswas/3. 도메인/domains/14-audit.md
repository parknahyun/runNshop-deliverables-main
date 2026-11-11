# 러닝 커머스 플랫폼 Bounded Context 정의서 — 14. Audit

> 상위 문서: [runNshop_bounded_context_v1_0.md](../runNshop_bounded_context_v1_0.md)
> 문서 버전: v1.0 | 상태: 초안 (Draft)

---

## 핵심 책임

> 전 도메인의 로그·감사·Trace를 수집·보존·모니터링한다.

## 소유 데이터

| 엔티티 | 설명 |
|--------|------|
| `AuditLog` | 감사 로그 (도메인·이벤트유형·변경전후·처리주체·TraceID) |
| `TraceLog` | Trace 로그 (TraceID·SpanID·레벨·메시지·시각) |
| `OutboxEvent` | Outbox 이벤트 (상태·재시도횟수·처리시각) |
| `DLQ` | Dead Letter Queue (실패 이벤트·운영팀 처리 이력) |

## 감사 로그 수집 대상

| 도메인 | 수집 항목 |
|--------|---------|
| Order | 주문 생성·상태 변경·취소·반품·교환 |
| Payment | 결제 요청·승인·실패·환불·보상 |
| Catalog | 재고 변경·가격 변경·상품 상태 변경 |
| Member | 포인트·쿠폰 사용·복원 |
| Settlement | 정산 확정·지급·재정산 |
| 전 도메인 | 소프트 삭제 이벤트 |

## 로그 레벨

| 레벨 | 환경 | 보존 기간 |
|------|------|---------|
| ERROR·WARN·INFO | 운영 수집 | 1년 |
| DEBUG | 스테이징만 수집 | 30일 |
| Trace 전체 | 전 환경 | 1년 |

## Trace ID 구조

```
TRC-{YYYYMMDD}-{일련번호 8자리}
전파: HTTP Header X-Trace-Id
출력: [TraceID] [SpanID] [레벨] 메시지
```

## 모니터링 기준

| 항목 | 알림 조건 | 대상 |
|------|---------|------|
| ERROR 발생 | 건별 즉시 | 운영팀 |
| ERROR 임계치 | 10분 내 2회 이상 | 관리자 |
| DLQ 적재 | 건별 즉시 | 운영팀 |

---

*Confidential | 3TOP | Bounded Context v1.0 | 2026.06.22*
