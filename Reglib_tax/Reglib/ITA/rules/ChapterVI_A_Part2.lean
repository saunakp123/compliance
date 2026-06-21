-- Auto-generated rules file: ChapterVI_A_Part2.lean
-- Chapter VI-A, Part II: DEDUCTION FOR HEALTH INSURANCE

import Reglib.ITA.definitions.Core

namespace Reglib.ITA.Rules

open Reglib.ITA

/-! ## Regulation 80d -/
/-- Reg 80D(1): In computing the total income of an assessee, being an individual or a Hindu undivided family, there shall be deducted s... -/
def reg_80d_1 (issuer : Taxpayer) : Prop :=
  issuer.health_insurance_premium_amount ≥ 0  -- TODO: set correct threshold
  ∧ issuer.max_80d_deduction_self ≥ 0  -- TODO: set correct threshold

/-- Reg 80D(senior): In case of a senior citizen, the deduction limit under section 80D for health insurance premium shall be fifty thousand ... -/
def reg_80d_senior (issuer : Taxpayer) : Prop :=
  issuer.max_80d_deduction_senior ≥ 0  -- TODO: set correct threshold

/-- Combined Regulation 80d gate -/
def reg_80d_eligible (issuer : Taxpayer) : Prop :=
  reg_80d_1 issuer
  ∧ reg_80d_senior issuer

/-! ## Composite Chapter VI-A Part II Gate -/

def chapterVI_A_part2_eligible (issuer : Taxpayer) : Prop :=
  reg_80d_eligible issuer

end Reglib.ITA.Rules
