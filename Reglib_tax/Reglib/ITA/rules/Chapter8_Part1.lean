-- Auto-generated rules file: Chapter8_Part1.lean
-- Chapter VIII, Part I: REBATE FOR RESIDENT INDIVIDUALS

import Reglib.ITA.definitions.Core

namespace Reglib.ITA.Rules

open Reglib.ITA

/-! ## Regulation 87a -/
/-- Reg 87A(new): Under the new tax regime (section 115BAC), the rebate under section 87A is available up to twenty-five thousand rupees f... -/
def reg_87a_new_regime (issuer : Taxpayer) : Prop :=
  issuer.is_new_tax_regime = true
  ∧ issuer.rebate_87a_new_threshold ≥ 0  -- TODO: set correct threshold
  ∧ issuer.max_rebate_87a_new ≥ 0  -- TODO: set correct threshold

/-- Reg 87A: An assessee, being an individual resident in India, whose total income does not exceed five hundred thousand rupees, sha... -/
def reg_87a_rebate (issuer : Taxpayer) : Prop :=
  issuer.total_income_amount ≥ 0  -- TODO: set correct threshold
  ∧ issuer.rebate_87a_threshold ≥ 0  -- TODO: set correct threshold
  ∧ issuer.max_rebate_87a ≥ 0  -- TODO: set correct threshold

/-- Combined Regulation 87a gate -/
def reg_87a_eligible (issuer : Taxpayer) : Prop :=
  reg_87a_rebate issuer
  ∧ reg_87a_new_regime issuer

/-! ## Composite Chapter VIII Part I Gate -/

def chapter8_part1_eligible (issuer : Taxpayer) : Prop :=
  reg_87a_eligible issuer

end Reglib.ITA.Rules
