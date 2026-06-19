import { _decorator } from "cc";
import GameView from "../GameView";
import { log } from "cc";
import { BaseState, newExtraManager, newBottombarManager, stateManager, eventManager } from "db://astarte-framework/Managers";
import Game_Define from "../Game_Define";
import { GAME_INTRO_MANAGER_EVENT } from "../GameIntroManager";

const { ccclass } = _decorator;

@ccclass( "FeatureShowState" )
export class FeatureShowState extends BaseState
{
    private m_gameView: GameView = null;

    /**
     * @ch 是否需要展示特色
     */
    public IsNeedFeatureDemo: boolean = false;

    constructor( gameView: GameView )
    {
        super();
        this.m_gameView = gameView;
    }

    public async OnEnter()
    {
        log( "OnEnter State : FEATURE_SHOW" );

        // 原有的特色展示邏輯
        const isSkip = this.PlayDefaultFeatureDemo();
        if (isSkip)
        {
            return;
        }

        stateManager.NextState( Game_Define.GameState.SCATTER_SHOW );
    }

    public OnProcess()
    {

    }

    public OnLeave()
    {
        log( "OnLeave State : FEATURE_SHOW" );
    }

    /**
     * @ch 播放預設特色功能
     * @returns 是否跳過特色展示
     */
    private PlayDefaultFeatureDemo() : boolean
    {
        if ( !newExtraManager.IsFeaturesDemo || this.m_gameView.IsAutoShowFeatures)
        {
            return false;
        }

        if (!this.IsNeedFeatureDemo)
        {
            return false;
        }

        this.IsNeedFeatureDemo = false;

        newBottombarManager.CanPlayFeaturesDemo( true );
        this.m_gameView.IsAutoShowFeatures = true;
        newBottombarManager.SetBarNodeVisiable( true );
        this.m_gameView.BuyBonus?.SetBuyBtnVisible( true );
        newExtraManager.AutoShowFeatures();

        eventManager.Dispatch( GAME_INTRO_MANAGER_EVENT.HIDE_NODE );

        log( "FeatureShowState: Playing default feature" );
        return true;
    }
}
