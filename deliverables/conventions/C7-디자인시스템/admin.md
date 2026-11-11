# C7 디자인 시스템 — Admin (runNshop-admin)

> **스타일링**: 순수 CSS 클래스 (globals.css), BEM 네이밍
> **레이아웃**: NavBar + TabBar + TabContent (MDI 패턴)
> **뷰포트**: 데스크톱 전용 (반응형 미적용)
> **수립 데드라인**: S3 화면레이아웃 작성 전 | **참고 대상**: DN 화면레이아웃, tsx 구현

---

## 1. Foundation

### Color

| 역할 | 값 | 용도 |
|---|---|---|
| NavBar 배경 | `#1e293b` (slate-800) | 최상단 네비게이션 |
| NavBar 텍스트 | `#f1f5f9` | 메뉴 라벨 |
| NavBar 활성 | `#0ea5e9` (sky-500) | 선택 메뉴 하단 바 |
| Body 배경 | `#f5f6fa` | 전체 배경 |
| Body 텍스트 | `#1a1a2e` | 기본 텍스트 |
| 카드 배경 | `#ffffff` | 카드, 테이블, 모달 |
| 구분선 | `#e2e8f0` (slate-200) | border 전반 |
| TabBar 배경 | `#f1f5f9` (slate-100) | 탭 바 |
| Tab 활성 | `#1e293b` / 600 | 활성 탭 텍스트 |
| Tab 비활성 | `#64748b` (slate-500) | 비활성 탭 |
| 보조 텍스트 | `#94a3b8` (slate-400) | 부가정보 |
| Primary | `#0ea5e9` (sky-500) | 링크, CTA |
| Success | `#22c55e` | 완료 뱃지 |
| Warning | `#f59e0b` | 경고 뱃지, 대기 |
| Error | `#ef4444` | 에러, 삭제 |

### Typography

| 용도 | 스타일 |
|---|---|
| 시스템 폰트 | `-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif` |
| 기본 | 14px |
| `.page-title` | 22px / 700 |
| 섹션 제목 | 16px / 600 |
| `.table th` | 12px / 500 / uppercase |
| `.tab` | 12px / 활성 600 |
| `.badge` | 11px / 500 |
| `.nav-item__label` | 13px |

### Spacing

| 용도 | 값 |
|---|---|
| NavBar 높이 | 56px |
| TabBar 높이 | 40px |
| `.page` 패딩 | 32px 24px (max-width: 1200px) |
| `.summary-card` 패딩 | 16px 20px |
| `.filter-bar` 패딩 | 14px 16px |
| 컴포넌트 gap | 8~12px |
| 섹션 margin-bottom | 16~24px |

### Border & Radius

| 용도 | 값 |
|---|---|
| 카드, 필터, 모달 | `border-radius: 8px` |
| 탭 (상단) | `6px 6px 0 0` |
| 버튼, 입력 | `6px` |
| 뱃지 | `4px` |
| 원형 | `50%` |
| 구분선 색상 | `#e2e8f0` |

### Elevation

| 용소 | 값 |
|---|---|
| 대부분 | 그림자 없음 (border 구분) |
| 모달 | `0 20px 60px rgba(0,0,0,0.3)` |
| 드롭다운 | `0 4px 12px rgba(0,0,0,0.1)` |

---

## 2. Component (BEM 클래스)

### Shell

| 클래스 | 역할 |
|---|---|
| `.shell` | `display:flex; flex-direction:column; height:100vh; overflow:hidden;` |
| `.navbar` | 상단 NavBar (h:56px, bg:#1e293b) |
| `.tabbar` | MDI 탭 바 (h:40px, bg:#f1f5f9) |
| `.tab-content` | 탭 콘텐츠 (flex:1, overflow:auto) |

### NavBar

| 클래스 | 역할 |
|---|---|
| `.nav-brand` | 로고 (16px, 700, color:#0ea5e9) |
| `.nav-menu` | 메뉴 목록 (flex, gap:4px) |
| `.nav-item` | 메뉴 항목 (13px, color:#94a3b8) |
| `.nav-item--active` | 활성 (color:#f1f5f9, border-bottom:2px #0ea5e9) |
| `.nav-item__badge` | 알림 수 뱃지 |
| `.nav-user` | 우측 사용자 |

### TabBar

| 클래스 | 역할 |
|---|---|
| `.tab` | 탭 (12px, color:#64748b, top:1px) |
| `.tab--active` | 활성 (bg:#fff, border, 600) |
| `.tab__label` | 제목 (ellipsis, max-width:200px) |
| `.tab__close` | [×] (16×16, 50%, hover:bg) |

### Page

| 클래스 | 역할 |
|---|---|
| `.page` | max-width:1200px, margin:auto, padding:32px 24px |
| `.page-title` | 22px/700, mb:24px |

### SummaryBar

| 클래스 | 역할 |
|---|---|
| `.summary-bar` | flex, gap:12px, mb:20px |
| `.summary-bar--compact` | 카드 다수(5+)일 때 — 카드를 가로 배치, 내용 크기 기반 폭 |
| `.summary-card` | flex:1, bg:#fff, border, radius:8px, padding:16px 20px |
| `.summary-card` (compact 내) | flex:initial, flex-direction:row, min-height:36px, padding:0 14px, gap:6px |
| `.summary-card__label` | 12px, color:#64748b (compact: mb:0) |
| `.summary-card__count` | 24px, 700 (compact: 13px, 700) |
| `.summary-card--warn` | border:#f59e0b, bg:#fffbeb, count:#d97706 |
| `.summary-card--info` | border:#60a5fa, bg:#eff6ff, count:#1d4ed8 |

#### SummaryBar + Toolbar 한 줄 패턴

SummaryBar 옆에 액션 버튼([엑셀 다운로드] 등)을 같은 행에 배치하는 패턴:

```
┌─ 한 줄 row (flex, align-items:center, gap:12px) ─────────────┐
│ [summary-bar--compact: 카드1 카드2 ... 카드N]  [엑셀 다운로드] │
│  ← flex:1                                    ← flex-shrink:0  │
└───────────────────────────────────────────────────────────────┘
```

- 래퍼: `display:flex; align-items:center; gap:12px; margin-bottom:16px;`
- SummaryBar: `flex:1; margin-bottom:0;`
- 버튼: `flex-shrink:0;`

### FilterBar

| 클래스 | 역할 |
|---|---|
| `.filter-bar` | flex, gap:8px, bg:#fff, border, radius:8px, padding:14px 16px, mb:16px |
| `.filter-bar__input` | h:32px, border, radius:6px, min-width:180px |
| `.filter-bar__select` | h:32px, border, radius:6px |
| `.filter-bar__btn` | h:32px, bg:#0ea5e9, color:#fff, radius:6px |

### Table

| 클래스 | 역할 |
|---|---|
| `.table-wrap` | bg:#fff, border, radius:8px, overflow:hidden |
| `.table` | width:100%, collapse |
| `.table th` | 12px, uppercase, bg:#f8fafc, border-bottom |
| `.table td` | 13px, border-bottom:#f1f5f9 |
| `.table tr:hover td` | bg:#f8fafc |
| `.table__link` | color:#0ea5e9, underline on hover |

### Badge

| 클래스 | 스타일 |
|---|---|
| `.badge` | inline-flex, gap:4px, padding:2px 8px, radius:4px, 11px/500 |
| `.badge--blue` | bg:#eff6ff, color:#1d4ed8 |
| `.badge--green` | bg:#f0fdf4, color:#15803d |
| `.badge--yellow` | bg:#fffbeb, color:#b45309 |
| `.badge--red` | bg:#fef2f2, color:#dc2626 |
| `.badge--gray` | bg:#f1f5f9, color:#64748b |

### Modal

| 클래스 | 역할 |
|---|---|
| `.modal-overlay` | fixed, inset:0, bg:rgba(0,0,0,0.4), z:200 |
| `.modal` | max-width:640px, bg:#fff, radius:12px, shadow |
| `.modal__header` | flex, padding:20px 24px, border-bottom |
| `.modal__body` | padding:24px, overflow-y:auto |
| `.modal__footer` | flex, gap:8px, padding:16px 24px, border-top |
| `.modal--sm` | max-width:400px |

### Form

| 클래스 | 역할 |
|---|---|
| `.form-group` | mb:16px |
| `.form-group__label` | 12px/500, mb:6px |
| `.form-input` | h:36px, border, radius:6px, padding:0 12px |
| `.form-select` | 동일 |
| `.btn` | h:36px, radius:6px, padding:0 16px, 13px/500 |
| `.btn--primary` | bg:#0ea5e9, color:#fff |
| `.btn--danger` | bg:#ef4444, color:#fff |

### Timeline

| 클래스 | 역할 |
|---|---|
| `.timeline` | padding-left:20px, border-left:2px #e2e8f0 |
| `.timeline-item` | position:relative, mb:16px |
| `.timeline-item__dot` | absolute, left:-25px, w:10px, h:10px, radius:50% |
| `.timeline-item__content` | 13px |
| `.timeline-item__time` | 11px, color:#94a3b8 |

### Toast

| 클래스 | 스타일 |
|---|---|
| `.toast` | fixed, bottom:24px, left:50%, transform, padding:10px 20px, radius:8px, z:9999, shadow |
| `.toast--success` | bg:#22c55e, color:#fff |
| `.toast--error` | bg:#ef4444, color:#fff |
| `.toast--info` | bg:#1e293b, color:#fff |
| 동작 | 3초 후 fadeOut (opacity transition 0.3s) |

### Skeleton

| 클래스 | 스타일 |
|---|---|
| `.skeleton` | bg:#e2e8f0, radius:6px, animation:pulse 1.5s infinite |
| `.skeleton--line` | height:14px, mb:8px |
| `.skeleton--card` | height:80px, mb:12px |

### Pagination

| 클래스 | 역할 |
|---|---|
| `.pagination` | flex, center, gap:4px, padding:16px |
| `.pagination__btn` | 32×32, border, radius:6px, 13px |
| `.pagination__btn--active` | bg:#0ea5e9, color:#fff |

---

## 3. Layout — MDI 쉘

```
┌────────────────────────────────────────────────────────────────┐
│ .navbar (h:56px, bg:#1e293b)                                    │
│  [nav-brand] [nav-menu: 홈|상품|주문|회원|...] [nav-user]      │
├────────────────────────────────────────────────────────────────┤
│ .tabbar (h:40px, bg:#f1f5f9, border-bottom)                    │
│  [tab--active: 주문현황 ×] [tab: 클레임관리 ×]                  │
├────────────────────────────────────────────────────────────────┤
│ .tab-content (flex:1, overflow:auto, bg:#f5f6fa)               │
│   .page (max-width:1200px, padding:32px 24px)                  │
│     [page-title] + [summary-bar] + [filter-bar] + [table-wrap] │
└────────────────────────────────────────────────────────────────┘
```

---

## 4. Template → Page 매핑

| Template | 구성 | 해당 페이지 |
|---|---|---|
| T-DASHBOARD | SummaryCards + TrendChart + PendingItems + SystemAlerts | 홈 |
| T-LIST | PageTitle + SummaryBar + FilterBar + Table + Pagination | 주문현황, 클레임관리, 회원, 상품 |
| T-DETAIL-MDI | PageTitle + InnerTabs(탭별 콘텐츠) | 주문상세, 클레임상세 |
| T-FORM-MODAL | Modal(Header + Form + Footer) | 생성/수정 |
| T-TREE | PageTitle + TreeView + Detail Panel | 카테고리 |

---

## 근거

| 항목 | 출처 |
|---|---|
| BEM 클래스 전체 | `apps/runNshop-admin/src/app/globals.css` (1800+ lines) |
| 레이아웃 | `app/layout.tsx` |
| 테마 색상 | NavBar #1e293b, Primary #0ea5e9 |
| 스타일링 규칙 | `.kiro/steering/coding-standards.md` — "순수 CSS 클래스 (globals.css)" |
