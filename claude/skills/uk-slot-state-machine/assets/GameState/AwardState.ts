import { log } from "cc";
import { BaseState, newBottombarManager, SlotBottomBarState } from "db://astarte-framework/Managers";
import GameView from "../GameView";
import Game_Define from "../Game_Define";
import { tools } from "db://astarte-framework/utilis";
import { SwitchOffKeyDefine } from "db://astarte-framework/License/LicenseSetting";

export class AwardState extends BaseState
{
    private m_gameView: GameView = null;

    /**
     * @ch 是否顯示獎勵效果結束
     */
    private m_isShowAwardEffectEnd: boolean = false;

    constructor( gameView: GameView )
    {
        super();
        this.m_gameView = gameView;
    }

    public async OnEnter()
    {
        log( "OnEnter State : AWARD" );

        this.m_isShowAwardEffectEnd = false;

        // TODO 若有需要處理大小報獎表演，請在這裡處理，目前先註解

        /*
        this.m_gameView.SlotReels.SetSymbolDark( false, -1 );
        let thisRoundWin: number = this.m_gameView.RoundInfo.RoundWin;
        let bet: number = Game_Define.GetNowBetValue();
        let rate = thisRoundWin / bet;
        let SpinAck = this.m_gameView.SpinAck;

        // 有贏分
        if ( rate > 0 && !this.m_gameView.IsFreeGame )
        {
            if (
                rate < 1
                && tools.CheckSwitchOff( SwitchOffKeyDefine.NoSoundUnder1 )// 送審規範
            )
            {
                newBottombarManager.SetWinValueWithCheck( { maxWin: thisRoundWin, value: this.m_gameView.Win } );
                this.m_gameView.SmallWin.SetWinLabelRunning( thisRoundWin, 0.1 );
                if ( SpinAck.RoundQueue[ this.m_gameView.CurPlateIndex ].AwardDataVec )
                {
                    await this.m_gameView.EffectPlate.ShowSymbolEffect(
                        SpinAck.RoundQueue[ 0 ].AwardDataVec,
                        // SpinAck.RoundQueue[ 0 ].MGWildWinner
                    );
                    // this.m_gameView.SlotReels.ShowPlate();
                }
                // this.m_gameView.AfterShowWin();
            }
            else if ( rate < Game_Define.PlateEftOdds[ 2 ] )
            {
                // 地bar上的小贏分label
                newBottombarManager.SetWinValueWithCheck( { maxWin: SpinAck.TotalWin, value: thisRoundWin } );
                // newBottombarManager.SetWinValue( thisRoundWin );
                this.m_gameView.SmallWin.SetWinLabelRunning( thisRoundWin, 0.1 );
                // // 小獎音效根據倍率不同播放
                if ( rate < Game_Define.PlateEftOdds[ 0 ] )
                {
                    soundManager.Play( Game_Define.AudioClips.Small_Win01 );
                }
                else if ( rate < Game_Define.PlateEftOdds[ 1 ] )
                {
                    soundManager.Play( Game_Define.AudioClips.Small_Win02 );
                }
                else if ( rate < Game_Define.PlateEftOdds[ 2 ] )
                {
                    soundManager.Play( Game_Define.AudioClips.Small_Win03 );
                }
                if ( this.m_gameView.RoundInfo.AwardDataVec )
                {
                    await this.m_gameView.EffectPlate.ShowSymbolEffect(
                        SpinAck.RoundQueue[ 0 ].AwardDataVec,
                        // SpinAck.RoundQueue[ 0 ].MGWildWinner,
                    );
                    // this.m_gameView.SlotReels.ShowPlate();
                }
                // this.m_gameView.AfterShowWin();
            }
            else
            {
                // 大贏分
                soundManager.Play( Game_Define.AudioClips.Small_Win03 );
                this.m_gameView.BigWin.IsEnd = false;
                await this.m_gameView.EffectPlate.ShowSymbolEffect( SpinAck.RoundQueue[ 0 ].AwardDataVec );
                // this.m_gameView.SlotReels.ShowPlate();
                this.m_gameView.ShowBigWin( thisRoundWin, rate );
                newBottombarManager.SetSpinState( SlotBottomBarState.GET_AWARD_NO_AUTO );
            }
        }
        */
        this.m_isShowAwardEffectEnd = true;
    }

    public OnProcess()
    {
        // 若獎勵效果結束，則進入下一個狀態
        if ( this.IsProcessEnd() ) {
            this.m_gameView.AfterShowWin();
        }
    }

    public OnLeave()
    {
        log( "OnLeave State : AWARD" );
    }

    /**
     * @ch 是否處理結束
     */
    private IsProcessEnd(): boolean
    {
        return this.m_isShowAwardEffectEnd;
    }
}
