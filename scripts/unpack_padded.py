"""Merge the padded BiRefNet run (kaggle/birefnet-padded) into <plantvillage>/segmented/.

Only images that run segmented are written, and only over images the manifest still lists as kept whole. Masks
that are hazy (more than MAX_HAZE of pixels semi-transparent) are skipped too: the run's IoU check doesn't catch
BiRefNet's faded, smeared masks, and above ~8% they visibly leave background in or fade out leaf. Everything
skipped stays whole and stays in `fallback_full_image`. The chosen pad ratio, IoU and haze per merged image go
under `padded` in the manifest. Run after unpack_segmented.py and remove_bad_images.py.

Usage: python scripts/unpack_padded.py KAGGLE_OUTPUT_DIR PLANTVILLAGE_DIR
  KAGGLE_OUTPUT_DIR holds segmented_padded.zip and manifest_padded.json
"""
import io
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

MAX_HAZE = 0.08

if __name__ == "__main__":
    src, plantvillage = Path(sys.argv[1]), Path(sys.argv[2])
    seg = plantvillage / "segmented"
    manifest = json.loads((seg / "manifest.json").read_text())
    padded = json.loads((src / "manifest_padded.json").read_text())

    fallback = set(manifest["fallback_full_image"])
    missing = sorted(set(padded["chosen"]) - fallback)
    if missing:
        sys.exit(f"{len(missing)} padded images aren't in fallback_full_image, e.g. {missing[0]}; not merging")

    merged, hazy = {}, 0
    with zipfile.ZipFile(src / "segmented_padded.zip") as zf:
        for key, info in padded["chosen"].items():
            png = zf.read(f"segmented/{key}")
            alpha = np.asarray(Image.open(io.BytesIO(png)))[..., 3]
            haze = float(((alpha > 25) & (alpha < 230)).mean())
            if haze > MAX_HAZE:
                hazy += 1
                continue
            (seg / key).write_bytes(png)
            merged[key] = {**info, "haze": round(haze, 3)}

    manifest["fallback_full_image"] = sorted(fallback - set(merged))
    manifest["padded"] = merged
    (seg / "manifest.json").write_text(json.dumps(manifest, indent=1))
    print(f"{len(merged)} images replaced, {hazy} skipped as hazy; {len(manifest['fallback_full_image'])} still kept whole")
