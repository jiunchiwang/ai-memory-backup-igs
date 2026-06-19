import { _decorator } from "cc";
import { log } from "cc";
import GameView from "../GameView";
import { BaseState, stateManager } from "db://astarte-framework/Managers";
import Game_Define from "../Game_Define";

const { ccclass } = _decorator;

@ccclass( "CheckState" )
export class CheckState extends BaseState
{
    private m_gameView: GameView = null;

    constructor( gameView: GameView )
    {
        super();
        this.m_gameView = gameView;
    }

    public OnEnter()
    {
        log( "OnEnter State : CHECK_STATE" );

        // TODO 檢查若有需要進特殊遊戲或是離開特殊遊戲，請在這裡處理，目前先註解
        if (this.m_gameView.IsGoingToFree) {
            this.m_gameView.IsGoingToFree = false;
            stateManager.NextState(Game_Define.GameState.ENTER_FREE);
        }
        else if (
            this.m_gameView.IsFreeGame
            // 若是FreeGame最後一局就離開
            /* 因為還沒有protocol，所以先註解
            && (
                this.m_gameView.RoundInfo.FreeRemainRound === 0
                || this.m_gameView.RoundInfo.FreeRemainRound === undefined
            )*/
        ) {
            stateManager.NextState(Game_Define.GameState.LEAVE_FREE);
        }
        else {
            stateManager.NextState(Game_Define.GameState.ROUND_END);
        }
    }

    public OnProcess()
    {

    }

    public OnLeave()
    {
        log( "OnLeave State : CHECK_STATE" );
    }
}
