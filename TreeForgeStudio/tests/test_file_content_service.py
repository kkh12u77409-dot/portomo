"""Tests for the file content service."""

from __future__ import annotations

import os

import pytest

from app.file_content_service import (
    FileContentService,
    WriteMode,
    parse_batch_content,
)

IS_ROOT = os.geteuid() == 0 if hasattr(os, "geteuid") else False


@pytest.fixture()
def service():
    return FileContentService()


def test_write_and_read_utf8(service, tmp_path):
    path = tmp_path / "test.py"
    result = service.write_file(path, 'print("hello")', WriteMode.REPLACE)
    assert result.success
    assert service.read_file(path) == 'print("hello")'


def test_write_arabic_unicode_internationally(service, tmp_path):
    path = tmp_path / "arabic.txt"
    content = "مرحبا بالعالم\nHello World\n"
    service.write_file(path, content, WriteMode.REPLACE)
    assert service.read_file(path) == content


def test_write_emoji(service, tmp_path):
    path = tmp_path / "emoji.txt"
    content = "Emoji: 🎉🚀🔥\nMixed: مرحبا 🎉 World\n"
    service.write_file(path, content, WriteMode.REPLACE)
    assert service.read_file(path) == content


def test_multiline_content(service, tmp_path):
    path = tmp_path / "multi.txt"
    content = "line1\nline2\nline3\n\nline5\n"
    service.write_file(path, content, WriteMode.REPLACE)
    assert service.read_file(path) == content
    assert content.count("\n") == 5


def test_replace_mode(service, tmp_path):
    path = tmp_path / "r.txt"
    service.write_file(path, "original", WriteMode.REPLACE)
    service.write_file(path, "new content", WriteMode.REPLACE)
    assert service.read_file(path) == "new content"


def test_append_mode(service, tmp_path):
    path = tmp_path / "a.txt"
    service.write_file(path, "line1", WriteMode.REPLACE)
    service.write_file(path, "line2", WriteMode.APPEND)
    assert service.read_file(path) == "line1line2"


def test_prepend_mode(service, tmp_path):
    path = tmp_path / "p.txt"
    service.write_file(path, "body", WriteMode.REPLACE)
    service.write_file(path, "header\n", WriteMode.PREPEND)
    assert service.read_file(path) == "header\nbody"


def test_binary_detection(service, tmp_path):
    png = tmp_path / "img.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
    assert service.is_binary(png)
    with pytest.raises(ValueError):
        service.read_file(png)


@pytest.mark.skipif(IS_ROOT, reason="Running as root bypasses file permission bits")
def test_read_only_detection(service, tmp_path):
    path = tmp_path / "ro.txt"
    path.write_text("data", encoding="utf-8")
    os.chmod(path, 0o444)
    try:
        assert service.is_read_only(path)
        result = service.write_file(path, "new", WriteMode.REPLACE)
        assert not result.success
        assert result.is_read_only
    finally:
        os.chmod(path, 0o644)


def test_read_only_flag_on_results(service, tmp_path):
    # Verify the read-only field exists on results even when writable.
    path = tmp_path / "rw.txt"
    result = service.write_file(path, "data", WriteMode.REPLACE)
    assert result.success
    assert service.is_read_only(path) is False


def test_atomic_write_leaves_no_tmp(service, tmp_path):
    path = tmp_path / "atomic.txt"
    service.write_file(path, "content", WriteMode.REPLACE)
    assert not (tmp_path / "atomic.txt.tmp").exists()


def test_backup_before_replace(service, tmp_path):
    service.create_backups = True
    path = tmp_path / "backup.txt"
    service.write_file(path, "original", WriteMode.REPLACE)
    result = service.write_file(path, "replaced", WriteMode.REPLACE)
    assert result.backed_up
    assert (tmp_path / "backup.txt.bak").read_text(encoding="utf-8") == "original"


def test_write_creates_parent_dirs(service, tmp_path):
    path = tmp_path / "a" / "b" / "c.txt"
    result = service.write_file(path, "data", WriteMode.REPLACE)
    assert result.success
    assert path.is_file()


def test_batch_write_multiple_files(service, tmp_path):
    files = [tmp_path / f"f{i}.txt" for i in range(3)]
    results = service.write_to_multiple(files, "# comment\n", WriteMode.REPLACE)
    assert all(r.success for r in results)
    for f in files:
        assert f.read_text(encoding="utf-8") == "# comment\n"


def test_save_different_content_to_multiple_files(service, tmp_path):
    mapping = {
        tmp_path / "a.py": "print('a')",
        tmp_path / "b.md": "# Title B",
        tmp_path / "c.txt": "content c\nعربي",
    }
    results = service.save_multiple(mapping)
    assert all(r.success for r in results)
    assert (tmp_path / "a.py").read_text(encoding="utf-8") == "print('a')"
    assert (tmp_path / "b.md").read_text(encoding="utf-8") == "# Title B"
    assert (tmp_path / "c.txt").read_text(encoding="utf-8") == "content c\nعربي"


def test_partial_batch_failure_is_reported(service, tmp_path):
    good = tmp_path / "good.txt"
    # A path whose parent is a *file* (not a directory) fails to write for
    # every user, including root.
    blocker = tmp_path / "blocker"
    blocker.write_text("not a directory", encoding="utf-8")
    bad = blocker / "child.txt"
    results = service.write_to_multiple([good, bad], "x", WriteMode.REPLACE)
    assert good.is_file()
    assert not bad.exists()
    statuses = [r.success for r in results]
    assert True in statuses
    assert False in statuses
    # The failing result must carry a message and not claim success.
    failing = [r for r in results if not r.success][0]
    assert failing.message


def test_parse_batch_content_basic(tmp_path):
    text = """=== FILE: main.py ===
print("hello")

=== FILE: README.md ===
# My Project

=== FILE: requirements.txt ===
PyQt6"""
    parsed = parse_batch_content(text, tmp_path)
    assert len(parsed) == 3
    assert parsed[tmp_path / "main.py"] == 'print("hello")'
    assert parsed[tmp_path / "README.md"] == "# My Project"
    assert parsed[tmp_path / "requirements.txt"] == "PyQt6"


def test_parse_batch_content_multiline(tmp_path):
    text = """=== FILE: s.py ===
def foo():
    return 1


def bar():
    return 2"""
    parsed = parse_batch_content(text, tmp_path)
    assert "def foo():" in parsed[tmp_path / "s.py"]
    assert "def bar():" in parsed[tmp_path / "s.py"]


def test_parse_batch_rejects_absolute(tmp_path):
    with pytest.raises(ValueError):
        parse_batch_content("=== FILE: /etc/passwd ===\nroot", tmp_path)


def test_parse_batch_rejects_traversal(tmp_path):
    with pytest.raises(ValueError):
        parse_batch_content("=== FILE: ../../../etc/passwd ===\nroot", tmp_path)


def test_parse_batch_no_markers(tmp_path):
    with pytest.raises(ValueError):
        parse_batch_content("random text without markers", tmp_path)


def test_parse_batch_nested_paths(tmp_path):
    text = "=== FILE: src/utils/helper.py ===\ncode"
    parsed = parse_batch_content(text, tmp_path)
    assert (tmp_path / "src" / "utils" / "helper.py") in parsed
