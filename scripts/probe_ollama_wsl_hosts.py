#!/usr/bin/env python3
"""Run inside WSL: try common paths to Windows-hosted Ollama."""
from __future__ import annotations

import json
import re
import subprocess
import urllib.request


def candidates() -> list[str]:
    hosts: list[str] = ["127.0.0.1", "localhost"]
    try:
        ns = subprocess.check_output(
            ["grep", "-m1", "^nameserver ", "/etc/resolv.conf"], text=True
        ).split()[1]
        hosts.append(ns)
    except Exception:
        pass
    try:
        gw = subprocess.check_output(
            ["sh", "-c", "ip route show default | awk '{print $3}'"],
            text=True,
        ).strip()
        if gw:
            hosts.append(gw)
    except Exception:
        pass
    try:
        out = subprocess.check_output(["hostname", "-I"], text=True).strip()
        # first token only; not Windows host but sometimes useful
        if out:
            hosts.append(out.split()[0])
    except Exception:
        pass
    # dedupe preserve order
    seen: set[str] = set()
    uniq: list[str] = []
    for h in hosts:
        if h and h not in seen:
            seen.add(h)
            uniq.append(h)
    return uniq


def try_host(host: str) -> str:
    url = f"http://{host}:11434/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=3) as resp:
            data = json.loads(resp.read().decode())
        n = len(data.get("models", []))
        return f"OK ({n} models)"
    except Exception as exc:
        return f"FAIL ({exc})"


def main() -> None:
    print("WSL Ollama host probe:")
    for h in candidates():
        print(f"  http://{h}:11434 -> {try_host(h)}")


if __name__ == "__main__":
    main()
