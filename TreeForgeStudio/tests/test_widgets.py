"""Widget-level tests for the text editor and multi-file editor.

These tests are optional-import (skipped automatically when PyQt6 is not
installed) so the analytical suite can still run headless.
"""

from __future__ import annotations

import contextlib
import sys
import tempfile
from pathlib import Path

import pytest

pytest.importorskip("PyQt6", reason="PyQt6 is required for widget tests")

from PyQt6.QtWidgets import QApplication, QMessageBox  # noqa: E402

from app.widgets.text_editor import TextEditor  # noqa: E402
from app.widgets.multi_file_editor import MultiFileEditor  # noqa: E402
from app.widgets.project_explorer import ProjectExplorer, ExplorerRole  # noqa: E402
from app.tree_parser import parse_tree  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    """A single QApplication for all widget tests in this module."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv or [])
    return app


@pytest.fixture()
def editor(qapp):
    return TextEditor()


def _discard_dialogs(monkeypatch):
    """Make unsaved-change prompts auto-discard so tests are non-interactive."""
    monkeypatch.setattr(
        QMessageBox,
        "question",
        classmethod(lambda cls, *a, **k: QMessageBox.StandardButton.Discard),
    )


# ----------------------------------------------------------------------
# Text editor: content & dirty state
# ----------------------------------------------------------------------

def test_editor_dirty_state(editor):
    editor.set_content("original")
    assert not editor.is_modified()
    editor._editor.setPlainText("changed")
    assert editor.is_modified()
    editor.mark_clean()
    assert not editor.is_modified()


def test_editor_unicode_roundtrip(editor):
    content = "محتوى عربي\nEmoji 🎉🚀\nEnglish"
    editor.set_content(content)
    assert editor.get_content() == content


def test_find_selects_match(editor):
    editor.set_content("alpha beta gamma")
    editor._do_find("gamma", False, False, False)
    assert editor._editor.textCursor().hasSelection()


def test_replace_all_case_insensitive(editor):
    editor.set_content("Hello hello HELLO")
    editor._do_replace_all("hello", "X", False, False)
    assert editor.get_content() == "X X X"


def test_replace_all_case_sensitive(editor):
    editor.set_content("Hello hello HELLO")
    editor._do_replace_all("hello", "X", True, False)
    assert editor.get_content() == "Hello X HELLO"


def test_replace_all_whole_words(editor):
    editor.set_content("cat category cats cat")
    editor._do_replace_all("cat", "DOG", False, True)
    assert editor.get_content() == "DOG category cats DOG"


def test_replace_all_empty_find_is_noop(editor):
    editor.set_content("unchanged")
    editor._do_replace_all("", "X", False, False)
    assert editor.get_content() == "unchanged"


def test_replace_all_undoable(editor):
    editor.set_content("a a a")
    editor._do_replace_all("a", "b", False, False)
    editor._editor.undo()
    assert editor.get_content() == "a a a"


# ----------------------------------------------------------------------
# Multi-file editor
# ----------------------------------------------------------------------

def test_multi_open_and_count(qapp):
    mfe = MultiFileEditor()
    with temp_dir() as d:
        p1, p2 = Path(d) / "a.py", Path(d) / "b.py"
        p1.write_text("A", encoding="utf-8")
        p2.write_text("B", encoding="utf-8")
        mfe.open_file(p1, "A content")
        mfe.open_file(p2, "B content")
        assert mfe.count() == 2


def test_multi_save_writes_distinct_content(qapp):
    mfe = MultiFileEditor()
    with temp_dir() as d:
        p1, p2 = Path(d) / "a.py", Path(d) / "b.md"
        for p in (p1, p2):
            p.write_text("seed", encoding="utf-8")
        mfe.open_file(p1, "content A")
        mfe.open_file(p2, "محتوى ب عربي")
        mfe._tabs.widget(0).set_content("final A")
        mfe._tabs.widget(1).set_content("final B")
        mfe.save_all()
        assert p1.read_text(encoding="utf-8") == "final A"
        assert p2.read_text(encoding="utf-8") == "final B"


def test_multi_close_middle_tab_preserves_paths(qapp, monkeypatch):
    _discard_dialogs(monkeypatch)
    mfe = MultiFileEditor()
    with temp_dir() as d:
        p1, p2, p3 = Path(d) / "a.py", Path(d) / "b.py", Path(d) / "c.py"
        for p in (p1, p2, p3):
            p.write_text("seed", encoding="utf-8")
        mfe.open_file(p1, "A")
        mfe.open_file(p2, "B")
        mfe.open_file(p3, "C")
        mfe._close_tab_at(1)
        remaining = [mfe._tabs.widget(i).get_path().name for i in range(mfe.count())]
        assert remaining == ["a.py", "c.py"]
        # Saving after reindex must write to the correct remaining files.
        mfe._tabs.widget(0).set_content("new A")
        mfe._tabs.widget(1).set_content("new C")
        mfe.save_all()
        assert p1.read_text(encoding="utf-8") == "new A"
        assert p2.read_text(encoding="utf-8") == "seed"  # untouched
        assert p3.read_text(encoding="utf-8") == "new C"


def test_multi_unsaved_count(qapp):
    mfe = MultiFileEditor()
    with temp_dir() as d:
        p = Path(d) / "a.py"
        p.write_text("x", encoding="utf-8")
        mfe.open_file(p, "content")
        assert mfe.unsaved_count() == 0
        # Simulate a real keystroke edit, which marks the document modified.
        mfe._tabs.widget(0)._editor.appendPlainText(" edited")
        assert mfe.unsaved_count() == 1


def test_multi_set_editor_font(qapp):
    mfe = MultiFileEditor()
    with temp_dir() as d:
        p = Path(d) / "a.py"
        p.write_text("x", encoding="utf-8")
        mfe.open_file(p, "content")
        # Must not raise.
        mfe.set_editor_font("Courier New", 14)
        assert mfe._tabs.widget(0)._editor.font().pointSize() == 14


# ----------------------------------------------------------------------
# Project explorer
# ----------------------------------------------------------------------

def test_explorer_counts_only_files(qapp):
    ex = ProjectExplorer()
    result = parse_tree(
        "Root/\n├── main.py\n├── ui/\n│   ├── w.py\n│   └── s.py\n└── core/\n    └── a.py"
    )
    ex.load_from_tree(result.root)
    assert ex.count_files() == 4  # main, w, s, a — not the directories


def test_explorer_folder_selection_includes_descendants(qapp):
    ex = ProjectExplorer()
    result = parse_tree("Root/\n├── core/\n│   ├── a.py\n│   └── b.py\n└── main.py")
    ex.load_from_tree(result.root)

    is_file_role = ExplorerRole.IS_FILE.value

    def find(parent, name, want_dir):
        for row in range(parent.rowCount()):
            it = parent.child(row, 0)
            if it is None:
                continue
            if it.text() == name and bool(it.data(is_file_role)) == (not want_dir):
                return it
            found = find(it, name, want_dir)
            if found:
                return found
        return None

    model = ex._model
    core = find(model.item(0, 0), "core", want_dir=True)
    assert core is not None
    from PyQt6.QtCore import QItemSelectionModel

    ex._tree.selectionModel().select(
        model.indexFromItem(core),
        QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows,
    )
    assert set(ex.all_files_under_selection()) == {"core/a.py", "core/b.py"}


def test_explorer_clear(qapp):
    ex = ProjectExplorer()
    result = parse_tree("Root/\n└── main.py")
    ex.load_from_tree(result.root)
    assert ex.count_files() == 1
    ex.clear()
    assert ex.count_files() == 0


@contextlib.contextmanager
def temp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d
