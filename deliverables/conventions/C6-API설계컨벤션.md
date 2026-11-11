# C6 API설계컨벤션

> **수립 데드라인**: S3 인터페이스명세 작성 전 | **참고 대상**: DL 인터페이스명세, DM 시퀀스, DQ 프로그램목록
> **책임 경계**: C6는 외부 인터페이스(API Contract)를 정의한다. 내부 구현은 C3 아키텍처, 데이터는 C4, 이벤트는 C5를 따른다.

---

## 1. 목적

RESTful API의 URL 설계, 요청/응답 계약, HTTP 상태 코드, 에러 처리, 버저닝 규칙을 정의하여,
FE/BE 간 API 계약의 일관성을 확보한다.

---

## 2. API 기본 원칙

| 원칙 | 설명 |
|------|------|
| Resource 중심 | URL은 명사(리소스)로 표현, 행위는 HTTP Method로 |
| Command API 허용 | 단순 CRUD로 표현 불가한 업무 행위는 `POST /{resource}/{id}/{action}` 허용 |
| Contract First | API 계약(Request/Response)을 먼저 정의하고, 구현은 계약을 따름 |
| DTO 분리 | Entity를 API Request/Response에 직접 노출하지 않음 |
| 서버 검증 우선 | 모든 유효성 검증·금액 계산은 서버에서 수행 (C1 보안 원칙) |

---

## 3. URL / Resource 설계

### 3.1 API Prefix

| App | Prefix | 역할 |
|-----|--------|------|
| 고객웹 (mobile) | `/api/v1/**` | CUSTOMER |
| 어드민 (admin) | `/api/admin/v1/**` | ADMIN |
| 판매자 (partner) | `/api/partner/v1/**` | VENDOR |

> Prefix는 **라우팅 및 API 영역 구분**이다. 실제 접근 통제는 인증·인가 정책(C1)으로 수행한다.

### 3.2 Resource URL

| 규칙 | 예시 |
|------|------|
| 복수형 명사 | `/orders`, `/products`, `/claims` |
| 소문자 kebab-case | `/payment-methods`, `/shipping-address` |
| 계층 관계 | `/orders/{orderId}/items`, `/members/me/claims` |
| 행위 금지 (기본) | ✗ `/getOrders`, ✗ `/createProduct` |

### 3.3 Command API (행위형 예외)

> 단순 CRUD로 표현하기 어려운 **업무 행위(Domain Command)**는 행위형 URL을 허용한다.

```
POST /orders/{orderId}/cancel        ← 주문 취소
POST /orders/{orderId}/confirm       ← 구매확정
POST /orders/{orderSheetId}/pay      ← 결제 요청
POST /claims/{claimId}/shipping-payment  ← 배송비 결제
POST /claims/{claimId}/inspect-pass  ← 품질점검 합격
POST /claims/{claimId}/refund        ← 환불 처리
```

### 3.4 `me` API

| 패턴 | 용도 |
|------|------|
| `/members/me/orders` | 현재 로그인 사용자의 리소스 (JWT에서 memberId 추출) |
| `/members/{memberId}/orders` | 관리자가 특정 회원 리소스 조회 |

### 3.5 Path Parameter / Query Parameter

| 구분 | 용도 | 예시 |
|------|------|------|
| Path Parameter | 리소스 식별자 | `/orders/{orderId}` |
| Query Parameter | 조회 조건, 필터, 페이징, 정렬 | `?page=1&size=20&status=PAID&sort=createdAt&direction=desc` |

---

## 4. HTTP Method

| Method | 용도 | 멱등성 | 비고 |
|--------|------|--------|------|
| GET | 조회 | ✓ | Body 없음 |
| POST | 생성 / Command | ✗ | 재시도 시 Idempotency-Key 권장 |
| PUT | 전체 수정 | ✓ | |
| PATCH | 부분 수정 | 구현에 따라 다름 | 증분 연산이면 비멱등 |
| DELETE | 삭제 | ✓ | Soft Delete 또는 물리 삭제 |

### Idempotency-Key

| 규칙 | 적용 |
|------|------|
| 대상 | POST 요청 중 중복 실행 시 문제되는 API (주문생성, 결제) |
| 헤더 | `Idempotency-Key: {ULID}` |
| 서버 처리 | 동일 Key 재요청 시 이전 결과 반환 (중복 실행 방지) |
| 유효기간 | 24시간 |

---

## 5. Request

### 5.1 규칙

| 항목 | 규칙 |
|------|------|
| Content-Type | `application/json` |
| JSON property | **camelCase** |
| Path Parameter | camelCase (`{orderId}`, `{claimId}`) |
| Query Parameter | camelCase (`page`, `size`, `status`, `sort`) |
| 인증 | `Authorization: Bearer {token}` (프로토타입: 미적용) |

### 5.2 Request DTO 원칙

| 규칙 | 설명 |
|------|------|
| Entity 직접 노출 금지 | 별도 Request DTO 정의 |
| 유효성 어노테이션 | `@NotBlank`, `@Size`, `@Min`, `@Max` |
| 불필요 필드 금지 | API에 필요한 필드만 포함 |

---

## 6. Response

### 6.1 성공 응답

```json
{
  "code": "SUCCESS",
  "data": { ... }
}
```

### 6.2 목록 (Pagination)

```json
{
  "code": "SUCCESS",
  "data": {
    "items": [ ... ],
    "pagination": {
      "page": 1,
      "size": 20,
      "totalCount": 150,
      "totalPages": 8
    }
  }
}
```

| 항목 | 규칙 |
|------|------|
| page | 1-based |
| size | 최대 100 (기본 20) |
| sort | 필드명 (camelCase) |
| direction | `asc` / `desc` |
| 무한스크롤 (향후) | cursor 기반 `{ cursor, hasNext }` |

### 6.3 에러 응답

```json
{
  "code": "ORDER_ALREADY_CANCELLED",
  "message": "이미 취소된 주문입니다.",
  "errors": [
    {
      "field": "status",
      "code": "INVALID_STATUS",
      "message": "현재 상태에서 취소할 수 없습니다."
    }
  ],
  "traceId": "trc_01HXYZ..."
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `code` | string | ✅ | 비즈니스/서비스 오류 코드 (UPPER_SNAKE_CASE) |
| `message` | string | ✅ | 사용자 친화적 메시지 (FE 표시용) |
| `errors` | array | 선택 | 필드별 상세 에러 (유효성 검증 실패 시) |
| `traceId` | string | 선택 | 로그 추적 ID (운영 환경) |

### 6.4 code 의미

| 구분 | 역할 | 예시 |
|------|------|------|
| HTTP Status | 프로토콜 수준 상태 | 200, 400, 409, 500 |
| code | 비즈니스 오류 식별자 | `CART_FULL`, `STOCK_INSUFFICIENT`, `CARD_RESTRICTED` |

---

## 7. HTTP Status Code

| Status | 의미 | 사용 상황 |
|--------|------|-----------|
| 200 | OK | 조회, 수정 성공 |
| 201 | Created | 리소스 생성 성공 (POST) |
| 202 | Accepted | 비동기 처리 접수 (결제 요청) |
| 204 | No Content | 삭제 성공 (Body 없음) |
| 400 | Bad Request | 유효성 검증 실패, 잘못된 파라미터 |
| 401 | Unauthorized | 인증 필요 (토큰 없음/만료) |
| 403 | Forbidden | 인가 실패 (권한 없음) |
| 404 | Not Found | 리소스 없음 |
| 409 | Conflict | 상태 충돌 (이미 취소된 주문, 재고 부족, 중복 요청) |
| 422 | Unprocessable | 비즈니스 규칙 위반 (기한 초과, 금액 불일치) |
| 429 | Too Many Requests | Rate Limit 초과 |
| 500 | Internal Error | 서버 오류 (스택트레이스 미노출) |

---

## 8. 공통 규칙

### 8.1 DateTime

| 항목 | 규칙 |
|------|------|
| 기준 | **`LocalDateTime`(2026-10-27 확정)** — 시간대 정보 없이 서버 로컬 시각 그대로 사용, 변환 없음 |
| 저장 | `timestamp`(시간대 없음), 로컬 시각 |
| API 전달 | 표시용 일시 `yyyy-MM-dd HH:mm`(목록·상세), 전체 시각 ISO 8601 offset 없음(`2026-08-21T15:30:00`) |
| FE 표시 | 변환 없이 그대로 표시 |

### 8.2 ID / Enum

| 항목 | 규칙 | 예시 |
|------|------|------|
| ID 타입 | string (ULID) | `"ord_01HXYZ..."` |
| ID 네이밍 (JSON) | camelCase | `orderId`, `claimId`, `memberId` |
| Enum 값 | UPPER_SNAKE_CASE | `PAYMENT_COMPLETED`, `IN_DELIVERY` |

### 8.3 금액

| 항목 | 규칙 |
|------|------|
| 단위 | 원(KRW) 정수 |
| 타입 | number (int) |
| 할인 | 양수 저장, FE에서 `-` 표시 |

---

## 9. API Versioning

| 규칙 | 설명 |
|------|------|
| 위치 | URL Path (`/api/v1/`, `/api/v2/`) |
| v 증가 기준 | Breaking Change (필드 제거, 타입 변경, 응답 구조 변경) |
| v 유지 | Optional 필드 추가, 새 endpoint 추가 |
| 병행 운영 | 신버전 배포 후 구버전 6개월 유지 |
| 하위 호환 | Consumer(FE) 먼저 업데이트 → Producer(BE) 배포 |

---

## 10. Prototype / Mock API

> API 계약(Contract)은 실제 운영과 동일하게 유지한다. 데이터 영속화만 생략.

### 10.1 Mock 파일 규칙

| 항목 | 규칙 |
|------|------|
| 위치 | `api/runNshop-api/src/main/resources/mock/{channel}/` |
| 채널 | `v1/` (고객), `admin/` (어드민), `partner/` (판매자) |
| 파일명 | `{domain}__{HTTP_METHOD}_{API_PATH}.json` |
| 구분자 | `__` (이중 언더스코어)로 도메인과 API 분리 |
| Path 치환 | URL의 `/`를 `_`로, path parameter는 `{paramName}` 유지 |

**예시:**

| 파일명 | API |
|--------|-----|
| `order__GET_cart.json` | GET /api/v1/cart |
| `order__GET_members_me_orders.json` | GET /api/v1/members/me/orders |
| `catalog__GET_products_{productId}.json` | GET /api/v1/products/{productId} |
| `order__GET_admin_orders.json` | GET /api/admin/v1/orders |

### 10.2 HTTP Method별 동작

| Method | 프로토타입 동작 | 비고 |
|--------|----------------|------|
| GET | Mock JSON 반환 | 정상 동작 |
| POST | 성공 응답 반환 (영속화 없음) | Mutation은 실제 저장하지 않음 |
| PUT/PATCH | 성공 응답 반환 (영속화 없음) | |
| DELETE | 성공 응답 반환 (삭제 없음) | |

> **Prototype API는 실제 API Contract을 동일하게 유지한다.** Mock이 임의의 API를 만들지 않는다.

### 10.3 Controller 패턴

> 구현 상세는 C3 아키텍처 §4.3(Repository 추상화) 참조.
> 프로토타입에서는 MockRepository가 JSON 파일을 로딩한다.

---

## 11. 예시

### Resource API (CRUD)

```
GET    /api/v1/cart                     ← 장바구니 조회
POST   /api/v1/cart/items               ← 장바구니 담기
PATCH  /api/v1/cart/items/{id}/quantity  ← 수량 변경
DELETE /api/v1/cart/items/{id}           ← 장바구니 삭제
```

### Command API (업무 행위)

```
POST   /api/v1/orders/{sheetId}/pay           ← 결제 요청
POST   /api/v1/orders/{orderId}/cancel        ← 주문 취소
POST   /api/v1/orders/{orderId}/confirm       ← 구매확정
POST   /api/v1/orders/{orderId}/claims        ← 클레임 신청
POST   /api/admin/v1/claims/{claimId}/refund  ← 환불 처리
```

### 에러 응답 예시

```
HTTP/1.1 409 Conflict

{
  "code": "ORDER_ALREADY_CANCELLED",
  "message": "이미 취소된 주문입니다.",
  "traceId": "trc_01HXYZ..."
}
```

```
HTTP/1.1 400 Bad Request

{
  "code": "VALIDATION_FAILED",
  "message": "입력값을 확인해주세요.",
  "errors": [
    { "field": "quantity", "code": "MIN_VALUE", "message": "수량은 1 이상이어야 합니다." },
    { "field": "shippingAddress", "code": "REQUIRED", "message": "배송지를 입력해주세요." }
  ]
}
```

---

## 근거

| 항목 | 출처 |
|------|------|
| Path Prefix | `.kiro/steering/api-design-rules.md` |
| Mock 파일 규칙 | `.kiro/steering/mock-data-rules.md` |
| 에러 코드 체계 | DL 인터페이스명세 error_catalog |
| Command API 예시 | DM 시퀀스 — /cancel, /confirm, /pay, /refund 등 |
| 금액 int | C4 데이터모델링 — KRW 정수 |
| camelCase | C9 코딩컨벤션 — JSON property 규칙 |
| 서버 검증 | C1 보안 §3.2 Server Trust |
| Controller 패턴 | C3 아키텍처 §4.2~§4.3 |
