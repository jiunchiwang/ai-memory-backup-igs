import { log } from "cc";
import { newBottombarManager, BaseState, commonGameManager, SlotBottomBarState, stateManager } from "db://astarte-framework/Managers";
import GameView from "../GameView";
import Game_Define from "../Game_Define";
import { roundController } from "db://astarte-framework/utilis";

export class SpinState extends BaseState
{
    private m_gameView: GameView = null;

    constructor( gameView: GameView )
    {
        super();
        this.m_gameView = gameView;
    }

    public OnEnter()
    {
        log( "OnEnter State : SPIN" );

        roundController.StartSpin();
        // TODO 停止之前的效果，目前先註解
        /*
        this.m_gameView.EffectPlate.CurAwardLines.length = 0;
        this.m_gameView.EffectPlate.StopOneLineShow();
        this.m_gameView.ClearAll();
        */

        if ( commonGameManager.HasUnshow )
        {
            commonGameManager.HasUnshow = false;
            this.m_gameView.IsHardStop = newBottombarManager.IsHardStop;
            // TODO 若有需要處理Unshow，請在這裡處理，目前先註解
            /*
            this.m_gameView.OnRecvSpinAck( this.m_gameView.UnshowSpinAck, true );
            this.m_gameView.UnshowSpinAck = null;
            */
        }
        else
        {
            this.m_gameView.CurPlateIndex = this.m_gameView.CurPlateIndex + 1;
            this.m_gameView.StartSpin();
        }

        if ( this.m_gameView.IsFreeGame )
        {
            // TODO 若有需要設置現在局數，請在這裡處理，目前先註解
            /*
            this.m_gameView.SetNowRoundInfo( this.m_gameView.SpinAck.RoundQueue[ this.m_gameView.CurPlateIndex ] );
            */

            if ( this.m_gameView.IsHardStop )
            {
                // TODO 目前沒有轉輪的主程式，所以先註解
                /*
                this.m_gameView.SinglePlateMgr.ClickStopBtn();
                */
                newBottombarManager.SetSpinWithSpeed();
            }
            else
            {
                if ( !newBottombarManager.IsAutoSpin )
                {
                    newBottombarManager.SetSpinState( SlotBottomBarState.START_SPIN );
                }
            }
        }
    }

    public OnProcess( dt: number )
    {
        // TODO 需等停輪，但因為還沒有轉輪，所以先註解
        /*
        if ( this.m_gameView.IsFreeGame )
        {
            this.m_gameView.SinglePlateMgr.Spin( dt );
            if ( !this.m_gameView.SinglePlateMgr.IsPlateStop() )
            {
                return;
            }
        }
        else
        {
            this.m_gameView.SlotReels.Spin( dt );
            if ( !this.m_gameView.SlotReels.IsStop )
            {
                return;
            }
        }

        this.m_gameView.EffectPlate.CloseNearWin();
        */

        this.m_gameView.CanPlateStop = true;
        this.m_gameView.CanSpaceStop = true;
        if ( !newBottombarManager.IsAutoSpin )
        {
            newBottombarManager.SetSpinState( SlotBottomBarState.CLICK_SPIN );
        }

        stateManager.NextState( Game_Define.GameState.EFFECT_START );
    }

    public OnLeave()
    {
        log( "OnLeave State : SPIN" );
    }
}
