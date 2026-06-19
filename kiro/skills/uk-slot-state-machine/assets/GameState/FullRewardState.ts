import { _decorator, log } from "cc";
import { stateManager, BaseState } from "db://astarte-framework/Managers";
import GameView from "../GameView";
import Game_Define from "../Game_Define";

const { ccclass } = _decorator;
@ccclass( "FullRewardState" )
export class FullRewardState extends BaseState
{
    private m_gameView: GameView = null;

    constructor( gameView: GameView )
    {
        super();
        this.m_gameView = gameView;
    }

    public async OnEnter()
    {
        log( "OnEnter State : FullRewardState" );

        // TODO 若有需要處理FullReward，請在這裡處理

        // NextState
        stateManager.NextState( Game_Define.GameState.LEAVE_FREE );
    }

    public OnProcess()
    {

    }

    public OnLeave()
    {
        log( "OnLeave State : FullRewardState" );
    }
}
