-- Auto-generated rules file: Chapter12_Part2.lean
-- Chapter XII, Part II: LONG-TERM CAPITAL GAINS ON EQUITY

import Reglib.ITA.definitions.Core

namespace Reglib.ITA.Rules

open Reglib.ITA

/-! ## Regulation 112a -/
/-- Reg 112A(1): Where the total income of an assessee includes any income chargeable under the head capital gains, arising from the tran... -/
def reg_112a_1 (issuer : Taxpayer) : Prop :=
  issuer.ltcg_listed_equity_amount ≥ 0  -- TODO: set correct threshold
  ∧ issuer.ltcg_exempt_limit ≥ 0  -- TODO: set correct threshold
  ∧ issuer.ltcg_tax_rate_pct_x10 ≥ 0  -- TODO: set correct threshold

/-- Reg 112A(exemption): The amount of long-term capital gains of one lakh twenty-five thousand rupees shall not be chargeable to tax under secti... -/
def reg_112a_exemption (issuer : Taxpayer) : Prop :=
  issuer.ltcg_exempt_limit ≥ 0  -- TODO: set correct threshold

/-- Reg 112A(holding): Derived rule: an equity share in a listed company is a long-term capital asset if held for more than twelve months.... -/
def reg_112a_holding (issuer : Taxpayer) : Prop :=
  issuer.holding_period_months_equity ≥ 0  -- TODO: set correct threshold

/-- Reg 112A(stt-acq): Derived eligibility: section 112A applies only if STT was paid both at acquisition and at transfer of the equity share o... -/
def reg_112a_stt_acquisition (issuer : Taxpayer) : Prop :=
  issuer.is_stt_paid_at_acquisition = true

/-- Combined Regulation 112a gate -/
def reg_112a_eligible (issuer : Taxpayer) : Prop :=
  reg_112a_1 issuer
  ∧ reg_112a_holding issuer
  ∧ reg_112a_stt_acquisition issuer
  ∧ reg_112a_exemption issuer

/-! ## Composite Chapter XII Part II Gate -/

def chapter12_part2_eligible (issuer : Taxpayer) : Prop :=
  reg_112a_eligible issuer

end Reglib.ITA.Rules
