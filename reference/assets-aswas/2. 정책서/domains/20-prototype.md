# 러닝 커머스 플랫폼 정책서 — 20. 프로토타입 개발 정책

> 상위 문서: [runNshop_policy_v1_2.md](../runNshop_policy_v1_2.md)
> 문서 버전: v3.4 | 상태: 초안 (Draft)

---

## 20.1 프로토타입 목적 및 범위

프로토타입은 **UI 흐름 검증**을 목적으로 하며, 실제 데이터 처리·외부 연동·보안은 이후 단계에서 구현한다.

| 항목 | 기준 |
|------|------|
| 목적 | 화면 UI/UX 흐름 검증, 이해관계자 피드백 수집 |
| 데이터 소스 | Back-end API Mock JSON 반환 |
| 데이터 수정/등록 | **미수행** (Mock 읽기 전용) |
| 외부 연동 | 미구현 (PG, 배송사, SNS 등) |
| 인증/보안 | 항상 로그인된 상태로 간주 (JWT bypass) |

## 20.2 프로토타입 기술 스택

| 영역 | 기술 | 비고 |
|------|------|------|
| Front-end (고객웹) | Next.js 14+ (App Router) + TypeScript + Tailwind CSS | SSR + BFF 구조 |
| Front-end (어드민/입점사) | Next.js 15 + TypeScript + 순수 CSS 클래스 | CSR (SPA), MDI 탭 |
| Back-end API | Kotlin + Spring Boot 3.3 (단일 실행 모듈) | 12개 업무도메인 패키지 |
| 데이터 | Mock JSON 파일 (API resources 내 관리) | DB 미사용 |

## 20.2-1 고객웹 SSR + BFF 구조

고객웹은 SEO·보안을 위해 SSR + BFF(Backend For Frontend) 구조를 적용한다.

```
브라우저 ←→ Next.js Server (BFF) ←→ Back-end API (내부 네트워크)
           쿠키 기반 인증              서버 간 토큰 통신
           API 키·로직 은닉            외부 직접 접근 불가
```

| 구분 | 역할 |
|------|------|
| Server Component (SSR) | 초기 데이터 fetch + HTML 렌더링, API 키 서버에서만 사용 |
| Route Handler (`app/api/`) | BFF 프록시, 브라우저 → BFF → 백엔드 중계 |
| Client Component | 인터랙션(장바구니·옵션 선택 등), BFF 경유 `/api/*` 호출 |
| 쿠키 인증 | httpOnly + secure + sameSite=strict, 서버에서만 읽기 |

### 보안 원칙

| 항목 | 기준 |
|------|------|
| API 키 은닉 | `SERVER_API_BASE` (서버 전용 환경변수), 브라우저에 미노출 |
| 백엔드 폐쇄 | 브라우저에서 직접 접근 불가, Next.js Server만 통신 |
| 쿠키 보안 | httpOnly + secure + sameSite=strict |
| CORS | Next.js BFF만 허용 |

### 프로토타입 단계 처리

| 항목 | 프로토타입 | 본개발 |
|------|----------|--------|
| API 호출 주체 | Server Component (이미 적용) | Server Component + Route Handler |
| 인증 | bypass (항상 로그인) | httpOnly 쿠키 + JWT |
| 백엔드 접근 | localhost:8080 직접 | 내부 네트워크만 |

## 20.2-2 어드민/입점사 CSR (SPA) 구조

어드민·입점사는 내부 운영자 전용이므로 SSR/BFF 불필요. CSR(SPA)로 운영하며 네트워크 수준 접근 통제를 적용한다.

| 구분 | 기준 |
|------|------|
| 렌더링 | CSR (Client Side Rendering, MDI 탭 SPA) |
| API 호출 | Client Component에서 직접 호출 |
| 접근 통제 | VPN/IP 제한 (어드민), 2FA + 세션 (입점사) |
| SEO | 불필요 (로그인 후 화면) |

## 20.2-3 어드민/입점사 UI 구조

화면정의서의 `화면 구조 재사용 지침`에 따라 MDI(Multi Document Interface) 탭 기반으로 구성한다.

| 구성요소 | 역할 |
|---------|------|
| NavBar | 상단 드롭다운 메뉴 (화면 열기) |
| TabBar | 열린 화면 탭 표시 (최대 8개, 대시보드 고정) |
| TabContent | 활성 탭 화면 렌더링 |

### 화면 유형별 CSS 클래스 패턴

| 유형 | 최외곽 | 핵심 구조 |
|------|--------|---------|
| 메인 (Dashboard) | `.dashboard` | `.dashboard__grid` + `.dash-card` |
| 현황 (Table) | `.page` | `.filter-bar` → `.summary-bar` → `.table-wrap` → `.pagination` |
| 상세 (Detail Modal) | `.detail-modal-overlay` | `.detail-modal__header` → `InnerTabs` → `.tab-panel-content` |

### 상세 화면 운영 원칙

| 원칙 | 설명 |
|------|------|
| 모달 필수 | 모든 상세·등록·수정 화면은 모달(detail-modal)로 구현. 탭으로 열지 않음 |
| 기본 내부 구조 | InnerTabs (탭 방식). 명시적으로 단계별(step) UI를 요청한 경우에만 stepper 사용 |
| MDI 탭 용도 | 현황(table) 화면을 여는 데만 사용 |

### 색상 구분

| 앱 | NavBar 배경 | 포인트 색상 |
|----|-----------|-----------|
| 플랫폼 어드민 | #1e293b (슬레이트 다크) | #3b82f6 (블루) |
| 플랫폼 입점사 | #7c2d12 (다크 오렌지) | #ea580c (오렌지) |

### 구현 진행 표시

- 메뉴 항목에 `implemented: true` 속성 추가 시 초록 원(●) 표시
- 미구현 화면은 PlaceholderPage로 "아직 구현되지 않았습니다" 표시

## 20.3 앱 구성 및 접근 통제

| 앱 | 모듈명 | URL | API Path Prefix |
|----|--------|-----|----------------|
| 플랫폼 고객웹 | runNshop-mobile | www.runNshop.com | `/api/v1/**` |
| 플랫폼 어드민 | runNshop-admin | admin.runNshop.com | `/api/admin/v1/**` |
| 플랫폼 입점사 | runNshop-partner | partners.runNshop.com | `/api/partner/v1/**` |
| 플랫폼 API | runNshop-api | api.runNshop.com | - |

> 앱별 API 접근은 URL path prefix로 구분하며, 하나의 Back-end에서 3개 앱의 API를 모두 서비스한다.

## 20.4 구현 우선순위

| 단계 | 대상 | 범위 |
|------|------|------|
| 1단계 | API | 공통 MockLoader + Catalog·Order Mock API |
| 2단계 | 플랫폼 고객웹 | CUS-001 홈 → CUS-011 상품상세 → CUS-040 장바구니 → CUS-041 주문서 |
| 3단계 | 플랫폼 어드민 | ADM-HOME → ADM-020 상품심사 → ADM-040 주문관리 |
| 4단계 | 플랫폼 입점사 | VND-HOME → VND-010 상품관리 → VND-020 주문관리 |

## 20.5 데이터 수정/등록 처리 방침

프로토타입에서도 POST/PUT/DELETE 요청은 실제로 API를 호출한다.
API는 실제 저장 없이 성공 응답(Mock)을 반환하며, Front-end는 응답 결과를 사용자에게 표시한다.

| 원칙 | 설명 |
|------|------|
| API 호출 | 모든 저장/수정/삭제 요청은 실제 API를 호출한다 |
| API 응답 | 실제 DB 저장 없이 성공 Mock 응답을 반환한다 |
| 결과 표시 | Front-end는 API 응답을 받아 사용자에게 알린다 (예: "저장되었습니다") |
| 화면 이동 | 모든 네비게이션은 정상 동작한다 |
| 유효성 검증 | 프론트 유효성 검증은 실제와 동일하게 구현한다 |

## 20.5-1 보안 요건 프로토타입 처리 기준

| # | 보안 요건 | 정책서 기준 | 프로토타입 처리 |
|---|---------|-----------|-------------|
| 1 | 본인인증 | 휴대폰 인증 필수 | 화면 UI 구현, API 항상 성공 응답 |
| 2 | 세션 유지 (고객) | 1시간, 최대 3디바이스 | 세션 만료 없이 항상 로그인 유지 |
| 3 | 세션 유지 (입점사) | 30분, 단일 디바이스 | 세션 만료 없이 항상 로그인 유지 |
| 4 | 세션 유지 (어드민) | 8시간 | 세션 만료 없이 항상 로그인 유지 |
| 5 | 로그인 실패 잠금 | 5회 → 30분 잠금 | 로그인 UI 구현, API 항상 성공 |
| 6 | 비밀번호 정책 | 8자+영문+숫자(+특수문자) | 프론트 유효성 검증 구현, API 항상 성공 |
| 7 | 2단계 인증 (입점사) | JWT + 2FA 필수 | 2FA 화면 UI 구현, API 항상 성공 |
| 8 | 권한 체크 | 롤별 메뉴·기능 접근 제한 | 메뉴 전체 노출 (권한 제한 미적용) |
| 9 | 주요 작업 재인증 | 비밀번호 재확인 | 재인증 모달 UI 구현, API 항상 성공 |
| 10 | 개인정보 마스킹 | 이름·폰·이메일·계좌 마스킹 | Mock 데이터에 마스킹 적용 |
| 11 | IP 접근 제한 | VPN/IP 제한 | 미적용 (로컬 개발) |
| 12 | HTTPS | 전 구간 | 미적용 (localhost HTTP) |
| 13 | FDS | 이상결제 자동 차단 | 미구현 |
| 14 | Nginx 접근 통제 | Whitelist 방식 | 미적용 (직접 API 접근) |
| 15 | JWT 토큰 | Access/Refresh + Redis | 토큰 없이 API 직접 호출 |

> **원칙**: 보안 관련 UI/UX 흐름(로그인·2FA·재인증·마스킹)은 실제와 동일하게 구현하되, 인프라 보안(HTTPS·Nginx·IP제한·JWT검증)은 미적용한다.

## 20.6 프로토타입 제약사항 (의도적 생략)

| 항목 | 프로토타입 처리 | 이후 구현 |
|------|--------------|----------|
| 인증/로그인 | 항상 로그인된 상태로 간주 (JWT bypass) | Spring Security + Redis 세션 |
| 결제 | 주문 완료 화면으로 바로 이동 | PG 연동 (토스페이먼츠) |
| 이미지 업로드 | 로컬 placeholder 이미지 사용 | AWS S3 + Rekognition |
| 알림 | 미구현 | FCM + 카카오 알림톡 |
| 검색 | Mock 고정 결과 반환 | Elasticsearch |
| 배송 추적 | Mock 상태 고정 | 배송사 API 연동 |
| 포인트/쿠폰 계산 | Mock 고정 금액 | 실시간 계산 로직 |
| 동시성 제어 | 미구현 | Redis 분산 락 + Outbox |
| 데이터베이스 | Mock JSON 파일 | PostgreSQL + MyBatis |
| 외부 API 연동 | 미구현 | PG, 배송사, SNS 로그인 |

## 20.7 에러 처리 표준

프로토타입 단계에서도 API 에러 응답 표준을 준수한다.

### 정상 응답

```json
{
  "code": "SUCCESS",
  "data": { ... }
}
```

### 에러 응답

```json
{
  "code": "ERROR_CODE",
  "message": "사용자에게 보여줄 메시지",
  "detail": "개발자용 디버그 정보 (운영 환경에서는 생략)"
}
```

### 주요 에러 코드

| code | HTTP Status | 의미 |
|------|------------|------|
| `SUCCESS` | 200 | 정상 |
| `BAD_REQUEST` | 400 | 파라미터 오류 |
| `UNAUTHORIZED` | 401 | 인증 필요 |
| `FORBIDDEN` | 403 | 권한 없음 |
| `NOT_FOUND` | 404 | 리소스 없음 |
| `INTERNAL_ERROR` | 500 | 서버 오류 |

## 20.8 프로토타입 → 본개발 전환 기준

| 전환 조건 | 확인 항목 |
|----------|----------|
| UI 흐름 검증 완료 | 핵심 화면 38개(고객웹) 프로토타입 리뷰 완료 |
| 이해관계자 피드백 반영 | UX 수정사항 반영 완료 |
| 본개발 인프라 준비 | 개발서버 PostgreSQL·Redis·ES 접속 확인 |
| Mock → 실구현 전환 | Controller → Service → Repository 레이어 확장 |

---

*Confidential | 3TOP | v3.4 | 2026.06.26*
