#!/usr/bin/env python
# coding=utf-8
#? -------------------------------------------------------------------------------
#?
#?                              _                   _           __
#?             ____ ___  ____ _(_)___     _      __(_)___  ____/ /___ _      __
#?            / __ `__ \/ __ `/ / __ \   | | /| / / / __ \/ __  / __ \ | /| / /
#?           / / / / / / /_/ / / / / /   | |/ |/ / / / / / /_/ / /_/ / |/ |/ /
#?          /_/ /_/ /_/\__,_/_/_/ /_/____|__/|__/_/_/ /_/\__,_/\____/|__/|__/
#?                                 /_____/
#?
#?
#? Name:        main_window.py
#? Purpose:     Main application window: sidebar navigation, connection bar, pages and console.
#?
#? Author:      Mohamed Gueni ( mohamedgueni@outlook.com)
#?
#? Created:     05/09/2019
#? -------------------------------------------------------------------------------
#? -------------------------------------------------------------------------------
from    __future__                    import  annotations

from    pathlib                       import  Path

from    PySide6.QtCore                import  QEasingCurve, QParallelAnimationGroup, QPropertyAnimation, QSize, Qt, QTimer
from    PySide6.QtGui                 import  QIcon, QKeySequence, QShortcut
from    PySide6.QtWidgets             import  (QApplication, QButtonGroup, QComboBox, QFrame, QHBoxLayout, QLabel, QMainWindow, QMessageBox,
                                               QProgressBar, QSizePolicy, QSplitter, QStackedWidget, QToolButton, QVBoxLayout, QWidget)

from    flash                         import  APP_NAME, __version__
from    flash.core.runner             import  ToolRunner
from    flash.core.serial_monitor     import  list_ports
from    flash.core.tools              import  BAUD_RATES, CHIPS, Connection, classify_line
from    flash.paths                   import  asset
from    flash.settings                import  StateStore, app_settings
from    flash.ui.pages.device_page    import  DevicePage
from    flash.ui.pages.efuse_page     import  EfusePage
from    flash.ui.pages.flash_page     import  FlashPage
from    flash.ui.pages.memory_page    import  MemoryPage
from    flash.ui.pages.monitor_page   import  MonitorPage
from    flash.ui.pages.settings_page  import  SettingsPage
from    flash.ui.pages.tools_page     import  ToolsPage
from    flash.ui.theme                import  theme
from    flash.ui.widgets              import  Console, FlowLayout, StatusPill, Toast, icon_button, repolish, set_icon
#?----------------------------------------------------------------------------------------------------------------------------------------
SIDEBAR_EXPANDED            = 212
SIDEBAR_COLLAPSED           = 68
AUTO_COLLAPSE_WIDTH         = 1040
WIDE_LAYOUT_WIDTH           = 1640
#?----------------------------------------------------------------------------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} {__version__}")
        self.setWindowIcon(QIcon(asset("flash.ico")))
        self.setMinimumSize(560, 480)
        self.setAcceptDrops(False)

        self.store          = StateStore()
        self.runner         = ToolRunner(self)
        self._sidebar_pinned: bool | None = None
        self._known_ports: set[str] = set()

        root                = QWidget()
        root.setObjectName("Root")
        h                   = QHBoxLayout(root)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)
        self.setCentralWidget(root)

        self.pages          = [FlashPage(self), MemoryPage(self), DevicePage(self), ToolsPage(self),
                               EfusePage(self), MonitorPage(self), SettingsPage(self)]
        self.monitor: MonitorPage = self.pages[5]
        self.settings_page: SettingsPage = self.pages[6]

        h.addWidget(self._build_sidebar())
        content             = QWidget()
        v                   = QVBoxLayout(content)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)
        v.addWidget(self._build_topbar())
        self.stack          = QStackedWidget()
        for page in self.pages:
            self.stack.addWidget(page)
        self.splitter       = QSplitter(Qt.Orientation.Vertical)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.addWidget(self.stack)
        self.splitter.addWidget(self._build_console())
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 1)
        v.addWidget(self.splitter, 1)
        h.addWidget(content, 1)

        self._build_statusbar()
        self.toast_widget   = Toast(self)
        self._wire_runner()
        self._shortcuts()

        self.refresh_ports(initial=True)
        self._port_timer    = QTimer(self, interval=2000)
        self._port_timer.timeout.connect(self.refresh_ports)
        self._port_timer.start()

        self.store.bind("conn/baud", self.baud_combo)
        self.store.bind("conn/chip", self.chip_combo)
        self.store.restore()
        self._restore_port_selection()
        self._restore_geometry()
        self.select_page(int(app_settings().value("ui/page", 0) or 0))
        theme().changed.connect(lambda *_: self._apply_theme_icons())
        self._apply_theme_icons()
        self.log(f"{APP_NAME} {__version__} ready. Select a serial port and an operation.", "muted")

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? Construction
    #?------------------------------------------------------------------------------------------------------------------------------------
    def _build_sidebar(self) -> QWidget:
        self.sidebar        = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(SIDEBAR_EXPANDED)
        lay                 = QVBoxLayout(self.sidebar)
        lay.setContentsMargins(12, 16, 12, 12)
        lay.setSpacing(2)

        brand               = QHBoxLayout()
        brand.setContentsMargins(6, 0, 0, 12)
        self.brand_icon     = QLabel()
        self.brand_icon.setPixmap(QIcon(asset("flash.ico")).pixmap(QSize(30, 30)))
        brand.addWidget(self.brand_icon)
        texts               = QVBoxLayout()
        texts.setSpacing(0)
        self.brand_name     = QLabel(APP_NAME)
        self.brand_name.setObjectName("Brand")
        self.brand_sub      = QLabel("ESP flashing toolkit")
        self.brand_sub.setObjectName("BrandSub")
        texts.addWidget(self.brand_name)
        texts.addWidget(self.brand_sub)
        brand.addLayout(texts, 1)
        lay.addLayout(brand)

        self.nav_group      = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        self.nav_buttons: list[QToolButton] = []
        for i, page in enumerate(self.pages):
            b               = QToolButton()
            b.setObjectName("NavButton")
            b.setText(page.title)
            b.setToolTip(f"{page.title}  (Ctrl+{i + 1})")
            b.setCheckable(True)
            b.setIconSize(QSize(20, 20))
            b.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda _=False, idx=i: self.select_page(idx))
            set_icon(b, page.icon_name, "muted")
            self.nav_group.addButton(b, i)
            self.nav_buttons.append(b)
            lay.addWidget(b)
        lay.addStretch(1)
        self.sidebar_footer = QLabel(f"v{__version__}")
        self.sidebar_footer.setObjectName("SidebarFooter")
        self.sidebar_footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.sidebar_footer)
        return self.sidebar

    def _build_topbar(self) -> QWidget:
        bar                 = QFrame()
        bar.setObjectName("TopBar")
        v                   = QVBoxLayout(bar)
        v.setContentsMargins(16, 12, 16, 12)
        v.setSpacing(10)

        top                 = QHBoxLayout()
        top.setSpacing(8)
        self.menu_btn       = icon_button("menu", "Collapse / expand sidebar", self.toggle_sidebar)
        top.addWidget(self.menu_btn)
        titles              = QVBoxLayout()
        titles.setSpacing(0)
        self.page_title     = QLabel()
        self.page_title.setObjectName("PageTitle")
        self.page_subtitle  = QLabel()
        self.page_subtitle.setObjectName("PageSubtitle")
        titles.addWidget(self.page_title)
        titles.addWidget(self.page_subtitle)
        top.addLayout(titles, 1)
        self.state_pill     = StatusPill("Idle", "idle")
        top.addWidget(self.state_pill, 0, Qt.AlignmentFlag.AlignVCenter)
        self.theme_btn      = icon_button("moon", "Toggle light / dark theme (Ctrl+T)", self._toggle_theme)
        top.addWidget(self.theme_btn)
        self.console_btn    = icon_button("panel", "Show / hide console (Ctrl+J)", self.toggle_console, checkable=True)
        self.console_btn.setChecked(True)
        top.addWidget(self.console_btn)
        v.addLayout(top)

        strip               = QWidget()
        fl                  = FlowLayout(strip, spacing=10)

        def group(label: str, *widgets) -> QWidget:
            w               = QWidget()
            hl              = QHBoxLayout(w)
            hl.setContentsMargins(0, 0, 0, 0)
            hl.setSpacing(6)
            lab             = QLabel(label)
            lab.setObjectName("FieldLabel")
            hl.addWidget(lab)
            for x in widgets:
                hl.addWidget(x)
            return w

        self.port_combo     = QComboBox()
        self.port_combo.setMinimumWidth(240)
        self.port_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.port_combo.setToolTip("Serial port of the ESP board")
        self.port_combo.currentIndexChanged.connect(self._port_changed)
        self.refresh_btn    = icon_button("refresh", "Rescan serial ports (F5)", lambda: self.refresh_ports(manual=True))
        self.baud_combo     = QComboBox()
        self.baud_combo.setEditable(True)
        self.baud_combo.addItems(BAUD_RATES)
        self.baud_combo.setCurrentText("460800")
        self.baud_combo.setMinimumWidth(110)
        self.baud_combo.setToolTip("Baud rate for data transfer (initial sync always uses 115200)")
        self.chip_combo     = QComboBox()
        self.chip_combo.addItems(CHIPS)
        self.chip_combo.setMinimumWidth(120)
        self.chip_combo.setToolTip("Target chip - 'auto' detects it on connect")
        self.chip_combo.currentTextChanged.connect(self._chip_changed)
        fl.addWidget(group("PORT", self.port_combo, self.refresh_btn))
        fl.addWidget(group("BAUD", self.baud_combo))
        fl.addWidget(group("CHIP", self.chip_combo))
        v.addWidget(strip)
        return bar

    def _build_console(self) -> QWidget:
        panel               = QFrame()
        panel.setObjectName("ConsolePanel")
        v                   = QVBoxLayout(panel)
        v.setContentsMargins(16, 10, 16, 12)
        v.setSpacing(8)
        head                = QHBoxLayout()
        head.setSpacing(6)
        title               = QLabel("Console")
        title.setObjectName("ConsoleTitle")
        head.addWidget(title)
        self.job_label      = QLabel("")
        self.job_label.setObjectName("Hint")
        head.addWidget(self.job_label, 1)
        self.progress       = QProgressBar()
        self.progress.setRange(0, 1000)
        self.progress.setFixedHeight(8)
        self.progress.setMinimumWidth(120)
        self.progress.setMaximumWidth(260)
        self.progress.setValue(0)
        head.addWidget(self.progress, 1)
        self.pct_label      = QLabel("")
        self.pct_label.setObjectName("Hint")
        self.pct_label.setMinimumWidth(44)
        head.addWidget(self.pct_label)
        self.stop_btn       = icon_button("stop", "Stop the running operation (Esc)", self.runner.stop, role="danger")
        self.stop_btn.setEnabled(False)
        head.addWidget(self.stop_btn)
        self.autoscroll_btn = icon_button("chevron-down", "Auto-scroll", checkable=True)
        self.autoscroll_btn.setChecked(True)
        self.autoscroll_btn.toggled.connect(lambda on: setattr(self.console, "autoscroll", on))
        head.addWidget(self.autoscroll_btn)
        head.addWidget(icon_button("copy", "Copy log", self._copy_log))
        head.addWidget(icon_button("save", "Save log to file", self._save_log))
        head.addWidget(icon_button("trash", "Clear log (Ctrl+L)", lambda: self.console.clear()))
        v.addLayout(head)
        self.console        = Console()
        self.console.setMinimumHeight(90)
        v.addWidget(self.console, 1)
        self.console_panel  = panel
        return panel

    def _build_statusbar(self) -> None:
        sb                  = self.statusBar()
        sb.setSizeGripEnabled(True)
        self.status_conn    = QLabel("")
        sb.addPermanentWidget(self.status_conn)
        sb.showMessage("Ready")

    def _shortcuts(self) -> None:
        for i in range(len(self.pages)):
            QShortcut(QKeySequence(f"Ctrl+{i + 1}"), self, lambda idx=i: self.select_page(idx))
        QShortcut(QKeySequence("F5"), self, lambda: self.refresh_ports(manual=True))
        QShortcut(QKeySequence("Escape"), self, self.runner.stop)
        QShortcut(QKeySequence("Ctrl+L"), self, lambda: self.console.clear())
        QShortcut(QKeySequence("Ctrl+J"), self, lambda: self.console_btn.click())
        QShortcut(QKeySequence("Ctrl+T"), self, self._toggle_theme)
        QShortcut(QKeySequence("Ctrl+B"), self, self.toggle_sidebar)

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? Context API used by pages
    #?------------------------------------------------------------------------------------------------------------------------------------
    def connection(self) -> Connection:
        adv                 = self.settings_page.connection_options()
        try:
            baud            = int(self.baud_combo.currentText())
        except ValueError:
            baud            = 115200
        return Connection(port=self.current_port(), baud=baud, chip=self.chip_combo.currentText(), **adv)

    def current_port(self) -> str:
        data                = self.port_combo.currentData()
        return str(data) if data else ""

    def require_port(self) -> Connection | None:
        conn                = self.connection()
        if not conn.port:
            self.toast("No serial port selected. Connect a board and pick its port.", "error")
            self.port_combo.setFocus()
            return None
        return conn

    def require_chip(self, conn: Connection, what: str) -> bool:
        if conn.chip == "auto":
            self.toast(f"{what} needs an explicit chip. Pick one in the CHIP selector.", "warning")
            self.chip_combo.setFocus()
            self.chip_combo.showPopup()
            return False
        return True

    def run(self, tool: str, args: list[str], title: str, on_done=None, uses_port: bool = True) -> bool:
        if self.runner.busy:
            self.toast("Another operation is still running.", "warning")
            return False
        reopen              = False
        if uses_port and self.monitor.is_open and self.monitor.port == self.current_port():
            reopen          = self.settings_page.reopen_monitor()
            self.monitor.close_port()
            self.log("Serial monitor paused while the operation runs.", "muted")

        def done(code: int) -> None:
            if on_done is not None:
                on_done(code)
            if reopen:
                QTimer.singleShot(300, self.monitor.open_port)

        return self.runner.run(tool, args, title, done)

    def toast(self, text: str, kind: str = "info", ms: int = 3500) -> None:
        self.toast_widget.show_message(text, kind, ms)

    def log(self, text: str, kind: str = "info") -> None:
        for line in text.splitlines() or [""]:
            self.console.append_line(line, kind)

    def confirm(self, title: str, text: str, danger: bool = False, ok_text: str = "Continue") -> bool:
        box                 = QMessageBox(self)
        box.setWindowTitle(title)
        box.setText(f"<b>{title}</b>")
        box.setInformativeText(text)
        box.setIcon(QMessageBox.Icon.Warning if danger else QMessageBox.Icon.Question)
        ok                  = box.addButton(ok_text, QMessageBox.ButtonRole.AcceptRole)
        ok.setProperty("kind", "danger" if danger else "primary")
        box.addButton(QMessageBox.StandardButton.Cancel)
        box.setDefaultButton(QMessageBox.StandardButton.Cancel)
        box.exec()
        return box.clickedButton() is ok

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? Behaviour
    #?------------------------------------------------------------------------------------------------------------------------------------
    def _wire_runner(self) -> None:
        r                   = self.runner
        r.started.connect(self._job_started)
        r.line.connect(self._job_line)
        r.progress.connect(self._job_progress)
        r.finished.connect(self._job_finished)
        r.busy_changed.connect(self._busy_changed)

    def _job_started(self, title: str, cmd: str) -> None:
        self.console.append_line("")
        self.console.append_line(f"▶ {title}", "command")
        self.console.append_line(f"$ {cmd}", "muted")
        self.job_label.setText(title)
        self.statusBar().showMessage(f"{title}…")
        if not self.console_btn.isChecked():
            self.console_btn.click()

    def _job_line(self, text: str, is_progress: bool) -> None:
        self.console.append_line(text, "info" if is_progress else classify_line(text), progress=is_progress)

    def _job_progress(self, pct: float) -> None:
        if pct < 0:
            self.progress.setRange(0, 0)                                               # busy indicator
            self.pct_label.setText("")
        else:
            self.progress.setRange(0, 1000)
            self.progress.setValue(int(pct * 10))
            self.pct_label.setText(f"{pct:.0f}%")

    def _job_finished(self, title: str, code: int, seconds: float) -> None:
        self.progress.setRange(0, 1000)
        took                = f"{seconds:.1f}s"
        if code == 0:
            self.console.append_line(f"✓ {title} finished in {took}", "success")
            self.toast(f"{title} completed ({took})", "success")
            self.statusBar().showMessage(f"{title} completed in {took}", 8000)
            self.state_pill.set_state("Done", "ok")
        elif code == -2:
            self.console.append_line(f"■ {title} stopped by user", "warning")
            self.toast(f"{title} stopped", "warning")
            self.statusBar().showMessage(f"{title} stopped", 8000)
            self.state_pill.set_state("Stopped", "idle")
        else:
            self.console.append_line(f"✗ {title} failed (exit code {code})", "error")
            self.toast(f"{title} failed - see console for details", "error", 5000)
            self.statusBar().showMessage(f"{title} failed", 8000)
            self.state_pill.set_state("Failed", "error")
        self.job_label.setText(f"{title} · {took}")

    def _busy_changed(self, busy: bool) -> None:
        self.stop_btn.setEnabled(busy)
        for p in self.pages:
            p.set_busy(busy)
        self.port_combo.setEnabled(not busy)
        self.chip_combo.setEnabled(not busy)
        self.baud_combo.setEnabled(not busy)
        if busy:
            self.state_pill.set_state("Working…", "busy")
            self.progress.setValue(0)

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? Ports
    #?------------------------------------------------------------------------------------------------------------------------------------
    def refresh_ports(self, initial: bool = False, manual: bool = False) -> None:
        if self.port_combo.view().isVisible():
            return
        ports               = list_ports()
        devices             = {p.device for p in ports}
        if devices == self._known_ports and not manual and not initial:
            return
        added               = devices - self._known_ports
        current             = self.current_port()
        self.port_combo.blockSignals(True)
        self.port_combo.clear()
        for p in ports:
            self.port_combo.addItem(p.label, p.device)
        if not ports:
            self.port_combo.addItem("No serial ports found", "")
            self.port_combo.model().item(0).setEnabled(False)
        idx                 = self.port_combo.findData(current)
        if idx < 0 and added and not initial:
            idx             = self.port_combo.findData(sorted(added)[-1])
        self.port_combo.setCurrentIndex(max(idx, 0))
        self.port_combo.blockSignals(False)
        if not initial:
            if added:
                self.toast(f"Device connected: {', '.join(sorted(added))}", "info")
            elif manual:
                self.toast(f"{len(ports)} serial port(s) found", "info", 2000)
        self._known_ports   = devices
        self._port_changed()

    def _restore_port_selection(self) -> None:
        saved               = app_settings().value("conn/port", "")
        idx                 = self.port_combo.findData(saved)
        if idx >= 0:
            self.port_combo.setCurrentIndex(idx)

    def _port_changed(self, *_):
        port                = self.current_port()
        chip                = self.chip_combo.currentText()
        self.status_conn.setText(f"{port or 'no port'}  ·  {chip}  ")
        if port:
            app_settings().setValue("conn/port", port)

    def _chip_changed(self, chip: str) -> None:
        self._port_changed()
        for p in self.pages:
            if hasattr(p, "chip_changed"):
                p.chip_changed(chip)

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? Layout
    #?------------------------------------------------------------------------------------------------------------------------------------
    def select_page(self, index: int) -> None:
        index               = max(0, min(index, len(self.pages) - 1))
        self.stack.setCurrentIndex(index)
        self.nav_buttons[index].setChecked(True)
        page                = self.pages[index]
        self.page_title.setText(page.title)
        self.page_subtitle.setText(page.subtitle)
        app_settings().setValue("ui/page", index)

    def toggle_sidebar(self) -> None:
        expand              = self.sidebar.width() < SIDEBAR_EXPANDED
        self._sidebar_pinned = expand
        self._set_sidebar(expand, animate=True)

    def _set_sidebar(self, expanded: bool, animate: bool = False) -> None:
        target              = SIDEBAR_EXPANDED if expanded else SIDEBAR_COLLAPSED
        style               = Qt.ToolButtonStyle.ToolButtonTextBesideIcon if expanded else Qt.ToolButtonStyle.ToolButtonIconOnly
        for b in self.nav_buttons:
            b.setToolButtonStyle(style)
        self.brand_name.setVisible(expanded)
        self.brand_sub.setVisible(expanded)
        if self.sidebar.width() == target:
            return
        if not animate:
            self.sidebar.setFixedWidth(target)
            return
        group               = QParallelAnimationGroup(self)
        for prop in (b"minimumWidth", b"maximumWidth"):
            a               = QPropertyAnimation(self.sidebar, prop, group)
            a.setDuration(180)
            a.setEasingCurve(QEasingCurve.Type.OutCubic)
            a.setStartValue(self.sidebar.width())
            a.setEndValue(target)
            group.addAnimation(a)
        group.start(QParallelAnimationGroup.DeletionPolicy.DeleteWhenStopped)

    def toggle_console(self) -> None:
        self.console_panel.setVisible(self.console_btn.isChecked())

    def resizeEvent(self, event) -> None:                                              # noqa: N802
        super().resizeEvent(event)
        w                   = self.width()
        if self._sidebar_pinned is None:
            self._set_sidebar(w >= AUTO_COLLAPSE_WIDTH)
        elif self._sidebar_pinned and w < 700:
            self._set_sidebar(False)
        wide                = w >= WIDE_LAYOUT_WIDTH
        orientation         = Qt.Orientation.Horizontal if wide else Qt.Orientation.Vertical
        if self.splitter.orientation() != orientation:
            self.splitter.setOrientation(orientation)
            total           = self.splitter.width() if wide else self.splitter.height()
            self.splitter.setSizes([int(total * 0.62), int(total * 0.38)] if wide else
                                   [int(total * 0.68), int(total * 0.32)])
        if self.toast_widget.isVisible():
            self.toast_widget._place()

    def _toggle_theme(self) -> None:
        theme().toggle()
        self.settings_page.sync_theme_combo()

    def _apply_theme_icons(self) -> None:
        set_icon(self.theme_btn, "sun" if theme().palette.name == "dark" else "moon")
        repolish(self.state_pill)

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? Log
    #?------------------------------------------------------------------------------------------------------------------------------------
    def _copy_log(self) -> None:
        QApplication.clipboard().setText(self.console.toPlainText())
        self.toast("Log copied to clipboard", "info", 1800)

    def _save_log(self) -> None:
        from    flash.ui.widgets              import  save_path
        path                = save_path(self, "Save log", "Text files (*.txt);;All files (*)", "flash-log.txt")
        if path:
            Path(path).write_text(self.console.toPlainText(), encoding="utf-8")
            self.toast(f"Log saved to {Path(path).name}", "success")

    #?------------------------------------------------------------------------------------------------------------------------------------
    #? Persist
    #?------------------------------------------------------------------------------------------------------------------------------------
    def _restore_geometry(self) -> None:
        s                   = app_settings()
        geo                 = s.value("ui/geometry")
        if geo is not None:
            self.restoreGeometry(geo)
        else:
            screen          = QApplication.primaryScreen().availableGeometry()
            self.resize(int(screen.width() * 0.78), int(screen.height() * 0.82))
            self.move(screen.center() - self.rect().center())
        sizes               = s.value("ui/splitter")
        if sizes:
            try:
                self.splitter.setSizes([int(x) for x in sizes])
            except (TypeError, ValueError):
                pass

    def closeEvent(self, event) -> None:                                               # noqa: N802
        if self.runner.busy:
            if not self.confirm("Operation running", "An operation is still running. Stop it and quit?",
                                danger=True, ok_text="Stop and quit"):
                event.ignore()
                return
            self.runner.stop()
        self.monitor.close_port()
        self.store.save()
        s                   = app_settings()
        s.setValue("ui/geometry", self.saveGeometry())
        s.setValue("ui/splitter", self.splitter.sizes())
        s.sync()
        super().closeEvent(event)
#?----------------------------------------------------------------------------------------------------------------------------------------
