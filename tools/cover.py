# -*- coding: utf-8 -*-
"""把任意截图 / 生图规格化成案例卡缩略图（912×608 · 3:2）。

为什么要有这个工具：首页 `.case-thumb` 用 `aspect-ratio:912/608` + `object-fit:cover`
渲染，`<img width height>` 与文件真实尺寸必须一致（tests/test_media_geometry.py 有硬锁）。
手裁很容易差几像素，差一点就会被 cover 二次裁切、把界面文字切掉。

用法（站点根目录）：
    python tools/cover.py 原图.png case/assets/shot-01.jpg
    python tools/cover.py 原图.png case/assets/shot-01.jpg --fit pad
    python tools/cover.py 原图.png 输出.jpg --fit cover --quality 88

参数：
    --fit cover  铺满后居中裁切（默认，适合整屏截图与生图封面）
    --fit pad    完整装进画框，空处填 --bg（适合不能裁掉边缘的图）
    --bg         留白底色，默认站点近黑 #070D14
    --quality    JPEG 质量，默认 86

输出会打印最终尺寸、体积；源图短边不足 608 时会提示已放大。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    sys.exit("需要 Pillow：pip install pillow")

TARGET = (912, 608)
DEFAULT_BG = "#070D14"


def parse_bg(value: str) -> tuple[int, int, int]:
    v = value.lstrip("#")
    if len(v) != 6:
        raise argparse.ArgumentTypeError("颜色要写成 #RRGGBB")
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def fit_cover(im: Image.Image, size: tuple[int, int]) -> Image.Image:
    tw, th = size
    scale = max(tw / im.width, th / im.height)
    nw, nh = round(im.width * scale), round(im.height * scale)
    im = im.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - tw) // 2, (nh - th) // 2
    return im.crop((left, top, left + tw, top + th))


def fit_pad(im: Image.Image, size: tuple[int, int], bg: tuple[int, int, int]) -> Image.Image:
    tw, th = size
    scale = min(tw / im.width, th / im.height)
    nw, nh = round(im.width * scale), round(im.height * scale)
    im = im.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGB", size, bg)
    canvas.paste(im, ((tw - nw) // 2, (th - nh) // 2))
    return canvas


def main() -> int:
    ap = argparse.ArgumentParser(description="案例卡缩略图规格化（912×608）")
    ap.add_argument("src", type=Path)
    ap.add_argument("dst", type=Path)
    ap.add_argument("--fit", choices=("cover", "pad"), default="cover")
    ap.add_argument("--bg", type=parse_bg, default=parse_bg(DEFAULT_BG))
    ap.add_argument("--quality", type=int, default=86)
    args = ap.parse_args()

    if not args.src.exists():
        return print(f"源图不存在：{args.src}") or 2

    im = Image.open(args.src).convert("RGB")
    src_size = im.size
    if min(src_size) < min(TARGET):
        print(f"提示：源图 {src_size[0]}×{src_size[1]} 短边不足 {min(TARGET)}，会被放大，建议给更大的原图")

    out = fit_cover(im, TARGET) if args.fit == "cover" else fit_pad(im, TARGET, args.bg)
    args.dst.parent.mkdir(parents=True, exist_ok=True)
    out.save(args.dst, "JPEG", quality=args.quality, optimize=True, progressive=True)

    kb = args.dst.stat().st_size / 1024
    ratio = src_size[0] / src_size[1]
    cut = abs(ratio - 1.5) / 1.5
    print(f"源图 {src_size[0]}×{src_size[1]}（{ratio:.3f}:1）→ {args.dst} 912×608  {kb:.0f}KB")
    if args.fit == "cover" and cut > 0.02:
        print(f"  注意：源图比例与 3:2 相差 {cut:.0%}，cover 已裁掉多余边缘，确认主体没有被切")
    if kb > 200:
        print(f"  注意：{kb:.0f}KB 偏大，参考现有四张 40–55KB；可降 --quality 到 82")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
