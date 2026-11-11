---
name: backend-service-pattern
description: runNshop 백엔드(Spring Boot 공통 — Kotlin/Java 언어 무관) Controller·Service를 구현하거나 리팩토링할 때 사용. 레이어 경계(Controller→Service→MockLoader/Repository), Service 내부 4단계 구조(validation→mapper execute→dto convert), 코멘트·섹션 규칙, 공용 예외 처리를 다룬다. 코드 예시는 Kotlin이지만 구조 자체는 Java 구현에도 동일하게 적용된다. design-doc-to-code(공통)·screen-to-fe-code(React FE)의 백엔드 짝.
---

> **분류: 공통(표준)** — 이 skill은 특정 언어에 종속되지 않는다. 파생 프로젝트(예: Java+Spring Boot 구현)를 만들 때도 그대로 적용하고, 코드 예시만 해당 언어 문법으로 치환한다.

# 백엔드 Controller/Service 구현 패턴

## 레이어 경계 — Controller는 요청/응답만

```
Controller (요청 파싱 + 응답 반환만, 가공 로직 없음)
    → Service (validation + 데이터 접근 + 가공, 도메인당 단일 클래스)
        → MockLoader (프로토타입: JSON 로딩) / Repository·Mapper (DB 전환 후)
```

- **Controller는 `MockLoader`를 직접 주입받지 않는다.** Controller 생성자는 Service(들)만 주입받는다. Controller가 `mockLoader.load(...)`를 직접 호출하는 코드를 발견하면 Service로 옮기는 리팩토링 대상이다.
- 이렇게 분리해두면 DB 전환 시 Service 내부(`MockLoader` 호출부)만 `Repository`/Mapper 호출로 바뀌고 Controller는 전혀 바뀌지 않는다.
- Mock JSON은 "Repository/Mapper가 쿼리했다면 돌려줬을 전체 데이터셋"으로 간주한다. 그 데이터를 가공(필터/정렬/페이징/집계)하는 책임은 Service에 있다.
- Controller/Service 클래스를 앱(mobile/admin/partner)별로 나눌지, 서브도메인 단위로 통합할지는 **AI가 단독으로 결정하지 않는다** — `.kiro/steering/api-design-rules.md` "Controller/Service 분리 단위" 절의 절차(분리안/통합안을 제시하고 휴먼이 확정)를 따른다. 이미 결정된 서브도메인(예: Order)이 있으면 `deliverables/S3-상세설계/DP-클래스설계/{domain}.md`에 적힌 클래스/메서드 네이밍을 그대로 따른다 — 임의로 새 이름을 짓지 않는다.

## Service 메서드 내부 — 4단계 구조

목록 조회처럼 "필터+페이징+집계"가 섞이는 메서드는 아래 4단계로 명확히 나눈다. 프로토타입이라고 이 구조를 생략하지 않는다 — DB 전환 시 그대로 쿼리 구조에 대응되어야 한다.

```kotlin
fun getAdminOrders(filter: AdminOrderFilter): OrderListResponse {
    // ① validation — 형식/범위를 명시적으로 검증. 조용히 보정(coerceAtLeast 등)하지 않고 예외로 거부.
    val page = validatePage(filter.page)
    val size = validateSize(filter.size)
    validateDateRange(filter.from, filter.to)

    // ② mapper execute — list/count/summary가 섞여 있으면 쿼리 단위로 메서드를 분리한다.
    //    공유 조건(모든 쿼리가 쓰는 WHERE)과 쿼리별 전용 조건을 구분해서 섞지 않는다.
    val allOrders = loadAdminOrderDataset()                       // 조회 (DB: SELECT ... FROM ...)
    val sharedFiltered = applySharedFilters(allOrders, ...)        // 공유 조건 (keyword, dateRange)
    val summary = aggregateAdminSummary(sharedFiltered)           // summary 쿼리: 공유조건만, GROUP BY
    val listFiltered = sharedFiltered.filter { matchesStatus(...) } // list/count 쿼리 전용 조건 (status)
    val sorted = sortByOrderDateDesc(listFiltered)                  // list 쿼리의 ORDER BY
    val pageOrders = selectPage(sorted, page, size)                 // list 쿼리의 LIMIT/OFFSET
    val totalCount = countFiltered(sorted)                         // count 쿼리 (list와 동일 WHERE, LIMIT 없음)

    // ③ dto convert — Map<String, Any> 대신 명시적 DTO로 변환해서 반환한다.
    return OrderListResponse(orders = pageOrders, summary = summary, pagination = buildPagination(page, size, totalCount))
}
```

- **① validation**: `require()`는 쓰지 않는다(아래 "예외 처리" 참조 — `IllegalArgumentException`은 전역 핸들러가 400으로 받아주지만, 메시지를 코드화하려면 `BadRequestException`을 명시적으로 던지는 게 낫다).
- **② mapper execute**: list(목록)와 summary(집계)가 "검색조건은 같지만 상태 필터만 다르게" 적용돼야 하는 경우가 흔하다 (예: "요약 카드는 전체 상태 분포, 목록은 선택한 상태로 좁힘"). 이런 설계 의도가 있으면 반드시 코멘트로 명시한다 — 그냥 보면 버그처럼 보이기 쉽다. count는 메모리 리스트의 `.size`로 임시 대체해도 되지만, 메서드 이름과 코멘트에 "이건 나중에 별도 COUNT 쿼리가 된다"를 남긴다.
- **③ dto convert**: 응답 DTO는 해당 도메인의 `dto/` 패키지에 둔다. `DP-클래스설계/{domain}.md`에 이미 타입명이 정의돼 있으면(예: `OrderListResponse`) 그 이름을 그대로 쓴다.

> **Java 구현 시**: ①~④ 단계 순서와 레이어 경계는 동일하게 유지한다. 문법만 치환한다 — 예: `val`/`var` → `final`/일반 변수, data class → Java `record` 또는 Lombok `@Value`/`@Getter`, `require()` 기반 검증 → 명시적 `if` + 커스텀 예외 던지기. Controller/Service 클래스 분리 기준(최대 30개 메서드, 분리 시 휴먼 확정)도 언어와 무관하게 동일하게 적용한다.

가공 로직 없이 단순히 데이터를 그대로 반환하는 메서드(예: 상세 조회, 고정 응답)는 4단계를 전부 쓰지 않아도 된다 — 다만 Service를 거치는 것(레이어 경계)은 예외 없이 지킨다.

## 코멘트/섹션/분리 규칙

KDoc 작성, 섹션 주석(`// ── ... ──`)으로 채널(mobile/admin/partner) 구분, 메서드 30개 초과 시 휴먼 확정 절차는 `.kiro/steering/kotlin-guide.md`의 "코멘트 규칙"/"섹션 구분"/"Controller/Service 분리 기준" 절을 그대로 따른다 — 이 skill에서 별도로 반복하지 않는다(중복 방지, steering이 단일 원본).

## 공용 예외 처리

`com.runnshop.common.exception`에 공용 예외 유형과 전역 핸들러가 있다 — 전 도메인이 공유한다.

```kotlin
BadRequestException(code, message, detail)       // 400 — 파라미터/Body 형식 오류
UnauthorizedException(code, message, detail)      // 401 — 인증 필요
ForbiddenException(code, message, detail)         // 403 — 권한 없음
NotFoundException(code, message, detail)          // 404 — 리소스 없음
ConflictException(code, message, detail)          // 409 — 상태머신 위반(예: CANCEL_NOT_ALLOWED)
UnprocessableException(code, message, detail)     // 422 — 기한초과/만료 등
```

- Service의 validation/비즈니스 규칙 위반은 이 예외들을 `throw`한다 — `require()`나 직접 `ResponseEntity`를 만들어 반환하지 않는다.
- `code` 값은 DL-인터페이스명세의 "Error Responses" 표에 이미 정의된 code를 그대로 쓴다 (예: `ADDRESS_REQUIRED`, `STOCK_NOT_AVAILABLE`). 문서에 없는 새 케이스를 추가할 때만 신규 code를 짓는다.
- `GlobalExceptionHandler`(`@RestControllerAdvice`)가 이 예외들과 `IllegalArgumentException`, 그 외 모든 `Exception`을 `{code, message, detail}` 표준 응답(`KIRO_START.md` 에러 처리 표준)으로 변환한다 — Controller에서 try/catch로 직접 처리하지 않는다.

## 인증 미연동 구간 — Controller placeholder 규칙

실 인증(로그인 토큰 파싱)이 아직 연동되지 않은 구간에서 memberId/vendorId 같은 "요청자 식별값"이 필요하면, **Controller에 고정값 + TODO 주석**으로 둔다. Service 메서드 시그니처는 이미 그 식별값을 파라미터로 받는 모양으로 작성해, 인증 연동 시 Controller 쪽 한 줄만 바뀌고 Service는 그대로 유지되게 한다.

```kotlin
@PostMapping("/api/mobile/v1/my/orders/{orderSheetId}/pay")
fun placeOrder(@PathVariable orderSheetId: String, @RequestBody request: PayRequest): ResponseEntity<Any> {
    // memberId는 실 인증 연동 전 placeholder — 추후 Authorization 헤더 파싱으로 교체
    val memberId = 1L
    val data = orderService.placeOrder(memberId, orderSheetId, request)
    return ResponseEntity.ok(mapOf("code" to "SUCCESS", "data" to data))
}
```

- 고정값은 Service나 Repository 안에 숨기지 않고 Controller 메서드 본문 맨 앞에 둔다 — 인증 연동 시 수정할 위치가 한눈에 보여야 한다.
- 주석에 "무엇으로 교체될지"(`Authorization 헤더 파싱`, `X-Vendor-Id 헤더` 등)를 구체적으로 남긴다 — 단순히 "TODO"만 쓰지 않는다.
- 이 placeholder는 `coding-standards.md`의 "보안 요건 프로토타입 처리"(로그인·세션·권한체크 미적용)와 같은 맥락이다 — 화면 UI뿐 아니라 API 레이어도 동일하게 "항상 성공/고정값" 전제로 둔다.

## 타 도메인 Port 호출 — 3가지 유형과 실패 처리

타 도메인의 Port(이 도메인이 소유한 인터페이스, 제공 도메인이 구현 — 네이밍/구조는 아래 "Port 작성 규칙" 참조)를 호출할 때는 **②(mapper execute) 단계**에 포함시킨다 — 별도 단계가 아니라 "데이터 접근"의 한 종류다. 호출이 실패했을 때 어떻게 처리할지는 그 호출의 성격에 따라 3가지로 나뉜다. 목적은 **의존성을 늘리지 않는 것**이다 — 상대 도메인의 구체적인 실패 원인(타임아웃 종류, 5xx 코드 등)에 맞춰 분기하지 않는다. 그건 Order가 상대 도메인의 내부 사정을 알아야 한다는 뜻이라, 인터페이스로 분리한 의미가 없어진다.

1. **제한적 서비스 가능(단순조회) — 실패해도 전체를 막지 않는다.** 응답의 부가 정보(표시용 텍스트 등)를 가져오는 호출이 대상이다. 예: `memberApi.getMemberName()`/`getMemberNames()`(고객명), `vendorApi.getVendorName()`/`getVendorNames()`(판매자명). 이 값이 없어도 나머지 응답(주문 금액·상태·상품 등)은 그 자체로 의미가 있다. 호출을 `try/catch`로 감싸 실패 시 기존 "매핑표 밖" 폴백과 동일한 값으로 넘어간다(전체 요청을 500으로 죽이지 않는다). 다만 **정상적으로 null이 돌아온 경우(매핑표 밖)와 호출 자체가 실패한 경우는 로그로 구분**한다 — 둘 다 같은 폴백 문자열을 보여주더라도, 운영자가 "이게 데이터 누락인지 장애인지"를 추적할 수 있어야 한다.

2. **필수적 서비스(결제요청 등) — 실패하면 전체 실패.** 그 호출 자체가 요청의 핵심 목적인 경우다. 예: `paymentApi.requestPayment()`. 실패하면 트랜잭션 전체가 의미 없으므로 예외를 그대로 전파한다 — `@Transactional`이 그 이전 단계의 저장(`platformOrderRepository.save()` 등)까지 함께 롤백한다. 별도 복구 로직을 만들지 않는다.

3. **판단이 필요한 서비스(할인율/포인트/회원인증 등) — 결과를 Order의 비즈니스 규칙으로 판정.** 호출 자체는 성공했는데 결과가 "허용/거부" 판단이 필요한 경우다. 이 유형은 두 하위 패턴으로 나뉜다 — 핵심 차이는 "대체 가능한 안전한 기본값이 있는가"다.

   - **3-a. 거부 판정형**: 결과값 자체가 비즈니스 규칙 위반이라 요청을 더 진행할 수 없는 경우. 예: `memberApi.getPointBalance()`(잔액 초과), `promotionApi.validateCoupon()`(쿠폰 적용 불가). 호출이 실패(네트워크 등)하면 2번과 동일하게 전체 실패로 전파하고, 호출은 성공했지만 결과가 거부(`balance 미달`, `applicable=false`)면 Order가 **자신의 공용 예외**(`UnprocessableException` 등)를 던진다 — code는 DL-인터페이스명세에 이미 정의된 식별자를 재사용한다(예: `POINT_EXCEED`, `COUPON_NOT_APPLICABLE`). Port가 던진 예외를 그대로 다시 던지지 않는다 — Order가 자기 언어로 재해석해서 던진다.
   - **3-b. 안전한 기본값 대체형**: 계산에 실제로 쓰이는 값이지만, 못 구해도 **플랫폼/고객에게 손해가 가지 않는 쪽으로 대체해 서비스를 계속 제공**할 수 있는 경우. 예: 상품 할인율 조회 — Port 장애나 "적용되는 할인조건을 찾지 못함"일 때, 할인율을 0%(정가)로 간주하고 계속 진행한다. 왜 0%(미할인)가 안전한 기본값인지: 할인이 있다고 잘못 가정하면 플랫폼이 손해를 보고 결제 데이터가 틀어지지만, 할인 없음으로 가정하면 고객이 당장 그 할인만큼 손해를 보는 대신 데이터는 안전하고 **사후 보정(CS 환불 등)이 가능**하다 — "되돌릴 수 있는 쪽" 기본값을 쓴다. 단, 1번(단순조회)처럼 조용히 넘기지 않는다 — 실제 금액 계산에 영향을 준 대체이므로 `log.error`(WARN이 아니라 ERROR)로 남겨 사후 추적·보정 대상이 되게 한다.

어떤 유형인지 애매하면 두 질문으로 판단한다: "이 호출이 실패해도 응답이 여전히 의미가 있는가" → 의미 있으면 1번, 없으면 2번/3번. "실패 시 되돌릴 수 있는 안전한 기본값이 있는가" → 있으면 3-b, 없으면(요청 자체를 막아야 함) 2번 또는 3-a.

**1번(제한적 서비스 가능) 유형은 공용 private 헬퍼로 감싼다.** 호출마다 try/catch를 반복해서 작성하지 않고, 아래처럼 "실패 시 null + WARN 로그"를 한곳에 모은다 — `apiName` 파라미터로 어떤 Port 호출인지 로그에 남겨서, 매핑표 밖이라 정상적으로 null인 경우와 호출 자체가 장애난 경우를 운영자가 구분할 수 있게 한다(실제 Order 도메인 적용 사례).

```kotlin
/**
 * "제한적 서비스 가능(단순조회)" 유형의 Port 호출을 감싼다. 호출이 실패해도 그 예외를 호출자에게
 * 전파하지 않고 null을 반환해 응답 전체를 막지 않는다. 실패를 조용히 삼키지 않고 apiName을 포함한
 * WARN 로그를 남겨, 매핑표 밖이라 정상적으로 null인 경우와 호출 자체가 실패한 경우를 구분한다.
 */
private fun <T> callWithFallback(apiName: String, call: () -> T): T? =
    try {
        call()
    } catch (e: Exception) {
        log.warn("타 도메인 Port 호출 실패 — $apiName, 폴백값으로 계속 진행: ${e.message}", e)
        null
    }

// 사용 예
val memberNames = callWithFallback("MemberApi.getMemberNames") { memberApi.getMemberNames(ids) }
```

2번(필수적 서비스)·3번(판단필요)은 이 헬퍼로 감싸지 않는다 — 예외가 그대로 전파되어야 트랜잭션 롤백/재해석 로직이 동작한다.

## Port 작성 규칙 — 패키지/네이밍/시그니처

Port는 "이 도메인이 다른 도메인의 데이터/기능이 필요할 때 거는 호출 계약"이다. 구현체는 반드시 제공 도메인에 있다 — 소유(인터페이스)와 구현이 분리되는 것이 핵심이다.

- **소유권**: 인터페이스는 **소비하는 도메인**의 `{domain}.port` 패키지에 둔다 (예: Order가 Member를 호출하면 `com.runnshop.order.port.MemberApi`를 Order 쪽에 둔다 — Member 쪽에 두지 않는다). 구현 클래스는 **제공하는 도메인**의 `service` 패키지에 두고(`member.service.MemberService`가 `order.port.MemberApi`를 구현), Spring DI가 그 구현체를 소비 도메인의 Service에 인터페이스 타입으로 주입한다. 소비 도메인은 제공 도메인의 Mock 파일 경로·테이블명·구현 세부사항을 전혀 참조하지 않는다.
- **네이밍**: 클래스명은 `{Domain}Api` 패턴(PascalCase) — `MemberApi`, `VendorApi`, `PaymentApi`, `PromotionApi`. "Public" 접두어는 쓰지 않는다(과거 `PublicApi` 네이밍에서 간소화된 결정, 사유: `IPayment`식 `I` 접두어나 `inf` 패키지명 등 다른 대안보다 헥사고날 아키텍처 표준 용어 "port"가 더 명확함 — PublicApi → Port 리네임 전례, `deliverables/.../DP-클래스설계/common.md` §5 참조).
- **배치/단건 시그니처 분리**: 목록(N건) 화면에서 행마다 Port를 호출하면 N+1 호출이 된다. 단건용(`getMemberName(id)`)과 배치용(`getMemberNames(ids): Map<Id, Name>`)을 각각 시그니처로 둬서, 목록 Service는 배치 메서드로 한 번에 조회한다.
- **DTO**: Port가 반환하는 DTO(`PointInfo`, `PaymentInfo`, `PaymentResult` 등)는 Port 파일과 같은 파일에 정의한다. 1차 근거 문서(`DP-클래스설계/common.md`)에 이미 필드가 정의돼 있으면 그대로 따르고, 없으면 신규로 채우되 그 사실을 KDoc에 "완전 신규 — 1차 근거 없음"으로 남긴다(`work-scope.md` 1차 근거 우선 원칙).
- **실패 처리**: 호출 실패/결과 판정 처리는 위 "타 도메인 Port 호출 — 3가지 유형과 실패 처리" 절을 따른다.

## Domain(Entity)/Repository 작성 규칙

- **PK 타입**: ERD에 명시된 타입을 그대로 쓴다(1차 근거 우선). 별다른 지정이 없으면 `Long` + `@GeneratedValue(strategy = GenerationType.IDENTITY)`를 기본값으로 채택한다 — String/ULID 등 대체 타입은 실제로 필요한 사유(외부 노출 식별자 등)가 있을 때만 쓴다(order-admin-erd-redesign에서 String/ULID 안을 검토했다가 ERD 리터럴 그대로인 Long/IDENTITY로 확정한 전례).
- **연관관계 cascade**: 애그리거트 루트(예: `PlatformOrder`)가 자식 Entity(`Order`, `PlatformOrderDiscount`)를 소유하는 구조면 `@OneToMany(cascade = [CascadeType.ALL], orphanRemoval = true)`를 쓰고, 자식은 **자체 Repository를 두지 않는다** — 루트의 Repository를 통해서만 저장/삭제된다. 비정규화 FK 컬럼(예: `OrderItem.platformOrderId`)이 실제 id를 필요로 하면 "1차 저장(자식 없이 save → id 확보) → 2차 저장(자식 포함 save)"의 2단계 저장 패턴을 쓴다.
- **fetch 전략**: 연관관계는 기본 `FetchType.LAZY`로 선언한다. 상세 조회처럼 연관 Entity를 바로 써야 하는 메서드는 Repository에 `@EntityGraph(attributePaths = [...])`를 붙인 전용 메서드(`findDetailById`)를 따로 둬서 즉시 로딩한다 — 목록/기본 조회까지 전부 즉시 로딩으로 만들지 않는다.
- **`MultipleBagFetchException` 회피**: 컬렉션 연관관계(`@OneToMany`, List 타입) 2개 이상을 같은 `@EntityGraph`/fetch join에 동시에 넣지 않는다 — Hibernate가 예외를 던진다(items+claims를 동시에 fetch join 시도한 사례). 둘 다 필요하면 하나만 EntityGraph로 즉시 로딩하고 나머지는 LAZY로 둬서 접근 시 별도 쿼리 1회를 추가로 허용한다(단건 조회 기준으로는 허용 범위).
- **soft delete 필드**: 삭제 가능한 Entity는 `isDeleted: Boolean`, `deletedAt: LocalDateTime?`, `deletedBy: String?` 3개 필드를 세트로 둔다(물리 삭제 대신 논리 삭제, ERD 원문 컬럼 기준).
- **채번/카운트 쿼리**: `countByXxxBetween(from, to): Long` 같은 derived query는 구현 코드 없이 Spring Data JPA 메서드 시그니처만 선언하면 자동 구현된다 — 직접 `@Query`를 작성하지 않는다.
- **Repository 분리 기준**: 단건 조회·연관관계 탐색(JPA, master 계정)은 `repository/`, 목록·동적 검색조건·집계(MyBatis, slave 계정)는 `mapper/`로 역할을 분리한다. 목록 조회를 JPA Repository에 넣지 않는다(아래 "Mapper 작성 규칙" 참조).

## Mapper(MyBatis) 작성 규칙

- **역할 분리 기준**: 검색조건(keyword/status/날짜범위 등)이 동적으로 섞이는 목록·건수·집계 쿼리는 MyBatis(`mapper/` 패키지, slave 계정, 읽기전용)로 작성한다. 연관관계를 즉시 로딩해야 하는 단건 상세 조회는 JPA(`repository/`, master 계정)로 작성한다 — 하나의 조회를 두 기술로 나눠서 중복 구현하지 않는다.
- **파일 위치**: Kotlin 인터페이스(+Row DTO)는 `com.runnshop.{domain}.mapper` 패키지, SQL은 `resources/mapper/{domain}/{MapperName}.xml`에 둔다. `@Mapper` 어노테이션 없이 `namespace`(XML)로 인터페이스를 연결한다(MyBatis-Spring 설정에 스캔 경로가 등록돼 있다는 전제).
- **공유조건/전용조건 분리**: 여러 쿼리(list/count/summary)가 공통으로 쓰는 WHERE 조건은 `<sql id="listWhere">`처럼 별도 fragment로 뽑아 `<include refid="...">`로 재사용한다. summary(집계) 쿼리가 list보다 적은 조건만 쓰는 경우(예: status 필터는 목록에만, 전체 상태 분포는 summary에) 전용 fragment(`summaryWhere`)를 따로 둔다 — 하나의 fragment에 조건을 다 넣고 파라미터로 켜고 끄지 않는다. 이 설계 의도는 Kotlin 인터페이스 쪽 KDoc에도 "왜 다른지" 남긴다(안 그러면 버그처럼 보인다).
- **Row DTO**: Mapper가 반환하는 결과 매핑용 데이터 클래스(`OrderRow` 등)는 **원시 FK 값만** 담는다. 표시용 이름(고객명/판매자명 등 타 도메인 소유 데이터)을 SQL `CASE`나 서브쿼리로 채우지 않는다 — 그 변환은 Service가 해당 도메인의 Port(`MemberApi.getMemberNames()` 등)를 배치 호출해서 수행한다(Mapper가 타 도메인 테이블을 직접 JOIN하지 않는다는 원칙).
- **nullable 처리**: "매핑표 밖" 값(마스터 데이터에 없는 코드 등)은 SQL에서 `NULL`을 그대로 반환하고, Kotlin 쪽 Row DTO 필드를 nullable(`String?`)로 선언한다 — SQL에서 임의의 기본 문자열로 대체하지 않는다. 기본값 대체가 필요하면 Service 단계(④ dto convert)에서 수행한다.
- **count 쿼리**: list와 동일한 WHERE(페이징 조건 제외)를 공유하는 `count{Name}` 메서드를 별도로 둔다 — list 결과의 `.size`로 대체하지 않는다(페이징된 목록은 전체 건수를 반영하지 못한다).

## 비동기 처리 — DB 아웃박스 + 별도 컨슈머/배치 앱(업무 처리는 API 호출)

브로커(Kafka/RabbitMQ)가 없는 현재, 비동기 후속 처리(예: 재고차감 → PG 요청)는 **DB 아웃박스 + 별도 컨슈머 앱**으로 구현한다. **컨슈머와 배치는 API 서버와 별도 애플리케이션**(`api/runNshop-consumer` 등)이며, 역할 분담은 다음과 같다. 배치도 같은 구조를 따른다(스케줄 + 대상 조회·상태 관리는 배치 앱, 업무 처리는 API 호출).

```
API(Service)        ── 같은 트랜잭션 ──▶ 상태 변경 + ord_outbox_event(PENDING) INSERT(적재만) → 즉시 응답
Consumer 앱(@Scheduled) ── 이벤트 조회 / 이벤트 상태 변경(DONE·재시도·FAILED) / 후속 이벤트 적재 = 컨슈머 소유
                       ── 업무 처리만 API 호출: POST /api/internal/v1/order-events/process
API(InternalController → Handler @Transactional) ──▶ 타 도메인 Port 호출 + 주문 상태 전이 + 이력, 처리 후 업무 상태(result) 반환
```

- **컨슈머 앱의 책임**: 스케줄, 이벤트 테이블(`ord_outbox_event`) 조회·상태 변경(JDBC, master 계정), 호출 결과에 따른 후속 이벤트 적재(예: 결과 `STOCK_DEDUCTED` → `PAYMENT_REQUESTED`), 재시도·종결 관리. **업무 로직(재고차감·주문 상태 전이·PG 요청)은 컨슈머 앱에 두지 않는다** — 전부 API 호출이다.
- **API의 책임**: 이벤트 테이블을 조회하지 않는다(적재만). 내부 API는 `{eventType, platformOrderId, payload}`를 받아 업무를 처리하고 `result`(처리 후 업무 상태: STOCK_DEDUCTED/STOCK_FAILED/DEPOSIT_PENDING/SKIPPED)를 반환한다. 재시도 소진 시 컨슈머가 `give-up` API로 업무 실패 전이를 요청한다.
- **내부 API는 채널명 `internal`(`/api/internal/v1` 하위)** 을 쓰고 외부에 노출하지 않는다(`api-design-rules.md`).
- **API 처리는 멱등해야 한다.** 이미 처리된 주문이면 재처리 없이 현재 업무 상태를 `result`로 돌려준다(컨슈머가 API 성공 후 DONE 기록 전에 장애가 나도 재호출로 복구). 타 도메인 Port도 `requestId`로 멱등하게 만든다(예: `CatalogApi.deductStock(requestId, items)`).
- **이벤트 1건 = 트랜잭션 1개**(API 처리 단위). 비즈니스 거부(재고 부족 등)는 예외가 아니라 결과값으로 받아 상태를 `*_FAILED`로 전이하고 이벤트는 DONE(사유는 `last_error`)으로 종결한다. 호출 실패(연결/5xx)는 컨슈머가 재시도 횟수를 올리고 PENDING으로 남기며, 한도(기본 3회) 도달 시 FAILED로 종결하고 `give-up`을 호출한다.
- **Port가 도메인 경계를 넘는 트랜잭션을 분리해야 하면** 제공 도메인 구현에 `REQUIRES_NEW`를 둔다(예: `StockService.deductStock` — 재고 부족 롤백이 호출한 Handler의 주문 상태 갱신 트랜잭션까지 롤백시키지 않도록).
- **컨슈머 다중 실행 지원**: 처리량이 필요하면 컨슈머 앱을 여러 개 띄운다. 이벤트는 **점유(claim)** 방식이다 — `UPDATE ... WHERE id IN (SELECT ... WHERE status='PENDING' AND next_attempt_at <= now() ORDER BY id LIMIT n FOR UPDATE SKIP LOCKED) RETURNING`으로 가져가며 PROCESSING(`locked_at`, `locked_by`)으로 바꿔 인스턴스끼리 겹치지 않는다. 점유 후 임대 시간(`lease-seconds`, 기본 60초) 안에 끝나지 않은 이벤트(컨슈머 장애)는 어느 인스턴스든 PENDING으로 되돌려 재처리하므로 **API 처리는 임대 만료 후 중복 호출돼도 안전(멱등)** 해야 한다. 시각 비교는 인스턴스 시계 차이를 피하려고 DB `now()`를 쓴다. API 서버 인스턴스 수는 제한이 없다(스케줄러가 API에 없다).
- **재시도 백오프**: 호출 실패는 PENDING으로 되돌리되 `next_attempt_at = now() + backoff × 실패횟수`로 간격을 둔다(`retry-backoff-seconds`, 기본 5초) — API가 잠깐 내려가도 재시도를 몇 초 만에 소진하지 않는다.
- **부분 실패는 단위별로 멱등 처리**: 한 이벤트가 여러 하위 작업(예: 주문의 SKU 여러 개 재고 차감)을 포함하면 하위 작업을 독립 트랜잭션(`REQUIRES_NEW`)으로 처리하고 성공분을 멱등 키(예: `cat_stock_deduction`의 request_id+sku_id)로 기록한다. 일부만 실패하면 API는 `STOCK_PARTIAL` 같은 결과를 반환하고(주문 상태 불변), 컨슈머가 실패로 기록해 재시도하면 **실패한 하위 작업만** 다시 수행한다. 재시도를 소진하면 `give-up`에서 성공분을 되돌리는 보상(`CatalogApi.restoreStock`)을 수행하고 주문을 실패 상태로 전이한다.
- 상태 전이마다 `OrderStatusHistoryService.record()`로 이력을 남긴다(사유에 처리 내용 요약).
- 새 테이블(아웃박스 등)은 수동 SQL(`resources/db/*.sql`)로 만들고 **master 계정 소유 + slave SELECT 권한**을 부여한다(슈퍼유저로 실행하면 owner가 달라 앱이 접근하지 못함).
- KDoc에 `/api/.../**` 같은 와일드카드 경로를 그대로 적지 않는다(`/**`가 중첩 주석을 열어 컴파일이 깨진다 — 아래 자가 점검 첫 항목과 동일).

## 확장 지점은 SPI + 레지스트리(모듈 추가만으로 확장)

새 PG·결제수단처럼 **종류가 계속 늘어나는 대상**은 `if/when` 분기나 허용 목록을 소비 도메인에 두지 않고, 제공 도메인에 **SPI(인터페이스) + 레지스트리(Spring 빈 자동 수집) + DB 카탈로그/라우팅 테이블**로 둔다. 소비 도메인(Order·Claim)은 안정된 Port(`PaymentApi`)만 쓰고 수단·PG 코드를 하드코딩하지 않는다. 모듈 추가 변경은 제공 도메인의 모듈 패키지와 설정 데이터로 한정되어야 하며, 모든 모듈은 공통 계약 테스트 킷을 통과한다. (결제 모듈 구조: `deliverables/S3-상세설계/DP-클래스설계/payment.md` "결제 모듈 확장 구조")

## 커밋 전 자가 점검 — AI 생성 코드 가독성 체크리스트

AI가 작성한 코드는 사람 리뷰 없이 그대로 쌓이면 아래 패턴이 반복해서 섞여 들어간다. 코드를 작성한 직후, 커밋하기 전에 스스로 점검한다 (실제로 Order 도메인 DB 연동 테스트 작업 중 전부 발견된 사례).

- **KDoc(`/** ... */`) 안에 코드 예시·파일 패턴을 적을 때 `*/`가 포함되는지 확인한다.** `*.xml` 같은 와일드카드 패턴을 KDoc 안에 그대로 적으면 `*/`가 주석을 조기 종료시켜 그 뒤의 코드가 전부 깨진다 (실제로 `classpath:mapper/order/*.xml`을 KDoc에 적어 컴파일 에러가 난 사례). 코드 예시가 필요하면 백틱(`` ` ``)으로 감싸거나, `*`가 포함된 패턴은 "resources/mapper 하위 전체"처럼 말로 풀어서 쓴다.
- **생성한 주석을 다시 읽고 오타를 확인한다.** 특히 한글 조사·명사 끝맺음("쪽"을 "쪽"이 아닌 다른 글자로 치는 등)은 기계적으로 놓치기 쉽다.
- **중간에 틀린 API를 추측해서 넣었다가 다시 쓴 코드(placeholder, 미완성 빈 등)가 최종 파일에 남아있지 않은지 확인한다.** 컴파일이 안 되는 임시 코드를 거쳐 정답에 도달하는 과정 자체는 괜찮지만, 그 흔적(죽은 import, 안 쓰는 빈 정의)이 최종본에 남으면 안 된다.
- **함수 파라미터를 선언했지만 본문에서 쓰지 않는 경우, 그 이유를 함수 시그니처 바로 옆(또는 KDoc 1줄)에서 바로 알 수 있게 한다.** 주석이 함수 본문 중간에 멀리 떨어져 있으면 "왜 안 쓰는 파라미터를 받는지"가 시그니처만 보고는 안 보인다.
- **코드를 수정할 때 그 코드를 설명하는 주변 코멘트도 같이 갱신한다.** "지금은 X를 하지만 Y로 전환되면 Z가 된다"는 식의 미래 서술형 코멘트는, 실제로 전환이 일어난 뒤에도 과거 서술이 그대로 남아 최신 코드와 어긋나기 쉽다(코멘트-코드 drift). 메서드 하나만 전환했다면 그 코멘트도 "이 메서드는 전환됨/이 메서드는 아직 전환 전"으로 쪼개서 갱신한다.
- **`Map<String, Any>` 같은 동적 타입을 쓸 때, 서로 다른 스키마(필드명)를 하나의 메서드 안에서 `a ?: b` 식으로 암묵적으로 흡수하지 않는다.** 예: `order["customer"] ?: order["customerName"]`처럼 두 호출부(admin/partner)가 다른 필드명을 쓰는데 메서드 하나가 둘 다 받아주면, 호출부가 실제로 어떤 스키마인지 그 메서드 밖에서는 알 수 없다. 호출부별로 필드명을 명시하거나, 호출 전에 공통 스키마로 변환하는 별도 매핑 함수를 둔다.
- **반복되는 문자열 리터럴(Mock 파일명, 테이블명 등)은 상수로 뽑는다.** 메서드마다 같은 문자열을 하드코딩하면 오타가 나도 컴파일 타임에 안 걸리고 런타임에야 발견된다.

## 적용 절차

1. 대상 Controller/Service 파일을 읽고, 위 규칙(레이어 경계·4단계·코멘트·예외) 중 어긋나는 지점을 찾는다.
2. `deliverables/S3-상세설계/DP-클래스설계/{domain}.md`에서 클래스/메서드 네이밍이 이미 정의돼 있는지 먼저 확인한다(`work-scope.md` 1차 근거 우선 원칙).
3. 수정 후 `./gradlew compileKotlin`(또는 `clean compileKotlin`)으로 컴파일 확인.
4. `./gradlew bootRun`으로 서버 기동 후 curl로 정상 케이스 + validation 실패 케이스(400 응답 확인) 둘 다 검증. 서버 종료.
5. 이 패턴은 Order 도메인에서 처음 정립됐고 다른 도메인(member/catalog/promotion/vendor/config)에는 아직 전체 적용되지 않았다 — 그 도메인 코드를 다음에 건드릴 때 이 skill을 적용해 점진적으로 맞춘다. 기존 코드가 이 패턴에서 벗어나 있다는 사실만으로 지금 작업 범위 밖에서 먼저 나서서 고치지 않는다(범위 확인 후 진행).

## 참고 steering
- `.kiro/steering/kotlin-guide.md` — 패키지 구조, 코멘트/섹션/분리 기준 (이 skill의 steering측 근거)
- `.kiro/steering/api-design-rules.md` — URL Prefix(내부 API `internal` 채널 포함), Controller 분리 단위 휴먼결정 절차
- `.kiro/steering/mock-data-rules.md` — Mock 파일 위치/네이밍
- `.kiro/steering/work-scope.md` — 1차 근거 우선 원칙, 도메인 작업 범위
