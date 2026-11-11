# runNshop 요구사항 정의서 — 4. 상품·카탈로그 (Catalog)

> 상위 문서: [runNshop_requirements_v1_0.md](../runNshop_requirements_v1_0.md)
> 문서 버전: v1.0 | 상태: 확정 (Confirmed)

---

## FR-CAT-001 카테고리 관리
- **우선순위**: P1
- **내용**:
  - 표준 카테고리: 상품 등록 기준
  - 전시 카테고리: 고객 화면 노출 기준
  - N:M 매핑 (cat_standard_display_category_mapping)
  - 자동 매핑: is_default=TRUE 기준
  - 우선순위: BRAND(2) > CATEGORY(1) > DEFAULT(0)
  - 표준/전시 카테고리 각각 대분류·중분류·소분류 3단계 독립 관리, categoryId·depth는 생성 후 변경 불가
  - 전시 카테고리는 status(ACTIVE/INACTIVE)와 별개로 visible(GNB 노출 여부) 필드 보유
  - 카테고리 삭제 미지원, INACTIVE 처리로 대체
  - 화면: 표준카테고리 ADM-020-003, 전시카테고리 ADM-020-004

## FR-CAT-002 상품 등록
- **우선순위**: P1
- **내용**:
  - 6단계: 기본정보·가격·이미지·상세소개·SKU·완료
  - 임시저장(DRAFT) 지원
  - 이미지: 최대 10장·5MB
  - 금지어: BLOCK(차단)·MASK(마스킹)
  - 상품 상세 타입 자동 적용
  - 가격 검증: 판매가 ≤ 정가, 공급가 ≤ 판매가
  - 옵션은 최대 2단계(예: 색상·사이즈)로 제한, 값 입력 후 SKU 생성 버튼으로 조합 생성(생성된 조합은 재생성되지 않음)
  - SKU별 판매중/판매중지 상태 개별 설정 가능(상품 전체 판매상태와 무관)
  - 메인 이미지는 용도별(목록형·카드형·상세형·썸네일형) 리사이징 이미지를 용도당 1개까지 등록 가능
  - 관리자도 간이 등록 가능(상품명·브랜드·카테고리·입점사명·정가·판매가), 등록 시 심사상태(PENDING) 자동 설정, 선택 판매상태는 심사 승인 후 적용
- **관련 화면**: VND-010-002

## FR-CAT-003 상품 심사
- **우선순위**: P1
- **내용**:
  - 상태: DRAFT → REVIEW_REQUESTED → UNDER_REVIEW → ON_SALE/REJECTED
  - Rekognition 이미지 비동기 분석 (2단계)
  - 반려 3회 이상: MD 특별 검토 플래그
  - 재심사: 거절 후 30일 이후 가능
  - 심사 기간: 7영업일 이내
  - 반려 처리 시 반려 사유 입력 필수, 입점사에게 전달
  - 판매상태에는 판매중·품절·심사중·반려·임시저장 외 판매종료(DISCONTINUED) 상태가 별도 존재
  - 입점사는 심사와 별개로 상품 상세에서 상태를 판매중/품절/임시저장 중 직접 변경 가능

## FR-CAT-004 재고 관리
- **우선순위**: P1
- **내용**:
  - 3테이블 구조: cat_sku → cat_sku_stock → cat_sku_stock_history
  - 품절 자동 전환: available_quantity=0 → SOLD_OUT
  - 취소 재고 복구: 자동 (SOLD_OUT → ON_SALE)
  - 반품 재고 복구: 수동 (입점사 검수 후)
  - 변경 이력 source: ORDER·CANCEL_RESTORE·RETURN_RESTORE·CATALOG
  - 재고 변경은 입고(IN)/출고(OUT)/조정(ADJUST) 유형과 사유(메모) 필수 입력으로 기록, 이력은 수정·삭제 불가(정정 시 반대 방향 조정 이력 추가)
  - SKU별 안전재고(safety stock) 값 설정, 현재고가 안전재고 미만이면 경고 표시
  - 재고 엑셀 일괄 업로드/다운로드(양식 다운로드 포함) 기능 제공

## FR-CAT-005 상품 미리보기
- **우선순위**: P1
- **내용**:
  - preview_token 발급 (Redis TTL 30분)
  - 고객 화면 기준 렌더링
  - 미리보기 모드 배너 표시
  - 장바구니·구매·찜 비활성

## FR-CAT-006 전시 페이지 관리
- **우선순위**: P1
- **내용**:
  - 유형: 홈·카테고리·기획전
  - 즉시 게시·예약 게시 지원
  - 예약: 페이지당 1개만 허용 (조건부 유니크 인덱스)
  - 운영 중 수정: DRAFT_EDIT 행 별도 생성
  - 편집 잠금: 30분 (동시 편집 방지)
  - 페이지 유형: HOME·CATEGORY·EXHIBITION·EXHIBITION_MAIN·PROMOTION·BRAND
  - 페이지 등록은 2단계(템플릿 선택 → 기본정보 입력), 슬러그(slug) 미입력 시 페이지명 기반 자동 생성
  - 신규 페이지 등록 시 선택 가능한 상태는 DRAFT·SCHEDULED·PUBLISHED로 제한
  - 템플릿은 복사(참조 아님) 방식으로 페이지에 적용, 템플릿 수정이 기존 페이지에 영향 없음
  - 섹션은 개별적으로 화면 노출 여부(visible) 토글 가능

| 상태 | 설명 |
|------|------|
| DRAFT | 최초 작성 중 |
| DRAFT_EDIT | PUBLISHED 수정 중 |
| PUBLISHED | 고객 화면 노출 |
| SCHEDULED | 예약 대기 |
| RESERVED | 이전 버전 보관 |
| CLOSED | 종료 |
| CANCELLED | 예약 취소 |

## FR-CAT-007 브랜드 관리
- **우선순위**: P1
- **내용**:
  - 브랜드 등록·수정·삭제
  - 브랜드 인증 여부 관리
  - 카테고리 매핑 우선순위 반영
  - 필드: 브랜드ID(BRD-XXX)·브랜드명·영문명·이미지·설명·상품등록수(자동 집계)·상태(ACTIVE/INACTIVE)
  - 브랜드 삭제 미지원, INACTIVE 처리로 대체
  - 화면: ADM-020-006
- **관련 테이블**: cat_brand

---

*Confidential | 3TOP | 요구사항 정의서 v1.0 | 2026.06.25*
