---
name: uk-slot-prefab-target-overrides
description: 在 UK 老虎機 Cocos 專案要用編輯器開啟或修改 MainGame.prefab 這類含巢狀 prefab 的檔案時、或發現 GameView 的 @property 元件參考（m_slotReels / m_effectPlate / m_buyBonus 等）執行期是 null、轉輪整片空白卻沒有任何錯誤訊息時使用。涵蓋 Cocos Creator 3.6.2 重存 prefab 會清掉 targetOverrides.source 的靜默損壞、檢查指令、以 git HEAD 為對照的修復法，以及避免踩到的編輯紀律。
---

# MainGame.prefab 的 targetOverrides 靜默損壞

## 症狀

- `GameView` 的 `m_slotReels` / `m_effectPlate` / `m_reelDevTool` / `m_buyBonus` /
  `m_plateSpinBtn` / `m_bigWinComp` / `m_expandFollowers[]` … 執行期**全是 `null`**
- 轉輪區整片空白（`CreateSymbol()` 沒被呼叫）
- **完全沒有任何錯誤訊息** —— GameView 對這些欄位一律 `?.` 呼叫，靜默跳過
- `git diff` 看起來很正常

## 根因

Cocos Creator 3.6.2 在 **prefab 編輯模式**開啟並重存 `MainGame.prefab` 時，
會把 `cc.TargetOverrideInfo` 裡 **`source` 指向「元件」的那些條目清成 `null`**。
`source` 指向 `cc.Node` 的條目不受影響。

`targetOverrides` 是 Cocos 存「跨 prefab 參考」的機制：
`m_slotReels` 指到的 `SlotReel` 在另一支巢狀 prefab 裡，
所以它在 `MainGame.prefab` 的 GameView 元件上**序列化成 `null` 是正常的**，
真正的連線資訊放在 `targetOverrides`，實例化時才寫回去。
`source` 被清掉 ⇒ 沒有目標元件可寫 ⇒ 永遠是 null。

⚠️ **正因為欄位本來就是 `null`，直接看檔案 diff 看不出壞掉。**
唯一的判斷點是 `targetOverrides[].source` 有沒有 `__id__`。

## 檢查（source 為 null 的數量應為 0）

```python
import json
d = json.load(open(PREFAB_PATH, encoding='utf-8'))
bad = [o for o in d if isinstance(o, dict)
       and o.get('__type__') == 'cc.TargetOverrideInfo'
       and o.get('source') is None]
print(len(bad))          # 0 才正常
```

想確認損壞規模，比對 source 的型別分佈（正常檔會有 `cc.Node` 與各元件 ccclass id 兩類；
壞掉的檔會出現一堆 `None`）。

## 修復（以 git HEAD 為對照）

前提：`HEAD` 版本是好的（壞損發生在工作區）。不能整檔 checkout，因為工作區
往往還混著別人未 commit 的掛載工作。

作法：以 **`(propertyPath, targetInfo.localID)`** 當 key 比對，把 `source` 補回去。
不能用陣列 index 對照——新增節點會讓 index 整批位移。

```python
def key(d, o):
    ti = o.get('targetInfo')
    return (json.dumps(o.get('propertyPath')),
            json.dumps(d[ti['__id__']].get('localID') if ti else None))

# 1. 從 git show HEAD:<path> 讀好版，建 key -> source 的 __type__ 對照表
# 2. 在工作區找出該 __type__ 的元件 index（同型別應唯一，不唯一就要停下來人工判斷）
# 3. 對每個 source is None 的條目，依 key 查出型別、寫回 {'__id__': idx}
# 4. 統計 fixed / unmatched，unmatched 不得為 0 以外的數字就當修失敗
```

修完 `asset_reimport` 該 prefab，再到預覽驗證那些欄位不是 null
（走 scene graph 讀 `gv.m_slotReels?.constructor.name`，見 `uk-slot-preview-runtime`）。

修之前先把壞掉的檔複製一份備份。

## 預防

- **非必要不要用編輯器開 `MainGame.prefab` 的 prefab 編輯模式**（包含只是「開起來看一下樹狀結構」）
- 要改巢狀 prefab（ExtraBetNode、各種 Manager prefab 等）就**只開那支子 prefab**，不要開 MainGame
- 需要看 MainGame 的節點樹時，改用**執行期**走 scene graph，不要開編輯器
- 真的非開不可 → 開完立刻跑上面的檢查指令

## 順帶：MCP 設不了參考型別的欄位（Node 也一樣）

`component_set_property` 傳 `{ refNodeUuid }`，值會被當成**字面字串**塞進去
（存檔後在 prefab 裡會看到 `"m_xxx": "{\"refNodeUuid\": \"...\"}"`，
連你寫的空白排版都一字不差保留）。

⚠️ **2026-08-19 修正**：本節原本寫「只設得了 Node 參考、只有元件型別會壞」——**這是錯的**。
實測 `BlackMaskManager.m_blackMask`（宣告型別就是 `Node`）同樣變成字面字串。
`BaseSpine` / `Button` 這類元件型別當然也壞。**Node 與元件都一樣壞。**

真正的成因不是欄位型別，是 `component_set_property` 的 `value` 參數
**在 schema 裡沒宣告 `type`**，Claude Code 會把它當純文字送，工具的「物件 → 參考」
分支永遠不觸發。對照證據：同一個 server 的 `node_set_property.props` 有宣告
`"type": "object"`，傳 `{"position":{"x":11,"y":22,"z":33}}` 就正確變成 `cc.Vec3`。
∴ 這是 client/schema interop，**不是工具邏輯壞**，別拿這個去回報「MCP 壞了」。
完整診斷步驟見 `ms-mcp-untyped-param-string-coercion`。

作法：用 MCP `component_add` 把元件加上去（它會正確產生 `CompPrefabInfo`），
**存檔關閉後**再直接改 prefab JSON 把參考欄位寫成
`{"__id__": <目標 node／元件在檔案裡的 index>}`，然後 `asset_reimport`。

驗證兩層，都不能省：
1. 讀檔確認是 `{"__id__": N}` 而不是字串——不要相信 `ok: true`
2. **開預覽走 scene graph 讀實際物件**（檔案對 ≠ 執行期解析得到）

改檔前先確認該 prefab 已 commit，這樣實驗搞壞可以 `git checkout --` 還原。
