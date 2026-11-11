---
inclusion: manual
---
# Steering 파일 가이드 (runNshop-docs 허브)

이 레포(`runNshop-docs`)는 파생 프로젝트(`runNshop-react-kotlin`, `runNshop-vue-java` 등)가
git submodule로 참조하는 **공통(표준) steering/skill의 원본**이다. 분류 기준과 전체 구조는
`docs/methodology/파생프로젝트-가이드.md` 참조.

## 이 레포에 있는 것 = 전부 "공통(표준)"

언어/프레임워크에 종속되지 않는 규칙만 둔다. 특정 언어·프레임워크 전용 가이드(Kotlin, Next.js,
Java, Vue 등)는 이 레포에 두지 않고 각 파생 레포 자체에 둔다.

| 파일 | 용도 |
|------|------|
| work-scope.md | 작업 범위, 도출 근거 원칙 |
| api-design-rules.md | URL prefix, Controller 분리 기준 |
| mock-data-rules.md | Mock 파일명, 응답 표준 |
| screen-definition.md | 화면정의서 참조 |
| coding-standards.md | 공통 코딩 컨벤션, 네이밍, Git 규칙, 앱별 스택 레지스트리 |
| admin-ux-pattern.md | admin/partner 화면 유형·Shell구조·색상·spec.md 규칙 (React+Vue 공통) |

## 관련 Skill (`.kiro/skills/`)

| Skill | 용도 |
|---|---|
| design-doc-to-code | 화면설계→코드 변환 공통 절차 |
| backend-service-pattern | Controller/Service 레이어 패턴 (언어 무관) |
| derivative-project-scaffold | 신규 파생 프로젝트 생성 절차 |

## 파생 레포 쪽 사용법

각 파생 레포는 이 레포를 `docs/` 경로에 git submodule로 추가하고, 자기 `.kiro/steering/`·
`.kiro/skills/`에 위 파일들을 가리키는 **stub 파일**을 둔다(`#[[file:docs/.kiro/...]]`로 include).
원본을 복사하지 않는다 — 이 레포가 바뀌면 각 파생 레포가 원하는 시점에
`git submodule update --remote docs`로 동기화한다.
