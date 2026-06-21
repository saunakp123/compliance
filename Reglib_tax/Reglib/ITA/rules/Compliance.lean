-- Auto-generated compliance gate file.

import Reglib.ITA.rules.Chapter1_Part1
import Reglib.ITA.rules.Chapter8_Part1
import Reglib.ITA.rules.Chapter12_Part1
import Reglib.ITA.rules.Chapter12_Part2
import Reglib.ITA.rules.ChapterVI_A_Part1
import Reglib.ITA.rules.ChapterXIV_Part1
import Reglib.ITA.rules.ChapterXVII_Part1
import Reglib.ITA.rules.ChapterVI_A_Part2
import Reglib.ITA.rules.ChapterXVII_Part2
import Reglib.ITA.definitions.Core

namespace Reglib.ITA.Rules
open Reglib.ITA

/-! ## Full Compliance Gate -/

def compliance_eligible (issuer : Taxpayer) : Prop :=
  chapter1_part1_eligible issuer
  ∧ chapter8_part1_eligible issuer
  ∧ chapter12_part1_eligible issuer
  ∧ chapter12_part2_eligible issuer
  ∧ chapterVI_A_part1_eligible issuer
  ∧ chapterXIV_part1_eligible issuer
  ∧ chapterXVII_part1_eligible issuer
  ∧ chapterVI_A_part2_eligible issuer
  ∧ chapterXVII_part2_eligible issuer

/-! ## Sample Taxpayer -/

def sample_taxpayer : Taxpayer := {
  advance_tax_paid_amount := 1,
  advance_tax_threshold_pct := 20,
  assessed_tax_amount := 1,
  basic_exemption_limit := 1,
  basic_exemption_limit_senior := 1,
  basic_exemption_limit_super_senior := 1,
  days_in_india_fy := 1,
  dividend_income_amount := 1,
  health_insurance_premium_amount := 1,
  holding_period_months_equity := 12,
  interest_income_bank_amount := 1,
  interest_threshold_bank := 1,
  interest_threshold_senior_bank := 1,
  investment_80c_amount := 1,
  is_new_tax_regime := true,
  is_pan_furnished := true,
  is_resident := true,
  is_return_filing_required := true,
  is_senior_citizen := true,
  is_stt_paid_at_acquisition := true,
  is_stt_paid_on_transfer := true,
  ltcg_exempt_limit := 1,
  ltcg_listed_equity_amount := 1,
  ltcg_tax_rate_pct_x10 := 20,
  max_80c_deduction := 1,
  max_80d_deduction_self := 1,
  max_80d_deduction_senior := 1,
  max_rebate_87a := 1,
  max_rebate_87a_new := 1,
  rebate_87a_new_threshold := 1,
  rebate_87a_threshold := 1,
  stcg_listed_equity_amount := 1,
  stcg_tax_rate_pct := 20,
  tds_rate_194_dividend_pct := 20,
  tds_rate_194a_pct := 20,
  tds_rate_no_pan_pct := 20,
  total_income_amount := 1,
}

/-! ## Smoke-Test Proofs -/


end Reglib.ITA.Rules
