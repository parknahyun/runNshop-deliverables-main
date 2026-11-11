# 러닝 커머스 플랫폼 Modular Monolith 설계서

> 작성 주체: 3TOP 2본부
> 문서 버전: v1.0
> 작성일: 2026.06.22
> 상태: 초안 (Draft)

---

## 목차

1. [개요](#1-개요)
2. [설계 원칙](#2-설계-원칙)
3. [패키지 구조](#3-패키지-구조)
4. [모듈 내부 레이어 구조](#4-모듈-내부-레이어-구조)
5. [모듈 간 통신 규칙](#5-모듈-간-통신-규칙)
6. [데이터 접근 규칙](#6-데이터-접근-규칙)
7. [DB 스키마 격리](#7-db-스키마-격리)
8. [복제 테이블 동기화](#8-복제-테이블-동기화)
9. [Outbox Pattern](#9-outbox-pattern)
10. [모듈 의존 방향](#10-모듈-의존-방향)
11. [Nginx API 라우팅](#11-nginx-api-라우팅)
12. [MSA 전환 전략](#12-msa-전환-전략)

---

## 1. 개요

### 아키텍처 개요

```
단일 배포 단위 (1개 Spring Boot 애플리케이션)
    + 12개 도메인 모듈로 내부 분리
    + 모듈 간 의존 규칙 강제
    + 2단계 MSA 전환 시 모듈 = 독립 서비스
```

### 기술 스택

| 항목 | 기술 |
|------|------|
| 언어 | Kotlin |
| 프레임워크 | Spring Boot |
| DB | PostgreSQL |
| ORM | MyBatis |
| 인증 | JWT + Redis |
| 검색 | Elasticsearch |
| 파일 | AWS S3 |
| 이벤트 | Outbox Pattern + Spring Event Consumer |
| 배포 | Docker Compose (1단계) |

### Runtime 선택 실행 구조

| 컴포넌트 | 로컬 | 개발서버 |
|---------|------|---------|
| Backend API | ✅ 로컬 실행 | ✅ |
| Consumer | ✅ 로컬 실행 | ✅ |
| Batch | ✅ 로컬 실행 | ✅ |
| Frontend | ✅ 로컬 실행 | ✅ |
| PostgreSQL | ❌ 개발서버 공용 | ✅ |
| Redis | ❌ 개발서버 공용 | ✅ |
| Elasticsearch | ❌ 개발서버 공용 | ✅ |

---

## 2. 설계 원칙

### 6대 설계 원칙

| # | 원칙 | 구현 방식 |
|---|------|---------|
| 1 | 도메인 중심 아키텍처 | 12개 Bounded Context 기반 모듈 분리 |
| 2 | Runtime 선택 실행 | Frontend·Backend·Consumer·Batch 독립 실행 |
| 3 | 운영 안정성 우선 | Outbox + 재시도 3회 + DLQ + 모니터링 |
| 4 | Event-driven Architecture | Outbox + Spring Event Consumer |
| 5 | 독립 배포 가능 구조 | 모듈 단위 설계 → 2단계 K8s Pod |
| 6 | Spec 기반 개발 프로세스 | AI 9대 공정 기반 |

### 모듈 간 통신 원칙

```
허용
    ├─ 동기: PublicApi Interface 호출만 허용
    ├─ 비동기: Outbox 이벤트 발행·Consumer 수신
    └─ 복제 테이블: Query(조회) 전용만 허용

금지
    ├─ 타 모듈 내부 클래스 직접 호출
    ├─ 타 모듈 DB 테이블 직접 접근
    └─ 순환 의존 (A→B→A)
```

---

## 3. 패키지 구조

```
com.top3.running
    ├─ common                               ← 기술 공통 (모듈 아님)
    │   ├─ outbox                           ← Outbox Pattern
    │   │   ├─ OutboxEvent.kt
    │   │   ├─ OutboxEventRepository.kt
    │   │   └─ OutboxEventConsumer.kt
    │   ├─ event                            ← 이벤트 인터페이스
    │   │   └─ DomainEvent.kt
    │   ├─ audit                            ← 소프트 삭제·감사 공통
    │   │   ├─ Auditable.kt
    │   │   └─ SoftDeletable.kt
    │   ├─ exception                        ← 공통 예외
    │   │   ├─ BusinessException.kt
    │   │   └─ ErrorCode.kt
    │   └─ sync                             ← 복제 테이블 동기화
    │       ├─ replica
    │       │   ├─ ConfigCodeReplica.kt
    │       │   ├─ ConfigCodeReplicaMapper.kt
    │       │   └─ ConfigCodeReplicaRepository.kt
    │       ├─ CodeSyncBatch.kt
    │       └─ SyncHistory.kt
    │
    ├─ module
    │   ├─ order                            ← Order 모듈
    │   ├─ catalog                          ← Catalog 모듈
    │   ├─ member                           ← Member 모듈
    │   ├─ payment                          ← Payment 모듈
    │   ├─ promotion                        ← Promotion 모듈
    │   ├─ settlement                       ← Settlement 모듈
    │   ├─ vendor                           ← Vendor 모듈
    │   ├─ notification                     ← Notification 모듈
    │   ├─ community                        ← Community 모듈
    │   ├─ search                           ← Search 모듈
    │   ├─ config                           ← Config 모듈
    │   └─ audit                            ← Audit 모듈
    │
    └─ RunningCommerceApplication.kt
```

---

## 4. 모듈 내부 레이어 구조

각 모듈은 동일한 레이어 구조를 따른다.

```
{module}
    ├─ api                                  ← REST API 진입점
    │   ├─ {Domain}Controller.kt
    │   └─ dto
    │       ├─ request
    │       └─ response
    │
    ├─ application                          ← 비즈니스 로직
    │   ├─ command                          ← Command: PublicApi 호출만 허용
    │   │   └─ {Domain}Service.kt
    │   ├─ query                            ← Query: 복제 테이블 사용 허용
    │   │   └─ {Domain}QueryService.kt
    │   └─ {Domain}PublicApi.kt             ← 타 모듈 호출용 Public Interface
    │
    ├─ domain                               ← 도메인 모델
    │   ├─ {Entity}.kt
    │   ├─ {Domain}Repository.kt
    │   └─ vo
    │
    ├─ infrastructure                       ← 구현체
    │   ├─ persistence
    │   │   ├─ {Entity}Mapper.kt            ← MyBatis Mapper
    │   │   └─ {Domain}RepositoryImpl.kt
    │   ├─ external                         ← 외부 API 연동
    │   └─ replica                          ← 복제 테이블 Mapper (Query 전용)
    │       └─ {Replica}Mapper.kt
    │
    ├─ event
    │   ├─ publisher
    │   │   └─ {Domain}EventPublisher.kt
    │   └─ consumer
    │       └─ {Domain}EventConsumer.kt
    │
    └─ batch                                ← 스케줄 배치 (해당 모듈만)
        └─ {Domain}Batch.kt

### 모듈별 주요 배치 목록

| 모듈 | 배치명 | 주기 | 역할 |
|------|--------|------|------|
| Order | TempOrderTimeoutBatch | 1분 | TEMP 30분 초과 → CANCELLED + 보상 |
| Order | ProcessingTimeoutBatch | 1분 | PROCESSING 3분 초과 → CANCELLED + 보상 |
| Order | ShippingDeadlineBatch | 매일 09:00 | 출고기한 초과 → Notification + Vendor 지표 |
| Order | AutoConfirmBatch | 매일 02:00 | 배송완료 7일 경과 → 구매확정 이벤트 |
| Order | ClaimExpireBatch | 매일 02:00 | 배송완료 10일 경과 → 클레임 불가 전환 |
| Catalog | DisplayPageScheduleBatch | 매 5분 | 예약 전시 페이지 자동 전환 |
| Catalog | ProductIndexSyncBatch | 매일 03:00 | ES 상품 인덱스 전체 동기화 |
| Member | MemberGradeBatch | 매월 1일 00:00 | 전 회원 등급 산정·쿠폰 지급 |
| Member | YearEndGradeCouponBatch | 매년 12월 31일 | 등급별 연말 쿠폰 일괄 지급 |
| Member | PointExpireBatch | 매일 02:00 | 소멸 30일 전 알림 이벤트 발행 |
| Settlement | SettlementCalculateBatch | 매월 5일 | 입점사별 월 정산 계산 |
| Settlement | SettlementPayBatch | 매월 15일 | 정산금 지급 처리 |
| common | CodeSyncBatch | 1분 | 공통코드 복제 테이블 동기화 |
```

---

## 5. 모듈 간 통신 규칙

### PublicApi Interface 패턴

타 모듈 호출 시 반드시 `PublicApi` 인터페이스를 통해서만 접근한다.

```kotlin
// catalog 모듈 Public API 정의
interface CatalogPublicApi {
    fun checkStock(productId: Long, skuId: Long): StockCheckResult
    fun getProductPrice(productId: Long): ProductPriceResult
    fun reserveStock(productId: Long, skuId: Long, quantity: Int): Boolean
    fun releaseStock(productId: Long, skuId: Long, quantity: Int)
}

// order 모듈에서 호출 (Interface만 의존)
class OrderService(
    private val catalogApi: CatalogPublicApi,
    private val memberApi: MemberPublicApi,
    private val promotionApi: PromotionPublicApi
) {
    fun createOrder(command: CreateOrderCommand) {
        val stockResult = catalogApi.checkStock(
            command.productId, command.skuId
        )
        if (!stockResult.available) throw OutOfStockException()
    }
}
```

### 동기 vs 비동기 구분 기준

| 방식 | 사용 조건 | 예시 |
|------|---------|------|
| 동기 API | 즉시 응답 필요·실패 시 주문 중단 | 재고 확인·쿠폰 유효성·권한 확인 |
| 비동기 이벤트 | 실제 처리·알림·정산 | 재고 선점·결제·구매확정·알림 |

---

## 5-1. 외부 시스템 연동 목록

| 모듈 | 외부 시스템 | 연동 방식 | 용도 |
|------|-----------|---------|------|
| Payment | PG사 | REST API (동기) | 결제 승인·취소·환불 |
| Payment | FDS | REST API (동기) | 이상 결제 탐지·자동 차단 |
| Order | 배송사 API | REST API (동기) | 운송장 등록·배송 추적 |
| Catalog | AWS Rekognition | REST API (비동기) | 상품 이미지 분석 (2단계) |
| Catalog | AWS S3 | REST API | 이미지·파일 저장 |
| Vendor | 계좌 인증 API | REST API (동기) | 1원 송금 계좌 인증 |
| Notification | 카카오 알림톡 | REST API | 알림 발송 |
| Notification | SMS | REST API | 알림 발송 Fallback |
| Notification | 이메일 (SES) | REST API | 알림 발송 Fallback |
| Member | 네이버 OAuth | OAuth 2.0 | SNS 로그인·가입 |
| Member | Apple OAuth | Sign in with Apple | SNS 로그인·가입 |

---

## 6. 데이터 접근 규칙

### CQRS 기반 접근 규칙

```
Query (조회)
    → 복제 테이블 직접 사용 허용
    → 화면 표시·목록 조회·코드명 변환

Command (쓰기·비즈니스 로직)
    → 반드시 PublicApi 호출
    → 최신 데이터 보장 필요
```

### 데이터 접근 규칙 요약

| 접근 대상 | Query | Command |
|---------|-------|---------|
| 자체 도메인 테이블 | ✅ | ✅ |
| 복제 테이블 | ✅ | ❌ |
| 타 모듈 PublicApi | ✅ | ✅ |
| 타 모듈 DB 직접 | ❌ | ❌ |

### 코드 레벨 예시

```kotlin
// ✅ Query — 복제 테이블 사용
class OrderQueryService(
    private val configCodeReplicaRepository: ConfigCodeReplicaRepository
) {
    fun getOrderStatusName(code: String): String {
        return configCodeReplicaRepository
            .findByGroupAndCode("ORDER_STATUS", code)
            ?.codeName ?: code
    }
}

// ✅ Command — PublicApi 호출
class OrderService(
    private val catalogApi: CatalogPublicApi
) {
    fun createOrder(command: CreateOrderCommand) {
        val stock = catalogApi.checkStock(command.productId, command.skuId)
        if (!stock.available) throw OutOfStockException()
    }
}

// ❌ 금지 — Command에서 복제 테이블 직접 사용
class SettlementService(
    private val vendorFeeReplicaRepository: VendorFeeRateReplicaRepository
) {
    fun calculateFee(vendorId: Long): BigDecimal {
        // 금지: 정산 계산에 복제 테이블 사용
        return vendorFeeReplicaRepository.findByVendorId(vendorId)?.rate
    }
}
```

---

## 7. DB 스키마 격리

### 모듈별 테이블 Prefix

| 모듈 | Prefix | 예시 |
|------|--------|------|
| order | `ord_` | `ord_order`, `ord_order_item`, `ord_claim` |
| catalog | `cat_` | `cat_product`, `cat_sku`, `cat_price` |
| member | `mbr_` | `mbr_member`, `mbr_point`, `mbr_coupon` |
| payment | `pay_` | `pay_payment`, `pay_cancel` |
| promotion | `prm_` | `prm_coupon`, `prm_event_price`, `prm_quantity_discount` |
| settlement | `stl_` | `stl_settlement`, `stl_target`, `stl_payment` |
| vendor | `vnd_` | `vnd_vendor`, `vnd_contract`, `vnd_grade` |
| notification | `ntf_` | `ntf_history`, `ntf_template`, `ntf_batch` |
| community | `cmt_` | `cmt_review`, `cmt_crew`, `cmt_challenge` |
| search | `sch_` | `sch_keyword`, `sch_autocomplete` |
| config | `cfg_` | `cfg_operator`, `cfg_code`, `cfg_banner` |
| audit | `adt_` | `adt_log`, `adt_trace`, `adt_dlq` |
| common | `cmn_` | `cmn_outbox_event`, `cmn_sync_history` |

### 공통 컬럼 (전 테이블 적용)

```sql
-- 모든 테이블 공통 컬럼
created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
deleted_at      DATETIME,
deleted_by      VARCHAR(50)

-- 물리적 DELETE 전면 금지
-- 모든 삭제는 is_deleted = true 소프트 삭제로 처리
```

---

## 8. 복제 테이블 동기화

### 복제 원칙

> Config가 마스터 데이터 소유.  
> 타 모듈(Config 포함)은 복제 테이블 조회.  
> 배치가 주기적으로 마스터 → 복제 테이블 Upsert.  
> 복제 테이블은 Query 전용으로만 사용.

### 복제 테이블 목록

| 마스터 테이블 | 복제 테이블 | 배치 주기 | 조회 모듈 |
|-------------|-----------|---------|---------|
| `cfg_common_code` | `config_code_replica` | 1분 | 전 모듈 |
| `cat_category` | `catalog_category_replica` | 10분 | Search·Settlement |
| `vnd_fee_rate` | `vendor_fee_rate_replica` | 10분 | Settlement |
| `mbr_grade_discount` | `member_grade_discount_replica` | 10분 | Order·프론트 |

### config_code_replica 테이블

```sql
config_code_replica (
    id              BIGINT          PK AUTO_INCREMENT,
    group_code      VARCHAR(50)     NOT NULL,
    code            VARCHAR(50)     NOT NULL,
    code_name       VARCHAR(100)    NOT NULL,
    sort_order      INT             NOT NULL DEFAULT 0,
    status          VARCHAR(20)     NOT NULL DEFAULT 'ACTIVE',
    synced_at       DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50),
    UNIQUE KEY uk_group_code (group_code, code)
)
```

### 동기화 배치

```kotlin
// common/sync/CodeSyncBatch.kt
@Component
class CodeSyncBatch(
    private val configPublicApi: ConfigPublicApi,
    private val configCodeReplicaRepository: ConfigCodeReplicaRepository,
    private val syncHistoryRepository: SyncHistoryRepository
) {
    @Scheduled(fixedDelay = 60_000)
    fun sync() {
        val history = SyncHistory.start("CODE")
        try {
            val masterCodes = configPublicApi.getAllCodes()
            configCodeReplicaRepository.upsertAll(masterCodes)
            history.success(masterCodes.size)
        } catch (e: Exception) {
            history.fail(e.message)
        } finally {
            syncHistoryRepository.save(history)
        }
    }
}
```

### 동기화 이력 테이블

```sql
cmn_sync_history (
    id              BIGINT          PK AUTO_INCREMENT,
    sync_type       VARCHAR(50)     NOT NULL,
    target_module   VARCHAR(50)     NOT NULL,
    synced_count    INT             NOT NULL DEFAULT 0,
    status          VARCHAR(20)     NOT NULL,   -- SUCCESS·FAILED
    started_at      DATETIME        NOT NULL,
    finished_at     DATETIME,
    error_message   VARCHAR(500),
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

---

## 9. Outbox Pattern

### 동작 원리

```
[저장] 비즈니스 로직 + Outbox 저장 → 단일 DB 트랜잭션
[감시] Outbox Consumer (상시 대기) → PENDING 레코드 즉시 감지
[처리] Spring @EventListener + @Async → 수신 모듈 Consumer에 전달
[완료] 성공/실패 상태 업데이트
```

### Outbox 테이블

```sql
cmn_outbox_event (
    id              BIGINT          PK AUTO_INCREMENT,
    aggregate_id    VARCHAR(100)    NOT NULL,
    aggregate_type  VARCHAR(50)     NOT NULL,
    event_type      VARCHAR(100)    NOT NULL,
    payload         JSON            NOT NULL,
    status          VARCHAR(20)     NOT NULL DEFAULT 'PENDING',
    retry_count     INT             NOT NULL DEFAULT 0,
    created_at      DATETIME        NOT NULL,
    processed_at    DATETIME,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### Outbox 상태값

| 상태 | 설명 |
|------|------|
| `PENDING` | 처리 대기 |
| `PROCESSING` | Consumer 처리 중 |
| `PROCESSED` | 처리 완료 |
| `FAILED` | 최종 실패 (운영팀 이관) |

### 재시도 및 실패 처리

| 항목 | 기준 |
|------|------|
| 재시도 횟수 | 최대 3회 |
| 재시도 간격 | 즉시 → 30초 → 1분 (점진적 백오프) |
| 최종 실패 | `FAILED` 전환 + DLQ 적재 + 운영팀 알림 |
| 프로세스 중단 복구 | 재기동 시 PENDING·PROCESSING 레코드 자동 재발행 |

### 2단계 MSA 전환

```
1단계: Outbox Consumer (인프로세스 상시 감시)
    ↓
2단계: Debezium CDC → Outbox 테이블 변경 감지
       → Kafka Topic 자동 발행
       → Kafka Consumer로 전환
       → 코드 변경 없이 브로커 교체
```

---

## 10. 모듈 의존 방향

### 허용 의존

```
order      → catalog    (PublicApi: 재고 확인·선점·복구)
order      → member     (PublicApi: 쿠폰·포인트 사용·복원)
order      → payment    (PublicApi: 결제·취소)
order      → promotion  (PublicApi: 쿠폰 유효성·행사가)
order      → config     (PublicApi: CS 권한 확인)

catalog    → vendor     (PublicApi: 입점사 유효성)
catalog    → config     (PublicApi: MD 권한 확인)

settlement → order      (PublicApi: 분담금·배송비 조회)
settlement → vendor     (PublicApi: 계좌·수수료율)

notification → member   (PublicApi: 수신 거부 확인)

모든 모듈  → common     (공통 유틸·Outbox·Audit)
```

### 금지 의존

```
catalog    → order      ❌ 역방향
member     → order      ❌ 역방향
payment    → order      ❌ 역방향
settlement → catalog    ❌ 불필요 (복제 테이블 사용)
A          → B → A      ❌ 순환 의존
타 모듈 DB 직접 접근    ❌ 전면 금지
```

### 의존 방향 다이어그램

```
[고객 경험]
    Member ──→ (이벤트) ──→ Order
    Catalog ──→ (이벤트) ──→ Order
    Promotion ──→ (이벤트) ──→ Order

[거래 처리]
    Order ──→ Catalog   (PublicApi)
    Order ──→ Member    (PublicApi)
    Order ──→ Payment   (PublicApi)
    Order ──→ Promotion (PublicApi)

[정산]
    Order ──→ (이벤트) ──→ Settlement
    Settlement ──→ Order  (PublicApi)
    Settlement ──→ Vendor (PublicApi)

[운영 인프라]
    전 도메인 ──→ (이벤트) ──→ Notification
    전 도메인 ──→ (이벤트) ──→ Audit
    Catalog·Promotion·Community ──→ (배치) ──→ Search
    전 도메인 ──→ common (공통)
```

---

## 11. Nginx API 라우팅

### 채널별 라우팅 기준

```nginx
# ── 고객 API ──────────────────────────────
location /api/v1/orders/          { proxy_pass http://backend-api:8080; }
location /api/v1/products/        { proxy_pass http://backend-api:8080; }
location /api/v1/members/         { proxy_pass http://backend-api:8080; }
location /api/v1/payments/        { proxy_pass http://backend-api:8080; }
location /api/v1/promotions/      { proxy_pass http://backend-api:8080; }
location /api/v1/community/       { proxy_pass http://backend-api:8080; }
location /api/v1/search/          { proxy_pass http://backend-api:8080; }

# ── Webhook (PG사·배송사 IP 제한) ─────────
location /webhook/v1/payment/     {
    allow 1.2.3.4;
    deny all;
    proxy_pass http://backend-api:8080;
    proxy_set_header X-Request-Source "webhook";
}
location /webhook/v1/delivery/    {
    allow 5.6.7.8;
    deny all;
    proxy_pass http://backend-api:8080;
    proxy_set_header X-Request-Source "webhook";
}

# ── 어드민 (VPN·허용 IP 제한) ─────────────
location /api/admin/v1/           {
    allow 10.0.0.0/8;
    deny all;
    proxy_pass http://backend-api:8080;
    proxy_set_header X-Request-Source "admin";
}

# ── 입점사 BO (VPN·허용 IP 제한) ───────────
location /api/partner/v1/         {
    allow 10.0.0.0/8;
    deny all;
    proxy_pass http://backend-api:8080;
    proxy_set_header X-Request-Source "partner";
}

# ── 기본 차단 ─────────────────────────────
location / { return 403; }
```

### API 네이밍 패턴

```
내부 API (단일 정의)
    /{domain}/{resource}/{action}

외부 채널 (Nginx 라우터로 노출 제어)
    /api/v1/{domain}/{resource}         ← 고객용
    /webhook/v1/{provider}/{event}      ← 외부 시스템용
    /api/admin/v1/{domain}/{resource}   ← 플랫폼 어드민용
    /api/partner/v1/{domain}/{resource} ← 입점사 BO용

X-Request-Source 헤더
    api     → 고객 인증 검증
    webhook → PG사·배송사 서명 검증
    admin   → 운영자 권한 검증
    partner → 입점사 2FA + 세션 검증
```

---

## 12. MSA 전환 전략

### 단계별 전환 기준

| 단계 | 아키텍처 | 배포 | 조건 |
|------|----------|------|------|
| 1단계 | Modular Monolith | Docker Compose | 런칭 시점 |
| 2단계 | Hybrid MSA | Kubernetes | Pod 설계 완성 시 |
| 3단계 | Full MSA | Kubernetes | 서비스 안정화 후 |

### MSA 전환 우선순위

| 순서 | 도메인 | 분리 이유 |
|------|--------|---------|
| 1 | Payment | 결제 안정성·보안 독립 필요 |
| 2 | Notification | 발송량 증가 시 독립 스케일링 |
| 3 | Search | ES 인덱스 별도 관리 필요 시 |
| 4 | Settlement | 정산 배치 독립 실행 필요 시 |

### 전환 시 변경 최소화 설계

```
현재 (Monolith)
    모듈 간 PublicApi Interface 호출
    Outbox Consumer (인프로세스)
    복제 배치 → 동일 프로세스 내 직접 호출

전환 후 (MSA)
    PublicApi → REST API 호출로 교체 (Interface 유지)
    Outbox Consumer → Kafka Consumer로 교체
    복제 배치 → 외부 서비스 API 호출로 교체
    DB → 서비스별 독립 DB
```

### Docker Compose (1단계)

```yaml
services:
  backend-api:
    build: .
    ports:
      - "8080:8080"
    environment:
      - SPRING_PROFILES_ACTIVE=local
    profiles: [api]

  consumer:
    build: .
    environment:
      - SPRING_PROFILES_ACTIVE=local,consumer
    profiles: [consumer]

  batch:
    build: .
    environment:
      - SPRING_PROFILES_ACTIVE=local,batch
    profiles: [batch]

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    profiles: [frontend]

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    profiles: [nginx]

  prometheus:
    image: prom/prometheus
    profiles: [monitoring]

  grafana:
    image: grafana/grafana
    profiles: [monitoring]
```

---

*Confidential | 3TOP | Modular Monolith v1.0 | 2026.06.22*
