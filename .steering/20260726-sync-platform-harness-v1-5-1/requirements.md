# 要求内容

## 概要

`inner-platform-harness` を、社内配布固有の情報境界を保持したまま、リリース済みの上流正典 `platform-harness v1.5.1` へ直接同期する。

- **関連Issue**: https://github.com/kanan4gh/inner-platform-harness/issues/3
- **使用ハーネス**: Codex
- **軽量パス**: 非適用

## パス判定

- [x] 1. 既存パターンの踏襲のみで、新しいアーキテクチャ要素・新規依存を導入しない
- [ ] 2. 変更対象が3ファイル以下（テスト除く）
- [ ] 3. 対象文書の更新が不要
- [x] 4. データ形式・API契約の破壊的変更がない

**判定理由**:

- 基準1: 満たす。リリース済み上流差分のdirect syncであり、新規依存や新規レイヤーを導入しない。
- 基準2: 満たさない。正典、手順、アダプタ、hook、lint、テストを含む30ファイル超を同期する。
- 基準3: 満たさない。`AGENTS.md`、ハーネスアダプタ、`docs/procedures/`の方針・条件・手順そのものを更新する。
- 基準4: 満たす。公開APIや永続データ形式を持たないプロセスハーネスの更新である。

## G3受け入れ要否

- **判定**: 要
- **理由**: Claude Code・Codex・KiroのStop hook実装と、各ハーネスのadd-feature実行面を更新するため。
- **対象**: Claude Code / Codex / Kiro
- **実施方法**: 候補コミットを使い捨てclean cloneへ固定し、IDEまたは対話型CLIで未着手tasklistのfail-open、着手済み未完了tasklistのblock、完了tasklistのpassを確認する。従量課金型headless modeは使用しない。

## 背景

`inner-platform-harness v0.1.0` は、`platform-harness` のコミット `d25b91927838b91a194d6ff2ed3e18545630bad9`（v1.3.0直後）から履歴なしで抽出された。上流ではその後、軽量steering、承認・受け入れの終端ゲート順序、worktree走査除外、Stop hookのfail-open、関連する決定論的テストがv1.5.1までに追加された。

社内版には、空の派生プロジェクト台帳、一般化された展開例、配布衛生lint、社員向けREADME、上流履歴を持ち込まない方針があるため、上流ツリーの全面置換ではなく排他的manifestに基づくdirect syncが必要である。

## ユースケースの軸

社員が、社内情報境界を維持した最新のSDDハーネス正典を、Claude Code・Codex・Kiroのいずれからも同じ手順と品質ゲートで利用できる。

## 展開preflight

- 対象remote: `kanan4gh/inner-platform-harness`
- default branch / OID: `main` / `f0b258792452f3fa918341e9e506624c0a19e20f`
- remote確認日時・方法: 2026-07-26 / `git fetch origin --tags --prune`後の`origin/main`とGitHub API
- archive / template状態: archive=false / template=true
- visibility: public（現状を記録。今回変更しない）
- local checkout: `WORKSPACE_ROOT/inner-platform-harness`
- dirty / ahead / behind: clean / 0 / 0
- active Issue / PR / branch: open Issue 0件、open PR 0件。`feature/create-inner-platform-harness`はPR #2でマージ済みの残存branchであり競合しない
- 同期元: `platform-harness v1.5.1` / `bb125b52eaf7c603c612f363bbd5960f46f3d367`
- 前回同期元: `platform-harness` / `d25b91927838b91a194d6ff2ed3e18545630bad9`
- bootstrap executor: Codex
- authority handoff: v1.5.1の`AGENTS.md`汎用層とCodexアダプタをinner向けに統合し、段3・段4レビューを完了した時点
- 作業隔離: clean worktree / `/private/tmp/inner-platform-harness-sync-v1-5-1`

## 実装対象の機能

### 1. v1.5.1中立コアの反映

- 軽量パス判定と2/3ファイルsteering契約を反映する。
- add-featureのフェーズ別消化、終端品質ゲート、G3受け入れ順序を反映する。
- worktree走査除外とsteering lintの誤検知防止を反映する。

### 2. 3ハーネスアダプタの同期

- Claude Code・Codex・KiroのStop hookを、未着手tasklistはfail-open、着手済み未完了tasklistはblockする契約へ同期する。
- add-feature、implementation-validator、各READMEの説明を新しい正典契約へ合わせる。

### 3. 社内配布境界の保持

- `inner-platform-harness`のSOURCE表記、配布衛生lint、社員向け入口を保持する。
- 派生プロジェクト台帳を空のまま保持し、上流の個人プロジェクト台帳・パイロット記録を取り込まない。
- 上流の実作業steering履歴、個人パス、実行時状態を取り込まない。

## 受け入れ条件

### 正典同期

- [x] 同期元がv1.5.1のtag commitに固定されている。
- [x] 上流の対象差分がmanifestどおりReplace / Add / Mergeされている。
- [x] 上流の実作業steering履歴が含まれていない。

### 社内配布境界

- [x] `docs/derived-projects.md`は空の配布用台帳である。
- [x] `docs/procedures/derived-project-rollout.md`はinner起点の一般例だけを持つ。
- [x] distribution hygiene lintが違反0件で成功する。
- [x] 会社向け`git archive`の`.steering/`直下には`example/`だけが含まれる。
- [x] `README.md`、パッケージ名、SOURCE表記がinner向けのまま維持される。

### 検証と配布

- [x] pytest、ruff、basedpyright、steering lint、外部有料自動化lint、配布衛生lintが成功する。
- [ ] 3ハーネスのG3対話型受け入れ結果が`acceptance-record.md`に記録される。
- [ ] GitHub Actions自動runと有料LLM headless modeの起動が0件である。
- [ ] `feature/sync-platform-harness-v1-5-1`からPRが作成される。

## 成功指標

- ローカル品質ゲートが全緑になる。
- 配布衛生違反が0件である。
- 同期manifestの各pathが重複なく1分類へ属する。
- 上流v1.5.1由来の新規テストを含む全テストが成功する。

## スコープ外

- repository visibility、team権限、branch protectionの変更。
- 会社Organizationへのコピーまたは所有権移管。
- `platform-harness`からの自動同期機構。
- `platform-harness`側の派生プロジェクト台帳更新（PRマージ後の別作業）。
- `inner-platform-harness`のリリース作成とPRマージ。

## 参照ドキュメント

- `AGENTS.md`
- `docs/procedures/add-feature.md`
- `docs/procedures/steering.md`
- `docs/procedures/derived-project-rollout.md`
- `docs/external-automation-policy.md`
- `docs/derived-projects.md`
