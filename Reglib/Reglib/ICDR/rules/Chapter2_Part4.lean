-- Auto-generated rules file: Chapter2_Part4.lean
-- Chapter II, Part IV: LOCK-IN AND RESTRICTIONS ON TRANSFERABILITY

import Reglib.ICDR.definitions.Core

namespace Reglib.ICDR.Rules

open Reglib.ICDR

/-! ## Regulation 16 -/
/-- Reg 16(1): The specified securities held by the promoters shall not be transferable (hereinafter referred to as “lock-in”) for the ... -/
def reg_16_1 (issuer : Issuer) : Prop :=
  issuer.promoter_lock_in_period_months ≥ 0  -- TODO: set correct threshold

/-- Reg 16(1)(a): minimum promoters’ contribution including contribution made by alternative investment funds or foreign venture capital i... -/
def reg_16_1_a (issuer : Issuer) : Prop :=
  issuer.promoter_contribution_lock_in_months ≥ 0  -- TODO: set correct threshold

/-- Reg 16(1)(a)(proviso): in case the majority of the issue proceeds excluding the portion of offer for sale is proposed to be utilized for capita... -/
def reg_16_1_a_proviso (issuer : Issuer) : Prop :=
  issuer.ofs_lock_in_period_years ≥ 0  -- TODO: set correct threshold

/-- Reg 16(1)(b): promoters’ holding in excess of minimum promoters’ contribution shall be locked-in for a period of [six months] from the... -/
def reg_16_1_b (issuer : Issuer) : Prop :=
  issuer.ofs_holding_period_months_reg16 ≥ 0  -- TODO: set correct threshold

/-- Reg 16(2): The SR equity shares shall be under lock-in until conversion into equity shares having voting rights same as that of ord... -/
def reg_16_2 (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 16(explanation): For the purpose of this sub-regulation, “capital expenditure” shall include civil work, miscellaneous fixed assets, purc... -/
def reg_16_explanation (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Combined Regulation 16 gate -/
def reg_16_eligible (issuer : Issuer) : Prop :=
  reg_16_1 issuer
  ∧ reg_16_1_a issuer
  ∧ reg_16_1_b issuer

/-! ## Regulation 17 -/
/-- Reg 17: The entire pre-issue capital held by persons other than the promoters shall be locked-in for a period of six months from... -/
def reg_17 (issuer : Issuer) : Prop :=
  issuer.non_promoter_lock_in_period_months ≥ 0  -- TODO: set correct threshold

/-- Reg 17(1)(a): [equity shares allotted to employees, whether currently an employee or not, under an employee stock option or employee s... -/
def reg_17_1_a (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 17(1)(a)(proviso): the equity shares allotted to the employees shall be subject to the provisions of lock-in as specified under the Securit... -/
def reg_17_1_a_proviso (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 17(1)(b): [equity shares held by an employee stock option trust or transferred to the employees by an employee stock option trust ... -/
def reg_17_1_b (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 17(1)(b)(proviso): such equity shares shall be locked in for a period of at least six months from the date of purchase by the venture capit... -/
def reg_17_1_b_proviso (issuer : Issuer) : Prop :=
  issuer.ofs_holding_period_months_reg17 ≥ 0  -- TODO: set correct threshold

/-- Reg 17(explanation)(i): For the purpose of clause (c), in case such equity shares have resulted pursuant to conversion of fully paid-up compulso... -/
def reg_17_explanation_i (issuer : Issuer) : Prop :=
  issuer.holding_period_months ≥ 0  -- TODO: set correct threshold

/-- Reg 17(explanation)(ii): For the purpose of clause (c), in case such equity shares have resulted pursuant to a bonus issue, then the holding peri... -/
def reg_17_explanation_ii (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 17(explanation)(ii)(a): that the bonus shares being issued out of free reserves and share premium existing in the books of account as at the end... -/
def reg_17_explanation_ii_a (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 17(explanation)(ii)(b): that the bonus shares not being issued by utilisation of revaluation reserves or unrealized profits of the issuer.... -/
def reg_17_explanation_ii_b (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 17(explanation)(iii): For the purpose of clauses (a) and (b), equity shares shall include any equity shares allotted pursuant to a bonus issue... -/
def reg_17_explanation_iii (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 17(proviso): nothing contained in this regulation shall apply to:... -/
def reg_17_proviso (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-! ## Regulation 18 -/
/-- Reg 18: The lock-in provisions shall not apply with respect to the specified securities lent to stabilising agent for the purpos... -/
def reg_18 (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 18(proviso): Provided that the specified securities shall be locked-in for the remaining period from the date on which they are retur... -/
def reg_18_proviso (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-! ## Regulation 19 -/
/-- Reg 19: If the specified securities which are subject to lock-in are partly paid-up and the amount called-up on such specified s... -/
def reg_19 (issuer : Issuer) : Prop :=
  issuer.ofs_holding_period_years ≥ 0  -- TODO: set correct threshold

/-! ## Regulation 20 -/
/-- Reg 20: The certificates of specified securities which are subject to lock-in shall contain the inscription “non-transferable” a... -/
def reg_20 (issuer : Issuer) : Prop :=
  issuer.is_lock_in_recorded_by_depository = true

/-! ## Regulation 21 -/
/-- Reg 21: Specified securities held by the promoters and locked-in may be pledged as a collateral security for a loan granted by a... -/
def reg_21 (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 21(a): if the specified securities are locked-in in terms of clause (a) of regulation 16, the loan has been granted to the issu... -/
def reg_21_a (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 21(b): if the specified securities are locked-in in terms of clause (b) of regulation 16 and the pledge of specified securities... -/
def reg_21_b (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-- Reg 21(proviso): such lock-in shall continue pursuant to the invocation of the pledge and such transferee shall not be eligible to transf... -/
def reg_21_proviso (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-! ## Regulation 22 -/
/-- Reg 22: Subject to the provisions of Securities and Exchange Board of India (Substantial Acquisition of shares and Takeovers) Re... -/
def reg_22 (issuer : Issuer) : Prop :=
  sorry  -- TODO: no fields extracted

/-! ## Composite Chapter II Part IV Gate -/

def chapter2_part4_eligible (issuer : Issuer) : Prop :=
  reg_16_eligible issuer

end Reglib.ICDR.Rules
