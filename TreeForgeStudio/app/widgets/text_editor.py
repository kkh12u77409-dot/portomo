"""Text editor widget with find/replace, UTF-8 support, and dirty state.

A plain-text editor (QPlainTextEdit subclass) used for editing file
contents.  It intentionally never renders HTML or executes code.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import (
    QFont,
    QTextCursor,
    QTextDocument,
)
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPlainTextEdit,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QFrame,
)


class FindReplaceBar(QFrame):
    """A find/replace bar docked above the editor."""

    find_next_requested = pyqtSignal(str, bool, bool, bool)  # text, case, whole, backwards
    replace_current_requested = pyqtSignal(str, str, bool, bool)  # find, replace, case, whole
    replace_all_requested = pyqtSignal(str, str, bool, bool)
    close_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("FindReplaceBar")
        self._build_ui()
        self.hide()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(6)

        self._find_input = QLineEdit()
        self._find_input.setPlaceholderText(self.tr("Find"))
        self._find_input.setObjectName("FindInput")
        self._find_input.setMinimumWidth(160)
        layout.addWidget(self._find_input, 1)

        self._replace_input = QLineEdit()
        self._replace_input.setPlaceholderText(self.tr("Replace"))
        self._replace_input.setObjectName("ReplaceInput")
        self._replace_input.setMinimumWidth(160)
        layout.addWidget(self._replace_input, 1)

        self._case_check = QCheckBox(self.tr("Aa"))
        self._case_check.setToolTip(self.tr("Case sensitive"))
        self._case_check.setObjectName("CaseCheck")
        layout.addWidget(self._case_check)

        self._whole_check = QCheckBox("ab")
        self._whole_check.setToolTip(self.tr("Whole words"))
        self._whole_check.setObjectName("WholeCheck")
        layout.addWidget(self._whole_check)

        self._prev_button = QPushButton(self.tr("Previous"))
        self._prev_button.clicked.connect(self._emit_next_backwards)
        layout.addWidget(self._prev_button)

        self._next_button = QPushButton(self.tr("Next"))
        self._next_button.clicked.connect(self._emit_next)
        layout.addWidget(self._next_button)

        self._replace_button = QPushButton(self.tr("Replace"))
        self._replace_button.clicked.connect(self._emit_replace)
        layout.addWidget(self._replace_button)

        self._replace_all_button = QPushButton(self.tr("Replace All"))
        self._replace_all_button.clicked.connect(self._emit_replace_all)
        self._replace_all_button.setObjectName("ReplaceAllButton")
        layout.addWidget(self._replace_all_button)

        self._close_button = QPushButton(self.tr("Close"))
        self._close_button.clicked.connect(self.close_requested.emit)
        self._close_button.setObjectName("CloseFindButton")
        layout.addWidget(self._close_button)

        self._find_input.returnPressed.connect(self._emit_next)

    def _get_options(self) -> tuple[str, bool, bool]:
        return (
            self._find_input.text(),
            self._case_check.isChecked(),
            self._whole_check.isChecked(),
        )

    def _emit_next(self) -> None:
        text, case, whole = self._get_options()
        self.find_next_requested.emit(text, case, whole, False)

    def _emit_next_backwards(self) -> None:
        text, case, whole = self._get_options()
        self.find_next_requested.emit(text, case, whole, True)

    def _emit_replace(self) -> None:
        text, case, whole = self._get_options()
        self.replace_current_requested.emit(text, self._replace_input.text(), case, whole)

    def _emit_replace_all(self) -> None:
        text, case, whole = self._get_options()
        self.replace_all_requested.emit(text, self._replace_input.text(), case, whole)

    def focus_find(self) -> None:
        self._find_input.setFocus()
        self._find_input.selectAll()

    def showEvent(self, event) -> None:  # type: ignore[override]
        super().showEvent(event)
        self.focus_find()


class TextEditor(QWidget):
    """A plain-text editor widget with dirty state and find/replace."""

    content_changed = pyqtSignal()
    cursor_moved = pyqtSignal(int, int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._path: Optional[Path] = None
        self._saved_text: str = ""
        self._encoding: str = "utf-8"
        self._build_ui()
        self._connect_signals()
        self.setObjectName("TextEditor")

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self._find_bar = FindReplaceBar(self)
        self._find_bar.find_next_requested.connect(self._do_find)
        self._find_bar.replace_current_requested.connect(self._do_replace_current)
        self._find_bar.replace_all_requested.connect(self._do_replace_all)
        self._find_bar.close_requested.connect(self._find_bar.hide)
        layout.addWidget(self._find_bar)

        self._editor = QPlainTextEdit()
        self._editor.setObjectName("EditorArea")
        self._editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self._editor.setTabStopDistance(32)
        layout.addWidget(self._editor)

    def _connect_signals(self) -> None:
        self._editor.textChanged.connect(self._on_text_changed)
        self._editor.cursorPositionChanged.connect(self._emit_cursor_position)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_path(self, path: Optional[Path]) -> None:
        self._path = path

    def get_path(self) -> Optional[Path]:
        return self._path

    def set_content(self, text: str) -> None:
        self._editor.setPlainText(text)
        self._saved_text = text
        self._editor.document().setModified(False)

    def get_content(self) -> str:
        return self._editor.toPlainText()

    def set_encoding(self, encoding: str) -> None:
        self._encoding = encoding

    def mark_clean(self) -> None:
        self._saved_text = self.get_content()
        self._editor.document().setModified(False)

    def is_modified(self) -> bool:
        return self._editor.document().isModified() or (self.get_content() != self._saved_text)

    def set_font(self, family: str, size: int) -> None:
        font = QFont(family, size)
        if not font.exactMatch():
            font = QFont("monospace", size)
        self._editor.setFont(font)

    def set_read_only(self, read_only: bool) -> None:
        self._editor.setReadOnly(read_only)

    def is_read_only(self) -> bool:
        """Return True if the inner editor is read-only."""
        return self._editor.isReadOnly()

    def focus_editor(self) -> None:
        self._editor.setFocus()

    # ------------------------------------------------------------------
    # Find / Replace
    # ------------------------------------------------------------------

    def show_find(self) -> None:
        self._find_bar.show()
        self._find_bar.focus_find()

    def hide_find(self) -> None:
        self._find_bar.hide()

    def _do_find(self, text: str, case_sensitive: bool, whole_words: bool, backwards: bool) -> None:
        if not text:
            return
        options = QTextDocument.FindFlag(0)
        if case_sensitive:
            options |= QTextDocument.FindFlag.FindCaseSensitively
        if whole_words:
            options |= QTextDocument.FindFlag.FindWholeWords
        if backwards:
            options |= QTextDocument.FindFlag.FindBackward
        found = self._editor.find(text, options)
        if not found:
            # Wrap around.
            cursor = self._editor.textCursor()
            cursor.movePosition(
                QTextCursor.MoveOperation.Start if backwards
                else QTextCursor.MoveOperation.End
            )
            self._editor.setTextCursor(cursor)
            self._editor.find(text, options)

    def _do_replace_current(
        self, find: str, replace: str, case_sensitive: bool, whole_words: bool
    ) -> None:
        cursor = self._editor.textCursor()
        if cursor.hasSelection() and self._matches(cursor.selectedText(), find, case_sensitive, whole_words):
            cursor.insertText(replace)
        self._do_find(find, case_sensitive, whole_words, False)

    def _do_replace_all(
        self, find: str, replace: str, case_sensitive: bool, whole_words: bool
    ) -> None:
        if not find:
            return
        import re as _re

        pattern = _re.escape(find)
        if whole_words:
            pattern = r"\b" + pattern + r"\b"
        flags = 0 if case_sensitive else _re.IGNORECASE
        try:
            compiled = _re.compile(pattern, flags)
        except _re.error:
            return
        text = self._editor.toPlainText()
        # ``re.sub`` treats backslashes in the replacement specially; keep
        # literal backslashes by escaping them.
        replacement = replace.replace("\\", "\\\\")
        new_text = compiled.sub(replacement, text)
        if new_text != text:
            cursor = self._editor.textCursor()
            cursor.beginEditBlock()
            cursor.select(QTextCursor.SelectionType.Document)
            cursor.insertText(new_text)
            cursor.endEditBlock()

    def _matches(self, text: str, find: str, case_sensitive: bool, whole_words: bool) -> bool:
        if not case_sensitive:
            text = text.lower()
            find = find.lower()
        if whole_words:
            return text == find
        return text == find

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_text_changed(self) -> None:
        self.content_changed.emit()

    def _emit_cursor_position(self) -> None:
        cursor = self._editor.textCursor()
        self.cursor_moved.emit(cursor.blockNumber() + 1, cursor.columnNumber() + 1)
