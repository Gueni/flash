#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?             __  _ __  __     __
#?            / /_(_) /_/ /__  / /_  ____ ______
#?           / __/ / __/ / _ \/ __ \/ __ `/ ___/
#?          / /_/ / /_/ /  __/ /_/ / /_/ / /
#?          \__/_/\__/_/\___/_.___/\__,_/_/
#?
#?
#? Name:        titlebar.py
#? Purpose:     Custom window chrome: a modern title bar (icon, title, minimize / maximize / close) and the frameless
#?              window plumbing behind it. Dragging and edge-resizing are handed to the OS (startSystemMove /
#?              startSystemResize), so Windows snap layouts, Aero shake and Linux window managers keep working.
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     05/09/2019
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
from    __future__                  import  annotations

import  sys

from    PySide6.QtCore              import  QEvent, QObject, QPoint, QSize, Qt
from    PySide6.QtGui               import  QIcon
from    PySide6.QtWidgets           import  QApplication, QFrame, QHBoxLayout, QLabel, QToolButton, QWidget

from    flash.ui.theme              import  theme
from    flash.ui.widgets            import  set_icon
#?----------------------------------------------------------------------------------------------------------------------------------------
TITLEBAR_HEIGHT             = 40
RESIZE_MARGIN               = 6                                                        # px from the window edge that start a resize
#?----------------------------------------------------------------------------------------------------------------------------------------
class TitleBar(QFrame):
    """Draggable title bar with window buttons. Double-click toggles maximize."""

    def __init__(self, window: QWidget, icon: QIcon, title: str, subtitle: str = "") -> None:
        super().__init__(window)
        self.setObjectName("TitleBar")
        self.setFixedHeight(TITLEBAR_HEIGHT)
        self._window        = window

        lay                 = QHBoxLayout(self)
        lay.setContentsMargins(14, 0, 0, 0)
        lay.setSpacing(10)

        self.icon_label     = QLabel()
        self.icon_label.setPixmap(icon.pixmap(QSize(20, 20)))
        self.icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        lay.addWidget(self.icon_label)

        self.title_label    = QLabel(title)
        self.title_label.setObjectName("TitleText")
        self.title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        lay.addWidget(self.title_label)

        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setObjectName("TitleSub")
        self.subtitle_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        lay.addWidget(self.subtitle_label)
        lay.addStretch(1)

        self.min_btn        = self._window_button("win-min", "Minimize", window.showMinimized)
        self.max_btn        = self._window_button("win-max", "Maximize", self.toggle_maximize)
        self.close_btn      = self._window_button("win-close", "Close", window.close)
        self.close_btn.setObjectName("WinClose")
        self.close_btn.installEventFilter(self)                                        # white glyph on the red hover background
        for b in (self.min_btn, self.max_btn, self.close_btn):
            lay.addWidget(b)

        window.installEventFilter(self)
        theme().changed.connect(lambda *_: self.sync_state())
        self.sync_state()

    def _window_button(self, icon_name: str, tip: str, slot) -> QToolButton:
        b                   = QToolButton()
        b.setObjectName("WinButton")
        b.setToolTip(tip)
        b.setFixedSize(46, TITLEBAR_HEIGHT)
        b.setIconSize(QSize(14, 14))
        b.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        b.clicked.connect(slot)
        set_icon(b, icon_name, "text")
        return b

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? Behaviour
    #?------------------------------------------------------------------------------------------------------------------------------------
    def toggle_maximize(self) -> None:
        w                   = self._window
        w.showNormal() if w.isMaximized() else w.showMaximized()

    def sync_state(self) -> None:
        maximized           = self._window.isMaximized()
        set_icon(self.max_btn, "win-restore" if maximized else "win-max", "text")
        self.max_btn.setToolTip("Restore down" if maximized else "Maximize")
        active              = self._window.isActiveWindow()
        for label in (self.title_label, self.subtitle_label, self.icon_label):
            label.setEnabled(active)                                                   # dims the title when the window is inactive

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:                        # noqa: N802
        etype               = event.type()
        if obj is self._window and etype in (QEvent.Type.WindowStateChange, QEvent.Type.ActivationChange):
            self.sync_state()
        elif obj is self.close_btn and etype == QEvent.Type.Enter:
            self.close_btn.setIcon(theme().icon("win-close", "#ffffff"))
        elif obj is self.close_btn and etype == QEvent.Type.Leave:
            set_icon(self.close_btn, "win-close", "text")
        return False

    def mousePressEvent(self, event) -> None:                                          # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self._window.windowHandle() is not None:
            self._window.windowHandle().startSystemMove()                              # native drag: snap, multi-monitor, restore-on-drag
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:                                    # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_maximize()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)
#?----------------------------------------------------------------------------------------------------------------------------------------
class FramelessResizer(QObject):
    """Lets a frameless window be resized from its edges by watching mouse moves on its QWindow."""

    EDGE_CURSORS            = {
        Qt.Edge.LeftEdge: Qt.CursorShape.SizeHorCursor,
        Qt.Edge.RightEdge: Qt.CursorShape.SizeHorCursor,
        Qt.Edge.TopEdge: Qt.CursorShape.SizeVerCursor,
        Qt.Edge.BottomEdge: Qt.CursorShape.SizeVerCursor,
        Qt.Edge.LeftEdge | Qt.Edge.TopEdge: Qt.CursorShape.SizeFDiagCursor,
        Qt.Edge.RightEdge | Qt.Edge.BottomEdge: Qt.CursorShape.SizeFDiagCursor,
        Qt.Edge.RightEdge | Qt.Edge.TopEdge: Qt.CursorShape.SizeBDiagCursor,
        Qt.Edge.LeftEdge | Qt.Edge.BottomEdge: Qt.CursorShape.SizeBDiagCursor,
    }

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self._window        = window
        self._override      = False
        window.winId()                                                                 # make sure the native QWindow exists
        window.windowHandle().installEventFilter(self)

    def _edges(self, pos: QPoint) -> Qt.Edge:
        w                   = self._window
        if w.isMaximized() or w.isFullScreen():
            return Qt.Edge(0)
        m, r                = RESIZE_MARGIN, w.rect()
        edges               = Qt.Edge(0)
        if pos.x() <= m:
            edges          |= Qt.Edge.LeftEdge
        elif pos.x() >= r.width() - m:
            edges          |= Qt.Edge.RightEdge
        if pos.y() <= m:
            edges          |= Qt.Edge.TopEdge
        elif pos.y() >= r.height() - m:
            edges          |= Qt.Edge.BottomEdge
        return edges

    def _set_cursor(self, edges: Qt.Edge) -> None:
        shape               = self.EDGE_CURSORS.get(edges)
        if shape is not None:
            if self._override:
                QApplication.changeOverrideCursor(shape)
            else:
                QApplication.setOverrideCursor(shape)
                self._override = True
        elif self._override:
            QApplication.restoreOverrideCursor()
            self._override  = False

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:                        # noqa: N802
        etype               = event.type()
        if etype == QEvent.Type.MouseMove and not event.buttons():
            self._set_cursor(self._edges(event.position().toPoint()))
        elif etype == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
            edges           = self._edges(event.position().toPoint())
            if edges:
                self._set_cursor(Qt.Edge(0))
                self._window.windowHandle().startSystemResize(edges)
                return True
        elif etype == QEvent.Type.Leave:
            self._set_cursor(Qt.Edge(0))
        return False
#?----------------------------------------------------------------------------------------------------------------------------------------
class WindowChrome:
    """Turns a top-level window frameless and restores native niceties where the OS allows it."""

    @staticmethod
    def make_frameless(window: QWidget) -> None:
        """Call before the window is shown."""
        window.setWindowFlags(window.windowFlags() | Qt.WindowType.FramelessWindowHint)
        window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

    @staticmethod
    def polish(window: QWidget) -> FramelessResizer:
        """Call once the window is shown: edge resizing plus Windows 11 corners / shadow / taskbar minimize."""
        resizer             = FramelessResizer(window)
        if sys.platform == "win32":
            WindowChrome._windows_polish(int(window.winId()))
        return resizer

    @staticmethod
    def _windows_polish(hwnd: int) -> None:
        try:
            import  ctypes
            from    ctypes                      import  wintypes

            dwm             = ctypes.windll.dwmapi
            user32          = ctypes.windll.user32

            class MARGINS(ctypes.Structure):
                _fields_    = [("left", ctypes.c_int), ("right", ctypes.c_int),
                               ("top", ctypes.c_int), ("bottom", ctypes.c_int)]

            corner          = ctypes.c_int(2)                                          # DWMWCP_ROUND (Windows 11; ignored on 10)
            dwm.DwmSetWindowAttribute(wintypes.HWND(hwnd), 33, ctypes.byref(corner), ctypes.sizeof(corner))
            dwm.DwmExtendFrameIntoClientArea(wintypes.HWND(hwnd), ctypes.byref(MARGINS(1, 1, 1, 1)))   # drop shadow

            GWL_STYLE, WS_MINIMIZEBOX, WS_SYSMENU = -16, 0x00020000, 0x00080000
            style           = user32.GetWindowLongW(wintypes.HWND(hwnd), GWL_STYLE)
            user32.SetWindowLongW(wintypes.HWND(hwnd), GWL_STYLE, style | WS_MINIMIZEBOX | WS_SYSMENU)  # taskbar click minimizes
        except Exception:
            pass
#?----------------------------------------------------------------------------------------------------------------------------------------
