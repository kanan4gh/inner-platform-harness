# タスクリスト

## 作業状態

- **状態**: complete
- **状態更新日時**: 2026-07-28T12:00:12+09:00
- **使用ハーネス**: Codex

## 作業履歴

### 再開記録: 2026-07-28T11:43:49+09:00

- **使用ハーネス**: Codex
- **再開位置**: G3自動実行を最小運用へ整理
- **再開理由**: ユーザーの再開依頼と認証阻害時の即時依頼方針

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
- [x] G3の実行主体を実行エージェントへ変更し、専用基盤を追加せず既存対話型手順を使う最小運用へ整理する
- [x] 認証・MFA・権限確認等で止まった時点で直ちにユーザーへ必要最小限の操作を依頼する契約を追加する

## フェーズ4: 4段検証（ステップ6）

- [x] 段1: G3最小運用の静的検証（210 tests、ruff、basedpyright、3 lint成功）
  - [x] `uv run pytest`（最終再検証210 passed）
  - [x] `uv run ruff check .`（All checks passed）
  - [x] `uv run basedpyright`（0 errors / 0 warnings）
  - [x] `uv run python3 scripts/steering_lint.py`（active状態の未完了を許容してexit 0）
  - [x] `uv run python3 scripts/metered_automation_lint.py`（passed）
  - [x] `uv run python3 scripts/distribution_hygiene_lint.py`（passed）
- [x] 段2: 状態遷移、通常/完了lint、latest境界拒否、6検査ゲート、配布archiveを実データで観察する（active→paused→active→complete、通常lint成功・active完了lint G1拒否・complete完了lint成功、latest外部symlinkはexit 1かつ外部SHA-256不変、明示steering付き6コマンド列、candidate archiveはexampleのみ）
- [x] 段3: G3最小運用の変更差分をレビューする（過剰な設定隔離・runtime管理・更新抑止を除去し、実行主体と即時依頼の最小差分13pathに限定。blockerなし）
- [x] 段4: requirements / design / tasklistと永続ドキュメントの整合を確認する（実行エージェント、専用基盤を追加しないこと、認証阻害時の即時依頼、固定commitからの再開が一致）

## フェーズ5: 振り返りとドキュメント更新（ステップ7）

- [x] 永続ドキュメントへG3最小運用を反映する
- [x] README類の更新要否を判断し、root READMEとharness guideだけを更新する
- [x] 実装後の振り返りへ方針修正を記録する
- [x] 全テスト通過、lintエラーなし、リリース判断を更新する（210 tests、ruff、basedpyright、steering / metered automation / distribution hygiene lint成功）

> 全チェック完了後、`python3 scripts/steering_state.py --steering 20260728-sync-platform-harness-v1-6-1 complete --harness Codex`で`complete`へ遷移する。G3が必要なため、add-featureステップ8-Bの候補ゲート → 候補コミット → 3ハーネスG3 → `acceptance-record.md` → 最終ゲート → 記録コミット → push → PRの順に進む。

---

## 実装後の振り返り

### 実装完了日

2026-07-28

### 計画と実績の差分

**計画と異なった点**:

- 初期manifestはReplace更新16 / Merge 16だったが、独立レビューで状態変更対象・受け入れ記録・社内台帳の契約を補強したため、canonical分類をReplace更新8 / Merge 24へ再分類した。canonical 49pathの総集合は不変である。
- canonical変更外にREADME、空台帳、PRテンプレートのinner-only hardening 3pathを追加した。社内配布元と会社運用版の境界を実行可能にするためである。
- G3自動実行を完全な設定・runtime隔離基盤として広げたが、ユーザー意図は既存G3操作の代行だった。過剰な変更を取り消し、実行主体と認証阻害時の即時依頼だけを追加した。

**新たに必要になったタスク**:

- 会社側SOURCE変更とdistribution hygiene policyの同時更新、空台帳からの初回G0、配布元では完了後も空台帳を維持する条件分岐を追加した。
- 状態変更・完了lint・PR前ゲートの対象明示と、Claude Code / Codex / Kiro別の受け入れ証跡を追加した。
- G3を実行エージェントが行い、認証・MFA・権限確認等で停止した時点でユーザーへ最小操作を依頼する契約を追加した。

**技術的理由でスキップしたタスク**:

- 該当なし。

### 学んだこと

**技術的な学び**:

- `latest`探索を互換用に残す場合でも、状態変更とPR証跡は日付付きsteering名を明示しないと、並行作業で別tasklistを操作し得る。
- 空の配布台帳は情報境界そのものなので、「未登録remoteから開始できること」と「配布元では完了後も書き込まないこと」を対で定義する必要がある。

**プロセス上の改善点**:

- canonical blob一致だけでは社内版の実用性を保証できない。独立レビューで配布元・会社運用版・派生先の3者を分けて読むと、手順の循環や情報境界の矛盾を検出できる。
- レビュー起点でMerge内容が増えた場合は、manifest件数と完了証跡の旧数値を同時に更新し、集合比較を再実行する。
- G3の自動化は既存手順の操作主体を変えることを基本とし、認証阻害を検出したら追加調査より先にユーザーへ助けを求める。

### 次回への改善提案

- 次回同期では、初回manifest作成時から「配布元では空、会社運用版では記録可」の読み書き条件を専用チェックリストにする。
- 状態変更・完了lint・PR前ゲートの例は、全アダプタで`--steering`を含むことを単一の回帰テストで横断検査する。
- G3では専用自動化基盤を構築せず、既存の対話型手順を実行して認証阻害時だけ即時にユーザーへ依頼する。

### リリース判断

| 観点 | 評価 |
|---|---|
| ユーザー価値のあるまとまりか | Yes |
| 未解決の重大バグ | なし |
| 適切なバージョン種別 | MINOR |

**提案**:

PRマージ後の次回inner-platform-harness releaseをMINORとして提案する。Stop hook廃止、明示的steeringライフサイクル、3ハーネス受け入れ契約という利用者向け機能変更を含むため。リリース作成自体は今回のスコープ外とする。
