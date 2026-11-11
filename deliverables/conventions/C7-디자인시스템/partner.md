# C7 디자인 시스템 — Partner (runNshop-partner)

> **스타일링**: 순수 CSS 클래스 (globals.css), BEM 네이밍 (Admin과 동일 구조, 테마 색상 변경)
> **레이아웃**: NavBar + TabBar + TabContent (MDI 패턴)
> **뷰포트**: 데스크톱 전용 (반응형 미적용)
> **수립 데드라인**: S3 화면레이아웃 작성 전 | **참고 대상**: DN 화면레이아웃, tsx 구현

---

## 1. Foundation

### Color (Admin 대비 테마 색상 차이점)

| 역할 | Partner | Admin | 차이 |
|---|---|---|---|
| NavBar 배경 | `#7c2d12` (orange-900) | `#1e293b` (slate-800) | **주요 차이** |
| NavBar 활성/Primary | `#7c2d12` (orange-900) | `#0ea5e9` (sky-500) | **주요 차이** |
| Body 배경 | `#f5f6fa` | `#f5f6fa` | 동일 |
| Body 텍스트 | `#1a1a2e` | `#1a1a2e` | 동일 |
| 카드 배경 | `#ffffff` | `#ffffff` | 동일 |
| 구분선 | `#e2e8f0` | `#e2e8f0` | 동일 |
| TabBar 배경 | `#f1f5f9` | `#f1f5f9` | 동일 |
| Success | `#22c55e` | `#22c55e` | 동일 |
| Warning | `#f59e0b` | `#f59e0b` | 동일 |
| Error | `#ef4444` | `#ef4444` | 동일 |

> **테마 원칙**: Partner는 Admin과 동일한 BEM 클래스·레이아웃을 사용하되, NavBar/Primary 색상만 orange-900 계열로 변경하여 시각적으로 구분합니다.

### Typography

Admin과 동일 (시스템 폰트, 14px 기본, `.page-title` 22px/700 등)

### Spacing

Admin과 동일 (NavBar 56px, TabBar 40px, `.page` 32px 24px 등)

### Border & Radius

Admin과 동일

### Elevation

Admin과 동일

---

## 2. Component (BEM 클래스)

> Admin의 모든 BEM 클래스를 **그대로 사용**합니다. 차이점만 아래 기술합니다.

### NavBar (색상 차이만)

| 클래스 | Admin | Partner |
|---|---|---|
| `.navbar` background | `#1e293b` | `#7c2d12` |
| `.nav-brand` color | `#0ea5e9` | `#7c2d12` (→ 배경 위에서는 white) |
| `.nav-item--active` border-bottom | `#0ea5e9` | `#f97316` (orange-500) |

### 배송관리 전용 — 배경색 구분

> Partner 배송관리 화면에서 출고/회수/재배송을 배경색으로 구분합니다.

| 구분 | 배경색 | 클래스 |
|---|---|---|
| 출고 (OUTBOUND) | 흰색 (기본) | — |
| 회수 (PICKUP) | 연노랑 `#fffbeb` | `.table-row--pickup` |
| 재배송 (EXCHANGE_OUT) | 연파랑 `#eff6ff` | `.table-row--exchange` |

### 나머지 컴포넌트

Admin과 동일:
- Shell, TabBar, Page, SummaryBar (+ compact 변형 + Toolbar 한 줄 패턴), FilterBar, Table, Badge, Modal, Form, Timeline, Toast, Skeleton, Pagination

---

## 3. Layout — MDI 쉘

Admin과 동일한 MDI 구조:

```
┌────────────────────────────────────────────────────────────────┐
│ .navbar (h:56px, bg:#7c2d12)  ← 색상만 다름                    │
│  [nav-brand: runNshop Partners] [nav-menu] [nav-user]          │
├────────────────────────────────────────────────────────────────┤
│ .tabbar (h:40px, bg:#f1f5f9)                                   │
├────────────────────────────────────────────────────────────────┤
│ .tab-content → .page                                           │
└────────────────────────────────────────────────────────────────┘
```

---

## 4. Template → Page 매핑

| Template | 구성 | 해당 페이지 |
|---|---|---|
| T-DASHBOARD | SummaryCards (접수대기/출고대기/배송중/클레임) | 홈 |
| T-LIST | PageTitle + SummaryBar + FilterBar + Table + Pagination | 주문목록, 클레임현황, 배송관리 |
| T-DETAIL-MDI | PageTitle + InnerTabs | 주문상세(주문상품/배송정보/클레임/변경이력), 클레임상세(클레임상품/배송정보/변경이력) |
| T-FORM-MODAL | Modal | 출고처리, 운송장등록, 품질점검 |

---

## 5. Admin과의 차이 요약

| 항목 | Admin | Partner |
|---|---|---|
| NavBar 색상 | slate-800 (#1e293b) | orange-900 (#7c2d12) |
| Primary 강조색 | sky-500 (#0ea5e9) | orange-500 (#f97316) |
| 브랜드 텍스트 | "runNshop Admin" | "runNshop Partners" |
| 배송관리 행 배경색 | — | 출고:흰 / 회수:연노랑 / 재배송:연파랑 |
| 메뉴 구조 | 홈/상품/프로모션/주문/회원/판매자/정산/커뮤니티/운영설정/시스템 | 홈/주문/배송/클레임/정산/상품/설정 |
| 기능 범위 | 전체 관리 (클레임 접수/판정/환불/폐기) | 제한 (출고/수거/품질점검/재배송) |

---

## 근거

| 항목 | 출처 |
|---|---|
| BEM 클래스 | `apps/runNshop-partner/src/app/globals.css` |
| NavBar 색상 | globals.css `.navbar { background: #7c2d12 }` |
| 배경색 구분 | 화면레이아웃(DN) §14 배송관리 "배경색상으로 구분(흰/연노랑/연파랑)" |
| 스타일링 규칙 | `.kiro/steering/coding-standards.md` — "순수 CSS 클래스 (globals.css, 틸 테마)" |
| Admin 참조 | C7-디자인시스템/admin.md — 공통 구조 |
