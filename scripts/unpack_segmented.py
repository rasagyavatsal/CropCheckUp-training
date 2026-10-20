"""Unpack the Kaggle runs' per-class zips into <plantvillage>/segmented/<class>/<name>.png.

Fully transparent pixels still carry the original background colour in older runs; they are zeroed
here so the background can't come back via .convert("RGB") and so the PNGs compress better.
Visible pixels (including soft edges) are unchanged.

The manifest is rebuilt from the images rather than taken from Kaggle, since a crashed run never
writes one: per-class counts checked against raw/, plus the fully opaque images, which are exactly
the close-ups where the mask was too small and the whole image was kept.

Usage: python scripts/unpack_segmented.py ZIPS_DIR PLANTVILLAGE_DIR
"""
import io
import json
import sys
import zipfile
from collections import Counter
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
    return out.parent.name, out.name, bool((rgba[..., 3] == 255).all())


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
        results = list(pool.imap_unordered(blank_and_save, members(zips, plantvillage), chunksize=64))

    counts = Counter(cls for cls, _, _ in results)
    raw_counts = {d.name: sum(1 for _ in d.iterdir()) for d in (plantvillage / "raw").iterdir() if d.is_dir()}
    mismatched = {c: {"raw": n, "segmented": counts.get(c, 0)} for c, n in raw_counts.items() if counts.get(c, 0) != n}
    manifest = {
        "total": len(results),
        "classes": dict(sorted(counts.items())),
        "mismatched_vs_raw": mismatched,
        "fallback_full_image": sorted(f"{cls}/{name}" for cls, name, opaque in results if opaque),
    }
    (plantvillage / "segmented" / "manifest.json").write_text(json.dumps(manifest, indent=1))
    print(f"{len(zips)} class zips, {len(results)} PNGs written to {plantvillage / 'segmented'}")
    print(f"classes not matching raw/: {mismatched or 'none'}")
    print(f"kept whole (mask below threshold): {len(manifest['fallback_full_image'])}")
