"""Structural contracts for the empty derived-project catalog and rollout procedure."""

from pathlib import Path

ROOT = Path(__file__).parents[2]
CATALOG = ROOT / "docs" / "derived-projects.md"
PROCEDURE = ROOT / "docs" / "procedures" / "derived-project-rollout.md"
CATALOG_COLUMNS = (
    "Remote",
    "Repository URL",
    "Lineage evidence",
    "Harness generation",
    "Strategy",
    "Priority",
    "State",
    "Last source",
    "Last inspected",
    "Local caution",
    "Decision / next action",
)


def catalog_text() -> str:
    return CATALOG.read_text(encoding="utf-8")


def procedure_text() -> str:
    return PROCEDURE.read_text(encoding="utf-8")


def catalog_data_rows() -> list[str]:
    section = catalog_text().split("## 展開候補", maxsplit=1)[1].split(
        "## 重複ローカルコピーの除外", maxsplit=1
    )[0]
    table_lines = [line for line in section.splitlines() if line.startswith("|")]
    headers = tuple(cell.strip() for cell in table_lines[0].strip("|").split("|"))
    assert headers == CATALOG_COLUMNS
    return table_lines[2:]


def test_catalog_is_an_empty_distribution_template() -> None:
    text = catalog_text()
    assert catalog_data_rows() == []
    assert "配布時点では候補を登録しない" in text
    assert "会社Organizationへ配置後" in text
    assert "個人ホームディレクトリの絶対パスは記録しない" in text


def test_catalog_defines_remote_key_classifications_and_state_model() -> None:
    text = catalog_text()
    assert "一意キーは`OWNER/REPOSITORY`形式のGitHub remote" in text
    for value in (
        "current-neutral",
        "legacy-platform-claude",
        "legacy-sdd",
        "distribution-asset",
        "direct-sync",
        "migrate-then-sync",
        "decision-required",
        "excluded",
        "candidate",
        "approved",
        "planned",
        "in-progress",
        "verified",
        "synced",
        "on-hold",
    ):
        assert value in text
    assert "履歴を確定できない場合を`unknown (investigate)`" in text


def test_catalog_preserves_on_demand_boundary() -> None:
    text = catalog_text()
    assert "ユーザーが対象remoteを明示" in text
    assert "候補登録だけで展開を開始しない" in text
    assert "複数remoteへの一括Issue・一括branch・一括PRも作らない" in text
    assert "`on-hold`は阻害要因をG0で裁定・解消" in text
    assert "`decision-required`は人の裁定を記録" in text


def test_procedure_defines_unit_preflight_and_manifest() -> None:
    text = procedure_text()
    assert "1 inner-platform-harness release × 1 GitHub remote × 1 feature branch × 1 PR" in text
    for value in (
        "対象remote",
        "default branch / OID",
        "dirty / ahead / behind",
        "同期元: inner-platform-harness",
        "作業隔離",
        "Preserve",
        "Replace from canonical",
        "Add from canonical",
        "Merge manually",
        "Exclude",
    ):
        assert value in text


def test_preflight_fixes_freshness_concurrency_and_isolation_contracts() -> None:
    text = procedure_text()
    for contract in (
        "archive / template状態",
        "remote-tracking refをfetchした日時・方法とcommit OID",
        "active Issue / PR / branch",
        "同期元inner-platform-harness release tagとcommit",
        "clean worktreeまたはclean clone",
        "dirtyな既存checkoutを清掃・stash・上書きして移行を始めない",
        "対象リポジトリ内に独立Issue・steering・feature branch",
        "プロダクト固有層、技術スタック固有層",
    ):
        assert contract in text
    assert "G0で既存PRをマージする、破棄する、新移行へ引き継ぐ" in text


def test_procedure_defines_bootstrap_authority_and_handoff() -> None:
    text = procedure_text()
    assert "ユーザーがG0とG1で承認した本展開手順" in text
    assert "bootstrap executor" in text
    assert "旧ハーネスを実行したことにしない" in text
    assert "Authority handoff" in text
    assert "新しい`AGENTS.md`と対象エージェント用アダプタ" in text


def test_general_example_is_placeholder_only_and_non_authoritative() -> None:
    text = procedure_text()
    example = text.split("## 一般化された展開例", maxsplit=1)[1]
    for placeholder in (
        "OWNER/REPOSITORY",
        "COMMIT_SHA",
        "YYYY-MM-DD",
        "WORKSPACE_ROOT/REPOSITORY",
        "SOURCE_COMMIT_SHA",
    ):
        assert placeholder in example
    assert "この例は承認済みmanifestではない" in example
    assert "各具体pathまたは明示した文書sectionをちょうど1分類" in example


def test_procedure_requires_local_and_interactive_validation_without_paid_automation() -> None:
    text = procedure_text()
    assert "local_quality_gate.py" in text
    assert "人がIDEまたは対話型CLI受け入れ" in text
    assert "GitHub Actions自動runと有料LLM headless mode起動が0件" in text
    assert "従量課金型headless mode" in text
