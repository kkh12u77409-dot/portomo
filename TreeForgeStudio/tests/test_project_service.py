"""Tests for the project service (structure creation)."""

from __future__ import annotations

import pytest

from app.tree_parser import parse_tree
from app.project_service import ProjectService, ConflictPolicy


TREE = """SumMaster/
├── main.py
├── README.md
├── assets/icons/
├── ui/ (main_window.py, spinner.py)
└── tests/ (test_main.py)"""


@pytest.fixture()
def parsed():
    return parse_tree(TREE)


@pytest.fixture()
def service(tmp_path):
    svc = ProjectService(tmp_path)
    svc.conflict_policy = ConflictPolicy.SKIP
    return svc


def test_creates_nested_directories(parsed, service, tmp_path):
    report = service.create_structure(parsed)
    assert report.total_failures == 0
    root = tmp_path / "SumMaster"
    assert root.is_dir()
    assert (root / "assets" / "icons").is_dir()
    assert (root / "ui").is_dir()
    assert (root / "tests").is_dir()


def test_creates_empty_directory(parsed, service, tmp_path):
    service.create_structure(parsed)
    # assets/icons/ is effectively empty (no declared children).
    icons = tmp_path / "SumMaster" / "assets" / "icons"
    assert icons.is_dir()
    assert list(icons.iterdir()) == []


def test_creates_files(parsed, service, tmp_path):
    report = service.create_structure(parsed)
    root = tmp_path / "SumMaster"
    assert (root / "main.py").is_file()
    assert (root / "README.md").is_file()
    assert (root / "ui" / "main_window.py").is_file()
    assert (root / "ui" / "spinner.py").is_file()
    assert report.files_created >= 5


def test_does_not_overwrite_existing_files_by_default(parsed, service, tmp_path):
    root = tmp_path / "SumMaster"
    root.mkdir()
    (root / "main.py").write_text("PRESERVED", encoding="utf-8")
    service.conflict_policy = ConflictPolicy.SKIP
    report = service.create_structure(parsed)
    assert (root / "main.py").read_text(encoding="utf-8") == "PRESERVED"
    assert report.files_skipped >= 1


def test_error_policy_halts_on_conflict(parsed, service, tmp_path):
    root = tmp_path / "SumMaster"
    root.mkdir()
    (root / "main.py").write_text("EXISTING", encoding="utf-8")
    service.conflict_policy = ConflictPolicy.ERROR
    report = service.create_structure(parsed)
    assert report.total_failures > 0
    assert (root / "main.py").read_text(encoding="utf-8") == "EXISTING"


def test_backup_policy(parsed, service, tmp_path):
    root = tmp_path / "SumMaster"
    root.mkdir()
    (root / "main.py").write_text("ORIGINAL", encoding="utf-8")
    service.conflict_policy = ConflictPolicy.BACKUP
    report = service.create_structure(parsed)
    assert (root / "main.py.bak").is_file()
    assert (root / "main.py.bak").read_text(encoding="utf-8") == "ORIGINAL"
    assert report.files_backed_up >= 1


def test_preserves_nested_relationships(parsed, service, tmp_path):
    service.create_structure(parsed)
    ui_dir = tmp_path / "SumMaster" / "ui"
    assert ui_dir.is_dir()
    assert (ui_dir / "main_window.py").is_file()


def test_rejects_path_traversal(tmp_path):
    tree = "Root/\n├── ../escape\n└── main.py"
    parsed = parse_tree(tree)
    svc = ProjectService(tmp_path)
    errors = svc.validate_tree(parsed)
    assert errors


def test_resolve_file_path_blocks_traversal(tmp_path):
    svc = ProjectService(tmp_path)
    assert svc.resolve_file_path("main.py") is not None
    assert svc.resolve_file_path("../../etc/passwd") is None


def test_partial_report_counts(parsed, service, tmp_path):
    report = service.create_structure(parsed)
    assert report.directories_created > 0
    assert report.files_created > 0
