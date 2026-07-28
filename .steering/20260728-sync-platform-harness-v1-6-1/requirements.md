# 要求内容

## 概要

`inner-platform-harness` を、社内向け配布ハーネスとしての情報境界と運用契約を保持したまま、公開済みの上流正典 `platform-harness v1.6.1 / 6b13140461916167ae1144055e2652d8aa20fa20` へdirect syncする。

- **関連Issue**: https://github.com/kanan4gh/inner-platform-harness/issues/5
- **使用ハーネス**: Codex
- **軽量パス**: 非適用

## パス判定

- [x] 1. 既存パターンの踏襲のみで、新しいアーキテクチャ要素・新規依存を導入しない
- [ ] 2. 変更対象が3ファイル以下(テスト除く)
- [ ] 3. 対象文書の更新が不要
- [x] 4. データ形式・API契約の破壊的変更がない

**判定理由**:

- 基準1: 満たす。前回v1.5.1同期で確立した排他的manifestによるdirect syncを踏襲し、新しい依存・レイヤー・抽象化を導入しない。
- 基準2: 満たさない。正典差分は49pathで、steering履歴6pathを除外しても中立コア、3ハーネスアダプタ、lint、テストを含む多数のファイルを変更する。
- 基準3: 満たさない。`AGENTS.md`、ハーネスアダプタ、`docs/procedures/`、`docs/harness-guide.md`、`docs/external-automation-policy.md`の方針・条件・手順そのものを更新する。
- 基準4: 満たす。tasklist状態を追加するが、状態なしの旧tasklistを後方互換で扱う。公開API・永続データの破壊的変更はない。

**結論**: 通常パス

## G3受け入れの要否判定

- **判定**: 要
- **対象**: Claude Code / Codex / Kiro
- **理由**: Claude CodeのStop hook登録、Codexのhook定義、Kiroのhook登録を削除し、各ハーネスの設定・アダプタ説明・終了挙動を変更するため。
- **実施主体**: 計画承認を根拠に、Codexが3ハーネスの対話型CLIをPTYで自動操作する。`CLAUDE_CONFIG_DIR` / `CODEX_HOME` / `KIRO_HOME`で設定ホームを、`CLAUDE_CODE_TMPDIR` / Codex `sqlite_home` / `KIRO_CHAT_LOG_FILE`でruntime / logをハーネス別に隔離し、既存ユーザー設定を変更しない。`DISABLE_UPDATES=1` / `check_for_update_on_startup=false` / `app.disableAutoupdates=true`でCLI更新を抑止する。ログイン・MFA・GUI専用操作等の阻害時だけユーザーへ最小操作を依頼する。
- **確認軸**: 新しいスキル/コマンドの実読込、承認境界、通常応答が未完了tasklistでブロックされないこと、`pause / resume / complete`と通常/完了lintが共通経路として機能すること。
- **GUI境界**: GUI IDEは標準合格条件にせず、変更対象にGUI専用能力がある場合だけ例外確認する。
- **限定操作**: 各ハーネス専用の`/private/tmp/inner-platform-harness-g3-*` clone・設定ホーム・runtime内で、fixture読取、`acceptance-scratch/{harness}.txt`への`g3-write-ok`書込、`pwd`を各1回確認する。trust / read / write / shellは単発確認だけとし、永続許可・外部API・リモート変更を行わない。

## 背景

`inner-platform-harness`は`platform-harness v1.5.1`まで同期済みである。上流v1.6.0ではStopフックによる応答終了ブロックを廃止し、tasklistの`active / paused / complete`状態、明示的な状態遷移、通常lintと完了lint、対象steeringを固定する最終品質ゲートへ移行した。v1.6.1では、`--steering`省略時のlatest tasklist探索にもproject root境界検査が適用された。

一方、innerは社員向けの特殊ハーネスであり、個人版正典の単純複製ではない。社内配布用の`SOURCE: inner-platform-harness`、履歴なし`git archive`配布、空の派生台帳、distribution hygiene lint、6検査のローカル品質ゲート、社内向けREADMEと外部自動化ポリシーを維持する必要がある。

## ユースケースの軸

> 社員が、社内情報境界を維持した最新のSDDハーネスを、Claude Code・Codex・Kiroのいずれでも同じ状態遷移とローカル品質ゲートを使って利用できる。

## 展開preflight

- 対象remote: `kanan4gh/inner-platform-harness`
- default branch / OID: `main / a888e3be500aaf4f79d397e871109e55963953f0`
- remote確認日時・方法: 2026-07-28 / GitHub APIとfresh clean clone
- archive / template状態: `archived=false / is_template=true`
- visibility: public（現状記録。今回変更しない）
- local checkout: 既存checkoutはcleanだが`main`がremoteより4commit古いため参照専用
- dirty / ahead / behind: 既存checkout `clean / 0 / 4`、作業clone `clean / 0 / 0`
- active Issue / PR / branch: preflight時点のopen Issue / PRは0件。マージ済みv1.5.1 branch/worktreeは参照用で今回の変更と競合しない
- Issue / branch: `#5 / feature/sync-platform-harness-v1-6-1`
- 同期元: `platform-harness v1.6.1 / 6b13140461916167ae1144055e2652d8aa20fa20`
- 比較元: `platform-harness v1.5.1 / bb125b52eaf7c603c612f363bbd5960f46f3d367`
- bootstrap executor: 不要（v1.5.1時点でcurrent-neutralかつCodexアダプタ導入済み）
- authority handoff: 既存mainの`AGENTS.md`とCodexアダプタが有効。v1.6.1統合後は新しい状態遷移・lint契約を使用する
- 作業隔離: fresh clean clone `/private/tmp/inner-platform-harness-sync-v1-6-1`

## 実装対象の機能

### 1. v1.6.1中立コアの反映

- Stopフックを廃止し、steeringライフサイクル状態と明示的状態遷移へ移行する。
- 通常lintと完了lintを分離し、最終品質ゲートが対象steeringを明示できるようにする。
- latest tasklist探索をproject root境界内に限定する。

### 2. 3ハーネスアダプタの同期

- Claude Code、Codex、KiroからStop hook定義・登録・実装を削除する。
- add-feature / steeringアダプタとREADMEを、新しい状態遷移・終了非ブロック契約へ合わせる。
- Claude Codeの編集リマインドは非強制の補助として保持する。

### 3. 社内配布境界の保持

- `SOURCE: inner-platform-harness`、社員向けREADME、空の派生台帳、履歴なし配布を保持する。
- distribution hygiene lintと6検査のlocal quality gateを保持し、新しい`--steering`引数を統合する。
- 会社側でSOURCEを変更するときはdistribution hygiene policyも同時更新させ、空台帳でも明示された初回remoteのG0を開始できるようにする。
- 上流の実作業steering、個人プロジェクト台帳、個人パス、上流Git履歴を取り込まない。

## 受け入れ条件

### 正典同期

- [ ] 同期元v1.6.1と比較元v1.5.1のtag commitが固定されている。
- [ ] canonical 49pathがReplace / Add / Merge / Excludeへ重複・欠落なく分類されている。
- [ ] Replace / Add対象がv1.6.1のcanonical blobと一致し、削除対象が存在しない。
- [ ] 上流の実作業steering 6pathが含まれていない。

### 社内配布境界

- [ ] `AGENTS.md`のSOURCEとinner固有の永続文書一覧が保持されている。
- [ ] `docs/derived-projects.md`は空の配布用台帳のままである。
- [ ] distribution hygiene lintと会社向け`git archive`境界が維持されている。
- [ ] README、パッケージ名、6検査の品質ゲートがinner向けのままである。
- [ ] 状態変更とPR前ゲートが対象steeringを明示し、会社側SOURCE変更とpolicy更新が連動する。

### 検証と配布

- [ ] pytest、ruff、basedpyright、steering lint、metered automation lint、distribution hygiene lintが成功する。
- [ ] 状態遷移、通常/完了lint、latest境界拒否、配布archiveを実データで観察する。
- [ ] 3ハーネスのG3対話型受け入れ結果が`acceptance-record.md`に記録される。
- [ ] G3は実行エージェントが対話型CLI + PTYで自動実施し、各ハーネスの操作をユーザーへ差し戻さない。
- [ ] 3ハーネスのtrustと単発許可が公式環境変数で切り替えた使い捨て設定ホームへ隔離され、既存ユーザー設定・trust store変更が0件である。
- [ ] 3ハーネスのruntime / logが使い捨て領域へ隔離され、既存runtime / log領域へのG3由来の書き込みが0件である。
- [ ] G3中のCLI自動更新・手動更新が0件で、記録したバージョンがセッション中に固定される。
- [ ] 既存設定ホームから認証情報や設定を使い捨て環境へコピーせず、GUIは専用能力の例外確認に限定される。
- [ ] GitHub Actions自動runと従量課金型LLM headless modeの起動が0件である。
- [ ] Conventional Commit、push、PR作成まで完了する。

## 成功指標

- canonical変更path集合49件のmanifest欠落・重複が0件である。
- Replace / Add対象のcanonical blob不一致が0件である。
- 配布衛生違反が0件で、会社向けarchiveの`.steering/`直下は`example/`だけである。
- 明示対象のローカル品質ゲートが全6検査で成功する。

## スコープ外

- repository visibility、team権限、branch protectionの変更
- 会社Organizationへのコピーまたは所有権移管
- `platform-harness`からの自動同期
- 上流側の派生プロジェクト台帳更新
- PRのマージとinnerのリリース作成

## 参照ドキュメント

- `AGENTS.md`
- `docs/procedures/add-feature.md`
- `docs/procedures/steering.md`
- `docs/procedures/derived-project-rollout.md`
- `docs/procedures/harness-acceptance.md`
- `docs/external-automation-policy.md`
- `docs/derived-projects.md`
- `.steering/20260726-sync-platform-harness-v1-5-1/`
