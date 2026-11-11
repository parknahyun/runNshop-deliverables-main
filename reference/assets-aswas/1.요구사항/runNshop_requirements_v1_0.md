# runNshop 요구사항 정의서

> 작성 주체: 3TOP 2본부  
> 문서 버전: v1.0  
> 작성일: 2026.06.25  
> 기준 산출물: 정책서 v1.0·BC v1.0·ERD v1.0·프로세스 v1.0  
> 상태: 확정 (Confirmed)

---

## 목차

1. [문서 개요](#1-문서-개요)
2. [플랫폼 공통](domains/02-common.md)
3. [회원 (Member)](domains/03-member.md)
4. [상품·카탈로그 (Catalog)](domains/04-catalog.md)
5. [프로모션 (Promotion)](domains/05-promotion.md)
6. [주문 (Order)](domains/06-order.md)
7. [결제 (Payment)](domains/07-payment.md)
8. [배송 (Delivery)](domains/08-delivery.md)
9. [클레임 (Claim)](domains/09-claim.md)
10. [정산 (Settlement)](domains/10-settlement.md)
11. [입점사 (Vendor)](domains/11-vendor.md)
12. [커뮤니티 (Community)](domains/12-community.md)
13. [전시·검색 (Display·Search)](domains/13-display-search.md)
14. [운영·시스템 (Config·Audit)](domains/14-config-audit.md)
15. [비기능 요구사항](domains/15-nfr.md)
16. [미확정 항목](domains/16-open-items.md)

> 각 장은 `domains/` 폴더 아래 도메인별 파일로 분리되어 있습니다. 이 문서는 개요·분류 기준을 담은 인덱스입니다.

---

## 요구사항 분류 기준

| 구분 | 코드 | 설명 |
|------|------|------|
| 기능 요구사항 | FR | 시스템이 수행해야 하는 기능 |
| 비기능 요구사항 | NFR | 성능·보안·가용성 등 품질 속성 |
| 제약 사항 | CR | 기술·법적·운영 제약 |

| 우선순위 | 의미 |
|---------|------|
| P1 | 런칭 필수 (Must Have) |
| P2 | 런칭 권장 (Should Have) |
| P3 | 2단계 (Nice to Have) |

---

## 1. 문서 개요

### 1.1 시스템 개요

runNshop은 러닝 전문 e커머스 플랫폼으로 3개 애플리케이션으로 구성된다.

| 애플리케이션 | URL | 대상 | 채널 |
|-----------|-----|------|------|
| 고객 웹 | www.runNshop.com | 일반 고객 | 모바일 웹 (360px) |
| 플랫폼 어드민 | admin.runNshop.com | 플랫폼 운영자 | PC 웹 |
| 입점사 BO | partners.runNshop.com | 입점사 담당자 | PC 웹 |

### 1.2 기술 스택

| 항목 | 기술 |
|------|------|
| 백엔드 | Spring Boot + Kotlin |
| 프론트엔드 | React + Next.js |
| DB | PostgreSQL + MyBatis |
| 캐시 | Redis |
| 검색 | Elasticsearch |
| 파일 | AWS S3 |
| 이벤트 | Outbox Pattern |
| 배포 | Docker Compose → Kubernetes |

### 1.3 아키텍처

- Modular Monolith (1단계) → MSA (2단계)
- 12개 Bounded Context
- 107개 DB 테이블 + 5개 복제 테이블

---

## 도메인별 요구사항

| 장 | 도메인 | 코드 | 파일 |
|----|--------|------|------|
| 2 | 플랫폼 공통 | FR-COM | [domains/02-common.md](domains/02-common.md) |
| 3 | 회원 (Member) | FR-MBR | [domains/03-member.md](domains/03-member.md) |
| 4 | 상품·카탈로그 (Catalog) | FR-CAT | [domains/04-catalog.md](domains/04-catalog.md) |
| 5 | 프로모션 (Promotion) | FR-PRO | [domains/05-promotion.md](domains/05-promotion.md) |
| 6 | 주문 (Order) | FR-ORD | [domains/06-order.md](domains/06-order.md) |
| 7 | 결제 (Payment) | FR-PAY | [domains/07-payment.md](domains/07-payment.md) |
| 8 | 배송 (Delivery) | FR-DEL | [domains/08-delivery.md](domains/08-delivery.md) |
| 9 | 클레임 (Claim) | FR-CLM | [domains/09-claim.md](domains/09-claim.md) |
| 10 | 정산 (Settlement) | FR-STL | [domains/10-settlement.md](domains/10-settlement.md) |
| 11 | 입점사 (Vendor) | FR-VND | [domains/11-vendor.md](domains/11-vendor.md) |
| 12 | 커뮤니티 (Community) | FR-CMT | [domains/12-community.md](domains/12-community.md) |
| 13 | 전시·검색 (Display·Search) | FR-SCH | [domains/13-display-search.md](domains/13-display-search.md) |
| 14 | 운영·시스템 (Config·Audit) | FR-CFG, FR-AUD | [domains/14-config-audit.md](domains/14-config-audit.md) |
| 15 | 비기능 요구사항 | NFR | [domains/15-nfr.md](domains/15-nfr.md) |
| 16 | 미확정 항목 | - | [domains/16-open-items.md](domains/16-open-items.md) |

---

*Confidential | 3TOP | 요구사항 정의서 v1.0 | 2026.06.25*
