# runNshop 화면 정의서

> 작성 주체: 3TOP 2본부
> 문서 버전: v1.1
> 작성일: 2026.06.26
> 상태: 초안 (Draft)

---

## 목차

1. [애플리케이션 개요](#1-애플리케이션-개요)
2. [고객 웹 (www.runNshop.com)](#2-고객-웹)
3. [플랫폼 어드민 (admin.runNshop.com)](#3-플랫폼-어드민)
4. [입점사 BO (partners.runNshop.com)](#4-입점사-bo)
5. [전체 API 목록 요약](#5-전체-api-목록-요약)
6. [화면 유형 분류](#6-화면-유형-분류)
5. [전체 API 목록 요약](#5-전체-api-목록-요약)

---

## 1. 애플리케이션 개요

| 애플리케이션 | URL | 채널 | 인증 | 대상 |
|------------|-----|------|------|------|
| 고객 웹 | www.runNshop.com | 모바일 웹 (360px) | JWT + Redis | 일반 고객 |
| 플랫폼 어드민 | admin.runNshop.com | PC 웹 | JWT + 세션 8시간 | 플랫폼 운영자 |
| 입점사 BO | partners.runNshop.com | PC 웹 | JWT + 2단계 인증 필수 + 세션 3시간 | 입점사 담당자 |

### API 접두사

| 애플리케이션 | API 접두사 |
|------------|----------|
| 고객 웹 | `/api/v1/` |
| 플랫폼 어드민 | `/api/admin/v1/` |
| 입점사 BO | `/api/partner/v1/` |

---

## 2. 고객 웹

### 2.1 공통 레이아웃

#### 레이아웃 구조

```
┌─────────────────────────────┐
│         Header               │  로고·검색·장바구니·MY
├─────────────────────────────┤
│         GNB (카테고리)        │  러닝화·의류·기어·보충제·웨어러블
├─────────────────────────────┤
│         Content              │
├─────────────────────────────┤
│    Bottom Navigation         │  홈·기획전·검색·MY
└─────────────────────────────┘
```

#### Bottom Navigation 노출 기준

| 화면 그룹 | Bottom Nav |
|---------|-----------|
| 홈·카테고리·기획전·검색·상품상세·마이페이지·커뮤니티·공지·약관 | ✅ 노출 |
| 장바구니·주문서·결제·주문완료·로그인·회원가입 | ❌ 숨김 |

#### 공통 UI 패턴

| 패턴 | 적용 화면 |
|------|---------|
| Layer Popup | 로그인·공지상세·약관·약관추가동의 |
| Bottom Sheet | 상품 옵션·수량 선택·쿠폰 선택·필터 |

---

### 2.2 상품 카드 유형

| 유형 | 사용 화면 | 이미지 | 행사아이콘 | 브랜드 | 평점 |
|------|---------|--------|---------|--------|------|
| A | 홈·카테고리·기획전·검색 | 360×360 | ✅ 좌하단 | ❌ | ✅ |
| B | 장바구니·주문서 | 80×80 | ❌ | ❌ | ❌ |
| C | 마이페이지 주문목록 | 80×80 | ❌ | ❌ | ❌ |
| D | 찜 목록 | 280×280 | ❌ | ❌ | ❌ |

#### 행사 아이콘 유형

| 유형 | 배경색 | 내용 |
|------|--------|------|
| 가격 행사 | 빨간색 | SALE N% |
| 수량 한정 | 주황색 | 선착순 N개 남음 |

---

### 2.3 기획전 카드

| 항목 | 기준 |
|------|------|
| 썸네일 | 340×200px (16:9) |
| 상태 뱃지 | 진행중(초록)·D-N(파란)·종료(회색+딤) |
| 노출 타이틀 | 최대 2줄 |

---

### 2.4 화면 목록

| 화면ID | 화면명 | URL | 비고 |
|--------|--------|-----|------|
| CUS-001 | 메인 홈 | `/` | 전시페이지 HOME |
| CUS-020 | 기획전 메인 | `/exhibitions` | 전시페이지 EXHIBITION_MAIN |
| CUS-021 | 기획전 상세 | `/exhibitions/{exhibition_code}` | |
| CUS-010 | 카테고리 목록 | `/category/{category_code}` | 전시페이지 CATEGORY |
| CUS-011 | 상품 상세 | `/products/{product_id}` | 옵션·수량 Bottom Sheet |
| CUS-030 | 통합 검색 | `/search?q={keyword}` | |
| CUS-040 | 장바구니 | `/cart` | Bottom Nav 숨김 |
| CUS-041 | 주문서 | `/orders/new` | Bottom Nav 숨김·주문전 휴대폰인증 |
| CUS-042 | 주문 접수 완료 | `/orders/complete/{platform_order_no}` | Bottom Nav 숨김 |
| CUS-050 | 마이페이지 홈 | `/my` | |
| CUS-051 | 주문 목록 | `/my/orders` | PlatformOrder 단위 |
| CUS-052 | 주문 상세 | `/my/orders/{platform_order_no}` | 3단계 클레임 액션 |
| CUS-053 | 취소 신청 | `/my/orders/{platform_order_no}/cancel` | |
| CUS-054 | 반품 신청 | `/my/orders/{order_no}/return` | 다중 선택·부분 반품 |
| CUS-055 | 교환 신청 | `/my/orders/{order_no}/exchange` | 상품 단위만 |
| CUS-056 | 클레임 상세 | `/my/claims/{claim_no}` | |
| CUS-057 | 찜 목록 | `/my/wishlist` | Type D 카드 |
| CUS-058 | 쿠폰 | `/my/coupons` | |
| CUS-059 | 포인트 | `/my/points` | |
| CUS-060 | 리뷰 관리 | `/my/reviews` | |
| CUS-061 | 리뷰 작성 | `/my/reviews/new/{order_item_id}` | 금지어·이미지 검증 |
| CUS-062 | QnA 목록 | `/my/qna` | |
| CUS-063 | 배송지 관리 | `/my/addresses` | |
| CUS-064 | 회원 정보 | `/my/profile` | |
| CUS-065 | 러닝 프로필 | `/my/running-profile` | |
| CUS-066 | 알림 설정 | `/my/notifications` | |
| CUS-070 | 상품 리뷰 목록 | `/products/{product_id}/reviews` | |
| CUS-071 | 상품 QnA 목록 | `/products/{product_id}/qna` | |
| CUS-072 | 상품 QnA 작성 | `/products/{product_id}/qna/new` | 금지어 적용 |
| CUS-080 | 로그인 | Layer Popup | 네이버·Apple만 |
| CUS-081-01 | 회원가입 - 약관동의 | `/join/terms` | |
| CUS-081-02 | 회원가입 - 가입방식 | `/join/type` | 네이버·Apple·이메일 |
| CUS-081-03 | 회원가입 - 본인인증 | `/join/verify` | 옵션널·SNS 번호 기본값 |
| CUS-081-04 | 회원가입 - 정보입력 | `/join/info` | |
| CUS-081-05 | 회원가입 - 완료 | `/join/complete` | 웰컴쿠폰 안내 |
| CUS-082 | 비밀번호 찾기 | `/find-password` | 계정 확인 후 발송 |
| CUS-083 | 공지사항 목록 | `/notices` | |
| CUS-084 | 공지사항 상세 | Layer Popup | |
| CUS-085 | 약관·정책 | Layer Popup | 갱신 시 추가동의 |

**총 38개 화면**

---

### 2.5 화면별 주요 기능

#### CUS-001 메인 홈
- 전시 페이지 템플릿 기반 동적 렌더링
- 배너 자동 슬라이드 (3초)
- 영역: 메인배너·MD추천상품·진행중기획전·신상품·브랜드배너

#### CUS-011 상품 상세
- 이미지 슬라이더
- 행사 아이콘 레이어
- 로그인 시 회원 등급 혜택 노출
- 옵션·수량 Bottom Sheet
- 품절 SKU 선택 불가
- [상품정보][리뷰][QnA] 탭

**화면별 할인가 노출 정책**

| 그룹 | 화면 | 행사가 | 공개쿠폰 | 회원등급쿠폰 | 장바구니할인 | 쿠폰 | 포인트 |
|------|------|--------|---------|------------|------------|------|--------|
| A (상품목록) | 홈·카테고리·기획전·검색·찜 | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| B (상품상세) | 상품상세 (로그인) | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ |
| C (장바구니) | 장바구니 | ✅ | ✅ | ✅ | ✅ (자동) | 안내만 | 안내만 |
| D (주문서) | 주문서·주문상세·주문목록 | 항목별 | 항목별 | 항목별 | 항목별 | 항목별 | 항목별 |

#### CUS-040 장바구니
- 입점사별 그룹핑
- 쿠폰 안내만 (적용은 주문서)
- 포인트 잔액 안내만
- 장바구니 할인 자동 적용
- 하단 고정: [선택상품 주문하기]

#### CUS-041 주문서
- 주문 전 휴대폰 OTP 인증 (세션 1회)
- 쿠폰·포인트 주문서에서 적용
- 하단 고정: 약관동의 + 최종금액 + 결제하기
- 결제하기 활성 조건: 배송지 + 결제수단 + 약관동의 + 휴대폰인증

#### CUS-052 주문 상세 — 3단계 클레임 액션

| 레벨 | 단위 | 취소 | 반품 | 교환 |
|------|------|------|------|------|
| Level 1 | PlatformOrder 전체 | ✅ | ✅ | ❌ |
| Level 2 | Order (입점사) | ✅ | ✅ | ❌ |
| Level 3 | OrderItem (상품) | ✅ | ✅ | ✅ |

#### CUS-054 반품 신청
- 다중 상품 선택 (전체선택 체크박스)
- 상품별 부분 반품 수량 선택
- 사진 첨부 최대 3장 / 1MB
- 고객 변심 시 반품 배송비 추가 결제

---

### 2.6 공통 정책

#### 이미지 업로드

| 항목 | 기준 |
|------|------|
| 최대 크기 | 1MB |
| 최대 개수 | 3개 |
| 허용 형식 | JPG·PNG·WEBP |
| 상품 포함 여부 | AWS Rekognition 비동기 분석 (2단계 차별 기능) |

#### 금지어 정책

| 유형 | 처리 | 적용 화면 |
|------|------|---------|
| BLOCK | 등록 차단 | 리뷰·QnA 작성 |
| MASK | 마스킹 저장 | 리뷰·QnA 작성 |

#### 계정 잠금 정책

| 조건 | 기간 | 해제 |
|------|------|------|
| 5회 실패 | 3일 | 자동 |

#### SNS 로그인·가입

| 제공사 | 로그인 | 가입 |
|--------|--------|------|
| 네이버 | ✅ | ✅ |
| Apple | ✅ | ✅ |

#### 약관 갱신 추가 동의

| 약관 유형 | 미동의 처리 |
|---------|-----------|
| 이용약관·개인정보처리방침 (필수) | 서비스 이용 불가 |
| 마케팅 수신 (선택) | 서비스 이용 가능 |

#### 주문 상태 고객 노출명

| 시스템 상태 | 고객 노출 |
|-----------|---------|
| TEMP / PROCESSING | 결제 진행 중 |
| PAYMENT_COMPLETED | 주문 접수 |
| PREPARING | 준비 중 |
| IN_DELIVERY | 배송 중 |
| DELIVERED | 배송 완료 |
| CONFIRMED | 구매 확정 |
| CANCELLED | 주문 취소 |
| RETURNING / RETURNED | 반품 진행중 / 완료 |
| EXCHANGING / EXCHANGED | 교환 진행중 / 완료 |

---

### 2.7 고객 웹 전체 API 목록

| # | API | Method | URL | 화면 |
|---|-----|--------|-----|------|
| 1 | 카테고리 목록 | GET | `/api/v1/categories/standard` | 공통 GNB |
| 2 | 장바구니 수량 | GET | `/api/v1/cart/count` | 공통 Header |
| 3 | 미확인 알림 수 | GET | `/api/v1/members/me/notifications/unread-count` | 공통 MY |
| 4 | 홈 전시 페이지 | GET | `/api/v1/display/pages/home` | CUS-001 |
| 5 | 기획전 메인 전시 페이지 | GET | `/api/v1/display/pages/exhibition-main` | CUS-020 |
| 6 | 기획전 목록 | GET | `/api/v1/exhibitions?status={status}` | CUS-020 |
| 7 | 기획전 상세 전시 페이지 | GET | `/api/v1/display/pages/exhibition/{exhibition_code}` | CUS-021 |
| 8 | 카테고리 전시 페이지 | GET | `/api/v1/display/pages/category/{category_code}` | CUS-010 |
| 9 | 카테고리 상품 목록 | GET | `/api/v1/categories/{category_code}/products` | CUS-010 |
| 10 | 카테고리 필터 옵션 | GET | `/api/v1/categories/{category_code}/filters` | CUS-010 |
| 11 | 상품 상세 | GET | `/api/v1/products/{product_id}` | CUS-011 |
| 12 | 상품 가격 | GET | `/api/v1/products/{product_id}/price` | CUS-011 |
| 13 | 상품 SKU 목록 | GET | `/api/v1/products/{product_id}/skus` | CUS-011 |
| 14 | 상품 상세 소개 | GET | `/api/v1/products/{product_id}/detail` | CUS-011 |
| 15 | 수량 할인 조회 | GET | `/api/v1/promotions/quantity-discount/{vendor_id}` | CUS-011 |
| 16 | 장바구니 담기 | POST | `/api/v1/cart/items` | CUS-011 |
| 17 | 찜 등록 | POST | `/api/v1/members/me/wishlist/{product_id}` | CUS-011 |
| 18 | 찜 해제 | DELETE | `/api/v1/members/me/wishlist/{product_id}` | CUS-011 |
| 19 | 찜 여부 확인 | GET | `/api/v1/members/me/wishlist/{product_id}/status` | CUS-011 |
| 20 | 상품 리뷰 요약 | GET | `/api/v1/products/{product_id}/reviews/summary` | CUS-011 |
| 21 | 상품 QnA 목록 (미리보기) | GET | `/api/v1/products/{product_id}/qna` | CUS-011 |
| 22 | 자동완성 | GET | `/api/v1/search/autocomplete?q={keyword}` | CUS-030 |
| 23 | 인기 검색어 | GET | `/api/v1/search/keywords/popular` | CUS-030 |
| 24 | 통합 검색 | GET | `/api/v1/search?q={keyword}&type={type}` | CUS-030 |
| 25 | 상품 검색 | GET | `/api/v1/search/products?q={keyword}` | CUS-030 |
| 26 | 기획전 검색 | GET | `/api/v1/search/exhibitions?q={keyword}` | CUS-030 |
| 27 | 장바구니 조회 | GET | `/api/v1/cart` | CUS-040 |
| 28 | 장바구니 수량 변경 | PUT | `/api/v1/cart/items/{cart_item_id}` | CUS-040 |
| 29 | 장바구니 삭제 | DELETE | `/api/v1/cart/items/{cart_item_id}` | CUS-040 |
| 30 | 장바구니 전체 삭제 | DELETE | `/api/v1/cart/items` | CUS-040 |
| 31 | 쿠폰 혜택 안내 | GET | `/api/v1/members/me/coupons/benefit-summary?cart=true` | CUS-040 |
| 32 | 포인트 잔액 (장바구니) | GET | `/api/v1/members/me/points/balance` | CUS-040 |
| 33 | 장바구니 금액 계산 | POST | `/api/v1/cart/calculate` | CUS-040 |
| 34 | 장바구니 병합 | POST | `/api/v1/cart/merge` | CUS-040 |
| 35 | 주문서 생성 | POST | `/api/v1/orders/sheet` | CUS-041 |
| 36 | 배송지 목록 | GET | `/api/v1/members/me/addresses` | CUS-041 |
| 37 | 적용 가능 쿠폰 | GET | `/api/v1/members/me/coupons/available?order=true` | CUS-041 |
| 38 | 주문 금액 계산 | POST | `/api/v1/orders/calculate` | CUS-041 |
| 39 | 결제 요청 | POST | `/api/v1/payments` | CUS-041 |
| 40 | 주문 완료 조회 | GET | `/api/v1/orders/{platform_order_no}/complete` | CUS-042 |
| 41 | 마이페이지 요약 | GET | `/api/v1/members/me/summary` | CUS-050 |
| 42 | 주문 목록 | GET | `/api/v1/members/me/orders?period={period}` | CUS-051 |
| 43 | 주문 상세 | GET | `/api/v1/members/me/orders/{platform_order_no}` | CUS-052 |
| 44 | 구매 확정 | POST | `/api/v1/orders/{order_no}/items/{order_item_id}/confirm` | CUS-052 |
| 45 | 배송 추적 | GET | `/api/v1/orders/{order_no}/delivery/tracking` | CUS-052 |
| 46 | 전체 취소 | POST | `/api/v1/platform-orders/{platform_order_no}/cancel` | CUS-053 |
| 47 | 입점사 취소 | POST | `/api/v1/orders/{order_no}/cancel` | CUS-053 |
| 48 | 개별 취소 | POST | `/api/v1/orders/{order_no}/items/{order_item_id}/cancel` | CUS-053 |
| 49 | 반품 신청 | POST | `/api/v1/orders/{order_no}/return` | CUS-054 |
| 50 | 반품 배송비 결제 | POST | `/api/v1/claims/{claim_no}/extra-payment` | CUS-054 |
| 51 | 환불 예정금액 계산 | POST | `/api/v1/orders/{order_no}/refund-estimate` | CUS-054 |
| 52 | 교환 신청 | POST | `/api/v1/orders/{order_no}/items/{order_item_id}/exchange` | CUS-055 |
| 53 | 클레임 상세 | GET | `/api/v1/members/me/claims/{claim_no}` | CUS-056 |
| 54 | 찜 목록 | GET | `/api/v1/members/me/wishlist` | CUS-057 |
| 55 | 쿠폰 목록 | GET | `/api/v1/members/me/coupons?status={status}` | CUS-058 |
| 56 | 포인트 이력 | GET | `/api/v1/members/me/points?type={type}` | CUS-059 |
| 57 | 리뷰 작성 가능 목록 | GET | `/api/v1/members/me/reviews/writable` | CUS-060 |
| 58 | 작성 리뷰 목록 | GET | `/api/v1/members/me/reviews` | CUS-060 |
| 59 | 리뷰 삭제 | DELETE | `/api/v1/members/me/reviews/{review_id}` | CUS-060 |
| 60 | 리뷰 등록 | POST | `/api/v1/products/{product_id}/reviews` | CUS-061 |
| 61 | 리뷰 수정 | PUT | `/api/v1/members/me/reviews/{review_id}` | CUS-061 |
| 62 | 이미지 업로드 | POST | `/api/v1/uploads/images` | CUS-061·054·055 |
| 63 | 금지어 검증 | POST | `/api/v1/content/validate` | CUS-061·072 |
| 64 | 내 QnA 목록 | GET | `/api/v1/members/me/qna?type={type}` | CUS-062 |
| 65 | 배송지 등록 | POST | `/api/v1/members/me/addresses` | CUS-063 |
| 66 | 배송지 수정 | PUT | `/api/v1/members/me/addresses/{address_id}` | CUS-063 |
| 67 | 배송지 삭제 | DELETE | `/api/v1/members/me/addresses/{address_id}` | CUS-063 |
| 68 | 기본 배송지 설정 | PUT | `/api/v1/members/me/addresses/{address_id}/default` | CUS-063 |
| 69 | 회원 정보 조회 | GET | `/api/v1/members/me` | CUS-064 |
| 70 | 회원 정보 수정 | PUT | `/api/v1/members/me` | CUS-064 |
| 71 | 비밀번호 변경 | PUT | `/api/v1/members/me/password` | CUS-064 |
| 72 | 휴대폰 변경 | PUT | `/api/v1/members/me/phone` | CUS-064 |
| 73 | 회원 탈퇴 | DELETE | `/api/v1/members/me` | CUS-064 |
| 74 | 러닝 프로필 조회 | GET | `/api/v1/members/me/running-profile` | CUS-065 |
| 75 | 러닝 프로필 저장 | PUT | `/api/v1/members/me/running-profile` | CUS-065 |
| 76 | 알림 설정 조회 | GET | `/api/v1/members/me/notification-preferences` | CUS-066 |
| 77 | 알림 설정 변경 | PUT | `/api/v1/members/me/notification-preferences` | CUS-066 |
| 78 | 리뷰 목록 | GET | `/api/v1/products/{product_id}/reviews` | CUS-070 |
| 79 | 상품 QnA 목록 | GET | `/api/v1/products/{product_id}/qna` | CUS-071 |
| 80 | QnA 등록 | POST | `/api/v1/products/{product_id}/qna` | CUS-072 |
| 81 | 이메일 로그인 | POST | `/api/v1/auth/login` | CUS-080 |
| 82 | SNS 로그인 | POST | `/api/v1/auth/social/{provider}` | CUS-080 |
| 83 | 로그아웃 | POST | `/api/v1/auth/logout` | CUS-080 |
| 84 | 토큰 갱신 | POST | `/api/v1/auth/refresh` | CUS-080 |
| 85 | 약관 동의 여부 확인 | GET | `/api/v1/members/me/terms/check` | CUS-080 |
| 86 | 약관 최신 버전 | GET | `/api/v1/terms/latest` | CUS-081-01 |
| 87 | 인증번호 발송 | POST | `/api/v1/auth/phone/send` | CUS-081-03·041·082 |
| 88 | 인증번호 확인 | POST | `/api/v1/auth/phone/verify` | CUS-081-03·041·082 |
| 89 | 휴대폰 중복 확인 | POST | `/api/v1/auth/phone/check` | CUS-081-03 |
| 90 | 이메일 중복 확인 | POST | `/api/v1/auth/email/check` | CUS-081-04 |
| 91 | 회원가입 | POST | `/api/v1/auth/join` | CUS-081-05 |
| 92 | 웰컴 쿠폰 조회 | GET | `/api/v1/members/me/coupons/welcome` | CUS-081-05 |
| 93 | 회원 존재 확인 | POST | `/api/v1/auth/member/check` | CUS-082 |
| 94 | 비밀번호 찾기 이메일 | POST | `/api/v1/auth/password/email` | CUS-082 |
| 95 | 비밀번호 찾기 휴대폰 | POST | `/api/v1/auth/password/phone` | CUS-082 |
| 96 | 비밀번호 재설정 | POST | `/api/v1/auth/password/reset` | CUS-082 |
| 97 | 공지사항 목록 | GET | `/api/v1/notices?target=CUSTOMER&type={type}` | CUS-083 |
| 98 | 팝업 공지 조회 | GET | `/api/v1/notices/popup` | CUS-083 |
| 99 | 공지사항 상세 | GET | `/api/v1/notices/{notice_id}` | CUS-084 |
| 100 | 약관 상세 | GET | `/api/v1/terms/{terms_type}/latest` | CUS-085 |
| 101 | 약관 추가 동의 | POST | `/api/v1/members/me/terms/agree` | CUS-085 |

**고객 웹 총 101개 API**

---

## 3. 플랫폼 어드민

### 3.1 공통 레이아웃

```
┌──────────────────────────────────────────────────┐
│  [로고/홈] [메뉴1▼] ... [메뉴9▼]  [운영자·알림·로그아웃] │
├──────────────────────────────────────────────────┤
│  [🏠 홈] [탭1 ×] [탭2 ×] ... (최대 9개)         │
├──────────────────────────────────────────────────┤
│  Breadcrumb                                       │
├──────────────────────────────────────────────────┤
│                   Content                         │
└──────────────────────────────────────────────────┘
```

#### 탭 정책

| 항목 | 기준 |
|------|------|
| 홈 탭 | 로고 클릭·첫 번째 고정·닫기 불가 |
| 최대 탭 수 | 9개 (홈 탭 제외) |
| 탭 초과 시 | 가장 오래된 탭 LRU 자동 닫힘 |
| 탭 중복 | 동일 화면 재진입 시 기존 탭 활성화 |
| 탭 더블클릭 | 현재 탭 리로드 |

#### Layer Popup 패턴

```
모든 상세·등록·수정 화면 → Layer Popup
목록 화면에서 진입
독립 URL 없음
```

### 3.2 롤별 메뉴 접근 권한

| 메뉴 | 슈퍼 | MD | CS | 정산 | 입점관리 |
|------|------|----|----|------|---------|
| 상품 관리 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 프로모션 관리 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 주문 관리 | ✅ | ❌ | ✅ | ❌ | ❌ |
| 회원 관리 | ✅ | ❌ | ✅ | ❌ | ❌ |
| 입점사 관리 | ✅ | ❌ | ❌ | ❌ | ✅ |
| 정산 관리 | ✅ | ❌ | ❌ | ✅ | ❌ |
| 커뮤니티 관리 | ✅ | ✅ | ✅ | ❌ | ❌ |
| 운영 설정 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 시스템 관리 | ✅ | ❌ | ❌ | ❌ | ❌ |

### 3.3 메뉴 트리

```
인증
  ├─ ADM-000-001 로그인
  ├─ ADM-000-002 운영자 신청
  └─ ADM-000-003 비밀번호 변경 (최초)

홈 탭 (ADM-HOME)

1. 상품 관리
  ├─ ADM-020-001 상품 심사
  ├─ ADM-020-002 상품 목록
  ├─ ADM-020-003 표준 카테고리
  ├─ ADM-020-004 전시 카테고리
  ├─ ADM-020-005 카테고리 매핑
  ├─ ADM-020-006 브랜드 관리
  ├─ ADM-020-007 전시 페이지 목록 (예약 기능 포함)
  ├─ ADM-020-008 페이지 템플릿 관리
  ├─ ADM-020-009 상품 상세 타입 관리
  └─ ADM-020-010 섹션종류 관리

2. 프로모션 관리
  ├─ ADM-030-001 기획전
  ├─ ADM-030-002 행사가
  ├─ ADM-030-003 쿠폰
  ├─ ADM-030-004 수량 할인
  ├─ ADM-030-005 장바구니 할인
  └─ ADM-030-006 프로모션 그룹

3. 주문 관리
  ├─ ADM-040-001 주문 목록 (CS 클레임접수·장바구니담아주기)
  └─ ADM-040-002 클레임 목록

4. 회원 관리
  ├─ ADM-050-001 회원 목록 (필수 검색어·접근이력 기록)
  └─ ADM-050-002 등급 기준 관리

5. 입점사 관리
  ├─ ADM-060-001 입점 신청 심사
  ├─ ADM-060-002 입점사 목록
  └─ ADM-060-003 배송사 관리

6. 정산 관리
  ├─ ADM-070-001 정산 목록
  ├─ ADM-070-002 지급 관리
  └─ ADM-070-003 외부 정산

7. 커뮤니티 관리
  ├─ ADM-080-001 리뷰 관리
  └─ ADM-080-002 QnA 관리

8. 운영 설정
  ├─ ADM-090-001 운영자 계정 목록
  ├─ ADM-090-002 운영자 신청 승인
  ├─ ADM-090-003 권한·프로그램 관리
  ├─ ADM-090-004 공통코드 관리
  ├─ ADM-090-005 알림 템플릿
  ├─ ADM-090-006 금지어 관리
  ├─ ADM-090-007 공지사항 관리
  ├─ ADM-090-008 약관 관리
  ├─ ADM-090-009 배너 관리
  └─ ADM-090-010 고객정보 접근 이력

9. 시스템 관리
  ├─ ADM-100-001 배치 관리
  ├─ ADM-100-002 Outbox·DLQ 관리
  └─ ADM-100-003 감사 로그
```

### 3.4 주요 특이사항

#### 홈 탭 노출 항목
- 신규주문·신규회원·클레임 카드 (매출금액 제외)
- 진행중 이벤트 (기획전·행사가·쿠폰 유형별)
- 판매 상품 현황 (판매중·품절·심사중)
- 처리 필요 항목 (롤별 차등)
- 주문 추이 차트
- 시스템 알림 (슈퍼관리자만)

#### ADM-020-010 섹션종류 관리

| 화면 | 화면유형 | 스펙 파일 |
|------|---------|----------|
| 섹션종류 목록 | 목록 (table) | `apps/runNshop-admin/src/display/section/SectionTypePage.spec.md` |
| 섹션종류 상세 | 상세 모달 (InnerTabs) | `apps/runNshop-admin/src/display/section/SectionTypeDetail.spec.md` |
| 섹션종류 등록 | 등록 모달 (InnerTabs) | `apps/runNshop-admin/src/display/section/AddSectionTypeModal.spec.md` |
| 기본정보 탭 | 탭 (읽기/편집/등록) | `apps/runNshop-admin/src/display/section/tabs/BasicInfoTab.spec.md` |
| 필드관리 탭 | 탭 (CRUD + 순서변경) | `apps/runNshop-admin/src/display/section/tabs/FieldsTab.spec.md` |
| 필드 추가/편집 | 서브 모달 | `apps/runNshop-admin/src/display/section/tabs/AddFieldModal.spec.md` |

- 목록: 조회 버튼 클릭 후 테이블 노출, 필터(키워드+상태), 요약카드(전체/활성/비활성)
- 상세/등록: 동일한 InnerTabs 구조 (기본정보 + 필드관리)
- 필드관리: 로컬 state 기반 CRUD, 순서변경(↑↓), 최종 저장 시 API 일괄 전송
- 스펙 확인: 각 화면 타이틀 옆 `?` 버튼 → API Route로 .spec.md 읽어서 모달 표시

#### 전시 페이지 예약 기능
- 페이지당 최대 1개 예약
- 예약 시각 도래 시 배치 자동 전환
- 예약 상태: PENDING·APPLIED·CANCELLED
- PostgreSQL 조건부 유니크 인덱스

#### 카테고리 매핑
- 표준→전시 카테고리 N:M 매핑
- is_default: 상품 등록 시 자동 선택 여부
- 우선순위: BRAND(2) > CATEGORY(1) > DEFAULT(0)

#### 회원 목록 검색
- 이름·이메일·휴대폰 중 1개 필수
- 검색 전 목록 미노출
- 조회 시 adt_member_access_log 자동 기록

#### 개인정보 접근 이력 기록 대상

| 화면 | access_type | target_type |
|------|------------|------------|
| 회원 목록 검색 | LIST | MEMBER |
| 회원 상세 조회 | DETAIL | MEMBER |
| 주문 목록 검색 | LIST | ORDER |
| 주문 상세 조회 | DETAIL | ORDER |
| 클레임 목록 검색 | LIST | CLAIM |
| 클레임 상세 조회 | DETAIL | CLAIM |
| 포인트 지급 | ACTION | MEMBER_POINT |
| 쿠폰 발급 | ACTION | MEMBER_COUPON |
| 상태 변경 | ACTION | MEMBER |
| 장바구니 교체 | ACTION | CART_REPLACE |

#### 주문 상세 CS 기능
- 클레임 접수 (고객과 동일 3단계 + CS 귀책 선판단)
- 장바구니 담아주기 (기존 장바구니 삭제 후 교체)
- 예외 취소 처리

### 3.5 플랫폼 어드민 전체 API 목록

| # | API | Method | URL | 화면 |
|---|-----|--------|-----|------|
| 1 | 운영자 로그인 | POST | `/api/admin/v1/auth/login` | ADM-000-001 |
| 2 | 토큰 갱신 | POST | `/api/admin/v1/auth/refresh` | 공통 |
| 3 | 로그아웃 | POST | `/api/admin/v1/auth/logout` | 공통 |
| 4 | 운영자 신청 | POST | `/api/admin/v1/auth/apply` | ADM-000-002 |
| 5 | 이메일 중복 확인 | POST | `/api/admin/v1/auth/email/check` | ADM-000-002 |
| 6 | 홈 요약 | GET | `/api/admin/v1/home/summary` | ADM-HOME |
| 7 | 처리 필요 항목 | GET | `/api/admin/v1/home/pending` | ADM-HOME |
| 8 | 주문·매출 추이 | GET | `/api/admin/v1/home/trend?days=7` | ADM-HOME |
| 9 | 시스템 알림 | GET | `/api/admin/v1/home/alerts` | ADM-HOME |
| 10 | 진행 중 이벤트 | GET | `/api/admin/v1/home/events/active` | ADM-HOME |
| 11 | 판매 상품 현황 | GET | `/api/admin/v1/home/products/summary` | ADM-HOME |
| 12 | 심사 목록 | GET | `/api/admin/v1/products/review` | ADM-020-001 |
| 13 | 심사 상세 | GET | `/api/admin/v1/products/{id}/review` | ADM-020-001 |
| 14 | 심사 승인 | PUT | `/api/admin/v1/products/{id}/approve` | ADM-020-001 |
| 15 | 심사 반려 | PUT | `/api/admin/v1/products/{id}/reject` | ADM-020-001 |
| 16 | 일괄 승인 | PUT | `/api/admin/v1/products/bulk-approve` | ADM-020-001 |
| 17 | 일괄 반려 | PUT | `/api/admin/v1/products/bulk-reject` | ADM-020-001 |
| 18 | 심사 엑셀 | GET | `/api/admin/v1/products/review/excel` | ADM-020-001 |
| 19 | 상품 목록 | GET | `/api/admin/v1/products` | ADM-020-002 |
| 20 | 상품 상세 | GET | `/api/admin/v1/products/{id}` | ADM-020-002 |
| 21 | 상품 수정 | PUT | `/api/admin/v1/products/{id}` | ADM-020-002 |
| 22 | 상태 변경 | PUT | `/api/admin/v1/products/{id}/status` | ADM-020-002 |
| 23 | 재고 조정 | PUT | `/api/admin/v1/products/{id}/skus/{sku_id}/stock` | ADM-020-002 |
| 24 | 노출 설정 | PUT | `/api/admin/v1/products/{id}/exposure` | ADM-020-002 |
| 25 | 상품 엑셀 | GET | `/api/admin/v1/products/excel` | ADM-020-002 |
| 26 | 표준카테고리 목록 | GET | `/api/admin/v1/categories/standard` | ADM-020-003 |
| 27 | 표준카테고리 등록 | POST | `/api/admin/v1/categories/standard` | ADM-020-003 |
| 28 | 표준카테고리 수정 | PUT | `/api/admin/v1/categories/standard/{id}` | ADM-020-003 |
| 29 | 표준카테고리 삭제 | DELETE | `/api/admin/v1/categories/standard/{id}` | ADM-020-003 |
| 30 | 전시카테고리 목록 | GET | `/api/admin/v1/categories/display` | ADM-020-004 |
| 31 | 전시카테고리 등록 | POST | `/api/admin/v1/categories/display` | ADM-020-004 |
| 32 | 전시카테고리 수정 | PUT | `/api/admin/v1/categories/display/{id}` | ADM-020-004 |
| 33 | 전시카테고리 삭제 | DELETE | `/api/admin/v1/categories/display/{id}` | ADM-020-004 |
| 34 | 카테고리 매핑 목록 | GET | `/api/admin/v1/categories/mappings` | ADM-020-005 |
| 35 | 카테고리 매핑 등록 | POST | `/api/admin/v1/categories/mappings` | ADM-020-005 |
| 36 | 카테고리 매핑 수정 | PUT | `/api/admin/v1/categories/mappings/{id}` | ADM-020-005 |
| 37 | 카테고리 매핑 삭제 | DELETE | `/api/admin/v1/categories/mappings/{id}` | ADM-020-005 |
| 38 | 자동 매핑 조회 | GET | `/api/admin/v1/categories/standard/{id}/display-mappings` | ADM-020-005 |
| 39 | 브랜드 목록 | GET | `/api/admin/v1/brands` | ADM-020-006 |
| 40 | 브랜드 등록 | POST | `/api/admin/v1/brands` | ADM-020-006 |
| 41 | 브랜드 수정 | PUT | `/api/admin/v1/brands/{id}` | ADM-020-006 |
| 42 | 브랜드 삭제 | DELETE | `/api/admin/v1/brands/{id}` | ADM-020-006 |
| 43 | 페이지 목록 | GET | `/api/admin/v1/display/pages` | ADM-020-007 |
| 44 | 페이지 등록 | POST | `/api/admin/v1/display/pages` | ADM-020-007 |
| 45 | 페이지 수정 | PUT | `/api/admin/v1/display/pages/{id}` | ADM-020-007 |
| 46 | 페이지 삭제 | DELETE | `/api/admin/v1/display/pages/{id}` | ADM-020-007 |
| 47 | 영역 수정 | PUT | `/api/admin/v1/display/pages/{id}/areas/{area_id}` | ADM-020-007 |
| 48 | 예약 목록 | GET | `/api/admin/v1/display/pages/{id}/schedules` | ADM-020-007 |
| 49 | 예약 등록 | POST | `/api/admin/v1/display/pages/{id}/schedules` | ADM-020-007 |
| 50 | 예약 취소 | PUT | `/api/admin/v1/display/pages/{id}/schedules/{schedule_id}/cancel` | ADM-020-007 |
| 51 | 예약 미리보기 | GET | `/api/admin/v1/display/pages/{id}/schedules/{schedule_id}/preview` | ADM-020-007 |
| 52 | 템플릿 목록 | GET | `/api/admin/v1/display/templates` | ADM-020-008 |
| 53 | 템플릿 등록 | POST | `/api/admin/v1/display/templates` | ADM-020-008 |
| 54 | 템플릿 수정 | PUT | `/api/admin/v1/display/templates/{id}` | ADM-020-008 |
| 55 | 템플릿 삭제 | DELETE | `/api/admin/v1/display/templates/{id}` | ADM-020-008 |
| 56 | 타입 목록 | GET | `/api/admin/v1/product-detail-types` | ADM-020-009 |
| 57 | 타입 등록 | POST | `/api/admin/v1/product-detail-types` | ADM-020-009 |
| 58 | 타입 수정 | PUT | `/api/admin/v1/product-detail-types/{id}` | ADM-020-009 |
| 59 | 타입 삭제 | DELETE | `/api/admin/v1/product-detail-types/{id}` | ADM-020-009 |
| 60 | 매핑 등록 | POST | `/api/admin/v1/product-detail-types/{id}/mappings` | ADM-020-009 |
| 61 | 매핑 삭제 | DELETE | `/api/admin/v1/product-detail-types/{id}/mappings/{mapping_id}` | ADM-020-009 |
| 62 | 기획전 목록 | GET | `/api/admin/v1/exhibitions` | ADM-030-001 |
| 63 | 기획전 상세 | GET | `/api/admin/v1/exhibitions/{id}` | ADM-030-001 |
| 64 | 기획전 등록 | POST | `/api/admin/v1/exhibitions` | ADM-030-001 |
| 65 | 기획전 수정 | PUT | `/api/admin/v1/exhibitions/{id}` | ADM-030-001 |
| 66 | 기획전 삭제 | DELETE | `/api/admin/v1/exhibitions/{id}` | ADM-030-001 |
| 67 | 기획전 상품 추가 | POST | `/api/admin/v1/exhibitions/{id}/products` | ADM-030-001 |
| 68 | 기획전 상품 제거 | DELETE | `/api/admin/v1/exhibitions/{id}/products/{product_id}` | ADM-030-001 |
| 69 | 행사가 목록 | GET | `/api/admin/v1/event-prices` | ADM-030-002 |
| 70 | 행사가 상세 | GET | `/api/admin/v1/event-prices/{id}` | ADM-030-002 |
| 71 | 행사가 등록 | POST | `/api/admin/v1/event-prices` | ADM-030-002 |
| 72 | 행사가 수정 | PUT | `/api/admin/v1/event-prices/{id}` | ADM-030-002 |
| 73 | 행사가 삭제 | DELETE | `/api/admin/v1/event-prices/{id}` | ADM-030-002 |
| 74 | 쿠폰 목록 | GET | `/api/admin/v1/coupons` | ADM-030-003 |
| 75 | 쿠폰 상세 | GET | `/api/admin/v1/coupons/{id}` | ADM-030-003 |
| 76 | 쿠폰 등록 | POST | `/api/admin/v1/coupons` | ADM-030-003 |
| 77 | 쿠폰 수정 | PUT | `/api/admin/v1/coupons/{id}` | ADM-030-003 |
| 78 | 쿠폰 삭제 | DELETE | `/api/admin/v1/coupons/{id}` | ADM-030-003 |
| 79 | 쿠폰 발급 | POST | `/api/admin/v1/coupons/{id}/issue` | ADM-030-003 |
| 80 | 수량할인 목록 | GET | `/api/admin/v1/quantity-discounts` | ADM-030-004 |
| 81 | 수량할인 상세 | GET | `/api/admin/v1/quantity-discounts/{id}` | ADM-030-004 |
| 82 | 수량할인 등록 | POST | `/api/admin/v1/quantity-discounts` | ADM-030-004 |
| 83 | 수량할인 수정 | PUT | `/api/admin/v1/quantity-discounts/{id}` | ADM-030-004 |
| 84 | 수량할인 삭제 | DELETE | `/api/admin/v1/quantity-discounts/{id}` | ADM-030-004 |
| 85 | 장바구니할인 목록 | GET | `/api/admin/v1/cart-discounts` | ADM-030-005 |
| 86 | 장바구니할인 상세 | GET | `/api/admin/v1/cart-discounts/{id}` | ADM-030-005 |
| 87 | 장바구니할인 등록 | POST | `/api/admin/v1/cart-discounts` | ADM-030-005 |
| 88 | 장바구니할인 수정 | PUT | `/api/admin/v1/cart-discounts/{id}` | ADM-030-005 |
| 89 | 장바구니할인 삭제 | DELETE | `/api/admin/v1/cart-discounts/{id}` | ADM-030-005 |
| 90 | 그룹 목록 | GET | `/api/admin/v1/promotion-groups` | ADM-030-006 |
| 91 | 그룹 상세 | GET | `/api/admin/v1/promotion-groups/{id}` | ADM-030-006 |
| 92 | 그룹 등록 | POST | `/api/admin/v1/promotion-groups` | ADM-030-006 |
| 93 | 그룹 수정 | PUT | `/api/admin/v1/promotion-groups/{id}` | ADM-030-006 |
| 94 | 그룹 삭제 | DELETE | `/api/admin/v1/promotion-groups/{id}` | ADM-030-006 |
| 95 | 프로모션 추가 | POST | `/api/admin/v1/promotion-groups/{id}/items` | ADM-030-006 |
| 96 | 프로모션 제거 | DELETE | `/api/admin/v1/promotion-groups/{id}/items/{item_id}` | ADM-030-006 |
| 97 | 주문 목록 | GET | `/api/admin/v1/orders` | ADM-040-001 |
| 98 | 주문 상세 | GET | `/api/admin/v1/orders/{platform_order_no}` | ADM-040-001 |
| 99 | 주문 상태 변경 | PUT | `/api/admin/v1/orders/{order_no}/status` | ADM-040-001 |
| 100 | 예외 취소 | POST | `/api/admin/v1/orders/{order_no}/exception-cancel` | ADM-040-001 |
| 101 | 주문 처리 이력 | GET | `/api/admin/v1/orders/{platform_order_no}/history` | ADM-040-001 |
| 102 | CS 클레임 접수 | POST | `/api/admin/v1/orders/{order_no}/claims` | ADM-040-001 |
| 103 | 장바구니 교체 | POST | `/api/admin/v1/members/{member_id}/cart/replace` | ADM-040-001 |
| 104 | 주문 엑셀 | GET | `/api/admin/v1/orders/excel` | ADM-040-001 |
| 105 | 클레임 목록 | GET | `/api/admin/v1/claims` | ADM-040-002 |
| 106 | 클레임 상세 | GET | `/api/admin/v1/claims/{claim_no}` | ADM-040-002 |
| 107 | 귀책 판단 | PUT | `/api/admin/v1/claims/{claim_no}/blame` | ADM-040-002 |
| 108 | 클레임 처리 | PUT | `/api/admin/v1/claims/{claim_no}/process` | ADM-040-002 |
| 109 | 클레임 처리이력 | GET | `/api/admin/v1/claims/{claim_no}/history` | ADM-040-002 |
| 110 | 환불 금액 계산 | GET | `/api/admin/v1/claims/{claim_no}/refund-estimate` | ADM-040-002 |
| 111 | 클레임 엑셀 | GET | `/api/admin/v1/claims/excel` | ADM-040-002 |
| 112 | 회원 목록 | GET | `/api/admin/v1/members` | ADM-050-001 |
| 113 | 회원 상세 | GET | `/api/admin/v1/members/{id}` | ADM-050-001 |
| 114 | 주문 내역 | GET | `/api/admin/v1/members/{id}/orders` | ADM-050-001 |
| 115 | 클레임 이력 | GET | `/api/admin/v1/members/{id}/claims` | ADM-050-001 |
| 116 | 포인트 이력 | GET | `/api/admin/v1/members/{id}/points` | ADM-050-001 |
| 117 | 쿠폰 목록 | GET | `/api/admin/v1/members/{id}/coupons` | ADM-050-001 |
| 118 | 계정 잠금 해제 | PUT | `/api/admin/v1/members/{id}/unlock` | ADM-050-001 |
| 119 | 포인트 수동 지급 | POST | `/api/admin/v1/members/{id}/points` | ADM-050-001 |
| 120 | 쿠폰 수동 발급 | POST | `/api/admin/v1/members/{id}/coupons` | ADM-050-001 |
| 121 | 상태 변경 | PUT | `/api/admin/v1/members/{id}/status` | ADM-050-001 |
| 122 | 회원 엑셀 | GET | `/api/admin/v1/members/excel` | ADM-050-001 |
| 123 | 등급 기준 목록 | GET | `/api/admin/v1/member-grades` | ADM-050-002 |
| 124 | 등급 기준 수정 | PUT | `/api/admin/v1/member-grades/{grade_code}` | ADM-050-002 |
| 125 | 입점신청 목록 | GET | `/api/admin/v1/vendors/applications` | ADM-060-001 |
| 126 | 입점신청 상세 | GET | `/api/admin/v1/vendors/applications/{id}` | ADM-060-001 |
| 127 | 심사 상태 변경 | PUT | `/api/admin/v1/vendors/applications/{id}/status` | ADM-060-001 |
| 128 | 심사 승인 | PUT | `/api/admin/v1/vendors/applications/{id}/approve` | ADM-060-001 |
| 129 | 심사 반려 | PUT | `/api/admin/v1/vendors/applications/{id}/reject` | ADM-060-001 |
| 130 | 심사 이력 | GET | `/api/admin/v1/vendors/applications/{id}/history` | ADM-060-001 |
| 131 | 입점사 목록 | GET | `/api/admin/v1/vendors` | ADM-060-002 |
| 132 | 입점사 상세 | GET | `/api/admin/v1/vendors/{id}` | ADM-060-002 |
| 133 | 입점사 수정 | PUT | `/api/admin/v1/vendors/{id}` | ADM-060-002 |
| 134 | 입점사 상태 변경 | PUT | `/api/admin/v1/vendors/{id}/status` | ADM-060-002 |
| 135 | 수수료율 조회 | GET | `/api/admin/v1/vendors/{id}/fee-rates` | ADM-060-002 |
| 136 | 수수료율 변경 | POST | `/api/admin/v1/vendors/{id}/fee-rates` | ADM-060-002 |
| 137 | 패널티 목록 | GET | `/api/admin/v1/vendors/{id}/penalties` | ADM-060-002 |
| 138 | 패널티 부과 | POST | `/api/admin/v1/vendors/{id}/penalties` | ADM-060-002 |
| 139 | 입점사 엑셀 | GET | `/api/admin/v1/vendors/excel` | ADM-060-002 |
| 140 | 배송사 목록 | GET | `/api/admin/v1/delivery-companies` | ADM-060-003 |
| 141 | 배송사 등록 | POST | `/api/admin/v1/delivery-companies` | ADM-060-003 |
| 142 | 배송사 수정 | PUT | `/api/admin/v1/delivery-companies/{id}` | ADM-060-003 |
| 143 | 배송사 삭제 | DELETE | `/api/admin/v1/delivery-companies/{id}` | ADM-060-003 |
| 144 | 정산 목록 | GET | `/api/admin/v1/settlements` | ADM-070-001 |
| 145 | 정산 상세 | GET | `/api/admin/v1/settlements/{no}` | ADM-070-001 |
| 146 | 정산 항목 | GET | `/api/admin/v1/settlements/{no}/items` | ADM-070-001 |
| 147 | 재정산 내역 | GET | `/api/admin/v1/settlements/{no}/adjustments` | ADM-070-001 |
| 148 | 정산 확정 | PUT | `/api/admin/v1/settlements/{no}/confirm` | ADM-070-001 |
| 149 | 일괄 확정 | PUT | `/api/admin/v1/settlements/bulk-confirm` | ADM-070-001 |
| 150 | 정산 엑셀 | GET | `/api/admin/v1/settlements/excel` | ADM-070-001 |
| 151 | 지급 목록 | GET | `/api/admin/v1/settlements/payments` | ADM-070-002 |
| 152 | 지급 상세 | GET | `/api/admin/v1/settlements/payments/{id}` | ADM-070-002 |
| 153 | 지급 완료 | PUT | `/api/admin/v1/settlements/payments/{id}/pay` | ADM-070-002 |
| 154 | 일괄 지급 | PUT | `/api/admin/v1/settlements/payments/bulk-pay` | ADM-070-002 |
| 155 | 지급 보류 | PUT | `/api/admin/v1/settlements/payments/{id}/hold` | ADM-070-002 |
| 156 | 보류 해제 | PUT | `/api/admin/v1/settlements/payments/{id}/release` | ADM-070-002 |
| 157 | 지급 엑셀 | GET | `/api/admin/v1/settlements/payments/excel` | ADM-070-002 |
| 158 | 외부정산 목록 | GET | `/api/admin/v1/settlements/external` | ADM-070-003 |
| 159 | 외부정산 상세 | GET | `/api/admin/v1/settlements/external/{id}` | ADM-070-003 |
| 160 | 외부정산 등록 | POST | `/api/admin/v1/settlements/external` | ADM-070-003 |
| 161 | 외부정산 수정 | PUT | `/api/admin/v1/settlements/external/{id}` | ADM-070-003 |
| 162 | 외부정산 삭제 | DELETE | `/api/admin/v1/settlements/external/{id}` | ADM-070-003 |
| 163 | 리뷰 목록 | GET | `/api/admin/v1/reviews` | ADM-080-001 |
| 164 | 리뷰 상세 | GET | `/api/admin/v1/reviews/{id}` | ADM-080-001 |
| 165 | 리뷰 숨김 | PUT | `/api/admin/v1/reviews/{id}/hide` | ADM-080-001 |
| 166 | 리뷰 활성화 | PUT | `/api/admin/v1/reviews/{id}/activate` | ADM-080-001 |
| 167 | 일괄 숨김 | PUT | `/api/admin/v1/reviews/bulk-hide` | ADM-080-001 |
| 168 | 일괄 활성화 | PUT | `/api/admin/v1/reviews/bulk-activate` | ADM-080-001 |
| 169 | 리뷰 엑셀 | GET | `/api/admin/v1/reviews/excel` | ADM-080-001 |
| 170 | QnA 목록 | GET | `/api/admin/v1/qna` | ADM-080-002 |
| 171 | QnA 상세 | GET | `/api/admin/v1/qna/{id}` | ADM-080-002 |
| 172 | QnA 답변 등록 | POST | `/api/admin/v1/qna/{id}/answer` | ADM-080-002 |
| 173 | QnA 답변 수정 | PUT | `/api/admin/v1/qna/{id}/answer` | ADM-080-002 |
| 174 | 활동지수 지급 | POST | `/api/admin/v1/qna/{id}/activity-score` | ADM-080-002 |
| 175 | QnA 숨김 | PUT | `/api/admin/v1/qna/{id}/hide` | ADM-080-002 |
| 176 | QnA 활성화 | PUT | `/api/admin/v1/qna/{id}/activate` | ADM-080-002 |
| 177 | QnA 엑셀 | GET | `/api/admin/v1/qna/excel` | ADM-080-002 |
| 178 | 운영자 목록 | GET | `/api/admin/v1/operators` | ADM-090-001 |
| 179 | 운영자 상세 | GET | `/api/admin/v1/operators/{id}` | ADM-090-001 |
| 180 | 운영자 등록 | POST | `/api/admin/v1/operators` | ADM-090-001 |
| 181 | 운영자 수정 | PUT | `/api/admin/v1/operators/{id}` | ADM-090-001 |
| 182 | 운영자 잠금해제 | PUT | `/api/admin/v1/operators/{id}/unlock` | ADM-090-001 |
| 183 | 비밀번호 초기화 | PUT | `/api/admin/v1/operators/{id}/password/reset` | ADM-090-001 |
| 184 | 운영자 신청 목록 | GET | `/api/admin/v1/operators/applications` | ADM-090-002 |
| 185 | 운영자 신청 상세 | GET | `/api/admin/v1/operators/applications/{id}` | ADM-090-002 |
| 186 | 운영자 신청 승인 | PUT | `/api/admin/v1/operators/applications/{id}/approve` | ADM-090-002 |
| 187 | 운영자 신청 반려 | PUT | `/api/admin/v1/operators/applications/{id}/reject` | ADM-090-002 |
| 188 | 롤 목록 | GET | `/api/admin/v1/roles` | ADM-090-003 |
| 189 | 롤 권한 조회 | GET | `/api/admin/v1/roles/{role_code}/permissions` | ADM-090-003 |
| 190 | 롤 권한 수정 | PUT | `/api/admin/v1/roles/{role_code}/permissions` | ADM-090-003 |
| 191 | 프로그램 목록 | GET | `/api/admin/v1/programs` | ADM-090-003 |
| 192 | 프로그램 등록 | POST | `/api/admin/v1/programs` | ADM-090-003 |
| 193 | 프로그램 수정 | PUT | `/api/admin/v1/programs/{id}` | ADM-090-003 |
| 194 | 프로그램 삭제 | DELETE | `/api/admin/v1/programs/{id}` | ADM-090-003 |
| 195 | 코드 목록 | GET | `/api/admin/v1/codes` | ADM-090-004 |
| 196 | 코드 등록 | POST | `/api/admin/v1/codes` | ADM-090-004 |
| 197 | 코드 수정 | PUT | `/api/admin/v1/codes/{id}` | ADM-090-004 |
| 198 | 코드 삭제 | DELETE | `/api/admin/v1/codes/{id}` | ADM-090-004 |
| 199 | 알림템플릿 목록 | GET | `/api/admin/v1/notification-templates` | ADM-090-005 |
| 200 | 알림템플릿 상세 | GET | `/api/admin/v1/notification-templates/{id}` | ADM-090-005 |
| 201 | 알림템플릿 등록 | POST | `/api/admin/v1/notification-templates` | ADM-090-005 |
| 202 | 알림템플릿 수정 | PUT | `/api/admin/v1/notification-templates/{id}` | ADM-090-005 |
| 203 | 알림템플릿 삭제 | DELETE | `/api/admin/v1/notification-templates/{id}` | ADM-090-005 |
| 204 | 금지어 목록 | GET | `/api/admin/v1/banned-words` | ADM-090-006 |
| 205 | 금지어 등록 | POST | `/api/admin/v1/banned-words` | ADM-090-006 |
| 206 | 금지어 수정 | PUT | `/api/admin/v1/banned-words/{id}` | ADM-090-006 |
| 207 | 금지어 삭제 | DELETE | `/api/admin/v1/banned-words/{id}` | ADM-090-006 |
| 208 | 공지사항 목록 | GET | `/api/admin/v1/notices` | ADM-090-007 |
| 209 | 공지사항 상세 | GET | `/api/admin/v1/notices/{id}` | ADM-090-007 |
| 210 | 공지사항 등록 | POST | `/api/admin/v1/notices` | ADM-090-007 |
| 211 | 공지사항 수정 | PUT | `/api/admin/v1/notices/{id}` | ADM-090-007 |
| 212 | 공지사항 삭제 | DELETE | `/api/admin/v1/notices/{id}` | ADM-090-007 |
| 213 | 약관 목록 | GET | `/api/admin/v1/terms` | ADM-090-008 |
| 214 | 약관 상세 | GET | `/api/admin/v1/terms/{id}` | ADM-090-008 |
| 215 | 약관 등록 | POST | `/api/admin/v1/terms` | ADM-090-008 |
| 216 | 약관 삭제 | DELETE | `/api/admin/v1/terms/{id}` | ADM-090-008 |
| 217 | 배너 목록 | GET | `/api/admin/v1/banners` | ADM-090-009 |
| 218 | 배너 상세 | GET | `/api/admin/v1/banners/{id}` | ADM-090-009 |
| 219 | 배너 등록 | POST | `/api/admin/v1/banners` | ADM-090-009 |
| 220 | 배너 수정 | PUT | `/api/admin/v1/banners/{id}` | ADM-090-009 |
| 221 | 배너 삭제 | DELETE | `/api/admin/v1/banners/{id}` | ADM-090-009 |
| 222 | 접근 이력 목록 | GET | `/api/admin/v1/audit/member-access` | ADM-090-010 |
| 223 | 접근 이력 엑셀 | GET | `/api/admin/v1/audit/member-access/excel` | ADM-090-010 |
| 224 | 배치 목록 | GET | `/api/admin/v1/batches` | ADM-100-001 |
| 225 | 배치 상세 | GET | `/api/admin/v1/batches/{job_code}` | ADM-100-001 |
| 226 | 배치 상태 변경 | PUT | `/api/admin/v1/batches/{job_code}/status` | ADM-100-001 |
| 227 | 배치 즉시 실행 | POST | `/api/admin/v1/batches/{job_code}/execute` | ADM-100-001 |
| 228 | 실행 이력 | GET | `/api/admin/v1/batches/{job_code}/executions` | ADM-100-001 |
| 229 | 실행 로그 | GET | `/api/admin/v1/batches/{job_code}/executions/{id}/logs` | ADM-100-001 |
| 230 | Outbox 목록 | GET | `/api/admin/v1/outbox` | ADM-100-002 |
| 231 | DLQ 목록 | GET | `/api/admin/v1/dlq` | ADM-100-002 |
| 232 | DLQ 상세 | GET | `/api/admin/v1/dlq/{id}` | ADM-100-002 |
| 233 | DLQ 재시도 | PUT | `/api/admin/v1/dlq/{id}/retry` | ADM-100-002 |
| 234 | DLQ 무시 | PUT | `/api/admin/v1/dlq/{id}/ignore` | ADM-100-002 |
| 235 | 감사 로그 목록 | GET | `/api/admin/v1/audit/logs` | ADM-100-003 |
| 236 | 감사 로그 상세 | GET | `/api/admin/v1/audit/logs/{id}` | ADM-100-003 |
| 237 | Trace 로그 목록 | GET | `/api/admin/v1/audit/traces` | ADM-100-003 |
| 238 | Trace 전체 흐름 | GET | `/api/admin/v1/audit/traces/{trace_id}` | ADM-100-003 |

**플랫폼 어드민 총 238개 API**

---

## 4. 입점사 BO

### 4.1 공통 정책

| 항목 | 기준 |
|------|------|
| 세션 유지 | 3시간 |
| 동시 세션 | 최대 2개 |
| 동시 세션 초과 | 가장 오래된 세션 종료 후 로그인 |
| 만료 안내 | 만료 10분 전 팝업 |
| 2단계 인증 | 필수 (이메일OTP·SMS OTP·TOTP) |
| 비밀번호 분실 | 초기화 → 임시 비밀번호 이메일 발송 |
| 최초 로그인 | 비밀번호 변경 강제 |

### 4.2 메뉴 트리

```
인증
  ├─ VND-000-001 로그인
  ├─ VND-000-002 2단계 인증
  ├─ VND-000-003 비밀번호 초기화
  ├─ VND-000-004 입점 신청
  └─ VND-000-005 비밀번호 변경 (최초)

홈 탭 (VND-HOME)

1. 상품 관리
  ├─ VND-010-001 상품 목록
  ├─ VND-010-002 상품 등록 (6단계 + 미리보기)
  └─ VND-010-003 재고 관리 (엑셀 일괄 업로드)

2. 주문 관리
  ├─ VND-020-001 주문 목록
  └─ VND-020-002 배송 관리 (엑셀 일괄 업로드)

3. 클레임 관리
  ├─ VND-030-001 취소 목록
  ├─ VND-030-002 반품 목록 (수거확인·재고복구·이의제기)
  └─ VND-030-003 교환 목록 (수거·출고 처리)

4. 정산 관리
  ├─ VND-040-001 정산 목록
  └─ VND-040-002 지급 내역

5. 커뮤니티 관리
  └─ VND-050-001 상품 QnA

6. 프로모션 관리
  ├─ VND-060-001 쿠폰 관리 (MD 승인 필요)
  └─ VND-060-002 수량 할인 관리 (MD 승인 필요)

7. 통계
  ├─ VND-070-001 판매 통계
  └─ VND-070-002 클레임 통계

8. 운영 설정
  ├─ VND-080-001 계정 관리 (2FA·세션·정산계좌)
  ├─ VND-080-002 배송 설정
  └─ VND-080-003 알림 설정
```

### 4.3 주요 특이사항

#### 상품 등록 6단계
1. 기본정보 (카테고리 선택 → 전시카테고리 자동 매핑)
2. 가격 (정가·판매가·공급가)
3. 이미지 (최대 10장 · 5MB)
4. 상세소개 (블록 에디터)
5. SKU (옵션값 입력 → 자동 생성)
6. 완료 (미리보기·심사요청)

#### 상품 상세 미리보기
- 고객 화면 기준 렌더링
- preview_token 발급 (Redis TTL 30분)
- 미리보기 모드 배너 표시
- 장바구니·구매·찜 비활성

#### 프로모션 제약
- 쿠폰·수량할인: 플랫폼 MD 승인 후 활성화
- 자사 상품에만 적용 가능

#### 입점사 클레임 권한

| 기능 | 입점사 | 플랫폼 |
|------|--------|--------|
| 반품 수거 처리 | ✅ | ✅ |
| 재고 수동 복구 | ✅ | ✅ |
| 귀책 이의 제기 | ✅ | ✅ |
| 귀책 최종 판단 | ❌ | ✅ |
| 환불 처리 | ❌ | ✅ |

### 4.4 프로모션 적용 순서

```
① 정상가 (price_original)
② 가격 할인 (행사가 event_price)
③ 수량 할인 (quantity_discount)
④ 쿠폰 할인 (coupon)
⑤ 장바구니 할인 (cart_discount)
⑥ 포인트 차감 (결제 수단)
```

### 4.5 회원 등급별 혜택

| 등급 | 월 쿠폰 | 포인트 적립률 | 무료배송 기준 |
|------|--------|------------|------------|
| New | 0장 | 0.5% | 50,000원 |
| Runner | 1장 | 1.0% | 30,000원 |
| Pacer | 2장 | 1.5% | 20,000원 |
| Elite | 3장 | 2.0% | 무조건 무료 |

### 4.6 입점사 BO 전체 API 목록

| # | API | Method | URL | 화면 |
|---|-----|--------|-----|------|
| 1 | 로그인 1단계 | POST | `/api/partner/v1/auth/login` | VND-000-001 |
| 2 | OTP 발송 | POST | `/api/partner/v1/auth/otp/send` | VND-000-002 |
| 3 | OTP 확인 | POST | `/api/partner/v1/auth/otp/verify` | VND-000-002 |
| 4 | TOTP 확인 | POST | `/api/partner/v1/auth/totp/verify` | VND-000-002 |
| 5 | TOTP 등록 | POST | `/api/partner/v1/auth/totp/register` | VND-000-002 |
| 6 | TOTP 해제 | DELETE | `/api/partner/v1/auth/totp` | VND-000-002 |
| 7 | 활성 세션 목록 | GET | `/api/partner/v1/auth/sessions` | VND-000-002 |
| 8 | 세션 강제 종료 | DELETE | `/api/partner/v1/auth/sessions/{id}` | VND-000-002 |
| 9 | 세션 연장 | PUT | `/api/partner/v1/auth/sessions/extend` | 공통 |
| 10 | 토큰 갱신 | POST | `/api/partner/v1/auth/refresh` | 공통 |
| 11 | 로그아웃 | POST | `/api/partner/v1/auth/logout` | 공통 |
| 12 | 계정 존재 확인 | POST | `/api/partner/v1/auth/account/check` | VND-000-003 |
| 13 | 비밀번호 초기화 이메일 | POST | `/api/partner/v1/auth/password/initialize` | VND-000-003 |
| 14 | 비밀번호 초기화 휴대폰 | POST | `/api/partner/v1/auth/password/phone` | VND-000-003 |
| 15 | 사업자번호 인증 | POST | `/api/partner/v1/auth/business/verify` | VND-000-004 |
| 16 | 이메일 중복 확인 | POST | `/api/partner/v1/auth/email/check` | VND-000-004 |
| 17 | 인증번호 발송 | POST | `/api/partner/v1/auth/phone/send` | VND-000-004 |
| 18 | 인증번호 확인 | POST | `/api/partner/v1/auth/phone/verify` | VND-000-004 |
| 19 | 서류 업로드 | POST | `/api/partner/v1/auth/documents/upload` | VND-000-004 |
| 20 | 입점 신청 | POST | `/api/partner/v1/auth/apply` | VND-000-004 |
| 21 | 약관 최신 버전 | GET | `/api/partner/v1/auth/terms/latest` | VND-000-004 |
| 22 | 비밀번호 변경 | PUT | `/api/partner/v1/auth/password/change` | VND-000-005 |
| 23 | 홈 요약 | GET | `/api/partner/v1/home/summary` | VND-HOME |
| 24 | 처리 필요 항목 | GET | `/api/partner/v1/home/pending` | VND-HOME |
| 25 | 주문 추이 | GET | `/api/partner/v1/home/trend?days=7` | VND-HOME |
| 26 | 상품 현황 | GET | `/api/partner/v1/home/products/summary` | VND-HOME |
| 27 | 공지사항 | GET | `/api/partner/v1/home/notices` | VND-HOME |
| 28 | 상품 목록 | GET | `/api/partner/v1/products` | VND-010-001 |
| 29 | 상품 상세 | GET | `/api/partner/v1/products/{id}` | VND-010-001 |
| 30 | 상품 수정 | PUT | `/api/partner/v1/products/{id}` | VND-010-001 |
| 31 | 심사 요청 | PUT | `/api/partner/v1/products/{id}/review-request` | VND-010-001 |
| 32 | 심사 취소 | PUT | `/api/partner/v1/products/{id}/review-cancel` | VND-010-001 |
| 33 | 판매 중단 | PUT | `/api/partner/v1/products/{id}/discontinue` | VND-010-001 |
| 34 | 상품 엑셀 | GET | `/api/partner/v1/products/excel` | VND-010-001 |
| 35 | 자동 전시카테고리 | GET | `/api/partner/v1/categories/standard/{id}/display-mappings` | VND-010-001 |
| 36 | 상품 등록 | POST | `/api/partner/v1/products` | VND-010-002 |
| 37 | 이미지 업로드 | POST | `/api/partner/v1/products/images` | VND-010-002 |
| 38 | 임시저장 | PUT | `/api/partner/v1/products/{id}/draft` | VND-010-002 |
| 39 | 상세타입 조회 | GET | `/api/partner/v1/product-detail-types` | VND-010-002 |
| 40 | 브랜드 목록 | GET | `/api/partner/v1/brands` | VND-010-002 |
| 41 | 미리보기 토큰 발급 | POST | `/api/partner/v1/products/preview` | VND-010-002 |
| 42 | 미리보기 조회 | GET | `/api/v1/products/preview/{preview_token}` | VND-010-002 |
| 43 | 재고 목록 | GET | `/api/partner/v1/inventory` | VND-010-003 |
| 44 | 재고 수정 | PUT | `/api/partner/v1/inventory/{sku_id}` | VND-010-003 |
| 45 | 재고 이력 | GET | `/api/partner/v1/inventory/{sku_id}/history` | VND-010-003 |
| 46 | 재고 엑셀 양식 | GET | `/api/partner/v1/inventory/excel/template` | VND-010-003 |
| 47 | 재고 엑셀 업로드 | POST | `/api/partner/v1/inventory/excel/upload` | VND-010-003 |
| 48 | 재고 엑셀 결과 | GET | `/api/partner/v1/inventory/excel/result/{job_id}` | VND-010-003 |
| 49 | 주문 목록 | GET | `/api/partner/v1/orders` | VND-020-001 |
| 50 | 주문 상세 | GET | `/api/partner/v1/orders/{order_no}` | VND-020-001 |
| 51 | 출고 처리 | PUT | `/api/partner/v1/orders/{order_no}/prepare` | VND-020-001 |
| 52 | 일괄 출고 처리 | PUT | `/api/partner/v1/orders/bulk-prepare` | VND-020-001 |
| 53 | 주문 처리 이력 | GET | `/api/partner/v1/orders/{order_no}/history` | VND-020-001 |
| 54 | 주문 엑셀 | GET | `/api/partner/v1/orders/excel` | VND-020-001 |
| 55 | 배송 목록 | GET | `/api/partner/v1/deliveries` | VND-020-002 |
| 56 | 배송정보 입력 | PUT | `/api/partner/v1/deliveries/{order_no}` | VND-020-002 |
| 57 | 일괄 배송정보 | PUT | `/api/partner/v1/deliveries/bulk` | VND-020-002 |
| 58 | 배송 추적 | GET | `/api/partner/v1/deliveries/{order_no}/tracking` | VND-020-002 |
| 59 | 배송 엑셀 양식 | GET | `/api/partner/v1/deliveries/excel/template` | VND-020-002 |
| 60 | 배송 엑셀 업로드 | POST | `/api/partner/v1/deliveries/excel/upload` | VND-020-002 |
| 61 | 배송 엑셀 | GET | `/api/partner/v1/deliveries/excel` | VND-020-002 |
| 62 | 취소 목록 | GET | `/api/partner/v1/claims/cancel` | VND-030-001 |
| 63 | 취소 상세 | GET | `/api/partner/v1/claims/cancel/{claim_no}` | VND-030-001 |
| 64 | 취소 엑셀 | GET | `/api/partner/v1/claims/cancel/excel` | VND-030-001 |
| 65 | 반품 목록 | GET | `/api/partner/v1/claims/return` | VND-030-002 |
| 66 | 반품 상세 | GET | `/api/partner/v1/claims/return/{claim_no}` | VND-030-002 |
| 67 | 수거 운송장 등록 | PUT | `/api/partner/v1/claims/return/{claim_no}/tracking` | VND-030-002 |
| 68 | 수거 완료 처리 | PUT | `/api/partner/v1/claims/return/{claim_no}/collected` | VND-030-002 |
| 69 | 재고 수동 복구 | PUT | `/api/partner/v1/claims/return/{claim_no}/stock-restore` | VND-030-002 |
| 70 | 의견 등록 | POST | `/api/partner/v1/claims/return/{claim_no}/opinion` | VND-030-002 |
| 71 | 반품 처리이력 | GET | `/api/partner/v1/claims/return/{claim_no}/history` | VND-030-002 |
| 72 | 반품 엑셀 | GET | `/api/partner/v1/claims/return/excel` | VND-030-002 |
| 73 | 교환 목록 | GET | `/api/partner/v1/claims/exchange` | VND-030-003 |
| 74 | 교환 상세 | GET | `/api/partner/v1/claims/exchange/{claim_no}` | VND-030-003 |
| 75 | 교환 재고 확인 | GET | `/api/partner/v1/claims/exchange/{claim_no}/stock-check` | VND-030-003 |
| 76 | 교환 수거 운송장 | PUT | `/api/partner/v1/claims/exchange/{claim_no}/return-tracking` | VND-030-003 |
| 77 | 교환 수거 완료 | PUT | `/api/partner/v1/claims/exchange/{claim_no}/collected` | VND-030-003 |
| 78 | 교환 출고 처리 | PUT | `/api/partner/v1/claims/exchange/{claim_no}/ship` | VND-030-003 |
| 79 | 교환 처리이력 | GET | `/api/partner/v1/claims/exchange/{claim_no}/history` | VND-030-003 |
| 80 | 교환 엑셀 | GET | `/api/partner/v1/claims/exchange/excel` | VND-030-003 |
| 81 | 정산 목록 | GET | `/api/partner/v1/settlements` | VND-040-001 |
| 82 | 정산 상세 | GET | `/api/partner/v1/settlements/{no}` | VND-040-001 |
| 83 | 정산 항목 | GET | `/api/partner/v1/settlements/{no}/items` | VND-040-001 |
| 84 | 재정산 내역 | GET | `/api/partner/v1/settlements/{no}/adjustments` | VND-040-001 |
| 85 | 정산 엑셀 | GET | `/api/partner/v1/settlements/excel` | VND-040-001 |
| 86 | 지급 목록 | GET | `/api/partner/v1/settlements/payments` | VND-040-002 |
| 87 | 지급 상세 | GET | `/api/partner/v1/settlements/payments/{id}` | VND-040-002 |
| 88 | 지급 엑셀 | GET | `/api/partner/v1/settlements/payments/excel` | VND-040-002 |
| 89 | QnA 목록 | GET | `/api/partner/v1/qna` | VND-050-001 |
| 90 | QnA 상세 | GET | `/api/partner/v1/qna/{id}` | VND-050-001 |
| 91 | QnA 답변 등록 | POST | `/api/partner/v1/qna/{id}/answer` | VND-050-001 |
| 92 | QnA 답변 수정 | PUT | `/api/partner/v1/qna/{id}/answer` | VND-050-001 |
| 93 | 활동지수 지급 | POST | `/api/partner/v1/qna/{id}/activity-score` | VND-050-001 |
| 94 | QnA 엑셀 | GET | `/api/partner/v1/qna/excel` | VND-050-001 |
| 95 | 쿠폰 목록 | GET | `/api/partner/v1/coupons` | VND-060-001 |
| 96 | 쿠폰 상세 | GET | `/api/partner/v1/coupons/{id}` | VND-060-001 |
| 97 | 쿠폰 등록 | POST | `/api/partner/v1/coupons` | VND-060-001 |
| 98 | 쿠폰 수정 | PUT | `/api/partner/v1/coupons/{id}` | VND-060-001 |
| 99 | 쿠폰 비활성화 | PUT | `/api/partner/v1/coupons/{id}/deactivate` | VND-060-001 |
| 100 | 쿠폰 엑셀 | GET | `/api/partner/v1/coupons/excel` | VND-060-001 |
| 101 | 수량할인 목록 | GET | `/api/partner/v1/quantity-discounts` | VND-060-002 |
| 102 | 수량할인 상세 | GET | `/api/partner/v1/quantity-discounts/{id}` | VND-060-002 |
| 103 | 수량할인 등록 | POST | `/api/partner/v1/quantity-discounts` | VND-060-002 |
| 104 | 수량할인 수정 | PUT | `/api/partner/v1/quantity-discounts/{id}` | VND-060-002 |
| 105 | 수량할인 종료 | PUT | `/api/partner/v1/quantity-discounts/{id}/end` | VND-060-002 |
| 106 | 자사 상품 목록 | GET | `/api/partner/v1/products/selling` | VND-060-002 |
| 107 | 수량할인 엑셀 | GET | `/api/partner/v1/quantity-discounts/excel` | VND-060-002 |
| 108 | 판매 요약 | GET | `/api/partner/v1/stats/sales/summary` | VND-070-001 |
| 109 | 판매 추이 | GET | `/api/partner/v1/stats/sales/trend` | VND-070-001 |
| 110 | 상품별 순위 | GET | `/api/partner/v1/stats/sales/products` | VND-070-001 |
| 111 | SKU별 현황 | GET | `/api/partner/v1/stats/sales/skus` | VND-070-001 |
| 112 | 판매 엑셀 | GET | `/api/partner/v1/stats/sales/excel` | VND-070-001 |
| 113 | 클레임 요약 | GET | `/api/partner/v1/stats/claims/summary` | VND-070-002 |
| 114 | 클레임 추이 | GET | `/api/partner/v1/stats/claims/trend` | VND-070-002 |
| 115 | 유형별 비율 | GET | `/api/partner/v1/stats/claims/types` | VND-070-002 |
| 116 | 귀책별 현황 | GET | `/api/partner/v1/stats/claims/blame` | VND-070-002 |
| 117 | 상품별 현황 | GET | `/api/partner/v1/stats/claims/products` | VND-070-002 |
| 118 | 클레임 엑셀 | GET | `/api/partner/v1/stats/claims/excel` | VND-070-002 |
| 119 | 계정 정보 조회 | GET | `/api/partner/v1/settings/account` | VND-080-001 |
| 120 | 담당자 정보 수정 | PUT | `/api/partner/v1/settings/account` | VND-080-001 |
| 121 | 비밀번호 변경 | PUT | `/api/partner/v1/settings/account/password` | VND-080-001 |
| 122 | 2단계 인증 변경 | PUT | `/api/partner/v1/settings/account/2fa` | VND-080-001 |
| 123 | 세션 전체 종료 | DELETE | `/api/partner/v1/auth/sessions` | VND-080-001 |
| 124 | 정산계좌 조회 | GET | `/api/partner/v1/settings/account/bank` | VND-080-001 |
| 125 | 정산계좌 변경 | PUT | `/api/partner/v1/settings/account/bank` | VND-080-001 |
| 126 | 계좌 인증 | POST | `/api/partner/v1/settings/account/bank/verify` | VND-080-001 |
| 127 | 배송 설정 조회 | GET | `/api/partner/v1/settings/delivery` | VND-080-002 |
| 128 | 배송 설정 수정 | PUT | `/api/partner/v1/settings/delivery` | VND-080-002 |
| 129 | 배송사 목록 | GET | `/api/partner/v1/settings/delivery/companies` | VND-080-002 |
| 130 | 알림 설정 조회 | GET | `/api/partner/v1/settings/notifications` | VND-080-003 |
| 131 | 알림 설정 수정 | PUT | `/api/partner/v1/settings/notifications` | VND-080-003 |

**입점사 BO 총 131개 API**

---

## 5. 전체 API 목록 요약

| 애플리케이션 | 화면 수 | API 수 |
|------------|--------|--------|
| 고객 웹 | 38개 | 101개 |
| 플랫폼 어드민 | 80개 | 238개 |
| 입점사 BO | 40개 | 131개 |
| **합계** | **158개** | **470개** |

---

## 6. 화면 유형 분류

### 6.1 유형 정의

모든 화면은 아래 유형 중 하나로 분류한다. 개발자는 해당 유형의 가이드 샘플(`/guide/{type}`)을 참조하여 일관된 레이아웃을 구현한다.

| 유형 코드 | 유형명 | 설명 | 적용 앱 |
|----------|--------|------|--------|
| `dashboard` | 대시보드 | KPI 카드·차트·요약 정보 | 전체 |
| `list` | 목록 (그리드) | 상품·기획전 카드형 그리드 | 고객웹 |
| `table` | 목록 (테이블) | 검색·필터·페이지네이션 테이블 | 어드민·입점사 |
| `detail` | 상세 조회 | 단일 리소스 상세 정보 | 전체 |
| `form` | 입력 폼 | 등록·수정·주문서 | 전체 |
| `stepper` | 단계별 위자드 | 다단계 입력 (상품등록 6단계) | 입점사 |
| `layer` | 레이어 팝업 | 전체 화면 오버레이 | 고객웹 |
| `bottomsheet` | 바텀시트 | 하단 슬라이드업 | 고객웹 |
| `modal` | 모달 다이얼로그 | 확인·처리 팝업 | 어드민·입점사 |

### 6.2 고객 웹 화면별 유형 매핑

| 화면ID | 화면명 | 유형 |
|--------|--------|------|
| CUS-001 | 메인 홈 | `dashboard` |
| CUS-010 | 카테고리 목록 | `list` |
| CUS-011 | 상품 상세 | `detail` |
| CUS-020 | 기획전 메인 | `list` |
| CUS-021 | 기획전 상세 | `detail` |
| CUS-030 | 통합 검색 | `list` |
| CUS-040 | 장바구니 | `list` |
| CUS-041 | 주문서 | `form` |
| CUS-042 | 주문 접수 완료 | `detail` |
| CUS-050 | 마이페이지 홈 | `dashboard` |
| CUS-051 | 주문 목록 | `list` |
| CUS-052 | 주문 상세 | `detail` |
| CUS-053~055 | 취소/반품/교환 신청 | `form` |
| CUS-057 | 찜 목록 | `list` |
| CUS-058 | 쿠폰 | `list` |
| CUS-059 | 포인트 | `list` |
| CUS-060 | 리뷰 관리 | `list` |
| CUS-061 | 리뷰 작성 | `form` |
| CUS-063 | 배송지 관리 | `list` |
| CUS-064 | 회원 정보 | `form` |
| CUS-070 | 상품 리뷰 목록 | `list` |
| CUS-080 | 로그인 | `layer` |
| CUS-081 | 회원가입 | `stepper` |
| CUS-011 옵션선택 | 옵션·수량 | `bottomsheet` |

### 6.3 플랫폼 어드민 화면별 유형 매핑

| 화면ID | 화면명 | 유형 |
|--------|--------|------|
| ADM-HOME | 홈 | `dashboard` |
| ADM-020-001 | 상품 심사 | `table` |
| ADM-020-002 | 상품 목록 | `table` |
| ADM-020-003~006 | 카테고리·브랜드 | `table` |
| ADM-020-007 | 전시 페이지 | `table` |
| ADM-030-001~006 | 프로모션 관리 | `table` |
| ADM-040-001 | 주문 목록 | `table` |
| ADM-040-002 | 클레임 목록 | `table` |
| ADM-050-001 | 회원 목록 | `table` |
| ADM-060-001 | 입점 심사 | `table` |
| ADM-070-001 | 정산 목록 | `table` |
| ADM-090-001~010 | 운영 설정 | `table` + `form` |

### 6.4 입점사 BO 화면별 유형 매핑

| 화면ID | 화면명 | 유형 |
|--------|--------|------|
| VND-HOME | 홈 | `dashboard` |
| VND-010-001 | 상품 목록 | `table` |
| VND-010-002 | 상품 등록 | `stepper` |
| VND-010-003 | 재고 관리 | `table` |
| VND-020-001 | 주문 목록 | `table` |
| VND-020-002 | 배송 관리 | `table` |
| VND-030-001~003 | 클레임 관리 | `table` |
| VND-040-001 | 정산 목록 | `table` |
| VND-050-001 | 상품 QnA | `table` |
| VND-060-001~002 | 프로모션 | `form` |
| VND-070-001~002 | 통계 | `dashboard` |
| VND-080-001~003 | 운영 설정 | `form` |

---

*Confidential | 3TOP | 화면 정의서 v1.1 | 2026.06.22*
