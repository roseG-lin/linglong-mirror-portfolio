# -*- coding: utf-8 -*-
"""站点审计修复契约（2026-10-28）。对应 docs/portfolio-audit-20261028.md。

跑法：python -m pytest tests/test_site_audit_fixes.py -q
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
OS = (ROOT / "os" / "index.html").read_text(encoding="utf-8")
FOLIO = (ROOT / "folio" / "index.html").read_text(encoding="utf-8")
CASE_PAGES = sorted((ROOT / "case").glob("0*.html"))


def _all_text_files():
    pats = ["*.html", "*.txt", "case/*.html", "os/*.html", "folio/*.html", "editorial/*.html"]
    for pat in pats:
        yield from ROOT.glob(pat)


# ---------- P0 口径 ----------

def test_no_stale_job_title_anywhere():
    bad = [str(p.relative_to(ROOT)) for p in _all_text_files()
           if "技术售前专家" in p.read_text(encoding="utf-8", errors="ignore")]
    assert not bad, f"旧抬头「技术售前专家」仍在：{bad}"


def test_llms_availability_matches_site():
    txt = (ROOT / "llms.txt").read_text(encoding="utf-8")
    assert "随时可到岗" not in txt, "llms.txt 到岗口径与站点不一致（站点是一周内到岗）"
    assert "一周内到岗" in txt


# ---------- P0 隐私 ----------

def test_no_tailored_resumes_in_deploy():
    d = ROOT / "downloads"
    if not d.exists():
        return
    leaked = [p.name for p in d.rglob("*") if p.is_file() and p.suffix.lower() in (".html", ".zip", ".pdf")]
    assert not leaked, f"定制简历/源文件包仍在部署目录：{leaked}"


def test_no_backup_or_oversized_avatar_in_deploy():
    assert not (ROOT / "assets" / "_original_backup").exists(), "原始素材备份目录仍在部署目录"
    assert not (ROOT / "assets" / "avatar.png").exists(), "3.4MB 原图 avatar.png 仍在部署目录"


# ---------- P0 AA（07 主题演示） ----------

def _rgb(color: str, bg=None):
    c = color.strip()
    if c.startswith("rgba"):
        nums = [float(x) for x in re.findall(r"[\d.]+", c)]
        r, g, b, a = nums[:4]
        return tuple(x * a + y * (1 - a) for x, y in zip((r, g, b), bg))
    if c.startswith("#"):
        h = c.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    raise ValueError(c)


def _lum(c):
    def f(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2])


def _ratio(a, b):
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def test_case07_demo_themes_pass_aa():
    src = (ROOT / "case" / "04-mirror-value.html").read_text(encoding="utf-8")
    block = re.search(r"const THEMES = \{(.*?)\n      \};", src, re.S).group(1)
    rows = re.findall(r"(\w+):\s*\{[^}]*bg:'([^']+)'[^}]*surf:'([^']+)'[^}]*acc:'([^']+)'", block)
    assert len(rows) == 4, f"解析到 {len(rows)} 套主题"
    fails = []
    for name, bg, surf, acc in rows:
        bgc = _rgb(bg)
        surfc = _rgb(surf, bgc) if surf.startswith("rgba") else _rgb(surf)
        r = _ratio(_rgb(acc), surfc)
        if r < 4.5:
            fails.append(f"{name}: accent/卡面 {r:.2f}")
    assert not fails, "主题演示自称 AA 门禁但不达标：\n" + "\n".join(fails)


# ---------- P1 坏页 / SEO ----------

def test_editorial_is_a_redirect_stub():
    p = ROOT / "editorial" / "index.html"
    assert p.exists(), "editorial 页被删除但 sitemap/外链未处理"
    s = p.read_text(encoding="utf-8")
    assert 'http-equiv="refresh"' in s, "editorial 应改为跳转桩"
    assert 'name="robots" content="noindex"' in s
    refs = re.findall(r'(?:src|href)="([^"#]+)"', s)
    bad = [r for r in refs if r.startswith(("css/", "js/", "assets/", "project-"))]
    assert not bad, f"editorial 仍引用不存在的本地资源：{bad}"


def test_404_page_exists_and_points_home():
    p = ROOT / "404.html"
    assert p.exists(), "缺少 404.html"
    s = p.read_text(encoding="utf-8")
    assert 'lang="zh-CN"' in s
    assert "noindex" in s
    assert 'href="/"' in s


def test_os_and_folio_have_canonical_and_og():
    for name, src, url in (("os", OS, "https://www.remifei.cn/os/"),
                           ("folio", FOLIO, "https://www.remifei.cn/folio/")):
        assert f'<link rel="canonical" href="{url}">' in src, f"{name} 缺 canonical"
        for prop in ('property="og:title"', 'property="og:description"',
                     'property="og:image"', 'property="og:url"'):
            assert prop in src, f"{name} 缺 {prop}"
        assert 'name="twitter:card"' in src, f"{name} 缺 twitter card"


def test_sitemap_covers_all_public_pages():
    sm = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    for path in ["/", "/os/", "/folio/"] + [f"/case/{p.name}" for p in CASE_PAGES]:
        assert f"https://www.remifei.cn{path}" in sm, f"sitemap 缺 {path}"
    assert "editorial" not in sm, "跳转桩不该进 sitemap"


# ---------- P1 性能 ----------

def test_os_background_video_is_gated():
    tag = re.search(r"<video[^>]*>", OS).group(0)
    assert "autoplay" not in tag, "视频仍在自动播放（移动端会强制下载 3.4MB）"
    assert "data-src=" in tag, "视频应改为 data-src 条件加载"
    assert '<source src=' not in OS, "静态 source 会绕过条件加载"
    assert "saveData" in OS and "prefers-reduced-motion" in OS, "缺少条件加载判断"


# ---------- P2 无障碍 ----------

def test_star_map_canvas_has_accessible_name():
    tag = re.search(r"<canvas id=\"constellation\"[^>]*>", INDEX).group(0)
    assert "aria-label" in tag and "role=" in tag, "星图 canvas 缺可访问名"


def test_pending_states_are_not_dimmed_below_aa():
    """待运行态不得靠 opacity 压暗（muted 叠 0.4 只有 2.16:1）；分隔线/禁用态不在此列。"""
    css = (ROOT / "case" / "case.css").read_text(encoding="utf-8")
    for sel in (".rag-node {", ".val-card.dim"):
        i = css.find(sel)
        assert i >= 0, f"case.css 找不到 {sel}"
        block = css[i: css.find("}", i)]
        assert "opacity" not in block, f"{sel} 仍用 opacity 压暗：{block[:80]}"
    # 待运行态的文字色必须是 muted（对 surface 6.98:1）
    assert ".rag-node .t { color: hsl(var(--muted-foreground)); }" in css


def test_home_and_os_have_live_regions():
    assert "aria-live" in INDEX, "首页动态 demo 缺 aria-live"
    assert "aria-live" in OS, "os 动态 demo 缺 aria-live"


def test_case_pages_have_skip_link():
    for p in CASE_PAGES:
        s = p.read_text(encoding="utf-8")
        assert 'class="skip"' in s, f"{p.name} 缺 skip link"
        assert 'id="main"' in s, f"{p.name} 的 main 缺 id"


# ---------- P2 口径与内容 ----------

def test_facts_ledger_covers_site_numbers():
    facts = Path(r"E:/AI项目/玲珑职举工作台/data/facts.yaml").read_text(encoding="utf-8")
    nums = re.search(r"^numbers:.*?(?=^\w|\Z)", facts, re.S | re.M).group(0)
    for val in ["1529", "1527", "724", "448", "94%", "171", "2499", "228", "553", "222", "26", "7/7", "250", "1080", "191", "446", "479"]:
        assert val in nums, f"facts.yaml 的 numbers 未收编 {val}"


def test_case_pages_state_measurement_date():
    for p in CASE_PAGES:
        assert "实测口径" in p.read_text(encoding="utf-8"), f"{p.name} 缺实测口径说明"


def test_home_first_screen_shows_salary():
    kicker = re.search(r'<p class="hero-kicker">(.*?)</p>', INDEX, re.S).group(1)
    assert "12-15K" in kicker, "首屏（hero-kicker）没有期望薪资"


def test_footer_links_to_evidence_wall():
    footer = re.search(r"<footer>(.*?)</footer>", INDEX, re.S).group(1)
    assert "证据" in footer and 'href="./os/"' in footer, "页脚没有证据墙入口"
