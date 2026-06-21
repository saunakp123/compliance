-- Auto-generated rules file: Chapter12_Part1.lean
-- Chapter XII, Part I: SHORT-TERM CAPITAL GAINS ON EQUITY

import Reglib.ITA.definitions.Core

namespace Reglib.ITA.Rules

open Reglib.ITA

/-! ## Regulation 111a -/
/-- Reg 111A(1): Where the total income of an assessee includes any income chargeable under the head capital gains, arising from the tran... -/
def reg_111a_1 (issuer : Taxpayer) : Prop :=
  issuer.is_stt_paid_on_transfer = true
  ∧ issuer.stcg_listed_equity_amount ≥ 0  -- TODO: set correct threshold
  ∧ issuer.stcg_tax_rate_pct ≥ 0  -- TODO: set correct threshold

/-- Reg 111A(stt): Derived eligibility: section 111A applies only if STT was paid on the transfer of the listed equity share or unit.... -/
def reg_111a_stt_check (issuer : Taxpayer) : Prop :=
  issuer.is_stt_paid_on_transfer = true

/-- Combined Regulation 111a gate -/
def reg_111a_eligible (issuer : Taxpayer) : Prop :=
  reg_111a_1 issuer
  ∧ reg_111a_stt_check issuer

/-! ## Composite Chapter XII Part I Gate -/

def chapter12_part1_eligible (issuer : Taxpayer) : Prop :=
  reg_111a_eligible issuer

end Reglib.ITA.Rules
