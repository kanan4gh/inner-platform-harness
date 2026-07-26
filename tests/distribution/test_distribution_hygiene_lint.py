"""Tests for distribution hygiene enforcement."""

from __future__ import annotations

import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import tarfile
from types import ModuleType
from typing import Any

SCRIPT_PATH = Path(__file__).parents[2] / "scripts" / "distribution_hygiene_lint.py"
ROOT = SCRIPT_PATH.parents[1]


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


def test_steering_may_name_the_upstream_canonical_as_historical_context() -> None:
    legacy_name = "platform" + "-harness"
    assert rules(legacy_name, Path(".steering/20260726-sync/requirements.md")) == set()


def test_steering_legacy_name_exception_does_not_disable_other_rules() -> None:
    legacy_name = "platform" + "-harness"
    text = "\n".join(
        (
            legacy_name,
            "/" + "Users/person/work/project",
            "https://github" + ".com/person/repository",
            "<" + "!-- SOURCE: external-repository -->",
        )
    )
    assert rules(text, Path(".steering/20260726-sync/requirements.md")) == {
        "absolute-home-path",
        "github-owner",
        "source-marker",
    }


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


def test_untracked_nonignored_text_file_is_automatically_scanned(tmp_path: Path) -> None:
    subprocess.run(("git", "init", "-q"), cwd=tmp_path, check=True)
    notes = tmp_path / "NOTES.md"
    notes.write_text("https://github" + ".com/person/repository\n", encoding="utf-8")
    assert {item.rule for item in lint.scan_project(tmp_path, policy())} == {"github-owner"}


def test_ignored_untracked_file_is_not_part_of_the_distribution(tmp_path: Path) -> None:
    subprocess.run(("git", "init", "-q"), cwd=tmp_path, check=True)
    (tmp_path / ".gitignore").write_text("ignored.md\n", encoding="utf-8")
    ignored = tmp_path / "ignored.md"
    ignored.write_text("https://github" + ".com/person/repository\n", encoding="utf-8")
    assert lint.scan_project(tmp_path, policy()) == []


def test_derived_projects_can_track_their_own_steering_history() -> None:
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".steering/*" not in text


def test_distribution_archive_contains_only_example_steering() -> None:
    attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")
    assert ".steering/[0-9]* export-ignore" in attributes
    result = subprocess.run(
        ("git", "archive", "--worktree-attributes", "--format=tar", "HEAD"),
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    with tarfile.open(fileobj=io.BytesIO(result.stdout), mode="r:") as archive:
        steering_roots = {
            Path(name).parts[1]
            for member in archive.getmembers()
            if (name := member.name).startswith(".steering/")
            and len(Path(name).parts) >= 2
        }
    assert steering_roots == {"example"}


def test_all_worktree_steering_directories_are_covered_by_the_export_rule() -> None:
    steering_roots = {
        path.name for path in (ROOT / ".steering").iterdir() if path.is_dir()
    }
    assert "example" in steering_roots
    assert all(
        name == "example" or (len(name) > 9 and name[:8].isdigit() and name[8] == "-")
        for name in steering_roots
    )


def test_repository_passes_distribution_hygiene_policy() -> None:
    configured = lint.load_policy(ROOT / "scripts" / "distribution_hygiene_policy.json")
    assert lint.scan_project(ROOT, configured) == []
