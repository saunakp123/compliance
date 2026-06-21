-- Auto-generated rules file: ChapterXVII_Part1.lean
-- Chapter XVII, Part I: TDS ON DIVIDENDS

import Reglib.ITA.definitions.Core

namespace Reglib.ITA.Rules

open Reglib.ITA

/-! ## Regulation 194 -/
/-- Reg 194(1): Any person responsible for paying to a resident any income by way of dividends shall, at the time of payment thereof, de... -/
def reg_194_1 (issuer : Taxpayer) : Prop :=
  issuer.tds_rate_194_dividend_pct ≥ 0  -- TODO: set correct threshold
  ∧ issuer.dividend_income_amount ≥ 0  -- TODO: set correct threshold

/-- Reg 194(PAN): Where the recipient does not furnish PAN to the payer, TDS shall be deducted at the higher of the rate specified in the ... -/
def reg_194_pan_check (issuer : Taxpayer) : Prop :=
  issuer.is_pan_furnished = true
  ∧ issuer.tds_rate_no_pan_pct ≥ 0  -- TODO: set correct threshold

/-- Combined Regulation 194 gate -/
def reg_194_eligible (issuer : Taxpayer) : Prop :=
  reg_194_1 issuer
  ∧ reg_194_pan_check issuer

/-! ## Regulation 234b -/
/-- Reg 234B: Where, in any financial year, an assessee who is liable to pay advance tax has failed to pay such tax or where the advan... -/
def reg_234b_advance_tax (issuer : Taxpayer) : Prop :=
  issuer.advance_tax_paid_amount ≥ 0  -- TODO: set correct threshold
  ∧ issuer.assessed_tax_amount ≥ 0  -- TODO: set correct threshold
  ∧ issuer.advance_tax_threshold_pct ≥ 0  -- TODO: set correct threshold

/-! ## Composite Chapter XVII Part I Gate -/

def chapterXVII_part1_eligible (issuer : Taxpayer) : Prop :=
  reg_194_eligible issuer

end Reglib.ITA.Rules
