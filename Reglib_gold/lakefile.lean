-- Reglib_gold/lakefile.lean (no LeanCopilot — gold APOLLO ablation)
import Lake
open Lake DSL

package Reglib where

@[default_target]
lean_lib Reglib where
  roots := #[`Reglib]

lean_lib GoldProbe where
  roots := #[`Reglib.ICDR.GoldProbe]
