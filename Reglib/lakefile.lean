-- Reglib/lakefile.lean
import Lake
open Lake DSL

package Reglib where
  moreLinkArgs := #[
    "-L./.lake/packages/LeanCopilot/.lake/build/lib",
    "-lctranslate2",
  ]

require LeanCopilot from git
  "https://github.com/lean-dojo/LeanCopilot" @ "main"

@[default_target]
lean_lib Reglib where
  roots := #[`Reglib]

lean_lib CopilotProbe where
  roots := #[`Reglib.ICDR.CopilotProbe]
  moreLinkArgs := #[
    "-L./.lake/packages/LeanCopilot/.lake/build/lib",
    "-lctranslate2",
  ]

