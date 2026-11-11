# 러닝 커머스 플랫폼 ERD 정의서

> 작성 주체: 3TOP 2본부
> 문서 버전: v1.0
> 작성일: 2026.06.22
> 상태: 초안 (Draft)

---

## 목차

1. [설계 원칙](#1-설계-원칙)
2. [Common 레이어](#2-common-레이어)
3. [Config 도메인](#3-config-도메인)
4. [Vendor 도메인](#4-vendor-도메인)
5. [Catalog 도메인](#5-catalog-도메인)
6. [Member 도메인](#6-member-도메인)
7. [Promotion 도메인](#7-promotion-도메인)
8. [Order 도메인](#8-order-도메인)
9. [Payment 도메인](#9-payment-도메인)
10. [Settlement 도메인](#10-settlement-도메인)
11. [Notification 도메인](#11-notification-도메인)
12. [Community 도메인](#12-community-도메인)
13. [Search 도메인](#13-search-도메인)
14. [Audit 도메인](#14-audit-도메인)
15. [복제 테이블 목록](#15-복제-테이블-목록)
16. [전체 테이블 목록](#16-전체-테이블-목록)

---

## 1. 설계 원칙

### 공통 원칙

- **물리적 DELETE 전면 금지**: 모든 삭제는 소프트 삭제(`is_deleted = true`)로 처리
- **모든 테이블 공통 컬럼**: `created_at`, `updated_at`, `is_deleted`, `deleted_at`, `deleted_by`
- **도메인별 테이블 Prefix**: 모듈 경계 명확화
- **스냅샷 저장**: 주문 시점 가격·수수료율 등 변경 가능한 값은 스냅샷 저장
- **복제 테이블**: Query 전용, 배치 동기화, Command는 PublicApi 호출

### 공통 컬럼

```sql
created_at      DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at      DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
is_deleted      BOOLEAN     NOT NULL DEFAULT FALSE,
deleted_at      DATETIME,
deleted_by      VARCHAR(50)
```

### 도메인별 테이블 Prefix

| 도메인 | Prefix |
|--------|--------|
| Common | `cmn_` |
| Config | `cfg_` |
| Vendor | `vnd_` |
| Catalog | `cat_` |
| Member | `mbr_` |
| Promotion | `prm_` |
| Order | `ord_` |
| Payment | `pay_` |
| Settlement | `stl_` |
| Notification | `ntf_` |
| Community | `cmt_` |
| Search | `sch_` |
| Audit | `adt_` |

---

## 2. Common 레이어

### cmn_outbox_event

```sql
cmn_outbox_event (
    id              BIGINT          PK AUTO_INCREMENT,
    trace_id        VARCHAR(50),
    aggregate_id    VARCHAR(100)    NOT NULL,
    aggregate_type  VARCHAR(50)     NOT NULL,
    event_type      VARCHAR(100)    NOT NULL,
    payload         JSON            NOT NULL,
    status          VARCHAR(20)     NOT NULL DEFAULT 'PENDING',
    -- PENDING·PROCESSING·PROCESSED·FAILED
    retry_count     INT             NOT NULL DEFAULT 0,
    error_message   VARCHAR(500),
    created_at      DATETIME        NOT NULL,
    processed_at    DATETIME,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### cmn_sync_history

```sql
cmn_sync_history (
    id              BIGINT          PK AUTO_INCREMENT,
    sync_type       VARCHAR(50)     NOT NULL,
    -- CODE·CATEGORY·FEE_RATE·DELIVERY_COMPANY 등
    target_module   VARCHAR(50)     NOT NULL,
    synced_count    INT             NOT NULL DEFAULT 0,
    status          VARCHAR(20)     NOT NULL,
    -- SUCCESS·FAILED
    started_at      DATETIME        NOT NULL,
    finished_at     DATETIME,
    error_message   VARCHAR(500),
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### cmn_batch_job

```sql
cmn_batch_job (
    id              BIGINT          PK AUTO_INCREMENT,
    job_code        VARCHAR(100)    NOT NULL UNIQUE,
    job_name        VARCHAR(200)    NOT NULL,
    domain          VARCHAR(50)     NOT NULL,
    schedule        VARCHAR(100),
    -- Cron 표현식
    description     VARCHAR(300),
    status          VARCHAR(20)     NOT NULL DEFAULT 'ACTIVE',
    timeout_minutes INT             NOT NULL DEFAULT 30,
    retry_count     INT             NOT NULL DEFAULT 0,
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### cmn_batch_execution

```sql
cmn_batch_execution (
    id              BIGINT          PK AUTO_INCREMENT,
    job_id          BIGINT          NOT NULL FK → cmn_batch_job.id,
    job_code        VARCHAR(100)    NOT NULL,
    status          VARCHAR(20)     NOT NULL DEFAULT 'RUNNING',
    -- RUNNING·SUCCESS·FAILED·RETRYING·CANCELLED
    trigger_type    VARCHAR(20)     NOT NULL DEFAULT 'SCHEDULE',
    -- SCHEDULE·MANUAL·RETRY
    triggered_by    VARCHAR(100),
    started_at      DATETIME        NOT NULL,
    finished_at     DATETIME,
    duration_ms     BIGINT,
    total_count     INT             DEFAULT 0,
    success_count   INT             DEFAULT 0,
    fail_count      INT             DEFAULT 0,
    retry_attempt   INT             NOT NULL DEFAULT 0,
    error_message   VARCHAR(1000),
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### cmn_batch_execution_log

```sql
cmn_batch_execution_log (
    id              BIGINT          PK AUTO_INCREMENT,
    execution_id    BIGINT          NOT NULL FK → cmn_batch_execution.id,
    log_level       VARCHAR(10)     NOT NULL,
    -- INFO·WARN·ERROR
    message         VARCHAR(2000)   NOT NULL,
    item_id         VARCHAR(100),
    item_type       VARCHAR(50),
    created_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

---

## 3. Config 도메인

### cfg_operator

```sql
cfg_operator (
    id              BIGINT          PK AUTO_INCREMENT,
    email           VARCHAR(100)    NOT NULL UNIQUE,
    name            VARCHAR(50)     NOT NULL,
    password        VARCHAR(255)    NOT NULL,
    role_id         BIGINT          NOT NULL FK → cfg_role.id,
    status          VARCHAR(20)     NOT NULL DEFAULT 'ACTIVE',
    -- ACTIVE·INACTIVE·LOCKED
    last_login_at   DATETIME,
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### cfg_role

```sql
cfg_role (
    id              BIGINT          PK AUTO_INCREMENT,
    role_code       VARCHAR(50)     NOT NULL UNIQUE,
    -- SUPER_ADMIN·MD·CS·SETTLEMENT·VENDOR_MANAGER
    role_name       VARCHAR(100)    NOT NULL,
    description     VARCHAR(200),
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### cfg_permission

```sql
cfg_permission (
    id              BIGINT          PK AUTO_INCREMENT,
    role_id         BIGINT          NOT NULL FK → cfg_role.id,
    program_id      BIGINT          NOT NULL FK → cfg_program.id,
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50),
    UNIQUE KEY uk_role_program (role_id, program_id)
)
```

### cfg_program

```sql
cfg_program (
    id              BIGINT          PK AUTO_INCREMENT,
    program_code    VARCHAR(100)    NOT NULL UNIQUE,
    program_name    VARCHAR(200)    NOT NULL,
    http_method     VARCHAR(10)     NOT NULL,
    -- GET·POST·PUT·PATCH·DELETE
    api_url         VARCHAR(500)    NOT NULL,
    channel         VARCHAR(20)     NOT NULL DEFAULT 'API',
    -- API·WEBHOOK·ADMIN
    description     VARCHAR(200),
    status          VARCHAR(20)     NOT NULL DEFAULT 'ACTIVE',
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50),
    UNIQUE KEY uk_method_url (http_method, api_url)
)
```

### cfg_common_code

```sql
cfg_common_code (
    id              BIGINT          PK AUTO_INCREMENT,
    group_code      VARCHAR(50)     NOT NULL,
    code            VARCHAR(50)     NOT NULL,
    code_name       VARCHAR(100)    NOT NULL,
    sort_order      INT             NOT NULL DEFAULT 0,
    status          VARCHAR(20)     NOT NULL DEFAULT 'ACTIVE',
    description     VARCHAR(200),
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50),
    UNIQUE KEY uk_group_code (group_code, code)
)
```

### cfg_delivery_company

```sql
cfg_delivery_company (
    id              BIGINT          PK AUTO_INCREMENT,
    company_code    VARCHAR(50)     NOT NULL UNIQUE,
    company_name    VARCHAR(100)    NOT NULL,
    api_endpoint    VARCHAR(500),
    api_key         VARCHAR(500),
    -- 암호화 저장
    tracking_url    VARCHAR(500),
    api_connected   BOOLEAN         NOT NULL DEFAULT FALSE,
    status          VARCHAR(20)     NOT NULL DEFAULT 'ACTIVE',
    sort_order      INT             NOT NULL DEFAULT 0,
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### cfg_notice

```sql
cfg_notice (
    id              BIGINT          PK AUTO_INCREMENT,
    target_type     VARCHAR(20)     NOT NULL,
    -- CUSTOMER·VENDOR·ALL
    title           VARCHAR(200)    NOT NULL,
    content         TEXT            NOT NULL,
    is_popup        BOOLEAN         NOT NULL DEFAULT FALSE,
    is_important    BOOLEAN         NOT NULL DEFAULT FALSE,
    display_from    DATETIME,
    display_to      DATETIME,
    created_by      BIGINT          NOT NULL FK → cfg_operator.id,
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### cfg_terms

```sql
cfg_terms (
    id              BIGINT          PK AUTO_INCREMENT,
    terms_type      VARCHAR(50)     NOT NULL,
    -- SERVICE·PRIVACY·MARKETING
    version         VARCHAR(20)     NOT NULL,
    content         TEXT            NOT NULL,
    effective_at    DATETIME        NOT NULL,
    created_by      BIGINT          NOT NULL FK → cfg_operator.id,
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50),
    UNIQUE KEY uk_type_version (terms_type, version)
)
```

### cfg_banner

```sql
cfg_banner (
    id              BIGINT          PK AUTO_INCREMENT,
    position_code   VARCHAR(50)     NOT NULL,
    -- MAIN_TOP·MAIN_MIDDLE·CATEGORY_TOP 등
    title           VARCHAR(200)    NOT NULL,
    image_url       VARCHAR(500)    NOT NULL,
    link_url        VARCHAR(500),
    sort_order      INT             NOT NULL DEFAULT 0,
    display_from    DATETIME,
    display_to      DATETIME,
    created_by      BIGINT          NOT NULL FK → cfg_operator.id,
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

---

## 4. Vendor 도메인

### vnd_vendor_application

```sql
vnd_vendor_application (
    id                  BIGINT          PK AUTO_INCREMENT,
    business_name       VARCHAR(200)    NOT NULL,
    business_no         VARCHAR(20)     NOT NULL,
    representative      VARCHAR(100)    NOT NULL,
    business_type       VARCHAR(20)     NOT NULL,
    -- CORPORATION·INDIVIDUAL·BRAND_DIRECT
    category_id         BIGINT          NOT NULL FK → cat_standard_category.id,
    contact_email       VARCHAR(100)    NOT NULL,
    contact_phone       VARCHAR(20)     NOT NULL,
    status              VARCHAR(30)     NOT NULL DEFAULT 'APPLIED',
    -- APPLIED·REVIEWING·CONTRACT·APPROVED·REJECTED
    reject_reason       VARCHAR(500),
    reject_count        INT             NOT NULL DEFAULT 0,
    reviewed_by         BIGINT          FK → cfg_operator.id,
    reviewed_at         DATETIME,
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

### vnd_vendor

```sql
vnd_vendor (
    id                  BIGINT          PK AUTO_INCREMENT,
    application_id      BIGINT          NOT NULL UNIQUE FK → vnd_vendor_application.id,
    business_name       VARCHAR(200)    NOT NULL,
    business_no         VARCHAR(20)     NOT NULL UNIQUE,
    representative      VARCHAR(100)    NOT NULL,
    business_type       VARCHAR(20)     NOT NULL,
    vendor_type         VARCHAR(20)     NOT NULL DEFAULT 'VENDOR',
    -- VENDOR·DIRECT
    status              VARCHAR(20)     NOT NULL DEFAULT 'ACTIVE',
    -- ACTIVE·WARNING·SUSPENDED·TERMINATED
    contact_email       VARCHAR(100)    NOT NULL,
    contact_phone       VARCHAR(20)     NOT NULL,
    grade_code          VARCHAR(20)     NOT NULL DEFAULT 'NEW',
    -- NEW·RUNNER·PACER·ELITE
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

### vnd_vendor_contract

```sql
vnd_vendor_contract (
    id                  BIGINT          PK AUTO_INCREMENT,
    vendor_id           BIGINT          NOT NULL FK → vnd_vendor.id,
    contract_no         VARCHAR(100)    NOT NULL UNIQUE,
    is_exclusive        BOOLEAN         NOT NULL DEFAULT FALSE,
    auto_renewal        BOOLEAN         NOT NULL DEFAULT TRUE,
    start_date          DATE            NOT NULL,
    end_date            DATE            NOT NULL,
    status              VARCHAR(20)     NOT NULL DEFAULT 'ACTIVE',
    -- ACTIVE·EXPIRED·TERMINATED
    signed_at           DATETIME,
    terminated_at       DATETIME,
    terminate_reason    VARCHAR(500),
    created_by          BIGINT          FK → cfg_operator.id,
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

### vnd_vendor_fee_rate

```sql
vnd_vendor_fee_rate (
    id                  BIGINT          PK AUTO_INCREMENT,
    vendor_id           BIGINT          NOT NULL FK → vnd_vendor.id,
    category_id         BIGINT          NOT NULL FK → cat_standard_category.id,
    base_fee_rate       DECIMAL(5,2)    NOT NULL,
    grade_discount_rate DECIMAL(5,2)    NOT NULL DEFAULT 0.00,
    final_fee_rate      DECIMAL(5,2)    NOT NULL,
    effective_from      DATE            NOT NULL,
    effective_to        DATE,
    -- NULL = 현재 적용 중
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50),
    UNIQUE KEY uk_vendor_category_date (vendor_id, category_id, effective_from)
)
```

### vnd_vendor_grade

```sql
vnd_vendor_grade (
    id                  BIGINT          PK AUTO_INCREMENT,
    vendor_id           BIGINT          NOT NULL FK → vnd_vendor.id,
    grade_code          VARCHAR(20)     NOT NULL,
    score               DECIMAL(5,2)    NOT NULL,
    monthly_amount      DECIMAL(15,2)   NOT NULL,
    fulfillment_rate    DECIMAL(5,2)    NOT NULL,
    claim_rate          DECIMAL(5,2)    NOT NULL,
    review_rating       DECIMAL(3,2)    NOT NULL,
    calculated_at       DATE            NOT NULL,
    applied_at          DATE,
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

### vnd_vendor_account

```sql
vnd_vendor_account (
    id                  BIGINT          PK AUTO_INCREMENT,
    vendor_id           BIGINT          NOT NULL FK → vnd_vendor.id,
    bank_code           VARCHAR(10)     NOT NULL,
    account_no          VARCHAR(50)     NOT NULL,
    -- 암호화 저장
    account_holder      VARCHAR(100)    NOT NULL,
    is_primary          BOOLEAN         NOT NULL DEFAULT TRUE,
    verified_at         DATETIME,
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

### vnd_vendor_delivery

```sql
vnd_vendor_delivery (
    id                      BIGINT          PK AUTO_INCREMENT,
    vendor_id               BIGINT          NOT NULL UNIQUE FK → vnd_vendor.id,
    delivery_company_id     BIGINT          FK → cfg_delivery_company.id,
    -- NULL = 미선택 (수동)
    free_shipping_min       DECIMAL(12,2)   NOT NULL DEFAULT 50000.00,
    base_shipping_fee       DECIMAL(8,2)    NOT NULL DEFAULT 3000.00,
    created_at              DATETIME        NOT NULL,
    updated_at              DATETIME        NOT NULL,
    is_deleted              BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at              DATETIME,
    deleted_by              VARCHAR(50)
)
```

### vnd_vendor_penalty

```sql
vnd_vendor_penalty (
    id                  BIGINT          PK AUTO_INCREMENT,
    vendor_id           BIGINT          NOT NULL FK → vnd_vendor.id,
    penalty_type        VARCHAR(50)     NOT NULL,
    amount              DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    reason              VARCHAR(500)    NOT NULL,
    penalty_date        DATE            NOT NULL,
    settlement_id       BIGINT,
    created_by          BIGINT          FK → cfg_operator.id,
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

### vnd_vendor_session

```sql
vnd_vendor_session (
    id                  BIGINT          PK AUTO_INCREMENT,
    vendor_id           BIGINT          NOT NULL FK → vnd_vendor.id,
    session_token       VARCHAR(500)    NOT NULL UNIQUE,
    -- JWT Refresh Token
    device_info         VARCHAR(200),
    ip_address          VARCHAR(50),
    login_at            DATETIME        NOT NULL,
    expires_at          DATETIME        NOT NULL,
    -- 세션 유지 3시간
    last_accessed_at    DATETIME,
    is_active           BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

> 동시 세션 최대 2개. 초과 시 가장 오래된 세션 만료 처리.

---

## 5. Catalog 도메인

### cat_standard_category

```sql
cat_standard_category (
    id              BIGINT          PK AUTO_INCREMENT,
    parent_id       BIGINT          FK → cat_standard_category.id,
    -- NULL = 최상위. 현재 항상 NULL (1depth 제한)
    category_code   VARCHAR(50)     NOT NULL UNIQUE,
    category_name   VARCHAR(100)    NOT NULL,
    depth           INT             NOT NULL DEFAULT 1,
    base_fee_rate   DECIMAL(5,2),
    sort_order      INT             NOT NULL DEFAULT 0,
    status          VARCHAR(20)     NOT NULL DEFAULT 'ACTIVE',
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### cat_display_category

```sql
cat_display_category (
    id              BIGINT          PK AUTO_INCREMENT,
    parent_id       BIGINT          FK → cat_display_category.id,
    category_code   VARCHAR(50)     NOT NULL UNIQUE,
    category_name   VARCHAR(100)    NOT NULL,
    depth           INT             NOT NULL DEFAULT 1,
    description     VARCHAR(300),
    image_url       VARCHAR(500),
    sort_order      INT             NOT NULL DEFAULT 0,
    status          VARCHAR(20)     NOT NULL DEFAULT 'ACTIVE',
    display_from    DATETIME,
    display_to      DATETIME,
    created_by      BIGINT          FK → cfg_operator.id,
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### cat_product_display_category

```sql
cat_product_display_category (
    id                  BIGINT          PK AUTO_INCREMENT,
    product_id          BIGINT          NOT NULL FK → cat_product.id,
    display_category_id BIGINT          NOT NULL FK → cat_display_category.id,
    sort_order          INT             NOT NULL DEFAULT 0,
    created_by          BIGINT          FK → cfg_operator.id,
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50),
    UNIQUE KEY uk_product_display (product_id, display_category_id)
)
```

### cat_standard_display_category_mapping

```sql
cat_standard_display_category_mapping (
    id                      BIGINT          PK AUTO_INCREMENT,
    standard_category_id    BIGINT          NOT NULL FK → cat_standard_category.id,
    display_category_id     BIGINT          NOT NULL FK → cat_display_category.id,
    is_default              BOOLEAN         NOT NULL DEFAULT FALSE,
    -- TRUE: 상품 등록 시 자동 선택
    -- FALSE: 선택 가능 후보만 제공
    sort_order              INT             NOT NULL DEFAULT 0,
    created_by              BIGINT          FK → cfg_operator.id,
    created_at              DATETIME        NOT NULL,
    updated_at              DATETIME        NOT NULL,
    is_deleted              BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at              DATETIME,
    deleted_by              VARCHAR(50),
    UNIQUE KEY uk_std_display (standard_category_id, display_category_id)
)
```

### cat_brand

```sql
cat_brand (
    id              BIGINT          PK AUTO_INCREMENT,
    brand_code      VARCHAR(50)     NOT NULL UNIQUE,
    brand_name      VARCHAR(100)    NOT NULL,
    brand_name_en   VARCHAR(100),
    logo_url        VARCHAR(500),
    is_certified    BOOLEAN         NOT NULL DEFAULT FALSE,
    status          VARCHAR(20)     NOT NULL DEFAULT 'ACTIVE',
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### cat_product

```sql
cat_product (
    id                      BIGINT          PK AUTO_INCREMENT,
    vendor_id               BIGINT          NOT NULL FK → vnd_vendor.id,
    standard_category_id    BIGINT          NOT NULL FK → cat_standard_category.id,
    brand_id                BIGINT          FK → cat_brand.id,
    product_code            VARCHAR(100)    NOT NULL UNIQUE,
    product_name            VARCHAR(300)    NOT NULL,
    product_name_en         VARCHAR(300),
    summary                 VARCHAR(500),
    -- 짧은 한 줄 소개 (목록·검색 노출)
    description             TEXT,
    -- HTML 기본 설명 (단순 입점사용)
    status                  VARCHAR(30)     NOT NULL DEFAULT 'DRAFT',
    -- DRAFT·REVIEW_REQUESTED·UNDER_REVIEW·ON_SALE·SOLD_OUT·DISCONTINUED·REJECTED
    vendor_type             VARCHAR(20)     NOT NULL DEFAULT 'VENDOR',
    -- VENDOR·DIRECT
    release_date            DATE,
    review_count            INT             NOT NULL DEFAULT 0,
    avg_rating              DECIMAL(3,2)    NOT NULL DEFAULT 0.00,
    reject_reason           VARCHAR(500),
    reject_count            INT             NOT NULL DEFAULT 0,
    reviewed_by             BIGINT          FK → cfg_operator.id,
    reviewed_at             DATETIME,
    total_available_quantity INT            NOT NULL DEFAULT 0,
    -- 전체 SKU available_quantity 합계 (비정규화)
    -- SKU 재고 변경 시 함께 업데이트
    created_at              DATETIME        NOT NULL,
    updated_at              DATETIME        NOT NULL,
    is_deleted              BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at              DATETIME,
    deleted_by              VARCHAR(50)
)
```

### cat_product_image

```sql
cat_product_image (
    id              BIGINT          PK AUTO_INCREMENT,
    product_id      BIGINT          NOT NULL FK → cat_product.id,
    image_url       VARCHAR(500)    NOT NULL,
    image_type      VARCHAR(20)     NOT NULL DEFAULT 'MAIN',
    -- MAIN·DETAIL·THUMBNAIL
    sort_order      INT             NOT NULL DEFAULT 0,
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### cat_product_attribute

```sql
cat_product_attribute (
    id              BIGINT          PK AUTO_INCREMENT,
    product_id      BIGINT          NOT NULL FK → cat_product.id,
    attribute_code  VARCHAR(100)    NOT NULL,
    attribute_value VARCHAR(300)    NOT NULL,
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50),
    UNIQUE KEY uk_product_attribute (product_id, attribute_code)
)
```

### cat_sku

```sql
cat_sku (
    id              BIGINT          PK AUTO_INCREMENT,
    product_id      BIGINT          NOT NULL FK → cat_product.id,
    sku_code        VARCHAR(100)    NOT NULL UNIQUE,
    option1_type    VARCHAR(50),
    option1_value   VARCHAR(100),
    option2_type    VARCHAR(50),
    option2_value   VARCHAR(100),
    status          VARCHAR(20)     NOT NULL DEFAULT 'ON_SALE',
    -- ON_SALE·SOLD_OUT·DISCONTINUED
    -- stock_quantity 제거 → cat_sku_stock으로 분리
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### cat_sku_stock

```sql
cat_sku_stock (
    id                  BIGINT      PK AUTO_INCREMENT,
    sku_id              BIGINT      NOT NULL UNIQUE FK → cat_sku.id,
    stock_quantity      INT         NOT NULL DEFAULT 0,
    -- 총 재고 수량
    reserved_quantity   INT         NOT NULL DEFAULT 0,
    -- 선점 수량 (TEMP_ORDER 30분)
    available_quantity  INT         NOT NULL DEFAULT 0,
    -- 실제 주문 가능 수량 = stock - reserved
    created_at          DATETIME    NOT NULL,
    updated_at          DATETIME    NOT NULL,
    is_deleted          BOOLEAN     NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

### cat_sku_stock_history

```sql
cat_sku_stock_history (
    id                  BIGINT          PK AUTO_INCREMENT,
    sku_id              BIGINT          NOT NULL FK → cat_sku.id,
    change_source       VARCHAR(20)     NOT NULL DEFAULT 'ORDER',
    -- CATALOG: 초기등록·임의조정
    -- ORDER: 선점·차감·복구
    change_type         VARCHAR(30)     NOT NULL,
    -- [CATALOG 출처]
    -- REGISTER        : 재고 초기 등록 (입점사)
    -- ADMIN_ADJUST    : 운영자 수동 조정
    -- VENDOR_ADJUST   : 입점사 수동 조정
    -- [ORDER 출처]
    -- ORDER_RESERVE   : 주문 선점
    -- ORDER_CONFIRM   : 결제 완료 차감
    -- CANCEL_RESTORE  : 취소 복구 (자동)
    -- RETURN_RESTORE  : 반품 복구 (수작업)
    change_quantity     INT             NOT NULL,
    -- 양수: 증가 / 음수: 감소
    before_quantity     INT             NOT NULL,
    after_quantity      INT             NOT NULL,
    ref_id              BIGINT,
    -- 참조 ID (order_id·claim_id 등)
    ref_type            VARCHAR(30),
    -- ORDER·CLAIM·ADMIN·VENDOR
    actor_type          VARCHAR(20)     NOT NULL DEFAULT 'SYSTEM',
    -- SYSTEM·OPERATOR·VENDOR
    actor_id            BIGINT,
    reason              VARCHAR(200),
    trace_id            VARCHAR(50),
    created_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

### cat_product_price

```sql
cat_product_price (
    id              BIGINT          PK AUTO_INCREMENT,
    product_id      BIGINT          NOT NULL FK → cat_product.id,
    price_original  DECIMAL(12,2)   NOT NULL,
    price_sale      DECIMAL(12,2)   NOT NULL,
    price_supply    DECIMAL(12,2)   NOT NULL,
    effective_from  DATETIME        NOT NULL,
    effective_to    DATETIME,
    changed_by      BIGINT          FK → cfg_operator.id,
    change_reason   VARCHAR(200),
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### cat_product_exposure

```sql
cat_product_exposure (
    id              BIGINT          PK AUTO_INCREMENT,
    product_id      BIGINT          NOT NULL UNIQUE FK → cat_product.id,
    md_override     INT,
    ai_score        DECIMAL(8,4),
    -- 1단계 NULL
    is_recommended  BOOLEAN         NOT NULL DEFAULT FALSE,
    is_new          BOOLEAN         NOT NULL DEFAULT FALSE,
    new_until       DATE,
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### cat_product_tag

```sql
cat_product_tag (
    id              BIGINT          PK AUTO_INCREMENT,
    product_id      BIGINT          NOT NULL FK → cat_product.id,
    tag             VARCHAR(100)    NOT NULL,
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50),
    UNIQUE KEY uk_product_tag (product_id, tag)
)
```

### cat_product_detail_type

```sql
cat_product_detail_type (
    id                  BIGINT          PK AUTO_INCREMENT,
    type_code           VARCHAR(50)     NOT NULL UNIQUE,
    -- RUNNING_SHOE·SUPPLEMENT·WEARABLE·APPAREL·GEAR·DEFAULT
    type_name           VARCHAR(100)    NOT NULL,
    description         VARCHAR(300),
    apply_target        VARCHAR(20)     NOT NULL DEFAULT 'CATEGORY',
    -- CATEGORY·BRAND·PRODUCT
    block_schema        JSON            NOT NULL,
    -- 허용 블록 타입·순서·필수 여부·최대 수량 정의
    status              VARCHAR(20)     NOT NULL DEFAULT 'ACTIVE',
    created_by          BIGINT          FK → cfg_operator.id,
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

### cat_product_detail_type_mapping

```sql
cat_product_detail_type_mapping (
    id                  BIGINT          PK AUTO_INCREMENT,
    detail_type_id      BIGINT          NOT NULL FK → cat_product_detail_type.id,
    apply_target        VARCHAR(20)     NOT NULL,
    -- CATEGORY·BRAND·DEFAULT
    target_id           BIGINT,
    -- CATEGORY → cat_standard_category.id
    -- BRAND    → cat_brand.id
    -- DEFAULT  → NULL
    priority            INT             NOT NULL DEFAULT 0,
    -- 우선순위: BRAND(2) > CATEGORY(1) > DEFAULT(0)
    created_by          BIGINT          FK → cfg_operator.id,
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50),
    UNIQUE KEY uk_target (apply_target, target_id)
)
```

### cat_product_detail

```sql
cat_product_detail (
    id                  BIGINT          PK AUTO_INCREMENT,
    product_id          BIGINT          NOT NULL UNIQUE FK → cat_product.id,
    detail_type_id      BIGINT          NOT NULL FK → cat_product_detail_type.id,
    -- 적용된 타입 (BRAND > CATEGORY > DEFAULT 우선순위)
    blocks              JSON            NOT NULL DEFAULT '[]',
    -- 타입 스키마에 맞는 콘텐츠 블록 배열
    -- [
    --   { "type": "IMAGE",      "url": "...", "alt": "..." },
    --   { "type": "TEXT",       "content": "..." },
    --   { "type": "SPEC_TABLE", "fields": {...} },
    --   { "type": "SIZE_CHART", "data": {...} }
    -- ]
    block_version       INT             NOT NULL DEFAULT 1,
    -- 블록 스키마 버전
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

### cat_display_template

```sql
cat_display_template (
    id              BIGINT          PK AUTO_INCREMENT,
    template_code   VARCHAR(50)     NOT NULL UNIQUE,
    template_name   VARCHAR(100)    NOT NULL,
    template_type   VARCHAR(20)     NOT NULL,
    -- HOME·CATEGORY·EXHIBITION·EVENT (2026-07-06 크로스체크: HOME 누락 보완, 프로토타입 코드와 일치)
    description     VARCHAR(300),
    thumbnail_url   VARCHAR(500),
    status          VARCHAR(20)     NOT NULL DEFAULT 'ACTIVE',
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### cat_display_area

```sql
cat_display_area (
    id              BIGINT          PK AUTO_INCREMENT,
    template_id     BIGINT          NOT NULL FK → cat_display_template.id,
    area_code       VARCHAR(50)     NOT NULL,
    area_name       VARCHAR(100)    NOT NULL,
    area_type       VARCHAR(30)     NOT NULL,
    -- FIXED·FLEXIBLE
    sort_order      INT             NOT NULL DEFAULT 0,
    description     VARCHAR(200),
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50),
    UNIQUE KEY uk_template_area (template_id, area_code)
)
```

### cat_display_content

```sql
cat_display_content (
    id              BIGINT          PK AUTO_INCREMENT,
    area_id         BIGINT          NOT NULL FK → cat_display_area.id,
    content_code    VARCHAR(50)     NOT NULL,
    content_name    VARCHAR(100)    NOT NULL,
    content_type    VARCHAR(30)     NOT NULL,
    -- BANNER·PRODUCT_GRID·PRODUCT_LIST·TEXT·IMAGE·VIDEO
    sort_order      INT             NOT NULL DEFAULT 0,
    is_required     BOOLEAN         NOT NULL DEFAULT FALSE,
    max_item_count  INT,
    column_count    INT             DEFAULT 2,
    description     VARCHAR(200),
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50),
    UNIQUE KEY uk_area_content (area_id, content_code)
)
```

### cat_display_page

```sql
cat_display_page (
    id              BIGINT          PK AUTO_INCREMENT,
    template_id     BIGINT          NOT NULL FK → cat_display_template.id,
    page_type       VARCHAR(20)     NOT NULL,
    -- CATEGORY·EXHIBITION·EVENT
    ref_id          BIGINT,
    page_name       VARCHAR(200)    NOT NULL,
    page_url        VARCHAR(300)    NOT NULL UNIQUE,
    status          VARCHAR(20)     NOT NULL DEFAULT 'DRAFT',
    -- DRAFT·DRAFT_EDIT·PUBLISHED·SCHEDULED·RESERVED·CLOSED·CANCELLED
    -- (2026-07-06 크로스체크: 정책서 3.12 전시 페이지 상태 정책 기준 7종으로 정정, 기존 3종 코멘트는 축약 오류)
    -- ⚠ 프로토타입 Mock(mockData.ts)은 PUBLISHED/SCHEDULED/DRAFT/DEPRECATED 4종으로 단순화되어 있어
    --   이 컬럼과 구조가 다름(Mock은 단일 행 status, 본 ERD는 cat_display_page_schedule로 별도 행 관리).
    --   본개발 전환 시 반드시 재확인. 상세: docs/x. 하네스/샘플/09-DPL 참고
    display_from    DATETIME,
    display_to      DATETIME,
    created_by      BIGINT          FK → cfg_operator.id,
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### cat_display_page_area

```sql
cat_display_page_area (
    id              BIGINT          PK AUTO_INCREMENT,
    page_id         BIGINT          NOT NULL FK → cat_display_page.id,
    area_id         BIGINT          NOT NULL FK → cat_display_area.id,
    title           VARCHAR(200),
    subtitle        VARCHAR(300),
    more_link_url   VARCHAR(300),
    is_visible      BOOLEAN         NOT NULL DEFAULT TRUE,
    sort_order      INT             NOT NULL DEFAULT 0,
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50),
    UNIQUE KEY uk_page_area (page_id, area_id)
)
```

### cat_display_page_content_item

```sql
cat_display_page_content_item (
    id              BIGINT          PK AUTO_INCREMENT,
    page_area_id    BIGINT          NOT NULL FK → cat_display_page_area.id,
    content_id      BIGINT          NOT NULL FK → cat_display_content.id,
    item_type       VARCHAR(20)     NOT NULL,
    -- PRODUCT·BANNER·CATEGORY·IMAGE·TEXT
    item_ref_id     BIGINT,
    item_url        VARCHAR(500),
    item_text       VARCHAR(1000),
    sort_order      INT             NOT NULL DEFAULT 0,
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### cat_display_section_type

> 2026-07-06 신규 추가. decision_log(2026-06-30 "전시 도메인 4단계 계층 구조 확정")에서 이미
> 결정된 구조(필드 정의 → 섹션 정의 → 템플릿 정의 → 페이지 생성)를 ERD에 반영. 어드민이 섹션종류를
> 직접 정의하는 메타 스키마이므로 cat_display_content(콘텐츠 유형 고정 enum)와는 다른 개념.

```sql
cat_display_section_type (
    id              BIGINT          PK AUTO_INCREMENT,
    section_code    VARCHAR(50)     NOT NULL UNIQUE,
    section_name    VARCHAR(100)    NOT NULL,
    type            VARCHAR(30)     NOT NULL,
    -- BANNER·PRODUCT_GRID·PRODUCT_CAROUSEL·TEXT·IMAGE_LINK·COUNTDOWN·COUPON_BAND·DIVIDER
    description     VARCHAR(300),
    preview_color   VARCHAR(20),
    item_count      INT             NOT NULL DEFAULT 1,
    layout_type     VARCHAR(20)     NOT NULL DEFAULT 'LAYERED',
    -- LAYERED·CAROUSEL·TILE
    sort_order      INT             NOT NULL DEFAULT 0,
    status          VARCHAR(20)     NOT NULL DEFAULT 'ACTIVE',
    -- ACTIVE·INACTIVE·DEPRECATED (물리 삭제 금지, 삭제는 DEPRECATED 전환)
    created_by      BIGINT          FK → cfg_operator.id,
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### cat_display_section_field

```sql
cat_display_section_field (
    id                  BIGINT          PK AUTO_INCREMENT,
    section_type_id     BIGINT          NOT NULL FK → cat_display_section_type.id,
    field_key           VARCHAR(50)     NOT NULL,
    -- 등록 후 수정 불가 (immutable)
    label               VARCHAR(100)    NOT NULL,
    field_type          VARCHAR(20)     NOT NULL,
    -- IMAGE·PRODUCT·TEXT·LINK·COLOR·NUMBER·DATETIME·LAYOUT_SELECT·IMAGE_ARRAY·PRODUCT_ARRAY·TEXT_ARRAY
    is_required         BOOLEAN         NOT NULL DEFAULT FALSE,
    default_value       VARCHAR(500),
    placeholder         VARCHAR(200),
    -- TEXT 타입 필드만 사용
    sort_order          INT             NOT NULL DEFAULT 0,
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50),
    UNIQUE KEY uk_section_field (section_type_id, field_key)
)
```

### cat_display_page_schedule

```sql
cat_display_page_schedule (
    id                      BIGINT          PK AUTO_INCREMENT,
    page_id                 BIGINT          NOT NULL FK → cat_display_page.id,
    -- 원본 페이지 (현재 운영 중)
    scheduled_page_id       BIGINT          NOT NULL FK → cat_display_page.id,
    -- 예약 페이지 (전환 대상)
    scheduled_at            DATETIME        NOT NULL,
    -- 전환 예약 시각
    status                  VARCHAR(20)     NOT NULL DEFAULT 'PENDING',
    -- PENDING: 예약 대기
    -- APPLIED: 전환 완료
    -- CANCELLED: 취소
    applied_at              DATETIME,
    cancelled_at            DATETIME,
    cancel_reason           VARCHAR(200),
    created_by              BIGINT          FK → cfg_operator.id,
    created_at              DATETIME        NOT NULL,
    updated_at              DATETIME        NOT NULL,
    is_deleted              BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at              DATETIME,
    deleted_by              VARCHAR(50)
    -- 조건부 유니크 인덱스 (PostgreSQL)
    -- CREATE UNIQUE INDEX uk_page_pending
    -- ON cat_display_page_schedule (page_id)
    -- WHERE status = 'PENDING'
    -- → 페이지당 PENDING 예약 최대 1개 보장
)
```

---

## 6. Member 도메인

### mbr_member

```sql
mbr_member (
    id                  BIGINT          PK AUTO_INCREMENT,
    member_no           VARCHAR(50)     NOT NULL UNIQUE,
    email               VARCHAR(100)    NOT NULL UNIQUE,
    password            VARCHAR(255),
    name                VARCHAR(50)     NOT NULL,
    phone               VARCHAR(20)     NOT NULL UNIQUE,
    -- 암호화 저장
    birth_date          DATE,
    gender              VARCHAR(10),
    -- MALE·FEMALE·NONE
    join_type           VARCHAR(20)     NOT NULL DEFAULT 'EMAIL',
    -- EMAIL·NAVER·APPLE (1단계 런칭 기준)
    sns_provider        VARCHAR(20),
    sns_id              VARCHAR(200),
    -- 암호화 저장
    grade_code          VARCHAR(20)     NOT NULL DEFAULT 'NEW',
    activity_score      INT             NOT NULL DEFAULT 0,
    purchase_amount     DECIMAL(15,2)   NOT NULL DEFAULT 0.00,
    point_balance       INT             NOT NULL DEFAULT 0,
    status              VARCHAR(20)     NOT NULL DEFAULT 'ACTIVE',
    -- ACTIVE·INACTIVE·WITHDRAWN
    last_login_at       DATETIME,
    withdrawn_at        DATETIME,
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

### mbr_member_running_profile

```sql
mbr_member_running_profile (
    id                  BIGINT          PK AUTO_INCREMENT,
    member_id           BIGINT          NOT NULL UNIQUE FK → mbr_member.id,
    running_career      INT,
    weekly_distance     DECIMAL(6,2),
    shoe_size           INT,
    preferred_brand_ids JSON,
    wearable_connected  BOOLEAN         NOT NULL DEFAULT FALSE,
    wearable_type       VARCHAR(50),
    -- APPLE_HEALTH·GARMIN·STRAVA
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

### mbr_member_grade

```sql
mbr_member_grade (
    id              BIGINT          PK AUTO_INCREMENT,
    member_id       BIGINT          NOT NULL FK → mbr_member.id,
    grade_code      VARCHAR(20)     NOT NULL,
    purchase_amount DECIMAL(15,2)   NOT NULL,
    activity_score  INT             NOT NULL,
    calculated_at   DATE            NOT NULL,
    applied_at      DATE,
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### mbr_point

```sql
mbr_point (
    id              BIGINT          PK AUTO_INCREMENT,
    member_id       BIGINT          NOT NULL FK → mbr_member.id,
    point_type      VARCHAR(20)     NOT NULL,
    -- EARN·USE·RESTORE·EXPIRE
    amount          INT             NOT NULL,
    balance_after   INT             NOT NULL,
    status          VARCHAR(20)     NOT NULL DEFAULT 'COMPLETED',
    -- COMPLETED·FAILED·PENDING
    reason          VARCHAR(100)    NOT NULL,
    ref_id          BIGINT,
    ref_sub_id      BIGINT,
    ref_type        VARCHAR(50),
    expire_at       DATE,
    error_message   VARCHAR(300),
    trace_id        VARCHAR(50),
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### mbr_member_coupon

```sql
mbr_member_coupon (
    id              BIGINT          PK AUTO_INCREMENT,
    member_id       BIGINT          NOT NULL FK → mbr_member.id,
    coupon_id       BIGINT          NOT NULL,
    coupon_code     VARCHAR(100)    NOT NULL,
    status          VARCHAR(20)     NOT NULL DEFAULT 'AVAILABLE',
    -- AVAILABLE·USED·EXPIRED
    issued_at       DATETIME        NOT NULL,
    expire_at       DATE            NOT NULL,
    used_at         DATETIME,
    used_order_id   BIGINT,
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50),
    UNIQUE KEY uk_member_coupon (member_id, coupon_id)
)
```

### mbr_member_coupon_log

```sql
mbr_member_coupon_log (
    id                  BIGINT          PK AUTO_INCREMENT,
    member_coupon_id    BIGINT          NOT NULL FK → mbr_member_coupon.id,
    member_id           BIGINT          NOT NULL,
    coupon_id           BIGINT          NOT NULL,
    action_type         VARCHAR(20)     NOT NULL,
    -- USE·RESTORE·EXPIRE
    status              VARCHAR(20)     NOT NULL DEFAULT 'COMPLETED',
    -- COMPLETED·FAILED·PENDING
    platform_order_id   BIGINT,
    order_id            BIGINT,
    claim_id            BIGINT,
    discount_amount     DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    error_message       VARCHAR(300),
    trace_id            VARCHAR(50),
    created_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

### mbr_device_session

```sql
mbr_device_session (
    id              BIGINT          PK AUTO_INCREMENT,
    member_id       BIGINT          NOT NULL FK → mbr_member.id,
    device_id       VARCHAR(200)    NOT NULL,
    device_type     VARCHAR(20)     NOT NULL,
    -- WEB·IOS·ANDROID
    device_name     VARCHAR(100),
    refresh_token   VARCHAR(500)    NOT NULL,
    -- 암호화 저장
    last_accessed_at DATETIME       NOT NULL,
    expire_at       DATETIME        NOT NULL,
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50),
    UNIQUE KEY uk_member_device (member_id, device_id)
)
```

### mbr_address

```sql
mbr_address (
    id              BIGINT          PK AUTO_INCREMENT,
    member_id       BIGINT          NOT NULL FK → mbr_member.id,
    address_name    VARCHAR(100)    NOT NULL,
    recipient       VARCHAR(50)     NOT NULL,
    phone           VARCHAR(20)     NOT NULL,
    zipcode         VARCHAR(10)     NOT NULL,
    address1        VARCHAR(200)    NOT NULL,
    address2        VARCHAR(200),
    is_default      BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### mbr_notification_preference

```sql
mbr_notification_preference (
    id                  BIGINT          PK AUTO_INCREMENT,
    member_id           BIGINT          NOT NULL UNIQUE FK → mbr_member.id,
    email_marketing     BOOLEAN         NOT NULL DEFAULT TRUE,
    sms_marketing       BOOLEAN         NOT NULL DEFAULT TRUE,
    push_marketing      BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

### mbr_terms_agreement

```sql
mbr_terms_agreement (
    id                  BIGINT          PK AUTO_INCREMENT,
    member_id           BIGINT          NOT NULL FK → mbr_member.id,
    terms_type          VARCHAR(50)     NOT NULL,
    -- SERVICE·PRIVACY·MARKETING
    terms_version       VARCHAR(20)     NOT NULL,
    -- 약관 버전
    agreed              BOOLEAN         NOT NULL DEFAULT FALSE,
    agreed_at           DATETIME,
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50),
    UNIQUE KEY uk_member_terms (member_id, terms_type, terms_version)
)
```

---

## 7. Promotion 도메인

### prm_coupon

```sql
prm_coupon (
    id                  BIGINT          PK AUTO_INCREMENT,
    coupon_code         VARCHAR(100)    NOT NULL UNIQUE,
    coupon_name         VARCHAR(200)    NOT NULL,
    issuer_type         VARCHAR(20)     NOT NULL,
    -- PLATFORM·VENDOR
    vendor_id           BIGINT,
    target_type         VARCHAR(20)     NOT NULL,
    -- ALL·GRADE·CATEGORY·PRODUCT
    target_ref_id       BIGINT,
    apply_unit          VARCHAR(20)     NOT NULL,
    -- ORDER·PRODUCT·CATEGORY
    discount_type       VARCHAR(20)     NOT NULL,
    -- FIXED·RATE
    discount_value      DECIMAL(12,2)   NOT NULL,
    min_order_amount    DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    max_discount_amount DECIMAL(12,2),
    issue_type          VARCHAR(20)     NOT NULL DEFAULT 'DOWNLOAD',
    -- DOWNLOAD·AUTO·ADMIN
    issue_limit         INT,
    issued_count        INT             NOT NULL DEFAULT 0,
    valid_days          INT,
    valid_from          DATE,
    valid_to            DATE,
    status              VARCHAR(20)     NOT NULL DEFAULT 'ACTIVE',
    -- ACTIVE·INACTIVE·EXHAUSTED
    cost_share_rate     DECIMAL(5,2)    NOT NULL DEFAULT 0.00,
    created_by          BIGINT          FK → cfg_operator.id,
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

### prm_event_price

```sql
prm_event_price (
    id                  BIGINT          PK AUTO_INCREMENT,
    product_id          BIGINT          NOT NULL FK → cat_product.id,
    event_name          VARCHAR(200)    NOT NULL,
    event_price         DECIMAL(12,2)   NOT NULL,
    discount_rate       DECIMAL(5,2)    NOT NULL,
    quantity_limit      BOOLEAN         NOT NULL DEFAULT FALSE,
    total_quantity      INT,
    remaining_quantity  INT,
    start_at            DATETIME        NOT NULL,
    end_at              DATETIME        NOT NULL,
    status              VARCHAR(20)     NOT NULL DEFAULT 'ACTIVE',
    -- ACTIVE·SOLD_OUT·ENDED
    created_by          BIGINT          FK → cfg_operator.id,
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

### prm_quantity_discount

```sql
prm_quantity_discount (
    id              BIGINT          PK AUTO_INCREMENT,
    event_name      VARCHAR(200)    NOT NULL,
    vendor_id       BIGINT          NOT NULL FK → vnd_vendor.id,
    start_at        DATETIME        NOT NULL,
    end_at          DATETIME        NOT NULL,
    status          VARCHAR(20)     NOT NULL DEFAULT 'ACTIVE',
    created_by      BIGINT          FK → cfg_operator.id,
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### prm_quantity_discount_product

```sql
prm_quantity_discount_product (
    id                      BIGINT          PK AUTO_INCREMENT,
    quantity_discount_id    BIGINT          NOT NULL FK → prm_quantity_discount.id,
    product_id              BIGINT          NOT NULL FK → cat_product.id,
    price_sale              DECIMAL(12,2)   NOT NULL,
    created_at              DATETIME        NOT NULL,
    updated_at              DATETIME        NOT NULL,
    is_deleted              BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at              DATETIME,
    deleted_by              VARCHAR(50),
    UNIQUE KEY uk_discount_product (quantity_discount_id, product_id)
)
```

### prm_quantity_discount_tier

```sql
prm_quantity_discount_tier (
    id                      BIGINT          PK AUTO_INCREMENT,
    quantity_discount_id    BIGINT          NOT NULL FK → prm_quantity_discount.id,
    min_quantity            INT             NOT NULL,
    max_quantity            INT,
    discount_rate           DECIMAL(5,2)    NOT NULL,
    created_at              DATETIME        NOT NULL,
    updated_at              DATETIME        NOT NULL,
    is_deleted              BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at              DATETIME,
    deleted_by              VARCHAR(50)
)
```

### prm_cart_discount

```sql
prm_cart_discount (
    id                      BIGINT          PK AUTO_INCREMENT,
    discount_name           VARCHAR(200)    NOT NULL,
    apply_unit              VARCHAR(20)     NOT NULL DEFAULT 'PLATFORM',
    -- PLATFORM·VENDOR
    min_order_amount        DECIMAL(12,2)   NOT NULL,
    discount_type           VARCHAR(20)     NOT NULL,
    -- FIXED·RATE
    discount_value          DECIMAL(12,2)   NOT NULL,
    max_discount_amount     DECIMAL(12,2),
    partial_cancel_policy   VARCHAR(20)     NOT NULL DEFAULT 'KEEP',
    -- KEEP·RECALCULATE·DENY
    start_at                DATETIME        NOT NULL,
    end_at                  DATETIME        NOT NULL,
    status                  VARCHAR(20)     NOT NULL DEFAULT 'ACTIVE',
    created_by              BIGINT          FK → cfg_operator.id,
    created_at              DATETIME        NOT NULL,
    updated_at              DATETIME        NOT NULL,
    is_deleted              BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at              DATETIME,
    deleted_by              VARCHAR(50)
)
```

### prm_exhibition

```sql
prm_exhibition (
    id                  BIGINT          PK AUTO_INCREMENT,
    exhibition_code     VARCHAR(100)    NOT NULL UNIQUE,
    exhibition_name     VARCHAR(200)    NOT NULL,
    description         TEXT,
    thumbnail_url       VARCHAR(500),
    start_at            DATETIME        NOT NULL,
    end_at              DATETIME        NOT NULL,
    status              VARCHAR(20)     NOT NULL DEFAULT 'DRAFT',
    -- DRAFT·PUBLISHED·CLOSED
    created_by          BIGINT          FK → cfg_operator.id,
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

### prm_promotion_group

```sql
prm_promotion_group (
    id              BIGINT          PK AUTO_INCREMENT,
    group_code      VARCHAR(100)    NOT NULL UNIQUE,
    group_name      VARCHAR(200)    NOT NULL,
    description     VARCHAR(500),
    start_at        DATETIME        NOT NULL,
    end_at          DATETIME        NOT NULL,
    status          VARCHAR(20)     NOT NULL DEFAULT 'DRAFT',
    -- DRAFT·ACTIVE·ENDED·CANCELLED
    ref_type        VARCHAR(20),
    -- EXHIBITION·EVENT·SEASON·NONE
    ref_id          BIGINT,
    created_by      BIGINT          FK → cfg_operator.id,
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### prm_promotion_group_item

```sql
prm_promotion_group_item (
    id              BIGINT          PK AUTO_INCREMENT,
    group_id        BIGINT          NOT NULL FK → prm_promotion_group.id,
    promotion_type  VARCHAR(30)     NOT NULL,
    -- EVENT_PRICE·COUPON·QUANTITY_DISCOUNT·CART_DISCOUNT
    promotion_id    BIGINT          NOT NULL,
    sort_order      INT             NOT NULL DEFAULT 0,
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50),
    UNIQUE KEY uk_group_promotion (group_id, promotion_type, promotion_id)
)
```

---

## 8. Order 도메인

### ord_platform_order

```sql
ord_platform_order (
    id                      BIGINT          PK AUTO_INCREMENT,
    platform_order_no       VARCHAR(50)     NOT NULL UNIQUE,
    -- PO-20260622-00001
    member_id               BIGINT          NOT NULL,
    status                  VARCHAR(30)     NOT NULL DEFAULT 'TEMP',
    -- TEMP·PROCESSING·DEPOSIT_PENDING·PAYMENT_COMPLETED
    -- CANCELLED·PARTIALLY_CANCELLED
    -- ⚠ DEPOSIT_PENDING(입금대기, 2026-10-19 추가): 결제요청 성공 시 PAYMENT_COMPLETED가 아니라
    --   이 상태로 생성됨을 시뮬레이션(가상계좌/포인트 혼합결제 등 결제 확정 전 대기 상태 가정).
    --   정책서(payment.md §110)상 가상계좌 실연동은 범위 제외이므로, 이 상태는 실제 PG/가상계좌
    --   연동 없이 "결제요청=즉시 완료가 아님"을 표현하는 목적의 상태값이다. 본개발 전환 시 재확인.
    --   PROCESSING은 이번 라운드 미사용(재고 비동기 차감 대기 상태, 재고차감 미실행) — TEMP에서
    --   DEPOSIT_PENDING으로 직행하며 PROCESSING을 거치지 않는다.
    total_item_amount       DECIMAL(15,2)   NOT NULL,
    total_discount_amount   DECIMAL(15,2)   NOT NULL DEFAULT 0.00,
    total_shipping_amount   DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    point_used_amount       INT             NOT NULL DEFAULT 0,
    payment_amount          DECIMAL(15,2)   NOT NULL,
    receiver_name           VARCHAR(50)     NOT NULL,
    receiver_phone          VARCHAR(20)     NOT NULL,
    zipcode                 VARCHAR(10)     NOT NULL,
    address1                VARCHAR(200)    NOT NULL,
    address2                VARCHAR(200),
    delivery_memo           VARCHAR(300),
    ordered_at              DATETIME        NOT NULL,
    created_at              DATETIME        NOT NULL,
    updated_at              DATETIME        NOT NULL,
    carted_at               DATETIME        NOT NULL,
    -- 장바구니 담은 일시
    last_validated_at       DATETIME,
    -- 마지막 유효성 검사 일시
    price_snapshot          DECIMAL(12,2),
    -- 담을 당시 가격 스냅샷
    event_price_id          BIGINT          FK → prm_event_price.id,
    -- 담을 당시 적용된 행사가 ID
    is_deleted              BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at              DATETIME,
    deleted_by              VARCHAR(50)
)
```

### ord_platform_order_discount

```sql
ord_platform_order_discount (
    id                      BIGINT          PK AUTO_INCREMENT,
    platform_order_id       BIGINT          NOT NULL FK → ord_platform_order.id,
    discount_type           VARCHAR(30)     NOT NULL,
    -- CART_DISCOUNT·ORDER_COUPON
    promotion_id            BIGINT,
    discount_amount         DECIMAL(12,2)   NOT NULL,
    platform_share          DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    vendor_share            DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    partial_cancel_policy   VARCHAR(20)     NOT NULL DEFAULT 'KEEP',
    -- KEEP·RECALCULATE·DENY (스냅샷)
    is_revoked              BOOLEAN         NOT NULL DEFAULT FALSE,
    -- 소급 취소 여부
    created_at              DATETIME        NOT NULL,
    updated_at              DATETIME        NOT NULL,
    is_deleted              BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at              DATETIME,
    deleted_by              VARCHAR(50)
)
```

### ord_order

```sql
ord_order (
    id                      BIGINT          PK AUTO_INCREMENT,
    order_no                VARCHAR(50)     NOT NULL UNIQUE,
    -- ORD-20260622-00001
    platform_order_id       BIGINT          NOT NULL FK → ord_platform_order.id,
    vendor_id               BIGINT          NOT NULL,
    status                  VARCHAR(30)     NOT NULL DEFAULT 'PAYMENT_COMPLETED',
    -- DEPOSIT_PENDING·PAYMENT_COMPLETED·PREPARING·IN_DELIVERY
    -- DELIVERED·CONFIRMED·CANCELLED
    -- RETURN_REQUESTED·RETURNING·RETURN_WITHDRAWN·RETURNED
    -- EXCHANGE_REQUESTED·EXCHANGING·EXCHANGE_WITHDRAWN·EXCHANGED
    -- ⚠ DEPOSIT_PENDING(입금대기, 2026-10-19 추가): ord_platform_order와 동일 사유.
    --   실제 INSERT 시점의 값은 애플리케이션에서 'DEPOSIT_PENDING'을 명시적으로 지정하며,
    --   컬럼 DEFAULT 리터럴('PAYMENT_COMPLETED')은 레거시 as-is 값 그대로 유지한다
    --   (DEFAULT는 안전장치일 뿐 실제 생성 경로는 항상 명시적 INSERT이므로 변경 불필요 — 하네스 범위 밖 DDL 변경 최소화).
    item_amount             DECIMAL(15,2)   NOT NULL,
    discount_amount         DECIMAL(15,2)   NOT NULL DEFAULT 0.00,
    shipping_fee            DECIMAL(8,2)    NOT NULL DEFAULT 0.00,
    shipping_fee_payer      VARCHAR(20)     NOT NULL DEFAULT 'CUSTOMER',
    -- CUSTOMER·VENDOR·PLATFORM
    payment_amount          DECIMAL(15,2)   NOT NULL,
    claim_lock              BOOLEAN         NOT NULL DEFAULT FALSE,
    shipping_deadline       DATETIME,
    confirmed_at            DATETIME,
    created_at              DATETIME        NOT NULL,
    updated_at              DATETIME        NOT NULL,
    is_deleted              BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at              DATETIME,
    deleted_by              VARCHAR(50)
)
```

### ord_order_item

```sql
ord_order_item (
    id                  BIGINT          PK AUTO_INCREMENT,
    platform_order_id   BIGINT          NOT NULL,
    -- 비정규화
    order_id            BIGINT          NOT NULL FK → ord_order.id,
    product_id          BIGINT          NOT NULL,
    sku_id              BIGINT          NOT NULL,
    product_name        VARCHAR(300)    NOT NULL,
    option1_type        VARCHAR(50),
    option1_value       VARCHAR(100),
    option2_type        VARCHAR(50),
    option2_value       VARCHAR(100),
    quantity            INT             NOT NULL,
    price_original      DECIMAL(12,2)   NOT NULL,
    price_sale          DECIMAL(12,2)   NOT NULL,
    price_supply        DECIMAL(12,2)   NOT NULL,
    fee_rate            DECIMAL(5,2)    NOT NULL,
    status              VARCHAR(30)     NOT NULL DEFAULT 'ORDERED',
    review_written      BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

### ord_order_item_discount

```sql
ord_order_item_discount (
    id              BIGINT          PK AUTO_INCREMENT,
    order_item_id   BIGINT          NOT NULL FK → ord_order_item.id,
    discount_type   VARCHAR(30)     NOT NULL,
    -- EVENT_PRICE·PRODUCT_COUPON·QUANTITY_DISCOUNT·POINT
    promotion_id    BIGINT,
    discount_amount DECIMAL(12,2)   NOT NULL,
    platform_share  DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    vendor_share    DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### ord_delivery

```sql
ord_delivery (
    id                  BIGINT          PK AUTO_INCREMENT,
    order_id            BIGINT          NOT NULL UNIQUE FK → ord_order.id,
    delivery_company_id BIGINT          FK → cfg_delivery_company.id,
    tracking_no         VARCHAR(100),
    shipping_fee        DECIMAL(8,2)    NOT NULL DEFAULT 0.00,
    shipping_fee_payer  VARCHAR(20)     NOT NULL DEFAULT 'CUSTOMER',
    status              VARCHAR(20)     NOT NULL DEFAULT 'READY',
    -- READY·IN_DELIVERY·DELIVERED·RETURNED
    shipped_at          DATETIME,
    delivered_at        DATETIME,
    return_tracking_no  VARCHAR(100),
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

### ord_claim

```sql
ord_claim (
    id                      BIGINT          PK AUTO_INCREMENT,
    order_id                BIGINT          NOT NULL FK → ord_order.id,
    claim_no                VARCHAR(50)     NOT NULL UNIQUE,
    -- CLM-20260622-00001
    claim_type              VARCHAR(20)     NOT NULL,
    -- CANCEL·RETURN·EXCHANGE
    cancel_type             VARCHAR(20),
    -- SIMPLE·EXCEPTION
    status                  VARCHAR(30)     NOT NULL DEFAULT 'REQUESTED',
    -- REQUESTED·PROCESSING·COMPLETED·REJECTED
    blame_type              VARCHAR(20),
    -- CUSTOMER·VENDOR·PLATFORM·PENDING
    blame_evidence_urls     JSON,
    reason                  VARCHAR(500),
    channel                 VARCHAR(20)     NOT NULL DEFAULT 'SELF',
    -- SELF·COUNSELOR
    counselor_id            BIGINT,
    counselor_memo          VARCHAR(500),
    refund_amount           DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    extra_delivery_fee      DECIMAL(8,2)    NOT NULL DEFAULT 0.00,
    extra_payment_id        BIGINT,
    extra_payment_status    VARCHAR(20),
    -- PENDING·COMPLETED·FAILED
    completed_at            DATETIME,
    created_at              DATETIME        NOT NULL,
    updated_at              DATETIME        NOT NULL,
    is_deleted              BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at              DATETIME,
    deleted_by              VARCHAR(50)
)
```

### ord_claim_item

```sql
ord_claim_item (
    id                  BIGINT          PK AUTO_INCREMENT,
    claim_id            BIGINT          NOT NULL FK → ord_claim.id,
    order_id            BIGINT          NOT NULL,
    -- 비정규화
    order_item_id       BIGINT          NOT NULL FK → ord_order_item.id,
    quantity            INT             NOT NULL DEFAULT 1,
    refund_amount       DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    exchange_sku_id     BIGINT,
    stock_restored      BOOLEAN         NOT NULL DEFAULT FALSE,
    stock_restored_at   DATETIME,
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

### ord_cart

```sql
ord_cart (
    id                  BIGINT          PK AUTO_INCREMENT,
    member_id           BIGINT          NOT NULL FK → mbr_member.id,
    product_id          BIGINT          NOT NULL FK → cat_product.id,
    sku_id              BIGINT          NOT NULL FK → cat_sku.id,
    vendor_id           BIGINT          NOT NULL,
    quantity            INT             NOT NULL DEFAULT 1,
    price_snapshot      DECIMAL(12,2)   NOT NULL,
    -- 담을 당시 가격 스냅샷
    event_price_id      BIGINT          FK → prm_event_price.id,
    -- 담을 당시 적용된 행사가 ID
    carted_at           DATETIME        NOT NULL,
    -- 장바구니 담은 일시
    last_validated_at   DATETIME,
    -- 마지막 유효성 검사 일시
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

---

## 9. Payment 도메인

### pay_payment

```sql
pay_payment (
    id                  BIGINT          PK AUTO_INCREMENT,
    payment_no          VARCHAR(50)     NOT NULL UNIQUE,
    -- PAY-20260622-00001
    platform_order_id   BIGINT          NOT NULL UNIQUE,
    member_id           BIGINT          NOT NULL,
    payment_amount      DECIMAL(15,2)   NOT NULL,
    approved_amount     DECIMAL(15,2),
    payment_method      VARCHAR(20)     NOT NULL DEFAULT 'CARD',
    -- CARD·EASY_PAY·POINT·VIRTUAL_ACCOUNT·MIXED
    point_amount        INT             NOT NULL DEFAULT 0,
    card_amount         DECIMAL(15,2)   NOT NULL DEFAULT 0.00,
    pg_provider         VARCHAR(50),
    pg_transaction_id   VARCHAR(200),
    pg_approval_no      VARCHAR(100),
    pg_approved_at      DATETIME,
    status              VARCHAR(20)     NOT NULL DEFAULT 'PENDING',
    -- PENDING·COMPLETED·FAILED·CANCELLED·PARTIAL_CANCELLED
    failed_reason       VARCHAR(300),
    retry_count         INT             NOT NULL DEFAULT 0,
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

> **(2026-10-19 구현확인/실제 구현 반영)**: `payment_method` enum은 결제 채널이 실제로 구분하는 결제수단
> 5종(`CARD`/`EASY_PAY`/`POINT`/`VIRTUAL_ACCOUNT`/`MIXED`)을 전부 열거한다. 컬럼 타입은 `VARCHAR(20)`로
> 스키마 변경 없이 5종 전부를 수용한다 — 열거값을 3종(`CARD`/`POINT`/`MIXED`)으로만 좁혀 적을 경우,
> `EASY_PAY`/`VIRTUAL_ACCOUNT`로 결제한 주문이 집계상 `CARD`로 뭉개져 어드민 결제정보 화면(결제수단)이
> 실제 선택값과 달라지는 손실이 생긴다(주문 생성 채널이 이 5종 중 하나를 그대로 넘겨주므로, 저장 시
> 근사 매핑할 이유가 없다). `MIXED`(복합결제)는 열거값으로는 유지하되, 주문 생성 채널이 아직 복합결제
> 요청 자체를 보내지 않아(단일 결제수단만 선택 가능) 현재는 생성되지 않는 값이다 — 복합결제 기능이
> 추가되는 시점에 실제로 쓰이기 시작한다.

### pay_payment_cancel

```sql
pay_payment_cancel (
    id                      BIGINT          PK AUTO_INCREMENT,
    cancel_no               VARCHAR(50)     NOT NULL UNIQUE,
    -- CAN-20260622-00001
    payment_id              BIGINT          NOT NULL FK → pay_payment.id,
    platform_order_id       BIGINT          NOT NULL,
    order_id                BIGINT,
    -- 부분 취소 시 해당 Order ID
    claim_id                BIGINT,
    cancel_type             VARCHAR(20)     NOT NULL,
    -- FULL·PARTIAL·CLAIM
    cancel_amount           DECIMAL(15,2)   NOT NULL,
    card_cancel_amount      DECIMAL(15,2)   NOT NULL DEFAULT 0.00,
    point_restore_amount    INT             NOT NULL DEFAULT 0,
    cancel_reason           VARCHAR(300),
    pg_cancel_id            VARCHAR(200),
    pg_cancelled_at         DATETIME,
    status                  VARCHAR(20)     NOT NULL DEFAULT 'PENDING',
    -- PENDING·COMPLETED·FAILED
    created_at              DATETIME        NOT NULL,
    updated_at              DATETIME        NOT NULL,
    is_deleted              BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at              DATETIME,
    deleted_by              VARCHAR(50)
)
```

### pay_extra_payment

```sql
pay_extra_payment (
    id                  BIGINT          PK AUTO_INCREMENT,
    extra_payment_no    VARCHAR(50)     NOT NULL UNIQUE,
    -- EPAY-20260622-00001
    platform_order_id   BIGINT          NOT NULL,
    order_id            BIGINT          NOT NULL,
    claim_id            BIGINT          NOT NULL,
    extra_type          VARCHAR(20)     NOT NULL DEFAULT 'DELIVERY_FEE',
    payment_amount      DECIMAL(12,2)   NOT NULL,
    payment_method      VARCHAR(20)     NOT NULL DEFAULT 'CARD',
    pg_provider         VARCHAR(50),
    pg_transaction_id   VARCHAR(200),
    pg_approval_no      VARCHAR(100),
    pg_approved_at      DATETIME,
    status              VARCHAR(20)     NOT NULL DEFAULT 'PENDING',
    -- PENDING·COMPLETED·FAILED
    failed_reason       VARCHAR(300),
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

### pay_payment_log

```sql
pay_payment_log (
    id                  BIGINT          PK AUTO_INCREMENT,
    payment_id          BIGINT          FK → pay_payment.id,
    -- NULL 가능 (주문서 진입 시점)
    platform_order_id   BIGINT          NOT NULL,
    member_id           BIGINT          NOT NULL,
    step                VARCHAR(30)     NOT NULL,
    -- ORDER_SHEET_ENTER
    -- AUTH_REQUEST / AUTH_APPROVED
    -- PAYMENT_REQUEST / PAYMENT_RECEIVED
    -- POINT_USE_REQUEST / POINT_USE_RECEIVED
    -- POINT_RESTORE_REQUEST / POINT_RESTORE_RECEIVED
    -- COUPON_USE_REQUEST / COUPON_USE_RECEIVED
    -- COUPON_RESTORE_REQUEST / COUPON_RESTORE_RECEIVED
    -- CANCEL_REQUEST / CANCEL_RECEIVED
    -- PARTIAL_CANCEL_REQUEST / PARTIAL_CANCEL_RECEIVED
    step_status         VARCHAR(20)     NOT NULL,
    -- SUCCESS·FAILED·TIMEOUT
    request_data        JSON,
    response_data       JSON,
    pg_provider         VARCHAR(50),
    pg_transaction_id   VARCHAR(200),
    error_code          VARCHAR(50),
    error_message       VARCHAR(500),
    elapsed_ms          BIGINT,
    is_threshold_alerted BOOLEAN        NOT NULL DEFAULT FALSE,
    -- 임계치 알림 여부 (10분 내 2회 이상)
    created_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

### pay_fds_log

```sql
pay_fds_log (
    id                  BIGINT          PK AUTO_INCREMENT,
    payment_id          BIGINT          FK → pay_payment.id,
    member_id           BIGINT          NOT NULL,
    detection_type      VARCHAR(50)     NOT NULL,
    -- ABNORMAL_AMOUNT·REPEATED_FAILURE·SUSPICIOUS_PATTERN
    risk_score          INT             NOT NULL DEFAULT 0,
    -- 0~100
    action_taken        VARCHAR(30)     NOT NULL,
    -- BLOCKED·FLAGGED·ALLOWED
    detail              TEXT,
    detected_at         DATETIME        NOT NULL,
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

---

## 10. Settlement 도메인

### stl_settlement_target

```sql
stl_settlement_target (
    id                  BIGINT          PK AUTO_INCREMENT,
    order_id            BIGINT          NOT NULL UNIQUE,
    platform_order_id   BIGINT          NOT NULL,
    vendor_id           BIGINT          NOT NULL,
    confirmed_at        DATETIME        NOT NULL,
    item_amount         DECIMAL(15,2)   NOT NULL,
    discount_amount     DECIMAL(15,2)   NOT NULL DEFAULT 0.00,
    shipping_fee        DECIMAL(8,2)    NOT NULL DEFAULT 0.00,
    shipping_fee_payer  VARCHAR(20)     NOT NULL,
    point_vendor_share  DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    coupon_vendor_share DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    fee_rate            DECIMAL(5,2)    NOT NULL,
    -- 수수료율 스냅샷
    fee_amount          DECIMAL(12,2)   NOT NULL,
    net_amount          DECIMAL(15,2)   NOT NULL,
    settlement_id       BIGINT,
    status              VARCHAR(20)     NOT NULL DEFAULT 'PENDING',
    -- PENDING·SETTLED·ADJUSTED
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

### stl_settlement

```sql
stl_settlement (
    id                  BIGINT          PK AUTO_INCREMENT,
    settlement_no       VARCHAR(50)     NOT NULL UNIQUE,
    -- STL-202606-00001
    vendor_id           BIGINT          NOT NULL,
    settlement_month    VARCHAR(7)      NOT NULL,
    -- 2026-06
    status              VARCHAR(20)     NOT NULL DEFAULT 'CALCULATING',
    -- CALCULATING·CONFIRMED·PAID·HOLD
    target_amount       DECIMAL(15,2)   NOT NULL DEFAULT 0.00,
    adjustment_amount   DECIMAL(15,2)   NOT NULL DEFAULT 0.00,
    penalty_amount      DECIMAL(12,2)   NOT NULL DEFAULT 0.00,
    final_amount        DECIMAL(15,2)   NOT NULL DEFAULT 0.00,
    carried_over_amount DECIMAL(15,2)   NOT NULL DEFAULT 0.00,
    objection_count     INT             NOT NULL DEFAULT 0,
    -- 이의제기 횟수
    objection_deadline  DATETIME,
    -- 이의제기 가능 기간 (확정일 + 5영업일)
    confirmed_at        DATETIME,
    confirmed_by        BIGINT,
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

### stl_settlement_item

```sql
stl_settlement_item (
    id              BIGINT          PK AUTO_INCREMENT,
    settlement_id   BIGINT          NOT NULL FK → stl_settlement.id,
    item_type       VARCHAR(30)     NOT NULL,
    -- SALES·FEE·SHIPPING·POINT_SHARE·COUPON_SHARE·PENALTY·CARRY_OVER
    amount          DECIMAL(15,2)   NOT NULL,
    description     VARCHAR(200),
    ref_id          BIGINT,
    ref_type        VARCHAR(50),
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### stl_settlement_adjustment

```sql
stl_settlement_adjustment (
    id                  BIGINT          PK AUTO_INCREMENT,
    settlement_id       BIGINT          NOT NULL FK → stl_settlement.id,
    order_id            BIGINT          NOT NULL,
    adjustment_type     VARCHAR(20)     NOT NULL,
    -- RETURN·CANCEL·EXCHANGE
    adjustment_amount   DECIMAL(15,2)   NOT NULL,
    original_target_id  BIGINT          NOT NULL,
    reason              VARCHAR(200),
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

### stl_settlement_payment

```sql
stl_settlement_payment (
    id                  BIGINT          PK AUTO_INCREMENT,
    settlement_id       BIGINT          NOT NULL UNIQUE FK → stl_settlement.id,
    vendor_id           BIGINT          NOT NULL,
    bank_code           VARCHAR(10)     NOT NULL,
    account_no          VARCHAR(50)     NOT NULL,
    account_holder      VARCHAR(100)    NOT NULL,
    payment_amount      DECIMAL(15,2)   NOT NULL,
    scheduled_date      DATE            NOT NULL,
    paid_at             DATETIME,
    status              VARCHAR(20)     NOT NULL DEFAULT 'SCHEDULED',
    -- SCHEDULED·PAID·HOLD·FAILED
    hold_reason         VARCHAR(300),
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

### stl_external_settlement

```sql
stl_external_settlement (
    id                  BIGINT          PK AUTO_INCREMENT,
    settlement_month    VARCHAR(7)      NOT NULL,
    partner_type        VARCHAR(20)     NOT NULL,
    -- PG·LOGISTICS·ADVERTISER·PLATFORM
    partner_name        VARCHAR(100)    NOT NULL,
    billing_amount      DECIMAL(15,2)   NOT NULL,
    paid_amount         DECIMAL(15,2)   NOT NULL DEFAULT 0.00,
    status              VARCHAR(20)     NOT NULL DEFAULT 'PENDING',
    billing_date        DATE,
    paid_date           DATE,
    description         VARCHAR(300),
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

### stl_settlement_objection

```sql
stl_settlement_objection (
    id                  BIGINT          PK AUTO_INCREMENT,
    settlement_no       VARCHAR(50)     NOT NULL FK → stl_settlement.settlement_no,
    vendor_id           BIGINT          NOT NULL FK → vnd_vendor.id,
    objection_reason    TEXT            NOT NULL,
    -- 이의제기 사유
    objection_amount    DECIMAL(12,2),
    -- 이의제기 금액
    status              VARCHAR(20)     NOT NULL DEFAULT 'PENDING',
    -- PENDING: 검토 중
    -- ACCEPTED: 수용·재정산
    -- REJECTED: 기각
    result_reason       TEXT,
    -- 처리 결과 사유
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

---

## 11. Notification 도메인

### ntf_template

```sql
ntf_template (
    id                  BIGINT          PK AUTO_INCREMENT,
    template_code       VARCHAR(100)    NOT NULL UNIQUE,
    template_name       VARCHAR(200)    NOT NULL,
    event_type          VARCHAR(100)    NOT NULL,
    receiver_type       VARCHAR(20)     NOT NULL,
    -- CUSTOMER·VENDOR·OPERATOR
    channel             VARCHAR(20)     NOT NULL,
    -- KAKAO·SMS·EMAIL
    title               VARCHAR(200),
    body                TEXT            NOT NULL,
    variables           JSON,
    is_required         BOOLEAN         NOT NULL DEFAULT FALSE,
    -- 거래 알림 여부 (수신 거부 불가)
    status              VARCHAR(20)     NOT NULL DEFAULT 'ACTIVE',
    created_by          BIGINT          FK → cfg_operator.id,
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50),
    UNIQUE KEY uk_event_receiver_channel (event_type, receiver_type, channel)
)
```

### ntf_history

```sql
ntf_history (
    id                  BIGINT          PK AUTO_INCREMENT,
    template_id         BIGINT          NOT NULL FK → ntf_template.id,
    event_type          VARCHAR(100)    NOT NULL,
    receiver_type       VARCHAR(20)     NOT NULL,
    receiver_id         BIGINT          NOT NULL,
    channel             VARCHAR(20)     NOT NULL,
    -- 실제 발송 채널
    original_channel    VARCHAR(20)     NOT NULL,
    -- 최초 시도 채널
    receiver_contact    VARCHAR(200)    NOT NULL,
    -- 마스킹 저장
    title               VARCHAR(200),
    body                TEXT            NOT NULL,
    ref_id              BIGINT,
    ref_type            VARCHAR(50),
    status              VARCHAR(20)     NOT NULL DEFAULT 'PENDING',
    -- PENDING·SENT·FAILED
    retry_count         INT             NOT NULL DEFAULT 0,
    sent_at             DATETIME,
    failed_reason       VARCHAR(300),
    is_night_blocked    BOOLEAN         NOT NULL DEFAULT FALSE,
    scheduled_at        DATETIME,
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

### ntf_batch_queue

```sql
ntf_batch_queue (
    id                  BIGINT          PK AUTO_INCREMENT,
    batch_type          VARCHAR(50)     NOT NULL,
    -- CLAIM_RECEIVED·PRODUCT_APPROVED·PRODUCT_REJECTED·SETTLEMENT_CONFIRMED
    receiver_type       VARCHAR(20)     NOT NULL,
    receiver_id         BIGINT          NOT NULL,
    ref_id              BIGINT          NOT NULL,
    ref_type            VARCHAR(50)     NOT NULL,
    ref_data            JSON,
    status              VARCHAR(20)     NOT NULL DEFAULT 'PENDING',
    -- PENDING·SENT·FAILED
    scheduled_batch_at  DATETIME        NOT NULL,
    -- 09·13·18시 중 다음 배치
    history_id          BIGINT,
    created_at          DATETIME        NOT NULL,
    updated_at          DATETIME        NOT NULL,
    is_deleted          BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at          DATETIME,
    deleted_by          VARCHAR(50)
)
```

---

## 12. Community 도메인

### cmt_review

```sql
cmt_review (
    id              BIGINT          PK AUTO_INCREMENT,
    product_id      BIGINT          NOT NULL,
    order_item_id   BIGINT          NOT NULL UNIQUE,
    -- 주문 상품당 1개
    member_id       BIGINT          NOT NULL,
    rating          TINYINT         NOT NULL,
    -- 1~5
    content         TEXT,
    image_urls      JSON,
    is_photo_review BOOLEAN         NOT NULL DEFAULT FALSE,
    status          VARCHAR(20)     NOT NULL DEFAULT 'ACTIVE',
    -- ACTIVE·HIDDEN·DELETED
    hidden_reason   VARCHAR(200),
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### cmt_rating

```sql
cmt_rating (
    id              BIGINT          PK AUTO_INCREMENT,
    product_id      BIGINT          NOT NULL UNIQUE,
    avg_rating      DECIMAL(3,2)    NOT NULL DEFAULT 0.00,
    review_count    INT             NOT NULL DEFAULT 0,
    rating_1_count  INT             NOT NULL DEFAULT 0,
    rating_2_count  INT             NOT NULL DEFAULT 0,
    rating_3_count  INT             NOT NULL DEFAULT 0,
    rating_4_count  INT             NOT NULL DEFAULT 0,
    rating_5_count  INT             NOT NULL DEFAULT 0,
    updated_at      DATETIME        NOT NULL,
    created_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### cmt_qna (통합 QnA)

```sql
cmt_qna (
    id                      BIGINT          PK AUTO_INCREMENT,
    qna_type                VARCHAR(20)     NOT NULL,
    -- PRODUCT·ORDER
    ref_id                  BIGINT          NOT NULL,
    -- PRODUCT → cat_product.id
    -- ORDER   → platform_order_id
    ref_sub_id              BIGINT,
    -- ORDER 타입 시 order_id
    member_id               BIGINT          NOT NULL,
    question                TEXT            NOT NULL,
    answer                  TEXT,
    answered_by             BIGINT,
    answered_by_type        VARCHAR(20),
    -- OPERATOR·VENDOR
    answered_at             DATETIME,
    is_public               BOOLEAN         NOT NULL DEFAULT TRUE,
    -- ORDER 타입은 항상 FALSE
    activity_score_granted  BOOLEAN         NOT NULL DEFAULT FALSE,
    -- 활동지수 지급 여부 (옵션)
    activity_score_at       DATETIME,
    status                  VARCHAR(20)     NOT NULL DEFAULT 'PENDING',
    -- PENDING·ANSWERED·HIDDEN
    created_at              DATETIME        NOT NULL,
    updated_at              DATETIME        NOT NULL,
    is_deleted              BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at              DATETIME,
    deleted_by              VARCHAR(50)
)
```

---

## 13. Search 도메인

### ES 인덱스

| 인덱스명 | 설명 | 소스 도메인 |
|---------|------|-----------|
| `product_index` | 상품 통합 인덱스 | Catalog·Promotion |
| `exhibition_index` | 기획전·이벤트 인덱스 | Promotion |
| `community_index` | 커뮤니티 콘텐츠 인덱스 | Community |

### sch_search_keyword

```sql
sch_search_keyword (
    id              BIGINT          PK AUTO_INCREMENT,
    keyword         VARCHAR(100)    NOT NULL UNIQUE,
    sort_order      INT             NOT NULL DEFAULT 0,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    search_count    BIGINT          NOT NULL DEFAULT 0,
    created_by      BIGINT          FK → cfg_operator.id,
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### sch_auto_complete

```sql
sch_auto_complete (
    id              BIGINT          PK AUTO_INCREMENT,
    keyword         VARCHAR(100)    NOT NULL UNIQUE,
    keyword_type    VARCHAR(20)     NOT NULL DEFAULT 'PRODUCT',
    -- PRODUCT·BRAND·CATEGORY
    ref_id          BIGINT,
    sort_order      INT             NOT NULL DEFAULT 0,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### sch_index_sync_history

```sql
sch_index_sync_history (
    id              BIGINT          PK AUTO_INCREMENT,
    index_type      VARCHAR(20)     NOT NULL,
    -- PRODUCT·EXHIBITION·COMMUNITY
    sync_type       VARCHAR(20)     NOT NULL,
    -- BATCH·EVENT
    ref_id          BIGINT,
    synced_count    INT             NOT NULL DEFAULT 0,
    status          VARCHAR(20)     NOT NULL DEFAULT 'SUCCESS',
    -- SUCCESS·FAILED·PARTIAL
    error_message   VARCHAR(500),
    started_at      DATETIME        NOT NULL,
    finished_at     DATETIME,
    created_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### sch_category_view_history

```sql
sch_category_view_history (
    id              BIGINT          PK AUTO_INCREMENT,
    category_id     BIGINT          NOT NULL,
    category_type   VARCHAR(20)     NOT NULL DEFAULT 'STANDARD',
    -- STANDARD·DISPLAY
    member_id       BIGINT,
    -- NULL = 비로그인
    session_id      VARCHAR(200),
    device_type     VARCHAR(20),
    -- WEB·IOS·ANDROID
    ref_type        VARCHAR(20),
    -- SEARCH·BANNER·EXHIBITION·DIRECT
    ref_id          BIGINT,
    viewed_at       DATETIME        NOT NULL,
    created_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### sch_category_view_daily

```sql
sch_category_view_daily (
    id                      BIGINT          PK AUTO_INCREMENT,
    category_id             BIGINT          NOT NULL,
    category_type           VARCHAR(20)     NOT NULL DEFAULT 'STANDARD',
    view_date               DATE            NOT NULL,
    total_view_count        BIGINT          NOT NULL DEFAULT 0,
    unique_view_count       BIGINT          NOT NULL DEFAULT 0,
    login_view_count        BIGINT          NOT NULL DEFAULT 0,
    anonymous_view_count    BIGINT          NOT NULL DEFAULT 0,
    created_at              DATETIME        NOT NULL,
    updated_at              DATETIME        NOT NULL,
    is_deleted              BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at              DATETIME,
    deleted_by              VARCHAR(50),
    UNIQUE KEY uk_category_date (category_id, category_type, view_date)
)
```

---

## 14. Audit 도메인

### adt_audit_log

```sql
adt_audit_log (
    id              BIGINT          PK AUTO_INCREMENT,
    trace_id        VARCHAR(50)     NOT NULL,
    domain          VARCHAR(30)     NOT NULL,
    event_type      VARCHAR(100)    NOT NULL,
    aggregate_id    VARCHAR(100)    NOT NULL,
    aggregate_type  VARCHAR(50)     NOT NULL,
    action          VARCHAR(20)     NOT NULL,
    -- CREATE·UPDATE·DELETE·STATUS_CHANGE
    before_value    JSON,
    after_value     JSON,
    actor_type      VARCHAR(20)     NOT NULL,
    -- SYSTEM·MEMBER·OPERATOR·VENDOR
    actor_id        BIGINT,
    actor_ip        VARCHAR(50),
    created_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### adt_trace_log

```sql
adt_trace_log (
    id              BIGINT          PK AUTO_INCREMENT,
    trace_id        VARCHAR(50)     NOT NULL,
    span_id         VARCHAR(50)     NOT NULL,
    parent_span_id  VARCHAR(50),
    domain          VARCHAR(30)     NOT NULL,
    log_level       VARCHAR(10)     NOT NULL,
    -- ERROR·WARN·INFO·DEBUG
    message         TEXT            NOT NULL,
    elapsed_ms      BIGINT,
    extra_data      JSON,
    created_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### adt_dlq

```sql
adt_dlq (
    id              BIGINT          PK AUTO_INCREMENT,
    outbox_event_id BIGINT          NOT NULL,
    trace_id        VARCHAR(50),
    event_type      VARCHAR(100)    NOT NULL,
    payload         JSON            NOT NULL,
    fail_reason     VARCHAR(500)    NOT NULL,
    retry_count     INT             NOT NULL DEFAULT 0,
    status          VARCHAR(20)     NOT NULL DEFAULT 'PENDING',
    -- PENDING·RESOLVED·IGNORED
    resolved_by     BIGINT,
    resolved_at     DATETIME,
    resolve_memo    VARCHAR(500),
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### adt_log_retention_policy

```sql
adt_log_retention_policy (
    id              BIGINT          PK AUTO_INCREMENT,
    log_type        VARCHAR(30)     NOT NULL UNIQUE,
    -- AUDIT·TRACE_INFO·TRACE_DEBUG·DLQ·OUTBOX
    retention_days  INT             NOT NULL,
    last_purged_at  DATETIME,
    created_at      DATETIME        NOT NULL,
    updated_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### adt_member_access_log

```sql
adt_member_access_log (
    id              BIGINT          PK AUTO_INCREMENT,
    operator_id     BIGINT          NOT NULL FK → cfg_operator.id,
    operator_name   VARCHAR(50)     NOT NULL,
    -- 스냅샷 저장
    operator_role   VARCHAR(50)     NOT NULL,
    -- 스냅샷 저장
    access_type     VARCHAR(20)     NOT NULL,
    -- LIST: 목록 검색
    -- DETAIL: 상세 조회
    search_keyword  VARCHAR(200),
    -- 검색어 (마스킹 저장) 예) 010-****-5678
    member_id       BIGINT,
    -- DETAIL 조회 시 대상 회원 ID
    member_name     VARCHAR(50),
    -- 스냅샷 저장 (마스킹)
    result_count    INT,
    -- LIST 조회 시 결과 건수
    access_ip       VARCHAR(50)     NOT NULL,
    access_at       DATETIME        NOT NULL,
    created_at      DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

---

## 15. 복제 테이블 목록

| 복제 테이블 | 마스터 | 배치 주기 | 조회 모듈 |
|-----------|--------|---------|---------|
| `config_code_replica` | `cfg_common_code` | 1분 | 전 모듈 |
| `config_delivery_company_replica` | `cfg_delivery_company` | 10분 | Order·Vendor |
| `catalog_standard_category_replica` | `cat_standard_category` | 10분 | Search·Settlement |
| `vendor_fee_rate_replica` | `vnd_vendor_fee_rate` | 10분 | Settlement |
| `member_grade_discount_replica` | `mbr_member` (등급 정보) | 10분 | Order·프론트 |

### config_code_replica

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

### config_delivery_company_replica

```sql
config_delivery_company_replica (
    id              BIGINT          PK AUTO_INCREMENT,
    company_code    VARCHAR(50)     NOT NULL UNIQUE,
    company_name    VARCHAR(100)    NOT NULL,
    api_endpoint    VARCHAR(500),
    tracking_url    VARCHAR(500),
    api_connected   BOOLEAN         NOT NULL DEFAULT FALSE,
    status          VARCHAR(20)     NOT NULL DEFAULT 'ACTIVE',
    synced_at       DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### catalog_standard_category_replica

```sql
catalog_standard_category_replica (
    id              BIGINT          PK AUTO_INCREMENT,
    category_code   VARCHAR(50)     NOT NULL UNIQUE,
    category_name   VARCHAR(100)    NOT NULL,
    base_fee_rate   DECIMAL(5,2),
    depth           INT             NOT NULL DEFAULT 1,
    parent_id       BIGINT,
    synced_at       DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50)
)
```

### vendor_fee_rate_replica

```sql
vendor_fee_rate_replica (
    id              BIGINT          PK AUTO_INCREMENT,
    vendor_id       BIGINT          NOT NULL,
    category_id     BIGINT          NOT NULL,
    final_fee_rate  DECIMAL(5,2)    NOT NULL,
    synced_at       DATETIME        NOT NULL,
    is_deleted      BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at      DATETIME,
    deleted_by      VARCHAR(50),
    UNIQUE KEY uk_vendor_category (vendor_id, category_id)
)
```

### member_grade_discount_replica

```sql
member_grade_discount_replica (
    id                      BIGINT          PK AUTO_INCREMENT,
    grade_code              VARCHAR(20)     NOT NULL UNIQUE,
    discount_rate           DECIMAL(5,2)    NOT NULL,
    free_shipping_min       DECIMAL(12,2)   NOT NULL,
    monthly_coupon_count    INT             NOT NULL DEFAULT 0,
    point_bonus_rate        DECIMAL(5,2)    NOT NULL DEFAULT 0.00,
    synced_at               DATETIME        NOT NULL,
    is_deleted              BOOLEAN         NOT NULL DEFAULT FALSE,
    deleted_at              DATETIME,
    deleted_by              VARCHAR(50)
)
```

---

## 16. 전체 테이블 목록

| # | 도메인 | 테이블 | 비고 |
|---|--------|--------|------|
| 1 | Common | `cmn_outbox_event` | |
| 2 | Common | `cmn_sync_history` | |
| 3 | Common | `cmn_batch_job` | |
| 4 | Common | `cmn_batch_execution` | |
| 5 | Common | `cmn_batch_execution_log` | |
| 6 | Config | `cfg_operator` | |
| 7 | Config | `cfg_role` | |
| 8 | Config | `cfg_permission` | |
| 9 | Config | `cfg_program` | |
| 10 | Config | `cfg_common_code` | |
| 11 | Config | `cfg_delivery_company` | |
| 12 | Config | `cfg_notice` | |
| 13 | Config | `cfg_terms` | |
| 14 | Config | `cfg_banner` | |
| 15 | Vendor | `vnd_vendor_application` | |
| 16 | Vendor | `vnd_vendor` | |
| 17 | Vendor | `vnd_vendor_contract` | |
| 18 | Vendor | `vnd_vendor_fee_rate` | 이력 관리 |
| 19 | Vendor | `vnd_vendor_grade` | |
| 20 | Vendor | `vnd_vendor_account` | |
| 21 | Vendor | `vnd_vendor_delivery` | |
| 22 | Vendor | `vnd_vendor_penalty` | |
| 23 | Catalog | `cat_standard_category` | 1depth 제한 |
| 24 | Catalog | `cat_display_category` | |
| 25 | Catalog | `cat_product_display_category` | |
| 26 | Catalog | `cat_brand` | |
| 27 | Catalog | `cat_product` | |
| 28 | Catalog | `cat_product_image` | |
| 29 | Catalog | `cat_product_attribute` | |
| 30 | Catalog | `cat_sku` | |
| 31 | Catalog | `cat_product_price` | 이력 관리 |
| 32 | Catalog | `cat_product_exposure` | |
| 33 | Catalog | `cat_product_tag` | |
| 34 | Catalog | `cat_display_template` | |
| 35 | Catalog | `cat_display_area` | |
| 36 | Catalog | `cat_display_content` | |
| 37 | Catalog | `cat_display_page` | |
| 38 | Catalog | `cat_display_page_area` | |
| 39 | Catalog | `cat_display_page_content_item` | |
| 40 | Catalog | `cat_display_section_type` | 섹션종류 마스터 (신규) |
| 41 | Catalog | `cat_display_section_field` | 섹션종류 필드 스키마 (신규) |
| 42 | Member | `mbr_member` | |
| 43 | Member | `mbr_member_running_profile` | |
| 44 | Member | `mbr_member_grade` | |
| 45 | Member | `mbr_point` | |
| 46 | Member | `mbr_member_coupon` | |
| 47 | Member | `mbr_member_coupon_log` | |
| 48 | Member | `mbr_device_session` | |
| 49 | Member | `mbr_address` | |
| 50 | Member | `mbr_notification_preference` | |
| 51 | Promotion | `prm_coupon` | |
| 52 | Promotion | `prm_event_price` | |
| 53 | Promotion | `prm_quantity_discount` | |
| 54 | Promotion | `prm_quantity_discount_product` | |
| 55 | Promotion | `prm_quantity_discount_tier` | |
| 56 | Promotion | `prm_cart_discount` | partial_cancel_policy |
| 57 | Promotion | `prm_exhibition` | |
| 58 | Promotion | `prm_promotion_group` | |
| 59 | Promotion | `prm_promotion_group_item` | |
| 60 | Order | `ord_platform_order` | |
| 61 | Order | `ord_platform_order_discount` | |
| 62 | Order | `ord_order` | |
| 63 | Order | `ord_order_item` | |
| 64 | Order | `ord_order_item_discount` | |
| 65 | Order | `ord_delivery` | |
| 66 | Order | `ord_claim` | |
| 67 | Order | `ord_claim_item` | |
| 68 | Payment | `pay_payment` | |
| 69 | Payment | `pay_payment_cancel` | |
| 70 | Payment | `pay_extra_payment` | |
| 71 | Payment | `pay_payment_log` | 결제 전 과정 + 포인트·쿠폰 |
| 72 | Settlement | `stl_settlement_target` | |
| 73 | Settlement | `stl_settlement` | |
| 74 | Settlement | `stl_settlement_item` | |
| Settlement | `stl_settlement_objection` | 정산 이의제기 |
| 75 | Settlement | `stl_settlement_adjustment` | |
| 76 | Settlement | `stl_settlement_payment` | |
| 77 | Settlement | `stl_external_settlement` | |
| 78 | Notification | `ntf_template` | |
| 79 | Notification | `ntf_history` | |
| 80 | Notification | `ntf_batch_queue` | |
| 81 | Community | `cmt_review` | |
| 82 | Community | `cmt_rating` | |
| 83 | Community | `cmt_qna` | 통합 (PRODUCT·ORDER) |
| 84 | Search | `sch_search_keyword` | |
| 85 | Search | `sch_auto_complete` | |
| 86 | Search | `sch_index_sync_history` | |
| 87 | Search | `sch_category_view_history` | |
| 88 | Search | `sch_category_view_daily` | |
| 89 | Audit | `adt_audit_log` | |
| 90 | Audit | `adt_trace_log` | |
| 91 | Audit | `adt_dlq` | |
| 92 | Audit | `adt_log_retention_policy` | |
| 93 | Audit | `adt_member_access_log` | 고객 정보 접근 이력 (개인정보보호) |
| — | 복제 | `config_code_replica` | |
| — | 복제 | `config_delivery_company_replica` | |
| — | 복제 | `catalog_standard_category_replica` | |
| — | 복제 | `vendor_fee_rate_replica` | |
| — | 복제 | `member_grade_discount_replica` | |

**총 101개 테이블 + 5개 복제 테이블 = 106개**

---

*Confidential | 3TOP | ERD v1.0 | 2026.06.22*
