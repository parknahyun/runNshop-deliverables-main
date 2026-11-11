# 러닝 커머스 플랫폼 Bounded Context 정의서 — 9. Vendor

> 상위 문서: [runNshop_bounded_context_v1_0.md](../runNshop_bounded_context_v1_0.md)
> 문서 버전: v1.0 | 상태: 초안 (Draft)

---

## 핵심 책임

> 입점사의 전체 생명주기와 계약·등급·배송사를 관리한다.

## 소유 데이터

| 엔티티 | 설명 |
|--------|------|
| `Vendor` | 입점사 (사업자정보·상태·유형) |
| `VendorContract` | 계약 (기간·수수료율·독점여부·자동갱신) |
| `VendorGrade` | 등급 (등급·산정점수·산정일·이력) |
| `VendorAccount` | 정산 계좌 (1원 송금 인증 완료 여부 포함·3회 실패 시 수동 처리) |
| `VendorDelivery` | 배송사 선택 (플랫폼 제공 2곳 중 선택) |
| `VendorPenalty` | 패널티 (사유·금액·부과일) |

## 입점사 상태 전이

```
신청 → 서류검토 → 심사중 → 계약체결 → 운영중
                        ↓
                      거절 → (재신청: 거절 후 30일 이후 가능)

운영중 → 경고 → 판매중지 → 강제퇴점
운영중 → 계약만료 → 자동갱신 or 퇴점
```

## 입점사 등급 체계

| 등급 | 명칭 | 진입 조건 |
|------|------|---------|
| 1 | 신규 (New) | 3개월 미만 또는 기준 미달 | 0% |
| 2 | 일반 (Runner) | 60점 + 월 100만원 | 0.5% |
| 3 | 우수 (Pacer) | 75점 + 월 500만원 | 1.0% |
| 4 | 프리미엄 (Elite) | 90점 + 월 2,000만원 | 1.5% |

> 최종 수수료율 = 카테고리 기본 수수료율 − 등급 감면율

## 입점사 유형 및 원천징수

| 유형 | 원천징수 |
|------|---------|
| 사업자 입점사 | 미적용 |
| 개인 셀러 | 소득 유형에 따라 관련 법령 처리 |

## 배송사 정책

- 플랫폼 제공 배송사 2개사 (API 연동 완료)
- 미선택 시 수동 운송장 등록 (API 자동화 미적용)
- 미선택 입점사 배송 관련 분쟁 귀책 입점사 귀속

## 제공 API

| API | 설명 | 호출 도메인 |
|-----|------|-----------|
| `GET /vendors/{id}/status` | 입점사 계약·운영 상태 | Catalog |
| `GET /vendors/{id}/fee-rate` | 수수료율 조회 | Settlement |
| `GET /vendors/{id}/account` | 정산 계좌 조회 | Settlement |
| `GET /vendors/{id}/delivery` | 배송사 선택 정보 | Order |

## 발행 이벤트

| 이벤트 | 수신 도메인 | 시점 |
|--------|-----------|------|
| `VendorApproved` | Notification | 심사 승인 |
| `VendorRejected` | Notification | 심사 반려 |
| `VendorGradeChanged` | Notification | 등급 변경 |
| `VendorContractExpiring` | Notification | 만료 30일·7일 전 |
| `VendorSuspended` | Catalog·Notification | 판매 중지 |
| `VendorTerminated` | Catalog·Settlement·Notification | 퇴점 |

## 수신 이벤트

| 이벤트 | 발행 도메인 | 처리 내용 |
|--------|-----------|---------|
| `OrderMetricPublished` | Order | 등급 산정 지표 누적 |

---

*Confidential | 3TOP | Bounded Context v1.0 | 2026.06.22*
