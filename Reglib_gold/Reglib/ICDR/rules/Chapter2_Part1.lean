-- Auto-generated rules file: Chapter2_Part1.lean
-- Chapter II, Part I: ELIGIBILITY REQUIREMENTS

import Reglib.ICDR.definitions.Core

namespace Reglib.ICDR.Rules

open Reglib.ICDR

/-! ## Regulation 4 -/
/-- Reg 4: Unless otherwise provided in this Chapter, an issuer making an initial public offer of specified securities shall satisf... -/
def reg_4 (issuer : Issuer) : Prop :=
  issuer.is_conditions_satisfied_filing_date = true

/-! ## Regulation 5 -/
/-- Reg 5(1)(a): if the issuer, any of its promoters, promoter group or directors or selling shareholders are debarred from accessing the... -/
def reg_5_1_a (issuer : Issuer) : Prop :=
  issuer.is_debarred = false

/-- Reg 5(1)(b): if any of the promoters or directors of the issuer is a promoter or director of any other company which is debarred from... -/
def reg_5_1_b (issuer : Issuer) : Prop :=
  issuer.has_director_of_debarred_company = false

/-- Reg 5(1)(c): if the issuer or any of its promoters or directors is a [wilful defaulter or a fraudulent borrower.]... -/
def reg_5_1_c (issuer : Issuer) : Prop :=
  issuer.is_wilful_defaulter_or_fraudulent_borrower = false

/-- Reg 5(1)(d): if any of its promoters or directors is a fugitive economic offender.... -/
def reg_5_1_d (issuer : Issuer) : Prop :=
  issuer.has_fugitive_economic_offender = false

/-- Reg 5(1)(explanation): The restrictions under (a) and (b) above shall not apply to the persons or entities mentioned therein, who were debarred... -/
def reg_5_1_explanation (issuer : Issuer) : Prop :=
  issuer.is_debarment_period_over = false

/-- Reg 5(2): An issuer shall not be eligible to make an initial public offer if there are any outstanding convertible securities or a... -/
def reg_5_2 (issuer : Issuer) : Prop :=
  issuer.has_outstanding_convertible_securities = false

/-- Reg 5(2)(proviso): outstanding options granted to employees, whether currently an employee or not, pursuant to an employee stock option sch... -/
def reg_5_2_proviso (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 5(2)(proviso)(b): outstanding stock appreciation rights granted to employees pursuant to a stock appreciation right scheme, which are full... -/
def reg_5_2_proviso_2 (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 5(2)(proviso)(c): fully paid-up outstanding convertible securities which are required to be converted on or before the date of filing of t... -/
def reg_5_2_proviso_3 (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Combined Regulation 5 gate -/
def reg_5_eligible (issuer : Issuer) : Prop :=
  reg_5_1_a issuer
  ∧ reg_5_1_b issuer
  ∧ reg_5_1_c issuer
  ∧ reg_5_1_d issuer
  ∧ reg_5_2 issuer

/-! ## Regulation 6 -/
/-- Reg 6(1)(a): it has net tangible assets of at least three crore rupees, calculated on a restated and consolidated basis, in each of t... -/
def reg_6_1_a (issuer : Issuer) : Prop :=
  (issuer.net_tangible_assets_3yr.length = 3 ∧ issuer.net_tangible_assets_3yr.all (· ≥ 1))

/-- Reg 6(1)(b): it has an average operating profit of at least fifteen crore rupees, calculated on a restated and consolidated basis, du... -/
def reg_6_1_b (issuer : Issuer) : Prop :=
  (issuer.operating_profit_avg_crore.length = 3 ∧ issuer.operating_profit_avg_crore.all (· ≥ 1))

/-- Reg 6(1)(c): it has a net worth of at least one crore rupees in each of the preceding three full years (of twelve months each), calcu... -/
def reg_6_1_c (issuer : Issuer) : Prop :=
  (issuer.net_worth_3yr.length = 3 ∧ issuer.net_worth_3yr.all (· ≥ 1))

/-- Reg 6(1)(d): if it has changed its name within the last one year, at least fifty per cent. of the revenue, calculated on a restated a... -/
def reg_6_1_d (issuer : Issuer) : Prop :=
  issuer.revenue_from_new_activity_pct ≥ 0  -- TODO: set correct threshold

/-- Reg 6(1)(a)(proviso): if more than fifty per cent. of the net tangible assets are held in monetary assets, the issuer has utilised or made fir... -/
def reg_6_1_proviso (issuer : Issuer) : Prop :=
  issuer.is_excess_monetary_assets_utilised = true

/-- Reg 6(1)(a)(proviso)(2): the limit of fifty per cent. on monetary assets shall not be applicable in case the initial public offer is made entirel... -/
def reg_6_1_proviso_2 (issuer : Issuer) : Prop :=
  issuer.is_ipo_entirely_ofs = false

/-- Reg 6(2): An issuer not satisfying the condition stipulated in sub-regulation (1) shall be eligible to make an initial public offe... -/
def reg_6_2 (issuer : Issuer) : Prop :=
  issuer.qib_allotment_pct ≥ 0  -- TODO: set correct threshold

/-- Reg 6(3): If an issuer has issued SR equity shares to its promoters/ founders, the said issuer shall be allowed to do an initial p... -/
def reg_6_3 (issuer : Issuer) : Prop :=
  issuer.has_issued_sr_equity_shares = true

/-- Reg 6(3)(i): the issuer shall be intensive in the use of technology, information technology, intellectual property, data analytics, b... -/
def reg_6_3_i (issuer : Issuer) : Prop :=
  issuer.is_technology_intensive = true

/-- Reg 6(3)(ii): the net worth of the SR shareholder, as determined by a Registered Valuer, shall not be more than rupees one thousand cr... -/
def reg_6_3_ii (issuer : Issuer) : Prop :=
  issuer.sr_shareholder_net_worth_max_crore ≥ 0  -- TODO: set correct threshold

/-- Reg 6(3)(ii)(explanation): While determining the individual net worth of the SR shareholder, his investment/ shareholding in other listed companies... -/
def reg_6_3_ii_explanation (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 6(3)(iii): The SR shares were issued only to the promoters/ founders who hold an executive position in the issuer company;... -/
def reg_6_3_iii (issuer : Issuer) : Prop :=
  issuer.sr_shares_issued_to_executive_promoters_only = true

/-- Reg 6(3)(iv): The issue of SR equity shares had been authorized by a special resolution passed at a general meeting of the shareholder... -/
def reg_6_3_iv (issuer : Issuer) : Prop :=
  issuer.has_special_resolution_for_sr_shares = true

/-- Reg 6(3)(iv)(a): the size of issue of SR equity shares,... -/
def reg_6_3_iv_a (issuer : Issuer) : Prop :=
  issuer.sr_issue_size_disclosed = true

/-- Reg 6(3)(iv)(b): ratio of voting rights of SR equity shares vis-à-vis the ordinary shares,... -/
def reg_6_3_iv_b (issuer : Issuer) : Prop :=
  issuer.sr_voting_ratio_disclosed = true

/-- Reg 6(3)(iv)(c): rights as to differential dividends, if any... -/
def reg_6_3_iv_c (issuer : Issuer) : Prop :=
  issuer.sr_differential_dividends_disclosed = true

/-- Reg 6(3)(iv)(d): sunset provisions, which provide for a time frame for the validity of such SR equity shares,... -/
def reg_6_3_iv_d (issuer : Issuer) : Prop :=
  issuer.sr_sunset_provisions_disclosed = true

/-- Reg 6(3)(iv)(e): matters in respect of which the SR equity shares would have the same voting right as that of the ordinary shares,... -/
def reg_6_3_iv_e (issuer : Issuer) : Prop :=
  issuer.sr_equal_voting_matters_disclosed = true

/-- Reg 6(3)(ix): The SR equity shares shall be equivalent to ordinary equity shares in all respects, except for having superior voting ri... -/
def reg_6_3_ix (issuer : Issuer) : Prop :=
  issuer.sr_shares_equivalent_except_voting = true

/-- Reg 6(3)(v): the SR equity shares have been issued prior to the filing of draft red herring prospectus and held for a period of at le... -/
def reg_6_3_v (issuer : Issuer) : Prop :=
  issuer.sr_shares_holding_period_months ≥ 0  -- TODO: set correct threshold

/-- Reg 6(3)(vi): The SR equity shares shall have voting rights in the ratio of a minimum of 2:1 upto a maximum of 10:1 compared to ordina... -/
def reg_6_3_vi (issuer : Issuer) : Prop :=
  issuer.sr_voting_ratio_min ≥ 0  -- TODO: set correct threshold
  ∧ issuer.sr_voting_ratio_max ≥ 0  -- TODO: set correct threshold

/-- Reg 6(3)(vii): The SR equity shares shall have the same face value as the ordinary shares;... -/
def reg_6_3_vii (issuer : Issuer) : Prop :=
  issuer.sr_shares_same_face_value = true

/-- Reg 6(3)(viii): The issuer shall only have one class of SR equity shares;... -/
def reg_6_3_viii (issuer : Issuer) : Prop :=
  issuer.has_only_one_sr_equity_class = true

/-- Combined Regulation 6 gate -/
def reg_6_eligible (issuer : Issuer) : Prop :=
  reg_6_1_a issuer
  ∧ reg_6_1_b issuer
  ∧ reg_6_1_c issuer
  ∧ reg_6_1_d issuer
  ∧ reg_6_2 issuer
  ∧ reg_6_3 issuer
  ∧ reg_6_3_i issuer
  ∧ reg_6_3_ii issuer
  ∧ reg_6_3_iii issuer
  ∧ reg_6_3_iv issuer
  ∧ reg_6_3_iv_a issuer
  ∧ reg_6_3_iv_b issuer
  ∧ reg_6_3_iv_c issuer
  ∧ reg_6_3_iv_d issuer
  ∧ reg_6_3_iv_e issuer
  ∧ reg_6_3_v issuer
  ∧ reg_6_3_vi issuer
  ∧ reg_6_3_vii issuer
  ∧ reg_6_3_viii issuer
  ∧ reg_6_3_ix issuer

/-! ## Regulation 7 -/
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
  issuer.partly_paid_shares_forfeited_or_paid = true

/-- Reg 7(1)(e): it has made firm arrangements of finance through verifiable means towards seventy five per cent. of the stated means of ... -/
def reg_7_1_e (issuer : Issuer) : Prop :=
  issuer.firm_finance_arrangement_pct ≥ 0  -- TODO: set correct threshold

/-- Reg 7(2): The amount for general corporate purposes, as mentioned in objects of the issue in the draft offer document and the offe... -/
def reg_7_2 (issuer : Issuer) : Prop :=
  issuer.gcp_pct_limit ≥ 0  -- TODO: set correct threshold

/-- Reg 7(3): The amount for: (i) general corporate purposes, and (ii) such objects where the issuer company has not identified acquis... -/
def reg_7_3 (issuer : Issuer) : Prop :=
  issuer.gcp_unidentified_objects_pct_limit ≥ 0  -- TODO: set correct threshold

/-- Reg 7(3)(proviso): the amount raised for such objects where the issuer company has not identified acquisition or investment target, as ment... -/
def reg_7_3_proviso (issuer : Issuer) : Prop :=
  issuer.unidentified_objects_pct_limit ≥ 0  -- TODO: set correct threshold

/-- Reg 7(3)(proviso)(2): such limits shall not apply if the proposed acquisition or strategic investment object has been identified and suitable ... -/
def reg_7_3_proviso_2 (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 7(explanation)(III): In case of an issuer formed out of a division of an existing company, the track record of distributable profits of the d... -/
def reg_7_explanation (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 7(explanation)(II)(b)(i): the accounts and the disclosures made are in accordance with the provisions of schedule III of the Companies Act, 2013;... -/
def reg_7_explanation_b_i (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 7(explanation)(II)(b)(ii): the applicable accounting standards have been followed;... -/
def reg_7_explanation_b_ii (issuer : Issuer) : Prop :=
  issuer.has_followed_accounting_standards = true

/-- Reg 7(explanation)(II)(b)(iii): the financial statements present a true and fair view of the firm's accounts;... -/
def reg_7_explanation_b_iii (issuer : Issuer) : Prop :=
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
/-- Reg 8: Only such fully paid-up equity shares may be offered for sale to the public, which have been held by the sellers for a p... -/
def reg_8 (issuer : Issuer) : Prop :=
  issuer.ofs_holding_period_years ≥ 0  -- TODO: set correct threshold

/-- Reg 8(explanation): If the equity shares arising out of the conversion or exchange of the fully paid-up compulsorily convertible securities ... -/
def reg_8_explanation (issuer : Issuer) : Prop :=
  issuer.conversion_completed_before_offer_doc = true

/-- Reg 8(proviso): in case the equity shares received on conversion or exchange of fully paid-up compulsorily convertible securities includ... -/
def reg_8_proviso (issuer : Issuer) : Prop :=
  issuer.combined_convertible_holding_period_months ≥ 0  -- TODO: set correct threshold

/-- Reg 8(proviso)(2): such holding period of one year shall be required to be complied with at the time of filing of the draft offer document.... -/
def reg_8_proviso_2 (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 8(proviso)(3): the requirement of holding equity shares for a period of one year shall not apply:... -/
def reg_8_proviso_3 (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 8(proviso)(3)(a): in case of an offer for sale of a government company or statutory authority or corporation or any special purpose vehicl... -/
def reg_8_proviso_3_a (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 8(proviso)(3)(b): if the equity shares offered for sale were acquired pursuant to any scheme approved by a High Court or approved by a tri... -/
def reg_8_proviso_3_b (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 8(proviso)(3)(c): if the equity shares offered for sale were issued under a bonus issue on securities held for a period of at least one ye... -/
def reg_8_proviso_3_c (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 8(proviso)(3)(c)(i): such specified securities being issued out of free reserves and share premium existing in the books of account as at the... -/
def reg_8_proviso_3_c_i (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 8(proviso)(3)(c)(ii): such equity shares not being issued by utilisation of revaluation reserves or unrealized profits of the issuer.... -/
def reg_8_proviso_3_c_ii (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 8A(a): shares offered for sale to the public by shareholder(s) holding, individually or with persons acting in concert, more th... -/
def reg_8a_a (issuer : Issuer) : Prop :=
  issuer.major_shareholder_ofs_pct_limit ≥ 0  -- TODO: set correct threshold

/-- Reg 8A(b): shares offered for sale to the public by shareholder(s) holding, individually or with persons acting in concert, less th... -/
def reg_8a_b (issuer : Issuer) : Prop :=
  issuer.minority_shareholder_ofs_pct_limit ≥ 0  -- TODO: set correct threshold

/-- Reg 8A(c): for shareholder(s) holding, individually or with persons acting in concert, more than twenty per cent of pre-issue share... -/
def reg_8a_c (issuer : Issuer) : Prop :=
  issuer.major_shareholder_lockin_applicable = false

/-- Reg 8A(explanation): The limits set out in (a) and (b) above shall be calculated with reference to the shareholding as on the date of filing ... -/
def reg_8a_explanation (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Combined Regulation 8 gate -/
def reg_8_eligible (issuer : Issuer) : Prop :=
  reg_8 issuer
  ∧ reg_8a_a issuer
  ∧ reg_8a_b issuer
  ∧ reg_8a_c issuer

/-! ## Composite Chapter II Part I Gate -/

def chapter2_part1_eligible (issuer : Issuer) : Prop :=
  reg_5_eligible issuer
  ∧ reg_6_eligible issuer
  ∧ reg_7_eligible issuer
  ∧ reg_8_eligible issuer

end Reglib.ICDR.Rules
