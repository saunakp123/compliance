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

def compliance_eligible (issuer : Issuer) : Prop :=
  chapter2_part1_eligible issuer
  ∧ chapter2_part2_eligible issuer
  ∧ chapter2_part3_eligible issuer
  ∧ chapter2_part4_eligible issuer
  ∧ chapter2_part5_eligible issuer

/-! ## Sample Compliant Issuer -/

def sample_compliant_issuer : Issuer := {
  alternative_contributor_max_pct := 20,
  assets_free_from_encumbrance := true,
  assets_sufficient_for_principal := true,
  capex_lockin_years := 1,
  combined_convertible_holding_period_months := 12,
  conversion_completed_before_offer_doc := true,
  convertible_debt_exceeds_ten_crore := true,
  eligible_via_court_approved_scheme := true,
  excess_holding_capex_lockin_years := 1,
  excess_holding_lockin_months := 12,
  firm_finance_arrangement_pct := 20,
  fully_convertible_debt_period_months := 12,
  gcp_pct_limit := 20,
  gcp_unidentified_objects_pct_limit := 20,
  has_consent_for_second_charge := true,
  has_credit_rating := true,
  has_debenture_trustee := true,
  has_depository_agreement := true,
  has_director_of_debarred_company := false,
  has_followed_accounting_standards := true,
  has_fugitive_economic_offender := false,
  has_identifiable_promoter := true,
  has_issued_sr_equity_shares := true,
  has_lead_manager_agreement := true,
  has_non_associate_lead_manager := true,
  has_only_one_sr_equity_class := true,
  has_outstanding_convertible_securities := false,
  has_positive_consent_for_conversion := true,
  has_registered_lead_manager := true,
  has_special_resolution_for_sr_shares := true,
  is_conditions_satisfied_filing_date := true,
  is_debarment_period_over := true,
  is_debarred := false,
  is_excess_monetary_assets_utilised := true,
  is_ipo_entirely_ofs := true,
  is_technology_intensive := true,
  is_wilful_defaulter_or_fraudulent_borrower := false,
  lockin_recorded_by_depository := true,
  major_shareholder_lockin_applicable := true,
  major_shareholder_ofs_pct_limit := 20,
  min_contribution_lockin_months := 12,
  minority_shareholder_ofs_pct_limit := 20,
  net_tangible_assets_3yr := [10, 12, 15],
  net_worth_3yr := [10, 12, 15],
  no_cdi_for_promoter_group_financing := true,
  no_debt_default_more_than_six_months := true,
  non_promoter_lockin_months := 12,
  ofs_holding_period_years := 1,
  operating_profit_avg_crore := [10, 12, 15],
  partly_paid_lockin_years := 1,
  partly_paid_shares_forfeited_or_paid := true,
  pledged_securities_ineligible := false,
  price_comparison_applies := true,
  promoter_contribution_not_below_weighted_avg := true,
  promoter_contribution_pct := 20,
  promoter_contribution_pct_issue_size := 20,
  promoter_contribution_pct_project_cost := 20,
  promoter_initial_contribution_crore := 10,
  promoter_lockin_pledgeable := true,
  promoter_min_holding_pct := 20,
  promoter_shares_dematerialised := true,
  qib_allotment_pct := 20,
  redeems_per_offer_doc := true,
  redeems_unconverted_within_one_month := true,
  revenue_from_new_activity_pct := 20,
  sr_differential_dividends_disclosed := true,
  sr_equal_voting_matters_disclosed := true,
  sr_issue_size_disclosed := true,
  sr_shareholder_net_worth_max_crore := 10,
  sr_shares_equivalent_except_voting := true,
  sr_shares_holding_period_months := 12,
  sr_shares_issued_to_executive_promoters_only := true,
  sr_shares_lockin_until_conversion := true,
  sr_shares_same_face_value := true,
  sr_sunset_provisions_disclosed := true,
  sr_voting_ratio_disclosed := true,
  sr_voting_ratio_max := 20,
  sr_voting_ratio_min := 20,
  unidentified_objects_pct_limit := 20,
  vcf_aif_lockin_months := 12,
  warrant_exercise_period_months := 12,
  warrant_tenure_months := 12,
  warrant_upfront_consideration_pct := 20,
  issue_type := IssueType.initialPublicOffer,
  specified_securities_type := SpecifiedSecurities.equityShares,
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
}

/-! ## Smoke-Test Proofs -/

theorem sample_passes_reg5 :
    reg_5_eligible sample_compliant_issuer := by
  unfold reg_5_eligible reg_5_1_a reg_5_1_b reg_5_1_c reg_5_1_d reg_5_2
  simp [sample_compliant_issuer]

end Reglib.ICDR.Rules
