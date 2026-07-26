# 設計書

## アーキテクチャ概要

`platform-harness v1.5.1`と初回抽出元commitの差分を入力にし、社内版で未変更のpathは正典から機械的に置換し、社内版で一般化済みのpathは上流差分だけを手動統合する。

```text
platform-harness d25b919 (初回抽出元)
             │
             ├── diff ── platform-harness v1.5.1 / bb125b5
             │                         │
             │                    sync manifest
             │                         │
             v                         v
inner-platform-harness v0.1.0 ── preserve / replace / add / merge / exclude
                                       │
                         distribution hygiene + quality gate
                                       │
                         candidate commit + interactive G3
                                       │
                                      PR
```

## 同期manifest

### Preserve（派生固有のまま保持）

- `CLAUDE.md` — `inner-platform-harness`を正とする薄いアダプタ
- `pyproject.toml` / `uv.lock` — innerパッケージ名と既存依存。上流差分に依存変更なし
- `docs/derived-projects.md` — 実値を持たない空の社内配布用台帳
- `scripts/distribution_hygiene_policy.json` — 社内配布固有の衛生ポリシー
- `.steering/example/` — 派生プロジェクトが作るsteeringの配布例

### Replace from canonical（v1.5.1で置換）

- `.agents/skills/add-feature/SKILL.md`
- `.claude/agents/implementation-validator.md`
- `.claude/hooks/check_tasklist_complete.py`
- `.claude/skills/development-guidelines/guides/implementation.md`
- `.codex/hooks/check_tasklist_complete.py`
- `.kiro/README.md`
- `.kiro/agents/implementation-validator.md`
- `.kiro/hooks/check_tasklist_complete.py`
- `.kiro/skills/add-feature/SKILL.md`
- `docs/procedures/add-feature.md`
- `docs/procedures/templates/tasklist.md`
- `docs/procedures/validate-implementation.md`
- `scripts/metered_automation_policy.json`
- `scripts/steering_lint.py`
- `tests/adapters/test_harness_acceptance.py`
- `tests/hooks/test_check_tasklist_complete.py`
- `tests/hooks/test_check_tasklist_complete_codex.py`
- `tests/hooks/test_check_tasklist_complete_kiro.py`
- `tests/lint/test_metered_automation_lint.py`
- `tests/lint/test_steering_lint.py`

### Add from canonical（v1.5.1から新規導入）

- `tests/lint/test_worktree_scan_exclusion.py`
- `tests/procedures/test_lightweight_path_criteria.py`

### Merge manually（inner固有差分を保持して上流変更を統合）

- `AGENTS.md` — 軽量パスと永続文書一覧の契約を反映し、SOURCE・配布衛生・inner正典表記を保持
- `.gitattributes` — 日付付き保守steeringを`git archive`の配布集合から除外し、exampleだけを残す
- `.claude/README.md` — v1.5.1のhook・add-feature・軽量パス説明を反映し、環流先をinnerのまま保持
- `.claude/commands/add-feature.md` — v1.5.1の順序契約を反映し、inner固有の6検査ゲート表示へ補正
- `.gitignore` — v1.5.1のworktree除外を反映し、派生先が自身のsteeringを追跡できるようテンプレート固有ignoreを除去
- `docs/external-automation-policy.md` — v1.5.1の禁止表現・走査境界を反映し、distribution hygieneを含むinner品質ゲートを保持
- `docs/procedures/derived-project-rollout.md` — v1.5.1のG3順序契約を反映し、inner release起点・一般化例・パイロット非同梱を保持
- `docs/procedures/harness-acceptance.md` — v1.5.1のG3順序契約を反映し、製品修正と環境・権限だけの解消で再実施起点を分離
- `docs/procedures/steering.md` — v1.5.1の軽量パスを反映し、モード2の対象を実装フェーズへ限定
- `docs/procedures/templates/requirements.md` — v1.5.1の軽量パス契約を反映し、既存のtrailing whitespace除去を保持
- `README.md` — 会社Organizationへの履歴なし配置を、保守steeringも除外する`git archive`手順へ具体化
- `scripts/distribution_hygiene_lint.py` — v1.5.1同期後の候補ゲートで、ignoreされていない未追跡ファイルも走査
- `tests/distribution/test_distribution_hygiene_lint.py` — 未追跡・非ignoreファイルの走査とignore境界を回帰テスト化
- `tests/procedures/test_add_feature_ordering.py` — v1.5.1の順序テストへinner固有のsteering・Claude README・G3再実施契約を追加
- `tests/procedures/test_derived_project_rollout.py` — 空台帳と一般例の契約を保持し、v1.5.1のG3順序契約を追加

### Exclude（同期・コミット対象外）

- 上流の`.steering/**` — platform-harnessの実作業履歴
- inner初回作成時の`.steering/20260716-create-inner-platform-harness/**` 3 path — テンプレート作成元の実作業履歴として削除
- 上流の`docs/derived-projects.md`の実データ — 個人プロジェクト台帳
- 上流`docs/procedures/derived-project-rollout.md`のOutfit固有パイロット — 個人プロジェクト記録
- 上流`docs/ideas/**` — 初回配布時から除外している個人経緯・旧構成
- `.claude/hooks/state/**` / `.codex/hooks/state/**` / `.kiro/hooks/state/**` — 実行時状態
- `.venv/**` / cache / coverage / 一時archive — 再生成物
- 上流Git履歴とrelease tag — innerの独立履歴へ取り込まない

## コンポーネント設計

### 1. 機械的な正典同期

**責務**:

- v1.5.1のReplace / Add対象だけを固定commitから取り込む。
- import対象とmanifestの一致を検査する。

**実装の要点**:

- source worktreeの現在HEADではなく、必ずtag commit `bb125b52eaf7c603c612f363bbd5960f46f3d367`からarchiveする。
- sourceの`.steering/`、台帳、パイロットをarchive対象へ含めない。

### 2. inner境界の手動統合

**責務**:

- 上流のプロセス改善を取り込みつつ、社員向け配布物から個人情報・個人運用記録を排除する。

**実装の要点**:

- `AGENTS.md`は汎用プロセス更新とinner固有層をsection単位で統合する。
- 派生展開手順は名称置換だけでなく、上流の新しいG3終端順序を一般例へ移植する。
- 上流の実値をテストfixtureや文字列期待値へ再導入しない。

### 3. 検証と受け入れ

**責務**:

- 静的テスト、実データでのlint、独立レビュー、対話型G3を直列化する。

**実装の要点**:

- 実装後の4段検証では、段3コードレビューと段4スペック・ドキュメントレビューを独立文脈で行う。
- hook変更があるため、最終品質ゲート後の固定commitからclean cloneを作り、3ハーネスを対話型で受け入れる。
- G3結果を記録後、最終品質ゲートを再実行してから記録commitとPRを作る。

## データフロー

```text
1. v1.5.1 tagと初回抽出元commitの差分pathを列挙
2. targetが初回抽出元と同一のpathをReplace
3. v1.5.1で新規追加された対象テストをAdd
4. target固有差分またはレビューで必要性が判明した15 pathをMerge
5. inner初回作成時の実作業steering 3 pathを配布対象から削除
6. `git archive`の実配布集合が`.steering/example/`だけを含むことを検証
7. distribution hygieneと全静的検証を実行
8. 独立レビューとスペック準拠検証
9. 終端品質ゲート、候補commit、3ハーネスG3、記録後ゲート
10. pushとPR作成
```

## エラーハンドリング戦略

- tag commitが一致しない場合はarchiveを作らず停止する。
- manifest外の変更が発生した場合は、分類を追加してdesign / tasklistへ理由を記録する。
- 配布衛生lint違反は例外拡張で隠さず、該当内容を一般化または除外する。
- G3が不合格の場合は影響する4段検証行と最終品質ゲート行を未完了へ戻し、修正後に再実行する。

## テスト戦略

### ユニット・静的テスト

- 既存148件とv1.5.1追加テストを含むpytest全件
- ruff / basedpyright
- steering lint / metered automation lint / distribution hygiene lint
- manifest外変更と個人固有語彙の残留監査

### 実挙動・統合テスト

- 実リポジトリで`steering_lint.py`と`distribution_hygiene_lint.py`を実行して違反0件を観察する。
- Stop hookを未着手・着手済み未完了・完了のfixtureで直接実行し、exit/outputを観察する。
- Claude Code・Codex・Kiroの対話型環境で同じ3状態をG3受け入れする。

## 依存ライブラリ

新規依存なし。既存のPython標準ライブラリ、pytest、ruff、basedpyrightを使う。

## ディレクトリ構造

```text
.steering/20260726-sync-platform-harness-v1-5-1/
├── requirements.md
├── design.md
├── tasklist.md
└── acceptance-record.md  # G3実施後に追加

既存の中立コア・3ハーネスアダプタ・scripts・testsをmanifestどおり更新

git archiveによる会社向け配布物
└── .steering/example/  # 日付付き保守steeringはexport-ignore
```

## 実装の順序

1. Replace / Add対象をv1.5.1固定commitから取り込む。
2. inner固有差分と配布境界のレビュー修正を含む15 pathを手動統合する。
3. テンプレート作成元の実作業steering 3 pathを削除し、manifestと配布衛生境界を監査する。
4. 4段検証と振り返りを完了する。
5. 終端品質ゲート、候補commit、G3、記録後ゲート、PRを順に実施する。

## セキュリティ考慮事項

- 個人プロジェクト名・URL・絶対パスをinner配布物へ再導入しない。
- secrets、認証情報、ローカル設定、hook stateをコピーしない。
- GitHub Actions自動runや従量課金型LLM headless modeを起動しない。

## パフォーマンス考慮事項

- 新規worktree除外により、入れ子のcheckoutやcacheをlintが重複走査しない。
- 追加検査は小規模テキスト走査と既存pytestに限定する。

## 将来の拡張性

次回同期でも、前回同期元commitと新releaseの差分を同じ5分類へ割り当てる。自動同期は導入せず、1 release × 1 remote × 1 branch × 1 PRの承認境界を維持する。
