# タスクリスト

## 作業状態

- **状態**: complete
- **状態更新日時**: 2026-07-28T11:30:12+09:00
- **使用ハーネス**: Codex

## 作業履歴

### 再開記録: 2026-07-28T10:45:58+09:00

- **使用ハーネス**: Codex
- **再開位置**: G3自動実行を標準化する手順・テストの更新
- **再開理由**: ユーザー指示によりG3の認知的負荷を除き、エージェントによる対話型PTY実施を標準化する

## タスク管理の原則

- `active`: 作業系列が継続中。未完了を許容する
- `paused`: 意図的な中断。有効な中断記録がある場合に未完了を許容する
- `complete`: 全タスクと振り返りが完了。未完了を許容しない
- 完了・技術的スキップは実態に合わせて即時記録する
- 「今日はここまで」はスキップではなく`scripts/steering_state.py --steering 20260728-sync-platform-harness-v1-6-1 pause`で記録する
- 最終品質ゲート、コミット、G3受け入れ記録、push、PRはチェックボックスにしない

---

## フェーズ1: 同期元とmanifestの固定（実装フェーズ / ステップ5）

- [x] 同期元`v1.6.1 / 6b131404`、比較元`v1.5.1 / bb125b52`、対象base`a888e3b`を再検証する
- [x] canonical 49pathをReplace 16 / Add 3 / Merge 24 / Exclude 6へ重複・欠落なく検証する（更新8・削除8・追加3・手動統合24・履歴除外6）
- [x] inner固有のPreserve集合、inner-only hardening 3path、Merge方針をpath単位で再確認する（gitattributes、distribution hygiene、pyproject/lockを保持し、README・空台帳・PRテンプレートを社内運用向けに補強）

## フェーズ2: canonical lifecycleの同期（実装フェーズ / ステップ5）

- [x] Replace更新8pathとAdd 3pathをcanonical v1.6.1 blobへ一致させる（11pathのworking tree blobをtag refと照合）
- [x] canonicalで削除されたStop hook実装・登録・テスト8pathを除去する（8pathすべて不在を確認）
- [x] Merge 24pathへcanonical lifecycle差分を統合し、innerの社内配布境界を保持する（状態変更とPRゲートの対象明示、3ハーネス別受け入れ記録、6検査表示を含む）

## フェーズ3: 同期境界の監査（実装フェーズ / ステップ5）

- [x] Replace / Addのblob一致、削除8pathとExclude 6pathの不在を確認する（canonical blob 11一致、削除8・履歴除外6不在）
- [x] `SOURCE: inner-platform-harness`、空台帳、社員向けREADME、パッケージ名、6検査ゲートを確認する（会社側SOURCE変更時のpolicy連動と、空台帳からの初回G0もテストで固定）
- [x] distribution hygiene、`git archive`、既存inner steering履歴の保持を確認する（candidate treeの154 entryを検査し、`.steering/`は`example/`の3ファイルだけ）
- [x] manifest外変更を分類する（canonical 49pathのうち履歴除外6を除く43製品path、独立レビュー起点のinner-only hardening 3path、inner側steering 3path）
- [x] G3を実行エージェントによる対話型CLI + PTY自動実施へ変更し、公式環境変数による設定ホーム分離、既存trust store不変、GUI例外境界を中立手順、3アダプタ、ポリシーへ反映する
- [x] G3自動実行・設定ホーム分離契約をharness acceptance / add-feature / derived rolloutの回帰テストへ追加する（増分44 testsとmetered automation lint成功）

## フェーズ4: 4段検証（ステップ6）

- [x] 段1: 設定ホーム分離を含むG3自動実行方針反映後の静的検証（213 tests、ruff、basedpyright 0 errors / 0 warnings、3 lint成功）
  - [x] `uv run pytest`（213 passed）
  - [x] `uv run ruff check .`（All checks passed）
  - [x] `uv run basedpyright`（0 errors / 0 warnings）
  - [x] `uv run python3 scripts/steering_lint.py`（active状態でexit 0）
  - [x] `uv run python3 scripts/metered_automation_lint.py`（passed）
  - [x] `uv run python3 scripts/distribution_hygiene_lint.py`（passed）
- [x] 段2: 状態遷移、通常/完了lint、latest境界拒否、6検査ゲート、配布archiveを実データで観察する（active→paused→active→complete、通常lint成功・active完了lint G1拒否・complete完了lint成功、latest外部symlinkはexit 1かつ外部SHA-256不変、明示steering付き6コマンド列、candidate archiveはexampleのみ）
- [x] 段3: 設定ホーム分離を含むG3自動実行方針の変更差分レビューと指摘対応を完了する（clean cloneだけでは不足するtrust隔離、CLI/GUI矛盾、runtime/log分離、自動更新抑止を順次修正。増分44 testsと3 lint成功）
- [x] 段4: G3自動実行方針のスペック準拠検証と永続ドキュメントレビューを完了する（前回指摘の振り返り先行記入も解消し、最終再レビューBlocker 0 / Major 0）

## フェーズ5: 振り返りとドキュメント更新（ステップ7）

- [x] G3自動実行方針を含む永続ドキュメント更新とレビューを完了する
- [x] G3自動実行方針を含むREADME類の更新を完了する
- [x] G3自動実行方針を反映して実装後の振り返りを更新する
- [x] 全テスト通過、lintエラーなし、リリース判断を更新する（213 tests、ruff、basedpyright、3 lint成功。MINOR提案）

> 全チェック完了後、`python3 scripts/steering_state.py --steering 20260728-sync-platform-harness-v1-6-1 complete --harness Codex`で`complete`へ遷移する。G3が必要なため、add-featureステップ8-Bの候補ゲート → 候補コミット → 3ハーネスG3 → `acceptance-record.md` → 最終ゲート → 記録コミット → push → PRの順に進む。

---

## 実装後の振り返り

### 実装完了日

2026-07-28

### 計画と実績の差分

**計画と異なった点**:

- 初期manifestはReplace更新16 / Merge 16だったが、独立レビューで状態変更対象・受け入れ記録・社内台帳の契約を補強したため、canonical分類をReplace更新8 / Merge 24へ再分類した。canonical 49pathの総集合は不変である。
- canonical変更外にREADME、空台帳、PRテンプレートのinner-only hardening 3pathを追加した。社内配布元と会社運用版の境界を実行可能にするためである。
- 当初のG3はユーザーが各ハーネスを操作する前提だったが、ユーザー指示を受け、計画承認後は実行エージェントが3つの対話型CLI + PTYを自動操作する方式へ変更した。

**新たに必要になったタスク**:

- 会社側SOURCE変更とdistribution hygiene policyの同時更新、空台帳からの初回G0、配布元では完了後も空台帳を維持する条件分岐を追加した。
- 状態変更・完了lint・PR前ゲートの対象明示と、Claude Code / Codex / Kiro別の受け入れ証跡を追加した。
- G3自動化に伴い、設定・trust・session、runtime / log、自動更新をハーネス別の使い捨て領域へ隔離し、既存ユーザー領域の起動前後不変を記録する契約を追加した。

**技術的理由でスキップしたタスク**:

- 該当なし。

### 学んだこと

**技術的な学び**:

- clean cloneは製品ファイルしか隔離しない。実機受け入れを安全に自動化するには、`CLAUDE_CONFIG_DIR` / `CODEX_HOME` / `KIRO_HOME`に加え、runtime / logとCLI更新経路も分離・抑止する必要がある。
- `latest`探索を互換用に残す場合でも、状態変更とPR証跡は日付付きsteering名を明示しないと、並行作業で別tasklistを操作し得る。
- 空の配布台帳は情報境界そのものなので、「未登録remoteから開始できること」と「配布元では完了後も書き込まないこと」を対で定義する必要がある。

**プロセス上の改善点**:

- 実機受け入れをユーザー操作へ差し戻すと、社内展開のたびに認知的負荷が発生する。計画承認へ限定操作を含め、外部阻害時だけ最小操作を依頼する方が自動化と権限境界を両立できる。
- 振り返りは4段検証より先に確定しない。レビュー指摘を反映してからフェーズ5で記録することで、tasklist状態と実績を一致させる。
- canonical blob一致だけでは社内版の実用性を保証できない。独立レビューで配布元・会社運用版・派生先の3者を分けて読むと、手順の循環や情報境界の矛盾を検出できる。

### 次回への改善提案

- 次回同期では、G3計画時点から設定ホーム、runtime / log、更新抑止、既存領域比較方法をハーネス別表へ記載する。
- 初回manifest作成時から「配布元では空、会社運用版では記録可」の読み書き条件を専用チェックリストにする。
- 状態変更・完了lint・PR前ゲートの例は、全アダプタで`--steering`を含むことを単一の回帰テストで横断検査する。

### リリース判断

| 観点 | 評価 |
|---|---|
| ユーザー価値のあるまとまりか | Yes |
| 未解決の重大バグ | なし |
| 適切なバージョン種別 | MINOR |

**提案**:

PRマージ後の次回inner-platform-harness releaseをMINORとして提案する。Stop hook廃止、明示的steeringライフサイクル、エージェント自動実施の3ハーネス受け入れ契約という利用者向け機能変更を含むため。リリース作成自体は今回のスコープ外とする。
