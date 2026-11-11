# 러닝 커머스 플랫폼 Bounded Context 정의서 — 2. 도메인 구조 및 관계

> 상위 문서: [runNshop_bounded_context_v1_0.md](../runNshop_bounded_context_v1_0.md)
> 문서 버전: v1.0 | 상태: 초안 (Draft)

---

## 레이어별 구조

```
[고객 경험]
    Member ─── Catalog ─── Promotion

[거래 처리]  ← Order (오케스트레이터)
    Order ─── Payment

[혜택·정산]
    Settlement ─── Community

[파트너]
    Vendor

[운영 인프라]
    Notification · Search · Config · Audit
```

## 핵심 의존 원칙

```
Order → Catalog   : 재고 선점(PG 결제 요청 시)·복구
Order → Member    : 쿠폰·포인트 사용·복원
Order → Payment   : 결제·취소
Order → Settlement: 구매확정·재정산 (비동기)
Order → Vendor    : 주문 지표 전달 (비동기)
Order → Community : QnA 요청 (비동기)

Notification ← 전 도메인 이벤트 수신
Search       ← Catalog·Promotion·Community 인덱스
Audit        ← 전 도메인 로그 수신
Config       → 전 도메인 권한 확인 제공
```

---

*Confidential | 3TOP | Bounded Context v1.0 | 2026.06.22*
