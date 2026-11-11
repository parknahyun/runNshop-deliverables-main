#!/bin/sh
# 산출물 문서 웹 뷰어 실행: ./run.sh  →  http://127.0.0.1:8000
cd "$(dirname "$0")"
exec ./.venv/bin/mkdocs serve -a 127.0.0.1:8000
