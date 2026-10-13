"""Multi-file editor widget: opens several files as separate tabs.

Each tab has an independent editor, unsaved-change indicator, and file path.
Supports Save All with per-file result reporting.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QPushButton,
    QLabel,
    QMessageBox,
    QFileDialog,
)

from app.widgets.text_editor import TextEditor
from app.icons import get_icon


@dataclass
class OpenFileEntry:
    """Bookkeeping for one open file tab."""

    path: Optional[Path]
    is_read_only: bool = False
    error_message: str = ""


class MultiFileEditor(QWidget):
    """Tabbed editor for editing different content in multiple files."""

    files_saved = pyqtSignal(list)  # list of FileWriteResult
    status_message = pyqtSignal(str, str)  # kind, message

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._entries: dict[int, OpenFileEntry] = {}
        self._build_ui()
        self.setObjectName("MultiFileEditor")

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Toolbar row
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self._save_all_button = QPushButton(get_icon("save-all", 16, "#FFFFFF"), self.tr("Save All"))
        self._save_all_button.setObjectName("accent")
        self._save_all_button.setToolTip(self.tr("Save all open files"))
        self._save_all_button.clicked.connect(self.save_all)
        toolbar.addWidget(self._save_all_button)

        self._save_selected_button = QPushButton(get_icon("save", 16, "#60A5FA"), self.tr("Save Current"))
        self._save_selected_button.clicked.connect(self.save_current)
        toolbar.addWidget(self._save_selected_button)

        self._close_tab_button = QPushButton(get_icon("close", 16, "#F87171"), self.tr("Close Tab"))
        self._close_tab_button.clicked.connect(self.close_current_tab)
        toolbar.addWidget(self._close_tab_button)

        self._status_label = QLabel(self.tr("No open files"))
        self._status_label.setObjectName("MultiStatus")
        toolbar.addStretch(1)
        toolbar.addWidget(self._status_label)
        layout.addLayout(toolbar)

        # Tabs
        self._tabs = QTabWidget()
        self._tabs.setTabsClosable(True)
        self._tabs.setObjectName("MultiTabs")
        self._tabs.tabCloseRequested.connect(self._close_tab_at)
        self._tabs.currentChanged.connect(self._on_tab_changed)
        layout.addWidget(self._tabs)

        # Empty state
        self._empty_widget = QLabel(self.tr("No open files"))
        self._empty_widget.setObjectName("MultiEmpty")
        self._empty_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._empty_widget)
        self._empty_widget.hide()
        self._update_visibility()

    # ------------------------------------------------------------------
    # Tab management
    # ------------------------------------------------------------------

    def open_file(self, path: Path, content: Optional[str] = None, read_only: bool = False) -> Optional[int]:
        """Open a file in a new or existing tab.  Returns the tab index."""
        for i in range(self._tabs.count()):
            entry = self._entries.get(i)
            if entry and entry.path == path:
                self._tabs.setCurrentIndex(i)
                return i
        editor = TextEditor(self)
        editor.set_path(path)
        entry = OpenFileEntry(path=path, is_read_only=read_only)

        if content is None:
            # Will be loaded by the host application.
            content = ""
        editor.set_content(content)
        editor.set_read_only(read_only)

        name = path.name if path else self.tr("New File")
        index = self._tabs.addTab(editor, name)
        self._entries[index] = entry
        # Bind the tab index explicitly to avoid late-binding closure bugs.
        editor.content_changed.connect(
            lambda _checked=False, idx=index: self._on_content_changed(idx)
        )
        self._on_content_changed(index)
        self._tabs.setCurrentIndex(index)
        self._update_visibility()
        return index

    def open_blank(self, suggested_name: Optional[str] = None) -> Optional[int]:
        editor = TextEditor(self)
        editor.set_path(None)
        editor.set_content("")
        name = suggested_name or self.tr("New File")
        index = self._tabs.addTab(editor, name)
        self._entries[index] = OpenFileEntry(path=None)
        self._tabs.setCurrentIndex(index)
        self._update_visibility()
        return index

    def _close_tab_at(self, index: int) -> None:
        if index not in range(self._tabs.count()):
            return
        editor = self._tabs.widget(index)
        if isinstance(editor, TextEditor) and editor.is_modified():
            result = QMessageBox.question(
                self,
                self.tr("Save Changes"),
                self.tr("Save changes to '{filename}'?").format(filename=self._tab_name(editor)),
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save,
            )
            if result == QMessageBox.StandardButton.Cancel:
                return
            if result == QMessageBox.StandardButton.Save:
                self._save_editor(index)

        self._tabs.removeTab(index)
        self._entries.pop(index, None)
        self._reindex_entries()
        self._update_visibility()

    def _reindex_entries(self) -> None:
        """Rebuild the entry map so it matches the current tab order.

        Each :class:`TextEditor` holds its own path, so the mapping is
        re-derived from the widgets, which stay correct after a tab close
        shifts the remaining tabs.
        """
        new_entries: dict[int, OpenFileEntry] = {}
        for i in range(self._tabs.count()):
            editor = self._tabs.widget(i)
            if isinstance(editor, TextEditor):
                new_entries[i] = OpenFileEntry(
                    path=editor.get_path(),
                    is_read_only=editor.isReadOnly(),
                )
            else:
                new_entries[i] = OpenFileEntry(path=None)
        self._entries = new_entries

    def close_current_tab(self) -> None:
        self._close_tab_at(self._tabs.currentIndex())

    def _tab_name(self, editor: TextEditor) -> str:
        path = editor.get_path()
        if path:
            return path.name
        text = self._tabs.tabText(self._tabs.indexOf(editor))
        return text

    # ------------------------------------------------------------------
    # Dirty state
    # ------------------------------------------------------------------

    def _on_content_changed(self, index: int) -> None:
        if index >= self._tabs.count():
            return
        editor = self._tabs.widget(index)
        if isinstance(editor, TextEditor):
            label = self._tab_name(editor)
            if editor.is_modified():
                self._tabs.setTabText(index, f"● {label}")
            else:
                self._tabs.setTabText(index, label)

    def _on_tab_changed(self, index: int) -> None:
        self._update_status()

    # ------------------------------------------------------------------
    # Saving
    # ------------------------------------------------------------------

    def save_all(self) -> None:
        """Save every dirty tab.  Emits ``files_saved`` with the results."""
        from app.file_content_service import FileContentService, FileWriteResult

        results: list[FileWriteResult] = []
        service = FileContentService()
        for index in range(self._tabs.count()):
            editor = self._tabs.widget(index)
            if isinstance(editor, TextEditor):
                if self._save_editor(index, service=service):
                    results.append(True)
                else:
                    results.append(False)
        self._update_status()
        self.files_saved.emit(results)

    def save_current(self) -> None:
        self._save_editor(self._tabs.currentIndex())

    def _save_editor(self, index: int, service: Optional[object] = None) -> bool:
        """Save a single editor's content.  Returns True on success."""
        from app.file_content_service import FileContentService, FileWriteResult, WriteMode

        if not (0 <= index < self._tabs.count()):
            return False
        editor = self._tabs.widget(index)
        if not isinstance(editor, TextEditor):
            return False

        path = editor.get_path()
        if path is None:
            return self._save_as(editor, index)

        if service is None:
            service = FileContentService()
        result: FileWriteResult = service.write_file(path, editor.get_content(), WriteMode.REPLACE)
        if result.success:
            editor.mark_clean()
            self._on_content_changed(index)
            self.status_message.emit("info", self.tr("Saved: {path}").format(path=str(path)))
        else:
            self.status_message.emit("error", self.tr("Failed to save {name}: {error}").format(
                name=editor.get_path().name, error=result.message
            ))
        return result.success

    def _save_as(self, editor: TextEditor, index: int) -> bool:
        """Save a tab with no path using a Save As dialog."""
        path, _ = QFileDialog.getSaveFileName(
            self, self.tr("Save As"), "", self.tr("Text Files (*.txt *.py *.md *.json *.csv);;All Files (*)")
        )
        if not path:
            return False
        editor.set_path(Path(path))
        entry = self._entries.get(index, OpenFileEntry(path=Path(path)))
        entry.path = Path(path)
        self._entries[index] = entry
        self._on_content_changed(index)
        return self._save_editor(index)

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def count(self) -> int:
        return self._tabs.count()

    def has_unsaved(self) -> bool:
        return any(
            isinstance(self._tabs.widget(i), TextEditor) and self._tabs.widget(i).is_modified()
            for i in range(self._tabs.count())
        )

    def unsaved_count(self) -> int:
        return sum(
            1
            for i in range(self._tabs.count())
            if isinstance(self._tabs.widget(i), TextEditor) and self._tabs.widget(i).is_modified()
        )

    def save_all_if_needed(self) -> bool:
        """Prompt the user about unsaved changes.  Returns False to abort closing."""
        if not self.has_unsaved():
            return True
        count = self.unsaved_count()
        msg = QMessageBox(self)
        msg.setWindowTitle(self.tr("Save Changes"))
        msg.setText(self.tr("You have unsaved changes in {count} file(s).").format(count=count))
        msg.setStandardButtons(
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
        )
        msg.setDefaultButton(QMessageBox.StandardButton.Save)
        result = msg.exec()
        if result == QMessageBox.StandardButton.Save:
            self.save_all()
            return not self.has_unsaved()
        if result == QMessageBox.StandardButton.Discard:
            return True
        return False

    def set_editor_font(self, family: str, size: int) -> None:
        for i in range(self._tabs.count()):
            editor = self._tabs.widget(i)
            if isinstance(editor, TextEditor):
                editor.set_font(family, size)

    def close_all(self) -> bool:
        """Close all tabs, prompting for unsaved changes.  Returns False if cancelled."""
        if self.has_unsaved() and not self.save_all_if_needed():
            return False
        while self._tabs.count():
            self._tabs.removeTab(0)
        self._entries.clear()
        self._update_visibility()
        return True

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def _update_visibility(self) -> None:
        has_tabs = self._tabs.count() > 0
        self._tabs.setVisible(has_tabs)
        self._empty_widget.setVisible(not has_tabs)

    def _update_status(self) -> None:
        total = self._tabs.count()
        modified = self.unsaved_count()
        parts = [f"{total} open"]
        if modified:
            parts.append(f"{modified} modified")
        self._status_label.setText(self.tr(", ").join(parts) if total else self.tr("No open files"))
