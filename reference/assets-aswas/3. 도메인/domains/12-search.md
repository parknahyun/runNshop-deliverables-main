# 러닝 커머스 플랫폼 Bounded Context 정의서 — 12. Search

> 상위 문서: [runNshop_bounded_context_v1_0.md](../runNshop_bounded_context_v1_0.md)
> 문서 버전: v1.0 | 상태: 초안 (Draft)

---

## 핵심 책임

> 전 도메인의 콘텐츠를 통합 인덱싱하여 검색·필터·정렬 서비스를 제공한다.

## 소유 데이터

| 엔티티 | 설명 |
|--------|------|
| `ProductIndex` | 상품 인덱스 (상품명·브랜드·태그·가격·평점·출시일) |
| `ExhibitionIndex` | 기획전·이벤트 인덱스 |
| `CommunityIndex` | 커뮤니티 콘텐츠 인덱스 |
| `SearchKeyword` | 인기 검색어 (MD 수동 관리) |
| `AutoComplete` | 자동완성 데이터 |

## 검색 기준

| 항목 | 기준 |
|------|------|
| 검색 대상 | 상품명·브랜드·태그 전체 |
| 기본 정렬 | 출시일 내림차순 (`release_date`) |
| 품절 상품 | 동일 위치 노출 |
| 인기 검색어 | MD 수동 관리 (추후 배치 자동화) |

## 제공 API

| API | 설명 |
|-----|------|
| `GET /search?q={keyword}` | 통합 검색 |
| `GET /search/products` | 상품 검색·필터 |
| `GET /search/autocomplete` | 자동완성 |

## 수신 이벤트

| 이벤트 | 발행 도메인 | 처리 내용 |
|--------|-----------|---------|
| `ProductApproved` | Catalog | 상품 인덱스 추가 |
| `ProductSoldOut` | Catalog | 품절 상태 갱신 |
| `ProductPriceChanged` | Catalog | 가격 인덱스 갱신 |
| `ProductUpdated` | Catalog | updated_at 갱신 (장바구니 유효성 검사 기준) |
| `EventPriceSoldOut` | Promotion | 행사가 종료 갱신 |
| `ExhibitionPublished` | Promotion | 기획전 인덱스 추가 |

## 배치 인덱스 동기화

| 대상 | 주기 | API |
|------|------|-----|
| ON_SALE 상품 | 주기적 | Catalog API |
| 기획전·이벤트 | 주기적 | Promotion API |
| 커뮤니티 콘텐츠 | 주기적 | Community API |

---

*Confidential | 3TOP | Bounded Context v1.0 | 2026.06.22*
