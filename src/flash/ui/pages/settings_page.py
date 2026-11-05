#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?                        __  __  _
#?             ________  / /_/ /_(_)___  ____ ______      ____  ____ _____ ____
#?            / ___/ _ \/ __/ __/ / __ \/ __ `/ ___/     / __ \/ __ `/ __ `/ _ \
#?           (__  )  __/ /_/ /_/ / / / / /_/ (__  )     / /_/ / /_/ / /_/ /  __/
#?          /____/\___/\__/\__/_/_/ /_/\__, /____/_____/ .___/\__,_/\__, /\___/
#?                                    /____/    /_____/_/          /____/
#?
#?
#? Name:        settings_page.py
#? Purpose:     Appearance, advanced connection options, profiles and about.
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     05/09/2019
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
from    __future__                  import  annotations

import  platform
from    pathlib                     import  Path

from    PySide6                     import  __version__ as pyside_version
from    PySide6.QtCore              import  Qt, QUrl
from    PySide6.QtGui               import  QDesktopServices, QPixmap
from    PySide6.QtWidgets           import  QCheckBox, QFileDialog, QLabel, QSpinBox

from    flash                       import  APP_NAME, __author__, __url__, __version__
from    flash.core.tools            import  AFTER_RESET, BEFORE_RESET
from    flash.paths                 import  asset
from    flash.settings              import  app_settings
from    flash.ui.theme              import  theme
from    flash.ui.widgets            import  Card, Page, button, combo, field, flow, row, save_path
#?----------------------------------------------------------------------------------------------------------------------------------------
def _esptool_version() -> str:
    try:
        import  esptool
        return esptool.__version__
    except Exception:                                                                  # pragma: no cover - only when esptool is missing
        return "not installed"
#?----------------------------------------------------------------------------------------------------------------------------------------
class SettingsPage(Page):
    title                   = "Settings"
    subtitle                = "Appearance, connection behaviour and profiles"
    icon_name               = "settings"

    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        st                  = ctx.store

        #? Appearance
        c                   = Card("Appearance", "Follow the operating system or force a theme. Shortcut: Ctrl+T.", "sun")
        self.theme_combo    = combo(["System", "Light", "Dark"])
        self.theme_combo.setCurrentText((app_settings().value("ui/theme", "system") or "system").capitalize())
        self.theme_combo.currentTextChanged.connect(self._theme_changed)
        c.add(field("Theme", self.theme_combo))
        self.grid.add(c)

        #? Connection
        c                   = Card("Connection", "How esptool resets the chip into the bootloader and back.", "plug")
        self.before         = st.bind("conn/before", combo(BEFORE_RESET, current="default-reset"))
        self.after          = st.bind("conn/after", combo(AFTER_RESET, current="hard-reset"))
        c.add(row(field("Before", self.before), field("After", self.after)))
        self.attempts       = QSpinBox()
        self.attempts.setRange(0, 50)
        self.attempts.setValue(7)
        self.attempts.setToolTip("0 = retry forever")
        st.bind("conn/attempts", self.attempts)
        c.add(field("Connect attempts", self.attempts, "Use 'no-reset' + hold BOOT if auto-reset does not work."))
        self.no_stub        = st.bind("conn/no_stub", QCheckBox("Talk to the ROM loader only (--no-stub)"))
        self.reopen         = st.bind("conn/reopen", QCheckBox("Re-open the serial monitor after an operation"))
        self.reopen.setChecked(True)
        c.add(self.no_stub)
        c.add(self.reopen)
        self.grid.add(c)

        #? Profiles
        c                   = Card("Profiles", "Save every field (images, offsets, options) to a JSON file and load it later.",
                                   "save")
        c.add(flow(button("Save profile…", "save", "primary", slot=self.save_profile),
                   button("Load profile…", "folder", slot=self.load_profile),
                   button("Reset connection defaults", "refresh", kind="ghost", slot=self.defaults)))
        self.grid.add(c)

        #? About
        c                   = Card(f"About {APP_NAME}", "", "info")
        logo                = QLabel()
        pm                  = QPixmap(asset("logo.png"))
        if not pm.isNull():
            logo.setPixmap(pm.scaled(96, 96, Qt.AspectRatioMode.KeepAspectRatio,
                                     Qt.TransformationMode.SmoothTransformation))
        info                = QLabel(
            f"<b>{APP_NAME} {__version__}</b><br>"
            f"by <a href='https://github.com/Gueni'>{__author__}</a><br><br>"
            f"esptool {_esptool_version()} · PySide6 {pyside_version}<br>"
            f"Python {platform.python_version()} · {platform.system()} {platform.release()} "
            f"({platform.machine()})<br><br>"
            "Free software under the GNU GPL v3. Uses Espressif's esptool, espefuse and espsecure.")
        info.setWordWrap(True)
        info.setOpenExternalLinks(True)
        info.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        c.add(row(logo, info, stretch=[0, 1]))
        c.add(flow(button("GitHub", "external", slot=lambda: QDesktopServices.openUrl(QUrl(__url__))),
                   button("esptool docs", "external", slot=lambda: QDesktopServices.openUrl(
                       QUrl("https://docs.espressif.com/projects/esptool/en/latest/")))))
        self.grid.add(c, span=2)

        self._apply_saved_theme()

    #?------------------------------------------------------------------------------------------------------------------------------------
    def connection_options(self) -> dict:
        return {"before": self.before.currentText(), "after": self.after.currentText(),
                "connect_attempts": self.attempts.value(), "no_stub": self.no_stub.isChecked()}

    def reopen_monitor(self) -> bool:
        return self.reopen.isChecked()

    def _apply_saved_theme(self) -> None:
        mode                = (app_settings().value("ui/theme", "system") or "system").lower()
        if theme().mode != mode:
            theme().set_mode(mode)

    def _theme_changed(self, text: str) -> None:
        mode                = text.lower()
        app_settings().setValue("ui/theme", mode)
        theme().set_mode(mode)

    def sync_theme_combo(self) -> None:
        self.theme_combo.blockSignals(True)
        self.theme_combo.setCurrentText(theme().palette.name.capitalize())
        self.theme_combo.blockSignals(False)
        app_settings().setValue("ui/theme", theme().mode)

    def save_profile(self) -> None:
        path                = save_path(self, "Save profile", "Flash profile (*.json)", "flash-profile.json")
        if path:
            if not path.lower().endswith(".json"):
                path       += ".json"
            self.ctx.store.export_profile(path)
            self.ctx.toast(f"Profile saved: {Path(path).name}", "success")

    def load_profile(self) -> None:
        path, _             = QFileDialog.getOpenFileName(self, "Load profile", str(Path.home()),
                                                          "Flash profile (*.json);;All files (*)")
        if not path:
            return
        try:
            self.ctx.store.import_profile(path)
        except (OSError, ValueError) as exc:
            self.ctx.toast(f"Could not load profile: {exc}", "error")
            return
        self.ctx.toast(f"Profile loaded: {Path(path).name}", "success")

    def defaults(self) -> None:
        self.before.setCurrentText("default-reset")
        self.after.setCurrentText("hard-reset")
        self.attempts.setValue(7)
        self.no_stub.setChecked(False)
        self.reopen.setChecked(True)
        self.ctx.baud_combo.setCurrentText("460800")
        self.ctx.chip_combo.setCurrentText("auto")
        self.ctx.toast("Connection settings reset", "info")
#?----------------------------------------------------------------------------------------------------------------------------------------
