#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?                 __          _
#?            ____/ /__ _   __(_)_______        ____  ____ _____ ____
#?           / __  / _ \ | / / / ___/ _ \      / __ \/ __ `/ __ `/ _ \
#?          / /_/ /  __/ |/ / / /__/  __/     / /_/ / /_/ / /_/ /  __/
#?          \__,_/\___/|___/_/\___/\___/_____/ .___/\__,_/\__, /\___/
#?                                    /_____/_/          /____/
#?
#?
#? Name:        device_page.py
#? Purpose:     Identify the connected chip, load programs into RAM, reset / run.
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     05/09/2019
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
from    __future__                  import  annotations

from    flash.ui.widgets            import  Card, FileField, Page, button, field, flow
#?----------------------------------------------------------------------------------------------------------------------------------------
class DevicePage(Page):
    title                   = "Device"
    subtitle                = "Identify the chip and run code from RAM"
    icon_name               = "cpu"

    def __init__(self, ctx) -> None:
        super().__init__(ctx)

        c                   = Card("Chip information", "Results are printed in the console.", "cpu")
        self.btns           = [
            button("Chip ID", "hash", slot=lambda: self._simple("chip-id", "Read chip ID")),
            button("MAC address", "scan", slot=lambda: self._simple("read-mac", "Read MAC address")),
            button("Flash ID & size", "memory", slot=lambda: self._simple("flash-id", "Read flash ID")),
            button("Security info", "shield", slot=lambda: self._simple("get-security-info", "Security info")),
        ]
        self.btns[0].setProperty("kind", "primary")
        c.add(flow(*self.btns))
        self.grid.add(c)

        c                   = Card("Load into RAM", "Upload an IRAM/DRAM-only image and execute it immediately (no flash write).",
                                   "upload")
        self._ram_field     = FileField(caption="Program to load into RAM")
        self.ram_file       = ctx.store.bind("device/ram_file", self._ram_field.edit)
        c.add(field("Image", self._ram_field))
        self.ram_btn        = button("Load & run", "play", slot=self.load_ram)
        c.add(flow(self.ram_btn))
        self.grid.add(c)

        c                   = Card("Reset", "Restart the chip and run the application already in flash.", "power")
        self.run_btn        = button("Run application", "power", slot=lambda: self._simple("run", "Run application"))
        c.add(flow(self.run_btn))
        self.grid.add(c)

        self.device_actions(*self.btns, self.ram_btn, self.run_btn)

    def _simple(self, command: str, title: str) -> None:
        if conn := self.ctx.require_port():
            self.ctx.run("esptool", conn.esptool_args() + [command], title)

    def load_ram(self) -> None:
        path                = self.ram_file.text().strip()
        if not path:
            self._ram_field.pick()
            path            = self.ram_file.text().strip()
        if not path:
            return
        if conn := self.ctx.require_port():
            conn.no_stub    = True                                                     # RAM loading talks to the ROM loader directly
            self.ctx.run("esptool", conn.esptool_args() + ["load-ram", path], "Load RAM")
#?----------------------------------------------------------------------------------------------------------------------------------------
