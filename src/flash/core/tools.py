#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?             __              __
#?            / /_____  ____  / /____
#?           / __/ __ \/ __ \/ / ___/
#?          / /_/ /_/ / /_/ / (__  )
#?          \__/\____/\____/_/____/
#?
#?
#? Name:        tools.py
#? Purpose:     How to invoke esptool / espefuse / espsecure, and how to read their output.
#?              From source the tools run as ``python -m esptool ...``. In a frozen PyInstaller build there is no Python
#?              interpreter, so the executable re-launches *itself* with ``--run-tool <tool> ...`` and :func:`dispatch_tool`
#?              runs the tool module. Either way the GUI talks to a separate process, so a hung or crashing flash operation
#?              can always be stopped without taking the window down.
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     05/09/2019
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
from    __future__                  import  annotations

import  os
import  re
import  runpy
import  sys
from    dataclasses                 import  dataclass, field
from    pathlib                     import  Path
#?----------------------------------------------------------------------------------------------------------------------------------------
TOOL_FLAG                   = "--run-tool"
TOOLS                       = ("esptool", "espefuse", "espsecure")

CHIPS                       = [
    "auto", "esp32", "esp32s2", "esp32s3", "esp32c2", "esp32c3", "esp32c5",
    "esp32c6", "esp32c61", "esp32h2", "esp32p4", "esp8266",
]
BAUD_RATES                  = ["115200", "230400", "460800", "921600", "1500000", "2000000", "74880", "9600"]
FLASH_MODES                 = ["keep", "qio", "qout", "dio", "dout"]
FLASH_FREQS                 = ["keep", "80m", "64m", "60m", "48m", "40m", "32m", "30m", "26m", "24m", "20m"]
FLASH_SIZES                 = [
    "keep", "detect", "256KB", "512KB", "1MB", "2MB", "2MB-c1", "4MB", "4MB-c1",
    "8MB", "16MB", "32MB", "64MB", "128MB",
]
BEFORE_RESET                = ["default-reset", "usb-reset", "no-reset", "no-reset-no-sync"]
AFTER_RESET                 = ["hard-reset", "soft-reset", "no-reset", "no-reset-stub", "watchdog-reset"]

# Default image layouts: (offset, label) per chip family.
LAYOUTS: dict[str, list[tuple[str, str]]] = {
    "ESP32 / ESP32-S2": [("0x1000", "bootloader.bin"), ("0x8000", "partitions.bin"), ("0x10000", "application.bin")],
    "ESP32-S3 / C3 / C6 / H2": [("0x0", "bootloader.bin"), ("0x8000", "partitions.bin"), ("0x10000", "application.bin")],
    "ESP32-P4 / C5": [("0x2000", "bootloader.bin"), ("0x8000", "partitions.bin"), ("0x10000", "application.bin")],
    "Single image @ 0x0": [("0x0", "firmware.bin")],
}
#?----------------------------------------------------------------------------------------------------------------------------------------
#? Process invocation
#?----------------------------------------------------------------------------------------------------------------------------------------
def tool_invocation(tool: str, args: list[str]) -> tuple[str, list[str]]:
    """Return ``(program, arguments)`` that run *tool* with *args*."""
    if tool not in TOOLS:
        raise ValueError(f"unknown tool {tool!r}")
    if getattr(sys, "frozen", False):
        return sys.executable, [TOOL_FLAG, tool, *args]
    return _python_executable(), ["-u", "-m", tool, *args]
#?----------------------------------------------------------------------------------------------------------------------------------------
def _python_executable() -> str:
    exe                     = Path(sys.executable)
    # Under pythonw.exe there is no console; python.exe would pop one up for the child.
    # pythonw still writes to the pipes QProcess hands it, so prefer it on Windows.
    if os.name == "nt" and exe.name.lower() == "python.exe":
        pythonw             = exe.with_name("pythonw.exe")
        if pythonw.exists():
            return str(pythonw)
    return str(exe)
#?----------------------------------------------------------------------------------------------------------------------------------------
def tool_environment() -> dict[str, str]:
    """Extra environment variables for tool processes (plain, unbuffered UTF-8 output)."""
    return {
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUTF8": "1",
        "NO_COLOR": "1",
        "TERM": "dumb",
        "COLUMNS": "160",
    }
#?----------------------------------------------------------------------------------------------------------------------------------------
def dispatch_tool(argv: list[str]) -> int:
    """Entry point used when the frozen executable is started with ``--run-tool``."""
    if len(argv) < 2 or argv[1] not in TOOLS:
        print(f"usage: {TOOL_FLAG} {{{'|'.join(TOOLS)}}} [args...]", file=sys.stderr)
        return 2
    tool, args              = argv[1], argv[2:]
    _ensure_std_streams()
    sys.argv                = [tool, *args]
    try:
        runpy.run_module(tool, run_name="__main__", alter_sys=True)
    except SystemExit as exc:
        code                = exc.code
        if code is None:
            return 0
        if isinstance(code, int):
            return code
        print(code, file=sys.stderr)
        return 1
    return 0
#?----------------------------------------------------------------------------------------------------------------------------------------
def _ensure_std_streams() -> None:
    """Windowed builds may start without usable std streams; attach to the inherited pipes."""
    for name, fd in (("stdout", 1), ("stderr", 2)):
        stream              = getattr(sys, name)
        if stream is None:
            try:
                stream      = open(fd, "w", encoding="utf-8", errors="replace", closefd=False)
            except OSError:
                stream      = open(os.devnull, "w", encoding="utf-8")
            setattr(sys, name, stream)
        try:
            stream.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass
    if sys.stdin is None:
        sys.stdin           = open(os.devnull, encoding="utf-8")
#?----------------------------------------------------------------------------------------------------------------------------------------
#? Command building
#?----------------------------------------------------------------------------------------------------------------------------------------
@dataclass
class Connection:
    port: str               = ""
    baud: int               = 115200
    chip: str               = "auto"
    before: str             = "default-reset"
    after: str              = "hard-reset"
    connect_attempts: int   = 7
    no_stub: bool           = False

    def esptool_args(self, *, with_port: bool = True, with_reset: bool = True) -> list[str]:
        args                = ["--chip", self.chip or "auto"]
        if with_port and self.port:
            args           += ["--port", self.port]
        args               += ["--baud", str(self.baud)]
        if with_reset:
            args           += ["--before", self.before, "--after", self.after,
                               "--connect-attempts", str(self.connect_attempts)]
        if self.no_stub:
            args.append("--no-stub")
        return args

    def espefuse_args(self, *, virtual: bool = False) -> list[str]:
        chip                = self.chip if self.chip and self.chip != "auto" else ("esp32" if virtual else "auto")
        args                = ["--chip", chip]
        if virtual:
            args.append("--virt")
        elif self.port:
            args           += ["--port", self.port]
        args               += ["--baud", str(self.baud)]
        return args
#?----------------------------------------------------------------------------------------------------------------------------------------
@dataclass
class FlashOptions:
    mode: str               = "keep"
    freq: str               = "keep"
    size: str               = "detect"
    erase_all: bool         = False
    compress: bool          = True
    skip_flashed: bool      = False

    def args(self) -> list[str]:
        out                 = ["--flash-mode", self.mode, "--flash-freq", self.freq, "--flash-size", self.size]
        if self.erase_all:
            out.append("--erase-all")
        out.append("--compress" if self.compress else "--no-compress")
        if self.skip_flashed:
            out.append("--skip-flashed")
        return out
#?----------------------------------------------------------------------------------------------------------------------------------------
@dataclass
class Image:
    offset: str
    path: str
    enabled: bool           = True
#?----------------------------------------------------------------------------------------------------------------------------------------
@dataclass
class ImageSet:
    images: list[Image]     = field(default_factory=list)

    def selected(self) -> list[Image]:
        return [i for i in self.images if i.enabled and i.path.strip()]

    def pairs(self) -> list[str]:
        out: list[str]      = []
        for img in self.selected():
            out            += [normalize_number(img.offset), img.path]
        return out

    def validate(self) -> str | None:
        """Return an error message, or ``None`` if the selection can be flashed."""
        sel                 = self.selected()
        if not sel:
            return "Select at least one image with a file."
        seen: set[int]      = set()
        for img in sel:
            value           = parse_number(img.offset)
            if value is None:
                return f"Invalid offset {img.offset!r} for {Path(img.path).name}."
            if value in seen:
                return f"Offset {img.offset} is used twice."
            seen.add(value)
            if not Path(img.path).is_file():
                return f"File not found: {img.path}"
        return None
#?----------------------------------------------------------------------------------------------------------------------------------------
_NUMBER_RE                  = re.compile(r"^\s*(0[xX][0-9a-fA-F]+|\d+)\s*([kKmM]?)[bB]?\s*$")
#?----------------------------------------------------------------------------------------------------------------------------------------
def parse_number(text: str) -> int | None:
    """Parse ``0x1000``, ``4096``, ``4k``, ``1M`` into an int. Returns ``None`` if invalid."""
    m                       = _NUMBER_RE.match(text or "")
    if not m:
        return None
    value                   = int(m.group(1), 0)
    unit                    = m.group(2).lower()
    if unit == "k":
        value              *= 1024
    elif unit == "m":
        value              *= 1024 * 1024
    return value
#?----------------------------------------------------------------------------------------------------------------------------------------
def normalize_number(text: str) -> str:
    value                   = parse_number(text)
    return text.strip() if value is None else hex(value)
#?----------------------------------------------------------------------------------------------------------------------------------------
def human_size(n: int) -> str:
    size                    = float(n)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size               /= 1024
    return f"{n} B"
#?----------------------------------------------------------------------------------------------------------------------------------------
#? Output parsing
#?----------------------------------------------------------------------------------------------------------------------------------------
_ANSI_RE                    = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]|\x1b\][^\x07]*\x07")
_PERCENT_RE                 = re.compile(r"(\d{1,3}(?:\.\d+)?)\s?%")
_PROGRESS_HINT_RE           = re.compile(
    r"(writing|reading|verifying|erasing|uploading|downloading|dumping|compressed|\[[=>#\-━╸ ]+\])", re.I
)
#?----------------------------------------------------------------------------------------------------------------------------------------
def strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text)
#?----------------------------------------------------------------------------------------------------------------------------------------
def parse_progress(line: str) -> float | None:
    """Return progress in percent if *line* is a progress update, else ``None``."""
    if not _PROGRESS_HINT_RE.search(line):
        return None
    matches                 = _PERCENT_RE.findall(line)
    if not matches:
        return None
    value                   = float(matches[-1])
    return value if 0.0 <= value <= 100.0 else None
#?----------------------------------------------------------------------------------------------------------------------------------------
def classify_line(line: str) -> str:
    """Rough severity of an output line: ``error``, ``warning``, ``success`` or ``info``."""
    low                     = line.lower()
    if any(k in low for k in ("fatal error", "error:", "a fatal", "failed", "exception", "traceback", "permission denied")):
        return "error"
    if low.startswith("warning") or "warning:" in low or "deprecated" in low:
        return "warning"
    if any(k in low for k in ("hash of data verified", "verification successful", "successfully", "hard resetting",
                              "chip erase completed", "done", "wrote ")):
        return "success"
    return "info"
#?----------------------------------------------------------------------------------------------------------------------------------------
class LineSplitter:
    """Turn a raw byte stream into complete lines, treating ``\\r`` as a line break too."""

    def __init__(self) -> None:
        self._buf           = ""

    def feed(self, data: str) -> list[str]:
        self._buf          += data.replace("\r\n", "\n").replace("\r", "\n")
        *lines, self._buf   = self._buf.split("\n")
        return [strip_ansi(l).rstrip() for l in lines]

    def flush(self) -> list[str]:
        rest, self._buf     = self._buf, ""
        rest                = strip_ansi(rest).rstrip()
        return [rest] if rest else []
#?----------------------------------------------------------------------------------------------------------------------------------------
def quote_command(program: str, args: list[str]) -> str:
    """Human readable command line for the console."""
    def q(a: str) -> str:
        return f'"{a}"' if (" " in a or not a) else a
    name                    = Path(program).stem
    args                    = [f"<{len(a.split(','))} board index URLs>" if i and args[i - 1] == "--additional-urls" else a
                               for i, a in enumerate(args)]                            # keep the echo readable
    if args[:2] == ["-u", "-m"]:
        return " ".join(q(a) for a in args[2:])
    if args[:1] == [TOOL_FLAG]:
        return " ".join(q(a) for a in args[1:])
    return " ".join([name, *map(q, args)])
#?----------------------------------------------------------------------------------------------------------------------------------------
