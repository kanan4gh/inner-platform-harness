# 要求内容

## 概要

個人プロジェクトの情報を持ち込まず、社員が各プロジェクトへ導入できる社内配布用SDDハーネステンプレート `inner-platform-harness` を作成する。

- **関連Issue**: https://github.com/kanan4gh/inner-platform-harness/issues/1
- **使用ハーネス**: Codex
- **同期元**: 個人版source repositoryの`origin/main` / `d25b91927838b91a194d6ff2ed3e18545630bad9`

## 背景

既存のハーネスには中立コア、複数ハーネス用アダプタ、品質ゲートに加え、個人プロジェクトの展開台帳、パイロット記録、個人環境のローカルパス、実作業のsteering履歴が含まれる。社員へ配布する版では、再利用可能な仕組みを維持しつつ、これらの個人固有情報と元リポジトリの履歴を分離する必要がある。

## ユースケースの軸

社員が `inner-platform-harness` をテンプレートとして複製し、個人プロジェクトの情報を目にすることなく、Claude Code・Codex・Kiroのいずれからも同じSDDプロセスを開始できる。

## 実装対象の機能

### 1. 独立した社内配布テンプレート

- 元リポジトリのGit履歴を継承しない非公開リポジトリとして構成する。
- リポジトリ名、パッケージ名、READMEを `inner-platform-harness` 用にする。
- GitHub上でテンプレートリポジトリとして利用できる状態にする。

### 2. 中立コアと3ハーネス対応の維持

- `AGENTS.md`、中立手順、Claude Code・Codex・Kiroアダプタを保持する。
- steering lint、外部有料自動化lint、ローカル品質ゲートと対応テストを保持する。
- GitHub Actionsは手動起動のみとし、標準品質ゲートはローカル実行とする。

### 3. 個人固有情報の除去

- 個人プロジェクトの名称・URL・展開状況を含む台帳を空の配布用台帳へ置換する。
- 派生プロジェクト展開手順から固有パイロット記録を除き、プレースホルダーによる一般例へ置換する。
- 個人環境の絶対パス、個人プロジェクト由来の設計例、実作業のsteering履歴を含めない。
- 配布対象ファイルに残留情報がないことを決定論的に検査できるようにする。

### 4. 社員向け導入手順

- READMEに目的、対象ユーザー、テンプレート利用方法、初回セットアップ、品質ゲート、Organizationへのコピー時の注意を記載する。
- 実行時状態、秘密情報、個人設定を配布対象へ含めないことを明記する。

## 受け入れ条件

### 独立した社内配布テンプレート

- [ ] `kanan4gh/inner-platform-harness` がprivateで、元リポジトリのGit履歴を継承していない。
- [ ] `feature/create-inner-platform-harness` からPRが作成される。
- [ ] リポジトリがtemplate repositoryに設定される。

### 中立コアと3ハーネス対応の維持

- [ ] 3ハーネスのアダプタ構造テストが成功する。
- [ ] `uv run python3 scripts/local_quality_gate.py` が成功する。
- [ ] GitHub Actions自動runと有料LLM headless modeの起動が0件である。

### 個人固有情報の除去

- [ ] tracked filesに個人プロジェクト名、元の個人アカウントURL、個人ホームディレクトリの絶対パスが残っていない。ただし、このリポジトリ自身のIssue URLなど作業証跡は対象外とする。
- [ ] 実作業のsteering履歴は本作業分以外に存在せず、テンプレート用exampleだけが配布される。
- [ ] 空の派生プロジェクト台帳と一般化された展開手順が整合する。

### 社員向け導入手順

- [ ] READMEだけでテンプレート利用開始とローカル品質ゲート実行まで辿れる。
- [ ] Organizationへコピー後に更新すべきリポジトリ固有メタデータが明記される。

## 成功指標

- ローカル品質ゲートの全項目が成功する。
- 残留情報検査の違反が0件である。
- GitHub Actions自動runと有料LLM headless modeの起動が0件である。

## スコープ外

- 会社Organizationへのコピー、所有権移管、社員・teamのアクセス権設定。
- 会社固有の技術スタック、セキュリティ規程、Organization名の埋め込み。
- 元リポジトリから社内版への自動同期。

## 参照ドキュメント

- `AGENTS.md` - SDDプロセス正典
- `docs/harness-guide.md` - ハーネス導入ガイド
- `docs/procedures/derived-project-rollout.md` - 派生プロジェクト展開手順
- `docs/external-automation-policy.md` - 外部有料自動化ポリシー
