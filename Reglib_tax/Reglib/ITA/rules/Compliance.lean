-- Auto-generated compliance gate file.

import Reglib.ITA.rules.Chapter1_Part1
import Reglib.ITA.rules.Chapter8_Part1
import Reglib.ITA.rules.Chapter12_Part1
import Reglib.ITA.rules.Chapter12_Part2
import Reglib.ITA.rules.ChapterVI_A_Part1
import Reglib.ITA.rules.ChapterXIV_Part1
import Reglib.ITA.rules.ChapterXVII_Part1
import Reglib.ITA.rules.ChapterVI_A_Part2
import Reglib.ITA.rules.ChapterXVII_Part2
import Reglib.ITA.definitions.Core
import Reglib.ITA.instances.SampleTaxpayer

namespace Reglib.ITA.Rules
open Reglib.ITA

/-! ## Full Compliance Gate -/

def compliance_eligible (issuer : Taxpayer) : Prop :=
  chapter1_part1_eligible issuer
  ∧ chapter8_part1_eligible issuer
  ∧ chapter12_part1_eligible issuer
  ∧ chapter12_part2_eligible issuer
  ∧ chapterVI_A_part1_eligible issuer
  ∧ chapterXIV_part1_eligible issuer
  ∧ chapterXVII_part1_eligible issuer
  ∧ chapterVI_A_part2_eligible issuer
  ∧ chapterXVII_part2_eligible issuer

/-! ## Sample Taxpayer -/
-- Canonical instance: `Reglib.ITA.sample_taxpayer` from instances/SampleTaxpayer.lean
-- (stub values removed so TaxProbe / ablation use real FY 2024–25 field values).

end Reglib.ITA.Rules
