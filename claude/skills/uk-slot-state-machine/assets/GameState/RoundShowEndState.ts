import { _decorator } from "cc";
import GameView from "../GameView";
import { log } from "cc";
import { CommonState } from "db://astarte-framework/utilis";
import { BaseState, stateManager } from "db://astarte-framework/Managers";

const { ccclass, } = _decorator;

@ccclass( "RoundShowEndState" )
export class RoundShowEndState extends BaseState
{
    private m_gameView: GameView = null;

    constructor( gameView: GameView )
    {
        super();
        this.m_gameView = gameView;
    }

    public OnEnter()
    {
        log( "OnEnter State : ROUND_SHOW_END" );

        stateManager.NextState( CommonState.COMMON_SHOW );
    }

    public OnProcess()
    {

    }

    public OnLeave()
    {
        log( "OnLeave State : ROUND_SHOW_END" );
    }
}
