# GWT 수용기준

> **단계**: 상세설계 (S3)
> **문서범위**: Bolt (Order + Payment + Catalog)
> **문서종류**: Spec
>
> **작성 목적**: EARS(DD)의 기능요구를 Given-When-Then 시나리오로 변환하여,
> "이 요구가 올바르게 구현되었는지 어떻게 검증하는가"를 정의한다.
> QA가 그대로 테스트 케이스로 사용할 수 있는 수준으로 작성한다.
>
> **흐름 내 위치**:
> ```
> Bolt 분할 → DJ GWT → DK 세부UC → DL 인터페이스 명세
> ```

---

도메인별 파일로 분리되어 있습니다. ID 접두사(`AC-ORD-*`/`AC-PAY-*`/`AC-CAT-*`) 기준으로 나뉘며,
Order·Payment처럼 두 도메인에 걸친 Bolt(예: "3. 결제 완료 처리", "15. 어드민 환불·폐기·반송")는
같은 제목으로 양쪽 파일에 각자 소유한 행만 나뉘어 있고, 상대 도메인 파일로 상호 참조 링크가
달려 있습니다. Catalog는 1차 파트(Order+Payment)와 겹치는 Bolt가 없어 독립 파일로 완결됩니다.

| 구분 | 파일 |
|---|---|
| Order 도메인 (AC-ORD-*) | [order.md](order.md) |
| Payment 도메인 (AC-PAY-*) | [payment.md](payment.md) |
| Catalog 도메인 (AC-CAT-*) | [catalog.md](catalog.md) |

근거는 각 도메인 파일에 동일한 패턴으로 포함되어 있습니다.
