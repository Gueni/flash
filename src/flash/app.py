#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?            ____ _____  ____
#?           / __ `/ __ \/ __ \
#?          / /_/ / /_/ / /_/ /
#?          \__,_/ .___/ .___/
#?              /_/   /_/
#?
#?
#? Name:        app.py
#? Purpose:     Application setup and start-up (high DPI, theme, main window).
#?              Start it with `python main.py`. Frozen builds started with --run-tool run a bundled tool instead.
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     05/09/2019
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
from    __future__                  import  annotations

import  os
import  sys

from    flash.core.tools            import  TOOL_FLAG, dispatch_tool
#?----------------------------------------------------------------------------------------------------------------------------------------
class App:
    """Application setup and start-up."""

    @staticmethod
    def _enable_high_dpi():
        from    PySide6.QtCore              import  Qt
        from    PySide6.QtGui               import  QGuiApplication
        QGuiApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        if sys.platform == "win32":                                                    # own taskbar icon/group instead of python.exe's
            try:
                import  ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Gueni.Flash")
            except Exception:
                pass

    @staticmethod
    def run(argv: list[str]) -> int:
        """Create the application, apply the saved theme and show the main window."""
        from    PySide6.QtCore              import  QTimer
        from    PySide6.QtGui               import  QIcon
        from    PySide6.QtWidgets           import  QApplication

        from    flash                       import  APP_NAME, ORG_DOMAIN, ORG_NAME, __version__
        from    flash.paths                 import  asset
        from    flash.settings              import  app_settings
        from    flash.ui.main_window        import  MainWindow
        from    flash.ui.theme              import  theme

        App._enable_high_dpi()
        app                 = QApplication(argv)
        app.setApplicationName(APP_NAME)
        app.setApplicationDisplayName(APP_NAME)
        app.setOrganizationName(ORG_NAME)
        app.setOrganizationDomain(ORG_DOMAIN)
        app.setApplicationVersion(__version__)
        app.setWindowIcon(QIcon(asset("flash.ico")))
        if sys.platform.startswith("linux"):
            app.setDesktopFileName("flash")

        theme().set_mode((app_settings().value("ui/theme", "system") or "system").lower())
        window              = MainWindow()
        window.show()

        if os.environ.get("FLASH_SMOKE_TEST"):                                         # used by build scripts: start, render, quit
            QTimer.singleShot(int(os.environ.get("FLASH_SMOKE_TEST_MS", "1500")), app.quit)
        return app.exec()
#?----------------------------------------------------------------------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    """Entry point: run a bundled tool (frozen builds, --run-tool) or start the GUI."""
    argv                    = list(sys.argv if argv is None else argv)
    if len(argv) > 1 and argv[1] == TOOL_FLAG:
        return dispatch_tool(argv[1:])
    return App.run(argv)
#?----------------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    raise SystemExit(main())
#?----------------------------------------------------------------------------------------------------------------------------------------
