import { _decorator, log } from "cc";
import { stateManager, BaseState, SlotBottomBarState, newBottombarManager } from "db://astarte-framework/Managers";
import GameView from "../GameView";
import Game_Define from "../Game_Define";

const { ccclass } = _decorator;
@ccclass( "EnterFreeState" )
export class EnterFreeState extends BaseState
{
    private m_gameView: GameView = null;

    constructor( gameView: GameView )
    {
        super();
        this.m_gameView = gameView;
    }

    public async OnEnter()
    {
        log( "OnEnter State : ENTER_FREE" );

        // 暫停主遊戲背景音樂
        this.m_gameView.PauseMainGameBgm();

        newBottombarManager.SetEnterFree();

        // 停止效果
        this.StopEffect();
        this.m_gameView.IsFreeGame = true;

        newBottombarManager.SetBarNodeVisiable( false );
        this.m_gameView.BuyBonus?.SetBuyBtnVisible( false );

        // TODO 播放免費遊戲進場


        // 播放免費遊戲音樂
        this.m_gameView.PlayFreeGameBgm();

        // 設置地bar
        newBottombarManager.SetBarNodeVisiable( true );

        // 各遊戲須自己處理自動玩
        if ( newBottombarManager.IsAutoSpin )
        {
            if ( this.m_gameView.AutoplayInfos.isCheckFree )
            {
                newBottombarManager.ShowAutoPlayState( false );
                newBottombarManager.SetSpinState( SlotBottomBarState.IDLE );
                this.m_gameView.IsFirstRound = true;
            }
            else
            {
                this.m_gameView.IsFirstRound = false;
            }
        }
        else
        {
            newBottombarManager.SetSpinState( SlotBottomBarState.IDLE );
            this.m_gameView.IsFirstRound = true;
        }

        // NextState
        stateManager.NextState( Game_Define.GameState.ROUND_END );
    }

    public OnProcess()
    {

    }

    public OnLeave()
    {
        log( "OnLeave State : ENTER_FREE" );
    }

    /**
     * @ch 停止效果
     */
    private StopEffect()
    {

    }
}
