---
inclusion: always
---
# Mock 데이터 규칙

## 파일 위치 — 도메인 기준 폴더

> 아래 경로는 현재 Kotlin 구현(`api/runNshop-api`) 기준이다. 이 규칙 자체는 언어 무관 공통 규칙이며, 파생 프로젝트(예: Java 백엔드)는 **자기 백엔드 모듈의 `src/main/resources/mock/` 하위**에 동일한 구조(도메인 폴더 + 아래 파일명 규칙)를 그대로 적용한다 — 루트 모듈명만 바뀔 뿐 구조는 바뀌지 않는다.

```
api/runNshop-api/src/main/resources/mock/
├── order/           ← Order 도메인
├── catalog/         ← Catalog 도메인
├── member/          ← Member 도메인
├── payment/         ← Payment 도메인
├── promotion/       ← Promotion 도메인
├── settlement/      ← Settlement 도메인
├── vendor/          ← Vendor 도메인
├── notification/    ← Notification 도메인
├── community/       ← Community 도메인
├── search/          ← Search 도메인
├── config/          ← Config 도메인
└── audit/           ← Audit 도메인
```

- 폴더는 **도메인(업무영역) 기준**으로 나눈다 (12개 업무도메인 — 아래 "12개 업무도메인" 절 참조). 채널(admin/partner/mobile)로는 폴더를 나누지 않는다 — 하나의 도메인 폴더 안에 모든 채널의 mock 파일이 함께 들어간다.
- 채널 구분은 **폴더가 아니라 파일명**으로 표현한다 (아래 파일명 규칙 참조).

> 이전 버전(v1)은 `mock/{channel}/` 구조였다. 도메인 폴더 기준으로 변경한 이유: `MockLoader`가 이미 `load(domain, filename)` 성격의 공용 로더이고, 같은 도메인의 admin/partner/mobile mock을 한곳에서 보는 게 Controller/Service 코드와의 대응이 더 명확하기 때문.

## 파일명 규칙

```
{channel}__{HTTP_METHOD}_{API_PATH}.json
```
- 구분자: `__` (이중 언더스코어)로 **채널**과 API를 분리 (v1에서는 도메인과 API를 분리했으나, 도메인은 이제 폴더가 담당하므로 파일명에서는 뺀다)
- `{channel}`: `admin` | `partner` | `mobile` 중 하나. URL Path Prefix(`api-design-rules.md`)도 이 채널명으로 통일되어 `/api/{channel}/v1/**` 형태다(고객웹도 `/api/mobile/v1/**`).
- API_PATH: URL의 `/`를 `_`로 치환, 그 URL의 **Path Prefix(`/api/mobile/v1`, `/api/admin/v1`, `/api/partner/v1`)는 생략**하고 그 이후 경로만 쓴다 (채널은 이미 `{channel}` 토큰으로 표현했으므로 중복 기재하지 않음)
- path parameter는 `{param_name}` 형태로 유지하며, 실제 API의 파라미터명 표기(camelCase 등)와 무관하게 **snake_case로 표기**한다 (파일명 가독성을 위한 고정 관례)

### 예시
| 파일명 (폴더: `mock/{domain}/`) | API |
|--------|-----|
| `catalog/mobile__GET_products_{product_id}.json` | GET /api/mobile/v1/products/{product_id} |
| `order/mobile__GET_my_orders.json` | GET /api/mobile/v1/my/orders |
| `order/mobile__GET_my_orders_{order_id}.json` | GET /api/mobile/v1/my/orders/{orderId} |
| `order/mobile__GET_my_cart.json` | GET /api/mobile/v1/my/cart |
| `order/admin__GET_orders.json` | GET /api/admin/v1/orders |
| `order/admin__GET_orders_{order_id}.json` | GET /api/admin/v1/orders/{orderId} |
| `order/partner__GET_orders.json` | GET /api/partner/v1/orders |
| `vendor/partner__GET_home_summary.json` | GET /api/partner/v1/home/summary |

> `my`도 URL 경로의 일부이므로 Path Prefix(`/api/{channel}/{version}`)만 생략하고 `my`는 그대로 파일명에 포함한다 (`mobile__GET_my_orders.json`, "my_orders" — 생략 대상이 아님).

## 12개 업무도메인
order, catalog, member, payment, promotion, settlement, vendor, notification, community, search, config, audit

## 응답 구조 표준
```json
{ "code": "SUCCESS", "data": { ... } }
```

## 에러 응답
```json
{ "code": "ERROR_CODE", "message": "사용자 메시지", "detail": "디버그 정보" }
```
