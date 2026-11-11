# 러닝 커머스 플랫폼 Bounded Context 정의서 — 11. Community

> 상위 문서: [runNshop_bounded_context_v1_0.md](../runNshop_bounded_context_v1_0.md)
> 문서 버전: v1.0 | 상태: 초안 (Draft)

---

## 핵심 책임

> 러너 커뮤니티 활동(리뷰·QnA·크루·챌린지·러닝기록)을 관리한다.

## 소유 데이터

| 엔티티 | 설명 |
|--------|------|
| `Review` | 리뷰 (상품ID·회원ID·별점·내용·이미지·상태) |
| `Rating` | 평점 집계 (상품ID·평균별점·리뷰수) |
| `ProductQnA` | 상품 QnA (상품ID·질문·답변·공개여부) |
| `OrderQnA` | 주문 QnA (주문ID·질문·답변·상태) |
| `Crew` | 크루 (이름·소개·멤버·활동) |
| `Challenge` | 챌린지 (목표·기간·참여자·달성여부) |
| `RunningLog` | 러닝 기록 (거리·페이스·심박수·케이던스) |
| `CourseReview` | 코스 추천 (위치·거리·난이도·리뷰) |

## 활동지수 산정

| 활동 | 지수 |
|------|------|
| 리뷰 작성 | +2 |
| 러닝 기록 공유 | +1 |
| 크루 활동 참여 | +1 |
| 챌린지 완료 | +3 |
| QnA 답변 채택 | +2 |

## 제공 API

| API | 설명 | 호출 도메인 |
|-----|------|-----------|
| `GET /community/products/{id}/rating` | 상품 평점 조회 | Catalog·프론트 |
| `GET /community/products/{id}/reviews` | 리뷰 목록 | 프론트 |
| `GET /community/products/{id}/qna` | 상품 QnA | 프론트 |

## 발행 이벤트

| 이벤트 | 수신 도메인 | 시점 |
|--------|-----------|------|
| `ReviewCompleted` | Order | 리뷰 작성 완료 |
| `RatingUpdated` | Catalog | 평점 변경 |
| `ActivityCompleted` | Member | 활동 완료 |

## 수신 이벤트

| 이벤트 | 발행 도메인 | 처리 내용 |
|--------|-----------|---------|
| `ProductQnaRequested` | Catalog | 상품 QnA 등록 |
| `OrderQnaRequested` | Order | 주문 QnA 등록 |

---

*Confidential | 3TOP | Bounded Context v1.0 | 2026.06.22*
