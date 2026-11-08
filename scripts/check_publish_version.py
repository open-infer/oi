#!/usr/bin/env python3
"""Refuse a publish whose version does not fit its target.

    python scripts/check_publish_version.py --version <v> --target {testpypi,pypi}

The release workflow deliberately lets a dispatch from ``main`` build a
``X.Y.Z.devN`` draft, so the version a publish is asked for is not trusted.
``pypi`` accepts only a final release ``X.Y.Z``; ``testpypi`` also accepts
``X.Y.Z.devN``, so a dev draft can be dry-run there. Anything else (a
pre-release, a ``v`` prefix, a two-part version, an empty string) is refused
for both targets, so a dev wheel can never reach PyPI. Exit 0 to proceed, 1
with the input and the target named on stderr otherwise.
"""

from __future__ import annotations

import argparse
import re
import sys

_FINAL = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
_DEV = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(\.dev[0-9]+)?$")


def accepts(version: str, target: str) -> bool:
    if target == "pypi":
        return bool(_FINAL.match(version))
    if target == "testpypi":
        return bool(_DEV.match(version))
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument("--version", default="")
    parser.add_argument("--target", required=True, choices=("testpypi", "pypi"))
    args = parser.parse_args(argv)
    if not accepts(args.version, args.target):
        print(
            f"check_publish_version: refusing version {args.version!r} for target {args.target}",
            file=sys.stderr,
        )
        return 1
    print(f"check_publish_version: {args.version} may go to {args.target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
