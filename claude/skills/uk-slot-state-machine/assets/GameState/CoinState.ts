import { log } from "cc";
import { stateManager, BaseState } from "db://astarte-framework/Managers";
import GameView from "../GameView";
import Game_Define from "../Game_Define";

export class CoinState extends BaseState
{
    private m_gameView: GameView = null;

    constructor( gameView: GameView )
    {
        super();
        this.m_gameView = gameView;
    }

    public async OnEnter()
    {
        log( "OnEnter State : CoinState" );

        if ( !this.m_gameView.IsFreeGame )
        {
            return;
        }

        // TODO 若有需要處理FreeGame的Coin表演，請在這裡處理，目前先註解

        stateManager.NextState( Game_Define.GameState.AWARD );
    }

    public OnProcess()
    {

    }

    public OnLeave()
    {
        log( "OnLeave State : CoinState" );
    }
}
