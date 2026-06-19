import { log } from "cc";
import { BaseState, SlotBottomBarState, autoShowManager, eventManager, newBottombarManager, stateManager } from "db://astarte-framework/Managers";
import GameView from "../GameView";
import { Define, CommonState } from "db://astarte-framework/utilis";
import Game_Define from "../Game_Define";
import { GAME_INTRO_MANAGER_EVENT } from "../GameIntroManager";

export class PlateShowState extends BaseState
{
    private m_gameView: GameView = null;

    constructor( gameView: GameView )
    {
        super();
        this.m_gameView = gameView;
    }

    public async OnEnter() {
        log( "OnEnter State : PLATE_SHOW" );

        // TODO 判斷要展示的intro方向，若只有一個方向時，不管直或橫，index都為0
        const index = this.m_gameView.IsLandscape ? 0 : 1;

        await Promise.all([
            // 若有需要展示遊戲介紹，請在這裡處理
            this.ShowIntro(index),
        ])
            .then(
                () => {
                    // 播放主遊戲BGM
                    this.m_gameView.PlayMainGameBgm();

                    this.m_gameView.BuyBonus?.SetBuyBtnVisible(true);
                    newBottombarManager.SetSpinState(SlotBottomBarState.IDLE);
                    if (Define.FreeSpinRemain > 0) {
                        stateManager.NextState(CommonState.CHECK_FREESPIN);
                    }
                    else {
                        stateManager.NextState(CommonState.IDLE);
                    }
                    autoShowManager.StartAutoShow();
                    newBottombarManager.SetBarNodeVisiable(true);
                }
            );
    }

    public OnProcess()
    {
    }

    public OnLeave()
    {
        log( "OnLeave State : PLATE_SHOW" );
    }

    /**
     * @ch 展示intro
     * @param index 索引 0:橫 1:直 (若只有一個方向時，不管直或橫，index都為0)
     * @returns Promise<void>
     */
    private async ShowIntro(index: number = 0) : Promise<void>
    {
        return new Promise(resolve => {
            eventManager.Dispatch(GAME_INTRO_MANAGER_EVENT.SHOW_INTRO, index, resolve);
        });
    }
}
