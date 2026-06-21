#!/usr/bin/env python3
"""Quick Ollama connectivity check (Windows localhost + WSL host IP)."""
from __future__ import annotations

import json
import subprocess
import sys
import urllib.error
import urllib.request


def fetch_tags(base: str, timeout: float = 5.0) -> tuple[bool, str]:
    url = f"{base.rstrip('/')}/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
        models = [m.get("name", "") for m in data.get("models", [])]
        qwen = [m for m in models if "qwen" in m.lower()]
        return True, f"{len(models)} models; qwen: {qwen or 'none'}"
    except Exception as exc:
        return False, str(exc)


def wsl_windows_host() -> str | None:
    try:
        out = subprocess.check_output(
            ["wsl", "grep", "-m1", "^nameserver ", "/etc/resolv.conf"],
            text=True,
            timeout=10,
        )
        return out.split()[1].strip()
    except Exception:
        return None


def main() -> int:
    ok = True
    for label, base in [
        ("Windows localhost", "http://127.0.0.1:11434"),
    ]:
        success, msg = fetch_tags(base)
        print(f"[{'OK' if success else 'FAIL'}] {label} ({base}): {msg}")
        ok = ok and success

    host = wsl_windows_host()
    if host:
        base = f"http://{host}:11434"
        success, msg = fetch_tags(base)
        print(f"[{'OK' if success else 'FAIL'}] WSL->Windows ({base}): {msg}")
        ok = ok and success
    else:
        print("[FAIL] Could not read WSL nameserver from /etc/resolv.conf")
        ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
