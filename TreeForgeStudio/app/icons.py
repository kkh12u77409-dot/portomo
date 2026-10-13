"""Icons module: provides SVG-based icons as QIcon objects.

Icons are defined as raw SVG strings rendered with QSvgRenderer / QPixmap
so that no binary image assets are required and themes can recolor them.
"""

from __future__ import annotations

from functools import lru_cache

from PyQt6.QtCore import QByteArray, QSize, Qt
from PyQt6.QtGui import QIcon, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer

_ICON_COLOR = "currentColor"


@lru_cache(maxsize=128)
def _svg_icon(svg: str, size: int, color: str) -> QIcon:
    """Render an SVG string to a QIcon at the given size and color."""
    renderer = QSvgRenderer(QByteArray(svg.replace(_ICON_COLOR, color).encode("utf-8")))
    pixmap = QPixmap(QSize(size, size))
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    icon = QIcon(pixmap)
    icon.addPixmap(pixmap, QIcon.Mode.Normal)
    return icon


def icon(name: str, size: int = 24, color: str = "#F1F5F9") -> QIcon:
    """Return a QIcon for *name*, rendered at *size* in *color*."""
    if name in _SVG_ICONS:
        return _svg_icon(_SVG_ICONS[name], size, color)
    return QIcon()


def get_icon(name: str, size: int = 24, color: str = "#F1F5F9") -> QIcon:
    """Alias for :func:`icon`."""
    return icon(name, size, color)


# --------------------------------------------------------------------------
# SVG source files (single path icons, using currentColor for theming)
# --------------------------------------------------------------------------

_SVG_ICONS: dict[str, str] = {
    # Application
    "app": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M3 7C3 5.89543 3.89543 5 5 5H9L11 7H19C20.1046 7 21 7.89543 21 9V17C21 18.1046 20.1046 19 19 19H5C3.89543 19 3 18.1046 3 17V7Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M12 10V16M9 13H15" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
</svg>""",
    "folder": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M3 7C3 5.89543 3.89543 5 5 5H9L11 7H19C20.1046 7 21 7.89543 21 9V17C21 18.1046 20.1046 19 19 19H5C3.89543 19 3 18.1046 3 17V7Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
</svg>""",
    "folder-open": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M3 7C3 5.89543 3.89543 5 5 5H9L11 7H19C20.1046 7 21 7.89543 21 9V17C21 18.1046 20.1046 19 19 19H5C3.89543 19 3 18.1046 3 17V7Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M7 19L8.5 16H15L13.5 19H7Z" fill="currentColor" fill-opacity="0.3" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
</svg>""",
    "folder-plus": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M3 7C3 5.89543 3.89543 5 5 5H9L11 7H19C20.1046 7 21 7.89543 21 9V17C21 18.1046 20.1046 19 19 19H5C3.89543 19 3 18.1046 3 17V7Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M12 10.5V15.5M9.5 13H14.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
</svg>""",
    "file": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M6 3C5.44772 3 5 3.44772 5 4V20C5 20.5523 5.44772 21 6 21H18C18.5523 21 19 20.5523 19 20V9.41421C19 9.01642 18.8431 8.63531 18.5607 8.35355L13.6464 3.43934C13.3647 3.15758 12.9826 3 12.5858 3H6Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M13 3V8C13 8.55229 13.4477 9 14 9H18" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
</svg>""",
    "file-text": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M6 3C5.44772 3 5 3.44772 5 4V20C5 20.5523 5.44772 21 6 21H18C18.5523 21 19 20.5523 19 20V9.41421C19 9.01642 18.8431 8.63531 18.5607 8.35355L13.6464 3.43934C13.3647 3.15758 12.9826 3 12.5858 3H6Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M13 3V8C13 8.55229 13.4477 9 14 9H18" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M8.5 12.5H15.5M8.5 15.5H15.5M8.5 18H12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
</svg>""",
    "file-plus": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M6 3C5.44772 3 5 3.44772 5 4V20C5 20.5523 5.44772 21 6 21H18C18.5523 21 19 20.5523 19 20V9.41421C19 9.01642 18.8431 8.63531 18.5607 8.35355L13.6464 3.43934C13.3647 3.15758 12.9826 3 12.5858 3H6Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M13 3V8C13 8.55229 13.4477 9 14 9H18" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M12 12V16M10 14H14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
</svg>""",
    "file-warning": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M6 3C5.44772 3 5 3.44772 5 4V20C5 20.5523 5.44772 21 6 21H18C18.5523 21 19 20.5523 19 20V9.41421C19 9.01642 18.8431 8.63531 18.5607 8.35355L13.6464 3.43934C13.3647 3.15758 12.9826 3 12.5858 3H6Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M13 3V8C13 8.55229 13.4477 9 14 9H18" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M12 11.5V14M12 16.5H12.01" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
</svg>""",
    # Actions
    "plus": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 5V19M5 12H19" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</svg>""",
    "trash": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M4 7H20M10 4H14M6 7L7 21H17L18 7M10 11V17M14 11V17" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "edit": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M4 20H20M14.5 4.5L19.5 9.5M16 3L21 8L11.5 17.5L5 19L6.5 12.5L16 3Z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "save": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M5 3H15L19 7V21H5V3Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M8 3V8H14V3" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M9 14H15V21H9V14Z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
</svg>""",
    "save-all": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M5 3H13L16 6V21H5V3Z" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/>
  <path d="M7 3V8H13V3" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/>
  <path d="M8 12H13V18H8V12Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
  <path d="M17 15H19V21H17" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/>
</svg>""",
    "refresh": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M20 12C20 16.4183 16.4183 20 12 20C7.58172 20 4 16.4183 4 12C4 7.58172 7.58172 4 12 4C14.8535 4 17.3541 5.42541 18.7508 7.555M18.7508 7.555L18.7508 3.25M18.7508 7.555H14.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "search": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="1.8"/>
  <path d="M16 16L21 21" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
</svg>""",
    "settings": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 15C13.6569 15 15 13.6569 15 12C15 10.3431 13.6569 9 12 9C10.3431 9 9 10.3431 9 12C9 13.6569 10.3431 15 12 15Z" stroke="currentColor" stroke-width="1.8"/>
  <path d="M19.4 15C19.1284 15.8357 19.1484 16.7241 19.4576 17.546C19.8004 18.457 20.0749 18.5561 19.2184 18.9858C18.362 19.4155 17.9044 18.8618 16.9442 18.5792C15.9841 18.2966 14.9789 18.4265 14.1 18.4576C13.2211 18.4887 12.4395 18.5869 11.7316 18.0686C10.9603 17.5033 10.4354 16.656 10.2725 15.7037C10.4821 14.8244 10.2225 13.9108 9.57626 13.2645C8.93004 12.6183 8.01636 12.3587 7.13707 12.5684C6.18478 12.7313 5.33747 13.2562 4.77217 14.0275C4.25393 14.7354 4.35207 15.517 4.38319 16.3959C4.41429 17.2748 4.54428 18.2799 4.26146 19.24C3.97862 20.2002 3.42486 20.6577 3.85458 21.5142C4.28431 22.3707 4.38343 22.0962 5.2944 21.7534C6.11632 21.4442 7.00467 21.4242 7.84034 21.6958C8.7285 21.9811 9.45872 22.6227 9.91331 23.4354M9.91331 4.56463C9.45873 5.37733 8.72849 6.01887 7.84033 6.30418C7.00467 6.57581 6.11632 6.5558 5.2944 6.24662C4.38343 5.90375 4.28431 5.62924 3.85458 6.4857C3.42486 7.34217 3.97862 7.89988 4.26146 8.86004C4.54428 9.8201 4.41429 10.8252 4.38319 11.7041C4.35207 12.583 4.25393 13.3646 4.77217 14.0725C5.33747 14.8438 6.18478 15.3687 7.13707 15.5316C8.01636 15.7411 8.93004 15.4815 9.57626 14.8353C10.2225 14.1891 10.4821 13.2754 10.2725 12.3962C10.4354 11.4439 10.9603 10.5966 11.7316 10.0313C12.4395 9.51302 13.2211 9.61116 14.1 9.64226C14.9789 9.67335 15.9841 9.80337 16.9442 9.52056C17.9044 9.23772 18.362 8.68403 19.2184 9.11364C20.0749 9.54325 19.8004 9.64239 19.4576 10.5534C19.1484 11.3753 19.1284 12.2636 19.4 13.0992C19.6853 13.9874 20.3268 14.7176 21.1395 15.1722C21.9523 15.6268 22.1776 16.4286 22.1395 17.3974M14.5 6.5C15.209 6.98775 16.0042 7.32492 16.8442 7.49321" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    # Navigation
    "dashboard": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M4 4H10V10H4V4ZM14 4H20V10H14V4ZM4 14H10V20H4V14ZM14 14H20V20H14V14Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
</svg>""",
    "compass": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.8"/>
  <path d="M14.5 9.5L11 11L9.5 14.5L13 13L14.5 9.5Z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
</svg>""",
    "layers": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 3L3 7.5L12 12L21 7.5L12 3Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M3 12L12 16.5L21 12" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M3 16.5L12 21L21 16.5" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
</svg>""",
    # Status
    "check": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M5 13L9 17L19 7" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "check-circle": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.8"/>
  <path d="M8 12.5L11 15.5L16 9.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "warning": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 3L22 20H2L12 3Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M12 9.5V13.5M12 16.5H12.01" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
</svg>""",
    "error": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.8"/>
  <path d="M9 9L15 15M15 9L9 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</svg>""",
    "info": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.8"/>
  <path d="M12 8V12M12 16H12.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</svg>""",
    # Misc
    "lang": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M3 6C3 4.34315 4.34315 3 6 3H15L21 9V18C21 19.6569 19.6569 21 18 21H6C4.34315 21 3 19.6569 3 18V6Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M15 3V9H21" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M11.5 11.5C10.5 10.5 9 10 7.5 10V15C9 15 10.5 15.5 11.5 16.5M11.5 11.5C12.5 10.5 14 10 15.5 10V15C14 15 12.5 15.5 11.5 16.5M9 7.5C9 9 9.5 10 9.5 12.5M9 7.5C9 9 8.5 10 8.5 12.5M9.5 7.5H14M9.5 7.5L11.5 7.5M14 7.5C14 9 14.5 10 14.5 12.5M14 7.5C14 9 13.5 10 13.5 12.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
</svg>""",
    "theme": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M12 3C7.02944 3 3 6.58172 3 11C3 15.4183 7.02944 19 12 19C13.5 19 12.7 17.5 13.7 16C14.7 14.5 16.5 13.5 17 12C18.5 10 18.5 8 17 6.5C15.5 5 12 3 12 3Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M16 11C16 11.5523 15.5523 12 15 12C14.4477 12 14 11.5523 14 11C14 10.4477 14.4477 10 15 10C15.5523 10 16 10.4477 16 11Z" fill="currentColor"/>
</svg>""",
    "terminal": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="3" y="4" width="18" height="16" rx="2" stroke="currentColor" stroke-width="1.8"/>
  <path d="M7 9L9.5 11.5L7 14M12.5 14.5H16.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "copy": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="9" y="9" width="11" height="11" rx="2" stroke="currentColor" stroke-width="1.8"/>
  <path d="M15 9V5.58579C15 5.26922 14.8139 4.97673 14.5171 4.83426L11.4829 3.31737C11.3012 3.21742 11.0881 3.19084 10.8857 3.24299L5 4H5C5 4 5 4 5 4" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
</svg>""",
    "close": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M6 6L18 18M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</svg>""",
    "undo": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M4 9C4 8.44772 4.44772 8 5 8H19C19.5523 8 20 8.44772 20 9V15" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M7 5L4 8L7 11" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "redo": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M20 9C20 8.44772 19.5523 8 19 8H5C4.44772 8 4 8.44772 4 9V15" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M17 5L20 8L17 11" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "cut": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="6" cy="6" r="2.5" stroke="currentColor" stroke-width="1.7"/>
  <circle cx="6" cy="18" r="2.5" stroke="currentColor" stroke-width="1.7"/>
  <path d="M7.5 8L20 20M7.5 16L20 4" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/>
</svg>""",
    "paste": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M9 4H15V7H9V4Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M9 3H15V5H9V3Z" stroke="currentColor" stroke-width="1.6"/>
  <path d="M8 5H6C5.44772 5 5 5.44772 5 6V20C5 20.5523 5.44772 21 6 21H18C18.5523 21 19 20.5523 19 20V6C19 5.44772 18.5523 5 18 5H16" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
</svg>""",
    "select-all": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="4" y="4" width="16" height="16" rx="2" stroke="currentColor" stroke-width="1.6" stroke-dasharray="3 3"/>
  <rect x="8" y="8" width="8" height="8" rx="1" fill="currentColor" fill-opacity="0.35" stroke="currentColor" stroke-width="1.6"/>
</svg>""",
    "filter": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M3 5H21L14 13V19L10 21V13L3 5Z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>""",
    "eye": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M2 12C2 12 5.5 5.5 12 5.5C18.5 5.5 22 12 22 12C22 12 18.5 18.5 12 18.5C5.5 18.5 2 12 2 12Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
  <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="1.8"/>
</svg>""",
    "eye-off": """<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M4 8C2.7 9.5 2 12 2 12C2 12 5.5 18.5 12 18.5C13.7 18.5 15.2 18 16.4 17.3M20 15.5C21.2 13.8 22 12 22 12C22 12 18.5 5.5 12 5.5C11 5.5 10 5.6 9.1 5.9" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/>
  <path d="M4 4L20 20" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
</svg>""",
}
