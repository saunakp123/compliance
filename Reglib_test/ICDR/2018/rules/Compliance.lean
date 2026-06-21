-- Auto-generated compliance gate file.

import Reglib.ICDR.rules.Chapter2_Part1
import Reglib.ICDR.rules.Chapter2_Part2
import Reglib.ICDR.rules.Chapter2_Part3
import Reglib.ICDR.rules.Chapter2_Part4
import Reglib.ICDR.rules.Chapter2_Part5
import Reglib.ICDR.definitions.Core

namespace Reglib.ICDR.Rules
open Reglib.ICDR

/-! ## Full IPO Compliance Gate -/

def ipo_eligible (issuer : Issuer) : Prop :=
  chapter2_part1_eligible issuer
  ∧ chapter2_part2_eligible issuer
  ∧ chapter2_part3_eligible issuer
  ∧ chapter2_part4_eligible issuer
  ∧ chapter2_part5_eligible issuer

/-! ## Sample Compliant Issuer -/

def sample_compliant_issuer : Issuer := {
  assets_cover_principal_amount := true,
  assets_free_from_encumbrance := true,
  convertible_debt_instruments_value_exceeds := 1,
  finance_arrangements_pct := 20,
  formula_based_warrants_upfront_contribution_pct := 20,
  fully_convertible_debt_period_months := 12,
  general_corporate_purpose_pct_limit := 20,
  has_appointed_debenture_trustee := true,
  has_credit_rating_from_one_agency := true,
  has_debarred_promoter_or_director := false,
  has_depository_agreement := true,
  has_non_associate_lead_manager := true,
  has_positive_consent_from_holders := true,
  has_second_or_pari_passu_charge_consent := true,
  holding_period_months := 12,
  holding_period_years := 1,
  ipo_book_building_pct := 20,
  is_debarment_period_over := true,
  is_debarred := false,
  is_eligible_for_convertible_debt_instruments := true,
  is_fugitive_economic_offender := false,
  is_lock_in_recorded_by_depository := true,
  is_over_20_pct_pre_issue_shareholder := true,
  is_partly_paidup_shares_forfeited_or_fully_paid_up := true,
  is_redeemed_within_month := true,
  is_sr_shares_issued_to_executive_promoters_only := true,
  is_wilful_defaulter_or_fraudulent_borrower := false,
  issuer_conversion_from_partnership_or_llp := true,
  monetary_assets_pct_limit := 20,
  net_tangible_assets_3yr := [10, 12, 15],
  net_worth_3yr := [10, 12, 15],
  no_default_payment_more_than_six_months := true,
  non_promoter_lock_in_period_months := 12,
  ofs_holding_period_months_reg16 := 12,
  ofs_holding_period_months_reg17 := 12,
  ofs_holding_period_years := 1,
  ofs_lock_in_period_years := 1,
  operating_profit_last_3yr := [10, 12, 15],
  promoter_compliance_deadline_days_prior_issue_opening := 1,
  promoter_contribution_lock_in_months := 12,
  promoter_contribution_pct := 20,
  promoter_contribution_pct_project_cost := 20,
  promoter_contribution_price_lower_limit := 1,
  promoter_lock_in_period_months := 12,
  promoter_min_contribution_pct := 20,
  promoter_min_post_issue_capital_pct := 20,
  promoter_securities_eligibility_period_months := 12,
  promoter_shares_dematerialised := true,
  promoters_contribution_escrow_account := true,
  promoters_of_converted_entity := [10, 12, 15],
  revenue_from_new_activity_pct := 20,
  shareholder_offer_limit_pct := 20,
  small_shareholder_offer_limit_pct := 20,
  sr_equity_share_holding_period_months := 12,
  sr_shareholder_net_worth_max_crore := 10,
  unspecified_objects_pct_limit := 20,
  untargeted_acquisition_investment_pct_limit := 20,
  warrant_consideration_upfront_pct := 20,
  warrant_exercise_period_months := 12,
  warrant_tenure_months := 12,
  issue_type := IssueType.initialPublicOffer
  specified_securities_type := SpecifiedSecurities.equityShares
  promoters := [
    { named_in_offer_doc := true
      has_control := true
      board_acts_on_instructions := false
      acting_only_professionally := false
      holding_pct := 25
      is_debarred := false
      is_wilful_defaulter_or_fraudulent := false
      is_fugitive_economic_offender := false }
  ]
  convertible_security := ConvertibleSecurity.convertibleIntoEquityShares
}

/-! ## Smoke-Test Proofs -/

theorem sample_passes_reg5 :
    reg_5_eligible sample_compliant_issuer := by
  unfold reg_5_eligible reg_5_1_a reg_5_1_b reg_5_1_c reg_5_1_d reg_5_2
  simp [sample_compliant_issuer, List.all]

end Reglib.ICDR.Rules
