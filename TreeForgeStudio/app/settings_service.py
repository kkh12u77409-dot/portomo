"""Settings service using QSettings for persistent preferences."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from PyQt6.QtCore import QSettings
except ImportError:  # pragma: no cover
    QSettings = None


_DEFAULTS: dict[str, Any] = {
    "language": "en",
    "theme": "dark",
    "window_width": 1400,
    "window_height": 900,
    "window_x": -1,
    "window_y": -1,
    "last_destination": "",
    "last_project_dir": "",
    "recent_projects": [],
    "editor_font_family": "Segoe UI, Cairo, Fira Code, monospace",
    "editor_font_size": 12,
    "tab_spaces": 4,
    "show_whitespace": False,
    "auto_indent": True,
    "conflict_policy": "skip",
    "create_backups": False,
    "sidebar_visible": True,
    "sidebar_width": 280,
    "show_hidden_files": False,
    "max_recent_projects": 10,
}


class SettingsService:
    """Wraps QSettings to persist application preferences."""

    def __init__(self, app_name: str = "TreeForgeStudio") -> None:
        self.app_name = app_name
        if QSettings is not None:
            self._qsettings = QSettings(
                "TreeForgeStudio", app_name
            )
        else:
            self._qsettings = None
        self._cache: dict[str, Any] = {}

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a setting, falling back to defaults."""
        if key in self._cache:
            return self._cache[key]
        if key in _DEFAULTS:
            default = _DEFAULTS[key]
        if self._qsettings is not None:
            value = self._qsettings.value(key, default)
            # QSettings may return QVariant-wrapped strings; normalize.
            if isinstance(value, str):
                result: Any = value
            else:
                result = value
            self._cache[key] = result
            return result
        return default

    def set(self, key: str, value: Any) -> None:
        """Persist a setting."""
        self._cache[key] = value
        if self._qsettings is not None:
            self._qsettings.setValue(key, value)
            self._qsettings.sync()

    def get_recent_projects(self) -> list[str]:
        """Return the list of recent project paths."""
        projects = self.get("recent_projects", [])
        if isinstance(projects, str):
            return [projects] if projects else []
        if not isinstance(projects, list):
            return []
        return [str(p) for p in projects]

    def add_recent_project(self, path: str) -> None:
        """Add a project to the recent list (dedup, capped)."""
        max_count = int(self.get("max_recent_projects", 10))
        projects = self.get_recent_projects()
        if path in projects:
            projects.remove(path)
        projects.insert(0, path)
        projects = projects[:max_count]
        self.set("recent_projects", projects)

    def clear_recent_projects(self) -> None:
        """Clear the recent projects list."""
        self.set("recent_projects", [])

    def clear_all_settings(self) -> None:
        """Reset all settings to defaults."""
        if self._qsettings is not None:
            self._qsettings.clear()
            self._qsettings.sync()
        self._cache.clear()
        for key, value in _DEFAULTS.items():
            self._cache[key] = value

    def get_default_destination(self) -> str:
        dest = self.get("last_destination", "")
        if dest:
            return str(dest)
        home = Path.home()
        return str(home / "TreeForgeProjects")

    def get_language(self) -> str:
        lang = self.get("language", "en")
        return str(lang) if lang else "en"

    def get_theme(self) -> str:
        theme = self.get("theme", "dark")
        return str(theme) if theme else "dark"

    def get_conflict_policy(self) -> str:
        return str(self.get("conflict_policy", "skip"))

    def window_geometry(self) -> tuple[int, int, int, int]:
        """Return (x, y, width, height) for window placement."""
        w = int(self.get("window_width", 1400))
        h = int(self.get("window_height", 900))
        x = int(self.get("window_x", -1))
        y = int(self.get("window_y", -1))
        return x, y, w, h

    def save_window_geometry(self, x: int, y: int, w: int, h: int) -> None:
        self.set("window_x", x)
        self.set("window_y", y)
        self.set("window_width", w)
        self.set("window_height", h)

    def get_editor_settings(self) -> dict[str, Any]:
        return {
            "font_family": self.get("editor_font_family", "monospace"),
            "font_size": int(self.get("editor_font_size", 12)),
            "tab_spaces": int(self.get("tab_spaces", 4)),
            "show_whitespace": bool(self.get("show_whitespace", False)),
            "auto_indent": bool(self.get("auto_indent", True)),
        }

    def get_ui_settings(self) -> dict[str, Any]:
        return {
            "sidebar_visible": bool(self.get("sidebar_visible", True)),
            "sidebar_width": int(self.get("sidebar_width", 280)),
            "show_hidden_files": bool(self.get("show_hidden_files", False)),
        }
