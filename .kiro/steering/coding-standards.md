---
inclusion: always
---
# 코딩 표준

## 공통 규칙
- 모든 데이터는 Back-end API를 통해 가져온다 (하드코딩 금지)
- 프로토타입 단계에서도 POST/PUT/DELETE 요청은 실제로 API를 호출한다
- API는 실제 저장 없이 성공 응답(Mock)을 반환한다
- Front-end는 API 응답 결과를 받아 사용자에게 알려준다 (예: "저장되었습니다")
- 화면 이동(네비게이션)은 모두 정상 동작해야 한다
- 유효성 검증(필수값, 형식 등)은 실제와 동일하게 구현한다
- 설계 문서(deliverables/)를 우선 참조하여 구현한다

## 앱별 스타일링 방식
| 앱 | 스타일링 | 구조 |
|----|---------|------|
| runNshop-mobile | Tailwind CSS | Header + Content + BottomNav (App Router) |
| runNshop-admin-react | 순수 CSS 클래스 (globals.css) | NavBar + TabBar + TabContent (MDI) |
| runNshop-admin-vue | 순수 CSS 클래스 (globals.css) | NavBar + TabBar + TabContent (MDI, Vue 3 + Vite SPA) |
| runNshop-partner | 순수 CSS 클래스 (globals.css, 틸 테마) | NavBar + TabBar + TabContent (MDI) |

## 네이밍 규칙
- 컴포넌트: PascalCase (ProductCard.tsx)
- 유틸/훅: camelCase (useProductList.ts)
- 상수: UPPER_SNAKE_CASE (MAX_CART_ITEMS)
- 백엔드 패키지: 소문자 (com.runnshop.{domain}) — Kotlin/Java 등 언어 무관 공통 규칙
- Mock 파일: {domain}__{METHOD}_{path}.json
- CSS 클래스: BEM 스타일 (.dash-card__header, .nav-item__label--active)

## Git 브랜치
- 형식: {type}/{app}-{설명}
- type: feat, fix, refactor, chore
- app: mobile, admin, partner, api, common

## 구현 완료 표시
- admin/partner 메뉴: `implemented: true` 추가 → 초록 원(●) 표시
- 미구현 화면: PlaceholderPage로 "아직 구현되지 않았습니다" 표시

## 보안 요건 프로토타입 처리
- 로그인·2FA·본인인증·재인증: 화면 UI 구현 + API 항상 성공 응답
- 세션 만료: 미적용 (항상 로그인 유지)
- 권한 체크: 미적용 (메뉴 전체 노출)
- 개인정보 마스킹: Mock 데이터에 적용 (홍*동, 010-****-5678)
- 인프라 보안(HTTPS, Nginx, JWT 검증): 미적용
