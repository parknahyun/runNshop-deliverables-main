# runNshop-docs

runNshop **deliverables(실 산출물) 허브**. 파생 구현 프로젝트가 공통으로 참조하는 단일 원본
(Single Source of Truth)이다. 프로젝트 무관 방법론 자체는 [ai-dev-methodology](https://github.com/3top-fepest/ai-dev-methodology)
레포로 분리돼 있다(2026-11-06, 이력 보존 분리 — 아래 "원본 레포" 참고).

## 구성
- `deliverables/` — **산출물**. 방법론을 실제로 적용해 만드는 실제 작업 결과물(단계별 실
  프로젝트 산출물, `conventions/` 포함).
- `reference/` — **참조 자료**(산출물 작성 참고용). 세 가지로 구분한다:
  - `reference/assets-aswas/` — 방법론 적용 이전 원본 문서(source), 수정하지 않음
  - `reference/assets-working/` — as-is를 가공한 보조자료, 진행 중 계속 갱신
  - `reference/methodology/` — [ai-dev-methodology](https://github.com/3top-fepest/ai-dev-methodology)
    레포(`reference/.ai-methodology/`, git submodule, 숨김)의 `methodology/`만 가리키는
    심링크. read-only 참조 전용 — 이 레포에서 내용을 수정하지 않고, 갱신이 필요하면
    ai-dev-methodology 쪽에서 고친 뒤 `git submodule update --remote reference/.ai-methodology`로
    당겨온다.
- `review-alignment/` — 이 프로젝트(runNshop) 실 산출물에 대한 검토·정합성 점검 기록.
- `weekly-report/` — 진행 중인 주간보고(runNshop 프로젝트 진행 상황).
- `derivative-projects.md` — 파생 구현 프로젝트 레지스트리.
- `deliverables-viewer/` — 산출물 웹 뷰어 앱 (구 `docs-viewer/`).
- `.kiro/steering/`, `.kiro/skills/` — 언어/프레임워크에 종속되지 않는 공통(표준) 규칙. 상세는
  `.kiro/steering/README.md`.

> 2026-11-06: 위 폴더들은 과거 `docs/` 하위에 있었다(`deliverables/` 등). 방법론 자산이
> ai-dev-methodology로 분리된 뒤 `docs/` 한 겹을 유지할 실익이 없어져, 그 하위 폴더들을 레포
> 루트로 평탄화하고 `docs/`는 삭제했다. `docs-viewer/`도 `deliverables-viewer/`로 이름을
> 바꿨다. 같은 날, `reference/`를 "산출물 작성용 참고자료" 용도로 재정리했다 —
> `as-is/`→`assets-aswas/`, `working/`→`assets-working/`로 이름을 바꾸고, ai-dev-methodology를
> 숨김 submodule(`reference/.ai-methodology/`)로 추가해 `reference/methodology/` 심링크로만
> 노출했다.
>
> **주의(mkdocs 뷰어 제약)**: `deliverables-viewer/`(mkdocs)는 기본적으로 심링크를 따라가지
> 않아 `reference/methodology/`가 웹 뷰어에는 안 보일 수 있다 — 필요하면 추후 확인·보완.

## 방법론을 보려면

"이 산출물을 어떻게 작성하는가"(AI활용 개발방법론, 산출물 표준양식, 프롬프트 라이브러리,
신규 참여자 온보딩 등)는 이 레포에 없다 —
[ai-dev-methodology](https://github.com/3top-fepest/ai-dev-methodology) 레포를 참고한다.

## 파생 프로젝트
- [runNshop-react-kotlin](https://github.com/3top-fepest/runNshop-react-kotlin) — React + Kotlin/Spring Boot 구현
- [runNshop-vue-java](https://github.com/3top-fepest/runNshop-vue-java) — Vue + Java/Spring Boot 구현

현황과 추천 버전은 `derivative-projects.md` 참조. 신규 파생 생성 절차는
[ai-dev-methodology](https://github.com/3top-fepest/ai-dev-methodology)의
`docs/methodology/파생프로젝트-가이드.md`와 `.kiro/skills/derivative-project-scaffold/SKILL.md` 참조.

## 원본 레포
이 레포는 기존 `runNshop`(현재 아카이브) 레포에서 `docs/`, `docs-viewer/` 경로를 이력 보존하여
분리했다. GitHub의 `main`과 작업 브랜치 `fepest`가 분기돼 있었던 것을 병합해(2026-11-05 재동기화)
Catalog 도메인정책서 최신 재설계 내용까지 반영했다.

## 분리 이력
2026-11-06: 프로젝트 무관 방법론 자산(`docs/methodology/`, `docs/onboarding.md`, 방법론 관련
review-alignment·weekly-report)을 `git filter-repo`로 커밋 이력 보존한 채
[ai-dev-methodology](https://github.com/3top-fepest/ai-dev-methodology) 레포로 분리했다. 이
레포(runNshop-docs)엔 runNshop 프로젝트 고유 산출물(deliverables)·참조자료·리뷰·주간보고만
남겼다. `docs/archive/`(산출물샘플-공정별·자산화-공정별)는 미참조 확인 후 폐기했다.
