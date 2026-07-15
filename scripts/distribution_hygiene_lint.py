"""Detect personal-environment references in the internal distribution template."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

DEFAULT_POLICY = Path(__file__).with_name("distribution_hygiene_policy.json")
HOME_PATH_PATTERN = re.compile(r"(?<![A-Za-z0-9])/(?:Users|home)/[^/\s`'\"()]+")
GITHUB_HTTPS_PATTERN = re.compile(
    r"(?:https?|git)://(?:www\.)?github\.com/([^/\s`'\"()]+)/([^/\s`'\"()]+)(?:/([^\s`'\"()]+))?",
    re.IGNORECASE,
)
GITHUB_BARE_PATTERN = re.compile(
    r"(?<![A-Za-z0-9@/.:])(?:www\.)?github\.com/([^/\s`'\"()]+)/([^/\s`'\"()]+)(?:/([^\s`'\"()]+))?",
    re.IGNORECASE,
)
GITHUB_SSH_PATTERN = re.compile(
    r"(?:git@|ssh://git@)github\.com[:/]([^/\s:`'\"()]+)/([^/\s`'\"()]+)",
    re.IGNORECASE,
)
SOURCE_MARKER_PATTERN = re.compile(r"<!--\s*SOURCE:\s*(.*?)\s*-->", re.IGNORECASE)
CANONICAL_NAME = "inner-platform-harness"
LEGACY_CANONICAL_PATTERN = re.compile(
    rf"(?<!inner-){re.escape(CANONICAL_NAME.removeprefix('inner-'))}"
)


class PolicyError(ValueError):
    """Raised when the distribution hygiene policy is invalid."""


@dataclass(frozen=True)
class Policy:
    exclude_paths: tuple[Path, ...]
    allowed_home_prefixes: tuple[str, ...]
    allowed_github_owners: frozenset[str]
    allowed_source_markers: frozenset[str]
    derived_catalog: Path
    require_empty_derived_catalog: bool


@dataclass(frozen=True)
class Violation:
    path: Path
    line: int
    rule: str


def _string_list(raw: dict[str, Any], key: str) -> list[str]:
    value = raw.get(key)
    if not isinstance(value, list) or not value:
        raise PolicyError(f"{key} must be a non-empty list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise PolicyError(f"{key} must contain non-empty strings")
    return value


def _relative_path(value: str, key: str) -> Path:
    path = Path(value)
    if path.is_absolute() or value in {"", ".", "/"} or ".." in path.parts:
        raise PolicyError(f"unsafe {key}: {value!r}")
    return path


def load_policy(path: Path = DEFAULT_POLICY) -> Policy:
    try:
        raw_object: object = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PolicyError(f"cannot read policy: {exc}") from exc
    if not isinstance(raw_object, dict):
        raise PolicyError("policy root must be an object")
    raw: dict[str, Any] = raw_object
    if raw.get("version") != 1:
        raise PolicyError("unsupported policy version")

    require_empty = raw.get("require_empty_derived_catalog")
    if not isinstance(require_empty, bool):
        raise PolicyError("require_empty_derived_catalog must be a boolean")

    return Policy(
        exclude_paths=tuple(
            _relative_path(item, "exclude path") for item in _string_list(raw, "exclude_paths")
        ),
        allowed_home_prefixes=tuple(_string_list(raw, "allowed_home_prefixes")),
        allowed_github_owners=frozenset(_string_list(raw, "allowed_github_owners")),
        allowed_source_markers=frozenset(_string_list(raw, "allowed_source_markers")),
        derived_catalog=_relative_path(
            str(raw.get("derived_catalog", "")), "derived catalog"
        ),
        require_empty_derived_catalog=require_empty,
    )


def _is_excluded(relative: Path, excludes: tuple[Path, ...]) -> bool:
    return any(relative == excluded or excluded in relative.parents for excluded in excludes)


def iter_target_files(root: Path, policy: Policy) -> list[Path]:
    if not root.is_dir():
        raise PolicyError(f"project root is not a directory: {root}")
    try:
        result = subprocess.run(
            ("git", "ls-files", "-z"),
            cwd=root,
            check=False,
            shell=False,
            capture_output=True,
        )
    except OSError as exc:
        raise PolicyError(f"cannot list tracked files: {exc}") from exc
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise PolicyError(f"git ls-files failed: {message or result.returncode}")

    files: list[Path] = []
    for raw_path in result.stdout.split(b"\0"):
        if not raw_path:
            continue
        try:
            relative = Path(raw_path.decode("utf-8"))
        except UnicodeDecodeError as exc:
            raise PolicyError("tracked path is not valid UTF-8") from exc
        candidate = root / relative
        if not _is_excluded(relative, policy.exclude_paths) and (
            candidate.is_file() or candidate.is_symlink()
        ):
            files.append(candidate)
    return sorted(files)


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _table_data_line_offsets(text: str, heading: str, next_heading: str | None) -> list[int]:
    if heading not in text:
        return []
    start = text.index(heading)
    end = text.index(next_heading, start) if next_heading and next_heading in text[start:] else len(text)
    section = text[start:end]
    offsets: list[int] = []
    separator_seen = False
    offset = start
    for line in section.splitlines(keepends=True):
        stripped = line.strip()
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        is_separator = len(cells) >= 2 and all(
            re.fullmatch(r":?-{3,}:?", cell) for cell in cells
        )
        if not separator_seen:
            separator_seen = is_separator
        elif not stripped or stripped.startswith(("#", ">")):
            break
        elif "|" in stripped:
            offsets.append(offset)
        else:
            break
        offset += len(line)
    return offsets


def _catalog_data_line_offsets(text: str) -> list[int]:
    return [
        *_table_data_line_offsets(text, "## 展開候補", "## 重複ローカルコピーの除外"),
        *_table_data_line_offsets(
            text, "## 重複ローカルコピーの除外", "## オンデマンド運用"
        ),
    ]


def scan_text(
    path: Path,
    text: str,
    policy: Policy,
    *,
    origin_repository: str | None = None,
) -> list[Violation]:
    violations: list[Violation] = []
    for match in HOME_PATH_PATTERN.finditer(text):
        matched_path = match.group(0)
        if not any(
            matched_path == prefix.rstrip("/")
            or matched_path.startswith(f"{prefix.rstrip('/')}/")
            for prefix in policy.allowed_home_prefixes
        ):
            violations.append(
                Violation(path, _line_number(text, match.start()), "absolute-home-path")
            )
    allowed_owners = {owner.casefold() for owner in policy.allowed_github_owners}
    for pattern in (GITHUB_HTTPS_PATTERN, GITHUB_SSH_PATTERN, GITHUB_BARE_PATTERN):
        for match in pattern.finditer(text):
            repository = f"{match.group(1)}/{match.group(2).removesuffix('.git')}".casefold()
            path_suffix = match.group(3) if pattern is not GITHUB_SSH_PATTERN else None
            is_origin_issue = (
                path.parts[:1] == (".steering",)
                and origin_repository is not None
                and repository == origin_repository.casefold()
                and path_suffix is not None
                and re.fullmatch(r"issues/\d+", path_suffix.rstrip(".,;:")) is not None
            )
            if match.group(1).casefold() not in allowed_owners and not is_origin_issue:
                violations.append(
                    Violation(path, _line_number(text, match.start()), "github-owner")
                )
    for match in SOURCE_MARKER_PATTERN.finditer(text):
        allowed_markers = {marker.casefold() for marker in policy.allowed_source_markers}
        if match.group(1).strip().casefold() not in allowed_markers:
            violations.append(Violation(path, _line_number(text, match.start()), "source-marker"))
    if policy.require_empty_derived_catalog and path == policy.derived_catalog:
        for offset in _catalog_data_line_offsets(text):
            violations.append(Violation(path, _line_number(text, offset), "derived-catalog-data"))
    for match in LEGACY_CANONICAL_PATTERN.finditer(text):
        violations.append(Violation(path, _line_number(text, match.start()), "canonical-name"))
    return violations


def _origin_repository(root: Path) -> str | None:
    try:
        result = subprocess.run(
            ("git", "config", "--get", "remote.origin.url"),
            cwd=root,
            check=False,
            shell=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        raise PolicyError(f"cannot read origin remote: {exc}") from exc
    if result.returncode != 0:
        return None
    remote = result.stdout.strip()
    for pattern in (GITHUB_HTTPS_PATTERN, GITHUB_SSH_PATTERN):
        match = pattern.fullmatch(remote)
        if match is not None:
            return f"{match.group(1)}/{match.group(2).removesuffix('.git')}"
    return None


def scan_project(root: Path, policy: Policy) -> list[Violation]:
    violations: list[Violation] = []
    origin_repository = _origin_repository(root)
    for path in iter_target_files(root, policy):
        relative = path.relative_to(root)
        try:
            if path.is_symlink():
                text = os.readlink(path)
            else:
                data = path.read_bytes()
                if b"\0" in data:
                    continue
                try:
                    text = data.decode("utf-8")
                except UnicodeDecodeError:
                    continue
        except OSError as exc:
            raise PolicyError(f"cannot read {relative}: {exc}") from exc
        violations.extend(
            scan_text(relative, text, policy, origin_repository=origin_repository)
        )
    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path.cwd())
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    args = parser.parse_args(argv)
    try:
        policy = load_policy(args.policy.resolve())
        violations = scan_project(args.root.resolve(), policy)
    except PolicyError as exc:
        print(f"distribution hygiene lint: {exc}", file=sys.stderr)
        return 2
    for violation in violations:
        print(f"{violation.path}:{violation.line}: {violation.rule}")
    if violations:
        print(f"distribution hygiene lint: {len(violations)} violation(s)", file=sys.stderr)
        return 1
    print("distribution hygiene lint: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
