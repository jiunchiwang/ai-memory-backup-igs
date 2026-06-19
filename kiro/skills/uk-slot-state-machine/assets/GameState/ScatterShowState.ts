import { BaseState, msgBoxManager, stateManager } from "db://astarte-framework/Managers";
import GameView from "../GameView";
import Game_Define from "../Game_Define";
import { log } from "cc";
import { Define } from "db://astarte-framework/utilis";

export class ScatterShowState extends BaseState
{
    private m_gameView: GameView = null;

    constructor( gameView: GameView )
    {
        super();
        this.m_gameView = gameView;
    }

    public async OnEnter()
    {
        log( "OnEnter State : ScatterShowState" );

        // 若無需表演，直接進入下一個狀態
        if ( !this.m_gameView.IsFreeGame )
        {
            stateManager.NextState( Game_Define.GameState.AWARD );
            return;
        }

        // TODO 檢查是否達到MaxWin 因為還沒有protocol，所以先註解
        /*
        let maxFlag = this.m_gameView.SpinAck.RoundQueue[ this.m_gameView.CurPlateIndex ].MaxFlag;
        if ( maxFlag )
        {
            msgBoxManager.ShowMessageBox(
                Define.StringKey.MSGBOX_MAX_REWARD,
                Define.StringKey.MSGBOX_TITLE_SYSTEM_INFO,
                () =>
                {
                    stateManager.NextState( Game_Define.GameState.AWARD );
                }
            );
        }
        else
        {
            stateManager.NextState( Game_Define.GameState.AWARD );
        }
        */
    }

    public OnProcess()
    {

    }

    public OnLeave()
    {
        log( "OnLeave State : ScatterShowState" );
    }
}
