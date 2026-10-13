"""Shared pytest configuration and fixtures for TreeForge Studio tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure the project root is importable so ``app`` can be imported.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture()
def qapp():
    """Provide a QApplication instance for widget tests (GUI-optional)."""
    try:
        from PyQt6.QtWidgets import QApplication
    except ImportError:
        pytest.skip("PyQt6 is not installed")
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.fixture(autouse=True)
def _isolate_qsettings(qapp, tmp_path, monkeypatch):
    """Redirect QSettings to a temporary file so tests never touch user prefs."""
    from PyQt6.QtCore import QSettings

    ini_path = str(tmp_path / "treeforge_test.ini")
    QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, ini_path)
    yield
