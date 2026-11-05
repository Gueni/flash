#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?             ____ ___  ___  ____ ___  ____  _______  __      ____  ____ _____ ____
#?            / __ `__ \/ _ \/ __ `__ \/ __ \/ ___/ / / /     / __ \/ __ `/ __ `/ _ \
#?           / / / / / /  __/ / / / / / /_/ / /  / /_/ /     / /_/ / /_/ / /_/ /  __/
#?          /_/ /_/ /_/\___/_/ /_/ /_/\____/_/   \__, /_____/ .___/\__,_/\__, /\___/
#?                                              /____/_____/_/          /____/
#?
#?
#? Name:        memory_page.py
#? Purpose:     Read / erase flash regions, peek & poke RAM words, dump memory, flash status register.
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     05/09/2019
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
from    __future__                  import  annotations

from    PySide6.QtWidgets           import  QCheckBox

from    flash.ui.widgets            import  Card, NumberEdit, Page, button, combo, field, flow, row, save_path
#?----------------------------------------------------------------------------------------------------------------------------------------
class MemoryPage(Page):
    title                   = "Memory"
    subtitle                = "Read, erase and inspect flash and RAM"
    icon_name               = "memory"

    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        st                  = ctx.store

        #? Read flash
        c                   = Card("Read flash to file", "Back up firmware or data partitions. Size accepts 'ALL'.", "download")
        self.rf_addr        = st.bind("mem/rf_addr", NumberEdit("0x0"))
        self.rf_size        = st.bind("mem/rf_size", NumberEdit("0x400000 or ALL", allow_all=True))
        c.add(row(field("Start address", self.rf_addr), field("Size", self.rf_size)))
        self.rf_btn         = button("Read flash…", "download", "primary", slot=self.read_flash)
        c.add(flow(self.rf_btn))
        self.grid.add(c)

        #? Erase region
        c                   = Card("Erase region", "Address and size must be multiples of the 4 KB sector size (0x1000).",
                                   "eraser", danger=True)
        self.er_addr        = st.bind("mem/er_addr", NumberEdit("0x9000"))
        self.er_size        = st.bind("mem/er_size", NumberEdit("0x6000"))
        c.add(row(field("Start address", self.er_addr), field("Size", self.er_size)))
        self.er_btn         = button("Erase region", "eraser", "danger", slot=self.erase_region)
        c.add(flow(self.er_btn))
        self.grid.add(c)

        #? Read / write memory word
        c                   = Card("Memory word (peek / poke)", "Read or write a single 32-bit word - useful for registers.", "hash")
        self.rm_addr        = st.bind("mem/rm_addr", NumberEdit("0x3ff00000"))
        self.rm_btn         = button("Read word", "search", slot=self.read_mem)
        c.add(field("Address", self.rm_addr))
        self.wm_value       = st.bind("mem/wm_value", NumberEdit("0x00000000"))
        self.wm_mask        = st.bind("mem/wm_mask", NumberEdit("0xFFFFFFFF", required=False))
        c.add(row(field("Value", self.wm_value), field("Mask (optional)", self.wm_mask)))
        self.wm_btn         = button("Write word", "upload", slot=self.write_mem)
        c.add(flow(self.rm_btn, self.wm_btn))
        self.grid.add(c)

        #? Dump memory
        c                   = Card("Dump memory", "Copy a region of the chip's address space (RAM/ROM) to a file.", "save")
        self.dm_addr        = st.bind("mem/dm_addr", NumberEdit("0x3ffb0000"))
        self.dm_size        = st.bind("mem/dm_size", NumberEdit("0x2000"))
        c.add(row(field("Start address", self.dm_addr), field("Size", self.dm_size)))
        self.dm_btn         = button("Dump to file…", "save", slot=self.dump_mem)
        c.add(flow(self.dm_btn))
        self.grid.add(c)

        #? Flash status
        c                   = Card("Flash status register", "Debug write-protection problems (RDSR / WRSR commands).", "activity")
        self.rs_bytes       = st.bind("mem/rs_bytes", combo(["1", "2", "3"], current="2"))
        self.ws_value       = st.bind("mem/ws_value", NumberEdit("0x0"))
        self.ws_nv          = st.bind("mem/ws_nv", QCheckBox("Non-volatile"))
        c.add(row(field("Bytes", self.rs_bytes), field("New value", self.ws_value)))
        c.add(self.ws_nv)
        self.rs_btn         = button("Read status", "search", slot=self.read_status)
        self.ws_btn         = button("Write status", "upload", "danger", slot=self.write_status)
        c.add(flow(self.rs_btn, self.ws_btn))
        self.grid.add(c)

        self.device_actions(self.rf_btn, self.er_btn, self.rm_btn, self.wm_btn, self.dm_btn, self.rs_btn,
                            self.ws_btn)

    #?------------------------------------------------------------------------------------------------------------------------------------
    def _need(self, *edits: NumberEdit) -> bool:
        for e in edits:
            if not e.is_valid():
                e.setFocus()
                self.ctx.toast("Please enter a valid address / size (hex like 0x1000 or decimal).", "error")
                return False
        return True

    def read_flash(self) -> None:
        if not self._need(self.rf_addr, self.rf_size):
            return
        conn                = self.ctx.require_port()
        if not conn:
            return
        out                 = save_path(self, "Save flash contents", "Binary files (*.bin);;All files (*)", "flash-dump.bin")
        if out:
            self.ctx.run("esptool", conn.esptool_args() + ["read-flash", self.rf_addr.arg(), self.rf_size.arg(), out],
                         "Read flash")

    def erase_region(self) -> None:
        if not self._need(self.er_addr, self.er_size):
            return
        conn                = self.ctx.require_port()
        if conn and self.ctx.confirm("Erase flash region?",
                                     f"Erase {self.er_size.arg()} bytes starting at {self.er_addr.arg()}?",
                                     danger=True, ok_text="Erase"):
            self.ctx.run("esptool", conn.esptool_args() + ["erase-region", self.er_addr.arg(), self.er_size.arg()],
                         "Erase region")

    def read_mem(self) -> None:
        if self._need(self.rm_addr) and (conn := self.ctx.require_port()):
            self.ctx.run("esptool", conn.esptool_args() + ["read-mem", self.rm_addr.arg()], "Read memory")

    def write_mem(self) -> None:
        if not self._need(self.rm_addr, self.wm_value, self.wm_mask):
            return
        conn                = self.ctx.require_port()
        if conn:
            args            = ["write-mem", self.rm_addr.arg(), self.wm_value.arg()]
            if self.wm_mask.text().strip():
                args.append(self.wm_mask.arg())
            self.ctx.run("esptool", conn.esptool_args() + args, "Write memory")

    def dump_mem(self) -> None:
        if not self._need(self.dm_addr, self.dm_size):
            return
        conn                = self.ctx.require_port()
        if not conn:
            return
        out                 = save_path(self, "Save memory dump", "Binary files (*.bin);;All files (*)", "memory-dump.bin")
        if out:
            self.ctx.run("esptool", conn.esptool_args() + ["dump-mem", self.dm_addr.arg(), self.dm_size.arg(), out],
                         "Dump memory")

    def read_status(self) -> None:
        if conn := self.ctx.require_port():
            self.ctx.run("esptool", conn.esptool_args() + ["read-flash-status", "--bytes", self.rs_bytes.currentText()],
                         "Read flash status")

    def write_status(self) -> None:
        if not self._need(self.ws_value):
            return
        conn                = self.ctx.require_port()
        if conn and self.ctx.confirm("Write flash status register?",
                                     "A wrong value can write-protect the flash chip.", danger=True, ok_text="Write"):
            args            = ["write-flash-status", "--bytes", self.rs_bytes.currentText()]
            if self.ws_nv.isChecked():
                args.append("--non-volatile")
            args.append(self.ws_value.arg())
            self.ctx.run("esptool", conn.esptool_args() + args, "Write flash status")
#?----------------------------------------------------------------------------------------------------------------------------------------
