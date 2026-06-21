-- Auto-generated rules file: Chapter2_Part1.lean
-- Chapter II, Part I: ELIGIBILITY REQUIREMENTS

import Reglib.ICDR.definitions.Core

namespace Reglib.ICDR.Rules

open Reglib.ICDR

/-! ## Regulation 4 -/
/-- Reg 4: Unless otherwise provided in this Chapter, an issuer making an initial public offer of specified securities shall satisf... -/
def reg_4 (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-! ## Regulation 5 -/
/-- Reg 5(1)(a): if the issuer, any of its promoters, promoter group or directors or selling shareholders are debarred from accessing the... -/
def reg_5_1_a (issuer : Issuer) : Prop :=
  issuer.is_debarred = false

/-- Reg 5(1)(b): if any of the promoters or directors of the issuer is a promoter or director of any other company which is debarred from... -/
def reg_5_1_b (issuer : Issuer) : Prop :=
  issuer.has_debarred_promoter_or_director = false

/-- Reg 5(1)(c): if the issuer or any of its promoters or directors is a [wilful defaulter or a fraudulent borrower.]... -/
def reg_5_1_c (issuer : Issuer) : Prop :=
  issuer.is_wilful_defaulter_or_fraudulent_borrower = false

/-- Reg 5(1)(d): if any of its promoters or directors is a fugitive economic offender.... -/
def reg_5_1_d (issuer : Issuer) : Prop :=
  issuer.is_fugitive_economic_offender = false

/-- Reg 5(2): An issuer shall not be eligible to make an initial public offer if there are any outstanding convertible securities or a... -/
def reg_5_2 (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 5(explanation): The restrictions under (a) and (b) above shall not apply to the persons or entities mentioned therein, who were debarred... -/
def reg_5_explanation (issuer : Issuer) : Prop :=
  issuer.is_debarment_period_over = false

/-- Reg 5(proviso)(2): these regulations shall not apply to issue of securities under clause (b), (d) and (e) of sub-regulation (1) of regulati... -/
def reg_5_proviso_2 (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Combined Regulation 5 gate -/
def reg_5_eligible (issuer : Issuer) : Prop :=
  reg_5_1_a issuer
  ∧ reg_5_1_b issuer
  ∧ reg_5_1_c issuer
  ∧ reg_5_1_d issuer

/-! ## Regulation 6 -/
/-- Reg 6(1)(a): it has net tangible assets of at least three crore rupees, calculated on a restated and consolidated basis, in each of t... -/
def reg_6_1_a (issuer : Issuer) : Prop :=
  (issuer.net_tangible_assets_3yr.length = 3 ∧ issuer.net_tangible_assets_3yr.all (· ≥ 1))
  ∧ issuer.monetary_assets_pct_limit ≥ 0  -- TODO: set correct threshold

/-- Reg 6(1)(b): it has an average operating profit of at least fifteen crore rupees, calculated on a restated and consolidated basis, du... -/
def reg_6_1_b (issuer : Issuer) : Prop :=
  (issuer.operating_profit_last_3yr.length = 3 ∧ issuer.operating_profit_last_3yr.all (· ≥ 1))

/-- Reg 6(1)(c): it has a net worth of at least one crore rupees in each of the preceding three full years (of twelve months each), calcu... -/
def reg_6_1_c (issuer : Issuer) : Prop :=
  (issuer.net_worth_3yr.length = 3 ∧ issuer.net_worth_3yr.all (· ≥ 1))

/-- Reg 6(1)(d): if it has changed its name within the last one year, at least fifty per cent. of the revenue, calculated on a restated a... -/
def reg_6_1_d (issuer : Issuer) : Prop :=
  issuer.revenue_from_new_activity_pct ≥ 0  -- TODO: set correct threshold

/-- Reg 6(2): An issuer not satisfying the condition stipulated in sub-regulation (1) shall be eligible to make an initial public offe... -/
def reg_6_2 (issuer : Issuer) : Prop :=
  issuer.ipo_book_building_pct ≥ 0  -- TODO: set correct threshold

/-- Reg 6(3): If an issuer has issued SR equity shares to its promoters/ founders, the said issuer shall be allowed to do an initial p... -/
def reg_6_3 (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 6(3)(i): the issuer shall be intensive in the use of technology, information technology, intellectual property, data analytics, b... -/
def reg_6_3_i (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 6(3)(ii): the net worth of the SR shareholder, as determined by a Registered Valuer, shall not be more than rupees one thousand cr... -/
def reg_6_3_ii (issuer : Issuer) : Prop :=
  issuer.sr_shareholder_net_worth_max_crore ≥ 0  -- TODO: set correct threshold

/-- Reg 6(3)(iii): The SR shares were issued only to the promoters/ founders who hold an executive position in the issuer company;... -/
def reg_6_3_iii (issuer : Issuer) : Prop :=
  issuer.is_sr_shares_issued_to_executive_promoters_only = true

/-- Reg 6(3)(iv): The issue of SR equity shares had been authorized by a special resolution passed at a general meeting of the shareholder... -/
def reg_6_3_iv (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 6(3)(iv)(a): the size of issue of SR equity shares, ratio of voting rights of SR equity shares vis-à-vis the ordinary shares... -/
def reg_6_3_iv_a (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 6(3)(iv)(b): ratio of voting rights of SR equity shares vis-à-vis the ordinary shares,... -/
def reg_6_3_iv_b (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 6(v): The SR equity shares have been held for a period of atleast 6 months prior to the filing of the red herring prospectus;... -/
def reg_6_v (issuer : Issuer) : Prop :=
  issuer.sr_equity_share_holding_period_months ≥ 0  -- TODO: set correct threshold

/-- Combined Regulation 6 gate -/
def reg_6_eligible (issuer : Issuer) : Prop :=
  reg_6_1_a issuer
  ∧ reg_6_1_b issuer
  ∧ reg_6_1_c issuer
  ∧ reg_6_1_d issuer
  ∧ reg_6_2 issuer
  ∧ reg_6_3_ii issuer
  ∧ reg_6_3_iii issuer
  ∧ reg_6_v issuer

/-! ## Regulation 7 -/
/-- Reg 7(1): An issuer making an initial public offer shall ensure that it has made an application to one or more stock exchanges to ... -/
def reg_7_1 (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 7(1)(a): it has made an application to one or more stock exchanges to seek an in-principle approval for listing of its specified ... -/
def reg_7_1_a (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 7(1)(b): it has entered into an agreement with a depository for dematerialisation of the specified securities already issued and ... -/
def reg_7_1_b (issuer : Issuer) : Prop :=
  issuer.has_depository_agreement = true

/-- Reg 7(1)(c): all its specified securities held by the promoters are in dematerialised form prior to filing of the offer document;... -/
def reg_7_1_c (issuer : Issuer) : Prop :=
  issuer.promoter_shares_dematerialised = true

/-- Reg 7(1)(d): all its existing partly paid-up equity shares have either been fully paid-up or have been forfeited;... -/
def reg_7_1_d (issuer : Issuer) : Prop :=
  issuer.is_partly_paidup_shares_forfeited_or_fully_paid_up = true

/-- Reg 7(1)(e): it has made firm arrangements of finance through verifiable means towards seventy five per cent. of the stated means of ... -/
def reg_7_1_e (issuer : Issuer) : Prop :=
  issuer.finance_arrangements_pct ≥ 0  -- TODO: set correct threshold

/-- Reg 7(2): The amount for general corporate purposes, as mentioned in objects of the issue in the draft offer document and the offe... -/
def reg_7_2 (issuer : Issuer) : Prop :=
  issuer.general_corporate_purpose_pct_limit ≥ 0  -- TODO: set correct threshold

/-- Reg 7(3): (i) general corporate purposes, and (ii) such objects where the issuer company has not identified acquisition or investm... -/
def reg_7_3 (issuer : Issuer) : Prop :=
  issuer.untargeted_acquisition_investment_pct_limit ≥ 0  -- TODO: set correct threshold

/-- Reg 7(3)(proviso): the amount raised for such objects where the issuer company has not identified acquisition or investment target, as ment... -/
def reg_7_3_proviso (issuer : Issuer) : Prop :=
  issuer.unspecified_objects_pct_limit ≥ 0  -- TODO: set correct threshold

/-- Reg 7(3)(proviso)(2): Provided further that such limits shall not apply if the proposed acquisition or strategic investment object has been id... -/
def reg_7_3_proviso_2 (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 7(3)(proviso)(2)(i): such specified securities being issued out of free reserves and share premium existing in the books of account as at the... -/
def reg_7_3_proviso_2_i (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 7(3)(proviso)(2)(i)(a): in case of an offer for sale of a government company or statutory authority or corporation or any special purpose vehicl... -/
def reg_7_3_proviso_2_i_a (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 7(3)(proviso)(2)(i)(b): if the equity shares offered for sale were acquired pursuant to any scheme approved by a High Court or approved by a tri... -/
def reg_7_3_proviso_2_i_b (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 7(3)(proviso)(2)(i)(c)(ii): such equity shares not being issued by utilisation of revaluation reserves or unrealized profits of the issuer.... -/
def reg_7_3_proviso_2_i_c_ii (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 7(explanation): (II)(a) adequate disclosures are made in the financial statements as required to be made by the issuer as per schedule I... -/
def reg_7_explanation (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Combined Regulation 7 gate -/
def reg_7_eligible (issuer : Issuer) : Prop :=
  reg_7_1_b issuer
  ∧ reg_7_1_c issuer
  ∧ reg_7_1_d issuer
  ∧ reg_7_1_e issuer
  ∧ reg_7_2 issuer
  ∧ reg_7_3 issuer

/-! ## Regulation 8 -/
/-- Reg 8(explanation): If the equity shares arising out of the conversion or exchange of the fully paid-up compulsorily convertible securities ... -/
def reg_8_explanation (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 8a(a): shares offered for sale to the public by shareholder(s) holding, individually or with persons acting in concert, more th... -/
def reg_8a_a (issuer : Issuer) : Prop :=
  issuer.shareholder_offer_limit_pct ≥ 0  -- TODO: set correct threshold

/-- Reg 8a(b): shares offered for sale to the public by shareholder(s) holding, individually or with persons acting in concert, less th... -/
def reg_8a_b (issuer : Issuer) : Prop :=
  issuer.small_shareholder_offer_limit_pct ≥ 0  -- TODO: set correct threshold

/-- Reg 8a(c): for shareholder(s) holding, individually or with persons acting in concert, more than twenty per cent of pre-issue share... -/
def reg_8a_c (issuer : Issuer) : Prop :=
  issuer.is_over_20_pct_pre_issue_shareholder = true

/-- Combined Regulation 8 gate -/
def reg_8_eligible (issuer : Issuer) : Prop :=
  reg_8a_a issuer
  ∧ reg_8a_b issuer
  ∧ reg_8a_c issuer

/-! ## Composite Chapter II Part I Gate -/

def chapter2_part1_eligible (issuer : Issuer) : Prop :=
  reg_5_eligible issuer
  ∧ reg_6_eligible issuer
  ∧ reg_7_eligible issuer
  ∧ reg_8_eligible issuer

end Reglib.ICDR.Rules
