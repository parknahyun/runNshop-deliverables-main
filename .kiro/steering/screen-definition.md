---
inclusion: manual
---
# 화면정의 참조

화면 프로토타입 작업 시 아래 문서를 기준으로 구현합니다.

## 화면정의서
#[[file:docs/6. 화면정의/runNshop_screen_definition_v1_0.md]]

## 와이어프레임
- 참조: `docs/6. 화면정의/runNshop_wireframe_v1_0.html`
- 스타일, 레이아웃, 컴포넌트 배치를 참고

## 앱별 화면 수
| 앱 | 화면수 | 해상도 |
|----|--------|--------|
| 플랫폼 고객웹 | 38개 | 모바일 360px |
| 플랫폼 어드민 | 80개 | PC 1280px+ |
| 플랫폼 판매자 | 40개 | PC 1280px+ |

## 화면정의서(DN) 폴더·파일 규칙
`deliverables/S3-상세설계/DN-화면레이아웃/` 문서를 만들거나 수정할 때 따릅니다. 상세는 해당 폴더 `readme.md` §0-1.

- 폴더는 도메인 기준: `{app}/{domain}/` (예: `admin/order/`, `mobile/claim/`)
- 문서는 화면 단위: `{화면ID}_{영문명}.md` (예: `SCR-M-001_cart.md`), 제목에 `[화면ID]` 표시
- 탭(MDI) 화면은 화면 ID 폴더 생성 후 탭 단위 문서: `SCR-A-002/SCR-A-002_detail.md`(컨테이너) + `SCR-A-002/SCR-A-002-T{n}_{영문명}.md`
- 파일을 옮기거나 이름을 바꾸면 상대 링크·목차(index.md, readme.md)·S4 기록을 함께 갱신
