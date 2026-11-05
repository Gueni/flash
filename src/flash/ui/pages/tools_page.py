#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?             __              __
#?            / /_____  ____  / /____      ____  ____ _____ ____
#?           / __/ __ \/ __ \/ / ___/     / __ \/ __ `/ __ `/ _ \
#?          / /_/ /_/ / /_/ / (__  )     / /_/ / /_/ / /_/ /  __/
#?          \__/\____/\____/_/____/_____/ .___/\__,_/\__, /\___/
#?                               /_____/_/          /____/
#?
#?
#? Name:        tools_page.py
#? Purpose:     Offline image tools and flash-encryption key management.
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     05/09/2019
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
from    __future__                  import  annotations

from    pathlib                     import  Path

from    PySide6.QtWidgets           import  QCheckBox

from    flash.ui.widgets            import  Card, FileField, Page, button, combo, field, flow, row, save_path
#?----------------------------------------------------------------------------------------------------------------------------------------
KEY_BLOCKS_ESP32            = ["flash_encryption", "secure_boot_v1", "secure_boot_v2", "BLOCK1", "BLOCK2", "BLOCK3"]
KEY_BLOCKS                  = ["BLOCK_KEY0", "BLOCK_KEY1", "BLOCK_KEY2", "BLOCK_KEY3", "BLOCK_KEY4", "BLOCK_KEY5"]
KEY_PURPOSES                = ["XTS_AES_128_KEY", "XTS_AES_256_KEY_1", "XTS_AES_256_KEY_2", "HMAC_UP", "HMAC_DOWN_ALL",
                               "HMAC_DOWN_JTAG", "HMAC_DOWN_DIGITAL_SIGNATURE", "SECURE_BOOT_DIGEST0", "USER"]
#?----------------------------------------------------------------------------------------------------------------------------------------
class ToolsPage(Page):
    title                   = "Tools"
    subtitle                = "Convert and inspect images, manage encryption keys"
    icon_name               = "tools"

    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        st                  = ctx.store

        #? ELF -> BIN
        c                   = Card("ELF to binary", "Build a flashable application image from an ELF file. Needs an explicit chip.",
                                   "file")
        self.elf            = FileField("Select .elf file…", "ELF files (*.elf);;All files (*)", caption="Select ELF")
        st.bind("tools/elf", self.elf.edit)
        self.elf_ver        = st.bind("tools/elf_ver", combo(["1", "2", "3"], current="1"))
        c.add(field("ELF file", self.elf))
        c.add(field("Image version", self.elf_ver, "Version 1 for most chips; ESP8266 SDKs may need 2."))
        self.elf_btn        = button("Convert…", "play", "primary", slot=self.elf2image)
        c.add(flow(self.elf_btn))
        self.grid.add(c)

        #? Image info
        c                   = Card("Image info", "Show header, segments and checksums of a firmware or bootloader image.", "image")
        self.info_file      = FileField(caption="Select image")
        st.bind("tools/info_file", self.info_file.edit)
        c.add(field("Image", self.info_file))
        self.info_btn       = button("Show info", "search", slot=self.image_info)
        c.add(flow(self.info_btn))
        self.grid.add(c)

        #? Flash encryption
        c                   = Card("Flash encryption key", "Generate a development key, then burn it into an eFuse key block. "
                                   "Burning is permanent.", "key", danger=True)
        self.key_file       = FileField("Key file (.bin)", caption="Select key file")
        st.bind("tools/key_file", self.key_file.edit)
        c.add(field("Key file", self.key_file))
        self.key_len        = st.bind("tools/key_len", combo(["256", "512", "128"], current="256"))
        self.block          = st.bind("tools/key_block", combo(KEY_BLOCKS_ESP32 + KEY_BLOCKS, editable=True,
                                                               current="flash_encryption"))
        self.purpose        = st.bind("tools/key_purpose", combo(KEY_PURPOSES, current="XTS_AES_128_KEY"))
        c.add(row(field("Key bits", self.key_len), field("Block", self.block), field("Purpose", self.purpose)))
        self.no_rp          = st.bind("tools/no_rp", QCheckBox("Keep key readable (no read-protect) - insecure, dev only"))
        c.add(self.no_rp)
        self.gen_btn        = button("Generate key…", "key", slot=self.generate_key)
        self.burn_btn       = button("Burn key", "flame", "danger", slot=self.burn_key)
        c.add(flow(self.gen_btn, self.burn_btn))
        self.grid.add(c)

        self.device_actions(self.elf_btn, self.info_btn, self.gen_btn, self.burn_btn)
        self.chip_changed("auto")

    def chip_changed(self, chip: str) -> None:
        self.purpose.setEnabled(chip not in ("esp32", "auto", "esp8266"))
        if chip == "esp32" and self.block.currentText().startswith("BLOCK_KEY"):
            self.block.setCurrentText("flash_encryption")
        elif chip not in ("esp32", "auto") and self.block.currentText() == "flash_encryption":
            self.block.setCurrentText("BLOCK_KEY0")

    def elf2image(self) -> None:
        elf                 = self.elf.text()
        if not Path(elf).is_file():
            self.ctx.toast("Select an existing ELF file first.", "error")
            return
        conn                = self.ctx.connection()
        if not self.ctx.require_chip(conn, "ELF conversion"):
            return
        default             = Path(elf).with_suffix(".bin")
        out                 = save_path(self, "Save application image", "Binary files (*.bin);;All files (*)", default.name)
        if not out:
            return
        args                = ["--chip", conn.chip, "elf2image", "--version", self.elf_ver.currentText(), "-o", out, elf]
        self.ctx.run("esptool", args, "ELF to binary", uses_port=False)

    def image_info(self) -> None:
        f                   = self.info_file.text()
        if not f:
            f               = self.info_file.pick()
        if not f or not Path(f).is_file():
            return
        chip                = self.ctx.connection().chip
        self.ctx.run("esptool", ["--chip", chip, "image-info", f], "Image info", uses_port=False)

    def generate_key(self) -> None:
        out                 = save_path(self, "Save new flash encryption key", "Key files (*.bin);;All files (*)",
                                        "flash_encryption_key.bin")
        if not out:
            return
        if Path(out).exists():
            Path(out).unlink()                                                         # espsecure refuses to overwrite; the dialog already asked

        def done(code: int) -> None:
            if code == 0:
                self.key_file.setText(out)
                self.ctx.log("Keep this key file safe - it is needed to re-flash an encrypted device.", "warning")
        self.ctx.run("espsecure", ["generate-flash-encryption-key", "--keylen", self.key_len.currentText(), out],
                     "Generate key", done, uses_port=False)

    def burn_key(self) -> None:
        key                 = self.key_file.text()
        if not Path(key).is_file():
            self.ctx.toast("Select or generate a key file first.", "error")
            return
        conn                = self.ctx.require_port()
        if not conn:
            return
        block               = self.block.currentText().strip()
        if not self.ctx.confirm(
                "Burn encryption key?",
                f"The key in <b>{Path(key).name}</b> will be burned into <b>{block}</b>.<br><br>"
                "eFuses can never be reset. A mistake can permanently lock the chip.",
                danger=True, ok_text="Burn permanently"):
            return
        args                = conn.espefuse_args() + ["--do-not-confirm", "burn-key"]
        if self.no_rp.isChecked():
            args.append("--no-read-protect")
        args               += [block, key]
        if self.purpose.isEnabled():
            args.append(self.purpose.currentText())
        self.ctx.run("espefuse", args, "Burn key")
#?----------------------------------------------------------------------------------------------------------------------------------------
