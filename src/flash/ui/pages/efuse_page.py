#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?                  ____
#?            ___  / __/_  __________        ____  ____ _____ ____
#?           / _ \/ /_/ / / / ___/ _ \      / __ \/ __ `/ __ `/ _ \
#?          /  __/ __/ /_/ (__  )  __/     / /_/ / /_/ / /_/ /  __/
#?          \___/_/  \__,_/____/\___/_____/ .___/\__,_/\__, /\___/
#?                                 /_____/_/          /____/
#?
#?
#? Name:        efuse_page.py
#? Purpose:     Browse, search, export and burn eFuses.
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     05/09/2019
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
from    __future__                  import  annotations

import  os
import  tempfile
from    pathlib                     import  Path

from    PySide6.QtCore              import  QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt
from    PySide6.QtGui               import  QColor
from    PySide6.QtWidgets           import  (QAbstractItemView, QCheckBox, QDialog, QDialogButtonBox, QHeaderView, QLabel, QLineEdit, QTableView,
                                             QVBoxLayout)

from    flash.core                  import  efuse
from    flash.core.efuse            import  EfuseField
from    flash.ui.theme              import  theme
from    flash.ui.widgets            import  Card, Page, button, combo, field, flow, repolish, save_path
#?----------------------------------------------------------------------------------------------------------------------------------------
class EfuseModel(QAbstractTableModel):
    def __init__(self) -> None:
        super().__init__()
        self.fields: list[EfuseField] = []

    def set_fields(self, fields: list[EfuseField]) -> None:
        self.beginResetModel()
        self.fields         = fields
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:                                   # noqa: N802
        return 0 if parent.isValid() else len(self.fields)

    def columnCount(self, parent=QModelIndex()) -> int:                                # noqa: N802
        return len(efuse.COLUMNS)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):      # noqa: N802
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return efuse.COLUMNS[section]
        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        f                   = self.fields[index.row()]
        col                 = index.column()
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.ToolTipRole):
            values          = [f.name, f.category, f.value, f.raw_value, f.access, f.block, f.description]
            return values[col]
        if role == Qt.ItemDataRole.ForegroundRole:
            p               = theme().palette
            if col == 4 and not f.writeable:
                return QColor(p.warning)
            if col in (2, 3) and f.raw_value not in ("", "0x0", "0x00", "0", "False") and \
                    not set(f.raw_value.replace("0x", "")) <= {"0"}:
                return QColor(p.accent)
            if col in (1, 6):
                return QColor(p.muted)
        if role == Qt.ItemDataRole.FontRole and col == 0:
            from    PySide6.QtGui               import  QFont
            font            = QFont()
            font.setBold(True)
            return font
        return None
#?----------------------------------------------------------------------------------------------------------------------------------------
class EfuseFilter(QSortFilterProxyModel):
    def __init__(self) -> None:
        super().__init__()
        self.category       = "All categories"
        self.text           = ""
        self.only_set       = False

    def update(self, text: str | None = None, category: str | None = None, only_set: bool | None = None) -> None:
        if text is not None:
            self.text       = text.lower()
        if category is not None:
            self.category   = category
        if only_set is not None:
            self.only_set   = only_set
        self.invalidate()

    def filterAcceptsRow(self, source_row: int, parent) -> bool:                       # noqa: N802
        f: EfuseField       = self.sourceModel().fields[source_row]
        if self.category != "All categories" and f.category != self.category:
            return False
        if self.only_set and set(f.raw_value.replace("0x", "")) <= {"0"}:
            return False
        if self.text:
            hay             = f"{f.name} {f.description} {f.value} {f.category}".lower()
            return all(part in hay for part in self.text.split())
        return True
#?----------------------------------------------------------------------------------------------------------------------------------------
class BurnDialog(QDialog):
    """Asks for the new value and requires typing the eFuse name to confirm."""

    def __init__(self, parent, f: EfuseField) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Burn eFuse {f.name}")
        self.setMinimumWidth(460)
        v                   = QVBoxLayout(self)
        v.setSpacing(12)
        title               = QLabel(f"<b>{f.name}</b>")
        title.setObjectName("CardTitle")
        v.addWidget(title)
        desc                = QLabel(f.description or "")
        desc.setWordWrap(True)
        desc.setObjectName("CardSubtitle")
        v.addWidget(desc)
        info                = QLabel(f"Current value: <b>{f.value}</b> &nbsp; (raw {f.raw_value}) &nbsp; · &nbsp; "
                                     f"type {f.efuse_type or '?'} &nbsp; · &nbsp; block {f.block}")
        info.setWordWrap(True)
        v.addWidget(info)
        self.value          = QLineEdit()
        self.value.setObjectName("Mono")
        self.value.setPlaceholderText("1" if f.efuse_type == "bool" else "new value (e.g. 1, 0x2a)")
        v.addWidget(field("New value", self.value))
        warn                = QLabel(f"eFuse bits can only change from 0 to 1 and <b>can never be reset</b>. "
                                     f"Type <b>{f.name}</b> to confirm.")
        warn.setWordWrap(True)
        warn.setStyleSheet(f"color: {theme().palette.danger};")
        v.addWidget(warn)
        self.confirm        = QLineEdit()
        self.confirm.setPlaceholderText(f.name)
        v.addWidget(self.confirm)
        self.buttons        = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        self.ok             = self.buttons.addButton("Burn permanently", QDialogButtonBox.ButtonRole.AcceptRole)
        self.ok.setProperty("kind", "danger")
        repolish(self.ok)
        self.ok.setEnabled(False)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        v.addWidget(self.buttons)
        check               = lambda: self.ok.setEnabled(self.confirm.text().strip() == f.name and bool(self.value.text().strip()))
        self.confirm.textChanged.connect(check)
        self.value.textChanged.connect(check)
        if f.efuse_type == "bool":
            self.value.setText("1")
#?----------------------------------------------------------------------------------------------------------------------------------------
class EfusePage(Page):
    title                   = "eFuse"
    subtitle                = "Inspect and burn one-time-programmable eFuses"
    icon_name               = "shield"

    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        card                = Card("eFuse table", "Read the eFuses of the connected chip. Double-click a row to burn it.",
                                   "shield")
        self.model          = EfuseModel()
        self.proxy          = EfuseFilter()
        self.proxy.setSourceModel(self.model)
        self.proxy.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        self.search         = QLineEdit()
        self.search.setPlaceholderText("Search name, description or value…")
        self.search.setClearButtonEnabled(True)
        self.search.setMinimumWidth(220)
        self.search.textChanged.connect(lambda t: self._filter(text=t))
        self.category       = combo(["All categories"])
        self.category.setMinimumWidth(160)
        self.category.currentTextChanged.connect(lambda c: self._filter(category=c))
        self.only_set       = QCheckBox("Non-zero only")
        self.only_set.toggled.connect(lambda on: self._filter(only_set=on))
        self.virtual        = ctx.store.bind("efuse/virtual", QCheckBox("Virtual chip (demo, no hardware)"))
        self.virtual.setToolTip("Use espefuse --virt with the selected chip (esp32 if 'auto').")

        self.read_btn       = button("Read eFuses", "refresh", "primary", slot=self.refresh)
        self.burn_btn       = button("Burn selected…", "flame", "danger", slot=self.burn_selected)
        self.export_btn     = button("Export…", "download", slot=self.export)
        self.dump_btn       = button("Raw dump", "file", slot=self.raw_dump)
        card.add(flow(self.read_btn, self.burn_btn, self.export_btn, self.dump_btn, self.virtual))
        card.add(flow(self.search, self.category, self.only_set))

        self.table          = QTableView()
        self.table.setModel(self.proxy)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setWordWrap(False)
        self.table.setMinimumHeight(420)
        hh                  = self.table.horizontalHeader()
        hh.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        hh.setStretchLastSection(True)
        hh.setHighlightSections(False)
        for col, w in enumerate((230, 110, 170, 150, 50, 56)):
            self.table.setColumnWidth(col, w)
        self.table.doubleClicked.connect(lambda _i: self.burn_selected())
        card.add(self.table)
        self.count          = QLabel("No data yet - connect a chip and press Read eFuses.")
        self.count.setObjectName("Hint")
        card.add(self.count)
        self.grid.add(card, span=3)

        self.device_actions(self.read_btn, self.burn_btn, self.dump_btn)
        self._tmp: str | None = None

    def set_busy(self, busy: bool) -> None:
        super().set_busy(busy)
        self.export_btn.setEnabled(bool(self.model.fields))

    def resizeEvent(self, e) -> None:                                                  # noqa: N802
        super().resizeEvent(e)
        self.table.setMinimumHeight(max(320, self.viewport().height() - 260))

    def _filter(self, **kw) -> None:
        self.proxy.update(**kw)
        self._update_count()

    def _update_count(self) -> None:
        total               = len(self.model.fields)
        if total:
            self.count.setText(f"Showing {self.proxy.rowCount()} of {total} eFuses")

    def _conn(self):
        if self.virtual.isChecked():
            return self.ctx.connection()
        return self.ctx.require_port()

    #?------------------------------------------------------------------------------------------------------------------------------------
    def refresh(self) -> None:
        conn                = self._conn()
        if not conn:
            return
        fd, self._tmp       = tempfile.mkstemp(prefix="flash-efuse-", suffix=".json")
        os.close(fd)
        args                = conn.espefuse_args(virtual=self.virtual.isChecked()) + ["summary", "--format", "json",
                                                                                      "--file", self._tmp]
        self.ctx.run("espefuse", args, "Read eFuses", self._loaded, uses_port=not self.virtual.isChecked())

    def _loaded(self, code: int) -> None:
        tmp, self._tmp      = self._tmp, None
        try:
            if code != 0 or not tmp:
                return
            try:
                fields      = efuse.load_summary_file(tmp)
            except (OSError, ValueError) as exc:
                self.ctx.log(f"Could not parse eFuse summary: {exc}", "error")
                return
            self.model.set_fields(fields)
            cats            = ["All categories"] + sorted({f.category for f in fields if f.category})
            current         = self.category.currentText()
            self.category.blockSignals(True)
            self.category.clear()
            self.category.addItems(cats)
            self.category.setCurrentText(current if current in cats else "All categories")
            self.category.blockSignals(False)
            self.proxy.update(category=self.category.currentText())
            self.export_btn.setEnabled(True)
            self._update_count()
            self.ctx.log(f"Loaded {len(fields)} eFuses.", "success")
        finally:
            if tmp:
                Path(tmp).unlink(missing_ok=True)

    def _selected(self) -> EfuseField | None:
        idx                 = self.table.currentIndex()
        if not idx.isValid():
            return None
        return self.model.fields[self.proxy.mapToSource(idx).row()]

    def burn_selected(self) -> None:
        if self.ctx.runner.busy:
            return
        f                   = self._selected()
        if f is None:
            self.ctx.toast("Select an eFuse in the table first (read the eFuses if the table is empty).", "warning")
            return
        if not f.writeable:
            self.ctx.toast(f"{f.name} is write-protected and cannot be burned.", "error")
            return
        dlg                 = BurnDialog(self, f)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        conn                = self._conn()
        if not conn:
            return
        args                = conn.espefuse_args(virtual=self.virtual.isChecked()) + [
            "--do-not-confirm", "burn-efuse", f.name, dlg.value.text().strip()]
        self.ctx.run("espefuse", args, f"Burn {f.name}",
                     lambda code: code == 0 and not self.virtual.isChecked() and self.refresh(),
                     uses_port=not self.virtual.isChecked())

    def raw_dump(self) -> None:
        conn                = self._conn()
        if conn:
            self.ctx.run("espefuse", conn.espefuse_args(virtual=self.virtual.isChecked()) + ["dump"],
                         "eFuse dump", uses_port=not self.virtual.isChecked())

    def export(self) -> None:
        if not self.model.fields:
            self.ctx.toast("Nothing to export yet - read the eFuses first.", "warning")
            return
        path                = save_path(self, "Export eFuse table", "Excel workbook (*.xlsx);;CSV (*.csv)", "efuses.xlsx")
        if not path:
            return
        if not Path(path).suffix:
            path           += ".xlsx"
        visible             = [self.model.fields[self.proxy.mapToSource(self.proxy.index(r, 0)).row()]
                               for r in range(self.proxy.rowCount())]
        out                 = efuse.export(visible, path)
        self.ctx.toast(f"Exported {len(visible)} eFuses to {out.name}", "success")
#?----------------------------------------------------------------------------------------------------------------------------------------
