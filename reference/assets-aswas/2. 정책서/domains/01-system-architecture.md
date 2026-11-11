# 러닝 커머스 플랫폼 정책서 — 1. 시스템 아키텍처 정책

> 상위 문서: [runNshop_policy_v1_2.md](../runNshop_policy_v1_2.md)
> 문서 버전: v3.4 | 상태: 초안 (Draft)

---

## 1.0 설계 원칙

플랫폼 설계는 아래 6개 원칙을 기반으로 한다. 원래 MSA + Kafka 스펙에서 Modular Monolith + Outbox Pattern으로 변경하였으나 설계 원칙은 동일하게 유지한다.

| # | 원칙 | 구현 방식 |
|---|------|----------|
| 1 | **도메인 중심 아키텍처** | 12개 업무 도메인 기반 Bounded Context 설계 |
| 2 | **Runtime 선택 실행 가능 구조** | Frontend·Backend·Consumer·Batch 로컬·개발서버 선택 실행 |
| 3 | **운영 안정성 우선** | Outbox Pattern + 재시도 3회 + DLQ + 모니터링 |
| 4 | **Event-driven Architecture** | Outbox + Spring Event Consumer → 2단계 Kafka 전환 |
| 5 | **독립 배포 가능 구조** | 모듈 단위 설계 → 2단계 K8s 독립 배포 |
| 6 | **Spec 기반 개발 프로세스** | AI 9대 공정 기반 Spec → 코드 생성 흐름 |

### Runtime 선택 실행 구조

DB·Redis·Elasticsearch는 개발서버 공용 인프라로만 제공한다. 로컬은 애플리케이션(Frontend·Backend·Consumer·Batch)만 실행하며, 개발 착수 전 프레임워크가 필수 인프라 접속 환경을 제공해야 한다.

| 컴포넌트 | 로컬 (Local) | 개발서버 (Dev) |
|---------|------------|--------------|
| Frontend | ✅ 로컬 실행 | ✅ 개발서버 실행 |
| Backend API | ✅ 로컬 실행 | ✅ 개발서버 실행 |
| Consumer | ✅ 로컬 실행 | ✅ 개발서버 실행 |
| Batch | ✅ 로컬 실행 | ✅ 개발서버 실행 |
| PostgreSQL | ❌ 로컬 미제공 | ✅ 개발서버 공용 |
| Redis | ❌ 로컬 미제공 | ✅ 개발서버 공용 |
| Elasticsearch | ❌ 로컬 미제공 | ✅ 개발서버 공용 |

### 로컬 실행 구조

```
프로토타입 환경 (prototype 프로파일)
    ├─ Frontend    (localhost:3000~3002)  → Backend Mock API
    └─ Backend     (localhost:8080)       → Mock JSON 반환 (DB·Redis·ES 미사용)

본개발 환경 (local 프로파일)
    ├─ Frontend    (localhost:3000~3002)  ─┐
    ├─ Backend     (localhost:8080)       ─┤→ 개발서버 PostgreSQL
    ├─ Consumer    (로컬 프로세스)         ─┤→ 개발서버 Redis
    └─ Batch       (로컬 수동 실행)       ─┘→ 개발서버 ES
```

### 프로파일 구성 기준

| 프로파일 | 용도 | 인프라 |
|---------|------|--------|
| `prototype` | 프로토타입 개발 | Mock JSON (DB·Redis·ES 미사용) |
| `local` | 로컬 개발·검증 | 개발서버 인프라 연결 |
| `dev` | 개발서버 전체 실행 | 개발서버 인프라 |
| `staging` | 스테이징 검증 | 스테이징 인프라 |
| `prod` | 운영 | 운영 인프라 |

> 프로토타입 단계에서는 `prototype` 프로파일로 실행하며, DB·Redis·ES 없이 Mock JSON만으로 동작한다.

### 개발 착수 전 필수 제공 항목

프레임워크가 개발 착수 전 아래 항목을 완료 상태로 제공한다.

| 항목 | 제공 주체 |
|------|----------|
| 개발서버 PostgreSQL·Redis·ES 접속 정보 | 인프라팀 |
| `application-local.yml` 템플릿 | 프레임워크 |
| `.env.example` 파일 | 프레임워크 |
| 초기 DB DDL 스크립트 | 프레임워크 |
| 초기 ES 인덱스 매핑 스크립트 | 프레임워크 |
| VPN / 허용 IP 설정 | 인프라팀 |

### 개발 착수 체크리스트

```
□ 개발서버 PostgreSQL 접속 확인
□ 개발서버 Redis 접속 확인
□ 개발서버 ES 접속 확인
□ application-local.yml 템플릿 제공
□ .env.example 파일 제공
□ 초기 DDL 스크립트 실행 완료
□ 초기 ES 인덱스 생성 완료
□ VPN / IP 허용 설정 완료
□ 로컬 Backend 기동 확인
□ 로컬 Consumer 기동 확인
```

## 1.1 기술 스택

### Frontend

| 대상 | 모듈명 | 기술 | 비고 |
|------|--------|------|------|
| 플랫폼 고객웹 | runNshop-mobile | Next.js 14+ (App Router) + TypeScript + Tailwind CSS | 모바일 360px, SSR 기반 SEO·성능 최적화 |
| 플랫폼 어드민 | runNshop-admin | Next.js 14+ (App Router) + TypeScript + Tailwind CSS | PC 1280px+, SPA 기반 관리 화면 |
| 플랫폼 입점사 | runNshop-partner | Next.js 14+ (App Router) + TypeScript + Tailwind CSS | PC 1280px+, SPA 기반 관리 화면 |

| 공통 라이브러리 | 용도 |
|---------------|------|
| React Query | 서버 상태 관리 |
| Zustand | 클라이언트 상태 관리 |
| Chart.js | 차트 (어드민/입점사) |

### Backend

| 항목 | 기술 | 비고 |
|------|------|------|
| 프레임워크 | Spring Boot 3.3 | |
| 언어 | Kotlin | |
| 실행 모듈 | runNshop-api (단일) | 12개 업무도메인 패키지로 분리 |
| 아키텍처 | Modular Monolith | com.runnshop.{order,catalog,member,...} |
| 인터페이스 | REST API | 앱별 URL path prefix로 접근 통제 |
| DB | PostgreSQL | 프로토타입: Mock JSON, 본개발: PostgreSQL |
| ORM | MyBatis | SQL 중심 |
| 인증 | JWT + Redis | Access/Refresh Token, 3디바이스 관리 |
| 캐시·세션 | Redis | 재고 선점·인증번호·블랙리스트·BO 세션 |
| 검색 | Elasticsearch | 상품·기획전·커뮤니티 통합 검색 |
| 파일 스토리지 | AWS S3 | 상품 이미지·심사 서류·정산서 PDF |

### Backend 앱별 API Path Prefix

| 앱 | API Path Prefix | 인증 방식 |
|----|----------------|----------|
| 플랫폼 고객웹 | `/api/v1/**` | JWT + Redis |
| 플랫폼 어드민 | `/api/admin/v1/**` | JWT + 세션 8시간 |
| 플랫폼 입점사 | `/api/partner/v1/**` | JWT + 2단계 인증 + 세션 3시간 |

> 하나의 Back-end에서 3개 앱의 API를 모두 서비스하되, path prefix로 접근 권한을 통제한다.
> 동일 비즈니스 로직을 여러 앱에서 사용하는 경우, 하나의 Controller 메서드에 다중 path를 매핑한다.

### 인프라

| 항목 | 기술 | 비고 |
|------|------|------|
| 클라우드 | AWS | |
| 컨테이너 | Docker | |
| 오케스트레이션 | Kubernetes | 2단계 MSA 전환 시 |
| CI/CD | GitHub Actions | |
| 메시지 브로커 | Kafka + Debezium | 2단계 MSA 전환 시 |
| 모니터링 | Prometheus + Grafana | Trace ID 기반 로그 추적 연동 |
| API 문서 | SpringDoc OpenAPI (Swagger) | Kiro IDE 연동 |

### Redis 활용 범위

| 용도 | Key 구조 | TTL |
|------|---------|-----|
| Refresh Token | `refresh:{member_id}:{device_id}` | 1시간 |
| Access Token 블랙리스트 | `blacklist:{jti}` | 토큰 잔여 유효시간 |
| 인증번호 임시 저장 | `otp:{phone_number}` | 3분 |
| 재고 선점 | `stock:lock:{product_id}:{sku_id}` | 30분 |
| 입점사 BO 세션 | `bo:session:{session_id}` | 30분 |

## 1.2 이벤트 처리 정책

### 이벤트 처리 방식

| 단계 | 방식 | 비고 |
|------|------|------|
| 1단계 (Monolith) | Outbox Pattern + Spring Event Consumer | Kafka 없음. 인프로세스 Consumer |
| 2단계 (Hybrid MSA) | Kafka + Debezium CDC | Outbox 테이블 → Kafka 자동 전환 |
| 3단계 (Full MSA) | Kafka | 전 도메인 브로커 기반 |

### Outbox Pattern 기반 이벤트 처리 (1단계)

모듈 간 비동기 이벤트는 **Transactional Outbox Pattern + Spring Event Consumer**로 처리한다.

```
[저장] 비즈니스 로직 + Outbox 테이블 저장 → 단일 DB 트랜잭션
[감시] Outbox Consumer (상시 대기 스레드)가 PENDING 레코드 즉시 감지
[처리] Spring @EventListener + @Async → 수신 모듈 Consumer에 전달
[완료] 성공/실패 상태 업데이트
```

### 배치 vs Consumer 처리 방식 비교

| 항목 | 배치 (Polling) | Consumer (채택) |
|------|--------------|----------------|
| 실행 방식 | 주기적 실행 (N초 간격) | 상시 대기·즉시 처리 |
| 처리 지연 | 폴링 주기만큼 지연 | 거의 즉시 |
| Kafka 필요 | 없음 | 없음 (인프로세스) |

### Outbox 테이블 상태값

| 상태 | 설명 |
|------|------|
| `PENDING` | 처리 대기 중 |
| `PROCESSING` | Consumer 처리 중 |
| `PROCESSED` | 처리 완료 |
| `FAILED` | 최종 실패 (운영팀 이관) |

### 재시도 및 실패 처리

| 항목 | 기준 |
|------|------|
| 재시도 횟수 | 최대 3회 |
| 재시도 간격 | 즉시 → 30초 → 1분 (점진적 백오프) |
| 최종 실패 시 | `FAILED` 상태 전환 + 운영팀 알림 + 수동 처리 |
| 프로세스 중단 복구 | 재기동 시 `PENDING`·`PROCESSING` 레코드 자동 재발행 |

### 2단계 MSA 전환 시 연결

```
1단계: Outbox Consumer (인프로세스 상시 감시)
    ↓
2단계: Debezium CDC가 Outbox 테이블 변경 감지
       → Kafka Topic 자동 발행
       → Kafka Consumer로 전환
       → 코드 변경 없이 브로커 교체
```

## 1.3 시스템 진화 정책

| 단계 | 아키텍처 | 배포 | 조건 |
|------|----------|------|------|
| 1단계 (기본) | Modular Monolith + Event-Driven | Docker Compose | 런칭 시점 |
| 2단계 | Hybrid MSA | Kubernetes (Pod 설계 완성 시) | 트래픽·도메인 복잡도 증가 시 |
| 3단계 | Full MSA | Kubernetes 전면 운영 | 서비스 안정화 및 팀 규모 성장 후 |

### 1단계 — Docker Compose 운영

```
컨테이너 구성 (4개)
    ├─ backend-api   (Spring Boot)
    ├─ consumer      (Spring Boot)
    ├─ batch         (Spring Boot)
    └─ frontend      (Next.js)

스케일 아웃: 수동 (docker-compose scale)
Load Balancing: 수동 설정
```

### 2단계 — Kubernetes 도입 기준

Kubernetes 도입은 **컨테이너 수**가 아닌 **Pod 설계 완성** 시점에 결정한다.

```
Pod 설계 완성 기준
    ├─ 분리할 도메인 서비스 확정
    ├─ Pod별 스케일 정책 정의
    ├─ Pod 간 네트워크 통신 방식 확정
    └─ Pod별 리소스 할당 기준 정의
```

### 자동 스케일 아웃 (K8s HPA)

Prometheus가 Pod 리소스 사용률을 수집하고 HPA가 자동으로 Pod를 증감한다.

```
Prometheus → Pod 사용률 수집
    ↓
HPA → 임계치 비교
    ↓
초과 시 → Pod 자동 추가 + Load Balancer 자동 연결
이하 시 → Pod 자동 감소
```

### 도메인별 스케일 아웃 기준 (2단계 예시)

| Pod | 주요 지표 | 임계치 |
|-----|---------|--------|
| backend-api | CPU 사용률 | 70% 초과 |
| consumer | Outbox PENDING 건수 | 1,000건 초과 |
| payment | CPU + HTTP 요청 수 | CPU 60% or 초당 500건 |
| batch | 메모리 사용률 | 80% 초과 |
| frontend | CPU 사용률 | 70% 초과 |

### Prometheus + Grafana 연동

| 도구 | 역할 |
|------|------|
| Prometheus | Pod 리소스 사용률 수집·HPA 메트릭 제공·알림 발송 |
| Grafana | Pod별 CPU·메모리·요청수 대시보드·스케일 아웃 이력 시각화 |

---

*Confidential | 3TOP | v3.4 | 2026.06.26*
