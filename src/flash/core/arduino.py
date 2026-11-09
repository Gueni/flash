#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?                            __      _
#?            ____ __________/ /_  __(_)___  ____
#?           / __ `/ ___/ __  / / / / / __ \/ __ \
#?          / /_/ / /  / /_/ / /_/ / / / / / /_/ /
#?          \__,_/_/   \__,_/\__,_/_/_/ /_/\____/
#?
#?
#? Name:        arduino.py
#? Purpose:     Arduino IDE backend: locate / download arduino-cli, build its command lines and parse its output.
#?              arduino-cli (the engine behind Arduino IDE 2) does compiling, uploading, board cores and libraries. Flash
#?              bundles it in the installer; from source it is downloaded on first use into the user data folder. It shares
#?              the standard Arduino15 data folder and sketchbook with the Arduino IDE, so cores and libraries installed in
#?              either are reused.
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     05/09/2019
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
from    __future__                  import  annotations

import  hashlib
import  io
import  json
import  os
import  platform
import  re
import  shutil
import  subprocess
import  sys
import  tarfile
import  tempfile
import  urllib.request
import  zipfile
from    collections.abc             import  Callable
from    dataclasses                 import  dataclass, field
from    pathlib                     import  Path

from    PySide6.QtCore              import  QThread, Signal

from    flash.paths                 import  PACKAGE_DIR
#?----------------------------------------------------------------------------------------------------------------------------------------
CLI_NAME                    = "arduino-cli.exe" if os.name == "nt" else "arduino-cli"
RELEASE_API                 = "https://api.github.com/repos/arduino/arduino-cli/releases/latest"
USER_AGENT                  = "Flash-ESP-GUI"

DEFAULT_BOARD_URLS          = [
    "https://espressif.github.io/arduino-esp32/package_esp32_index.json",
    "https://arduino.esp8266.com/stable/package_esp8266com_index.json",
    "https://github.com/earlephilhower/arduino-pico/releases/download/global/package_rp2040_index.json",
    "https://github.com/stm32duino/BoardManagerFiles/raw/main/package_stmicroelectronics_index.json",
]

SKETCH_EXTENSIONS           = (".ino", ".h", ".hpp", ".cpp", ".c", ".S", ".pde")

NEW_SKETCH_TEMPLATE         = """void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
}

void loop() {
  // put your main code here, to run repeatedly:
}
"""

# Small built-in examples (Arduino's own "Built-in examples" are not shipped with arduino-cli).
BUILTIN_EXAMPLES: dict[str, str] = {
    "Blink": """// Blink the on-board LED once per second.
#ifndef LED_BUILTIN
#define LED_BUILTIN 2   // most ESP32 dev boards
#endif

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);
  delay(500);
  digitalWrite(LED_BUILTIN, LOW);
  delay(500);
}
""",
    "SerialHello": """// Print a counter on the serial port (open the Monitor page at 115200 baud).
unsigned long counter = 0;

void setup() {
  Serial.begin(115200);
  while (!Serial) { }
  Serial.println("Hello from Flash!");
}

void loop() {
  Serial.print("tick ");
  Serial.println(counter++);
  delay(1000);
}
""",
    "AnalogReadSerial": """// Read an analog pin and print the value.
const int SENSOR_PIN = A0;

void setup() {
  Serial.begin(115200);
}

void loop() {
  int value = analogRead(SENSOR_PIN);
  Serial.println(value);
  delay(100);
}
""",
    "ESP32_WiFiScan": """// ESP32 / ESP8266: list the Wi-Fi networks around you.
#if defined(ESP32)
#include <WiFi.h>
#elif defined(ESP8266)
#include <ESP8266WiFi.h>
#endif

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);
}

void loop() {
  int n = WiFi.scanNetworks();
  Serial.printf("%d networks found\\n", n);
  for (int i = 0; i < n; ++i) {
    Serial.printf("%2d  %-32s  %4d dBm\\n", i + 1, WiFi.SSID(i).c_str(), WiFi.RSSI(i));
  }
  Serial.println();
  delay(5000);
}
""",
    "ESP32_WebServer": """// ESP32: tiny web server - set your Wi-Fi credentials, then open the printed IP address.
#include <WiFi.h>
#include <WebServer.h>

const char* SSID     = "your-ssid";
const char* PASSWORD = "your-password";

WebServer server(80);

void handleRoot() {
  server.send(200, "text/html", "<h1>Hello from ESP32</h1><p>Uptime: " + String(millis() / 1000) + " s</p>");
}

void setup() {
  Serial.begin(115200);
  WiFi.begin(SSID, PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(300);
    Serial.print(".");
  }
  Serial.printf("\\nConnected: http://%s/\\n", WiFi.localIP().toString().c_str());
  server.on("/", handleRoot);
  server.begin();
}

void loop() {
  server.handleClient();
}
""",
}
#?----------------------------------------------------------------------------------------------------------------------------------------
#? Locating / downloading arduino-cli
#?----------------------------------------------------------------------------------------------------------------------------------------
def user_data_dir() -> Path:
    if os.name == "nt":
        base                = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return base / "Gueni" / "Flash"
    base                    = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "flash-esp"
#?----------------------------------------------------------------------------------------------------------------------------------------
def bundled_cli() -> Path:
    return PACKAGE_DIR / "bin" / CLI_NAME
#?----------------------------------------------------------------------------------------------------------------------------------------
def downloaded_cli() -> Path:
    return user_data_dir() / "arduino-cli" / CLI_NAME
#?----------------------------------------------------------------------------------------------------------------------------------------
def find_cli() -> str | None:
    """Bundled binary first, then a previously downloaded one, then any arduino-cli on PATH."""
    for candidate in (bundled_cli(), downloaded_cli()):
        if candidate.is_file():
            return str(candidate)
    return shutil.which("arduino-cli")
#?----------------------------------------------------------------------------------------------------------------------------------------
def release_asset_suffix() -> str:
    machine                 = platform.machine().lower()
    if sys.platform == "win32":
        return "Windows_ARM64.zip" if machine in ("arm64", "aarch64") else "Windows_64bit.zip"
    if sys.platform == "darwin":
        return "macOS_ARM64.tar.gz" if machine in ("arm64", "aarch64") else "macOS_64bit.tar.gz"
    if machine in ("aarch64", "arm64"):
        return "Linux_ARM64.tar.gz"
    if machine.startswith("armv7") or machine == "armv7l":
        return "Linux_ARMv7.tar.gz"
    return "Linux_64bit.tar.gz"
#?----------------------------------------------------------------------------------------------------------------------------------------
def _get(url: str, timeout: int = 60) -> bytes:
    req                     = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()
#?----------------------------------------------------------------------------------------------------------------------------------------
def _download(url: str, progress: Callable[[int, int], None] | None) -> bytes:
    req                     = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as resp:
        total               = int(resp.headers.get("Content-Length") or 0)
        buf                 = io.BytesIO()
        while True:
            chunk           = resp.read(256 * 1024)
            if not chunk:
                break
            buf.write(chunk)
            if progress:
                progress(buf.tell(), total)
        return buf.getvalue()
#?----------------------------------------------------------------------------------------------------------------------------------------
def download_cli(dest_dir: Path | None = None, progress: Callable[[int, int], None] | None = None) -> Path:
    """Download the latest arduino-cli release for this platform, verify its SHA-256 and unpack the binary."""
    dest_dir                = Path(dest_dir) if dest_dir else downloaded_cli().parent
    release                 = json.loads(_get(RELEASE_API))
    version                 = str(release["tag_name"]).lstrip("v")
    suffix                  = release_asset_suffix()
    assets                  = {a["name"]: a["browser_download_url"] for a in release.get("assets", [])}
    name                    = f"arduino-cli_{version}_{suffix}"
    if name not in assets:
        raise RuntimeError(f"No arduino-cli build for this platform ({suffix}) in release {version}")
    data                    = _download(assets[name], progress)

    checksum_name           = next((n for n in assets if n.endswith("checksums.txt")), None)
    if checksum_name:
        sums                = _get(assets[checksum_name]).decode("utf-8", "replace")
        expected            = next((line.split()[0] for line in sums.splitlines() if line.strip().endswith(name)), None)
        if expected and hashlib.sha256(data).hexdigest().lower() != expected.lower():
            raise RuntimeError("Checksum mismatch for the downloaded arduino-cli - download aborted")

    dest_dir.mkdir(parents=True, exist_ok=True)
    target                  = dest_dir / CLI_NAME
    tmp                     = Path(tempfile.mkdtemp(prefix="flash-acli-"))
    try:
        if name.endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                member      = next(m for m in zf.namelist() if Path(m).name == CLI_NAME)
                (tmp / CLI_NAME).write_bytes(zf.read(member))
        else:
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
                member      = next(m for m in tf.getmembers() if Path(m.name).name == CLI_NAME and m.isfile())
                (tmp / CLI_NAME).write_bytes(tf.extractfile(member).read())
        os.replace(tmp / CLI_NAME, target)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if os.name != "nt":
        target.chmod(0o755)
    return target
#?----------------------------------------------------------------------------------------------------------------------------------------
def cli_version(cli: str) -> str:
    try:
        out                 = subprocess.run([cli, "version", "--json"], capture_output=True, text=True, timeout=20,
                                             creationflags=_NO_WINDOW).stdout
        return str(json.loads(out).get("VersionString", "")) or "?"
    except (OSError, ValueError, subprocess.SubprocessError):
        return "?"
#?----------------------------------------------------------------------------------------------------------------------------------------
_NO_WINDOW                  = 0x08000000 if os.name == "nt" else 0                     # CREATE_NO_WINDOW: no console flash from a GUI app
#?----------------------------------------------------------------------------------------------------------------------------------------
#? Command lines
#?----------------------------------------------------------------------------------------------------------------------------------------
def global_args(board_urls: list[str]) -> list[str]:
    urls                    = [u.strip() for u in board_urls if u.strip()]
    return ["--additional-urls", ",".join(urls)] if urls else []
#?----------------------------------------------------------------------------------------------------------------------------------------
def compile_args(fqbn: str, sketch: str, *, port: str = "", export_dir: str = "", verbose: bool = False,
                 board_urls: list[str] | None = None) -> list[str]:
    args                    = ["compile", "--fqbn", fqbn, "--warnings", "default"]
    if verbose:
        args.append("--verbose")
    if export_dir:
        args               += ["--output-dir", export_dir]
    if port:
        args               += ["--upload", "--port", port]
    return args + global_args(board_urls or []) + [sketch]
#?----------------------------------------------------------------------------------------------------------------------------------------
def fqbn_with_options(fqbn: str, options: dict[str, str]) -> str:
    """``esp32:esp32:esp32`` + {"PartitionScheme": "huge_app"} -> ``esp32:esp32:esp32:PartitionScheme=huge_app``."""
    base                    = ":".join(fqbn.split(":")[:3])
    opts                    = ",".join(f"{k}={v}" for k, v in options.items() if v)
    return f"{base}:{opts}" if opts else base
#?----------------------------------------------------------------------------------------------------------------------------------------
#? Output parsing
#?----------------------------------------------------------------------------------------------------------------------------------------
DIAG_RE                     = re.compile(r"^(?P<path>(?:[A-Za-z]:)?[^:]+?):(?P<line>\d+):(?:(?P<col>\d+):)?\s*"
                                         r"(?P<sev>fatal error|error|warning|note):\s*(?P<msg>.*)$")
#?----------------------------------------------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Diagnostic:
    path: str
    line: int
    col: int
    severity: str
    message: str
#?----------------------------------------------------------------------------------------------------------------------------------------
def parse_diagnostic(text: str) -> Diagnostic | None:
    m                       = DIAG_RE.match(text.strip())
    if not m:
        return None
    sev                     = "error" if m.group("sev") in ("error", "fatal error") else m.group("sev")
    return Diagnostic(m.group("path"), int(m.group("line")), int(m.group("col") or 1), sev, m.group("msg"))
#?----------------------------------------------------------------------------------------------------------------------------------------
def _load(data: str | bytes | dict) -> dict:
    if isinstance(data, dict):
        return data
    text                    = data.decode("utf-8", "replace") if isinstance(data, bytes) else data
    start                   = text.find("{")
    return json.loads(text[start:]) if start >= 0 else {}
#?----------------------------------------------------------------------------------------------------------------------------------------
@dataclass
class Board:
    name: str
    fqbn: str
    platform: str           = ""
#?----------------------------------------------------------------------------------------------------------------------------------------
def parse_boards(data) -> list[Board]:
    """``board listall --json`` -> sorted boards."""
    out                     = []
    for b in _load(data).get("boards", []) or []:
        if b.get("fqbn"):
            plat            = ((b.get("platform") or {}).get("metadata") or {}).get("id", "")
            out.append(Board(b.get("name", b["fqbn"]), b["fqbn"], plat))
    return sorted(out, key=lambda b: (b.platform, b.name.lower()))
#?----------------------------------------------------------------------------------------------------------------------------------------
@dataclass
class Platform:
    id: str
    name: str
    maintainer: str
    latest: str
    installed: str
    boards: list[str]       = field(default_factory=list)
#?----------------------------------------------------------------------------------------------------------------------------------------
def parse_platforms(data) -> list[Platform]:
    """``core search --json`` / ``core list --json``."""
    out                     = []
    for p in _load(data).get("platforms", []) or []:
        releases            = p.get("releases") or {}
        latest              = p.get("latest_version") or (max(releases, key=version_key) if releases else "")
        rel                 = releases.get(latest) or (next(iter(releases.values())) if releases else {}) or {}
        boards              = [b.get("name", "") for b in rel.get("boards", []) or []]
        out.append(Platform(p.get("id", ""), rel.get("name") or p.get("name") or p.get("id", ""),
                            p.get("maintainer", ""), latest, p.get("installed_version", "") or "", boards))
    return out
#?----------------------------------------------------------------------------------------------------------------------------------------
def version_key(version: str) -> tuple:
    """Sort key so that 2.0.10 > 2.0.9 and 3.0.0 > 3.0.0-rc1."""
    parts                   = re.split(r"[.\-+]", version)
    return tuple((0, int(p), "") if p.isdigit() else (-1 if i >= 3 else 1, 0, p) for i, p in enumerate(parts)) + ((0, 0, ""),)
#?----------------------------------------------------------------------------------------------------------------------------------------
@dataclass
class Library:
    name: str
    latest: str
    installed: str
    author: str
    sentence: str
    versions: list[str]     = field(default_factory=list)
#?----------------------------------------------------------------------------------------------------------------------------------------
def parse_library_search(data, installed: dict[str, str] | None = None) -> list[Library]:
    """``lib search --json`` (merged with ``lib list`` versions)."""
    installed               = installed or {}
    out                     = []
    for lib in _load(data).get("libraries", []) or []:
        latest              = lib.get("latest") or {}
        releases            = lib.get("releases") or {}
        name                = lib.get("name", "")
        versions            = lib.get("available_versions") or list(releases)
        out.append(Library(name, latest.get("version", ""), installed.get(name, ""),
                           latest.get("author", ""), latest.get("sentence", ""),
                           sorted(versions, key=version_key, reverse=True)))
    return out
#?----------------------------------------------------------------------------------------------------------------------------------------
def parse_installed_libraries(data) -> dict[str, str]:
    """``lib list --json`` -> {name: version} (user-installed libraries)."""
    out                     = {}
    for item in _load(data).get("installed_libraries", []) or []:
        lib                 = item.get("library") or {}
        if lib.get("name"):
            out[lib["name"]] = lib.get("version", "")
    return out
#?----------------------------------------------------------------------------------------------------------------------------------------
@dataclass
class BoardOption:
    option: str
    label: str
    values: list[tuple[str, str]]                                                      # (value, label)
    default: str
#?----------------------------------------------------------------------------------------------------------------------------------------
def parse_board_options(data) -> list[BoardOption]:
    """``board details --json`` -> menu options (partition scheme, upload speed, ...)."""
    out                     = []
    for opt in _load(data).get("config_options", []) or []:
        values              = [(v.get("value", ""), v.get("value_label", v.get("value", ""))) for v in opt.get("values", []) or []]
        default             = next((v.get("value", "") for v in opt.get("values", []) or [] if v.get("selected")),
                                   values[0][0] if values else "")
        out.append(BoardOption(opt.get("option", ""), opt.get("option_label", opt.get("option", "")), values, default))
    return out
#?----------------------------------------------------------------------------------------------------------------------------------------
@dataclass
class DetectedPort:
    address: str
    label: str
    boards: list[Board]
#?----------------------------------------------------------------------------------------------------------------------------------------
def parse_board_list(data) -> list[DetectedPort]:
    """``board list --json`` -> serial ports with the boards arduino-cli recognises on them."""
    out                     = []
    for item in _load(data).get("detected_ports", []) or []:
        port                = item.get("port") or {}
        boards              = [Board(b.get("name", ""), b.get("fqbn", "")) for b in item.get("matching_boards", []) or []]
        out.append(DetectedPort(port.get("address", ""), port.get("label", ""), boards))
    return out
#?----------------------------------------------------------------------------------------------------------------------------------------
def parse_examples(data) -> dict[str, list[str]]:
    """``lib examples --json`` -> {library name: [example folder, ...]}."""
    out: dict[str, list[str]] = {}
    for item in _load(data).get("examples", []) or []:
        lib                 = (item.get("library") or {}).get("name", "")
        paths               = item.get("examples") or []
        if lib and paths:
            out[lib]        = sorted(paths, key=lambda p: Path(p).name.lower())
    return dict(sorted(out.items(), key=lambda kv: kv[0].lower()))
#?----------------------------------------------------------------------------------------------------------------------------------------
#? Sketches
#?----------------------------------------------------------------------------------------------------------------------------------------
def default_sketchbook() -> Path:
    docs                    = Path.home() / "Documents"
    return (docs if docs.is_dir() else Path.home()) / "Arduino"
#?----------------------------------------------------------------------------------------------------------------------------------------
def sketch_dir(path: str | Path) -> Path:
    p                       = Path(path)
    return p.parent if p.is_file() else p
#?----------------------------------------------------------------------------------------------------------------------------------------
def main_sketch_file(folder: str | Path) -> Path:
    folder                  = Path(folder)
    for ext in (".ino", ".pde"):
        candidate           = folder / f"{folder.name}{ext}"
        if candidate.is_file():
            return candidate
    return folder / f"{folder.name}.ino"
#?----------------------------------------------------------------------------------------------------------------------------------------
def sketch_files(folder: str | Path) -> list[Path]:
    """Main .ino first, then the other sketch sources in name order (like Arduino's tabs)."""
    folder                  = Path(folder)
    main                    = main_sketch_file(folder)
    others                  = sorted((p for p in folder.iterdir() if p.is_file() and p.suffix in SKETCH_EXTENSIONS and p != main),
                                     key=lambda p: (p.suffix != ".ino", p.name.lower()))
    return ([main] if main.is_file() else []) + others
#?----------------------------------------------------------------------------------------------------------------------------------------
VALID_SKETCH_NAME           = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.-]{0,62}$")
#?----------------------------------------------------------------------------------------------------------------------------------------
def create_sketch(parent: str | Path, name: str, content: str = NEW_SKETCH_TEMPLATE) -> Path:
    if not VALID_SKETCH_NAME.match(name):
        raise ValueError("Sketch names may contain letters, digits, '_', '-' and '.', and must not start with '-' or '.'")
    folder                  = Path(parent) / name
    if folder.exists():
        raise FileExistsError(f"{folder} already exists")
    folder.mkdir(parents=True)
    main                    = folder / f"{name}.ino"
    main.write_text(content, encoding="utf-8")
    return main
#?----------------------------------------------------------------------------------------------------------------------------------------
def unique_sketch_name(parent: str | Path, prefix: str = "sketch") -> str:
    import  datetime
    stamp                   = datetime.date.today().strftime("%b%d").lower()
    for letter in "abcdefghijklmnopqrstuvwxyz":
        name                = f"{prefix}_{stamp}{letter}"
        if not (Path(parent) / name).exists():
            return name
    return f"{prefix}_{stamp}_{os.getpid()}"
#?----------------------------------------------------------------------------------------------------------------------------------------
#? Background helpers (Qt)
#?----------------------------------------------------------------------------------------------------------------------------------------
class CliQuery(QThread):
    """Run a quick arduino-cli query (``--json``) off the GUI thread."""

    done                    = Signal(object, str)                                      # parsed JSON dict (or None), error text

    def __init__(self, cli: str, args: list[str], parent=None, timeout: int = 180) -> None:
        super().__init__(parent)
        self.cli, self.args, self.timeout = cli, args, timeout

    def run(self) -> None:
        try:
            proc            = subprocess.run([self.cli, *self.args, "--json"], capture_output=True, text=True,
                                             encoding="utf-8", errors="replace", timeout=self.timeout, creationflags=_NO_WINDOW)
        except (OSError, subprocess.SubprocessError) as exc:
            self.done.emit(None, str(exc))
            return
        try:
            data            = _load(proc.stdout) if proc.stdout.strip() else {}
        except ValueError:
            data            = None
        if proc.returncode != 0:
            err             = (proc.stderr or proc.stdout).strip()
            if isinstance(data, dict) and data.get("error"):
                err         = str(data["error"])
            self.done.emit(data, err or f"arduino-cli exited with code {proc.returncode}")
            return
        self.done.emit(data, "")
#?----------------------------------------------------------------------------------------------------------------------------------------
class CliDownloader(QThread):
    """Download arduino-cli in the background, reporting progress."""

    progress                = Signal(int, int)
    done                    = Signal(str, str)                                         # path, error

    def run(self) -> None:
        try:
            path            = download_cli(progress=lambda got, total: self.progress.emit(got, total))
        except Exception as exc:                                                       # network, checksum, disk
            self.done.emit("", str(exc))
            return
        self.done.emit(str(path), "")
#?----------------------------------------------------------------------------------------------------------------------------------------
