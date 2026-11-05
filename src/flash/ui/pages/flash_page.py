#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?              ______           __
#?             / __/ /___ ______/ /_        ____  ____ _____ ____
#?            / /_/ / __ `/ ___/ __ \      / __ \/ __ `/ __ `/ _ \
#?           / __/ / /_/ (__  ) / / /     / /_/ / /_/ / /_/ /  __/
#?          /_/ /_/\__,_/____/_/ /_/_____/ .___/\__,_/\__, /\___/
#?                                /_____/_/          /____/
#?
#?
#? Name:        flash_page.py
#? Purpose:     Write firmware: multiple images at offsets, flash options, verify, merge, erase.
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     05/09/2019
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
from    __future__                  import  annotations

import  re
from    pathlib                     import  Path

from    PySide6.QtCore              import  Qt, Signal
from    PySide6.QtWidgets           import  QCheckBox, QFrame, QHBoxLayout, QLabel, QMenu, QToolButton, QVBoxLayout, QWidget

from    flash.core.tools            import  FLASH_FREQS, FLASH_MODES, FLASH_SIZES, LAYOUTS, FlashOptions, Image, ImageSet, human_size
from    flash.ui.widgets            import  Card, FileField, NumberEdit, Page, button, combo, field, flow, icon_button, row, save_path, set_icon
#?----------------------------------------------------------------------------------------------------------------------------------------
_HEX_IN_NAME                = re.compile(r"0x([0-9a-fA-F]{1,8})")
#?----------------------------------------------------------------------------------------------------------------------------------------
def guess_offset(path: str, chip: str) -> str:
    name                    = Path(path).name.lower()
    m                       = _HEX_IN_NAME.search(name)
    if m:
        return "0x" + m.group(1).lower()
    if "boot" in name and "app" not in name:
        if chip in ("esp32", "esp32s2", "auto"):
            return "0x1000"
        if chip in ("esp32p4", "esp32c5"):
            return "0x2000"
        return "0x0"
    if "partition" in name:
        return "0x8000"
    if "ota_data" in name or "otadata" in name:
        return "0xd000"
    return "0x10000"
#?----------------------------------------------------------------------------------------------------------------------------------------
class ImageRow(QFrame):
    removed                 = Signal(object)
    changed                 = Signal()

    def __init__(self, offset: str = "", path: str = "", enabled: bool = True) -> None:
        super().__init__()
        lay                 = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)
        self.check          = QCheckBox()
        self.check.setChecked(enabled)
        self.check.setToolTip("Include this image")
        self.offset         = NumberEdit("0x10000")
        self.offset.setFixedWidth(112)
        self.offset.setText(offset)
        self.file           = FileField("Drop or browse a .bin file…", caption="Select firmware image")
        self.file.setText(path)
        self.size           = QLabel("")
        self.size.setObjectName("Hint")
        self.size.setMinimumWidth(64)
        self.size.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        rm                  = icon_button("x", "Remove image", lambda: self.removed.emit(self))
        lay.addWidget(self.check)
        lay.addWidget(self.offset)
        lay.addWidget(self.file, 1)
        lay.addWidget(self.size)
        lay.addWidget(rm)
        self.file.changed.connect(self._update_size)
        self.file.changed.connect(self.changed)
        self.offset.textChanged.connect(self.changed)
        self.check.toggled.connect(self.changed)
        self._update_size()

    def _update_size(self) -> None:
        p                   = Path(self.file.text())
        self.size.setText(human_size(p.stat().st_size) if p.is_file() else "")

    def image(self) -> Image:
        return Image(self.offset.text().strip(), self.file.text(), self.check.isChecked())
#?----------------------------------------------------------------------------------------------------------------------------------------
class ImageTable(QWidget):
    changed                 = Signal()

    def __init__(self, chip_getter) -> None:
        super().__init__()
        self._chip          = chip_getter
        self.setAcceptDrops(True)
        v                   = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(8)
        head                = QHBoxLayout()
        head.setSpacing(8)
        for text, width in (("", 26), ("OFFSET", 112), ("IMAGE FILE", 0)):
            lab             = QLabel(text)
            lab.setObjectName("FieldLabel")
            if width:
                lab.setFixedWidth(width)
            head.addWidget(lab, 0 if width else 1)
        v.addLayout(head)
        self.rows_box       = QVBoxLayout()
        self.rows_box.setSpacing(8)
        v.addLayout(self.rows_box)
        self.drop_hint      = QLabel("Drop .bin files here - offsets are guessed from the file names")
        self.drop_hint.setObjectName("DropHint")
        self.drop_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_hint.setMinimumHeight(56)
        self.drop_hint.setVisible(False)
        v.addWidget(self.drop_hint)
        self.rows: list[ImageRow] = []

    def add_row(self, offset: str = "", path: str = "", enabled: bool = True) -> ImageRow:
        r                   = ImageRow(offset, path, enabled)
        r.removed.connect(self.remove_row)
        r.changed.connect(self.changed)
        self.rows.append(r)
        self.rows_box.addWidget(r)
        self.changed.emit()
        return r

    def remove_row(self, r: ImageRow) -> None:
        if r in self.rows:
            self.rows.remove(r)
            r.deleteLater()
            self.changed.emit()

    def clear(self) -> None:
        for r in list(self.rows):
            self.remove_row(r)

    def image_set(self) -> ImageSet:
        return ImageSet([r.image() for r in self.rows])

    def to_list(self) -> list[dict]:
        return [{"offset": i.offset, "path": i.path, "enabled": i.enabled} for i in self.image_set().images]

    def from_list(self, data) -> None:
        if not isinstance(data, list):
            return
        self.clear()
        for item in data:
            if isinstance(item, dict):
                self.add_row(str(item.get("offset", "")), str(item.get("path", "")), bool(item.get("enabled", True)))
        if not self.rows:
            self.add_row()

    def add_files(self, paths: list[str]) -> None:
        empty               = [r for r in self.rows if not r.file.text()]
        for p in paths:
            off             = guess_offset(p, self._chip())
            existing        = next((r for r in self.rows if r.offset.text().strip().lower() == off), None)
            target          = existing if existing and not existing.file.text() else (empty.pop(0) if empty else None)
            if target is None:
                self.add_row(off, p)
            else:
                target.offset.setText(off)
                target.file.setText(p)
                if target in empty:
                    empty.remove(target)

    # drag & drop many files at once
    def dragEnterEvent(self, e) -> None:                                               # noqa: N802
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
            self.drop_hint.setVisible(True)

    def dragLeaveEvent(self, e) -> None:                                               # noqa: N802
        self.drop_hint.setVisible(False)

    def dropEvent(self, e) -> None:                                                    # noqa: N802
        self.drop_hint.setVisible(False)
        files               = [u.toLocalFile() for u in e.mimeData().urls() if u.toLocalFile()]
        if files:
            self.add_files(files)
#?----------------------------------------------------------------------------------------------------------------------------------------
class FlashPage(Page):
    title                   = "Flash"
    subtitle                = "Write firmware images to the chip's SPI flash"
    icon_name               = "flash"

    def __init__(self, ctx) -> None:
        super().__init__(ctx)

        #? --- images
        images              = Card("Firmware images", "Tick the images to write. Drag & drop several .bin files at once.",
                                   "layers")
        self.table          = ImageTable(self._chip)
        images.add(self.table)
        self.add_btn        = button("Add image", "plus", slot=lambda: self.table.add_row())
        self.layout_btn     = QToolButton()
        self.layout_btn.setObjectName("Button")
        self.layout_btn.setText("Layout preset")
        set_icon(self.layout_btn, "layers")
        self.layout_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.layout_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        menu                = QMenu(self.layout_btn)
        for name, entries in LAYOUTS.items():
            menu.addAction(name, lambda e=entries: self._apply_layout(e))
        self.layout_btn.setMenu(menu)
        self.add_files_btn  = button("Add files…", "folder", slot=self._pick_files)
        clear_btn           = button("Clear", "trash", kind="ghost", slot=self._clear)
        images.add(flow(self.add_btn, self.add_files_btn, self.layout_btn, clear_btn))
        self.summary        = QLabel("")
        self.summary.setObjectName("Hint")
        images.add(self.summary)
        self.table.changed.connect(self._update_summary)
        self.grid.add(images, span=2)

        #? --- options
        opts                = Card("Flash options", "'keep' preserves the values stored in each image header.", "settings")
        self.mode           = combo(FLASH_MODES, current="keep")
        self.freq           = combo(FLASH_FREQS, current="keep")
        self.size           = combo(FLASH_SIZES, current="detect")
        opts.add(row(field("Mode", self.mode), field("Frequency", self.freq), field("Size", self.size)))
        self.erase_all      = QCheckBox("Erase entire flash before writing")
        self.compress       = QCheckBox("Compress data during transfer (faster)")
        self.compress.setChecked(True)
        self.skip           = QCheckBox("Skip images that are already in flash")
        for w in (self.erase_all, self.compress, self.skip):
            opts.add(w)
        self.grid.add(opts)

        #? --- actions
        act                 = Card("Actions", "Writes are verified automatically by esptool.", "play")
        self.flash_btn      = button("Flash selected images", "flash", "primary", "Write the ticked images (Ctrl+Enter)",
                                     self.flash)
        self.flash_btn.setMinimumHeight(40)
        act.add(self.flash_btn)
        self.verify_btn     = button("Verify", "check", tip="Compare flash contents with the ticked images",
                                     slot=self.verify)
        self.merge_btn      = button("Merge to one .bin", "layers", tip="Combine the ticked images into a single file "
                                     "that can be flashed at 0x0", slot=self.merge)
        self.erase_btn      = button("Erase flash", "eraser", "danger", "Erase the entire flash chip", self.erase)
        act.add(flow(self.verify_btn, self.merge_btn, self.erase_btn))
        self.grid.add(act)

        self.device_actions(self.flash_btn, self.verify_btn, self.merge_btn, self.erase_btn)

        st                  = ctx.store
        for key, w in (("flash/mode", self.mode), ("flash/freq", self.freq), ("flash/size", self.size),
                       ("flash/erase_all", self.erase_all), ("flash/compress", self.compress),
                       ("flash/skip", self.skip)):
            st.bind(key, w)
        st.bind_custom("flash/images", self.table.to_list, self.table.from_list)
        self._apply_layout(LAYOUTS["ESP32 / ESP32-S2"])

        from    PySide6.QtGui               import  QKeySequence, QShortcut
        QShortcut(QKeySequence("Ctrl+Return"), self, self.flash)

    #?------------------------------------------------------------------------------------------------------------------------------------
    def options(self) -> FlashOptions:
        return FlashOptions(self.mode.currentText(), self.freq.currentText(), self.size.currentText(),
                            self.erase_all.isChecked(), self.compress.isChecked(), self.skip.isChecked())

    def _apply_layout(self, entries) -> None:
        old                 = {r.offset.text().strip().lower(): r.file.text() for r in self.table.rows}
        self.table.clear()
        for off, _label in entries:
            self.table.add_row(off, old.get(off, ""))
        for r, (_off, label) in zip(self.table.rows, entries):
            r.file.edit.setPlaceholderText(f"{label}  - drop or browse…")

    def _pick_files(self) -> None:
        from    PySide6.QtWidgets           import  QFileDialog
        files, _            = QFileDialog.getOpenFileNames(self, "Select firmware images", "",
                                                           "Binary files (*.bin);;All files (*)")
        if files:
            self.table.add_files(files)

    def _clear(self) -> None:
        self.table.clear()
        self.table.add_row()

    def _update_summary(self) -> None:
        sel                 = self.table.image_set().selected()
        total               = sum(Path(i.path).stat().st_size for i in sel if Path(i.path).is_file())
        self.summary.setText(f"{len(sel)} image(s) selected · {human_size(total)}" if sel else "No images selected")

    def _chip(self) -> str:
        combo_              = getattr(self.ctx, "chip_combo", None)
        return combo_.currentText() if combo_ is not None else "auto"

    def _checked_images(self) -> ImageSet | None:
        images              = self.table.image_set()
        err                 = images.validate()
        if err:
            self.ctx.toast(err, "error")
            return None
        return images

    #?------------------------------------------------------------------------------------------------------------------------------------
    def flash(self) -> None:
        if self.ctx.runner.busy:
            return
        images              = self._checked_images()
        conn                = self.ctx.require_port() if images else None
        if not conn:
            return
        opts                = self.options()
        if opts.erase_all and not self.ctx.confirm(
                "Erase entire flash?", "All data on the chip (including NVS and file systems) will be lost before "
                "the images are written.", danger=True, ok_text="Erase and flash"):
            return
        args                = conn.esptool_args() + ["write-flash", *opts.args(), *images.pairs()]
        n                   = len(images.selected())
        self.ctx.run("esptool", args, f"Flash {n} image{'s' if n > 1 else ''}")

    def verify(self) -> None:
        images              = self._checked_images()
        conn                = self.ctx.require_port() if images else None
        if conn:
            o               = self.options()
            args            = conn.esptool_args() + ["verify-flash", "--flash-mode", o.mode, "--flash-freq", o.freq,
                                                     "--flash-size", o.size, "--diff", *images.pairs()]
            self.ctx.run("esptool", args, "Verify flash")

    def merge(self) -> None:
        images              = self._checked_images()
        if not images:
            return
        conn                = self.ctx.connection()
        if not self.ctx.require_chip(conn, "Merging images"):
            return
        out                 = save_path(self, "Save merged binary", "Binary files (*.bin);;All files (*)", "merged-firmware.bin")
        if not out:
            return
        o                   = self.options()
        size                = "keep" if o.size == "detect" else o.size
        args                = ["--chip", conn.chip, "merge-bin", "-o", out, "--flash-mode", o.mode, "--flash-freq", o.freq,
                               "--flash-size", size, *images.pairs()]

        def done(code: int) -> None:
            if code == 0:
                self.ctx.log(f"Merged image written to {out} (flash it at offset 0x0)", "success")
        self.ctx.run("esptool", args, "Merge binaries", done, uses_port=False)

    def erase(self) -> None:
        conn                = self.ctx.require_port()
        if conn and self.ctx.confirm("Erase entire flash?", "Every byte of the flash chip will be set to 0xFF. "
                                     "Firmware, NVS and file systems will be lost.", danger=True, ok_text="Erase"):
            self.ctx.run("esptool", conn.esptool_args() + ["erase-flash"], "Erase flash")
#?----------------------------------------------------------------------------------------------------------------------------------------
