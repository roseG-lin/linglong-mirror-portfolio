# -*- coding: utf-8 -*-
"""证据图工具契约 · tools/evidence.py

锁三件事：
1. 落盘规格：宽 ≤1400、JPEG、EXIF 清干净（截图常带设备/软件信息）；
2. 脱敏有效：--redact 区域像素必须被打烂，区域外一个像素都不许动；
3. 保密门：涉密项目没打码也没 --checked 时直接拒绝执行（保密铁律的机械版本）。

跑法（站点根目录）：
    python -m pytest tests/test_evidence_tool.py -q

零外呼；临时目录自管（本机 tmp_path 工厂目录有 WinError 5，不用它）。
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "evidence.py"
Image = pytest.importorskip("PIL.Image")


def solid(path: Path, size=(1600, 900), exif=False) -> None:
    im = Image.new("RGB", size, (220, 40, 40))
    if exif:
        ex = Image.Exif()
        ex[0x010F] = "TestCam"   # Make
        ex[0x0112] = 1           # Orientation
        im.save(path, exif=ex.tobytes())
    else:
        im.save(path)


def noise(path: Path, size=(400, 240)) -> None:
    """确定性噪点：马赛克后像素必变，便于断言"打码真的打了"。"""
    w, h = size
    im = Image.new("RGB", size)
    im.putdata([
        ((x * 7 + y * 13) % 256, (x * 3 + y * 29) % 256, (x * 17 + y * 5) % 256)
        for y in range(h) for x in range(w)
    ])
    im.save(path)


def run(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(TOOL), *args],
        cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", timeout=120,
    )


@pytest.fixture()
def workdir():
    d = Path(tempfile.mkdtemp(prefix="evid-"))
    try:
        yield d
    finally:
        shutil.rmtree(d, ignore_errors=True)


BASE = ["--slug", "99-test", "--no", "01", "--op", "点一下", "--num", "测试 1 项"]
OUT = Path("case") / "assets" / "evidence" / "99-test-01.jpg"


def mean_diff(a: "Image.Image", b: "Image.Image", box: tuple[int, int, int, int]) -> float:
    pa, pb = a.crop(box).load(), b.crop(box).load()
    w, h = box[2] - box[0], box[3] - box[1]
    total = 0
    for y in range(0, h, 3):
        for x in range(0, w, 3):
            total += sum(abs(pa[x, y][i] - pb[x, y][i]) for i in range(3))
    return total / (len(range(0, h, 3)) * len(range(0, w, 3)) * 3)


def test_install_normalizes_size_jpeg_and_strips_exif(workdir: Path):
    src = workdir / "src.png"
    solid(src, exif=True)
    assert len(Image.open(src).getexif()) > 0, "源图应带 EXIF，否则这条测试证明不了清理"

    r = run(workdir, str(src), *BASE)
    assert r.returncode == 0, r.stdout + r.stderr
    out = workdir / OUT
    assert out.exists(), r.stdout

    im = Image.open(out)
    assert im.format == "JPEG"
    assert im.width == 1400, "宽图应压到 1400"
    assert im.height == round(900 * 1400 / 1600)
    assert len(im.getexif()) == 0, "EXIF 必须清掉"
    assert '<figure class="evidence">' in r.stdout
    assert "ev-meta" in r.stdout


def test_html_block_declares_the_real_file_size(workdir: Path):
    src = workdir / "src.png"
    solid(src)
    r = run(workdir, str(src), *BASE)
    assert r.returncode == 0, r.stdout + r.stderr
    m = re.search(r'width="(\d+)" height="(\d+)"', r.stdout)
    assert m, r.stdout
    assert (int(m.group(1)), int(m.group(2))) == Image.open(workdir / OUT).size


def test_redaction_destroys_the_region_and_leaves_the_rest(workdir: Path):
    src = workdir / "noise.png"
    noise(src)

    clean_dir = workdir / "clean"
    clean_dir.mkdir()
    assert run(clean_dir, str(src), *BASE).returncode == 0
    r = run(workdir, str(src), *BASE, "--redact", "10,10,40,40")
    assert r.returncode == 0, r.stdout + r.stderr

    a = Image.open(clean_dir / OUT).convert("RGB")
    b = Image.open(workdir / OUT).convert("RGB")
    assert a.size == b.size

    w, h = a.size
    inside = (round(w * 0.12), round(h * 0.12), round(w * 0.38), round(h * 0.38))
    outside = (round(w * 0.55), round(h * 0.55), round(w * 0.95), round(h * 0.95))
    assert mean_diff(a, b, inside) > 20, "打码区应该被明显破坏"
    assert mean_diff(a, b, outside) < 1, "打码不许溢出到区域外"


def test_redaction_box_edges_are_exact(workdir: Path):
    """百分比是含边界的：0,0,50,50 只动左上四分之一，右下角保持原样。"""
    src = workdir / "noise.png"
    noise(src, size=(320, 320))
    clean_dir = workdir / "clean"
    clean_dir.mkdir()
    assert run(clean_dir, str(src), *BASE).returncode == 0
    assert run(workdir, str(src), *BASE, "--redact", "0,0,50,50", "--force").returncode == 0

    a = Image.open(clean_dir / OUT).convert("RGB")
    b = Image.open(workdir / OUT).convert("RGB")
    w, h = a.size
    assert mean_diff(a, b, (round(w * 0.55), round(h * 0.55), w - 1, h - 1)) < 1


def test_confidential_without_redaction_is_refused(workdir: Path):
    src = workdir / "src.png"
    solid(src, size=(400, 240))
    r = run(workdir, str(src), *BASE, "--confidential")
    assert r.returncode == 3, r.stdout + r.stderr
    assert "涉密" in r.stdout
    assert not (workdir / "case").exists(), "被拒时不许落盘"


def test_confidential_with_checked_is_allowed(workdir: Path):
    src = workdir / "src.png"
    solid(src, size=(400, 240))
    r = run(workdir, str(src), *BASE, "--confidential", "--checked")
    assert r.returncode == 0, r.stdout + r.stderr
    assert (workdir / OUT).exists()


def test_bad_redaction_spec_is_rejected(workdir: Path):
    src = workdir / "src.png"
    solid(src, size=(400, 240))
    for spec in ("50,50", "a,b,c,d", "40,10,10,40"):
        r = run(workdir, str(src), *BASE, "--redact", spec)
        assert r.returncode != 0, f"{spec} 应被拒"
        assert not (workdir / "case").exists()


def test_refuses_to_overwrite_without_force(workdir: Path):
    src = workdir / "src.png"
    solid(src, size=(400, 240))
    assert run(workdir, str(src), *BASE).returncode == 0
    r = run(workdir, str(src), *BASE)
    assert r.returncode == 5, r.stdout + r.stderr
    assert "--force" in r.stdout


def test_never_upscales(workdir: Path):
    src = workdir / "small.png"
    solid(src, size=(640, 360))
    r = run(workdir, str(src), *BASE)
    assert r.returncode == 0, r.stdout + r.stderr
    assert Image.open(workdir / OUT).width == 640
    assert "会糊" in r.stdout


def test_missing_source_exits_2(workdir: Path):
    r = run(workdir, str(workdir / "nope.png"), *BASE)
    assert r.returncode == 2
