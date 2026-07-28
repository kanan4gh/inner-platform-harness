"""対話型受け入れ手順の状態・単一ゲート・無課金境界を検証する。"""

from pathlib import Path

ROOT = Path(__file__).parents[2]
PROCEDURE = ROOT / "docs" / "procedures" / "harness-acceptance.md"


def section(text: str, heading: str, next_heading: str) -> str:
    start = text.index(f"## {heading}")
    end = text.index(f"## {next_heading}", start)
    return text[start:end]


def assert_in_order(text: str, markers: tuple[str, ...]) -> None:
    positions = [text.index(marker) for marker in markers]
    assert positions == sorted(positions)


def test_acceptance_connects_to_add_feature_with_single_candidate_gate() -> None:
    text = PROCEDURE.read_text(encoding="utf-8")
    connection = section(text, "add-feature ステップ8-Bとの接続", "自動検証との境界")
    assert_in_order(
        connection,
        (
            "**候補ゲート**",
            "**候補コミット**",
            "**G3実施**",
            "**結果記録**",
            "**最終ゲート**",
            "**記録コミット**",
            "**push / PR作成**",
        ),
    )
    assert "候補ゲート**: ローカル品質ゲートを1回で全緑" in connection
    assert "受け入れ記録が製品ファイルを変更しない" in connection
    assert "状態を`active`へ戻し" in connection


def test_acceptance_defaults_to_agent_orchestrated_interactive_pty() -> None:
    text = PROCEDURE.read_text(encoding="utf-8")
    automation = section(text, "実行主体と自動化原則", "使い捨て設定ホーム契約")
    assert "ユーザーへ各ハーネスの操作を差し戻す手動作業ではない" in automation
    assert "実行エージェントが対象ハーネスの対話型CLIをPTYで起動" in automation
    assert "非対話headless modeへの置換ではない" in automation
    assert "計画承認を、この限定されたG3操作の事前承認" in automation
    assert "G3全体をユーザーへ差し戻さず" in automation
    assert "必要最小限の操作をユーザーへ依頼" in automation
    assert "永続許可、グローバル設定変更" in automation


def test_adapter_guides_bind_g3_to_their_disposable_config_home() -> None:
    adapters = (
        (
            ROOT / ".claude" / "README.md",
            ("CLAUDE_CONFIG_DIR", "CLAUDE_CODE_TMPDIR", "DISABLE_UPDATES"),
            "~/.claude",
        ),
        (
            ROOT / ".codex" / "README.md",
            ("CODEX_HOME", "sqlite_home", "check_for_update_on_startup"),
            "~/.codex",
        ),
        (
            ROOT / ".kiro" / "README.md",
            ("KIRO_HOME", "KIRO_CHAT_LOG_FILE", "app.disableAutoupdates"),
            "~/.kiro",
        ),
    )
    for path, isolation_names, existing_home in adapters:
        text = path.read_text(encoding="utf-8")
        for isolation_name in isolation_names:
            assert isolation_name in text
        assert existing_home in text
        assert "対話型PTY" in text
        assert "認証情報や設定" in text


def test_acceptance_isolates_each_cli_with_its_official_config_home() -> None:
    text = PROCEDURE.read_text(encoding="utf-8")
    profiles = section(text, "使い捨て設定ホーム契約", "add-feature ステップ8-Bとの接続")
    for cli, variable in (
        ("`claude`（対話型）", "CLAUDE_CONFIG_DIR"),
        ("`codex`（対話型TUI）", "CODEX_HOME"),
        ("`kiro-cli`（対話型TUI）", "KIRO_HOME"),
    ):
        assert cli in profiles
        assert variable in profiles
    assert "既存設定ホームからcredentials、token、cookie、session、設定ファイルをコピーしない" in profiles
    assert "既存設定ホームの非secretな設定・trust対象について変更が0件" in profiles
    for runtime_isolation in ("CLAUDE_CODE_TMPDIR", "sqlite_home", "KIRO_CHAT_LOG_FILE"):
        assert runtime_isolation in profiles
    for update_control in (
        "DISABLE_UPDATES=1",
        "check_for_update_on_startup=false",
        "app.disableAutoupdates=true",
    ):
        assert update_control in profiles
    assert "設定・trust・session等の永続ユーザー状態が使い捨て設定ホーム内" in profiles
    assert "製品固有のruntime / logが明示した使い捨て領域内" in profiles
    assert "認証阻害として保留" in profiles


def test_acceptance_replaces_stop_sentinel_with_active_read_only_fixture() -> None:
    text = PROCEDURE.read_text(encoding="utf-8")
    preparation = section(text, "共通準備", "共通の状態・lint確認")
    assert "- **状態**: active" in preparation
    assert "- [ ] 応答終了を妨げない未完了タスク" in preparation
    assert "agentへfixtureを完了・更新させず" in preparation
    assert "Stop smoke sentinel" not in preparation
    assert "fixture内へ記録ファイルは作らない" in preparation
    assert "元リポジトリ側" in preparation
    assert "実行エージェントがfixtureを作る" in preparation


def test_acceptance_exercises_full_state_lifecycle_and_profiles() -> None:
    text = PROCEDURE.read_text(encoding="utf-8")
    checks = section(text, "共通の状態・lint確認", "Claude Code")
    assert_in_order(
        checks,
        (
            "activeかつ未完了",
            "G1だけ",
            "steering_state.py --steering [確認用ステアリング名] pause",
            "pausedの通常lint",
            "steering_state.py --steering [確認用ステアリング名] resume",
            "steering_state.py --steering [確認用ステアリング名] complete",
            "8. `python3 scripts/steering_lint.py --require-complete",
        ),
    )
    assert checks.count("--require-complete [確認用ステアリング名]") == 2


def test_each_harness_requires_read_only_response_to_finish_without_block() -> None:
    text = PROCEDURE.read_text(encoding="utf-8")
    sections = (
        section(text, "Claude Code", "Codex"),
        section(text, "Codex", "Kiro CLI"),
        section(text, "Kiro CLI", "GUI IDEの例外的補足確認"),
    )
    for harness in sections:
        assert "fixture tasklistを読" in harness
        assert "正常終了" in harness
    assert "Stop blockが登録されていない" in sections[0]
    assert "`.codex/hooks.json`がなく" in sections[1]
    assert "stop hookがなく" in sections[2]


def test_standard_g3_surface_is_cli_and_gui_is_a_minimal_exception() -> None:
    text = PROCEDURE.read_text(encoding="utf-8")
    claude = section(text, "Claude Code", "Codex")
    codex = section(text, "Codex", "Kiro CLI")
    kiro = section(text, "Kiro CLI", "GUI IDEの例外的補足確認")
    gui = section(text, "GUI IDEの例外的補足確認", "判定")
    assert "Claude Code CLIを対話型PTY起動" in claude
    assert "Codex CLIを対話型PTY起動" in codex
    assert "`kiro-cli --agent sdd`を対話型PTY起動" in kiro
    assert "自動G3の標準合格条件ではない" in gui
    assert "その最小確認だけをユーザーへ依頼" in gui
    assert "GUIで繰り返さない" in gui


def test_acceptance_forbids_metered_headless_modes() -> None:
    text = PROCEDURE.read_text(encoding="utf-8")
    conditions = section(text, "実施条件", "add-feature ステップ8-Bとの接続")
    assert "従量課金型headless modeを使わない" in conditions
    assert "Claude Codeのprint mode" in conditions
    assert "Codexの非対話exec mode" in conditions


def test_acceptance_template_can_record_not_applicable_items() -> None:
    template = (
        ROOT / "docs" / "procedures" / "templates" / "harness-acceptance-record.md"
    ).read_text(encoding="utf-8")
    assert "合格 / 不合格 / 保留 / 対象外" in template
    assert "対象外: 実行面が対象能力を提供せず" in template
    assert "代替経路:" in template
    assert "Claude Code / Codex / Kiroごとに複製" in template
    assert "1つのハーネスの結果で別ハーネスを代替しない" in template
    assert "GitHub Actions自動run: 0件" in template
    assert "従量課金型headless mode起動: 0件" in template
    assert "G3実行主体" in template
    assert "対話型CLI + PTY自動実行" in template
    assert "永続権限・グローバル設定変更: 0件" in template
    assert "既存ユーザー設定・trust storeの起動前後の変更が0件" in template
    assert "`CLAUDE_CONFIG_DIR` / `CODEX_HOME` / `KIRO_HOME`" in template
    assert "| 標準実行面 | 対話型CLI + PTY |" in template
    assert "runtime / log環境変数・設定と使い捨てpath" in template
    assert "更新抑止" in template
    assert "認証経路" in template
    assert "既存設定・trust比較方法と結果" in template
    assert "既存runtime / log比較方法と結果" in template
    assert "ユーザーへの例外的な操作依頼" in template
