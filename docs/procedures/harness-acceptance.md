# ハーネス対話型受け入れ手順

Claude Code、Codex、Kiroの表示・読込・権限・状態操作と応答終了を、従量課金型headless modeを使わずに確認する。構造と状態/lintロジックはpytestへ寄せ、本手順では実セッションでしか確認できない項目だけを扱う。

## 実施条件

- ローカル品質ゲートが1回で全緑になっている
- 対象commitが固定されている
- `/private/tmp`等の使い捨てclean cloneで実施する
- 自動G3の標準実行面は対話型CLI + PTYとする
- Claude Codeのprint mode、Codexの非対話exec mode等、従量課金型headless modeを使わない

## 実行主体と自動化原則

G3は、ユーザーへ各ハーネスの操作を差し戻す手動作業ではない。**ステップ4.5またはG1で計画が承認された後は、実行エージェントが対象ハーネスの対話型CLIをPTYで起動し、本手順を自動的に最後までオーケストレーションする**。ここでいう自動化は対話型セッションの操作自動化であり、print / exec等の非対話headless modeへの置換ではない。

- G3要否、対象ハーネス、対話型CLI + PTY自動実行、使い捨てclone内で行うscratch path・書き込み内容・shellコマンド・承認回数を計画に列挙する。計画承認を、この限定されたG3操作の事前承認とする
- ハーネスごとに独立した対話型セッションと、後述の公式環境変数で切り替えた使い捨て設定ホームを使う。trust storeと単発許可をこの一時設定へ閉じ込め、既存のユーザー設定を変更しない
- 認証情報をcloneや記録へコピーしない。組織が許可した使い捨て設定ホームまたはread-onlyの認証参照を利用できない場合は、認証阻害として扱う
- trustや承認結果を一時設定へ隔離できない場合、自動承認しない。永続許可、グローバル設定変更、アカウント・Organization設定変更を必要とする場合も外部阻害として扱う
- GUI IDEはPTY自動操作の標準対象にしない。IDE固有能力の確認が必須で、別の許可済みGUI自動操作機構がない場合だけ、その画面の最小確認をユーザーへ依頼する
- ログイン、MFA、GUI専用操作、ライセンス不足、組織ポリシー等でエージェントが続行できない場合だけ、必要最小限の操作をユーザーへ依頼する。G3全体をユーザーへ差し戻さず、阻害要因の解消後は同じ固定commitから自動再開する
- 実行面が能力を提供しない場合は推測で合格にせず、対象外または保留と理由・代替経路を記録する

## 使い捨て設定ホーム契約

自動G3では、clean cloneだけでなく永続ユーザー状態とruntime / logも隔離する。各CLIを起動するプロセスにだけ次の環境変数・設定を適用し、既存の`~/.claude`、`~/.codex`、`~/.kiro`を設定・trust・sessionの参照先や書き込み先にしない。

| ハーネス | 標準CLI | 使い捨て設定ホーム | 使い捨てruntime / log | バージョン固定 |
|---|---|---|---|---|
| Claude Code | `claude`（対話型） | `CLAUDE_CONFIG_DIR=/private/tmp/...` | `CLAUDE_CODE_TMPDIR=/private/tmp/...` | 起動プロセスで`DISABLE_UPDATES=1` |
| Codex | `codex`（対話型TUI） | `CODEX_HOME=/private/tmp/...` | 使い捨て`config.toml`の`sqlite_home`を`/private/tmp/...`へ固定。logは既定の`$CODEX_HOME/log`内 | 同じ`config.toml`で`check_for_update_on_startup=false` |
| Kiro | `kiro-cli`（対話型TUI） | `KIRO_HOME=/private/tmp/...` | `KIRO_CHAT_LOG_FILE=/private/tmp/.../kiro-chat.log`。必要に応じ同じ使い捨てrootへ`TMPDIR` / `XDG_RUNTIME_DIR`も設定 | 使い捨て設定で`app.disableAutoupdates=true` |

- 設定ホームとruntime / log rootはハーネスごとに別directoryとし、cloneの外に置く
- 起動前に環境変数・設定値、更新抑止、各使い捨てdirectoryが新規または空であることを確認する。起動後は、設定・trust・session等の永続ユーザー状態が使い捨て設定ホーム内、製品固有のruntime / logが明示した使い捨て領域内にだけ書かれたことを確認する
- 既存設定ホームはG3中に書き込まない。起動前後で、既存設定ホームの非secretな設定・trust対象について変更が0件であることを確認し、内容ではなく変更有無だけを記録する
- 既存設定ホームからcredentials、token、cookie、session、設定ファイルをコピーしない。OS keychain、組織SSO、環境注入等の許可済みread-only認証経路を利用できなければ、認証阻害として保留する
- trust、sandbox、単発許可は使い捨て設定ホームにだけ記録する。自動更新を抑止した起動済みバージョンを受け入れ対象として記録し、更新コマンドは実行しない。CLIが明示した設定ホーム、runtime / log、clone以外の永続領域へ書くことが判明した場合は、その承認を行わずG3を停止する

環境変数の根拠は各製品の公式仕様に固定する。

- Claude Code: https://code.claude.com/docs/en/env-vars
- Codex: https://learn.chatgpt.com/docs/config-file/config-reference
- Kiro CLI: https://kiro.dev/docs/cli/reference/settings/
- Kiro CLI log: https://kiro.dev/docs/cli/installation/

## add-feature ステップ8-Bとの接続

受け入れ結果を記録すると候補ゲート後にファイルが増える。この循環は、**受け入れ記録が製品ファイルを変更しない**ことを使って次の順序で直線化する。

1. **候補ゲート**: ローカル品質ゲートを1回で全緑にする
2. **候補コミット**: 全変更をコミットし、G3の固定commitにする
3. **G3実施**: 固定commitをclean cloneし、実行エージェントが対象ハーネスの対話型CLIをPTYで起動して受け入れを自動実行する
4. **結果記録**: 観察結果を元リポジトリ側の`acceptance-record.md`へ記録する
5. **最終ゲート**: 記録を含む最終状態でゲートを1回実行し全緑にする
6. **記録コミット**: acceptance recordをコミットする
7. **push / PR作成**: PR本文にG3結果を含める

不合格・保留で製品ファイルを変更した場合は、状態を`active`へ戻し、影響する4段検証行を未完了へ戻してステップ6・7、`complete`遷移、候補ゲートからやり直す。G3不要の変更ではadd-featureステップ8-Aを使う。
リポジトリ差分を生じさせず、環境・権限だけを解消した場合は、同じ固定commitに対してG3だけを再実施し、解消内容と再実施結果を記録する。

## 自動検証との境界

| 観点 | 検証方法 |
|---|---|
| ファイル存在、JSON / Markdown構造 | pytest |
| 状態解析、pause / resume / complete、通常/完了lint | pytestと実スクリプト |
| Stopフック登録・実装の不在 | pytest |
| 禁止headlessシグネチャの不在 | metered automation lint |
| スキル・エージェントの表示と実読込 | 対話型実機確認 |
| read / write / shellの承認UI | 対話型実機確認 |
| 未完了tasklistを読むだけの依頼が正常終了すること | 対話型実機確認 |

## 共通準備

1. 対象commitをハーネスごとの`/private/tmp`配下へclean cloneする
2. 上表に従って設定ホームとruntime / logをハーネス別の使い捨てdirectoryへ設定し、trust・単発許可・session・logが既存ユーザー領域へ書かれないことを確認する
3. clone開始時点で未コミット変更がないことを確認する
4. 製品作業と重複しない確認専用の日付付きsteering名を決め、実行エージェントがfixtureを作る。後続コマンドは辞書順の「最新」へ依存せず、その名前を常に明示する
5. requirements.mdへ検証用Issue URLを記載し、design.mdを置く
6. tasklist.mdを次の状態で作る
7. `python3 scripts/steering_lint.py`が通常検査で成功することを確認する
8. `docs/procedures/templates/harness-acceptance-record.md`のハーネス別ブロックをClaude Code / Codex / Kiroごとに複製して記録項目を確認する。fixture内へ記録ファイルは作らない
9. ハーネス名、バージョン、CLI、使い捨て設定pathと環境変数名、runtime / log path、更新抑止、非secretの認証経路名、既存設定・trust・runtime / logの比較方法、設定・承認ポリシー、対象commitを、clone外の一時メモへ記録する

```markdown
# タスクリスト

## 作業状態

- **状態**: active
- **状態更新日時**: {現在のタイムゾーン付きISO 8601}
- **使用ハーネス**: {対象ハーネス}

## 確認タスク

- [x] fixture準備
- [ ] 応答終了を妨げない未完了タスク

## 実装後の振り返り

{通常検査ではactiveのためプレースホルダーを許容}
```

fixtureは使い捨て複製の中だけに作る。agentへfixtureを完了・更新させず、読み取り確認だけを依頼する。
実施時点の未コミット変更はこの意図したfixtureだけであることを確認し、その他の変更があれば受け入れを止める。

観察中はclone外の一時メモへ記録し、終了後に**元リポジトリ側**の`.steering/[日付]-[タスク名]/acceptance-record.md`へテンプレート形式で転記する。fixture内の記録を正式証跡にせず、clone破棄前に転記漏れがないことを確認する。

## 共通の状態・lint確認

対話型ハーネス確認の前後で、実行エージェントが次を実行して結果を記録する。`[確認用ステアリング名]`は共通準備で作成した名前へ置換し、状態変更と完了lintの対象を常に明示する。

1. activeかつ未完了のfixtureで`python3 scripts/steering_lint.py`を実行し、exit 0を確認する
2. `python3 scripts/steering_lint.py --require-complete [確認用ステアリング名]`を実行し、G1だけでexit 1になることを確認する
3. 次を実行し、pausedと中断記録が生成されることを確認する

   ```bash
   python3 scripts/steering_state.py --steering [確認用ステアリング名] pause \
     --harness "[対象ハーネス]" \
     --completed-scope "受け入れfixture準備" \
     --uncommitted-changes "確認fixtureのみ" \
     --resume-at "対話型確認" \
     --reason "状態遷移の受け入れ確認"
   ```

4. `python3 scripts/steering_lint.py`を実行し、pausedの通常lintがexit 0になることを確認する
5. 次を実行し、activeへ戻ることを確認する

   ```bash
   python3 scripts/steering_state.py --steering [確認用ステアリング名] resume \
     --harness "[対象ハーネス]" \
     --resume-at "対話型確認" \
     --reason "状態遷移の受け入れ確認を再開"
   ```

6. 実行エージェントがfixture内の全チェックと振り返りを完了する
7. `python3 scripts/steering_state.py --steering [確認用ステアリング名] complete --harness "[対象ハーネス]"`を実行し、completeへ遷移することを確認する
8. `python3 scripts/steering_lint.py --require-complete [確認用ステアリング名]`を実行し、exit 0を確認する

この操作は製品リポジトリではなく使い捨てfixtureに限定する。

## Claude Code

1. `CLAUDE_CONFIG_DIR`をハーネス専用の使い捨て設定ホームへ向け、clean cloneでClaude Code CLIを対話型PTY起動する
2. `AGENTS.md`、`CLAUDE.md`、主要スキルが表示されることを確認する
3. `@`候補または名前を明示した依頼で必要なsubagentを実起動できることを確認する
4. fixture tasklistを読み、状態・先頭の未完了タスク・再開位置候補だけを回答するよう依頼する
5. agentがfixtureを変更せず、未完了が残ったまま応答を正常終了することを確認する
6. read、write、shellを別々に依頼し、承認境界を観察する
7. PostToolUseリマインドは非強制であり、Stop blockが登録されていないことを設定表示と照合する
8. 実結果と証跡を記録する

## Codex

1. `CODEX_HOME`をハーネス専用の使い捨て設定ホームへ向け、clean cloneでCodex CLIを対話型PTY起動する
2. `AGENTS.md`、`.agents/skills/`、必要なagentsが表示されることを確認する
3. fixture tasklistを読み、状態・先頭の未完了タスク・再開位置候補だけを回答するよう依頼する
4. agentがfixtureを変更せず、未完了が残ったまま応答を正常終了することを確認する
5. `.codex/hooks.json`がなく、Stop hookのtrust確認やfeedbackが発生しないことを観察する
6. read、write、shellを別々に依頼し、sandbox / approvalを観察する
7. 実結果と証跡を記録する

## Kiro CLI

1. `KIRO_HOME`をハーネス専用の使い捨て設定ホームへ向け、agent validate後に`kiro-cli --agent sdd`を対話型PTY起動する
2. `/context`で`AGENTS.md`とskillsが重複せず表示されることを確認する
3. fixture tasklistを読むだけの依頼が変更なしで正常終了することを確認する
4. `.kiro/agents/sdd.json`にstop hookがなく、自動継続やblock decisionが発生しないことを観察する
5. read事前許可とwrite / shellの承認UIを個別に確認する
6. 状態操作と通常/完了lintの結果を共通確認と照合する
7. 実結果と証跡を記録する

## GUI IDEの例外的補足確認

GUI IDEは自動G3の標準合格条件ではない。変更したアダプタ契約にClaude Code / Codex / Kiro IDEでしか提供されない能力が含まれる場合だけ、対象能力をrequirements.mdへ明示して追加確認する。

- 許可済みGUI自動化機構がある場合は実行エージェントが操作し、機構名と操作範囲を記録する
- 許可済み機構がない場合は、必要な画面と期待結果を1つずつ示し、その最小確認だけをユーザーへ依頼する
- CLIで既に確認済みのtasklist読取、状態遷移、lint、read / write / shell確認をGUIで繰り返さない
- GUI側のtrustや設定を既存ユーザープロファイルへ永続化する必要がある場合は自動承認せず、保留または対象外として記録する

## 判定

- **合格**: 必須項目が期待どおりで、GitHub Actions自動runと禁止headless modeの起動がともに0件
- **不合格**: 期待結果との差異、意図しない変更・権限・自動継続がある
- **保留**: 環境・権限・製品バージョン差で観察できない
- **対象外**: 実行面が対象能力を提供しない。代替経路を記録する

未観察を推測で合格にしない。保留・対象外には理由と再確認条件または代替経路を記録する。

## 誤起動時

課金対象の可能性があるheadless実行に気づいたら直ちに停止し、時刻、呼び出し元、到達点、変更ファイルを記録する。別のheadless実行で再現せず、静的テストまたは対話型確認へ切り替える。
