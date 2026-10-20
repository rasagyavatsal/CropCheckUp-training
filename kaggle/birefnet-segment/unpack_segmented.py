"""Unpack the Kaggle run's per-class zips into <plantvillage>/segmented/<class>/<name>.png.

Fully transparent pixels still carry the original background colour; they are zeroed here so the
background can't come back via .convert("RGB") and so the PNGs compress better. Visible pixels
(including soft edges) are unchanged.

Usage: python unpack_segmented.py KAGGLE_OUTPUT_DIR PLANTVILLAGE_DIR
"""
import io
import json
import shutil
import sys
import zipfile
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image


def blank_and_save(args):
    data, out = args
    rgba = np.array(Image.open(io.BytesIO(data)).convert("RGBA"))
    rgba[rgba[..., 3] == 0, :3] = 0
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgba).save(out, optimize=True)


def members(zips, out_root):
    for z in zips:
        with zipfile.ZipFile(z) as zf:
            for name in zf.namelist():
                if name.endswith(".png"):
                    yield zf.read(name), out_root / name


if __name__ == "__main__":
    src, plantvillage = Path(sys.argv[1]), Path(sys.argv[2])
    zips = sorted(src.glob("segmented__*.zip"))
    with Pool() as pool:
        n = sum(1 for _ in pool.imap_unordered(blank_and_save, members(zips, plantvillage), chunksize=64))
    shutil.copy(src / "manifest.json", plantvillage / "segmented" / "manifest.json")
    manifest = json.loads((src / "manifest.json").read_text())
    print(f"{len(zips)} class zips, {n} PNGs written to {plantvillage / 'segmented'}")
    print(f"not started (time budget): {manifest['skipped_for_time']}")
    print(f"failures: {len(manifest['failures'])}, kept whole: {len(manifest['fallback_full_image'])}")
