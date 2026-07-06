import { _decorator, log } from "cc";
import { stateManager, BaseState, newBottombarManager } from "db://astarte-framework/Managers";
import GameView from "../GameView";
import Game_Define from "../Game_Define";
import { Define, tools } from "db://astarte-framework/utilis";
import { SwitchOffKeyDefine } from "db://astarte-framework/License/LicenseSetting";

const { ccclass } = _decorator;
@ccclass( "LeaveFreeState" )
export class LeaveFreeState extends BaseState
{
    private m_gameView: GameView = null;

    constructor( gameView: GameView )
    {
        super();
        this.m_gameView = gameView;
    }

    public async OnEnter()
    {
        log( "OnEnter State : LeaveFreeState" );

        this.LeaveFreeSetting();
    }

    async LeaveFreeSetting()
    {
        newBottombarManager.SetBarNodeVisiable( false );

        // 若有需要等待，可在這裡處理

        // 停止免費遊戲BGM
        this.m_gameView.StopFreeGameBgm();

        newBottombarManager.SetLeaveFree();
        newBottombarManager.LockBetEnable( true );
        this.StopEffect();

        /*
        // 特色描述
        if ( !tools.CheckSwitchOff( SwitchOffKeyDefine.CloseManual ) )
        {
            this.m_gameView.Manual.node.active = true;
        }
        */

        // ==================== 離開時的處理 ====================

        // 設置免費遊戲狀態為false
        this.m_gameView.IsFreeGame = false;

        // TODO 切換到主遊戲UI


        // 設置主遊戲下注介面可見
        newBottombarManager.SetBarNodeVisiable( true );

        // 設置BuyBonus可見
        this.m_gameView.BuyBonus?.SetBuyBtnVisible( true );

        // 播放主遊戲BGM
        this.m_gameView.ResumeMainGameBgm();

        // NextState
        stateManager.NextState( Game_Define.GameState.ROUND_END );
    }

    public OnProcess()
    {

    }

    public OnLeave()
    {
        log( "OnLeave State : LeaveFreeState" );
    }

    /**
     * @ch 停止效果
     * @returns {void}
     */
    private StopEffect(): void
    {
        // TODO 請將要停止的效果都放在這裡
    }
}
