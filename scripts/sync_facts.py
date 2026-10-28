#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 data/site-facts.json 同步进各页面，消除口径分叉。

用法：
    python scripts/sync_facts.py            # 写入
    python scripts/sync_facts.py --check    # 只检查，漂移则 exit 1

设计：不引入构建步骤，只做「已知片段的幂等替换」。
新增口径时，在这里加一条规则 + 在 tests/test_site_contract.py 加一条断言。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FACTS = json.loads((ROOT / "data" / "site-facts.json").read_text(encoding="utf-8"))

TARGETS = ("index.html", "os/index.html", "llms.txt", "llms-full.txt")


def rules() -> list[tuple[str, str]]:
    product = str(FACTS["product_count"])
    salary = str(FACTS["salary"])
    return [
        # 联系区薪资 chip
        (r'(<span class="chip">)\d+-\d+K( · 可议</span>)', rf"\g<1>{salary}\g<2>"),
        # 首屏 KPI 第四格（玲珑产品数）
        (
            r'(<span data-count=")\d+(">0</span><small>\+</small></div><div class="l">玲珑系列产品)',
            rf"\g<1>{product}\g<2>",
        ),
        # 任何「N 款玲珑」
        (r"(\d+)(\s*款玲珑)", rf"{product}\g<2>"),
        # OS 仪表盘第 4 格
        (
            r"\{\s*n:\s*\d+,\s*suffix:\s*'\+',\s*label:\s*'[^']*(?:产物|产品)'\s*\}",
            f"{{ n: {product}, suffix: '+', label: '玲珑系列产品' }}",
        ),
        # 「产品」与「产物」混写的旧句式
        (r"15\s*款产品\s*·\s*20\+\s*产物", f"{product} 款产品矩阵"),
    ]


def apply(text: str) -> str:
    for pattern, repl in rules():
        text = re.sub(pattern, repl, text)
    return text


def main() -> int:
    check = "--check" in sys.argv
    drift: list[str] = []
    for name in TARGETS:
        path = ROOT / name
        if not path.exists():
            continue
        old = path.read_text(encoding="utf-8")
        new = apply(old)
        if new != old:
            if check:
                lineno = next(
                    (i + 1 for i, (a, b) in enumerate(zip(old.splitlines(), new.splitlines())) if a != b),
                    0,
                )
                drift.append(f"{name}:{lineno}")
            else:
                path.write_text(new, encoding="utf-8")
                print(f"[sync] {name} 已更新")
    if check:
        if drift:
            print("[drift] " + ", ".join(drift))
            print("跑 python scripts/sync_facts.py 修复")
            return 1
        print("[ok] 全部页面与 data/site-facts.json 一致")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
