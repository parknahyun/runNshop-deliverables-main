# runNshop 요구사항 정의서 — 13. 전시·검색 (Display·Search)

> 상위 문서: [runNshop_requirements_v1_0.md](../runNshop_requirements_v1_0.md)
> 문서 버전: v1.0 | 상태: 확정 (Confirmed)

---

## FR-SCH-001 전시 페이지 렌더링
- **우선순위**: P1
- **내용**:
  - 템플릿 기반 동적 렌더링
  - 영역 유형: BANNER·PRODUCT_GRID·PRODUCT_LIST·EXHIBITION
  - 상품 노출 순서: md_override → ai_score → release_date
  - Redis 캐시 적용
  - 고객 홈 화면 영역 유형: MAIN_BANNER·MD_RECOMMEND·EXHIBITION·NEW_PRODUCT·BRAND_BANNER
  - 상품 카드: 할인율(discount_rate) 존재 시에만 정가 취소선·할인 배지 노출, 평점(rating) 0이면 별점 영역 미노출
  - 기획전 목록 상태: ACTIVE(진행중)·SCHEDULED(예정)·ENDED(종료) 3종 배지 구분

## FR-SCH-002 통합 검색
- **우선순위**: P1
- **내용**:
  - 대상: 상품명·브랜드·태그
  - Elasticsearch 기반
  - 자동완성·인기 검색어 지원
  - 인기 검색어: MD 수동 관리
- **관련 화면**: CUS-030

## FR-SCH-003 상품 필터·정렬
- **우선순위**: P1
- **내용**:
  - 카테고리·브랜드·가격·사이즈·색상 필터
  - 정렬: 최신순·인기순·가격순·평점순
  - 품절 상품: 동일 위치 노출

## FR-SCH-004 전시 예약
- **우선순위**: P1
- **내용**:
  - 페이지당 예약 1개 허용
  - DisplayPageScheduleBatch: 매 5분 자동 전환
  - 배치 실패: DLQ·수동 전환
  - 페이지는 상태(status)+게시일(publishedAt) 단일 필드 구조로 관리되어 페이지당 예약이 자연히 1개로 제한됨
  - 예약 등록 시 시작일시 ≤ 종료일시 검증
  - 게시일시(publishedAt)는 최초 PUBLISHED 전환 시점에만 기록, 이후 재게시해도 갱신되지 않음

## FR-SCH-005 인덱스 동기화
- **우선순위**: P1
- **내용**:
  - 실시간: 상품 승인·가격변경·품절 이벤트 수신
  - 배치: ProductIndexSyncBatch (매일 03:00) 전체 동기화

## FR-SCH-006 전시 템플릿·섹션 관리
- **우선순위**: P1
- **내용**:
  - 템플릿(템플릿ID·템플릿명·유형·상태·영역수·사용 페이지수) CRUD, 유형: HOME·CATEGORY·EXHIBITION·EVENT
  - 섹션 타입(섹션코드·영역유형·상태·필드스키마) CRUD, 영역 유형: BANNER·PRODUCT_GRID·TEXT·IMAGE_LINK·COUNTDOWN·COUPON_BAND·DIVIDER·PRODUCT_CAROUSEL
  - 필드 타입: 이미지·상품·텍스트·링크·색상·숫자·날짜시간·선택·이미지배열·상품배열·텍스트배열
  - 공통코드(그룹→코드) 관리로 선택형 필드 기본값 제공

---

*Confidential | 3TOP | 요구사항 정의서 v1.0 | 2026.06.25*
