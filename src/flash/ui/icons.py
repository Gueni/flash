#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?              _
#?             (_)________  ____  _____
#?            / / ___/ __ \/ __ \/ ___/
#?           / / /__/ /_/ / / / (__  )
#?          /_/\___/\____/_/ /_/____/
#?
#?
#? Name:        icons.py
#? Purpose:     Crisp, theme-colored line icons rendered from inline SVG (no image files needed).
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     05/09/2019
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
from    __future__                  import  annotations

import  hashlib
import  tempfile
from    functools                   import  lru_cache
from    pathlib                     import  Path

from    PySide6.QtCore              import  QByteArray, QRectF, Qt
from    PySide6.QtGui               import  QGuiApplication, QIcon, QPainter, QPixmap
from    PySide6.QtSvg               import  QSvgRenderer
#?----------------------------------------------------------------------------------------------------------------------------------------
# 24x24 stroke icons in the spirit of Lucide (ISC licensed design language).
PATHS: dict[str, str]       = {
    "flash": '<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>',
    "memory": '<path d="M22 12H2"/><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/><path d="M6 16h.01M10 16h.01"/>',
    "cpu": '<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M15 2v2M15 20v2M2 15h2M2 9h2M20 15h2M20 9h2M9 2v2M9 20v2"/>',
    "tools": '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M12 8v4M12 16h.01"/>',
    "terminal": '<path d="m4 17 6-6-6-6M12 19h8"/>',
    "settings": '<path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6"/>',
    "info": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>',
    "plug": '<path d="M12 22v-5M9 8V2M15 8V2M18 8v5a4 4 0 0 1-4 4h-4a4 4 0 0 1-4-4V8z"/>',
    "unplug": '<path d="M12 22v-5M9 8V2M15 8V2M18 8v5a4 4 0 0 1-4 4h-4a4 4 0 0 1-4-4V8z"/><path d="M3 3l18 18"/>',
    "refresh": '<path d="M21 12a9 9 0 1 1-3-6.7L21 8"/><path d="M21 3v5h-5"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>',
    "moon": '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9z"/>',
    "menu": '<path d="M4 6h16M4 12h16M4 18h16"/>',
    "play": '<path d="M6 3l14 9-14 9z"/>',
    "stop": '<rect x="6" y="6" width="12" height="12" rx="2"/>',
    "trash": '<path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>',
    "folder": '<path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2z"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "x": '<path d="M18 6 6 18M6 6l12 12"/>',
    "download": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/>',
    "upload": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>',
    "eraser": '<path d="m7 21-4.3-4.3c-1-1-1-2.5 0-3.4l9.6-9.6c1-1 2.5-1 3.4 0l5.6 5.6c1 1 1 2.5 0 3.4L13 21M22 21H7M5 11l9 9"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "copy": '<rect x="8" y="8" width="14" height="14" rx="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>',
    "save": '<path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><path d="M17 21v-8H7v8M7 3v5h8"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "file": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/>',
    "flame": '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.07-2.14-.22-4.05 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.15.43-2.29 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>',
    "key": '<circle cx="7.5" cy="15.5" r="5.5"/><path d="m21 2-9.6 9.6M15.5 7.5l3 3L22 7l-3-3"/>',
    "send": '<path d="m22 2-7 20-4-9-9-4z"/><path d="M22 2 11 13"/>',
    "layers": '<path d="m12 2 10 5-10 5L2 7z"/><path d="m2 17 10 5 10-5M2 12l10 5 10-5"/>',
    "external": '<path d="M15 3h6v6M10 14 21 3M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
    "chevron-down": '<path d="m6 9 6 6 6-6"/>',
    "chevron-up": '<path d="m18 15-6-6-6 6"/>',
    "hash": '<path d="M4 9h16M4 15h16M10 3 8 21M16 3l-2 18"/>',
    "activity": '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    "panel": '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 15h18"/>',
    "check-square": '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="m8 12 3 3 5-6"/>',
    "power": '<path d="M12 2v10"/><path d="M18.4 6.6a9 9 0 1 1-12.77.04"/>',
    "image": '<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.1-3.1a2 2 0 0 0-2.8 0L6 21"/>',
    "scan": '<path d="M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2M7 12h10"/>',
    "code": '<path d="m16 18 6-6-6-6M8 6l-6 6 6 6"/>',
    "book": '<path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>',
    "library": '<path d="m16 6 4 14M12 6v14M8 8v12M4 4v16"/>',
    # window buttons (custom title bar)
    "win-min": '<path d="M4 12h16"/>',
    "win-max": '<rect x="4" y="4" width="16" height="16" rx="2.5"/>',
    "win-restore": '<rect x="4" y="8" width="12" height="12" rx="2"/><path d="M8 8V6.5A2.5 2.5 0 0 1 10.5 4h7A2.5 2.5 0 0 1 20 6.5v7a2.5 2.5 0 0 1-2.5 2.5H16"/>',
    "win-close": '<path d="M5 5l14 14M19 5 5 19"/>',
}
#?----------------------------------------------------------------------------------------------------------------------------------------
def svg(name: str, color: str, stroke: float = 2.0) -> str:
    body                    = PATHS.get(name, PATHS["info"])
    fill                    = color if name in ("play",) else "none"
    if name.startswith("win-"):
        stroke              = 1.6                                                      # thin glyphs like native caption buttons
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{fill}" stroke="{color}" '
            f'stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round">{body}</svg>')
#?----------------------------------------------------------------------------------------------------------------------------------------
def pixmap(name: str, color: str, size: int = 18) -> QPixmap:
    app                     = QGuiApplication.instance()
    ratio                   = app.devicePixelRatio() if app else 1.0
    ratio                   = max(ratio, 2.0)                                          # oversample: sharp on any screen the window moves to
    px                      = QPixmap(int(size * ratio), int(size * ratio))
    px.fill(Qt.GlobalColor.transparent)
    renderer                = QSvgRenderer(QByteArray(svg(name, color).encode()))
    painter                 = QPainter(px)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(painter, QRectF(0, 0, px.width(), px.height()))
    painter.end()
    px.setDevicePixelRatio(ratio)
    return px
#?----------------------------------------------------------------------------------------------------------------------------------------
@lru_cache(maxsize=512)
def icon(name: str, color: str, active_color: str | None = None, disabled_color: str | None = None) -> QIcon:
    ic                      = QIcon()
    for size in (16, 20, 24, 32):
        ic.addPixmap(pixmap(name, color, size), QIcon.Mode.Normal, QIcon.State.Off)
        if active_color:
            ic.addPixmap(pixmap(name, active_color, size), QIcon.Mode.Normal, QIcon.State.On)
            ic.addPixmap(pixmap(name, active_color, size), QIcon.Mode.Active, QIcon.State.On)
        if disabled_color:
            ic.addPixmap(pixmap(name, disabled_color, size), QIcon.Mode.Disabled, QIcon.State.Off)
    return ic
#?----------------------------------------------------------------------------------------------------------------------------------------
def svg_file(name: str, color: str) -> str:
    """Write an icon to a cache file so stylesheets can reference it with ``url(...)``."""
    key                     = hashlib.md5(f"{name}{color}".encode()).hexdigest()[:10]
    folder                  = Path(tempfile.gettempdir()) / "flash-ui-icons"
    folder.mkdir(parents=True, exist_ok=True)
    path                    = folder / f"{name}-{key}.svg"
    if not path.exists():
        path.write_text(svg(name, color, 2.4), encoding="utf-8")
    return path.as_posix()
#?----------------------------------------------------------------------------------------------------------------------------------------
