-- Auto-generated rules file: ChapterXVII_Part2.lean
-- Chapter XVII, Part II: TDS ON INTEREST

import Reglib.ITA.definitions.Core

namespace Reglib.ITA.Rules

open Reglib.ITA

/-! ## Regulation 194a -/
/-- Reg 194A(1)(bank): Any person, not being an individual or a Hindu undivided family, responsible for paying to a resident any income by way ... -/
def reg_194a_1_bank (issuer : Taxpayer) : Prop :=
  issuer.interest_income_bank_amount ≥ 0  -- TODO: set correct threshold
  ∧ issuer.interest_threshold_bank ≥ 0  -- TODO: set correct threshold
  ∧ issuer.tds_rate_194a_pct ≥ 0  -- TODO: set correct threshold

/-- Reg 194A(senior): The threshold for TDS on interest from banking companies is fifty thousand rupees for a senior citizen (an individual re... -/
def reg_194a_senior_citizen (issuer : Taxpayer) : Prop :=
  issuer.is_senior_citizen = true
  ∧ issuer.interest_threshold_senior_bank ≥ 0  -- TODO: set correct threshold

/-- Combined Regulation 194a gate -/
def reg_194a_eligible (issuer : Taxpayer) : Prop :=
  reg_194a_1_bank issuer
  ∧ reg_194a_senior_citizen issuer

/-! ## Composite Chapter XVII Part II Gate -/

def chapterXVII_part2_eligible (issuer : Taxpayer) : Prop :=
  reg_194a_eligible issuer

end Reglib.ITA.Rules
