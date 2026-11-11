# 러닝 커머스 플랫폼 Bounded Context 정의서 — 5. Member

> 상위 문서: [runNshop_bounded_context_v1_0.md](../runNshop_bounded_context_v1_0.md)
> 문서 버전: v1.0 | 상태: 초안 (Draft)

---

## 핵심 책임

> 고객 계정·등급·포인트·쿠폰을 관리한다.

## 소유 데이터

| 엔티티 | 설명 |
|--------|------|
| `Member` | 회원 (이름·이메일·휴대폰·등급·상태) |
| `MemberGrade` | 등급 이력 (등급·산정일·기준점수) |
| `Point` | 포인트 (잔액·적립·사용·소멸 이력) |
| `MemberCoupon` | 보유 쿠폰 (쿠폰ID·사용여부·만료일) |
| `DeviceSession` | 디바이스 세션 (최대 3개) |
| `Address` | 배송지 목록 |
| `NotificationPreference` | 수신 거부 설정 (채널별) |

## 회원 등급 체계

| 등급 | 명칭 | 진입 조건 |
|------|------|---------|
| 1 | New | 기준 미달 |
| 2 | Runner | 누적 구매 100만원 + 활동지수 10점 이상 |
| 3 | Pacer | 누적 구매 200만원 + 활동지수 20점 이상 |
| 4 | Elite | 누적 구매 300만원 + 활동지수 30점 이상 |

## 포인트 정책

| 항목 | 기준 |
|------|------|
| 등급별 적립률 | New 0.5% / Runner 1.0% / Pacer 1.5% / Elite 2.0% |
| 최대 적립 | 1건당 1,000원 |
| 적립 시점 | 구매확정 완료 후 |
| 유효기간 | 적립일로부터 3년 |
| 최소 사용 | 1,000원 이상 보유 시 |
| 최대 사용 | 결제금액 100% |
| 입점사 부담 | 30% |

## 제공 API

| API | 설명 | 호출 도메인 |
|-----|------|-----------|
| `GET /members/{id}/coupons/available/{product_id}` | 보유 쿠폰 유효성 | Order |
| `GET /members/{id}/point/balance` | 포인트 잔액 | Order |
| `GET /members/{id}/grade-discount` | 등급 할인율 | 프론트 |

## 발행 이벤트

| 이벤트 | 수신 도메인 | 시점 |
|--------|-----------|------|
| `CouponUseCompleted` | Order | 쿠폰 사용 완료 |
| `PointUseCompleted` | Order | 포인트 사용 완료 |
| `CouponRestoreCompleted` | Order | 쿠폰 복원 완료 |
| `PointRestoreCompleted` | Order | 포인트 복원 완료 |
| `GradeChanged` | Notification | 등급 변경 |
| `PointExpiringSoon` | Notification | 소멸 30일 전 |

## 수신 이벤트

| 이벤트 | 발행 도메인 | 처리 내용 |
|--------|-----------|---------|
| `CouponUseRequested` | Order | 쿠폰 사용 처리 |
| `PointUseRequested` | Order | 포인트 사용 처리 |
| `CouponRestoreRequested` | Order | 쿠폰 복원 처리 |
| `PointRestoreRequested` | Order | 포인트 복원 처리 |
| `PurchaseConfirmed` | Order | 구매확정 포인트 적립 |
| `ReviewPointGrantRequested` | Order | 리뷰 포인트 적립 |
| `ActivityCompleted` | Community | 활동지수 반영 |
| `CouponIssued` | Promotion | 발급 쿠폰 → MemberCoupon 저장 |
| `CartMergeValidationRequested` | Order | 장바구니 머지 후 재고·행사 유효성 검사 |

## Member 배치 목록

| 배치명 | 실행 주기 | 처리 내용 |
|--------|---------|---------| 
| MemberGradeBatch | 매월 1일 00:00 | 전 회원 등급 산정·쿠폰 지급 |
| YearEndGradeCouponBatch | 매년 12월 31일 | 등급별 연말 쿠폰 일괄 지급 |
| PointExpireBatch | 매일 02:00 | 소멸 30일 전 알림 이벤트 발행 |

---

*Confidential | 3TOP | Bounded Context v1.0 | 2026.06.22*
