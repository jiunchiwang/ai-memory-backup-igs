---
name: SS GitHub 管理工具 GUI 化
description: 專案決定用 Streamlit 建立 GUI 工具，批量管理 GitHub 組織倉庫（建倉、加團隊、查詢、多組織 Token 管理）
type: project
originSessionId: 413dcea4-7369-43c4-a35e-6a521b4b14bc
---
專案決定將現有 Python 腳本 GUI 化，技術選型 Streamlit。

**Why:** 現有工具是純腳本 + Excel 驅動，操作不直覺且 Token 硬編碼在程式碼中有安全風險。

**How to apply:** 已確認的功能規格（2026-04-15）：
1. 設定管理：多組織/多 Token，安全儲存，團隊預設
2. 倉庫查詢：列出組織倉庫，顯示全部資訊（名稱/描述/屬性/團隊權限），篩選搜尋
3. 批量建倉 + 設屬性：Excel/CSV/手動輸入，預覽確認後執行
4. 批量加團隊/協作者：同上資料來源，預覽確認後執行
5. 操作日誌：記錄時間、類型、影響倉庫、結果，可查閱歷史

不含 Git 操作（remote/submodule）功能。
