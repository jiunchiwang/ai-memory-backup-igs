---
name: ms-telegram-ask-button-protocol
description: Use when emitting <<ASK:...>> for Telegram bridge buttons, or when an ASK token renders verbatim. Label soft cap 20 chars; >20 SHALL use numbered body list with short labels. See SKILL.md for limits.
---

# Telegram Bridge `<<ASK>>` Button Protocol

## Overview

The bridge strips `<<ASK:...>>` from the reply and renders an **inline keyboard** attached to the final message. Tapping a button posts `[ASK:<question_id>] <key>` back as a new user turn.

**Iron rule:** If any validation fails, the bridge leaves the **whole token verbatim** in the user's chat — broken tokens are visible, not silently dropped. Self-check every token before sending.

## Token Shape

```
<<ASK:question_id|key1=label1|*key2=label2|...|keyN=labelN>>
```

- **Single line.** A `\n` anywhere inside the `<<...>>` aborts the match — the opener is shown to the user as plain text.
- **`question_id`** — `[a-zA-Z0-9_-]`, length 1–32. Echoed back in `[ASK:question_id] key`.
- **`key`** — `[a-zA-Z0-9_-]`, length 1–20. This is what the agent receives; pick short machine-friendly keys.
- **`label`** — shown on the button. Max **40 characters** (emoji counts). Must not contain `|` or `=`.
- **`*` prefix** on at most one option marks it as recommended:
  - That option's label gets a `⭐ ` prefix on the button.
  - An extra full-width `👉 照你的建議` button is added on its own row using the same callback as the starred key.
  - If you mark two, only the first `*` is honored; later ones become regular options silently.
- **Options:** minimum 1, maximum 8. (1 works but is pointless — use only for a single confirm-style nudge.)

## When To Use

- User has an obvious small set of next moves (2–5 options), and tapping is faster than typing.
- The next step branches on a choice you can pre-list (kind of run, yes/no, file to pick).
- Disambiguation after a tool call: "found 3 candidates, which one?"

## When NOT To Use

- The next step is free-form text. Just ask in prose.
- More than 8 meaningful choices. Paginate with follow-up ASKs or prose.
- The agent is just confirming completion. Don't ASK "ok?" after every turn.
- Inside a `/goal` continuation where the user is passive. ASK forces a tap.

## Long Option Descriptions

**量化規則：任何 label 超過 20 字時，SHALL 改用正文編號清單 + 短 label 的模式。**

Label 上限是 40 字，但 20 字就是可讀性臨界：
- CJK 在按鈕上視覺很重，20 字已經佔滿手機一行
- 讀者眼睛要停下來讀，比起純瀏覽「點哪個快」變慢
- 40 字的 hard limit 留給意外情境（例如不得不含路徑），不是常規使用

判斷 checklist（任一符合 → 必須改編號清單）：
- 任何 label 的字數 > 20（CJK 每字算 1）
- label 需要解釋**後果**（「會清掉 custom 設定」這類副作用說明）
- label 含路徑、檔名、或專有名詞超過一個
- 你自己讀 token 都覺得擠

**模式**：把完整描述放正文 1./2./3. 編號清單，label 做成「編號 + 短標題」。

Body:
```
1. 直接覆蓋現有檔案（會清掉原本的 custom 設定）
2. 另存為新檔，保留原檔 .bak
3. 先 diff 再決定
```

Token (same message, separate line):
```
<<ASK:overwrite_choice|overwrite=1 覆蓋|backup=2 另存新檔|diff=3 先 diff>>
```

The agent reads back `[ASK:overwrite_choice] backup` and knows exactly which numbered item the user chose.

## Recommended Option

Use `*` when you have a genuine opinion, not by default. Two reasons:
- The ⭐ + `👉 照你的建議` row adds a **second button with the same callback_data**, so one tap on either resolves the same way.
- If every ASK has a recommendation, users learn to tap it blindly and the signal becomes noise.

Skip `*` entirely when the options are symmetric (e.g. `yes/no` for a destructive op — don't steer).

## Callback Round-Trip

```
User taps button → bridge sends user turn: `[ASK:overwrite_choice] backup`
```

To react cleanly in your next reply, match on the `[ASK:<id>] <key>` pattern at the start of the incoming user message. The label is **not** sent — only the key. Pick keys that are self-descriptive (`backup` not `opt2`).

## Validation Self-Check (Before Emitting)

Run this checklist mentally on every `<<ASK:...>>` you're about to write:

| Check | Fail symptom |
|---|---|
| Single line, no `\n` inside `<<...>>` | Token shown verbatim (regex aborts) |
| Every label ≤ 40 chars (count CJK as 1 char each, but emoji count visually) | Whole token rejected |
| Every key unique, `[a-zA-Z0-9_-]{1,20}` | Whole token rejected |
| `question_id` matches `[a-zA-Z0-9_-]{1,32}` | Whole token rejected |
| No `\|` or `=` inside any label | Parser splits wrong, token rejected |
| 1 ≤ options ≤ 8 | Whole token rejected |
| At most one `*` prefix | Later `*` silently downgraded |
| Token NOT inside `` ` `` or ``` ``` ``` fenced block | Masked, no keyboard rendered |

"Rejected" means: the bridge logs `[ASK] malformed token rejected: <reason>` **and leaves the raw `<<ASK:...>>` visible to the user**. That's the protection against silent misrender.

## Common Mistakes

**Putting the full explanation in the label.**
Wrong: `<<ASK:x|a=直接覆蓋現有檔案會清掉原本的 custom 設定|b=另存新檔>>` → label 1 is 19 chars of CJK = easily over 40 in byte-heavy fonts and often over limit. Use body list + short labels.

**Breaking the token across lines for readability.**
Wrong:
```
<<ASK:overwrite_choice
 |overwrite=覆蓋
 |backup=另存>>
```
Regex requires single line. Keep it on one line no matter how long; the message body above it carries the readable version.

**Using `|` or `=` inside a label.**
Wrong: `<<ASK:m|both=A | B|neither=none>>` → the `|` in `A | B` gets parsed as a separator. Replace with `/`, `、`, or `＋`.

**Marking everything recommended.**
Wrong: `<<ASK:q|*a=A|*b=B|*c=C>>` → only the first `*` is kept. Use at most one, and only when you really recommend one option.

**Pasting an ASK example inside a code fence while also trying to render real buttons.**
Wrong:
````
Here's how ASK works:
```
<<ASK:demo|yes=Yes|no=No>>
```
````
The bridge masks everything inside code regions, so that token is documentation and won't render. If you want real buttons, put the live `<<ASK:...>>` outside any `` ` `` or ``` ``` ``` block. (This masking is intentional — it lets the agent explain the protocol without accidentally spawning buttons.)

**Asking a free-form question with ASK.**
Wrong: ASK for "which filename should I use?" with 3 guesses. The user's real answer is probably none of them. Ask in prose.

## Red Flags — Stop and Re-check

- 任何 label **超過 20 字** → **必改編號清單**（見 §Long Option Descriptions）
- You wrote `\n` inside `<<ASK:...>>` for readability → **single-line it, move prose to body**
- You want 9+ options → **redesign as body prose or two-step ASK**
- A label started with a verb longer than "覆蓋既有檔案並重啟 bridge" → **shorten, or add a numbered body**
- You're about to mark 3 of 4 options as recommended → **pick one or none**
- You're wrapping the ASK inside a ``` fence because it "looks cleaner" → **unfence it or accept that it's docs, not live**

## Quick Reference

| Limit | Value |
|---|---|
| `question_id` pattern | `[a-zA-Z0-9_-]{1,32}` |
| `key` pattern | `[a-zA-Z0-9_-]{1,20}` |
| `label` max length (hard limit) | 40 chars |
| `label` soft threshold | **20 chars** — 超過 SHALL 改編號清單模式（見 §Long Option Descriptions） |
| Options per token | 1–8 |
| `*` recommended markers | ≤ 1 effective |
| Token placement | Single line, outside code fences |
| Callback format | `[ASK:<question_id>] <key>` |

## Real-World Impact

The ones that have actually bitten in this bridge:
- Long CJK labels getting rejected and the raw `<<ASK:...>>` appearing in chat.
- Multi-line tokens failing silently (opener visible, no buttons).
- Code-fenced examples the agent wrote to *explain* ASK getting masked as expected — operators confused why "the same token" doesn't render (answer: masking is intentional; unfence the live one).
