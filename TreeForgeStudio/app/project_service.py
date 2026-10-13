"""Project service: creates directory/file structures from parsed trees.

All filesystem creation runs on a worker thread (see :mod:`project_service`
usage from the UI) to avoid blocking the main thread.
"""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from app.tree_parser import ParseResult, TreeNode


class ConflictPolicy(Enum):
    """Behaviour when a file already exists at the destination."""

    SKIP = "skip"          # Skip existing files, preserve content.
    BACKUP = "backup"      # Back up then overwrite.
    ERROR = "error"        # Treat as an error and halt.


@dataclass
class CreationResult:
    """Result of a single filesystem creation operation."""

    success: bool
    path: Path
    is_directory: bool
    skipped: bool = False
    backed_up: bool = False
    message: str = ""


@dataclass
class CreationReport:
    """Aggregated report for a full structure-creation run."""

    directories_created: int = 0
    files_created: int = 0
    files_skipped: int = 0
    directories_skipped: int = 0
    files_backed_up: int = 0
    failures: list[CreationResult] = field(default_factory=list)
    successes: list[CreationResult] = field(default_factory=list)

    @property
    def total_failures(self) -> int:
        return len(self.failures)

    @property
    def success(self) -> bool:
        return len(self.failures) == 0


@dataclass
class FileWriteResult:
    """Result of writing to a single file."""

    success: bool
    path: Path
    operation: str  # "replace", "append", "prepend", "save", "save_as"
    message: str = ""
    backed_up: bool = False


class ProjectService:
    """Service for creating directory trees and writing files."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir.resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.conflict_policy = ConflictPolicy.SKIP
        self.backup_extension = ".bak"

    def set_base_dir(self, base_dir: Path) -> None:
        self.base_dir = base_dir.resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def validate_tree(self, parse_result: ParseResult) -> list[str]:
        """Return a list of validation error messages (empty if valid)."""
        errors: list[str] = []
        if parse_result.root is None:
            errors.append("No tree structure to create.")
            return errors
        # Already validated by parser, but double-check path safety.
        root = parse_result.root
        self._collect_unsafe_paths(root, errors)
        return errors

    def _collect_unsafe_paths(self, node: TreeNode, errors: list[str]) -> None:
        name = node.name
        if name.startswith("/") or name.startswith("\\"):
            errors.append(f"Absolute path not allowed: {name}")
        if ".." in name:
            errors.append(f"Path traversal not allowed: {name}")
        if "\x00" in name:
            errors.append(f"Null byte in path: {name}")
        if re.match(r"^[A-Za-z]:", name):
            errors.append(f"Drive prefix not allowed: {name}")
        for f in node.all_files():
            self._collect_unsafe_paths(f, errors)
        for d in node.children.values():
            self._collect_unsafe_paths(d, errors)

    def create_structure(self, parse_result: ParseResult) -> CreationReport:
        """Create the directory/file structure described by a parse result."""
        report = CreationReport()
        if parse_result.root is None:
            report.failures.append(
                CreationResult(False, self.base_dir, False, message="No root node")
            )
            return report

        root = parse_result.root
        root_dest = self.base_dir / root.name

        # Ensure no path traversal escapes the base.
        if not _is_within(root_dest, self.base_dir):
            report.failures.append(
                CreationResult(False, root_dest, False, message="Path escapes destination")
            )
            return report

        self._create_node(root, root_dest, report)
        return report

    def _create_node(
        self, node: TreeNode, dest: Path, report: CreationReport
    ) -> None:
        """Recursively create a directory node and its children."""
        # Create the directory itself.
        result = self._create_directory(dest, node)
        if not result.success and not result.skipped:
            report.failures.append(result)
            return
        if result.skipped:
            report.directories_skipped += 1
        else:
            report.directories_created += 1

        # Create files inside this directory.
        for fname, fnode in node.files.items():
            file_dest = dest / fname
            fresult = self._create_file(file_dest, node)
            if not fresult.success:
                report.failures.append(fresult)
            else:
                report.successes.append(fresult)
                if fresult.skipped:
                    report.files_skipped += 1
                else:
                    report.files_created += 1
                    if fresult.backed_up:
                        report.files_backed_up += 1

        # Recurse into subdirectories.
        for cname, cnode in node.children.items():
            child_dest = dest / cname
            if not _is_within(child_dest, self.base_dir):
                report.failures.append(
                    CreationResult(False, child_dest, False, message="Path traversal blocked")
                )
                continue
            # If the child was classified as AMBIGUOUS, treat as directory.
            self._create_node(cnode, child_dest, report)

    def _create_directory(self, dest: Path, node: TreeNode) -> CreationResult:
        try:
            if dest.exists():
                if dest.is_dir():
                    return CreationResult(True, dest, True, skipped=True)
                else:
                    msg = f"Path exists as a file, not a directory: {dest}"
                    return CreationResult(False, dest, True, message=msg)
            dest.mkdir(parents=True, exist_ok=True)
            return CreationResult(True, dest, True)
        except PermissionError as exc:
            return CreationResult(False, dest, True, message=str(exc))
        except OSError as exc:
            return CreationResult(False, dest, True, message=str(exc))

    def _create_file(self, dest: Path, parent_node: TreeNode) -> CreationResult:
        try:
            if dest.exists():
                if self.conflict_policy == ConflictPolicy.SKIP:
                    return CreationResult(True, dest, False, skipped=True)
                elif self.conflict_policy == ConflictPolicy.BACKUP:
                    backup = dest.with_name(dest.name + self.backup_extension)
                    shutil.copy2(dest, backup)
                    dest.write_text("", encoding="utf-8")
                    return CreationResult(True, dest, False, message="backed up", backed_up=True)
                elif self.conflict_policy == ConflictPolicy.ERROR:
                    return CreationResult(
                        False, dest, False,
                        message=f"File already exists: {dest}",
                    )
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.touch(exist_ok=True)
            return CreationResult(True, dest, False)
        except PermissionError as exc:
            return CreationResult(False, dest, False, message=str(exc))
        except OSError as exc:
            return CreationResult(False, dest, False, message=str(exc))

    # ------------------------------------------------------------------
    # File content operations
    # ------------------------------------------------------------------

    def resolve_file_path(self, relative_path: str) -> Optional[Path]:
        """Resolve a relative file path to an absolute path under the base dir."""
        try:
            candidate = (self.base_dir / relative_path).resolve()
        except (ValueError, OSError):
            return None
        if not _is_within(candidate, self.base_dir):
            return None
        return candidate

    def resolve_path_from_node(self, node: TreeNode) -> Path:
        """Resolve a file node to its filesystem path."""
        return self.base_dir / node.path

    def ensure_directory(self, relative_path: str) -> Path:
        """Ensure a directory exists under the base."""
        dest = (self.base_dir / relative_path).resolve()
        if not _is_within(dest, self.base_dir):
            raise ValueError("Path escapes destination directory")
        dest.mkdir(parents=True, exist_ok=True)
        return dest

    def list_tree_nodes(self) -> list[TreeNode]:
        """Return a simple flat listing of all nodes."""
        # This is a helper for the explorer model.
        return []


def _is_within(path: Path, base: Path) -> bool:
    """Return True if ``path`` is inside ``base`` (or equals it)."""
    try:
        path.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False



