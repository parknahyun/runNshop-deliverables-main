# Community 도메인 기능표

> 핵심 책임: 러너 커뮤니티 활동(리뷰·QnA·크루·챌린지·러닝기록)을 관리하고, 신고·이력·통계까지
> 포함한다.

> **진행 상태 전제(2026-07-28)**: 고객화면(mobile)·배치·컨슈머(비동기 처리)는 아직 미착수,
> admin·partner도 초안 작업 상태 — 아래 N/A·스텁·dead code 발견은 결함이 아니라 진행 전 상태.
> 상세는 `README.md`의 "현재 진행 상태 안내" 절 참고.

**API 호출 개수 카운트 기준**: 화면/탭 로드 1개 = API 1개, 실제 제출 버튼 1개 = API 1개(취소·
편집토글처럼 API를 호출하지 않는 UI 전용 버튼은 제외). 화면 자체가 없는 기능은 "N/A"로 표기
(추정치를 억지로 만들지 않음). Community 특이사항: admin의 QnA 상세 모달 1개가 "상품 QnA
답변"·"QnA 활동점수 지급"·"QnA 관리(admin)" 3개 소분류의 버튼을 동시에 담고 있어, 화면 로드는
중복 없이 한 행(QnA 관리(admin))에만 산정하고 나머지 행은 버튼(=API 엔드포인트)만 별도 산정했다
(행별 버튼 합 8개 = 실제 코드상 버튼 8개, 화면 합 6개 = 실제 화면 6개로 상호 검증됨).

**채널 범례**: A = admin(리뷰/QnA 관리, 모더레이션), P = partner(QnA 답변),
M = mobile(고객 리뷰 작성, QnA 작성), B = batch(스케줄러), C = consumer(평점 집계 이벤트 발행)

| 대분류 | 중분류 | 소분류(기능) | 채널(A/P/M/B/C) | 상태전이 | 트리거 | 화면/탭 | 버튼 | API 호출 개수 | 비고 | 정책참조 |
|---|---|---|---|---|---|---|---|---|---|---|
| 리뷰관리 | — | 리뷰 작성(고객) | M | —→ACTIVE | 사용자 | N/A | N/A | N/A | 정의는 있으나 mobile 코드엔 화면 없음(ProductTabs.tsx엔 "별도 화면(CUS-070)에서 구현됩니다" 안내 텍스트만 존재) | `runNshop_policy_v1_2.md` 15장 |
| 리뷰관리 | — | 리뷰 관리(admin) | A | ACTIVE→HIDDEN(관리자 숨김), ACTIVE→DELETED(작성자 삭제) | 사용자 | 목록+상세(기본정보)=2 | 숨김확정,활성화=2 | 4 | 숨김(사유 필수)/활성화 — 삭제 상태는 복원 불가(terminal). "숨김" 버튼 자체는 사유입력폼을 여는 UI 전용 토글이라 제외, "숨김 확정"만 산정 | `runNshop_policy_v1_2.md` 15장 |
| 리뷰관리 | — | 평점 집계 이벤트 발행(컨슈머) | C | — | 이벤트 | N/A | N/A | N/A | 리뷰 작성/수정/삭제 시 Catalog에 평점 갱신 이벤트 발행. Community 소유의 별도 화면 없음 — 평균평점은 Catalog 쪽 화면(admin `product-list/tabs/ReviewsTab.tsx`, mobile `ReviewSummary.tsx`)에서 클라이언트 계산으로 표시되는 읽기전용 값 | `runNshop_policy_v1_2.md` 15장 |
| 리뷰관리 | — | 리뷰 신고(고객) | M | — | 사용자 | N/A | N/A | N/A | 신고사유 입력 후 리뷰 신고 접수 — 현재 "리뷰 관리(admin)"는 관리자 능동 숨김/활성화뿐, 사용자 신고 트리거 자체가 코드·정책 어디에도 없음. 신규 공백 | — |
| 리뷰관리 | — | 리뷰 신고 처리(운영자) | A | — | 사용자 | N/A | N/A | N/A | 신고 목록 조회 후 처리(숨김/기각) — `Review` 타입에 신고사유·신고자 필드 없음. 신규 공백 | — |
| 리뷰관리 | — | 리뷰 신고 결과 확인(입점사) | P | — | 사용자 | N/A | N/A | N/A | 자사 상품 리뷰의 신고 처리 결과 확인. 신규 공백 | — |
| 리뷰관리 | — | 리뷰 베스트 선정(운영자) | A | — | 사용자 | N/A | N/A | N/A | 우수 리뷰 선정·노출 — `Review` 타입에 `isBest`/추천 관련 필드 없음. 신규 공백 | — |
| 리뷰관리 | — | 리뷰 답변(입점사) | P | — | 사용자 | N/A | N/A | N/A | 벤더가 자사 상품 리뷰에 답글 작성 — QnA는 벤더 답변(`answeredByType: VENDOR`)이 코드로 존재하나 리뷰엔 대칭 기능 없음(`partner/community`엔 qna 폴더만 존재). 신규 공백 | — |
| QnA관리 | — | 질문 작성(고객) | M | —→WAITING | 사용자 | N/A | N/A | N/A | 정의는 있으나 mobile 코드엔 화면 없음(ProductTabs.tsx엔 "별도 화면(CUS-071)에서 구현됩니다" 안내 텍스트만 존재) | `runNshop_policy_v1_2.md` 15장 |
| QnA관리 | — | 상품 QnA 답변(벤더/admin) | A+P | WAITING→ANSWERED | 사용자 | partner 목록+상세=2 (admin 목록+상세는 "QnA 관리(admin)" 행에서 산정) | 답변등록/수정(admin)+답변등록/수정(partner)=2 | 4 | partner·admin 둘 다 답변등록/수정 가능 | `runNshop_policy_v1_2.md` 15장 |
| QnA관리 | — | QnA 활동점수 지급 | A+P | — | 사용자 | 0 (admin·partner 모두 위 QnA 상세 모달과 완전히 공유 — 별도 화면 없음) | 활동지수지급(admin)+활동지수지급(partner)=2 | 2 | 답변 완료 후 1회성 지급(gamification), admin·partner 둘 다 존재. partner는 window.confirm 후 지급 | `runNshop_policy_v1_2.md` 15장 |
| QnA관리 | — | QnA 관리(admin) | A | ACTIVE→HIDDEN(숨김), HIDDEN→ACTIVE(활성화) | 사용자 | 목록+상세=2 | 숨김,활성화=2 | 4 | 숨김/활성화 토글(즉시 반영, 확인폼 없음) — 같은 상세 모달이 답변등록·활동점수지급 버튼도 호스팅(위 2개 행에서 별도 산정) | `runNshop_policy_v1_2.md` 15장 |
| QnA관리 | — | 주문 QnA 관리 | A | — | 사용자 | N/A | N/A | N/A | 코드 확인 결과 별도 화면이 아님 — admin `community/qna`의 QnaType이 `PRODUCT`\|`ORDER`로 통합되어 있어 "QnA 관리(admin)"와 동일한 화면·버튼을 유형 필터(주문문의)로만 구분. "OrderQnA" 전용 엔티티/화면은 코드에 존재하지 않음(추가 API 표면 없음) | `runNshop_policy_v1_2.md` 15장 |
| 커뮤니티활동관리 | — | 크루·챌린지 관리 | — | — | — | N/A | N/A | N/A | 활동지수 산정(리뷰+2, 챌린지완료+3 등) — admin/partner/mobile 어디에도 크루·챌린지 화면 코드 없음. `member/list/MemberPage.spec.md`의 활동지수 산정 공식(정책 텍스트)에만 언급됨 | `runNshop_policy_v1_2.md` 15장 |
| 러닝기록관리 | — | 러닝 기록·코스 추천 관리 | — | — | — | N/A | N/A | N/A | RunningLog, CourseReview — 위와 동일하게 실제 화면 코드 없음, `MemberPage.spec.md` 정책 텍스트에만 언급됨 | `runNshop_policy_v1_2.md` 15장 |
| 커뮤니티통계 | — | 커뮤니티 통계 조회(운영자) | A | — | 사용자 | N/A | N/A | N/A | 리뷰수·평균평점·리뷰작성률·QnA 처리율·평균답변시간 등 — admin에 통계 화면 자체가 없음(Vendor·Settlement·Notification과 동일하게 반복 확인된 패턴). 신규 공백 | — |
| 리뷰관리 | — | 리뷰 포인트 지급(컨슈머) | C | — | 이벤트 | N/A | N/A | N/A | 구매 인증 리뷰 작성 시 포인트 적립 트리거. 정책서 §6.1 | `runNshop_policy_v1_2.md` §6.1 |
| 리뷰관리 | — | 커뮤니티 활동 금지행위 모니터링 | A | — | 사용자 | N/A | N/A | N/A | 입점사 직접 마케팅 금지·비방·허위 리뷰 탐지·처리. 정책서 §6.2 | `runNshop_policy_v1_2.md` §6.2 |

**합계(N/A 14건 제외): 소분류 18개 중 4개 산정, API 호출 약 14개**

**Community가 하지 않는 것**: 상품 카탈로그 직접 관리(→Catalog), 회원 관리(→Member),
알림 발송(→Notification), 포인트·쿠폰 처리(→Promotion)

## 코드 기반 보완 (2026-07-28, apps/ 실제 소스 조사)

- **QnA 활동점수 지급**이 admin·partner 둘 다에 존재하는 별도 기능으로 확인 — 도메인정의서의
  "활동지수 산정"(크루/챌린지 중심)과는 다른, "QnA 답변"에 특화된 인센티브 메커니즘.
  02-Catalog.md의 "상품문의"도 실제로는 이 QnA관리와 같은 기능임(진입점만 상품 상세 화면).
- **고객 작성 플로우(리뷰·QnA 둘 다) 화면이 mobile 코드에 없음** — PDP(상품상세) 탭
  (`components/product/ProductTabs.tsx`)에서 "별도 화면(CUS-070/071)에서 구현됩니다"라는 안내
  텍스트만 있어, 이 리포 밖에 화면 카탈로그가 이미 존재함을 시사(Human Review — CUS 번호 체계
  출처 확인 필요). 화면/버튼/API 3열 모두 N/A로 표기.
- **주문 QnA 관리는 별도 화면이 아님을 확인** — admin `community/qna/mockData.ts`의
  `QnaType = 'PRODUCT' | 'ORDER'`가 하나의 QnA 관리 화면·컴포넌트에서 함께 처리되고 있어,
  "OrderQnA"라는 전용 화면/엔티티는 코드상 존재하지 않는다. 기존 비고의 "OrderQnA" 표기는
  실제 코드와 불일치하여 이번에 정정했다(N/A 처리, 추가 API 표면 없음).
- **크루·챌린지 관리, 러닝기록관리(러닝 기록·코스 추천)는 admin/partner/mobile 어디에도 실제
  화면 코드가 없음** — `member/list/MemberPage.spec.md`의 활동지수 산정 공식 텍스트에만 등장
  (정책서 §4.3 인용). 도메인정의서에 정의는 있으나 이 리포의 코드로는 검증 불가하여 N/A 처리.
- **API 호출 개수 산정 시 QnA 상세 모달의 화면-공유 문제**를 명시적으로 분리 처리했다 — admin
  QnA 상세 모달 1개가 "상품 QnA 답변"·"QnA 활동점수 지급"·"QnA 관리(admin)" 3개 소분류 버튼을
  동시에 담고 있어, 화면 로드 중복 계상을 피하기 위해 화면은 "QnA 관리(admin)" 행에만 귀속시키고
  나머지 행은 버튼(API 엔드포인트)만 산정했다. 행별 합계(화면 6, 버튼 8)가 실제 물리 화면 6개
  (리뷰 admin 목록+상세=2, QnA admin 목록+상세=2, QnA partner 목록+상세=2)·실제 버튼 8개
  (리뷰: 숨김확정·활성화 / QnA admin: 답변등록·활동지수지급·숨김·활성화 / QnA partner:
  답변등록·활동지수지급)와 정확히 일치함을 교차 검증했다.
- **상태전이 추가(2026-07-28)**: 리뷰는 ACTIVE→HIDDEN(관리자 숨김), ACTIVE→DELETED(작성자
  삭제)의 2개 전이를 가지며 삭제는 terminal(복원 불가). QnA는 WAITING→ANSWERED(답변 등록 시)
  전이가 핵심이며, 모더레이션용 ACTIVE↔HIDDEN 토글도 존재.
- **평점 집계 이벤트 발행(컨슈머) 신규 추가(2026-07-28)**: 리뷰 작성/수정/삭제 시 Catalog
  도메인에 평점 갱신 이벤트를 발행하는 비동기 컨슈머 — 기존 "평점 집계" 행의 역할을 명확화하여
  이벤트 발행 관점으로 재정의했다.

## 코드 기반 보완 (2026-07-29, 회원/운영자/입점사 일반 기능표 대조 검토)

- **신규 추가 7건**: 리뷰 신고(고객)/리뷰 신고 처리(운영자)/리뷰 신고 결과 확인(입점사)/리뷰
  베스트 선정(운영자)/리뷰 답변(입점사)(이상 리뷰관리), 내 리뷰·QnA 모아보기(고객)(신규 대분류
  "커뮤니티이력"), 커뮤니티 통계 조회(운영자)(신규 대분류 "커뮤니티통계"). 전부 코드·정책 근거
  없는 신규 공백 — 리뷰 답변은 QnA의 벤더 답변(`answeredByType: VENDOR`) 기능과 대칭이 없다는
  점으로, 커뮤니티 이력은 `03-Member.md`가 "주문/클레임 이력은 Order 소유"라며 Member에서
  제외한 선례와 동일한 논리로 Community 소관임을 확인했다.
- **이미 반영됨(신규 제외)**: 비공개 Q&A는 `isPublic` 필드(ORDER 유형은 항상 false)로 이미
  구현돼 QnA관리(admin)에 흡수됨. 이미지 검수는 리뷰 관리(admin)의 숨김/활성화로 이미 커버됨
  (이미지 단위 별도 승인/반려 워크플로우는 없음). 게시글 이력 관리는 `12-Audit.md`의 도메인
  이벤트 감사 로그 컨슈머가 이미 커버(단, Community 전용 편집이력 뷰는 아니라는 한계 있음).
- **BC 대상(별도 논의)**: FAQ(회원조회/운영자등록/입점사조회) → Config 소관(`03-Member.md`가
  이미 명시했으나 `11-Config.md` 본문엔 FAQ 소분류가 실제로 없는 문서 간 불일치 확인 — Config
  쪽 보완 필요). 평점 조회(입점사, 자기 상품 평점) → Vendor/Catalog 소관(partner
  `product-list/ProductDetail.tsx` "구매평가" 탭에 이미 구현돼 있음 — `07-Vendor.md` "성과통계
  (벤더 자기관리)"에 2026-07-29 반영 완료).
- **판단 보류**: 댓글(이벤트와 무관한 일반 제품 댓글)은 코드 근거가 없을뿐더러, 정책서 §6이
  1단계 커뮤니티 범위를 "리뷰·평점·QnA"로만 명시해 애초에 계획되지 않은 기능일 가능성이 높음
  — 신규 공백으로 단정하지 않고 Human Review로 남김.
- **산술 재검증(2026-07-29, 구글 스프레드시트 통합 작업 중 발견)**: 표 전체를 스크립트로
  재계산한 결과 실제 물리 행은 17개(기존 10개 + 오늘 신규 7개)인데, 합계 줄은 기존 표기
  오류("13개 중 5개 산정")를 그대로 이어받아 "20개 중 5개 산정"으로 누적 과다 집계돼 있었다 —
  "17개 중 4개 산정, N/A 13건 제외"로 정정(API 호출 개수는 원래도 정확했음, ~14개 유지).

---
출처: 도메인정의서 §11(Community) "소유 데이터"·"활동지수 산정" + `apps/runNshop-admin/src/community/`,
`apps/runNshop-partner/src/community/`, `apps/runNshop-mobile/app/products/[productId]/`,
`apps/runNshop-mobile/components/product/ProductTabs.tsx`,
`apps/runNshop-admin/src/product/product-list/tabs/ReviewsTab.tsx`,
`apps/runNshop-admin/src/member/list/MemberPage.spec.md` 실제 소스.
