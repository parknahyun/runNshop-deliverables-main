# runNshop 기술 스택 정의서

> 작성 주체: 3TOP 2본부
> 문서 버전: v1.0
> 작성일: 2026.06.26
> 상태: 확정

## 문서 목적

프로젝트의 기술 스택·폴더 구조·실행 방법을 정의하여, 새로 합류하는 개발자 또는 타 프로젝트에서 동일 구조를 세팅할 때 참조하는 공식 기술 문서입니다.

## 대상 독자

- 프로젝트에 합류하는 개발자 (온보딩)
- 타 팀이 동일 구조로 신규 프로젝트를 세팅할 때 (scaffolding 가이드와 함께 사용)
- 기술 의사결정 시 현재 스택 확인용

---

## 1. 프로젝트 구조

```
runNshop/                         ← 모노레포 루트
├── apps/
│   ├── runNshop-mobile/          ← 플랫폼 고객웹 (Next.js 14, Tailwind)
│   │   ├── app/                  ← App Router 페이지 (SSR)
│   │   ├── components/           ← UI 컴포넌트
│   │   └── lib/                  ← api.ts, constants.ts
│   ├── runNshop-admin/           ← 플랫폼 어드민 (Next.js 15, CSR SPA)
│   │   └── src/
│   │       ├── app/              ← layout + page + globals.css
│   │       ├── shell/            ← AppShell, Dashboard, TabContext, shared/
│   │       └── {domain}/         ← 도메인별 화면
│   └── runNshop-partner/         ← 플랫폼 입점사 (Next.js 15, CSR SPA)
│       └── src/
│           ├── app/              ← layout + page + globals.css
│           ├── shell/            ← AppShell, Dashboard, TabContext, shared/
│           └── {domain}/         ← 도메인별 화면
├── api/
│   └── runNshop-api/             ← Back-end API (Kotlin + Spring Boot 3.3)
│       └── src/main/
│           ├── kotlin/com/runnshop/
│           │   ├── {domain}/controller/
│           │   ├── {domain}/service/
│           │   ├── {domain}/dto/
│           │   └── common/       ← MockLoader, CorsConfig
│           └── resources/
│               ├── mock/v1/      ← 고객웹 Mock JSON
│               ├── mock/admin/   ← 어드민 Mock JSON
│               ├── mock/partner/ ← 입점사 Mock JSON
│               └── application.yml
├── docs/                         ← 설계 문서
└── .kiro/
    ├── KIRO_START.md             ← 개발 가이드
    └── steering/                 ← AI 작업 지시 규칙
```

---

## 2. 앱별 기술 스택

### 2.1 플랫폼 고객웹 (runNshop-mobile)

| 항목 | 기술 |
|------|------|
| 프레임워크 | Next.js 14+ (App Router) |
| 언어 | TypeScript |
| 스타일링 | Tailwind CSS |
| 렌더링 | SSR + BFF (Server Component + Route Handler) |
| 인증 | httpOnly 쿠키 (본개발), bypass (프로토타입) |
| 해상도 | 모바일 360px |
| 포트 | 3000 |

### 2.2 플랫폼 어드민 (runNshop-admin)

| 항목 | 기술 |
|------|------|
| 프레임워크 | Next.js 15 |
| 언어 | TypeScript |
| 스타일링 | 순수 CSS 클래스 (globals.css, BEM 스타일) |
| 렌더링 | CSR (SPA) |
| UI 구조 | NavBar + TabBar + TabContent (MDI 탭) |
| 색상 | 슬레이트 다크(#1e293b) + 블루(#3b82f6) |
| 접근 통제 | VPN/IP 제한 |
| 해상도 | PC 1280px+ |
| 포트 | 3001 |

### 2.3 플랫폼 입점사 (runNshop-partner)

| 항목 | 기술 |
|------|------|
| 프레임워크 | Next.js 15 |
| 언어 | TypeScript |
| 스타일링 | 순수 CSS 클래스 (globals.css, BEM 스타일) |
| 렌더링 | CSR (SPA) |
| UI 구조 | NavBar + TabBar + TabContent (MDI 탭) |
| 색상 | 다크 오렌지(#7c2d12) + 오렌지(#ea580c) |
| 접근 통제 | 2FA + 세션 3시간 |
| 해상도 | PC 1280px+ |
| 포트 | 3002 |

### 2.4 Back-end API (runNshop-api)

| 항목 | 기술 |
|------|------|
| 언어 | Kotlin |
| 프레임워크 | Spring Boot 3.3 |
| 빌드 | Gradle (Kotlin DSL) |
| JDK | 21 |
| 아키텍처 | Modular Monolith (12개 업무도메인 패키지) |
| 포트 | 8080 |

---

## 3. 12개 업무도메인

| # | 도메인 | 패키지 | 핵심 책임 |
|---|--------|--------|----------|
| 1 | Order | com.runnshop.order | 주문 생명주기 |
| 2 | Catalog | com.runnshop.catalog | 상품·재고·카테고리 |
| 3 | Member | com.runnshop.member | 회원·포인트·쿠폰 |
| 4 | Payment | com.runnshop.payment | 결제 트랜잭션 |
| 5 | Promotion | com.runnshop.promotion | 쿠폰·행사가·할인 |
| 6 | Settlement | com.runnshop.settlement | 정산 |
| 7 | Vendor | com.runnshop.vendor | 입점사 |
| 8 | Notification | com.runnshop.notification | 알림 |
| 9 | Community | com.runnshop.community | 리뷰·QnA |
| 10 | Search | com.runnshop.search | 통합검색 |
| 11 | Config | com.runnshop.config | 권한·설정 |
| 12 | Audit | com.runnshop.audit | 로그·감사 |

---

## 4. API URL Path Prefix

| 앱 | Path Prefix | 인증 |
|----|------------|------|
| 고객웹 | /api/v1/** | JWT + Redis |
| 어드민 | /api/admin/v1/** | JWT + 세션 8시간 |
| 입점사 | /api/partner/v1/** | JWT + 2FA + 세션 3시간 |

---

## 5. Mock 데이터 규칙

- 위치: `api/runNshop-api/src/main/resources/mock/{v1,admin,partner}/`
- 파일명: `{domain}__{METHOD}_{path}.json` (이중 언더스코어 구분)
- 응답: `{ "code": "SUCCESS", "data": { ... } }`

---

## 6. 실행 방법

```bash
# API 서버
cd api/runNshop-api && ./gradlew bootRun  # → :8080

# 고객웹
cd apps/runNshop-mobile && npm install && npm run dev  # → :3000

# 어드민
cd apps/runNshop-admin && npm install && npm run dev   # → :3001

# 입점사
cd apps/runNshop-partner && npm install && npm run dev  # → :3002
```

---

*Confidential | 3TOP | 기술 스택 정의서 v1.0 | 2026.06.26*
