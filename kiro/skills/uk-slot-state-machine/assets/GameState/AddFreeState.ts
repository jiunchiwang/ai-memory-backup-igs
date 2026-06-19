import { _decorator, log } from "cc";
import { stateManager, BaseState } from "db://astarte-framework/Managers";
import GameView from "../GameView";
import Game_Define from "../Game_Define";

const { ccclass } = _decorator;
@ccclass( "AddFreeState" )
export class AddFreeState extends BaseState
{
    private m_gameView: GameView = null;

    constructor( gameView: GameView )
    {
        super();
        this.m_gameView = gameView;
    }

    public async OnEnter()
    {
        log( "OnEnter State : AddFreeState" );

        // this.m_gameView.FgCounter.AddRound();
        stateManager.NextState( Game_Define.GameState.ROUND_END );
    }

    public OnProcess()
    {

    }

    public OnLeave()
    {
        log( "OnLeave State : AddFreeState" );
    }
}
