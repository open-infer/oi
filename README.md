# oi

`oi` points the coding harness you already use at OpenInfer and launches it.
One command sets the provider, the base URL (`https://api.openinfer.ai`), your
API key and the models, then starts the harness. Your harness's native
configuration is never modified, so each harness keeps working in its native
mode beside OpenInfer mode.

Supported harnesses: Claude Code (`claude`), Antigravity (`agy`), Pi (`pi`),
oh-my-pi (`omp`), OpenCode (`opencode`) and Kilo (`kilo`).

> This repository holds release binaries of the `oi` CLI and its publish
> workflow — not source.

## Install

macOS:

```sh
brew install open-infer/tap/oi
```

or with [uv](https://docs.astral.sh/uv/):

```sh
uv tool install openinfer-cli
```

Linux:

```sh
uv tool install openinfer-cli
```

Homebrew on Linux and the tarball on the
[Releases](https://github.com/open-infer/oi/releases) page are alternatives.

Windows (PowerShell):

```powershell
irm https://astral.sh/uv/install.ps1 | iex
uv tool install openinfer-cli
```

or with [Scoop](https://scoop.sh):

```powershell
scoop bucket add openinfer https://github.com/open-infer/homebrew-tap
scoop install oi
```

The zip on the Releases page is the fallback; see the Mark of the Web note
below.

WSL: install and run `oi` inside the distro, exactly as on Linux.

To run without installing, use `uvx`:

```sh
uvx openinfer-cli claude
```

## First run

Get an API key at <https://console.openinfer.ai>, then run

```sh
oi claude --reconfigure
```

— or the alias of any other harness — once, to write the configuration. `oi`
prompts for the key when it is missing.

## Usage

```sh
uvx openinfer-cli claude             # run without installing
uvx --from openinfer-cli oi claude   # the same, naming the command
oi <harness> -- <harness args>       # everything after -- reaches the harness
```

The six aliases are `claude`, `agy`, `pi`, `omp`, `opencode` and `kilo`.

## Notes

### tmux-resurrect (Linux)

tmux-resurrect restores a pane by typing its saved command again, so a pane
that `oi` launched comes back configured only if `oi` is on `PATH` — install
with `uv tool install`, brew or scoop. A pane started through `uvx` has no
`oi` to restore through.

`oi tmux-resurrect-hook` rewrites each saved harness pane to
`oi <harness> --continue` right after every save, while the panes are still
live. Add to `~/.tmux.conf`:

```tmux
set -g @resurrect-hook-post-save-layout 'oi tmux-resurrect-hook'
set -g @resurrect-processes '"~^oi (claude|agy|pi|opencode|kilo) " "~(^|/)claude( |$)->claude --continue" "~(^|/)pi( |$)->pi --continue" "~(^|/)agy( |$)->agy --continue"'
```

Anchor any rule you add on the program name (`~^oi `, `~(^|/)claude( |$)`):
resurrect types the restore command of every rule a pane matches, and a
substring rule like `~claude` would also match the rewritten
`oi claude --continue`.

### Shell completion

`oi completion` writes bash, zsh and fish completion scripts. No other shells
are supported.

### WSL

- Install the harness inside WSL. `oi` refuses a harness installed on the
  Windows side, because it cannot see the environment `oi` sets.
- WSL's `~/.config/openinfer` is separate from Windows'.

### Hand downloads on macOS

A binary downloaded in a browser is quarantined by Gatekeeper. Install with
uv, brew or scoop instead, or clear the quarantine bit:

```sh
xattr -d com.apple.quarantine oi.dist/oi
xattr -dr com.apple.quarantine oi.dist
```

The binaries are unsigned apart from the ad-hoc arm64 signature macOS
requires, and there are no plans to sign them.

### Hand downloads on Windows

A zip downloaded in a browser carries the Mark of the Web. Run
`Unblock-File` on it before extracting, or install with uv or scoop instead.

### Configuration and cache

Configuration lives at `~/.config/openinfer/config.json`, overridable with
the `OI_CONFIG_PATH` environment variable. Per-launch cache directories live
under `~/.cache/openinfer/`.

### License

The binaries are proprietary; see
[LICENSE](https://github.com/open-infer/oi/blob/main/LICENSE). This README and the
publish workflow are MIT.