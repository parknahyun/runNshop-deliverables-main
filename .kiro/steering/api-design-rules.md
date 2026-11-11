---
inclusion: always
---
# API 설계 규칙

## URL Path Prefix 규칙

Prefix 형식을 **`/api/{channel}/{version}/**`** 로 고정한다 — 채널이 버전보다 앞에 온다. 채널명은 `mobile`/`admin`/`partner`로 통일한다 (mock 파일 채널명과 동일 — `mock-data-rules.md` 참조). 현재 `{version}`은 전 채널 공통으로 `v1`이다.

| 앱 | 채널명 | Path Prefix |
|----|--------|------------|
| 플랫폼 고객웹 | `mobile` | `/api/mobile/v1/**` |
| 플랫폼 어드민 | `admin` | `/api/admin/v1/**` |
| 플랫폼 판매자 | `partner` | `/api/partner/v1/**` |

**내부(시스템 간) API — 채널명 `internal`**: 별도 컨슈머/배치 앱 등 서비스 내부 호출 전용 API는 `/api/internal/v1/{resource}` 를 쓴다(예: `POST /api/internal/v1/order-events/process`). 고객/어드민/판매자 화면이 호출하지 않으며 Gateway/Nginx에서 외부 접근을 차단한다. 비동기 처리 구조는 `backend-service-pattern` skill의 "비동기 처리 — DB 아웃박스 + 별도 컨슈머/배치 앱" 절 참조.

**채널을 버전보다 앞에 두는 이유**: 이 Prefix는 접근 통제 경계로도 쓰인다. 채널이 맨 앞에 있으면 Gateway/Nginx 레벨에서 `/api/admin/**` 같은 패턴 하나로 버전에 상관없이 해당 채널 전체를 통제(허용/차단)할 수 있다. 버전을 앞에 두면(`/api/v1/{channel}/**`) 버전 전환은 한 번에 되지만 채널별 접근 통제 패턴이 버전마다 늘어난다 — 이 프로젝트는 채널 간 접근 통제(어드민/판매자/고객웹 분리)가 우선순위가 높아 채널을 앞에 둔다.

**Controller/method를 찾기 쉬운 구조는 이 순서와는 별개다**: Spring MVC는 세그먼트 순서와 무관하게 `@GetMapping`에 적힌 전체 경로 문자열로 매칭하므로, "채널이 앞인지 버전이 앞인지"는 코드 탐색 편의성에 영향을 주지 않는다. 리소스명(`orders`, `products`)으로 Controller를 찾기 쉽게 만드는 요인은 "Controller/Service 분리 단위"(아래 섹션, 서브도메인 단위로 통합)이다 — 즉 `/api/{channel}/{version}/orders/**`로 들어오는 요청이 전부 `OrderController` 하나로 모이기 때문이다.

> 변경 이력: 고객웹 Prefix는 과거 `/api/v1/**`(채널명 없음)였으나, 세 채널의 Prefix 표기를 대칭화하기 위해 `/api/mobile/v1/**`로 변경했다 (전사 적용 — Order 도메인에 한정되지 않음). 이 변경은 백엔드 전체 Controller 매핑, FE `lib/api.ts`의 PREFIX 상수, DL-인터페이스명세의 모든 API 경로 표기에 반영한다.

## URL에 도메인(업무영역)은 노출하지 않는다

URL은 `/api/{channel}/{version}/{resource}` 형태로 **리소스 중심**으로만 구성한다. `order`, `catalog`, `payment` 같은 도메인명은 URL에 넣지 않는다 — 도메인은 백엔드 패키지 구조(`com.runnshop.{domain}`)와 Mock 파일 폴더(`mock/{domain}/`, `mock-data-rules.md`)에서만 쓰이는 내부 개념이다.

- **이유 1 (REST 관례)**: 클라이언트는 "이 데이터가 어떤 백엔드 패키지/서비스에서 처리되는지" 알 필요가 없고, 알게 하면 구현 세부사항이 노출된다.
- **이유 2 (MSA 전환 대비)**: `KIRO_START.md`에 "MSA 전환 시: 도메인 패키지 = 독립 서비스 분리 단위"가 이미 명시돼 있다. URL에 도메인이 없으면 서비스 경계가 바뀌어도(예: `order` 패키지의 `shipping`을 별도 `logistics-service`로 분리) API Gateway 라우팅 규칙만 수정하면 되고 클라이언트(FE)는 영향받지 않는다. URL에 도메인을 노출했다면 서비스 재편 시 URL도 함께 바뀌어 하위호환이 깨진다.
- 예: `GET /api/admin/v1/orders` (O), `GET /api/admin/v1/order/orders` (X — "order" 중복 노출)

## mobile 채널의 "본인 소유 리소스"는 `/my/{resource}`

mobile(고객) 채널에서 **로그인한 회원 본인 소유** 데이터를 다루는 리소스는 예외 없이 `/api/mobile/v1/my/{resource}` 형태를 쓴다 (`orders`, `claims`, `cart`, `payment-methods`, `payments` 등).

- **이유**: `orders`/`claims`처럼 admin·partner 채널에도 같은 이름의 리소스가 존재하면, mobile의 `orders`가 "전체"인지 "본인 것"인지 리소스명만으로 구분이 안 된다. `my`를 붙여 "본인 전용"임을 구조적으로 보장한다.
- **지금 admin/partner에 대응 리소스가 없는 것(`cart`, `payment-methods`)도 동일하게 `my`를 적용**한다 — CS가 고객을 대신해 장바구니에 담아주거나 결제수단을 등록해주는 기능이 추후 추가될 수 있어, 그때 `admin/v1/cart`가 생겨도 `mobile/v1/my/cart`와 충돌하지 않도록 미리 대비한다.
- **보안 근거**: "본인 것"임을 쿼리 파라미터(`?memberId=1234`)로 넘기지 않고 path(`/my/`)로 고정 + 인증 토큰(Bearer memberId)으로만 판별한다. 쿼리 파라미터 방식은 다른 회원 ID로 치환하는 IDOR(Insecure Direct Object Reference) 공격에 노출된다.
- **예외**: 특정 회원 소유가 아닌 공용 카탈로그성 리소스(상품, 기획전 등)는 `my`를 붙이지 않는다. 예: `GET /api/mobile/v1/exhibitions`, `GET /api/mobile/v1/products/{id}`.

| 채널 | 리소스 성격 | 예시 |
|---|---|---|
| admin | 전체/검색 | `GET /api/admin/v1/orders` |
| partner | 자기 매장 | `GET /api/partner/v1/orders` |
| mobile | 본인 소유 | `GET /api/mobile/v1/my/orders` |
| mobile | 공용(비소유) | `GET /api/mobile/v1/exhibitions` |

## Controller 분리 기준

### 앱 전용 — 별도 Controller
```kotlin
@RequestMapping("/api/mobile/v1/orders")  // 고객웹 전용
@RequestMapping("/api/admin/v1/orders")   // 어드민 전용
@RequestMapping("/api/partner/v1/orders") // 판매자 전용
```

### 공용 — 하나의 메서드에 다중 매핑
```kotlin
@GetMapping("/api/mobile/v1/products/{id}", "/api/admin/v1/products/{id}", "/api/partner/v1/products/{id}")
```

## 규칙
- 동일 로직 3개 앱 사용 → 하나의 메서드에 3개 URL 매핑
- 앱별 응답/권한 다르면 → 별도 Controller 분리
- 프로토타입: Controller → MockLoader → JSON 반환

## Controller/Service 분리 단위 — 휴먼 검토·결정 필수 영역

**Controller와 Service를 앱별로 쪼갤지, 서브도메인 단위로 합칠지는 AI가 단독으로 확정할 수 없다 — 휴먼(담당자)이 면밀히 검토하고 결정해야 하는 사항이다.** 업무 영역의 실제 특성(앱별 응답/권한 차이, 조직의 코드 소유 경계, 향후 변경 가능성 등)에 달려 있어 보편 규칙으로 미리 정할 수 없다. DL(인터페이스 명세)만 보면 앱별로 쪼개는 게 자연스러워 보이고, DM(시퀀스)에서 업무 흐름을 보면 Service가 공유되니 합치는 게 자연스러워 보이는 식으로, 보는 관점에 따라 결론이 달라진다. 그래서 AI는 아래 절차를 매번 거친다 — "이전에 이렇게 했으니 다음도 이렇게"로 기계적으로 복사하지 않는다.

1. 해당 서브도메인의 DL-인터페이스명세에서 앱별 요청/응답 스키마·권한을 비교한다.
2. Service가 이미 공유 구조인지, 메서드 분기만으로 로직이 충분히 명확한지 확인한다.
3. **AI는 분리안·통합안 두 가지를 구체적으로(Controller 목록, 메서드 매핑) 작성해 휴먼 담당자에게 제시만 한다. 최종 결정은 AI가 내리지 않고 휴먼의 명시적 확정을 거쳐야 적용한다.** 임의로 과거 사례를 다른 서브도메인/도메인에 그대로 복사해 "이미 결정된 것"처럼 처리하지 않는다.
4. 확정된 결과는 해당 도메인의 `DP-클래스설계/{domain}.md`(패키지 구조)와 `DM-시퀀스/readme.md`(해당 도메인 섹션)에 "이 서브도메인에 대한 결정"으로 기록한다 — 다른 도메인에 적용되는 보편 규칙처럼 서술하지 않는다.
5. 이후 실제 업무가 바뀌어 분리/통합 기준이 안 맞게 되면, 담당자가 변경을 요청하고 그 시점에 다시 1~4를 거쳐 재검토한다 — 이때도 최종 결정은 휴먼이 한다.
