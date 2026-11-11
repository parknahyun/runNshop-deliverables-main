# runNshop 프로젝트 Scaffolding 가이드

> 작성 주체: 3TOP 2본부
> 문서 버전: v1.0
> 작성일: 2026.06.26
> 상태: 확정

---

## 1. 목적

docs 폴더의 설계 문서를 기반으로 runNshop 프로젝트를 처음부터 생성하는 절차를 정의한다.

---

## 2. 전제 조건

| 항목 | 버전 |
|------|------|
| Node.js | 20+ |
| JDK | 21 (OpenJDK) |
| Gradle | 8.8+ |
| npm | 10+ |

---

## 3. Scaffolding 순서

### Step 1: docs 기반 설계 확인

| 순서 | 문서 | 확인 내용 |
|------|------|---------|
| 1 | `1. 요구사항/` | 기능 범위·화면 수 |
| 2 | `2. 정책서/` (v1_1) | 프로토타입 정책 (20장) |
| 3 | `3. 도메인/bounded_context` | 12개 도메인 목록 |
| 4 | `6. 화면정의/screen_definition` | 메뉴 구조·화면 유형·API 목록 |
| 5 | `6. 화면정의/admin_screen_guide` | 화면 구조 재사용 패턴 |
| 6 | `7. 기술정의/tech_stack` | 기술 스택·폴더 구조 |

### Step 2: Back-end API 생성

1. `api/runNshop-api/` 디렉토리 생성
2. `build.gradle.kts` + `settings.gradle.kts` 작성
3. 12개 도메인 패키지 생성 (controller/service/dto)
4. `common/MockLoader.kt` + `CorsConfig.kt` 생성
5. `RunnshopApiApplication.kt` 생성
6. `resources/mock/{v1,admin,partner}/` 디렉토리 생성
7. Gradle wrapper 생성 (`gradle wrapper`)
8. 실행 확인 (`./gradlew bootRun`)

### Step 3: Front-end 고객웹 생성

1. `apps/runNshop-mobile/` 디렉토리 생성
2. package.json (Next.js 14 + Tailwind)
3. tsconfig.json, next.config.js, tailwind.config.ts, postcss.config.js
4. `app/layout.tsx` + `app/page.tsx`
5. `lib/api.ts` (PREFIX = '/api/v1')
6. `styles/globals.css` (@tailwind)
7. `.env.example`
8. 실행 확인 (`npm install && npm run dev`)

### Step 4: Front-end 어드민 생성

1. `apps/runNshop-admin/src/` 디렉토리 생성
2. package.json (Next.js 15, Tailwind 없음)
3. tsconfig.json (`paths: @/* → ./src/*`), next.config.ts
4. `src/app/layout.tsx` + `src/app/page.tsx` + `src/app/globals.css`
5. `src/shell/TabContext.tsx` + `src/shell/AppShell.tsx` + `src/shell/Dashboard.tsx`
6. `src/shell/shared/Pagination.tsx` + `src/shell/shared/InnerTabs.tsx`
7. NAV_MENUS: 화면정의서 3.3 메뉴 트리 기준
8. Dashboard: 고정 pinned 탭
9. 실행 확인

### Step 5: Front-end 입점사 생성

1. Step 4와 동일 구조 (색상만 다크 오렌지 적용)
2. NAV_MENUS: 화면정의서 4.2 메뉴 트리 기준
3. globals.css에서 색상 치환 (#1e293b→#7c2d12, #3b82f6→#ea580c)

### Step 6: .kiro 설정

1. `KIRO_START.md` 작성
2. `steering/` 폴더 생성:
   - coding-standards.md (always)
   - api-design-rules.md (always)
   - mock-data-rules.md (always)
   - admin-guide.md (fileMatch: admin/partner tsx)
   - kotlin-guide.md (fileMatch: *.kt)
   - nextjs-guide.md (fileMatch: mobile tsx)
   - screen-definition.md (manual)

### Step 7: 첫 번째 화면 구현

- 우선순위: API Mock → 고객웹 홈(CUS-001) → 어드민 홈(ADM-HOME) → 입점사 홈(VND-HOME)
- 각 화면의 Mock JSON + Controller + 프론트 컴포넌트 세트로 구현

---

## 4. 수정 발생 시 갱신 규칙

| 변경 사항 | 갱신 대상 |
|----------|---------|
| 도메인 추가/제거 | bounded_context + tech_stack + KIRO_START |
| 화면 추가 | screen_definition + admin_screen_guide |
| API 추가 | screen_definition (API 목록) + Mock JSON |
| 기술 스택 변경 | tech_stack + KIRO_START + steering |
| 정책 변경 | policy (버전 올림) + steering |

---

## 5. 참조 문서 매핑

| scaffolding 단계 | 참조 docs |
|-----------------|---------|
| 도메인 패키지 생성 | `3. 도메인/bounded_context` |
| API Controller 생성 | `6. 화면정의/screen_definition` (API 목록) |
| Mock JSON 생성 | `5. 엔티티정의/erd` + `6. 화면정의/screen_definition` |
| 메뉴 구조 | `6. 화면정의/screen_definition` (3.3, 4.2) |
| 화면 유형 결정 | `6. 화면정의/screen_definition` (6장 화면 유형) |
| 화면 구조 패턴 | `6. 화면정의/admin_screen_guide` |
| 비즈니스 룰 | `2. 정책서/policy` |

---

*Confidential | 3TOP | Scaffolding 가이드 v1.0 | 2026.06.26*
