# -*- coding: utf-8 -*-
"""内容去重契约（2026-10-27 审计结论的回归锁）。

1. 案例页 tag/chips 里的数字，全页只能出现一次（证据位唯一）
2. pn-nav 只留上一篇/下一篇，回目录全站只有顶栏一处
3. 首页跑马灯对读屏隐藏（无缝循环克隆不重复播报）
4. case09 的 1011 / 368 两个测试数必须带口径
"""
from __future__ import annotations

import html as H
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "case"
PAGES = sorted(CASE.glob("0*.html"))

CN = re.compile(r"[\u4e00-\u9fff]")
# 数字 token：前面不能是数字/字母/¥（排除 V1-V12、¥12 这类），可带量词
TOKEN = re.compile(r"(?<![\dA-Za-z¥])(\d[\d,.]*\+?)(?:\s*(?:项|个|款|条|s|秒|%))?")
LIT = re.compile(r"'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\"")


def _strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s)


def _body(src: str) -> str:
    """可见文本 + JS 里含中文的用户可见字符串（demo 渲染内容）。"""
    src = re.sub(r"<style\b.*?</style>", " ", src, flags=re.S)
    src = re.sub(r"<!--.*?-->", " ", src, flags=re.S)
    js_bits = []
    for block in re.findall(r"<script\b[^>]*>(.*?)</script>", src, re.S):
        # 字符组形式的正则字面量（如 /[&<>"]/g）里的引号会打乱字符串配对，先中性化
        block = re.sub(r"/\[[^\]\n]+\]/[gimsuy]*", " ", block)
        for a, b in LIT.findall(block):
            t = a or b
            if CN.search(t):
                js_bits.append(_strip_tags(t))
    src = re.sub(r"<script\b.*?</script>", " ", src, flags=re.S)
    visible = re.sub(r"<[^>]+>", " ", src)
    return re.sub(r"\s+", " ", H.unescape(visible + " " + " ".join(js_bits)))


def _tokens(fragment: str):
    out = []
    for tok in TOKEN.findall(_strip_tags(fragment)):
        tok = tok.strip()
        if len(tok) >= 2:
            out.append(tok)
    return out


def _hit(token: str, body: str):
    """token 在 body 里出现（166 不得命中 166.5，14 不得命中 14px 之外的数字段）。"""
    return re.search(r"(?<![\d.])" + re.escape(token) + r"(?![\d.])", body)


def test_case_numbers_appear_once():
    """tag/chips 的数字不得再出现在页面其余部分；chips 至少保留 3 个。"""
    failures = []
    for p in PAGES:
        src = p.read_text(encoding="utf-8")
        tag = re.search(r'<p class="tag">(.*?)</p>', src, re.S).group(1)
        metrics = re.search(r'<div class="case-metrics">(.*?)</div>', src, re.S).group(1)
        if len(re.findall(r'<span class="chip', metrics)) < 3:
            failures.append(f"{p.name}: chips 被删过头了")
            continue
        # tag 文本同时存在于 meta description / og / twitter 的属性里，必须全删
        body = _body(src.replace(tag, " ").replace(metrics, " "))
        dups = []
        for tok in _tokens(tag) + _tokens(metrics):
            base = re.match(r"\d[\d,.]*", tok).group(0)
            for t in {tok, base}:
                if len(t) >= 2 and _hit(t, body):
                    dups.append(t)
                    break
        if dups:
            failures.append(f"{p.name}: 数字重复出现 {sorted(set(dups))}")
    assert not failures, "\n" + "\n".join(failures)


def test_pnnav_is_prev_next_only():
    """pn-nav 只留上一篇/下一篇；回目录全页只有顶栏一处。"""
    for p in PAGES:
        src = p.read_text(encoding="utf-8")
        block = re.search(r'<div class="pn-nav">(.*?)</div>\s*</main>', src, re.S).group(1)
        assert "返回作品集目录" not in block, f"{p.name} pn-nav 还带着回目录行"
        assert 'href="../"' not in block, f"{p.name} pn-nav 不应再链目录"
        links = re.findall(r"<a ([^>]*)>", block)
        assert 1 <= len(links) <= 2, f"{p.name} pn-nav 链接数异常: {len(links)}"
        for attrs in links:
            assert re.search(r'href="0\d-', attrs), f"{p.name} pn-nav 只许链案例页: {attrs}"
        assert src.count('href="../"') == 1, f"{p.name} 回目录链接应只有顶栏一处"


def test_topnav_next_points_to_the_real_next_case():
    """顶栏右侧的「下一篇」必须真的指向下一案例；末篇没有；回目录全页只有左侧一处。"""
    order = [p.name for p in PAGES]
    for i, p in enumerate(PAGES):
        src = p.read_text(encoding="utf-8")
        nav = re.search(r'<nav class="case-nav-bar"[^>]*>(.*?)</nav>', src, re.S).group(1)
        links = re.findall(r'<a href="([^"]*)"[^>]*>([^<]*)</a>', nav)
        assert links and links[0][0] == "../" and "目录" in links[0][1], f"{p.name} 顶栏左侧应是目录"
        assert src.count('href="../"') == 1, f"{p.name} 回目录链接应只有顶栏左侧一处"
        if i + 1 < len(order):
            assert len(links) == 2, f"{p.name} 顶栏应有下一篇入口"
            href, label = links[1]
            assert href == order[i + 1], f"{p.name} 顶栏下一篇指向错了：{href}"
            assert "下一篇" in label, f"{p.name} 顶栏右侧文案应为下一篇：{label}"
        else:
            assert len(links) == 1, f"{p.name} 末篇顶栏不该有下一案例入口"


def test_marquee_hidden_from_screen_readers():
    """跑马灯整体对读屏隐藏（无缝循环的克隆不该被播报两遍）。"""
    src = (ROOT / "index.html").read_text(encoding="utf-8")
    m = re.search(r'<div class="marquee"([^>]*)>', src)
    assert m, "首页找不到跑马灯"
    assert "aria-hidden" in m.group(1), "跑马灯容器缺 aria-hidden"


def test_case09_test_counts_disambiguated():
    """1011 与 368 两个测试数必须能分清口径。"""
    src = (CASE / "09-longjob-pipeline.html").read_text(encoding="utf-8")
    assert src.count("1011") == 1, "1011 应只出现在页首指标里"
    assert "368 测试（longjob 仓，全仓回归见页首）" in src, "368 缺口径标注"
