"""File content service: safe read/write of text files.

Features:
  * UTF-8 encoding by default.
  * Atomic writes via temp files + os.replace.
  * Optional backups before replacement.
  * Per-file result tracking for batch operations.
  * Read-only / binary detection.
"""

from __future__ import annotations

import os
import re
import shutil
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class WriteMode(Enum):
    """Write modes for batch file operations."""

    REPLACE = "replace"
    APPEND = "append"
    PREPEND = "prepend"


# Extensions that are likely binary and should not be loaded as plain text.
_BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".icns",
    ".pdf", ".zip", ".tar", ".gz", ".bz2", ".7z", ".rar",
    ".exe", ".dll", ".so", ".dylib", ".o", ".a",
    ".class", ".pyc", ".pyo", ".wasm",
    ".mp3", ".mp4", ".avi", ".mov", ".wav", ".flac",
    ".woff", ".woff2", ".ttf", ".otf", ".eot",
    ".db", ".sqlite", ".sqlite3",
    ".bin", ".dat",
}


@dataclass
class FileWriteResult:
    """Result of writing to a single file."""

    success: bool
    path: Path
    operation: str
    message: str = ""
    backed_up: bool = False
    skipped: bool = False
    is_read_only: bool = False


class FileContentService:
    """Service for reading and writing file contents safely."""

    def __init__(self) -> None:
        self.encoding: str = "utf-8"
        self.backup_extension: str = ".bak"
        self.create_backups: bool = False

    # ------------------------------------------------------------------
    # Reading
    # ------------------------------------------------------------------

    def read_file(self, path: Path) -> str:
        """Read a text file safely, returning its content.

        Raises :class:`ValueError` for binary files.
        Raises :class:`OSError` for read failures.
        """
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if self.is_binary(path):
            raise ValueError(f"Binary file detected, cannot edit as text: {path.name}")

        data = path.read_bytes()
        return self._bytes_to_text(data)

    @staticmethod
    def _bytes_to_text(data: bytes) -> str:
        """Decode bytes to text, trying common encodings."""
        for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
            try:
                return data.decode(enc)
            except (UnicodeDecodeError, LookupError):
                continue
        # Last resort: decode with replacement.
        return data.decode("utf-8", errors="replace")

    @staticmethod
    def is_binary(path: Path) -> bool:
        """Return True if the file appears to be binary."""
        if path.suffix.lower() in _BINARY_EXTENSIONS:
            return True
        # Heuristic: check for null bytes in the first 8KB.
        try:
            chunk = path.read_bytes()[:8192]
            if b"\x00" in chunk:
                return True
        except OSError:
            pass
        return False

    @staticmethod
    def is_read_only(path: Path) -> bool:
        """Return True if the file is read-only."""
        if not path.exists():
            return False
        return not os.access(path, os.W_OK)

    # ------------------------------------------------------------------
    # Writing (single file)
    # ------------------------------------------------------------------

    def write_file(
        self,
        path: Path,
        content: str,
        mode: WriteMode = WriteMode.REPLACE,
    ) -> FileWriteResult:
        """Write content to a single file.

        ``mode`` controls replace/append/prepend.
        """
        if not path.parent.exists():
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                return FileWriteResult(
                    False, path, mode.value,
                    message=f"Cannot create directory: {exc}",
                )

        existing = ""
        existed = path.exists()
        if existed:
            if self.is_read_only(path):
                return FileWriteResult(
                    False, path, mode.value,
                    message="File is read-only",
                    is_read_only=True,
                )
            try:
                existing = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                existing = ""

        if mode == WriteMode.APPEND:
            new_content = existing + content
        elif mode == WriteMode.PREPEND:
            new_content = content + existing
        else:
            new_content = content

        # Backup if configured and we're replacing existing content.
        backed_up = False
        if existed and self.create_backups and mode == WriteMode.REPLACE:
            backup_path = path.with_name(path.name + self.backup_extension)
            try:
                shutil.copy2(path, backup_path)
                backed_up = True
            except OSError:
                pass

        if not _atomic_write(path, new_content):
            return FileWriteResult(
                False, path, mode.value,
                message="Failed to write file atomically",
                backed_up=backed_up,
            )

        return FileWriteResult(
            True, path, mode.value,
            message="OK" if not existed else "Replaced",
            backed_up=backed_up,
        )

    # ------------------------------------------------------------------
    # Writing (batch — same content)
    # ------------------------------------------------------------------

    def write_to_multiple(
        self,
        paths: list[Path],
        content: str,
        mode: WriteMode = WriteMode.REPLACE,
    ) -> list[FileWriteResult]:
        """Apply the same content to multiple files.

        Returns a list of :class:`FileWriteResult`.
        """
        results: list[FileWriteResult] = []
        for path in paths:
            result = self.write_file(path, content, mode)
            results.append(result)
        return results

    # ------------------------------------------------------------------
    # Saving different content to multiple files
    # ------------------------------------------------------------------

    def save_multiple(
        self,
        file_contents: dict[Path, str],
        create_backups: bool = False,
    ) -> list[FileWriteResult]:
        """Save different content to multiple files.

        ``file_contents`` maps each file path to its new content.
        """
        results: list[FileWriteResult] = []
        old_backup = self.create_backups
        self.create_backups = create_backups
        try:
            for path, content in file_contents.items():
                result = self.write_file(path, content, WriteMode.REPLACE)
                results.append(result)
        finally:
            self.create_backups = old_backup
        return results

    def save_file_as(self, source: Path, dest: Path) -> FileWriteResult:
        """Save a file's content to a new path."""
        try:
            content = self.read_file(source)
        except (ValueError, OSError) as exc:
            return FileWriteResult(
                False, dest, "save_as",
                message=str(exc),
            )
        return self.write_file(dest, content, WriteMode.REPLACE)


def _atomic_write(path: Path, content: str) -> bool:
    """Write *content* to *path* atomically using a temp file.

    Returns True on success, False on failure.
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = path.with_name(path.name + ".tmp")
        # Preserve existing CRLF line endings when the file already uses them
        # and the new content does not.
        line_ending = "\n"
        if path.exists():
            old = path.read_bytes()
            if b"\r\n" in old and b"\r\n" not in content.encode("utf-8"):
                line_ending = "\r\n"

        data = content.replace("\n", line_ending).encode("utf-8")
        tmp_path.write_bytes(data)
        os.replace(str(tmp_path), str(path))
        return True
    except (OSError, PermissionError):
        return False


def parse_batch_content(text: str, base_dir: Path) -> dict[Path, str]:
    """Parse a batch-content format with ``=== FILE: path ===`` markers.

    Returns a dict mapping safe paths to their content.
    Raises ValueError on unsafe paths.

    Supported delimiter format::

        === FILE: path/to/file.py ===
        content here

        === FILE: another.py ===
        more content
    """
    pattern = re.compile(
        r"=== FILE:\s*(?P<filename>.+?)\s*===\s*\n(?P<content>.*?)(?=\n=== FILE:|\Z)",
        re.DOTALL,
    )

    results: dict[Path, str] = {}
    for match in pattern.finditer(text):
        filename = match.group("filename").strip()
        content = match.group("content")
        # The blank line before the next marker (or EOF) is a separator, not
        # part of the content, so trim trailing newlines.
        content = content.strip("\n")
        if not filename:
            continue
        if filename.startswith("/") or filename.startswith("\\"):
            raise ValueError(f"Unsafe path (absolute): {filename}")
        if ".." in filename:
            raise ValueError(f"Unsafe path (traversal): {filename}")
        if "\x00" in filename:
            raise ValueError(f"Unsafe path (null byte): {filename}")
        if re.match(r"^[A-Za-z]:", filename):
            raise ValueError(f"Unsafe path (drive prefix): {filename}")
        candidate = (base_dir / filename).resolve()
        # Verify it stays within base_dir.
        try:
            candidate.relative_to(base_dir.resolve())
        except ValueError:
            raise ValueError(f"Path escapes destination: {filename}")
        results[candidate] = content

    if not results:
        raise ValueError("No valid file markers found in batch content.")

    return results
