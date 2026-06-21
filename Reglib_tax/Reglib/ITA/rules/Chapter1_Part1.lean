-- Auto-generated rules file: Chapter1_Part1.lean
-- Chapter I, Part I: INDIVIDUALS

import Reglib.ITA.definitions.Core

namespace Reglib.ITA.Rules

open Reglib.ITA

/-! ## Regulation 6 -/
/-- Reg 6(1): An individual is said to be resident in India in any previous year, if he has been in India during that year for a perio... -/
def reg_6_1 (issuer : Taxpayer) : Prop :=
  issuer.days_in_india_fy ≥ 0  -- TODO: set correct threshold

/-- Reg 6(1)(check): Derived rule: an individual is resident if days_in_india_fy is at least 182.... -/
def reg_6_1_resident_check (issuer : Taxpayer) : Prop :=
  issuer.is_resident = true

/-- Combined Regulation 6 gate -/
def reg_6_eligible (issuer : Taxpayer) : Prop :=
  reg_6_1 issuer
  ∧ reg_6_1_resident_check issuer

/-! ## Composite Chapter I Part I Gate -/

def chapter1_part1_eligible (issuer : Taxpayer) : Prop :=
  reg_6_eligible issuer

end Reglib.ITA.Rules
