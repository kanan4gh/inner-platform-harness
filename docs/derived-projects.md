# 派生プロジェクト展開候補台帳

`inner-platform-harness`のリリース済み正典を展開する候補を、ローカルディレクトリではなくGitHub remote単位で管理する。配布時点では実プロジェクトを登録しない。会社Organizationへ配置後、会社の情報管理規程に従って運用を開始する。

- **台帳確認日**: 未設定
- **確認時のinner-platform-harness release**: 未設定
- **展開手順**: `docs/procedures/derived-project-rollout.md`

## 管理規則

### 一意性

- 一意キーは`OWNER/REPOSITORY`形式のGitHub remoteとする。
- 同じremoteを指す通常checkout、worktree、clean clone、運用コピーは別候補として登録しない。
- ローカルパスは一時的な参考情報であり、同期先の識別子に使わない。
- 実展開時にはGitHub上のdefault branch、archive / template状態、最新commitを再確認する。

### Harness generation

| 値 | 意味 |
|---|---|
| `current-neutral` | `AGENTS.md`、中立`docs/procedures/`、複数ハーネスアダプタを持つ現行世代 |
| `legacy-platform-claude` | 正典を`CLAUDE.md`へ内包する旧Claude専用世代 |
| `legacy-sdd` | 現行ハーネス以前の共通SDD原則・steeringを持つ旧世代 |
| `distribution-asset` | 派生製品ではなく、ハーネス配布・実験を目的とする資産 |

### Strategy

| 値 | 意味 |
|---|---|
| `direct-sync` | 現行中立構成があり、release差分だけを同期できる |
| `migrate-then-sync` | 旧構成から中立コアとアダプタへ移行してからrelease差分を同期する |
| `decision-required` | 継続利用・統合・archive等の人による判断が先に必要 |
| `excluded` | 重複コピー、配布資産等で通常の派生プロジェクト展開対象にしない |

### State

```text
candidate
  ├─ user selects → approved → planned → in-progress → verified → synced
  ├─ unsafe / ongoing work → on-hold
  ├─ ownership unclear → decision-required
  └─ duplicate / superseded / distribution only → excluded
```

- 候補登録だけで展開を開始しない。`candidate`から`approved`へ進めるのは、ユーザーが対象remoteを明示した場合だけとする。
- `synced`は将来releaseへの追随完了を意味しない。`Last source`と最新releaseを比較し、次回の対象指定を待つ。
- `Local caution`は確認日時点の参考情報であり、展開可否は毎回のpreflightで再判定する。
- `on-hold`は阻害要因をG0で裁定・解消し、再preflightの証拠を記録した場合だけ`candidate`または`approved`へ戻す。`decision-required`は人の裁定を記録して`candidate`または`excluded`へ遷移する。
- `Last source`は未展開を`none`、履歴を確定できない場合を`unknown (investigate)`、展開済みを`vX.Y.Z / <7〜40桁のcommit SHA>`で表す。

## 展開候補

| Remote | Repository URL | Lineage evidence | Harness generation | Strategy | Priority | State | Last source | Last inspected | Local caution | Decision / next action |
|---|---|---|---|---|---|---|---|---|---|---|

> 配布時点では候補を登録しない。会社Organizationへ配置後、承認されたremoteだけを1行ずつ追加する。

## 重複ローカルコピーの除外

| Local path | 対応remote | 扱い |
|---|---|---|

> 個人ホームディレクトリの絶対パスは記録しない。必要な場合は`WORKSPACE_ROOT/project-name`等の組織内プレースホルダーを使う。

## オンデマンド運用

1. ユーザーがremoteを`OWNER/REPOSITORY`で1件指定する。台帳に候補行があればその行を出発点にし、空または未登録でも指定remoteのG0 preflightを開始できる。
2. 実行エージェントはGitHub metadataとローカル状態を再取得する。会社Organizationへ配置済みで情報管理規程が許す場合だけ、未登録remoteを独立した台帳更新として追加する。配布元の本リポジトリでは空台帳を維持する。
3. 対象リポジトリに独立Issue・steering・feature branchを作成し、同期元release / commitを固定する。
4. `docs/procedures/derived-project-rollout.md`に従って、差分同期または移行後同期を行う。
5. PRマージ後、会社Organizationへ配置済みの運用版では`State`、`Last source`、`Last inspected`、`Decision / next action`を更新する。配布元の本リポジトリでは台帳を更新せず、空のまま維持する。

候補登録、inner-platform-harness release作成、他候補の同期完了をトリガーにした自動展開は行わない。複数remoteへの一括Issue・一括branch・一括PRも作らない。
