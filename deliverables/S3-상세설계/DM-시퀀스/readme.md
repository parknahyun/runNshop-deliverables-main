# 시퀀스 — 주문·결제 도메인

> **단계**: 상세설계 (S3)  
> **문서범위**: Bolt (Order + Payment)  
> **문서종류**: Design  
>
> **작성 목적**: 인터페이스 명세(DL)의 API를 호출 순서·참여 객체·트랜잭션 경계로 구체화한다.  
> "이 API가 호출되면 내부에서 어떤 순서로 어떤 객체가 상호작용하는가"를 확정한다.
>
> **흐름 내 위치**:
> ```
> DL 인터페이스 명세 → DM 시퀀스 → DN 화면 레이아웃 / DP 클래스 설계
> ```

---

## 공통 규칙 (C3 아키텍처컨벤션 / C5 이벤트설계컨벤션 준수)

### 1. Controller 분리 기준 (C3 §4.2)

> Controller 분리 단위는 서브도메인·업무 특성에 따라 매번 판단한다 (판단 기준은 `.kiro/steering/api-design-rules.md` 참조 — 보편 규칙으로 고정하지 않음).
>
> **Order 도메인에 대한 확정 결과** (2026-10): `order/` 서브도메인은 앱별 응답/권한 차이가 있음에도 Service가 이미 공유 구조이고 메서드 분기로 충분히 명확해, **단일 `OrderController`**로 통합한다 — `getMyOrders()`(`/api/mobile/v1/my/orders`), `getMyOrderDetail()`(`/api/mobile/v1/my/orders/{orderId}`), `createOrderSheet()`(`/api/mobile/v1/my/orders/sheet`), `placeOrder()`(`/api/mobile/v1/my/orders/{orderSheetId}/pay`, 2026-10-19 신규), `getAdminOrders()`(`/api/admin/v1/orders`), `getAdminOrderDetail()`(`/api/admin/v1/orders/{orderId}`), `getPartnerOrders()`(`/api/partner/v1/orders`), `getPartnerOrderDetail()`(`/api/partner/v1/orders/{orderId}`). `claim/` 서브도메인(`getMyClaims`/`getMyClaimDetail` 포함)은 별도 `ClaimController`로 둔다. 이 결정은 Order 서브도메인에 한정되며, 다른 서브도메인(`cart/`, `shipping/`, 또는 Payment 등 타 도메인)에 자동 적용되지 않는다 — 각 담당자가 그때그때 판단한다.
>
> **(2026-10-19 구현 확인·보완)** 위 URL(`getMyOrders`/`getMyOrderDetail`)은 원래 `/api/v1/members/me/orders` 구버전으로 적혀 있었다 — order-domain-api-migration 작업이 Controller/DL은 `/api/mobile/v1/my/...`로 바꿨지만 이 문단은 갱신 대상에서 빠져 있던 것을 이번 작업으로 발견·정정했다. `placeOrder()` 메서드도 메서드 목록에 없었다가 이번에 추가(2026-10-19 신규 구현).
>
> 과거(v1/v2) 버전에서 쓰던 `{App}{Domain}Controller`(`AdminOrderController`, `PartnerOrderController`, `CustomerClaimController`, `AdminClaimController` 등) 네이밍은 Order에서는 폐기됐다 — 아래 다이어그램에 남아있는 해당 이름은 위 통합 Controller의 메서드로 환산해 읽는다. 다른 도메인/서브도메인에서 이 네이밍을 쓰는 것 자체가 틀린 것은 아니다.

### 2. EventPublisher = Outbox 패턴 표현 (C5 §5.1)

> 본 문서의 시퀀스에서 `Service -> EventPublisher : publish(EVENT_NAME)` 호출은
> **"비즈니스 데이터 변경과 동일 트랜잭션 내에서 Outbox 테이블에 이벤트를 저장하는 행위"**를 축약 표현한 것이다.
> 즉 `EventPublisher.publish(...)`는 `outboxRepository.save(OutboxEvent(...))`와 동일 트랜잭션에서 실행되며,
> 실제 Broker(또는 프로토타입의 in-process ApplicationEventPublisher) 발행은 별도의 **Outbox Publisher**가
> Outbox 테이블을 polling(1초 주기)하여 비동기로 수행한다(C5 §5.1~§5.3).
>
> ```
> [Service 트랜잭션]                    [Outbox Publisher (비동기, 별도 프로세스)]
> 1. 비즈니스 데이터 변경                  Outbox 테이블 polling
> 2. EventPublisher.publish(...)   ──▶   → Broker 발행 (프로토타입: ApplicationEvent)
>    = Outbox 테이블 INSERT               → 발행 완료 시 Outbox row 삭제
> 3. COMMIT (1·2 원자적)
> ```
>
> 프로토타입 단계에서는 C5 §5.3에 따라 Outbox 테이블 대신 in-process `ApplicationEventPublisher`를 사용하므로,
> 아래 다이어그램의 `EventPublisher` 참여자는 실 프로젝트 전환 시 `OutboxEventPublisher`(Outbox INSERT) + `OutboxPublisher`(polling·발행) 2단계로 분리된다.
> 컨슈머 측 멱등 처리(`processed_event` 테이블, eventId UNIQUE)는 C5 §6.1을 따른다.

---

## 도메인별 파일

도메인별 파일로 분리되어 있습니다.

| 구분 | 파일 | 시퀀스 수 |
|---|---|---|
| Order 도메인 | [order.md](order.md) | 29개 절 (§1~26, 7-1·7-2·18-1 포함) — API 20, 컨슈머 1, 배치 8. 하위 흐름 §3-1·§4-1(비동기 컨슈머)·§4-2(폐기 이력)·§5-1(입금 통보·취소 경합) 별도. §23~25는 DQ BAT-004·006·005 시퀀스(2026-10-29 추가), §26 입고 확인(pickup-confirm, 2026-11-03 추가) |
| Payment 도메인 | [payment.md](payment.md) | 1개 (§4-1) |
| Catalog 도메인 | [catalog.md](catalog.md) | 13개 (API 9건 + 컨슈머 2건 + 배치 2건) |

---

## 작성 규칙

| 규칙 | 설명 |
|---|---|
| 1 시퀀스 = 1 트리거 | API endpoint, 이벤트 수신, 스케줄 배치 각각 1개 시퀀스 |
| 태그로 유형 구분 | `[API]` 사용자 요청, `[컨슈머]` 이벤트 수신, `[배치]` 스케줄러 |
| 참여자 = 클래스 후보 | Controller/Listener/Scheduler, Service, Repository, PublicApi, EventPublisher |
| 트랜잭션 경계 표시 | Service 레벨에서 @Transactional |
| 에러 분기 포함 | 인터페이스 명세의 에러 응답과 대응 |
| 도메인 경계 명시 | 타 도메인 호출은 PublicApi(동기) 또는 EventPublisher(비동기)로 표현 |
| Controller 네이밍 | 앱별 분리 — `{App}{Domain}Controller` (C3 §4.2, 상단 공통 규칙 §1 참조) |
| EventPublisher 표현 | Outbox 패턴 축약 표현 — 비즈니스 변경과 동일 트랜잭션 (C5 §5.1, 상단 공통 규칙 §2 참조) |

---

## 근거

| 항목 | 출처 |
|---|---|
| API endpoint | 인터페이스 명세(DL) API 중 20개 API 시퀀스 상세화 (+ 컨슈머 1건, 배치 8건 — Order 총 29개 절, 2026-10-29 재집계. 종전 "25개"·"26개"는 실제 건수와 불일치했음) |
| 컨슈머 시퀀스 | 이벤트 플로우(DI) PAYMENT_APPROVED 수신 액션 |
| 배치 시퀀스 | EARS(DD) REQ-ORD-015(D+11 자동확정, 진행 중 클레임 제외·실패 재처리), REQ-ORD-042(배송비 24시간 만료), REQ-ORD-043(12시간 리마인드), REQ-ORD-014(입금기한 만료·TEMP TTL, DQ BAT-004~006) |
| 에러 분기 | GWT(DJ) 예외 시나리오 |
| HTTP Status 코드 정합 | 인터페이스 명세(DL) 공통 규칙 §2 C6 §7 기준 — 2026-08-24 재고/상태충돌류(409)·기한초과류(422) 20건 및 INVALID_STATUS(신규, 409) 6건 정정 |
| 도메인 간 호출 | 이벤트 플로우(DI) 동기/비동기 판단 |
| 참여 객체 | ERD(DF) 엔티티 + 컴포넌트(D9) 모듈 구조 |
| 상태 전이 | 상태머신(DH) 전이 규칙 |
| Controller 네이밍 | C3 아키텍처컨벤션 §4.2 (앱별 Controller 분리) |
| Outbox 패턴 | C5 이벤트설계컨벤션 §5.1 (비즈니스 변경 + Outbox 저장 = 동일 트랜잭션) |

