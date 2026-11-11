# Spring Boot 4.1.1 업그레이드 + Skill 적용 내용 공유

이번 PR에는 두 가지 작업이 묶여 있습니다: (1) Spring Boot 3.x EOL 대응 업그레이드, (2) Order 도메인 작업 중 정립한 코딩 패턴을 **재사용 가능한 skill 2종**으로 문서화. PR 열기 전 팀원 공유용으로 정리했습니다.

---

## 1. Spring Boot 4.1.1 업그레이드 (EOL 대응)

### 왜 업그레이드했나

Spring Boot **3.3.0**(현재 사용 중)은 OSS 지원이 **2025-06-30 종료**됐습니다. 조사해보니 3.4, 3.5(3.x 마지막 버전)까지도 전부 EOL 상태(3.5는 2026-06-30 종료)라, 보안 패치를 받으려면 **메이저 버전(4.x)**으로 가야 하는 상황이었습니다. 현재 유지보수 중인 최신 안정 버전인 **4.1.1**로 업그레이드했습니다.

### 버전 변경 내역

| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| Spring Boot | 3.3.0 (EOL) | **4.1.1** |
| Kotlin | 1.9.25 | **2.3.21** |
| Dependency Management Plugin | 1.1.5 | **1.1.7** |
| Gradle | 8.8 | **9.7.1** |
| Jackson | 2.x (`com.fasterxml.jackson`) | **3.x (`tools.jackson`)** |

### 실제로 깨졌던 부분과 수정 내용

#### ① Kotlin `kotlinOptions` DSL 제거

Kotlin 2.3부터 기존 `kotlinOptions { ... }` 설정 방식이 완전히 제거(컴파일 에러)됐습니다. 신규 `compilerOptions` DSL로 전환했습니다.

```kotlin
// 변경 전
tasks.withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile> {
    kotlinOptions {
        freeCompilerArgs = listOf("-Xjsr305=strict")
        jvmTarget = "21"
    }
}

// 변경 후
kotlin {
    compilerOptions {
        freeCompilerArgs.add("-Xjsr305=strict")
        jvmTarget.set(org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_21)
    }
}
```

#### ② Jackson 2 → 3 전환 (가장 핵심적인 변경)

Spring Boot 4는 기본으로 **Jackson 3**을 사용합니다. Jackson 2는 공식적으로 **deprecated**(향후 제거 예정)라, 임시방편(Jackson 2 유지)이 아니라 Jackson 3으로 바로 전환하는 쪽을 선택했습니다.

영향받은 지점은 `MockLoader.kt` 한 곳뿐이었습니다 — 프로젝트 전체에서 Jackson을 직접 쓰는 코드가 여기뿐이라 전환 범위가 작았습니다.

```kotlin
// MockLoader.kt
// 변경 전
import com.fasterxml.jackson.databind.ObjectMapper
// 변경 후
import tools.jackson.databind.ObjectMapper
```

```kotlin
// build.gradle.kts
// 변경 전
implementation("com.fasterxml.jackson.module:jackson-module-kotlin")
// 변경 후
implementation("tools.jackson.module:jackson-module-kotlin")
```

API 시그니처(`objectMapper.readValue(...)`)는 그대로 호환돼서, import 경로와 의존성 좌표만 바꾸면 됐습니다. **Jackson 2를 직접 참조하는 코드를 새로 추가할 때는 `tools.jackson.*` 패키지를 써야 한다**는 점을 다들 알고 있으면 좋겠습니다.

### 검증 내용

- `./gradlew clean build -x test` 성공
- 서버 기동 후 **전 도메인**(Order, Catalog, Promotion, Vendor, Config, Member) 엔드포인트 curl 전수 확인 — 전부 `200 / {"code":"SUCCESS"}` 정상 응답
- Order 도메인의 validation 거부 케이스(`size=0` 등)도 여전히 `400 / {"code":"INVALID_SIZE", ...}`로 정상 동작 확인 (전역 예외 처리기도 Jackson 3 응답 직렬화와 문제없이 호환)

### 영향 범위 / 팀원이 확인해야 할 것

- **비즈니스 로직 변경 없음** — 전부 빌드 설정·의존성·import 레벨 변경이고, Controller/Service 코드 로직은 그대로입니다.
- **로컬 개발 환경**: Gradle Wrapper가 9.7.1로 바뀌어서, 다음 pull 후 처음 빌드할 때 Gradle 9.7.1을 새로 다운로드합니다 (`./gradlew` 사용 시 자동 처리).
- **Jackson 관련 신규 코드 작성 시**: `com.fasterxml.jackson.*`이 아니라 `tools.jackson.*`을 import해야 합니다. IDE 자동완성이 옛 패키지를 제안할 수 있으니 주의가 필요합니다.
- 이번 조사로는 `MockLoader.kt` 외 Jackson 2 직접 의존 코드는 발견되지 않았습니다 — 다른 곳에 있다면 공유해주세요.

---

## 2. Skill 적용 내용 — `.kiro/skills/`에 2종 신설

Order 도메인 작업(API 연동 전환, URL/네이밍 규칙 정리, Controller/Service 리팩토링)을 진행하며 반복적으로 쓴 패턴을 **재사용 가능한 skill**로 뽑아냈습니다. 다음에 다른 도메인 작업을 할 때 이 skill들이 자동으로 로드되어 같은 설명을 반복하지 않고 일관된 패턴을 적용합니다.

### 2-1. `screen-to-fe-code` — FE 쪽 (화면설계 → 코드)

DN-화면레이아웃 설계 문서를 읽고 admin/partner/mobile FE 코드로 변환하거나, 기존 화면의 하드코딩 mock을 API 연동으로 전환할 때 쓰는 skill입니다.

**핵심 규칙:**
- **하드코딩 전면 금지** — `MOCK_XXX` 데이터 배열 + `useState(MOCK_XXX)` 패턴 금지. 전부 `lib/api.ts`의 `api()`로 fetch.
- **조회 트리거는 전부 서버 재요청** — 필터/페이지/페이지크기 변경 시마다 서버에 새 쿼리. 클라이언트에서 `.filter()`/`.slice()`로 재가공하지 않음.
- **목록→상세는 ID만 전달** — row 객체 전체를 넘기지 않고, 상세 컴포넌트가 `{domain}Id`로 자체 fetch.
- **FE 네이밍은 camelCase 통일** — DL-인터페이스명세와 불일치하는 snake_case 관례는 발견 시 교정.
- **`mockData.ts` → `types.ts`로 명명** — 신규 화면부터는 타입 + 상태→라벨 매핑만 담는 `types.ts`로 작성 (하드코딩 데이터 배열은 두지 않음).
- **Controller 분리 전 병합 가능성 먼저 확인** — FE 앱 개수가 아니라 응답 스키마·권한이 같은지로 분리 여부 판단.

### 2-2. `backend-service-pattern` — BE 쪽 (Controller/Service 구현 패턴, 신규)

`screen-to-fe-code`의 **백엔드 짝**입니다. Kotlin Controller/Service를 구현·리팩토링할 때 쓰는 skill입니다.

**핵심 규칙:**
- **레이어 경계** — Controller는 요청/응답만, Service(들)만 주입받고 `MockLoader`를 직접 호출하지 않음. 이렇게 분리해야 DB 전환 시 Service 내부만 바뀌고 Controller는 그대로.
- **Service 메서드 내부 4단계 구조** — ① validation(명시적 거부, 조용한 보정 금지) → ② mapper execute(list/count/summary 쿼리 단위로 메서드 분리, 공유조건과 전용조건 구분) → ③ dto convert(`Map<String,Any>` 대신 명시적 DTO).
- **코멘트 규칙** — 모든 Controller/Service 메서드(public/private 포함)에 KDoc 필수. 섹션 주석은 최소 회원(mobile)/관리자(admin)/파트너(partner) 3채널로 구분.
- **공용 예외 처리** — `com.runnshop.common.exception`에 `ApiException` 계열(`BadRequestException` 등 400/401/403/404/409/422) + `GlobalExceptionHandler`(`@RestControllerAdvice`)를 전 도메인 공용으로 신설. `code` 값은 DL-인터페이스명세의 Error Responses 표를 그대로 사용.
- **적용 범위는 점진적** — 이 패턴은 Order 도메인에서 처음 정립됐고, 다른 도메인(member/catalog/promotion/vendor/config)은 아직 전체 적용되지 않음. 그 도메인을 다음에 건드릴 때 점진적으로 맞추는 방식이며, 지금 당장 일괄 리팩토링하지 않습니다.

### 실제로 이번에 신설된 공용 컴포넌트

`backend-service-pattern` skill에 따라 Order Service를 리팩토링하며, 전 도메인이 공유할 신규 파일이 생겼습니다:

- `com.runnshop.common.exception.ApiException` (+ 하위 6종 예외 클래스)
- `com.runnshop.common.exception.GlobalExceptionHandler`

이 두 파일은 **설치되는 순간 전 도메인에 자동 적용**됩니다. 다만 다른 도메인엔 아직 이 예외를 던지는 코드가 없어서, 당장 동작이 바뀌는 건 Order뿐이고 나머지 도메인은 영향 없습니다. 각자 담당 도메인에 validation/비즈니스 예외를 추가할 때 이 공용 예외 클래스를 사용해주시면 됩니다.

---

## 브랜치 / PR 상태

- 작업 브랜치: `fepest` (개인 브랜치, `main` 대비 커밋 3개 포함: Order 코딩 패턴 리팩토링 + skill 2종 신설 + Spring Boot 업그레이드)
- PR: 10월 14일 16:00 진행 예정 (`fepest` → `main`)
