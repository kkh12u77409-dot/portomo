"""Project explorer widget: interactive file/folder tree.

Displays the parsed project structure and the real filesystem created from it.
Supports selection, search filtering, context menus, and multi-selection
across files.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from PyQt6.QtCore import Qt, QModelIndex, QPoint
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QAction
from PyQt6.QtWidgets import (
    QTreeView,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QMenu,
    QAbstractItemView,
)

from app.icons import get_icon


class ExplorerRole(Enum):
    """Roles for custom data stored on tree items."""

    NODE_ID = Qt.ItemDataRole.UserRole + 1
    IS_FILE = Qt.ItemDataRole.UserRole + 2
    REL_PATH = Qt.ItemDataRole.UserRole + 3
    IS_READ_ONLY = Qt.ItemDataRole.UserRole + 4
    IS_MISSING = Qt.ItemDataRole.UserRole + 5


@dataclass
class ExplorerNode:
    """A node in the explorer model."""

    name: str
    rel_path: str
    is_file: bool
    is_read_only: bool = False
    is_missing: bool = False
    children: list["ExplorerNode"] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.children is None:
            self.children = []


class _ExplorerModel(QStandardItemModel):
    """Standard item model wrapped for our node data."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setHorizontalHeaderLabels(["Project"])

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        base = (
            Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsDropEnabled
        )
        item = self.itemFromIndex(index)
        if item is not None and bool(item.data(ExplorerRole.IS_FILE.value)):
            base |= Qt.ItemFlag.ItemIsEditable
        return base


class ProjectExplorer(QWidget):
    """Interactive project file/folder tree with search and context menus."""

    files_selected = None  # signal emitted externally via PyQt6
    file_activated = None

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._nodes: list[ExplorerNode] = []
        self._all_rel_paths: set[str] = set()
        self._file_icon = get_icon("file-text", 20, "#60A5FA")
        self._dir_icon = get_icon("folder", 20, "#FBBF24")
        self._root_icon = get_icon("app", 20, "#34D399")
        self._build_ui()
        self.setObjectName("ProjectExplorer")

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Search row
        self._search = QLineEdit()
        self._search.setObjectName("ExplorerSearch")
        self._search.setPlaceholderText(self.tr("Search files and folders..."))
        self._search.setClearButtonEnabled(True)
        self._search.textChanged.connect(self._on_search_changed)
        layout.addWidget(self._search)

        # Tree view
        self._tree = QTreeView()
        self._tree.setObjectName("ProjectTree")
        self._tree.setHeaderHidden(True)
        self._tree.setUniformRowHeights(True)
        self._tree.setIconSize(self._tree.iconSize().scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio))
        self._tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._show_context_menu)
        self._tree.doubleClicked.connect(self._on_double_clicked)
        self._model = _ExplorerModel(self)
        self._tree.setModel(self._model)
        layout.addWidget(self._tree)

        # Status label
        self._status = QLabel(self.tr("No project loaded."))
        self._status.setObjectName("ExplorerStatus")
        self._status.setWordWrap(False)
        layout.addWidget(self._status)

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def load_nodes(self, nodes: list[ExplorerNode]) -> None:
        """Replace the entire tree with *nodes*."""
        self._nodes = nodes
        self._all_rel_paths = set()
        self._collect_paths(self._nodes)
        self._rebuild_model("")

    def load_from_tree(self, tree) -> None:  # tree: TreeNode
        """Build explorer nodes from a parsed :class:`TreeNode`."""
        root_node = self._build_from_treenode(tree)
        # Expose the root as a single top-level node whose children are the
        # actual project contents.
        nodes = [root_node]
        self.load_nodes(nodes)

    def _build_from_treenode(self, node) -> ExplorerNode:
        entry = ExplorerNode(
            name=node.name,
            rel_path=node.path,
            is_file=node.is_file(),
        )
        for child in node.children.values():
            entry.children.append(self._build_from_treenode(child))
        for fnode in node.files.values():
            entry.children.append(
                ExplorerNode(
                    name=fnode.name,
                    rel_path=fnode.path,
                    is_file=True,
                )
            )
        return entry

    def _collect_paths(self, nodes: list[ExplorerNode]) -> None:
        for n in nodes:
            self._all_rel_paths.add(n.rel_path)
            self._collect_paths(n.children or [])

    # ------------------------------------------------------------------
    # Model building
    # ------------------------------------------------------------------

    def _rebuild_model(self, filter_text: str) -> None:
        self._model.clear()
        self._model.setHorizontalHeaderLabels(["Project"])
        root = self._model.invisibleRootItem()
        filter_lower = filter_text.strip().lower()
        for node in self._nodes:
            self._add_item(node, root, filter_lower)
        if filter_lower:
            self._tree.expandAll()
        if self._nodes:
            self._tree.expandToDepth(0)

    def _add_item(
        self, node: ExplorerNode, parent: QStandardItem, filter_text: str
    ) -> Optional[QStandardItem]:
        name_matches = not filter_text or filter_text in node.name.lower()
        if node.is_file:
            if filter_text and not name_matches:
                return None
            item = QStandardItem(self._file_icon, node.name)
            item.setData(node.rel_path, ExplorerRole.REL_PATH.value)
            item.setData(True, ExplorerRole.IS_FILE.value)
            item.setData(node.is_read_only, ExplorerRole.IS_READ_ONLY.value)
            item.setData(node.is_missing, ExplorerRole.IS_MISSING.value)
            item.setEditable(False)
            parent.appendRow(item)
            return item
        else:
            item = QStandardItem(self._dir_icon, node.name)
            item.setData(node.rel_path, ExplorerRole.REL_PATH.value)
            item.setData(False, ExplorerRole.IS_FILE.value)
            item.setData(node.is_read_only, ExplorerRole.IS_READ_ONLY.value)
            item.setData(node.is_missing, ExplorerRole.IS_MISSING.value)
            item.setEditable(False)
            parent.appendRow(item)
            child_appended = False
            for child in node.children or []:
                if self._add_item(child, item, filter_text):
                    child_appended = True
            return item if (not filter_text or name_matches or child_appended) else item

    # ------------------------------------------------------------------
    # Selection helpers
    # ------------------------------------------------------------------

    def selected_file_paths(self) -> list[str]:
        """Return the relative paths of all selected files (recursive)."""
        selected = self._tree.selectedIndexes()
        files: list[str] = []
        for index in selected:
            item = self._model.itemFromIndex(index)
            if item is None:
                continue
            if bool(item.data(ExplorerRole.IS_FILE.value)):
                path = str(item.data(ExplorerRole.REL_PATH.value))
                if path and path not in files:
                    files.append(path)
        return files

    def selected_folder_nodes(self) -> list[str]:
        """Return relative paths of selected directories."""
        selected = self._tree.selectedIndexes()
        folders: list[str] = []
        for index in selected:
            item = self._model.itemFromIndex(index)
            if item is None:
                continue
            if not bool(item.data(ExplorerRole.IS_FILE.value)):
                path = str(item.data(ExplorerRole.REL_PATH.value))
                if path and path not in folders:
                    folders.append(path)
        return folders

    def all_files_under_selection(self) -> list[str]:
        """Return all file relative paths under currently selected items.

        Selecting folders includes all their descendant files.
        """
        selected = self._tree.selectedIndexes()
        rel_paths: list[str] = []

        def _collect(item: QStandardItem) -> None:
            if bool(item.data(ExplorerRole.IS_FILE.value)):
                path = str(item.data(ExplorerRole.REL_PATH.value))
                if path and path not in rel_paths:
                    rel_paths.append(path)
                return
            # Directory: recurse
            for row in range(item.rowCount()):
                child = item.child(row, 0)
                if child is not None:
                    _collect(child)

        for index in selected:
            item = self._model.itemFromIndex(index)
            if item is not None:
                _collect(item)
        return rel_paths

    def selected_file_count(self) -> int:
        return len(self.selected_file_paths())

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_search_changed(self, text: str) -> None:
        self._rebuild_model(text)

    def _on_double_clicked(self, index: QModelIndex) -> None:
        item = self._model.itemFromIndex(index)
        if item is None:
            return
        if bool(item.data(ExplorerRole.IS_FILE.value)):
            path = str(item.data(ExplorerRole.REL_PATH.value))
            # Notify listeners
            if self.file_activated is not None:
                self.file_activated(path)

    def _show_context_menu(self, pos: QPoint) -> None:
        index = self._tree.indexAt(pos)
        if index.isValid():
            self._tree.selectionModel().select(
                index,
                self._tree.selectionModel().SelectionFlag.Select
                | self._tree.selectionModel().SelectionFlag.Rows,
            )
        menu = QMenu(self)

        files = self.selected_file_paths()

        if files:
            edit_action = QAction(get_icon("edit", 16, "#60A5FA"), self.tr("Open in Editor"), self)
            edit_action.triggered.connect(lambda: self._emit_file_activated(files[0]))
            menu.addAction(edit_action)

        if files:
            multi_action = QAction(get_icon("layers", 16, "#60A5FA"), self.tr("Open in Multi-File Editor"), self)
            multi_action.triggered.connect(lambda: self._emit_multi_open(files))
            menu.addAction(multi_action)
            menu.addSeparator()

        expand_action = QAction(get_icon("folder-open", 16, "#FBBF24"), self.tr("Expand All"), self)
        expand_action.triggered.connect(self._tree.expandAll)
        menu.addAction(expand_action)

        collapse_action = QAction(get_icon("folder", 16, "#FBBF24"), self.tr("Collapse All"), self)
        collapse_action.triggered.connect(self._tree.collapseAll)
        menu.addAction(collapse_action)

        menu.addSeparator()
        refresh_action = QAction(get_icon("refresh", 16, "#94A3B8"), self.tr("Refresh"), self)
        refresh_action.triggered.connect(self.refresh)
        menu.addAction(refresh_action)

        menu.exec(self._tree.mapToGlobal(pos))

    def _emit_file_activated(self, path: str) -> None:
        if self.file_activated is not None:
            self.file_activated(path)

    def _emit_multi_open(self, paths: list[str]) -> None:
        if hasattr(self, "multi_open"):
            self.multi_open(paths)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """Clear the explorer."""
        self._nodes = []
        self._all_rel_paths = set()
        self._model.clear()
        self._model.setHorizontalHeaderLabels(["Project"])
        self._update_status()

    def count_files(self) -> int:
        return len(self._all_rel_paths)

    def _update_status(self) -> None:
        total = self.count_files()
        if total == 0:
            self._status.setText(self.tr("No project loaded."))
        else:
            plural = "s" if total != 1 else ""
            self._status.setText(f"{total} file{plural}")

    def refresh(self) -> None:
        """Refresh the tree from the internal nodes."""
        text = self._search.text()
        self._rebuild_model(text)
        self._update_status()

    def get_selected_path(self) -> Optional[str]:
        files = self.selected_file_paths()
        return files[0] if files else None
