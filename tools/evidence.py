# -*- coding: utf-8 -*-
"""把一张真实项目截图装成案例页的「证据图」，顺手做脱敏与规格化。

为什么要有这个工具：
1. 案例页里的图必须是**真截图**（首页卡片才是概念封面），而真截图最容易带出
   客户名、真实订单号、手机号、内网地址——保密铁律（湛江项目在简历/作品集
   产出中自动脱敏）是硬规则，不能靠"我记得遮一下"。
2. 页面 `.evidence` 用 `width:100%; height:auto` 渲染，图太大拖慢首屏、
   太小在高分屏糊。统一在这里定宽，页面就不用管。

用法（站点根目录）：
    python tools/evidence.py 原图.png --slug 01-huodai --no 01 \\
        --op "点【跑一单】：订单→报关→账单三段自动流转" \\
        --num "2800 项测试，见 tests/test_* 与 CI 绿门禁" \\
        [--redact 12,8,46,14 ...] [--confidential] [--checked] [--mark]

参数：
    --slug        案例页文件名前缀（01-huodai 之类），决定落盘目录与命名
    --no          第几张（01、02 …）
    --op          这张图演示的动作（figcaption 第一行）
    --num         图上数字的出处（figcaption 第二行）
    --date        截图日期，默认今天
    --redact      打码区 x1,y1,x2,y2，单位是**百分比**（0-100），可重复给多次
    --confidential 涉密项目：必须至少有一个 --redact，或用 --checked 明确声明
                  "已逐帧看过，没有客户信息"；否则拒绝执行
    --checked     见上
    --mark        右下角压一行「已脱敏」小字（--confidential 时建议开）
    --force       目标文件已存在时覆盖（默认拒绝，避免误覆盖已验收的图）

退出码：0 成功 / 2 源图不存在或参数不合法（argparse）/ 3 保密门未过 / 5 目标已存在
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    sys.exit("需要 Pillow：pip install pillow")

MAX_WIDTH = 1400
MIN_WIDTH = 880
QUALITY = 86
EVIDENCE_DIR = Path("case/assets/evidence")


def parse_box(value: str) -> tuple[float, float, float, float]:
    parts = value.split(",")
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("--redact 要写成 x1,y1,x2,y2（百分比）")
    try:
        x1, y1, x2, y2 = (float(p) for p in parts)
    except ValueError:
        raise argparse.ArgumentTypeError("--redact 的四个值必须是数字") from None
    if not all(0 <= v <= 100 for v in (x1, y1, x2, y2)):
        raise argparse.ArgumentTypeError("--redact 取值要在 0-100 之间")
    if x2 <= x1 or y2 <= y1:
        raise argparse.ArgumentTypeError("--redact 需要 x2>x1 且 y2>y1")
    return x1, y1, x2, y2


def pixelate(im: Image.Image, pct: tuple[float, float, float, float]) -> None:
    """把百分比区域打成马赛克（就地修改）。块边长取图像短边的 1/24，正文字号必糊。"""
    w, h = im.size
    box = (
        max(0, round(pct[0] / 100 * w)), max(0, round(pct[1] / 100 * h)),
        min(w, round(pct[2] / 100 * w)), min(h, round(pct[3] / 100 * h)),
    )
    if box[2] - box[0] < 2 or box[3] - box[1] < 2:
        return
    block = max(6, round(min(w, h) / 24))
    region = im.crop(box)
    small = region.resize(
        (max(1, region.width // block), max(1, region.height // block)), Image.BOX
    )
    im.paste(small.resize(region.size, Image.NEAREST), box[:2])


def stamp(im: Image.Image) -> None:
    """右下角压一行小字，免得被当成未脱敏的原图转发。"""
    from PIL import ImageDraw

    d = ImageDraw.Draw(im, "RGBA")
    text = "已脱敏"
    pad = 8
    try:
        tw = d.textlength(text)
    except AttributeError:  # pragma: no cover
        tw = len(text) * 12
    th = 14
    x, y = im.width - tw - pad * 2, im.height - th - pad * 2
    d.rectangle([x, y, x + tw + pad, y + th + pad], fill=(0, 0, 0, 140))
    d.text((x + pad / 2, y + pad / 2 - 1), text, fill=(255, 255, 255, 200))


def html_block(rel: str, w: int, h: int, alt: str, op: str, num: str, date: str) -> str:
    return (
        '<figure class="evidence">\n'
        f'  <a href="{rel}" target="_blank" rel="noopener">\n'
        f'    <img src="{rel}" width="{w}" height="{h}" alt="{alt}" loading="lazy" decoding="async">\n'
        "  </a>\n"
        "  <figcaption>\n"
        f"    <b>操作：</b>{op}\n"
        f'    <span class="ev-meta">数字出处：{num} · 截图 {date}</span>\n'
        "  </figcaption>\n"
        "</figure>"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="真实项目截图 → 案例页证据图（1400 宽 / 去 EXIF / 可打码）")
    ap.add_argument("src", type=Path)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--no", required=True)
    ap.add_argument("--op", required=True)
    ap.add_argument("--num", required=True)
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--alt", default=None)
    ap.add_argument("--redact", type=parse_box, action="append", default=[])
    ap.add_argument("--confidential", action="store_true")
    ap.add_argument("--checked", action="store_true")
    ap.add_argument("--mark", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if not args.src.exists():
        print(f"源图不存在：{args.src}")
        return 2

    if args.confidential and not args.redact and not args.checked:
        print("拒绝执行：涉密项目的截图必须先打码。")
        print("  逐帧确认过没有客户名/订单号/手机号/内网地址，请加 --checked；")
        print("  否则用 --redact x1,y1,x2,y2（百分比，可给多次）把敏感区打掉。")
        print("  依据：保密铁律——湛江项目内容在简历与作品集产出中必须脱敏。")
        return 3

    dst = EVIDENCE_DIR / f"{args.slug}-{args.no}.jpg"
    if dst.exists() and not args.force:
        print(f"{dst} 已存在；确认要替换请加 --force")
        return 5

    im = Image.open(args.src).convert("RGB")
    src_size = im.size
    for box in args.redact:
        pixelate(im, box)
    if args.mark or args.confidential:
        stamp(im)

    if im.width > MAX_WIDTH:
        im = im.resize((MAX_WIDTH, round(im.height * MAX_WIDTH / im.width)), Image.LANCZOS)
    elif im.width < MIN_WIDTH:
        print(f"提示：源图只有 {im.width}px 宽，案例页满宽约 960px，高分屏会糊；建议用原图重截")

    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst, "JPEG", quality=QUALITY, optimize=True, progressive=True)

    kb = dst.stat().st_size / 1024
    rel = f"assets/evidence/{dst.name}"
    print(f"源图 {src_size[0]}×{src_size[1]} → {dst.as_posix()} {im.width}×{im.height}  {kb:.0f}KB")
    print(f"打码 {len(args.redact)} 处" + ("（含「已脱敏」角标）" if (args.mark or args.confidential) else ""))
    if kb > 300:
        print("  注意：单张 >300KB 偏大，考虑裁掉无关区域或降 --quality")
    print("\n把下面这段贴进对应案例页（case/）的正文合适位置：\n")
    print(html_block(rel, im.width, im.height, args.alt or f"{args.slug} 实机操作截图", args.op, args.num, args.date))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
