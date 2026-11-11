# 러닝 커머스 플랫폼 Bounded Context 정의서 — 13. Config

> 상위 문서: [runNshop_bounded_context_v1_0.md](../runNshop_bounded_context_v1_0.md)
> 문서 버전: v1.0 | 상태: 초안 (Draft)

---

## 핵심 책임

> 운영자 계정·롤·권한·공통코드·공지·약관·배너를 관리한다.

## 소유 데이터

| 엔티티 | 설명 |
|--------|------|
| `Operator` | 운영자 계정 |
| `Role` | 롤 (슈퍼관리자·MD·CS·정산담당·입점관리) |
| `Permission` | 권한 (롤별 메뉴·기능 접근 권한) |
| `CommonCode` | 공통코드 |
| `Notice` | 공지사항 |
| `Terms` | 약관 (유형·버전·시행일) |
| `Banner` | 배너 (위치·이미지·링크·노출기간) |

## 운영자 롤 정의

| 롤 | 주요 접근 권한 |
|----|-------------|
| 슈퍼관리자 | 전체 |
| MD | Catalog·Promotion·Search 조회·수정 |
| CS | Order·Claim·Member 조회·처리 |
| 정산담당 | Settlement·Vendor 조회·처리 |
| 입점관리 | Vendor 심사·계약·등급 관리 |

## 제공 API

| API | 설명 | 호출 도메인 |
|-----|------|-----------|
| `GET /config/permissions/{operator_id}` | 운영자 권한 확인 | Catalog·Vendor·Order |
| `GET /config/codes/{group}` | 공통코드 조회 | 전 도메인 |
| `GET /config/banners` | 배너 목록 | 프론트 |
| `GET /config/notices` | 공지사항 | 프론트 |

---

*Confidential | 3TOP | Bounded Context v1.0 | 2026.06.22*
