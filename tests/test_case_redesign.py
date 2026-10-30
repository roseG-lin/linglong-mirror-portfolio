# -*- coding: utf-8 -*-
"""案例页去 AI 味 · P0 改造契约（2026-10-30 圆桌裁决的落地锁）。

依据：docs/case-redesign-20261030.md（圆桌 dwfrun-55324fc5 蒸馏）。
每条测试对应 P0 清单里的一项，全部锚在「能一次量出来」的判据上（D席纪律）：
  A1/A2/A3 字体链头  B kicker 字距  C1-C3 玻璃/发光/白叠层  D 单主色  E h2 真标题化

跑法（站点根目录）：python -m pytest tests/test_case_redesign.py -q
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "case" / "case.css").read_text(encoding="utf-8")
PAGES = sorted((ROOT / "case").glob("0*.html"))
PAGE_TEXT = {p.name: p.read_text(encoding="utf-8") for p in PAGES}


def _skins() -> dict[str, str]:
    out = {}
    for name, src in PAGE_TEXT.items():
        blocks = re.findall(r"<style>(.*?)</style>", src, re.S)
        out[name] = blocks[0] if blocks else ""
    return out


# ---------- A. 字体链头 ----------

def test_display_stack_heads_with_a_real_font():
    """A1：标题栈首项必须系统可得。Instrument Serif 从未下发（0 @font-face），
    把它排在栈首 = 「衬线大标题」实渲染宋体——AI 味第一病灶。"""
    m = re.search(r"--font-display:\s*([^;]+);", CSS)
    assert m, "case.css 缺 --font-display"
    first = m.group(1).split(",")[0].strip().strip("'\"")
    assert first in {"Inter", "PingFang SC", "Microsoft YaHei", "system-ui"}, (
        f"--font-display 栈首是 {first!r}：不是本站自托管（0 @font-face）就是系统字体"
    )


def test_titles_are_600_and_not_alone():
    """A2：标题 600，且不再是全文件唯一的 600（原来唯一 600 在图注 b）。"""
    m = re.search(r"h1, h2, h3\s*\{[^}]*font-weight:\s*(\d+)", CSS)
    assert m and int(m.group(1)) >= 600, "h1,h2,h3 标题字重必须 ≥600"
    assert CSS.count("font-weight: 600") >= 3, "600 字重应成体系（标题+强调），不能只有图注一处"


def test_chinese_carrying_components_not_mono():
    """A3：承载中文散文的组件不再用 mono 栈（mono 内中文=雅黑假等宽）。"""
    for sel in ("chip", "demo-note", "ev-meta", "df-bar"):
        blocks = re.findall(r"([^{}]*\." + re.escape(sel) + r"[^{}]*)\{([^}]*)\}", CSS)
        bad = [s for s, body in blocks if "--font-mono" in body]
        assert not bad, f".{sel} 仍引用 --font-mono（中文假等宽）：{bad[:3]}"


# ---------- B. kicker 字距 ----------

def test_kicker_letter_spacing_tight():
    """B：0.22em 的英文海报字距作用在中文上；大厂 UI 字距 ≤0.08em。"""
    for m in re.finditer(r"letter-spacing:\s*([\d.]+)em", CSS):
        assert float(m.group(1)) <= 0.08, f"kicker/标签字距 {m.group(1)}em 超 0.08em"


# ---------- C. 玻璃 / 发光 / 白叠层 ----------

def test_no_backdrop_filter():
    assert "backdrop-filter" not in CSS, "case.css 仍有 backdrop-filter（玻璃拟态）"


def test_no_glow_accent():
    assert "--glow-accent" not in CSS, "case.css 仍有 --glow-accent（accent 发光）"


def test_white_overlays_are_tokenized():
    """C3：写死 rgba(255,255,255,α) 直接叠色清零，层级一律走 surface 灰阶。"""
    n = len(re.findall(r"rgba\(255,\s*255,\s*255,\s*0\.\d+\)", CSS))
    assert n == 0, f"case.css 仍有 {n} 处写死白色叠层，应改为 --surface 阶梯或 --glass-fill"


def test_surface_ladder_stays_small():
    """Ge席预警：非标灰阶新增 >3 个 = 暗底结构坍塌，本测试就是闸。"""
    ladders = set(re.findall(r"--surface(?:-\d)?:", CSS))
    assert len(ladders) <= 4, f"surface 阶梯膨胀：{sorted(ladders)}"


# ---------- D. 单主色 ----------

def test_single_accent_no_per_page_overrides():
    """D：9 页皮肤不再各自覆写 accent（01/03 重复键自证身份机制失效）。"""
    for name, skin in _skins().items():
        assert "--accent:" not in skin, f"{name} 皮肤仍覆写 --accent，全站应收单主色"


def test_primary_accent_passes_aa_on_dark():
    """D：全站主色在暗底上 ≥4.5:1（WCAG 实时算，不认肉眼）。"""
    acc = re.search(r"--accent:\s*(\d+)\s+(\d+)%\s+(\d+)%", CSS)
    bg = re.search(r"--background:\s*(\d+)\s+(\d+)%\s+(\d+)%", CSS)
    assert acc and bg, "case.css 缺 --accent 或 --background 定义"

    def lum(h: float, s: float, l: float) -> float:
        c = (1 - abs(2 * l - 1)) * s
        hp = (h % 360) / 60
        x = c * (1 - abs(hp % 2 - 1))
        r1, g1, b1 = [(c, x, 0), (x, c, 0), (0, c, x), (0, x, c), (x, 0, c), (c, 0, x)][int(hp) % 6]
        m = l - c / 2

        def f(u: float) -> float:
            u += m
            return u / 12.92 if u <= 0.03928 else ((u + 0.055) / 1.055) ** 2.4

        return 0.2126 * f(r1) + 0.7152 * f(g1) + 0.0722 * f(b1)

    ah, as_, al = (float(g) for g in acc.groups())
    bh, bs, bl = (float(g) for g in bg.groups())
    la, lb = lum(ah, as_ / 100, al / 100), lum(bh, bs / 100, bl / 100)
    ratio = (max(la, lb) + 0.05) / (min(la, lb) + 0.05)
    assert ratio >= 4.5, f"主色 hsl({ah} {as_}% {al}%) 在暗底上只有 {ratio:.2f}:1，AA(4.5) 不达标"


# ---------- E. h2 真标题化 ----------

def test_evidence_section_heading_is_a_real_heading():
    """E：真机佐证区的 h2 不得复用 12px 的 .kicker（大纲层级在渲染层不存在）。"""
    for name, src in PAGE_TEXT.items():
        for m in re.finditer(r"<h2 class=\"([^\"]*)\"", src):
            assert "kicker" not in m.group(1), f"{name} 的 h2 仍复用 .kicker（12px < 正文）"
