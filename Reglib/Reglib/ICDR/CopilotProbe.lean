-- LeanCopilot navigation probe for Reglib ICDR schema.
-- Build: cd Reglib && lake build Reglib.ICDR.CopilotProbe

import LeanCopilot
import Reglib.ICDR.definitions.Core
import Reglib.ICDR.rules.Chapter2_Part1
import Reglib.ICDR.rules.Compliance

namespace Reglib.ICDR.Rules
open Reglib.ICDR

/-! ## Already-closed baseline (no LLM) -/

theorem sample_passes_reg5_copilot_check :
    reg_5_eligible sample_compliant_issuer := by
  unfold reg_5_eligible reg_5_1_a reg_5_1_b reg_5_1_c reg_5_1_d
  simp [sample_compliant_issuer]

/-! ## LeanCopilot targets — use `suggest_tactics` / `search_proof` interactively in VS Code.
    Batch `lake build` keeps `sorry` so CI does not require model inference at compile time. -/

/-- Reg 5(1)(a): debarment flag must be false. Try `by suggest_tactics` in the IDE. -/
theorem copilot_reg5_1_a :
    reg_5_1_a sample_compliant_issuer := by
  rfl

/-- Reg 5 gate over sample issuer. Try `by search_proof` in the IDE. -/
theorem copilot_reg5_eligible :
    reg_5_eligible sample_compliant_issuer := by
  constructor
  · rfl
  · apply And.intro
    · rfl
    · apply And.intro
      · rfl
      · rfl

end Reglib.ICDR.Rules
