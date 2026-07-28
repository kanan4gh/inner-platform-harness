# inner-platform-harness

社員がAIコーディングエージェントとスペック駆動開発（SDD）を始めるための社内テンプレートです。Claude Code、Codex、Kiroで同じ正典・手順・成果物を共有し、ローカルで再現可能な品質ゲートを提供します。

## 提供するもの

- `AGENTS.md`を正典とするSDDプロセス
- Claude Code、Codex、Kiro向けの薄いアダプタ
- requirements、design、tasklistを使うsteering手順
- pytest、ruff、basedpyright、steering規律、外部有料自動化、配布衛生を検査する単一ローカル品質ゲート
- AWS CLI、CDK、SAM CLIを含むdevcontainerスターター

## 利用開始

### 1. 会社Organizationへ配置する

このリポジトリを配布アーカイブとして会社Organizationへコピーし、privateのtemplate repositoryとして設定します。コピーには元リポジトリの履歴を含めず、会社側で新しいGit履歴を開始してください。

`git archive`は`.gitattributes`の`export-ignore`を適用し、テンプレート保守作業の日付付きsteeringを除外して`.steering/example/`だけを残します。任意の空ディレクトリを用意し、同期済みcommitから次のように展開してください。

```bash
git archive --format=tar HEAD | tar -x -C /path/to/empty/inner-platform-harness-export
```

展開後のディレクトリで新しいGitリポジトリを初期化し、会社Organizationへpushします。作業ツリーの単純コピーや元リポジトリのcloneを会社側テンプレートとして使うと、保守作業のsteeringまたは元のGit履歴が混入するため使用しません。

配置後に次を確認します。

- remoteが会社Organizationを指している
- repository visibilityが会社の規程に合っている
- teamと社員の権限が最小権限になっている
- `AGENTS.md`の`SOURCE`表記と`scripts/distribution_hygiene_policy.json`の`allowed_source_markers`が、同じ会社側の正典名を示している
- branch protection、secret scanning、監査設定が会社の規程に合っている

確認例:

```bash
git remote -v
git log --oneline --decorate
gh repo view --json nameWithOwner,visibility,isTemplate,defaultBranchRef
```

`git log`には会社側で作成した初期import以降の履歴だけが表示されることを確認します。forkやmirrorとして個人版の履歴を引き継いだ場合は配布を開始せず、履歴を持たない新規リポジトリへファイルをコピーし直します。

`SOURCE`を変更する場合は、同じコミットで`allowed_source_markers`も更新し、直後に`uv run python3 scripts/distribution_hygiene_lint.py`を実行します。初期import用の日付付きsteeringを作成した後は、公開前に6検査のローカル品質ゲートを`--steering`で対象明示して実行します。

### 2. テンプレートからプロジェクトを作る

GitHubの「Use this template」から新しいプロジェクトを作成します。作成後、`AGENTS.md`のプロダクト固有層と技術スタック固有層をプロジェクトに合わせて更新してください。

### 3. 開発環境を準備する

devcontainerを利用する場合は、Docker、VS Code、Dev Containers拡張を用意し、「Reopen in Container」を実行します。詳細は[`docs/harness-guide.md`](docs/harness-guide.md)を参照してください。

ローカル環境ではPython 3.12とuvを用意し、依存関係を同期します。

```bash
uv sync
```

### 4. 永続ドキュメントを作る

利用するハーネスで`setup-project`を実行します。永続ドキュメントは1ファイルずつ作成し、内容を承認してから次へ進みます。

### 5. 機能開発を始める

通常の会話で依頼するか、`add-feature`を実行します。Issue、feature branch、steering、実装、4段検証、PRまでの流れは`AGENTS.md`と[`docs/procedures/add-feature.md`](docs/procedures/add-feature.md)が定義します。

## 品質ゲート

PR前の必須入口は次の1コマンドです。

```bash
uv run python3 scripts/local_quality_gate.py --steering YYYYMMDD-task-name
```

GitHub Actionsは自動起動しない任意の手動ミラーです。従量課金型LLM headless modeを標準検証や受け入れに使用しません。G3実機受け入れは、計画承認後に実行エージェントが`CLAUDE_CONFIG_DIR` / `CODEX_HOME` / `KIRO_HOME`で切り替えた使い捨て設定ホームへtrustを隔離し、許可済みハーネスの対話型CLIをPTYで自動操作します。既存ユーザー設定は変更せず、GUIは専用能力の例外確認に限定します。隔離不能・ログイン・MFA・GUI専用操作等で阻害された場合だけ、ユーザーへ必要最小限の操作を依頼します。詳細は[`docs/procedures/harness-acceptance.md`](docs/procedures/harness-acceptance.md)を参照してください。

## ハーネスの選択

| ハーネス | アダプタ | 入口 |
|---|---|---|
| Claude Code | `CLAUDE.md`、`.claude/` | `/add-feature`等のコマンドとskills |
| Codex | `.codex/`、`.agents/skills/` | 「add-featureを実行して」等の会話 |
| Kiro | `.kiro/` | workspace skills、agents、`kiro-cli --agent sdd` |

各ハーネスのtrust、権限、能力差はそれぞれのREADMEを参照してください。

## 配布に含めないもの

- 個人プロジェクトの名称、URL、展開履歴
- 個人ホームディレクトリの絶対パス
- secrets、認証情報、ローカル設定
- hooksの実行時状態、cache、coverage成果物
- テンプレート保守作業の日付付きsteering（配布物には`.steering/example/`だけを含める）
- テンプレート作成元のGit履歴

`scripts/distribution_hygiene_lint.py`が構造的な再混入を検査します。会社固有の派生プロジェクト台帳を運用する場合は、Organization配置後に配布衛生ポリシーを会社の情報境界へ合わせて明示的に変更してください。

## 詳細資料

- [`AGENTS.md`](AGENTS.md): SDDプロセス正典
- [`docs/harness-guide.md`](docs/harness-guide.md): 導入とセットアップ
- [`docs/external-automation-policy.md`](docs/external-automation-policy.md): 外部有料自動化の境界
- [`docs/procedures/`](docs/procedures/): steering、機能追加、レビュー、受け入れ等の中立手順
