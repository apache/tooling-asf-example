# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from __future__ import annotations

import argparse
import dataclasses
import datetime
import enum
import os
import pathlib
import re
import sys
import tempfile
from typing import Final, Literal, NoReturn

import pygit2
import tomlkit
import tomlkit.container
import tomlkit.items

# TODO: Move most of this to __main__.py or wherever is appropriate

PROJECT: Final[str] = "asf-example"
# This is automatically updated
VERSION: Final[str] = "0.0.1-dev24"


class BumpMode(enum.Enum):
    RELEASE = "release"
    DEV = "dev"
    SPECIFIC = "specific"


@dataclasses.dataclass(frozen=True)
class HeadVersion:
    major: int
    minor: int
    patch: int
    dev: int | None

    def __str__(self) -> str:
        if self.dev is None:
            return f"{self.major}.{self.minor}.{self.patch}"
        return f"{self.major}.{self.minor}.{self.patch}-dev{self.dev}"


ZERO_VERSION_SENTINEL: Final[HeadVersion] = HeadVersion(major=0, minor=0, patch=0, dev=None)


def bump_mode_from_args(
    args: argparse.Namespace,
) -> (
    tuple[Literal[BumpMode.RELEASE], None] | tuple[Literal[BumpMode.DEV], None] | tuple[Literal[BumpMode.SPECIFIC], str]
):
    trace(f"args: {args}")
    if args.bump_release:
        return BumpMode.RELEASE, None
    elif args.bump_dev:
        return BumpMode.DEV, None
    elif args.bump_specific is not None:
        return BumpMode.SPECIFIC, args.bump_specific
    report_error_and_exit("--bump-dev, --bump-release, or --bump-specific is required")


def cli_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=PROJECT, add_help=True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--bump-dev", action="store_true", help="bump to a dev version")
    group.add_argument("--bump-release", action="store_true", help="bump to a release version")
    group.add_argument("--bump-specific", metavar="V", help="bump to a specific version")
    group.add_argument("--version", action="store_true", help="report the current version")
    return parser


def current_repository(current_path: pathlib.Path) -> pygit2.Repository:
    trace(f"current_path: {current_path}")
    repository_directory = pygit2.discover_repository(str(current_path))
    if repository_directory is None:
        report_error_and_exit("not inside a git repository")
    return pygit2.Repository(repository_directory)


def calculate_bumped_version(
    repository: pygit2.Repository, mode: BumpMode, specific: str | None
) -> tuple[HeadVersion, str]:
    trace(f"calculate bumped version from mode: {mode}, specific: {specific}")
    match mode:
        case BumpMode.SPECIFIC:
            if specific is None:
                report_error_and_exit("specific version required")
            return ZERO_VERSION_SENTINEL, specific
        case BumpMode.RELEASE:
            head_version = read_head_version(repository)
            if head_version.dev is not None:
                bumped = HeadVersion(
                    head_version.major,
                    head_version.minor,
                    head_version.patch,
                    None,
                )
                return head_version, str(bumped)
            bumped = HeadVersion(
                head_version.major,
                head_version.minor,
                head_version.patch + 1,
                None,
            )
            return head_version, str(bumped)
        case BumpMode.DEV:
            head_version = read_head_version(repository)
            if head_version.dev is None:
                bumped = HeadVersion(
                    head_version.major,
                    head_version.minor,
                    head_version.patch + 1,
                    1,
                )
                return head_version, str(bumped)
            bumped = HeadVersion(
                head_version.major,
                head_version.minor,
                head_version.patch,
                head_version.dev + 1,
            )
            return head_version, str(bumped)


def main() -> NoReturn:
    raise SystemExit(run_cli())


def parse_version(version: str) -> HeadVersion:
    trace(f"parsing version to HeadVersion: {version}")
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)(?:-dev(\d+))?", version)
    if not match:
        report_error_and_exit(f"unsupported version format: {version}")
    major = int(match.group(1))
    minor = int(match.group(2))
    patch = int(match.group(3))
    dev = int(match.group(4)) if match.group(4) is not None else None
    return HeadVersion(major=major, minor=minor, patch=patch, dev=dev)


def project_root_or_exit(project_root: pathlib.Path, project_name: str) -> None:
    trace(f"check project root: {project_root}, project_name: {project_name}")
    pyproject_path = project_root / "pyproject.toml"
    if not pyproject_path.is_file():
        report_error_and_exit(
            f"must run from project root with pyproject.toml for {project_name}",
        )
    with pyproject_path.open("r", encoding="utf-8") as f:
        data = tomlkit.load(f)
    name = data.get("project", {}).get("name")
    if name != project_name:
        report_error_and_exit(f"pyproject.toml does not belong to '{project_name}'")


def read_head_version(repo: pygit2.Repository) -> HeadVersion:
    trace(f"read head version from repository: {repo}")
    if repo.is_bare:
        report_error_and_exit("a working tree, not a bare git repository, is required")
    try:
        obj = repo.revparse_single("HEAD:pyproject.toml")
    except Exception:
        # This may be the first commit with pyproject.toml
        return ZERO_VERSION_SENTINEL
    if not isinstance(obj, pygit2.Blob):
        report_error_and_exit("pyproject.toml is in HEAD, but not a regular file")
    content = obj.data.decode("utf-8")
    data = tomlkit.parse(content)
    head_version = data.get("project", {}).get("version")
    # TODO: Not tomlkit.items.String?
    if not isinstance(head_version, str):
        report_error_and_exit("version missing in pyproject.toml in HEAD")
    return parse_version(head_version)


def replace_key_in_section(text: str, section: str, key: str, value: str) -> str:
    trace(f"replace key in section: section: {section}, key: {key}, value: {value}")
    # TODO: This is very messy and probably wrong, needs improvement
    doc = tomlkit.parse(text)
    current: tomlkit.container.Container = doc
    for part in section.split("."):
        item = current.get(part)
        if not isinstance(item, tomlkit.items.Table):
            current[part] = tomlkit.table()
            item = current[part]
        if not isinstance(item, tomlkit.items.Table):
            # Should be impossible
            report_error_and_exit(f"expected table, got {type(item)}")
        current = item.value
    current[key] = value
    return tomlkit.dumps(doc)


def report_error_and_exit(message: str) -> NoReturn:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(2)


def run_cli() -> int:
    parser = cli_argument_parser()
    args = parser.parse_args()
    return run_using_args(args)


def run_using_args(args: argparse.Namespace) -> int:
    # Report the current version if --version is present
    if args.version:
        print(VERSION)
        return 0

    # Check that we are in the correct directory
    current_path = pathlib.Path.cwd()
    project_root_or_exit(current_path, PROJECT)

    # Get the pygit2 repository, bump mode, and optional specific version
    repository = current_repository(current_path)
    mode, specific = bump_mode_from_args(args)

    # Calculate the bumped version
    head_version, bumped_version = calculate_bumped_version(repository, mode, specific)

    # Update the version in __init__.py and pyproject.toml
    # TODO: Allow paths to files containing the version to be specified
    update_init_version(bumped_version)
    update_pyproject_version(bumped_version)

    # Report the result
    print(f"{head_version} -> {bumped_version}")
    return 0


def trace(message: str) -> None:
    print(f"trace: {message}", file=sys.stderr)


def update_init_version(bumped_version: str) -> None:
    trace(f"update init version with bumped version: {bumped_version}")
    init_path = pathlib.Path(__file__)
    # TODO: This pattern is very fragile, needs improvement
    version_pattern = r'VERSION:\s*Final\[str\]\s*=\s*".*?"\s*\n?'
    tmp_fd, tmp_name = tempfile.mkstemp(prefix="__init__.", suffix=".tmp", dir=str(init_path.parent))
    try:
        with (
            os.fdopen(tmp_fd, "w", encoding="utf-8", newline="") as tmp,
            init_path.open("r", encoding="utf-8", newline="") as src,
        ):
            # Only do this once
            replaced = False
            for line in src:
                contains_version = re.fullmatch(version_pattern, line)
                if (not replaced) and contains_version:
                    tmp.write(f'VERSION: Final[str] = "{bumped_version}"\n')
                    replaced = True
                else:
                    tmp.write(line)
        os.replace(tmp_name, init_path)
    except Exception:
        try:
            os.remove(tmp_name)
        except Exception:
            pass
        report_error_and_exit("failed to update VERSION constant in __init__.py")


def update_pyproject_version(bumped_version: str) -> None:
    trace(f"update pyproject version with bumped version: {bumped_version}")
    pyproject_path = pathlib.Path("pyproject.toml")
    tmp_fd, tmp_name = tempfile.mkstemp(prefix="pyproject.", suffix=".tmp", dir=str(pyproject_path.parent))
    try:
        with (
            os.fdopen(tmp_fd, "w", encoding="utf-8", newline="") as tmp,
            pyproject_path.open("r", encoding="utf-8", newline="") as src,
        ):
            content = src.read()
            now = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
            content = replace_key_in_section(content, "project", "version", bumped_version)
            content = replace_key_in_section(content, "tool.uv", "exclude-newer", now)
            tmp.write(content)
        os.replace(tmp_name, pyproject_path)
    except Exception as exc:
        try:
            os.remove(tmp_name)
        except Exception:
            pass
        report_error_and_exit(
            f"failed to update pyproject.toml: {exc}; project may be in an inconsistent version state"
        )


if __name__ == "__main__":
    main()
