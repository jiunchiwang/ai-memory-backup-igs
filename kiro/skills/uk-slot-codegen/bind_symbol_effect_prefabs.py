#!/usr/bin/env python3
"""Bind generated SymbolEffect prefabs to EffectPlate without Cocos Editor."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path


SYMBOL_COUNT_RE = re.compile(r"\bSYMBOL_COUNT\s*(?::\s*number\s*)?=\s*(\d+)")
SYMBOL_EFFECT_SIZE = 178


def read_symbol_count(target: Path) -> int:
    game_define = target / "assets/Script/Game_Define.ts"
    match = SYMBOL_COUNT_RE.search(game_define.read_text(encoding="utf-8-sig"))
    if not match:
        raise ValueError(f"SYMBOL_COUNT not found: {game_define}")
    return int(match.group(1))


def load_prefab_uuid(meta_path: Path) -> str:
    if not meta_path.exists():
        raise FileNotFoundError(f"Missing prefab meta: {meta_path}")
    data = json.loads(meta_path.read_text(encoding="utf-8-sig"))
    uuid = data.get("uuid")
    if not isinstance(uuid, str) or not uuid:
        raise ValueError(f"Missing uuid in prefab meta: {meta_path}")
    return uuid


def compress_uuid(uuid: str) -> str:
    """Convert a Cocos UUID to the compressed class id stored in prefab __type__."""
    hex_value = uuid.replace("-", "")
    if len(hex_value) != 32:
        raise ValueError(f"Invalid UUID: {uuid}")
    tail = hex_value[5:] + "0"
    encoded = base64.urlsafe_b64encode(bytes.fromhex(tail)).decode("ascii")[:18]
    return hex_value[:5] + encoded


def script_class_id(target: Path, relative_meta: str) -> str:
    return compress_uuid(load_prefab_uuid(target / relative_meta))


def ensure_prefab_content_size(prefab_path: Path, check_only: bool) -> bool:
    document = json.loads(prefab_path.read_text(encoding="utf-8-sig"))
    ui_transforms = [
        item for item in document
        if isinstance(item, dict)
        and item.get("__type__") == "cc.UITransform"
        and isinstance(item.get("_contentSize"), dict)
    ]
    if not ui_transforms:
        raise ValueError(f"UITransform contentSize not found: {prefab_path}")
    changed = any(
        item["_contentSize"].get("width") != SYMBOL_EFFECT_SIZE
        or item["_contentSize"].get("height") != SYMBOL_EFFECT_SIZE
        for item in ui_transforms
    )
    if changed and not check_only:
        for item in ui_transforms:
            item["_contentSize"]["width"] = SYMBOL_EFFECT_SIZE
            item["_contentSize"]["height"] = SYMBOL_EFFECT_SIZE
        prefab_path.write_text(
            json.dumps(document, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return changed


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Invalid PNG: {path}")
    return struct.unpack(">II", data[16:24])


def ensure_texture_and_atlas(target: Path, check_only: bool) -> bool:
    spine_dir = target / "assets/game/Spine/SymbolEffect"
    png_path = spine_dir / "SymbolEffect.png"
    atlas_path = spine_dir / "SymbolEffect.atlas"
    skeleton_path = spine_dir / "SymbolEffect.json"
    texture_changed = png_size(png_path) != (SYMBOL_EFFECT_SIZE, SYMBOL_EFFECT_SIZE)
    atlas = atlas_path.read_text(encoding="utf-8-sig")
    expected_atlas = re.sub(r"(?m)^size:\s*\d+\s*,\s*\d+\s*$", "size: 178,178", atlas, count=1)
    expected_atlas = re.sub(r"(?m)^  size:\s*\d+\s*,\s*\d+\s*$", "  size: 178, 178", expected_atlas)
    expected_atlas = re.sub(r"(?m)^  orig:\s*\d+\s*,\s*\d+\s*$", "  orig: 178, 178", expected_atlas)
    atlas_changed = expected_atlas != atlas
    skeleton = json.loads(skeleton_path.read_text(encoding="utf-8-sig"))
    skeleton_info = skeleton.get("skeleton", {})
    attachment = (
        skeleton.get("skins", {})
        .get("default", {})
        .get("slot0", {})
        .get("placeholder", {})
    )
    skeleton_changed = any(
        values.get(key) != SYMBOL_EFFECT_SIZE
        for values in (skeleton_info, attachment)
        for key in ("width", "height")
    )

    if not check_only:
        if texture_changed:
            temp_path = png_path.with_name("SymbolEffect.codegen-tmp.png")
            subprocess.run(
                [
                    "ffmpeg", "-y", "-loglevel", "error", "-i", str(png_path),
                    "-vf", "scale=178:178:flags=lanczos", "-frames:v", "1",
                    "-update", "1", str(temp_path),
                ],
                check=True,
            )
            temp_path.replace(png_path)
        if atlas_changed:
            atlas_path.write_text(expected_atlas, encoding="utf-8")
        if skeleton_changed:
            for values in (skeleton_info, attachment):
                values["width"] = SYMBOL_EFFECT_SIZE
                values["height"] = SYMBOL_EFFECT_SIZE
            skeleton_path.write_text(
                json.dumps(skeleton, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
    return texture_changed or atlas_changed or skeleton_changed


def ensure_symbol_spine_component(
    target: Path,
    prefab_path: Path,
    symbol_id: int,
    check_only: bool,
) -> bool:
    document = json.loads(prefab_path.read_text(encoding="utf-8-sig"))
    symbol_spine_type = script_class_id(
        target, "assets/Script/EffectPlate/SymbolSpine.ts.meta"
    )
    base_spine_type = script_class_id(
        target, "assets/Script/Spine/BaseSpine.ts.meta"
    )
    base_index = next(
        (
            index for index, item in enumerate(document)
            if isinstance(item, dict)
            and item.get("__type__") == base_spine_type
            and "m_spine" in item
        ),
        None,
    )
    symbol_index = next(
        (
            index for index, item in enumerate(document)
            if isinstance(item, dict)
            and item.get("__type__") == symbol_spine_type
            and "m_spine" in item
        ),
        None,
    )

    # Repair the previous broken migration, which changed BaseSpine into
    # SymbolSpine instead of adding SymbolSpine as a wrapper component.
    broken_migration = base_index is None and symbol_index is not None
    if broken_migration:
        broken = document[symbol_index]
        broken["__type__"] = base_spine_type
        for key in (
            "m_spineRootNode", "m_skinName", "m_spineAnimKey",
            "m_timeScale", "m_symbolId",
        ):
            broken.pop(key, None)
        base_index = symbol_index
        symbol_index = None

    if base_index is None:
        raise ValueError(f"BaseSpine component not found: {prefab_path}")

    expected_fields = {
        "m_spineRootNode": {"__id__": 2},
        "m_spine": {"__id__": base_index},
        "m_skinName": "default",
        "m_spineAnimKey": "",
        "m_timeScale": 1,
        "m_symbolId": symbol_id,
    }

    if symbol_index is None:
        comp_info_index = len(document) + 1
        digest = hashlib.sha1(f"SymbolSpine:{symbol_id}".encode()).digest()
        file_id = base64.b64encode(digest).decode("ascii")[:22]
        symbol_component = {
            "__type__": symbol_spine_type,
            "_name": "",
            "_objFlags": 0,
            "node": {"__id__": 1},
            "_enabled": True,
            "__prefab": {"__id__": comp_info_index},
            **expected_fields,
            "_id": "",
        }
        symbol_index = len(document)
        document.append(symbol_component)
        document.append({"__type__": "cc.CompPrefabInfo", "fileId": file_id})
        root = document[1]
        if not isinstance(root, dict) or not isinstance(root.get("_components"), list):
            raise ValueError(f"Root node components not found: {prefab_path}")
        root["_components"].append({"__id__": symbol_index})
        changed = True
    else:
        symbol_component = document[symbol_index]
        changed = broken_migration or any(
            symbol_component.get(key) != value
            for key, value in expected_fields.items()
        )
        root = document[1]
        root_refs = root.get("_components", []) if isinstance(root, dict) else []
        has_root_ref = {"__id__": symbol_index} in root_refs
        changed |= not has_root_ref
        if not check_only:
            symbol_component.update(expected_fields)
            if not has_root_ref:
                root_refs.append({"__id__": symbol_index})

    if changed and not check_only:
        prefab_path.write_text(
            json.dumps(document, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return changed


def expected_refs(
    target: Path,
    symbol_count: int,
    check_only: bool,
) -> tuple[list[dict[str, str]], bool]:
    prefab_dir = target / "assets/game/Prefab/Reel/SymbolEffect"
    refs = []
    component_changed = False
    for symbol_id in range(symbol_count):
        stem = f"SymbolEffect_{symbol_id:02d}.prefab"
        prefab_path = prefab_dir / stem
        if not prefab_path.exists():
            raise FileNotFoundError(f"Missing symbol effect prefab: {prefab_path}")
        component_changed |= ensure_symbol_spine_component(
            target, prefab_path, symbol_id, check_only
        )
        component_changed |= ensure_prefab_content_size(prefab_path, check_only)
        refs.append({
            "__uuid__": load_prefab_uuid(prefab_path.with_suffix(".prefab.meta")),
            "__expectedType__": "cc.Prefab",
        })
    uuids = [ref["__uuid__"] for ref in refs]
    if len(set(uuids)) != len(uuids):
        raise ValueError("Duplicate UUID found in SymbolEffect prefab metas")
    return refs, component_changed


def find_effect_plate_component(document: list[object]) -> dict[str, object]:
    for item in document:
        if isinstance(item, dict) and "m_symbolEffectPrefabs" in item:
            return item
    raise ValueError("EffectPlate component with m_symbolEffectPrefabs not found")


def bind(target: Path, check_only: bool = False) -> tuple[bool, int]:
    symbol_count = read_symbol_count(target)
    asset_changed = ensure_texture_and_atlas(target, check_only)
    template_changed = ensure_prefab_content_size(
        target / "assets/game/Prefab/Reel/SymbolEffectPrefab.prefab",
        check_only,
    )
    refs, component_changed = expected_refs(target, symbol_count, check_only)
    effect_plate = target / "assets/game/Prefab/Reel/EffectPlate.prefab"
    document = json.loads(effect_plate.read_text(encoding="utf-8-sig"))
    component = find_effect_plate_component(document)
    refs_changed = component["m_symbolEffectPrefabs"] != refs
    if refs_changed and not check_only:
        component["m_symbolEffectPrefabs"] = refs
        effect_plate.write_text(
            json.dumps(document, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return asset_changed or template_changed or refs_changed or component_changed, symbol_count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    changed, symbol_count = bind(args.target.resolve(), args.check)
    if args.check and changed:
        print(
            "FAIL: SymbolEffect texture/atlas/prefab size, bindings, or components do not match "
            f"SymbolEffect_00..{symbol_count - 1:02d}"
        )
        return 1
    action = "verified" if args.check else ("updated" if changed else "unchanged")
    print(f"OK: {action} {symbol_count} SymbolEffect prefab bindings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
