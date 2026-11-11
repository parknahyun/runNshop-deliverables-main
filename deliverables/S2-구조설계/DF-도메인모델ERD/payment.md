# 도메인 모델 (ERD) — Payment

> **단계**: 구조설계
> **문서범위**: Domain
> **문서종류**: Design
>
> **작성 목적**: EARS(DD)에서 도출된 엔티티·속성·관계를 테이블 설계로 구체화한다.
> **흐름 내 위치**: DD EARS → **DF 도메인 모델(ERD)** → DG 비즈니스 프로세스
> **작성 주체**: 시니어 개발자 + AI 협업 (DBA/아키텍트 검토)

| 항목 | 내용 |
|---|---|
| ID | DESIGN-ERD-PAYMENT-001 |
| 상태 | **Finalized** |
| 작성일 | 2026-08-11 |
| 갱신일 | 2026-10-29 |

---

## ERD 다이어그램 (PlantUML)

```plantuml
@startuml
skinparam backgroundColor transparent
skinparam linetype ortho
skinparam classAttributeIconSize 0
skinparam classFontSize 11
skinparam classAttributeFontSize 10

title Payment 도메인 — ERD

' ===== Payment =====
entity "pay_payment" as payment {
  * id : varchar <<PK, ULID>>
  --
  * payment_no : varchar [YyMMdd-NNNNN-NN, 2026-10-27]
  * order_id : varchar <<FK ord_order>>
  * platform_order_id : varchar
  * pay_group_no : int [1, 결제 시도 번호]
  * member_id : varchar <<FK Member>>
  * pg_provider : varchar [TOSS]
    pg_token : varchar
  * payment_method : varchar [CARD/VIRTUAL_ACCOUNT/EASY_PAY/POINT — 결제수단별 1행.]
  * amount : int [해당 수단 금액]
  * status : varchar [PENDING/WAITING_DEPOSIT/CONFIRMING/PAID/CANCELLED/REFUNDED/PARTIAL_REFUNDED]
    virtual_account_no : varchar [VIRTUAL_ACCOUNT만]
    virtual_account_bank : varchar [VIRTUAL_ACCOUNT만]
    deposit_due_at : timestamp [입금 기한, 발급 후 12시간]
    refund_bank_name : varchar [VIRTUAL_ACCOUNT만]
    refund_account_no : varchar [암호화 저장]
    refund_holder_name : varchar [주문자 본인]
    refund_reason : varchar [LATE_DEPOSIT 등]
    refund_base_date : date [자동 환불 기준일]
    approved_at : timestamp
    cancelled_at : timestamp
    refunded_at : timestamp
  * created_at : timestamp
  * updated_at : timestamp
}

' ===== Payment Log =====
entity "pay_payment_log" as plog {
  * id : varchar <<PK, ULID>>
  --
  * payment_id : varchar <<FK>>
  * event_type : varchar [{EV}]
    pg_transaction_id : varchar
    request_amount : int
    response_code : varchar
    raw_response : text
    reason : varchar
    retry_count : int [0, 자동 재시도 횟수 0~2]
  * created_at : timestamp
}

' ===== Payment Method =====
entity "pay_payment_method" as pmethod {
  * id : varchar <<PK, ULID>>
  --
  * member_id : varchar
  * method_type : varchar [CARD/ACCOUNT/EASY_PAY]
  * pg_billing_key : varchar
  * display_name : varchar [****-1234]
    card_company : varchar
    is_default : boolean [false]
  * created_at : timestamp
  * updated_at : timestamp
    is_deleted : boolean [false]
}

' ===== Card Restriction =====
entity "pay_card_restriction" as crestr {
  * id : varchar <<PK, ULID>>
  --
  * card_hash : varchar
  * restricted_date : date
  * fail_count : int [3]
    released_at : timestamp
  * created_at : timestamp
  ..
  <<UQ>> card_hash + restricted_date
}

' ===== Card Fail Counter (신규 v2 — REQ-PAY-023) =====
entity "pay_card_fail_counter" as cfcnt {
  * card_hash : varchar <<PK>>
  --
  * consecutive_fail_count : int [0]
  * updated_at : timestamp
}

' ===== Relations =====
payment ||--o{ plog : "1:N\nPG 이력"

' ===== Cross-domain (논리적) =====
note bottom of payment
  order_id → ord_order.id (논리적 FK)
  member_id → Member 도메인
end note

note bottom of pmethod
  member_id → Member 도메인
  카드번호 미저장 (PCI DSS)
end note

@enduml
```

---

## 테이블 구조

```
pay_payment (결제 트랜잭션, 결제수단별 1행 — 1 order : N payment)
  └── pay_payment_log (PG 요청·응답 이력)

pay_payment_method (고객 결제수단)
pay_card_restriction (카드 일일 제한)
pay_card_fail_counter (카드 연속실패 카운터, v2 신설 — REQ-PAY-023)
```

---

## DBML

```dbml
Table pay_payment {
  id varchar [pk, note: 'ULID']
  payment_no varchar [not null, unique, note: 'Y+플랫폼 주문번호 본문(yyMMdd-NNNNN)+주문 내 결제 행 순번(01~99). 예: Y261026-00001-01']
  order_id varchar [not null, note: 'ord_order.id 참조 (논리적 FK)']
  platform_order_id varchar [not null, note: '역추적용. 주문당 여러 행(복합결제·재시도) — UNIQUE 아님']
  pay_group_no int [not null, default: 1, note: '결제 시도 번호 — 한 번의 결제 요청(복합결제 수단별 행들)을 묶음. 고객 재결제 시에만 +1, 자동 재시도(REQ-PAY-003)는 같은 행이라 불변']
  member_id varchar [not null, note: '결제자']
  pg_provider varchar [not null, default: 'TOSS', note: '토스페이먼츠']
  pg_token varchar [note: 'PG 발급 토큰 (카드번호 원본 저장 금지, REQ-PAY-017)']
  virtual_account_no varchar [note: '발급된 가상계좌 번호 (VIRTUAL_ACCOUNT만, 입금대기 취소 시 폐기. 2026-10-29 명시·컬럼명은 제안)']
  virtual_account_bank varchar [note: '가상계좌 은행 (VIRTUAL_ACCOUNT만, 제안)']
  deposit_due_at timestamp [note: '입금 기한 = 발급 후 12시간 (정책서 4.4.1, 제안)']
  refund_bank_name varchar [note: '가상계좌 환불계좌 은행 (VIRTUAL_ACCOUNT만, 2026-10-29 신설·미구현)']
  refund_account_no varchar [note: '가상계좌 환불계좌 번호 — 암호화 저장·마스킹 표시 (신설·미구현)']
  refund_holder_name varchar [note: '가상계좌 환불계좌 예금주 (주문자 본인, 신설·미구현)']
  refund_reason varchar [note: '환불 사유. 입금 통보·취소 경합 자동 환불은 LATE_DEPOSIT (REQ-PAY-030, 제안)']
  refund_base_date date [note: '자동 환불 기준일 = 입금 통보 수신일, 기한 8.1.3 3영업일 (REQ-PAY-030, 제안)']
  payment_method varchar [not null, note: 'CARD / VIRTUAL_ACCOUNT / EASY_PAY / POINT (결제수단별 1행, 복합결제=여러 행).']
  amount int [not null, note: '해당 결제수단의 금액(PG 승인 요청 금액 또는 포인트 사용액)']
  status varchar [not null, note: 'PENDING / WAITING_DEPOSIT(가상계좌 입금대기) / CONFIRMING(결제 확인 중, 2026-10-29 신설·미구현) / PAID / CANCELLED / REFUNDED / PARTIAL_REFUNDED. 구현의 COMPLETED는 PAID와 같은 상태(PAID로 통일)']
  approved_at timestamp
  cancelled_at timestamp
  refunded_at timestamp
  created_at timestamp [not null]
  updated_at timestamp [not null]

  indexes {
    order_id [name: 'idx_payment_order']
    (platform_order_id, pay_group_no) [name: 'idx_payment_order_group']
    member_id [name: 'idx_payment_member']
    (status, created_at) [name: 'idx_payment_status_date']
  }

  note: '결제 트랜잭션(결제수단별 1행). 1 order : N payment — 복합결제는 같은 pay_group_no의 수단별 행들 (REQ-PAY-001~007, 025~027)'
}

Table pay_payment_log {
  id varchar [pk, note: 'ULID']
  payment_id varchar [not null, ref: > pay_payment.id]
  event_type varchar [not null, note: 'REQUEST / APPROVE / FAIL / RETRY / TIMEOUT(3초 무응답·결제 확인 중) / CANCEL / REFUND / PARTIAL_REFUND / REFUND_FAIL(자동 환불 실패) / BANK_TRANSFER(수동 계좌이체 환불) / DEPOSIT(입금 통보). DG 로그 타입과 일치']
  pg_transaction_id varchar [note: 'PG측 거래번호 (멱등 판별)']
  request_amount int [note: '요청 금액']
  response_code varchar [note: 'PG 응답 코드']
  raw_response text [note: 'PG 응답 문자열 자체 (PII 마스킹 후 저장, 2026-10-29 확정). 요청 원문은 저장하지 않음 — 요청은 event_type·request_amount·pg_transaction_id·reason으로만 기록']
  reason varchar [note: '작업 내용(오류 코드 포함, 정책 4.5.4)']
  retry_count int [default: 0, note: '자동 재시도 횟수, 최대 2회(총 3회 시도, REQ-PAY-003). 누적 실패 횟수 자체는 별도 컬럼 없이 같은 행의 FAIL·TIMEOUT(조회 미승인 확정) 로그 건수로 센다 — 누적 실패 3회 도달 시 CANCELLED. 카드 단위 연속 실패(REQ-PAY-023)와는 별개']
  created_at timestamp [not null]

  indexes {
    payment_id [name: 'idx_plog_payment']
    pg_transaction_id [name: 'idx_plog_pg_tx']
  }

  note: 'REQ-PAY-006: 모든 PG 요청·응답 기록 (응답은 문자열 자체, 요청은 원문 없이 구조화 이력)'
}

Table pay_payment_method {
  id varchar [pk, note: 'ULID']
  member_id varchar [not null]
  method_type varchar [not null, note: 'CARD / ACCOUNT / EASY_PAY']
  pg_billing_key varchar [not null, note: 'PG 토큰 (카드번호 미저장, REQ-PAY-017)']
  display_name varchar [not null, note: '마스킹 표시명: ****-1234']
  card_company varchar [note: '카드사명 (CARD 유형만)']
  is_default boolean [default: false]
  created_at timestamp [not null]
  updated_at timestamp [not null]
  is_deleted boolean [default: false]

  indexes {
    member_id [name: 'idx_pmethod_member']
    (member_id, is_default) [name: 'idx_pmethod_default']
  }

  note: 'REQ-PAY-014~016: 고객 등록 결제수단'
}

Table pay_card_restriction {
  id varchar [pk, note: 'ULID']
  card_hash varchar [not null, note: '카드 식별 해시 (원본 미저장)']
  restricted_date date [not null]
  fail_count int [not null, default: 3]
  released_at timestamp [note: '익일 00:00 자동 해제 (REQ-PAY-019)']
  created_at timestamp [not null]

  indexes {
    (card_hash, restricted_date) [unique, name: 'uq_card_date']
  }

  note: 'REQ-PAY-018: 동일 카드 3회 연속 실패 시 당일 제한'
}

Table pay_card_fail_counter {
  card_hash varchar [pk, note: '카드 식별 해시 (원본 미저장)']
  consecutive_fail_count int [not null, default: 0, note: '결제 성공 시 0으로 초기화 (REQ-PAY-023)']
  updated_at timestamp [not null]

  note: 'REQ-PAY-023: 3회 도달 시 pay_card_restriction 레코드 생성 후 이 카운터는 0으로 리셋'
}
```

---

## 불변식 (Invariants)

| 불변식 | 검증 시점 | 도출 근거 |
|---|---|---|
| 같은 `pay_group_no`의 `pay_payment.amount` 합계 == 플랫폼 주문 `payment_amount + point_used_amount` (= 주문금액 `total_order_amount`) | 결제 요청 시 | REQ-PAY-007: 금액 위변조 방지 (복합결제는 수단별 행 합계로 검증) |
| `payment_no`는 플랫폼 주문번호 본문을 포함하고 주문당 행 순번은 99를 넘지 않는다 | 채번 시 | 플랫폼 제약(주문당 결제 행 99건) |
| `pay_payment_log`의 APPROVE 이벤트는 payment당 최대 1건 | 승인 처리 시 | 멱등성 보장 |
| `pay_card_restriction` 동일 card_hash+date는 unique | 제한 생성 시 | 중복 제한 방지 |
| 환불 금액 합계 ≤ 원결제 금액 | 환불 요청 시 | 과잉 환불 방지 |
| 환불금액 = 상품주문금액 + 환불 대상 배송비(전체 취소·판매자 귀책 전체 반품만, 배송비 − 배송비 할인금액). 반품·교환 배송비는 별도 결제분이라 차감하지 않음 | 환불 산정 시 | REQ-PAY-024 (2026-10-29) |
| 부분환불(PARTIAL_REFUNDED) 금액은 배송비를 제외한 상품주문금액 기준 | 부분 환불 요청 시 | REQ-PAY-024 |

---

## Soft Delete 정책

| 테이블 | 정책 | 사유 |
|---|---|---|
| pay_payment | 물리 삭제 없음, 영구 보존 | 결제 데이터 법적 보관 의무 |
| pay_payment_log | 물리 삭제 없음, 영구 보존 | PG 거래 감사 이력 |
| pay_payment_method | `is_deleted = true` | 고객 삭제 요청 시 논리 삭제 |
| pay_card_restriction | 90일 후 배치 물리 삭제 | 일시적 보안 데이터 |
| pay_card_fail_counter | 물리 삭제 없음(카드별 1행 upsert) | 상시 갱신되는 카운터 |

---

## 근거

| 항목 | 출처 |
|---|---|
| 엔티티 도출 | `../DD-EARS기능요구/payment.md` 주어/목적어 명사 추출 |
| 테이블 접두사 `pay_` | `DB-도메인정의서.md` 스키마 그룹핑 (rns_trade) |
| PCI DSS (카드 미저장) | `D8-NFR.md` NFR-SE-08, REQ-PAY-017 |
| 카드 3회 제한 | REQ-PAY-018 |
| 총 3회 시도 | REQ-PAY-003 |
| 멱등 판별 (pg_transaction_id) | REQ-PAY-006 |
| 카드 연속실패 카운터(pay_card_fail_counter) | REQ-PAY-023 (바텀업 검토 보완, 2026-08-21) |
| 환불 산식(상품주문금액 + 환불 대상 배송비) | REQ-PAY-024 (2026-10-29 개정) |
| 복합결제·결제번호·주문금액 검증 | REQ-PAY-025~028 (2026-10-27) |
| 결제 확인 중·누적 실패 합산 | REQ-PAY-029 (2026-10-29) |
| 입금 통보·취소 경합 자동 환불(LATE_DEPOSIT) | REQ-PAY-030 (2026-10-29) |
| 가상계좌 환불계좌(refund_* 3컬럼) | REQ-PAY-031 (2026-10-29) |
