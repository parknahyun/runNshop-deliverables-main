# NB Korea 공식 온라인스토어 — 모바일 Design System 역설계

> **분석 대상**: nbkorea.com 모바일웹 + 뉴발란스 코리아 공식 앱 (com.leadon.v1.nbkorea)
> **분석 일자**: 2026-08-12
> **분석 방법**: 사이트 직접 접근(JS SPA로 크롤링 제한), Google Play 앱 정보, NB Global 사이트 패턴 참조
>
> **범례**:
> - ✅ **확인됨** — 실제 사이트/앱에서 직접 확인된 사항
> - 🔍 **추정** — NB Global 패턴·업계 표준·스크린샷 기반 추정

---

## 1. Foundation (디자인 기초)

### 1-1. Color

| 토큰 | 값 (추정) | 용도 | 확인 |
|---|---|---|---|
| `--nb-black` | #000000 | 주 텍스트, 헤더 배경 | 🔍 |
| `--nb-white` | #FFFFFF | 배경, 카드 | 🔍 |
| `--nb-red` | #CF0A2C | CTA(장바구니, 구매), SALE 뱃지 | 🔍 |
| `--nb-gray-100` | #F5F5F5 | 섹션 배경 | 🔍 |
| `--nb-gray-300` | #D9D9D9 | 구분선, 비활성 | 🔍 |
| `--nb-gray-600` | #767676 | 보조 텍스트 | 🔍 |
| `--nb-gray-900` | #1A1A1A | 본문 텍스트 | 🔍 |

- 브랜드 컬러: **블랙+레드** 조합 (NB 로고 컬러)
- 모노톤 기반 + 레드 포인트 (CTA, SALE, NEW 뱃지)

### 1-2. Typography

| 토큰 | 스타일 | 용도 | 확인 |
|---|---|---|---|
| Display | 24px / Bold / -0.5px | 메인 배너 타이틀 | 🔍 |
| Heading-1 | 20px / Bold | 섹션 타이틀 | 🔍 |
| Heading-2 | 16px / Bold | 카드 제목, 가격 | 🔍 |
| Body-1 | 14px / Regular | 본문, 설명 | 🔍 |
| Body-2 | 13px / Regular | 보조 텍스트 | 🔍 |
| Caption | 11px / Regular | 뱃지, 부가정보 | 🔍 |

- 본문: **Noto Sans KR** (한글) + **Helvetica Neue** (영문/숫자) 🔍
- 가격 표시: 숫자 전용 폰트(Tabular figures) 우측 정렬 🔍

### 1-3. Spacing

| 토큰 | 값 | 용도 | 확인 |
|---|---|---|---|
| space-4 | 4px | 인라인 간격 | 🔍 |
| space-8 | 8px | 요소 내부 패딩 | 🔍 |
| space-12 | 12px | 카드 내부 패딩 | 🔍 |
| space-16 | 16px | 섹션 좌우 마진 | 🔍 |
| space-20 | 20px | 섹션 간 간격 | 🔍 |
| space-32 | 32px | 대섹션 간격 | 🔍 |

- 좌우 마진: 16px 고정 (Safe Area) 🔍
- 8px 그리드 시스템 🔍

### 1-4. Border & Radius

| 토큰 | 값 | 용도 | 확인 |
|---|---|---|---|
| radius-none | 0px | 상품 이미지, 배너 | 🔍 |
| radius-sm | 4px | 버튼, 뱃지 | 🔍 |
| radius-md | 8px | 카드, 입력 필드 | 🔍 |
| radius-full | 50% | 아바타, 카테고리 아이콘 | 🔍 |

- NB Korea는 직각(Sharp) 디자인 지향 — radius 최소 사용 🔍

### 1-5. Elevation (Shadow)

| 레벨 | 값 | 용도 | 확인 |
|---|---|---|---|
| elevation-0 | none | 대부분의 요소 | 🔍 |
| elevation-1 | 0 1px 4px rgba(0,0,0,0.08) | 플로팅 요소 | 🔍 |
| elevation-2 | 0 4px 12px rgba(0,0,0,0.12) | Bottom Sheet, 모달 | 🔍 |

- 플랫 디자인 기조 — 그림자 최소 사용 🔍

### 1-6. Icon

- 24x24px 기본 사이즈, stroke 기반 (outline 스타일) 🔍
- 주요 아이콘: 검색, 장바구니, 마이, 홈, 뒤로가기, 하트(위시), 공유, 필터, 정렬 🔍

---

## 2. Component (기본 컴포넌트)

### 2-1. Button

| 변형 | 스타일 | 용도 | 확인 |
|---|---|---|---|
| Primary | 블랙 배경 + 흰 텍스트, H:48px | 구매하기, 장바구니 담기 | 🔍 |
| Secondary | 흰 배경 + 블랙 테두리, H:48px | 옵션 선택, 매장 찾기 | 🔍 |
| Text | 텍스트만, 밑줄 | 더보기, 전체보기 | 🔍 |
| Icon | 아이콘 + 텍스트 조합 | 필터, 정렬 | 🔍 |
| Chip | pill 형태, H:32px | 사이즈 선택, 컬러 선택 | 🔍 |

### 2-2. Badge

| 변형 | 스타일 | 용도 | 확인 |
|---|---|---|---|
| NEW | 블랙 배경 + 흰 텍스트 | 신상품 | 🔍 |
| SALE | 레드 배경 + 흰 텍스트 | 할인 상품 | 🔍 |
| BEST | 그레이 배경 + 블랙 텍스트 | 인기 상품 | 🔍 |
| 품절 | 반투명 오버레이 | 재고 없음 | 🔍 |
| 온라인단독 | 블랙 테두리 | 온라인 전용 | ✅ (Play Store 설명 확인) |

### 2-3. Input

| 변형 | 스타일 | 용도 | 확인 |
|---|---|---|---|
| Search | 라운드 바, 돋보기 아이콘 | 검색 | 🔍 |
| Text | 밑줄(underline) 스타일 | 로그인, 주소 입력 | 🔍 |
| Stepper | -/+ 버튼 + 수량 | 수량 선택 | 🔍 |
| Select | 드롭다운 | 사이즈, 컬러 | 🔍 |

### 2-4. Card

| 변형 | 구조 | 용도 | 확인 |
|---|---|---|---|
| ProductCard | 이미지(1:1) + 뱃지 + 브랜드 + 상품명 + 가격 + 위시 | 상품 리스트 | 🔍 |
| BannerCard | 풀폭 이미지 + 오버레이 텍스트 | 기획전 배너 | 🔍 |
| ContentCard | 이미지(16:9) + 타이틀 + 설명 | 매거진/룩북 | 🔍 |
| ReviewCard | 별점 + 텍스트 + 이미지 썸네일 | 상품 후기 | 🔍 |

### 2-5. Navigation

| 변형 | 구조 | 확인 |
|---|---|---|
| TopBar | 로고(좌) + 검색+장바구니(우), H:56px | 🔍 |
| BackHeader | ←뒤로(좌) + 타이틀(중) + 공유/장바구니(우) | 🔍 |
| BottomNav | 5탭: 홈/카테고리/검색/위시/마이, H:56px | 🔍 |
| TabBar | 수평 스크롤 탭 (카테고리 하위) | 🔍 |

### 2-6. 기타 컴포넌트

| 컴포넌트 | 설명 | 확인 |
|---|---|---|
| Swiper/Carousel | 배너 자동 슬라이드, 인디케이터 dot | 🔍 |
| BottomSheet | 사이즈/컬러 선택, 필터 | 🔍 |
| Modal | 알림, 확인 팝업 | 🔍 |
| Toast | 장바구니 담기 완료 등 피드백 | 🔍 |
| Skeleton | 로딩 시 그레이 플레이스홀더 | 🔍 |
| Divider | 8px 높이 그레이 배경 섹션 구분 | 🔍 |
| Accordion | FAQ, 상품 상세 정보 접기/펼치기 | 🔍 |

---

## 3. Pattern (복합 패턴)

### 3-1. Product List Pattern

```
┌─────────────────────────────────────┐
│ [FilterBar] 필터 | 정렬 | 뷰전환    │
├─────────────────────────────────────┤
│ ┌────────┐ ┌────────┐              │
│ │Product │ │Product │  ← 2-column  │
│ │Card    │ │Card    │    Grid      │
│ └────────┘ └────────┘              │
│ ┌────────┐ ┌────────┐              │
│ │Product │ │Product │              │
│ │Card    │ │Card    │              │
│ └────────┘ └────────┘              │
│ ... 무한 스크롤                      │
└─────────────────────────────────────┘
```

- 2열 그리드 (기본) / 1열 리스트 (전환 가능) 🔍
- Sticky FilterBar (스크롤 시 상단 고정) 🔍
- 무한 스크롤 (페이지네이션 없음) 🔍

### 3-2. Product Detail Pattern

```
┌─────────────────────────────────────┐
│ [Image Swiper] 상품 이미지 (1:1)     │
│  ● ○ ○ ○ (dot indicator)            │
├─────────────────────────────────────┤
│ [뱃지] NEW / SALE                    │
│ 브랜드명                             │
│ 상품명                               │
│ ₩89,000  ₩119,000 (할인가/정가)     │
│ ★★★★☆ 4.2 (128)                    │
├── Divider ──────────────────────────┤
│ 컬러: [●] [●] [●] [●]              │
│ 사이즈: [230] [240] [250] [260]     │
├── Divider ──────────────────────────┤
│ [Accordion] 상품 정보                │
│ [Accordion] 배송/교환/반품 안내       │
│ [Accordion] 상품 후기 (128)          │
│ [Accordion] 상품 문의 (5)            │
├─────────────────────────────────────┤
│ 추천 상품 (수평 스크롤)               │
└─────────────────────────────────────┘
│ [StickyBottom] 위시 | 장바구니 | 구매 │
└─────────────────────────────────────┘
```

### 3-3. Cart Pattern

```
┌─────────────────────────────────────┐
│ [전체선택] □ 전체 (3)  [선택삭제]     │
├─────────────────────────────────────┤
│ □ [상품이미지] 상품명                 │
│              옵션: 블랙 / 260        │
│              ₩89,000                 │
│              [-] 1 [+]    [×삭제]    │
├── Divider ──────────────────────────┤
│ □ [상품이미지] 상품명                 │
│              ...                     │
├─────────────────────────────────────┤
│ 상품금액      ₩178,000              │
│ 배송비        무료                   │
│ 할인금액      -₩30,000              │
│ ─────────────────────               │
│ 결제예정금액  ₩148,000              │
└─────────────────────────────────────┘
│ [StickyBottom] 주문하기 (₩148,000)   │
└─────────────────────────────────────┘
```

### 3-4. Order Form Pattern

```
┌─────────────────────────────────────┐
│ 주문 상품 (2개)          [접기 ∨]    │
├─────────────────────────────────────┤
│ 배송지 정보                          │
│  홍*동 / 010-****-5678              │
│  서울시 강남구...          [변경]     │
├── Divider ──────────────────────────┤
│ 쿠폰 / 할인                         │
│  보유쿠폰 3장              [적용]     │
│  포인트 12,000P            [전액사용] │
├── Divider ──────────────────────────┤
│ 결제 수단                            │
│  ○ 신용카드  ○ 간편결제  ○ 계좌이체  │
├── Divider ──────────────────────────┤
│ 최종 결제금액                         │
│  상품금액 ₩178,000                   │
│  할인    -₩30,000                   │
│  배송비   ₩0                         │
│  ─────────                           │
│  합계    ₩148,000                    │
├─────────────────────────────────────┤
│ □ 전체 동의                          │
│   □ 구매조건 확인 (필수)              │
│   □ 개인정보 수집·이용 (필수)         │
└─────────────────────────────────────┘
│ [StickyBottom] ₩148,000 결제하기     │
└─────────────────────────────────────┘
```

### 3-5. MyPage Pattern

```
┌─────────────────────────────────────┐
│ 프로필: 홍*동님 (멤버십 등급)         │
│ 마일리지: 12,000P | 쿠폰: 3장       │
├─────────────────────────────────────┤
│ 주문/배송 상태 요약 (아이콘 4개)      │
│  입금대기(0) 배송준비(1) 배송중(1) 배송완료(2)│
├── Divider ──────────────────────────┤
│ [메뉴 리스트]                         │
│  주문/배송 조회                       │
│  취소/반품/교환                       │
│  위시리스트                           │
│  상품후기                            │
│  1:1 문의                            │
│  매장 찾기                           │
│  회원정보 수정                        │
│  멤버십 바코드                        │
└─────────────────────────────────────┘
```

---

## 4. Layout (레이아웃 구조)

### 4-1. Layout 유형 정의

| Layout ID | 명칭 | 구조 | 용도 | 확인 |
|---|---|---|---|---|
| L-HOME | 홈 레이아웃 | TopBar + Content(스크롤) + BottomNav | 메인 홈 | 🔍 |
| L-LIST | 리스트 레이아웃 | BackHeader + FilterBar(Sticky) + Content(무한스크롤) + BottomNav | 상품 목록, 검색 결과 | 🔍 |
| L-DETAIL | 상세 레이아웃 | BackHeader(투명→불투명) + Content + StickyBottom | 상품 상세 | 🔍 |
| L-FORM | 폼 레이아웃 | BackHeader + Content(스크롤) + StickyBottom(CTA) | 주문서, 회원가입 | 🔍 |
| L-MY | 마이 레이아웃 | BackHeader + Content + BottomNav | 마이페이지 | 🔍 |
| L-FULL | 풀스크린 레이아웃 | Content(100vh) + Close 버튼 | 로그인, 이미지 뷰어 | 🔍 |
| L-TAB | 탭 레이아웃 | BackHeader + TabBar + TabContent + BottomNav | 카테고리, 브랜드 | 🔍 |

### 4-2. Layout 구조 상세

```
┌─────────────── L-HOME ──────────────┐
│ ┌─ TopBar ─────────────────────┐    │
│ │ [NB로고]    [🔍] [🛒]       │    │
│ └──────────────────────────────┘    │
│ ┌─ Content (scroll) ───────────┐    │
│ │                              │    │
│ │  (페이지별 Template 삽입)     │    │
│ │                              │    │
│ └──────────────────────────────┘    │
│ ┌─ BottomNav ──────────────────┐    │
│ │ 홈  카테고리  검색  위시  마이 │    │
│ └──────────────────────────────┘    │
└─────────────────────────────────────┘

┌─────────────── L-DETAIL ────────────┐
│ ┌─ BackHeader (투명→Scroll시 불투명)─┐│
│ │ [←]              [♡] [공유] [🛒] ││
│ └──────────────────────────────────┘│
│ ┌─ Content (scroll) ───────────────┐│
│ │                                  ││
│ │  (상품 상세 Template)             ││
│ │                                  ││
│ └──────────────────────────────────┘│
│ ┌─ StickyBottom ───────────────────┐│
│ │ [♡]  [장바구니]  [바로구매]       ││
│ └──────────────────────────────────┘│
└─────────────────────────────────────┘

┌─────────────── L-FORM ──────────────┐
│ ┌─ BackHeader ─────────────────┐    │
│ │ [←] 주문/결제                │    │
│ └──────────────────────────────┘    │
│ ┌─ Content (scroll) ───────────┐    │
│ │                              │    │
│ │  (폼 Template)               │    │
│ │                              │    │
│ └──────────────────────────────┘    │
│ ┌─ StickyBottom ───────────────┐    │
│ │ [₩148,000 결제하기]          │    │
│ └──────────────────────────────┘    │
└─────────────────────────────────────┘
```

---

## 5. Template (Layout 기반 템플릿)

### 5-1. Template 목록

| Template ID | 명칭 | Layout | Content 구성 | 확인 |
|---|---|---|---|---|
| T-HOME-MAIN | 메인 홈 | L-HOME | HeroBanner + QuickMenu + NewArrivals + BestSellers + Magazine + EventBanner | 🔍 |
| T-LIST-PRODUCT | 상품 목록 | L-LIST | FilterBar + ProductGrid(2col) + InfiniteScroll | 🔍 |
| T-LIST-SEARCH | 검색 결과 | L-LIST | SearchBar + RecentKeyword/ProductGrid | 🔍 |
| T-DETAIL-PRODUCT | 상품 상세 | L-DETAIL | ImageSwiper + ProductInfo + Options + Accordion(정보/배송/후기/문의) + Recommend | 🔍 |
| T-FORM-ORDER | 주문서 | L-FORM | OrderItems + ShippingInfo + Coupon + PaymentMethod + Summary + Agreement | 🔍 |
| T-FORM-CLAIM | 클레임 신청 | L-FORM | ClaimType + ClaimReason + ImageUpload + ShippingInfo | 🔍 |
| T-MY-MAIN | 마이페이지 | L-MY | Profile + OrderSummary + MenuList | 🔍 |
| T-MY-ORDERS | 주문 목록 | L-LIST | OrderStatusFilter + OrderCardList | 🔍 |
| T-MY-ORDER-DETAIL | 주문 상세 | L-DETAIL | OrderInfo + ItemList + ShippingTrack + PaymentInfo + ActionButtons | 🔍 |
| T-CATEGORY-MAIN | 카테고리 | L-TAB | CategoryTab + SubCategoryChips + ProductGrid | 🔍 |
| T-CART | 장바구니 | L-FORM | SelectAll + CartItemList + PriceSummary | 🔍 |
| T-AUTH-LOGIN | 로그인 | L-FULL | Logo + SocialLogin + EmailLogin + Join | 🔍 |
| T-CONTENT-MAGAZINE | 매거진/룩북 | L-DETAIL | HeroImage + ArticleBody + RelatedProducts | 🔍 |
| T-MEMBERSHIP | 멤버십 바코드 | L-MY | BarcodeArea + MileageInfo + Benefits | ✅ |

### 5-2. Template 구성 상세 (주요 3개)

#### T-HOME-MAIN (메인 홈)

```
┌─────────────────────────────────────┐
│ [HeroBanner] 풀폭 캐러셀 (자동)      │
│  ● ○ ○ ○ ○                         │
├─────────────────────────────────────┤
│ [QuickMenu] 원형 아이콘 가로 스크롤   │
│  🔴신발  🔴의류  🔴용품  🔴키즈  🔴SALE│
├─────────────────────────────────────┤
│ [SectionHeader] NEW ARRIVALS [더보기]│
│ [ProductScroller] 수평 스크롤 카드    │
│  ┌────┐ ┌────┐ ┌────┐              │
│  │    │ │    │ │    │              │
│  └────┘ └────┘ └────┘              │
├─────────────────────────────────────┤
│ [FullBanner] 기획전 배너              │
├─────────────────────────────────────┤
│ [SectionHeader] BEST SELLERS [더보기]│
│ [ProductGrid] 2열 그리드 (4개)       │
├─────────────────────────────────────┤
│ [SectionHeader] MAGAZINE [더보기]    │
│ [ContentScroller] 매거진 카드 스크롤  │
├─────────────────────────────────────┤
│ [EventBanner] 이벤트/프로모션 배너    │
└─────────────────────────────────────┘
```

#### T-DETAIL-PRODUCT (상품 상세)

```
┌─────────────────────────────────────┐
│ [ImageSwiper] 1:1 비율, 풀폭         │
│  인디케이터 + 이미지 번호 (3/8)      │
├─────────────────────────────────────┤
│ [ProductMeta]                        │
│  [뱃지] NEW                          │
│  New Balance                         │
│  574 Core 라이프스타일 러닝화         │
│  ₩89,000                            │
│  ★★★★☆ 4.2 (128건)                 │
│  [공유] [위시]                       │
├── Divider ──────────────────────────┤
│ [OptionSelector]                     │
│  컬러: [🔴] [⚫] [⚪] [🔵]          │
│  사이즈: [230] [240] [250] [260]    │
│  (선택 시 BottomSheet 오픈)          │
├── Divider ──────────────────────────┤
│ [Accordion] 상품 정보 ∨              │
│ [Accordion] 사이즈 가이드 ∨          │
│ [Accordion] 배송/교환/반품 안내 ∨    │
├── Divider ──────────────────────────┤
│ [ReviewSection]                      │
│  상품 후기 (128)  [전체보기 >]       │
│  ★★★★☆ 4.2                        │
│  [ReviewCard] [ReviewCard]           │
├── Divider ──────────────────────────┤
│ [RecommendSection]                   │
│  이 상품과 함께 본 상품               │
│  [ProductScroller]                   │
└─────────────────────────────────────┘
```

#### T-FORM-ORDER (주문서)

```
┌─────────────────────────────────────┐
│ [OrderItemSummary]                   │
│  주문 상품 2개            [접기 ∨]   │
│  [미니 상품카드] [미니 상품카드]       │
├── Divider ──────────────────────────┤
│ [ShippingSection]                    │
│  배송지 정보             [변경]      │
│  홍*동 / 010-****-5678              │
│  서울시 강남구 테헤란로 123           │
│  [배송 메모 선택 ∨]                  │
├── Divider ──────────────────────────┤
│ [CouponSection]                      │
│  쿠폰 할인              [쿠폰 적용]  │
│  적용 쿠폰: 10% 할인쿠폰 (-₩8,900)  │
│  포인트: 12,000P         [전액사용]  │
├── Divider ──────────────────────────┤
│ [PaymentMethodSection]               │
│  결제 수단                           │
│  ○ 신용카드 (기본)                   │
│  ○ 카카오페이                        │
│  ○ 네이버페이                        │
│  ○ 계좌이체                          │
├── Divider ──────────────────────────┤
│ [PriceSummary]                       │
│  상품금액      ₩178,000             │
│  쿠폰 할인    -₩8,900               │
│  포인트 사용  -₩12,000              │
│  배송비       무료                   │
│  ─────────────────                   │
│  최종 결제금액 ₩157,100              │
├── Divider ──────────────────────────┤
│ [AgreementSection]                   │
│  □ 전체 동의                         │
│    □ 구매조건 확인 (필수)             │
│    □ 개인정보 수집·이용 (필수)        │
│    □ 마케팅 수신 동의 (선택)          │
└─────────────────────────────────────┘
```

---

## 6. Page (Template 참조)

| Page | 경로 (추정) | Template | Layout | 비고 | 확인 |
|---|---|---|---|---|---|
| 메인 홈 | / | T-HOME-MAIN | L-HOME | 앱 진입 시 첫 화면 | 🔍 |
| 카테고리 | /category | T-CATEGORY-MAIN | L-TAB | 신발/의류/용품/키즈 | 🔍 |
| 상품 목록 | /products?cat={catId} | T-LIST-PRODUCT | L-LIST | 카테고리별 상품 | 🔍 |
| 검색 | /search | T-LIST-SEARCH | L-LIST | 키워드 검색 | 🔍 |
| 상품 상세 | /products/{productId} | T-DETAIL-PRODUCT | L-DETAIL | PDP | 🔍 |
| 장바구니 | /cart | T-CART | L-FORM | | 🔍 |
| 주문서 | /order/new | T-FORM-ORDER | L-FORM | | 🔍 |
| 주문 완료 | /order/complete | (단순 결과) | L-FORM | 주문번호+안내 | 🔍 |
| 로그인 | /login | T-AUTH-LOGIN | L-FULL | 소셜+이메일 | 🔍 |
| 회원가입 | /join | (폼 Template) | L-FORM | | 🔍 |
| 마이페이지 | /my | T-MY-MAIN | L-MY | | 🔍 |
| 주문/배송 조회 | /my/orders | T-MY-ORDERS | L-LIST | | 🔍 |
| 주문 상세 | /my/orders/{orderId} | T-MY-ORDER-DETAIL | L-DETAIL | | 🔍 |
| 클레임 신청 | /my/orders/{orderId}/claim | T-FORM-CLAIM | L-FORM | 반품/교환 | 🔍 |
| 위시리스트 | /my/wish | T-LIST-PRODUCT | L-LIST | 위시 상품 목록 | 🔍 |
| 멤버십 바코드 | /my/membership | T-MEMBERSHIP | L-MY | 오프라인 매장 적립 | ✅ |
| 매거진 | /magazine/{id} | T-CONTENT-MAGAZINE | L-DETAIL | 룩북/컨텐츠 | 🔍 |
| 매장 찾기 | /stores | (지도 Template) | L-MY | NB 옴니쇼핑 연동 | ✅ |
| 상품 후기 작성 | /review/write | (폼 Template) | L-FORM | 이미지 첨부 | ✅ |
| 1:1 문의 | /my/inquiry | (폼 Template) | L-FORM | | ✅ |

---

## 7. 전체 계층 참조 구조

```
Foundation ─── Color, Typography, Spacing, Radius, Elevation, Icon
    │
    ▼
Component ─── Button, Badge, Input, Card, Navigation, Swiper, BottomSheet, ...
    │
    ▼
Pattern ───── ProductList, ProductDetail, Cart, OrderForm, MyPage, ...
    │
    ▼
Layout ────── L-HOME, L-LIST, L-DETAIL, L-FORM, L-MY, L-FULL, L-TAB
    │
    ▼
Template ──── T-HOME-MAIN, T-LIST-PRODUCT, T-DETAIL-PRODUCT, T-FORM-ORDER, ...
    │           (Layout + Pattern 조합)
    ▼
Page ──────── 메인홈, 상품목록, 상품상세, 장바구니, 주문서, 마이페이지, ...
              (Template 인스턴스 + 라우팅)
```

---

## 8. NB Korea 특이사항 (확인 기반)

| 항목 | 내용 | 확인 |
|---|---|---|
| 멤버십 바코드 | 오프라인 매장에서 적립/사용 가능한 멤버십 카드 | ✅ (Play Store) |
| NB 옴니쇼핑 | 오프라인 매장 재고 연동 — 앱에서 매장 재고 확인 | ✅ (Play Store) |
| 온라인 단독 상품 | Online Only 뱃지 — 온라인에서만 구매 가능 | ✅ (Play Store) |
| 자주 가는 매장 | 즐겨찾기 매장 등록 → 매장별 혜택 제공 | ✅ (Play Store) |
| 마일리지 통합 | 온라인+오프라인 통합 마일리지 적립/사용 | ✅ (Play Store) |
| 모바일 전용 혜택 | 앱 고객 전용 쿠폰, 이벤트 | ✅ (Play Store) |

---

## 9. runNshop 적용 시사점

| NB Korea 패턴 | runNshop 참조 포인트 |
|---|---|
| L-HOME + T-HOME-MAIN | 메인 홈 구성: Hero배너 + QuickMenu + 섹션별 수평스크롤 |
| L-DETAIL + StickyBottom | 상품 상세 하단 고정 CTA (위시/장바구니/구매) |
| L-FORM + Agreement | 주문서: 배송지→쿠폰→결제수단→금액요약→동의 순서 |
| BottomSheet 옵션선택 | 사이즈/컬러 선택 UX — 팝업 아닌 BottomSheet |
| 2열 그리드 + FilterBar | 상품 목록 기본 패턴 |
| 무한 스크롤 | 페이지네이션 대신 InfiniteScroll |
| 멤버십 바코드 | O2O 연동 (현재 runNshop 범위 외, 향후 참고) |

---

## 근거

| 항목 | 출처 |
|---|---|
| 앱 기능 설명 | [Google Play - NB Korea 앱](https://play.google.com/store/apps/details?id=com.leadon.v1.nbkorea) |
| 사이트 트래픽 | siteindices.com/nbkorea.com (월 75K UV) |
| UI 패턴 | NB Global (newbalance.com) 구조 참조 |
| 디자인 토큰 | 업계 표준 + NB 브랜드 가이드라인 추정 |
