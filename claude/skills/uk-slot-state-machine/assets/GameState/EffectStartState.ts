import { stateManager, BaseState, soundManager } from "db://astarte-framework/Managers";
import GameView from "../GameView";
import Game_Define from "../Game_Define";
import { Define } from "db://astarte-framework/utilis";
import { log } from "cc";

export class EffectStartState extends BaseState
{
    private m_gameView: GameView = null;

    constructor( gameView: GameView )
    {
        super();
        this.m_gameView = gameView;
    }

    public async OnEnter()
    {
        log( "OnEnter State : EFFECTSTART" );
        this.m_gameView.IsMgOmen = false;

        // 若無需等待，直接進入下一個狀態
        if (this.m_gameView.IsFreeGame) {
            stateManager.NextState(Game_Define.GameState.SCATTER_SHOW);
            return;
        }

        await Define.Wait(this.m_gameView, Game_Define.WaitTime);

        stateManager.NextState(Game_Define.GameState.SCATTER_SHOW);
    }

    public OnProcess()
    {

    }

    public OnLeave()
    {
        log( "OnLeave State : EFFECTSTART" );
    }
}
