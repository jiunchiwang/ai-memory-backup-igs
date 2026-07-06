import { log, tween } from "cc";
import { BaseState, SlotBottomBarState, newBottombarManager, stateManager } from "db://astarte-framework/Managers";
import GameView from "../GameView";
import Game_Define from "../Game_Define";
import { CommonState } from "db://astarte-framework/utilis";

export class WaitResState extends BaseState
{
    private m_gameView: GameView = null;

    constructor( gameView: GameView )
    {
        super();
        this.m_gameView = gameView;
    }

    public OnEnter()
    {
        log( "OnEnter State : WAIT_RES" );

        this.m_gameView.ChangeDemoPlateByRatio();
        newBottombarManager.FeaturesDemoInit(
            ( featuresType: number ) =>
            {
                // TODO 請自行判斷進Demo時，是否要播放主遊戲BGM，若要播放，請在這裡播放
                this.m_gameView.PlayMainGameBgm();

                tween( this.m_gameView.node )
                    .call( () =>
                    {
                        newBottombarManager.SetSpinState( SlotBottomBarState.CLICK_SPIN );
                        stateManager.NextState( CommonState.SPIN );
                    } )
                    .delay( 0.5 )
                    .call( () =>
                    {
                        // TODO 若有需要處理Feature，請在這裡處理，目前先註解
                        /*
                        this.m_gameView.OnRecvSpinAck(this.m_gameView.GetFeatureSpinAckForDemo(featuresType));
                        */
                    } )
                    .start();
            },
            this.m_gameView.GetFeatureSpinAckLengthForDemo(),
            newBottombarManager.FindBetIndexByValue( Game_Define.FeatureBetValue ),
            () =>
            {
                if ( this.m_gameView.IsAutoShowFeatures )
                {
                    this.m_gameView.IsAutoShowFeatures = false;
                    stateManager.NextState( Game_Define.GameState.WAIT_READY );
                }
            },
        );
        stateManager.NextState( Game_Define.GameState.WAIT_READY );
    }

    public OnProcess()
    {

    }

    public OnLeave()
    {
        log( "OnLeave State : WAIT_RES" );
    }
}
