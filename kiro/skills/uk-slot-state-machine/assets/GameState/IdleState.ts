import { log } from "cc";
import { newBottombarManager, newExtraManager } from "db://astarte-framework/Managers";
import GameView from "../GameView";
import { Common_IdleState } from "db://astarte-framework/Component";

export class IdleState extends Common_IdleState
{
    private m_gameView: GameView = null;

    constructor( gameView: GameView )
    {
        super();
        this.m_gameView = gameView;
    }

    Enter()
    {
        log( "OnEnter State : IdleState" );

        // 非特殊遊戲，盤面Index歸零
        if (
            !this.m_gameView.IsGoingToFree
            && !this.m_gameView.IsFreeGame
            && !newExtraManager.IsFeaturesDemoMode
        )
        {
            // 若有需要顯示線獎，請在這裡處理
            /*
            this.m_gameView.EffectPlate.ShowSingleLineEffect();
            */
            this.m_gameView.CurPlateIndex = -1;
        }

        if ( !this.m_gameView.IsFreeGame )
        {
            newBottombarManager.CanPlayFeaturesDemo( true );
            newBottombarManager.IsGameIdle = true;
            if ( !newBottombarManager.IsFreeSpin )
            {
                newExtraManager.SetBuyBonusState( true );
            }
        }
    }

    Leave()
    {
        log( "OnLeave State : IdleState" );
    }
}
