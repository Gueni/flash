"""Code editor for Arduino / C++ sketches.

Syntax highlighting, line numbers, current-line highlight, bracket matching, auto-indent, comment toggling,
word / keyword completion, compiler diagnostics (squiggles + gutter markers + tooltips) and a find / replace bar.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from PySide6.QtCore import QEvent, QRect, QRegularExpression, QSize, QStringListModel, Qt, QTimer, Signal
from PySide6.QtGui import (QColor, QFont, QKeySequence, QPainter, QShortcut, QSyntaxHighlighter, QTextCharFormat,
                           QTextCursor, QTextDocument, QTextFormat)
from PySide6.QtWidgets import (QCheckBox, QCompleter, QFrame, QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit,
                               QTextEdit, QToolTip, QWidget)

from flash.ui.theme import theme
from flash.ui.widgets import icon_button

# ----------------------------------------------------------------------------------------------
# Language data
# ----------------------------------------------------------------------------------------------

CPP_KEYWORDS = """alignas alignof and asm auto break case catch class const constexpr const_cast continue decltype default
delete do dynamic_cast else enum explicit export extern false for friend goto if inline mutable namespace new noexcept not
nullptr operator or override private protected public register reinterpret_cast return sizeof static static_assert
static_cast struct switch template this throw true try typedef typeid typename union using virtual volatile while final""".split()

CPP_TYPES = """void bool char short int long float double signed unsigned size_t int8_t int16_t int32_t int64_t uint8_t
uint16_t uint32_t uint64_t byte word boolean String array wchar_t char16_t char32_t""".split()

ARDUINO_API = """setup loop pinMode digitalWrite digitalRead analogRead analogWrite analogReference analogReadResolution
analogWriteResolution delay delayMicroseconds millis micros pulseIn pulseInLong shiftIn shiftOut tone noTone
attachInterrupt detachInterrupt digitalPinToInterrupt interrupts noInterrupts map constrain min max abs pow sqrt sq
sin cos tan random randomSeed bit bitRead bitWrite bitSet bitClear highByte lowByte isAlpha isDigit isSpace yield
Serial Serial1 Serial2 Wire SPI WiFi EEPROM Preferences SD SPIFFS LittleFS ESP ledcSetup ledcAttachPin ledcWrite
ledcAttach touchRead hallRead xTaskCreate xTaskCreatePinnedToCore vTaskDelay begin end print println printf write read
available peek flush setTimeout readString readStringUntil parseInt parseFloat""".split()

ARDUINO_CONSTANTS = """HIGH LOW INPUT OUTPUT INPUT_PULLUP INPUT_PULLDOWN LED_BUILTIN A0 A1 A2 A3 A4 A5 A6 A7 RISING FALLING
CHANGE DEC HEX OCT BIN PI HALF_PI TWO_PI DEG_TO_RAD RAD_TO_DEG LSBFIRST MSBFIRST NULL F WIFI_STA WIFI_AP
WL_CONNECTED""".split()

COMPLETION_WORDS = sorted(set(CPP_KEYWORDS + CPP_TYPES + ARDUINO_API + ARDUINO_CONSTANTS +
                              ["#include", "#define", "#ifdef", "#ifndef", "#endif", "#if", "#else", "#pragma"]),
                          key=str.lower)

SYNTAX = {
    "dark": {"keyword": "#c792ea", "type": "#82aaff", "api": "#4fc1ff", "const": "#f78c6c", "number": "#f78c6c",
             "string": "#c3e88d", "comment": "#6b7489", "preproc": "#ff9cac", "function": "#ffcb6b",
             "gutter": "#5b6375", "gutter_active": "#cdd3de", "line": "#1a1f29", "match": "#3a4a6b",
             "search": "#5a4a1f", "error": "#f05252", "warning": "#f5a524"},
    "light": {"keyword": "#7c3aed", "type": "#1d4ed8", "api": "#0e7490", "const": "#c2410c", "number": "#c2410c",
              "string": "#15803d", "comment": "#8a93a6", "preproc": "#be185d", "function": "#a16207",
              "gutter": "#a0a8b8", "gutter_active": "#3b4252", "line": "#f2f5fa", "match": "#d6e4ff",
              "search": "#fde68a", "error": "#dc2626", "warning": "#b45309"},
}


def syntax_colors() -> dict[str, str]:
    return SYNTAX["dark" if theme().palette.name == "dark" else "light"]


# ----------------------------------------------------------------------------------------------
# Highlighter
# ----------------------------------------------------------------------------------------------

class CppHighlighter(QSyntaxHighlighter):
    def __init__(self, document: QTextDocument) -> None:
        super().__init__(document)
        self.rules: list[tuple[QRegularExpression, QTextCharFormat]] = []
        self.comment_fmt = QTextCharFormat()
        self.build()

    @staticmethod
    def _fmt(color: str, bold: bool = False, italic: bool = False) -> QTextCharFormat:
        f = QTextCharFormat()
        f.setForeground(QColor(color))
        if bold:
            f.setFontWeight(QFont.Weight.DemiBold)
        if italic:
            f.setFontItalic(True)
        return f

    def build(self) -> None:
        c = syntax_colors()
        words = lambda ws: QRegularExpression(r"\b(" + "|".join(map(re.escape, ws)) + r")\b")
        self.rules = [
            (QRegularExpression(r"\b[A-Za-z_]\w*(?=\s*\()"), self._fmt(c["function"])),
            (words(ARDUINO_API), self._fmt(c["api"])),
            (words(CPP_TYPES), self._fmt(c["type"])),
            (words(CPP_KEYWORDS), self._fmt(c["keyword"], bold=True)),
            (words(ARDUINO_CONSTANTS), self._fmt(c["const"])),
            (QRegularExpression(r"\b(0[xX][0-9A-Fa-f']+|0[bB][01']+|\d[\d']*\.?\d*([eE][-+]?\d+)?)[uUlLfF]*\b"),
             self._fmt(c["number"])),
            (QRegularExpression(r"^\s*#\s*\w+"), self._fmt(c["preproc"])),
            (QRegularExpression(r"<[\w./-]+\.h(pp)?>"), self._fmt(c["string"])),
            (QRegularExpression(r"\"(\\.|[^\"\\])*\""), self._fmt(c["string"])),
            (QRegularExpression(r"'(\\.|[^'\\])+'"), self._fmt(c["string"])),
        ]
        self.comment_fmt = self._fmt(c["comment"], italic=True)
        self.rehighlight()

    def highlightBlock(self, text: str) -> None:  # noqa: N802
        for rx, fmt in self.rules:
            it = rx.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)
        self._comments(text)

    def _comments(self, text: str) -> None:
        """Line comments and /* block */ comments spanning lines (state 1 = inside a block comment)."""
        self.setCurrentBlockState(0)
        i, n = 0, len(text)
        in_block = self.previousBlockState() == 1
        start = 0
        in_str: str | None = None
        while i < n:
            ch = text[i]
            if in_block:
                end = text.find("*/", i)
                if end < 0:
                    self.setFormat(start, n - start, self.comment_fmt)
                    self.setCurrentBlockState(1)
                    return
                self.setFormat(start, end + 2 - start, self.comment_fmt)
                i, in_block = end + 2, False
                continue
            if in_str:
                if ch == "\\":
                    i += 2
                    continue
                if ch == in_str:
                    in_str = None
            elif ch in "\"'":
                in_str = ch
            elif text.startswith("//", i):
                self.setFormat(i, n - i, self.comment_fmt)
                return
            elif text.startswith("/*", i):
                in_block, start = True, i
                i += 2
                continue
            i += 1


# ----------------------------------------------------------------------------------------------
# Editor
# ----------------------------------------------------------------------------------------------

@dataclass
class Marker:
    line: int            # 1-based
    col: int             # 1-based
    severity: str        # error / warning / note
    message: str


class LineNumberArea(QWidget):
    def __init__(self, editor: "CodeEditor") -> None:
        super().__init__(editor)
        self.editor = editor
        self.setMouseTracking(True)

    def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(self.editor.gutter_width(), 0)

    def paintEvent(self, event) -> None:  # noqa: N802
        self.editor.paint_gutter(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        block = self.editor.cursorForPosition(event.position().toPoint()).block()
        msgs = [m for m in self.editor.markers if m.line == block.blockNumber() + 1]
        if msgs:
            QToolTip.showText(event.globalPosition().toPoint(), "\n".join(f"{m.severity}: {m.message}" for m in msgs), self)
        else:
            QToolTip.hideText()


class CodeEditor(QPlainTextEdit):
    cursor_moved = Signal(int, int)       # line, column (1-based)
    modified = Signal(bool)

    PAIRS = {"(": ")", "[": "]", "{": "}", '"': '"', "'": "'"}
    INDENT = "  "                           # Arduino style: two spaces

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("CodeEditor")
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setTabChangesFocus(False)
        self.markers: list[Marker] = []
        self._search_hits: list[QTextEdit.ExtraSelection] = []
        self._font_size = 10.5
        self._apply_font()
        self.gutter = LineNumberArea(self)
        self.highlighter = CppHighlighter(self.document())
        self.blockCountChanged.connect(lambda _: self._update_gutter_width())
        self.updateRequest.connect(self._update_gutter)
        self.cursorPositionChanged.connect(self._on_cursor)
        self.document().modificationChanged.connect(self.modified)
        self._update_gutter_width()

        self.completer = QCompleter(self)
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchStartsWith)
        self.completer.setModel(QStringListModel(COMPLETION_WORDS, self.completer))
        self.completer.activated.connect(self._insert_completion)
        self._words_timer = QTimer(self, singleShot=True, interval=1200)
        self._words_timer.timeout.connect(self._refresh_words)
        self.textChanged.connect(self._words_timer.start)

        theme().changed.connect(lambda *_: self.restyle())
        self.restyle()

    # ------------------------------------------------------------------ look
    def _apply_font(self) -> None:
        font = QFont(theme().mono)
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setPointSizeF(self._font_size)
        self.setFont(font)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(" ") * 2)

    def zoom(self, step: float) -> None:
        self._font_size = max(7.0, min(28.0, self._font_size + step))
        self._apply_font()
        self._update_gutter_width()

    def restyle(self) -> None:
        self._apply_font()
        self.highlighter.build()
        self._highlight_extras()
        self.gutter.update()

    # ---------------------------------------------------------------- gutter
    def gutter_width(self) -> int:
        digits = max(3, len(str(self.blockCount())))
        return 18 + self.fontMetrics().horizontalAdvance("9") * digits + 10

    def _update_gutter_width(self) -> None:
        self.setViewportMargins(self.gutter_width(), 0, 0, 0)

    def _update_gutter(self, rect: QRect, dy: int) -> None:
        if dy:
            self.gutter.scroll(0, dy)
        else:
            self.gutter.update(0, rect.y(), self.gutter.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self._update_gutter_width()

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.gutter.setGeometry(QRect(cr.left(), cr.top(), self.gutter_width(), cr.height()))

    def paint_gutter(self, event) -> None:
        c = syntax_colors()
        p = theme().palette
        painter = QPainter(self.gutter)
        painter.fillRect(event.rect(), QColor(p.console_bg if p.name == "dark" else p.surface))
        block = self.firstVisibleBlock()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        current = self.textCursor().blockNumber()
        by_line: dict[int, str] = {}
        for m in self.markers:
            if by_line.get(m.line) != "error":
                by_line[m.line] = m.severity
        h = self.fontMetrics().height()
        while block.isValid() and top <= event.rect().bottom():
            bottom = top + round(self.blockBoundingRect(block).height())
            if block.isVisible() and bottom >= event.rect().top():
                n = block.blockNumber()
                painter.setPen(QColor(c["gutter_active"] if n == current else c["gutter"]))
                painter.setFont(self.font())
                painter.drawText(0, top, self.gutter.width() - 10, h, Qt.AlignmentFlag.AlignRight, str(n + 1))
                sev = by_line.get(n + 1)
                if sev:
                    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                    painter.setBrush(QColor(c["error"] if sev == "error" else c["warning"]))
                    painter.setPen(Qt.PenStyle.NoPen)
                    d = max(6, h // 2)
                    painter.drawEllipse(5, top + (h - d) // 2, d, d)
            block = block.next()
            top = bottom

    # ------------------------------------------------------------ highlights
    def _on_cursor(self) -> None:
        cur = self.textCursor()
        self.cursor_moved.emit(cur.blockNumber() + 1, cur.positionInBlock() + 1)
        self._highlight_extras()
        self.gutter.update()

    def _highlight_extras(self) -> None:
        c = syntax_colors()
        extras: list[QTextEdit.ExtraSelection] = []
        line = QTextEdit.ExtraSelection()
        line.format.setBackground(QColor(c["line"]))
        line.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
        line.cursor = self.textCursor()
        line.cursor.clearSelection()
        extras.append(line)
        extras += self._search_hits
        extras += self._bracket_match(c)
        for m in self.markers:
            block = self.document().findBlockByNumber(m.line - 1)
            if not block.isValid():
                continue
            sel = QTextEdit.ExtraSelection()
            sel.format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.WaveUnderline)
            sel.format.setUnderlineColor(QColor(c["error"] if m.severity == "error" else c["warning"]))
            sel.format.setToolTip(m.message)
            cur = QTextCursor(block)
            text = block.text()
            start = min(max(m.col - 1, len(text) - len(text.lstrip())), max(len(text) - 1, 0))
            cur.setPosition(block.position() + start)
            cur.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
            sel.cursor = cur
            extras.append(sel)
        self.setExtraSelections(extras)

    def _bracket_match(self, c) -> list[QTextEdit.ExtraSelection]:
        doc = self.document()
        pos = self.textCursor().position()
        pairs = {"(": ")", "[": "]", "{": "}"}
        rev = {v: k for k, v in pairs.items()}
        for p in (pos - 1, pos):
            ch = doc.characterAt(p)
            if ch in pairs or ch in rev:
                forward = ch in pairs
                other = pairs.get(ch) or rev.get(ch)
                depth, q = 0, p
                limit = 20000
                while 0 <= q < doc.characterCount() and limit:
                    x = doc.characterAt(q)
                    if x == ch:
                        depth += 1
                    elif x == other:
                        depth -= 1
                        if depth == 0:
                            out = []
                            for at in (p, q):
                                s = QTextEdit.ExtraSelection()
                                s.format.setBackground(QColor(c["match"]))
                                cur = QTextCursor(doc)
                                cur.setPosition(at)
                                cur.movePosition(QTextCursor.MoveOperation.NextCharacter, QTextCursor.MoveMode.KeepAnchor)
                                s.cursor = cur
                                out.append(s)
                            return out
                    q += 1 if forward else -1
                    limit -= 1
                return []
        return []

    def set_markers(self, markers: list[Marker]) -> None:
        self.markers = markers
        self._highlight_extras()
        self.gutter.update()

    def set_search_hits(self, cursors: list[QTextCursor]) -> None:
        c = syntax_colors()
        self._search_hits = []
        for cur in cursors[:2000]:
            s = QTextEdit.ExtraSelection()
            s.format.setBackground(QColor(c["search"]))
            s.cursor = cur
            self._search_hits.append(s)
        self._highlight_extras()

    def event(self, e) -> bool:
        if e.type() == QEvent.Type.ToolTip:
            cur = self.cursorForPosition(e.pos())
            msgs = [m for m in self.markers if m.line == cur.blockNumber() + 1]
            if msgs:
                QToolTip.showText(e.globalPos(), "\n".join(f"{m.severity}: {m.message}" for m in msgs), self)
            else:
                QToolTip.hideText()
            return True
        return super().event(e)

    # --------------------------------------------------------------- editing
    def goto(self, line: int, col: int = 1) -> None:
        block = self.document().findBlockByNumber(max(0, line - 1))
        cur = QTextCursor(block)
        cur.setPosition(block.position() + min(max(col - 1, 0), len(block.text())))
        self.setTextCursor(cur)
        self.centerCursor()
        self.setFocus()

    def toggle_comment(self) -> None:
        cur = self.textCursor()
        start, end = sorted((cur.selectionStart(), cur.selectionEnd()))
        doc = self.document()
        first = doc.findBlock(start).blockNumber()
        last_block = doc.findBlock(end)
        if end > start and end == last_block.position():
            last_block = last_block.previous()
        last = last_block.blockNumber()
        blocks = [doc.findBlockByNumber(n) for n in range(first, last + 1)]
        code = [b for b in blocks if b.text().strip()]
        uncomment = bool(code) and all(b.text().lstrip().startswith("//") for b in code)
        indent = min((len(b.text()) - len(b.text().lstrip()) for b in code), default=0)
        edit = QTextCursor(doc)
        edit.beginEditBlock()
        for b in blocks:
            text = b.text()
            if not text.strip():
                continue
            c = QTextCursor(b)
            if uncomment:
                i = text.index("//")
                n = 3 if text[i:i + 3] == "// " else 2
                c.setPosition(b.position() + i)
                c.setPosition(b.position() + i + n, QTextCursor.MoveMode.KeepAnchor)
                c.removeSelectedText()
            else:
                c.setPosition(b.position() + indent)
                c.insertText("// ")
        edit.endEditBlock()

    def _indent_lines(self, unindent: bool) -> None:
        cur = self.textCursor()
        doc = self.document()
        first = doc.findBlock(cur.selectionStart()).blockNumber()
        last_block = doc.findBlock(cur.selectionEnd())
        if cur.selectionEnd() > cur.selectionStart() and cur.selectionEnd() == last_block.position():
            last_block = last_block.previous()
        edit = QTextCursor(doc)
        edit.beginEditBlock()
        for n in range(first, last_block.blockNumber() + 1):
            b = doc.findBlockByNumber(n)
            c = QTextCursor(b)
            if unindent:
                lead = len(b.text()) - len(b.text().lstrip(" "))
                c.setPosition(b.position() + min(lead, len(self.INDENT)), QTextCursor.MoveMode.KeepAnchor)
                c.removeSelectedText()
            else:
                c.insertText(self.INDENT)
        edit.endEditBlock()

    def _current_word(self) -> str:
        cur = self.textCursor()
        text = cur.block().text()[:cur.positionInBlock()]
        m = re.search(r"[#A-Za-z_][\w]*$", text)
        return m.group(0) if m else ""

    def _refresh_words(self) -> None:
        words = set(re.findall(r"\b[A-Za-z_]\w{3,}\b", self.toPlainText()))
        self.completer.model().setStringList(sorted(set(COMPLETION_WORDS) | words, key=str.lower))

    def _insert_completion(self, word: str) -> None:
        prefix = self.completer.completionPrefix()
        cur = self.textCursor()
        cur.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor, len(prefix))
        cur.insertText(word)
        self.setTextCursor(cur)

    def show_completions(self, force: bool = False) -> None:
        prefix = self._current_word()
        if not force and len(prefix) < 3:
            self.completer.popup().hide()
            return
        self.completer.setCompletionPrefix(prefix)
        popup = self.completer.popup()
        if self.completer.completionCount() == 0 or (self.completer.completionCount() == 1 and
                                                     self.completer.currentCompletion() == prefix):
            popup.hide()
            return
        popup.setCurrentIndex(self.completer.completionModel().index(0, 0))
        rect = self.cursorRect()
        rect.setWidth(popup.sizeHintForColumn(0) + popup.verticalScrollBar().sizeHint().width() + 24)
        self.completer.complete(rect)

    def keyPressEvent(self, e) -> None:  # noqa: N802
        popup = self.completer.popup()
        if popup.isVisible() and e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Tab,
                                             Qt.Key.Key_Escape, Qt.Key.Key_Backtab):
            e.ignore()                       # let the completer handle it
            return
        key, mods, text = e.key(), e.modifiers(), e.text()
        ctrl = bool(mods & Qt.KeyboardModifier.ControlModifier)

        if ctrl and key == Qt.Key.Key_Space:
            self.show_completions(force=True)
            return
        if key == Qt.Key.Key_Tab and not ctrl:
            if self.textCursor().hasSelection():
                self._indent_lines(False)
            else:
                self.insertPlainText(self.INDENT)
            return
        if key == Qt.Key.Key_Backtab:
            self._indent_lines(True)
            return
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and not ctrl:
            self._newline()
            return
        cur = self.textCursor()
        if text in self.PAIRS and not cur.hasSelection():
            nxt = self.document().characterAt(cur.position())
            if text in "\"'" and nxt == text:
                cur.movePosition(QTextCursor.MoveOperation.Right)
                self.setTextCursor(cur)
                return
            if text in "([{" or (text in "\"'" and (nxt.isspace() or nxt in ")]};,\u2029" or not nxt)):
                cur.insertText(text + self.PAIRS[text])
                cur.movePosition(QTextCursor.MoveOperation.Left)
                self.setTextCursor(cur)
                return
        if text in ")]}" and self.document().characterAt(cur.position()) == text:
            cur.movePosition(QTextCursor.MoveOperation.Right)
            self.setTextCursor(cur)
            return
        if key == Qt.Key.Key_Backspace and not cur.hasSelection():
            before = self.document().characterAt(cur.position() - 1)
            after = self.document().characterAt(cur.position())
            if self.PAIRS.get(before) == after and before:
                cur.deleteChar()
        if text == "}" :
            block_text = cur.block().text()
            if not block_text.strip() and block_text.endswith(self.INDENT):
                cur.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor, len(self.INDENT))
                cur.removeSelectedText()
        super().keyPressEvent(e)
        if text and (text.isalnum() or text in "_#"):
            self.show_completions()
        elif popup.isVisible():
            popup.hide()

    def _newline(self) -> None:
        cur = self.textCursor()
        line = cur.block().text()
        before = line[:cur.positionInBlock()]
        indent = before[:len(before) - len(before.lstrip())]
        stripped = before.rstrip()
        after_char = self.document().characterAt(cur.position())
        cur.beginEditBlock()
        if stripped.endswith("{") and after_char == "}":
            cur.insertText("\n" + indent + self.INDENT + "\n" + indent)
            cur.movePosition(QTextCursor.MoveOperation.Up)
            cur.movePosition(QTextCursor.MoveOperation.EndOfBlock)
        elif stripped.endswith(("{", "(", "[")) or re.match(r"^\s*(case .*|default\s*):\s*$", stripped):
            cur.insertText("\n" + indent + self.INDENT)
        else:
            cur.insertText("\n" + indent)
        cur.endEditBlock()
        self.setTextCursor(cur)
        self.ensureCursorVisible()

    def wheelEvent(self, e) -> None:  # noqa: N802
        if e.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.zoom(1 if e.angleDelta().y() > 0 else -1)
            return
        super().wheelEvent(e)


# ----------------------------------------------------------------------------------------------
# Find / replace bar
# ----------------------------------------------------------------------------------------------

class _EscLineEdit(QLineEdit):
    escaped = Signal()

    def event(self, e) -> bool:
        if e.type() == QEvent.Type.ShortcutOverride and e.key() == Qt.Key.Key_Escape:
            e.accept()                       # beat the window-wide Esc (= stop) shortcut
            return True
        return super().event(e)

    def keyPressEvent(self, e) -> None:  # noqa: N802
        if e.key() == Qt.Key.Key_Escape:
            self.escaped.emit()
            return
        super().keyPressEvent(e)


class FindBar(QFrame):
    def __init__(self, editor_getter, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("FindBar")
        self._editor = editor_getter
        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 6, 10, 6)
        lay.setSpacing(6)
        self.find = _EscLineEdit()
        self.find.setPlaceholderText("Find")
        self.find.setClearButtonEnabled(True)
        self.replace = _EscLineEdit()
        self.replace.setPlaceholderText("Replace")
        self.case = QCheckBox("Aa")
        self.case.setToolTip("Match case")
        self.word = QCheckBox("Word")
        self.word.setToolTip("Whole word")
        self.count = QLabel("")
        self.count.setObjectName("Hint")
        lay.addWidget(self.find, 2)
        lay.addWidget(icon_button("chevron-up", "Previous (Shift+F3)", lambda: self.next(back=True)))
        lay.addWidget(icon_button("chevron-down", "Next (F3)", self.next))
        lay.addWidget(self.case)
        lay.addWidget(self.word)
        lay.addWidget(self.count)
        lay.addWidget(self.replace, 2)
        self.rep_btn = icon_button("check", "Replace", self.replace_one)
        self.rep_all_btn = icon_button("layers", "Replace all", self.replace_all)
        lay.addWidget(self.rep_btn)
        lay.addWidget(self.rep_all_btn)
        lay.addWidget(icon_button("x", "Close (Esc)", self.close_bar))
        for w in (self.find, self.replace):
            w.escaped.connect(self.close_bar)
        self.find.returnPressed.connect(self.next)
        self.replace.returnPressed.connect(self.replace_one)
        self.find.textChanged.connect(self.refresh)
        self.case.toggled.connect(self.refresh)
        self.word.toggled.connect(self.refresh)
        self.hide()

    def _flags(self, back: bool = False) -> QTextDocument.FindFlag:
        f = QTextDocument.FindFlag(0)
        if self.case.isChecked():
            f |= QTextDocument.FindFlag.FindCaseSensitively
        if self.word.isChecked():
            f |= QTextDocument.FindFlag.FindWholeWords
        if back:
            f |= QTextDocument.FindFlag.FindBackward
        return f

    def open_bar(self, replace: bool) -> None:
        ed = self._editor()
        self.replace.setVisible(replace)
        self.rep_btn.setVisible(replace)
        self.rep_all_btn.setVisible(replace)
        self.show()
        if ed is not None and ed.textCursor().hasSelection() and "\u2029" not in ed.textCursor().selectedText():
            self.find.setText(ed.textCursor().selectedText())
        self.find.setFocus()
        self.find.selectAll()
        self.refresh()

    def close_bar(self) -> None:
        self.hide()
        ed = self._editor()
        if ed is not None:
            ed.set_search_hits([])
            ed.setFocus()

    def refresh(self) -> None:
        ed = self._editor()
        if ed is None:
            return
        needle = self.find.text()
        hits = []
        if needle and self.isVisible():
            cur = QTextCursor(ed.document())
            while True:
                cur = ed.document().find(needle, cur, self._flags())
                if cur.isNull():
                    break
                hits.append(QTextCursor(cur))
                if len(hits) > 5000:
                    break
        ed.set_search_hits(hits)
        self.count.setText(f"{len(hits)} found" if needle else "")

    def next(self, back: bool = False) -> None:
        ed = self._editor()
        if ed is None or not self.find.text():
            return
        if not ed.find(self.find.text(), self._flags(back)):
            cur = ed.textCursor()
            cur.movePosition(QTextCursor.MoveOperation.End if back else QTextCursor.MoveOperation.Start)
            ed.setTextCursor(cur)
            ed.find(self.find.text(), self._flags(back))

    def replace_one(self) -> None:
        ed = self._editor()
        if ed is None or not self.find.text():
            return
        cur = ed.textCursor()
        sel = cur.selectedText()
        same = sel == self.find.text() if self.case.isChecked() else sel.lower() == self.find.text().lower()
        if cur.hasSelection() and same:
            cur.insertText(self.replace.text())
        self.next()
        self.refresh()

    def replace_all(self) -> None:
        ed = self._editor()
        if ed is None or not self.find.text():
            return
        cur = QTextCursor(ed.document())
        cur.beginEditBlock()
        n = 0
        find = QTextCursor(ed.document())
        while True:
            find = ed.document().find(self.find.text(), find, self._flags())
            if find.isNull():
                break
            find.insertText(self.replace.text())
            n += 1
        cur.endEditBlock()
        self.refresh()
        self.count.setText(f"{n} replaced")
