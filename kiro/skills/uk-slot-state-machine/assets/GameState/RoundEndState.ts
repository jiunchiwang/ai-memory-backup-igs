import { log } from "cc";
import { BaseState, SlotBottomBarState, commonGameManager, newBottombarManager, newExtraManager } from "db://astarte-framework/Managers";
import GameView from "../GameView";
import { roundController, tempoSetting, tools } from "db://astarte-framework/utilis";

export class RoundEndState extends BaseState
{
    private m_gameView: GameView = null;
    private m_processTick: number = 0;

    constructor( gameView: GameView )
    {
        super();
        this.m_gameView = gameView;
    }

    public OnEnter()
    {
        log( "OnEnter State : ROUND_END" );

        // 不是FG的話要歸零
        if ( !this.m_gameView.IsFreeGame && !this.m_gameView.IsGoingToFree )
        {
            // 記得 歸0
            this.m_gameView.Win = 0;

            // 盤面Index回復
            this.m_gameView.CurPlateIndex = -1;
            if ( newExtraManager.IsFeaturesDemoMode )
            {
                // 停止效果
                /*
                this.m_gameView.EffectPlate.StopOneLineShow();
                newExtraManager.CheckBuyBonusOverAni();
                this.m_gameView.ClearAll();
                */
            }
        }

        this.m_gameView.CanSpaceStop = true;
        this.m_gameView.CanPlateStop = true;

        if ( newBottombarManager.IsAutoSpin )
        {
            // 轉輪節奏模組：三幣瑞龍
            this.m_processTick = tempoSetting.TempoSetting.TripleCoinTreasure.AUTO_DELAY_TIME;
        }
        else
        {
            this.m_processTick = 0;
        }

        this.m_gameView.RetryRoundEnd();
    }

    public OnProcess( dt: number )
    {
        this.m_processTick = tools.strip( this.m_processTick - dt );
        if ( this.m_processTick > 0
            || !roundController.CanToNextRound()
            || ( commonGameManager.IsTwice && !commonGameManager.IsGetRoundEndAck ) )
        {
            return;
        }

        // 離開特色，要將自動玩關閉
        if ( newExtraManager.IsFeaturesDemoMode && !newBottombarManager.IsAutoSpin )
        {
            newBottombarManager.ShowAutoPlayState( false );

            // TODO 中獎線數歸零，目前先註解
            /*
            this.m_gameView.EffectPlate.CurAwardLines.length = 0;
            */
        }

        // 確認有無自動玩次數 要改變地bar顯示
        if ( newBottombarManager.IsAutoSpin && newBottombarManager.IsAutoPlayByTimes() )
        {
            newBottombarManager.SetSpinState( SlotBottomBarState.CLICK_STOP_IN_AUTOPLAY );
        }

        this.m_gameView.ForEndToNext();
    }

    public OnLeave()
    {
        log( "OnLeave State : ROUND_END" );
    }
}
