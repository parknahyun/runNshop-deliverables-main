---
inclusion: fileMatch
fileMatchPattern: "**/runNshop-admin-react/**/*.tsx,**/runNshop-partner/**/*.tsx,**/runNshop-admin-vue/**/*.vue,**/runNshop-admin-vue/**/*.ts"
---
# 어드민/파트너 화면 UX 패턴 (공통)

> **분류: 공통(표준)** — React(`admin-react`, `partner`)와 Vue(`admin-vue`) 모두에 적용되는 화면 구조·UX 규칙. 프레임워크별 파일 구조·구현 문법은 각 프레임워크 전용 steering(React는 `admin-guide.md`, Vue는 해당 가이드)을 따른다.

## 화면 구조 재사용 지침

#[[file:docs/6. 화면정의/runNshop_admin_screen_guide_v1_0.md]]

## 화면 유형 (3가지)

### 메인 화면 (Dashboard)
- 최외곽: `.dashboard`
- 구조: `.dashboard__head` + `.dashboard__grid` + `.dash-card`
- 대시보드는 첫 번째 pinned 탭으로 고정 (닫기 불가)

### 현황 화면 (Table)
- 최외곽: `.page`
- 구조: `.filter-bar` → `.summary-bar` → `.table-wrap` → `.pagination`
- 행 클릭 시 상세 모달 오픈

### 상세 화면 (Detail Modal)
- 최외곽: `.detail-modal-overlay` + `.detail-modal`
- 구조: `.detail-modal__header` → `InnerTabs` → `.tab-panel-content`
- **규칙: admin/partner의 모든 상세·등록·수정 화면은 모달(detail-modal)로 구현한다**
- 현황 화면(table)에서 행 클릭 또는 등록 버튼 → 모달 오픈
- 탭으로 열지 않음 (MDI 탭은 현황 화면 전용)
- **모달 내부 기본 구조: InnerTabs (탭 방식)**
- 명시적으로 단계별(step) UI를 요청한 경우에만 stepper 사용
- 요청 없으면 항상 InnerTabs로 구현

## Shell 구조
- NavBar: 상단 드롭다운 메뉴 (MDI 방식)
- TabBar: 열린 화면 탭 (최대 8개, 대시보드 고정)
- TabContent: 활성 탭 화면 렌더링

이 Shell 구조는 React(`admin-react`)와 Vue(`admin-vue`) 둘 다 동일한 구조로 구현한다 — `coding-standards.md` "앱별 스타일링 방식" 표에 두 스택 모두 "NavBar + TabBar + TabContent (MDI)"로 명시돼 있다. 각 프레임워크의 실제 컴포넌트 구현(React 컴포넌트 vs Vue SFC)만 다르다.

## 색상 구분
- Admin: 슬레이트 다크(#1e293b) + 블루(#3b82f6)
- Partner: 다크 오렌지(#7c2d12) + 오렌지(#ea580c)

## 공통 컴포넌트 역할
각 프레임워크에서 동등하게 구현해야 하는 컴포넌트:
- `Pagination` — 페이지네이션
- `InnerTabs` — 상세 모달 내부 탭

(React 구현 위치는 `admin-guide.md` 참조. Vue 구현 위치는 해당 Vue 전용 가이드에서 정의.)

## 코드성 속성 입력방식
- 코드 4개 미만: 라디오(단일선택) 또는 체크박스(다중선택)
- 코드 4개 이상: select 드롭다운
- 예: 상태(3개: 활성/비활성/폐기) → 라디오, 템플릿유형(6개) → select

## 화면 작성 단위
- **목록/상세/등록**: 각각 독립 파일
- **상세 모달 내부 탭**: 반드시 탭별 파일 분리(React는 `tabs/` 폴더, Vue는 동등한 하위 폴더)
- **spec.md도 탭 단위로 분리**: 상위 spec은 탭 참조 링크만, 실제 내용은 `tabs/*.spec.md`에 작성
- 이유: 탭별 독립 수정 가능, AI가 관련 파일만 읽어서 정확도 향상

## 구현 완료 표시
`coding-standards.md`의 "구현 완료 표시" 규칙을 그대로 따른다(중복 기재하지 않음) — `implemented: true` → 초록 원(●), 미구현은 PlaceholderPage.

## spec.md 작성 규칙 (설계 문서 — 프레임워크 무관)

### 파일 구조
```
{domain}/{ScreenName}/
  {ScreenName}Page.spec.md         ← 목록 화면 (영역정의 + 필터 + 테이블컬럼 + API)
  {ScreenName}Detail.spec.md       ← 상세 모달 (헤더 + 탭구성 참조만)
  Add{ScreenName}Modal.spec.md     ← 등록 모달 (헤더 + 탭구성 참조 + Footer + 유효성)
  tabs/
    BasicInfoTab.spec.md           ← 읽기/편집/등록 모드별 폼 정의
    {기능}Tab.spec.md              ← CRUD 탭 (동작 + 서브모달 + 데이터관리 + 수정불가 조건)
```

### 상위 spec (Detail/Add) 작성 범위
- 화면 정보 (ID, 명, 유형, 진입경로)
- 모달 헤더 구성 (타이틀, 부가정보)
- 탭 구성 표 (탭명 + 컴포넌트 + spec 링크)
- API (상세 조회만)
- **탭 내부 기능은 적지 않음** → tabs/*.spec.md 참조

### 탭 spec 작성 범위
- 수정 처리 (상세화면에서의 동작)
- 등록 처리 (등록 모달에서의 동작)
- 수정 불가 조건 (있는 경우)
- 폼 필드 정의 (필드명, 타입, 필수, 비고)
- 데이터 관리 방식 (로컬 state / API 호출 시점)
- API 목록
