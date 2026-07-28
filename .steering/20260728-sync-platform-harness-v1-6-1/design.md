# 設計書

## アーキテクチャ概要

`platform-harness v1.5.1..v1.6.1`の49変更pathを入力とし、innerがv1.5.1正典blobのまま保持しているpathは機械的に置換・削除し、inner固有差分を持つpathは上流のsteeringライフサイクル変更だけを手動統合する。社内配布の情報境界はPreserve集合と、独立レビューで必要性を確認したinner-only hardening集合として固定する。

```text
platform-harness v1.5.1 ── diff 49path ── platform-harness v1.6.1
                                      │
                               sync manifest
                                      │
inner-platform-harness main ─ preserve / replace / add / merge / exclude
                                      │
                  distribution hygiene + 6-check quality gate
                                      │
                        candidate commit + 3-harness G3
                                      │
                                     PR
```

## 同期manifest

canonical `v1.5.1..v1.6.1`の49pathを、Replace 16（更新8・削除8）/ Add 3 / Merge 24 / Exclude 6へ一度だけ分類する。canonical変更path外のinner固有資産はPreserveとし、独立レビューで判明した社内運用上の欠落だけをinner-only hardeningとして3path変更する。

### Preserve（canonical 49path外の社内固有資産）

- `.gitattributes` — 日付付き保守steeringを配布archiveから除外する`export-ignore`
- `scripts/distribution_hygiene_lint.py` / `scripts/distribution_hygiene_policy.json` / `tests/distribution/**` — 社内配布情報境界
- `pyproject.toml` / `uv.lock` — innerパッケージ名と既存依存
- `.steering/example/**`と既存inner作業履歴 — テンプレート例とinner自身の監査証跡

### Inner-only hardening（canonical 49path外の3path）

- `README.md` — 会社側で`SOURCE`を変更するとき`allowed_source_markers`も同時更新し、明示対象の6検査ゲートを実施する手順を追加
- `docs/derived-projects.md` — 配布元の空台帳を維持したまま、会社配置後の初回未登録remoteをG0へ渡せる契約を追加
- `.github/pull_request_template.md` — PR証跡の品質ゲートへ`--steering`対象を必須化

### Replace from canonical（16path）

更新8pathをv1.6.1 blobで置換する。

- `.agents/skills/add-feature/SKILL.md`
- `.claude/settings.json`
- `.kiro/agents/sdd.json`
- `.kiro/skills/add-feature/SKILL.md`
- `docs/procedures/validate-implementation.md`
- `scripts/steering_lint.py`
- `tests/lint/test_steering_lint.py`
- `tests/lint/test_worktree_scan_exclusion.py`

削除8pathをv1.6.1に合わせて除去する。

- `.claude/hooks/check_tasklist_complete.py`
- `.codex/hooks.json`
- `.codex/hooks/check_tasklist_complete.py`
- `.kiro/hooks/check_tasklist_complete.py`
- `.kiro/hooks/state/.gitkeep`
- `tests/hooks/test_check_tasklist_complete.py`
- `tests/hooks/test_check_tasklist_complete_codex.py`
- `tests/hooks/test_check_tasklist_complete_kiro.py`

### Add from canonical（3path）

- `scripts/steering_state.py`
- `tests/adapters/test_stop_hook_absence.py`
- `tests/lint/test_steering_state.py`

### Merge manually（24path）

- `.agents/skills/steering/SKILL.md` — canonical状態遷移を採用し、innerレビューで状態変更対象の明示を必須化
- `.claude/README.md` — Stop hook廃止と状態遷移を統合し、innerの6検査・環流先表記を保持
- `.claude/commands/add-feature.md` — 新しい終端手順を統合し、innerの6検査表示を保持
- `.claude/skills/steering/SKILL.md` — canonical状態遷移を採用し、innerレビューで状態変更対象の明示を必須化
- `.codex/README.md` — hook廃止・状態遷移を統合し、innerの6検査説明を保持
- `.gitignore` — canonicalのhook state削除を反映し、innerの配布・steering追跡境界を保持
- `.kiro/README.md` — hook廃止・状態遷移を統合し、innerの6検査説明と明示対象を保持
- `.kiro/skills/steering/SKILL.md` — canonical状態遷移を採用し、innerレビューで状態変更対象の明示を必須化
- `AGENTS.md` — 汎用層をv1.6.1へ更新し、SOURCE、inner永続文書一覧、distribution hygiene、inner正典表記を保持
- `CLAUDE.md` — canonicalの薄いアダプタ更新を統合し、innerの環流先を保持
- `docs/external-automation-policy.md` — steering状態・Stop廃止を統合し、distribution hygieneを含む6検査を保持
- `docs/harness-guide.md` — 新しい操作契約を統合し、社員向け導入・配布説明を保持
- `docs/procedures/add-feature.md` — canonical終端順序を統合し、状態変更の明示対象を必須化
- `docs/procedures/derived-project-rollout.md` — v1.6.1の状態/G3順序を統合し、inner release起点の一般化と個人台帳非同梱を保持
- `docs/procedures/harness-acceptance.md` — Stop非ブロック・状態/lint受け入れへ更新し、innerの3ハーネス受け入れ境界を保持
- `docs/procedures/steering.md` — lifecycle状態・遷移・通常/完了lintを統合し、innerで先行補強したフェーズ限定契約を保持
- `docs/procedures/templates/harness-acceptance-record.md` — canonical記録項目を採用し、Claude / Codex / Kiro別の反復記録と自動run 0件証跡を追加
- `docs/procedures/templates/tasklist.md` — canonical状態契約を採用し、状態変更対象の明示を必須化
- `scripts/local_quality_gate.py` — canonicalの`--steering`指定を統合し、distribution hygieneを含む6番目の検査を保持
- `tests/adapters/test_harness_acceptance.py` — canonical受け入れ契約を統合し、明示対象・3ハーネス別記録・無課金証跡を固定
- `tests/adapters/test_kiro_adapter.py` — canonicalのhook不在契約を統合し、inner固有の構造期待を保持
- `tests/procedures/test_add_feature_ordering.py` — canonical順序契約を統合し、innerの6検査・アダプタ回帰を保持
- `tests/procedures/test_derived_project_rollout.py` — canonical手順契約を統合し、空台帳・一般化例を保持
- `tests/scripts/test_local_quality_gate.py` — `--steering`契約を統合し、6検査の固定順序を保持

全Merge pathは「canonicalのライフサイクル契約を採用し、inner固有の配布境界を保持する」とG1で一括裁定できる。実装中にこの原則で決められない競合が現れた場合だけG2へ進む。

### Exclude（6path）

- `.steering/20260728-reject-latest-external-symlink/requirements.md`
- `.steering/20260728-reject-latest-external-symlink/tasklist.md`
- `.steering/20260728-steering-lifecycle-without-stop-hooks/acceptance-record.md`
- `.steering/20260728-steering-lifecycle-without-stop-hooks/design.md`
- `.steering/20260728-steering-lifecycle-without-stop-hooks/requirements.md`
- `.steering/20260728-steering-lifecycle-without-stop-hooks/tasklist.md`

これらはplatform-harness側の実装履歴であり、inner側には本同期の独立したIssue・steeringを残す。

## コンポーネント設計

### 1. 中立steeringライフサイクル

**責務**:

- tasklistの`active / paused / complete`状態を正本化する。
- `pause / resume / complete`を明示操作として提供する。
- 通常lintは作業中を許容し、完了lintはPR対象だけcompleteを要求する。

**実装の要点**:

- `scripts/steering_state.py`と対応テストはcanonical blobをそのまま導入する。
- 状態なし旧tasklistの後方互換を維持する。
- latest探索と明示指定の両方をproject root境界検査へ通す。

### 2. 3ハーネスアダプタ

**責務**:

- Stopフックを削除し、通常応答終了と作業状態変更を分離する。
- 各ハーネスの入口から同じ中立手順・状態遷移・lintを使えるようにする。

**実装の要点**:

- Claude CodeのPostToolUseリマインドは非強制補助として残す。
- Codexはtasklistを自律更新し、Stop hook定義を持たない。
- Kiroはagent hook登録を削除し、workspace skillから状態遷移手順を参照する。

### 3. inner社内配布境界

**責務**:

- 個人版正典の名称、URL、実作業履歴を社員向けartifactへ混入させない。
- 6検査の品質ゲートと履歴なし配布を維持する。

**実装の要点**:

- inner固有文字列や検査件数をcanonical blobで上書きしない。
- distribution hygiene lintのpolicyとarchive回帰テストを変更しない。空台帳は維持しつつ、会社配置後の未登録remoteをG0へ渡せる運用だけを明文化する。
- Merge pathの変更後に個人固有語彙、絶対home path、SOURCE markerを監査する。

## データフロー

```text
1. v1.5.1..v1.6.1の49pathをmanifestへ固定
2. Replace更新8pathとAdd 3pathをv1.6.1 blobへ一致
3. canonicalで削除された8pathを除去
4. Merge 24pathへcanonical lifecycle差分とinner固有差分を統合
5. Exclude 6pathの不在、Preserve集合の不変、inner-only hardening 3pathの契約を検証
6. 6検査の静的検証と実挙動観察
7. 独立コード/スペック/docsレビュー
8. complete遷移、候補ゲート、候補commit、3ハーネスG3
9. acceptance記録後の最終ゲート、記録commit、push、PR
```

## エラーハンドリング戦略

- tag commit、base OID、manifest件数が一致しなければ同期を停止する。
- manifest外の変更が必要になった場合は分類と理由をdesign / tasklistへ即時追記する。
- inner固有表記の上書きやdistribution hygiene違反は除外拡張で隠さず、Merge内容を修正する。
- G1で裁定できない実競合が判明した場合だけG2としてユーザー判断を求める。
- G3不合格時は`resume`でactiveへ戻し、影響する検証段から再実施する。

## テスト戦略

### 静的検証

- `uv run pytest`
- `uv run ruff check .`
- `uv run basedpyright`
- `uv run python3 scripts/steering_lint.py`
- `uv run python3 scripts/metered_automation_lint.py`
- `uv run python3 scripts/distribution_hygiene_lint.py`

### 実挙動検証

- `pause / resume / complete`の状態遷移と通常/完了lintを隔離fixtureで観察する。
- latest外部symlinkを拒否し、外部tasklistが不変であることをCLIで観察する。
- `local_quality_gate.py --steering`が指定対象を完了検査へ渡し、distribution hygieneを6番目に実行することを観察する。
- `git archive`の`.steering/`直下が`example/`だけであることを観察する。
- Stop hook定義・登録・実装の不在を検査する。

### 独立レビュー

- 変更差分のコードレビュー
- requirements / design / tasklistと実装のスペック準拠検証
- 永続ドキュメント変更のドキュメントレビュー

### G3対話型受け入れ

- Claude Code / Codex / Kiroの変更した3ハーネスを対象にする。
- 候補ゲート成功後の固定commitをclean cloneし、利用許可済みIDEまたは対話型CLIで実施する。
- 従量課金型LLM headless modeは使用しない。

## 依存ライブラリ

新規依存なし。Python標準ライブラリと既存のpytest、ruff、basedpyrightを使用する。

## ディレクトリ構造

```text
.steering/20260728-sync-platform-harness-v1-6-1/
├── requirements.md
├── design.md
├── tasklist.md
└── acceptance-record.md  # G3実施後に追加

scripts/
├── steering_lint.py      # canonical v1.6.1
├── steering_state.py     # canonical v1.6.1から追加
├── local_quality_gate.py # innerの6検査を保持して統合
└── distribution_hygiene_* # Preserve
```

## 実装の順序

1. canonical tag、49path manifest、inner固有境界を検証する。
2. Replace / Add / Delete対象をcanonical v1.6.1へ同期する。
3. Merge 24pathをcanonical lifecycle + inner distribution方針で統合し、inner-only hardening 3pathを反映する。
4. manifest、blob、固有差分を監査する。
5. 4段検証、振り返り、complete遷移を行う。
6. 候補ゲート、候補commit、3ハーネスG3、記録後ゲート、記録commit、push、PRを行う。

## セキュリティ考慮事項

- 個人プロジェクト名・URL・絶対home path・実作業履歴をinner配布物へ再導入しない。
- secrets、認証情報、ローカル設定、hook runtime stateをコピーしない。
- GitHub Actionsを起動せず、従量課金型LLM headless modeを実行しない。
- canonical sourceは公開済みrelease tagとcommitへ固定する。

## パフォーマンス考慮事項

- 新しい検査は既存の小規模テキスト走査とpytestに限定する。
- 入れ子worktree、cache、runtime stateを重複走査しない既存境界を維持する。

## 将来の拡張性

次回同期も、前回同期releaseと新releaseの差分pathを排他的manifestへ分類する。社内版を上流のmirrorにせず、1 release × 1 remote × 1 feature branch × 1 PRの承認境界を維持する。
