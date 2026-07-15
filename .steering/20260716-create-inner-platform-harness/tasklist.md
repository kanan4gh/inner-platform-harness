# タスクリスト

## 🚨 タスク完全完了の原則

**このファイルの全タスクが完了するまで作業を継続すること**

- 全てのタスクを`[x]`にする。
- 完了・スキップは実行直後に記録する。
- 技術的理由のない先送りを行わない。

## フェーズ1: 配布ベースの構築

- [x] 固定source commitとimport manifestを照合する
- [x] 再利用可能な中立コア、3ハーネスアダプタ、品質ゲート、テストを導入する
- [x] 元リポジトリの実作業steering履歴と実行時状態が含まれないことを確認する（本作業分と配布用example、空state保持用`.gitkeep`のみ）
- [x] `AGENTS.md`、`pyproject.toml`、リポジトリ内名称を`inner-platform-harness`向けに更新する

## フェーズ2: 個人固有情報の一般化

- [x] `docs/derived-projects.md`を実データのない配布用台帳へ置換する
- [x] `docs/procedures/derived-project-rollout.md`から固有パイロット記録を除き一般例へ置換する
- [x] `docs/ideas/`の個別プロジェクト由来記述を一般化し、不要な履歴文書を除外する（独立文書レビューで全source文書に個人経緯・旧構成が混在すると判明したため、初期ファイルを全面除外。利用者の下書き用という機能は維持）
- [x] 固有名称に依存する既存テストを一般仕様のテストへ更新する

## フェーズ3: 社員向け導線と配布衛生

- [x] 社員向けREADMEを作成する
- [x] 配布衛生lintを実装する
  - [x] 個人ホームディレクトリ絶対パスを検出する
  - [x] 実値が登録された派生プロジェクト台帳行を検出する
  - [x] source markerの形式違反を検出する
- [x] 配布衛生lintのユニットテストを追加する
- [x] 配布衛生lintを`local_quality_gate.py`へ統合する
- [x] Organizationコピー後の確認事項をREADMEへ記載する

## フェーズ4: 4段検証

- [x] 段1: 静的検証をすべて成功させる
  - [x] `uv sync`
  - [x] `uv run pytest`（148件成功）
  - [x] `uv run ruff check .`
  - [x] `uv run basedpyright`
  - [x] `uv run python3 scripts/steering_lint.py`（配送タスク完了状態の隔離fixtureで成功）
  - [x] `uv run python3 scripts/metered_automation_lint.py`
  - [x] `uv run python3 scripts/distribution_hygiene_lint.py`
  - [x] `uv run python3 scripts/local_quality_gate.py`（配送タスク完了状態の隔離fixtureで6検査すべて成功）
- [x] 段2: 配布衛生lintを実データへ実行し、違反0件の出力を観察する
- [x] 段2: source調査で把握した既知の個人固有語彙と絶対パス形式の残留が0件であることを観察する（`.steering/`の本Issue URLを除く）
- [x] 段3: 変更差分を独立した文脈でレビューし、tracked範囲・台帳表記・URL形式等の指摘を反映後、ブロッカーなしを再確認する
- [x] 段4: requirements/design/tasklistと実装の準拠を独立した文脈で検証する（ideas除外判断と欠落リンクを修正後、実装・文書の不足ブロッカーなし）
- [x] 段4: 永続ドキュメント変更を独立した文脈でレビューする（個人由来ideas除去・入口・devcontainer・品質ゲート表記を修正後、ブロッカーなし）
- [x] GitHub Actions自動runと有料LLM headless modeの起動が0件であることを確認する（Actions API `total_count: 0`、有料自動化lint成功）

## フェーズ5: 配布設定とPR

- [x] GitHub repositoryをprivateのtemplate repositoryとして設定する（GitHub APIで`private: true`、`is_template: true`を確認）
- [ ] Conventional Commits形式でcommitし、本文に`Closes #1`を記載する
- [ ] feature branchをpushする
- [ ] 概要・理由・変更・検証結果・関連Issueを含むPRを作成する
- [ ] PR URLとOrganizationへ手動コピーする際の注意点を報告する
- [x] 実装後の振り返りをこのファイルに記録する

---

## 実装後の振り返り

### 実装完了日

2026-07-16

### 計画と実績の差分

**計画と異なった点**:

- 計画時はsource側`docs/ideas/`の一部を一般化して残す想定だったが、独立文書レビューで全対象に個人経緯・旧構成・完了済みロードマップが混在し、`setup-project`がPRD入力として自動読込することが判明した。設計へ理由を追記し、初期ideasファイルを全面除外した。
- 配布衛生lintは固定include path方式から、`git ls-files`に基づくtracked/stagedファイル全体の走査へ変更した。本作業のIssue URLだけはorigin repositoryから導出してsteering内で許可し、個人識別子をpolicyへ固定しない設計にした。
- 派生台帳の空検査は、2テーブルと先頭pipeを省略したMarkdown表記を検出するよう強化した。

**新たに必要になったタスク**:

- 独立レビューで発見したURL表記、SOURCE表記、旧正典名、container homeの境界に対する回帰テストを追加した。
- 社員向け入口、devcontainerの同梱範囲、品質ゲート6項目、履歴なしコピーの確認方法を文書へ追加した。

**技術的理由でスキップしたタスク**:

- なし

### 学んだこと

**技術的な学び**:

- 個人固有情報の除去は既知語彙の検索だけでは不十分で、tracked集合の完全性、自然言語の由来、削除済み文書への隠しファイル内リンクを別々に検証する必要がある。
- private repositoryを一時配布元にしても、会社Organizationへ移す際はfork/mirrorではなく履歴なしimportとし、remote・visibility・template・権限を再確認する必要がある。

**プロセス上の改善点**:

- 配布版を作る計画では、初期manifestに「履歴として価値があるが新規プロジェクト入力へ混ぜてはいけない文書」を独立分類する。
- 個人情報境界のレビューでは通常ファイルだけでなく、`.claude/`、`.codex/`、`.kiro/`等の隠しアダプタも必ず同じ検索対象にする。

### 次回への改善提案

- 未記録

### リリース判断

**前提条件の確認**:

- [x] 全テスト通過（148件）
- [x] リントエラーなし
- [x] リリースノートに記載すべき変更内容が整理されている

**評価**:

| 観点 | 評価 |
|---|---|
| 今回の変更はユーザーにとって価値のあるまとまりか | Yes。社員が利用開始できる独立テンプレート一式 |
| 未解決の重大バグはないか | なし |
| 適切なバージョン種別 | MINOR（初期0.xリリース） |

**提案**:

PRマージ後、社内配布開始の基準点として`v0.1.0`を提案する。会社Organizationへの履歴なしコピーとアクセス権設定は別作業とする。
