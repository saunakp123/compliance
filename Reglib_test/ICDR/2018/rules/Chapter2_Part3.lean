-- Auto-generated rules file: Chapter2_Part3.lean
-- Chapter II, Part III: PROMOTERS’ CONTRIBUTION

import Reglib.ICDR.definitions.Core

namespace Reglib.ICDR.Rules

open Reglib.ICDR

/-! ## Regulation 14 -/
/-- Reg 14(1): The promoters of the issuer shall hold at least twenty per cent. of the post-issue capital.... -/
def reg_14_1 (issuer : Issuer) : Prop :=
  issuer.promoter_min_post_issue_capital_pct ≥ 0  -- TODO: set correct threshold

/-- Reg 14(2): The minimum promoters’ contribution shall be as follows:... -/
def reg_14_2 (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 14(3): The promoters shall satisfy the requirements of this regulation at least one day prior to the date of opening of the iss... -/
def reg_14_3 (issuer : Issuer) : Prop :=
  issuer.promoter_compliance_deadline_days_prior_issue_opening ≥ 0  -- TODO: set correct threshold

/-- Reg 14(4): In case the promoters have to subscribe to equity shares or convertible securities towards minimum promoters’ contributi... -/
def reg_14_4 (issuer : Issuer) : Prop :=
  issuer.promoters_contribution_escrow_account = true

/-- Reg 14(a): the promoters shall contribute twenty per cent. as stipulated in sub-regulation (1), as the case may be, either by way o... -/
def reg_14_a (issuer : Issuer) : Prop :=
  issuer.promoter_min_contribution_pct ≥ 0  -- TODO: set correct threshold

/-- Reg 14(b): in case of any issue of convertible securities which are convertible or exchangeable on different dates and if the promo... -/
def reg_14_b (issuer : Issuer) : Prop :=
  issuer.promoter_contribution_price_lower_limit ≥ 0  -- TODO: set correct threshold

/-- Reg 14(c): subject to the provisions of clause (a) and (b) above, in case of an initial public offer of convertible debt instrument... -/
def reg_14_c (issuer : Issuer) : Prop :=
  issuer.promoter_contribution_pct_project_cost ≥ 0  -- TODO: set correct threshold

/-- Combined Regulation 14 gate -/
def reg_14_eligible (issuer : Issuer) : Prop :=
  reg_14_1 issuer
  ∧ reg_14_a issuer
  ∧ reg_14_b issuer
  ∧ reg_14_c issuer
  ∧ reg_14_3 issuer
  ∧ reg_14_4 issuer

/-! ## Regulation 15 -/
/-- Reg 15(1)(a): specified securities acquired during the preceding three years, if these are: (i) acquired for consideration other than ... -/
def reg_15_1_a (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 15(1)(a)(c): specified securities allotted to [the promoters and alternative investment funds or foreign venture capital investors or... -/
def reg_15_1_a_c (issuer : Issuer) : Prop :=
  issuer.issuer_conversion_from_partnership_or_llp = true
  ∧ (issuer.promoters_of_converted_entity.length = 3 ∧ issuer.promoters_of_converted_entity.all (· ≥ 1))

/-- Reg 15(1)(a)(i): acquired for consideration other than cash and revaluation of assets or capitalisation of intangible assets is involved ... -/
def reg_15_1_a_i (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 15(1)(a)(ii): resulting from a bonus issue by utilisation of revaluation reserves or unrealised profits of the issuer or from bonus is... -/
def reg_15_1_a_ii (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 15(1)(a)(iv)(explanation): [Explanation.- For the purpose of this sub-regulation, it is clarified that the price per share for determining securiti... -/
def reg_15_1_a_iv_explanation (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 15(1)(a)(iv)(proviso): provided that full disclosures of the terms of conversion or exchange are made in such draft offer document;... -/
def reg_15_1_a_iv_proviso (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 15(1)(a)(iv)(proviso): specified securities, allotted to the promoters against the capital existing in such firms for a period of more than one... -/
def reg_15_1_a_iv_proviso (issuer : Issuer) : Prop :=
  issuer.promoter_securities_eligibility_period_months ≥ 0  -- TODO: set correct threshold

/-- Reg 15(1)(b): to equity shares arising from the conversion or exchange of fully paid-up compulsorily convertible securities, including... -/
def reg_15_1_b (issuer : Issuer) : Prop :=
  issuer.holding_period_years ≥ 0  -- TODO: set correct threshold

/-- Reg 15(2): Specified securities referred to in clauses (a) and (c) of sub-regulation (1) shall be eligible for the computation of p... -/
def reg_15_2 (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Combined Regulation 15 gate -/
def reg_15_eligible (issuer : Issuer) : Prop :=
  reg_15_1_b issuer
  ∧ reg_15_1_a_c issuer

/-! ## Composite Chapter II Part III Gate -/

def chapter2_part3_eligible (issuer : Issuer) : Prop :=
  reg_14_eligible issuer
  ∧ reg_15_eligible issuer

end Reglib.ICDR.Rules
