#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?                     _     __           __
#?           _      __(_)___/ /___ ____  / /______
#?          | | /| / / / __  / __ `/ _ \/ __/ ___/
#?          | |/ |/ / / /_/ / /_/ /  __/ /_(__  )
#?          |__/|__/_/\__,_/\__, /\___/\__/____/
#?                         /____/
#?
#?
#? Name:        widgets.py
#? Purpose:     Reusable building blocks: responsive layouts, cards, validated inputs, console, toasts.
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     05/09/2019
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
from    __future__                  import  annotations

import  html
import  weakref
from    collections.abc             import  Callable
from    pathlib                     import  Path

from    PySide6.QtCore              import  QEasingCurve, QPoint, QPropertyAnimation, QRect, QRegularExpression, QSize, Qt, QTimer, Signal
from    PySide6.QtGui               import  QRegularExpressionValidator, QTextCursor
from    PySide6.QtWidgets           import  (QAbstractButton, QCheckBox, QComboBox, QFileDialog, QFrame, QGraphicsOpacityEffect, QGridLayout,
                                             QHBoxLayout, QLabel, QLayout, QLineEdit, QPlainTextEdit, QPushButton, QScrollArea, QSizePolicy,
                                             QToolButton, QVBoxLayout, QWidget, QWidgetItem)

from    flash.core.tools            import  parse_number
from    flash.ui.theme              import  theme
#?----------------------------------------------------------------------------------------------------------------------------------------
#? Theme-aware icons
#?----------------------------------------------------------------------------------------------------------------------------------------
_iconed: "weakref.WeakKeyDictionary[QAbstractButton, tuple[str, str]]" = weakref.WeakKeyDictionary()
#?----------------------------------------------------------------------------------------------------------------------------------------
def set_icon(button: QAbstractButton, name: str, role: str = "text") -> None:
    _iconed[button]         = (name, role)
    button.setIcon(theme().icon(name, role))
#?----------------------------------------------------------------------------------------------------------------------------------------
def _refresh_icons(_palette) -> None:
    for button, (name, role) in list(_iconed.items()):
        try:
            button.setIcon(theme().icon(name, role))
        except RuntimeError:                                                           # C++ object already deleted
            pass
#?----------------------------------------------------------------------------------------------------------------------------------------
theme().changed.connect(_refresh_icons)
#?----------------------------------------------------------------------------------------------------------------------------------------
def button(text: str, icon_name: str | None = None, kind: str = "", tip: str = "",
           slot: Callable | None = None) -> QPushButton:
    b                       = QPushButton(f" {text}" if icon_name and text else text)
    if kind:
        b.setProperty("kind", kind)
    if icon_name:
        set_icon(b, icon_name, {"primary": "on-accent", "danger": "danger"}.get(kind, "text"))
        b.setIconSize(QSize(16, 16))
    if tip:
        b.setToolTip(tip)
    if slot:
        b.clicked.connect(slot)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    return b
#?----------------------------------------------------------------------------------------------------------------------------------------
def icon_button(icon_name: str, tip: str, slot: Callable | None = None, checkable: bool = False,
                role: str = "text") -> QToolButton:
    b                       = QToolButton()
    b.setObjectName("Ghost")
    set_icon(b, icon_name, role)
    b.setIconSize(QSize(18, 18))
    b.setToolTip(tip)
    b.setCheckable(checkable)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    if slot:
        b.clicked.connect(slot)
    return b
#?----------------------------------------------------------------------------------------------------------------------------------------
def repolish(w: QWidget) -> None:
    w.style().unpolish(w)
    w.style().polish(w)
#?----------------------------------------------------------------------------------------------------------------------------------------
#? Layouts
#?----------------------------------------------------------------------------------------------------------------------------------------
class FlowLayout(QLayout):
    """Lays widgets out left-to-right and wraps to new lines when space runs out."""

    def __init__(self, parent: QWidget | None = None, spacing: int = 8) -> None:
        super().__init__(parent)
        self._items: list   = []
        self._spacing       = spacing
        self.setContentsMargins(0, 0, 0, 0)

    def addItem(self, item) -> None:                                                   # noqa: N802 (Qt API)
        self._items.append(item)

    def addWidget(self, w: QWidget) -> None:                                           # noqa: N802
        self.addChildWidget(w)
        self.addItem(QWidgetItem(w))

    def count(self) -> int:
        return len(self._items)

    def itemAt(self, i: int):                                                          # noqa: N802
        return self._items[i] if 0 <= i < len(self._items) else None

    def takeAt(self, i: int):                                                          # noqa: N802
        return self._items.pop(i) if 0 <= i < len(self._items) else None

    def expandingDirections(self):                                                     # noqa: N802
        return Qt.Orientation(0)

    def hasHeightForWidth(self) -> bool:                                               # noqa: N802
        return True

    def heightForWidth(self, width: int) -> int:                                       # noqa: N802
        return self._do_layout(QRect(0, 0, width, 0), test=True)

    def setGeometry(self, rect: QRect) -> None:                                        # noqa: N802
        super().setGeometry(rect)
        self._do_layout(rect, test=False)

    def sizeHint(self) -> QSize:                                                       # noqa: N802
        return self.minimumSize()

    def minimumSize(self) -> QSize:                                                    # noqa: N802
        size                = QSize()
        for item in self._items:
            size            = size.expandedTo(item.minimumSize())
        m                   = self.contentsMargins()
        return size + QSize(m.left() + m.right(), m.top() + m.bottom())

    def _do_layout(self, rect: QRect, test: bool) -> int:
        m                   = self.contentsMargins()
        r                   = rect.adjusted(m.left(), m.top(), -m.right(), -m.bottom())
        x, y, line_h        = r.x(), r.y(), 0
        for item in self._items:
            if item.widget() is not None and item.widget().isHidden():
                continue                                                               # explicitly hidden; NOT isVisible(), which is False on off-screen pages
            hint            = item.sizeHint()
            next_x          = x + hint.width() + self._spacing
            if next_x - self._spacing > r.right() + 1 and line_h > 0:
                x, y        = r.x(), y + line_h + self._spacing
                next_x      = x + hint.width() + self._spacing
                line_h      = 0
            if not test:
                item.setGeometry(QRect(QPoint(x, y), hint))
            x               = next_x
            line_h          = max(line_h, hint.height())
        return y + line_h - rect.y() + m.bottom()
#?----------------------------------------------------------------------------------------------------------------------------------------
class ResponsiveGrid(QWidget):
    """Arranges cards in 1..N columns depending on the available width."""

    def __init__(self, min_column_width: int = 440, max_columns: int = 3, parent=None) -> None:
        super().__init__(parent)
        self._grid          = QGridLayout(self)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setSpacing(16)
        self._cards: list[tuple[QWidget, int]] = []
        self._min_w         = min_column_width
        self._max_cols      = max_columns
        self._cols          = 0

    def add(self, card: QWidget, span: int = 1) -> QWidget:
        self._cards.append((card, span))
        self._relayout(force=True)
        return card

    def resizeEvent(self, event) -> None:                                              # noqa: N802
        super().resizeEvent(event)
        self._relayout()

    def _relayout(self, force: bool = False) -> None:
        width               = max(self.width(), 1)
        cols                = max(1, min(self._max_cols, width // self._min_w))
        if cols == self._cols and not force:
            return
        self._cols          = cols
        while self._grid.count():
            self._grid.takeAt(0)
        for c in range(self._max_cols):
            self._grid.setColumnStretch(c, 1 if c < cols else 0)
        row = col = 0
        for card, span in self._cards:
            span            = min(span, cols)
            if col + span > cols:
                row, col    = row + 1, 0
            self._grid.addWidget(card, row, col, 1, span, Qt.AlignmentFlag.AlignTop)
            col            += span
            if col >= cols:
                row, col    = row + 1, 0
        self._grid.setRowStretch(row + 1, 1)
#?----------------------------------------------------------------------------------------------------------------------------------------
class Card(QFrame):
    def __init__(self, title: str, subtitle: str = "", icon_name: str | None = None,
                 danger: bool = False, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        outer               = QVBoxLayout(self)
        outer.setContentsMargins(20, 18, 20, 20)
        outer.setSpacing(14)
        head                = QHBoxLayout()
        head.setSpacing(10)
        self._icon          = None
        self._danger_title  = None
        if icon_name:
            ico             = QLabel()
            self._icon      = (ico, icon_name, "danger" if danger else "accent")
            head.addWidget(ico, 0, Qt.AlignmentFlag.AlignTop)
        texts               = QVBoxLayout()
        texts.setSpacing(2)
        t                   = QLabel(title)
        t.setObjectName("CardTitle")
        if danger:
            self._danger_title = t
        texts.addWidget(t)
        self._paint_icon()
        theme().changed.connect(lambda *_: self._paint_icon())
        if subtitle:
            s               = QLabel(subtitle)
            s.setObjectName("CardSubtitle")
            s.setWordWrap(True)
            texts.addWidget(s)
        head.addLayout(texts, 1)
        self.header_actions = QHBoxLayout()
        self.header_actions.setSpacing(4)
        head.addLayout(self.header_actions)
        outer.addLayout(head)
        self.body           = QVBoxLayout()
        self.body.setSpacing(12)
        outer.addLayout(self.body)
        self._danger        = danger

    def _paint_icon(self) -> None:
        p                   = theme().palette
        if self._icon is not None:
            label, name, role = self._icon
            label.setPixmap(theme().icon(name, p.danger if role == "danger" else p.accent).pixmap(QSize(20, 20)))
        if self._danger_title is not None:
            self._danger_title.setStyleSheet(f"color: {p.danger};")

    def add(self, item) -> None:
        if isinstance(item, QLayout):
            self.body.addLayout(item)
        else:
            self.body.addWidget(item)
#?----------------------------------------------------------------------------------------------------------------------------------------
class Page(QScrollArea):
    """A scrollable page holding a responsive grid of cards."""

    title                   = ""
    subtitle                = ""
    icon_name               = "info"

    def __init__(self, ctx, parent=None) -> None:
        super().__init__(parent)
        self.ctx            = ctx
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        body                = QWidget()
        body.setObjectName("PageBody")
        self.layout_        = QVBoxLayout(body)
        self.layout_.setContentsMargins(24, 20, 24, 24)
        self.layout_.setSpacing(16)
        self.grid           = ResponsiveGrid()
        self.layout_.addWidget(self.grid)
        self.layout_.addStretch(1)
        self.setWidget(body)
        self._actions: list[QWidget] = []

    def resizeEvent(self, event) -> None:                                              # noqa: N802
        super().resizeEvent(event)
        m                   = 12 if self.width() < 720 else 24
        if self.layout_.contentsMargins().left() != m:
            self.layout_.setContentsMargins(m, m - 4, m, m)

    def device_actions(self, *widgets: QWidget) -> None:
        """Widgets disabled while a tool process is running."""
        self._actions.extend(widgets)

    def set_busy(self, busy: bool) -> None:
        for w in self._actions:
            w.setEnabled(not busy)
#?----------------------------------------------------------------------------------------------------------------------------------------
#? Inputs
#?----------------------------------------------------------------------------------------------------------------------------------------
def field(label: str, widget: QWidget, hint: str = "") -> QWidget:
    w                       = QWidget()
    lay                     = QVBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(4)
    lab                     = QLabel(label.upper())
    lab.setObjectName("FieldLabel")
    lay.addWidget(lab)
    lay.addWidget(widget)
    if hint:
        h                   = QLabel(hint)
        h.setObjectName("Hint")
        h.setWordWrap(True)
        lay.addWidget(h)
    return w
#?----------------------------------------------------------------------------------------------------------------------------------------
def row(*widgets: QWidget, stretch: list[int] | None = None) -> QHBoxLayout:
    lay                     = QHBoxLayout()
    lay.setSpacing(12)
    for i, w in enumerate(widgets):
        lay.addWidget(w, (stretch or [1] * len(widgets))[i])
    return lay
#?----------------------------------------------------------------------------------------------------------------------------------------
def flow(*widgets: QWidget) -> QWidget:
    holder                  = QWidget()
    fl                      = FlowLayout(holder)
    for w in widgets:
        fl.addWidget(w)
    return holder
#?----------------------------------------------------------------------------------------------------------------------------------------
def combo(items: list[str], editable: bool = False, current: str | None = None) -> QComboBox:
    c                       = QComboBox()
    c.addItems(items)
    c.setEditable(editable)
    if current is not None:
        idx                 = c.findText(current)
        if idx >= 0:
            c.setCurrentIndex(idx)
    c.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
    c.setMinimumContentsLength(6)
    return c
#?----------------------------------------------------------------------------------------------------------------------------------------
class NumberEdit(QLineEdit):
    """Address / size input: accepts hex (0x1000), decimal, or k/M suffixes. Highlights bad input."""

    def __init__(self, placeholder: str = "0x00000000", allow_all: bool = False, required: bool = True) -> None:
        super().__init__()
        self.setObjectName("Mono")
        self.setPlaceholderText(placeholder)
        self._allow_all     = allow_all
        self._required      = required
        pattern             = r"^\s*((0[xX][0-9a-fA-F]{0,8})|(\d{0,10}[kKmM]?)" + ("|[aA][lL]{0,2}" if allow_all else "") + r")\s*$"
        self.setValidator(QRegularExpressionValidator(QRegularExpression(pattern)))
        self.textChanged.connect(self._check)

    def _check(self) -> None:
        bad                 = bool(self.text().strip()) and not self.is_valid()
        if bool(self.property("invalid")) != bad:
            self.setProperty("invalid", bad)
            repolish(self)

    def is_valid(self) -> bool:
        t                   = self.text().strip()
        if not t:
            return not self._required
        if self._allow_all and t.upper() == "ALL":
            return True
        return parse_number(t) is not None

    def arg(self) -> str:
        t                   = self.text().strip()
        if self._allow_all and t.upper() == "ALL":
            return "ALL"
        value               = parse_number(t)
        return hex(value) if value is not None else t
#?----------------------------------------------------------------------------------------------------------------------------------------
class FileField(QWidget):
    """Path input with a browse button; accepts drag-and-drop of files."""

    changed                 = Signal(str)

    def __init__(self, placeholder: str = "Select a file…", filters: str = "Binary files (*.bin);;All files (*)",
                 save: bool = False, caption: str = "Select file") -> None:
        super().__init__()
        self._filters, self._save, self._caption = filters, save, caption
        lay                 = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        self.edit           = QLineEdit()
        self.edit.setPlaceholderText(placeholder)
        self.edit.setClearButtonEnabled(True)
        self.edit.textChanged.connect(self.changed)
        self.edit.textChanged.connect(self._check)
        lay.addWidget(self.edit, 1)
        self.browse         = icon_button("folder", "Browse…", self.pick)
        lay.addWidget(self.browse)
        self.setAcceptDrops(True)

    def _check(self) -> None:
        t                   = self.edit.text().strip()
        bad                 = bool(t) and not self._save and not Path(t).is_file()
        if bool(self.edit.property("invalid")) != bad:
            self.edit.setProperty("invalid", bad)
            repolish(self.edit)

    def pick(self) -> str:
        start               = self.text() or str(Path.home())
        if self._save:
            path, _         = QFileDialog.getSaveFileName(self, self._caption, start, self._filters)
        else:
            path, _         = QFileDialog.getOpenFileName(self, self._caption, start, self._filters)
        if path:
            self.edit.setText(path)
        return path

    def text(self) -> str:
        return self.edit.text().strip()

    def setText(self, text: str) -> None:                                              # noqa: N802
        self.edit.setText(text)

    def dragEnterEvent(self, e) -> None:                                               # noqa: N802
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e) -> None:                                                    # noqa: N802
        urls                = e.mimeData().urls()
        if urls:
            self.edit.setText(urls[0].toLocalFile())
#?----------------------------------------------------------------------------------------------------------------------------------------
def save_path(parent: QWidget, caption: str, filters: str, default_name: str = "") -> str:
    path, _                 = QFileDialog.getSaveFileName(parent, caption, str(Path.home() / default_name), filters)
    return path
#?----------------------------------------------------------------------------------------------------------------------------------------
#? Feedback
#?----------------------------------------------------------------------------------------------------------------------------------------
class StatusPill(QLabel):
    def __init__(self, text: str = "", state: str = "idle") -> None:
        super().__init__(text)
        self.setObjectName("Pill")
        self.set_state(text, state)

    def set_state(self, text: str, state: str) -> None:
        self.setText(text)
        if self.property("state") != state:
            self.setProperty("state", state)
            repolish(self)
#?----------------------------------------------------------------------------------------------------------------------------------------
class Toast(QLabel):
    """Transient notification shown in the bottom-right corner of its parent."""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setObjectName("Toast")
        self.setWordWrap(True)
        self.setMaximumWidth(420)
        self.hide()
        self._effect        = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._effect)
        self._anim          = QPropertyAnimation(self._effect, b"opacity", self)
        self._anim.setDuration(220)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._timer         = QTimer(self, singleShot=True)
        self._timer.timeout.connect(self._fade_out)
        self._hide_connected = False
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def show_message(self, text: str, kind: str = "info", ms: int = 3500) -> None:
        self.setText(text)
        self.setProperty("kind", kind)
        repolish(self)
        self.adjustSize()
        self._place()
        self.show()
        self.raise_()
        self._anim.stop()
        if self._hide_connected:
            self._anim.finished.disconnect(self.hide)
            self._hide_connected = False
        self._anim.setStartValue(self._effect.opacity() if self.isVisible() else 0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()
        self._timer.start(ms)

    def _place(self) -> None:
        p                   = self.parentWidget()
        if p is None:
            return
        margin              = 24
        self.move(p.width() - self.width() - margin, p.height() - self.height() - margin - 28)

    def _fade_out(self) -> None:
        self._anim.stop()
        self._anim.setStartValue(1.0)
        self._anim.setEndValue(0.0)
        if not self._hide_connected:
            self._anim.finished.connect(self.hide)
            self._hide_connected = True
        self._anim.start()
#?----------------------------------------------------------------------------------------------------------------------------------------
class Console(QPlainTextEdit):
    """Read-only log with colored lines; progress lines overwrite each other."""

    def __init__(self, object_name: str = "Console") -> None:
        super().__init__()
        self.setObjectName(object_name)
        self.setReadOnly(True)
        self.setMaximumBlockCount(20000)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.setUndoRedoEnabled(False)
        self._last_progress = False
        self.autoscroll     = True

    def _color(self, kind: str) -> str | None:
        p                   = theme().palette
        return {"error": p.danger, "warning": p.warning, "success": p.success, "command": p.accent,
                "muted": p.muted}.get(kind)

    def append_line(self, text: str, kind: str = "info", progress: bool = False) -> None:
        bar                 = self.verticalScrollBar()
        if progress and self._last_progress:
            cursor          = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock, QTextCursor.MoveMode.KeepAnchor)
            cursor.removeSelectedText()
            if self.document().blockCount() > 1:
                cursor.deletePreviousChar()                                            # drop the now-empty line itself
        color               = self._color(kind)
        safe                = html.escape(text) or "&nbsp;"
        if kind == "command":
            safe            = f"<b>{safe}</b>"
        self.appendHtml(f'<span style="color:{color}">{safe}</span>' if color else
                        f'<span style="white-space:pre-wrap">{safe}</span>')
        self._last_progress = progress
        if self.autoscroll:
            bar.setValue(bar.maximum())

    def clear(self) -> None:                                                           # noqa: D401
        super().clear()
        self._last_progress = False
#?----------------------------------------------------------------------------------------------------------------------------------------
