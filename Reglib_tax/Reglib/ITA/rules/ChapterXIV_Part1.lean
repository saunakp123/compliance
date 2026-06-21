-- Auto-generated rules file: ChapterXIV_Part1.lean
-- Chapter XIV, Part I: RETURN FILING OBLIGATION

import Reglib.ITA.definitions.Core

namespace Reglib.ITA.Rules

open Reglib.ITA

/-! ## Regulation 139 -/
/-- Reg 139(1): Every person, being an individual whose total income of the previous year exceeds the maximum amount which is not charge... -/
def reg_139_1_filing (issuer : Taxpayer) : Prop :=
  issuer.total_income_amount ≥ 0  -- TODO: set correct threshold
  ∧ issuer.basic_exemption_limit ≥ 0  -- TODO: set correct threshold
  ∧ issuer.is_return_filing_required = true

/-- Reg 139(1)(senior): For a senior citizen (age 60 to 80 years), the basic exemption limit is three lakh rupees. For a super senior citizen (a... -/
def reg_139_senior_exemption (issuer : Taxpayer) : Prop :=
  issuer.basic_exemption_limit_senior ≥ 0  -- TODO: set correct threshold
  ∧ issuer.basic_exemption_limit_super_senior ≥ 0  -- TODO: set correct threshold

/-- Combined Regulation 139 gate -/
def reg_139_eligible (issuer : Taxpayer) : Prop :=
  reg_139_1_filing issuer
  ∧ reg_139_senior_exemption issuer

/-! ## Composite Chapter XIV Part I Gate -/

def chapterXIV_part1_eligible (issuer : Taxpayer) : Prop :=
  reg_139_eligible issuer

end Reglib.ITA.Rules
