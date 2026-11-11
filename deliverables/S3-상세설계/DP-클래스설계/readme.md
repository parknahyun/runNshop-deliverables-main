# 클래스 설계 — 주문·결제 도메인

> **단계**: 상세설계 (S3)
> **문서범위**: Bolt (Order + Payment)
> **문서종류**: Design
>
> **작성 목적**: 시퀀스(DM)에 등장한 참여 객체를 클래스 구조로 전환한다.
> "어떤 클래스가 어떤 책임을 갖고, 어떤 메서드를 제공하는가"를 확정하여
> 구현(코드) 단계의 직접 입력이 된다.
>
> **흐름 내 위치**:
> ```
> DM 시퀀스 (참여 객체) → DP 클래스 설계 → 구현
> ```

---

도메인별 파일로 분리되어 있습니다.

| 구분 | 파일 |
|---|---|
| Order 도메인 (패키지 구조·클래스 상세·엔티티) | [order.md](order.md) |
| Payment 도메인 (패키지 구조·클래스 상세·엔티티) | [payment.md](payment.md) |
| Catalog 도메인 (패키지 구조·클래스 상세·엔티티) | [catalog.md](catalog.md) |
| 도메인 간 공용 계약 (PublicApi) | [common.md](common.md) |

작성 규칙·근거는 각 도메인 파일에 동일하게 포함되어 있습니다. Catalog는 Order·Promotion이
호출하는 internal 컨트롤러를 자체 파일(catalog.md) 내 `internal/` 패키지에 포함한다 —
common.md는 Order+Payment Bolt 전용 파일이라 Catalog PublicApi 구현체는 별도 분리하지 않음.
