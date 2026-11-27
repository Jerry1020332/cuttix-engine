#!/usr/bin/env python3
"""Rebrand this Concat fork as Cuttix (剪刻).

Concat's TRADEMARK.md asks every modified build to ship under its own name
and icon. Run this from the repository root after merging upstream:

    python3 cuttix/rebrand.py          # apply
    python3 cuttix/rebrand.py --check  # exit 1 if anything is left to change

It is idempotent. It changes only what a person sees or what keeps this
app's data apart from an official Concat on the same machine: the window
title, the app identifier (and so the settings folder), user-facing
strings in every locale, and the icons. Crate names, the binary's name
inside the bundle, the project file format and code comments stay as they
are, so upstream merges stay small.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRAND = json.loads((ROOT / "cuttix" / "brand.json").read_text("utf-8"))
NAME = BRAND["name"]  # "Cuttix"
IDENT = BRAND["identifier"]  # "app.cuttix.editor"

CHECK = "--check" in sys.argv
changed = []


def edit(rel, fn):
    p = ROOT / rel
    old = p.read_text("utf-8")
    new = fn(old)
    if new != old:
        changed.append(rel)
        if not CHECK:
            p.write_text(new, "utf-8")


def sub_once(pattern, repl):
    def fn(text):
        out, n = re.subn(pattern, repl, text, count=1)
        if n == 0 and repl not in text:
            sys.exit(f"rebrand: pattern not found: {pattern}")
        return out

    return fn


# 1. Identifier: a folder of its own, so an official Concat's settings and
#    recents are never read or moved, and our defaults (automation on) apply.
edit(
    "src/crates/concat-host/src/dirs.rs",
    lambda t: sub_once(r'pub const IDENTIFIER: &str = "[^"]+";', f'pub const IDENTIFIER: &str = "{IDENT}";')(
        sub_once(
            r'const FORMER_IDENTIFIER: &str = "[^"]+";',
            f'const FORMER_IDENTIFIER: &str = "{IDENT}.former";',
        )(t)
    ),
)

# 2. Window title.
edit("src/crates/concat/ui/app.slint", sub_once(r'title: "[^"]*";', f'title: "{NAME}";'))

# 3. Links on the start screen: our site and our source (AGPL source offer).
edit(
    "src/crates/concat/src/panes/start.rs",
    lambda t: sub_once(r'const SITE: &str = "[^"]+";', f'const SITE: &str = "{BRAND["site"]}";')(
        sub_once(r'pub const REPOSITORY: &str = "[^"]+";', f'pub const REPOSITORY: &str = "{BRAND["source"]}";')(t)
    ),
)

# 3b. Windows file properties (Explorer, Task Manager). The upstream
#     copyright line stays: the AGPL requires keeping it.
edit(
    "src/crates/concat/build.rs",
    lambda t: re.sub(r'\.set\("(ProductName|FileDescription)", "[^"]*"\)', lambda m: f'.set("{m.group(1)}", "{NAME}")', t),
)

# 4. Every locale: the word "Concat" in values (never keys) becomes the name.
WORD = re.compile(r"(?<![A-Za-z0-9_.-])Concat(?![A-Za-z0-9_-])")


def locale(text):
    data = json.loads(text)
    for k, v in data.items():
        if isinstance(v, str):
            data[k] = WORD.sub(NAME, v)
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


for f in sorted((ROOT / "src/crates/concat/locales").glob("*.json")):
    edit(str(f.relative_to(ROOT)), locale)

# 5. Icons: rendered from cuttix/icon.png over the files the build already uses.
if not CHECK:
    subprocess.run([sys.executable, str(ROOT / "cuttix" / "make_icons.py")], check=True)

if CHECK and changed:
    print("rebrand: not applied to:\n  " + "\n  ".join(changed))
    sys.exit(1)
print(f"rebrand: {'checked' if CHECK else 'applied'} ({len(changed)} files {'would change' if CHECK else 'changed'})")
