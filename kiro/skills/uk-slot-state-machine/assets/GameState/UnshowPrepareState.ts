import { _decorator } from "cc";
import GameView from "../GameView";
import { log } from "cc";
import { BaseState, commonGameManager, eventManager, msgBoxManager, newBottombarManager, newExtraManager, stateManager } from "db://astarte-framework/Managers";
import { CommonState, Define } from "db://astarte-framework/utilis";
import Game_Define from "../Game_Define";
import { GAME_INTRO_MANAGER_EVENT } from "../GameIntroManager";

const { ccclass } = _decorator;

@ccclass( "UnshowPrepareState" )
export class UnshowPrepareState extends BaseState
{
    private m_gameView: GameView = null;

    constructor( gameView: GameView )
    {
        super();
        this.m_gameView = gameView;
    }

    public async OnEnter()
    {
        if ( !commonGameManager.HasUnshow )
        {
            return;
        }

        log( "OnEnter State : UnshowPrepare" );
        newExtraManager.HasUnshow = false;

        newBottombarManager.SetBarNodeVisiable( true );

        // 若有開頭動畫，請關閉
        eventManager.Dispatch( GAME_INTRO_MANAGER_EVENT.HIDE_NODE );

        // TODO 處理回到上一局的畫面，目前先註解
        /*
        let UnshowSpinAckQue = this.m_gameView.UnshowSpinAck;

        let round = this.m_gameView.CurPlateIndex = commonGameManager.UnshowStartRound;
        // console.error( "UnshowPrepare", UnshowSpinAckQue, commonGameManager.UnshowStartRound );
        */

        // 顯示確認視窗
        msgBoxManager.ShowMessageBox(
            Define.StringKey.MSGBOX_UNSHOW_BACK,
            Define.StringKey.MSGBOX_TITLE_SYSTEM_INFO,
            () =>
            {
                stateManager.NextState( CommonState.SPIN );
            }
        );
    }

    public OnProcess()
    {
    }

    public OnLeave()
    {
        log( "OnLeave State : UnshowPrepare" );
    }
}
