# 設計書

## アーキテクチャ概要

リリース済み構成を機械的に複製するのではなく、確認済みsource commitから配布対象を選別して新規Git履歴へ取り込む。中立コアとアダプタは保持し、個人固有の運用データだけを一般化または除外する。

```text
personal source repository snapshot (read only)
  ├─ reusable neutral core / adapters / deterministic gates ── import
  ├─ reusable docs containing project examples ─────────────── sanitize
  └─ personal catalog / pilot records / steering history ───── exclude or generalize
                                      │
                                      v
                  inner-platform-harness feature branch
                                      │
                     quality gate + hygiene audit
                                      │
                                      v
                         pull request to clean main
```

## コンポーネント設計

### 1. 配布用SDDコア

**責務**:

- `AGENTS.md`と`docs/procedures/`をハーネス中立な正として配布する。
- Claude Code・Codex・Kiroの薄いアダプタを同梱する。

**実装の要点**:

- source commitを固定し、作業中の元リポジトリ変更を暗黙に取り込まない。
- `AGENTS.md`のSOURCE表記と`pyproject.toml`の名称を社内版向けに変更する。
- `.steering/example/`は保持し、元リポジトリの実作業履歴は取り込まない。

### 2. 一般化された展開情報

**責務**:

- 派生プロジェクト展開の仕組みを、個人プロジェクトの実績なしで再利用可能にする。

**実装の要点**:

- `docs/derived-projects.md`はスキーマと運用規則だけを持つ空の台帳へ置換する。
- `docs/procedures/derived-project-rollout.md`の固有パイロット節を、`OWNER/REPOSITORY`等のプレースホルダーを使う一般例へ置換する。
- 関連テストを、固有名称ではなく台帳構造、状態遷移、Stop条件、一般例の整合性に対する検証へ変更する。
- source側の`docs/ideas/`は個人ディスカッション、旧構成、完了済みロードマップが混在し、`setup-project`が全件をPRD入力にするため配布対象から除外する。配布版の`docs/ideas/`は社員が新規プロジェクトの下書きを任意配置するための空の論理ディレクトリとして扱う。

### 3. 配布衛生lint

**責務**:

- 配布物に個人環境由来の絶対パスや、許可されていないsource repository表記が再混入することを検出する。

**実装の要点**:

- tracked対象と同等の静的ファイル集合を走査するローカルlintを追加する。
- 個人名のdenylistそのものを配布物へ保存せず、構造的に危険なホームディレクトリ絶対パス、実値の派生台帳行、source marker規則を検査する。
- source側で把握した既知の個人プロジェクト語彙は、コミット前の一回限りの監査として別途照合する。
- lintを`local_quality_gate.py`に組み込み、ユニットテストを追加する。

### 4. 社員向けREADME

**責務**:

- 社員が用途、前提、導入、初回セットアップ、検証、運用境界を理解できる入口を提供する。

**実装の要点**:

- `inner-platform-harness`を社内向けテンプレートとして説明する。
- 会社Organizationへコピー後にremote、SOURCE表記、可視性、権限を確認するチェックを記載する。
- ローカル品質ゲートを必須、GitHub Actionsを任意の手動ミラーとして案内する。

## データフロー

### 社員が新規プロジェクトを開始する

```text
1. 会社Organization上のinner-platform-harnessから新規repositoryを作る
2. AGENTS.mdのプロダクト固有層・技術スタック固有層を更新する
3. setup-projectで永続ドキュメントを1件ずつ作成・承認する
4. add-featureでIssue・steering・feature branch・PRの流れを開始する
5. local_quality_gate.pyで決定論的に検証する
```

## エラーハンドリング戦略

- import元に予定pathがない場合は黙って省略せず、manifestとの差分として停止する。
- 衛生lintで違反が出た場合は、許可例外を広げる前に該当文書を一般化または除外する。
- sourceと配布版のテスト期待値が異なる場合は、機能削除ではなく配布版の一般化した仕様へテストを書き換える。
- GitHub metadata更新に失敗した場合は、コード変更と混同せずtasklistへ実績を記録して再実行する。

## テスト戦略

### ユニットテスト

- 配布衛生lintの正常系、絶対パス検出、実値台帳行検出、source marker違反を検証する。
- 一般化された派生プロジェクト台帳・展開手順の構造を検証する。
- 既存のhooks、adapter、steering、外部有料自動化lintテストを維持する。

### 統合テスト

- `uv run python3 scripts/local_quality_gate.py`をリポジトリルートで実行する。
- source調査で抽出した既知語彙と絶対パス形式をtracked filesに対して照合する。
- GitHub APIでprivate、template、default branch、PR、Actions run件数を確認する。

## 依存ライブラリ

新規依存ライブラリは追加しない。Python標準ライブラリと既存のpytestを使用する。

## ディレクトリ構造

```text
inner-platform-harness/
├── .agents/ .claude/ .codex/ .kiro/   # 3ハーネス用アダプタ
├── .steering/
│   ├── example/                         # 配布用例
│   └── 20260716-create-inner-platform-harness/ # 本作業証跡
├── docs/
│   ├── derived-projects.md              # 空の展開候補台帳
│   ├── procedures/                      # 中立手順
│   └── ideas/                           # 利用者が下書きを置く任意ディレクトリ（初期ファイルなし）
├── scripts/
│   ├── distribution_hygiene_lint.py     # 配布衛生lint
│   └── local_quality_gate.py             # 単一品質入口
├── tests/
│   └── distribution/                    # 配布版固有テスト
├── AGENTS.md
├── CLAUDE.md
├── README.md
└── pyproject.toml
```

## 変更manifest

### Import and rename

- 中立コア、3ハーネスアダプタ、devcontainer、手動Actions、MCP例、品質スクリプト、既存テスト、依存lockを固定source commitから導入する。
- `README.md`、`AGENTS.md`、`pyproject.toml`は社内版の名称と入口へ変更する。

### Sanitize

- `docs/derived-projects.md`
- `docs/procedures/derived-project-rollout.md`
- 固有の台帳・パイロット内容を期待するテスト

### Exclude

- 元リポジトリのGit履歴とrelease/tag
- 元リポジトリの実作業steeringディレクトリ
- source側`docs/ideas/`の個人ディスカッション、旧構成、完了済みロードマップ
- キャッシュ、フック状態、ローカル設定、秘密情報
- 配布に不要な個別移行計画だけを記録したidea文書

## 実装の順序

1. 固定source commitからmanifest対象を新規履歴へ導入する。
2. 名称、README、台帳、展開手順、ideasを社内配布用に一般化する。
3. 配布衛生lintとテストを実装し、ローカル品質ゲートへ統合する。
4. 全静的検証、実挙動、独立レビュー、スペック準拠検証を行う。
5. GitHub metadataをtemplate向けに設定し、commit・push・PRを作成する。

## セキュリティ考慮事項

- リポジトリは会社Organizationへコピーされるまでprivateを維持する。
- secrets、認証情報、個人設定、フック状態をコピーしない。
- Git履歴を継承せず、削除済み情報が過去commitから参照される経路をなくす。
- 外部有料自動化とLLM headless modeを標準検証に使用しない。

## パフォーマンス考慮事項

- 衛生lintは小規模なテキストファイル走査に限定し、ローカル品質ゲートの実行時間を大きく増やさない。

## 将来の拡張性

会社Organizationへコピー後、Organization固有のsource marker、セキュリティ規程、技術スタックを別Issue・steeringで追加できる。元の個人版との自動同期は、情報境界とレビュー責任を別途設計してから導入する。
