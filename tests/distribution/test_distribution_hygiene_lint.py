"""Tests for distribution hygiene enforcement."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from typing import Any

SCRIPT_PATH = Path(__file__).parents[2] / "scripts" / "distribution_hygiene_lint.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("distribution_hygiene_lint", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


lint = load_module()


def policy() -> Any:
    return lint.Policy(
        exclude_paths=(),
        allowed_home_prefixes=("/home/vscode",),
        allowed_github_owners=frozenset({"OWNER", "example"}),
        allowed_source_markers=frozenset({"inner-platform-harness"}),
        derived_catalog=Path("docs/derived-projects.md"),
        require_empty_derived_catalog=True,
    )


def rules(text: str, path: Path = Path("docs/example.md")) -> set[str]:
    return {violation.rule for violation in lint.scan_text(path, text, policy())}


def test_safe_placeholders_pass() -> None:
    text = "https://github.com/OWNER/REPOSITORY\n<!-- SOURCE: inner-platform-harness -->\n"
    assert rules(text) == set()


def test_legacy_canonical_name_is_rejected_without_storing_a_second_name() -> None:
    legacy_name = "platform" + "-harness"
    assert rules(legacy_name) == {"canonical-name"}
    assert rules("inner-platform-harness") == set()


def test_personal_home_path_is_rejected() -> None:
    home_path = "/" + "Users/example/work/project"
    assert rules(home_path) == {"absolute-home-path"}


def test_allowed_container_home_does_not_allow_similar_usernames() -> None:
    assert rules("/home/vscode/.aws") == set()
    similar_username = "/home/" + "vscode-other/work"
    assert rules(similar_username) == {"absolute-home-path"}


def test_concrete_github_owner_forms_are_rejected() -> None:
    repository_urls = (
        "https://github" + ".com/person/repository",
        "https://www.github" + ".com/person/repository",
        "https://GITHUB" + ".COM/person/repository",
        "git://github" + ".com/person/repository",
        "github" + ".com/person/repository",
        "git@github" + ".com:person/repository.git",
        "ssh://git@github" + ".com/person/repository.git",
    )
    assert all(rules(url) == {"github-owner"} for url in repository_urls)


def test_unapproved_source_marker_is_rejected() -> None:
    markers = (
        "<!-- " + "SOURCE: external-repository -->",
        "<!-- " + "Source: external-repository -->",
    )
    assert all(rules(marker) == {"source-marker"} for marker in markers)


def test_distribution_catalog_must_not_contain_data_rows() -> None:
    text = """# Catalog
## 展開候補
| Remote | Repository URL |
|---|---|
| `OWNER/REPOSITORY` | placeholder |
## 重複ローカルコピーの除外
"""
    assert rules(text, Path("docs/derived-projects.md")) == {"derived-catalog-data"}


def test_distribution_catalog_duplicate_copy_table_must_be_empty() -> None:
    text = """# Catalog
## 展開候補
| Remote | Repository URL |
|---|---|
## 重複ローカルコピーの除外
| Local path | Remote |
|---|---|
| WORKSPACE_ROOT/project | OWNER/REPOSITORY |
## オンデマンド運用
"""
    assert rules(text, Path("docs/derived-projects.md")) == {"derived-catalog-data"}


def test_distribution_catalog_rejects_rows_without_leading_pipe() -> None:
    text = """# Catalog
## 展開候補
Remote | Repository URL
---|---
OWNER/REPOSITORY | placeholder
## 重複ローカルコピーの除外
Local path | Remote
---|---
WORKSPACE_ROOT/project | OWNER/REPOSITORY
## オンデマンド運用
"""
    violations = lint.scan_text(Path("docs/derived-projects.md"), text, policy())
    assert [item.rule for item in violations] == [
        "derived-catalog-data",
        "derived-catalog-data",
    ]


def test_staged_text_file_is_automatically_scanned(tmp_path: Path) -> None:
    subprocess.run(("git", "init", "-q"), cwd=tmp_path, check=True)
    notes = tmp_path / "NOTES.md"
    notes.write_text("https://github" + ".com/person/repository\n", encoding="utf-8")
    subprocess.run(("git", "add", "NOTES.md"), cwd=tmp_path, check=True)
    assert {item.rule for item in lint.scan_project(tmp_path, policy())} == {"github-owner"}


def test_repository_passes_distribution_hygiene_policy() -> None:
    root = Path(__file__).parents[2]
    configured = lint.load_policy(root / "scripts" / "distribution_hygiene_policy.json")
    assert lint.scan_project(root, configured) == []
