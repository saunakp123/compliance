-- Auto-generated rules file: Chapter2_Part2.lean
-- Chapter II, Part II: ISSUE OF CONVERTIBLE DEBT INSTRUMENTS AND WARRANTS

import Reglib.ICDR.definitions.Core

namespace Reglib.ICDR.Rules

open Reglib.ICDR

/-! ## Regulation 9 -/
/-- Reg 9: An issuer shall be eligible to make an initial public offer of convertible debt instruments even without making a prior ... -/
def reg_9 (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 9(proviso): it is not in default of payment of interest or repayment of principal amount in respect of debt instruments issued by it... -/
def reg_9_proviso (issuer : Issuer) : Prop :=
  issuer.no_default_payment_more_than_six_months = true

/-! ## Regulation 10 -/
/-- Reg 10(1): In addition to other requirements laid down in these regulations, an issuer making an initial public offer of convertibl... -/
def reg_10_1 (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 10(1)(a): it has obtained credit rating from at least one credit rating agency;... -/
def reg_10_1_a (issuer : Issuer) : Prop :=
  issuer.has_credit_rating_from_one_agency = true

/-- Reg 10(1)(b): it has appointed at least one debenture trustee in accordance with the provisions of the Companies Act, 2013 and the Sec... -/
def reg_10_1_b (issuer : Issuer) : Prop :=
  issuer.has_appointed_debenture_trustee = true

/-- Reg 10(1)(c): it shall create a debenture redemption reserve in accordance with the provisions of the Companies Act, 2013 and rules ma... -/
def reg_10_1_c (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 10(1)(d): if the issuer proposes to create a charge or security on its assets in respect of secured convertible debt instruments, ... -/
def reg_10_1_d (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 10(1)(d)(i): such assets are sufficient to discharge the principal amount at all times;... -/
def reg_10_1_d_i (issuer : Issuer) : Prop :=
  issuer.assets_cover_principal_amount = true

/-- Reg 10(1)(d)(ii): such assets are free from any encumbrance;... -/
def reg_10_1_d_ii (issuer : Issuer) : Prop :=
  issuer.assets_free_from_encumbrance = true

/-- Reg 10(1)(d)(iii): where security is already created on such assets in favour of any existing lender or security trustee or the issue of co... -/
def reg_10_1_d_iii (issuer : Issuer) : Prop :=
  issuer.has_second_or_pari_passu_charge_consent = true

/-- Reg 10(1)(d)(iv): the security or asset cover shall be arrived at after reduction of the liabilities having a first or prior charge, in ca... -/
def reg_10_1_d_iv (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 10(2): The issuer shall redeem the convertible debt instruments in terms of the offer document.... -/
def reg_10_2 (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Combined Regulation 10 gate -/
def reg_10_eligible (issuer : Issuer) : Prop :=
  reg_10_1_a issuer
  ∧ reg_10_1_b issuer
  ∧ reg_10_1_d_i issuer
  ∧ reg_10_1_d_ii issuer
  ∧ reg_10_1_d_iii issuer

/-! ## Regulation 11 -/
/-- Reg 11(1): The issuer shall not convert its optionally convertible debt instruments into equity shares unless the holders of such c... -/
def reg_11_1 (issuer : Issuer) : Prop :=
  issuer.has_positive_consent_from_holders = false

/-- Reg 11(2): Where the value of the convertible portion of any listed convertible debt instruments issued by an issuer exceeds ten cr... -/
def reg_11_2 (issuer : Issuer) : Prop :=
  issuer.convertible_debt_instruments_value_exceeds ≥ 0  -- TODO: set correct threshold

/-- Reg 11(2)(proviso): where the upper limit on the price of such convertible debt instruments and justification thereon is determined and disc... -/
def reg_11_2_proviso (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 11(3): Where an option is to be given to the holders of the convertible debt instruments in terms of sub-regulation (2) and if ... -/
def reg_11_3 (issuer : Issuer) : Prop :=
  issuer.is_redeemed_within_month = false

/-- Reg 11(4): The provision of sub-regulation (2) shall not apply if such redemption is as per the disclosures made in the offer docum... -/
def reg_11_4 (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Combined Regulation 11 gate -/
def reg_11_eligible (issuer : Issuer) : Prop :=
  reg_11_1 issuer
  ∧ reg_11_2 issuer
  ∧ reg_11_3 issuer

/-! ## Regulation 12 -/
/-- Reg 12: An issuer shall not issue convertible debt instruments for financing or for providing loans to or for acquiring shares o... -/
def reg_12 (issuer : Issuer) : Prop :=
  issuer.is_eligible_for_convertible_debt_instruments = false

/-- Reg 12(proviso): Provided that an issuer shall be eligible to issue fully convertible debt instruments for these purposes if the period o... -/
def reg_12_proviso (issuer : Issuer) : Prop :=
  issuer.fully_convertible_debt_period_months ≥ 0  -- TODO: set correct threshold

/-! ## Regulation 13 -/
/-- Reg 13: the price or formula for determination of exercise price of the warrants shall be determined upfront and disclosed in th... -/
def reg_13 (issuer : Issuer) : Prop :=
  issuer.warrant_consideration_upfront_pct ≥ 0  -- TODO: set correct threshold

/-- Reg 13(a): the tenure of such warrants shall not exceed eighteen months from the date of their allotment in the initial public offe... -/
def reg_13_a (issuer : Issuer) : Prop :=
  issuer.warrant_tenure_months ≥ 0  -- TODO: set correct threshold

/-- Reg 13(b): a specified security may have one or more warrants attached to it;... -/
def reg_13_b (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 13(c)(a): the promoters shall contribute twenty per cent. as stipulated in sub-regulation (1), as the case may be, either by way o... -/
def reg_13_c_a (issuer : Issuer) : Prop :=
  issuer.promoter_contribution_pct ≥ 0  -- TODO: set correct threshold

/-- Reg 13(c)(b): “price” means the price of equity shares on conversion arrived at after taking into account the predetermined conversion... -/
def reg_13_c_b (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 13(c)(proviso): twenty-five per cent. consideration amount based on the cap price of the price band determined for the linked equity sha... -/
def reg_13_c_proviso (issuer : Issuer) : Prop :=
  issuer.formula_based_warrants_upfront_contribution_pct ≥ 0  -- TODO: set correct threshold

/-- Reg 13(d): in case the warrant holder does not exercise the option to take equity shares against any of the warrants held by the wa... -/
def reg_13_d (issuer : Issuer) : Prop :=
  issuer.warrant_exercise_period_months ≥ 0  -- TODO: set correct threshold

/-- Reg 13(explanation): For the purpose of this regulation: Promoters’ contribution shall be computed on the basis of the post-issue expanded ca... -/
def reg_13_explanation (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Combined Regulation 13 gate -/
def reg_13_eligible (issuer : Issuer) : Prop :=
  reg_13 issuer
  ∧ reg_13_a issuer
  ∧ reg_13_d issuer
  ∧ reg_13_c_a issuer

/-! ## Composite Chapter II Part II Gate -/

def chapter2_part2_eligible (issuer : Issuer) : Prop :=
  reg_10_eligible issuer
  ∧ reg_11_eligible issuer
  ∧ reg_13_eligible issuer

end Reglib.ICDR.Rules
