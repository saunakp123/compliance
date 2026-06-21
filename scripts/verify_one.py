#!/usr/bin/env python3
"""
verify_one.py
=============
APOLLO automation loop for GoldProbe theorems.

Default engine: Pantograph (LeanDojo-v2 stack, no AST tracing).
Legacy engine: LeanDojo v1 (--engine leandojo, requires tracing).

WSL (recommended):
  bash scripts/wsl_setup_venv.sh          # once: pantograph + ollama
  bash scripts/run_verify_wsl.sh smoke    # ladder smoke test
  bash scripts/run_verify_wsl.sh ablation # full 3-config run

Reglib_gold uses Lean 4.29.1 (matches Pantograph). Rebuild in WSL before verify:
  bash scripts/_wsl_lake_build.sh

Three configs selectable via --config flag:
  ladder  : deterministic tactic ladder only (no LLM)
  extended: ladder + decide / native_decide / aesop
  qwen    : extended + Qwen2.5:14b-instruct via Ollama (domain-adapted fallback)

Usage:
    python scripts/verify_one.py \
        --reglib   Reglib_gold \
        --probe    Reglib_gold/Reglib/ICDR/GoldProbe.lean \
        --rules    data/gold_standard/gold_standard_regs_4_23.jsonl \
        --defs     data/processed/definitions_icdr_reg2.jsonl \
        --config   qwen \
        --out      reports/proof_results_qwen.jsonl \
        --max-llm-rounds 3
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional

# LeanDojo v1 is optional (legacy --engine leandojo only).
LeanGitRepo = Theorem = Dojo = ProofFinished = TacticState = None  # type: ignore


def _ensure_probe_ast_traced(repo, probe_rel: str) -> None:
    """LeanDojo batch trace can skip GoldProbe; trace it explicitly if needed."""
    import lean_dojo.data_extraction.trace as _trace_mod
    from lean_dojo.utils import execute, working_directory

    traced_path = _trace_mod.get_traced_repo_path(repo, build_deps=False)
    ast_json = (
        traced_path / ".lake/build/ir" / Path(probe_rel).with_suffix(".ast.json")
    )
    if ast_json.is_file():
        print(f"[verify_one] Probe trace OK: {ast_json.name}")
        return
    patched = Path(__file__).resolve().parent / "lean_dojo" / "ExtractData.lean"
    print(f"[verify_one] Tracing probe file: {probe_rel}")
    (traced_path / "lean-toolchain").write_text("leanprover/lean4:v4.14.0\n", encoding="utf-8")
    with working_directory(traced_path):
        if Path("ExtractData.lean").exists():
            Path("ExtractData.lean").unlink()
        shutil.copyfile(patched, "ExtractData.lean")
        execute("lake build GoldProbe")
        execute(f"lake env lean --threads 4 --run ExtractData.lean {probe_rel}")
    if not ast_json.is_file():
        raise SystemExit(f"LeanDojo probe trace failed: {ast_json}")


def _patch_leandojo_extractdata() -> None:
    """Use repo-patched ExtractData.lean (Lean 4.14 TSyntax header fix)."""
    patched = Path(__file__).resolve().parent / "lean_dojo" / "ExtractData.lean"
    if not patched.is_file():
        return
    import lean_dojo.data_extraction.trace as _trace_mod

    _trace_mod.LEAN4_DATA_EXTRACTOR_PATH = patched


def _init_leandojo() -> None:
    """Import lean-dojo and apply Windows patches (legacy engine only)."""
    global LeanGitRepo, Theorem, Dojo, ProofFinished, TacticState
    try:
        from lean_dojo import LeanGitRepo as _LGR
        from lean_dojo import Theorem as _Thm
        from lean_dojo import Dojo as _Dojo
        from lean_dojo import ProofFinished as _PF
        from lean_dojo import TacticState as _TS
        import lean_dojo.data_extraction.lean as _lean_mod
        import lean_dojo.utils as _ld_utils
        from lean_dojo.data_extraction.lean import RepoType
    except ImportError as e:
        raise SystemExit("lean_dojo not installed. Run: pip install lean-dojo") from e

    LeanGitRepo, Theorem, Dojo, ProofFinished, TacticState = (
        _LGR, _Thm, _Dojo, _PF, _TS
    )
    _patch_leandojo_extractdata()
    _patch_leandojo_for_windows(_lean_mod, _ld_utils, RepoType)


def _patch_leandojo_for_windows(_lean_mod, _ld_utils, RepoType) -> None:
    """LeanDojo's is_git_repo uses Unix shell redirects; fix for native Windows."""

    def _is_git_repo(path: Path) -> bool:
        try:
            r = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=path,
                capture_output=True,
                text=True,
            )
            return r.returncode == 0 and "true" in (r.stdout or "")
        except OSError:
            return False

    _orig_get_repo_type = _lean_mod.get_repo_type

    def _get_repo_type(url: str):
        p = Path(url)
        if p.is_dir() and _is_git_repo(p.resolve()):
            return RepoType.LOCAL
        return _orig_get_repo_type(url)

    _lean_mod.is_git_repo = _is_git_repo  # type: ignore[attr-defined]
    _ld_utils.is_git_repo = _is_git_repo
    _lean_mod.get_repo_type = _get_repo_type

    _orig_format_cache = _lean_mod._format_cache_dirname

    def _format_cache_dirname(url: str, commit: str) -> str:
        parts = url.replace("\\", "/").rstrip("/").split("/")
        if len(parts) >= 2:
            return _orig_format_cache(url.replace("\\", "/"), commit)
        repo_name = parts[-1] if parts else "repo"
        return f"gitpython-{repo_name}-{commit}"

    _lean_mod._format_cache_dirname = _format_cache_dirname

    # Skip .lake when copying local repos (avoids Windows file locks on build artifacts).
    _orig_url_to_repo = _lean_mod.url_to_repo.__wrapped__

    def _url_to_repo(url, num_retries=2, repo_type=None, tmp_dir=None):
        url_norm = _lean_mod.normalize_url(url)
        rt = repo_type or _lean_mod.get_repo_type(url_norm)
        if rt == RepoType.LOCAL:

            def _ignore(_dir: str, names: list[str]) -> set[str]:
                return {n for n in names if n in (".lake", "build", "__pycache__")}

            from git import Repo as GitRepo

            with _ld_utils.working_directory() as td:
                tmp = tmp_dir or td
                dest = tmp / os.path.basename(url_norm)
                shutil.copytree(url_norm, dest, ignore=_ignore, dirs_exist_ok=True)
                return GitRepo(dest)
        return _orig_url_to_repo(url, num_retries, repo_type, tmp_dir)

    _lean_mod.url_to_repo = _lean_mod.cache(_url_to_repo)  # type: ignore[method-assign]

    # Use the local git checkout in-place (avoids temp copytree locks on Windows/OneDrive).
    from git import Repo as GitRepo

    _orig_post_init = LeanGitRepo.__post_init__

    def _lean_git_repo_post_init(self) -> None:
        repo_type = _lean_mod.get_repo_type(self.url)
        if repo_type is None:
            raise ValueError(f"{self.url} is not a valid URL")
        if repo_type == RepoType.LOCAL:
            object.__setattr__(self, "repo_type", repo_type)
            url = _lean_mod.normalize_url(self.url, repo_type=repo_type)
            object.__setattr__(self, "url", url)
            git_repo = GitRepo(url)
            if not _lean_mod.is_commit_hash(self.commit):
                commit = _lean_mod._to_commit_hash(git_repo, self.commit)
                object.__setattr__(self, "commit", commit)
            object.__setattr__(self, "repo", git_repo)
            key = (self.url, self.commit)
            if key in _lean_mod.info_cache.lean_version:
                lean_version = _lean_mod.info_cache.lean_version[key]
            else:
                config = self.get_config("lean-toolchain")
                lean_version = _lean_mod.get_lean4_version_from_config(config["content"])
                _lean_mod.info_cache.lean_version[key] = lean_version
            object.__setattr__(self, "lean_version", lean_version)
            return
        _orig_post_init(self)

    LeanGitRepo.__post_init__ = _lean_git_repo_post_init  # type: ignore[method-assign]

    # In-place tracing only on native Windows (OneDrive locks). WSL uses stock LeanDojo trace.
    if sys.platform != "win32":
        return

    # Trace local repos in-place (no temp clone; fixes Windows file locks).
    import lean_dojo.data_extraction.trace as _trace_mod
    from lean_dojo.data_extraction.traced_data import TracedRepo
    from lean_dojo.data_extraction.trace import (
        LEAN4_DATA_EXTRACTOR_PATH,
        LEAN4_REPL_PATH,
        check_files,
        get_lean_version,
        is_new_version,
        launch_progressbar,
    )
    from lean_dojo.constants import NUM_PROCS
    from lean_dojo.utils import execute

    _orig_trace = _trace_mod._trace
    _orig_get_traced = _trace_mod.get_traced_repo_path

    def _trace_local_in_place(repo: LeanGitRepo, build_deps: bool) -> None:
        root = Path(repo.url)
        with _ld_utils.working_directory(root):
            if build_deps:
                execute("lake build")
            else:
                try:
                    execute("lake exe cache get")
                except Exception:
                    pass
            lean_prefix = execute("lean --print-prefix", capture_output=True)[0].strip()
            if is_new_version(get_lean_version()):
                packages_path = Path(".lake/packages")
                build_path = Path(".lake/build")
            else:
                packages_path = Path("lake-packages")
                build_path = Path("build")
            if not (packages_path / "lean4").exists():
                shutil.copytree(lean_prefix, str(packages_path / "lean4"))
            shutil.copyfile(LEAN4_DATA_EXTRACTOR_PATH, LEAN4_DATA_EXTRACTOR_PATH.name)
            dirs = [build_path]
            if build_deps:
                dirs.append(packages_path)
            with launch_progressbar(dirs):
                cmd = f"lake env lean --threads {NUM_PROCS} --run ExtractData.lean"
                if not build_deps:
                    cmd += " noDeps"
                execute(cmd)
            check_files(packages_path, not build_deps)
            if Path(LEAN4_DATA_EXTRACTOR_PATH.name).exists():
                os.remove(LEAN4_DATA_EXTRACTOR_PATH.name)
            if not Path(LEAN4_REPL_PATH.name).exists():
                shutil.copyfile(LEAN4_REPL_PATH, LEAN4_REPL_PATH.name)
            if Path("lakefile.lean").exists():
                with open("lakefile.lean", "a", encoding="utf-8") as oup:
                    oup.write("\nlean_lib Lean4Repl {\n\n}\n")
            try:
                execute("lake build Lean4Repl")
            except Exception:
                pass

    def _get_traced_repo_path(repo: LeanGitRepo, build_deps: bool = True) -> Path:
        rel_cache_dir = repo.get_cache_dirname() / repo.name
        path = _trace_mod.cache.get(rel_cache_dir)
        if path is not None:
            return path
        if repo.repo_type == RepoType.LOCAL:
            _trace_mod.logger.info(f"Tracing {repo} (in-place)")
            _trace_local_in_place(repo, build_deps)
            src_dir = Path(repo.url)
            TracedRepo.from_traced_files(src_dir, build_deps).save_to_disk()
            return _trace_mod.cache.store(src_dir, rel_cache_dir)
        return _orig_get_traced(repo, build_deps)

    _trace_mod.get_traced_repo_path = _get_traced_repo_path
    import lean_dojo.interaction.dojo as _dojo_mod
    _dojo_mod.get_traced_repo_path = _get_traced_repo_path


def _build_ladders() -> tuple[list[str], list[str]]:
    """Tactic ladders; use open Reglib.ICDR.Rules in Pantograph sorry snippets."""
    basic = [
        "simp [sample_compliant_issuer]",
        "simp [sample_compliant_issuer, List.all]",
        "simp [sample_compliant_issuer, List.all, List.length]",
        "decide",
        "omega",
        "norm_num",
        "trivial",
    ]
    extended = basic + [
        "native_decide",
        "simp [sample_compliant_issuer]; omega",
        "simp [sample_compliant_issuer, List.all]; omega",
        "tauto",
        "aesop",
        "decide <;> rfl",
    ]
    return basic, extended


LADDER_BASIC, LADDER_EXTENDED = _build_ladders()


def ensure_lake_build(reglib: Path) -> None:
    """Build Linux oleans in WSL before Pantograph (Windows .olean headers differ)."""
    if sys.platform == "win32":
        return
    env = os.environ.copy()
    elan = Path.home() / ".elan" / "bin"
    if elan.is_dir():
        env["PATH"] = f"{elan}:{env.get('PATH', '')}"
    print("[verify_one] lake build GoldProbe (Linux oleans)...")
    subprocess.run(
        ["lake", "build", "GoldProbe"],
        cwd=reglib,
        env=env,
        check=True,
    )


def build_sorry_snippet(thm_name: str, def_name: str) -> str:
    """Isolated theorem for Pantograph — does not clash with GoldProbe names."""
    return (
        f"namespace SmokeVerify_{thm_name}\n"
        "open Reglib.ICDR.Rules\n"
        "open Reglib.ICDR\n"
        f"theorem check_{thm_name} : {def_name} sample_compliant_issuer := by sorry"
    )


def try_panto_tactic(server, state, tactic: str):
    try:
        new_state = server.goal_tactic(state, tactic=tactic)
        solved = bool(getattr(new_state, "is_solved", False))
        return new_state, solved, None
    except Exception as e:
        return state, False, str(e)


def run_ladder_panto(
    server, init_state, ladder: list[str], def_name: str,
) -> Optional[tuple[str, object]]:
    extra = [
        f"unfold {def_name}; simp [sample_compliant_issuer]",
        f"unfold {def_name}; simp [sample_compliant_issuer, List.all]",
        f"unfold {def_name}; decide",
    ]
    for tactic in extra + ladder:
        state, solved, _err = try_panto_tactic(server, init_state, tactic)
        if solved:
            return tactic, state
    return None


def run_decompose_panto(
    server, init_state, sub_clauses: list[str],
) -> Optional[tuple[str, object]]:
    tactics = [
        "constructor <;> simp [sample_compliant_issuer]",
        "constructor <;> (simp [sample_compliant_issuer]; try omega)",
        "constructor <;> (simp [sample_compliant_issuer, List.all]; try omega)",
        "constructor <;> decide",
        "constructor <;> native_decide",
        f"unfold {' '.join(sub_clauses)}; simp [sample_compliant_issuer]",
        f"unfold {' '.join(sub_clauses)}; simp [sample_compliant_issuer, List.all]; omega",
        "decide",
        "native_decide",
    ]
    for tactic in tactics:
        state, solved, _err = try_panto_tactic(server, init_state, tactic)
        if solved:
            return tactic, state
    return None


def load_rules(path: Path) -> dict[str, dict]:
    rules = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                r = json.loads(line)
                rules[r["rule_id"]] = r
    return rules


def load_definitions(path: Path) -> dict[str, dict]:
    defs = {}
    if not path.exists():
        return defs
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                d = json.loads(line)
                field = d.get("maps_to_field", "")
                if field:
                    defs[field] = d
    return defs


def parse_probe_theorems(probe_path: Path) -> list[dict]:
    content = probe_path.read_text(encoding="utf-8")
    theorems = []

    thm_pattern = re.compile(
        r"theorem\s+(gold_\w+)\s*:\s*(\w+)\s+sample_compliant_issuer\s*:=\s*by",
        re.MULTILINE,
    )

    composite_comment = re.compile(
        r"Composite gate:\s*(\w+)\s*=\s*(.+)",
    )

    composite_names: set[str] = set()
    composite_subs: dict[str, list[str]] = {}
    for m in composite_comment.finditer(content):
        gate = m.group(1)
        subs = [s.strip() for s in m.group(2).split(",")]
        composite_names.add(gate)
        composite_subs[gate] = subs

    for m in thm_pattern.finditer(content):
        thm_name = m.group(1)
        def_name = m.group(2)
        is_composite = def_name in composite_names
        rule_id = def_name.replace("reg_", "ICDR_").upper()
        theorems.append({
            "theorem_name": thm_name,
            "def_name": def_name,
            "is_composite": is_composite,
            "sub_clauses": composite_subs.get(def_name, []),
            "rule_id": rule_id,
        })

    return theorems


def try_tactic(dojo, state, tactic: str):
    try:
        result = dojo.run_tac(state, tactic)
        return result, None
    except Exception as e:
        return None, str(e)


def run_ladder(dojo, init_state, ladder: list[str]) -> Optional[tuple[str, object]]:
    for tactic in ladder:
        result, _err = try_tactic(dojo, init_state, tactic)
        if result is not None and isinstance(result, ProofFinished):
            return tactic, result
    return None


def run_decompose(dojo, init_state, sub_clauses: list[str]) -> Optional[tuple[str, object]]:
    decompose_tactics = [
        "constructor <;> simp [sample_compliant_issuer]",
        "constructor <;> (simp [sample_compliant_issuer]; try omega)",
        "constructor <;> (simp [sample_compliant_issuer, List.all]; try omega)",
        "constructor <;> decide",
        "constructor <;> native_decide",
        f"unfold {' '.join(sub_clauses)}; simp [sample_compliant_issuer]",
        f"unfold {' '.join(sub_clauses)}; simp [sample_compliant_issuer, List.all]",
        f"unfold {' '.join(sub_clauses)}; simp [sample_compliant_issuer, List.all]; omega",
        "decide",
        "native_decide",
    ]
    for tactic in decompose_tactics:
        result, _err = try_tactic(dojo, init_state, tactic)
        if result is not None and isinstance(result, ProofFinished):
            return tactic, result
    return None


QWEN_SYSTEM = """You are an expert in Lean 4 theorem proving for financial regulatory compliance.

The theorems you prove are about a concrete Lean 4 `Issuer` struct called `sample_compliant_issuer`.
All fields are concrete values (Bool, Nat, List Nat). The proofs are always very short (1-2 tactics).

Known working tactics for this domain:
- Bool field: `simp [sample_compliant_issuer]`
- Nat threshold (≥): `omega` or `norm_num` after `simp [sample_compliant_issuer]`
- List length/all: `simp [sample_compliant_issuer, List.all]`
- Conjunction: `constructor <;> simp [sample_compliant_issuer]`
- Anything decidable: `decide` or `native_decide`

Respond with ONLY a single Lean 4 tactic or tactic sequence on one line. No explanation. No markdown."""


def build_qwen_prompt(goal_state: str, rule_text: str, def_texts: list[str]) -> str:
    def_block = "\n".join(f"  - {d}" for d in def_texts) if def_texts else "  (none)"
    return (
        f"Lean 4 proof goal:\n{goal_state}\n\n"
        f"SEBI ICDR regulatory text:\n{rule_text}\n\n"
        f"Field definitions:\n{def_block}\n\n"
        f"Suggest one Lean 4 tactic to close this goal:"
    )


def _strip_qwen_response(raw: str) -> str:
    raw = raw.strip()
    raw = re.sub(r"^```(?:lean)?\s*", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"\s*```$", "", raw, flags=re.MULTILINE)
    return raw.strip().splitlines()[0].strip()


def call_qwen_via_windows_powershell(
    goal_state: str, rule_text: str, def_texts: list[str]
) -> Optional[str]:
    """WSL cannot reach Windows Ollama on :11434 without a firewall rule; use host PowerShell."""
    import tempfile

    payload = {
        "model": "qwen2.5:14b-instruct",
        "messages": [
            {"role": "system", "content": QWEN_SYSTEM},
            {"role": "user", "content": build_qwen_prompt(goal_state, rule_text, def_texts)},
        ],
        "options": {"temperature": 0.1, "num_predict": 80},
        "stream": False,
    }
    tmp: Optional[str] = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(payload, f)
            tmp = f.name
        win_path = subprocess.check_output(["wslpath", "-w", tmp], text=True).strip()
        win_path_ps = win_path.replace("'", "''")
        ps = (
            f"$r = Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/chat' "
            f"-Method Post -Body (Get-Content -Raw -LiteralPath '{win_path_ps}') "
            f"-ContentType 'application/json' -TimeoutSec 300; "
            f"$r.message.content"
        )
        proc = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", ps],
            capture_output=True,
            text=True,
            timeout=320,
        )
        if proc.returncode != 0:
            err = (proc.stderr or proc.stdout or "").strip()[:300]
            print(f"  [qwen/win-proxy] failed: {err}")
            return None
        return _strip_qwen_response(proc.stdout)
    except Exception as e:
        print(f"  [qwen/win-proxy] error: {e}")
        return None
    finally:
        if tmp and os.path.isfile(tmp):
            try:
                os.unlink(tmp)
            except OSError:
                pass


def call_qwen(goal_state: str, rule_text: str, def_texts: list[str]) -> Optional[str]:
    if os.environ.get("OLLAMA_USE_WINDOWS_PROXY", "").lower() in ("1", "true", "yes"):
        return call_qwen_via_windows_powershell(goal_state, rule_text, def_texts)
    try:
        import ollama

        resp = ollama.chat(
            model="qwen2.5:14b-instruct",
            messages=[
                {"role": "system", "content": QWEN_SYSTEM},
                {"role": "user", "content": build_qwen_prompt(goal_state, rule_text, def_texts)},
            ],
            options={"temperature": 0.1, "num_predict": 80},
        )
        return _strip_qwen_response(resp["message"]["content"])
    except Exception as e:
        print(f"  [qwen] error: {e}")
        if shutil.which("wslpath") and shutil.which("powershell.exe"):
            print("  [qwen] retry via Windows PowerShell proxy...")
            return call_qwen_via_windows_powershell(goal_state, rule_text, def_texts)
        return None


def get_goal_state_string(state) -> str:
    if hasattr(state, "goals"):
        return "\n".join(str(g) for g in state.goals)
    return str(state)


def prove_theorem_pantograph(
    server,
    thm_info: dict,
    rules_db: dict,
    defs_db: dict,
    config: str,
    max_llm_rounds: int,
) -> dict:
    """Prove via Pantograph (LeanDojo-v2 interaction layer; no tracing)."""
    thm_name = thm_info["theorem_name"]
    def_name = thm_info["def_name"]
    rule_id = thm_info["rule_id"]
    is_comp = thm_info["is_composite"]
    subs = thm_info["sub_clauses"]

    result_record = {
        "theorem_name": thm_name,
        "def_name": def_name,
        "rule_id": rule_id,
        "is_composite": is_comp,
        "config": config,
        "engine": "pantograph",
        "status": "unproved",
        "tactic": None,
        "phase": None,
        "llm_rounds": 0,
        "time_s": 0.0,
        "error": None,
    }

    t0 = time.time()
    ladder = LADDER_EXTENDED if config in ("extended", "qwen") else LADDER_BASIC

    try:
        snippet = build_sorry_snippet(thm_name, def_name)
        unit, = server.load_sorry(snippet)
        state = unit.goal_state

        print(f"  [ladder] {thm_name}")
        win = run_ladder_panto(server, state, ladder, def_name)  # state = init goal
        if win:
            tactic, _ = win
            result_record.update(status="proved", tactic=tactic, phase="ladder")
            result_record["time_s"] = round(time.time() - t0, 2)
            return result_record

        if is_comp and subs:
            print(f"  [decompose] {thm_name} subs={subs}")
            win = run_decompose_panto(server, state, subs)
            if win:
                tactic, _ = win
                result_record.update(status="proved", tactic=tactic, phase="decompose")
                result_record["time_s"] = round(time.time() - t0, 2)
                return result_record

        if config == "qwen":
            rule = rules_db.get(rule_id, {})
            rule_text = rule.get("text", "")
            def_texts = []
            for m in rule.get("maps_to") or []:
                field = m.get("field", "")
                defn = defs_db.get(field)
                if defn:
                    def_texts.append(
                        f"{field}: {defn.get('definition_text', '')[:120]}"
                    )
            for round_num in range(1, max_llm_rounds + 1):
                result_record["llm_rounds"] = round_num
                goal_str = get_goal_state_string(state)
                print(f"  [qwen round {round_num}] goal: {goal_str[:80]}")
                tactic = call_qwen(goal_str, rule_text, def_texts)
                if not tactic:
                    continue
                print(f"  [qwen] suggested: {tactic}")
                state, solved, err = try_panto_tactic(server, state, tactic)
                if err:
                    print(f"  [qwen] kernel error: {err}")
                    continue
                if solved:
                    result_record.update(
                        status="proved",
                        tactic=tactic,
                        phase="qwen",
                        llm_rounds=round_num,
                    )
                    result_record["time_s"] = round(time.time() - t0, 2)
                    return result_record

    except Exception as e:
        result_record["error"] = str(e)
        print(f"  [ERROR] {thm_name}: {e}")

    result_record["time_s"] = round(time.time() - t0, 2)
    return result_record


def prove_theorem(
    repo,
    thm_info: dict,
    probe_file: str,
    rules_db: dict,
    defs_db: dict,
    config: str,
    max_llm_rounds: int,
) -> dict:
    thm_name = thm_info["theorem_name"]
    def_name = thm_info["def_name"]
    rule_id = thm_info["rule_id"]
    is_comp = thm_info["is_composite"]
    subs = thm_info["sub_clauses"]

    result_record = {
        "theorem_name": thm_name,
        "def_name": def_name,
        "rule_id": rule_id,
        "is_composite": is_comp,
        "config": config,
        "engine": "leandojo",
        "status": "unproved",
        "tactic": None,
        "phase": None,
        "llm_rounds": 0,
        "time_s": 0.0,
        "error": None,
    }

    t0 = time.time()
    ladder = LADDER_EXTENDED if config in ("extended", "qwen") else LADDER_BASIC

    try:
        # LeanDojo Theorem(repo, relative_lean_path, theorem_name_in_file)
        theorem_obj = Theorem(repo, probe_file, thm_name)
        with Dojo(theorem_obj) as (dojo, init_state):
            print(f"  [ladder] {thm_name}")
            win = run_ladder(dojo, init_state, ladder)
            if win:
                tactic, _ = win
                result_record.update(status="proved", tactic=tactic, phase="ladder")
                result_record["time_s"] = round(time.time() - t0, 2)
                return result_record

            if is_comp and subs:
                print(f"  [decompose] {thm_name} subs={subs}")
                win = run_decompose(dojo, init_state, subs)
                if win:
                    tactic, _ = win
                    result_record.update(status="proved", tactic=tactic, phase="decompose")
                    result_record["time_s"] = round(time.time() - t0, 2)
                    return result_record

            if config == "qwen":
                rule = rules_db.get(rule_id, {})
                rule_text = rule.get("text", "")

                def_texts = []
                for m in rule.get("maps_to") or []:
                    field = m.get("field", "")
                    defn = defs_db.get(field)
                    if defn:
                        def_texts.append(
                            f"{field}: {defn.get('definition_text', '')[:120]}"
                        )

                state = init_state
                for round_num in range(1, max_llm_rounds + 1):
                    result_record["llm_rounds"] = round_num
                    goal_str = get_goal_state_string(state)
                    print(f"  [qwen round {round_num}] goal: {goal_str[:80]}")
                    tactic = call_qwen(goal_str, rule_text, def_texts)
                    if not tactic:
                        continue
                    print(f"  [qwen] suggested: {tactic}")
                    res, err = try_tactic(dojo, state, tactic)
                    if res is None:
                        print(f"  [qwen] kernel error: {err}")
                        continue
                    if isinstance(res, ProofFinished):
                        result_record.update(
                            status="proved",
                            tactic=tactic,
                            phase="qwen",
                            llm_rounds=round_num,
                        )
                        result_record["time_s"] = round(time.time() - t0, 2)
                        return result_record
                    if isinstance(res, TacticState):
                        state = res

    except Exception as e:
        result_record["error"] = str(e)
        print(f"  [ERROR] {thm_name}: {e}")

    result_record["time_s"] = round(time.time() - t0, 2)
    return result_record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reglib", required=True, type=Path)
    parser.add_argument("--probe", required=True, type=Path)
    parser.add_argument("--rules", required=True, type=Path)
    parser.add_argument("--defs", required=True, type=Path)
    parser.add_argument(
        "--engine",
        default="pantograph",
        choices=["pantograph", "leandojo"],
        help="pantograph (default, LeanDojo-v2/Pantograph) or leandojo (legacy v1)",
    )
    parser.add_argument("--config", default="ladder", choices=["ladder", "extended", "qwen"])
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--max-llm-rounds", type=int, default=3)
    parser.add_argument("--only", type=str, default=None)
    args = parser.parse_args()

    reglib_abs = args.reglib.resolve()
    args.probe.resolve()

    print(f"[verify_one] Engine: {args.engine}")
    print(f"[verify_one] Config: {args.config}")

    rules_db = load_rules(args.rules)
    defs_db = load_definitions(args.defs)
    theorems = parse_probe_theorems(args.probe)

    if args.only:
        only_set = set(args.only.split(","))
        theorems = [t for t in theorems if t["theorem_name"] in only_set]

    print(f"[verify_one] Theorems to attempt: {len(theorems)}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    results = []
    proved = 0

    if args.engine == "pantograph":
        try:
            from pantograph.server import Server
        except ImportError as e:
            raise SystemExit(
                "pantograph not installed. Run: pip install pantograph "
                "(or bash scripts/wsl_setup_venv.sh in WSL)"
            ) from e
        ensure_lake_build(reglib_abs)
        server = Server(imports=["Reglib.ICDR.GoldProbe"], project_path=reglib_abs)
        prove_fn = lambda thm: prove_theorem_pantograph(
            server, thm, rules_db, defs_db, args.config, args.max_llm_rounds
        )
    else:
        _init_leandojo()
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=reglib_abs
        ).decode().strip()
        print(f"[verify_one] Reglib_gold commit: {commit}")
        repo_url = reglib_abs.resolve().as_posix()
        repo = LeanGitRepo(repo_url, commit)
        probe_rel = str(args.probe.resolve().relative_to(reglib_abs)).replace("\\", "/")
        _ensure_probe_ast_traced(repo, probe_rel)
        prove_fn = lambda thm: prove_theorem(
            repo, thm, probe_rel, rules_db, defs_db,
            args.config, args.max_llm_rounds,
        )

    with open(args.out, "w", encoding="utf-8") as fout:
        for i, thm in enumerate(theorems):
            print(f"\n[{i+1}/{len(theorems)}] {thm['theorem_name']}")
            rec = prove_fn(thm)
            results.append(rec)
            fout.write(json.dumps(rec) + "\n")
            fout.flush()

            if rec["status"] == "proved":
                proved += 1
                print(f"  OK proved via {rec['phase']}: {rec['tactic']}")
            else:
                print("  X unproved")

    total = len(results)
    pct = 100 * proved / total if total else 0
    print(f"\n{'='*60}")
    print(f"Config: {args.config}")
    print(f"Proved: {proved}/{total} ({pct:.1f}%)")

    from collections import Counter
    phase_counts = Counter(r["phase"] for r in results if r["status"] == "proved")
    for phase, count in phase_counts.most_common():
        print(f"  {phase:12s}: {count}")

    comp_proved = sum(1 for r in results if r["is_composite"] and r["status"] == "proved")
    comp_total = sum(1 for r in results if r["is_composite"])
    noncomp_proved = proved - comp_proved
    noncomp_total = total - comp_total
    print(f"\nSub-clause theorems: {noncomp_proved}/{noncomp_total}")
    print(f"Composite gates:     {comp_proved}/{comp_total}")
    print(f"\nResults written to: {args.out}")


if __name__ == "__main__":
    main()
