# 러닝 커머스 플랫폼 정책서 — 15. 세션·보안 정책

> 상위 문서: [runNshop_policy_v1_2.md](../runNshop_policy_v1_2.md)
> 문서 버전: v3.4 | 상태: 초안 (Draft)

---

## 15.1 본인인증 정책

| 항목 | 기준 |
|------|------|
| 인증 방식 | 휴대폰 본인인증 (통신사 인증) |
| 인증 시점 | 회원가입 필수 단계 |
| SNS 로그인 시 | 최초 로그인 시 휴대폰 본인인증 필수 |
| 1인 1계정 | 동일 휴대폰 번호 중복 가입 불가 |
| 외국인 가입 | 외국인 등록증 기반 인증 (추후 지원) |

## 15.2 세션 관리

| 항목 | 고객 | 입점사 BO |
|------|------|----------|
| 세션 유지 시간 | 1시간 (마지막 활동 기준 갱신) | 30분 |
| 동시 로그인 | 허용, 최대 3디바이스 | 미허용 (단일 디바이스) |
| 초과 디바이스 처리 | 가장 오래된 세션 자동 만료 | — |
| 디바이스 관리 | 마이페이지에서 조회·강제 로그아웃 가능 | — |

## 15.3 비밀번호 정책

| 항목 | 고객 | 입점사 BO |
|------|------|----------|
| 최소 길이 | 8자 이상 | 8자 이상 |
| 조합 기준 | 영문자 + 숫자 필수 | 영문자 + 숫자 + 특수문자 필수 |
| 최대 길이 | 20자 | 20자 |
| 변경 주기 | 강제 변경 없음 | 강제 변경 없음 |
| 재사용 제한 | 최근 3개 재사용 금지 | 최근 3개 재사용 금지 |

## 15.4 비밀번호 찾기 인증

```
비밀번호 찾기 요청
    ↓
가입 시 등록한 휴대폰 번호 확인
    ├─ 휴대폰 있음 (일반)
    │       → 휴대폰 뒷자리 2자 노출 (010-****-**12)
    │       → 본인 확인 후 SMS 인증번호 발송
    │       → 인증 완료 → 비밀번호 재설정
    │
    └─ 휴대폰 없음 (비정상 계정 예외)
            → 이메일 인증 링크 발송 (유효시간 30분)
            → 인증 완료 → 비밀번호 재설정
```

## 15.5 로그인 보안

| 항목 | 기준 |
|------|------|
| 로그인 실패 허용 횟수 | 5회 |
| 5회 초과 시 | 30분 계정 잠금 |
| 잠금 해제 | 30분 경과 자동 해제 또는 이메일 인증 |
| 이상 로그인 탐지 | 평소와 다른 국가·IP 접근 시 이메일 알림 |

## 15.6 입점사 BO 추가 보안

| 항목 | 기준 |
|------|------|
| 주요 작업 재인증 | 정산 계좌 변경·대량 재고 수정 시 비밀번호 재확인 |
| IP 접근 제한 | 선택 적용 (입점사 요청 시 허용 IP 등록 가능) |

## 15.7 개인정보 마스킹 기준

| 항목 | 마스킹 기준 | 예시 |
|------|-----------|------|
| 휴대폰 번호 | 뒷자리 2자 노출 | 010-\*\*\*\*-\*\*12 |
| 이메일 | 앞 2자 + 도메인 노출 | ab\*\*\*\*@gmail.com |
| 이름 | 가운데 문자 마스킹 | 홍\*동 (3자) / 홍\*\*동 (4자) |
| 아이디 | 3번째부터 3자 유지, 나머지 마스킹 | ab**cde**\*\*\* |
| 계좌번호 | 뒷자리 4자 노출 | \*\*\*\*-\*\*-\*\*\*\*1234 |

## 15.8 공통 보안 기준

- HTTPS 전 구간 적용
- 개인정보 포함 API 응답 마스킹 처리
- 관리자 어드민 접근은 허용 IP 기반 제한

## 15.9 외부 접속 제어 정책 (Nginx 라우터 기반)

### 핵심 원칙

> 외부에서 Backend API 직접 접속 불가.  
> 모든 외부 요청은 Nginx Reverse Proxy를 통해서만 접근.  
> Nginx 라우터에 등록된 경로만 외부 접속 허용 (Whitelist 방식).  
> 라우터 미등록 경로는 기본 차단 (403).

### 외부 접속 채널 구분

| 채널 | 경로 패턴 | 대상 | 접속 제어 |
|------|---------|------|---------|
| 고객 API | `/api/v1/{resource}` | 고객 | Nginx 라우터 등록 |
| 어드민 API | `/api/admin/v1/{resource}` | 운영자 | Nginx 라우터 등록 + VPN/IP 제한 |
| 입점사 API | `/api/partner/v1/{resource}` | 입점사 | Nginx 라우터 등록 |
| Webhook | `/webhook/v1/{provider}/{event}` | PG사·배송사 등 외부 시스템 | Nginx 라우터 등록 + IP 화이트리스트 |

### 컴포넌트별 외부 접속 차단 기준

| 컴포넌트 | 외부 접속 | 이유 |
|---------|---------|------|
| backend-api | ❌ 차단 | Nginx 통해서만 접근 |
| consumer | ❌ 차단 | 내부 이벤트 처리 전용 |
| batch | ❌ 차단 | 내부 스케줄 실행 전용 |
| PostgreSQL | ❌ 차단 | 내부 네트워크만 |
| Redis | ❌ 차단 | 내부 네트워크만 |
| Elasticsearch | ❌ 차단 | 내부 네트워크만 |

### API 네이밍 패턴

```
내부 API (단일 정의)
    /{domain}/{resource}/{action}
    예) /orders/create
        /payments/confirm
        /deliveries/complete

외부 채널 (Nginx 라우터로 노출 제어)
    /api/v1/{domain}/{resource}         → 고객용
    /webhook/v1/{provider}/{event}      → 외부 시스템용
    /admin/v1/{domain}/{resource}       → 운영자용
```

### Nginx 라우터 등록 샘플

```nginx
# =============================================
# Case 1. /webhook 오픈 안 할 때
# /api 채널만 등록 → webhook 접속 차단
# =============================================

# 고객용 결제 확인 API (등록 O → 허용)
location /api/v1/payment/confirm {
    proxy_pass http://backend-api:8080/v1/payment/confirm;
    proxy_set_header X-Request-Source "api";
}

# webhook 경로 미등록 → 기본 차단 규칙에 의해 자동 차단


# =============================================
# Case 2. /webhook 오픈 할 때
# /api + /webhook 둘 다 등록
# =============================================

# 고객용 결제 확인 API (등록 O → 허용)
location /api/v1/payment/confirm {
    proxy_pass http://backend-api:8080/v1/payment/confirm;
    proxy_set_header X-Request-Source "api";
}

# PG사 Webhook 결제 확인 (등록 O → PG사 IP만 허용)
location /webhook/v1/payment/confirm {
    proxy_pass http://backend-api:8080/v1/payment/confirm;
    proxy_set_header X-Request-Source "webhook";

    allow 1.2.3.4;    # PG사 IP
    allow 1.2.3.5;    # PG사 IP (백업)
    deny all;         # 나머지 차단
}


# =============================================
# 공통 - 기본 차단 규칙 (모든 설정 하단)
# =============================================
location / {
    return 403;
}
```

### X-Request-Source 헤더 활용

Nginx가 요청 출처를 헤더로 Backend에 전달하며, Backend는 출처별 처리를 분기할 수 있다.

| 채널 | 헤더값 | Backend 활용 예시 |
|------|--------|----------------|
| `/api` | `X-Request-Source: api` | 고객 인증 검증 |
| `/webhook` | `X-Request-Source: webhook` | PG사 서명 검증 |
| `/admin` | `X-Request-Source: admin` | 운영자 권한 검증 |

### 라우터 등록 기준 예시

| 내부 API | /api 노출 | /webhook 노출 | /admin 노출 |
|---------|----------|--------------|------------|
| orders/create | ✅ 등록 | ❌ 미등록 | ❌ 미등록 |
| payments/confirm | ✅ 등록 | ✅ 등록 (PG사) | ❌ 미등록 |
| deliveries/complete | ❌ 미등록 | ✅ 등록 (배송사) | ❌ 미등록 |
| vendors/approve | ❌ 미등록 | ❌ 미등록 | ✅ 등록 |

### 2단계 K8s 전환 시

```
Nginx 라우터 → K8s Ingress Controller로 동일 구조 유지
    Ingress 규칙에 등록된 경로만 외부 노출
    미등록 경로 자동 차단
    IP 화이트리스트 → K8s NetworkPolicy로 전환
```

---

*Confidential | 3TOP | v3.4 | 2026.06.26*
