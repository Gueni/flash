#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?                            __      _                     ___       __
#?            ____ __________/ /_  __(_)___  ____      ____/ (_)___ _/ /___  ____ ______
#?           / __ `/ ___/ __  / / / / / __ \/ __ \    / __  / / __ `/ / __ \/ __ `/ ___/
#?          / /_/ / /  / /_/ / /_/ / / / / / /_/ /   / /_/ / / /_/ / / /_/ / /_/ (__  )
#?          \__,_/_/   \__,_/\__,_/_/_/ /_/\____/____\__,_/_/\__,_/_/\____/\__, /____/
#?                                             /_____/                    /____/
#?
#?
#? Name:        arduino_dialogs.py
#? Purpose:     Boards manager and Library manager for the Code page (both driven by arduino-cli).
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     05/09/2019
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
from    __future__                  import  annotations

from    PySide6.QtCore              import  Qt, QTimer
from    PySide6.QtWidgets           import  (QAbstractItemView, QComboBox, QDialog, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QPlainTextEdit,
                                             QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from    flash.core                  import  arduino
from    flash.ui.widgets            import  button, icon_button
#?----------------------------------------------------------------------------------------------------------------------------------------
class _ManagerBase(QDialog):
    COLUMNS: list[str]      = []

    def __init__(self, ctx, code_page, parent=None, title: str = "", hint: str = "") -> None:
        super().__init__(parent)
        self.ctx, self.code = ctx, code_page
        self.setWindowTitle(title)
        self.resize(900, 600)
        self.setModal(False)
        self._index_tried   = False
        v                   = QVBoxLayout(self)
        v.setContentsMargins(18, 16, 18, 16)
        v.setSpacing(10)
        head                = QLabel(f"<b style='font-size:13pt'>{title}</b><br><span>{hint}</span>")
        head.setWordWrap(True)
        v.addWidget(head)
        top                 = QHBoxLayout()
        self.search         = QLineEdit()
        self.search.setClearButtonEnabled(True)
        top.addWidget(self.search, 1)
        self.refresh_btn    = icon_button("refresh", "Update the index from the internet", self.update_index)
        top.addWidget(self.refresh_btn)
        v.addLayout(top)
        self.table          = QTableWidget(0, len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setWordWrap(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.itemSelectionChanged.connect(self._selection_changed)
        v.addWidget(self.table, 1)
        self.actions        = QHBoxLayout()
        self.status         = QLabel("")
        self.status.setObjectName("Hint")
        self.actions.addWidget(self.status, 1)
        v.addLayout(self.actions)
        self._busy          = False

    def set_busy(self, busy: bool) -> None:
        self._busy          = busy
        self.refresh_btn.setEnabled(not busy)
        self._selection_changed()

    def _item(self, text: str, tip: str = "") -> QTableWidgetItem:
        it                  = QTableWidgetItem(text)
        if tip:
            it.setToolTip(tip)
        return it

    def _needs_index(self, err: str) -> bool:
        low                 = err.lower()
        return any(k in low for k in ("index", "not found", "no such file", "run update"))

    def _selection_changed(self) -> None:                                              # overridden
        pass

    def update_index(self) -> None:                                                    # overridden
        pass
#?----------------------------------------------------------------------------------------------------------------------------------------
class BoardsManager(_ManagerBase):
    COLUMNS                 = ["Platform", "ID", "Installed", "Latest", "Maintainer"]

    def __init__(self, ctx, code_page, parent=None) -> None:
        super().__init__(ctx, code_page, parent, "Boards manager",
                         "Install the core for your board family. ESP32 (esp32:esp32) is large: about 1-2 GB of "
                         "compilers are downloaded the first time.")
        self.search.setPlaceholderText("Filter: esp32, esp8266, avr, stm32, rp2040, nano …")
        self.search.textChanged.connect(self._filter)
        self.platforms: list[arduino.Platform] = []
        self.install_btn    = button("Install", "download", "primary", slot=self.install)
        self.remove_btn     = button("Remove", "trash", "danger", slot=self.remove)
        self.urls_btn       = button("Board URLs…", "external", kind="ghost", slot=self._toggle_urls)
        self.actions.addWidget(self.urls_btn)
        self.actions.addWidget(self.remove_btn)
        self.actions.addWidget(self.install_btn)
        self.urls_box       = QWidget()
        ul                  = QVBoxLayout(self.urls_box)
        ul.setContentsMargins(0, 0, 0, 0)
        lab                 = QLabel("Additional board manager URLs (one per line):")
        lab.setObjectName("FieldLabel")
        ul.addWidget(lab)
        self.urls           = QPlainTextEdit()
        self.urls.setObjectName("Input")
        self.urls.setFixedHeight(96)
        self.urls.setPlainText("\n".join(self.code.board_urls()))
        ul.addWidget(self.urls)
        row                 = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(button("Reset to defaults", kind="ghost", slot=lambda: self.urls.setPlainText(
            "\n".join(arduino.DEFAULT_BOARD_URLS))))
        row.addWidget(button("Save and update index", "check", "primary", slot=self._save_urls))
        ul.addLayout(row)
        self.urls_box.hide()
        self.layout().insertWidget(self.layout().count() - 1, self.urls_box)
        for col, w in enumerate((280, 190, 90, 90)):
            self.table.setColumnWidth(col, w)
        self._selection_changed()
        QTimer.singleShot(0, self.reload)

    def _toggle_urls(self) -> None:
        self.urls_box.setVisible(not self.urls_box.isVisible())

    def _save_urls(self) -> None:
        urls                = [u.strip() for u in self.urls.toPlainText().splitlines() if u.strip()]
        self.code.set_board_urls(urls)
        self.urls_box.hide()
        self.update_index()

    def reload(self) -> None:
        self.status.setText("Loading platforms…")
        self.code._query(["core", "search"], self._loaded)

    def _loaded(self, data, err: str) -> None:
        self.platforms      = arduino.parse_platforms(data) if data else []
        if not self.platforms and not self._index_tried:
            self._index_tried = True
            self.update_index()
            return
        self.platforms.sort(key=lambda p: (not p.installed, p.id.split(":")[0] not in ("esp32", "esp8266"),
                                           p.name.lower()))
        self._filter()
        n                   = sum(1 for p in self.platforms if p.installed)
        self.status.setText(f"{len(self.platforms)} platforms · {n} installed" if self.platforms else
                            (f"Could not load platforms: {err}" if err else "No platforms found"))

    def _filter(self) -> None:
        q                   = self.search.text().strip().lower()
        rows                = [p for p in self.platforms if not q or q in p.name.lower() or q in p.id.lower() or
                               any(q in b.lower() for b in p.boards)]
        self.table.setRowCount(0)
        for p in rows:
            r               = self.table.rowCount()
            self.table.insertRow(r)
            boards          = ", ".join(p.boards[:40]) + (" …" if len(p.boards) > 40 else "")
            self.table.setItem(r, 0, self._item(p.name, f"Boards: {boards}"))
            self.table.setItem(r, 1, self._item(p.id))
            self.table.setItem(r, 2, self._item(p.installed or "-"))
            self.table.setItem(r, 3, self._item(p.latest))
            self.table.setItem(r, 4, self._item(p.maintainer))
            self.table.item(r, 0).setData(Qt.ItemDataRole.UserRole, p.id)
        self._selection_changed()

    def _selected(self) -> arduino.Platform | None:
        rows                = self.table.selectionModel().selectedRows() if self.table.selectionModel() else []
        if not rows:
            return None
        pid                 = self.table.item(rows[0].row(), 0).data(Qt.ItemDataRole.UserRole)
        return next((p for p in self.platforms if p.id == pid), None)

    def _selection_changed(self) -> None:
        p                   = self._selected()
        busy                = getattr(self, "_busy", False)
        self.install_btn.setEnabled(p is not None and not busy and p.installed != p.latest)
        self.install_btn.setText(" Update" if p and p.installed and p.installed != p.latest else " Install")
        self.remove_btn.setEnabled(p is not None and not busy and bool(p.installed))

    def update_index(self) -> None:
        self.status.setText("Updating board index…")
        self.ctx.run_cli(["core", "update-index"] + arduino.global_args(self.code.board_urls()),
                         "Update board index", lambda code: self.reload())

    def install(self) -> None:
        p                   = self._selected()
        if p is None:
            return
        spec                = f"{p.id}@{p.latest}" if p.latest else p.id
        self.ctx.run_cli(["core", "install", spec] + arduino.global_args(self.code.board_urls()),
                         f"Install {p.name} {p.latest}", self._after_change)

    def remove(self) -> None:
        p                   = self._selected()
        if p and self.ctx.confirm("Remove core?", f"Uninstall <b>{p.name}</b> ({p.id})?", danger=True, ok_text="Remove"):
            self.ctx.run_cli(["core", "uninstall", p.id], f"Remove {p.name}", self._after_change)

    def _after_change(self, code: int) -> None:
        self.reload()
        if code == 0:
            self.code.cores_changed()
#?----------------------------------------------------------------------------------------------------------------------------------------
class LibraryManager(_ManagerBase):
    COLUMNS                 = ["Library", "Installed", "Latest", "Author", "Description"]

    def __init__(self, ctx, code_page, parent=None) -> None:
        super().__init__(ctx, code_page, parent, "Library manager",
                         "Search the Arduino library index. Installed libraries are listed when the search is empty.")
        self.search.setPlaceholderText("Search libraries (e.g. ArduinoJson, Adafruit NeoPixel, PubSubClient) …")
        self._timer         = QTimer(self, singleShot=True, interval=500)
        self._timer.timeout.connect(self.reload)
        self.search.textChanged.connect(lambda _t: self._timer.start())
        self.search.returnPressed.connect(self.reload)
        self.libs: list[arduino.Library] = []
        self.installed: dict[str, str] = {}
        self.includes: dict[str, list[str]] = {}
        self.version        = QComboBox()
        self.version.setMinimumWidth(110)
        self.version.setToolTip("Version to install")
        self.include_btn    = button("Include in sketch", "code", kind="ghost", slot=self.include)
        self.remove_btn     = button("Remove", "trash", "danger", slot=self.remove)
        self.install_btn    = button("Install", "download", "primary", slot=self.install)
        for w in (self.include_btn, self.remove_btn, self.version, self.install_btn):
            self.actions.addWidget(w)
        for col, w in enumerate((230, 80, 80, 180)):
            self.table.setColumnWidth(col, w)
        self._selection_changed()
        QTimer.singleShot(0, self.reload)

    def reload(self) -> None:
        self.status.setText("Loading…")
        self.code._query(["lib", "list"], self._installed_loaded)

    def _installed_loaded(self, data, err: str) -> None:
        self.installed      = arduino.parse_installed_libraries(data) if data else {}
        self.includes       = {}
        for item in (data or {}).get("installed_libraries", []) or []:
            lib             = item.get("library") or {}
            if lib.get("name"):
                self.includes[lib["name"]] = lib.get("provides_includes") or []
        q                   = self.search.text().strip()
        if len(q) >= 2:
            self.code._query(["lib", "search", q], self._search_loaded)
        else:
            self.libs       = [arduino.Library(n, "", v, "", "installed") for n, v in sorted(self.installed.items())]
            self._show()
            self.status.setText(f"{len(self.installed)} installed libraries · type at least 2 letters to search")

    def _search_loaded(self, data, err: str) -> None:
        if err and self._needs_index(err) and not self._index_tried:
            self._index_tried = True
            self.update_index()
            return
        self.libs           = arduino.parse_library_search(data, self.installed) if data else []
        self._show()
        self.status.setText(f"{len(self.libs)} results" if not err else f"Search failed: {err}")

    def _show(self) -> None:
        self.table.setRowCount(0)
        for lib in self.libs[:500]:
            r               = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, self._item(lib.name, lib.sentence))
            self.table.setItem(r, 1, self._item(lib.installed or "-"))
            self.table.setItem(r, 2, self._item(lib.latest or "-"))
            self.table.setItem(r, 3, self._item(lib.author))
            self.table.setItem(r, 4, self._item(lib.sentence, lib.sentence))
        self._selection_changed()

    def _selected(self) -> arduino.Library | None:
        rows                = self.table.selectionModel().selectedRows() if self.table.selectionModel() else []
        return self.libs[rows[0].row()] if rows and rows[0].row() < len(self.libs) else None

    def _selection_changed(self) -> None:
        lib                 = self._selected()
        busy                = getattr(self, "_busy", False)
        self.version.clear()
        if lib and lib.versions:
            self.version.addItems(lib.versions[:40])
        self.version.setEnabled(bool(lib and lib.versions))
        self.install_btn.setEnabled(lib is not None and not busy and bool(lib.versions or lib.latest))
        self.install_btn.setText(" Update" if lib and lib.installed and lib.latest and lib.installed != lib.latest
                                 else " Install")
        self.remove_btn.setEnabled(lib is not None and not busy and bool(lib.installed))
        self.include_btn.setEnabled(lib is not None and bool(lib.installed))

    def update_index(self) -> None:
        self.status.setText("Updating library index…")
        self.ctx.run_cli(["lib", "update-index"], "Update library index", lambda code: self.reload())

    def install(self) -> None:
        lib                 = self._selected()
        if lib is None:
            return
        version             = self.version.currentText() or lib.latest
        spec                = f"{lib.name}@{version}" if version else lib.name
        self.ctx.run_cli(["lib", "install", spec], f"Install library {lib.name} {version}", self._after_change)

    def remove(self) -> None:
        lib                 = self._selected()
        if lib and self.ctx.confirm("Remove library?", f"Uninstall <b>{lib.name}</b>?", danger=True, ok_text="Remove"):
            self.ctx.run_cli(["lib", "uninstall", lib.name], f"Remove library {lib.name}", self._after_change)

    def _after_change(self, code: int) -> None:
        self.reload()
        if code == 0:
            self.code.libraries_changed()

    def include(self) -> None:
        lib                 = self._selected()
        ed                  = self.code.current_editor()
        if lib is None or ed is None:
            return
        headers             = self.includes.get(lib.name) or [lib.name.replace(" ", "_") + ".h"]
        lines               = "".join(f"#include <{h}>\n" for h in headers)
        cur                 = ed.textCursor()
        cur.movePosition(cur.MoveOperation.Start)
        cur.insertText(lines)
        self.ctx.toast(f"Added {', '.join(headers)} to {self.code.sketch.name}", "success")
#?----------------------------------------------------------------------------------------------------------------------------------------
