"""Move images that aren't usable leaf photos out of raw/ and segmented/ into <plantvillage>/removed/.

Found by reviewing the images BiRefNet kept whole. Files are moved rather than deleted, so this can be undone by
moving them back. Rerunning is safe: images already moved are skipped. Run after unpack_segmented.py, which would
otherwise bring the segmented copies back.

Usage: python scripts/remove_bad_images.py PLANTVILLAGE_DIR
"""
import json
import sys
from pathlib import Path

FIELD_SHOT = "field photo of several plants and cardboard, no single leaf"
STAKE = "photo of a plant-label stake, not a leaf"
BAD = {
    "Cherry_(including_sour)___healthy/4b1fcb7b-3fa6-4bd9-bad0-59328645eef6___JR_HL 4087": "grass only, no leaf",
    "Soybean___healthy/b32e4516-9cd7-4226-be52-26f413c97834___RS_HL 3512": "blank board, no leaf",
    "Strawberry___Leaf_scorch/50ef3cab-ca8a-4c59-854f-8b84e68f6da2___RS_L.Scorch 9909": STAKE,
    "Strawberry___Leaf_scorch/5297eecc-3b42-42e6-87af-d01be13b3052___RS_L.Scorch 9910": STAKE,
    "Strawberry___Leaf_scorch/30e43c7d-0621-4827-8a3a-3ae771996f1e___RS_L.Scorch 9959": STAKE,
    "Strawberry___Leaf_scorch/0dda76f4-d38e-4547-a341-546e84d72346___RS_L.Scorch 9973": FIELD_SHOT,
    "Strawberry___Leaf_scorch/12709186-36c7-40d4-bdfb-516255291ada___RS_L.Scorch 9939": FIELD_SHOT,
    "Strawberry___Leaf_scorch/247833b5-b655-418d-80c8-72fa4889dc5b___RS_L.Scorch 9978": FIELD_SHOT,
    "Strawberry___Leaf_scorch/264b9cb2-f632-4d66-bf0b-8f0f445866e9___RS_L.Scorch 9979": FIELD_SHOT,
    "Strawberry___Leaf_scorch/4e407e24-e738-407c-9b4e-a77e99f85a32___RS_L.Scorch 9975": FIELD_SHOT,
    "Strawberry___Leaf_scorch/98ddf858-e4f2-4a85-a98c-c1143d4c7394___RS_L.Scorch 9970": FIELD_SHOT,
    "Strawberry___Leaf_scorch/a1e269d3-9f90-4395-86fe-422c9c8e612e___RS_L.Scorch 9974": FIELD_SHOT,
    "Strawberry___Leaf_scorch/ac7bb639-98a6-4c24-bbfe-af98bf814849___RS_L.Scorch 9972": FIELD_SHOT,
    "Strawberry___Leaf_scorch/bc27498b-e23c-4f4f-b2ac-5202de687ef5___RS_L.Scorch 9955": FIELD_SHOT,
    "Strawberry___Leaf_scorch/dcc1d2a3-8801-45ba-a2e7-c0b1ca07b456___RS_L.Scorch 9954": FIELD_SHOT,
    "Strawberry___Leaf_scorch/f2060a8e-fcb2-46ba-809e-9e90110591db___RS_L.Scorch 9917": FIELD_SHOT,
    "Strawberry___Leaf_scorch/f77fb02a-c6fe-42dc-a43c-fd7fa3340fb8___RS_L.Scorch 9936": FIELD_SHOT,
}


if __name__ == "__main__":
    plantvillage = Path(sys.argv[1])
    manifest_path = plantvillage / "segmented" / "manifest.json"
    manifest = json.loads(manifest_path.read_text())

    moved = 0
    for key in BAD:
        cls, stem = key.split("/")
        for split in ("raw", "segmented"):
            for src in [f for f in (plantvillage / split / cls).iterdir() if f.stem == stem]:
                dst = plantvillage / "removed" / split / cls / src.name
                dst.parent.mkdir(parents=True, exist_ok=True)
                src.rename(dst)
                moved += 1
                if split == "segmented":
                    manifest["classes"][cls] -= 1
                    manifest["total"] -= 1

    removed = {f"{k}.png": reason for k, reason in BAD.items()}
    manifest["fallback_full_image"] = [p for p in manifest["fallback_full_image"] if p not in removed]
    manifest["removed"] = {**manifest.get("removed", {}), **removed}
    manifest_path.write_text(json.dumps(manifest, indent=1))
    print(f"moved {moved} files to {plantvillage / 'removed'}; {manifest['total']} segmented images remain")
