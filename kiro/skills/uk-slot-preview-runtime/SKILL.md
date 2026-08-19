---
name: uk-slot-preview-runtime
description: 在瀏覽器把 UK 老虎機 Cocos 預覽真的跑起來做執行期實測時使用。涵蓋預覽網址必加的 ?forceTadaUat=1、開機三道關卡（Continue → PLAY → IDLE）各自解鎖了什麼、用 chrome-devtools 走 scene graph 取元件與對 canvas 送點擊、以及「看起來程式壞了其實是沒連上 server」這類誤判的分辨法。當你要驗證某個功能在真機跑得對不對、或預覽畫面轉輪空白 / 元件是 null 時觸發。
---

# UK Slot 預覽執行期實測

## ⚠️ 網址一定要帶 `?forceTadaUat=1`

```
http://<host>:7456/?forceTadaUat=1
```

Cocos MCP 的 `preview_query_url`（以及編輯器的 ▶ 按鈕）只給**裸 base URL**。
直接開那個裸網址，遊戲會卡在：

```
Common State LOGIN
RETRYMANAGER.CHECK_SOCKET false   ← 無限重試
```

**這個參數在 repo 裡 grep 不到**（assets / extensions / 所有 .md 都沒有），
純環境知識，不知道就只能問人。

### 沒連上 server 會連鎖壞掉哪些東西

socket 連不上 ⇒ **info ack 永遠不會到**，於是：

| 東西 | 沒連線時的狀態 | 容易被誤判成 |
|------|--------------|------------|
| `IGameInfoData` 的 `ShowExtra` / `Mul` / `JPOdds` … | 全是預設值（false / 空陣列） | 「我的 info 處理寫錯了」 |
| game bundle | 沒載 | — |
| `LoadSymbol()` → `CreateSymbol()` | 沒跑 ⇒ `m_isLoadingComplete=false`、`m_allColumns` 空 | 「轉輪程式壞了」 |
| 轉輪區 | 只有背景圖，沒有任何 symbol | 「盤面邏輯壞了」 |
| 任何寫盤面的呼叫 | 踩空 `m_allColumns[...]` → `TypeError: Cannot read properties of undefined` | 「我剛加的方法有 bug」 |

⛔ **看到這組症狀，先確認網址參數，再懷疑程式。**

## 開機三道關卡

預覽開起來不等於進得了遊戲。要跑到 `IDLE` 才有轉輪、才按得動 ExtraBet / BuyBonus 這類只在 IDLE 可用的按鈕：

1. **特色介紹頁** → 按 `Continue`
2. **前導 PLAY 頁** → 按 `PLAY`（這步之後才 `LoadSymbol` → `CreateSymbol`）
3. 進 `PLATE_SHOW` → `IDLE`

每關之間留 2~8 秒。跳過任一關就去讀 `m_slotReels.m_plateInfo`，拿到的都是空的。

## 用 chrome-devtools 驅動

### ⛔ 重新載入用 `navigate_page`，不要用 `new_page`

`new_page` 是**開新分頁**。拿它當「重新整理」用，每檢查一次新建置就多一個分頁，
最後會疊出一整排——而且**每個分頁都是獨立的遊戲 instance**，各自連 socket、各自跑 60fps，
會拖慢預覽也可能干擾連線。

```
navigate_page  { type: "reload", ignoreCache: true }   # 原地重載，分頁數不變
close_page     { pageId }                              # 收掉多餘分頁
list_pages                                             # 先看有幾個
```

會誤用多半是因為執行 script 時撞到 `Execution context was destroyed`
（頁面還在導航就跑 script）。正解是**等它載完再執行**（`evaluate_script` 開頭先 `await sleep`，
或直接重試一次），不是換一個乾淨分頁。

### 點 canvas（畫面上沒有 DOM 元素可點）

Cocos 全畫在一張 `<canvas>` 上，`take_snapshot` 取不到可點的 uid，只能自己送事件：

```js
const cv = document.querySelector('canvas');
const click = (x, y) => {                       // x,y 用截圖上的頁面座標
  const o = { bubbles: true, cancelable: true, clientX: x, clientY: y,
              button: 0, pointerId: 1, pointerType: 'mouse', isPrimary: true };
  cv.dispatchEvent(new PointerEvent('pointerdown', o));
  cv.dispatchEvent(new MouseEvent('mousedown', o));
  cv.dispatchEvent(new PointerEvent('pointerup', o));
  cv.dispatchEvent(new MouseEvent('mouseup', o));
};
```

### 走 scene graph 取元件（比按座標可靠得多）

```js
const find = (names) => {
  const out = {};
  const walk = (n) => {
    if (!n) return;
    for (const c of (n._components || [])) {
      const k = c.constructor.name;
      if (names.includes(k)) out[k] = c;
    }
    for (const ch of (n.children || [])) walk(ch);
  };
  walk(cc.director.getScene());
  return out;
};
const { GameView, SlotReel, EffectPlate } = find(['GameView','SlotReel','EffectPlate']);
```

`private` 在執行期不存在，`gv.m_xxx` 直接讀得到。

### 直接叫方法，不要硬點按鈕

要驗「按下某顆按鈕的完整流程」時，**先斷言 `CheckCanUseBtn()` 之類的可用性檢查為 true**（證明按鈕確實按得動），
再直接呼叫該流程方法。這樣比對準像素座標穩定太多，而且一樣會走完 callback / 動畫 / 鎖。

### 驗「演出期間有沒有鎖住」要用取樣

一次性的前後比對看不出中間狀態。在 `await` 流程 promise 的同時開一個取樣迴圈：

```js
const p = comp.SomeFlow();               // 不 await
const samples = [];
for (let i = 0; i < 6; i++) {
  await new Promise(r => setTimeout(r, 400));
  samples.push({ t: i * 400, locked: comp.m_someLockFlag, /* 其他觀測點 */ });
}
await p;
```

同時記 `performance.now()` 的總時長，跟各段動畫的預期秒數對表——順序對不對用時長就能佐證。

## 確認跑的是不是最新建置

不要猜。直接讀活體函式原始碼找你剛加的字串：

```js
SlotReel.SomeMethod.toString().includes('你剛寫的註解或訊息')
```

MCP 的 `preview_reload` / `preview_start` 在 3.6.2 實測都回 `ok: false`，**驅動不了**；
`asset_reimport` 只重整 asset-db meta，不強制重編。編輯器的檔案監看通常自己會編，
所以「以為是舊建置」多半是誤判——用上面那行確認，不要靠感覺。

## 相關

- 轉輪空白、但網址參數也帶了、也走完三道關卡 → 很可能是 prefab 的跨 prefab 參考被弄斷，見 `uk-slot-prefab-target-overrides`
