-- Reglib_tax/Reglib/ITA/AdversarialRules.lean
-- Adversarial predicates for the LLM-judge vs. Lean proof experiment.
--
-- Framing (ACL): LLM judge reliability at rule-boundary conditions —
-- natural-language interpretation of the same structured facts a typed
-- Lean predicate settles deterministically.
--
-- Statute year: FY 2024–25 / Finance Act 2024 thresholds (see
-- taxpayer_fields.json and generate_adversarial_taxpayers.py).
--
-- Each case has a positive predicate and its classical negation so the
-- Lean pipeline yields an explicit True/False verdict (symmetric with
-- the LLM judge), rather than "proved / unproved".

import Reglib.ITA.definitions.Core

namespace Reglib.ITA.Rules

open Reglib.ITA

/-!
## adv_01 — Section 112A LTCG taxability at the exemption boundary
-/

/-- LTCG on listed equity is taxable under §112A (amount exceeds exemption). -/
def adv_112a_taxable (t : Taxpayer) : Prop :=
  t.ltcg_listed_equity_amount > t.ltcg_exempt_limit

def adv_112a_taxable_negated (t : Taxpayer) : Prop :=
  t.ltcg_listed_equity_amount ≤ t.ltcg_exempt_limit

/-!
## adv_02 — Section 87A rebate eligibility (old regime)
-/

def adv_87a_rebate_eligible (t : Taxpayer) : Prop :=
  t.is_new_tax_regime = false ∧ t.total_income_amount ≤ t.rebate_87a_threshold

def adv_87a_rebate_eligible_negated (t : Taxpayer) : Prop :=
  t.is_new_tax_regime = true ∨ t.total_income_amount > t.rebate_87a_threshold

/-!
## adv_03 — Section 111A concessional rate (STT precondition)
-/

def adv_111a_concessional (t : Taxpayer) : Prop :=
  t.is_stt_paid_on_transfer = true ∧ t.stcg_listed_equity_amount > 0

def adv_111a_concessional_negated (t : Taxpayer) : Prop :=
  t.is_stt_paid_on_transfer = false ∨ t.stcg_listed_equity_amount = 0

/-!
## adv_04 — Section 80D full claimed-premium deductibility
-/

def adv_80d_full_deduction (t : Taxpayer) : Prop :=
  (t.is_senior_citizen = true ∧
    t.health_insurance_premium_amount ≤ t.max_80d_deduction_senior) ∨
  (t.is_senior_citizen = false ∧
    t.health_insurance_premium_amount ≤ t.max_80d_deduction_self)

def adv_80d_full_deduction_negated (t : Taxpayer) : Prop :=
  (t.is_senior_citizen = true ∧
    t.health_insurance_premium_amount > t.max_80d_deduction_senior) ∨
  (t.is_senior_citizen = false ∧
    t.health_insurance_premium_amount > t.max_80d_deduction_self)

/-!
## adv_05 — Section 6(1) residency at the day-count boundary
-/

def adv_6_1_resident (t : Taxpayer) : Prop :=
  t.days_in_india_fy ≥ 182

def adv_6_1_resident_negated (t : Taxpayer) : Prop :=
  t.days_in_india_fy < 182

/-!
## adv_06 / adv_14_tds — Section 194 TDS applicability (exceeds ₹5,000)
-/

/-- §194 TDS applies when dividend exceeds the FY 2024–25 threshold. -/
def adv_194_tds_applies (t : Taxpayer) : Prop :=
  t.dividend_income_amount > t.dividend_tds_threshold

def adv_194_tds_applies_negated (t : Taxpayer) : Prop :=
  t.dividend_income_amount ≤ t.dividend_tds_threshold

/-!
## adv_07 / adv_15_tds — Section 194A TDS applicability (age-gated threshold)
-/

/-- §194A TDS applies under the age-gated bank-interest threshold. -/
def adv_194a_tds_applies (t : Taxpayer) : Prop :=
  (t.is_senior_citizen = true ∧
    t.interest_income_bank_amount > t.interest_threshold_senior_bank) ∨
  (t.is_senior_citizen = false ∧
    t.interest_income_bank_amount > t.interest_threshold_bank)

def adv_194a_tds_applies_negated (t : Taxpayer) : Prop :=
  (t.is_senior_citizen = true ∧
    t.interest_income_bank_amount ≤ t.interest_threshold_senior_bank) ∨
  (t.is_senior_citizen = false ∧
    t.interest_income_bank_amount ≤ t.interest_threshold_bank)

/-!
## adv_08 — Section 139(1) filing obligation (exceeds basic exemption)
-/

def adv_139_1_filing_required (t : Taxpayer) : Prop :=
  t.total_income_amount > t.basic_exemption_limit

def adv_139_1_filing_required_negated (t : Taxpayer) : Prop :=
  t.total_income_amount ≤ t.basic_exemption_limit

/-!
## adv_09 — Section 80C full investment deductible (cap check, old regime)
-/

/-- Full invested amount is deductible under §80C (old regime ∧ within cap). -/
def adv_80c_full_investment_deductible (t : Taxpayer) : Prop :=
  t.is_new_tax_regime = false ∧
    t.investment_80c_amount ≤ t.max_80c_deduction

def adv_80c_full_investment_deductible_negated (t : Taxpayer) : Prop :=
  t.is_new_tax_regime = true ∨
    t.investment_80c_amount > t.max_80c_deduction

/-!
## adv_10 — Section 234B interest (advance tax < 90% of assessed)
-/

/-- §234B interest applies when advance tax is strictly below 90% of assessed. -/
def adv_234b_interest_applies (t : Taxpayer) : Prop :=
  t.advance_tax_paid_amount * 100 < t.assessed_tax_amount * t.advance_tax_threshold_pct

def adv_234b_interest_applies_negated (t : Taxpayer) : Prop :=
  t.advance_tax_paid_amount * 100 ≥ t.assessed_tax_amount * t.advance_tax_threshold_pct

/-!
## adv_11 — Holding period edge: exactly 12 months ⇒ short-term / §111A
-/

/-- §111A short-term concessional applies at holding ≤ 12 months with STT. -/
def adv_111a_short_term_at_12m (t : Taxpayer) : Prop :=
  t.holding_period_months_equity ≤ 12 ∧
    t.is_stt_paid_on_transfer = true ∧
    t.stcg_listed_equity_amount > 0

def adv_111a_short_term_at_12m_negated (t : Taxpayer) : Prop :=
  t.holding_period_months_equity > 12 ∨
    t.is_stt_paid_on_transfer = false ∨
    t.stcg_listed_equity_amount = 0

/-!
## adv_12 — Section 80C deduction allowed (regime precondition)
-/

/-- §80C deduction is allowed (old regime only). -/
def adv_80c_deduction_allowed (t : Taxpayer) : Prop :=
  t.is_new_tax_regime = false ∧ t.investment_80c_amount > 0

def adv_80c_deduction_allowed_negated (t : Taxpayer) : Prop :=
  t.is_new_tax_regime = true ∨ t.investment_80c_amount = 0

/-!
## adv_13 — Section 87A rebate under new regime
-/

def adv_87a_new_regime_eligible (t : Taxpayer) : Prop :=
  t.is_new_tax_regime = true ∧
    t.total_income_amount ≤ t.rebate_87a_new_threshold

def adv_87a_new_regime_eligible_negated (t : Taxpayer) : Prop :=
  t.is_new_tax_regime = false ∨
    t.total_income_amount > t.rebate_87a_new_threshold

/-!
## adv_14_rate / adv_15_rate — Section 206AA elevated 20% rate (no PAN)
-/

/-- §194 / 206AA: elevated 20% TDS rate applies when PAN is not furnished. -/
def adv_194_rate_20pct (t : Taxpayer) : Prop :=
  t.is_pan_furnished = false

def adv_194_rate_20pct_negated (t : Taxpayer) : Prop :=
  t.is_pan_furnished = true

/-- §194A / 206AA: elevated 20% TDS rate applies when PAN is not furnished. -/
def adv_194a_rate_20pct (t : Taxpayer) : Prop :=
  t.is_pan_furnished = false

def adv_194a_rate_20pct_negated (t : Taxpayer) : Prop :=
  t.is_pan_furnished = true

end Reglib.ITA.Rules
