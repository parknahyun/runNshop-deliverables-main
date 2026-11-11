# C7 디자인 시스템 — Mobile (runNshop-mobile)

> **스타일링**: Tailwind CSS
> **레이아웃**: Header + Content + BottomNav (App Router)
> **뷰포트**: max-width 360px, 모바일 전용
> **수립 데드라인**: S3 화면레이아웃 작성 전 | **참고 대상**: DN 화면레이아웃, tsx 구현

---

## 1. Foundation

### Color (Tailwind 토큰 — tailwind.config.ts)

| 토큰 | 값 | 용도 |
|---|---|---|
| `primary` | #FF4D00 | CTA, 강조, SALE 뱃지 |
| `secondary` | #1A1A1A | 제목, 주요 텍스트, NEW 뱃지 |
| `success` | #00C853 | 성공 상태, 완료 뱃지 |
| `warning` | #FF9800 | 경고, 대기 상태 |
| `error` | #F44336 | 에러, 실패, 취소 |
| `gray-50` | Tailwind 기본 | Body 배경 |
| `gray-200` | Tailwind 기본 | 구분선, 카드 border |
| `gray-400` | Tailwind 기본 | 비활성 텍스트, BottomNav 비활성 |
| `gray-600` | Tailwind 기본 | 보조 텍스트 |
| `gray-900` | Tailwind 기본 | BottomNav 배경 |
| `white` | #FFFFFF | 헤더·카드 배경 |

### Typography

| 용도 | Tailwind 클래스 | 크기 |
|---|---|---|
| 브랜드 로고 | `font-bold text-sm text-secondary` | 14px Bold |
| 섹션 타이틀 | `text-base font-bold text-secondary` | 16px Bold |
| 본문 | `text-sm text-secondary` | 14px Regular |
| 보조/캡션 | `text-xs text-gray-600` | 12px Regular |
| 카테고리 GNB | `text-xs text-gray-600 whitespace-nowrap` | 12px |
| BottomNav 활성 | `text-xs font-bold text-white` | 12px Bold |
| BottomNav 비활성 | `text-xs text-gray-400` | 12px |
| 가격 (할인 전) | `text-xs text-gray-400 line-through` | 12px 취소선 |
| 가격 (판매가) | `text-sm font-bold text-secondary` | 14px Bold |

### Spacing

| 용도 | Tailwind | 값 |
|---|---|---|
| 좌우 Safe Area | `px-3` | 12px |
| 컴포넌트 간 gap | `gap-3` ~ `gap-4` | 12~16px |
| 섹션 간 간격 | `space-y-3` | 12px |
| 카드 내부 패딩 | `p-3` | 12px |

### Border & Radius

| 용도 | Tailwind |
|---|---|
| 카드 | `rounded-lg border border-gray-200` |
| 버튼 | `rounded` |
| 팝업 상단 | `rounded-t-2xl` |
| 원형 | `rounded-full` |

### Elevation

| 요소 | 처리 |
|---|---|
| 헤더 | `sticky top-0 z-20` |
| GNB | `sticky top-12 z-10` |
| BottomNav | `fixed bottom-0 z-30` |
| StickyBottom CTA | `fixed bottom-12 z-20 border-t` |
| Toast | `shadow-lg z-50` |
| LayerPopup | Overlay `z-40` + Sheet `z-50` |

---

## 2. Component

### Button

| 변형 | 클래스 | 용도 |
|---|---|---|
| Primary | `bg-primary text-white px-4 py-3 rounded font-bold text-sm` | 구매, 결제, 신청 |
| Secondary | `border border-gray-300 text-secondary px-4 py-3 rounded text-sm` | 취소, 닫기 |
| Text | `text-primary text-xs` / `text-sm` | 더보기, 링크, [옵션변경] |
| Disabled | `bg-gray-200 text-gray-400 cursor-not-allowed` | 미동의, 재고부족 |
| Small | `border border-primary text-primary rounded px-2 py-1 text-xs` | [전액사용] 등 |

### Badge

| 변형 | 클래스 | 용도 |
|---|---|---|
| NEW | `bg-secondary text-white text-xs px-1` | 신상품 |
| SALE | `bg-primary text-white text-xs px-1` | 할인 |
| 품절 | `absolute inset-0 bg-gray-500/70 rounded` + 중앙 텍스트 | 품절 오버레이 |
| 상태 | `bg-{success/warning/error} text-white text-xs rounded px-2` | 주문/클레임 상태 |
| 기본배송지 | `border border-gray-300 rounded text-xs text-gray-500 px-1` | 태그 |

### Input

| 변형 | 클래스 | 용도 |
|---|---|---|
| Text | `border border-gray-300 rounded px-2 py-1 text-sm` | 일반 입력 |
| Number | 위와 동일 + `type="number"` | 포인트, 수량 |
| Checkbox | `w-4 h-4` | 약관 동의 |
| Stepper | `w-6 h-6 border border-gray-300 rounded text-xs` 버튼 + 가운데 수량 | 수량 +/- |

### Card

| 변형 | 구조 | 용도 |
|---|---|---|
| ProductCard | 이미지(1:1) + 뱃지 + 상품명 + 가격 | 상품 목록 |
| CartItem | 이미지(w-16 h-16) + 상품명/옵션/가격/수량/삭제 | 장바구니 |
| OrderCard | 주문번호 + 상태뱃지 + 상품요약 + 금액 | 주문 목록 |
| ClaimCard | 클레임번호 + 유형 + 상태 + 타임라인 | 클레임 목록 |
| VendorGroup | `bg-white rounded-lg border border-gray-200 p-3` 안에 아이템 목록 | 판매자별 그룹 |

### Section (폼 섹션 카드)

> 주문서·클레임신청 등 L-FORM 화면에서 사용하는 정보 섹션 단위.
> 모든 섹션은 동일한 **섹션 헤더 패턴**을 따른다.

**섹션 컨테이너**: `bg-white rounded-lg border border-gray-200 p-3`

**섹션 헤더 패턴** (통일 규칙):

```
┌─────────────────────────────────────┐
│ [라벨]                   [우측 액션] │
│  text-sm font-bold        text-xs   │
│  text-secondary          text-primary│
└─────────────────────────────────────┘
```

| 요소 | 클래스 | 설명 |
|---|---|---|
| 래퍼 | `flex items-center justify-between mb-1` | 헤더 행 |
| 라벨 | `text-sm font-bold text-secondary` | 섹션 제목 (배송지, 쿠폰, 포인트, 결제수단) |
| 우측 액션 | `text-xs text-primary` | [변경], 사용 가능 N장 [>], 보유 N P 등 |
| 우측 보조값 | `text-xs text-gray-400` | 보유 포인트 등 비강조 정보 |

**적용 예시**:

| 섹션 | 라벨 | 우측 |
|---|---|---|
| 배송지 | "배송지" | `[변경]` (text-primary) |
| 쿠폰 | "쿠폰" | `사용 가능 2장 [>]` (text-primary) |
| 포인트 | "포인트" | `보유 5,200P` (text-gray-400) |
| 결제 수단 | "결제 수단" | — |
| 결제 금액 | "결제 금액" (font-bold) | — |

### Toast

| 변형 | 클래스 |
|---|---|
| Success | `fixed bottom-16 left-1/2 -translate-x-1/2 bg-secondary text-white px-4 py-2 rounded-lg text-xs shadow-lg z-50` |
| Error | 위와 동일 + `bg-error` |
| 동작 | 2초 후 opacity 0 → 제거 (transition-opacity duration-300) |

### LayerPopup (BottomSheet)

| 요소 | 클래스 |
|---|---|
| Overlay | `fixed inset-0 bg-black/50 z-40` (클릭 시 닫기) |
| Sheet | `fixed bottom-0 left-0 right-0 max-w-[360px] mx-auto bg-white rounded-t-2xl z-50 max-h-[80vh] overflow-y-auto` |
| Header | `flex items-center justify-between px-4 py-3 border-b border-gray-200` (타이틀 + [✕]) |
| Body | `px-4 py-3` |
| Footer | `px-4 py-3 border-t border-gray-200` (CTA 버튼) |
| 용도 | 옵션 변경, 쿠폰 적용, 배송지 선택, 배송비 결제 |

### Skeleton (로딩)

| 요소 | 클래스 |
|---|---|
| Block | `bg-gray-200 rounded-lg animate-pulse h-{20~24}` |
| Line | `h-3 bg-gray-200 rounded animate-pulse` |
| 사용법 | `count` prop으로 반복, API 응답 후 교체 |

---

## 3. Layout

| Layout | 구조 | 사용 페이지 |
|---|---|---|
| **L-MAIN** | Header(h-12, sticky) + GNB(h-8, sticky) + Content(scroll, pb-12) + BottomNav(h-12, fixed) | 홈, 목록, 마이페이지 |
| **L-DETAIL** | BackHeader + Content(scroll) + StickyBottom(fixed bottom-12) | 상품상세, 주문상세, 클레임상세 |
| **L-FORM** | BackHeader + Content(scroll, pb-24) + StickyBottom(CTA) | 주문서, 클레임신청, 배송비결제 |

---

## 4. Template → Page 매핑

| Template | Layout | 페이지 경로 |
|---|---|---|
| T-HOME | L-MAIN | `/` |
| T-LIST | L-MAIN | `/category/{code}`, `/search` |
| T-DETAIL | L-DETAIL | `/products/{id}` |
| T-CART | L-FORM | `/cart` |
| T-ORDER | L-FORM | `/orders/new` |
| T-MY | L-MAIN | `/my` |
| T-MY-ORDERS | L-MAIN | `/my/orders` |
| T-MY-CLAIMS | L-MAIN | `/my/claims` |
| T-CLAIM-DETAIL | L-DETAIL | `/my/claims/{id}` |
| T-CLAIM-REQUEST | L-FORM | `/my/orders/{id}/claim` |

---

## 근거

| 항목 | 출처 |
|---|---|
| 컬러 토큰 | `apps/runNshop-mobile/tailwind.config.ts` |
| 레이아웃 구조 | `components/layout/Header.tsx`, `BottomNav.tsx`, `GNB.tsx` |
| 뷰포트 | `app/layout.tsx` — `max-w-[360px] mx-auto bg-gray-50` |
| 스타일링 규칙 | `.kiro/steering/coding-standards.md` — "Tailwind CSS" |
