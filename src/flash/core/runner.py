#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?             _______  ______  ____  ___  _____
#?            / ___/ / / / __ \/ __ \/ _ \/ ___/
#?           / /  / /_/ / / / / / / /  __/ /
#?          /_/   \__,_/_/ /_/_/ /_/\___/_/
#?
#?
#? Name:        runner.py
#? Purpose:     Run one esptool-family command at a time in a QProcess and stream its output.
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     05/09/2019
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
from    __future__                  import  annotations

import  time
from    collections.abc             import  Callable
from    dataclasses                 import  dataclass

from    PySide6.QtCore              import  QObject, QProcess, QProcessEnvironment, Signal

from    flash.core.tools            import  LineSplitter, parse_progress, quote_command, tool_environment, tool_invocation
#?----------------------------------------------------------------------------------------------------------------------------------------
@dataclass
class Job:
    tool: str
    args: list[str]
    title: str
    on_done: Callable[[int], None] | None = None
    started_at: float       = 0.0
#?----------------------------------------------------------------------------------------------------------------------------------------
class ToolRunner(QObject):
    """Owns a single QProcess. Emits parsed output lines and progress."""

    line                    = Signal(str, bool)                                        # text, is_progress_line
    progress                = Signal(float)                                            # 0..100, or -1 for indeterminate
    started                 = Signal(str, str)                                         # title, command line
    finished                = Signal(str, int, float)                                  # title, exit code, seconds
    busy_changed            = Signal(bool)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._proc: QProcess | None = None
        self._job: Job | None = None
        self._splitter      = LineSplitter()
        self._killed        = False

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? API
    #?------------------------------------------------------------------------------------------------------------------------------------
    @property
    def busy(self) -> bool:
        return self._proc is not None

    def run(self, tool: str, args: list[str], title: str,
            on_done: Callable[[int], None] | None = None) -> bool:
        """Run esptool / espefuse / espsecure (see core.tools.tool_invocation)."""
        program, arguments  = tool_invocation(tool, args)
        return self.run_program(program, arguments, title, on_done, tool)

    def run_program(self, program: str, arguments: list[str], title: str,
                    on_done: Callable[[int], None] | None = None, name: str = "",
                    env_extra: dict[str, str] | None = None) -> bool:
        """Run any external program (e.g. arduino-cli) with streamed output and progress."""
        if self.busy:
            return False
        self._job           = Job(name or program, arguments, title, on_done, time.monotonic())
        self._splitter      = LineSplitter()
        self._killed        = False

        proc                = QProcess(self)
        env                 = QProcessEnvironment.systemEnvironment()
        for key, value in {**tool_environment(), **(env_extra or {})}.items():
            env.insert(key, value)
        proc.setProcessEnvironment(env)
        proc.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        proc.setProgram(program)
        proc.setArguments(arguments)
        proc.readyReadStandardOutput.connect(self._on_output)
        proc.finished.connect(self._on_finished)
        proc.errorOccurred.connect(self._on_error)
        self._proc          = proc

        self.busy_changed.emit(True)
        self.progress.emit(-1)
        self.started.emit(title, quote_command(program, arguments))
        proc.start()
        return True

    def stop(self) -> None:
        if self._proc is not None:
            self._killed    = True
            self._proc.kill()

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? Internals
    #?------------------------------------------------------------------------------------------------------------------------------------
    def _on_output(self) -> None:
        if self._proc is None:
            return
        data                = bytes(self._proc.readAllStandardOutput().data()).decode("utf-8", errors="replace")
        for text in self._splitter.feed(data):
            self._emit_line(text)

    def _emit_line(self, text: str) -> None:
        pct                 = parse_progress(text)
        if pct is not None:
            self.progress.emit(pct)
        if text or pct is None:
            self.line.emit(text, pct is not None)

    def _on_error(self, error: QProcess.ProcessError) -> None:
        if error == QProcess.ProcessError.FailedToStart:
            self.line.emit(f"Error: could not start {self._job.tool if self._job else 'tool'} "
                           f"({self._proc.errorString() if self._proc else ''})", False)
            self._finish(-1)

    def _on_finished(self, code: int, status: QProcess.ExitStatus) -> None:
        self._on_output()
        for text in self._splitter.flush():
            self._emit_line(text)
        if self._killed:
            code            = -2
        elif status == QProcess.ExitStatus.CrashExit:
            code            = -1
        self._finish(code)

    def _finish(self, code: int) -> None:
        job, proc           = self._job, self._proc
        if job is None:
            return
        self._job, self._proc = None, None
        if proc is not None:
            proc.deleteLater()
        elapsed             = time.monotonic() - job.started_at
        self.progress.emit(100.0 if code == 0 else 0.0)
        self.busy_changed.emit(False)
        self.finished.emit(job.title, code, elapsed)
        if job.on_done is not None:
            job.on_done(code)
#?----------------------------------------------------------------------------------------------------------------------------------------
