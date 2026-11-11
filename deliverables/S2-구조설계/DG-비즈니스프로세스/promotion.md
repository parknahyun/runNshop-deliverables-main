# 비즈니스 프로세스 — Promotion

> **단계**: 구조설계
> **문서범위**: Domain
> **문서종류**: Design
>
> **작성 목적**: 상태머신(⑩)의 전이를 액티비티 흐름으로 확장하여, "누가 어떤 순서로 업무를 수행하는가"를 시각화한다.
> **흐름 내 위치**: ⑩ 상태머신 → **⑪ 비즈니스 프로세스** → ⑫ 이벤트 플로우
> **작성 주체**: 시니어 개발자 + AI 협업 (기획자·현업 검토·확인)

| 항목 | 내용 |
|---|---|
| ID | DESIGN-BP-PROMOTION-001 |
| 상태 | **Draft** |
| 작성일 | 2026-07-08 |
| 갱신일 | 2026-07-08 |

---

## 1. 할인 적용 계산 프로세스 (Order 연동)

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title 할인 적용 계산 프로세스 (PublicApi)

|시스템(Order)|
start
:할인 계산 요청\n(productId, skuId, qty);

|시스템(Promotion)|
:상품별 ACTIVE 행사 조회;

if (행사가 ACTIVE?) then (yes)
  :할인 유형 = DISCOUNT_EVENT;
  :할인 금액 계산\n(정률 or 정액);
else if (수량구간 할인 ACTIVE?) then (yes)
  :구간별 조건 확인;
  if (qty ≥ min_quantity?) then (yes)
    :할인 유형 = QTY_TIER_DISCOUNT;
    :해당 구간 할인율 적용;
  else (조건 미충족)
    :할인 없음 (0원);
  endif
else (둘 다 없음)
  :할인 없음 (null);
endif

:할인 유형·할인금액·할인 후 단가 반환;
stop

@enduml
```

---

## 2. 쿠폰 등록·승인 프로세스

> ⚠️ **협의 대기**: 아래 직매입/입점형 분기 프로세스는 판매자(partner) 쿠폰 등록을 전제로 한다. 도메인정의서(DB)에 partner 채널이 추가된 후 확정한다(협의문서: `20260708_도메인정의서 Promotion 채널 보완 제안`). partner 채널 미확정 시 MD 직접 등록(즉시 ACTIVE) 흐름만 유효하다.

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title 쿠폰 등록·승인 비즈니스 프로세스

|시스템(Promotion)|
start
:등록 주체 판별;

if (vendor.is_platform_direct?) then (TRUE: 직매입)
  |관리자(MD)|
  :직매입 쿠폰 정보 입력\n(할인유형, 금액/율, 유효기간, 발급한도, 최소주문);
  :등록 요청;
  
  |시스템(Promotion)|
  :쿠폰 저장 → 즉시 ACTIVE;
  :승인 게이트 생략;
  stop
else (FALSE: 입점형)
  |판매자(벤더)|
  :쿠폰 정보 입력\n(할인유형, 금액/율, 유효기간, 발급한도, 최소주문);
  :등록 요청;
  
  |시스템(Promotion)|
  :쿠폰 저장 (PENDING_APPROVAL);
  
  |관리자(MD)|
  :승인 대기 쿠폰 확인;
  
  if (승인?) then (yes)
    |시스템(Promotion)|
    :ACTIVE 전환;
    :발급 가능 상태;
    stop
  else (반려)
    |시스템(Promotion)|
    :REJECTED 전환;
    :반려 사유 기록;
    :판매자에게 통보;
    stop
  endif
endif

@enduml
```

---

## 3. 쿠폰 발급·사용 프로세스

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title 쿠폰 발급·사용 프로세스

|고객|
start
:쿠폰 다운로드 요청;

|시스템(Promotion)|
:쿠폰 상태 확인;

if (ACTIVE && issued_count < issue_limit?) then (yes)
  :prm_coupon_issue 생성 (AVAILABLE);
  :issued_count 증가;
  :발급 완료 응답;
else (발급 불가)
  :한도 초과 / 비활성 안내;
  stop
endif

|고객|
:주문 시 쿠폰 적용 요청;

|시스템(Order → Promotion PublicApi)|
:쿠폰 유효성 검증;

if (유효?) then (yes)
  :할인 금액 계산·반환;
  note right
    사용 가능 판정 (모두 AND):
    ① status = AVAILABLE (미사용)
    ② now <= valid_to (유효기간 내)  ← 상태 아닌 날짜로 판정
    ③ 최소 상품금액 충족 (할인 후 상품금액 기준)
    ④ 적용상품 일치
    ※ 상태 단독 판정 금지 — 만료는 날짜로 차단
    (만료 배치 지연 구간 오판 방지, §6 참조)
  end note
else (무효)
  :사용 불가 사유 반환;
  stop
endif

|시스템(Promotion)|
:결제 완료 시 USED 전환;
:used_order_id, used_at 기록;
stop

@enduml
```

---

## 4. 행사가 등록·종료 프로세스

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title 행사가 등록·종료 프로세스

|관리자(MD)|
start
:행사가 정보 입력\n(대상상품, 할인율/금액, 기간[필수],\n종료방식: 기간형/선착순형[+제한수량]);
:등록·확정 요청\n(start_at 1영업일 전까지 — 정책서 §3.7);

|시스템(Promotion)|
:택1 규칙 검증\n(상품당 가격할인 1건);

if (동일 상품에 SCHEDULED/ACTIVE 가격할인 존재?) then (yes)
  :등록 거부\n(택1 규칙 위반 — 행사가·수량할인 통합);
  stop
else if (start_at < now+1영업일?) then (yes)
  :등록 거부\n(등록 마감 위반 — 정책서 §3.7);
  stop
else (통과)
  :DRAFT → SCHEDULED 전환\n(예약 등록, 가격 미반영);
  if (선착순형?) then (yes)
    :Redis remaining_quantity 셋업;
  else (기간형)
  endif
endif

... start_at 대기 ...

|시스템(배치/Consumer)|
:start_at 도래 감지;
:SCHEDULED → ACTIVE 전환 (자동);
:대상 상품 할인가 반영;
:DISPLAY_PRICE_CHANGED 이벤트 발행;

... 행사 기간 경과 ...

if (end_at 도래?) then (기간 만료, 공통)
  :ACTIVE → ENDED;
  :가격 자동 복원;
  :EVENT_ENDED 이벤트 발행;
  stop
else if (선착순형 AND remaining_quantity = 0?) then (선착순 수량 소진)
  :ACTIVE → ENDED;
  :가격 자동 복원;
  :EVENT_ENDED 이벤트 발행;
  stop
endif

@enduml
```

---

## 5. 장바구니 할인 평가 프로세스

> **⚠️ 비교 기준 금액**: 장바구니 할인 조건(`condition_amount`)은 **정가 총액이 아니라 상품 단위 할인(① 행사가/수량구간 + ② 상품쿠폰) 적용 후의 주문 총액**을 기준으로 판단한다. "상품 먼저, 플랫폼 나중" 원칙에 따라 Order가 상품 할인을 먼저 확정한 뒤 그 금액을 Promotion에 전달한다. (근거: `참고자료/프로모션-할인유형-적용순서.md` §4 — 확정)

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title 장바구니 할인 평가 프로세스

|시스템(Order)|
start
:상품 단위 할인(①행사가/수량구간 + ②상품쿠폰) 확정;
:장바구니 할인 평가 요청\n(상품할인 적용 후 주문 총액, 상품 목록);

|시스템(Promotion)|
:ACTIVE 장바구니 할인 정책 조회;

if (ACTIVE 정책 존재?) then (yes)
  if (상품할인 적용 후 총액 >= condition_amount?) then (충족)
    :할인금액·조건명 반환;
  else (미충족)
    :할인 0원, 미충족 반환;
  endif
else (정책 없음)
  :할인 0원, 정책 없음 반환;
endif

stop

@enduml
```

---

## 6. 쿠폰 만료 배치 프로세스

> **⚠️ 이 배치는 "사용 가능 판정"의 전제가 아니다.** 쿠폰 사용 가능 여부는 항상 `status + 유효기간` 조합으로 판정하며(§3 참조), **유효기간이 진실의 원천(SoT)**이다. 본 배치의 EXPIRED 전환은 판정용이 아니라 **조회 성능(status 인덱스)·통계(미사용 소멸 집계)·만료 알림** 목적의 캐시 갱신이다.
> 따라서 배치 실행 전(예: 자정~02:00) 만료된 쿠폰이 아직 `status=ACTIVE/AVAILABLE`로 남아 있어도, 사용 검증(§3)은 `now ≤ valid_to` 조건으로 이를 차단하므로 정합성이 깨지지 않는다.

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title 쿠폰 만료 배치 프로세스 (캐시 갱신 — 판정 전제 아님)

|시스템(배치)|
start
:매일 02:00 배치 실행;
:유효기간 만료 쿠폰 조회\n(prm_coupon.valid_to < now AND status = ACTIVE);
:대상 쿠폰 → EXPIRED 일괄 전환\n(조회/통계/알림용 캐시 갱신);
:해당 쿠폰의 미사용 발급 건\n(prm_coupon_issue.status = AVAILABLE)\n→ EXPIRED 일괄 전환;
note right
  ※ 사용 가능 판정은 이 배치와 무관하게
  status + (now <= valid_to) 조합으로 수행 (§3)
  배치 지연 구간에도 만료 쿠폰은 날짜 조건으로 차단됨
end note
stop

@enduml
```

---

## 7. 노출 할인가 사전 계산·갱신 프로세스

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title 노출 할인가 사전 계산 프로세스 (상품 목록용)

|시스템(Promotion)|
start
:행사 상태 변경 감지\n(ACTIVE 전환 / ENDED 전환 / 수량 소진);

if (ACTIVE 전환?) then (행사 시작)
  :대상 상품 목록 조회\n(prm_discount_event_product);
  :상품별 노출 할인가 계산\n(discount_type·discount_value 적용);
  :DISPLAY_PRICE_CHANGED 이벤트 발행\n(productId, displaySalePrice, discountRate, eventId);
else (ENDED 전환)
  :대상 상품 목록 조회;
  :원래 판매가(price_sale)로 복원;
  :DISPLAY_PRICE_CHANGED 이벤트 발행\n(productId, displaySalePrice=price_sale, discountRate=0, eventId=null);
endif

|시스템(Catalog)|
:이벤트 수신;
:cat_product.display_sale_price 갱신;
:cat_product.display_discount_rate 갱신;
:cat_product.active_event_id 갱신;
:Search 동기화 이벤트 발행\n(ProductUpdated);
stop

@enduml
```

---

## 8. 상품 상세 실시간 할인가 계산 프로세스

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam defaultFontSize 11
title 상품 상세 실시간 할인가 계산 (PublicApi)

|시스템(Catalog/BFF)|
start
:고객 상품 상세 진입\n(productId, memberId);
:Promotion PublicApi 호출\n(실시간 할인가 계산 요청);

|시스템(Promotion)|
:해당 상품 ACTIVE 행사 조회;

if (행사가 존재?) then (yes)
  :행사 할인가 계산\n(즉시할인 또는 수량구간);
else (no)
  :할인 없음 (원래 판매가);
endif

if (memberId 존재? - 로그인) then (yes)
  :해당 회원 적용 가능 쿠폰 조회\n(상품쿠폰 + 장바구니쿠폰);
  :쿠폰 적용 시 예상 최저가 계산;
else (비로그인)
  :쿠폰 정보 미제공;
endif

:응답 반환\n· 정가 (price_original)\n· 행사가 (event_price)\n· 할인율 (discount_rate)\n· 적용 가능 쿠폰 목록\n· 예상 최저가 (쿠폰 최대 적용 시);

|시스템(Catalog/BFF)|
:고객 화면 표시\n정가(취소선) / 행사가 / 쿠폰 추가할인 안내;
stop

@enduml
```

---

## 근거

| 항목 | 출처 |
|---|---|
| 상태 전이 | `DH-상태머신(Promotion).md` |
| PublicApi 흐름 | `DC-상위유스케이스(Promotion).md` 행사가·할인관리 업무그룹 |
| 택1 규칙 | REQ-PRM-007, REQ-PRM-021 |
| 쿠폰 검증 로직 | REQ-PRM-003, REQ-PRM-004 |
| 장바구니 할인 | REQ-PRM-002, REQ-PRM-030~032 |
| 배치 스케줄 | REQ-PRM-011, REQ-PRM-047 |
| 할인 적용 순서 | `프로모션-할인유형-적용순서.md` §3(순서)·§4(중복·방향 규칙) |
| 장바구니 할인 비교 기준 금액 (상품할인 후 총액) | `프로모션-할인유형-적용순서.md` §4, REQ-PRM-002 |
| 쿠폰 만료 판정 (status+기간 조합, 상태 단독 금지) | 상태머신 §3 판정식, REQ-PRM-004 |
