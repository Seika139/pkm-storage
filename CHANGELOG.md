# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Tagged Releases

- [unreleased](https://github.com/Seika139/pkm-storage/compare/v0.2.1...HEAD)
- [0.2.1](https://github.com/Seika139/pkm-storage/compare/v0.2.0...v0.2.1)
- [0.2.0](https://github.com/Seika139/pkm-storage/compare/v0.1.0...v0.2.0)
- [0.1.0](https://github.com/Seika139/pkm-storage/releases/tag/v0.1.0)

## [Unreleased]

### Added

- Windows のネイティブ環境で Framework の mise task を実行できるようにしました。`mise.toml` が Python `3.12` を mise 管理下で導入し、Bash が必要なのは初回 setup の bootstrap のみです ([#11](https://github.com/Seika139/pkm-storage/pull/11))

### Changed

- pkm-framework を v0.2.0 に更新し、配布される mise task が Bash script から Python file task になりました ([#11](https://github.com/Seika139/pkm-storage/pull/11))
- `git-secrets` は upstream が Windows 非対応のため、Linux / macOS でのみ導入するようにしました ([#11](https://github.com/Seika139/pkm-storage/pull/11))
- template 更新の手順を `mise install uv` + `mise exec uv -- uvx copier update` に変更し、旧バージョンから生成した Windows の repository でも更新を取り込めるようにしました ([#11](https://github.com/Seika139/pkm-storage/pull/11))
- Codex への MCP 登録を `mise run --raw -C` 方式に変更しました。旧 `mise/tasks/mcp.sh` の直指定で登録済みの端末は再登録が必要です ([#11](https://github.com/Seika139/pkm-storage/pull/11))
- `.gitattributes` で全ファイルの改行コードを LF に統一し、Windows で clone しても CRLF が混入しないようにしました ([#10](https://github.com/Seika139/pkm-storage/pull/10))

## [0.2.1] - 2026-10-10

### Changed

- Clarified Copier setup and Git synchronization instructions for repositories initialized by Terraform.

## [0.2.0] - 2026-10-10

### Added

- Copier で個人用 Storage repository を生成し、タグ付きテンプレート更新を取り込めるようにしました。

## [0.1.0] - 2026-10-09

### Added

- Initial PKM Storage template release.
