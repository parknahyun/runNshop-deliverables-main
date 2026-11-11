---
name: design-doc-to-code
description: DN-화면레이아웃 설계 문서를 읽고 화면을 구현할 때, FE 프레임워크(React/Vue 등)에 상관없이 먼저 거치는 공통 절차를 다룬다 — 문서 파싱, 데이터 흐름 원칙, 네이밍 컨벤션(camelCase), 화면 유형 판별, API/Mock 존재 확인·레이어 경계. 구체적인 프레임워크 코드 생성은 이 skill의 절차를 이어받는 프레임워크 전용 skill(예: screen-to-fe-code — React/Next.js)이 수행한다.
---

> **분류: 공통(표준)** — 프레임워크 무관. screen-to-fe-code(React), 향후 생길 Vue 전용 skill 등이 이 skill의 절차 1~4를 공유한다. 각 파생 프로젝트는 이 skill을 그대로 가져가고, 그 위에 자기 프레임워크 전용 skill만 추가한다.

# 화면설계 → 코드 변환 (공통 절차)

## 입력
- DN 문서 경로: `deliverables/S3-상세설계/DN-화면레이아웃/{app}/{domain}/{screen}.md`
- 문서 섹션: 메타블록(화면ID·앱·호출API) / 와이어프레임 / 화면 구성(영역별 데이터소스) / 화면 전환 / 유효성 검증 / 상태별 UI
- 1차 근거: DL-인터페이스명세(API 스키마), 도메인정의서/정책서. 후행 산출물(화면 내 안내 UI 텍스트, 비공식 참고자료)은 역참조하지 않는다 — DL/도메인정의서와 충돌하면 DL/도메인정의서가 우선.

## 데이터 흐름 원칙 (반드시 지킬 것 — 프레임워크 무관)

```
FE 컴포넌트 → lib/api.ts(또는 동등 모듈) → Controller (Spring Boot) → Service → MockLoader/Repository → mock/{domain}/*.json or DB → 응답
```

- **하드코딩 전면 금지**: 화면 쪽에 더미 데이터 배열을 두고 그걸로 초기 상태를 채우는 패턴은 금지. 모든 목록/상세 데이터는 API 호출 결과만 쓴다.
- **조회 트리거는 전부 서버 재요청**: 필터 조회 버튼 클릭, 페이지 번호 변경, 페이지 크기 변경 — 이 3가지 전부 서버에 새 쿼리로 fetch한다. "전체 목록을 한 번에 받아서 클라이언트가 재가공"하는 방식은 쓰지 않는다. 쿼리 파라미터(`keyword`, `status`, `from`, `to`, `page`, `size`)는 서버(Controller/Service)가 실제로 처리해 필터링+페이징된 결과와 `pagination`(page/size/totalCount/totalPages)을 응답으로 돌려주고, FE는 그 응답을 그대로 상태에 반영한다.
- **집계(SummaryBar 등)도 서버 응답 기준**: 상태별 건수 같은 집계는 서버가 응답에 `summary` 블록으로 내려주고, FE가 로컬에서 재계산하지 않는다.
- **목록→상세 이동 시 ID만 조건으로 전달**: 목록 row 객체 전체를 상세 컴포넌트에 넘기지 않는다. 상세 컴포넌트는 `{domain}Id`를 받아 자체적으로 `GET /{resource}/{id}` API를 호출해 최신 데이터를 가져온다.
- **상세 화면 내 하드코딩 금지**: 상세 탭/섹션 안에 적힌 옵션명·PG사명·주소·운송장번호 같은 더미 값은 전부 상세 API 응답 필드로 교체한다.

## 절차 1 — 문서 파싱
- 메타블록에서 화면ID, 앱(admin/partner/mobile), 호출 API 목록 추출
- "호출 API"가 가리키는 DL-인터페이스명세 문서를 열어 요청/응답 스키마, 쿼리 파라미터, 응답 필드명(대소문자 표기 그대로) 확인
- 화면 구성 표에서 영역별 데이터 소스(API vs FE 상태) 구분
- 같은 리소스를 가리키는 여러 API 문서(예: admin용/partner용)의 필드명이 다르면(예: `customer` vs `customerName`) **각 DL 스펙 그대로 유지**한다 — 억지로 통일하지 않는다. 통일하는 건 "FE 코드가 camelCase를 쓴다"는 네이밍 컨벤션 수준이지, 서로 다른 API의 필드 의미까지 맞추는 게 아니다.

## 절차 2 — 네이밍 컨벤션: FE는 camelCase로 통일
- admin/partner/mobile 전체 FE 타입·컴포넌트 필드 참조는 **camelCase**로 통일한다(React/Vue 등 프레임워크 무관).
- DB 컬럼(snake_case) ↔ Entity 필드(camelCase) ↔ Response DTO(camelCase) ↔ JSON(camelCase) ↔ FE(camelCase) 매핑은 백엔드 프레임워크(Spring JPA의 `SpringPhysicalNamingStrategy`, MyBatis `resultMap` 등)가 표준적으로 처리하는 영역이라, FE가 camelCase로 통일되어도 추후 실 DB/Mapper 연동 단계에서 문제가 없다. 이 부분은 재검토 불필요(확정 사항).

## 절차 3 — 화면 유형 판별 (admin/partner인 경우)
`.kiro/steering/admin-ux-pattern.md`(공통 UX 패턴) 기준으로 분류:
- 현황 화면(table): `.filter-bar → .summary-bar → .table-wrap → .pagination`
- 상세/등록/수정: 반드시 모달(`.detail-modal-overlay` + `.detail-modal`, InnerTabs) 또는 MDI 탭
- 메인 대시보드: `.dashboard__head` + `.dashboard__grid`

이 분류는 CSS 클래스/구조 수준이라 React(`admin-react`)든 Vue(`admin-vue`)든 동일하게 적용된다. 실제 구현 문법(JSX vs SFC, hooks vs composition API)은 프레임워크 전용 skill(`screen-to-fe-code` 등)이 담당한다.

mobile인 경우 해당 FE 스택의 전용 steering(Next.js라면 `nextjs-guide.md`)의 라우팅/상태관리 패턴을 따른다.

## 절차 4 — API/Mock 존재 확인

**Controller 분리 전 병합 가능성 먼저 확인** (`.kiro/steering/api-design-rules.md`): 여러 앱(admin/partner/mobile)에 "같은 기능"을 제공해야 한다고 해서 자동으로 Controller를 앱 수만큼 쪼개지 않는다. FE 개수가 아니라 **업무(응답 스키마·권한)가 같은지**가 기준이다.
- 먼저 DL-인터페이스명세에서 각 앱의 요청/응답 스키마를 나란히 비교한다.
- 응답 필드와 권한(노출 범위)이 완전히 동일하면 → 하나의 메서드에 여러 URL을 매핑한다.
- 하나라도 다르면(필드 추가/제외, 민감정보 노출 차이 등) → 앱별 Controller로 분리한다. 이때도 Service는 가능하면 공유한다(도메인당 단일 Service + 앱별 메서드).
- 임의로 "FE가 여러 개니 Controller도 여러 개"라고 가정하지 말고, 이 비교를 먼저 거친 뒤 결정한다.

**레이어 경계** — `mock/{domain}/*.json`에 담긴 데이터는 "Repository/Mapper가 쿼리했다면 돌려줬을 데이터"로 취급한다. 그 데이터를 가공(필터링, 정렬, 페이징, summary 집계)하는 로직은 Controller에 직접 넣지 않고 Service 클래스로 분리한다 — 상세는 `backend-service-pattern` skill 참조.

- 백엔드 모듈의 `{domain}/controller/`에 해당 Controller·엔드포인트 존재 확인
- `deliverables/S3-상세설계/DP-클래스설계/{domain}.md`에 Service 클래스명·메서드 시그니처가 이미 정의돼 있는지 먼저 확인한다 — **있으면 그 네이밍을 그대로 따른다**(임의로 새 Service 클래스명을 만들지 않는다). 없으면(신규 화면) 기존 메서드 네이밍 패턴과 일관되게 새 메서드를 추가한다.
- 백엔드 모듈의 `resources/mock/{domain}/`에 `{channel}__{METHOD}_{PATH}.json` 존재 확인 — 이 위치/네이밍은 `mock-data-rules.md`에 고정된 규칙이므로 변경하지 않는다.
- 없으면 DL-인터페이스명세 문서의 응답 스키마대로 Mock JSON 생성 (`{"code":"SUCCESS","data":{...}}` 표준 구조)
- 목록 API라면 Mock JSON에 전체 데이터셋(여러 건, 다양한 status)을 담아두고, **Service 메서드가 쿼리 파라미터로 이 데이터셋을 필터링+페이징해서 응답**하도록 구현한다.
- 상세 API는 하드코딩 제거 대상 필드(옵션/결제수단/주소 등)를 전부 응답에 포함시킨다.

## 프레임워크 독립성 — 이 skill이 존재하는 이유
"필터/페이지 변경 → API 호출 → 상태 갱신 → 서버 응답 그대로 렌더"라는 데이터 흐름 패턴, 문서 파싱 절차, camelCase 네이밍, API/Mock 확인 절차는 React든 Vue든 동일하다. 실제로 바뀌는 부분은 "컴포넌트 문법"(JSX+hooks vs SFC+composition API)뿐이다. 이 skill(절차 1~4)을 공통으로 두고, 프레임워크 전용 skill이 절차 5(파일 생성) 이후만 담당하게 분리한 이유가 여기 있다 — 새 프레임워크가 추가될 때마다 이 skill을 다시 쓰지 않아도 된다.

## 다음 단계
파일 생성·구체 코드 작성은 프레임워크 전용 skill로 넘어간다 — 예: `screen-to-fe-code`(React/Next.js, admin-react·partner·mobile 공통).
