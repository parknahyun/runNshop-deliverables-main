# 파생 프로젝트 레지스트리

> `runNshop-docs`(허브)를 기준으로 파생된 구현 프로젝트 목록. 신규 파생이 생기거나 상태가
> 바뀔 때마다 이 표를 갱신한다. 분류/절차 기준은 `docs/methodology/파생프로젝트-가이드.md` 참조.

| 프로젝트 | 스택 | 레포 | 상태 | 비고 |
|---|---|---|---|---|
| `runNshop-react-kotlin` | React(admin/mobile/partner) + Kotlin/Spring Boot | 현재 메인 레포(분리 예정) | 운영 중(기존 구현) | Spring Boot 4.1.1 / Java 21 / Gradle 9.7.1 |
| `runNshop-vue-java` | Vue(admin) + Java/Spring Boot | 미생성 | 계획 | 추천 버전: OpenJDK(Temurin) 25 LTS, Spring Boot 4.1.1, Gradle 9.7.1, Lombok 1.18.44+ |

## 추천 버전 근거 (2026-11-05 기준)

| 항목 | 버전 | 지원 종료(EOS) |
|---|---|---|
| Spring Boot | 4.1.x | OSS: 2027-07-31 / 상업: 2028-07-31 |
| OpenJDK(Temurin) | 25 (LTS) | 커뮤니티 보안 지원 2031-09-30 |
| Oracle JDK | 25 (LTS) | 무료 2030-09-30 / 유료 Extended 2033-09-30 |
| Gradle | 9.7.1 | 고정 EOS 없음(현재+직전 메이저만 보안 패치) |
| Lombok | 최신(1.18.4x~) | EOS 개념 없음, 지속 업데이트 |

OpenJDK(Temurin)를 Oracle JDK 대신 추천하는 이유: 무료 보안 지원 기간이 더 길다(2031-09 vs 2030-09)
그리고 운영 환경 사용에 라이선스 제약이 없다.
