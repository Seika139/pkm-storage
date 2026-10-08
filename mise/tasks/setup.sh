#!/usr/bin/env bash
# This bootstrap stays in Storage so setup works before managed tasks exist.
#MISE description="Frameworkの実行環境と管理ファイルを準備する"

set -euo pipefail

STORAGE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$STORAGE_ROOT"
BOOTSTRAP="$STORAGE_ROOT/.pkm/setup_bootstrap.py"
if [[ -L "$STORAGE_ROOT" || ! -d "$STORAGE_ROOT" || -L "$STORAGE_ROOT/.pkm" || ! -d "$STORAGE_ROOT/.pkm" || -L "$BOOTSTRAP" || ! -f "$BOOTSTRAP" ]]; then
  printf '%s\n' "Storage setup paths must be regular files and directories, not symbolic links." >&2
  exit 1
fi
if ! command -v uv >/dev/null 2>&1; then
  printf '%s\n' "uv is not on PATH; run mise install and retry mise run setup." >&2
  exit 127
fi
exec uv run --python 3.12 --no-project "$BOOTSTRAP" "$STORAGE_ROOT"
