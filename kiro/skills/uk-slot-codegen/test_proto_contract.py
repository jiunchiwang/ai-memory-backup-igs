import tempfile
import unittest
from pathlib import Path

from verify_compile import check_proto_contract


GOOD_DTS = """export namespace ar2xProto {
export interface IRoundInfo { PlateQueue?: IPlateInfo[]; WinLineIndex?: number[]; }
export class RoundInfo implements IRoundInfo { PlateQueue: IPlateInfo[]; WinLineIndex: number[]; }
export interface IAwardData { EliminatePos?: number[]; }
export class AwardData implements IAwardData { EliminatePos: number[]; }
export interface ISpinAck { FreeGameRound?: number; }
export class SpinAck implements ISpinAck { FreeGameRound: number; }
export class GameInfoData {}
export class CColumn {}
export interface IPlateInfo {}
}
declare const protocol: { ar2xProto: typeof ar2xProto };
export default protocol;
"""

GOOD_JS = """const ar2xProto = {};
ar2xProto.GameInfoData = function GameInfoData() {};
ar2xProto.CColumn = function CColumn() {};
ar2xProto.RoundInfo = function RoundInfo() { this.PlateQueue = []; this.WinLineIndex = []; };
ar2xProto.AwardData = function AwardData() { this.EliminatePos = []; };
ar2xProto.SpinAck = function SpinAck() { this.FreeGameRound = 0; };
module.exports = { ar2xProto };
"""


class ProtoContractTest(unittest.TestCase):
    def make_project(self, bridge: str, dts: str = GOOD_DTS, js: str = GOOD_JS) -> Path:
        root = Path(tempfile.mkdtemp())
        script = root / "assets" / "Script"
        test = script / "Test"
        test.mkdir(parents=True)
        (script / "Proto.ts").write_text(bridge, encoding="utf-8")
        (script / "GameView.ts").write_text(
            "const roundInfo = { PlateQueue: [], WinLineIndex: [] };", encoding="utf-8"
        )
        (test / "ar2xProto.js").write_text(js, encoding="utf-8")
        (test / "ar2xProto.d.ts").write_text(dts, encoding="utf-8")
        return root

    def test_valid_contract_passes(self):
        root = self.make_project(
            'import protocol from "./Test/ar2xProto.js";\n'
            'export type { ar2xProto } from "./Test/ar2xProto.js";\n'
            'export default protocol;\n'
        )
        self.assertEqual([], check_proto_contract(root))

    def test_export_star_and_missing_mock_fields_fail(self):
        root = self.make_project(
            'import protocol from "./Test/ar2xProto.js";\n'
            'export * from "./Test/ar2xProto.js";\n'
            'export default protocol;\n',
            dts=GOOD_DTS.replace(" PlateQueue?: IPlateInfo[]; WinLineIndex?: number[];", ""),
        )
        errors = check_proto_contract(root)
        self.assertTrue(any("export *" in error for error in errors))
        self.assertTrue(any("missing type export" in error for error in errors))
        self.assertTrue(any("IRoundInfo missing Mock field PlateQueue" in error for error in errors))

    def test_missing_runtime_constructor_fails(self):
        root = self.make_project(
            'import protocol from "./Test/ar2xProto.js";\n'
            'export type { ar2xProto } from "./Test/ar2xProto.js";\n'
            'export default protocol;\n',
            js=GOOD_JS.replace("ar2xProto.CColumn = function CColumn() {};\n", ""),
        )
        errors = check_proto_contract(root)
        self.assertTrue(any("runtime namespace contract failed" in error for error in errors))

    def test_used_compat_fields_and_stale_component_apis_fail(self):
        root = self.make_project(
            'import protocol from "./Test/ar2xProto.js";\n'
            'export type { ar2xProto } from "./Test/ar2xProto.js";\n'
            'export default protocol;\n',
            dts=GOOD_DTS.replace(" FreeGameRound?: number;", "").replace(" EliminatePos?: number[];", ""),
        )
        script = root / "assets" / "Script"
        (script / "GameView.ts").write_text(
            "private m_smallWinNode: Node; GenerateMockSpinAck() { return {}; }", encoding="utf-8"
        )
        (script / "GameState").mkdir()
        (script / "GameState" / "AwardState.ts").write_text(
            "game.SmallWin?.SetWinLabelRunning(1, .1);", encoding="utf-8"
        )
        (script / "GameState" / "EnterFreeState.ts").write_text(
            "game.SpinAck.FreeGameRound;", encoding="utf-8"
        )
        (script / "GameState" / "SpinState.ts").write_text(
            "game.EffectPlate.StopOneLineShow();", encoding="utf-8"
        )
        (script / "EffectPlate").mkdir()
        (script / "EffectPlate" / "EffectPlate.ts").write_text(
            "award.EliminatePos; export class EffectPlate {}", encoding="utf-8"
        )
        errors = check_proto_contract(root)
        self.assertTrue(any("ISpinAck missing used field FreeGameRound" in error for error in errors))
        self.assertTrue(any("IAwardData missing used field EliminatePos" in error for error in errors))
        self.assertTrue(any("must initialize used field FreeGameRound" in error for error in errors))
        self.assertTrue(any("SmallWin is Node" in error for error in errors))
        self.assertTrue(any("StopOneLineShow is used but not implemented" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
