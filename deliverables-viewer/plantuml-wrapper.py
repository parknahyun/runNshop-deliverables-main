#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""plantuml-markdown이 호출하는 PlantUML 실행 래퍼.
Graphviz(dot)가 없어도 클래스·상태 다이어그램이 그려지도록 smetana 레이아웃 pragma를 자동 삽입한다."""
import os, subprocess, sys

here = os.path.dirname(os.path.abspath(__file__))
jar = os.path.join(here, ".venv", "plantuml.jar")
data = sys.stdin.buffer.read().decode("utf-8")
if "!pragma layout" not in data:
    data = data.replace("@startuml", "@startuml\n!pragma layout smetana", 1)
proc = subprocess.run(
    ["java", "-Djava.awt.headless=true", "-jar", jar, *sys.argv[1:]],
    input=data.encode("utf-8"), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
)
sys.stdout.buffer.write(proc.stdout)
sys.stderr.buffer.write(proc.stderr)
sys.exit(proc.returncode)
