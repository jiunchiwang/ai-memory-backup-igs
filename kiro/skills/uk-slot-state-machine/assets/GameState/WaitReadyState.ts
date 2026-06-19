import { log } from "cc";
import { appManager, newBottombarManager, BaseState, eventManager } from "db://astarte-framework/Managers";
import GameView from "../GameView";
import { GAME_INTRO_MANAGER_EVENT } from "../GameIntroManager";

export class WaitReadyState extends BaseState
{

    private m_gameView: GameView = null;

    constructor( gameView: GameView )
    {
        super();
        this.m_gameView = gameView;
    }

    public async OnEnter()
    {
        log( "OnEnter State : WAIT_READY" );

        newBottombarManager.ShowGameScene();
        newBottombarManager.ShowPlayReady();
        newBottombarManager.SetBarNodeVisiable( false );
        appManager.LoadingComplete();
        this.m_gameView.InitExtra();

        // 若有開頭動畫就開啟
        eventManager.Dispatch(GAME_INTRO_MANAGER_EVENT.SHOW_NODE);
        eventManager.Dispatch(GAME_INTRO_MANAGER_EVENT.UPDATE_UI);
    }

    public OnProcess()
    {
    }

    public OnLeave()
    {
        log( "OnLeave State : WAIT_READY" );
    }
}
