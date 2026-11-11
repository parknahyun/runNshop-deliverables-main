# -*- coding: utf-8 -*-
"""MkDocs 훅: Obsidian 스타일 위키링크 `[[경로/파일|표시문구]]`를 문서 링크로 변환한다.
대상은 docs 하위에서 경로 끝이 `경로/파일.md`인 문서를 찾아 연결하고, 못 찾으면 표시문구만 남긴다."""
import os, re, shutil

_WIKI = re.compile(r"\[\[([^\]|#]+)(#[^\]|]*)?(?:\|([^\]]*))?\]\]")
_index = {}


def on_files(files, config):
    _index.clear()
    for f in files.documentation_pages():
        _index.setdefault(f.src_uri.lower(), f.src_uri)
    return files


def _resolve(target):
    t = target.strip().lower()
    if not t.endswith(".md"):
        t += ".md"
    matches = [u for k, u in _index.items() if k == t or k.endswith("/" + t)]
    return sorted(matches, key=len)[0] if matches else None


def on_page_markdown(markdown, page, config, files):
    def sub(m):
        target, anchor, label = m.group(1), m.group(2) or "", m.group(3)
        text = (label or target).strip()
        dest = _resolve(target)
        if not dest:
            return text
        rel = os.path.relpath(dest, os.path.dirname(page.file.src_uri)).replace(os.sep, "/")
        return f"[{text}]({rel}{anchor})"
    return _WIKI.sub(sub, markdown)


def on_post_build(config):
    """LNB 트리 스타일(extra.css)을 사이트 assets에 복사한다 (docs 디렉터리를 건드리지 않기 위함)."""
    dest = os.path.join(config["site_dir"], "assets")
    os.makedirs(dest, exist_ok=True)
    shutil.copy(os.path.join(os.path.dirname(__file__), "extra.css"), os.path.join(dest, "extra.css"))
