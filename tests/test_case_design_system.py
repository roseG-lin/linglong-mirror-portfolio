# -*- coding: utf-8 -*-
"""case 作品演示页 · 设计契约测试（玲珑镜面 design.md v1.0）。

跑法（站点根目录）：
    python -m pytest tests/test_case_design_system.py -q

只读静态检查：不联网、不起浏览器。
"""
from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "case"
CSS = (CASE / "case.css").read_text(encoding="utf-8")
JS = (CASE / "case.js").read_text(encoding="utf-8")
PAGES = sorted(CASE.glob("*.html"))
PAGE_TEXT = {p.name: p.read_text(encoding="utf-8") for p in PAGES}


def css_without_tokens(text: str) -> str:
    """去掉 :root token、滚动条特例、reduced-motion 降级块，只留作用于 UI 的声明。"""
    text = re.sub(r"::-webkit-scrollbar[^{]*\{[^}]*\}", "", text)
    text = text.split("@media (prefers-reduced-motion: reduce)")[0]
    out = []
    for line in text.splitlines():
        if "--radius" in line or "--text" in line or "--hairline" in line or "--dur" in line:
            continue
        out.append(line)
    return "\n".join(out)


# ---------- 结构与单一事实源 ----------

def test_nine_case_pages_exist():
    assert len(PAGES) == 9, [p.name for p in PAGES]


def test_pages_share_one_stylesheet_and_one_enhancer():
    for name, src in PAGE_TEXT.items():
        assert src.count('href="case.css"') == 1, f"{name} 未接入共享样式"
        assert src.count('src="case.js"') == 1, f"{name} 未接入渐进增强脚本"


def test_page_style_is_skin_only():
    for name, src in PAGE_TEXT.items():
        blocks = re.findall(r"<style>(.*?)</style>", src, re.S)
        assert len(blocks) == 1, f"{name} 应只有一段皮肤样式，实际 {len(blocks)}"
        block = blocks[0]
        # 2026-10-30 圆桌裁决：全站收单主色，页面不得再覆写 accent
        # （旧「9 页 9 色」里 01/03 的 accent 逐字相同，身份机制已自证失效）
        assert "--accent:" not in block, f"{name} 皮肤不应再覆写 --accent（全站单主色）"
        assert block.count("\n") < 40, f"{name} 皮肤块 {block.count(chr(10))} 行，疑似又把基础样式抄回来了"


def test_shared_css_keeps_the_token_tree():
    for token in ("--radius-sm", "--radius-md", "--radius-lg", "--radius-xl", "--radius-full",
                  "--hairline", "--shadow-sm", "--shadow-md", "--shadow-lg",
                  "--dur-fast", "--dur-normal", "--dur-slow", "--ease-out",
                  "--text-xs", "--text-sm", "--text-md", "--text-lg"):
        assert token in CSS, f"case.css 缺少 {token}"


# ---------- 几何与排版纪律 ----------

def test_no_thick_borders_in_shared_css():
    body = css_without_tokens(CSS)
    bad = re.findall(r"border(?:-[a-z]+)?:\s*(?:1|1\.5|2|3)px", body)
    assert not bad, f"case.css 仍存在粗边框：{bad[:5]}"


def test_no_sub_12px_font_sizes():
    for label, text in [("case.css", CSS)] + [(n, s) for n, s in PAGE_TEXT.items()]:
        for m in re.finditer(r"font-size:\s*([\d.]+)px", text):
            assert float(m.group(1)) >= 12, f"{label} 出现 {m.group(1)}px 字号（下限 12px）"


def test_radius_values_come_from_tokens():
    body = css_without_tokens(CSS)
    bad = re.findall(r"border-radius:\s*([\d.]+px)", body)
    assert not bad, f"case.css 出现未收敛圆角：{bad[:5]}"


def test_motion_uses_three_speed_tiers():
    body = css_without_tokens(CSS)
    durations = set(re.findall(r"--dur-[a-z]+:\s*(\d+)ms", CSS))
    assert {"0", "80", "180", "300"} <= durations
    # 过渡时长只允许走 token（关键帧里的循环动画不计）
    raw = re.findall(r"transition(?:-duration)?:[^;{}]*?(\d+)ms", body)
    assert not raw, f"case.css 里仍有裸毫秒过渡：{raw[:5]}"


def test_reduced_motion_is_guarded():
    block = CSS.split("@media (prefers-reduced-motion: reduce)")[-1]
    assert "animation-duration: 0.01ms" in block
    assert "transition-duration: 0.01ms" in block
    assert ".live-dot { animation: none" in block


def test_touch_targets_on_mobile():
    mobile = CSS.split("@media (max-width: 768px)")[-1]
    assert "min-height: 44px" in mobile
    for sel in (".chips .chip", ".df-reset", ".action", ".case-nav-bar a"):
        assert sel in mobile, f"移动端热区规则缺 {sel}"


# ---------- 文案与元信息 ----------

def test_no_middle_dot_separator_in_metadata():
    for name, src in PAGE_TEXT.items():
        chunks = (
            re.findall(r'<span class="cn-mid">(.*?)</span>', src, re.S)
            + re.findall(r'<p class="kicker">(.*?)</p>', src, re.S)
            + re.findall(r'<span class="hint">(.*?)</span>', src, re.S)
            + re.findall(r'<span class="chip[^"]*">(.*?)</span>', src, re.S)
        )
        for chunk in chunks:
            text = re.sub(r"<[^>]+>", "", chunk)
            assert "·" not in text, f"{name} 元信息仍用中点分隔：{text.strip()[:40]}"


def test_every_page_has_share_meta():
    for name, src in PAGE_TEXT.items():
        assert '<meta name="description"' in src, f"{name} 缺 description"
        assert '<meta property="og:title"' in src, f"{name} 缺 og:title"
        assert '<meta property="og:image"' in src, f"{name} 缺 og:image"
        assert '<meta name="twitter:card"' in src, f"{name} 缺 twitter card"
        canonical = re.search(r'<link rel="canonical" href="([^"]+)"', src)
        assert canonical and canonical.group(1).endswith("/case/" + name), f"{name} canonical 不对"


# ---------- 状态诚实与可达性 ----------

def test_empty_state_has_guidance():
    assert ".demo-log:empty::before" in CSS
    assert "content:" in CSS.split(".demo-log:empty::before")[1][:200]


def test_each_demo_has_error_state():
    for name, src in PAGE_TEXT.items():
        js = "\n".join(re.findall(r"<script>(.*?)</script>", src, re.S))
        assert ("catch" in js) or ("未响应" in js) or (".catch(" in js), f"{name} demo 缺失败兜底"


def test_progressive_enhancement_covers_aria():
    for needle in ("role", "aria-selected", "aria-live", "keydown", "MutationObserver"):
        assert needle in JS, f"case.js 缺 {needle}"


def test_loading_state_is_honest():
    """有异步步骤的 demo 必须把按钮置为运行中，避免重复触发。"""
    for name, src in PAGE_TEXT.items():
        js = "\n".join(re.findall(r"<script>(.*?)</script>", src, re.S))
        if ("setTimeout(tick" not in js) and ("await wait" not in js) and ("await sleep" not in js):
            continue
        assert ("disabled = true" in js) or ("aria-busy" in js) or ("playing" in js), \
            f"{name} 有异步交互但没有运行中状态"


# ---------- 回归守卫 ----------

def test_inline_js_parses():
    for name, src in PAGE_TEXT.items():
        blocks = re.findall(r"<script>(.*?)</script>", src, re.S)
        js = "\n".join(blocks)
        if not js.strip():
            continue
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
            fh.write(js)
            tmp = fh.name
        r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
        assert r.returncode == 0, f"{name} 内联脚本语法错误：{r.stderr[:300]}"


def test_local_assets_exist():
    for name, src in PAGE_TEXT.items():
        page = CASE / name
        for ref in re.findall(r'(?:href|src)="([^"]+)"', src):
            if ref.startswith(("http", "mailto:", "tel:", "#", "data:", "javascript:")):
                continue
            if "' +" in ref or "${" in ref:
                continue
            target = (page.parent / ref.split("#")[0].split("?")[0]).resolve()
            if target.is_dir():
                target = target / "index.html"
            assert target.exists(), f"{name} 引用了不存在的本地资源 {ref}"


def test_legacy_template_css_is_gone():
    """旧版长页模板的死样式不应再回到共享层。"""
    for dead in (".hero-h1", ".constellation", ".marquee", ".xf-", "#cursorDot", "#railL", ".manifesto", ".foot-big"):
        assert dead not in CSS, f"case.css 里还有旧模板残留 {dead}"


def test_no_hardcoded_colors_in_inline_styles():
    for name, src in PAGE_TEXT.items():
        for style in re.findall(r'style="([^"]*)"', src):
            assert not re.search(r"#[0-9a-fA-F]{3,6}\b", style), f"{name} 内联样式写死色值：{style[:60]}"
            assert "rgb(" not in style, f"{name} 内联样式写死 rgb：{style[:60]}"
