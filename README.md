# PKM Storage Template

<div align="center">
  <a href="https://github.com/Seika139/pkm-storage/releases/tag/v0.1.0">
    <img alt="version" src="https://img.shields.io/badge/version-v0.1.0-white.svg">
  </a>
  &nbsp;&nbsp;
  <a href="https://github.com/Seika139/pkm-storage/actions/workflows/ci.yml">
    <img alt="CI" src="https://github.com/Seika139/pkm-storage/actions/workflows/ci.yml/badge.svg?branch=main">
  </a>
</div>

この public repository は Copier template です。個人用 PKM を作るときは、Private な GitHub repository に Copier で初期生成し、必要な template 更新だけを後から取り込みます。知識データや secret 値はこの template に置かず、生成した Private repository で管理してください。

## Private repository を作成する

先に `~/programs/.github` の Terraform で空の Private repository を作り、その名前と owner を使って Copier でローカルへ生成します。Copier は repository の作成、Git の初期化、remote の設定、commit / push、`mise run setup` を実行しません。

```bash
mise install
uvx copier copy --vcs-ref "vX.Y.Z" gh:Seika139/pkm-storage pkm-storage-alpha
```

`vX.Y.Z` は Copier 設定を含む公開済み `pkm-storage` の tag に置き換えてください。質問される `repo_name` は生成先ディレクトリ名が初期値です。GitHub repository 名と違う場合だけ変更してください。`repo_owner` の初期値は `Seika139` です。これらの値は `.copier-answers.yml` に記録され、secret は質問にも記録にも含まれません。

生成先を Private repository の remote に接続し、初回 setup・push を手動で行います。

```bash
cd pkm-storage-alpha
git init -b main
git remote add origin git@github.com:Seika139/pkm-storage-alpha.git
mise install
mise run grant-permissions
mise run setup
git add -A
git commit -m "chore: initialize from pkm-storage template"
git push --set-upstream origin main
```

以後この Private repository を別の PC で使うときは、通常どおりその repository を clone して `mise run setup` を実行します。

## Template 更新を取り込む

Private repository で作業を commit し、working tree が clean な状態にしてから、取り込みたい `pkm-storage` のリリース tag を指定します。

```bash
mise install
uvx copier update --vcs-ref v0.2.0
git status --short
git diff
```

Copier は差分を作業ツリーへ適用します。競合は人が確認して手動で解決し、差分を review してから通常の Git 操作で commit / push してください。Copier 自身は remote 操作や Git 操作をしません。

`pkm-storage-vault/**`、`.gitignore`、`.pkm/pyproject.toml`、`.pkm/uv.lock` は初回生成時だけ seed され、その後の Copier 更新では変更も再生成もされません。個人ナレッジは vault に保存できます。Framework の更新は別経路で、`.pkm/pyproject.toml` の Git tag と `.pkm/uv.lock` を更新して取り込みます。

`CHANGELOG.md` と README の release / CI links は生成先の owner と repository 名に合わせます。生成直後の version badge は未リリースを表す `v0.0.0` で、初回 release workflow が実際の version とリンクに更新します。コピー元の release 履歴は生成先へ持ち込みません。

## Template 自身の変更

`README.md.jinja` と `CHANGELOG.md.jinja` は Copier が生成先向けに描画するファイルです。テンプレートと生成後プロジェクトに適用する変更は両方の表示先を意識し、公開 template の `CHANGELOG.md` では `## [Unreleased]` だけを更新してください。タグと Release はリリース時に追加します。
