/**
 * @ch FakeReelManager 參考實作（BetMode + Server fileIndex + 全部可選功能）
 *
 * 此檔案為包含所有功能的完整參考，以 uk_slot_eye_strike 實作為基礎。
 * 實際使用時需根據專案需求調整：
 * - 【適配點】標記處：必須替換為專案實際值
 * - 分類維度：以 BetMode（投注模式）或 GameType（遊戲類型）擇一，依專案需求決定
 * - fileIndex 來源：由 Server 提供（IRoundInfo.FakeReelWeightResult）或本地權重表選擇（見 architecture.md）
 * - 事件名稱與數量：可完全自訂
 * - 可選功能（SymbolInfo、Coin 金額）：不需要時移除對應程式碼
 */
import { _decorator, Component, error, TextAsset, warn, Enum, input, Input, EventKeyboard, log, KeyCode } from 'cc';
// 【適配點】根據專案實際引入，SymbolInfo 和列舉定義依專案 Game_Define.ts 為準
import Game_Define, { SymbolInfo, FeverGameType } from './Game_Define';
// 【適配點】astarte-framework 匯入依專案配置
import { eventManager, newBottombarManager } from 'db://astarte-framework/Managers';
import { DEBUG } from 'cc/env';
// 【適配點】tools 工具函式依專案引入
import { tools } from 'db://astarte-framework/utilis';
const { ccclass, property } = _decorator;

/**@ch 假轉輪帶讀取模式 */
enum FakeReelReadMode {
    /**@ch 以列讀取（橫向，檔案每一行 = 一條假轉輪帶）*/
    Row = 0,

    /**@ch 以行讀取（縱向，檔案每一列 = 一條假轉輪帶）*/
    Column = 1
}

// 【適配點】分類維度可選 BetMode（投注模式）或 GameType（遊戲類型），依專案需求決定
// 以下為 BetMode 方案範例；GameType 方案參見 architecture.md「兩種分類方案」
/**@ch 假轉輪帶投注模式 */
export enum FakeReelBetMode {
    /**@ch 一般投注 */
    Normal   = 0,
    /**@ch 道具卡 */
    ToolCard = 1,
    /**@ch 購買 Bonus */
    BuyBonus = 2,
    /**@ch 加注 Extra Bet */
    ExtraBet = 3,
}

// 【適配點】事件名稱與數量可完全自訂，以下為 BetMode + Server fileIndex 模式的完整範例
/**@ch 假轉輪管理器事件 */
export const FAKE_REEL_MANAGER_EVENT = {
    /**
     * @ch 載入假轉輪帶資料
     */
    LOAD_FAKE_REEL_DATA: "FAKE_REEL_LOAD_DATA",

    /**
     * @ch 生成假轉輪帶 Seed
     * @param betMode 投注模式（FakeReelBetMode，預設 Normal）
     * @param fakeReelWeightResult Server 回傳的假轉輪帶檔案索引（IRoundInfo.FakeReelWeightResult）
     * @param callback 回呼函式 (result: FakeReelSeed | null) => void
     */
    GENERATE_FAKE_REEL_SEED: "FAKE_REEL_GENERATE_SEED",

    /**
     * @ch 根據 Seed 取得假轉輪帶資料
     * @param seed FakeReelSeed
     * @param reelIndex Reel 編號
     * @param count 要取得的符號數量
     * @param autoUpdatePosition 是否自動更新位置（預設 false）
     * @param isDownward 是否往下取值（預設 true，true=位置+1，false=位置-1）
     * @param callback 回呼函式 (result: number[] | null) => void
     */
    GET_FAKE_REEL_DATA_BY_SEED: "FAKE_REEL_GET_DATA_BY_SEED",

    /**
     * @ch 為 Coin Symbol 生成金額
     * @param betMode 投注模式（FakeReelBetMode，預設 Normal）
     * @param callback 回呼函式 (result: { credit: number, symbolId: number } | null) => void
     */
    GENERATE_COIN_CREDIT: "FAKE_REEL_GENERATE_COIN_CREDIT",

    /**
     * @ch 根據 Seed 取得假轉輪帶符號資料
     * @param seed FakeReelSeed
     * @param reelIndex Reel 編號
     * @param count 要取得的符號數量
     * @param autoUpdatePosition 是否自動更新位置（預設 false）
     * @param isDownward 是否往下取值（預設 true，true=位置+1，false=位置-1）
     * @param callback 回呼函式 (result: SymbolInfo[] | null) => void
     */
    GET_FAKE_REEL_SYMBOL_BY_SEED: "FAKE_REEL_GET_SYMBOL_BY_SEED",

    /**
     * @ch 處理 Seed 位置 (正數=加，負數=減)
     * @param seed FakeReelSeed
     * @param reelIndex Reel 編號
     * @param count 要加減的符號數量 (正數=加，負數=減)
     * @param callback 回呼函式 (result: FakeReelSeed | null) => void
     */
    PROCESS_SEED_POSITION: "FAKE_REEL_PROCESS_SEED_POSITION",
};

export class FakeReelData {
    /**@ch 假轉輪帶資料 [假轉輪帶編號] = 符號陣列 */
    public ReelData: { [index: number]: number[] } = {};
}

/**@ch Coin 金額權重表項目 */
export class CoinCreditWeightEntry {
    // 【適配點】'JP' 標記可改為其他特殊 Symbol 標記
    /**@ch 金額（數字，以幣為單位，例如 5000 = 50.00 元）或 'JP' 標記 */
    public credit: number | 'JP' = 0;

    /**@ch 權重值 */
    public weight: number = 0;
}

/**@ch Coin 金額權重表 */
export class CoinCreditWeightTable {
    /**@ch 權重表項目列表 */
    public entries: CoinCreditWeightEntry[] = [];

    /**@ch 總權重 */
    public totalWeight: number = 0;
}

/**@ch 假轉輪帶 Seed 資訊 */
export class FakeReelSeed {
    // BetMode 方案：Seed 儲存投注模式
    // GameType 方案：將 betMode 改為 gameType: number = 0
    /**@ch 投注模式（FakeReelBetMode）*/
    public betMode: number = FakeReelBetMode.Normal;

    /**@ch 選中的檔案索引（由 Server 的 FakeReelWeightResult 直接指定）*/
    public fileIndex: number = 0;

    /**@ch 每條假轉輪帶的起始位置 [Reel編號] = 起始索引 */
    public startPositions: { [reelIndex: number]: number } = {};
}

@ccclass('FakeReelManager')
export class FakeReelManager extends Component {
    //#region Constants
    private static readonly EVENTS_TO_REGISTER = [
        FAKE_REEL_MANAGER_EVENT.LOAD_FAKE_REEL_DATA,
        FAKE_REEL_MANAGER_EVENT.GENERATE_FAKE_REEL_SEED,
        FAKE_REEL_MANAGER_EVENT.GET_FAKE_REEL_DATA_BY_SEED,
        FAKE_REEL_MANAGER_EVENT.GENERATE_COIN_CREDIT,
        FAKE_REEL_MANAGER_EVENT.GET_FAKE_REEL_SYMBOL_BY_SEED,
        FAKE_REEL_MANAGER_EVENT.PROCESS_SEED_POSITION,
    ];
    //#endregion Constants

    // 【適配點】屬性依分類維度（BetMode/GameType）和所需功能調整
    // 使用 @property group 可在 Inspector 中分組顯示

    //#region Properties — 一般（Normal）
    @property({
        type: [TextAsset],
        group: { name: '一般 (Normal)' },
        tooltip: "假轉輪帶資料檔案"
    })
    private m_fakeReelAssets: TextAsset[] = [];

    @property({
        type: Enum(FakeReelReadMode),
        group: { name: '一般 (Normal)' },
        tooltip: "假轉輪帶讀取模式"
    })
    private m_fakeReelReadMode: FakeReelReadMode = FakeReelReadMode.Row;

    @property({
        type: TextAsset,
        group: { name: '一般 (Normal)' },
        tooltip: "Coin Symbol 金額權重表"
    })
    private m_coinCreditWeightAsset: TextAsset = null;
    //#endregion Properties — 一般

    //#region Properties — 道具卡（ToolCard）
    @property({
        type: [TextAsset],
        group: { name: '道具卡 (ToolCard)' },
        tooltip: "[道具卡] 假轉輪帶資料檔案"
    })
    private m_fakeReelAssets_ToolCard: TextAsset[] = [];

    @property({
        type: Enum(FakeReelReadMode),
        group: { name: '道具卡 (ToolCard)' },
        tooltip: "[道具卡] 假轉輪帶讀取模式"
    })
    private m_fakeReelReadMode_ToolCard: FakeReelReadMode = FakeReelReadMode.Row;

    @property({
        type: TextAsset,
        group: { name: '道具卡 (ToolCard)' },
        tooltip: "[道具卡] Coin Symbol 金額權重表"
    })
    private m_coinCreditWeightAsset_ToolCard: TextAsset = null;
    //#endregion Properties — 道具卡

    //#region Properties — BuyBonus
    @property({
        type: [TextAsset],
        group: { name: 'BuyBonus' },
        tooltip: "[BuyBonus] 假轉輪帶資料檔案"
    })
    private m_fakeReelAssets_BuyBonus: TextAsset[] = [];

    @property({
        type: Enum(FakeReelReadMode),
        group: { name: 'BuyBonus' },
        tooltip: "[BuyBonus] 假轉輪帶讀取模式"
    })
    private m_fakeReelReadMode_BuyBonus: FakeReelReadMode = FakeReelReadMode.Row;

    @property({
        type: TextAsset,
        group: { name: 'BuyBonus' },
        tooltip: "[BuyBonus] Coin Symbol 金額權重表"
    })
    private m_coinCreditWeightAsset_BuyBonus: TextAsset = null;
    //#endregion Properties — BuyBonus

    //#region Properties — ExtraBet
    @property({
        type: [TextAsset],
        group: { name: 'ExtraBet' },
        tooltip: "[ExtraBet] 假轉輪帶資料檔案"
    })
    private m_fakeReelAssets_ExtraBet: TextAsset[] = [];

    @property({
        type: Enum(FakeReelReadMode),
        group: { name: 'ExtraBet' },
        tooltip: "[ExtraBet] 假轉輪帶讀取模式"
    })
    private m_fakeReelReadMode_ExtraBet: FakeReelReadMode = FakeReelReadMode.Row;

    @property({
        type: TextAsset,
        group: { name: 'ExtraBet' },
        tooltip: "[ExtraBet] Coin Symbol 金額權重表"
    })
    private m_coinCreditWeightAsset_ExtraBet: TextAsset = null;
    //#endregion Properties — ExtraBet

    //#region Internal Caches
    /**@ch Coin 金額權重表快取 [betMode] */
    private m_coinCreditWeightTables: { [betMode: number]: CoinCreditWeightTable } = {
        [FakeReelBetMode.Normal]:   null,
        [FakeReelBetMode.ToolCard]: null,
        [FakeReelBetMode.BuyBonus]: null,
        [FakeReelBetMode.ExtraBet]: null,
    };
    //#endregion Internal Caches

    //#region Variables
    // 【適配點】分類維度用 betMode；GameType 方案改為 { [gameType: number]: FakeReelData[] }
    /**@ch 假轉輪帶資料 [betMode][fileIndex] */
    private m_fakeReelData: { [betMode: number]: FakeReelData[] } = {
        [FakeReelBetMode.Normal]:   [],
        [FakeReelBetMode.ToolCard]: [],
        [FakeReelBetMode.BuyBonus]: [],
        [FakeReelBetMode.ExtraBet]: [],
    };

    /**@ch 假轉輪帶是否已載入 [betMode][fileIndex] */
    private m_isFakeReelLoaded: { [betMode: number]: boolean[] } = {
        [FakeReelBetMode.Normal]:   [],
        [FakeReelBetMode.ToolCard]: [],
        [FakeReelBetMode.BuyBonus]: [],
        [FakeReelBetMode.ExtraBet]: [],
    };

    /**@ch 是否已經初始化 */
    private m_isInitialized: boolean = false;
    //#endregion Variables

    //#region Lifecycle
    onLoad() {
        this.ParseCoinCreditWeightTables();
        this.OnLoadFakeReelData();
        this.RegisterEvent();
    }

    onDestroy() {
        if (!this.m_isInitialized) return;
        this.UnregisterEvent();
        this.m_isInitialized = false;
    }
    //#endregion Lifecycle

    //#region Event Management
    private RegisterEvent() {
        FakeReelManager.EVENTS_TO_REGISTER.forEach(eventName => {
            eventManager.Register(eventName, this);
        });
        this.m_isInitialized = true;
    }

    private UnregisterEvent() {
        FakeReelManager.EVENTS_TO_REGISTER.forEach(eventName => {
            eventManager.UnRegister(eventName, this);
        });
    }

    private ValidateEventName(event: string): boolean {
        if (!event || typeof event !== 'string') {
            warn('[FakeReelManager] OnEvent: 無效的事件名稱', event);
            return false;
        }
        return true;
    }

    OnEvent(event: string, ...args: any[]) {
        if (!this.ValidateEventName(event)) {
            return;
        }

        switch (event) {
            case FAKE_REEL_MANAGER_EVENT.LOAD_FAKE_REEL_DATA:
                this.OnLoadFakeReelData();
                break;

            case FAKE_REEL_MANAGER_EVENT.GENERATE_FAKE_REEL_SEED:
                return this.OnGenerateFakeReelSeed(args);

            case FAKE_REEL_MANAGER_EVENT.GET_FAKE_REEL_DATA_BY_SEED:
                return this.OnGetFakeReelDataBySeed(args);

            case FAKE_REEL_MANAGER_EVENT.GENERATE_COIN_CREDIT:
                return this.OnGenerateCoinCredit(args);

            case FAKE_REEL_MANAGER_EVENT.GET_FAKE_REEL_SYMBOL_BY_SEED:
                return this.OnGetFakeReelSymbolBySeed(args);

            case FAKE_REEL_MANAGER_EVENT.PROCESS_SEED_POSITION:
                return this.OnProcessSeedPosition(args);

            default:
                warn('[FakeReelManager] OnEvent: 未知的事件', event);
        }
    }
    //#endregion Event Management

    //#region Event Handlers
    private OnLoadFakeReelData() {
        const allBetModes = [FakeReelBetMode.Normal, FakeReelBetMode.ToolCard, FakeReelBetMode.BuyBonus, FakeReelBetMode.ExtraBet];

        for (const betMode of allBetModes) {
            const assets = this.GetFakeReelAssets(betMode);
            if (!assets || assets.length === 0) continue;

            assets.forEach((_, index) => {
                this.LoadFakeReelData(betMode, index);
            });
        }
    }

    /**
     * @ch 處理 GENERATE_FAKE_REEL_SEED 事件
     * @param args [betMode: number, fakeReelWeightResult: number, callback?: Function]
     */
    private OnGenerateFakeReelSeed(args: any[]): void {
        const betMode = args.length > 0 && typeof args[0] === 'number' ? args[0] : FakeReelBetMode.Normal;
        // 【適配點】fileIndex 由 Server 的 FakeReelWeightResult 直接提供；
        // GameType+本地權重表方案則改為 modelIndex，用 SelectFileByModel() 選 fileIndex
        const fakeReelWeightResult = args.length > 1 && typeof args[1] === 'number' ? args[1] : 0;
        const callback = args.length > 2 && typeof args[2] === 'function' ? args[2] : null;

        const result = this.GenerateFakeReelSeed(betMode, fakeReelWeightResult);
        if (callback) callback(result);
    }

    /**
     * @ch 處理 GET_FAKE_REEL_DATA_BY_SEED 事件
     * @param args [seed, reelIndex, count, autoUpdatePosition?, isDownward?, callback?]
     */
    private OnGetFakeReelDataBySeed(args: any[]): void {
        if (args.length < 1 || !(args[0] instanceof FakeReelSeed)) {
            warn('[FakeReelManager] OnGetFakeReelDataBySeed: 無效的 Seed 參數', args[0]);
            return;
        }
        const seed = args[0] as FakeReelSeed;

        if (args.length < 2 || typeof args[1] !== 'number') {
            warn('[FakeReelManager] OnGetFakeReelDataBySeed: 無效的 reelIndex 參數', args[1]);
            return;
        }
        const reelIndex = args[1];

        if (args.length < 3 || typeof args[2] !== 'number') {
            warn('[FakeReelManager] OnGetFakeReelDataBySeed: 無效的 count 參數', args[2]);
            return;
        }
        const count = args[2];

        const autoUpdatePosition = args.length > 3 && typeof args[3] === 'boolean' ? args[3] : false;
        const isDownward = args.length > 4 && typeof args[4] === 'boolean' ? args[4] : true;
        const callback = args.length > 5 && typeof args[5] === 'function' ? args[5] : null;

        const result = this.GetFakeReelDataBySeed(seed, reelIndex, count, autoUpdatePosition, isDownward);
        if (callback) callback(result);
    }

    /**
     * @ch 處理 GENERATE_COIN_CREDIT 事件
     * @param args [betMode?: number, callback?]
     */
    private OnGenerateCoinCredit(args: any[]): void {
        let betMode = FakeReelBetMode.Normal;
        let callback: ((result: any) => void) | null = null;

        if (args.length > 0) {
            if (typeof args[0] === 'function') {
                callback = args[0];
            } else if (typeof args[0] === 'number') {
                betMode = args[0];
                callback = args.length > 1 && typeof args[1] === 'function' ? args[1] : null;
            }
        }

        const maxAttempts = 100;
        let result = this.GenerateCoinCredit(betMode);
        // 【適配點】Coin Symbol ID 依專案定義調整（此處為 14）
        for (let i = 1; i < maxAttempts && result.symbolId !== 14; i++) {
            result = this.GenerateCoinCredit(betMode);
        }

        if (result.symbolId !== 14 || result.credit <= 0) {
            warn(`[FakeReelManager] OnGenerateCoinCredit: ${maxAttempts} 次仍未取得有效金額`);
        } else {
            // 【適配點】bet 計算方式依專案的 BottomBar/下注管理器調整
            const bet = newBottombarManager.GetNowBetValue();
            result.credit = tools.divide(result.credit * bet, 100);
        }

        if (callback) callback(result);
    }

    /**
     * @ch 處理 GET_FAKE_REEL_SYMBOL_BY_SEED 事件
     * @param args [seed, reelIndex, count, autoUpdatePosition?, isDownward?, callback?]
     */
    private OnGetFakeReelSymbolBySeed(args: any[]): void {
        if (args.length < 1 || !(args[0] instanceof FakeReelSeed)) {
            warn('[FakeReelManager] OnGetFakeReelSymbolBySeed: 無效的 Seed 參數', args[0]);
            return;
        }
        const seed = args[0] as FakeReelSeed;

        if (args.length < 2 || typeof args[1] !== 'number') {
            warn('[FakeReelManager] OnGetFakeReelSymbolBySeed: 無效的 reelIndex 參數', args[1]);
            return;
        }
        const reelIndex = args[1];

        if (args.length < 3 || typeof args[2] !== 'number') {
            warn('[FakeReelManager] OnGetFakeReelSymbolBySeed: 無效的 count 參數', args[2]);
            return;
        }
        const count = args[2];

        const autoUpdatePosition = args.length > 3 && typeof args[3] === 'boolean' ? args[3] : false;
        const isDownward = args.length > 4 && typeof args[4] === 'boolean' ? args[4] : true;
        const callback = args.length > 5 && typeof args[5] === 'function' ? args[5] : null;

        const result = this.GetFakeReelSymbolBySeed(seed, reelIndex, count, autoUpdatePosition, isDownward);
        if (callback) callback(result);
    }

    /**
     * @ch 處理 PROCESS_SEED_POSITION 事件
     * @param args [seed, reelIndex, count, callback?]
     */
    private OnProcessSeedPosition(args: any[]): void {
        if (args.length < 1 || !(args[0] instanceof FakeReelSeed)) {
            warn('[FakeReelManager] OnProcessSeedPosition: 無效的 Seed 參數', args[0]);
            return;
        }
        const seed = args[0] as FakeReelSeed;

        if (args.length < 2 || typeof args[1] !== 'number') {
            warn('[FakeReelManager] OnProcessSeedPosition: 無效的 reelIndex 參數', args[1]);
            return;
        }
        const reelIndex = args[1];

        if (args.length < 3 || typeof args[2] !== 'number') {
            warn('[FakeReelManager] OnProcessSeedPosition: 無效的 count 參數', args[2]);
            return;
        }
        const count = args[2];

        const callback = args.length > 3 && typeof args[3] === 'function' ? args[3] : null;

        const result = this.ProcessSeedPosition(seed, reelIndex, count);
        if (callback) callback(result);
    }
    //#endregion Event Handlers

    //#region Private Helpers — BetMode 資源查詢
    // 【適配點】switch/case 依專案分類維度（BetMode 或 GameType）調整
    /**@ch 取得指定 BetMode 的假轉輪帶資產陣列 */
    private GetFakeReelAssets(betMode: number): TextAsset[] {
        switch (betMode) {
            case FakeReelBetMode.ToolCard: return this.m_fakeReelAssets_ToolCard;
            case FakeReelBetMode.BuyBonus: return this.m_fakeReelAssets_BuyBonus;
            case FakeReelBetMode.ExtraBet: return this.m_fakeReelAssets_ExtraBet;
            default:                       return this.m_fakeReelAssets;
        }
    }

    /**@ch 取得指定 BetMode 的讀取模式 */
    private GetReadMode(betMode: number): FakeReelReadMode {
        switch (betMode) {
            case FakeReelBetMode.ToolCard: return this.m_fakeReelReadMode_ToolCard;
            case FakeReelBetMode.BuyBonus: return this.m_fakeReelReadMode_BuyBonus;
            case FakeReelBetMode.ExtraBet: return this.m_fakeReelReadMode_ExtraBet;
            default:                       return this.m_fakeReelReadMode;
        }
    }

    /**@ch 取得指定 BetMode 的 Coin 金額權重表資產 */
    private GetCoinCreditAsset(betMode: number): TextAsset | null {
        switch (betMode) {
            case FakeReelBetMode.ToolCard: return this.m_coinCreditWeightAsset_ToolCard;
            case FakeReelBetMode.BuyBonus: return this.m_coinCreditWeightAsset_BuyBonus;
            case FakeReelBetMode.ExtraBet: return this.m_coinCreditWeightAsset_ExtraBet;
            default:                       return this.m_coinCreditWeightAsset;
        }
    }

    /**@ch 取得 BetMode 的顯示名稱（用於日誌）*/
    private GetBetModeName(betMode: number): string {
        const names = {
            [FakeReelBetMode.Normal]:   '一般',
            [FakeReelBetMode.ToolCard]: '道具卡',
            [FakeReelBetMode.BuyBonus]: 'BuyBonus',
            [FakeReelBetMode.ExtraBet]: 'ExtraBet',
        };
        return names[betMode] ?? String(betMode);
    }

    /**@ch 指定 BetMode 是否有設定假轉輪帶檔案 */
    private HasFilesForBetMode(betMode: number): boolean {
        const assets = this.GetFakeReelAssets(betMode);
        return assets != null && assets.length > 0;
    }
    //#endregion Private Helpers

    //#region Private Methods
    private ParseCoinCreditWeightTables(): void {
        const allBetModes = [FakeReelBetMode.Normal, FakeReelBetMode.ToolCard, FakeReelBetMode.BuyBonus, FakeReelBetMode.ExtraBet];

        for (const betMode of allBetModes) {
            const asset = this.GetCoinCreditAsset(betMode);
            if (asset) {
                this.m_coinCreditWeightTables[betMode] = this.ParseCoinCreditWeightTable(asset.text, this.GetBetModeName(betMode));
            }
        }
    }

    /**
     * @ch 解析 Coin 金額權重表檔案
     * 格式: "5000\t300" (金額（幣）\t權重) 或 "JP\t120"
     * 注意: 檔案中的金額已經是放大 100 倍後的值（例如 5000 = 50.00 元）
     */
    private ParseCoinCreditWeightTable(fileContent: string, betModeName: string): CoinCreditWeightTable
    {
        const table = new CoinCreditWeightTable();

        if (!fileContent || fileContent.trim() === '') {
            warn(`[FakeReelManager] ParseCoinCreditWeightTable: ${betModeName} 檔案內容為空`);
            return table;
        }

        try {
            const lines = fileContent.split('\n').map(s => s.trim()).filter(s => s !== '');

            for (const line of lines) {
                const parts = line.split('\t').map(s => s.trim()).filter(s => s !== '');

                if (parts.length < 2) continue;

                const creditStr = parts[0];
                const weight = parseInt(parts[1], 10);

                if (isNaN(weight) || weight < 0) {
                    warn(`[FakeReelManager] ParseCoinCreditWeightTable: ${betModeName} 權重值無效 (${line})`);
                    continue;
                }

                const entry = new CoinCreditWeightEntry();
                entry.weight = weight;

                if (creditStr.toUpperCase() === 'JP') {
                    entry.credit = 'JP';
                } else {
                    const creditValue = parseInt(creditStr, 10);
                    if (isNaN(creditValue)) {
                        warn(`[FakeReelManager] ParseCoinCreditWeightTable: ${betModeName} 金額值無效 (${line})`);
                        continue;
                    }
                    entry.credit = creditValue;
                }

                table.entries.push(entry);
                table.totalWeight += weight;
            }
        } catch (err) {
            error(`[FakeReelManager] ParseCoinCreditWeightTable: ${betModeName} 解析失敗: ${err}`);
        }

        return table;
    }

    /**
     * @ch 載入並解析假轉輪帶資料
     * @param betMode 投注模式
     * @param index 假轉輪帶檔案索引
     */
    private LoadFakeReelData(betMode: number, index: number): boolean
    {
        if (this.m_isFakeReelLoaded[betMode]?.[index]) {
            return true;
        }

        const assets = this.GetFakeReelAssets(betMode);
        const asset = assets?.[index] ?? null;
        const readMode = this.GetReadMode(betMode);

        if (!asset) {
            warn(`[FakeReelManager] LoadFakeReelData: 找不到資源檔案 (${this.GetBetModeName(betMode)}, Index: ${index})`);
            return false;
        }

        try {
            this.ParseFakeReelData(betMode, index, asset.text, readMode);
            this.m_isFakeReelLoaded[betMode][index] = true;
            return true;
        } catch (err) {
            error(`[FakeReelManager] 解析假轉輪帶檔案失敗 (${this.GetBetModeName(betMode)}, Index: ${index}): ${err}`);
            return false;
        }
    }

    private ParseFakeReelData(betMode: number, index: number, fileContent: string, readMode: FakeReelReadMode): void
    {
        if (!fileContent || fileContent.trim() === '') {
            warn(`[FakeReelManager] ParseFakeReelData: 檔案內容為空 (${this.GetBetModeName(betMode)}, Index: ${index})`);
            return;
        }

        if (!this.m_fakeReelData[betMode][index]) {
            this.m_fakeReelData[betMode][index] = new FakeReelData();
        }

        const lines = fileContent.split('\n').filter(line => line.trim() !== '');

        if (lines.length === 0) {
            warn(`[FakeReelManager] ParseFakeReelData: 沒有有效的資料行 (${this.GetBetModeName(betMode)}, Index: ${index})`);
            return;
        }

        if (readMode === FakeReelReadMode.Row) {
            this.ParseRowMode(betMode, index, lines);
        } else {
            this.ParseColumnMode(betMode, index, lines);
        }
    }

    private ParseRowMode(betMode: number, index: number, lines: string[]): void
    {
        lines.forEach((line, reelIndex) => {
            const symbols = line.split('\t')
                .map(str => str.trim())
                .filter(str => str !== '')
                .map(str => parseInt(str, 10))
                .filter(num => !isNaN(num));

            if (symbols.length > 0) {
                this.m_fakeReelData[betMode][index].ReelData[reelIndex] = symbols;
            }
        });
    }

    private ParseColumnMode(betMode: number, index: number, lines: string[]): void
    {
        const matrix: (number | null)[][] = [];
        // 【適配點】應使用 Game_Define.COL 取代硬編碼數字（依專案實際欄數）
        const expectedColumns = 6;

        lines.forEach(line => {
            const parts = line.split('\t');
            const symbols: (number | null)[] = [];
            for (let i = 0; i < expectedColumns; i++) {
                if (i < parts.length) {
                    const trimmed = parts[i].trim();
                    if (trimmed === '') {
                        symbols.push(null);
                    } else {
                        const num = parseInt(trimmed, 10);
                        symbols.push(isNaN(num) ? null : num);
                    }
                } else {
                    symbols.push(null);
                }
            }

            if (symbols.some(s => s !== null)) {
                matrix.push(symbols);
            }
        });

        if (matrix.length === 0) {
            warn(`[FakeReelManager] ParseColumnMode: 無有效資料 (${this.GetBetModeName(betMode)}, Index: ${index})`);
            return;
        }

        for (let col = 0; col < expectedColumns; col++) {
            const columnData: number[] = [];

            for (let row = 0; row < matrix.length; row++) {
                const value = matrix[row][col];
                if (value !== null) {
                    columnData.push(value);
                }
            }

            if (columnData.length > 0) {
                this.m_fakeReelData[betMode][index].ReelData[col] = columnData;
            }
        }
    }

    /**
     * @ch 取得 Coin 金額權重表（優先用指定 betMode，若無則 fallback 到 Normal）
     * GameType 方案：無 fallback，直接回傳對應 gameType 的表
     */
    private GetCoinCreditWeightTable(betMode: number): CoinCreditWeightTable | null
    {
        const table = this.m_coinCreditWeightTables[betMode] ?? null;
        if (table && table.entries.length > 0) return table;

        // BetMode 方案特有：無對應表時 fallback 到 Normal
        if (betMode !== FakeReelBetMode.Normal) {
            return this.m_coinCreditWeightTables[FakeReelBetMode.Normal] ?? null;
        }

        return null;
    }

    /**
     * @ch 根據權重隨機生成 Coin Symbol 的金額
     */
    private GenerateCoinCredit(betMode: number): { credit: number, symbolId: number }
    {
        const table = this.GetCoinCreditWeightTable(betMode);
        // 【適配點】Coin Symbol ID（14）和 JP Symbol ID（20）依專案定義
        const defaultResult = { credit: 0, symbolId: 14 };

        if (!table || !table.entries || table.entries.length === 0) {
            warn(`[FakeReelManager] GenerateCoinCredit: 權重表不存在或為空 (${this.GetBetModeName(betMode)})`);
            return defaultResult;
        }

        if (table.totalWeight <= 0) {
            warn(`[FakeReelManager] GenerateCoinCredit: 總權重為 0 (${this.GetBetModeName(betMode)})`);
            return defaultResult;
        }

        const randomValue = Math.random() * table.totalWeight;
        let cumulativeWeight = 0;

        for (const entry of table.entries) {
            cumulativeWeight += entry.weight;

            if (randomValue <= cumulativeWeight) {
                if (entry.credit === 'JP') {
                    return { credit: 0, symbolId: 20 };
                } else {
                    return { credit: entry.credit as number, symbolId: 14 };
                }
            }
        }

        const lastEntry = table.entries[table.entries.length - 1];
        if (lastEntry.credit === 'JP') {
            return { credit: 0, symbolId: 20 };
        } else {
            return { credit: lastEntry.credit as number, symbolId: 14 };
        }
    }

    /**@ch 將符號ID陣列轉換為SymbolInfo陣列 */
    private ConvertSymbolsToSymbolInfos(symbols: number[], betMode: number): SymbolInfo[]
    {
        return symbols.map(symbolId => {
            let symbolInfo = new SymbolInfo();
            symbolInfo.JpType = 0;

            // 【適配點】Coin Symbol ID（14）依專案定義
            if (symbolId === 14) {
                const coinResult = this.GenerateCoinCredit(betMode);
                symbolInfo.Symbol = coinResult.symbolId;
                symbolInfo.Value = coinResult.credit;
            } else {
                symbolInfo.Symbol = symbolId;
                symbolInfo.Value = 0;
            }

            return symbolInfo;
        });
    }
    //#endregion Private Methods

    //#region Public Methods
    /**
     * @ch 生成假轉輪帶 Seed
     * @param betMode 投注模式（若該模式無檔案設定，自動 fallback 到 Normal）
     * @param fakeReelWeightResult Server 回傳的假轉輪帶檔案索引（IRoundInfo.FakeReelWeightResult）
     * @returns Seed 資訊，若失敗返回 null
     */
    public GenerateFakeReelSeed(betMode: number = FakeReelBetMode.Normal, fakeReelWeightResult: number = 0): FakeReelSeed | null
    {
        // BetMode fallback：若該模式無檔案，自動使用 Normal
        const effectiveBetMode = this.HasFilesForBetMode(betMode) ? betMode : FakeReelBetMode.Normal;

        const seed = new FakeReelSeed();
        seed.betMode = effectiveBetMode;
        // 【適配點】fileIndex 直接使用 Server 提供的值；本地權重表方案改用 SelectFileByModel()
        seed.fileIndex = fakeReelWeightResult;

        if (!this.m_fakeReelData[effectiveBetMode]?.[seed.fileIndex]) {
            error(`[FakeReelManager] GenerateFakeReelSeed: 假轉輪帶資料未載入 (${this.GetBetModeName(effectiveBetMode)}, FileIndex: ${seed.fileIndex})`);
            return null;
        }

        const fakeReelData = this.m_fakeReelData[effectiveBetMode][seed.fileIndex];
        const reelCount = Object.keys(fakeReelData.ReelData).length;

        for (let reelIndex = 0; reelIndex < reelCount; reelIndex++) {
            const reelData = fakeReelData.ReelData[reelIndex];

            if (!reelData || reelData.length === 0) {
                warn(`[FakeReelManager] GenerateFakeReelSeed: Reel ${reelIndex} 資料不存在，使用預設位置 0`);
                seed.startPositions[reelIndex] = 0;
                continue;
            }

            seed.startPositions[reelIndex] = Math.floor(Math.random() * reelData.length);
        }

        log(`[FakeReelManager] GenerateFakeReelSeed: BetMode=${effectiveBetMode}, FileIndex=${seed.fileIndex}, StartPositions=${JSON.stringify(seed.startPositions)}`);

        return seed;
    }

    /**
     * @ch 根據 Seed 取得假轉輪帶資料（從指定位置開始循環取值）
     * betMode 從 seed.betMode 讀取。
     */
    public GetFakeReelDataBySeed(seed: FakeReelSeed, reelIndex: number, count: number, autoUpdatePosition: boolean = false, isDownward: boolean = true): number[] | null
    {
        if (!seed) {
            error(`[FakeReelManager] GetFakeReelDataBySeed: Seed 為 null`);
            return null;
        }

        if (count <= 0) {
            warn(`[FakeReelManager] GetFakeReelDataBySeed: count 必須大於 0`);
            return null;
        }

        const betMode = seed.betMode;

        if (!this.m_fakeReelData[betMode]?.[seed.fileIndex]) {
            error(`[FakeReelManager] GetFakeReelDataBySeed: 假轉輪帶資料未載入 (${this.GetBetModeName(betMode)}, FileIndex: ${seed.fileIndex})`);
            return null;
        }

        const fakeReelData = this.m_fakeReelData[betMode][seed.fileIndex].ReelData[reelIndex];
        if (!fakeReelData || fakeReelData.length === 0) {
            error(`[FakeReelManager] GetFakeReelDataBySeed: Reel 資料不存在 (ReelIndex: ${reelIndex})`);
            return null;
        }

        const startPosition = seed.startPositions[reelIndex] || 0;
        const result: number[] = [];

        for (let i = 0; i < count; i++) {
            let index: number;
            if (isDownward) {
                index = (startPosition + i) % fakeReelData.length;
            } else {
                index = (startPosition - i + fakeReelData.length * count) % fakeReelData.length;
            }
            result.push(fakeReelData[index]);
        }

        if (autoUpdatePosition) {
            if (isDownward) {
                seed.startPositions[reelIndex] = (startPosition + count) % fakeReelData.length;
            } else {
                seed.startPositions[reelIndex] = (startPosition - count + fakeReelData.length * count) % fakeReelData.length;
            }
        }

        return result;
    }

    /**
     * @ch 根據 Seed 取得假轉輪帶符號資料
     * betMode 從 seed.betMode 讀取。
     */
    public GetFakeReelSymbolBySeed(seed: FakeReelSeed, reelIndex: number, count: number, autoUpdatePosition: boolean = false, isDownward: boolean = true): SymbolInfo[] | null
    {
        const symbols = this.GetFakeReelDataBySeed(seed, reelIndex, count, autoUpdatePosition, isDownward);
        if (!symbols) return null;
        return this.ConvertSymbolsToSymbolInfos(symbols, seed.betMode);
    }

    /**
     * @ch 處理 Seed 位置加減
     * betMode 從 seed.betMode 讀取。
     */
    public ProcessSeedPosition(seed: FakeReelSeed, reelIndex: number, count: number): FakeReelSeed | null
    {
        if (!seed) {
            error(`[FakeReelManager] ProcessSeedPosition: Seed 為 null`);
            return null;
        }

        const betMode = seed.betMode;

        if (!this.m_fakeReelData[betMode]?.[seed.fileIndex]) {
            error(`[FakeReelManager] ProcessSeedPosition: 假轉輪帶資料未載入 (${this.GetBetModeName(betMode)}, FileIndex: ${seed.fileIndex})`);
            return null;
        }

        const fakeReelData = this.m_fakeReelData[betMode][seed.fileIndex].ReelData[reelIndex];
        if (!fakeReelData || fakeReelData.length === 0) {
            error(`[FakeReelManager] ProcessSeedPosition: Reel 資料不存在 (ReelIndex: ${reelIndex})`);
            return null;
        }

        const currentPosition = seed.startPositions[reelIndex] || 0;
        const newPosition = (currentPosition + count + fakeReelData.length * Math.abs(count) + fakeReelData.length) % fakeReelData.length;
        seed.startPositions[reelIndex] = newPosition;

        return seed;
    }
    //#endregion Public Methods

    //#region 測試功能
    private CheckTestKeyCode() {
        if (!DEBUG) return;

        input.on(Input.EventType.KEY_DOWN, (event: EventKeyboard) => {
            log("CheckTestKeyCode", event.keyCode);
            switch (event.keyCode) {
               case KeyCode.DIGIT_0:
                    this.TestOnGenerateCoinCredit(FakeReelBetMode.Normal);
                    break;

                case KeyCode.DIGIT_1:
                    this.TestOnGenerateCoinCredit(FakeReelBetMode.ToolCard);
                    break;
            }
        });
    }

    private TestSeedGeneration(betMode: number, fakeReelWeightResult: number) {
        log(`[FakeReelManager] ========== 測試 Seed 生成 (${this.GetBetModeName(betMode)}, FileIndex=${fakeReelWeightResult}) ==========`);

        const seed = this.GenerateFakeReelSeed(betMode, fakeReelWeightResult);
        if (!seed) {
            error(`[FakeReelManager] Seed 生成失敗`);
            return;
        }

        log(`[FakeReelManager] Seed: BetMode=${seed.betMode}, FileIndex=${seed.fileIndex}`);

        const fakeReelDataObj = this.m_fakeReelData[seed.betMode]?.[seed.fileIndex];
        if (!fakeReelDataObj) {
            error(`[FakeReelManager] 無法取得假轉輪帶資料`);
            return;
        }

        const reelCount = Object.keys(fakeReelDataObj.ReelData).length;
        const getCount = 10;

        for (let reelIndex = 0; reelIndex < reelCount; reelIndex++) {
            const symbols = this.GetFakeReelDataBySeed(seed, reelIndex, getCount);
            if (symbols) {
                log(`[FakeReelManager] Reel ${reelIndex}: StartPos=${seed.startPositions[reelIndex]}, Symbols=[${symbols.join(', ')}]`);
            }
        }

        log(`[FakeReelManager] ========== 測試完成 ==========`);
    }

    private TestOnGenerateCoinCredit(betMode: number, testCount: number = 20) {
        const bet = newBottombarManager.GetNowBetValue();

        log(`[FakeReelManager] ========== 測試 OnGenerateCoinCredit (${this.GetBetModeName(betMode)}) ==========`);

        const table = this.GetCoinCreditWeightTable(betMode);
        if (!table || !table.entries || table.entries.length === 0) {
            error(`[FakeReelManager] ${this.GetBetModeName(betMode)} Coin金額權重表不存在或為空`);
            return;
        }

        const validRawCredits = new Set<number>();
        table.entries.forEach((entry, index) => {
            if (entry.credit === 'JP') {
                log(`[FakeReelManager]   ${index + 1}. JP → symbolId=20, credit=0`);
            } else {
                const raw = entry.credit as number;
                validRawCredits.add(raw);
                const final_ = tools.divide(raw * bet, 100);
                log(`[FakeReelManager]   ${index + 1}. 原始=${raw} → ${raw} × ${bet} ÷ 100 = ${final_}`);
            }
        });

        let allCorrect = true;
        for (let i = 0; i < testCount; i++) {
            let cbResult: { credit: number, symbolId: number } | null = null;
            this.OnGenerateCoinCredit([betMode, (result: { credit: number, symbolId: number }) => {
                cbResult = result;
            }]);

            if (!cbResult) {
                warn(`[FakeReelManager]   ✗ 第 ${i + 1} 次: callback 未被呼叫`);
                allCorrect = false;
                continue;
            }

            const { credit, symbolId } = cbResult as { credit: number, symbolId: number };
            const errors: string[] = [];

            if (symbolId === 20) {
                if (credit !== 0) errors.push(`JP 但 credit=${credit} 不為 0`);
            } else if (symbolId === 14) {
                if (credit <= 0) {
                    errors.push(`非 JP 但 credit=${credit} <= 0`);
                } else {
                    const rawReversed = tools.divide(credit * 100, bet);
                    if (!validRawCredits.has(rawReversed)) {
                        errors.push(`反推原始值=${rawReversed} 不在權重表中`);
                    }
                }
            } else {
                errors.push(`symbolId=${symbolId} 不合法（應為 14 或 20）`);
            }

            const passed = errors.length === 0;
            if (!passed) allCorrect = false;
            log(`[FakeReelManager]   ${passed ? '✓' : '✗'} 第 ${i + 1} 次: credit=${credit}, symbolId=${symbolId}` +
                (errors.length > 0 ? ` [${errors.join(', ')}]` : ''));
        }

        if (allCorrect) {
            log(`[FakeReelManager] ✓ 全部 ${testCount} 次測試通過`);
        } else {
            warn(`[FakeReelManager] ✗ 有測試未通過`);
        }
    }
    //#endregion 測試功能
}
