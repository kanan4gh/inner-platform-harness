# タスクリスト

## 🚨 タスク完全完了の原則

**このファイルの全タスクが完了するまで作業を継続すること**

### フェーズとステップの対応

| フェーズ | 消化する add-feature ステップ |
|---|---|
| 実装フェーズ（フェーズ1〜3） | ステップ5 |
| 4段検証フェーズ | ステップ6 |
| 振り返りとドキュメント更新フェーズ | ステップ7 |
| 最終品質ゲートフェーズ | ステップ8 |

コミット、push、PR作成、G3受け入れ記録はチェックボックスにせず、add-featureステップ8-Bの順序で管理する。

## フェーズ1: 上流差分の機械的導入（実装フェーズ / add-feature ステップ5で消化）

- [x] v1.5.1 tag commitとReplace / Add manifestを再照合する（tag `bb125b52eaf7c603c612f363bbd5960f46f3d367`、初期候補はReplace 25 path、Add 3 path）
- [x] Replace候補25 pathをv1.5.1固定commitから導入する（import時に全blob hash一致。requirementsテンプレートの既存空白正規化保持とレビュー対応後の最終分類はReplace 20 path）
- [x] Add候補3 pathをv1.5.1固定commitから導入する（import時に全blob hash一致。契約テスト拡張後の最終分類はAdd 2 path）
- [x] 上流の実作業steering、個人台帳、パイロット、runtime stateが導入されていないことを確認する（明示archive 28 pathと既知語彙検索で不在を確認）

## フェーズ2: inner固有境界の手動統合（実装フェーズ / add-feature ステップ5で消化）

- [x] `AGENTS.md`へ軽量パスと永続文書一覧の契約を統合し、inner固有表記を保持する
- [x] `.claude/README.md`へv1.5.1のhook・add-feature・軽量パス説明を統合する（環流先のinner表記を保持）
- [x] `docs/external-automation-policy.md`へv1.5.1の禁止表現・走査境界を統合する（distribution hygieneの社内固有説明を保持）
- [x] `docs/procedures/derived-project-rollout.md`へG3終端順序をinner向けに統合する（一般化例とinner release起点を保持）
- [x] `docs/procedures/templates/requirements.md`へv1.5.1の軽量パス契約を統合し、既存のtrailing whitespace除去を保持する（静的差分検査で発見しmanifestを非重複のまま再分類）
- [x] `tests/procedures/test_derived_project_rollout.py`へG3順序の回帰契約を追加する
- [x] ドキュメントレビュー指摘を反映し、steeringモード2、軽量2ファイル、G3再実施の契約を正規化する（関連回帰テストを追加）
- [x] コードレビュー指摘を反映し、distribution hygiene lintへ非ignore未追跡ファイルの走査を追加する（候補ゲート前の新規ファイル漏れを防止）
- [x] Claude add-featureアダプタのゲート表示をinner固有の6検査へ合わせ、requirementsテンプレートは既存のtrailing whitespace除去を保持する
- [x] 再ドキュメントレビュー指摘を反映し、派生先のsteering追跡を許可して初回テンプレート作業steering 3 pathを配布対象から削除する
- [x] `git archive`の配布集合から日付付き保守steeringを除外し、`.steering/example/`だけを残す境界をREADME・属性・実archive回帰テストで固定する

## フェーズ3: 同期境界と品質実装の確認（実装フェーズ / add-feature ステップ5で消化）

- [x] 変更pathが同期manifestの排他的分類と一致することを確認する（最終レビュー修正後の製品差分40 path、Replace 20 / Add 2 / Merge 15 / Exclude-delete 3、重複・未分類0件）
- [x] 配布固有ファイル、空台帳、inner名称、履歴非継承方針が保持されていることを確認する（初期root `8cc0368`、identityとPreserve分類は保持、配布関連のMerge分類は設計どおり更新）
- [x] source調査で把握した個人固有語彙・絶対パス・上流SOURCE表記の残留を監査する（tracked製品範囲0件）
- [x] `uv sync`で依存環境を同期する（lock変更なし、検証用`.venv`をworktree内に作成）

## フェーズ4: 4段検証（add-feature ステップ6で消化）

- [x] 段1: 静的検証（最終レビュー修正後 pytest 223 passed / ruff passed / basedpyright 0 errors / 3 lint passed）
  - [x] `uv run pytest`（最終レビュー修正後223 passed）
  - [x] `uv run ruff check .`（All checks passed）
  - [x] `uv run basedpyright`（0 errors）
  - [x] `uv run python3 scripts/steering_lint.py`（完了状態へ変換した隔離fixtureでexit 0）
  - [x] `uv run python3 scripts/metered_automation_lint.py`（passed）
  - [x] `uv run python3 scripts/distribution_hygiene_lint.py`（passed）
- [x] 段2: 実挙動検証（lint CLIと3種類のStop hookの入出力を観察）
  - [x] 実リポジトリでdistribution hygiene lintの違反0件を観察し、steering lintは作業中C3のみ、完了状態の隔離fixtureではexit 0になることを観察する
  - [x] 3種類のStop hookを未着手・着手済み未完了・完了fixtureで直接実行し、全てでfail-open / block / passを観察する
- [x] 段3: コードレビューを独立した文脈で実施し、指摘対応を完了する（最終再レビューでblocker / nonblocking findingなし）
- [x] 段4: スペック準拠検証と永続ドキュメントレビューを独立した文脈で実施し、指摘対応を完了する（スペック準拠、docs 5.0/5）

## フェーズ5: 振り返りとドキュメント更新（add-feature ステップ7で消化）

- [x] 永続ドキュメントの追加更新要否を判断する（配布境界変更は`docs/external-automation-policy.md`へ反映済み。他の同期対象外docsは追加更新不要）
- [x] README.mdへ会社向け配布archiveの生成手順を反映したことを確認する（単純コピー・cloneを避け、`git archive`を使用）
- [x] 実装後の振り返りを記録する

## フェーズ6: 最終品質ゲート（add-feature ステップ8で消化）

- [x] 最終品質ゲートを全体で1回パス（1回目はC3のみ、完了記録後の2回目で全6検査成功）: `uv run python3 scripts/local_quality_gate.py`

> G3が必要なためadd-featureステップ8-Bを使う。候補ゲート2回、候補commit、3ハーネス対話型受け入れ、`acceptance-record.md`記録、記録後の最終ゲート、記録commit、push、PRの順に実施する。

---

## 実装後の振り返り

### 実装完了日

2026-07-26

### 計画と実績の差分

**計画と異なった点**:

- 初期manifestはReplace 25 / Add 3を候補としたが、inner固有差分とレビュー修正を排他的に再分類し、最終的に製品40 path（Replace 20 / Add 2 / Merge 15 / Exclude-delete 3）となった。
- 上流requirementsテンプレートのMarkdown hard breakは、既存のtrailing whitespace除去方針を保持してMergeとした。
- 初回作成steering 3 pathは削除し、現在以降の日付付きsteeringは開発リポジトリで監査証跡として保持しながら、会社向け`git archive`では`export-ignore`する境界へ変更した。

**新たに必要になったタスク**:

- steeringモード2の後続フェーズ先取り防止、Claude READMEの旧tasklist契約除去、G3再実施分岐の明確化を追加した。
- distribution hygiene lintを、tracked/stagedだけでなくignoreされていない未追跡ファイルも走査するよう補強した。
- 実配布archiveのsteering集合、派生先のsteering追跡、steering内の旧正典名例外が他の衛生規則を弱めないことを回帰テスト化した。

**技術的理由でスキップしたタスク**:

- なし

### 学んだこと

**技術的な学び**:

- `git ls-files --cached --others --exclude-standard`により、次のcommitへ入り得る新規ファイルをstage前でも決定論的に品質ゲートへ含められる。
- `.gitattributes`の`export-ignore`により、開発リポジトリの監査証跡と履歴なし配布artifactの内容を分離できる。
- Stop hookの未着手fail-open / 着手済み未完了block / 完了passは3ハーネスで同一の入出力として維持できた。

**プロセス上の改善点**:

- 正典同期は機械的なblob一致だけでなく、派生固有の品質ゲート件数・配布境界・アダプタ説明まで独立レビューする必要がある。
- 配布衛生の検証対象は「tracked files」ではなく「次のcommitへ入り得る非ignoreファイル集合」として定義すると、ゲートとcommitの隙間を防げる。
- 次回同期では初期候補と最終分類を最初から分けて記録し、件数更新の手戻りを減らす。

### 次回への改善提案

- 今回見つかった中立手順のフェーズ限定、G3再実施分岐、未追跡ファイル走査は、inner固有境界を除いて上流`platform-harness`への環流候補として別途評価する。
- 配布artifactテストは今後も実archiveを検査し、ファイル名だけの許可リスト検査へ弱めない。

### リリース判断

**前提条件の確認**:

- 全テスト通過: はい（223 passed）
- リントエラーなし: はい（ruff / basedpyright / 3 lint成功）
- リリースノートに記載すべき変更内容が整理されている: はい（v1.5.1同期、軽量steering、終端ゲート、Stop hook、配布archive境界）

**評価**:

| 観点 | 評価 |
|---|---|
| 今回の変更はユーザーにとって価値のあるまとまりか | はい |
| 未解決の重大バグはないか | 独立レビュー3系統でなし |
| 適切なバージョン種別 | minor（v0.2.0候補） |

**提案**:

PRマージ後にv0.2.0としてリリース可能。今回はPR作成までを実施し、リリース自体はユーザー判断とする。
