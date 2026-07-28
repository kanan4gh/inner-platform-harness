# 派生プロジェクトのオンデマンド展開手順

リリース済みinner-platform-harness正典を、ユーザーが指定した1つの派生プロジェクトへ安全に展開する手順である。会社Organizationへ配置済みの運用環境では候補と状態を`docs/derived-projects.md`で管理する。配布元の空台帳や未登録remoteでも、ユーザーが`OWNER/REPOSITORY`を明示すれば初回のG0を開始できる。

## 原則

- 展開単位は`1 inner-platform-harness release × 1 GitHub remote × 1 feature branch × 1 PR`とする。
- 台帳登録だけで展開を開始しない。G0でユーザーが対象remoteを指定する。台帳行の不存在は、明示指定されたremoteの初回preflightを妨げない。
- 対象リポジトリ内に独立Issue・steering・feature branchを作り、実行・承認・履歴を対象remoteへ閉じ込める。
- dirtyな既存checkoutを清掃・stash・上書きして移行を始めない。最新baseからclean worktreeまたはclean cloneを用意する。
- プロダクト固有層、技術スタック固有層、ハーネス固有差分を正典コピーで暗黙に上書きしない。
- GitHub Actions自動run、GitHub APIに依存する自動同期、有料LLM headless modeを必須経路にしない。

## 実行主体と権限

### 通常実行者

移行前の通常作業は、対象リポジトリの既存ハーネスと、それが対応するAIエージェントが実行する。たとえば旧Claude専用ハーネスの通常実行者はClaude Codeである。

### Bootstrap executor

旧ハーネスに現在のAIエージェント用アダプタがない場合、ユーザーがG0とG1で承認した本展開手順を一時的な権限根拠として、外部AIエージェントが`bootstrap executor`として移行できる。

- bootstrap executorは旧ハーネスを実行したことにしない。
- 旧`CLAUDE.md`等からプロダクト固有規則、技術スタック、テスト、Git運用を抽出して制約として守る。
- Claude固有のツール名・コマンド呼び出しを別エージェントが模倣しない。
- 対象リポジトリのIssue・steering・feature branchへ全変更と判断を記録する。
- Claude Codeをbootstrap executorに選ぶこともできるが必須ではない。

### Authority handoff

新しい`AGENTS.md`と対象エージェント用アダプタが導入され、人にレビューされた時点を`authority handoff`とする。handoff後の通常作業は対象リポジトリの新しい`AGENTS.md`と各アダプタに従う。

移行完了の証拠として、bootstrap executor、handoff対象commit、handoff後に使用したハーネスをtasklistへ記録する。

## 人による承認ゲート

| ゲート | 人の判断 | エージェントが準備するもの |
|---|---|---|
| G0 対象選択・阻害要因裁定 | 対象remoteを指定し、競合PR等をマージ・破棄・新移行へ引継ぎのいずれにするか裁定 | 候補・状態・競合範囲・再preflight結果 |
| G1 計画承認 | 対象側requirements / design / tasklistを承認 | 差分調査、manifest、検証計画、bootstrap executor |
| G2 競合裁定 | 既存固有設定を保持・置換・統合のどれにするか | ファイル単位の比較と選択肢 |
| G3 対話型受入 | Claude / Codex / KiroのUI・権限・終了非ブロック・状態/lint経路を実行エージェントが操作 | 無課金の実機手順と記録テンプレート |
| G4 マージ | PRをレビューしてマージ | ローカル品質ゲート、差分、受入証跡 |

G2はG1で裁定できなかった実競合がある場合だけ停止する。競合がなければ、G1で承認されたtasklist完了まで自動継続する。

## フェーズ0: G0対象選択とpreflight

### 対象の再確認

1. ユーザーが指定した`OWNER/REPOSITORY`を対象remoteとして特定する。`docs/derived-projects.md`に候補行があれば補助情報として照合するが、空または未登録でもG0を続行する。
2. GitHub上のdefault branch、archive / template状態、最新commitを確認する。
3. 利用するremote-tracking refをfetchした日時・方法とcommit OIDを記録する。
4. ローカルcheckoutのdirty / ahead / behind、active Issue / PR / branchを確認する。
5. 同一remoteの複数checkoutがある場合、勝手に統合せず、参照用・作業用・除外を区別する。
6. 同期元inner-platform-harness release tagとcommitを確認する。未リリースmainを同期元にしない。
7. clean worktreeまたはclean cloneの方式と予定pathを記録する。branch付き作業場所は、阻害要因の解消とbase OIDの再確認後、対象側Issueを作成してから確保する。

activeな移行PRや同じ正典ファイルを変更するbranchがある場合、対象を`on-hold`としてG1へ進まない。G0で既存PRをマージする、破棄する、新移行へ引き継ぐ、のいずれかを人が裁定し、阻害要因の解消とbase OIDを再preflightで確認してから対象側Issueを開始する。引継ぎを選んだ後のファイル単位の統合方法だけをG2で裁定する。

### Preflight記録

対象側の`requirements.md`または`tasklist.md`へ次を記録する。

```markdown
## 展開preflight
- 対象remote: OWNER/REPOSITORY
- default branch / OID: main / SHA
- remote確認日時・方法: YYYY-MM-DD / fetch済みremote-tracking ref等
- archive / template状態: ...
- local checkout: path（参考。一意キーではない）
- dirty / ahead / behind: ...
- active Issue / PR / branch: ...
- 同期元: inner-platform-harness vX.Y.Z / SHA
- bootstrap executor: Claude Code / Codex / Kiro / other
- 作業隔離: worktreeまたはclean cloneの方式と予定path（作成後に確定pathを記録）
```

## フェーズ1: 対象側SDDとG1計画承認

1. 対象リポジトリで同期用GitHub Issueを作成する。
2. `feature/sync-inner-platform-harness-vX-Y-Z`形式のfeature branchをclean隔離環境に作る。
3. 対象側の規則に従い、同期用steeringのrequirements / design / tasklistを作る。
4. 現在の正典、同期元release、派生固有差分を比較して同期manifestを作る。
5. bootstrap executorとauthority handoff時点を計画へ明記する。
6. G1で人が計画を承認した後、実装を開始する。

## フェーズ2: 同期manifestとG2競合裁定

```markdown
## 同期manifest

### Preserve（派生固有のまま保持）
- path — 保持理由

### Replace from canonical（正典で置換）
- path — inner-platform-harness release内のsource path

### Add from canonical（正典から新規導入）
- path — inner-platform-harness release内のsource path

### Merge manually（人の裁定が必要）
- path — 競合点と選択肢

### Exclude（同期・コミット対象外）
- path — cache / runtime state / duplicate copy等
```

- `Preserve`は対象リポジトリを正とする。
- `Replace`と`Add`はrelease tagの内容を正とし、コピー元commitを記録する。
- `Merge manually`はG2で選択肢を提示する。ユーザー裁定前に片方を上書きしない。
- `Exclude`は読み取り・コピー・コミットが不要な実行時資産を含む。秘密情報の内容を記録しない。
- manifest変更が承認済み計画を実質的に変える場合は、design / tasklistへ理由を記録して再承認する。
- manifestでは各具体pathまたは明示した文書sectionをちょうど1分類へ割り当てる。親directoryを分類する場合は例外subpathを同じ行で除外し、別分類との包含・重複を残さない。

## フェーズ3: 移行または直接同期

### Direct sync

`current-neutral`な対象では、同期元releaseと対象の共通正典ファイルを比較し、manifestに記載した差分だけを取り込む。既存のプロダクト固有層・技術スタック固有層を丸ごとinner-platform-harness版へ置換しない。

### Migrate then sync

1. 旧正典からプロダクト固有層・技術スタック固有層を抽出する。
2. 中立`AGENTS.md`へ汎用層と保持した固有層を配置する。
3. `docs/procedures/`とtemplatesを導入する。
4. 旧ハーネス資産を中立手順を参照する薄いアダプタへ移行する。
5. 必要なClaude / Codex / Kiroアダプタと決定論的品質ゲートを導入する。
6. 新しい正典とアダプタをレビューしてauthority handoffを記録する。
7. handoff後は対象の新`AGENTS.md`とアダプタで残りのtasklistを実行する。

## フェーズ4: 検証とG3対話型受け入れ

1. 対象固有の既存テスト、lint、型検査を実行する。
2. 導入したsteering lint、有料自動化lint、アダプタ構造テストを実行する。
3. docs変更を独立した文脈でレビューし、実装とsteeringの準拠を検証する。
4. アダプタ・権限・hooks変更についてG3要否と対象ハーネスを確定する。G3要の場合は実行エージェントがIDEまたは対話型CLI受け入れを行うが、実施自体はフェーズ5で状態を`complete`へ遷移し候補ゲートと候補コミットを終えた後に行う。認証・MFA・権限確認等で止まった場合は直ちにユーザーへ必要最小限の操作を依頼し、解消後に同じ固定commitから再開する。
5. GitHub Actions自動runと有料LLM headless mode起動が0件であることを記録する。

1つのハーネスが受け入れ不能でも、別ハーネスの合格で代替しない。能力差、代替した決定論的ゲート、未確認理由を記録する。

## フェーズ5: PR、G4マージ、台帳更新

1. tasklistへ同期元、manifest、bootstrap executor、authority handoff、検証を記録し、全チェック完了後に状態を`complete`へ遷移する。
2. 対象に合わせた`local_quality_gate.py`を単一入口とし、G3不要なら`add-feature.md`ステップ8-A、G3要ならステップ8-Bに従う。後者は候補ゲート → 候補コミット → G3 → `acceptance-record.md`へ記録 → 最終ゲート → 記録コミット → PRの順で行う。状態遷移・ゲート・記録をtasklistのチェックボックスにしない。
3. G4で人がPRをマージする。
4. 必要な対象プロジェクトreleaseを作成する。
5. 会社Organizationへ配置済みの運用版で、情報管理規程が台帳への対象remote記録を許す場合だけ、`docs/derived-projects.md`を別の台帳更新PRで更新する。配布元inner-platform-harnessでは台帳を更新せず、空のまま維持して対象側Issue・steering・PRを展開証跡とする。

```markdown
## 展開完了記録
- 同期元: inner-platform-harness vX.Y.Z / SHA
- 同期対象: [ファイルとセクション]
- 派生固有差分: [保持・手動統合した内容]
- bootstrap executor: ...
- authority handoff: commit SHA / 新しい実行ハーネス
- ローカル品質ゲート: [日時、結果]
- 対話型受け入れ: [ハーネス、結果。不要なら理由]
- GitHub Actions自動run: 0件
- 有料LLM headless mode: 0件
- PR / release: URL
```

## Stop条件

次の場合は推測で続行せず、台帳を`on-hold`または`decision-required`として人に判断を求める。

- 対象remote、default branch、同期元release / commitを一意に確定できない。
- remote-tracking refの鮮度を確認できず、安全なbaseを選べない。
- dirty / aheadな唯一のcheckoutしかなく、clean worktree / cloneを準備できない。
- activeな移行PRまたは同じ正典ファイルを変更するfeature branchがあり、G0で処遇を裁定して再preflightを完了していない。
- 派生固有層と正典の境界をG1 / G2で裁定できない。
- 対象固有テストの失敗を、正典による固有設定の上書きでしか解消できない。

## 一般化された展開例

配布版には実プロジェクトのpreflight結果やmanifestを含めない。会社Organizationへ配置後、ユーザーが`OWNER/REPOSITORY`を明示した作業で、次の最小形を具体化する。

### Preflight例

```markdown
- 対象remote: OWNER/REPOSITORY
- default branch / OID: main / COMMIT_SHA
- remote確認日時・方法: YYYY-MM-DD / fetch済みremote-tracking ref
- archive / template状態: false / false
- local checkout: WORKSPACE_ROOT/REPOSITORY
- dirty / ahead / behind: clean / 0 / 0
- active Issue / PR / branch: none
- 同期元: inner-platform-harness vX.Y.Z / SOURCE_COMMIT_SHA
- bootstrap executor: Codex
- 作業隔離: clean worktree / WORKSPACE_ROOT/REPOSITORY-sync
```

### Manifest例

| 分類 | 対象例 |
|---|---|
| Preserve | `src/`、対象固有tests、永続docsのプロダクト固有section |
| Replace from canonical | `AGENTS.md`の汎用層、中立`docs/procedures/`、薄いアダプタ |
| Add from canonical | 未導入の`.agents/`、`.codex/`、`.kiro/`、品質ゲートscripts |
| Merge manually | `.gitignore`、`pyproject.toml`、devcontainer、MCP設定例 |
| Exclude | cache、coverage、hooks state、secrets、ローカル設定 |

この例は承認済みmanifestではない。実展開では各具体pathまたは明示した文書sectionをちょうど1分類へ割り当て、G1で承認する。対象固有の依存関係・テスト・技術スタックを正典で暗黙に上書きせず、従量課金型headless modeを受け入れや移行に使わない。
