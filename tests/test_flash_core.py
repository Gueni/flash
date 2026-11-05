#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?             __            __       ______           __
#?            / /____  _____/ /_     / __/ /___ ______/ /_      _________  ________
#?           / __/ _ \/ ___/ __/    / /_/ / __ `/ ___/ __ \    / ___/ __ \/ ___/ _ \
#?          / /_/  __(__  ) /_     / __/ / /_/ (__  ) / / /   / /__/ /_/ / /  /  __/
#?          \__/\___/____/\__/____/_/ /_/\__,_/____/_/ /_/____\___/\____/_/   \___/
#?                          /_____/                     /_____/
#?
#?
#? Name:        test_flash_core.py
#? Purpose:     Unit tests for Flash's GUI-independent logic.
#?              Run with:  python -m unittest tests.test_flash_core -v (The other test_*.py files in this folder are the
#?              legacy upstream esptool 2.x suites and need hardware.)
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     05/09/2019
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
import  json
import  subprocess
import  sys
import  tempfile
import  unittest
from    pathlib                     import  Path
#?----------------------------------------------------------------------------------------------------------------------------------------
ROOT                        = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from    flash.core                  import  efuse                                      # noqa: E402
from    flash.core.tools            import  (Connection, FlashOptions, Image, ImageSet, LineSplitter, classify_line, parse_number, parse_progress,
                                             quote_command, strip_ansi, tool_invocation)  # noqa: E402
#?----------------------------------------------------------------------------------------------------------------------------------------
SAMPLE_APP                  = ROOT / "tests" / "micropython-esp32" / "application.bin"
#?----------------------------------------------------------------------------------------------------------------------------------------
class NumberTests(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(parse_number("0x1000"), 0x1000)
        self.assertEqual(parse_number("4096"), 4096)
        self.assertEqual(parse_number("4k"), 4096)
        self.assertEqual(parse_number("1M"), 1 << 20)
        self.assertEqual(parse_number(" 0X10 "), 16)
        self.assertIsNone(parse_number("0xZZ"))
        self.assertIsNone(parse_number(""))
#?----------------------------------------------------------------------------------------------------------------------------------------
class CommandTests(unittest.TestCase):
    def test_connection_args(self):
        c                   = Connection(port="COM5", baud=921600, chip="esp32s3")
        args                = c.esptool_args()
        self.assertEqual(args[:6], ["--chip", "esp32s3", "--port", "COM5", "--baud", "921600"])
        self.assertIn("--before", args)
        self.assertNotIn("--no-stub", args)

    def test_espefuse_virtual_defaults_to_esp32(self):
        args                = Connection(chip="auto").espefuse_args(virtual=True)
        self.assertEqual(args[:3], ["--chip", "esp32", "--virt"])
        self.assertNotIn("--port", args)

    def test_flash_options(self):
        o                   = FlashOptions(mode="dio", erase_all=True, compress=False)
        self.assertEqual(o.args()[:2], ["--flash-mode", "dio"])
        self.assertIn("--erase-all", o.args())
        self.assertIn("--no-compress", o.args())

    def test_image_set(self):
        with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as fh:
            fh.write(b"\0" * 16)
        try:
            s               = ImageSet([Image("4k", fh.name), Image("0x8000", "", True), Image("0x10000", fh.name, False)])
            self.assertIsNone(s.validate())
            self.assertEqual(s.pairs(), ["0x1000", fh.name])
            self.assertIn("twice", ImageSet([Image("0x0", fh.name), Image("0", fh.name)]).validate())
            self.assertIn("Invalid offset", ImageSet([Image("zz", fh.name)]).validate())
            self.assertIsNotNone(ImageSet([]).validate())
        finally:
            Path(fh.name).unlink()

    def test_invocation_from_source(self):
        program, args       = tool_invocation("esptool", ["version"])
        self.assertEqual(args, ["-u", "-m", "esptool", "version"])
        self.assertEqual(quote_command(program, args), "esptool version")
        with self.assertRaises(ValueError):
            tool_invocation("rm", [])
#?----------------------------------------------------------------------------------------------------------------------------------------
class OutputTests(unittest.TestCase):
    def test_progress(self):
        self.assertEqual(parse_progress("Writing at 0x00010000 [=====>      ]  45.3% 1234/5678 bytes"), 45.3)
        self.assertEqual(parse_progress("Writing at 0x00011000... (12 %)"), 12.0)
        self.assertEqual(parse_progress("Reading flash [====] 100.0%"), 100.0)
        self.assertIsNone(parse_progress("Chip is ESP32 with 25% luck"))
        self.assertIsNone(parse_progress("Hash of data verified."))

    def test_splitter_handles_carriage_returns_and_partials(self):
        sp                  = LineSplitter()
        self.assertEqual(sp.feed("a\r\nb\rc"), ["a", "b"])
        self.assertEqual(sp.feed("d\n"), ["cd"])
        self.assertEqual(sp.feed("\x1b[32mgreen\x1b[0m"), [])
        self.assertEqual(sp.flush(), ["green"])

    def test_classify(self):
        self.assertEqual(classify_line("A fatal error occurred: Failed to connect"), "error")
        self.assertEqual(classify_line("Warning: deprecated option"), "warning")
        self.assertEqual(classify_line("Hash of data verified."), "success")
        self.assertEqual(classify_line("Chip type: ESP32"), "info")
        self.assertEqual(strip_ansi("\x1b[1mbold\x1b[0m"), "bold")
#?----------------------------------------------------------------------------------------------------------------------------------------
class EfuseTests(unittest.TestCase):
    SAMPLE                  = {
        "ABS_DONE_0": {"bit_len": 1, "block": 0, "category": "security", "description": "Secure boot V1",
                       "efuse_type": "bool", "name": "ABS_DONE_0", "raw_value": "0x0", "readable": True,
                       "value": False, "writeable": True},
        "MAC": {"block": 0, "category": "identity", "description": "MAC", "name": "MAC",
                "raw_value": "0xaabb", "readable": True, "value": "aa:bb", "writeable": False},
    }

    def test_parse_and_export(self):
        fields              = efuse.parse_summary(json.dumps(self.SAMPLE))
        self.assertEqual([f.name for f in fields], ["MAC", "ABS_DONE_0"])              # sorted by category
        self.assertEqual(fields[0].access, "R/-")
        self.assertEqual(fields[1].value, "False")
        with tempfile.TemporaryDirectory() as d:
            csv_path        = efuse.export(fields, Path(d) / "e.csv")
            self.assertIn("ABS_DONE_0", csv_path.read_text(encoding="utf-8"))
            xlsx            = efuse.export(fields, Path(d) / "e.xlsx")
            self.assertTrue(xlsx.exists())

    def test_load_tolerates_banner(self):
        with tempfile.TemporaryDirectory() as d:
            p               = Path(d) / "s.json"
            p.write_text("espefuse v5\n" + json.dumps(self.SAMPLE), encoding="utf-8")
            self.assertEqual(len(efuse.load_summary_file(p)), 2)
#?----------------------------------------------------------------------------------------------------------------------------------------
class ToolIntegrationTests(unittest.TestCase):
    """Run the real tools offline (no board needed)."""

    def run_tool(self, tool, *args):
        program, argv       = tool_invocation(tool, list(args))
        return subprocess.run([sys.executable, *argv], capture_output=True, text=True, timeout=120)

    def test_virtual_efuse_summary(self):
        with tempfile.TemporaryDirectory() as d:
            out             = Path(d) / "efuse.json"
            r               = self.run_tool("espefuse", "--chip", "esp32", "--virt", "summary", "--format", "json",
                                            "--file", str(out))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            fields          = efuse.load_summary_file(out)
            self.assertGreater(len(fields), 20)

    @unittest.skipUnless(SAMPLE_APP.exists(), "sample firmware not present")
    def test_image_info(self):
        r                   = self.run_tool("esptool", "--chip", "esp32", "image-info", str(SAMPLE_APP))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Checksum", r.stdout)
#?----------------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
#?----------------------------------------------------------------------------------------------------------------------------------------
