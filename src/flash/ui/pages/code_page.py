#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?                            __
#?            _________  ____/ /__        ____  ____ _____ ____
#?           / ___/ __ \/ __  / _ \      / __ \/ __ `/ __ `/ _ \
#?          / /__/ /_/ / /_/ /  __/     / /_/ / /_/ / /_/ /  __/
#?          \___/\____/\__,_/\___/_____/ .___/\__,_/\__, /\___/
#?                              /_____/_/          /____/
#?
#?
#? Name:        code_page.py
#? Purpose:     Code page: an Arduino-style IDE - write sketches, compile and upload them to ESP32 / ESP8266 / AVR / STM32 /
#?              RP2040.
#?              Compiling, uploading, cores and libraries are handled by arduino-cli; the upload port is the PORT selected in
#?              the connection bar. Compiler errors are marked in the editor and clickable in the console.
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     05/09/2019
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
from    __future__                  import  annotations

import  json
import  os
import  re
import  shutil
from    pathlib                     import  Path

from    PySide6.QtCore              import  QSize, Qt, QTimer
from    PySide6.QtGui               import  QAction, QActionGroup, QKeySequence, QShortcut
from    PySide6.QtWidgets           import  (QComboBox, QFileDialog, QFrame, QHBoxLayout, QInputDialog, QLabel, QMenu, QMessageBox, QProgressBar,
                                             QPushButton, QTabWidget, QToolButton, QVBoxLayout, QWidget)

from    flash.core                  import  arduino
from    flash.settings              import  app_settings
from    flash.ui.code_editor        import  CodeEditor, FindBar, Marker
from    flash.ui.widgets            import  FlowLayout, button, icon_button, set_icon
#?----------------------------------------------------------------------------------------------------------------------------------------
SIZE_RE                     = re.compile(r"(Sketch uses .*|Global variables use .*)")
DEFAULT_FQBN                = "esp32:esp32:esp32"
#?----------------------------------------------------------------------------------------------------------------------------------------
def _same_path(a: str | Path, b: str | Path) -> bool:
    try:
        return os.path.normcase(str(Path(a).resolve())) == os.path.normcase(str(Path(b).resolve()))
    except OSError:
        return False
#?----------------------------------------------------------------------------------------------------------------------------------------
class CodePage(QWidget):
    title                   = "Code"
    subtitle                = "Write, compile and upload Arduino sketches"
    icon_name               = "code"

    def __init__(self, ctx) -> None:
        super().__init__()
        self.ctx            = ctx
        self.sketch: Path | None = None
        self.editors: list[tuple[Path, CodeEditor]] = []
        self.boards: list[arduino.Board] = []
        self.board_options: list[arduino.BoardOption] = []
        self.option_values: dict[str, str] = {}
        self._queries: list = []
        self._collecting    = False
        self._diagnostics: list[arduino.Diagnostic] = []
        self._size_lines: list[str] = []
        self._downloader    = None
        self._boards_loaded = False
        self._examples: dict[str, list[str]] | None = None
        self._dialogs: dict[str, QWidget] = {}

        v                   = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)
        v.addWidget(self._build_toolbar())
        v.addWidget(self._build_cli_banner())
        self.tabs           = QTabWidget()
        self.tabs.setObjectName("EditorTabs")
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(False)
        self.tabs.tabBar().setDrawBase(False)
        self.tabs.currentChanged.connect(self._tab_changed)
        self.tabs.tabBar().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabs.tabBar().customContextMenuRequested.connect(self._tab_menu)
        add                 = icon_button("plus", "New file in this sketch (.h / .cpp / .ino)", self.new_file)
        self.tabs.setCornerWidget(add, Qt.Corner.TopRightCorner)
        v.addWidget(self.tabs, 1)
        self.find_bar       = FindBar(self.current_editor)
        v.addWidget(self.find_bar)
        v.addWidget(self._build_footer())

        self._shortcuts()
        self.ctx.runner.line.connect(self._collect_line)
        QTimer.singleShot(0, self._initial_sketch)

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? Construction
    #?------------------------------------------------------------------------------------------------------------------------------------
    def _build_toolbar(self) -> QWidget:
        bar                 = QFrame()
        bar.setObjectName("CodeToolbar")
        fl                  = FlowLayout(bar, spacing=8)
        fl.setContentsMargins(16, 10, 16, 10)

        self.verify_btn     = button("Verify", "check", tip="Compile the sketch (Ctrl+R)", slot=self.verify)
        self.upload_btn     = button("Upload", "upload", "primary", "Compile and upload to the board on PORT (Ctrl+U)",
                                     self.upload)
        fl.addWidget(self.verify_btn)
        fl.addWidget(self.upload_btn)

        self.file_btn       = QToolButton()
        self.file_btn.setObjectName("Button")
        self.file_btn.setText(" Sketch")
        set_icon(self.file_btn, "file")
        self.file_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.file_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.file_menu      = QMenu(self.file_btn)
        self.file_menu.aboutToShow.connect(self._fill_file_menu)
        self.file_btn.setMenu(self.file_menu)
        fl.addWidget(self.file_btn)

        self.save_btn       = icon_button("save", "Save (Ctrl+S)", self.save_all)
        fl.addWidget(self.save_btn)

        self.examples_btn   = QToolButton()
        self.examples_btn.setObjectName("Button")
        self.examples_btn.setText(" Examples")
        set_icon(self.examples_btn, "book")
        self.examples_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.examples_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.examples_menu  = QMenu(self.examples_btn)
        self.examples_menu.aboutToShow.connect(self._fill_examples_menu)
        self.examples_btn.setMenu(self.examples_menu)
        fl.addWidget(self.examples_btn)

        board_box           = QWidget()
        hb                  = QHBoxLayout(board_box)
        hb.setContentsMargins(0, 0, 0, 0)
        hb.setSpacing(6)
        lab                 = QLabel("BOARD")
        lab.setObjectName("FieldLabel")
        hb.addWidget(lab)
        self.board_combo    = QComboBox()
        self.board_combo.setEditable(True)
        self.board_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.board_combo.setMinimumWidth(250)
        self.board_combo.setMaxVisibleItems(18)
        self.board_combo.setToolTip("Target board (type to search). Install more in the Boards manager.")
        self.board_combo.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        self.board_combo.completer().setCompletionMode(self.board_combo.completer().CompletionMode.PopupCompletion)
        self.board_combo.activated.connect(self._board_chosen)
        self.board_combo.lineEdit().editingFinished.connect(self._board_text_entered)
        hb.addWidget(self.board_combo)
        self.options_btn    = QToolButton()
        self.options_btn.setObjectName("Ghost")
        set_icon(self.options_btn, "settings")
        self.options_btn.setToolTip("Board options (partition scheme, upload speed, CPU frequency, ...)")
        self.options_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.options_menu   = QMenu(self.options_btn)
        self.options_btn.setMenu(self.options_menu)
        hb.addWidget(self.options_btn)
        self.detect_btn     = icon_button("scan", "Detect the board connected on PORT", self.detect_board)
        hb.addWidget(self.detect_btn)
        fl.addWidget(board_box)

        self.boards_btn     = button("Boards", "cpu", kind="ghost", tip="Boards manager: install ESP32, ESP8266, AVR, "
                                     "STM32, RP2040 ... cores", slot=lambda: self.open_manager("boards"))
        self.libs_btn       = button("Libraries", "library", kind="ghost", tip="Library manager",
                                     slot=lambda: self.open_manager("libraries"))
        fl.addWidget(self.boards_btn)
        fl.addWidget(self.libs_btn)
        return bar

    def _build_cli_banner(self) -> QWidget:
        self.banner         = QFrame()
        self.banner.setObjectName("Card")
        lay                 = QHBoxLayout(self.banner)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(12)
        self.banner_text    = QLabel("<b>arduino-cli is needed to compile and upload.</b> "
                                     "It is the official Arduino engine (about 20 MB) and is downloaded once.")
        self.banner_text.setWordWrap(True)
        lay.addWidget(self.banner_text, 1)
        self.banner_progress = QProgressBar()
        self.banner_progress.setFixedWidth(180)
        self.banner_progress.setFixedHeight(8)
        self.banner_progress.hide()
        lay.addWidget(self.banner_progress)
        self.banner_btn     = button("Download arduino-cli", "download", "primary", slot=self.download_cli)
        lay.addWidget(self.banner_btn)
        wrap                = QWidget()
        wl                  = QVBoxLayout(wrap)
        wl.setContentsMargins(16, 12, 16, 0)
        wl.addWidget(self.banner)
        self.banner_wrap    = wrap
        wrap.setVisible(arduino.find_cli() is None)
        return wrap

    def _build_footer(self) -> QWidget:
        bar                 = QFrame()
        bar.setObjectName("CodeFooter")
        lay                 = QHBoxLayout(bar)
        lay.setContentsMargins(16, 4, 16, 4)
        lay.setSpacing(16)
        self.path_label     = QLabel("")
        self.path_label.setObjectName("Hint")
        self.path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.size_label     = QLabel("")
        self.size_label.setObjectName("Hint")
        self.pos_label      = QLabel("Ln 1, Col 1")
        self.pos_label.setObjectName("Hint")
        lay.addWidget(self.path_label, 1)
        lay.addWidget(self.size_label)
        lay.addWidget(self.pos_label)
        return bar

    def _shortcuts(self) -> None:
        def sc(keys: str, slot) -> None:
            s               = QShortcut(QKeySequence(keys), self)
            s.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
            s.activated.connect(slot)

        sc("Ctrl+R", self.verify)
        sc("Ctrl+U", self.upload)
        sc("Ctrl+S", self.save_all)
        sc("Ctrl+Shift+S", self.save_as)
        sc("Ctrl+N", self.new_sketch)
        sc("Ctrl+O", self.open_sketch)
        sc("Ctrl+F", lambda: self.find_bar.open_bar(False))
        sc("Ctrl+H", lambda: self.find_bar.open_bar(True))
        sc("F3", self.find_bar.next)
        sc("Shift+F3", lambda: self.find_bar.next(back=True))
        sc("Ctrl+G", self.goto_line)
        sc("Ctrl+/", lambda: self.current_editor() and self.current_editor().toggle_comment())
        sc("Ctrl+=", lambda: self._zoom(1))
        sc("Ctrl++", lambda: self._zoom(1))
        sc("Ctrl+-", lambda: self._zoom(-1))

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? Page protocol (used by MainWindow)
    #?------------------------------------------------------------------------------------------------------------------------------------
    def set_busy(self, busy: bool) -> None:
        for w in (self.verify_btn, self.upload_btn, self.boards_btn, self.libs_btn, self.detect_btn):
            w.setEnabled(not busy)
        for dlg in self._dialogs.values():
            if hasattr(dlg, "set_busy"):
                dlg.set_busy(busy)

    def showEvent(self, event) -> None:                                                # noqa: N802
        super().showEvent(event)
        has_cli             = arduino.find_cli() is not None
        self.banner_wrap.setVisible(not has_cli and self._downloader is None)
        if has_cli and not self._boards_loaded:
            self.refresh_boards()
        ed                  = self.current_editor()
        if ed is not None:
            ed.setFocus()

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? Sketch files
    #?------------------------------------------------------------------------------------------------------------------------------------
    def scratch_root(self) -> Path:
        return arduino.user_data_dir() / "sketches"

    def _initial_sketch(self) -> None:
        last                = app_settings().value("code/sketch", "")
        if last and arduino.main_sketch_file(last).is_file():
            self.load_sketch(Path(last))
        else:
            self._new_untitled()

    def _new_untitled(self) -> None:
        root                = self.scratch_root()
        root.mkdir(parents=True, exist_ok=True)
        name                = arduino.unique_sketch_name(root)
        self.load_sketch(arduino.create_sketch(root, name).parent)

    def is_scratch(self) -> bool:
        return self.sketch is not None and _same_path(self.sketch.parent, self.scratch_root())

    def load_sketch(self, folder: Path) -> None:
        folder              = arduino.sketch_dir(folder)
        self.tabs.blockSignals(True)
        while self.tabs.count():
            w               = self.tabs.widget(0)
            self.tabs.removeTab(0)
            w.deleteLater()
        self.tabs.blockSignals(False)
        self.editors        = []
        self.sketch         = folder
        for path in arduino.sketch_files(folder):
            self._add_editor(path)
        if not self.editors:
            self._add_editor(arduino.main_sketch_file(folder))
        self.tabs.setCurrentIndex(0)
        app_settings().setValue("code/sketch", str(folder))
        if not self.is_scratch():
            self._remember_recent(folder)
        self._update_path_label()
        self.size_label.setText("")

    def _add_editor(self, path: Path) -> CodeEditor:
        ed                  = CodeEditor()
        try:
            ed.setPlainText(path.read_text(encoding="utf-8", errors="replace") if path.exists() else "")
        except OSError as exc:
            self.ctx.toast(f"Cannot read {path.name}: {exc}", "error")
        ed.document().setModified(False)
        ed.modified.connect(lambda _m, e=ed: self._update_tab_title(e))
        ed.cursor_moved.connect(lambda l, c: self.pos_label.setText(f"Ln {l}, Col {c}"))
        self.editors.append((path, ed))
        self.tabs.addTab(ed, path.name)
        self.tabs.setTabToolTip(self.tabs.count() - 1, str(path))
        return ed

    def _update_tab_title(self, ed: CodeEditor) -> None:
        for i, (path, e) in enumerate(self.editors):
            if e is ed:
                self.tabs.setTabText(i, ("● " if ed.document().isModified() else "") + path.name)

    def _update_path_label(self) -> None:
        if self.sketch is None:
            return
        where               = "unsaved sketch - use Save As to keep it" if self.is_scratch() else str(self.sketch)
        self.path_label.setText(f"{self.sketch.name}  ·  {where}")

    def current_editor(self) -> CodeEditor | None:
        w                   = self.tabs.currentWidget()
        return w if isinstance(w, CodeEditor) else None

    def _tab_changed(self, _i: int) -> None:
        if self.find_bar.isVisible():
            self.find_bar.refresh()

    def dirty(self) -> bool:
        return any(ed.document().isModified() for _p, ed in self.editors)

    def save_all(self) -> bool:
        ok                  = True
        for path, ed in self.editors:
            try:
                differs     = not path.exists() or path.read_text(encoding="utf-8", errors="replace") != ed.toPlainText()
            except OSError:
                differs     = True
            if ed.document().isModified() or differs:
                try:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(ed.toPlainText(), encoding="utf-8", newline="\n")
                    ed.document().setModified(False)
                except OSError as exc:
                    ok      = False
                    self.ctx.toast(f"Could not save {path.name}: {exc}", "error")
        return ok

    def maybe_save(self) -> bool:
        """Ask about unsaved changes. Returns False if the user cancelled."""
        if not self.dirty():
            return True
        if self.is_scratch():
            return self.save_all()                                                     # untitled sketches are kept silently, like Arduino IDE 2
        box                 = QMessageBox(self)
        box.setWindowTitle("Unsaved changes")
        box.setText(f"<b>Save changes to {self.sketch.name}?</b>")
        box.setStandardButtons(QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard |
                               QMessageBox.StandardButton.Cancel)
        box.setDefaultButton(QMessageBox.StandardButton.Save)
        answer              = box.exec()
        if answer == QMessageBox.StandardButton.Cancel:
            return False
        if answer == QMessageBox.StandardButton.Save:
            return self.save_all()
        return True

    def new_sketch(self) -> None:
        if self.maybe_save():
            self._new_untitled()
            self.ctx.toast("New sketch - use Save As to give it a name and folder", "info")

    def open_sketch(self) -> None:
        if not self.maybe_save():
            return
        start               = str(arduino.default_sketchbook() if arduino.default_sketchbook().is_dir() else Path.home())
        path, _             = QFileDialog.getOpenFileName(self, "Open sketch", start, "Arduino sketch (*.ino *.pde);;All files (*)")
        if path:
            self._open_existing(Path(path))

    def _open_existing(self, path: Path) -> None:
        folder              = path.parent if path.is_file() else path
        if path.is_file() and path.stem != folder.name:
            # Arduino requires <name>/<name>.ino - offer to move the file into its own folder
            if not self.ctx.confirm("Move into a sketch folder?",
                                    f"Arduino sketches must live in a folder with the same name.<br>"
                                    f"Create <b>{path.stem}/</b> and move <b>{path.name}</b> into it?",
                                    ok_text="Create folder"):
                return
            target          = folder / path.stem
            target.mkdir(exist_ok=True)
            shutil.move(str(path), str(target / path.name))
            folder          = target
        self.load_sketch(folder)

    def save_as(self) -> None:
        if self.sketch is None:
            return
        base                = arduino.default_sketchbook()
        base.mkdir(parents=True, exist_ok=True)
        name, ok            = QInputDialog.getText(self, "Save sketch as", "Sketch name:", text=self.sketch.name)
        if not ok or not name.strip():
            return
        name                = name.strip()
        if not arduino.VALID_SKETCH_NAME.match(name):
            self.ctx.toast("Use letters, digits, '_', '-' or '.' for sketch names.", "error")
            return
        parent              = QFileDialog.getExistingDirectory(self, "Choose where to save the sketch", str(base))
        if not parent:
            return
        target              = Path(parent) / name
        if target.exists():
            self.ctx.toast(f"{target} already exists.", "error")
            return
        target.mkdir(parents=True)
        main_old            = arduino.main_sketch_file(self.sketch)
        for path, ed in self.editors:
            new_name        = f"{name}{path.suffix}" if _same_path(path, main_old) else path.name
            (target / new_name).write_text(ed.toPlainText(), encoding="utf-8", newline="\n")
        was_scratch, old    = self.is_scratch(), self.sketch
        self.load_sketch(target)
        if was_scratch:
            shutil.rmtree(old, ignore_errors=True)
        self.ctx.toast(f"Saved as {target}", "success")

    def new_file(self) -> None:
        if self.sketch is None:
            return
        name, ok            = QInputDialog.getText(self, "New file", "File name (e.g. config.h, helpers.cpp):")
        if not ok or not name.strip():
            return
        name                = name.strip()
        if Path(name).suffix not in arduino.SKETCH_EXTENSIONS:
            name           += ".h"
        path                = self.sketch / name
        if path.exists() or any(_same_path(p, path) for p, _e in self.editors):
            self.ctx.toast(f"{name} already exists in this sketch.", "error")
            return
        path.write_text("#pragma once\n\n" if path.suffix in (".h", ".hpp") else "", encoding="utf-8")
        self._add_editor(path)
        self.tabs.setCurrentIndex(self.tabs.count() - 1)

    def _tab_menu(self, pos) -> None:
        index               = self.tabs.tabBar().tabAt(pos)
        if index < 0:
            return
        path, ed            = self.editors[index]
        menu                = QMenu(self)
        main                = arduino.main_sketch_file(self.sketch)
        rename              = menu.addAction("Rename…")
        delete              = menu.addAction("Delete file")
        rename.setEnabled(not _same_path(path, main))
        delete.setEnabled(not _same_path(path, main))
        chosen              = menu.exec(self.tabs.tabBar().mapToGlobal(pos))
        if chosen is delete and self.ctx.confirm("Delete file?", f"Delete <b>{path.name}</b> from the sketch?",
                                                 danger=True, ok_text="Delete"):
            path.unlink(missing_ok=True)
            self.tabs.removeTab(index)
            self.editors.pop(index)
            ed.deleteLater()
        elif chosen is rename:
            name, ok        = QInputDialog.getText(self, "Rename file", "New name:", text=path.name)
            if ok and name.strip() and name.strip() != path.name:
                new         = path.with_name(name.strip())
                if new.exists():
                    self.ctx.toast(f"{new.name} already exists.", "error")
                    return
                self.save_all()
                path.rename(new)
                self.editors[index] = (new, ed)
                self.tabs.setTabText(index, new.name)
                self.tabs.setTabToolTip(index, str(new))

    def _remember_recent(self, folder: Path) -> None:
        s                   = app_settings()
        recent              = [r for r in (s.value("code/recent") or []) if not _same_path(r, folder)]
        if isinstance(recent, str):
            recent          = [recent]
        s.setValue("code/recent", [str(folder)] + recent[:9])

    def _fill_file_menu(self) -> None:
        m                   = self.file_menu
        m.clear()
        m.addAction("New sketch\tCtrl+N", self.new_sketch)
        m.addAction("Open…\tCtrl+O", self.open_sketch)
        recent_menu         = m.addMenu("Open recent")
        recent              = app_settings().value("code/recent") or []
        if isinstance(recent, str):
            recent          = [recent]
        recent              = [r for r in recent if arduino.main_sketch_file(r).is_file()]
        for r in recent:
            recent_menu.addAction(Path(r).name, lambda p=r: self.maybe_save() and self.load_sketch(Path(p))).setToolTip(r)
        recent_menu.setEnabled(bool(recent))
        m.addSeparator()
        m.addAction("Save\tCtrl+S", self.save_all)
        m.addAction("Save as…\tCtrl+Shift+S", self.save_as)
        m.addAction("New file in sketch…", self.new_file)
        m.addSeparator()
        m.addAction("Export compiled binaries", self.export_binaries)
        m.addAction("Show sketch folder", self._show_folder)
        m.addSeparator()
        verbose             = m.addAction("Verbose compiler output")
        verbose.setCheckable(True)
        verbose.setChecked(app_settings().value("code/verbose", False) in (True, "true"))
        verbose.toggled.connect(lambda on: app_settings().setValue("code/verbose", on))
        m.addAction("Go to line…\tCtrl+G", self.goto_line)
        m.addAction("Find / replace\tCtrl+H", lambda: self.find_bar.open_bar(True))

    def _show_folder(self) -> None:
        from    PySide6.QtCore              import  QUrl
        from    PySide6.QtGui               import  QDesktopServices
        if self.sketch:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.sketch)))

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? Examples
    #?------------------------------------------------------------------------------------------------------------------------------------
    def _fill_examples_menu(self) -> None:
        m                   = self.examples_menu
        m.clear()
        builtin             = m.addMenu("Built-in")
        for name in arduino.BUILTIN_EXAMPLES:
            builtin.addAction(name, lambda n=name: self._open_builtin_example(n))
        m.addSeparator()
        cli                 = arduino.find_cli()
        if cli is None:
            m.addAction("Install arduino-cli to see library examples").setEnabled(False)
            return
        if self._examples is None:
            m.addAction("Loading library examples…").setEnabled(False)
            args            = ["lib", "examples"] + (["--fqbn", self.fqbn()] if self.fqbn() else [])
            self._query(args, self._examples_loaded)
            return
        if not self._examples:
            m.addAction("No library examples installed").setEnabled(False)
        for lib, paths in self._examples.items():
            sub             = m.addMenu(lib)
            for p in paths:
                sub.addAction(Path(p).name, lambda path=p: self._open_example_folder(Path(path)))

    def _examples_loaded(self, data, err: str) -> None:
        self._examples      = arduino.parse_examples(data) if data else {}

    def _open_builtin_example(self, name: str) -> None:
        if not self.maybe_save():
            return
        root                = self.scratch_root()
        root.mkdir(parents=True, exist_ok=True)
        folder              = root / name
        if folder.exists():
            shutil.rmtree(folder, ignore_errors=True)
        self.load_sketch(arduino.create_sketch(root, name, arduino.BUILTIN_EXAMPLES[name]).parent)

    def _open_example_folder(self, src: Path) -> None:
        """Examples are copied to the scratch area so the originals stay untouched."""
        if not self.maybe_save():
            return
        dst                 = self.scratch_root() / src.name
        shutil.rmtree(dst, ignore_errors=True)
        shutil.copytree(src, dst)
        self.load_sketch(dst)

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? Boards
    #?------------------------------------------------------------------------------------------------------------------------------------
    def board_urls(self) -> list[str]:
        raw                 = app_settings().value("code/board_urls")
        if raw is None:
            return list(arduino.DEFAULT_BOARD_URLS)
        if isinstance(raw, str):
            raw             = [raw] if raw else []
        return [u for u in raw if u]

    def set_board_urls(self, urls: list[str]) -> None:
        app_settings().setValue("code/board_urls", urls)

    def fqbn(self) -> str:
        data                = self.board_combo.currentData()
        if data:
            return str(data)
        return str(app_settings().value("code/fqbn", "") or "")

    def full_fqbn(self) -> str:
        return arduino.fqbn_with_options(self.fqbn(), self.option_values) if self.fqbn() else ""

    def _query(self, args: list[str], callback, timeout: int = 180) -> None:
        cli                 = arduino.find_cli()
        if cli is None:
            return
        q                   = arduino.CliQuery(cli, args + arduino.global_args(self.board_urls()), self, timeout)
        q.done.connect(callback)
        q.finished.connect(lambda: self._queries.remove(q) if q in self._queries else None)
        self._queries.append(q)
        q.start()

    def refresh_boards(self) -> None:
        self._boards_loaded = True
        self.board_combo.setPlaceholderText("Loading boards…")
        self._query(["board", "listall"], self._boards_ready)

    def _boards_ready(self, data, err: str) -> None:
        self.boards         = arduino.parse_boards(data) if data else []
        saved               = str(app_settings().value("code/fqbn", "") or "")
        self.board_combo.blockSignals(True)
        self.board_combo.clear()
        for b in self.boards:
            self.board_combo.addItem(b.name, b.fqbn)
            self.board_combo.setItemData(self.board_combo.count() - 1, b.fqbn, Qt.ItemDataRole.ToolTipRole)
        idx                 = self.board_combo.findData(saved) if saved else -1
        if idx < 0 and self.boards:
            idx             = max(self.board_combo.findData(DEFAULT_FQBN), 0)
        self.board_combo.setCurrentIndex(idx)
        self.board_combo.blockSignals(False)
        if not self.boards:
            self.board_combo.setEditText("")
            self.board_combo.setPlaceholderText("No boards - open the Boards manager")
            self.options_btn.setEnabled(False)
        else:
            self._board_chosen(self.board_combo.currentIndex())
        self._examples      = None

    def _board_text_entered(self) -> None:
        idx                 = self.board_combo.findText(self.board_combo.currentText(), Qt.MatchFlag.MatchFixedString)
        if idx >= 0:
            self.board_combo.setCurrentIndex(idx)
            self._board_chosen(idx)

    def _board_chosen(self, index: int) -> None:
        fqbn                = self.board_combo.itemData(index) if index >= 0 else None
        if not fqbn:
            return
        app_settings().setValue("code/fqbn", fqbn)
        stored              = app_settings().value(f"code/options/{fqbn.replace(':', '_')}")
        try:
            self.option_values = json.loads(stored) if stored else {}
        except (TypeError, ValueError):
            self.option_values = {}
        self.options_menu.clear()
        self.options_menu.addAction("Loading options…").setEnabled(False)
        self.options_btn.setEnabled(True)
        self._query(["board", "details", "--fqbn", fqbn], lambda d, e, f=fqbn: self._options_ready(f, d, e))
        self._examples      = None
        self._update_path_label()

    def _options_ready(self, fqbn: str, data, err: str) -> None:
        if fqbn != self.fqbn():
            return
        self.board_options  = arduino.parse_board_options(data) if data else []
        self.options_menu.clear()
        if not self.board_options:
            self.options_menu.addAction("This board has no options").setEnabled(False)
            return
        for opt in self.board_options:
            current         = self.option_values.get(opt.option, opt.default)
            label           = dict(opt.values).get(current, current)
            sub             = self.options_menu.addMenu(f"{opt.label}:  {label}")
            group           = QActionGroup(sub)
            for value, value_label in opt.values:
                act         = QAction(value_label, sub, checkable=True)
                act.setChecked(value == current)
                act.triggered.connect(lambda _c=False, o=opt.option, v=value: self._set_option(o, v))
                group.addAction(act)
                sub.addAction(act)
        self.options_menu.addSeparator()
        self.options_menu.addAction("Reset to defaults", lambda: self._set_option(None, None))

    def _set_option(self, option: str | None, value: str | None) -> None:
        if option is None:
            self.option_values = {}
        else:
            default         = next((o.default for o in self.board_options if o.option == option), "")
            if value == default:
                self.option_values.pop(option, None)
            else:
                self.option_values[option] = value
        fqbn                = self.fqbn()
        app_settings().setValue(f"code/options/{fqbn.replace(':', '_')}", json.dumps(self.option_values))
        self._options_ready(fqbn, {"config_options": [
            {"option": o.option, "option_label": o.label,
             "values": [{"value": v, "value_label": l, "selected": v == o.default} for v, l in o.values]}
            for o in self.board_options]}, "")

    def detect_board(self) -> None:
        port                = self.ctx.current_port()
        self.ctx.toast("Looking for boards…", "info", 1500)

        def done(data, err: str) -> None:
            ports           = arduino.parse_board_list(data) if data else []
            hit             = next((p for p in ports if p.address == port and p.boards), None) or \
                            next((p for p in ports if p.boards), None)
            if hit is None:
                self.ctx.toast("No board identified. ESP boards with generic USB-serial chips can't be detected - "
                               "pick the board manually.", "warning", 6000)
                return
            board           = hit.boards[0]
            idx             = self.board_combo.findData(board.fqbn)
            if idx < 0:
                self.ctx.toast(f"Found {board.name} on {hit.address}, but its core is not installed. "
                               "Install it in the Boards manager.", "warning", 6000)
                return
            self.board_combo.setCurrentIndex(idx)
            self._board_chosen(idx)
            self.ctx.toast(f"Found {board.name} on {hit.address}", "success")
        self._query(["board", "list"], done, timeout=60)

    def open_manager(self, kind: str) -> None:
        if arduino.find_cli() is None:
            self.ctx.toast("Download arduino-cli first (banner at the top of the Code page).", "warning")
            return
        from    flash.ui.arduino_dialogs    import  BoardsManager, LibraryManager
        dlg                 = self._dialogs.get(kind)
        if dlg is None:
            dlg             = (BoardsManager if kind == "boards" else LibraryManager)(self.ctx, self, self.window())
            self._dialogs[kind] = dlg
        dlg.show()
        dlg.raise_()
        dlg.activateWindow()

    def shutdown(self) -> None:
        """Wait for background arduino-cli queries so no QThread is destroyed while running."""
        for q in list(self._queries):
            if not q.wait(8000):
                q.terminate()
                q.wait(1000)
        if self._downloader is not None:
            self._downloader.wait(3000)

    def cores_changed(self) -> None:
        """Called by the boards manager after installing / removing a core."""
        self.refresh_boards()

    def libraries_changed(self) -> None:
        self._examples      = None

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? Compile / upload
    #?------------------------------------------------------------------------------------------------------------------------------------
    def _prepare(self) -> str | None:
        if arduino.find_cli() is None:
            self.ctx.toast("Download arduino-cli first (banner at the top).", "warning")
            return None
        if not self.fqbn():
            self.ctx.toast("Choose a board first (install one in the Boards manager).", "warning")
            self.board_combo.setFocus()
            return None
        if not self.save_all():
            return None
        return self.full_fqbn()

    def _clear_markers(self) -> None:
        for _p, ed in self.editors:
            ed.set_markers([])

    def _start_collect(self) -> None:
        self._diagnostics, self._size_lines = [], []
        self._collecting    = True
        self._clear_markers()

    def _collect_line(self, text: str, is_progress: bool) -> None:
        if not self._collecting or is_progress:
            return
        diag                = arduino.parse_diagnostic(text)
        if diag is not None:
            self._diagnostics.append(diag)
        elif SIZE_RE.search(text):
            self._size_lines.append(SIZE_RE.search(text).group(1))

    def _finish_collect(self, code: int) -> None:
        self._collecting    = False
        per_editor: dict[int, list[Marker]] = {}
        for d in self._diagnostics:
            if d.severity == "note":
                continue
            for i, (path, _ed) in enumerate(self.editors):
                if _same_path(path, d.path):
                    per_editor.setdefault(i, []).append(Marker(d.line, d.col, d.severity, d.message))
        for i, markers in per_editor.items():
            self.editors[i][1].set_markers(markers)
        errors              = [d for d in self._diagnostics if d.severity == "error"]
        if self._size_lines:
            self.size_label.setText("  ·  ".join(s.split("(")[0].replace("Sketch uses", "Flash:")
                                                  .replace("Global variables use", "RAM:").strip()
                                                  for s in self._size_lines))
        if errors:
            first           = errors[0]
            self.open_location(first.path, first.line, first.col)
            self.ctx.toast(f"{len(errors)} compile error{'s' * (len(errors) != 1)} - click a red line in the "
                           "console to jump to it", "error", 6000)

    def verify(self) -> None:
        fqbn                = self._prepare()
        if fqbn is None or self.ctx.runner.busy:
            return
        self._start_collect()
        verbose             = app_settings().value("code/verbose", False) in (True, "true")
        args                = arduino.compile_args(fqbn, str(self.sketch), verbose=verbose, board_urls=self.board_urls())
        self.ctx.run_cli(args, f"Compile {self.sketch.name}", self._finish_collect)

    def upload(self) -> None:
        fqbn                = self._prepare()
        if fqbn is None or self.ctx.runner.busy:
            return
        conn                = self.ctx.require_port()
        if conn is None:
            return
        self._start_collect()
        verbose             = app_settings().value("code/verbose", False) in (True, "true")
        args                = arduino.compile_args(fqbn, str(self.sketch), port=conn.port, verbose=verbose,
                                                   board_urls=self.board_urls())
        self.ctx.run_cli(args, f"Upload {self.sketch.name} to {conn.port}", self._finish_collect, uses_port=True)

    def export_binaries(self) -> None:
        fqbn                = self._prepare()
        if fqbn is None or self.ctx.runner.busy:
            return
        out                 = self.sketch / "build" / re.sub(r"[^\w.-]", ".", self.fqbn())
        self._start_collect()
        args                = arduino.compile_args(fqbn, str(self.sketch), export_dir=str(out), board_urls=self.board_urls())

        def done(code: int) -> None:
            self._finish_collect(code)
            if code != 0:
                return
            bins            = sorted(out.glob("*.bin")) + sorted(out.glob("*.hex"))
            self.ctx.log(f"Binaries exported to {out}", "success")
            for b in bins:
                self.ctx.log(f"  {b.name}", "muted")
            if self.fqbn().startswith(("esp32:", "esp8266:")) and bins:
                if self.ctx.confirm("Open in the Flash page?", "Load the exported firmware into the Flash page "
                                    "so you can flash it with esptool?", ok_text="Open in Flash page"):
                    self._send_to_flash_page(out)
        self.ctx.run_cli(args, f"Export {self.sketch.name}", done)

    def _send_to_flash_page(self, out: Path) -> None:
        name                = self.sketch.name
        merged              = next(out.glob("*.merged.bin"), None)
        if merged is not None:
            images          = [{"offset": "0x0", "path": str(merged), "enabled": True}]
        else:
            images          = []
            for suffix, off in ((".bootloader.bin", "0x1000"), (".partitions.bin", "0x8000"), (".bin", "0x10000")):
                f           = out / f"{name}.ino{suffix}"
                if f.is_file():
                    images.append({"offset": off, "path": str(f), "enabled": True})
        self.ctx.flash_page.table.from_list(images)
        self.ctx.select_page(self.ctx.pages.index(self.ctx.flash_page))

    def open_location(self, path: str, line: int, col: int) -> bool:
        for i, (p, ed) in enumerate(self.editors):
            if _same_path(p, path):
                self.tabs.setCurrentIndex(i)
                ed.goto(line, col)
                return True
        if Path(path).is_file():
            self.ctx.toast(f"{Path(path).name} is outside this sketch (library or core file).", "info")
        return False

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? Misc
    #?------------------------------------------------------------------------------------------------------------------------------------
    def goto_line(self) -> None:
        ed                  = self.current_editor()
        if ed is None:
            return
        line, ok            = QInputDialog.getInt(self, "Go to line", "Line:", ed.textCursor().blockNumber() + 1, 1,
                                                  ed.blockCount())
        if ok:
            ed.goto(line)

    def _zoom(self, step: int) -> None:
        for _p, ed in self.editors:
            ed.zoom(step)

    def download_cli(self) -> None:
        if self._downloader is not None:
            return
        self.banner_btn.setEnabled(False)
        self.banner_progress.show()
        self.banner_progress.setRange(0, 0)
        self.banner_text.setText("<b>Downloading arduino-cli…</b>")
        dl                  = arduino.CliDownloader(self)
        dl.progress.connect(self._download_progress)
        dl.done.connect(self._download_done)
        self._downloader    = dl
        dl.start()

    def _download_progress(self, got: int, total: int) -> None:
        if total:
            self.banner_progress.setRange(0, total)
            self.banner_progress.setValue(got)
            self.banner_text.setText(f"<b>Downloading arduino-cli…</b> {got / 1e6:.1f} / {total / 1e6:.1f} MB")

    def _download_done(self, path: str, err: str) -> None:
        self._downloader    = None
        self.banner_progress.hide()
        self.banner_btn.setEnabled(True)
        if err:
            self.banner_text.setText(f"<b>Download failed:</b> {err}")
            self.ctx.toast("arduino-cli download failed - check your internet connection.", "error", 6000)
            return
        self.banner_wrap.hide()
        self.ctx.log(f"arduino-cli {arduino.cli_version(path)} installed at {path}", "success")
        self.ctx.toast("arduino-cli ready. Install a board core in the Boards manager.", "success", 5000)
        self.refresh_boards()
        if not self.boards:
            QTimer.singleShot(500, lambda: self.open_manager("boards"))
#?----------------------------------------------------------------------------------------------------------------------------------------
