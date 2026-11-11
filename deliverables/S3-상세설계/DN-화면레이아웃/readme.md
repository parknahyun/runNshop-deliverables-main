# 화면 레이아웃 — 주문·결제 도메인

> **단계**: 상세설계 (S3)  
> **문서범위**: Bolt (Order + Payment)  
> **문서종류**: Design  
> **도메인**: order, payment  
>
> **작성 목적**: 시퀀스(DM)에서 확정된 API 호출 시점과 응답 데이터를 화면에 매핑한다.  
> "어떤 화면에서 어떤 데이터를 어떤 API로부터 가져와 표시하는가"를 확정한다.
>
> **흐름 내 위치**:
> ```
> DE 메뉴구조도(화면 목록·앱 셸) ─┐
>                              ├─→ DN 화면 레이아웃
> DM 시퀀스(API 호출 시점) ──────┘
> ```
> DE는 "어떤 화면이 존재하는가"(화면 목차)를, DM은 "그 화면이 API를 언제·어떻게 호출하는가"를
> 각각 공급한다 — 화면 목차를 새로 만들지 않고 DE의 해당 앱 파일(admin/mobile/partner)에서
> 이 Bolt에 해당하는 화면만 발췌한다.
>
> **근거 소스**: `apps/runNshop-admin/src/order/`, `apps/runNshop-partner/src/order/`, `apps/runNshop-partner/src/claim/`, `apps/runNshop-mobile/app/cart/`, `apps/runNshop-mobile/app/orders/`, `api/runNshop-api/src/main/resources/mock/`

---

앱(채널)별 파일로 분리되어 있습니다. Catalog는 1차 파트(Order+Payment)와 화면이 겹치지 않아
도메인별 별도 파일(`catalog-{app}.md`)로 분리했다.

| 앱 | 파일 (Order+Payment) | 파일 (Catalog) |
|---|---|---|
| mobile (고객웹) | [mobile/index.md](mobile/index.md) — 화면 단위 분리 | [catalog-mobile.md](catalog-mobile.md) |
| admin (플랫폼 어드민) | [admin/index.md](admin/index.md) — 화면 단위 분리 | [catalog-admin.md](catalog-admin.md) |
| partner (판매자 어드민) | [partner/index.md](partner/index.md) — 화면 단위 분리 | [catalog-partner.md](catalog-partner.md) |

---

## 0. 문서 사용법 — 화면 섹션 표준 구조

> 모든 화면 섹션(`## N. ...`)은 아래 6개 하위섹션을 이 순서로 둔다.
> 이는 일반 웹 개발의 "화면정의서" 8항목(화면ID·접근권한·화면전환·유효성검증 등)을
> DN(화면레이아웃) 내부 구조로 흡수시켜, DK(세부UC)·DL(인터페이스명세)·DJ(GWT)를 오가지 않고도
> 화면 단위로 필요한 정보를 한 곳에서 찾을 수 있게 하기 위함이다.

```markdown
## N. {앱} — {화면명} ({컴포넌트명})

### 메타블록

| 항목 | 내용 |
|---|---|
| 화면 ID | SCR-M-001 |
| 앱 | mobile |
| 접근 권한 | 로그인 회원 |
| 관련 세부UC | [[DK-세부유스케이스/order|UC-1, UC-2, UC-23]] |
| 호출 API | [[DL-인터페이스명세/order|API-001~005]] |

### 와이어프레임
(ASCII 목업)

### 화면 구성
| 영역 | 데이터 소스 (API) | 표시 내용 |
|---|---|---|
...

### 화면 전환
| 트리거 | 이동 화면 (SCR-ID) |
|---|---|
| [선택상품 주문하기] 클릭 | SCR-M-002 (주문서) |
| [옵션변경] 클릭 | 레이어 팝업 (화면 전환 아님) |

### 유효성 검증
> [[DJ-GWT수용기준/order|GWT §1 장바구니 Bolt]] · 에러코드는 DL 참조

### 상태별 UI
| 상태 | 화면 표현 |
|---|---|
...
```

- **메타블록**: 화면 식별 정보(화면ID·앱·접근권한)와 상위 산출물 참조(관련 세부UC·호출 API)를 표로 묶는다.
  화면 ID는 프로그램목록(DQ) `SCR-*` ID를 그대로 표기. 외부 채널(알림톡/이메일)처럼 DQ에 화면(SCR)으로
  등록되지 않은 섹션은 `없음 (외부 채널)`로 표기. 관련 세부UC·호출 API는
  [[Foam-위키링크-활용가이드]] §3.2(별칭 링크) 방식을 사용한다 — 파일 단위 링크이며, 클릭하면 DK/DL
  파일이 열리고 본문에서 해당 번호를 검색(Ctrl+F)해 세부 내용을 확인한다(표 행 단위 정밀 앵커의 한계는
  [[Foam-위키링크-활용가이드]] §5 참조).
- **화면 전환**: 이 화면에서 발생하는 모든 화면 이동/레이어를 표로 나열한다. 다른 화면(SCR-ID)으로
  이동하는 트리거뿐 아니라, 레이어 팝업·모달처럼 **같은 화면 내에서 열리는 트리거도 함께 표기**한다 —
  다만 이동 화면 칸에 `레이어 팝업 (화면 전환 아님)`처럼 명시해 실제 SCR-ID 이동과 구분한다.
  외부(택배사 등) 이동이나 같은 화면 내 탭 전환(MDI)도 이 표에서 함께 표기한다.
- **유효성 검증**: 규칙 본문을 DN에 복제하지 않고 DJ(GWT)·DL(에러코드)로 링크만 건다 — 검증 규칙이
  바뀌어도 DN을 다시 손댈 필요가 없도록 하기 위함(방법론 "현행화는 자연 발생" 원칙 유지). 조회 전용 화면
  등 검증 대상이 없으면 `해당 없음`으로 표기.

### 0-1. 폴더·파일 구성 규칙 (2026-11-03 확정)

- **폴더는 도메인 기준**으로 나눈다: `{app}/{domain}/` (예: `admin/order/`, `admin/claim/`, `mobile/order/`, `partner/claim/`). 앱 폴더 바로 아래에는 `index.md`(앱 목차)와 도메인 폴더만 둔다.
- **문서는 화면 단위**로 분리한다: 화면 1개 = 파일 1개, 파일명은 `{화면ID}_{영문명}.md` (예: `SCR-M-001_cart.md`). 화면 ID가 없는 외부 채널(알림·이메일)은 영문명만 쓴다.
- **탭 화면(MDI 컨테이너+탭)은 화면 ID로 폴더를 만든다**: `{화면ID}/` 아래에 컨테이너 문서 `{화면ID}_detail.md`와 **탭 단위 문서** `{화면ID}-T{n}_{영문명}.md`를 둔다 (예: `admin/order/SCR-A-002/SCR-A-002-T2_payment.md`). 탭을 한 문서에 묶지 않는다.
- 문서 제목(H1)은 `# 화면 레이아웃 — [화면ID] {화면명} ({컴포넌트명})` 형식으로 화면 ID를 표시한다.
- 도메인 폴더에는 해당 도메인 화면 목록 `index.md`를 둘 수 있다.

### 0-0. 설계안과 구현 현황 표기 규칙 (2026-10-29 확정)

DN은 **목표 화면 설계안**이다. 현재 구현(프로토타입)과 다른 부분은 설계를 지우지 않고 다음처럼 표기한다.

- 화면 메타블록 바로 아래에 `> **구현 현황 (날짜)**: …` 인용 블록을 **한 개** 둔다(설계안/구현의 차이, Mock 여부, 미구현 API를 1~3문장으로).
- 설계에만 있고 구현에 없는 행·버튼에는 `프로토타입 미구현` 또는 `미구현`을 병기한다.
- 정책·값이 확정되지 않은 곳은 `[확인 필요: …]` 한 줄만 남기고 임의로 정하지 않는다.
- 화면이 쓰는 상세 조회 API는 DL의 탭별 Sub-API 정책(단일 응답)을 따른다. DN에 탭별 endpoint를 새로 적지 않는다.
- 개인정보 마스킹은 문서 규칙이 기준이다. 구현이 마스킹하지 않으면 "구현 갭"으로 기록한다.

### 0-1. 기획자·개발자 병행 작업 규칙 — "화면 구성" 표의 API 매핑

> admin/partner를 먼저 확정하고 mobile이 참조하는 순서(작성가이드 "화면 레이아웃" 절)가 원칙이지만,
> 실제로는 **화면 설계와 API 설계가 거의 동시에 진행**되는 경우가 많다. 이때는 완성된 문서를 넘기는
> 방식이 아니라, 미완성 칸을 서로 알아볼 수 있게 표시하고 각자 채워나가는 방식으로 협업한다.

- **데이터 소스(API) 칸에 확정된 API가 없을 때** — 기획자는 이 영역이 무엇을 보여줘야 하는지
  ("표시 내용" 칸)만 먼저 채우고, 데이터 소스 칸에는 `[TBD-API]`를 표기한다.
  ```markdown
  | 영역 | 데이터 소스 (API) | 표시 내용 |
  |---|---|---|
  | 클레임 가능 수량 뱃지 | [TBD-API] | 반품/교환 가능한 남은 수량을 뱃지로 표시 |
  ```
- **개발자가 API를 확정하면** — DL(인터페이스명세)에 endpoint를 추가한 뒤, DN의 `[TBD-API]`를
  실제 경로·필드명으로 교체한다. 이 교체는 화면 의미를 바꾸지 않는 단순 치환이라 기획자 재확인 없이
  진행 가능하다.
- **반대로 개발자가 먼저 API를 설계했는데 화면 표시 방식이 미정일 때** — "표시 내용" 칸에
  `[TBD-UX]`를 표기하고 기획자가 채우도록 남긴다.
- **`[TBD-*]` 태그는 Foam 미연결 언급(Unlinked mentions)처럼 grep으로 전수 검색 가능** —
  `grep -rn "TBD-" deliverables/` 로 채널·Bolt 전체에서 미확정 항목을 한 번에 추적한다.
  Bolt 상세설계 완료(DoD) 시점에는 `[TBD-*]`가 0건이어야 한다.
- 이 규칙은 admin/partner ↔ mobile 사이뿐 아니라, 같은 화면 안에서 기획자·개발자가 동시에
  작업하는 모든 경우에 적용한다.


---

## 채널별 완성 경로

| 채널 | 경로 | 이유 |
|---|---|---|
| mobile | md(스펙) → Figma(디자인) → tsx(React) | 고객 대면, 카드/리스트 중심 UX |
| admin | md(스펙) → tsx(React) 직행 | 내부 운영 도구, DataGrid + Form 패턴 |
| partner | md(스펙) → tsx(React) 직행 | 판매자 BO, admin과 동일 패턴 |


---

## 화면 목차

### mobile (고객 앱) — §1~10 — [mobile/index.md](mobile/index.md)

| § | 화면 | 유형 | 파일 |
|---|---|---|---|
| 1 | 장바구니 (CartPage) | 앱 내 | [mobile/order/SCR-M-001_cart.md](mobile/order/SCR-M-001_cart.md) |
| 2 | 주문서 (OrderNewPage) | 앱 내 | [mobile/order/SCR-M-002_order-sheet.md](mobile/order/SCR-M-002_order-sheet.md) |
| 3 | 주문 접수 완료 (OrderCompletePage) | 앱 내 | [mobile/order/SCR-M-003_order-complete.md](mobile/order/SCR-M-003_order-complete.md) |
| 4 | 주문 접수 실패 (OrderFailedPage) | 앱 내 | [mobile/order/SCR-M-004_order-failed.md](mobile/order/SCR-M-004_order-failed.md) |
| 5 | 알림 문자/알림톡 (NotificationMessage) | 외부 채널 | [mobile/order/notification.md](mobile/order/notification.md) |
| 6 | 주문 확인 이메일 (OrderConfirmationEmail) | 외부 채널 | [mobile/order/order-email.md](mobile/order/order-email.md) |
| 7 | 마이페이지 (MyPage) | 앱 내 | [mobile/order/SCR-M-005_mypage.md](mobile/order/SCR-M-005_mypage.md) |
| 8 | 주문/배송 조회 (MyOrdersPage) | 앱 내 | [mobile/order/SCR-M-006_my-orders.md](mobile/order/SCR-M-006_my-orders.md) |
| 8-1 | 주문 상세 (OrderDetailPage) | 앱 내 | [mobile/order/SCR-M-007_order-detail.md](mobile/order/SCR-M-007_order-detail.md) |
| 8-2 | 반품/교환 신청 (ClaimRequestPage) | 앱 내 | [mobile/claim/SCR-M-008_claim-request.md](mobile/claim/SCR-M-008_claim-request.md) |
| 8-3 | 반품/교환 신청 완료 (ClaimRequestCompletePage) | 앱 내 | [mobile/claim/SCR-M-009_claim-request-complete.md](mobile/claim/SCR-M-009_claim-request-complete.md) |
| 8-4 | 클레임 접수 완료 알림 (ClaimReceivedNotification) | 외부 채널 | [mobile/claim/claim-received-notification.md](mobile/claim/claim-received-notification.md) |
| 8-5 | 클레임 배송비 결제 완료 알림 (ClaimShippingPaymentNotification) | 외부 채널 | [mobile/claim/claim-shipping-payment-notification.md](mobile/claim/claim-shipping-payment-notification.md) |
| 8-6 | 클레임 처리 완료 알림 (ClaimCompletedNotification) | 외부 채널 | [mobile/claim/claim-completed-notification.md](mobile/claim/claim-completed-notification.md) |
| 9 | 클레임 목록 (MyClaimsPage) | 앱 내 | [mobile/claim/SCR-M-010_my-claims.md](mobile/claim/SCR-M-010_my-claims.md) |
| 10 | 클레임 상세 (ClaimDetailPage) | 앱 내 | [mobile/claim/SCR-M-011_claim-detail.md](mobile/claim/SCR-M-011_claim-detail.md) |

### admin (플랫폼 운영) — §11~12 — [admin/index.md](admin/index.md)

| § | 화면 | 파일 |
|---|---|---|
| 11 | 주문 현황 (OrderHistory) — 목록·상세·6개 탭 | [admin/order/index.md](admin/order/index.md) |
| 12 | 클레임 관리 (ClaimPage) — 목록 | [admin/claim/SCR-A-003_list.md](admin/claim/SCR-A-003_list.md) |
| 12-1 | 클레임 상세 (ClaimDetail MDI 탭) | [admin/claim/SCR-A-004/SCR-A-004_detail.md](admin/claim/SCR-A-004/SCR-A-004_detail.md) |

### partner (판매자) — §13~15 — [partner/index.md](partner/index.md)

| § | 화면 | 파일 |
|---|---|---|
| 13 | 주문 목록 (OrderListPage) · 상세·탭은 [SCR-P-002](partner/order/SCR-P-002/SCR-P-002_detail.md) 폴더 | [partner/order/SCR-P-001_list.md](partner/order/SCR-P-001_list.md) |
| 13-1 | 클레임 상세 (ClaimDetail MDI 탭) | [partner/claim/SCR-P-003/SCR-P-003_detail.md](partner/claim/SCR-P-003/SCR-P-003_detail.md) |
| 14 | 배송 관리 (ShippingPage) — 출고+회수+재배송 통합 | [partner/order/SCR-P-004_shipping.md](partner/order/SCR-P-004_shipping.md) |
| 15 | 클레임 현황 (ClaimStatusPage) — 취소/반품/교환 통합 | [partner/claim/SCR-P-005_claim-status.md](partner/claim/SCR-P-005_claim-status.md) |

### Catalog — admin — [catalog-admin.md](catalog-admin.md) §1~7

| § | 화면 |
|---|---|
| 1 | 직매입 상품 등록 (ProductDirectCreatePage) |
| 2 | 상품 심사 목록 (ProductReviewListPage) |
| 3 | 상품 목록 (ProductListPage) |
| 4 | 상품 상세 (ProductDetailPage) — 기본정보/심사/가격/재고 InnerTabs |
| 5 | 분류체계 관리 (CategoryManagePage) — 표준/전시/브랜드 InnerTabs |
| 6 | 노출 우선순위 관리 (ExposurePriorityPage) |
| 7 | 전시 페이지 목록·편집 (DisplayPageListPage/EditPage) |

### Catalog — partner — [catalog-partner.md](catalog-partner.md) §8~12

| § | 화면 |
|---|---|
| 8 | 상품 등록 (ProductCreatePage) |
| 9 | 반려 상품 재작성 (ProductRejectedEditPage) |
| 10 | 상품 목록 (ProductListPage) |
| 11 | 상품 상세·수정 (ProductEditPage) |
| 12 | 재고 관리 (StockManagePage) |

### Catalog — mobile — [catalog-mobile.md](catalog-mobile.md) §13~16

| § | 화면 |
|---|---|
| 13 | 상품 목록 (ProductListPage) |
| 14 | 상품 검색 (ProductSearchPage) |
| 15 | 상품 상세 (ProductDetailPage) |
| 16 | 재입고 알림 신청 완료 (RestockSubscribeToast, 레이어) |


---

## 공통 작성 규칙

| 규칙 | 설명 |
|---|---|
| 영역별 API 매핑 필수 | "이 데이터가 어디서 오는가" 명시 |
| 상태별 UI 정의 | 빈 상태, 로딩, 에러 상태 포함 |
| CTA(행동 유도) 명시 | 주요 버튼과 다음 화면 이동 |
| 인터페이스 명세(DL) 참조 | API 경로·응답 필드명 일치 |
| 개인정보 마스킹 | 연락처·이름은 마스킹 처리 (예: 010-****-5678, 홍*동) |


---

## 채널별 패턴 요약

| 채널 | 화면 패턴 | 특징 |
|---|---|---|
| admin | FilterBar → SummaryBar → DataGrid → Pagination → Detail(MDI탭/모달) | 테이블 중심, 상세는 InnerTabs |
| partner | FilterBar → SummaryBar → DataGrid → Pagination → Detail(MDI탭/모달) | admin과 동일 구조, 판매자 관점 데이터 |
| mobile | Header → 카드/리스트 섹션 → Summary → BottomBar(CTA) | 카드 중심 스크롤, 하단 고정 CTA |


---

## 근거

| 항목 | 출처 |
|---|---|
| API 매핑 | 시퀀스(DM) + 인터페이스 명세(DL) + mock JSON |
| 화면 목차 | 메뉴구조도(DE, 해당 앱 파일에서 이 Bolt 화면만 발췌) + 실제 구현 소스 |
| Catalog 화면 목차(§1~16) | `DK-세부유스케이스/catalog.md` 14개 Bolt를 화면 단위로 분해(admin 7·partner 5·mobile 4). 사용자 제안 목차(2026-09-28)를 기준으로 확정. DE-메뉴구조도에 Catalog 화면이 아직 없어(1차 파트 Order+Payment 중심) 선행 보강 없이 DN에서 화면 목차를 직접 정의 |
| Catalog 관리용 조회 API(§27~30) 보강 | 목차 설계 중 발견된 공백 — `DL-인터페이스명세/catalog.md` §27~30으로 선행 보강 후 DN에 반영 |
| 채널별 경로 | 코딩 표준 (앱별 스타일링 방식) |
| 데이터 필드 | `api/runNshop-api/src/main/resources/mock/order/*.json` |
| 컴포넌트 구현 | `apps/runNshop-*/src/order/`, `apps/runNshop-mobile/components/order/`, `apps/runNshop-mobile/components/cart/` |
| 화면 섹션 표준 구조(§0) | 화면정의서 8항목(화면ID·접근권한·화면전환·유효성검증 등)을 메타블록/화면구성/화면전환/유효성검증/상태별UI 6단 구조로 흡수. 화면ID·UC·API는 프로그램목록(DQ) §1 화면(SCR) 표에서 역추출. 위키링크 방식은 `reference/assets-working/Foam-위키링크-활용가이드.md` §3.2. 방법론 표준양식(DN 행)·샘플(17-화면레이아웃.md)에도 동일 템플릿 반영, 21개 화면 섹션 전체 적용 (2026-08-21, 기획자 리뷰 피드백 반영) |
| 화면 전환 — 레이어 팝업 표기 | "화면 전환" 표에 다른 SCR-ID로의 이동뿐 아니라, 같은 화면 내에서 열리는 레이어 팝업·모달 트리거도 함께 나열하고 `레이어 팝업 (화면 전환 아님)`으로 구분 표기하도록 §0 규칙 보강. §1(장바구니)·§2(주문서)·§8-2(반품/교환 신청)·§8-3(신청완료)·§10(클레임상세)·§11(admin 주문상세)·§14(배송관리) 등 실제 팝업이 있는 화면에 반영 (2026-08-21, 기획자 리뷰 피드백 반영) |
| 기획자·개발자 병행 작업 규칙(§0-1) | admin/partner 선행→mobile 후행 원칙과 달리, 화면·API 설계가 실제로는 동시 진행되는 경우를 위해 `[TBD-API]`/`[TBD-UX]` 태그 규칙 신설. "화면 구성" 표의 미확정 칸을 서로 표시하며 각자 채우는 협업 방식. 작성가이드·샘플문서(17-화면레이아웃.md)에도 동일 반영 (2026-08-21, 기획자 리뷰 피드백 반영) |

