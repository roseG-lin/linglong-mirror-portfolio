# -*- coding: utf-8 -*-
"""站点契约测试（P0/P1 验收 + 回归防线）。P2 已由用户明确回滚。

跑法（站点根目录）：python -m pytest tests/ -q
"""
from __future__ import annotations

import re
import subprocess
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


SKIP_DIRS = {".git", "_shots", "downloads", "node_modules"}


def html_files() -> list[Path]:
    return sorted(
        p for p in ROOT.rglob("*.html")
        if not (set(p.relative_to(ROOT).parts) & SKIP_DIRS)
    )


# ---------------- P0 · 对外口径 ----------------

def test_p0_01_salary_band_is_current():
    assert "15-20K" not in read("index.html")
    assert "12-15K" in read("index.html")
    for f in ("llms.txt", "llms-full.txt"):
        assert "15-20K" not in read(f), f


def test_p0_02_no_qinshou_claim():
    for f in ("index.html", "os/index.html", "llms.txt", "llms-full.txt"):
        assert "亲手" not in read(f), f


def test_p0_03_product_count_single():
    idx = read("index.html")
    assert 'data-count="12"' not in idx
    assert re.search(r'data-count="15">0</span><small>\+</small></div><div class="l">玲珑', idx)
    for m in re.finditer(r"(\d+)\s*款玲珑", idx):
        assert m.group(1) == "15", m.group(0)
    os_html = read("os/index.html")
    assert re.search(r"\{\s*n:\s*15,\s*suffix:\s*'\+',\s*label:", os_html)
    for m in re.finditer(r"(\d+)\s*款玲珑", os_html):
        assert m.group(1) == "15", m.group(0)


def test_p0_04_no_product_output_confusion():
    for f in ("index.html", "os/index.html"):
        t = read(f)
        assert "玲珑系列产物" not in t, f
        assert "20+ 产物" not in t, f


# ---------------- P1 · 转化路径 ----------------

def test_p1_05_hero_has_case_links():
    idx = read("index.html")
    hero = idx.split("<!-- 跑马灯")[0].split('<header id="hero">')[-1]
    links = set(re.findall(r'href="(case/[^"]+\.html)"', hero))
    assert len(links) >= 4, f"首屏案例链接只有 {len(links)} 个"


def test_p1_06_avatar_budget():
    idx = read("index.html")
    m = re.search(r'class="hero-avatar"[^>]*src="([^"]+)"', idx)
    assert m, "找不到 hero-avatar"
    p = ROOT / m.group(1)
    assert p.exists(), p
    assert p.stat().st_size < 150_000, f"{p.name} = {p.stat().st_size} bytes"


def test_p1_07_fonts_self_hosted():
    for p in html_files():
        assert "fonts.googleapis.com" not in p.read_text(encoding="utf-8"), str(p)
    css = read("css/fonts.css")
    assert "@font-face" in css and "Inter" in css
    files = list((ROOT / "assets" / "fonts").glob("*.woff2"))
    assert len(files) >= 5, f"字体文件只有 {len(files)} 个"
    assert sum(f.stat().st_size for f in files) < 600_000


def test_p1_08_home_has_four_case_thumbs():
    """首页四张卡片缩略图（现为概念封面，真截图在案例页里做证据图）。"""
    idx = read("index.html")
    assert "case-thumb" in idx
    for n in (1, 2, 3, 4):
        p = ROOT / "case" / "assets" / f"shot-0{n}.jpg"
        assert p.exists(), p
        assert p.stat().st_size < 120_000, p.name


def test_p1_09_wechat_channel_configured():
    idx = read("index.html")
    assert 'id="wechatSlot"' in idx
    assert 'var WECHAT_ID = "19200598917";' in idx


# ---------------- 回归防线 ----------------

def test_regression_inline_js_parses():
    """内联脚本必须能被 JS 引擎解析（防止删代码留下残块）。"""
    node = shutil.which("node")
    assert node, "需要 node 做语法检查"
    for page in ("index.html", "os/index.html"):
        html = read(page)
        for m in re.finditer(r"<script([^>]*)>(.*?)</script>", html, re.S):
            attrs, code = m.group(1), m.group(2)
            if "src=" in attrs or not code.strip():
                continue
            if "importmap" in attrs or "application/" in attrs or "text/template" in attrs:
                continue
            suffix = ".mjs" if "module" in attrs else ".js"
            with tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False, encoding="utf-8") as fh:
                fh.write(code)
                tmp = fh.name
            r = subprocess.run([node, "--check", tmp], capture_output=True, text=True, encoding="utf-8")
            Path(tmp).unlink(missing_ok=True)
            assert r.returncode == 0, f"{page}: 内联脚本语法错误 | {r.stderr[:300]}"


def test_regression_no_broken_local_links():
    """在役页面的站内链接必须存在。"""
    from urllib.parse import unquote
    pages = [ROOT / "index.html", ROOT / "os" / "index.html"]
    pages += sorted((ROOT / "case").glob("0*.html"))
    pages += sorted((ROOT / "folio").glob("*.html"))
    missing = []
    for page in pages:
        html = page.read_text(encoding="utf-8")
        for ref in re.findall(r'(?:href|src)="([^"]+)"', html):
            if ref.startswith(("http", "mailto:", "tel:", "#", "javascript:", "data:")):
                continue
            if "' +" in ref or "${" in ref:
                continue
            path = unquote(ref.split("#")[0].split("?")[0])
            if not path:
                continue
            target = (ROOT / path.lstrip("/")) if path.startswith("/") else (page.parent / path)
            target = target.resolve()
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                missing.append(f"{page.relative_to(ROOT)} -> {ref}")
    assert not missing, "死链: " + " | ".join(missing[:10])


def test_p1_10_video_local_and_budget():
    """背景视频已本地化：不再外链 CloudFront，≤6MB，带 poster。"""
    os_html = read("os/index.html")
    assert "cloudfront.net" not in os_html, "仍有外链视频"
    assert 'preload="none"' in os_html
    assert re.search(r'poster="\.\./assets/bg-poster\.jpg(\?v=\d+)?"', os_html), "poster 未设置"
    v = ROOT / "os" / "assets" / "bg-loop.mp4"
    assert v.exists() and v.stat().st_size < 6_000_000, v.stat().st_size if v.exists() else "missing"


def test_every_entry_page_declares_one_h1():
    """入口页恰好一个 h1（noscript 兜底标题不计）：读屏与 SEO 才有唯一主标题。

    folio 与 os 的首屏字标是 SVG/div 组字，视觉充当标题，因此补了 .sr-only 的 h1。
    """
    pages = ["index.html", "404.html", "folio/index.html", "os/index.html"]
    pages += [f"case/{p.name}" for p in sorted((ROOT / "case").glob("*.html"))]
    bad = []
    for rel in pages:
        src = read(rel)
        src = re.sub(r"<noscript>.*?</noscript>", "", src, flags=re.S | re.I)
        src = re.sub(r"<template.*?</template>", "", src, flags=re.S | re.I)
        n = len(re.findall(r"<h1\b", src, flags=re.I))
        if n != 1:
            bad.append(f"{rel}:{n}")
    assert not bad, "h1 数量不为 1 → " + ", ".join(bad)
