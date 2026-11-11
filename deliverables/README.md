
# 산출물 (Deliverables)

> 산출물 흐름 문서의 7단계 체계에 따라, 실제 프로젝트 산출물을 **작성순서** 기준으로 배치한다.
> 방법론 샘플(`docs/methodology/artifacts-sample/`)과 동일한 구조이며, 여기에는 **실제 프로젝트 산출물**이 들어간다.

---

## 폴더 구조

```
deliverables/
├── S0-착수/        ← D1~D6 (문제정의서·목표KPI·이해관계자맵·범위·대안비교·리스크가정)
├── S1-범위정의/    ← D7~DB (제약사항·NFR·컴포넌트·시스템구성도·도메인정의서)
├── S2-구조설계/    ← DC~DI (상위UC·메뉴구조도·EARS·ERD·상태머신·프로세스·이벤트) + Bolt 분할
├── S3-상세설계/    ← DJ~DQ (GWT·세부UC·인터페이스·시퀀스·화면·ADR·클래스·프로그램목록)
├── S4-구현/        ← 코드·자동검증·단위테스트
├── S5-테스트/      ← 통합테스트·E2E·GWT실행
├── S6-안정화/      ← 성능튜닝·버그수정·NFR검증·운영이관
└── conventions/    ← C1~C9 컨벤션 산출물 (보안·용어·아키텍처·데이터·이벤트·API·디자인시스템·UX Writing·코딩)
```

---

## 참조 자료 — as-is와 working의 구분

산출물을 작성할 때 참고하는 자료는 성격이 다른 두 가지로 나뉜다:

| 구분 | 위치 | 성격 | 용도 |
|---|---|---|---|
| **원본 자산** | `reference/assets-aswas/` | 방법론 적용 이전의 원본 문서(RFP·요구사항·정책서·도메인·화면정의 등). 수정하지 않는 archival 자료 | "실제 업무 사실이 뭔지" 확인 |
| **참고자료** | `reference/assets-working/` | as-is를 가공·분석한 보조자료(도메인기능표·화면정의서 샘플·가이드 등). 필요시 계속 갱신 | "어떤 형식·기준으로 작성할지" 확인 |

우선순위: as-is(사실) > working(형식·가이드). 두 자료가 충돌하면 as-is를 우선한다.

---

## 관련 문서

- [산출물 흐름](../reference/methodology/appendix/AI활용_개발방법론_산출물_흐름.md) — 7단계·작성순서·선행관계 정의
- [artifacts-sample](../reference/methodology/artifacts-sample/) — 단계별 표준 샘플 (방법론)
- [reference/assets-aswas](../reference/assets-aswas/) — 이관 전 원본 참조 자산
- [reference/assets-working](../reference/assets-working/) — 프로젝트 진행 중 작성된 보조 참고자료
