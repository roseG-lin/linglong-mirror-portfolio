# -*- coding: utf-8 -*-
"""首页信息职责分工契约（2026-10-28 第二轮）。

规则：
1. 每个核心数字在首页可见文本里出现 ≤2 次（正文一处 + 简历文档一处）
2. 跑马灯 / 星图 tag / 一屏索引案例行：零数字
3. 首页四大旗舰的 chips 必须与 case 页 chips 完全一致（防口径分叉）
4. index 与 os 不得共享 ≥12 字的整句（防第二入口复读）
"""
from __future__ import annotations

import html as H
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
OS = (ROOT / "os" / "index.html").read_text(encoding="utf-8")
CASE = ROOT / "case"
CN = re.compile(r"[\u4e00-\u9fff]")
LIT = re.compile(r"'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\"")

# 每个核心数字在全页可见文本里的预算：正文 1 次 + 简历文档 1 次
BUDGET = {
    "1300+": 2, "80+": 2, "20+": 3, "15 款": 2, "90 万级": 2, "18 个月": 3,
    "2800+": 2, "1529": 2, "724s": 2, "119": 2, "448": 2, "171": 2,
    "94%": 2, "222": 2, "166": 2, "913": 2, "61.9": 2, "2499": 2,
    "1011": 2, "29 测试": 2,
}


def _drop_div(src: str, marker: str) -> str:
    """删掉指定 class 的整个 div（按 <div>/</div> 配平，处理嵌套）。"""
    pat = re.compile(r'<div class="[^"]*' + re.escape(marker) + r'[^"]*"[^>]*>')
    while True:
        m = pat.search(src)
        if not m:
            return src
        depth = 0
        end = len(src)
        for tag in re.finditer(r"<div\b[^>]*>|</div>", src[m.start():]):
            depth += 1 if tag.group(0).startswith("<div") else -1
            if depth == 0:
                end = m.start() + tag.end()
                break
        src = src[: m.start()] + " " + src[end:]


def _js_strings(block: str):
    """逐字符扫描 JS，正确跳过注释与正则字面量，取出所有字符串内容。"""
    out, i, n = [], 0, len(block)
    while i < n:
        c = block[i]
        if c in "'\"`":
            q, i = c, i + 1
            buf = []
            while i < n:
                ch = block[i]
                if ch == "\\":
                    buf.append(block[i:i + 2]); i += 2; continue
                if ch == q:
                    break
                buf.append(ch); i += 1
            out.append("".join(buf)); i += 1; continue
        if c == "/":
            if i + 1 < n and block[i + 1] == "/":
                j = block.find("\n", i); i = n if j < 0 else j + 1; continue
            if i + 1 < n and block[i + 1] == "*":
                j = block.find("*/", i + 2); i = n if j < 0 else j + 2; continue
            k = i - 1
            while k >= 0 and block[k] in " \t\r\n": k -= 1
            if k < 0 or block[k] in "(,=:[!&|?{};+-*%<>~^":
                i += 1; in_class = False
                while i < n:
                    ch = block[i]
                    if ch == "\\":
                        i += 2; continue
                    if ch == "[":
                        in_class = True
                    elif ch == "]":
                        in_class = False
                    elif ch == "/" and not in_class:
                        i += 1; break
                    elif ch == "\n":
                        break
                    i += 1
                continue
        i += 1
    return out


def _body(src: str, keep_script_text: bool) -> str:
    """可见文本（去掉 head / style / 注释 / 打印区 / aria-hidden 装饰块）。"""
    src = re.sub(r"<head\b.*?</head>", " ", src, flags=re.S)
    src = _drop_div(src, "marquee")      # 跑马灯：装饰带，另有专门测试
    src = _drop_div(src, "xf")           # 转场带：数字归位等装饰动画
    src = re.sub(r'<div id="printArea">\s*</div>', " ", src)
    src = re.sub(r"<noscript\b.*?</noscript>", " ", src, flags=re.S)  # 无 JS 兜底，不算正常浏览可见
    src = re.sub(r"<style\b.*?</style>", " ", src, flags=re.S)
    src = re.sub(r"<!--.*?-->", " ", src, flags=re.S)
    # 计数器初值 0 由 data-count 决定，按渲染结果计（整元素替换，避免被标签剥离吃掉）
    src = re.sub(r'<span data-count="(\d+)">[^<]*</span>\s*<small>\+\s*</small>', r" \1+ ", src)
    src = re.sub(r'data-count="(\d+)"', r" \1+ ", src)
    bits = []
    if keep_script_text:
        for block in re.findall(r"<script\b[^>]*>(.*?)</script>", src, re.S):
            for t in _js_strings(block):
                if CN.search(t):
                    bits.append(re.sub(r"<[^>]+>", " ", t))
    src = re.sub(r"<script\b.*?</script>", " ", src, flags=re.S)
    visible = re.sub(r"<[^>]+>", " ", src)
    return re.sub(r"\s+", " ", H.unescape(visible + " " + " ".join(bits)))


def _count(text: str, phrase: str) -> int:
    return len(re.findall(r"(?<![\d.])" + re.escape(phrase) + r"(?![\d.])", text))


def test_homepage_number_budget():
    text = _body(INDEX, keep_script_text=True)
    over = []
    for num, cap in BUDGET.items():
        n = _count(text, num)
        if n > cap:
            over.append(f"{num}: {n} 次（预算 {cap}）")
    assert not over, "首页数字超出预算：\n" + "\n".join(over)


def test_marquee_has_no_digits():
    block = re.search(r'<div class="marquee"[^>]*>(.*?)</div>\s*</div>', INDEX, re.S).group(1)
    assert not re.search(r"\d", block), "跑马灯不该再带数字（应只做关键词带）"


def test_star_map_tags_have_no_digits():
    nodes = re.search(r"const NODES = \[(.*?)\n  \];", INDEX, re.S).group(1)
    tags = re.findall(r"tag:\s*'([^']*)'", nodes)
    bad = [t for t in tags if re.search(r"\d", t)]
    assert not bad, f"星图 tag 仍带数字：{bad}"


def test_quickindex_case_rows_have_no_digits():
    section = re.search(r'<section class="section" id="quickindex".*?</section>', INDEX, re.S).group(0)
    rows = re.findall(r'<article class="qi-card[^"]*">(.*?)</article>', section, re.S)
    assert len(rows) >= 5, "一屏索引行数异常"
    bad = []
    for i, row in enumerate(rows):
        text = re.sub(r'<a [^>]*class="[^"]*"[^>]*>', " ", row)  # 链接文字保留、属性去掉
        text = re.sub(r'href="[^"]*"', " ", text)
        text = re.sub(r"<[^>]+>", " ", text)
        text = H.unescape(text)
        if "联系" in text:  # OS 入口那行留着联系方式，不参与
            continue
        if re.search(r"\d", text):
            bad.append((i, re.findall(r".{0,12}\d.{0,12}", text)[:2]))
    assert not bad, f"一屏索引仍有数字：{bad}"


def _chips(case_html: str):
    metrics = re.search(r'<div class="case-metrics">(.*?)</div>', case_html, re.S).group(1)
    out = []
    for chip in re.findall(r'<span class="chip[^"]*">(.*?)</span>', metrics, re.S):
        t = re.sub(r"<[^>]+>", "", chip)          # 去掉 sep 等标签
        t = re.sub(r"[\s·]+", "", t)              # 分隔符不参与比较
        out.append(t)
    return out


def test_homepage_case_chips_match_case_pages():
    """首页四大旗舰的 chips 必须与对应 case 页一致（防口径再次分叉）。"""
    cases = re.search(r"cases: \[(.*?)\n  \],", INDEX, re.S).group(1)
    entries = re.findall(r"\{ id: '([a-z-]+)'.*?metrics: \[(.*?)\]", cases, re.S)
    by_id = dict(entries)
    pairs = {
        "huodai-mask": "01-huodai-platform.html",
        "rag-pipeline": "02-rag-pipeline.html",
        "miku-privacy": "03-miku-privacy.html",
        "reyes-video": "04-reyes-video.html",
    }
    for cid, page in pairs.items():
        raw = by_id[cid]
        home = [re.sub(r"[\s·]+", "", t.strip(" '")) for t in re.findall(r"'([^']*)'", raw)]
        page_chips = _chips((CASE / page).read_text(encoding="utf-8"))
        assert home == page_chips, f"{page} chips 与首页不一致：\n首页 {home}\n案例页 {page_chips}"


def _cut_range(src: str, start: str, end: str) -> str:
    i = src.find(start)
    if i < 0:
        return src
    j = src.find(end, i + len(start))
    if j < 0:
        return src
    return src[:i] + " " + src[j:]


def _narrative(src: str, is_index: bool) -> str:
    """只比叙述性文案：排除简历文档与内嵌 demo 的运行时输出。"""
    if is_index:
        src = _drop_div(src, "resume-card")
        src = _cut_range(src, "const RESUME_HTML =", "$('#resumeDoc')")
        src = _cut_range(src, "const DEMOS = {", "\nconst stage = document")
    else:
        src = _cut_range(src, "APPS.resume = {", "/* ----------")
        src = _cut_range(src, "const DEMOS = {", "\nAPPS.sandbox = {")
    return _body(src, keep_script_text=True)


def _sentences(src: str):
    out = set()
    for part in re.split(r"[。；;！!？?\n]", src):
        part = re.sub(r"\s+", " ", part).strip()
        if len(part) >= 12 and CN.search(part):
            out.add(part)
    return out


def test_index_and_os_share_no_long_sentences():
    shared = _sentences(_narrative(INDEX, True)) & _sentences(_narrative(OS, False))
    assert not shared, "index 与 os 仍有整句重复：\n" + "\n".join(sorted(shared)[:6])
