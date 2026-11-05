#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?                                    _ __
#?             ____ ___  ____  ____  (_) /_____  _____   ____  ____ _____ ____
#?            / __ `__ \/ __ \/ __ \/ / __/ __ \/ ___/  / __ \/ __ `/ __ `/ _ \
#?           / / / / / / /_/ / / / / / /_/ /_/ / /     / /_/ / /_/ / /_/ /  __/
#?          /_/ /_/ /_/\____/_/ /_/_/\__/\____/_/_____/ .___/\__,_/\__, /\___/
#?                                             /_____/_/          /____/
#?
#?
#? Name:        monitor_page.py
#? Purpose:     Serial monitor: watch the device's UART output and send commands.
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     05/09/2019
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
from    __future__                  import  annotations

import  codecs
from    datetime                    import  datetime
from    pathlib                     import  Path

from    PySide6.QtCore              import  QTimer
from    PySide6.QtWidgets           import  QCheckBox, QHBoxLayout, QLineEdit

from    flash.core.serial_monitor   import  SerialMonitor
from    flash.core.tools            import  classify_line, strip_ansi
from    flash.ui.widgets            import  Card, Console, Page, StatusPill, button, combo, flow, icon_button, save_path, set_icon
#?----------------------------------------------------------------------------------------------------------------------------------------
MONITOR_BAUDS               = ["115200", "74880", "9600", "19200", "38400", "57600", "230400", "460800", "921600"]
LINE_ENDINGS                = {"LF": b"\n", "CRLF": b"\r\n", "CR": b"\r", "None": b""}
#?----------------------------------------------------------------------------------------------------------------------------------------
class MonitorPage(Page):
    title                   = "Monitor"
    subtitle                = "Serial console for the connected board"
    icon_name               = "terminal"

    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        st                  = ctx.store
        self._mon: SerialMonitor | None = None
        self.port           = ""
        self._decoder       = codecs.getincrementaldecoder("utf-8")(errors="replace")
        self._partial       = ""
        self._flush_timer   = QTimer(self, singleShot=True, interval=120)
        self._flush_timer.timeout.connect(self._flush_partial)

        card                = Card("Serial monitor", "Uses the port selected at the top. Paused automatically while flashing.",
                                   "terminal")
        self.connect_btn    = button("Connect", "plug", "primary", slot=self.toggle)
        self.baud           = st.bind("monitor/baud", combo(MONITOR_BAUDS, editable=True, current="115200"))
        self.baud.setMinimumWidth(110)
        self.reset_btn      = button("Reset board", "power", tip="Pulse EN via RTS to restart the chip",
                                     slot=self.reset_board)
        self.ts             = st.bind("monitor/timestamps", QCheckBox("Timestamps"))
        self.pill           = StatusPill("Closed", "idle")
        self.clear_btn      = button("Clear", "trash", kind="ghost", slot=lambda: self.view.clear())
        self.save_btn       = button("Save", "save", kind="ghost", slot=self.save)
        card.add(flow(self.connect_btn, self.baud, self.reset_btn, self.ts, self.pill, self.clear_btn, self.save_btn))

        self.view           = Console("Monitor")
        self.view.setMinimumHeight(360)
        card.add(self.view)

        send_row            = QHBoxLayout()
        send_row.setSpacing(8)
        self.input          = QLineEdit()
        self.input.setObjectName("Mono")
        self.input.setPlaceholderText("Type a command and press Enter…")
        self.input.returnPressed.connect(self.send)
        self.ending         = st.bind("monitor/ending", combo(list(LINE_ENDINGS), current="LF"))
        self.send_btn       = icon_button("send", "Send", self.send, role="accent")
        send_row.addWidget(self.input, 1)
        send_row.addWidget(self.ending)
        send_row.addWidget(self.send_btn)
        card.add(send_row)
        self.grid.add(card, span=3)
        self._history: list[str] = []
        self._set_open_ui(False)

    def resizeEvent(self, e) -> None:                                                  # noqa: N802
        super().resizeEvent(e)
        self.view.setMinimumHeight(max(240, self.viewport().height() - 240))

    #?------------------------------------------------------------------------------------------------------------------------------------
    @property
    def is_open(self) -> bool:
        return self._mon is not None

    def toggle(self) -> None:
        if self.is_open:
            self.close_port()
        else:
            self.open_port()

    def open_port(self) -> None:
        if self.is_open:
            return
        if self.ctx.runner.busy:
            self.ctx.toast("Wait for the running operation to finish.", "warning")
            return
        port                = self.ctx.current_port()
        if not port:
            self.ctx.toast("No serial port selected.", "error")
            return
        try:
            baud            = int(self.baud.currentText())
        except ValueError:
            self.ctx.toast("Invalid baud rate.", "error")
            return
        self.port           = port
        self._decoder.reset()
        mon                 = SerialMonitor(port, baud, self)
        mon.data_received.connect(self._on_data)
        mon.error.connect(self._on_error)
        mon.opened.connect(lambda: self._set_open_ui(True))
        mon.closed.connect(self._on_closed)
        self._mon           = mon
        self.pill.set_state("Opening…", "busy")
        mon.start()

    def close_port(self) -> None:
        mon, self._mon      = self._mon, None
        if mon is not None:
            mon.stop()
            mon.deleteLater()
        self._flush_partial()
        self._set_open_ui(False)

    def _on_closed(self) -> None:
        mon                 = self.sender()
        if mon is not None and mon is self._mon:                                       # closed by itself (error / unplugged)
            self._mon       = None
            mon.wait(1000)
            mon.deleteLater()
        self._set_open_ui(self._mon is not None and self._mon.isRunning())

    def _set_open_ui(self, opened: bool) -> None:
        self.connect_btn.setText(" Disconnect" if opened else " Connect")
        set_icon(self.connect_btn, "unplug" if opened else "plug", "on-accent")
        self.pill.set_state(f"Open · {self.port}" if opened else "Closed", "ok" if opened else "idle")
        for w in (self.input, self.send_btn, self.reset_btn):
            w.setEnabled(opened)
        self.baud.setEnabled(not opened)

    def set_busy(self, busy: bool) -> None:
        self.connect_btn.setEnabled(not busy)

    #?------------------------------------------------------------------------------------------------------------------------------------
    def _on_data(self, data: bytes) -> None:
        text                = self._partial + self._decoder.decode(data)
        text                = text.replace("\r\n", "\n").replace("\r", "\n")
        *lines, self._partial = text.split("\n")
        for line in lines:
            self._emit(line)
        if self._partial:
            self._flush_timer.start()

    def _flush_partial(self) -> None:
        if self._partial:
            self._emit(self._partial)
            self._partial   = ""

    def _emit(self, line: str) -> None:
        line                = strip_ansi(line)
        if self.ts.isChecked():
            line            = f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {line}"
        kind                = classify_line(line)
        self.view.append_line(line, kind if kind in ("error", "warning") else "info")

    def _on_error(self, msg: str) -> None:
        self.view.append_line(msg, "error")
        self.ctx.toast(msg.splitlines()[0], "error", 5000)

    def send(self) -> None:
        text                = self.input.text()
        if not self._mon:
            return
        if self._mon.write(text.encode("utf-8") + LINE_ENDINGS.get(self.ending.currentText(), b"\n")):
            self.view.append_line(f"→ {text}", "command")
            self.input.clear()

    def reset_board(self) -> None:
        if self._mon:
            self._mon.reset_device()
            self.view.append_line("— board reset —", "muted")

    def save(self) -> None:
        path                = save_path(self, "Save monitor log", "Text files (*.txt);;All files (*)", "serial-log.txt")
        if path:
            Path(path).write_text(self.view.toPlainText(), encoding="utf-8")
            self.ctx.toast(f"Saved {Path(path).name}", "success")
#?----------------------------------------------------------------------------------------------------------------------------------------
