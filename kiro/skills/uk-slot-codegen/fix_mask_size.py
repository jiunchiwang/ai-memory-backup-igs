"""
fix_mask_size.py — 自動修正 SlotPlate_MG.prefab 的 Mask contentSize
用法：py fix_mask_size.py <target_path>

從 Game_Define.ts 讀 COL/ROW/SymbolWidth/SymbolHeight，
計算正確 mask 尺寸（w = COL * SymbolWidth, h = ROW * SymbolHeight），
然後更新 SlotPlate_MG.prefab 裡所有 _contentSize。
"""
import sys
import re
import json
from pathlib import Path

def extract_define_value(content: str, name: str) -> int:
    """從 Game_Define.ts 提取靜態數值"""
    m = re.search(rf'static\s+{name}\s*=\s*(\d+)', content)
    if not m:
        print(f"ERROR: Cannot find {name} in Game_Define.ts")
        sys.exit(1)
    return int(m.group(1))

def main():
    if len(sys.argv) < 2:
        print("Usage: py fix_mask_size.py <target_path>")
        sys.exit(1)
    
    target = Path(sys.argv[1])
    define_path = target / "assets" / "Script" / "Game_Define.ts"
    prefab_path = target / "assets" / "game" / "Prefab" / "Reel" / "SlotPlate_MG.prefab"
    
    if not define_path.exists():
        print(f"ERROR: {define_path} not found")
        sys.exit(1)
    if not prefab_path.exists():
        print(f"ERROR: {prefab_path} not found")
        sys.exit(1)
    
    # 讀取 Game_Define.ts
    define_content = define_path.read_text(encoding='utf-8')
    col = extract_define_value(define_content, 'COL')
    row = extract_define_value(define_content, 'ROW')
    sym_w = extract_define_value(define_content, 'SymbolWidth')
    sym_h = extract_define_value(define_content, 'SymbolHeight')
    
    # 計算正確尺寸
    mask_w = col * sym_w
    mask_h = row * sym_h
    print(f"Game_Define: COL={col}, ROW={row}, SymbolWidth={sym_w}, SymbolHeight={sym_h}")
    print(f"Expected Mask: width={mask_w}, height={mask_h}")
    
    # 讀取並修正 prefab
    prefab_content = prefab_path.read_text(encoding='utf-8')
    prefab_data = json.loads(prefab_content)
    
    fixed_count = 0
    for i, node in enumerate(prefab_data):
        if isinstance(node, dict) and node.get("__type__") == "cc.UITransform":
            cs = node.get("_contentSize")
            if isinstance(cs, dict) and "__type__" in cs:
                old_w = cs.get("width", 0)
                old_h = cs.get("height", 0)
                if old_w != mask_w or old_h != mask_h:
                    print(f"  Fixing node[{i}]: {old_w}x{old_h} -> {mask_w}x{mask_h}")
                    cs["width"] = mask_w
                    cs["height"] = mask_h
                    fixed_count += 1
                else:
                    print(f"  node[{i}]: already correct ({mask_w}x{mask_h})")
    
    if fixed_count > 0:
        prefab_path.write_text(json.dumps(prefab_data, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"\nDONE: Fixed {fixed_count} contentSize(s) in SlotPlate_MG.prefab")
    else:
        print("\nOK: All contentSize values already correct")

if __name__ == "__main__":
    main()
