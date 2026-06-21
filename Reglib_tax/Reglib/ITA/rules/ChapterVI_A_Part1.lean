-- Auto-generated rules file: ChapterVI_A_Part1.lean
-- Chapter VI-A, Part I: DEDUCTION FOR INVESTMENTS

import Reglib.ITA.definitions.Core

namespace Reglib.ITA.Rules

open Reglib.ITA

/-! ## Regulation 80c -/
/-- Reg 80C(1): In computing the total income of an assessee, being an individual or a Hindu undivided family, there shall be deducted, ... -/
def reg_80c_1 (issuer : Taxpayer) : Prop :=
  issuer.investment_80c_amount ≥ 0  -- TODO: set correct threshold
  ∧ issuer.max_80c_deduction ≥ 0  -- TODO: set correct threshold

/-! ## Composite Chapter VI-A Part I Gate -/

def chapterVI_A_part1_eligible (issuer : Taxpayer) : Prop :=
  True

end Reglib.ITA.Rules
