#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?                             _       __                           _ __
#?             ________  _____(_)___ _/ /    ____ ___  ____  ____  (_) /_____  _____
#?            / ___/ _ \/ ___/ / __ `/ /    / __ `__ \/ __ \/ __ \/ / __/ __ \/ ___/
#?           (__  )  __/ /  / / /_/ / /    / / / / / / /_/ / / / / / /_/ /_/ / /
#?          /____/\___/_/  /_/\__,_/_/____/_/ /_/ /_/\____/_/ /_/_/\__/\____/_/
#?                                  /_____/
#?
#?
#? Name:        serial_monitor.py
#? Purpose:     Serial port enumeration and a background serial reader for the monitor page.
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     05/09/2019
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
from    __future__                  import  annotations

import  threading
from    dataclasses                 import  dataclass

import  serial
import  serial.tools.list_ports
from    PySide6.QtCore              import  QThread, Signal
#?----------------------------------------------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class PortInfo:
    device: str
    description: str

    @property
    def label(self) -> str:
        desc                = self.description
        if not desc or desc == "n/a" or desc == self.device:
            return self.device
        return f"{self.device}  ·  {desc}"
#?----------------------------------------------------------------------------------------------------------------------------------------
def list_ports() -> list[PortInfo]:
    ports                   = []
    for p in serial.tools.list_ports.comports():
        ports.append(PortInfo(p.device, (p.description or "").strip()))

    def key(p: PortInfo):
        digits              = "".join(ch for ch in p.device if ch.isdigit())
        return (p.device.rstrip("0123456789"), int(digits) if digits else 0)

    return sorted(ports, key=key)
#?----------------------------------------------------------------------------------------------------------------------------------------
class SerialMonitor(QThread):
    """Reads a serial port on a background thread; writes happen on the caller's thread."""

    data_received           = Signal(bytes)
    error                   = Signal(str)
    opened                  = Signal()
    closed                  = Signal()

    def __init__(self, port: str, baud: int, parent=None) -> None:
        super().__init__(parent)
        self.port           = port
        self.baud           = baud
        self._serial: serial.Serial | None = None
        self._lock          = threading.Lock()
        self._running       = False

    def run(self) -> None:
        try:
            ser             = serial.Serial()
            ser.port        = self.port
            ser.baudrate    = self.baud
            ser.timeout     = 0.05
            # Keep the chip running: do not hold it in reset/bootloader when opening.
            ser.dtr         = False
            ser.rts         = False
            ser.open()
        except (serial.SerialException, OSError, ValueError) as exc:
            self.error.emit(_friendly_error(exc))
            self.closed.emit()
            return
        with self._lock:
            self._serial    = ser
        self._running       = True
        self.opened.emit()
        try:
            while self._running:
                try:
                    chunk   = ser.read(ser.in_waiting or 1)
                except (serial.SerialException, OSError) as exc:
                    if self._running:
                        self.error.emit(_friendly_error(exc))
                    break
                if chunk:
                    self.data_received.emit(bytes(chunk))
        finally:
            with self._lock:
                self._serial = None
            try:
                ser.close()
            except Exception:
                pass
            self._running   = False
            self.closed.emit()

    def stop(self) -> None:
        self._running       = False
        self.wait(1500)

    def write(self, data: bytes) -> bool:
        with self._lock:
            if self._serial is None:
                return False
            try:
                self._serial.write(data)
                return True
            except (serial.SerialException, OSError) as exc:
                self.error.emit(_friendly_error(exc))
                return False

    def reset_device(self) -> None:
        """Pulse EN via RTS (the usual auto-reset wiring on ESP dev boards)."""
        with self._lock:
            if self._serial is None:
                return
            self._serial.dtr = False
            self._serial.rts = True
        self.msleep(120)
        with self._lock:
            if self._serial is not None:
                self._serial.rts = False
#?----------------------------------------------------------------------------------------------------------------------------------------
def _friendly_error(exc: Exception) -> str:
    text                    = str(exc)
    low                     = text.lower()
    if "permission" in low or "access is denied" in low or "errno 13" in low:
        import  sys
        if sys.platform.startswith("linux"):
            return (f"{text}\nOn Linux add yourself to the serial group: "
                    "sudo usermod -aG dialout $USER (then log out and back in).")
        return f"{text}\nThe port is busy - close other programs (or Flash operations) using it."
    return text
#?----------------------------------------------------------------------------------------------------------------------------------------
