# 상위 유스케이스 — Payment

> **단계**: 구조설계
> **문서범위**: Domain
> **문서종류**: Design
>
> **작성 목적**: 도메인 정의서(DB)의 책임 목록을 "누가(액터) 무엇을(업무) 하는가" 단위로 분해한다.
> **흐름 내 위치**: DB 도메인 정의서 → **DC 상위 유스케이스** → DD EARS → DE 메뉴구조도
> **작성 주체**: 시니어 개발자 + AI 협업 (기획자·현업 검토·확인)

| 항목 | 내용 |
|---|---|
| ID | DESIGN-UC-PAYMENT-001 |
| 상태 | **Finalized** |
| 작성일 | 2026-08-11 |
| 갱신일 | 2026-10-29 |

---

## ① 액터 정의

| 액터 | 설명 | 채널 |
|---|---|---|
| 고객 | 로그인한 최종 구매자. 본인 결제수단 관리·결제 실행 | M(Mobile) |
| CS 담당자 | 플랫폼 관리자. 환불 처리·결제 이력 조회 권한 | A(Admin) |
| 시스템 | Order 도메인의 결제 요청, 배치 스케줄러 (카드 제한 해제) | C(Consumer)/B(Batch) |

---

## ② 업무그룹별 유스케이스

### 결제 실행

| 유스케이스 | 액터 | 도출 근거 |
|---|---|---|
| PG 결제 승인 요청 | 시스템(Order 도메인 요청) | 도메인정의서 "결제 승인" 책임 |
| 결제완료 이벤트 발행 → Order | 시스템 | 도메인정의서 §4: Payment→Order |
| 결제실패 이벤트 발행 → Order | 시스템 | 도메인정의서 §4: Payment→Order |
| 결제 재시도 (총 3회 시도) | 시스템 | PG 일시 장애 대응 |
| 가상계좌 발급 (입금대기) | 시스템(Order 도메인 요청) | 정책서 payment.md 4.4.1 (REQ-PAY-001) |
| 가상계좌 입금 통보 처리 (결제완료) | 시스템(PG 통보) | 정책서 4.4.2 |
| 결제 확인 중 처리 (3초 무응답 → PG 거래 조회) | 시스템 | REQ-PAY-005·029 |
| 환불계좌 입력·검증 (가상계좌 결제 시, 실명 확인은 결제 요청 시점) | 고객 | REQ-PAY-031, 정책서 8.7.1 |

### 환불·취소

| 유스케이스 | 액터 | 도출 근거 |
|---|---|---|
| 전액 환불 (주문 취소 시) | 시스템(Order 이벤트 수신) | 도메인정의서 "취소·환불" 책임 |
| 부분 환불 (클레임 환불, 어드민 [환불 처리] API-029 요청 시) | CS 담당자(어드민 환불 API) → 시스템 | 부분반품 환불 정책, REQ-PAY-009 (CLAIM_COMPLETED는 환불 트리거 아님) |
| 수동 환불 처리 | CS 담당자 | CS 운영: PG 자동 환불 실패 시 |
| 입금 통보·취소 경합 자동 환불 (LATE_DEPOSIT) | 시스템(PG 입금 통보) | REQ-PAY-030, 취소 우선·운영자 승인 없음 |

### 결제수단 관리

| 유스케이스 | 액터 | 도출 근거 |
|---|---|---|
| 결제수단 등록 / 삭제 | 고객 | 도메인정의서 "결제수단 관리" |
| 결제수단 목록 조회 | 고객 | 마이페이지 기능 |
| 카드 일일 제한 (3회 실패 시 당일 차단) | 시스템 | 보안 정책: 부정결제 방지 |
| 카드 제한 자동 해제 (익일 00:00) | 시스템(배치) | 보안 정책: 익일 자동 해제 |

### 결제 조회·관리

| 유스케이스 | 액터 | 도출 근거 |
|---|---|---|
| 내 결제 이력 조회 | 고객 | 마이페이지 기능 |
| 전체 결제 이력 검색·필터 | CS 담당자 | 관리자 업무 |
| PG 거래 로그 조회 | CS 담당자 | 장애 대응·감사 |

---

## ③ 액터-유스케이스 관계도

```plantuml
@startuml
left to right direction
skinparam backgroundColor transparent

actor 고객 as Customer
actor "CS 담당자" as CS
actor 시스템 as System

package "결제 실행" {
  usecase "PG 결제 승인" as UC1
  usecase "결제완료 이벤트 발행" as UC2
  usecase "결제실패 이벤트 발행" as UC3
  usecase "결제 재시도" as UC4
  usecase "가상계좌 발급" as UC15
  usecase "입금 통보 처리" as UC16
  usecase "결제 확인 중 처리" as UC17
  usecase "환불계좌 입력" as UC19
}

package "환불·취소" {
  usecase "전액 환불" as UC5
  usecase "부분 환불" as UC6
  usecase "수동 환불" as UC7
  usecase "LATE_DEPOSIT 자동 환불" as UC18
}

package "결제수단 관리" {
  usecase "결제수단 등록/삭제" as UC8
  usecase "결제수단 조회" as UC9
  usecase "카드 일일 제한" as UC10
  usecase "카드 제한 해제" as UC11
}

package "결제 조회·관리" {
  usecase "내 결제 이력" as UC12
  usecase "전체 결제 검색" as UC13
  usecase "PG 거래 로그" as UC14
}

System --> UC1
System --> UC2
System --> UC3
System --> UC4
System --> UC15
System --> UC16
System --> UC17
System --> UC18
System --> UC5
System --> UC6
System --> UC10
System --> UC11

Customer --> UC19
Customer --> UC8
Customer --> UC9
Customer --> UC12

CS --> UC7
CS --> UC13
CS --> UC14
@enduml
```

---

## ④ 권한 범위

| 규칙 | 도출 근거 |
|---|---|
| 고객은 본인 결제수단만 등록·삭제·조회 가능 | 개인정보 보호 원칙 |
| 환불은 원결제 수단으로 한다. 카드·간편결제는 PG 승인취소, 가상계좌는 결제 시 저장된 환불계좌 입금(예금주=주문자 본인)이다. 원결제 수단 환불 불가 시에 한해 CS 승인 하 수동 계좌이체로 대체한다(REQ-PAY-013) | PG 환불 정책, REQ-PAY-013·031 |
| CS 수동 환불은 PG 자동 환불 실패 건에 한함. 단 LATE_DEPOSIT 환불은 운영자 승인 없이 자동 요청(실패 시에만 수동) | CS 운영 규칙, REQ-PAY-030 |
| 카드 정보 원본(카드번호·CVV)은 서버 미저장, PG 토큰만 보유 | NFR-SE-08 PCI DSS |
| 동일 카드 3회 연속 실패 시 당일 결제 차단 | 보안 정책: 부정결제 방지 |

---

## 근거

| 항목 | 출처 |
|---|---|
| 업무그룹 분류 | `DB-도메인정의서.md` Payment "핵심 책임" |
| 액터·채널 | `D9-컴포넌트.md` 앱 구성 + 도메인 정의서 "채널" |
| 환불 정책 | PG 표준 환불 규칙 |
| 카드 제한 규칙 | `D8-NFR.md` NFR-SE-08, 보안 정책 |
| 이벤트 연동 | `DB-도메인정의서.md` Payment "의존·이벤트 발행" |
| 신규 REQ-PAY-023~031 반영 | 가상계좌 발급·입금 통보(정책서 4.4), 결제 확인 중(REQ-PAY-029), LATE_DEPOSIT 자동 환불(REQ-PAY-030), 환불계좌 입력(REQ-PAY-031). 023~028은 카드 카운터·환불 산식·복합결제로 기존 UC 범위 |
