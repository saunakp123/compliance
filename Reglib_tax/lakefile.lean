-- Reglib/lakefile.lean
import Lake
open Lake DSL

package Reglib where

@[default_target]
lean_lib Reglib where
  roots := #[`Reglib]
