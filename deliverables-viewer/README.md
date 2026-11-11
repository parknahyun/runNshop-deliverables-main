# 산출물 웹 뷰어

레포 루트(`deliverables/`·`reference/` 등) 하위 모든 md 문서를 웹으로 탐색한다 (폴더 트리 메뉴, 전체 검색, 위키링크 `[[경로/파일|문구]]` 변환, PlantUML 다이어그램 렌더링).

## 실행
```
./run.sh        # http://127.0.0.1:8000  (문서 수정 시 자동 새로고침)
```

## 최초 1회 설치 (이미 .venv가 있으면 생략)
```
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
curl -L -o .venv/plantuml.jar https://repo1.maven.org/maven2/net/sourceforge/plantuml/plantuml/1.2024.7/plantuml-1.2024.7.jar
```
- Java가 필요하다(PlantUML). Graphviz는 불필요 — `plantuml-wrapper.py`가 smetana 레이아웃을 자동 적용한다.
- 정적 사이트로 빌드: `./.venv/bin/mkdocs build` → `.site/` (사내 웹서버·GitHub Pages 배포용)
- 설정: `mkdocs.yml`, 위키링크 변환: `hooks.py`
