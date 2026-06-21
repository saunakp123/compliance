#!/usr/bin/env python3
"""Windows helper: fetch LeanCopilot native deps and HuggingFace models.

Run from repo root after `lake update` in Reglib/:
    python scripts/setup_leancopilot_windows.py --reglib Reglib

Notes:
  - HuggingFace models land in ~/.cache/lean_copilot/
  - Native LeanCopilot build on Windows is fragile when the repo lives on a
    OneDrive path with spaces. Prefer a short path like C:\\compliance\\Reglib
    or use WSL/Linux for `lake build LeanCopilot`.
"""

from __future__ import annotations

import argparse
import io
import shutil
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

try:
    import zstandard
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "zstandard", "-q"])
    import zstandard

MSYS2_PKGS = [
    (
        "headers-fixed.pkg.tar.zst",
        "https://mirror.msys2.org/mingw/clang64/mingw-w64-clang-x86_64-headers-14.0.0.r37.g2bfe61fba-1-any.pkg.tar.zst",
    ),
    (
        "clang.pkg.tar.zst",
        "https://repo.msys2.org/mingw/clang64/mingw-w64-clang-x86_64-clang-20.1.3-1-any.pkg.tar.zst",
    ),
    (
        "libcxx.pkg.tar.zst",
        "https://repo.msys2.org/mingw/clang64/mingw-w64-clang-x86_64-libc%2B%2B-20.1.3-1-any.pkg.tar.zst",
    ),
    (
        "pthread.pkg.tar.zst",
        "https://repo.msys2.org/mingw/clang64/mingw-w64-clang-x86_64-winpthreads-git-12.0.0.r724.g7e3f2dd90-1-any.pkg.tar.zst",
    ),
]

CTRANSLATE2_DLL = (
    "https://drive.google.com/uc?export=download&id=1W6ZsbBG8gK9FRoMedNCKkg8qqS-bDa9U"
)

HF_MODELS = [
    "kaiyuy/ct2-leandojo-lean4-tacgen-byt5-small",
    "kaiyuy/ct2-leandojo-lean4-retriever-byt5-small",
    "kaiyuy/premise-embeddings-leandojo-lean4-retriever-byt5-small",
    "kaiyuy/ct2-byt5-small",
]


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"[DL] {dest.name}")
    urllib.request.urlretrieve(url, dest)


def decompress_zst(path: Path) -> bytes:
    dctx = zstandard.ZstdDecompressor()
    with path.open("rb") as f:
        return dctx.stream_reader(f).read()


def extract_zst_tar(archive: Path, out_dir: Path) -> None:
    if archive.stat().st_size < 1024:
        raise RuntimeError(f"{archive.name} looks truncated ({archive.stat().st_size} bytes)")
    data = decompress_zst(archive)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as tar:
        tar.extractall(out_dir)


def copy_openblas(build: Path) -> None:
    src = build / "bin" / "libopenblas.dll"
    dst = build / "lib" / "libopenblas.dll"
    if not src.exists():
        print("[SKIP] OpenBLAS — run `lake build LeanCopilot` once to unpack OpenBLAS.zip")
        return
    shutil.copy2(src, dst)
    shutil.copy2(src, build / "lib" / "libopenblas.dll.0")
    print(f"[OK] OpenBLAS -> {dst}")


def fetch_ctranslate2_dll(build: Path) -> None:
    ct2_build = build / "CTranslate2" / "build"
    ct2_build.mkdir(parents=True, exist_ok=True)
    dll = ct2_build / "libctranslate2.dll"
    if not dll.exists() or dll.stat().st_size < 1_000_000:
        download(CTRANSLATE2_DLL, dll)
    for name in ("libctranslate2.dll", "libctranslate2.dll.4"):
        shutil.copy2(dll, build / "lib" / name)
    print(f"[OK] CTranslate2 DLL -> {build / 'lib' / 'libctranslate2.dll'}")


def fetch_msys2_headers(build: Path) -> None:
    for name, url in MSYS2_PKGS:
        dest = build / name
        if not dest.exists() or dest.stat().st_size < 1024:
            download(url, dest)
        if (build / "clang64").exists() and name.startswith("headers"):
            continue
        print(f"[EXTRACT] {name}")
        extract_zst_tar(dest, build)


def fetch_ctranslate2_headers(build: Path) -> None:
    include_root = build / "include"
    marker = include_root / "ctranslate2" / "translator.h"
    if marker.exists():
        print("[SKIP] CTranslate2 headers already present")
        return
    repo = build / "CTranslate2-src"
    if not (repo / "include" / "ctranslate2").exists():
        print("[CLONE] CTranslate2 headers...")
        subprocess.run(
            ["git", "clone", "--depth", "1", "https://github.com/OpenNMT/CTranslate2", str(repo)],
            check=True,
        )
    for sub in ("ctranslate2", "nlohmann", "half_float"):
        shutil.copytree(repo / "include" / sub, include_root / sub, dirs_exist_ok=True)
    print(f"[OK] headers -> {include_root}")


def download_hf_models() -> None:
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "huggingface_hub", "-q"])
        from huggingface_hub import snapshot_download

    cache = Path.home() / ".cache" / "lean_copilot"
    cache.mkdir(parents=True, exist_ok=True)
    for repo_id in HF_MODELS:
        name = repo_id.split("/")[-1]
        target = cache / name
        if target.exists() and any(target.iterdir()):
            print(f"[SKIP] model {name}")
            continue
        print(f"[HF] downloading {repo_id} ...")
        snapshot_download(repo_id=repo_id, local_dir=str(target))
        print(f"[OK] {target}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reglib", default="Reglib", help="Path to Reglib Lake package")
    ap.add_argument("--skip-models", action="store_true")
    ap.add_argument("--skip-native", action="store_true")
    args = ap.parse_args()

    reglib = Path(args.reglib).resolve()
    build = reglib / ".lake" / "packages" / "LeanCopilot" / ".lake" / "build"
    if not build.exists():
        raise SystemExit(f"LeanCopilot build dir not found: {build}\nRun: cd {reglib} && lake update")

    if not args.skip_native:
        copy_openblas(build)
        fetch_ctranslate2_dll(build)
        fetch_msys2_headers(build)
        fetch_ctranslate2_headers(build)
        print("\n[NEXT] cd Reglib && lake build LeanCopilot && lake build CopilotProbe")

    if not args.skip_models:
        download_hf_models()
        print("\n[DONE] Models in ~/.cache/lean_copilot/")


if __name__ == "__main__":
    main()
