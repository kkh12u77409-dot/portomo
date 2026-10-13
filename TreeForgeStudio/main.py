#!/usr/bin/env python3
"""TreeForge Studio — application entry point.

Usage::

    python main.py

Creates the QApplication, applies the persisted theme/language,
shows the main window, and runs the event loop.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the package directory is importable when run directly.
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication  # noqa: E402

from app.main_window import MainWindow  # noqa: E402
from app.settings_service import SettingsService  # noqa: E402
from app.translations import set_language as _set_lang  # noqa: E402
from app.theme_manager import apply_theme  # noqa: E402


def main() -> int:
    """Launch TreeForge Studio."""
    app = QApplication(sys.argv)
    app.setApplicationName("TreeForge Studio")
    app.setApplicationDisplayName("TreeForge Studio")
    app.setOrganizationName("TreeForgeStudio")

    # Persisted preferences must be created before the main window.
    settings = SettingsService("TreeForgeStudio")

    # Apply the persisted theme before the window is realised so the
    # first paint already matches the user's choice.
    set_language_early(settings)
    apply_theme(app, settings.get_theme())

    # Load the application icon from the SVG asset when available.
    icon_path = ROOT / "assets" / "icons" / "app_icon.svg"
    if icon_path.exists():
        app.setWindowIcon(_load_app_icon(icon_path))

    window = MainWindow(settings)
    window.show()
    return app.exec()


def _load_app_icon(icon_path: Path) -> QIcon:
    """Render the SVG application icon into a QIcon at multiple sizes."""
    from PyQt6.QtCore import QByteArray, QSize
    from PyQt6.QtGui import QPixmap, QPainter
    from PyQt6.QtSvg import QSvgRenderer

    svg_bytes = QByteArray(icon_path.read_bytes())
    result = QIcon()
    for size in (16, 24, 32, 48, 64, 128, 256):
        renderer = QSvgRenderer(svg_bytes)
        pixmap = QPixmap(QSize(size, size))
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        result.addPixmap(pixmap)
    return result


def set_language_early(settings: SettingsService) -> None:
    """Set the translation language from saved settings before UI creation."""
    _set_lang(settings.get_language())


if __name__ == "__main__":
    raise SystemExit(main())
