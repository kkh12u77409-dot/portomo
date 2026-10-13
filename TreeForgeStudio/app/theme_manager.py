"""Theme manager for TreeForge Studio.

Provides light and dark themes via Qt Style Sheets (QSS).
Themes are applied at runtime and persisted via :class:`SettingsService`.
"""

from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtGui import QColor, QPalette, QFont
from PyQt6.QtWidgets import QApplication


@dataclass
class Theme:
    """A colour palette definition for the application."""

    name: str
    display_name: str
    is_dark: bool

    # Palette colours
    bg_primary: str
    bg_secondary: str
    bg_tertiary: str
    surface: str
    surface_alt: str
    border: str
    border_strong: str

    text_primary: str
    text_secondary: str
    text_disabled: str

    accent: str
    accent_hover: str
    accent_pressed: str

    success: str
    warning: str
    error: str
    info: str

    scrollbar_bg: str
    scrollbar_thumb: str
    scrollbar_thumb_hover: str

    editor_bg: str
    editor_fg: str
    editor_selection: str
    editor_line_number_bg: str
    editor_line_number_fg: str
    editor_cursor: str


LIGHT_THEME = Theme(
    name="light",
    display_name="Light",
    is_dark=False,
    bg_primary="#F5F6F8",
    bg_secondary="#FFFFFF",
    bg_tertiary="#FAFAFA",
    surface="#FFFFFF",
    surface_alt="#F0F1F3",
    border="#D1D5DB",
    border_strong="#B8BAC0",
    text_primary="#1F2937",
    text_secondary="#6B7280",
    text_disabled="#9CA3AF",
    accent="#2563EB",
    accent_hover="#3B82F6",
    accent_pressed="#1D4ED8",
    success="#10B981",
    warning="#F59E0B",
    error="#EF4444",
    info="#3B82F6",
    scrollbar_bg="#E5E7EB",
    scrollbar_thumb="#CBD5E1",
    scrollbar_thumb_hover="#94A3B8",
    editor_bg="#FFFFFF",
    editor_fg="#1F2937",
    editor_selection="#93C5FD",
    editor_line_number_bg="#F3F4F6",
    editor_line_number_fg="#9CA3AF",
    editor_cursor="#2563EB",
)

DARK_THEME = Theme(
    name="dark",
    display_name="Dark",
    is_dark=True,
    bg_primary="#0F172A",
    bg_secondary="#1E293B",
    bg_tertiary="#334155",
    surface="#1E293B",
    surface_alt="#283548",
    border="#475569",
    border_strong="#64748B",
    text_primary="#F1F5F9",
    text_secondary="#94A3B8",
    text_disabled="#64748B",
    accent="#3B82F6",
    accent_hover="#60A5FA",
    accent_pressed="#2563EB",
    success="#34D399",
    warning="#FBBF24",
    error="#F87171",
    info="#60A5FA",
    scrollbar_bg="#334155",
    scrollbar_thumb="#475569",
    scrollbar_thumb_hover="#64748B",
    editor_bg="#0D1117",
    editor_fg="#E6EDF3",
    editor_selection="#26465D",
    editor_line_number_bg="#161B22",
    editor_line_number_fg="#6E7681",
    editor_cursor="#58A6FF",
)

SYSTEM_THEME = Theme(
    name="system",
    display_name="System",
    is_dark=True,
    bg_primary="#0F172A",
    bg_secondary="#1E293B",
    bg_tertiary="#334155",
    surface="#1E293B",
    surface_alt="#283548",
    border="#475569",
    border_strong="#64748B",
    text_primary="#F1F5F9",
    text_secondary="#94A3B8",
    text_disabled="#64748B",
    accent="#3B82F6",
    accent_hover="#60A5FA",
    accent_pressed="#2563EB",
    success="#34D399",
    warning="#FBBF24",
    error="#F87171",
    info="#60A5FA",
    scrollbar_bg="#334155",
    scrollbar_thumb="#475569",
    scrollbar_thumb_hover="#64748B",
    editor_bg="#0D1117",
    editor_fg="#E6EDF3",
    editor_selection="#26465D",
    editor_line_number_bg="#161B22",
    editor_line_number_fg="#6E7681",
    editor_cursor="#58A6FF",
)


_THEMES: dict[str, Theme] = {
    "light": LIGHT_THEME,
    "dark": DARK_THEME,
    "system": SYSTEM_THEME,
}


def get_theme(name: str = "dark") -> Theme:
    """Return the theme by name, falling back to dark."""
    return _THEMES.get(name, DARK_THEME)


def available_themes() -> list[tuple[str, str, bool]]:
    """Return list of ``(name, display_name, is_dark)``."""
    return [(t.name, t.display_name, t.is_dark) for t in _THEMES.values()]


def _generate_qss(theme: Theme) -> str:
    """Generate the Qt Style Sheet string for a theme."""
    t = theme
    radius = "8px"
    btn_pad = "8px 14px"
    return f"""
/* ===== Base / MainWindow ===== */
QMainWindow {{
    background-color: {t.bg_primary};
    color: {t.text_primary};
    font-family: "Segoe UI", "Cairo", "Fira Code", "Segoe UI Emoji", sans-serif;
    font-size: 14px;
}}

QWidget {{
    background-color: {t.bg_primary};
    color: {t.text_primary};
    font-family: "Segoe UI", "Cairo", "Fira Code", "Segoe UI Emoji", sans-serif;
}}

/* ===== Tooltips ===== */
QToolTip {{
    background-color: {t.surface};
    color: {t.text_primary};
    border: 1px solid {t.border};
    border-radius: {radius};
    padding: 6px 10px;
    font-size: 13px;
}}

/* ===== ScrollArea / ScrollBars ===== */
QScrollArea {{
    border: none;
    background-color: {t.bg_primary};
}}

QScrollBar:vertical {{
    background-color: {t.scrollbar_bg};
    width: 14px;
    margin: 0px;
    border-radius: 7px;
}}

QScrollBar::handle:vertical {{
    background-color: {t.scrollbar_thumb};
    border-radius: 7px;
    margin: 2px 3px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {t.scrollbar_thumb_hover};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{
    background: transparent;
}}

QScrollBar:horizontal {{
    background-color: {t.scrollbar_bg};
    height: 14px;
    margin: 0px;
    border-radius: 7px;
}}

QScrollBar::handle:horizontal {{
    background-color: {t.scrollbar_thumb};
    border-radius: 7px;
    margin: 2px 3px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {t.scrollbar_thumb_hover};
}}

/* ===== Buttons ===== */
QPushButton {{
    background-color: {t.surface};
    color: {t.text_primary};
    border: 1px solid {t.border};
    border-radius: {radius};
    padding: {btn_pad};
    font-family: "Segoe UI", "Cairo", "Fira Code", "Segoe UI Emoji", sans-serif;
    font-size: 14px;
}}

QPushButton:hover {{
    background-color: {t.surface_alt};
    border-color: {t.accent_hover};
}}

QPushButton:pressed {{
    background-color: {t.bg_tertiary};
    border-color: {t.accent_pressed};
}}

QPushButton:disabled {{
    color: {t.text_disabled};
    background-color: {t.surface_alt};
    border-color: {t.border};
}}

QPushButton:focus {{
    border: 2px solid {t.accent};
    padding: 6px 12px;
}}

QPushButton.flat {{
    background-color: transparent;
    border: none;
    padding: 4px 8px;
}}

QPushButton.flat:hover {{
    background-color: {t.bg_tertiary};
}}

/* Accent button */
QPushButton.accent {{
    background-color: {t.accent};
    color: #FFFFFF;
    border-color: {t.accent};
}}

QPushButton.accent:hover {{
    background-color: {t.accent_hover};
    border-color: {t.accent_hover};
}}

QPushButton.accent:pressed {{
    background-color: {t.accent_pressed};
}}

QPushButton.accent:disabled {{
    background-color: {t.text_disabled};
}}

/* Danger button */
QPushButton.danger {{
    background-color: {t.error};
    color: #FFFFFF;
    border-color: {t.error};
}}

QPushButton.danger:hover {{
    background-color: {t.error};
    opacity: 0.9;
}}

/* ===== Toolbar ===== */
QToolBar {{
    background-color: {t.surface};
    border: none;
    border-bottom: 1px solid {t.border};
    padding: 4px 8px;
    spacing: 4px;
    font-family: "Segoe UI", "Cairo", sans-serif;
}}

QToolBar::separator {{
    width: 1px;
    height: 24px;
    background-color: {t.border};
    margin: 4px 6px;
}}

/* ===== Menu ===== */
QMenuBar {{
    background-color: transparent;
    color: {t.text_primary};
    font-family: "Segoe UI", "Cairo", sans-serif;
    font-size: 14px;
}}

QMenuBar::item {{
    padding: 6px 12px;
    border-radius: {radius};
    background-color: transparent;
}}

QMenuBar::item:selected {{
    background-color: {t.bg_tertiary};
}}

QMenuBar::item:pressed {{
    background-color: {t.accent};
    color: #FFFFFF;
}}

QMenu {{
    background-color: {t.surface};
    border: 1px solid {t.border};
    border-radius: {radius};
    padding: 4px 2px;
    font-family: "Segoe UI", "Cairo", sans-serif;
    font-size: 13px;
}}

QMenu::item {{
    padding: 6px 24px 6px 20px;
    border-radius: 4px;
    background-color: transparent;
}}

QMenu::item:selected {{
    background-color: {t.bg_tertiary};
    color: {t.accent_hover};
}}

QMenu::item:disabled {{
    color: {t.text_disabled};
}}

QMenu::separator {{
    height: 1px;
    background-color: {t.border};
    margin: 4px 8px;
}}

/* ===== Dock Widget ===== */
QDockWidget {{
    background-color: {t.surface};
    border: 1px solid {t.border};
    border-radius: {radius};
    font-family: "Segoe UI", "Cairo", sans-serif;
}}

QDockWidget::title {{
    background-color: {t.surface_alt};
    color: {t.text_secondary};
    padding: 6px 10px;
    border-radius: {radius} {radius} 0 0;
    font-family: "Segoe UI", "Cairo", sans-serif;
    font-size: 13px;
}}

QDockWidget::close-button,
QDockWidget::float-button {{
    background: transparent;
    border: none;
    color: {t.text_secondary};
}}

QDockWidget::close-button:hover,
QDockWidget::float-button:hover {{
    color: {t.text_primary};
}}

/* ===== Splitters ===== */
QSplitter::handle {{
    background-color: {t.border};
}}

QSplitter::handle:horizontal {{
    width: 4px;
    margin: 2px 0;
}}

QSplitter::handle:vertical {{
    height: 4px;
    margin: 0 2px;
}}

QSplitter::handle:hover {{
    background-color: {t.accent};
}}

/* ===== Line Edit / Text Edit base ===== */
QLineEdit,
QTextEdit,
QPlainTextEdit {{
    background-color: {t.editor_bg};
    color: {t.editor_fg};
    border: 1px solid {t.border};
    border-radius: {radius};
    padding: 6px 10px;
    selection-background-color: {t.editor_selection};
    font-family: "Fira Code", "Cairo", "Segoe UI Emoji", monospace;
}}

QLineEdit:focus,
QTextEdit:focus,
QPlainTextEdit:focus {{
    border: 2px solid {t.accent};
    padding: 5px 9px;
}}

QLineEdit:disabled,
QTextEdit:disabled,
QPlainTextEdit:disabled {{
    color: {t.text_disabled};
    background-color: {t.surface_alt};
}}

/* ===== Combo Box ===== */
QComboBox {{
    background-color: {t.surface};
    border: 1px solid {t.border};
    border-radius: {radius};
    padding: 4px 10px;
    color: {t.text_primary};
}}

QComboBox:hover {{
    border-color: {t.accent_hover};
}}

QComboBox::drop-down {{
    background: transparent;
    border: none;
    padding: 0 6px;
}}

QComboBox QAbstractItemView {{
    background-color: {t.surface};
    border: 1px solid {t.border};
    border-radius: {radius};
    selection-background-color: {t.bg_tertiary};
    outline: none;
    color: {t.text_primary};
}}

QComboBox QAbstractItemView::item {{
    padding: 6px 10px;
}}

QComboBox QAbstractItemView::item:selected {{
    background-color: {t.accent};
    color: #FFFFFF;
}}

/* ===== Tree View / List View ===== */
QTreeView,
QListView {{
    background-color: {t.editor_bg};
    border: 1px solid {t.border};
    border-radius: {radius};
    gridline-color: {t.border};
    selection-background-color: {t.bg_tertiary};
    alternate-background-color: {t.surface_alt};
}}

QTreeView::item {{
    padding: 4px 6px;
    border-radius: 4px;
}}

QTreeView::item:selected {{
    background-color: {t.accent};
    color: #FFFFFF;
}}

QTreeView::item:selected:focus {{
    background-color: {t.accent};
    color: #FFFFFF;
}}

QTreeView::item:hover {{
    background-color: {t.bg_tertiary};
}}

QTreeView::branch {{
    background: transparent;
}}

QTreeView::branch:has-siblings {{
    border-left: 1px solid {t.border};
}}

QTreeView::branch:empty {{
    border-left: 1px solid {t.border};
}}

QTreeView::item:has-children {{
    font-weight: 500;
}}

/* ===== Tabs ===== */
QTabWidget {{
    background-color: {t.bg_secondary};
    border: 1px solid {t.border};
    border-radius: {radius};
}}

QTabWidget::pane {{
    border: none;
    background-color: {t.surface};
    border-radius: 0 0 {radius} {radius};
}}

QTabBar {{
    background-color: {t.surface_alt};
    border: none;
    border-bottom: 1px solid {t.border};
    border-radius: {radius} {radius} 0 0;
    padding: 2px 6px;
    font-family: "Segoe UI", "Cairo", sans-serif;
}}

QTabBar::tab {{
    background-color: transparent;
    color: {t.text_secondary};
    padding: 8px 16px 6px;
    border: none;
    border-bottom: 2px solid transparent;
    border-radius: {radius} {radius} 0 0;
}}

QTabBar::tab:selected {{
    background-color: {t.surface};
    color: {t.text_primary};
    border-bottom: 2px solid {t.accent};
    font-weight: 600;
}}

QTabBar::tab:hover {{
    color: {t.text_primary};
}}

QTabBar::tab:!selected {{
    font-weight: 400;
}}

QTabBar::tab:disabled {{
    color: {t.text_disabled};
}}

/* Close button on tabs */
QTabBar::tab CloseButton {{
    background: transparent;
    border: none;
    padding: 2px;
}}

/* ===== Status Bar ===== */
QStatusBar {{
    background-color: {t.surface};
    color: {t.text_secondary};
    border-top: 1px solid {t.border};
    font-family: "Segoe UI", "Cairo", sans-serif;
    font-size: 13px;
    padding: 4px 12px;
}}

QStatusBar::item {{
    border: none;
    padding: 0 8px;
}}

/* ===== Progress Bar ===== */
QProgressBar {{
    background-color: {t.surface_alt};
    border: 1px solid {t.border};
    border-radius: {radius};
    text-align: center;
    font-family: "Segoe UI", "Cairo", sans-serif;
    font-size: 13px;
    color: {t.text_primary};
}}

QProgressBar::chunk {{
    background-color: {t.accent};
    border-radius: {radius};
}}

/* ===== Group Box ===== */
QGroupBox {{
    border: 1px solid {t.border};
    border-radius: {radius};
    padding-top: 20px;
    margin-top: 10px;
    font-family: "Segoe UI", "Cairo", sans-serif;
    font-weight: 600;
}}

QGroupBox::title {{
    padding-left: 14px;
    padding-right: 14px;
    color: {t.text_secondary};
}}

/* ===== CheckBox ===== */
QCheckBox {{
    spacing: 6px;
    font-family: "Segoe UI", "Cairo", sans-serif;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 1px solid {t.border};
    border-radius: 4px;
}}

QCheckBox::indicator:checked {{
    background-color: {t.accent};
    border-color: {t.accent};
}}

QCheckBox:disabled {{
    color: {t.text_disabled};
}}

/* ===== ToolButton ===== */
QToolButton {{
    background-color: {t.surface};
    border: 1px solid {t.border};
    border-radius: 6px;
    padding: 6px 10px;
    font-family: "Segoe UI", "Cairo", sans-serif;
}}

QToolButton:hover {{
    background-color: {t.surface_alt};
    border-color: {t.accent_hover};
}}

QToolButton:pressed {{
    background-color: {t.bg_tertiary};
}}

QToolButton:disabled {{
    color: {t.text_disabled};
}}

QToolButton[popupMode="1"] {{
    padding: 4px 8px;
}}
"""


_QSS_CACHE: dict[str, str] = {}


def generate_qss(theme_name: str = "dark") -> str:
    """Return the QSS string for a theme, cached."""
    if theme_name in _QSS_CACHE:
        return _QSS_CACHE[theme_name]
    theme = get_theme(theme_name)
    qss = _generate_qss(theme)
    _QSS_CACHE[theme_name] = qss
    return qss


def apply_theme(app: QApplication, theme_name: str = "dark") -> Theme:
    """Apply a theme to the QApplication palette and style sheet.

    Returns the :class:`Theme` that was applied.
    """
    theme = get_theme(theme_name)

    # Apply the style sheet.
    qss = generate_qss(theme_name)
    app.setStyleSheet(qss)

    # Apply a QPalette for additional consistency.
    palette = _build_palette(theme)
    app.setPalette(palette)

    # Apply a base font.
    font = QFont("Segoe UI, Cairo, Fira Code, monospace", 14)
    app.setFont(font)

    return theme


def _build_palette(theme: Theme) -> QPalette:
    """Build a QPalette from a :class:`Theme`."""
    palette = QPalette()

    def _color(hex_str: str) -> QColor:
        c = QColor(hex_str)
        return c

    # Active
    palette.setColor(QPalette.ColorRole.Window, _color(theme.bg_primary))
    palette.setColor(QPalette.ColorRole.WindowText, _color(theme.text_primary))
    palette.setColor(QPalette.ColorRole.Base, _color(theme.editor_bg))
    palette.setColor(QPalette.ColorRole.AlternateBase, _color(theme.surface_alt))
    palette.setColor(QPalette.ColorRole.ToolTipBase, _color(theme.surface))
    palette.setColor(QPalette.ColorRole.ToolTipText, _color(theme.text_primary))
    palette.setColor(QPalette.ColorRole.Text, _color(theme.editor_fg))
    palette.setColor(QPalette.ColorRole.Button, _color(theme.surface))
    palette.setColor(QPalette.ColorRole.ButtonText, _color(theme.text_primary))
    palette.setColor(QPalette.ColorRole.BrightText, _color(theme.text_primary))
    palette.setColor(QPalette.ColorRole.Link, _color(theme.accent))
    palette.setColor(QPalette.ColorRole.Highlight, _color(theme.accent))
    palette.setColor(QPalette.ColorRole.HighlightedText, _color("#FFFFFF"))
    palette.setColor(QPalette.ColorRole.PlaceholderText, _color(theme.text_disabled))

    # Disabled
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, _color(theme.text_disabled))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, _color(theme.text_disabled))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, _color(theme.text_disabled))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, _color(theme.accent_pressed))

    return palette


def load_settings_into_service(settings) -> None:
    """Convenience function to initialize theme from settings."""
    # This is a hook for the main window; actual application done in main_window.
    pass
