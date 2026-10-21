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
FIELD_SERIES = "from the outdoor cardboard-backed field series, a background shortcut for this class (issue #2)"
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
    "Strawberry___Leaf_scorch/43c14761-a95f-4732-b5cd-5c2d4d4940de___RS_L.Scorch 9900": FIELD_SERIES,
    "Strawberry___Leaf_scorch/bcae87ed-fbc3-4e4a-bd23-d689c0cd56e6___RS_L.Scorch 9901": FIELD_SERIES,
    "Strawberry___Leaf_scorch/6a6590c0-f929-4e31-b532-f9990c5db9fa___RS_L.Scorch 9902": FIELD_SERIES,
    "Strawberry___Leaf_scorch/c944933f-ef35-443a-b9fc-a53538ebdc3e___RS_L.Scorch 9903": FIELD_SERIES,
    "Strawberry___Leaf_scorch/e9f7de15-8ed4-4c7b-9c04-223b0e00de81___RS_L.Scorch 9904": FIELD_SERIES,
    "Strawberry___Leaf_scorch/b39b1fbc-038c-4bc8-8154-3c6ea168af62___RS_L.Scorch 9905": FIELD_SERIES,
    "Strawberry___Leaf_scorch/4b1e034b-d3c8-4db4-a105-258cbd1227fb___RS_L.Scorch 9906": FIELD_SERIES,
    "Strawberry___Leaf_scorch/5532c994-169e-4702-8772-a8e7c1eb1ee0___RS_L.Scorch 9907": FIELD_SERIES,
    "Strawberry___Leaf_scorch/231ee42e-ca7b-4c1f-9272-b963d445a966___RS_L.Scorch 9908": FIELD_SERIES,
    "Strawberry___Leaf_scorch/2104ca91-9e5f-4b5c-8981-e02d01fb9268___RS_L.Scorch 9911": FIELD_SERIES,
    "Strawberry___Leaf_scorch/ca33c3f3-52d8-4401-8a6a-962a9b13f11d___RS_L.Scorch 9912": FIELD_SERIES,
    "Strawberry___Leaf_scorch/6c63ab7c-68a8-4ff8-a001-f3e7cf16f722___RS_L.Scorch 9913": FIELD_SERIES,
    "Strawberry___Leaf_scorch/4e3d5499-017b-4de5-8087-d7f94caec399___RS_L.Scorch 9914": FIELD_SERIES,
    "Strawberry___Leaf_scorch/fac15e1c-0f8e-4467-8bdb-9494e8bb431e___RS_L.Scorch 9915": FIELD_SERIES,
    "Strawberry___Leaf_scorch/97e3b941-e828-47fa-87f8-338c626ba6a2___RS_L.Scorch 9916": FIELD_SERIES,
    "Strawberry___Leaf_scorch/23359934-8e33-43b5-882b-40c78f59d830___RS_L.Scorch 9918": FIELD_SERIES,
    "Strawberry___Leaf_scorch/918cea78-874e-4329-9025-a74c58798ee8___RS_L.Scorch 9919": FIELD_SERIES,
    "Strawberry___Leaf_scorch/c1f18830-3536-4082-87ce-1296af942a28___RS_L.Scorch 9920": FIELD_SERIES,
    "Strawberry___Leaf_scorch/7acfc5d0-b17e-4d35-909c-f9b0320b01c1___RS_L.Scorch 9921": FIELD_SERIES,
    "Strawberry___Leaf_scorch/7742ea93-4001-46da-84e7-15aa856472d5___RS_L.Scorch 9922": FIELD_SERIES,
    "Strawberry___Leaf_scorch/b607d594-ef1d-4cea-8638-48fcf971a748___RS_L.Scorch 9923": FIELD_SERIES,
    "Strawberry___Leaf_scorch/e4d9dc76-f555-4ad9-a7e5-33a21ae5e6cf___RS_L.Scorch 9924": FIELD_SERIES,
    "Strawberry___Leaf_scorch/79c2506c-98e7-4e81-8daa-cc30fcc19436___RS_L.Scorch 9925": FIELD_SERIES,
    "Strawberry___Leaf_scorch/83c52095-d426-4f63-835f-215547a65ea0___RS_L.Scorch 9926": FIELD_SERIES,
    "Strawberry___Leaf_scorch/0b440206-f9aa-463a-9c52-3bc5721fdcb5___RS_L.Scorch 9927": FIELD_SERIES,
    "Strawberry___Leaf_scorch/99ac9cd2-8c79-4f36-b708-c5521025418b___RS_L.Scorch 9928": FIELD_SERIES,
    "Strawberry___Leaf_scorch/f78cfb53-cacc-4c0d-bccd-5ab3914e6351___RS_L.Scorch 9929": FIELD_SERIES,
    "Strawberry___Leaf_scorch/a8a746ee-d8c4-48c6-8601-cd72e7bbf235___RS_L.Scorch 9930": FIELD_SERIES,
    "Strawberry___Leaf_scorch/e285ffe0-4b24-4651-950e-014f82aa4df3___RS_L.Scorch 9931": FIELD_SERIES,
    "Strawberry___Leaf_scorch/96112daa-d4f5-4d7a-b968-b6858eb4459b___RS_L.Scorch 9932": FIELD_SERIES,
    "Strawberry___Leaf_scorch/2318c34f-6d18-421c-87ef-6c87cba47c79___RS_L.Scorch 9933": FIELD_SERIES,
    "Strawberry___Leaf_scorch/55f79b76-619c-4fad-8fbd-1663a4c13f2f___RS_L.Scorch 9935": FIELD_SERIES,
    "Strawberry___Leaf_scorch/1ad2c944-a4cf-4c97-a31f-6265c0a927e1___RS_L.Scorch 9937": FIELD_SERIES,
    "Strawberry___Leaf_scorch/5374828c-87b2-4ef9-a492-9a786092169d___RS_L.Scorch 9938": FIELD_SERIES,
    "Strawberry___Leaf_scorch/8521b2b5-d5fa-42fe-ad72-d0f5c94b3ca8___RS_L.Scorch 9940": FIELD_SERIES,
    "Strawberry___Leaf_scorch/d89256de-8d57-49d0-9fa3-3be4a3bb3c20___RS_L.Scorch 9941": FIELD_SERIES,
    "Strawberry___Leaf_scorch/e4a821c6-7c21-4876-b484-a25738e92c7e___RS_L.Scorch 9942": FIELD_SERIES,
    "Strawberry___Leaf_scorch/ca0ba54f-4cb3-4565-bc9b-70e5ef4eda37___RS_L.Scorch 9943": FIELD_SERIES,
    "Strawberry___Leaf_scorch/974dcb97-08a8-4b8a-aa40-f9a02c9e2ec2___RS_L.Scorch 9944": FIELD_SERIES,
    "Strawberry___Leaf_scorch/eccc2000-fb04-4c85-8a90-11498d11addd___RS_L.Scorch 9945": FIELD_SERIES,
    "Strawberry___Leaf_scorch/12836245-bd1b-4032-b758-ac9128f5f31c___RS_L.Scorch 9946": FIELD_SERIES,
    "Strawberry___Leaf_scorch/36307818-823a-4874-a556-c2c874314753___RS_L.Scorch 9947": FIELD_SERIES,
    "Strawberry___Leaf_scorch/2280786b-60a7-4005-8b52-d1cf1d434081___RS_L.Scorch 9948": FIELD_SERIES,
    "Strawberry___Leaf_scorch/320e9e4c-9d1e-456c-8eb4-e2c75bdf726f___RS_L.Scorch 9949": FIELD_SERIES,
    "Strawberry___Leaf_scorch/6d1f842b-d10d-4e78-a277-e8e909c38346___RS_L.Scorch 9950": FIELD_SERIES,
    "Strawberry___Leaf_scorch/65e5f561-70cd-4282-98d6-9ecc667881e5___RS_L.Scorch 9951": FIELD_SERIES,
    "Strawberry___Leaf_scorch/b5c0f28b-47de-45c5-a3ac-b612e0bee8ea___RS_L.Scorch 9952": FIELD_SERIES,
    "Strawberry___Leaf_scorch/11d22595-35dc-46be-9436-79bcacb8880a___RS_L.Scorch 9953": FIELD_SERIES,
    "Strawberry___Leaf_scorch/9ab653fe-889e-4f4a-a48b-c8d9a339fdf1___RS_L.Scorch 9956": FIELD_SERIES,
    "Strawberry___Leaf_scorch/062b151a-8132-477d-afff-dad79f0fbdd6___RS_L.Scorch 9958": FIELD_SERIES,
    "Strawberry___Leaf_scorch/e9d15f1c-6ff9-4220-918d-96a726279081___RS_L.Scorch 9960": FIELD_SERIES,
    "Strawberry___Leaf_scorch/804af05b-899f-44c2-8606-1b87bbe78c69___RS_L.Scorch 9961": FIELD_SERIES,
    "Strawberry___Leaf_scorch/c813028f-add4-4591-832c-72163c6ff701___RS_L.Scorch 9962": FIELD_SERIES,
    "Strawberry___Leaf_scorch/d06a9be8-2cfc-464c-8b2b-20f5442ea8fb___RS_L.Scorch 9963": FIELD_SERIES,
    "Strawberry___Leaf_scorch/ad48a0f5-3036-4d59-9d9b-27a5ea752131___RS_L.Scorch 9964": FIELD_SERIES,
    "Strawberry___Leaf_scorch/71f8c314-ef34-4521-b575-e06f8455f449___RS_L.Scorch 9965": FIELD_SERIES,
    "Strawberry___Leaf_scorch/5ab90f76-2584-402a-a8d2-661c0ebb354f___RS_L.Scorch 9966": FIELD_SERIES,
    "Strawberry___Leaf_scorch/87483aae-1c8c-47fc-af2d-512336395b2f___RS_L.Scorch 9967": FIELD_SERIES,
    "Strawberry___Leaf_scorch/32abf673-2dc9-45f2-984a-c1e920a274f9___RS_L.Scorch 9968": FIELD_SERIES,
    "Strawberry___Leaf_scorch/4df58d4e-39bf-4f90-bfc0-8d4e79f287ea___RS_L.Scorch 9969": FIELD_SERIES,
    "Strawberry___Leaf_scorch/91795b04-c65c-4a0e-99d0-793b797ed3c4___RS_L.Scorch 9971": FIELD_SERIES,
    "Strawberry___Leaf_scorch/c3da5694-ff77-42fe-9ce5-059318a22214___RS_L.Scorch 9976": FIELD_SERIES,
    "Strawberry___Leaf_scorch/70c7d7ed-2ca9-41f4-a19a-864e20f5bbb8___RS_L.Scorch 9977": FIELD_SERIES,
    "Strawberry___Leaf_scorch/70d2220e-f8b2-444f-8c75-12e49979d4c7___RS_L.Scorch 9980": FIELD_SERIES,
    "Strawberry___Leaf_scorch/e84ee8ed-5a7b-46e7-ae90-5b9571d789dc___RS_L.Scorch 9981": FIELD_SERIES,
    "Strawberry___Leaf_scorch/b3eb2228-f38e-4472-a39e-3e39917bac3d___RS_L.Scorch 9982": FIELD_SERIES,
    "Strawberry___Leaf_scorch/5c55f23a-1b75-460a-a0ea-7491dcb32eec___RS_L.Scorch 9983": FIELD_SERIES,
    "Strawberry___Leaf_scorch/6007f5b7-bd62-429b-a1cb-dea633ad3590___RS_L.Scorch 9984": FIELD_SERIES,
    "Strawberry___Leaf_scorch/c0be4fed-19c1-40ba-bb49-69b48a08015c___RS_L.Scorch 9985": FIELD_SERIES,
    "Strawberry___Leaf_scorch/115b843f-5c32-48dd-9602-b8fa5a3c7b29___RS_L.Scorch 9986": FIELD_SERIES,
    "Strawberry___Leaf_scorch/9148e2e9-20b1-4a2e-a928-d76718a36aa8___RS_L.Scorch 9987": FIELD_SERIES,
    "Strawberry___Leaf_scorch/2db4d464-0256-4484-8e28-daacafbba8be___RS_L.Scorch 9988": FIELD_SERIES,
    "Strawberry___Leaf_scorch/b6d298a7-40a5-4994-a430-190bda35abb4___RS_L.Scorch 9989": FIELD_SERIES,
    "Strawberry___Leaf_scorch/bfde826a-4ff5-49e0-b6b8-f3a14f4c7eeb___RS_L.Scorch 9990": FIELD_SERIES,
    "Strawberry___Leaf_scorch/c7712210-979f-4de2-9c4f-7067831286be___RS_L.Scorch 9991": FIELD_SERIES,
    "Strawberry___Leaf_scorch/2d90a8b3-1a11-4c72-9334-42fb50862f6d___RS_L.Scorch 9992": FIELD_SERIES,
    "Strawberry___Leaf_scorch/bfbc366b-d28e-48d6-9f82-d57535e17889___RS_L.Scorch 9993": FIELD_SERIES,
    "Strawberry___Leaf_scorch/02d53294-aa1c-4a33-8bdc-fd987e700305___RS_L.Scorch 9994": FIELD_SERIES,
    "Strawberry___Leaf_scorch/79d1eb82-6017-447a-b43f-3c477c26bd42___RS_L.Scorch 9995": FIELD_SERIES,
    "Strawberry___Leaf_scorch/4861c37b-e04f-4d15-b068-dbbd9ee5e722___RS_L.Scorch 9996": FIELD_SERIES,
    "Strawberry___Leaf_scorch/ee7d25d9-bb62-44ea-b70c-63ae7a05bc9f___RS_L.Scorch 9997": FIELD_SERIES,
    "Strawberry___Leaf_scorch/242657d2-7e24-4016-b837-10e7f905f02e___RS_L.Scorch 9998": FIELD_SERIES,
    "Strawberry___Leaf_scorch/5231f1a9-85f9-4485-8147-d2f3d42b18ec___RS_L.Scorch 9999": FIELD_SERIES,
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
