# 프로그램 목록 — Bolt1 주문 신청 (기능 단위 상세)

> 상위 문서: [readme.md](readme.md) · 도메인 문서: [order.md](order.md) §7 · WBS: [WBS-상세설계/order.md](../../S2-구조설계/WBS-상세설계/order.md) Bolt1
> **단계**: 상세설계 (S3) | **문서범위**: Bolt (Order + Payment 접수 구간) | **문서종류**: Design
>
> **작성 목적**: Bolt1(장바구니 → 주문서 → 주문 접수 완료, 어드민 주문 목록·상세)의 프로그램(PGM-ID)을 **기능 단위**까지 풀어 구현·확인 범위를 빠짐없이 나열한다. 화면 구성(DN)·인터페이스명세(DL)·시퀀스(DM)·실제 코드(`OrderController`·`OrderService`·FE)에서 도출했다.

| 항목 | 내용 |
|---|---|
| ID | DESIGN-PGM-BOLT1 |
| 상태 | Draft (휴먼 확인 전) |
| 작성일 | 2026-10-29 |
| 범위 | WBS Bolt1 작업 항목 9개: SC01-2, SC01-3, SC02-1, SC03-10, SC05-1, SC06-1, SC07-1, SC07-2, SC37-5 |

## 0. 읽는 법

- **구분**: 프로그램을 **화면(모바일·어드민·판매자)**, **API(모바일·어드민·판매자·공통 서비스)**, **Consumer**, **Batch** 순으로 나눈다. 화면의 PGM-ID는 `SCR-*`, API는 `API-*`, 컨슈머는 `CSM-*`, 배치는 `BAT-*`다(Order [order.md](order.md) §1~4 체계).
- **기능 ID** `B1-<영역>-NN`: CART(장바구니)·SHEET(주문서)·PAY(결제하기 접수)·DONE(접수 완료·실패)·ALIST(어드민 목록)·ADET(어드민 상세)·PART(판매자)·CSM(컨슈머)·BAT(배치)·XDOM(타 도메인 연동). 한 기능이 화면과 API에 걸치면 사용자 조작 쪽은 화면, 서버 처리는 API에 따로 둔다.
- **데이터 원칙(2026-10-29)**: 주문·결제는 **DB 기준**, 타 도메인은 **Port + Mock 기본**(이미 DB 샘플이면 유지). `데이터` 열에 `DB` / `Mock` / `DB샘플`로 표시한다.
- **상태**: `구현`(프로토타입 동작) / `미구현` / `Bolt밖`(다른 Bolt 소관, 경계 확인용). 결과 표시 화면 기능은 "구현"으로 센다.
- **용어**: 판매자(VENDOR)로 통일했다(2026-10-28 확정, 2026-10-29 산출물 일괄 반영). 앱·코드의 `partner` 표기는 그대로 인용한다.

## 1. 요약

| 구분 | 영역 | 기능 수 | 구현 | 미구현 | Bolt밖 |
|---|---|---|---|---|---|
| 화면 | 모바일 화면 | 28 | 22 | 5 | 1 |
| 화면 | 어드민 화면 | 20 | 13 | 4 | 3 |
| 화면 | 판매자 화면 | 2 | 0 | 0 | 2 |
| API | 모바일 API | 24 | 18 | 6 | 0 |
| API | 어드민 API | 5 | 4 | 0 | 1 |
| API | 판매자 API | 1 | 0 | 0 | 1 |
| API | 공통 서비스 | 1 | 1 | 0 | 0 |
| Consumer | Consumer | 2 | 0 | 0 | 2 |
| Batch | Batch | 1 | 0 | 0 | 1 |
| 연동 | 타 도메인 Port | 6 | 5 | 0 | 1 |
| | **합계** | **90** | **63** | **15** | **12** |

> 미구현 15건 중 **Bolt1에서 구현할 것은 6건**이다: 장바구니 DB 저장 B1-CART-01~05(SC01-3)와 배송지 선택 B1-SHEET-06(SC37-5). 나머지 9건(B1-SHEET-13·19, B1-PAY-12, B1-DONE-06·07, B1-ALIST-09~11, B1-ADET-13)은 `WBS 항목` 열의 후속 Bolt(4·7·13·14)로 이관된 항목이다. Bolt1에는 **판매자 화면·판매자 API·배치가 직접 포함되지 않는다**(판매자는 Bolt2, 배치는 Bolt14). 구현 건은 휴먼 확인(6·7) 대기이고, 장바구니는 서버가 Mock이라 SC01-3 완료 후 재확인한다.

---

## 2. 화면 (SCR)

### 2-1. 모바일 (mobile)

> SCR-M-001 장바구니(`app/cart`, `components/cart/*`), SCR-M-002 주문서(`app/orders/new`, `components/order/*`), SCR-M-003 접수 완료, SCR-M-004 접수 실패(`app/orders/complete`·`failed`).

| 기능 ID | 기능 | 프로그램 | 동작 요약 | 데이터 | 상태 | WBS 항목 | 비고 |
|---|---|---|---|---|---|---|---|
| B1-CART-06 | 판매자별 상품 그룹 표시 | 화면 `VendorGroup` | 판매자명·배송비/무료배송 기준·상품 카드 목록 | (표시) | 구현 | SC01-2 | |
| B1-CART-07 | 상품 카드 표시 | 화면 `VendorGroup` | 이미지·상품명·옵션(색상/사이즈)·정상가(취소선)·판매가·수량·삭제 | (표시) | 구현 | SC01-2 | |
| B1-CART-08 | 품절 처리 표시 | 화면 `VendorGroup` | `status≠ON_SALE`이면 체크 불가 + "품절" 배지 + 카드 음영 | (표시) | 구현 | SC01-2 | S4 10-23 품절배지. 실재고 연동은 Bolt4 |
| B1-CART-09 | 상품 선택(체크박스) | 화면 `CartClient` | 상품·판매자·전체 선택, 선택 건수 반영 | (표시) | 구현 | SC01-2 | S4 10-23 쿠폰약관모달·체크박스 |
| B1-CART-10 | 선택 합계 재계산 | 화면 `CartSummary`·`CartClient.buildSelectedSummary` | 선택 상품 기준 상품금액·상품할인·장바구니할인·배송비·주문금액(예상) | (표시) | 구현 | SC01-2 | 조건부 할인·배송비 재계산은 미반영(Bolt4) |
| B1-CART-11 | 수량 +/- · 삭제 UI | 화면 `VendorGroup` | PATCH/DELETE 호출, 삭제 성공 시 목록·선택·건수 갱신 + "삭제되었습니다." alert, 실패 시 오류 alert | (표시) | 구현 | SC01-2 | S4 10-23 삭제·수량변경 |
| B1-CART-12 | 헤더·빈 상태·로딩 실패 | 화면 `CartBackButton` 등 | 뒤로가기, 전체 수량, 빈 장바구니 "쇼핑하러 가기", 로딩 실패 안내 | (표시) | 구현 | SC01-2 | |
| B1-CART-13 | 선택상품 주문하기(CTA) | 화면 `CartBottomBar` → API-006 | "선택상품 주문하기 · {합계}원", 선택 0건 비활성, 임시주문 생성 후 `/orders/new?sheet=` 이동, 실패 시 alert | **DB** | 구현 | SC02-1 연계 | 임시주문은 아래 B1-SHEET-01 |
| B1-SHEET-04 | 주문 상품 표시 | 화면 `OrderItemList` | 판매자별 그룹·이미지·상품명·옵션·판매가·수량(저장값) | (표시) | 구현 | SC02-1 | |
| B1-SHEET-05 | 배송지 표시 | 화면 `AddressSection` | 기본 배송지(수령인·연락처·주소) 표시 | **Mock**(Member) | 구현(고정) | SC37-5 | 현재 기본 배송지 고정 Mock |
| B1-SHEET-06 | 배송지 선택 | 화면 `AddressSection` + Member Port | [변경] → 배송지 선택 팝업(등록 목록 라디오), 선택 값을 임시주문에 저장. 주문서 직접 입력 불가 | Order 저장 **DB**, 배송지 목록 **Mock** | 미구현 | SC37-5 | 현재 [변경]은 "지원하지 않는 기능" alert. 배송지 관리는 Member |
| B1-SHEET-07 | 쿠폰 목록·선택·해제 | 화면 `CouponSection` + API-052 | 인라인 목록에서 1건 선택/해제(라디오), "상세" 모달, 서버 검증 실패 시 되돌림 | 선택 저장 **DB**, 쿠폰 데이터 **Mock**(Promotion) | 구현 | SC02-1 | 쿠폰 팝업·조합 추천(API-008·009)은 Bolt13 |
| B1-SHEET-10 | 포인트 입력·전액 사용 | 화면 `PointSection` | 보유·사용가능 표시, 입력 400ms 후 서버 저장, [전액사용], 저장 실패 시 되돌림 | (표시) | 구현 | SC02-1 | |
| B1-SHEET-13 | 포인트 최소 사용액(1,000P) | 화면+API-052 | 1,000P 미만 입력 시 안내·거부 | — | 미구현 | Bolt4 | 문서에만 있고 코드 미확인 → Bolt4(SC16-1) 이관 |
| B1-SHEET-14 | 결제수단 선택 | 화면 `PaymentMethod` | 가상계좌 기본, 카드 선택 시 "작업중" 안내·결제 차단 | (표시) | 구현 | SC03-10 | 카드·간편결제는 Bolt5·6 |
| B1-SHEET-15 | 금액 요약 | 화면 `PriceSummary` | 상품금액·쿠폰할인·배송비·주문금액·포인트·결제금액(저장값). 상품할인·장바구니할인은 0이라 미표시 | (표시) | 구현 | SC02-1 | 상품할인·배송비 계산은 Bolt4 |
| B1-SHEET-16 | 약관 동의 | 화면 `TermsAgreement`·`TermDetailModal` | 필수/선택 약관 체크, 전문 모달, 필수 미동의 시 결제하기 비활성 | (표시) | 구현 | SC03-10 | 필수 T001~T003 |
| B1-SHEET-17 | 결제하기 버튼 상태 | 화면 `OrderBottomBar` | "{결제금액}원 결제하기", 쿠폰/포인트 저장 중 클릭 시 "적용 중입니다" alert 차단 | (표시) | 구현 | SC03-10 | |
| B1-SHEET-18 | 주문서 로딩 실패 | 화면 | "주문서 정보를 불러올 수 없습니다." 안내 | (표시) | 구현 | SC02-1 | |
| B1-SHEET-19 | 결제 중 로딩·중복 클릭 방지·멱등키 | 화면+API-007 | 스피너, 더블 클릭 차단, 멱등키 | — | 미구현 | Bolt13 | SC39-3(결제 멱등·중복 결제 방지)로 이관 |
| B1-DONE-01 | 접수 결과 표시 | SCR-M-003 | 주문번호·주문금액·결제수단·접수일시 | 결제하기 응답(`sessionStorage`) | 구현 | SC05-1 | 새로고침 시 유지 안 됨 |
| B1-DONE-02 | 배송지 정보 표시 | SCR-M-003 | 수령인(마스킹)·주소 | 응답/주문서 | 구현 | SC05-1 | |
| B1-DONE-03 | 안내문·CTA | SCR-M-003 | 진행 안내 고정 문구, "주문 상세 보기"(`/my/orders/{id}`)·"쇼핑 계속하기" | — | 구현 | SC05-1 | 주문 상세는 Bolt3(SC09-1) |
| B1-DONE-04 | 접수 실패 사유·안내 | SCR-M-004 | 실패 사유(에러 message)·안내 문구·유형별 문구(VALIDATION/SYSTEM/SESSION_EXPIRED) | — | 구현 | SC03-10 | |
| B1-DONE-05 | 접수 실패 CTA | SCR-M-004 | "다시 결제하기"(주문서 복귀), "장바구니로 이동", 고객센터 안내 | — | 구현 | SC03-10 | |
| B1-DONE-06 | 접수 후 데이터 유지 | SCR-M-003 / API-015 | 새로고침 시 주문 상세 API 기반으로 복원 | **DB** | 미구현 | Bolt14 | SC29-1(진행 상태 폴링)과 함께 |
| B1-DONE-07 | 진행 상태 반영(폴링) | SCR-M-003 | 재고확인중 → 입금대기 상태 실시간 갱신 | **DB** | 미구현 | Bolt14 | SC29-1 |
| B1-DONE-08 | 가상계좌 번호·입금기한 안내 | SCR-M-003 | 발급 계좌·입금기한(12시간) 표시 | **DB** | Bolt밖 | Bolt8 | SC20-1 |

> **Bolt1 밖(참고)**: 옵션 변경(API-005, Bolt13 SC25-1), 쿠폰 목록 팝업·장바구니 할인 행사·실재고·배송비 재계산(Bolt4 SC15-1~4), 담기(API-001, Bolt13 SC01-1).

### 2-2. 어드민 (admin)

> SCR-A-001 주문 현황(`order-history/OrderHistory.tsx`), SCR-A-002 주문 상세 컨테이너와 탭 T1~T6(`OrderDetail.tsx`, `tabs/*`). 모든 탭이 화면 진입 시 한 번 호출한 API-023 응답을 나눠 쓴다.

| 기능 ID | 기능 | 프로그램 | 동작 요약 | 데이터 | 상태 | WBS 항목 | 비고 |
|---|---|---|---|---|---|---|---|
| B1-ALIST-03 | 목록 컬럼 | 화면 `OrderTable` | 주문번호(platformOrderNo)·상품명(대표 외 N건)·주문자·판매자·상태 뱃지·주문금액·주문일시 | **DB** | 구현 | SC06-1 | |
| B1-ALIST-04 | 상태 필터 | 화면 `FilterBar` | 전체/재고확인중/재고차감완료/재고부족/입금대기/결제완료/취소 | **DB** | 구현 | SC06-1 | 접수~구매확정 8종 설계안은 배송 Bolt 이후 |
| B1-ALIST-05 | 요약 카드 | 화면 `SummaryBar` | 전체·입금대기·결제완료·취소 4개 건수(검색조건 반영, 상태 선택과 무관, 0건도 표시) | **DB** | 구현 | SC06-1 | |
| B1-ALIST-06 | 페이징·페이지 크기 | 화면 `Pagination` | 10/20/50 선택, 총 건수 | **DB** | 구현 | SC06-1 | |
| B1-ALIST-07 | 행 클릭 → 상세 탭 | 화면 | 주문 상세 탭 열기 | — | 구현 | SC06-1 | |
| B1-ALIST-08 | 상태 뱃지 스타일 | 화면 | 결제완료·취소 강조 속성, 재고 3상태는 기본 스타일 | (표시) | 구현 | SC06-1 | 재고 3상태 전용 색상은 Bolt13(SC30-1) |
| B1-ALIST-09 | 재고 상태 카드·뱃지 색상 | 화면 | 재고확인중·차감완료·재고부족 카드 | — | 미구현 | Bolt13 | SC30-1 |
| B1-ALIST-10 | 엑셀 다운로드 | 화면 `Toolbar` | 목록 엑셀 내보내기 | — | 미구현 | Bolt13 | 현재 "준비 중" alert, SC30-1 |
| B1-ALIST-11 | 자동 조회 | 화면 | 진입 시 자동 조회 | — | 미구현 | Bolt13 | 현재 [조회] 클릭 시 호출 |
| B1-ADET-02 | 탭 헤더 | SCR-A-002 | 주문번호·플랫폼주문 상태 뱃지·판매자명·주문금액·주문일시, 탭 전환 | **DB** | 구현 | SC07-1 | |
| B1-ADET-03 | 주문상품 탭 | SCR-A-002-T1 | 판매자 그룹(`■ 판매자명` + 판매자 주문 상태) 아래 상품명·옵션·수량·단가·소계 | **DB** | 구현 | SC07-1 | 스냅샷 값 사용. 클레임진행/완료 컬럼은 설계안(Bolt3 이후) |
| B1-ADET-04 | 배송정보 탭 | SCR-A-002-T3 | 수령인·연락처(마스킹)·주소, 판매자별 배송사·운송장·출고일·배송상태(없으면 `-`) | **DB** | 구현 | SC07-1 | 배송 데이터는 Bolt2 |
| B1-ADET-05 | 결제정보 탭 — 금액 | SCR-A-002-T2 | 상품금액·배송비·상품할인·장바구니 할인(쿠폰)·주문금액·포인트·결제금액 | **DB** | 구현 | SC07-2 | 상품할인 현재 0 고정. 2026-10-29 용어 반영(주문금액·결제금액 행 추가, "실결제금액" 폐기) |
| B1-ADET-06 | 결제정보 탭 — 결제 | SCR-A-002-T2 | 결제수단(복합결제 "가상계좌 + 포인트")·PG사·거래 ID·상태 | **DB**(`pay_payment`) | 구현(부분 표시) | SC07-2 | 결제상태는 현재 주문상태 라벨. `pay_payment.status` 표시는 Bolt7 SC19-1 |
| B1-ADET-07 | 변경이력 탭 | SCR-A-002-T6 | 일시·대상(주문/결제/배송/클레임)·이전→이후 상태(최초 "(신규)")·변경주체·사유, 최신 역순·최신 강조 | **DB**(`ord_status_history`) | 구현 | SC07-2 | |
| B1-ADET-09 | 상태 라벨·뱃지 2종 | 화면 | 플랫폼 상태 라벨 + 판매자 주문 상태 라벨 매핑 | (표시) | 구현 | SC07-1 | S4 10-23 vendor 라벨 보강 |
| B1-ADET-11 | CS·클레임 탭 | SCR-A-002-T4 | 클레임 접수·장바구니 담아주기·예외 취소(PREPARING·송장 등록 전일 때만) | — | Bolt밖 | Bolt3·10·13 | 현재 alert 스텁 |
| B1-ADET-12 | 주문문의 탭 | SCR-A-002-T5 | 주문문의 | Mock | Bolt밖 | Bolt13 | SC39-4 |
| B1-ADET-13 | 할인 항목 명세 툴팁·PG 실데이터 | SCR-A-002-T2 | 할인 항목별 명세·PG 상세 | — | 미구현 | Bolt7·13 | SC19-1, SC31-1 |
| B1-ADET-14 | 어드민 클레임·배송 입력 | SCR-A-002 | 운송장 등록·클레임 접수 등 | — | Bolt밖 | Bolt2·3 | |

### 2-3. 판매자 (partner)

> Bolt1에 포함되는 판매자 화면은 없다. 경계 확인용으로만 적는다.

| 기능 ID | 기능 | 프로그램 | 동작 요약 | 데이터 | 상태 | WBS 항목 | 비고 |
|---|---|---|---|---|---|---|---|
| B1-PART-01 | 판매자 주문 목록 | SCR-P-001 | 판매자(VENDOR) 본인 주문 조회 화면 | DB | Bolt밖 | SC37-1 (Bolt2) | Bolt1 범위 아님 — 현재 FE 없음 |
| B1-PART-02 | 판매자 주문 상세·출고 | SCR-P-002 | 주문 상세·출고·운송장 입력 | DB | Bolt밖 | SC37-1·2 (Bolt2) | Bolt1 범위 아님 |

---

## 3. API

### 3-1. 모바일 API (`/api/mobile/v1/my/...`)

> 장바구니(API-002~004), 주문서(API-006·051·052), 결제하기(API-007). `OrderController`·`CustomerCartController`·`OrderService`·`CartService`.

| 기능 ID | 기능 | 프로그램 | 동작 요약 | 데이터 | 상태 | WBS 항목 | 비고 |
|---|---|---|---|---|---|---|---|
| B1-CART-01 | 장바구니 조회 | API-002 `GET /my/cart` | 로그인 회원의 장바구니를 판매자별로 그룹해 반환(상품·옵션·단가·수량·재고상태·배송비 기준) | **Mock → DB 전환** | 미구현(DB) | SC01-3 | 현재 `CartService.getCart()`가 Mock 파일 로드. `ord_cart` ERD는 DF에 정의됨, SQL·엔티티 없음 |
| B1-CART-02 | 수량 변경 저장 | API-003 `PATCH /my/cart/items/{id}/quantity` | 수량을 1 이상으로 갱신하고 선택 합계 재계산용 금액 반환 | **Mock → DB 전환** | 미구현(DB) | SC01-3 | 현재 서버는 Mock 계산만, 저장 없음. 화면은 PATCH 호출 후 로컬 반영 |
| B1-CART-03 | 삭제 저장 | API-004 `DELETE /my/cart/items/{id}` | 장바구니 행 삭제(본인 소유만) | **Mock → DB 전환** | 미구현(DB) | SC01-3 | 현재 Mock 응답, 화면 로컬 상태로만 반영 |
| B1-CART-04 | 장바구니 담기의 DB 영속 기반 | (API-001 기반 구조) | `ord_cart` 엔티티·리포지토리·서비스 계층, 소유자 검증, 가격 스냅샷(`price_snapshot`)·`carted_at` | **DB** | 미구현 | SC01-3 | 담기 버튼·API-001 본 구현은 Bolt13(SC01-1) |
| B1-CART-05 | 장바구니 조회·변경 권한·예외 | API-002~004 | 타인 항목 접근 403/404, 없는 항목 404, 수량 범위 검증(DL 에러코드) | **DB** | 미구현 | SC01-3 | DL #2·#3·#4 에러 정의 대응 |
| B1-SHEET-01 | 임시주문(주문서) 생성 | API-006 `POST /my/orders/sheet` | 선택 상품 검증(빈 목록 `CART_ITEMS_REQUIRED`, 수량<1·가격<0 `INVALID_ITEM_PRICE`) → `ord_platform_order`(TEMP) + 판매자별 `ord_order`·`ord_order_item`(TEMP) 저장, 플랫폼주문번호 채번, `order_sheet_id`=주문번호 반환, 상태이력 기록 | **DB** | 구현 | SC02-1 | 채번 `PyyMMdd-NNNNN-00`(동시성 보장 안 함 → 중복 방지는 Bolt13 이후 검토) |
| B1-SHEET-02 | 판매자 주문 분할 | API-006 | 판매자별 주문 분리(`orderNo`=본문+순번 01~), 금액을 판매자별로 집계 | **DB** | 구현 | SC02-1 | |
| B1-SHEET-03 | 주문서 재조회 | API-051 `GET /my/orders/sheet/{id}` | 본인 TEMP 주문만 조회(타인·비TEMP는 거부), 새로고침 시 저장값으로 재구성 | **DB** | 구현 | SC02-1 | 새 임시주문을 만들지 않음 |
| B1-SHEET-08 | 쿠폰 할인 영속 | API-052 `PUT .../sheet/{id}/discount` | 선택 쿠폰 검증 후 `ord_platform_order_discount` 저장·합계 갱신. 쿠폰 미적용 시 0 | **DB** | 구현 | SC02-1 | 검증 실패 `COUPON_NOT_APPLICABLE`(422) |
| B1-SHEET-09 | 쿠폰 할인 상한 검증 | API-052 / API-007 | 쿠폰 할인액이 상품금액 초과 시 거부 | **DB** | 구현 | SC02-1 | 동일 코드 재사용 |
| B1-SHEET-11 | 포인트 사용 영속 | API-052 | 포인트 사용액을 임시주문에 저장, 음수 거부(`INVALID_ITEM_PRICE`) | **DB** | 구현 | SC02-1 | |
| B1-SHEET-12 | 포인트 잔액·상한 검증 | API-052 / API-007 | 잔액 초과·할인 후 금액 초과 시 `POINT_EXCEED`(422) | 잔액 **Mock**(Member) | 구현 | SC02-1 | |
| B1-PAY-01 | 요청 검증 | API-007 | 배송지 필수(`ADDRESS_REQUIRED`), 필수 약관 T001~T003(`TERMS_NOT_AGREED`), 결제수단 허용값(`INVALID_PAYMENT_METHOD`), 포인트 음수 거부 | — | 구현 | SC03-10 | **미구현 부분**: 가상계좌 결제 시 환불계좌(`refundAccount`: 은행·계좌번호·예금주, 예금주=주문자, 실명 확인은 결제 요청 시점) 필수 검증 — `REFUND_ACCOUNT_REQUIRED`·`REFUND_ACCOUNT_INVALID`(REQ-PAY-031, DL §6)가 현재 `PayRequest`에 없다. 이 항목은 Bolt를 지정하지 않았다 |
| B1-PAY-02 | 결제수단 제한(카드 차단) | API-007 | `CARD` 요청 시 `PAYMENT_METHOD_NOT_READY`로 거부, 가상계좌만 진행 | — | 구현 | SC03-10 | Order가 결제수단을 하드코딩 → Bolt5 SC03-8에서 제거 대상 |
| B1-PAY-03 | 임시주문 로드·재검증 | API-007 | 요청 바디가 아니라 DB의 임시주문(TEMP, 본인 소유)에서 상품·쿠폰·포인트를 읽어 재검증 | **DB** | 구현 | SC03-10 | 바디의 couponId·pointUsed는 무시 |
| B1-PAY-04 | 금액 확정 계산 | API-007 | 상품금액 − 할인 − 포인트 + 배송비 = 결제금액 저장(`payment_amount`) | **DB** | 구현 | SC03-10 | 2026-10-29 금액 용어 반영 — `total_order_amount`(주문금액) 신설, 결제금액=`payment_amount` |
| B1-PAY-05 | 배송지 확정 저장 | API-007 | 선택 배송지를 수령인·연락처·우편번호·주소로 복사 저장 | **DB**, 배송지 원본 **Mock** | 구현 | SC03-10 | 배송지 목록은 SC37-5 |
| B1-PAY-06 | 상태 전이(TEMP → STOCK_REQUESTED) | API-007 | 플랫폼주문·판매자 주문·상품 상태를 일괄 전이, 주문일시 확정 | **DB** | 구현 | SC03-10 | |
| B1-PAY-07 | 재고차감 요청 적재 | API-007 | 같은 트랜잭션에서 `ord_outbox_event`(`STOCK_DEDUCT_REQUESTED`, payload=결제수단) 저장 | **DB** | 구현 | SC03-10 | 처리는 Bolt8 |
| B1-PAY-08 | 상태전이 이력 기록 | API-007 | `ord_status_history`에 주문 접수 이력(변경자 CUSTOMER) 추가 | **DB** | 구현 | SC03-10, SC07-2 | |
| B1-PAY-09 | 응답 반환 | API-007 | `platformOrderId`·`platformOrderNo`·`orderId`(대표)·`totalOrderAmount`(주문금액)·`totalPayment`(결제금액)·`status`(`STOCK_REQUESTED`)·`message` | — | 구현 | SC05-1 | DL §6 응답 예시와 동일 |
| B1-PAY-10 | 복합결제 행 저장(가상계좌+포인트) | API-007 → Payment | 포인트 사용분을 `POINT` 행(같은 `pay_group_no`)으로 저장 | **DB**(`pay_payment`) | 구현 | SC03-10 | S4 10-27 |
| B1-PAY-11 | 접수 실패 응답 | API-007 | 검증 실패를 에러코드·메시지로 반환 → FE가 접수 실패 화면 이동 | — | 구현 | SC03-10 | |
| B1-PAY-12 | 결제 멱등·중복 요청 방지 | API-007 | 같은 주문서 중복 결제 요청 차단 | — | 미구현 | Bolt13 | SC39-3 |

> **결제하기 접수 원칙**: 접수만 동기로 처리한다(주문 상태 `STOCK_REQUESTED`). 재고차감 → PG 요청(가상계좌 발급)은 비동기(Consumer, Bolt8).

### 3-2. 어드민 API (`/api/admin/v1/...`)

| 기능 ID | 기능 | 프로그램 | 동작 요약 | 데이터 | 상태 | WBS 항목 | 비고 |
|---|---|---|---|---|---|---|---|
| B1-ALIST-01 | 주문 검색 | API-022 `GET /admin/v1/orders` | 키워드(주문번호·상품명·주문자명 부분 일치, 대소문자 무시)·상태·기간(`ordered_at`, 종료일 포함)·페이지 조건 조회, TEMP 제외 | **DB** | 구현 | SC06-1 | 검색 규칙 2026-10-27 확정 |
| B1-ALIST-02 | 조회 조건 검증 | API-022 | `from>to` `INVALID_DATE_RANGE`, 페이지·크기 범위 `INVALID_PAGE`·`INVALID_SIZE`(크기 1~100, 기본 10) | — | 구현 | SC06-1 | |
| B1-ALIST-12 | 진행 상태(준비중~구매확정) 필터 | API-022 | 배송·확정 상태 값 | — | Bolt밖 | Bolt2·9 | 전이 로직 없어 현재 빈 결과 |
| B1-ADET-01 | 주문 상세 조회 | API-023 | 플랫폼주문 1건 + 판매자 주문·상품·배송·결제·이력을 조합해 반환, 없으면 404 | **DB**(+ 이력·문의 일부 Mock) | 구현 | SC07-1 | 판매자명 조회는 Vendor Port Mock |
| B1-ADET-10 | 금액 요약 정합 | API-023 | 주문 합계(`productAmount`·`shippingFee`·`pointUsedAmount`·`amount`)와 판매자 주문 합 일치 | **DB** | 구현 | SC07-2 | 불변식 `SUM(actual_paid_amount)=total_amount`는 신규 용어 반영 전 |

### 3-3. 판매자 API (`/api/partner/v1/...`)

> Bolt1에 포함되는 판매자 API는 없다. 경계 확인용으로만 적는다.

| 기능 ID | 기능 | 프로그램 | 동작 요약 | 데이터 | 상태 | WBS 항목 | 비고 |
|---|---|---|---|---|---|---|---|
| B1-PART-03 | 판매자 주문 목록·상세 | API-032 `GET /partner/v1/orders`, API-033 `GET /partner/v1/orders/{id}` | 코드 존재하나 판매자 주문 데이터셋은 Mock(`partner__GET_orders*.json`) | Mock | Bolt밖 | SC37-1 (Bolt2) | Bolt2에서 DB 기준으로 전환 |

### 3-4. 공통 서비스·내부 처리

| 기능 ID | 기능 | 프로그램 | 동작 요약 | 데이터 | 상태 | WBS 항목 | 비고 |
|---|---|---|---|---|---|---|---|
| B1-ADET-08 | 상태이력 기록 서비스 | `OrderStatusHistoryService.record` | 주문 생성·접수·재고차감·PG 요청 상태전이를 같은 트랜잭션에서 기록 | **DB** | 구현 | SC07-2 | 배송·클레임 전이 호출부는 해당 Bolt에서 연결 |

### 3-5. 타 도메인 연동 Port (Bolt1 기준)

| 기능 ID | 대상 | Port 메서드(코드) | Bolt1 사용처 | 데이터 | 상태 | 비고 |
|---|---|---|---|---|---|---|
| B1-XDOM-01 | Promotion | `PromotionApi.validateCoupon` | 쿠폰 선택·결제 재검증 | **Mock** | 구현 | 실연동 Bolt4 SC16-2 |
| B1-XDOM-02 | Member | `MemberApi.getPointBalance` | 포인트 잔액 검증 | **Mock**(잔액 15,000) | 구현 | 실연동 Bolt4 SC16-3 |
| B1-XDOM-03 | Member | 배송지 목록·기본 배송지(`OrderAddressMock`) | 주문서 기본 배송지·결제 시 배송지 확정 | **Mock** | 구현 | 목록·선택은 SC37-5(주문 쪽) |
| B1-XDOM-04 | Vendor | `VendorApi` 판매자명 조회 | 어드민 상세·목록 판매자명 | **Mock** | 구현 | `callWithFallback`로 장애 대체 |
| B1-XDOM-05 | Catalog | 상품·SKU 정보(장바구니·주문서 상품 표시) | 장바구니 재고·품절 상태 | **Mock** | 구현 | 장바구니 재고는 Mock, 실연동 Bolt4 SC15-1·3 |
| B1-XDOM-06 | Catalog | `CatalogApi.deductStock`·`restoreStock` | (Bolt1 호출 없음 — 접수 후 컨슈머가 호출) | **DB샘플**(`cat_sku_stock`) | Bolt밖(Bolt8) | 유지 |

---

## 4. Consumer (CSM)

> Bolt1은 아웃박스에 요청을 **적재**하는 것까지이고, 처리는 Bolt8 소관이다. 컨슈머 앱: `api/runNshop-consumer`.

| 기능 ID | 기능 | 프로그램 | 동작 요약 | 데이터 | 상태 | WBS 항목 | 비고 |
|---|---|---|---|---|---|---|---|
| B1-CSM-01 | 재고차감 처리 | CSM-005 → API-053 `POST /internal/v1/order-events/process` | 아웃박스(`STOCK_DEDUCT_REQUESTED`) 점유·SKU 단위 부분 재시도·소진 시 복원 | **DB** / Catalog **DB샘플** | Bolt밖 | SC04-1 (Bolt8) | Bolt1은 아웃박스 적재까지(B1-PAY-07) |
| B1-CSM-02 | PG 결제요청(가상계좌 발급) | CSM-006 → API-053 → `PaymentApi.requestPayment` | 재고차감 성공 후 `PAYMENT_REQUESTED` 처리, → `DEPOSIT_PENDING` | **DB** / PG **Mock** | Bolt밖 | SC04-2 (Bolt8) | |

---

## 5. Batch (BAT)

> Bolt1에 직접 포함되는 배치는 없다. 경계 확인용으로만 적는다.

| 기능 ID | 기능 | 프로그램 | 동작 요약 | 데이터 | 상태 | WBS 항목 | 비고 |
|---|---|---|---|---|---|---|---|
| B1-BAT-01 | 임시주문(TEMP) 정리 | BAT-005 | 이탈한 주문서 만료·정리(TTL) | **DB** | Bolt밖 | SC28-4 (Bolt14) | Bolt1은 TEMP 생성까지, 정리는 미구현 → TEMP 누적 |

---

## 6. 저장 구조 (Bolt1 사용 테이블)

| 테이블 | 용도 | 상태 | 비고 |
|---|---|---|---|
| `ord_cart` | 장바구니 | **신규(SC01-3)** | DF ERD에는 정의됨, SQL·엔티티 없음 |
| `ord_platform_order` | 플랫폼주문(TEMP→STOCK_REQUESTED…) | 구현 | `order-platform-order.sql` |
| `ord_platform_order_discount` | 쿠폰 할인 내역 | 구현 | |
| `ord_order` | 판매자 주문 | 구현 | `order-admin-erd-redesign.sql` |
| `ord_order_item` | 주문 상품(스냅샷) | 구현 | |
| `ord_delivery` | 배송(조회만) | 구현(조회) | Bolt2에서 `ord_shipment` 전환 여부 확인 |
| `ord_status_history` | 상태전이 이력 | 구현 | `order-status-history.sql` |
| `ord_outbox_event` | 재고차감·PG 요청 아웃박스 | 구현 | `order-stock-outbox.sql` |
| `pay_payment` | 결제(복합결제 수단별 행) | 구현 | `payment-pay-payment.sql` |

---

## 7. 확인이 필요한 점

1. **장바구니 DB 전환(B1-CART-01~05)**: SC01-3의 구현 범위를 "조회·수량·삭제"로 한정할지, 담기(API-001)의 DB 저장까지 포함할지 — 현재 WBS는 담기 본 구현만 Bolt13에 남긴다.
2. **SC37-5 배송지 선택**: 배송지 데이터는 Member Mock으로 두고, 선택값만 임시주문(`ord_platform_order`)에 저장한다는 해석이 맞는지.
3. **포인트 최소 사용액(1,000P)**(B1-SHEET-13)은 Bolt4로 보냈다. Bolt1에 넣을지 확인 필요.
4. **금액 용어 개편 반영(2026-10-29)**: 주문금액·결제금액·`total_order_amount`는 코드·ERD·DL·DN에 반영했다. 상품할인금액·상품결제금액·배송비 할인금액 컬럼은 문서(DF)에만 "신규 필요"로 두고 미구현이다(B1-PAY-04, B1-ADET-05).
5. **DL API-051·052 전용 절(해결, 2026-10-29)**: 주문서 재조회(API-051)·쿠폰/포인트 적용(API-052)은 DL §5-1·§5-2로 분리됐다(수량 변경 API-003은 DL #3에 있음). 이전 지적은 [개발 검토 문서](../../../review-alignment/개발/Bolt1_산출물목록_및_내용검토.md) F6.
6. **ADET-06 결제상태 표시**는 주문 상태 라벨로 대체 중이다(Bolt7).

---

## 8. 산출 기준 (인수 담당자용)

> 이 문서는 팀원이 Bolt1을 처음부터 진행할 때 같은 기준으로 프로그램을 도출·검증하도록 기준을 적은 것이다. 아래 기준으로 다시 도출해 이 목록과 대조하면 누락·중복을 확인할 수 있다.

### 8-1. 도출 소스와 우선순위

| 순서 | 소스 | 쓰임 |
|---|---|---|
| 1 | WBS [order.md](../../S2-구조설계/WBS-상세설계/order.md) Bolt1 작업 항목(SC*) | 범위의 기준. 항목에 없으면 Bolt1 기능이 아니다 |
| 2 | DN 화면레이아웃(mobile §1~4, admin `order-history/*`) "화면 구성" 표 | 화면 영역·조작 단위 |
| 3 | DL 인터페이스명세, DM 시퀀스, DJ GWT | API·검증 규칙·에러코드 |
| 4 | DD EARS, DBA 정책서(order·payment) | 정책·금액 규칙 |
| 5 | 코드(`OrderController`·`OrderService`·FE) | 구현 여부 판정(문서와 다르면 문서에 현행화 각주를 단다) |

### 8-2. 기능 단위 정의

- **한 행 = 사용자 조작 하나 또는 서버 처리 하나**다. 화면은 "영역(DN 화면 구성 표의 한 행) × 조작(조회·선택·입력·이동·표시 상태)", API는 "엔드포인트 × 처리 책임(검증·저장·상태 전이·응답)"으로 쪼갠다.
- 한 기능이 화면과 API에 걸치면 사용자 조작은 화면, 서버 처리는 API에 따로 둔다(예: 쿠폰 선택 = B1-SHEET-07, 영속 = B1-SHEET-08).
- 검증 규칙은 에러코드 하나당 행을 만들지 않고 같은 API의 검증 행 하나에 코드를 모아 적는다.
- 상태 표시(빈 화면·로딩 실패·품절 등)는 DN "상태별 UI" 행마다 기능으로 센다.

### 8-3. 구분 규칙

- 화면: 채널별(mobile·admin·partner), PGM-ID `SCR-*`. API: URL 소유 도메인과 채널(`/mobile/`·`/admin/`·`/partner/`·`/internal/`), `API-*`. Consumer: 이벤트를 수신·구현하는 도메인 기준, `CSM-*`. Batch: 스케줄 실행 주체 기준, `BAT-*`([order.md](order.md) §1~4와 동일).
- Bolt에 속하지 않는 기능은 삭제하지 않고 `Bolt밖`으로 두어 경계를 보인다(접수 이후 비동기, 판매자 화면 등).

### 8-4. 상태 판정

| 상태 | 기준 |
|---|---|
| 구현 | 프로토타입이 동작하고 데이터가 데이터 원칙을 만족(주문·결제는 DB) |
| 미구현 | 코드가 없거나, 주문·결제인데 Mock 응답에 머물러 있다(장바구니 서버) |
| Bolt밖 | 기능은 맞지만 WBS상 다른 Bolt 소관 |

> 처음부터 진행할 때도 **상태 열은 2026-10-29 시점의 코드 기준**이다. 재구현·재확인 범위를 정하는 참고값이지 완료 판정이 아니다. 휴먼 확인(6·7)은 구현 63건 모두 아직 받지 않았다.

### 8-5. 데이터 원칙

주문·결제(Order·Payment)는 DB 기준, 타 도메인은 Port + Mock 기본이고 DB 샘플이 이미 있으면 유지한다(WBS order.md 머리말, 2026-10-29).

### 8-6. 재산출·검증 절차

1. WBS Bolt1의 작업 항목 9개를 읽고 각 항목의 화면·API를 DN·DL에서 찾는다.
2. 8-2 기준으로 기능을 행으로 쪼개 이 목록과 대조한다. 목록에 없으면 추가, 근거 없이 있으면 삭제 후보로 표시한다.
3. 코드를 열어 8-4 기준으로 상태를 확인한다(문서와 다르면 문서를 현행화하고 S4 기록에 남긴다).
4. §7 확인이 필요한 점 6건을 휴먼 가이드로 확정한 뒤 설계 패키지(Bolt 9단계 중 1단계)를 작성한다.

### 8-7. 인수 시 먼저 정할 것

- SC01-3의 범위(담기 DB 저장 포함 여부)와 계획 시간 5.5h(제안값).
- 포인트 최소 사용액을 Bolt1에 둘지.
- 금액 용어 개편(주문금액 등)을 Bolt1에서 코드·ERD·DL에 반영할지.
- Bolt 구성(항목 이동·분할)은 휴먼이 정한다. 팀원이 바꿔야 한다면 임의로 옮기지 말고 가이드를 받는다.

---

## 근거

| 항목 | 출처 |
|---|---|
| 기능·화면 구성 | DN mobile/ §1~4, DN admin `order-history/*` |
| API·검증 규칙 | `OrderController`·`OrderService`·`CartService`·`OrderInternalController`, DL order.md #2·#3·#4·#5·#6·#15·#16 |
| 범위·상태 | WBS order.md Bolt1·§2, DQ order.md §7-1 |
| 구현 실적 | S4-구현 2026-10-08~10-27 기록 |
