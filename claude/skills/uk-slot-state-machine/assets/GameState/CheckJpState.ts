import { log } from "cc";
import { stateManager, BaseState } from "db://astarte-framework/Managers";
import GameView from "../GameView";
import Game_Define from "../Game_Define";
import { Define } from "db://astarte-framework/utilis";

export class CheckJpState extends BaseState
{
    private m_gameView: GameView = null;

    constructor( gameView: GameView )
    {
        super();
        this.m_gameView = gameView;
    }

    public async OnEnter()
    {
        log( "OnEnter State : CheckJp" );

        if (
            !this.m_gameView.IsFreeGame
            || this.m_gameView.SinglePlateMgr.CurCoinNum !== Game_Define.FULL_PLATE_NUM )
        {
            stateManager.NextState( Game_Define.GameState.EFFECT_START );
            return;
        }

        // TODO 若有需要處理Jackpot，請在這裡處理，目前先註解
        // await Promise.all( [
        //     this.m_gameView.FgFullRewardSpine.PlayFullReward(),
        //     this.m_gameView.JpComplimentSpine.PlayJpCompliment()
        // ] );

        stateManager.NextState( Game_Define.GameState.EFFECT_START );
    }

    public OnProcess()
    {

    }

    public OnLeave()
    {
        log( "OnLeave State : CheckJp" );
    }
}
