# 비즈니스 프로세스 — Catalog

> **단계**: 구조설계
> **문서범위**: Domain
> **문서종류**: Design
>
> **작성 목적**: 상태머신(⑩)의 전이를 액티비티 흐름으로 확장하여, "누가 어떤 순서로 업무를 수행하는가"를 시각화한다.
> **흐름 내 위치**: ⑩ 상태머신 → **⑪ 비즈니스 프로세스** → ⑫ 이벤트 플로우
> **작성 주체**: 시니어 개발자 + AI 협업 (기획자·현업 검토·확인)

| 항목 | 내용 |
|---|---|
| ID | DESIGN-BP-CATALOG-001 |
| 상태 | **Draft** |
| 작성일 | 2026-08-21 |
| 갱신일 | 2026-11-06 |

> **2026-10-26 갱신**: `DH-상태머신/catalog.md`(직매입/입점형 분기 반영)·`DD-EARS기능요구/
> catalog.md`(REQ-CAT-001~051)를 기준으로 갱신했다. 구버전은 입점형 심사 프로세스만 있고
> 직매입 경로가 없었고, 재고 자동전환이 "SKU 합산" 기준으로만 서술돼 대안A(발생원인 무관·
> MD확인불필요)가 명확하지 않았다. 출시일 노출 게이트(C안) 프로세스를 신규 추가했다. 용어는
> "판매자"로 통일했다(C2 3관점 원칙).
>
> **2026-11-06 재동기화**: DBA 번호 재정비(2026-11-04)에 맞춰 전체 "DBA §x.x" 인용을
> 갱신하고, 신규 프로세스 3건(재고 품절임박 알림 발송, 찜 데이터 자동 삭제, 전시여부
> 플래그에 의한 긴급 회수·대체노출)을 추가했다.

---

## 1. 상품등록·심사 프로세스

> **직매입/입점형 분기**: `is_direct_sourced` 값에 따라 심사 게이트 유무가 갈린다(DH 1절,
> DBA §1.5.1). 분기점에서 경로가 나뉘고 직매입은 즉시 종료된다.

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title 상품등록·심사 비즈니스 프로세스

|관리자(MD) — 직매입등록자|
start
if (등록 경로?) then (직매입)
  :직매입 상품 정보 입력\n(name, category, price, image);
  :등록 완료;
  :상태: DRAFT → ON_SALE\n(심사 게이트 생략);
  stop
else (입점형)
endif

|판매자|
if (일반 등록 또는 복제/대량등록?) then (복제)
  :본인 상품 선택 후 복제 요청;
  :가격·재고·판매자상품코드 제외한\n전체 항목 복사 (이미지는 원본 참조);
  :신규 productId·skuId·상품번호 발급;
  :상태: DRAFT (등록 경로 그대로 재적용);
else (대량등록)
  :엑셀 업로드\n(기본정보+옵션/SKU);
  :행 단위로 DRAFT 상품 일괄 생성;
else (일반)
  :상품 초안 작성\n(name, category, price, image);
  :상태: DRAFT;
endif

if (필수 필드 충족?) then (yes)
  :심사 요청;
  :상태: REVIEW_REQUESTED;
else (no)
  :필수 필드 미충족 안내;
  stop
endif

|관리자(MD) — 심사자|
:심사 착수;
:상태: UNDER_REVIEW;

if (상품 적합?) then (승인)
  :심사 승인;
  :상태: ON_SALE;
  :ProductApproved 이벤트 발행;
  stop
else (반려)
  :반려 사유 작성;
  :상태: REJECTED;
  :reject_count +1, rejected_at 갱신;
  :판매자 알림 발송;

  if (동일 사유 3회 이상 반복?) then (yes)
    :입점 심사팀 에스컬레이션;
  else (no)
  endif
endif

|판매자|
:반려 사유 확인;

if (30일 이내 수정?) then (yes)
  :상품 수정;
  :상태: DRAFT;
  backward :심사 요청;
else (30일 초과)
  |시스템(배치)|
  :재제출 기한 만료 감지;
  :상품 자동 삭제;
  stop
endif

@enduml
```

---

## 2. 재고 선점 프로세스 (동기)

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title 재고 선점 비즈니스 프로세스 (동기)

|시스템(Order)|
start
:재고 차감 요청\n(sku_id, quantity);

|시스템(Catalog)|
:SKU 가용 재고 조회\n(available_quantity);

if (available_quantity >= 요청 수량?) then (yes)
  :available_quantity 차감;
  :sold_quantity_total 증가;
  :cat_stock_history 기록\n(change_type: RESERVE);
  :StockChanged 이벤트 발행;

  if (available_quantity == 0?) then (yes)
    :상품 상태: ON_SALE → SOLD_OUT;
    :cat_product_wishlist 삭제\n(DBA §1.14);
  else (no)
    if (기준수량 이하?) then (yes)
      :재고 품절 임박 알림 트리거\n(아래 8절);
    else (no)
    endif
  endif

  :성공 응답 반환;
  stop
else (no)
  :INSUFFICIENT_STOCK 응답 반환;
  stop
endif

@enduml
```

---

## 3. 재고 복원·자동전환 프로세스 (대안A, 비동기)

> **대안A 핵심**: 재고 복원의 **발생 원인과 무관하게** 재고 1 이상이면 MD 확인 없이 자동
> ON_SALE 전환한다(DBA §1.10, REQ-CAT-022). 발생 원인 3가지(주문취소·반품교환확정·판매자
> 재고신규등록)를 하나의 플로우로 통합 표현한다 — 분기는 원인 기록(change_type)에만 있고,
> 전환 로직 자체는 공통이다.

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title 재고 복원·자동전환 비즈니스 프로세스 (대안A)

|시스템(Order)| as ORD
|판매자| as VND
|시스템(Catalog)| as CAT

start

split
  :ORD: ORDER_CANCELLED 이벤트 발행;
  -> 주문 취소;
split again
  :ORD: 반품·교환 확정 이벤트 발행;
  -> 반품·교환;
split again
  :VND: 재고 수량 신규 등록(+N);
  -> 판매자 재고등록;
end split

|시스템(Catalog)|
:이벤트/요청 수신;

if (이벤트 수신 건?) then (yes)
  :멱등 검증 (eventId 중복 체크);
  if (이미 처리됨?) then (중복)
    :무시 (멱등);
    stop
  else (신규)
  endif
else (판매자 직접 등록)
endif

:available_quantity 복원/증가;
:cat_stock_history 기록\n(change_type: RESTORE_ORDER_CANCEL /\nRESTORE_RETURN_EXCHANGE / RESTOCK_VENDOR);
:StockChanged 이벤트 발행;

if (상태 == SOLD_OUT AND available_quantity > 0?) then (yes)
  :상태: SOLD_OUT → ON_SALE\n(발생원인 무관, MD 확인 불필요 — 대안A);
  :cat_restock_subscription PENDING 건 조회\n(SKU당 1건);
  :PENDING → NOTIFIED 전환;
  :재입고 알림 일괄 발송;
  note right: 찜 데이터는 품절 시점에\n이미 삭제됐으므로 복원 안 함
else (no)
endif
stop

@enduml
```

---

## 4. 출시일 노출 게이트 프로세스 (C안)

> `release_date`는 상품 상태를 바꾸지 않는다 — 조회 쿼리 시점에 `now`와 비교해 필터링만
> 한다(DBA §2.4 C안, REQ-CAT-033~034). 별도 배치나 이벤트가 없다는 점이 핵심이라, 이
> 프로세스는 "조회 시점 판정"이라는 하나의 결정 지점만 가진다. **상세 페이지 직접 접근
> (딥링크)도 동일 필터를 적용한다**(DBA §2.4에서 확정, 아래 다이어그램에 반영).

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title 출시일 노출 게이트 비즈니스 프로세스 (C안)

|고객|
start
:상품 목록·검색·전시 조회\n또는 상세 페이지 직접 접근(딥링크);

|시스템(Catalog)|
:ON_SALE 상품 집합 조회;

if (release_date IS NULL?) then (yes)
  :노출 대상에 포함\n(하위호환: 즉시 노출);
else (release_date 설정됨)
  if (release_date > now?) then (yes)
    :노출 대상에서 제외\n(목록·검색·전시·상세 딥링크 공통);
  else (no, 도달함)
    :노출 대상에 포함;
  endif
endif

:필터링된 결과 반환;
stop

note right
  별도 배치·이벤트 불필요.
  release_date 도달 즉시
  다음 조회부터 자동 반영됨.
  상세 페이지 딥링크 차단은
  2026-11-04 확정(DBA §2.4).
end note

@enduml
```

---

## 5. 전시페이지 게시 프로세스

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title 전시페이지 게시 비즈니스 프로세스

|관리자(MD) — 운영자|
start
:전시 페이지 생성\n(상태: DRAFT);
:섹션·템플릿 구성\n(콘텐츠유형×전시유형 2축 지정);
:display_start_at / display_end_at\n설정(둘 다 선택, 종료는 시작보다 이후);

if (display_start_at이 NULL이거나\n이미 지난 시각?) then (yes, 즉시 게시)
  :즉시 게시 실행;
  :상태: PUBLISHED;
  :published_at 기록;
else (no, 미래 시각)
  |시스템(배치)|
  :display_start_at 도달 감지;
  :상태: DRAFT → PUBLISHED;
  :published_at 기록;
endif

|관리자(MD) — 운영자|
fork
  :게시 중 운영;
fork again
  if (수정 필요?) then (yes)
    :PUBLISHED 상태에서\n섹션·일시 직접 수정;
    :저장 즉시 반영\n(별도 임시본 없음);
  else (no)
  endif
end fork

if (display_end_at 도달\n또는 관리자 종료 처리?) then (yes)
  :상태: PUBLISHED → CLOSED;
  :closed_at 기록;
  stop
else (no)
  stop
endif

@enduml
```

---

## 6. 홈 화면 지정 프로세스

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title 홈 화면 지정 비즈니스 프로세스

|관리자(MD) — 운영자|
start
:전시 페이지 목록에서 PUBLISHED 페이지 선택;
:"홈으로 설정" 클릭;

|시스템|
if (상태 == PUBLISHED?) then (아니오)
  :"게시된 페이지만 홈으로 지정할 수 있습니다" 안내;
  stop
else (예)
  :기존 is_home=TRUE 페이지 조회;
  if (기존 홈 존재?) then (예)
    :기존 페이지 is_home=FALSE로 해제;
  else (아니오)
  endif
  :선택 페이지 is_home=TRUE로 설정;
  stop
endif
@enduml
```

---

## 7. 이벤트 배너 동기화 프로세스

> **전제**: 이 프로세스는 Promotion이 기획전 등록·수정·취소 시 이벤트를 발행한다는 가정
> 위에 있다. 실제 발행 여부는 **[Human Review]** — DBA §6 Human Review #11~12 참조.

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title 이벤트 배너 동기화 비즈니스 프로세스

|시스템(Promotion)|
start
:기획전 등록·수정 (배너·기간 변경 등);
:PROMOTION_EXHIBITION_BANNER_SYNCED 이벤트 발행;

|시스템(Catalog)|
:이벤트 수신, 멱등 검증(eventId);
if (이미 처리됨?) then (예)
  :무시;
  stop
else (아니오)
  :cat_event_banner_schedule에\n이벤트 key로 upsert\n(start_at~end_at 포함, 사전 등록 가능);
  stop
endif

|관리자(MD) — 운영자|
:홈 전시 페이지의 EVENT_LIST 섹션에\n해당 이벤트 key 배치;

|고객|
:홈 화면 조회;

|시스템(Catalog)|
:조회 시점(now)에 유효한\ncat_event_banner_schedule 행 판정\n(start_at<=now<end_at);
:유효 배너 있으면 노출, 없으면 해당 항목 미노출;
stop
@enduml
```

---

## 8. 재고 품절 임박 알림 발송 프로세스 (2026-11-06 신설)

> 재입고 알림(3절)과 반대 방향 — 품절 **전** 내부 운영자(판매자·관리자)에게 보내는 예방용
> 알림이다(DBA §1.10).

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title 재고 품절 임박 알림 발송 비즈니스 프로세스

|시스템(Catalog)|
start
:SKU 재고 차감 처리(2절)\n또는 수동 재고 변경;
:상품의 restock_alert_threshold와\n각 SKU available_quantity 비교;

if (하나라도 기준수량 이하?) then (yes)
  if (이미 임박 상태로 발송됨?) then (예, 중복)
    :재발송하지 않음;
    stop
  else (아니오, 신규 진입)
    if (등록 경로?) then (입점형)
      :판매자에게 알림 발송\n(Notification 연계);
    else (직매입)
      :공통 관리자 계정체계의\n관리자(MD/MD-OPERATOR)에게 발송;
    endif
    :임박 상태 기록;
    stop
  endif
else (no, 기준수량 초과)
  if (이전에 임박 상태였음?) then (예, 회복)
    :임박 상태 해제\n(다음에 다시 기준 이하로 떨어지면 재발송);
  else (아니오)
  endif
  stop
endif
@enduml
```

---

## 9. 찜 데이터 자동 삭제 프로세스 (2026-11-06 신설)

> 찜하기(DBA §1.14)는 상품 노출 상태와 강하게 결합돼 있어, 상품 상태 전이(1절·2절·3절)의
> 부수효과로 트리거된다 — 별도의 독립된 업무 프로세스가 아니라 "상태 전이에 매달린 액션"
> 이라는 점을 명시하기 위해 별도 절로 뽑아둔다.

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title 찜 데이터 자동 삭제 비즈니스 프로세스

|시스템(Catalog)|
start
:상품 상태 전이 발생;

if (전이 결과 상태?) then (SOLD_OUT 또는 DISCONTINUED)
  :해당 product_id의\ncat_product_wishlist 행 전체 조회;
  if (찜 데이터 존재?) then (yes)
    :전체 물리 삭제;
  else (no)
  endif
  stop
else (그 외 상태)
  :처리 없음 (찜 데이터 유지);
  stop
endif
@enduml
```

---

## 10. 전시여부 플래그 긴급 회수·복원 프로세스 (2026-11-06 신설)

> §2.10 "긴급 게시·회수" — 전시 페이지 상태 전이(5절)와 독립적인 축이다. 상태를 전혀
> 건드리지 않고 노출 쿼리 필터만 토글한다는 점이 5절과의 핵심 차이다.

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title 전시여부 플래그 긴급 회수·복원 비즈니스 프로세스

|관리자(MD) — 운영자|
start
:문제 발견 (오표기 배너·부적절 콘텐츠 등);
:전시 페이지의 전시여부(is_exposed)를\nFALSE로 전환;

|시스템(Catalog)|
:상태·예약·is_home 값은 변경하지 않음;
:노출 쿼리에서 즉시 제외;

if (해당 페이지가 is_home=TRUE?) then (yes)
  :"홈 미지정"과 동일하게 처리\n(기본 카테고리 화면으로 대체 노출);
else (no)
endif

|관리자(MD) — 운영자|
:문제 조치 완료 후\n전시여부를 TRUE로 복원;

|시스템(Catalog)|
:노출 쿼리에 즉시 재포함\n(재게시 절차 불필요);
stop
@enduml
```

---

## 근거

> **원칙**: 구조설계 단계 산출물은 AS-IS 정책서를 직접 인용하지 않는다. `DH-상태머신/
> catalog.md`·`DD-EARS기능요구/catalog.md`가 1차 근거이며, `DBA-도메인정책서/catalog.md`로
> 정책 맥락을 보강한다.

| 항목 | 출처 |
|---|---|
| 상태 전이 | `deliverables/S2-구조설계/DH-상태머신/catalog.md` |
| 직매입/입점형 분기 흐름, 복제·대량등록 | DD REQ-CAT-001~007·056~057, DBA §1.5.1~§1.5.3 |
| 심사 반려·재제출·에스컬레이션 | DD REQ-CAT-006~009, DBA §1.6 |
| 재고 선점·판매량 집계 | DD REQ-CAT-020·023, DBA §1.10·§2.6 |
| 재고 복원·자동전환(대안A) | DD REQ-CAT-021~022·024~025, DBA §1.10 |
| 재고 품절임박 알림 | DD REQ-CAT-058~059, DBA §1.10(2026-11-06 신설) |
| 출시일 노출 게이트(C안, 딥링크 포함) | DD REQ-CAT-033~034, DBA §2.4 |
| 재입고 알림 | DD REQ-CAT-032 |
| 찜 데이터 자동 삭제 | DD REQ-CAT-062, DBA §1.14(2026-11-06 신설) |
| 전시 예약 게시 | DD REQ-CAT-038~043, DBA §2.7.1·§2.10 |
| 홈 화면 지정 | DD REQ-CAT-052, DBA §2.7.2 |
| 전시여부 플래그 긴급 회수·복원 | DD REQ-CAT-068, DBA §2.10(2026-11-06 신설) |
| 이벤트 배너 동기화 | DD REQ-CAT-054~055, DBA §2.8.2 — **[Human Review] Promotion 실제 이벤트 발행 여부 미확인** |
