"""Main window for TreeForge Studio.

Holds the toolbar, navigation sidebar, tree-input dashboard, destination
selector, project explorer, editor, batch editor and settings panel.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QToolBar,
    QStatusBar,
    QLabel,
    QPushButton,
    QLineEdit,
    QPlainTextEdit,
    QFileDialog,
    QComboBox,
    QMessageBox,
    QTreeWidget,
    QTreeWidgetItem,
    QStackedWidget,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
    QSpinBox,
    QGroupBox,
    QCheckBox,
    QApplication,
    QFrame,
)

from app import __version__
from app.tree_parser import NodeKind, ParseResult, TreeNode, parse_tree
from app.project_service import ProjectService, ConflictPolicy, CreationReport
from app.file_content_service import (
    FileContentService,
    FileWriteResult,
    WriteMode,
    parse_batch_content,
)
from app.settings_service import SettingsService
from app.theme_manager import apply_theme, get_theme, available_themes
from app.translations import (
    tr,
    set_language,
    is_rtl,
    available_languages,
)
from app.icons import icon as make_icon
from app.widgets.project_explorer import ProjectExplorer
from app.widgets.text_editor import TextEditor
from app.widgets.multi_file_editor import MultiFileEditor
from app.widgets.progress_dialog import ProgressDialog


class MainWindow(QMainWindow):
    """The main application window."""

    def __init__(
        self,
        settings: SettingsService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.settings = settings

        # ---- internal state ------------------------------------------------
        self._parse_result: Optional[ParseResult] = None
        self._project_service: Optional[ProjectService] = None
        self._file_service = FileContentService()
        self._current_destination: Optional[Path] = None
        self._accent_color = "#3B82F6"
        self._language = "en"
        self._theme_name = "dark"

        # ---- construction --------------------------------------------------
        self.setWindowTitle(f"{tr('app_name')} — {tr('app_version').format(version=__version__)}")
        self.setMinimumSize(1100, 700)
        self.resize(
            int(settings.get("window_width", 1400)),
            int(settings.get("window_height", 900)),
        )
        x = int(settings.get("window_x", -1))
        y = int(settings.get("window_y", -1))
        if x >= 0 and y >= 0:
            self.move(x, y)

        # ---- window geometry restore -------------------------------------
        self._restore_window_geometry(settings)

        # ---- setup ---------------------------------------------------------
        self._restore_from_settings()
        self._build_menu_bar()
        self._build_toolbar()
        self._build_status_bar()
        self._build_central()
        self._apply_theme_and_language()
        self._build_shortcuts()

    # ==================================================================
    # Window geometry / restore
    # ==================================================================

    def _restore_window_geometry(self, settings: SettingsService) -> None:
        """Restore the saved Qt window geometry and state (best effort)."""
        geometry = settings.get("geometry", "")
        if isinstance(geometry, str) and geometry:
            try:
                from PyQt6.QtCore import QByteArray

                self.restoreGeometry(QByteArray.fromLatin1(geometry.encode("latin1")))
            except (ValueError, TypeError):
                pass

    def closeEvent(self, event) -> None:  # type: ignore[override]
        # Warn about unsaved changes.
        if not self._multi_editor.close_all():
            event.ignore()
            return
        # Save window size and geometry.
        geo = self.geometry()
        self.settings.save_window_geometry(geo.x(), geo.y(), geo.width(), geo.height())
        self.settings.set("geometry", self.saveGeometry().data().decode("latin1"))
        self.settings.set("last_destination", self._current_destination_str())
        self.settings.set("language", self._language)
        self.settings.set("theme", self._theme_name)
        event.accept()

    def _current_destination_str(self) -> str:
        if self._current_destination:
            return str(self._current_destination)
        return self._destination_input.text()

    # ==================================================================
    # Setup helpers
    # ==================================================================

    def _restore_from_settings(self) -> None:
        self._language = self.settings.get_language()
        self._theme_name = self.settings.get_theme()
        self._conflict_policy = self.settings.get_conflict_policy()
        self._create_backups = bool(self.settings.get("create_backups", False))
        self._show_hidden = bool(self.settings.get("show_hidden_files", False))
        self._sidebar_visible = bool(self.settings.get("sidebar_visible", True))
        self._sidebar_width = int(self.settings.get("sidebar_width", 280))
        # Restore destination
        dest = self.settings.get("last_destination", "")
        if dest:
            self._current_destination = Path(str(dest))

    def _build_menu_bar(self) -> None:
        pass  # Menus replaced by toolbar intentionally.

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("MainToolbar")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setIconSize(toolbar.iconSize().scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio))
        toolbar.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)
        self._toolbar = toolbar
        self.addToolBar(toolbar)

        # App name
        self._title_label = QLabel(tr("app_name"))
        self._title_label.setObjectName("AppTitle")
        toolbar.addWidget(self._title_label)

        toolbar.addSeparator()

        # New project
        new_action = QAction(make_icon("plus", 20, self._accent_color), tr("action_new"), self)
        new_action.setToolTip(tr("tt_new"))
        new_action.triggered.connect(self.new_project)
        toolbar.addAction(new_action)

        # Open project
        open_action = QAction(make_icon("folder-open", 20, self._accent_color), tr("action_open"), self)
        open_action.setToolTip(tr("tt_open"))
        open_action.triggered.connect(self.open_project_dialog)
        toolbar.addAction(open_action)

        toolbar.addSeparator()

        # Save
        save_action = QAction(make_icon("save", 20, self._accent_color), tr("action_save"), self)
        save_action.setToolTip(tr("tt_save"))
        save_action.triggered.connect(lambda: self._multi_editor.save_current())
        toolbar.addAction(save_action)

        # Save all
        save_all_action = QAction(make_icon("save-all", 20, self._accent_color), tr("action_save_all"), self)
        save_all_action.setToolTip(tr("tt_save_all"))
        save_all_action.triggered.connect(lambda: self._multi_editor.save_all())
        toolbar.addAction(save_all_action)

        toolbar.addSeparator()

        # Language selector
        self._lang_combo = QComboBox()
        self._lang_combo.setObjectName("LangSelector")
        for code, display in available_languages():
            self._lang_combo.addItem(display, code)
        idx = self._lang_combo.findData(self._language)
        if idx >= 0:
            self._lang_combo.setCurrentIndex(idx)
        self._lang_combo.currentIndexChanged.connect(self._on_language_changed)
        toolbar.addWidget(self._lang_combo)

        # Theme selector
        self._theme_combo = QComboBox()
        self._theme_combo.setObjectName("ThemeSelector")
        for name, display, is_dark in available_themes():
            self._theme_combo.addItem(display, name)
        idx = self._theme_combo.findData(self._theme_name)
        if idx >= 0:
            self._theme_combo.setCurrentIndex(idx)
        self._theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        toolbar.addWidget(self._theme_combo)

        # Refresh
        refresh_action = QAction(make_icon("refresh", 20, "#94A3B8"), tr("refresh"), self)
        refresh_action.setToolTip(tr("tt_refresh"))
        refresh_action.triggered.connect(self.refresh_project)
        toolbar.addAction(refresh_action)

        # Settings
        settings_action = QAction(make_icon("settings", 20, "#94A3B8"), tr("action_settings"), self)
        settings_action.setToolTip(tr("action_settings"))
        settings_action.triggered.connect(lambda: self._sidebar.setCurrentRow(3))
        toolbar.addAction(settings_action)

        # About
        about_action = QAction(make_icon("info", 20, "#94A3B8"), tr("action_about"), self)
        about_action.triggered.connect(self._show_about_dialog)
        toolbar.addAction(about_action)

        # Spacer pushes accent picker to the right edge
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        # Accent color picker
        accent_button = QPushButton(self.tr("Accent"))
        accent_button.setObjectName("AccentButton")
        accent_button.setToolTip("Choose accent color")
        accent_button.clicked.connect(self._cycle_accent)
        toolbar.addWidget(accent_button)

    def _cycle_accent(self) -> None:
        colors = ["#3B82F6", "#8B5CF6", "#10B981", "#F59E0B", "#EF4444", "#EC4899"]
        try:
            i = colors.index(self._accent_color)
        except ValueError:
            i = 0
        self._accent_color = colors[(i + 1) % len(colors)]
        self._apply_theme_and_language()
        self.statusBar().showMessage(f"Accent: {self._accent_color}", 3000)

    def _build_status_bar(self) -> None:
        status = QStatusBar()
        self.setStatusBar(status)
        self._status_message = QLabel(tr("status_ready"))
        self._status_message.setObjectName("StatusMessage")
        status.addPermanentWidget(self._status_message, 1)

        self._status_selection = QLabel("")
        self._status_selection.setObjectName("StatusSelection")
        status.addPermanentWidget(self._status_selection)

        self._status_cursor = QLabel(tr("editor_line_col").format(line=1, col=1))
        self._status_cursor.setObjectName("StatusCursor")
        status.addPermanentWidget(self._status_cursor)

    def _build_central(self) -> None:
        central = QWidget()
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        self._splitter = splitter

        # ---------- Sidebar ----------
        self._sidebar = QListWidget()
        self._sidebar.setObjectName("Sidebar")
        self._sidebar.setFixedWidth(self._sidebar_width)
        self._sidebar.setSpacing(4)
        self._sidebar.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        pages = [
            ("dashboard", tr("sidebar_dashboard")),
            ("editor", tr("sidebar_explorer")),
            ("batch", tr("sidebar_batch")),
            ("multi", tr("multi_file_editor")),
            ("settings", tr("sidebar_settings")),
        ]
        self._pages_map: dict[str, int] = {}
        for key, label in pages:
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, key)
            self._sidebar.addItem(item)
            self._pages_map[key] = self._sidebar.row(item)

        self._sidebar.currentRowChanged.connect(self._on_sidebar_changed)
        splitter.addWidget(self._sidebar)

        # ---------- Pages ----------
        self._pages = QStackedWidget()
        self._pages.setObjectName("Pages")
        splitter.addWidget(self._pages)

        # Page 0: Dashboard (tree input + destination + preview)
        self._dashboard_page = self._build_dashboard_page()
        self._pages.addWidget(self._dashboard_page)

        # Page 1: Editor (project explorer + single-file editor)
        self._editor_page = self._build_editor_page()
        self._pages.addWidget(self._editor_page)

        # Page 2: Batch editor
        self._batch_page = self._build_batch_page()
        self._pages.addWidget(self._batch_page)

        # Page 3: Multi-file editor
        self._multi_editor = MultiFileEditor(self)
        self._multi_editor.status_message.connect(lambda kind, msg: self._flash_status(kind, msg))
        self._pages.addWidget(self._multi_editor)

        # Page 4: Settings
        self._settings_page = self._build_settings_page()
        self._pages.addWidget(self._settings_page)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([self._sidebar_width, 1100])

        layout.addWidget(splitter)
        self.setCentralWidget(central)

        # Start on dashboard.
        self._sidebar.setCurrentRow(0)
        self._pages.setCurrentIndex(0)

        # Restore destination text.
        if self._current_destination:
            self._destination_input.setText(str(self._current_destination))

    # ------------------------------------------------------------------
    # Page builders
    # ------------------------------------------------------------------

    def _build_dashboard_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("DashboardPage")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # Split: tree input on the left, preview on the right.
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        # --- left: input ---
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        left_layout.addWidget(self._form_label(tr("tree_input_label")))

        self._tree_input = QPlainTextEdit()
        self._tree_input.setObjectName("TreeInput")
        self._tree_input.setPlaceholderText(tr("tree_placeholder"))
        self._tree_input.setTabStopDistance(32)
        self._tree_input.setMinimumSize(300, 200)
        left_layout.addWidget(self._tree_input, 1)

        button_row = QHBoxLayout()
        self._parse_button = QPushButton(make_icon("layers", 16, "#FFFFFF"), tr("parse_button"))
        self._parse_button.setObjectName("accent")
        self._parse_button.setToolTip(tr("tt_parse"))
        self._parse_button.clicked.connect(self.parse_tree_action)
        button_row.addWidget(self._parse_button)

        self._load_example_button = QPushButton(self.tr("Load Example"))
        self._load_example_button.clicked.connect(self._load_example_tree)
        button_row.addWidget(self._load_example_button)

        self._clear_input_button = QPushButton(make_icon("trash", 16, "#F87171"), self.tr("Clear"))
        self._clear_input_button.clicked.connect(lambda: self._tree_input.clear())
        button_row.addWidget(self._clear_input_button)
        button_row.addStretch(1)
        left_layout.addLayout(button_row)

        splitter.addWidget(left)

        # --- right: destination + preview ---
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        # Destination block
        right_layout.addWidget(self._form_label(tr("destination_label")))
        dest_row = QHBoxLayout()
        self._destination_input = QLineEdit()
        self._destination_input.setObjectName("DestinationInput")
        self._destination_input.setPlaceholderText(tr("destination_placeholder"))
        self._destination_input.textChanged.connect(self._on_destination_changed)
        dest_row.addWidget(self._destination_input, 1)
        self._browse_button = QPushButton(make_icon("folder-open", 16, "#60A5FA"), tr("browse_button"))
        self._browse_button.setToolTip(tr("tt_browse"))
        self._browse_button.clicked.connect(self.browse_destination)
        dest_row.addWidget(self._browse_button)
        right_layout.addLayout(dest_row)

        self._root_info = QLabel("")
        self._root_info.setObjectName("RootInfo")
        self._root_info.setWordWrap(True)
        right_layout.addWidget(self._root_info)

        # Conflict policy
        policy_row = QHBoxLayout()
        policy_row.addWidget(self._form_label(tr("settings_conflict_policy") + ":"))
        self._policy_combo = QComboBox()
        self._policy_combo.setObjectName("PolicyCombo")
        self._policy_combo.addItem(tr("policy_skip"), "skip")
        self._policy_combo.addItem(tr("policy_backup"), "backup")
        self._policy_combo.addItem(tr("policy_error"), "error")
        self._policy_combo.setCurrentIndex(0)
        policy_row.addWidget(self._policy_combo, 1)
        right_layout.addLayout(policy_row)

        # Preview
        right_layout.addWidget(self._form_label(tr("preview_label")))
        self._preview_tree = QTreeWidget()
        self._preview_tree.setObjectName("PreviewTree")
        self._preview_tree.setHeaderHidden(True)
        self._preview_tree.setColumnCount(1)
        self._preview_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._preview_tree.customContextMenuRequested.connect(self._preview_context_menu)
        right_layout.addWidget(self._preview_tree, 1)

        # Validation feedback
        self._validation_label = QLabel("")
        self._validation_label.setObjectName("ValidationLabel")
        self._validation_label.setWordWrap(True)
        right_layout.addWidget(self._validation_label)

        # Create button
        self._create_button = QPushButton(make_icon("folder-plus", 16, "#FFFFFF"), tr("create_button"))
        self._create_button.setObjectName("accent")
        self._create_button.setToolTip(tr("tt_create"))
        self._create_button.setEnabled(False)
        self._create_button.clicked.connect(self.create_structure_action)
        right_layout.addWidget(self._create_button)

        splitter.addWidget(right)
        splitter.setSizes([500, 600])

        layout.addWidget(splitter, 1)
        return page

    def _build_editor_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("EditorPage")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        # Explorer
        explorer_wrap = QWidget()
        explorer_layout = QVBoxLayout(explorer_wrap)
        explorer_layout.setContentsMargins(0, 0, 0, 0)
        explorer_layout.setSpacing(6)
        explorer_layout.addWidget(self._form_label(tr("explorer_label")))

        self._explorer = ProjectExplorer(self)
        self._explorer.file_activated = self.open_file_in_editor
        self._explorer.multi_open = self.open_files_in_multi_editor
        # Keep the batch-page selection counter in sync with live selection.
        self._explorer._tree.selectionModel().selectionChanged.connect(
            lambda *_: self._set_selection_info()
        )
        explorer_layout.addWidget(self._explorer, 1)
        splitter.addWidget(explorer_wrap)

        # Editor area
        editor_wrap = QWidget()
        editor_layout = QVBoxLayout(editor_wrap)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(6)

        # Editor toolbar row
        editor_toolbar = QHBoxLayout()
        editor_toolbar.setSpacing(6)
        self._file_path_label = QLabel(tr("editor_select_file"))
        self._file_path_label.setObjectName("FilePathLabel")
        self._file_path_label.setWordWrap(False)
        editor_toolbar.addWidget(self._file_path_label, 1)

        self._find_action_button = QPushButton(make_icon("search", 16, "#94A3B8"), tr("find_replace"))
        self._find_action_button.setToolTip(tr("tt_find"))
        self._find_action_button.clicked.connect(lambda: self._editor.show_find())
        editor_toolbar.addWidget(self._find_action_button)

        self._editor_save_button = QPushButton(make_icon("save", 16, "#60A5FA"), tr("menu_save"))
        self._editor_save_button.clicked.connect(self.save_current_editor)
        editor_toolbar.addWidget(self._editor_save_button)

        self._editor_save_as_button = QPushButton(make_icon("save-all", 16, "#60A5FA"), tr("menu_save_as"))
        self._editor_save_as_button.clicked.connect(self.save_current_editor_as)
        editor_toolbar.addWidget(self._editor_save_as_button)
        editor_layout.addLayout(editor_toolbar)

        # The editor
        self._editor = TextEditor(self)
        self._editor.set_path(None)
        self._editor.set_font(self.settings.get("editor_font_family", "monospace"),
                              int(self.settings.get("editor_font_size", 12)))
        self._editor.content_changed.connect(lambda: self._on_editor_content_changed())
        self._editor.cursor_moved.connect(self._on_editor_cursor_moved)
        editor_layout.addWidget(self._editor, 1)

        splitter.addWidget(editor_wrap)
        splitter.setSizes([380, 720])

        layout.addWidget(splitter, 1)
        return page

    def _build_batch_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("BatchPage")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        # --- Mode A: same text ---
        mode_a = QWidget()
        ma_layout = QVBoxLayout(mode_a)
        ma_layout.setContentsMargins(0, 0, 0, 0)
        ma_layout.setSpacing(10)

        ma_layout.addWidget(self._form_label(tr("batch_same_text")))

        self._selection_info = QLabel(tr("batch_none_selected"))
        self._selection_info.setObjectName("SelectionInfo")
        self._selection_info.setWordWrap(True)
        ma_layout.addWidget(self._selection_info)

        # Write mode
        mode_row = QHBoxLayout()
        mode_row.addWidget(self._form_label(tr("batch_mode") + ":"))
        self._write_mode_combo = QComboBox()
        self._write_mode_combo.setObjectName("WriteModeCombo")
        self._write_mode_combo.addItem(self.tr("Replace"), "replace")
        self._write_mode_combo.addItem(self.tr("Append"), "append")
        self._write_mode_combo.addItem(self.tr("Prepend"), "prepend")
        mode_row.addWidget(self._write_mode_combo, 1)
        ma_layout.addLayout(mode_row)

        self._batch_content = QPlainTextEdit()
        self._batch_content.setObjectName("BatchContent")
        self._batch_content.setPlaceholderText(tr("batch_content_placeholder"))
        ma_layout.addWidget(self._batch_content, 1)

        self._batch_apply = QPushButton(make_icon("save-all", 16, "#FFFFFF"), tr("batch_apply"))
        self._batch_apply.setObjectName("accent")
        self._batch_apply.clicked.connect(self.apply_batch_to_selected)
        ma_layout.addWidget(self._batch_apply)

        splitter.addWidget(mode_a)

        # --- Mode B: batch content format ---
        mode_b = QWidget()
        mb_layout = QVBoxLayout(mode_b)
        mb_layout.setContentsMargins(0, 0, 0, 0)
        mb_layout.setSpacing(10)

        mb_layout.addWidget(self._form_label(tr("batch_format_label")))

        self._format_input = QPlainTextEdit()
        self._format_input.setObjectName("FormatInput")
        self._format_input.setPlaceholderText(tr("batch_format_placeholder"))
        mb_layout.addWidget(self._format_input, 1)

        self._format_parse_button = QPushButton(make_icon("layers", 16, "#60A5FA"), tr("batch_format_parse"))
        self._format_parse_button.clicked.connect(self.parse_batch_format)
        mb_layout.addWidget(self._format_parse_button)

        self._format_preview = QTreeWidget()
        self._format_preview.setObjectName("FormatPreview")
        self._format_preview.setHeaderHidden(True)
        mb_layout.addWidget(self._format_preview, 1)

        self._format_info = QLabel("")
        self._format_info.setObjectName("FormatInfo")
        self._format_info.setWordWrap(True)
        mb_layout.addWidget(self._format_info)

        self._format_apply = QPushButton(make_icon("save", 16, "#FFFFFF"), tr("batch_format_apply"))
        self._format_apply.setObjectName("accent")
        self._format_apply.setEnabled(False)
        self._format_apply.clicked.connect(self.apply_batch_format)
        mb_layout.addWidget(self._format_apply)

        splitter.addWidget(mode_b)
        splitter.setSizes([520, 620])

        layout.addWidget(splitter, 1)
        return page

    def _build_settings_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("SettingsPage")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        layout.addWidget(self._form_label(tr("settings_title")))

        scroll = QWidget()
        form = QVBoxLayout(scroll)
        form.setSpacing(14)

        # Appearance group
        appearance = QGroupBox(tr("menu_view"))
        ap_layout = QVBoxLayout(appearance)

        lang_row = QHBoxLayout()
        lang_row.addWidget(self._form_label(tr("settings_language") + ":"))
        self._settings_lang_combo = QComboBox()
        for code, display in available_languages():
            self._settings_lang_combo.addItem(display, code)
        idx = self._settings_lang_combo.findData(self._language)
        if idx >= 0:
            self._settings_lang_combo.setCurrentIndex(idx)
        self._settings_lang_combo.currentIndexChanged.connect(self._on_settings_language_changed)
        lang_row.addWidget(self._settings_lang_combo, 1)
        ap_layout.addLayout(lang_row)

        theme_row = QHBoxLayout()
        theme_row.addWidget(self._form_label(tr("settings_theme") + ":"))
        self._settings_theme_combo = QComboBox()
        for name, display, is_dark in available_themes():
            self._settings_theme_combo.addItem(display, name)
        idx = self._settings_theme_combo.findData(self._theme_name)
        if idx >= 0:
            self._settings_theme_combo.setCurrentIndex(idx)
        self._settings_theme_combo.currentIndexChanged.connect(self._on_settings_theme_changed)
        theme_row.addWidget(self._settings_theme_combo, 1)
        ap_layout.addLayout(theme_row)

        sidebar_check = QCheckBox(tr("settings_sidebar"))
        sidebar_check.setChecked(self._sidebar_visible)
        sidebar_check.toggled.connect(self._on_sidebar_visibility_changed)
        ap_layout.addWidget(sidebar_check)

        form.addWidget(appearance)

        # Editor group
        editor_group = QGroupBox(tr("settings_editor"))
        ed_layout = QVBoxLayout(editor_group)

        font_row = QHBoxLayout()
        font_row.addWidget(self._form_label(tr("settings_font_family") + ":"))
        self._font_combo = QComboBox()
        self._font_combo.addItems(["Segoe UI", "Cairo", "Fira Code", "Consolas", "Courier New", "monospace"])
        current_font = str(self.settings.get("editor_font_family", "monospace"))
        self._font_combo.setCurrentText(current_font)
        self._font_combo.currentTextChanged.connect(self._on_font_changed)
        font_row.addWidget(self._font_combo, 1)
        ed_layout.addLayout(font_row)

        size_row = QHBoxLayout()
        size_row.addWidget(self._form_label(tr("settings_font_size") + ":"))
        self._font_size_spin = QSpinBox()
        self._font_size_spin.setRange(8, 72)
        self._font_size_spin.setValue(int(self.settings.get("editor_font_size", 12)))
        self._font_size_spin.valueChanged.connect(self._on_font_size_changed)
        size_row.addWidget(self._font_size_spin, 1)
        ed_layout.addLayout(size_row)

        auto_indent_check = QCheckBox(tr("settings_auto_indent"))
        auto_indent_check.setChecked(bool(self.settings.get("auto_indent", True)))
        auto_indent_check.toggled.connect(lambda v: self.settings.set("auto_indent", bool(v)))
        ed_layout.addWidget(auto_indent_check)

        form.addWidget(editor_group)

        # Filesystem group
        fs_group = QGroupBox(tr("settings_filesystem"))
        fs_layout = QVBoxLayout(fs_group)

        hidden_check = QCheckBox(tr("settings_hidden_files"))
        hidden_check.setChecked(self._show_hidden)
        hidden_check.toggled.connect(self._on_show_hidden_changed)
        fs_layout.addWidget(hidden_check)

        policy_row = QHBoxLayout()
        policy_row.addWidget(self._form_label(tr("settings_conflict_policy") + ":"))
        self._settings_policy_combo = QComboBox()
        self._settings_policy_combo.addItem(tr("policy_skip"), "skip")
        self._settings_policy_combo.addItem(tr("policy_backup"), "backup")
        self._settings_policy_combo.addItem(tr("policy_error"), "error")
        idx = self._settings_policy_combo.findData(self._conflict_policy)
        if idx >= 0:
            self._settings_policy_combo.setCurrentIndex(idx)
        self._settings_policy_combo.currentIndexChanged.connect(self._on_conflict_policy_changed)
        policy_row.addWidget(self._settings_policy_combo, 1)
        fs_layout.addLayout(policy_row)

        backup_check = QCheckBox(tr("settings_create_backups"))
        backup_check.setChecked(self._create_backups)
        backup_check.toggled.connect(self._on_create_backups_changed)
        fs_layout.addWidget(backup_check)

        form.addWidget(fs_group)

        # Recent projects group
        recent_group = QGroupBox(tr("settings_recent_projects"))
        rec_layout = QVBoxLayout(recent_group)
        self._recent_list = QListWidget()
        self._recent_list.setObjectName("RecentList")
        rec_layout.addWidget(self._recent_list)
        refresh_recent = QPushButton(self.tr("Refresh"))
        refresh_recent.clicked.connect(self._refresh_recent_list)
        rec_layout.addWidget(refresh_recent)
        clear_recent = QPushButton(make_icon("trash", 16, "#F87171"), tr("settings_clear_recent"))
        clear_recent.setObjectName("danger")
        clear_recent.clicked.connect(self._clear_recent_projects)
        rec_layout.addWidget(clear_recent)
        form.addWidget(recent_group)

        # Danger zone
        restore_defaults = QPushButton(make_icon("undo", 16, "#F87171"), tr("settings_restore_defaults"))
        restore_defaults.setObjectName("danger")
        restore_defaults.clicked.connect(self._restore_default_settings)
        form.addWidget(restore_defaults)

        form.addStretch(1)

        from PyQt6.QtWidgets import QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setObjectName("SettingsScroll")
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        layout.addWidget(scroll_area, 1)

        self._refresh_recent_list()
        return page

    # ==================================================================
    # Shortcuts
    # ==================================================================

    def _build_shortcuts(self) -> None:
        from PyQt6.QtGui import QKeySequence, QShortcut

        QShortcut(QKeySequence(tr("shortcut_find")), self, self._editor.show_find)
        QShortcut(QKeySequence(tr("shortcut_save")), self, self.save_current_editor)
        QShortcut(QKeySequence(tr("shortcut_save_all")), self, self._multi_editor.save_all)
        QShortcut(QKeySequence(tr("shortcut_close")), self, self.close)

    # ==================================================================
    # Theme / Language
    # ==================================================================

    def _apply_theme_and_language(self) -> None:
        # Theme with accent override
        theme = get_theme(self._theme_name)
        theme.accent = self._accent_color
        apply_theme(QApplication.instance(), self._theme_name)

        # Language
        set_language(self._language)
        layout_dir = (
            Qt.LayoutDirection.RightToLeft if is_rtl()
            else Qt.LayoutDirection.LeftToRight
        )
        self.setLayoutDirection(layout_dir)
        QApplication.instance().setLayoutDirection(layout_dir)

        # Retranslate key labels.
        self._retranslate()

        # Update the toolbar selectors without triggering recursion.
        self._update_selector_indices()

    def _retranslate(self) -> None:
        self.setWindowTitle(f"{tr('app_name')} — {tr('app_version').format(version=__version__)}")
        if hasattr(self, "_title_label"):
            self._title_label.setText(tr("app_name"))
        if hasattr(self, "_tree_input"):
            self._tree_input.setPlaceholderText(tr("tree_placeholder"))
        if hasattr(self, "_destination_input"):
            self._destination_input.setPlaceholderText(tr("destination_placeholder"))
        if hasattr(self, "_parse_button"):
            self._parse_button.setText(tr("parse_button"))
        if hasattr(self, "_create_button"):
            self._create_button.setText(tr("create_button"))
        if hasattr(self, "_browse_button"):
            self._browse_button.setText(tr("browse_button"))
        if hasattr(self, "_explorer"):
            self._explorer._search.setPlaceholderText(tr("search_placeholder"))
        if hasattr(self, "_file_path_label"):
            label = self._file_path_label.text()
            if label == tr("editor_select_file") or not label:
                self._file_path_label.setText(tr("editor_select_file"))

        # Sidebar items
        if hasattr(self, "_sidebar"):
            labels = {
                "dashboard": tr("sidebar_dashboard"),
                "editor": tr("sidebar_explorer"),
                "batch": tr("sidebar_batch"),
                "multi": tr("multi_file_editor"),
                "settings": tr("sidebar_settings"),
            }
            for i in range(self._sidebar.count()):
                item = self._sidebar.item(i)
                key = str(item.data(Qt.ItemDataRole.UserRole))
                item.setText(labels.get(key, key))

        if hasattr(self, "_status_message") and self._status_message.text() == tr("status_ready"):
            self._status_message.setText(tr("status_ready"))

    def _update_selector_indices(self) -> None:
        for combo in (self._lang_combo, self._settings_lang_combo):
            idx = combo.findData(self._language)
            if idx >= 0:
                combo.blockSignals(True)
                combo.setCurrentIndex(idx)
                combo.blockSignals(False)
        for combo in (self._theme_combo, self._settings_theme_combo):
            idx = combo.findData(self._theme_name)
            if idx >= 0:
                combo.blockSignals(True)
                combo.setCurrentIndex(idx)
                combo.blockSignals(False)

    # ==================================================================
    # Slots: toolbar / sidebar
    # ==================================================================

    def _on_sidebar_changed(self, row: int) -> None:
        if row < 0:
            return
        self._pages.setCurrentIndex(row)

    def _on_language_changed(self, index: int) -> None:
        code = str(self._lang_combo.itemData(index))
        self._change_language(code)

    def _on_settings_language_changed(self, index: int) -> None:
        code = str(self._settings_lang_combo.itemData(index))
        self._change_language(code)

    def _change_language(self, code: str) -> None:
        if code == self._language:
            return
        self._language = code
        self.settings.set("language", code)
        self._apply_theme_and_language()

    def _on_theme_changed(self, index: int) -> None:
        name = str(self._theme_combo.itemData(index))
        self._change_theme(name)

    def _on_settings_theme_changed(self, index: int) -> None:
        name = str(self._settings_theme_combo.itemData(index))
        self._change_theme(name)

    def _change_theme(self, name: str) -> None:
        if name == self._theme_name:
            return
        self._theme_name = name
        self.settings.set("theme", name)
        self._apply_theme_and_language()

    def _on_sidebar_visibility_changed(self, checked: bool) -> None:
        self._sidebar_visible = checked
        self.settings.set("sidebar_visible", checked)
        self._sidebar.setVisible(checked)

    def _on_font_changed(self, family: str) -> None:
        self.settings.set("editor_font_family", family)
        self._editor.set_font(family, int(self.settings.get("editor_font_size", 12)))
        self._multi_editor.set_editor_font(family, int(self.settings.get("editor_font_size", 12)))

    def _on_font_size_changed(self, size: int) -> None:
        self.settings.set("editor_font_size", size)
        self._editor.set_font(str(self.settings.get("editor_font_family", "monospace")), size)
        self._multi_editor.set_editor_font(str(self.settings.get("editor_font_family", "monospace")), size)

    def _on_show_hidden_changed(self, checked: bool) -> None:
        self._show_hidden = checked
        self.settings.set("show_hidden_files", checked)

    def _on_conflict_policy_changed(self, index: int) -> None:
        policy = str(self._settings_policy_combo.itemData(index))
        self._conflict_policy = policy
        self.settings.set("conflict_policy", policy)
        # Sync the dashboard selector.
        idx = self._policy_combo.findData(policy)
        if idx >= 0:
            self._policy_combo.blockSignals(True)
            self._policy_combo.setCurrentIndex(idx)
            self._policy_combo.blockSignals(False)

    def _on_create_backups_changed(self, checked: bool) -> None:
        self._create_backups = checked
        self.settings.set("create_backups", checked)
        self._file_service.create_backups = checked

    def _refresh_recent_list(self) -> None:
        self._recent_list.clear()
        for path in self.settings.get_recent_projects():
            self._recent_list.addItem(str(path))

    def _clear_recent_projects(self) -> None:
        self.settings.clear_recent_projects()
        self._refresh_recent_list()
        self._flash_status("info", self.tr("Settings saved."))

    def _restore_default_settings(self) -> None:
        result = QMessageBox.question(
            self,
            tr("dialog_title_settings"),
            self.tr("Restore default settings?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if result != QMessageBox.StandardButton.Yes:
            return
        self.settings.clear_all_settings()
        self._language = "en"
        self._theme_name = "dark"
        self._conflict_policy = "skip"
        self._create_backups = False
        self._sidebar_visible = True
        self._current_destination = None
        self._destination_input.clear()
        self._apply_theme_and_language()
        self._refresh_recent_list()
        self._flash_status("info", self.tr("Settings saved."))

    # ==================================================================
    # Parsing
    # ==================================================================

    def _load_example_tree(self) -> None:
        example = (
            "SumMaster/\n"
            "├── main.py\n"
            "├── make_zip.py\n"
            "├── requirements.txt\n"
            "├── README.md\n"
            "├── assets/icons/\n"
            "├── ui/ (main_window.py, spinner.py, styles.py)\n"
            "├── core/ (calculator.py, worker.py)\n"
            "├── services/ (settings_service.py)\n"
            "└── tests/ (test_calculator.py, test_worker.py)\n"
        )
        self._tree_input.setPlainText(example)

    def parse_tree_action(self) -> None:
        text = self._tree_input.toPlainText()
        result = parse_tree(text)
        self._parse_result = result

        if result.root is None:
            self._show_validation_errors(result)
            self._create_button.setEnabled(False)
            self._preview_tree.clear()
            return

        self._show_preview(result.root)
        self._show_validation_errors(result)

        has_blocking_errors = result.has_errors
        self._create_button.setEnabled(not has_blocking_errors)

        # Update the explorer with the parsed tree.
        self._explorer.load_from_tree(result.root)
        self._set_selection_info()

        # Count summary.
        dirs = result.root.total_directories()
        files = result.root.total_files()
        self._validation_label.setText(
            tr("dirs_created").format(n=dirs) + "  •  " + tr("files_created").format(n=files)
        ) if not has_blocking_errors else self._validation_label.setText(
            self._validation_label.text() + f"\n{tr('dirs_created').format(n=dirs)} • {tr('files_created').format(n=files)}"
        )

    def _show_preview(self, root: TreeNode) -> None:
        self._preview_tree.clear()
        root_item = QTreeWidgetItem([root.name])
        root_item.setData(0, Qt.ItemDataRole.UserRole, root)
        root_item.setIcon(0, make_icon("app", 20, self._accent_color))
        self._preview_tree.addTopLevelItem(root_item)
        self._populate_preview(root_item, root)
        self._preview_tree.expandAll()

    def _populate_preview(self, parent_item: QTreeWidgetItem, node: TreeNode) -> None:
        for child in node.children.values():
            item = QTreeWidgetItem([child.name])
            item.setData(0, Qt.ItemDataRole.UserRole, child)
            self._apply_node_icon(item, child)
            parent_item.addChild(item)
            self._populate_preview(item, child)
        for fnode in node.files.values():
            item = QTreeWidgetItem([fnode.name])
            item.setData(0, Qt.ItemDataRole.UserRole, fnode)
            self._apply_node_icon(item, fnode)
            parent_item.addChild(item)

    def _apply_node_icon(self, item: QTreeWidgetItem, node: TreeNode) -> None:
        if node.kind == NodeKind.AMBIGUOUS:
            item.setIcon(0, make_icon("file-warning", 18, "#FBBF24"))
            item.setText(0, f"{node.name} [?]")
        elif node.kind == NodeKind.DIRECTORY:
            item.setIcon(0, make_icon("folder", 18, "#FBBF24"))
        else:
            item.setIcon(0, make_icon("file-text", 18, "#60A5FA"))

    def _show_validation_errors(self, result: ParseResult) -> None:
        if result.has_errors or result.has_warnings:
            lines = []
            if result.has_errors:
                lines.append(tr("parse_error") if not result.root else tr("validation_error"))
                for err in result.errors:
                    if not err.is_warning:
                        lines.append(f"• [{err.line_number}] {err.message}")
            if result.has_warnings:
                if lines:
                    lines.append("")
                lines.append(tr("parse_warning"))
                for err in result.errors:
                    if err.is_warning:
                        lines.append(f"• [{err.line_number}] {err.message}")
            self._validation_label.setText("\n".join(lines))
        else:
            self._validation_label.setText("")

    def _preview_context_menu(self, pos) -> None:
        item = self._preview_tree.itemAt(pos)
        if item is None:
            return
        node = item.data(0, Qt.ItemDataRole.UserRole)
        if node is None:
            return
        from PyQt6.QtWidgets import QMenu
        ctx = QMenu(self)
        as_file = ctx.addAction(make_icon("file", 16, "#60A5FA"), tr("set_as_file"))
        as_dir = ctx.addAction(make_icon("folder", 16, "#FBBF24"), tr("set_as_directory"))
        action = ctx.exec(self._preview_tree.mapToGlobal(pos))
        if action == as_file:
            node.resolve_to(NodeKind.FILE)
        elif action == as_dir:
            node.resolve_to(NodeKind.DIRECTORY)
        self._show_preview(self._parse_result.root)

    # ==================================================================
    # Destination
    # ==================================================================

    def browse_destination(self) -> None:
        start = self._current_destination or Path.home()
        path = QFileDialog.getExistingDirectory(
            self, tr("browse_button"), str(start)
        )
        if path:
            self._destination_input.setText(path)
            self._on_destination_changed()

    def _on_destination_changed(self) -> None:
        text = self._destination_input.text().strip()
        if not text:
            self._current_destination = None
            self._root_info.setText("")
            self._update_create_enabled()
            return
        candidate = Path(text)
        self._current_destination = candidate
        if self._parse_result and self._parse_result.root:
            self._root_info.setText(
                tr("root_created").format(root=str(candidate / self._parse_result.root.name))
            )
        else:
            self._root_info.setText("")
        self._update_create_enabled()

    def _update_create_enabled(self) -> None:
        enabled = (
            self._current_destination is not None
            and self._parse_result is not None
            and self._parse_result.is_valid
        )
        self._create_button.setEnabled(enabled)

    # ==================================================================
    # Structure creation
    # ==================================================================

    def create_structure_action(self) -> None:
        if not self._parse_result or not self._parse_result.root:
            QMessageBox.information(self, tr("app_name"), tr("no_tree_defined"))
            return
        if self._current_destination is None:
            QMessageBox.information(self, tr("app_name"), tr("destination_empty"))
            return

        root = self._parse_result.root
        dirs = root.total_directories()
        files = root.total_files()

        # Confirmation.
        summary = (
            f"{tr('dirs_created').format(n=dirs)}\n"
            f"{tr('files_created').format(n=files)}\n\n"
            f"{tr('root_created').format(root=str(self._current_destination / root.name))}"
        )
        reply = QMessageBox.question(
            self,
            tr("dialog_title_batch_confirm"),
            self.tr("Create structure?") + "\n\n" + summary,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        # Build service.
        service = ProjectService(self._current_destination)
        policy = str(self._policy_combo.currentData())
        service.conflict_policy = ConflictPolicy(policy)
        self._project_service = service

        # Run async.
        dialog = ProgressDialog(self, tr("create_button"))
        dialog.run_async(
            service.create_structure,
            self._parse_result,
            on_finished=lambda report: self._after_creation(report),
        )

    def _after_creation(self, report: CreationReport) -> None:
        lines = [
            tr("creation_summary"),
            tr("dirs_created").format(n=report.directories_created),
            tr("files_created").format(n=report.files_created),
            tr("items_skipped").format(n=report.directories_skipped + report.files_skipped),
            tr("items_failed").format(n=report.total_failures),
        ]
        for failure in report.failures:
            lines.append(f"  ✗ {failure.path}: {failure.message}")

        QMessageBox.information(
            self,
            tr("creation_summary"),
            "\n".join(lines),
        )

        # Refresh the explorer from the filesystem.
        self.refresh_project()
        if self._project_service is not None:
            self.settings.add_recent_project(str(self._project_service.base_dir))

        # Switch to the editor page.
        self._sidebar.setCurrentRow(1)

    def refresh_project(self) -> None:
        """Rebuild the explorer from the filesystem under the project root."""
        base = self._project_service.base_dir if self._project_service else self._current_destination
        if base is None or not Path(base).exists():
            return
        root_dir = Path(base)
        # If the tree has a root name, descend into it.
        if self._parse_result and self._parse_result.root:
            root_name = self._parse_result.root.name
            candidate = root_dir / root_name
            if candidate.exists():
                root_dir = candidate
        from app.widgets.project_explorer import ExplorerNode

        def build(path: Path) -> ExplorerNode:
            node = ExplorerNode(
                name=path.name,
                rel_path=str(path.relative_to(root_dir.parent)) if path != root_dir.parent else path.name,
                is_file=path.is_file(),
            )
            if path.is_dir():
                try:
                    children = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
                except OSError:
                    children = []
                for child in children:
                    if not self._show_hidden and child.name.startswith("."):
                        continue
                    node.children.append(build(child))
            return node

        top = build(root_dir)
        nodes = [ExplorerNode(name=top.name, rel_path=top.name, is_file=False, children=top.children)]
        self._explorer.load_nodes(nodes)
        self._set_selection_info()

    # ==================================================================
    # Editor integration
    # ==================================================================

    def _project_root(self) -> Optional[Path]:
        """Return the filesystem root of the current project.

        This is the directory that contains the parsed tree's root node
        (e.g. ``<destination>/SumMaster``).  Falls back to the empty
        destination when no tree has been parsed.
        """
        base = self._project_service.base_dir if self._project_service else self._current_destination
        if base is None:
            return None
        base = Path(base)
        if self._parse_result and self._parse_result.root:
            candidate = base / self._parse_result.root.name
            if candidate.exists():
                return candidate
        return base

    def open_file_in_editor(self, rel_path: str) -> None:
        root = self._project_root()
        if root is None:
            return
        path = Path(root) / rel_path
        if not path.exists():
            self._flash_status("warning", f"{self.tr('editor_unsaved_changes')}. File missing: {rel_path}")
        try:
            content = self._file_service.read_file(path)
        except ValueError:
            # Binary file
            result = QMessageBox.warning(
                self,
                tr("editor_binary_file"),
                tr("editor_binary_msg") + f"\n\n{path.name}",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            )
            if result != QMessageBox.StandardButton.Ok:
                return
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                return
        except OSError as exc:
            self._flash_status("error", str(exc))
            return

        self._editor.set_path(path)
        self._editor.set_content(content)
        self._editor.set_read_only(self._file_service.is_read_only(path))
        self._file_path_label.setText(rel_path)
        self._flash_status("info", tr("editor_saved").format(path=str(path)))

    def _on_editor_content_changed(self) -> None:
        label = self._file_path_label.text()
        base = label.rsplit(" [modified]", 1)[0]
        if self._editor.is_modified():
            if not base.endswith("*"):
                self._file_path_label.setText(f"{base} *")
        else:
            self._file_path_label.setText(base)

    def _on_editor_cursor_moved(self, line: int, col: int) -> None:
        self._status_cursor.setText(tr("editor_line_col").format(line=line, col=col))

    def save_current_editor(self) -> None:
        path = self._editor.get_path()
        if path is None:
            self.save_current_editor_as()
            return
        result = self._file_service.write_file(path, self._editor.get_content())
        if result.success:
            self._editor.mark_clean()
            self._on_editor_content_changed()
            self._flash_status("info", tr("editor_saved").format(path=str(path)))
        else:
            QMessageBox.critical(self, tr("dialog_title_save_changes"),
                                 tr("editor_save_failed").format(error=result.message))

    def save_current_editor_as(self) -> None:
        default_name = ""
        if self._editor.get_path():
            default_name = self._editor.get_path().name
        path, _ = QFileDialog.getSaveFileName(self, tr("editor_save_as_title"), default_name)
        if not path:
            return
        self._editor.set_path(Path(path))
        self.save_current_editor()
        self.refresh_project()

    def _editor_current_rel_path(self) -> Optional[str]:
        path = self._editor.get_path()
        if path is None or self._project_service is None:
            return None
        try:
            return str(path.relative_to(self._project_service.base_dir))
        except ValueError:
            return None

    # ==================================================================
    # Multi-file editor
    # ==================================================================

    def open_files_in_multi_editor(self, rel_paths: list[str]) -> None:
        root = self._project_root()
        if root is None:
            return
        opened = 0
        for rel_path in rel_paths:
            path = Path(root) / rel_path
            content = None
            try:
                content = self._file_service.read_file(path)
            except ValueError:
                content = ""  # skip binary silently in multi editor
            except OSError:
                content = ""
            self._multi_editor.open_file(path, content)
            opened += 1
        if opened:
            self._sidebar.setCurrentRow(3)
            self._flash_status("info", f"{opened} file(s) opened.")

    # ==================================================================
    # Batch operations
    # ==================================================================

    def _set_selection_info(self) -> None:
        count = len(self._explorer.selected_file_paths())
        if count == 0:
            self._selection_info.setText(tr("batch_none_selected"))
        else:
            self._selection_info.setText(
                self.tr("{n} selected").format(n=count)
            )

    def apply_batch_to_selected(self) -> None:
        files = self._explorer.selected_file_paths()
        if not files:
            # Also consider files under selected folders.
            files = self._explorer.all_files_under_selection()
        if not files:
            QMessageBox.information(self, tr("app_name"), tr("batch_select_files"))
            return

        content = self._batch_content.toPlainText()
        mode_raw = str(self._write_mode_combo.currentData())
        mode = WriteMode(mode_raw)

        root = self._project_root()
        if root is None:
            return

        paths = [Path(root) / f for f in files]

        # Warn about binary files.
        binary = [p.name for p in paths if self._file_service.is_binary(p)]
        if binary:
            res = QMessageBox.warning(
                self,
                tr("editor_binary_file"),
                self.tr("Some selected files appear to be binary:") + "\n" + ", ".join(binary[:8]) + "\n\n" + self.tr("Continue?"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if res != QMessageBox.StandardButton.Yes:
                return

        # Confirmation for replace on existing content.
        if mode == WriteMode.REPLACE:
            existing = [p for p in paths if p.exists() and p.is_file()]
            if existing:
                confirm = self._confirm_batch_write(tr("batch_preview_overwrite").format(count=len(paths)), paths)
                if not confirm:
                    return

        dialog = ProgressDialog(self, tr("dialog_title_batch_confirm"))
        dialog.run_async(
            self._file_service.write_to_multiple,
            paths,
            content,
            mode,
            on_finished=lambda results: self._after_batch_write(results),
        )

    def _confirm_batch_write(self, message: str, paths: list[Path]) -> bool:
        detail = "\n".join(str(p) for p in paths[:25])
        more = f"\n… +{len(paths) - 25} more" if len(paths) > 25 else ""
        return QMessageBox.question(
            self,
            tr("dialog_title_batch_confirm"),
            message + "\n\n" + detail + more,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        ) == QMessageBox.StandardButton.Yes

    def _after_batch_write(self, results: list[FileWriteResult]) -> None:
        successes = [r for r in results if r.success]
        failures = [r for r in results if not r.success]
        lines = [
            tr("batch_success").format(n=len(successes)),
        ]
        if failures:
            lines.append(tr("batch_failed").format(n=len(failures)))
            for fail in failures[:20]:
                lines.append(f"  ✗ {fail.path.name}: {fail.message}")
        QMessageBox.information(self, tr("batch_results"), "\n".join(lines))
        self.refresh_project()

    # ------------------------------------------------------------------
    # Mode B: batch content format
    # ------------------------------------------------------------------

    def parse_batch_format(self) -> None:
        text = self._format_input.toPlainText()
        base = self._project_root()
        if base is None:
            QMessageBox.information(self, tr("app_name"), tr("destination_empty"))
            return
        try:
            parsed = parse_batch_content(text, Path(base))
        except ValueError as exc:
            self._format_info.setText(str(exc))
            self._format_preview.clear()
            self._format_apply.setEnabled(False)
            return
        self._format_preview.clear()
        for path, content in parsed.items():
            item = QTreeWidgetItem([str(path.relative_to(Path(base)))])
            item.setToolTip(0, content[:400])
            self._format_preview.addTopLevelItem(item)
        self._format_info.setText(tr("batch_format_count").format(count=len(parsed)))
        self._format_apply.setEnabled(True)
        self._pending_batch_format = (base, parsed)

    def apply_batch_format(self) -> None:
        if not hasattr(self, "_pending_batch_format"):
            return
        base, parsed = self._pending_batch_format
        # Confirm.
        reply = QMessageBox.question(
            self,
            tr("dialog_title_batch_confirm"),
            self.tr("Write content to {count} file(s)?").format(count=len(parsed)),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        dialog = ProgressDialog(self, tr("batch_format_apply"))
        dialog.run_async(
            self._file_service.save_multiple,
            parsed,
            self._create_backups,
            on_finished=lambda results: self._after_batch_write(results),
        )

    # ==================================================================
    # Projects
    # ==================================================================

    def new_project(self) -> None:
        self._tree_input.clear()
        self._parse_result = None
        self._preview_tree.clear()
        self._create_button.setEnabled(False)
        self._explorer.clear()
        self._sidebar.setCurrentRow(0)
        self._flash_status("info", self.tr("New project"))

    def open_project_dialog(self) -> None:
        path = QFileDialog.getExistingDirectory(self, tr("action_open"), str(Path.home()))
        if not path:
            return
        base = Path(path)
        self._current_destination = base.parent
        self._destination_input.setText(str(base.parent))
        self._project_service = ProjectService(base)
        self.settings.add_recent_project(str(base))
        self.refresh_project()
        self._sidebar.setCurrentRow(1)
        self._flash_status("info", f"Opened: {base}")

    # ==================================================================
    # Utilities
    # ==================================================================

    def _flash_status(self, kind: str, message: str) -> None:
        self._status_message.setText(message)

    def _show_about_dialog(self) -> None:
        QMessageBox.about(
            self,
            tr("dialog_title_about"),
            f"<h2>TreeForge Studio</h2><p>{tr('app_version').format(version=__version__)}</p>"
            "<p>Transform plain-text directory trees into real project structures.</p>"
            "<p>Built with Python and PyQt6.</p>",
        )

    def _form_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("FormLabel")
        return label
