#!/usr/bin/env python3
"""Install the align-with-me skill at project or user scope."""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path


SKILL_NAME = "align-with-me"
SKILL_ROOT = Path(__file__).resolve().parents[1]
CORE_INSTALL_FILES = (Path("SKILL.md"),)
OPENAI_METADATA = Path("agents/openai.yaml")


class InstallError(RuntimeError):
    """Raised when installation cannot be completed safely."""


def default_user_skills_dir() -> Path:
    return (Path.home() / ".agents" / "skills").resolve()


def project_root_from(value: str | None) -> Path:
    project_root = Path(value).expanduser() if value else Path.cwd()
    project_root = project_root.resolve()
    if not project_root.is_dir():
        raise InstallError(f"项目目录不存在：{project_root}")
    return project_root


def choose_scope() -> str:
    print("请选择技能安装范围：")
    print("  1) 项目层：仅当前项目可用（.agents/skills/align-with-me）")
    print("  2) 用户层：当前用户的所有项目可用（~/.agents/skills/align-with-me）")

    while True:
        try:
            choice = input("请输入 1 或 2：").strip()
        except EOFError as error:
            raise InstallError("未完成选择；请使用交互终端，或传入 --scope project/user。") from error

        if choice == "1":
            return "project"
        if choice == "2":
            return "user"
        print("选择无效，请输入 1（项目层）或 2（用户层）。")


def resolve_skills_dir(value: str | None, default: Path, base: Path) -> Path:
    skills_dir = Path(value).expanduser() if value else default
    if not skills_dir.is_absolute():
        skills_dir = base / skills_dir
    return skills_dir.resolve()


def destination_for(
    scope: str,
    project_skills_dir: Path,
    user_skills_dir: Path,
) -> Path:
    if scope == "project":
        return project_skills_dir / SKILL_NAME
    return user_skills_dir / SKILL_NAME


def validate_source(install_files: tuple[Path, ...]) -> None:
    missing = [str(path) for path in install_files if not (SKILL_ROOT / path).is_file()]
    if missing:
        raise InstallError(f"技能源文件缺失：{', '.join(missing)}")


def is_matching_installation(
    destination: Path,
    install_files: tuple[Path, ...],
) -> bool:
    return destination.is_dir() and all(
        (destination / relative_path).is_file()
        and filecmp.cmp(
            SKILL_ROOT / relative_path,
            destination / relative_path,
            shallow=False,
        )
        for relative_path in install_files
    )


def install_files(destination: Path, install_files: tuple[Path, ...]) -> bool:
    """Copy the skill files, returning whether a new installation was made."""
    if destination.is_symlink():
        raise InstallError(f"目标路径是符号链接，未覆盖：{destination}")

    if destination.exists():
        if is_matching_installation(destination, install_files):
            return False
        raise InstallError(
            f"目标路径已存在且内容不同，未覆盖：{destination}\n"
            "如需更新，请先备份并移除该目录后重新安装。"
        )

    try:
        destination.mkdir(parents=True, exist_ok=False)
        for relative_path in install_files:
            target_file = destination / relative_path
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SKILL_ROOT / relative_path, target_file)

        if not is_matching_installation(destination, install_files):
            raise InstallError(f"安装后校验失败：{destination}")
    except OSError as error:
        raise InstallError(f"无法写入目标路径：{destination}（{error}）") from error
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="将 align-with-me 安装到项目层或用户层。默认会交互式询问安装范围。"
    )
    parser.add_argument(
        "--scope",
        choices=("project", "user"),
        help="跳过交互选择：project 表示项目层，user 表示用户层。",
    )
    parser.add_argument(
        "--project-root",
        help="项目层的目标项目目录；默认使用当前工作目录。",
    )
    parser.add_argument(
        "--project-skills-dir",
        help="项目层 skills 根目录；默认是 <project>/.agents/skills。",
    )
    parser.add_argument(
        "--user-skills-dir",
        help="用户层 skills 根目录；默认是 ~/.agents/skills。",
    )
    parser.add_argument(
        "--include-openai-metadata",
        action="store_true",
        help="额外安装可选的 agents/openai.yaml 适配元数据。",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        project_root = project_root_from(args.project_root)
        project_skills_dir = resolve_skills_dir(
            args.project_skills_dir,
            project_root / ".agents" / "skills",
            project_root,
        )
        user_skills_dir = resolve_skills_dir(
            args.user_skills_dir,
            default_user_skills_dir(),
            Path.cwd().resolve(),
        )
        scope = args.scope or choose_scope()
        install_files_to_copy = CORE_INSTALL_FILES
        if args.include_openai_metadata:
            install_files_to_copy += (OPENAI_METADATA,)
        validate_source(install_files_to_copy)
        destination = destination_for(scope, project_skills_dir, user_skills_dir)
        created = install_files(destination, install_files_to_copy)
    except InstallError as error:
        print(f"安装未完成：{error}", file=sys.stderr)
        return 1

    scope_label = "项目层" if scope == "project" else "用户层"
    if created:
        print(f"安装层级：{scope_label}")
        print(f"安装路径：{destination}")
        print(f"已安装：{SKILL_NAME}")
    else:
        print(f"{SKILL_NAME} 已在目标位置安装，内容一致，未覆盖现有文件。")
        print(f"安装层级：{scope_label}")
        print(f"安装路径：{destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
