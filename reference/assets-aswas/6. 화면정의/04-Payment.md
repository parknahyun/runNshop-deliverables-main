# 화면정의서 — Payment (결제) 도메인

> **작성 목적**: `runNshop_screen_definition_v1_1.md`에서 v1.0→v1.1 전환 시 삭제된 와이어프레임을 보완한다. `화면정의서_작성_표준안.md` 방식(메타정보+영역·속성·기능·UI상태)을 따르되 와이어프레임(ASCII)과 상세디스크립션을 한 파일에 통합했다.
> **소스 대조 원칙**: 구현이 있는 화면은 소스를 근거로, 없는 화면은 B2C 커머스 일반기능 수준으로 작성(문서 내 표기).
> **작성일**: 2026-08-26

---

## 이 문서의 특이사항 — Payment 도메인은 별도 화면 ID가 거의 없다

`runNshop_screen_definition_v1_1.md`·`DB-도메인정의서.md`를 대조한 결과, **Payment는 독립된 화면 목록을 갖지 않는 도메인**이다. 결제 관련 UI는 다른 도메인 화면 안에 컴포넌트/탭으로 흡수되어 있다:

| 위치 | 소속 화면 | Payment 관련 요소 |
|---|---|---|
| mobile | CUS-041(주문서, `01-Order.md`) | `PaymentMethod` 컴포넌트 — 결제수단 선택 |
| mobile | CUS-041(주문서) | `OrderBottomBar` — [결제하기] 버튼, `POST /api/v1/payments` 호출 지점 |
| mobile | CUS-042(주문 접수 완료, `01-Order.md`) | 결제 완료 후 결과 화면 |
| admin | ADM-040-001 상세(주문상세, `01-Order.md`) | `PaymentInfoTab` — 결제수단·PG사·거래ID·결제일시 조회 |
| admin | (없음) | **별도 "결제 관리" 화면 자체가 존재하지 않는다** — `apps/runNshop-admin/src/`에 `payment/` 폴더 없음, `navMenus.ts`에도 결제 전용 메뉴 없음 |
| partner | (없음) | Payment 도메인 화면 없음(정산은 Settlement 도메인, `06-Settlement.md`) |

이 문서는 위 화면들에서 **아직 다루지 않은 Payment 고유 관점**(결제수단 선택 UI 상세, 결제 실행 흐름, 결제정보 조회 상세, 공통코드로서의 결제수단 관리)만 보완한다. 화면 전체 와이어프레임 중복을 피하기 위해, CUS-041·042·ADM-040-001 상세의 전체 구조는 `01-Order.md`를 참조한다.

---

## 목차

| 항목 | 화면ID(있는 경우) | 채널 | 소스 상태 |
|---|---|---|---|
| 결제수단 선택 (PaymentMethod) | CUS-041 하위 영역 | mobile | 소스 있음 |
| 결제하기 실행 (OrderBottomBar) | CUS-041 하위 영역 | mobile | 소스 있음(미구현 확인) |
| 결제정보 조회 (PaymentInfoTab) | ADM-040-001 상세 하위 탭 | admin | 소스 있음 |
| 결제수단 공통코드 관리 | ADM-090-004(공통코드 관리) 하위 항목 | admin | 소스 있음(간접) |
| 환불 처리 | ADM-040-002(클레임 상세) 하위 기능 | admin | `01-Order.md` 참조(환불 로직은 클레임 처리에 흡수) |

---

## 결제수단 선택 — CUS-041 하위 영역 (mobile, PaymentMethod)

### 메타정보

> **소속 화면**: CUS-041 주문서 (`01-Order.md` R6 PaymentMethod와 동일 영역, 이 문서에서 상세 보완)
> **소스**: `apps/runNshop-mobile/components/order/PaymentMethod.tsx`
> **문서상태**: DRAFT-v1.0

### 와이어프레임

```
┌─────────────────────────────┐
│ 결제 수단 [R1]                 │
├─────────────────────────────┤
│ [카드] [계좌이체] [간편결제][F1]│ ← R1 버튼 그룹(선택형)
└─────────────────────────────┘
```

### 상세디스크립션

| 코드 | 이름 | 구분 |
|---|---|---|
| R1 | 결제수단 버튼 그룹 | 영역 |
| R1-P1 | 결제수단 목록(type/label) | 속성 |
| R1-F1 | 결제수단 선택 | 기능 |

| 항목 | 내용 |
|---|---|
| 데이터 소스 | `sheet.payment_methods[]`(주문서 API 응답의 일부, `01-Order.md` 참조) |
| UI 동작 | 클릭 시 선택된 버튼만 강조색(테두리+텍스트 primary색), 나머지는 회색 — 로컬 state(`selected`)로만 관리, 선택값이 실제 결제 요청(`POST /api/v1/payments`)에 반영되는지는 `OrderBottomBar`가 이 state를 참조하지 않아 **연동 안 됨**(아래 Human Review) |

> **결제수단의 실제 값(공통코드)**: `apps/runNshop-admin/src/system/common-code/mockData.ts`에 `PAYMENT_METHOD-001~005`(신용카드/계좌이체/가상계좌/간편결제/무통장입금) 공통코드가 정의되어 있다. 이 화면의 `payment_methods[]`가 이 공통코드 목록과 같은 소스를 공유해야 한다(ADM-090-004, 아래 참조).

---

## 결제하기 실행 — CUS-041 하위 영역 (mobile, OrderBottomBar)

### 메타정보

> **소속 화면**: CUS-041 주문서 (`01-Order.md` R9 BottomBar와 동일 영역)
> **소스**: `apps/runNshop-mobile/components/order/OrderBottomBar.tsx`
> **문서상태**: DRAFT-v1.0

### 와이어프레임

```
┌─────────────────────────────┐
│  xxx,xxx원 결제하기 [F1]       │
└─────────────────────────────┘
```

### 상세디스크립션

| 코드 | 기능명 | 트리거 | 동작 | 검증/제약사항 |
|---|---|---|---|---|
| F1 | 결제하기 | 클릭 | 소스상 `alert('프로토타입에서는 지원하지 않는 기능입니다.')` — 실제 `POST /api/v1/payments`(원본 화면정의서 §2.7 API #39) 미연동 | 활성 조건: 배송지+결제수단+약관동의+휴대폰인증(원본 §2.5 CUS-041 명시, `01-Order.md`에도 기록) — 소스에는 이 활성/비활성 조건 자체가 구현되어 있지 않음(버튼이 항상 클릭 가능) |

> **Human Review**: 결제수단 선택(`PaymentMethod`)과 결제 실행(`OrderBottomBar`)이 서로 다른 컴포넌트로 분리되어 있고, `OrderBottomBar`는 선택된 결제수단 값을 props로 받지 않는다. 실제 구현 시 이 두 컴포넌트 간 state 연결(선택된 결제수단을 결제 요청 payload에 포함)이 필요하다.

---

## 결제정보 조회 — ADM-040-001 상세 하위 탭 (admin, PaymentInfoTab)

### 메타정보

> **소속 화면**: ADM-040-001 주문 상세 (`01-Order.md`의 "결제정보" 탭과 동일 영역)
> **소스**: `apps/runNshop-admin/src/order/order-history/tabs/PaymentInfoTab.tsx`
> **문서상태**: DRAFT-v1.0

### 와이어프레임

```
┌──────────────────────────────────────┐
│ 상품 합계        xxx,xxx원 [P1]        │ ← R1 금액 정보
│ 할인 금액       −xx,xxx원 [P2]         │
│ 배송비          무료/x,xxx원 [P3]      │
│ 실결제금액       xxx,xxx원 [P4]         │
├──────────────────────────────────────┤
│ 결제수단        신용카드 [P5]           │ ← R2 결제 상세 정보
│ PG사           토스페이먼츠 [P6]        │
│ 거래 ID        TXN-XXXXXXX [P7]        │
│ 결제 일시       2026.06.26 [P8]         │
└──────────────────────────────────────┘
```

### 상세디스크립션

| 코드 | 이름 | 구분 |
|---|---|---|
| R1 | 금액 정보 | 영역 |
| R1-P1~4 | 상품합계/할인/배송비/실결제금액 | 속성 |
| R2 | 결제 상세 정보 | 영역 |
| R2-P5~8 | 결제수단/PG사/거래ID/결제일시 | 속성 |

| 항목 | 내용 |
|---|---|
| 데이터 소스(현재 소스 기준) | **하드코딩**: 할인 15%(`order.amount * 0.15`), 배송비는 5만원 기준 무료/3천원, 결제수단은 "신용카드" 고정, PG사는 "토스페이먼츠" 고정, 거래ID는 주문번호 뒷자리로 생성한 가짜 값 |
| 실제 필요 데이터 소스(추정) | `GET /api/admin/v1/orders/{platform_order_no}`(원본 §3.5 #98) 응답에 결제 상세 필드가 포함되어야 함 — 현재는 `Order` 목 데이터에 결제 필드 자체가 없어 컴포넌트 내부에서 임의 계산 |

> **Human Review**: 이 탭의 모든 값이 실제 결제 데이터가 아니라 `order.amount`를 기반으로 역산한 하드코딩 값이다. 실제 결제 도메인 데이터(승인번호, 카드사, 할부여부 등)를 담을 필드가 `Order` 모델에 없다 — 본 구현 시 Payment 도메인의 실제 엔티티(결제·환불)를 참조하도록 재설계가 필요하다(원본 `D9-컴포넌트.md`의 도메인 간 통신 원칙상 Order가 Payment 데이터를 직접 갖지 않고 조회 API로 가져와야 함).

---

## 결제수단 공통코드 관리 — ADM-090-004 하위 항목 (admin, CommonCodes)

### 메타정보

> **소속 화면**: ADM-090-004 공통코드 관리(`11-Platform.md`에서 화면 전체를 다룸, 이 문서에서는 결제수단 그룹만 발췌)
> **소스**: `apps/runNshop-admin/src/system/common-code/mockData.ts`
> **문서상태**: DRAFT-v1.0 (참조 발췌)

### 상세디스크립션

| codeId | codeName | codeValue | codeStatus |
|---|---|---|---|
| PAYMENT_METHOD-001 | 신용카드 | CREDIT_CARD | ACTIVE |
| PAYMENT_METHOD-002 | 계좌이체 | BANK_TRANSFER | ACTIVE |
| PAYMENT_METHOD-003 | 가상계좌 | VIRTUAL_ACCOUNT | ACTIVE |
| PAYMENT_METHOD-004 | 간편결제 | EASY_PAY | ACTIVE |
| PAYMENT_METHOD-005 | 무통장입금 | CASH | **SUSPENDED**(사용중지) |

> 결제수단 코드 그룹은 공통코드 관리 화면(ADM-090-004)에서 관리되며, 이 값이 CUS-041의 `payment_methods[]`(위 "결제수단 선택" 섹션)와 mobile의 `PaymentMethod.tsx` 렌더링 대상이 되어야 한다. 현재 CUS-041 소스는 이 공통코드를 직접 참조하지 않고 `orders/sheet` API 응답에 이미 포함된 값을 그대로 쓴다 — 두 소스가 일치하는지는 백엔드 구현 시 확인 필요(Human Review). SUSPENDED 상태인 "무통장입금"이 실제로 CUS-041에서 숨겨지는지도 확인 필요.

---

## 환불 처리 — ADM-040-002 하위 기능 (admin)

> Payment 도메인의 "환불"은 별도 화면이 아니라 클레임 처리(ADM-040-002 클레임 상세)의 상태 전이 과정에서 발생한다. 전체 구조는 `01-Order.md`의 "ADM-040-002 상세 — 클레임 상세" 섹션을 참조. 이 문서에서는 Payment 관점의 연계만 기록한다.

| 항목 | 내용 |
|---|---|
| 환불 예정 금액 계산 | mobile CUS-054(반품 신청)에서 `POST /api/v1/orders/{order_no}/refund-estimate`(원본 §2.7 API #51) 호출 — `01-Order.md` CUS-053~055 참조 |
| 환불 실행 | admin ClaimDetail의 [완료 처리](`01-Order.md` R4-F3)에서 `completedAt` 기록과 함께 발생하는 것으로 추정되나, 실제 PG 환불 API 호출은 소스에 없음(전부 `alert()` 처리) |
| 환불 실패 시나리오 | `D8-NFR.md`·원본 정책 어디에도 "환불 실패" 처리 흐름이 명시되어 있지 않음 |

> **Human Review**: 원본 화면정의서 §2.7 API #50 "반품 배송비 결제"(`POST /api/v1/claims/{claim_no}/extra-payment`)는 반품 시 **추가 결제**가 발생하는 경우인데, 이 역시 Payment 도메인 관점에서 별도 화면 없이 클레임 처리 흐름에 흡수되어 있다. 고객 변심 반품 시 배송비를 실제로 어떻게 결제받는지(기존 결제수단 재사용? 별도 결제창?) 화면 설계가 없다.

---

## 종합 Human Review 목록

| # | 항목 | 사유 |
|---|---|---|
| 1 | 결제수단 선택 ↔ 결제 실행 미연동 | `PaymentMethod`(선택)와 `OrderBottomBar`(실행)가 state를 공유하지 않음 |
| 2 | 결제하기 버튼 활성 조건 미구현 | 원본 정책(배송지+결제수단+약관동의+휴대폰인증)이 실제로는 검증되지 않음 |
| 3 | ADM PaymentInfoTab 전체 하드코딩 | 실제 결제 데이터 모델이 없어 주문 금액에서 역산한 가짜 값만 표시 |
| 4 | 결제수단 공통코드-주문서 API 값 일치 여부 | 두 소스가 같은 데이터를 참조하는지 백엔드 구현 시 확인 필요 |
| 5 | SUSPENDED 결제수단 노출 여부 | "무통장입금"이 CUS-041에서 실제로 숨겨지는지 미확인 |
| 6 | 환불 실행·실패 시나리오 부재 | 클레임 완료 처리와 실제 PG 환불 API 연동 지점이 설계에 없음 |
| 7 | 반품 배송비 추가결제 화면 부재 | 어떤 결제수단으로 추가 결제받는지 UI 설계 없음 |

---

## 변경 이력

| 버전 | 날짜 | 내용 |
|---|---|---|
| v1.0 | 2026-08-26 | 초판 — `docs_archive` 문서 수정 규칙 예외 적용. Payment 도메인은 독립 화면이 없어(원본 화면정의서·도메인정의서 대조로 확인) 다른 도메인 화면(CUS-041/042, ADM-040-001 상세, ADM-090-004, ADM-040-002)에 흡수된 Payment 관점 요소를 발췌·보완하는 문서로 구성. 소스 대조 5건, Human Review 7건 |
