---
name: derivative-project-scaffold
description: runNshop docs를 허브로 새로운 기술스택 파생 프로젝트(예: Vue+Java)를 만들 때 사용. 레포 생성, docs submodule 연결, 공통/언어별 steering·skill 분리, WBS 트래킹 초기화, derivative-projects.md 레지스트리 등록 절차를 다룬다. 방법론 근거는 docs/methodology/파생프로젝트-가이드.md.
---

> **분류: 공통(표준, 운영 skill)** — 이 skill은 파생 프로젝트를 "만드는 행위" 자체를 다루므로 언어에 종속되지 않는다. 허브(`runNshop-docs`)에 귀속되는 skill이며, 실제 신규 레포 생성·대규모 코드 포팅이 필요한 단계는 이 skill만으로 끝내지 말고 휴먼 확정 후 별도 작업(워크플로우 등)으로 진행한다.

# 파생 프로젝트 생성 절차

## 사전 확인 (휴먼 확정 필요 — 임의 진행 금지)
다음이 확정되지 않았으면 먼저 사용자에게 묻는다:
1. 프론트/백엔드 스택 조합과 레포명 (`runNshop-{frontend}-{backend}` 패턴)
2. 신규 레포 생성 권한/방법 (예: `gh repo create`) 보유 여부
3. 기존 구현(예: `runNshop-react-kotlin`)과 **병행 운영**인지, 완전 대체인지
4. 이번에 구현할 범위(전체 도메인 포팅인지, 특정 도메인/화면부터 시작하는 점진적 포팅인지)

## 절차

### 1. 레포 생성 + docs submodule 연결
```bash
# 새 레포가 이미 생성되어 있다고 가정
git submodule add <runNshop-docs repo url> docs
git submodule update --init --recursive
```
커밋에 "이 구현이 참조하는 docs 시점"이 고정된다. 이후 docs가 바뀌면 자연스러운 경계(새 Bolt 착수 등)에서만 `git submodule update --remote docs`로 동기화한다 — 매번 자동 추적하지 않는다.

### 2. 공통 steering/skill 연결 (stub)
`docs/methodology/파생프로젝트-가이드.md` §4 표의 "공통" 행에 해당하는 steering/skill을, 새 레포 자체 `.kiro/steering/`·`.kiro/skills/`에 **짧은 stub 파일**로 둔다(원본 복사 금지). stub은 `#[[file:docs/.kiro/steering/{원본}.md]]`로 허브 원본을 include한다. Kiro가 submodule 내부 `.kiro/`를 자동 탐색하지 않을 수 있으므로, 실제 로딩되는 파일은 새 레포의 `.kiro/steering/` 쪽 stub이어야 한다.

### 3. 언어/프레임워크 전용 steering·skill 신규 작성
공통에서 빠진 부분(파일 구조, 문법, 빌드 도구)만 신규로 쓴다. 기존 언어별 가이드(`kotlin-guide.md`/`nextjs-guide.md`/`admin-guide.md`/`screen-to-fe-code`)의 구조를 참고해 동일한 수준으로 작성한다 — 공통 skill(`design-doc-to-code`, `backend-service-pattern`, `admin-ux-pattern.md`)이 이미 다루는 내용은 반복하지 않고 참조만 한다.

### 4. 디렉토리 스캐폴딩
`apps/`, `api/` 등 기존 컨벤션을 그대로 따른다. 새 백엔드 모듈의 `mock-data-rules.md` 적용 루트(`{모듈}/src/main/resources/mock/`)를 레지스트리(§6)에 남긴다.

### 5. 버전 결정 — 공통 산출물 기반 추천치 재사용
새 언어/런타임 버전(Java, Node 등)과 프레임워크 버전은 임의로 최신을 쓰지 않고, `derivative-projects.md`에 이미 기록된 추천 버전·근거(EOS 등)를 우선 재사용한다. 기록이 없으면 결정 후 이 레지스트리에 근거와 함께 추가한다.

### 6. WBS 트래킹 초기화
`docs/methodology/파생프로젝트-가이드.md`의 WBS 템플릿(L0~L3)을 가져와, 새 레포 자체에 **0%(전체 미착수)** 상태의 진행 트래킹 문서를 만든다. 허브의 WBS에는 진행률을 기록하지 않는다.

### 7. 레지스트리 등록
`derivative-projects.md`에 신규 행을 추가한다 — 프로젝트명/스택/레포/상태/비고.

### 8. 도출 근거 원칙 재확인
`work-scope.md`를 그대로 적용한다 — 새 클래스명·메서드명·API 경로를 짓기 전에 `deliverables/S3-상세설계/DP-클래스설계/{domain}.md`, `DL-인터페이스명세/{domain}.md`에 이미 정의된 식별자가 있는지 먼저 검색하고, 있으면 그대로 쓴다.

## 완료 기준
위 1~7이 끝나면 새 파생 레포는 "docs를 허브로 참조하는 빈 스캐폴드" 상태가 된다. 실제 도메인 코드 포팅(대규모 작업)은 이 skill의 범위가 아니다 — 범위를 정해 별도로 진행한다.
