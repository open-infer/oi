#!/usr/bin/env python3
"""Rewrite the tap's Homebrew formula and Scoop manifest for one release.

    python scripts/bump_tap.py --version <x.y.z> --sums SHA256SUMS --tap <clone>

Reads the five archive digests from ``SHA256SUMS`` (``<hex>  <name>`` lines,
basenames only) by their exact names, renders ``Formula/oi.rb`` and
``bucket/oi.json`` from the templates beside this script, and writes them into
the tap clone. It refuses if any of the five archives is missing from the sums.
When the rendered files equal the committed ones it reports ``unchanged`` and
exits 0 without touching anything, so a re-run after a partial publish is a
no-op. Stdlib only, no network; the workflow commits and pushes.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
TEMPLATES = _HERE / "templates"

# The five release archives, by the target the formula/manifest slot they fill.
# These names must match what the build produces (archive.py's ARCHIVE_NAMES).
ARCHIVE_NAMES: dict[str, str] = {
    "linux_x86_64": "oi-{v}-linux-x86_64.tar.gz",
    "linux_aarch64": "oi-{v}-linux-aarch64.tar.gz",
    "macos_arm64": "oi-{v}-macos-arm64.tar.gz",
    "macos_x86_64": "oi-{v}-macos-x86_64.tar.gz",
    "windows_x64": "oi-{v}-windows-x86_64.zip",
}


def parse_sums(text: str) -> dict[str, str]:
    """``{basename: hex}`` from SHA256SUMS; a directory part is refused."""
    out: dict[str, str] = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        digest, _, name = line.partition("  ")
        if not name or "/" in name or "\\" in name or len(digest) != 64:
            raise SystemExit(f"bump_tap: malformed SHA256SUMS line: {line!r}")
        out[name] = digest
    return out


def digests_for(version: str, sums: dict[str, str]) -> dict[str, str]:
    """target -> digest for the five archives of ``version``; refuses a missing one."""
    out: dict[str, str] = {}
    missing = []
    for target, pattern in ARCHIVE_NAMES.items():
        name = pattern.format(v=version)
        if name not in sums:
            missing.append(name)
        else:
            out[target] = sums[name]
    if missing:
        raise SystemExit(f"bump_tap: SHA256SUMS lacks: {', '.join(missing)}")
    return out


def render(template: str, version: str, digests: dict[str, str]) -> str:
    text = template.replace("{version}", version)
    for target, digest in digests.items():
        text = text.replace(f"{{sha256_{target}}}", digest)
    if "{sha256_" in text or "{version}" in text:
        raise SystemExit("bump_tap: a template placeholder was not filled")
    return text


def bump(tap: Path, version: str, sums_text: str) -> list[str]:
    """Write the formula and manifest into ``tap``; return the files that changed."""
    digests = digests_for(version, parse_sums(sums_text))
    changed = []
    for template_name, rel in (
        ("oi.rb.in", "Formula/oi.rb"),
        ("oi.json.in", "bucket/oi.json"),
    ):
        rendered = render(
            (TEMPLATES / template_name).read_text(encoding="utf-8"), version, digests
        )
        dest = tap / rel
        if dest.is_file() and dest.read_text(encoding="utf-8") == rendered:
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(rendered, encoding="utf-8")
        changed.append(rel)
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument("--version", required=True)
    parser.add_argument("--sums", required=True, help="Path to SHA256SUMS.")
    parser.add_argument("--tap", required=True, help="A clone of the tap repository.")
    args = parser.parse_args(argv)
    changed = bump(
        Path(args.tap), args.version, Path(args.sums).read_text(encoding="utf-8")
    )
    if not changed:
        print(f"bump_tap: unchanged, the tap is already at {args.version}")
    else:
        print(f"bump_tap: wrote {', '.join(changed)} for {args.version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
