#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?             __            __                     __      _
#?            / /____  _____/ /_    ____ __________/ /_  __(_)___  ____
#?           / __/ _ \/ ___/ __/   / __ `/ ___/ __  / / / / / __ \/ __ \
#?          / /_/  __(__  ) /_    / /_/ / /  / /_/ / /_/ / / / / / /_/ /
#?          \__/\___/____/\__/____\__,_/_/   \__,_/\__,_/_/_/ /_/\____/
#?                          /_____/
#?
#?
#? Name:        test_arduino.py
#? Purpose:     Unit tests for the Code page backend (flash.core.arduino). No network or board needed.
#?              Run with:  python -m unittest tests.test_arduino -v
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     05/09/2019
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
import  sys
import  tempfile
import  unittest
from    pathlib                     import  Path
#?----------------------------------------------------------------------------------------------------------------------------------------
ROOT                        = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from    flash.core                  import  arduino                                    # noqa: E402
#?----------------------------------------------------------------------------------------------------------------------------------------
class DiagnosticTests(unittest.TestCase):
    def test_windows_path_with_drive(self):
        d                   = arduino.parse_diagnostic(r"C:\Users\me\Blink\Blink.ino:12:5: error: 'foo' was not declared in this scope")
        self.assertEqual((d.path, d.line, d.col, d.severity), (r"C:\Users\me\Blink\Blink.ino", 12, 5, "error"))
        self.assertIn("foo", d.message)

    def test_unix_path_without_column_and_fatal(self):
        d                   = arduino.parse_diagnostic("/home/me/a/a.ino:3: fatal error: Missing.h: No such file or directory")
        self.assertEqual((d.path, d.line, d.col, d.severity), ("/home/me/a/a.ino", 3, 1, "error"))

    def test_warning_and_noise(self):
        self.assertEqual(arduino.parse_diagnostic("x.cpp:7:1: warning: unused variable 'y'").severity, "warning")
        self.assertIsNone(arduino.parse_diagnostic("Sketch uses 924 bytes (2%) of program storage space."))
        self.assertIsNone(arduino.parse_diagnostic("Downloading packages: 45.3%"))
#?----------------------------------------------------------------------------------------------------------------------------------------
class CommandTests(unittest.TestCase):
    def test_fqbn_options(self):
        self.assertEqual(arduino.fqbn_with_options("esp32:esp32:esp32", {"PartitionScheme": "huge_app", "X": ""}),
                         "esp32:esp32:esp32:PartitionScheme=huge_app")
        self.assertEqual(arduino.fqbn_with_options("esp32:esp32:esp32:Old=1", {}), "esp32:esp32:esp32")

    def test_compile_args(self):
        args                = arduino.compile_args("arduino:avr:uno", "/s/Blink", port="COM5", board_urls=["u1", " ", "u2"])
        self.assertEqual(args[:3], ["compile", "--fqbn", "arduino:avr:uno"])
        self.assertIn("--upload", args)
        self.assertEqual(args[args.index("--port") + 1], "COM5")
        self.assertEqual(args[args.index("--additional-urls") + 1], "u1,u2")
        self.assertEqual(args[-1], "/s/Blink")
        self.assertNotIn("--upload", arduino.compile_args("a:b:c", "s"))

    def test_version_key(self):
        versions            = ["2.0.9", "2.0.10", "3.0.0-rc1", "3.0.0", "1.10.0"]
        self.assertEqual(sorted(versions, key=arduino.version_key)[-1], "3.0.0")
        self.assertLess(arduino.version_key("2.0.9"), arduino.version_key("2.0.10"))

    def test_release_asset(self):
        self.assertRegex(arduino.release_asset_suffix(), r"^(Windows|Linux|macOS)_\w+\.(zip|tar\.gz)$")
#?----------------------------------------------------------------------------------------------------------------------------------------
class ParserTests(unittest.TestCase):
    def test_boards(self):
        data                = {"boards": [{"name": "Uno", "fqbn": "arduino:avr:uno", "platform": {"metadata": {"id": "arduino:avr"}}},
                                          {"name": "No fqbn"}]}
        boards              = arduino.parse_boards(data)
        self.assertEqual([(b.name, b.fqbn, b.platform) for b in boards], [("Uno", "arduino:avr:uno", "arduino:avr")])
        self.assertEqual(arduino.parse_boards("{}"), [])

    def test_platforms(self):
        data                = {"platforms": [{"id": "esp32:esp32", "maintainer": "Espressif", "installed_version": "",
                                              "latest_version": "3.3.12",
                                              "releases": {"3.3.12": {"name": "esp32", "boards": [{"name": "ESP32 Dev Module"}]}}}]}
        p                   = arduino.parse_platforms(data)[0]
        self.assertEqual((p.id, p.name, p.latest, p.installed, p.boards),
                         ("esp32:esp32", "esp32", "3.3.12", "", ["ESP32 Dev Module"]))

    def test_libraries(self):
        data                = {"libraries": [{"name": "ArduinoJson", "available_versions": ["6.9.0", "7.4.3", "6.10.0"],
                                              "latest": {"version": "7.4.3", "author": "Benoit", "sentence": "JSON"}}]}
        lib                 = arduino.parse_library_search(data, {"ArduinoJson": "6.10.0"})[0]
        self.assertEqual((lib.latest, lib.installed, lib.versions[:2]), ("7.4.3", "6.10.0", ["7.4.3", "6.10.0"]))
        installed           = arduino.parse_installed_libraries(
            {"installed_libraries": [{"library": {"name": "Servo", "version": "1.2.1"}}]})
        self.assertEqual(installed, {"Servo": "1.2.1"})

    def test_board_options_and_ports(self):
        data                = {"config_options": [{"option": "PartitionScheme", "option_label": "Partition Scheme",
                                                   "values": [{"value": "default", "value_label": "Default", "selected": True},
                                                              {"value": "huge_app", "value_label": "Huge APP"}]}]}
        opt                 = arduino.parse_board_options(data)[0]
        self.assertEqual((opt.option, opt.default, len(opt.values)), ("PartitionScheme", "default", 2))
        ports               = arduino.parse_board_list({"detected_ports": [{"port": {"address": "COM3", "label": "COM3"},
                                                                            "matching_boards": [{"name": "Uno",
                                                                                                 "fqbn": "arduino:avr:uno"}]}]})
        self.assertEqual((ports[0].address, ports[0].boards[0].fqbn), ("COM3", "arduino:avr:uno"))

    def test_json_with_banner(self):
        self.assertEqual(arduino.parse_boards('noise\n{"boards": []}'), [])
#?----------------------------------------------------------------------------------------------------------------------------------------
class SketchTests(unittest.TestCase):
    def test_create_and_list(self):
        with tempfile.TemporaryDirectory() as d:
            main            = arduino.create_sketch(d, "Demo_1")
            self.assertEqual(main, Path(d) / "Demo_1" / "Demo_1.ino")
            (main.parent / "b.h").write_text("")
            (main.parent / "a.cpp").write_text("")
            (main.parent / "z.ino").write_text("")
            (main.parent / "notes.txt").write_text("")
            names           = [p.name for p in arduino.sketch_files(main.parent)]
            self.assertEqual(names, ["Demo_1.ino", "z.ino", "a.cpp", "b.h"])
            self.assertEqual(arduino.sketch_dir(main), main.parent)
            with self.assertRaises(FileExistsError):
                arduino.create_sketch(d, "Demo_1")
            with self.assertRaises(ValueError):
                arduino.create_sketch(d, "bad name")
            self.assertNotEqual(arduino.unique_sketch_name(d), "Demo_1")

    def test_builtin_examples_are_valid_sketch_names(self):
        for name in arduino.BUILTIN_EXAMPLES:
            self.assertRegex(name, arduino.VALID_SKETCH_NAME)
#?----------------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
#?----------------------------------------------------------------------------------------------------------------------------------------
