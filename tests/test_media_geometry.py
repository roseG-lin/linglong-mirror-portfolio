# -*- coding: utf-8 -*-
"""媒体几何契约 · 缩略图不许把界面截图裁成竖条。

背景：`<img>` 上的 height 属性是表现提示，CSS 的 `aspect-ratio` 只在另一维
为 auto 时才生效。首屏案例卡曾写死 width/height=1200x675（真实资源 1200x625），
配合竖长的渲染框 + object-fit:cover，把 1200 宽的界面截图左右各裁掉约三分之一，
截图里的句子被拦腰截断。

跑法（站点根目录）：
    python -m pytest tests/test_media_geometry.py -q

只读静态检查：不联网、不起浏览器。
"""
from __future__ import annotations

import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
SHOTS = sorted((ROOT / "case" / "assets").glob("shot-*.jpg"))


def jpeg_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:200000]
    i = 2
    while i < len(data) - 9:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            h, w = struct.unpack(">HH", data[i + 5:i + 9])
            return w, h
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
    raise ValueError(f"不是可解析的 JPEG：{path}")


def case_thumb_rule(src: str) -> str:
    m = re.search(r"\.case-thumb\s*\{([^}]*)\}", src)
    assert m, "index.html 里找不到 .case-thumb 规则"
    return m.group(1)


def aspect_of(rule: str) -> float:
    m = re.search(r"aspect-ratio\s*:\s*(\d+)\s*/\s*(\d+)", rule)
    assert m, ".case-thumb 未声明 aspect-ratio"
    return int(m.group(1)) / int(m.group(2))


# ---------- 案例卡缩略图 ----------

def test_four_shot_assets_share_one_ratio():
    sizes = {p.name: jpeg_size(p) for p in SHOTS}
    assert len(sizes) == 4, sizes
    ratios = {round(w / h, 3) for w, h in sizes.values()}
    assert len(ratios) == 1, f"四张截图比例不一致：{sizes}"


def test_case_thumb_height_is_auto():
    rule = case_thumb_rule(INDEX)
    assert re.search(r"height\s*:\s*auto", rule), (
        ".case-thumb 必须显式 height:auto —— 否则 <img height=...> 的表现提示会压过 aspect-ratio，"
        "把缩略图拉成竖条"
    )
    assert not re.search(r"(?<!-)\bheight\s*:\s*\d", rule), "不许给 .case-thumb 写死高度"


def test_case_thumb_ratio_matches_the_screenshot():
    rule = case_thumb_rule(INDEX)
    w, h = jpeg_size(SHOTS[0])
    want = w / h
    got = aspect_of(rule)
    assert abs(got - want) / want < 0.02, (
        f".case-thumb 的 aspect-ratio {got:.3f} 与截图真实比例 {want:.3f} 差超过 2%，"
        "object-fit:cover 会裁掉界面左右两侧的文字"
    )


def test_case_thumb_intrinsic_size_matches_the_file():
    m = re.search(r'<img class="case-thumb"[^>]*width="(\d+)"[^>]*height="(\d+)"', INDEX)
    assert m, "找不到 case-thumb 的 img 模板"
    declared = (int(m.group(1)), int(m.group(2)))
    real = jpeg_size(SHOTS[0])
    assert declared == real, f"模板声明 {declared[0]}x{declared[1]}，资源实际 {real[0]}x{real[1]}"


# ---------- 全站兜底 ----------

IMG_TAG = re.compile(r"<img\b[^>]*>", re.S)


def _attr(tag: str, name: str) -> str | None:
    m = re.search(r'\b%s\s*=\s*"([^"]*)"' % name, tag)
    return m.group(1) if m else None


def test_every_static_img_declares_the_real_ratio():
    """静态 img（模板拼接出来的除外）的 width/height 比例必须等于资源真实比例。"""
    offenders = []
    for html in sorted(ROOT.rglob("*.html")):
        if any(part in {".git", "_archive"} for part in html.parts):
            continue
        src = html.read_text(encoding="utf-8", errors="ignore")
        for tag in IMG_TAG.findall(src):
            w, h, s = _attr(tag, "width"), _attr(tag, "height"), _attr(tag, "src")
            if not (w and h and s) or s.startswith(("http", "data:", "//")) or "' +" in s:
                continue
            fp = (html.parent / s).resolve()
            if not fp.exists() or fp.suffix.lower() not in {".jpg", ".jpeg"}:
                continue
            rw, rh = jpeg_size(fp)
            if abs(int(w) / int(h) - rw / rh) > 0.01:
                offenders.append(f"{html.relative_to(ROOT)} -> {s}: 声明 {w}x{h}，实际 {rw}x{rh}")
    assert not offenders, "\n".join(offenders)
