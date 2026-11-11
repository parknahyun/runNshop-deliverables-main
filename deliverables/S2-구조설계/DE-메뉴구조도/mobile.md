# 메뉴구조도 (IA) — runNshop-mobile (고객웹)

> 상위 문서: [readme.md](readme.md)
> **단계**: 구조설계 | **문서종류**: Design | **상태**: Finalized

---

| 셸 구조 | Header + Content(App Router) + BottomNav |
|---|---|

| BottomNav/경로 | 화면(Bolt 대응) | 도메인 | 비고 |
|---|---|---|---|
| 홈 `/` | 메인(전시 페이지) (SCR-M-C04, 2026-09-28 설계완료) | Catalog(Display) | 2차 |
| 카테고리 `/category` | 카테고리 목록 · 상품목록 (SCR-M-C01) | Catalog | 2차 |
| 검색 `/search` | 검색결과 (SCR-M-C02) | Catalog | 2차 (※ 소유 도메인 정정, 아래 참조) |
| 마이페이지 `/my` | 마이페이지 허브 | Member | 3차 |
| **`/my/orders`** | 주문내역 | Order | 1차 |
| **`/my/orders/[id]`** | 주문상세 | Order | 1차 |
| **`/my/claims`** | 클레임내역 | Order | 1차 |
| `/my/wishlist` | 찜한 상품 (SCR-M-C05, 2026-11-09 소급 반영) | Catalog | 2차 |
| `/my/points` | 포인트내역 | Member | 3차 |
| `/my/coupons` | 쿠폰함 | Promotion | 2차 |
| `/my/reviews` | 내 리뷰 | Community | 3차 |
| `/my/address` | 배송지관리 | Member | 3차 |
| **`/my/payment-methods`** | 결제수단관리 | Payment | 1차 |
| `/my/settings` | 설정 | Member | 3차 |
| **장바구니 `/cart`** | 장바구니 | Order | 1차 |
| **주문서 `/checkout`** | 주문서 (배송지·결제·쿠폰) | Order | 1차 |
| **결제 `/checkout/payment`** | 결제 진행 | Payment | 1차 |
| 상품상세 `/products/[id]` | 상품상세 (SCR-M-C03) | Catalog | 2차 |
| 랭킹 `/ranking` | 상품 랭킹(실시간/일간/주간) (SCR-M-C06, 2026-11-09 신설) | Catalog | 2차 — 하단 탭 없음, 홈 배너·카테고리 화면 등에서 링크로 진입 |

---

## Catalog 화면 ↔ API 매핑 (2026-09-28 보강)

> DN-화면레이아웃/catalog-mobile.md에서 설계된 4개 화면을 경로에 연결한다.

| 경로 | 화면 (SCR-ID) | 주요 호출 API (DL §) |
|---|---|---|
| 홈 `/` | 홈 (SCR-M-C04, 2026-09-28 추가) | §32 홈 화면 조회 (섹션별 상품/이벤트배너/추천 resolve) |
| 카테고리 `/category` | 상품 목록 (SCR-M-C01) | §17 상품 목록(전시카테고리 기준, 2026-11-09 변경)·§40 카테고리 메뉴 트리 |
| 검색 `/search` | 상품 검색 (SCR-M-C02) | §18 상품 검색 |
| 상품상세 `/products/[id]` | 상품 상세 (SCR-M-C03) | §19 상세조회, §20 재입고알림신청, §35 찜 등록·해제, §37a 공유 메타데이터 |
| 찜한 상품 `/my/wishlist` | 찜한 상품 목록 (SCR-M-C05, 2026-11-09 소급 반영) | §36 찜한 상품 목록 조회 |
| 랭킹 `/ranking` | 상품 랭킹 (SCR-M-C06, 2026-11-09 신설) | §41 랭킹 조회(실시간/일간/주간) |

> **2026-11-09 소급 반영**: REQ-CAT-061~063(찜하기·SNS공유)이 2026-11-06 DBA/DD 신설 당시
> DK·DL에만 반영되고 메뉴구조도에는 등재되지 않았던 공백을 메웠다. 찜하기는 카테고리
> `/category`·상품상세 `/products/[id]` 화면 내 아이콘 액션이고, 마이페이지 "찜한 상품"만
> 신규 2depth 경로로 추가했다. 공유는 상품상세 내 아이콘 액션이라 별도 경로가 없다.

> **[Human Review] Promotion 관련**: 홈의 EVENT_LIST 섹션은 `cat_event_banner_schedule`
> (Promotion 기획전 배너 동기화 캐시)에 의존한다 — Promotion이 실제로 동기화 이벤트를
> 발행하는지, 그리고 배너 클릭 시 이동할 "기획전 상세" 화면이 Promotion 쪽에 실제로
> 존재하는지 모두 미확인 상태다. 상세는 `DF-도메인모델ERD/catalog.md`·`DBA-도메인정책서/
> catalog.md` §7.5의 Human Review 참조.

> **소유 도메인 정정 필요**: "검색" 행의 도메인이 기존 placeholder에서 **"Search"**로
> 표기돼 있었으나, 실제로 DL §18 `GET /api/mobile/v1/products/search`는 **Catalog**가
> 소유한 API다(DK-세부유스케이스/catalog.md §10). 별도 Search 도메인/서비스가 존재한다면
> Catalog가 그 앞단 BFF 역할만 하는 구조인지, 아니면 검색을 전담하는 Search 도메인이
> 실제로는 아직 설계되지 않아 임시로 Catalog API가 그 역할을 겸하고 있는 것인지 확인이
> 필요하다(Human Review — 다른 도메인 소유 영역이라 이 세션에서 임의로 정정하지 않음).

---

*근거: [readme.md](readme.md) "근거" 절 참조*
