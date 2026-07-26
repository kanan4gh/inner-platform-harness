# ハーネス実機受け入れ記録

## 実施情報

| 項目 | 内容 |
|---|---|
| 実施日時 | 2026-07-26 17:00–17:46 JST |
| 担当者 | Codex（ユーザー承認済みの対話操作） |
| 対象ハーネス | Claude Code / Codex / Kiro |
| バージョン | Claude Code 2.1.220 / Codex CLI 0.145.0 / Kiro CLI 2.14.2 |
| 実行面 | 対話型CLI（PTY） |
| OS | macOS 26.5.2 (25F84) |
| 対象リポジトリ | `kanan4gh/inner-platform-harness` |
| 候補commit | `3c5eee99e298df041e49c5357c01445200766199` |
| 同期元 | `platform-harness v1.5.1` / `bb125b52eaf7c603c612f363bbd5960f46f3d367` |
| 一時環境 | `/private/tmp/inner-platform-harness-g3-{claude,codex,kiro}-3c5eee9` |

## 事前条件

- [x] 候補commit直前のローカル品質ゲートが成功している（pytest 223件、Ruff、BasedPyright、steering lint、外部有料自動化lint、配布衛生lint）
- [x] 3つのclean cloneが候補commitに固定されている
- [x] 各cloneのfixtureが最新tasklistの選択条件に一致している
- [x] fixture作成前の各cloneに未コミット変更がない
- [x] 従量課金型headless modeを使用しないことを確認した

fixtureのtasklistは、人が次の状態で固定した。

```markdown
- [x] Stop smoke 着手マーカー（人が事前に付ける）
- [ ] Stop smoke sentinel（agentは完了・更新しない）
```

## Claude Code

| # | 段階 | 操作と実結果 | 証跡 | 判定 |
|---|---|---|---|---|
| 1 | 表示 | workspace trust画面で対象cloneと事前許可14件を確認した。`@doc-reviewer`と`@implementation-validator`の候補にworkspace agentsが表示された | trust画面、`@`候補表示 | 合格 |
| 2 | 読込 | `AGENTS.md`、`CLAUDE.md`、`.claude/README.md`を実読込し、AGENTS.mdが中立正典、対応ハーネスがClaude Code / Codex / Kiro、通常steeringが3ファイル、軽量steeringが2ファイルと回答した | 対話出力 | 合格 |
| 3 | 実行 | 対話型CLIで応答と安全な`pwd`を実行した | clone絶対パスの出力 | 合格 |
| 4 | 権限 | readは許可済み、`g3-claude-scratch.txt`のWriteは明示承認画面を表示し、単発承認後に`CLAUDE_G3_OK`を作成した。安全な`pwd`は既定権限内で実行された | Write承認画面、一時ファイル内容 | 合格 |
| 5 | Stop | sentinelを含む応答終了時にStop feedbackが発火し、対象tasklistと未完了行を表示して自動継続した。直後に中断し、sentinelは未更新のまま保持した | Stop feedback、fixture再読込 | 合格 |

**総合判定: 合格**

## Codex

| # | 段階 | 操作と実結果 | 証跡 | 判定 |
|---|---|---|---|---|
| 1 | 表示 | workspace trust後、hooks reviewでStopが`Installed 1 / Active 0 / Review 1`と表示された。trust後に`Installed 1 / Active 1`へ遷移した | trust画面、hooks review | 合格 |
| 2 | 読込 | `AGENTS.md`先頭と`.codex/hooks.json`を実読込し、正典見出しとイベント名`Stop`を回答した | `Explored: Read AGENTS.md, hooks.json`と回答 | 合格 |
| 3 | 実行 | 安全な`pwd`を対話で依頼し、clone絶対パスを返した | `/private/tmp/inner-platform-harness-g3-codex-3c5eee9` | 合格 |
| 4 | 権限 | `g3-codex-scratch.txt`へ`CODEX_G3_OK`を作成した。安全な`pwd`はsandbox内の許可済み操作として追加承認なしで実行された | 一時ファイル内容、対話出力 | 合格 |
| 5 | Stop | `.codex/hooks.json`をtrustしてStopをActiveにした状態で、sentinelにより自動継続を確認した。`Ctrl+C`で中断し、sentinelは未更新のまま保持した | hooks review、自動継続、fixture再読込 | 合格 |

Codex CLI 0.145.0は`/agents`一覧コマンドを提供せず、`Unrecognized command '/agents'`となった。この表示能力は対象外とし、`.codex/agents/doc-reviewer.toml`、`.codex/agents/implementation-validator.toml`、`.agents/skills/`5件の存在・形式・回帰テストを代替経路とする。最初のStop確認では自動継続後に不要なweb検索へ進みかけたため即時中断し、fixtureを外した最小プロンプトでreadとshellを再確認した。製品ファイルへの変更はなかった。

**総合判定: 条件付き合格（agents一覧UIのみ対象外、代替経路あり）**

## Kiro

| # | 段階 | 操作と実結果 | 証跡 | 判定 |
|---|---|---|---|---|
| 1 | 表示 | `kiro-cli agent validate --path .kiro/agents/sdd.json`がexit 0。`kiro-cli --agent sdd`の`/context`展開で`Active agent context: sdd`、AGENTS.md、5 skillsが各1回表示された | agent validate、`/context`表示 | 合格 |
| 2 | 読込 | `AGENTS.md`のL1-5を実読込し、1行目と`SDDプロセス正典`を回答した | `Read .../AGENTS.md (L1-5)`と回答 | 合格 |
| 3 | 実行 | shellで`pwd`だけを実行し、clone絶対パスを返した | `/private/tmp/inner-platform-harness-g3-kiro-3c5eee9` | 合格 |
| 4 | 権限 | readは事前許可。writeとshellはそれぞれ`requires approval`画面を表示し、単発承認後に実行した。`g3-kiro-scratch.txt`の内容は`KIRO_G3_OK` | write / shell承認画面、一時ファイル内容 | 合格 |
| 5 | Stop | sentinelを残して応答を終えると自動継続し、tasklistを再読込した。状態ファイルは`consecutive_blocks: 3`まで増加し、その後fail-openした。sentinelは未更新。steering lintもC3、exit 1で同じ未完了行を検出した | `.kiro/hooks/state/stop_guard.json`、fixture再読込、C3出力 | 合格 |

IDE固有のAgent selectorとStop非block表示は、今回はKiro CLI経路を選択したため対象外である。CLIのStopが最初の継続から短時間に連続して上限3回へ到達したが、設計どおり無限ループ防止でfail-openし、ファイル変更は行わなかった。

**総合判定: 合格**

## 総合判定

- [x] 合格: Claude CodeとKiro CLIの必須項目が期待どおりである
- [x] 条件付き合格: Codexのagents一覧UIだけが製品能力として存在せず、静的構成・回帰テストの代替経路がある
- [ ] 不合格
- [ ] 保留

3ハーネスとも、今回変更した正典読込、read / write / shellの権限境界、Stop hookのランタイム挙動を候補commit上で確認した。G3の総合結果は**合格（Codexの表示能力差を記録した条件付き合格を含む）**とする。

## 監査メモ

- 禁止headless mode起動回数: **0回**
- headless誤起動: **なし**
- GitHub Actions run: **0件**（2026-07-26 17:45 JST、GitHub API `total_count: 0`）
- 意図しない製品ファイル変更: **なし**
- 一時cloneの変更: fixture、確認用scratch、KiroのStop状態ファイルだけ
- sentinel更新: **0件**
- 後片付け: 各対話セッションを終了。使い捨てcloneは正本へ持ち帰らず、観察結果だけを本記録へ反映した
