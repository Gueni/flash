import os.path
import getpass
import os
import os.path
import os.path
import platform
import socket
import sqlite3
import sys
from pathlib import Path

import pyzipper
import serial.tools.list_ports
import xlwt
from PyQt5 import QtCore, QtGui, QtWidgets, QtTest
from PyQt5.QtCore import QSize, QRegExp, QCoreApplication, QSettings, QThread, pyqtSignal, Qt, QProcess, QEvent, \
    QSysInfo, QDate, QTime
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtGui import QPixmap, QRegExpValidator, QKeySequence, QIcon, QMovie
from PyQt5.QtNetwork import QHostAddress, QNetworkInterface
from PyQt5.QtWidgets import QFileDialog, QGraphicsScene, QShortcut, QMessageBox, QTableWidgetItem, QTableWidget, \
    QVBoxLayout, QApplication, QPlainTextEdit, QInputDialog, QLineEdit

import OpmodeMain
import aboutmain
import advancedgui

machinesettig = 'machinesettig'
ipaddresssetting = 'ipaddresssetting'
timenowsetting = 'timenowsetting'
datenowsetting = 'datenowsetting'

ORGANIZATION_NAME = 'Micro Device Tunisie'
ORGANIZATION_DOMAIN = 'mdtunisie.com'
APPLICATION_NAME = 'MicroTool'

SETTINGS_TRAYbaud = 'SETTINGS_TRAYbaud'
SETTINGS_TRAYchip = 'SETTINGS_TRAYchip'
SETTINGS_TRAYflashsize = 'SETTINGS_TRAYflashsize'
SETTINGS_TRAYflashmode = 'SETTINGS_TRAYflashmode'
SETTINGS_TRAYreadstatus = 'SETTINGS_TRAYreadstatus'
SETTINGS_TRAYwritestatus = 'SETTINGS_TRAYwritestatus'

SETTINGS_plainadv = 'SETTINGS_plainadv'
SETTING_verifyFlash = 'SETTING_verifyFlash'
SETTING_readmemory = 'SETTING_readmemory'
SETTING_writemem1 = 'SETTING_writemem1'
SETTING_writemem2 = 'SETTING_writemem2'
SETTING_writemem3 = 'SETTING_writemem3'
SETTING_eraseregion1 = 'SETTING_eraseregion1'
SETTING_eraseregion2 = 'SETTING_eraseregion2'
SETTING_dumpmem1 = 'SETTING_dumpmem1'
SETTING_dumpmem2 = 'SETTING_dumpmem2'
SETTING_readflash1 = 'SETTING_readflash1'
SETTING_readflash2 = 'SETTING_readflash2'
SETTING_plainmem = 'SETTING_plainmem'
SETTING_offset1 = 'SETTING_offset1'
SETTING_offset2 = 'SETTING_offset2'
SETTING_offset3 = 'SETTING_offset3'
SETTING_offsetcombined = 'SETTING_offsetcombined'
SETTING_path1 = 'SETTING_path1'
SETTING_path2 = 'SETTING_path2'
SETTING_path3 = 'SETTING_path3'
SETTING_path4 = 'SETTING_path4'
SETTING_path5 = 'SETTING_path5'
SETTING_path6 = 'SETTING_path6'

SETTINGS_check1 = 'SETTINGS_check1'
SETTINGS_check2 = 'SETTINGS_check2'
SETTINGS_check3 = 'SETTINGS_check3'

SETTINGS_style = 'style'

offset1 = 'offset1'
offset2 = 'offset2'
offset3 = 'offset3'
baudrate = 'baudrate'
flashsize = 'flashsize'
flashmode = 'flashmode'
verifyflash = 'verifyflash'
readmem = 'readmem'
writemem1 = 'writemem1'
writemem2 = 'writemem2'
writemem3 = 'writemem3'
eraseregion1 = 'eraseregion1'
eraseregion2 = 'eraseregion2'
readstatus = 'readstatus'
writestatus = 'writestatus'
readflash1 = 'readflash1'
readflash2 = 'readflash2'
combined_offset = 'combined_offset'
memdump1 = 'memdump1'
memdump2 = 'memdump2'

progressnum = 'progressnum'
verifconst = 'veriftest'
dump_progress = 'dump_progress'
read_flash_progress = 'read_flash_progress'
comport = 'comport'


class MyprogressbarThread(QThread):
    change_value = pyqtSignal(int)

    def run(self):
        cnt = 0
        while cnt < 100:
            settingsprogresswrite = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
            cnt = settingsprogresswrite.value(progressnum, type=int)
            self.change_value.emit(cnt)
            QtTest.QTest.qWait(500)
        if cnt == 100:
            print("done")
            self.change_value.emit(0)


class MyprogressbarThreadreadflash(QThread):
    change_valuereadflash = pyqtSignal(int)

    def run(self):
        cnt = 0
        while cnt < 100:
            settingsread_flash = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
            cnt = settingsread_flash.value(read_flash_progress, type=int)
            self.change_valuereadflash.emit(cnt)
            QtTest.QTest.qWait(500)


class MyprogressbarThreaddump(QThread):
    change_valuedump = pyqtSignal(int)

    def run(self):
        cnt = 0
        while cnt < 100:
            settingsprogresdump = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
            cnt = settingsprogresdump.value(dump_progress, type=int)
            self.change_valuedump.emit(cnt)
            QtTest.QTest.qWait(500)
        if cnt == 100:
            print("done")
            self.change_valuedump.emit(0)


class MyprogressbarThreadflashall(QThread):
    change_valueall = pyqtSignal(int)

    def run(self):
        cnt = 0
        while cnt <= 100:
            settingsprogresswrite = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
            cnt = settingsprogresswrite.value(progressnum, type=int)
            self.change_valueall.emit(cnt)
            QtTest.QTest.qWait(500)
        # if cnt == 100:
        #     print("done")
        #     self.change_value.emit(0)


class WorkerThread(QThread):
    def __init__(self, parent=None):
        super(WorkerThread, self).__init__(parent)
        self.bundle_dir = os.path.dirname(os.path.abspath(__file__))
        self.settingsport = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)

    def run(self):
        Com_port = self.settingsport.value(comport, type=str)
        os.system('python ' + self.bundle_dir + '/espefuse.py --port ' + " " + Com_port + " " + ' summary')


class AdvancedModeApp(QtWidgets.QMainWindow, advancedgui.Ui_MainWindowadvanced):
    updatePb = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super(AdvancedModeApp, self).__init__(parent)
        if getattr(sys, 'frozen', False):
            self.frozen = 'ever so'
            self.bundle_dir = sys._MEIPASS
        else:
            self.bundle_dir = os.path.dirname(os.path.abspath(__file__))
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(self.bundle_dir + '/icons/espLogo.png'))
        self.lay = QVBoxLayout()
        self.settingstyle = QSettings("settingsstyle.ini", QSettings.IniFormat)
        self.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.workerThread = WorkerThread()
        self.memoryESP8266 = ['detect', '512KB', '256KB', '1MB', '2MB', '4MB', '2MB-c1', '4MB-c1', '4MB-c2']
        self.memoryESP32 = ['detect', '1MB', '2MB', '4MB', '8MB', '16MB']
        self.ser = serial.Serial()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(50)
        self.initButtons()

        # To ensure that every time you call QSettings not enter the data of your application,
        # which will be the settings, you can set them globally for all applications
        QCoreApplication.setApplicationName(ORGANIZATION_NAME)
        QCoreApplication.setOrganizationDomain(ORGANIZATION_DOMAIN)
        QCoreApplication.setApplicationName(APPLICATION_NAME)
        self.initProcess()
        self.initProcessmem()
        self.baudRate = 115200
        self.setAcceptDrops(True)

        self.shellWin = PlainTextEdit()
        self.label_cpu = QtWidgets.QLabel()
        self.label_cpu.setObjectName("label_cpu")
        self.layout_terminal.addWidget(self.label_cpu)
        self.layout_terminal.addWidget(self.shellWin)
        sysinfo = QSysInfo()
        myMachine = "CPU Architecture: " + sysinfo.currentCpuArchitecture() + " | " + sysinfo.prettyProductName() + " | " + sysinfo.kernelType() + " | " + sysinfo.kernelVersion() + " | " + sysinfo.machineHostName()
        self.label_cpu.setText(myMachine)
        self.settings = QSettings("QTerminal", "QTerminal")
        self.readSettings()
        self.port = ''
        self.flasSize = self.comboBox_flashsize.currentText()
        self.frozen = 'not'
        self.chip = 'ESP32'
        self.statusbar.showMessage('Version 1.0')
        validator = QRegExpValidator(QRegExp("0x[0-9A-Fa-f][0-9A-Fa-f]{1,8}"))
        validator2 = QRegExpValidator(QRegExp("[0-9]{1,8}"))
        self.lineEdit_offset1.setValidator(validator)
        self.lineEdit_offset2.setValidator(validator)
        self.lineEdit_offset3.setValidator(validator)
        self.lineEdit_verifyoffset.setValidator(validator)
        self.lineEdit_offsetcombined.setValidator(validator)
        self.lineEditreadmemaddr.setValidator(validator)
        self.lineEdit_writemem1.setValidator(validator)
        self.lineEdit_writemem2.setValidator(validator)
        self.lineEdit_writemem3.setValidator(validator)
        self.lineEdit_eraseregion1.setValidator(validator)
        self.lineEdit_dumpmem1.setValidator(validator)
        self.lineEdit_readFlash1.setValidator(validator)
        self.lineEdit_eraseregion2.setValidator(validator2)
        self.lineEdit_dumpmem2.setValidator(validator2)
        self.lineEdit_readFlash2.setValidator(validator2)
        iconConnection = QtGui.QIcon(u'icons/connection.png')
        icondata = QtGui.QIcon(u'icons/settings.ico')
        iconoperation = QtGui.QIcon(u'icons/chip.png')
        iconsetting = QtGui.QIcon(u'icons/setting.png')
        iconmemo = QtGui.QIcon(u'icons/debug.png')
        iconfuse = QtGui.QIcon(u'icons/fuse.png')
        icon_terminal = QtGui.QIcon(u'icons/terminal.png')
        iconhelp = QtGui.QIcon(u'icons/Info-icon.png')
        self.tabWidget.setTabIcon(0, iconConnection)
        self.tabWidget.setTabIcon(1, iconoperation)
        self.tabWidget.setTabIcon(2, iconmemo)
        self.tabWidget.setTabIcon(3, icondata)
        self.tabWidget.setTabIcon(4, iconfuse)
        self.tabWidget.setTabIcon(5, iconsetting)
        self.tabWidget.setTabIcon(6, icon_terminal)
        self.tabWidget.setTabIcon(7, iconhelp)
        self.tabWidget.setIconSize(QSize(57, 57))
        scene = QGraphicsScene()
        pixmap = QPixmap('icons/disconnected.png')
        pixmapbig = pixmap.scaled(100, 100, QtCore.Qt.KeepAspectRatio)
        scene.addPixmap(pixmapbig)
        self.graphicsView.setScene(scene)
        self.label_8.setText("Serial Port Closed !")
        self.label_8.setStyleSheet(" border-radius: 5px;  color: #039BE5;font-weight: bold;")
        self.actionDark.triggered.connect(self.setDark)

        self.actionLight_Blue.triggered.connect(self.setactionLight_Blue)

        self.onStopbutton()
        self.onStopbuttonmemo()
        self.actionExit.triggered.connect(self.close_application)
        self.actionAbout.triggered.connect(self.showAbout)
        self.initui()
        self.checkBox_1.setDisabled(True)
        self.checkBox_2.setDisabled(True)
        self.checkBox_3.setDisabled(True)
        self.lineEdit_path1.textChanged[str].connect(
            lambda: self.checkBox_1.setEnabled(self.lineEdit_path1.text() != ""))
        self.lineEdit_path2.textChanged[str].connect(
            lambda: self.checkBox_2.setEnabled(self.lineEdit_path2.text() != ""))
        self.lineEdit_path3.textChanged[str].connect(
            lambda: self.checkBox_3.setEnabled(self.lineEdit_path3.text() != ""))
        self.initsettings()
        self.updatePb.connect(self.progressBar.setValue)
        self.tableWidget = QTableWidget()

        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)

    def initui(self):
        self.plainTextEditadvancedmem.setGeometry(QtCore.QRect(425, 10, 0, 0))
        self.groupBoxmemo.setGeometry(QtCore.QRect(30, 10, 720, 350))
        self.groupBox_2memo.setGeometry(QtCore.QRect(30, 370, 720, 100))
        self.pushButton_readmem.setGeometry(QtCore.QRect(30, 20, 320, 25))
        self.lineEditreadmemaddr.setGeometry(QtCore.QRect(370, 20, 320, 25))
        self.pushButton_writemem.setGeometry(QtCore.QRect(30, 55, 150, 25))
        self.lineEdit_writemem1.setGeometry(QtCore.QRect(200, 55, 150, 25))
        self.lineEdit_writemem2.setGeometry(QtCore.QRect(370, 55, 150, 25))
        self.lineEdit_writemem3.setGeometry(QtCore.QRect(540, 55, 150, 25))
        self.pushButton_eraseregion.setGeometry(QtCore.QRect(30, 90, 320, 25))
        self.lineEdit_eraseregion1.setGeometry(QtCore.QRect(370, 90, 150, 25))
        self.lineEdit_eraseregion2.setGeometry(QtCore.QRect(540, 90, 150, 25))
        self.pushButton_dumpmem.setGeometry(QtCore.QRect(30, 125, 320, 25))
        self.lineEdit_dumpmem1.setGeometry(QtCore.QRect(370, 125, 150, 25))
        self.lineEdit_dumpmem2.setGeometry(QtCore.QRect(540, 125, 150, 25))
        self.pushButton_readstatusreg.setGeometry(QtCore.QRect(30, 160, 320, 25))
        self.comboBox_readstatusreg.setGeometry(QtCore.QRect(370, 160, 320, 25))
        self.pushButton_writestatusreg.setGeometry(QtCore.QRect(30, 195, 320, 25))
        self.comboBox_writestatusreg.setGeometry(QtCore.QRect(370, 195, 320, 25))
        self.pushButton_readFlash.setGeometry(QtCore.QRect(30, 230, 320, 25))
        self.lineEdit_readFlash1.setGeometry(QtCore.QRect(370, 230, 150, 25))
        self.lineEdit_readFlash2.setGeometry(QtCore.QRect(540, 230, 150, 25))
        self.pushButton_Fusedump.setGeometry(QtCore.QRect(30, 265, 320, 25))
        self.pushButton_clearmemo.setGeometry(QtCore.QRect(30, 20, 320, 25))
        self.pushButton_stopmemo.setGeometry(QtCore.QRect(370, 20, 320, 25))
        self.progressBarmemo.setGeometry(QtCore.QRect(30, 60, 660, 13))
        self.pushButtoncollapsexpandm.setIcon(QIcon('icons/expandv.png'))
        self.pushButtoncollapsexpandm.setIconSize(QSize(24, 15))
        self.plainTextEditadvanced.setGeometry(QtCore.QRect(425, 10, 0, 0))
        self.groupBox.setGeometry(QtCore.QRect(30, 10, 720, 100))
        self.groupBox_2.setGeometry(QtCore.QRect(30, 140, 720, 161))
        self.groupBox_3.setGeometry(QtCore.QRect(30, 330, 720, 121))
        self.pushButton_verifyflash.setGeometry(QtCore.QRect(30, 20, 300, 25))
        self.lineEdit_verifyoffset.setGeometry(QtCore.QRect(390, 20, 300, 25))
        self.pushButton_loadram.setGeometry(QtCore.QRect(30, 55, 300, 25))
        self.pushButton_chipid.setGeometry(QtCore.QRect(390, 55, 300, 25))
        self.pushButton_flashcombined.setGeometry(QtCore.QRect(30, 30, 300, 25))
        self.pushButton_flashfirmware.setGeometry(QtCore.QRect(30, 70, 300, 25))
        self.pushButton_13.setGeometry(QtCore.QRect(30, 110, 300, 25))
        self.pushButton_flashAll.setGeometry(QtCore.QRect(390, 30, 300, 25))
        self.pushButton_eraseentireflash.setGeometry(QtCore.QRect(390, 70, 300, 25))
        self.pushButton_imageinfo.setGeometry(QtCore.QRect(390, 110, 300, 25))
        self.pushButton_clearop.setGeometry(QtCore.QRect(30, 30, 300, 25))
        self.pushButton_stop.setGeometry(QtCore.QRect(390, 30, 300, 25))
        self.progressBar.setGeometry(QtCore.QRect(30, 80, 660, 13))
        self.pushButtoncollapsexpand.setIcon(QIcon('icons/expandv.png'))
        self.pushButtoncollapsexpand.setIconSize(QSize(24, 15))
        self.pushButton_encrypt.setGeometry(QtCore.QRect(370, 265, 320, 25))
        self.pushButton_loadsetting.clicked.connect(self.loadsettingsbutton)

    def showAbout(self):
        self.window = aboutmain.abouthandel()
        self.window.show()

    def dataReady(self):
        self.plainTextEditadvanced.appendPlainText(bytearray(self.process.readAllStandardOutput()).decode('utf-8'))

    def dataReadymem(self):
        self.plainTextEditadvancedmem.appendPlainText(
            bytearray(self.processmem.readAllStandardOutput()).decode('utf-8'))

    def initProcessmem(self):
        self.processmem = QtCore.QProcess(self)
        self.processmem.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self.processmem.readyRead.connect(self.dataReadymem)
        self.processmem.started.connect(self.disableButtons)
        self.processmem.finished.connect(self.enableButtons)

    def initProcess(self):
        self.process = QtCore.QProcess(self)
        self.process.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self.process.readyRead.connect(self.dataReady)
        self.process.started.connect(self.disableButtons)
        self.process.finished.connect(self.enableButtons)

    def setDark(self):
        self.setStyleSheet(open("qssthemes/Dark/darkstyle.qss", "r").read())
        self.settingstyle.setValue(SETTINGS_style, "qssthemes/Dark/darkstyle.qss")
        self.settingstyle.sync()
        self.label_5.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.label.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.label_2.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.label_6.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.label_7.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.label_8.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButtoncollapsexpand.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_savesetting.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_13.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_browsecombined.setStyleSheet(
            open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_chipid.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_cleardata.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_clearmemo.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_clearop.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_combine.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_default.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_disconnect.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_dumpmem.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_elffile.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_encrypt.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_eraseentireflash.setStyleSheet(
            open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_eraseregion.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_flashAll.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_verifyflash.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_loadram.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.lineEdit_verifyoffset.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_flashcombined.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_flashfirmware.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_imageinfo.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_stop.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.progressBar.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.tabWidget.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.fusetab.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.optab.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.settingtab.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.infohelptab.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.datatab.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.info.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButtonconnect.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_logout.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.comboBox_baud.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.comboBox_serial.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_selectall.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_generatebinfromelf.setStyleSheet(
            open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_zipfiles.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_readmem.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.lineEditreadmemaddr.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_writemem.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.lineEdit_writemem1.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.lineEdit_writemem2.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.lineEdit_writemem3.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.lineEdit_eraseregion1.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.lineEdit_eraseregion2.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.lineEdit_dumpmem1.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.lineEdit_dumpmem2.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_readstatusreg.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.comboBox_readstatusreg.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_writestatusreg.setStyleSheet(
            open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.comboBox_writestatusreg.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_readFlash.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.lineEdit_readFlash1.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.lineEdit_readFlash2.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_Fusedump.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_stopmemo.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.progressBarmemo.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.Memo.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.tableWidget.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.terminal_tab.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        # self.shellWin.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.menubar.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

    def setactionLight_Blue(self):
        self.setStyleSheet(open("qssthemes/LightBlue/stylesheet.qss", "r").read())
        self.settingstyle.setValue(SETTINGS_style, "qssthemes/LightBlue/stylesheet.qss")
        self.settingstyle.sync()
        self.menubar.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.label_5.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.label.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.label_2.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.label_6.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.label_7.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.label_8.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButtoncollapsexpand.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_savesetting.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        # self.pushButton_reloadfusetab.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_13.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_browsecombined.setStyleSheet(
            open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_chipid.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_cleardata.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_clearmemo.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_clearop.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_combine.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_default.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_disconnect.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_dumpmem.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_elffile.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_encrypt.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_eraseentireflash.setStyleSheet(
            open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_eraseregion.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_flashAll.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_verifyflash.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_loadram.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.lineEdit_verifyoffset.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_flashcombined.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_flashfirmware.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_imageinfo.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_stop.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.progressBar.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.tabWidget.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.fusetab.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.optab.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.settingtab.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.infohelptab.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.datatab.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.info.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButtonconnect.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_logout.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.comboBox_baud.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.comboBox_serial.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_selectall.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_generatebinfromelf.setStyleSheet(
            open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_zipfiles.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_readmem.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.lineEditreadmemaddr.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_writemem.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.lineEdit_writemem1.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.lineEdit_writemem2.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.lineEdit_writemem3.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.lineEdit_eraseregion1.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.lineEdit_eraseregion2.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.lineEdit_dumpmem1.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.lineEdit_dumpmem2.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_readstatusreg.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.comboBox_readstatusreg.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_writestatusreg.setStyleSheet(
            open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.comboBox_writestatusreg.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_readFlash.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.lineEdit_readFlash1.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.lineEdit_readFlash2.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_Fusedump.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButton_stopmemo.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.progressBarmemo.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.Memo.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.tableWidget.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.terminal_tab.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        # self.shellWin.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

    def disableButtons(self):
        self.pushButton_eraseentireflash.setDisabled(True)
        self.pushButton_disconnect.setDisabled(True)
        self.pushButton_combine.setDisabled(True)
        self.pushButton_selectall.setDisabled(True)
        self.pushButton_loadsetting.setDisabled(True)
        self.pushButton_flashAll.setDisabled(True)
        self.pushButton_loadram.setDisabled(True)
        self.pushButton_13.setDisabled(True)
        self.pushButton_writestatusreg.setDisabled(True)
        self.pushButton_savesetting.setDisabled(True)
        self.pushButton_default.setDisabled(True)
        self.pushButtonconnect.setDisabled(True)
        self.pushButton_chipid.setDisabled(True)
        self.pushButton_dumpmem.setDisabled(True)
        self.pushButton_eraseregion.setDisabled(True)
        self.pushButton_flashcombined.setDisabled(True)
        self.pushButton_flashfirmware.setDisabled(True)
        self.pushButton_generatebinfromelf.setDisabled(True)
        self.pushButton_imageinfo.setDisabled(True)
        self.pushButton_logout.setDisabled(True)
        self.pushButton_readmem.setDisabled(True)
        self.pushButton_readstatusreg.setDisabled(True)
        self.pushButton_verifyflash.setDisabled(True)
        self.pushButton_writemem.setDisabled(True)
        self.lineEditreadmemaddr.setDisabled(True)
        self.lineEdit_combinedfile.setDisabled(True)
        self.lineEdit_offsetcombined.setDisabled(True)
        self.lineEdit_path2.setDisabled(True)
        self.lineEdit_path1.setDisabled(True)
        self.lineEdit_path3.setDisabled(True)
        self.lineEdit_offset1.setDisabled(True)
        self.lineEdit_elffile.setDisabled(True)
        self.lineEdit_offset2.setDisabled(True)
        self.lineEdit_offset3.setDisabled(True)
        self.lineEdit_verifyoffset.setDisabled(True)
        self.lineEdit_writemem2.setDisabled(True)
        self.lineEdit_keypath.setDisabled(True)
        self.lineEdit_eraseregion2.setDisabled(True)
        self.lineEdit_eraseregion1.setDisabled(True)
        self.lineEdit_dumpmem1.setDisabled(True)
        self.lineEdit_dumpmem2.setDisabled(True)
        self.lineEdit_writemem1.setDisabled(True)
        self.lineEdit_writemem3.setDisabled(True)
        self.comboBox_readstatusreg.setDisabled(True)
        self.comboBox_writestatusreg.setDisabled(True)
        self.comboBox_serial.setDisabled(True)
        self.pushButton_clearop.setDisabled(True)
        self.pushButton_cleardata.setDisabled(True)
        self.pushButton_clearmemo.setDisabled(True)
        self.pushButton_readFlash.setDisabled(True)
        self.pushButton_Fusedump.setDisabled(True)
        self.pushButton_encrypt.setDisabled(True)
        self.lineEdit_readFlash1.setDisabled(True)
        self.lineEdit_readFlash2.setDisabled(True)
        self.pushButton_path1.setDisabled(True)
        self.pushButton_path2.setDisabled(True)
        self.pushButton_path3.setDisabled(True)
        self.pushButton_pathkey.setDisabled(True)
        self.pushButton_browsecombined.setDisabled(True)
        self.pushButton_elffile.setDisabled(True)
        self.checkBox_1.setDisabled(True)
        self.checkBox_2.setDisabled(True)
        self.checkBox_3.setDisabled(True)
        self.pushButton_genkey.setDisabled(True)
        self.comboBox_serial.setDisabled(True)
        self.comboBox_chip.setDisabled(True)
        self.comboBox_flashsize.setDisabled(True)
        self.comboBox_flashmode.setDisabled(True)

    def readSettings(self):
        if self.settings.contains("commands"):
            self.shellWin.commands = self.settings.value("commands")

    def writeSettings(self):
        self.settings.setValue("commands", self.shellWin.commands)

    def enableButtons(self):
        self.pushButton_eraseentireflash.setDisabled(False)
        self.pushButton_disconnect.setDisabled(False)
        self.pushButton_combine.setDisabled(False)
        self.pushButton_selectall.setDisabled(False)
        self.pushButton_loadsetting.setDisabled(False)
        self.pushButton_flashAll.setDisabled(False)
        self.pushButton_loadram.setDisabled(False)
        self.pushButton_13.setDisabled(False)
        self.pushButton_writestatusreg.setDisabled(False)
        self.pushButton_savesetting.setDisabled(False)
        self.pushButton_default.setDisabled(False)
        self.pushButtonconnect.setDisabled(False)
        self.pushButton_chipid.setDisabled(False)
        self.pushButton_dumpmem.setDisabled(False)
        self.pushButton_eraseregion.setDisabled(False)
        self.pushButton_flashcombined.setDisabled(False)
        self.pushButton_flashfirmware.setDisabled(False)
        self.pushButton_generatebinfromelf.setDisabled(False)
        self.pushButton_imageinfo.setDisabled(False)
        self.pushButton_logout.setDisabled(False)
        self.pushButton_readmem.setDisabled(False)
        self.pushButton_readstatusreg.setDisabled(False)
        self.pushButton_verifyflash.setDisabled(False)
        self.pushButton_writemem.setDisabled(False)
        self.lineEditreadmemaddr.setDisabled(False)
        self.lineEdit_combinedfile.setDisabled(False)
        self.lineEdit_offsetcombined.setDisabled(False)
        self.lineEdit_path2.setDisabled(False)
        self.lineEdit_path1.setDisabled(False)
        self.lineEdit_path3.setDisabled(False)
        self.lineEdit_offset1.setDisabled(False)
        self.lineEdit_elffile.setDisabled(False)
        self.lineEdit_offset2.setDisabled(False)
        self.lineEdit_offset3.setDisabled(False)
        self.lineEdit_verifyoffset.setDisabled(False)
        self.lineEdit_writemem2.setDisabled(False)
        self.lineEdit_keypath.setDisabled(False)
        self.lineEdit_eraseregion2.setDisabled(False)
        self.lineEdit_eraseregion1.setDisabled(False)
        self.lineEdit_dumpmem1.setDisabled(False)
        self.lineEdit_dumpmem2.setDisabled(False)
        self.lineEdit_writemem1.setDisabled(False)
        self.lineEdit_writemem3.setDisabled(False)
        self.comboBox_readstatusreg.setDisabled(False)
        self.comboBox_writestatusreg.setDisabled(False)
        self.comboBox_serial.setDisabled(False)
        self.pushButton_clearop.setDisabled(False)
        self.pushButton_cleardata.setDisabled(False)
        self.pushButton_clearmemo.setDisabled(False)
        self.pushButton_readFlash.setDisabled(False)
        self.pushButton_Fusedump.setDisabled(False)
        self.pushButton_encrypt.setDisabled(False)
        self.lineEdit_readFlash1.setDisabled(False)
        self.lineEdit_readFlash2.setDisabled(False)
        self.pushButton_path1.setDisabled(False)
        self.pushButton_path2.setDisabled(False)
        self.pushButton_path3.setDisabled(False)
        self.pushButton_pathkey.setDisabled(False)
        self.pushButton_browsecombined.setDisabled(False)
        self.pushButton_elffile.setDisabled(False)
        self.checkBox_1.setDisabled(False)
        self.checkBox_2.setDisabled(False)
        self.checkBox_3.setDisabled(False)
        self.pushButton_genkey.setDisabled(False)
        self.comboBox_serial.setDisabled(False)
        self.comboBox_chip.setDisabled(False)
        self.comboBox_flashmode.setDisabled(False)
        self.comboBox_flashsize.setDisabled(False)

    def close_application(self):
        choice = QtWidgets.QMessageBox.question(self, ' Confirm Exit ', "Are You Sure You want To Exit MicroTool ?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            self.close_serial()
            self.savesettings()
            self.writeSettings()

            sys.exit()
        else:
            self.savesettings()
            pass

    def initButtons(self):
        self.pushButton_path1.clicked.connect(lambda: self.selectbinFile('Select Bin File', self.lineEdit_path1))
        self.pushButton_path2.clicked.connect(lambda: self.selectbinFile('Select Bin File', self.lineEdit_path2))
        self.pushButton_path3.clicked.connect(lambda: self.selectbinFile('Select Bin File', self.lineEdit_path3))
        self.pushButton_pathkey.clicked.connect(lambda: self.selectkeyFile('Select key File', self.lineEdit_keypath))
        self.pushButton_elffile.clicked.connect(lambda: self.selectelfFile('Select ELF File', self.lineEdit_elffile))
        self.pushButton_browsecombined.clicked.connect(
            lambda: self.selectbinFile('Select Bin File', self.lineEdit_combinedfile))
        self.pushButton_path1.setToolTip('Select Bin File')
        self.pushButton_path2.setToolTip('Select Bin File')
        self.pushButton_path3.setToolTip('Select Bin File')
        self.pushButton_pathkey.setToolTip('Select Bin File')
        self.pushButtonconnect.clicked.connect(self.open_serial)
        self.pushButtonconnect.setToolTip('F3 - Open serial port')
        self.pushButton_disconnect.clicked.connect(self.close_serial)
        self.pushButton_disconnect.setToolTip('Ctrl+F4 - Close serial port')
        self.comboBox_baud.addItems(['1500000', '921600', '512000', '256000', '230400', '115200', '74880', '9600'])
        self.comboBox_baud.setCurrentIndex(5)
        self.comboBox_baud.currentIndexChanged.connect(self.baudSelect)
        self.baudRate = int(self.comboBox_baud.currentText())
        self.comboBox_readstatusreg.addItems(['1', '2', '3'])
        self.comboBox_writestatusreg.addItems(['1', '2', '3'])
        self.comboBox_flashmode.addItems(["qio", "dio", "dout"])
        self.comboBox_flashmode.currentIndexChanged.connect(self.baudSelect)
        self.flashmode = self.comboBox_flashmode.currentText()
        self.comboBox_chip.addItems(['ESP32', 'ESP8266'])
        self.comboBox_chip.currentIndexChanged.connect(self.chipSelect)
        comPort = []
        try:
            for x in serial.tools.list_ports.comports():
                comPort.append(str(x.device))
        except IndexError:
            pass
        self.comboBox_serial.addItems(comPort)
        self.comboBox_serial.popupAboutToBeShown.connect(self.comPortClick)
        self.comboBox_serial.currentIndexChanged.connect(self.comPortSelect)
        self.port = self.comboBox_serial.currentText()
        self.comboBox_flashsize.addItems(self.memoryESP32)
        self.comboBox_flashsize.currentIndexChanged.connect(self.memorySelect)
        self.flasSize = self.comboBox_flashsize.currentText()
        self.pushButton_default.clicked.connect(self.onDefault)
        self.pushButton_cleardata.clicked.connect(self.clearData)
        self.pushButton_selectall.clicked.connect(self.selectall)
        self.pushButton_eraseentireflash.clicked.connect(self.erase)
        self.pushButton_flashfirmware.clicked.connect(self.flashfirmware)
        self.pushButton_clearop.clicked.connect(self.clear_log)
        self.pushButton_combine.clicked.connect(self.combine_bin)
        self.pushButton_readmem.clicked.connect(self.readmemory)
        self.pushButton_writemem.clicked.connect(self.writememory)
        self.pushButton_dumpmem.clicked.connect(self.dumpmemory)
        self.pushButton_eraseregion.clicked.connect(self.eraseregion)
        self.pushButton_chipid.clicked.connect(self.chipId)
        self.pushButton_readstatusreg.clicked.connect(self.readstatusreg)
        self.pushButton_writestatusreg.clicked.connect(self.writestatusreg)
        self.pushButton_clearmemo.clicked.connect(self.clear_mem)
        self.pushButton_chipid.clicked.connect(self.getChipid)
        self.pushButton_verifyflash.clicked.connect(self.verifyFlash)
        self.pushButton_loadram.clicked.connect(self.loadRam)
        self.pushButton_generatebinfromelf.clicked.connect(self.convertELFtoBIN)
        self.pushButton_imageinfo.clicked.connect(self.imageInfo)
        self.pushButton_13.clicked.connect(self.flash_boot)
        self.pushButton_flashAll.clicked.connect(self.flash_all)
        self.pushButton_flashcombined.clicked.connect(self.flashcombined)
        self.pushButton_readFlash.clicked.connect(self.readFlashfunc)
        self.connectshortcut = QShortcut(QKeySequence("CTRL+C"), self)
        self.connectshortcut.activated.connect(self.open_serial)
        self.pushButtonconnect.setStatusTip('Open Serial Connection CTRL+C')
        self.disconnectshortcut = QShortcut(QKeySequence("CTRL+D"), self)
        self.disconnectshortcut.activated.connect(self.close_serial)
        self.pushButton_disconnect.setStatusTip('Close Serial Connection CTRL+D')
        self.flashBootShortcut = QShortcut(QKeySequence("CTRL+B"), self)
        self.flashBootShortcut.activated.connect(self.flash_boot)
        self.pushButton_13.setStatusTip('Flash Bootloader CTRL+B')
        self.flashfirmwareShortcut = QShortcut(QKeySequence("CTRL+F"), self)
        self.flashfirmwareShortcut.activated.connect(self.flashfirmware)
        self.pushButton_flashfirmware.setStatusTip('Flash Firmware CTRL+F')
        self.flashallshortcut = QShortcut(QKeySequence("CTRL+A"), self)
        self.flashallshortcut.activated.connect(self.flash_all)
        self.pushButton_flashAll.setStatusTip('Flash Bootloader,Partition & Firmware CTRL+A')
        self.verifyshortcut = QShortcut(QKeySequence("Ctrl+V"), self)
        self.verifyshortcut.activated.connect(self.verifyFlash)
        self.pushButton_verifyflash.setStatusTip('Verify Flash  CTRL+V')
        self.chipIDshortcut = QShortcut(QKeySequence("CTRL+I"), self)
        self.chipIDshortcut.activated.connect(self.chipId)
        self.pushButton_chipid.setStatusTip('Chip Id CTRL+I')
        self.loadramshortcut = QShortcut(QKeySequence("CTRL+L"), self)
        self.loadramshortcut.activated.connect(self.loadRam)
        self.pushButton_loadram.setStatusTip('Load executable Bin into RAM CTRL+L')
        self.flashcombinedshortcut = QShortcut(QKeySequence("CTRL+ALT+F"), self)
        self.flashcombinedshortcut.activated.connect(self.flashcombined)
        self.pushButton_flashcombined.setStatusTip('Flash Combined Bin Files CTRL+ALT+F')
        self.eraseshortcut = QShortcut(QKeySequence("CTRL+E"), self)
        self.eraseshortcut.activated.connect(self.erase)
        self.pushButton_eraseentireflash.setStatusTip('Erase Entire Flash Memory CTRL+E')
        self.IMAGEINFOshortcut = QShortcut(QKeySequence("CTRL+ALT+I"), self)
        self.IMAGEINFOshortcut.activated.connect(self.imageInfo)
        self.pushButton_imageinfo.setStatusTip('Image Info CTRL+ALT+I')
        self.clearopshortcut = QShortcut(QKeySequence("CTRL+ALT+C"), self)
        self.clearopshortcut.activated.connect(self.clear_log)
        self.pushButton_clearop.setStatusTip('Clear Log CTRL+ALT+C')
        self.stopshortcut = QShortcut(QKeySequence("CTRL+S"), self)
        self.stopshortcut.activated.connect(self.onStopbutton)
        self.pushButton_stop.setStatusTip('Stop Process CTRL+S')
        self.readmemshortcut = QShortcut(QKeySequence("CTRL+M"), self)
        self.readmemshortcut.activated.connect(self.readmemory)
        self.pushButton_readmem.setStatusTip('Read Memory CTRL+M')
        self.writememshortcut = QShortcut(QKeySequence("CTRL+W"), self)
        self.writememshortcut.activated.connect(self.writememory)
        self.pushButton_writemem.setStatusTip('Write Memory CTRL+W')
        self.eraseregionshortcut = QShortcut(QKeySequence("CTRL+ALT+E"), self)
        self.eraseregionshortcut.activated.connect(self.eraseregion)
        self.pushButton_eraseregion.setStatusTip('Erase a Region of Flash  CTRL+ALT+E')
        self.dumpshortcut = QShortcut(QKeySequence("CTRL+ALT+D"), self)
        self.dumpshortcut.activated.connect(self.dumpmemory)
        self.pushButton_dumpmem.setStatusTip('Dump Memory into File CTRL+ALT+D')
        self.readstatshortcut = QShortcut(QKeySequence("CTRL+ALT+S"), self)
        self.readstatshortcut.activated.connect(self.readstatusreg)
        self.pushButton_readstatusreg.setStatusTip('Read Status Register CTRL+ALT+R')
        self.writestatshortcut = QShortcut(QKeySequence("CTRL+ALT+W"), self)
        self.writestatshortcut.activated.connect(self.writestatusreg)
        self.pushButton_writestatusreg.setStatusTip('Write Status Register CTRL+ALT+W')
        self.clearmemstatshortcut = QShortcut(QKeySequence("C"), self)
        self.clearmemstatshortcut.activated.connect(self.clear_mem)
        self.pushButton_clearmemo.setStatusTip('Clear Log C')
        self.pushButton_Fusedump.clicked.connect(self.fusedump)
        self.pushButton_logout.clicked.connect(self.pushbutton_handler)
        self.actionProduction_Mode.triggered.connect(self.pushbutton_handler)
        self.pushButtoncollapsexpand.clicked.connect(self.expandcollapseopt)
        self.pushButtoncollapsexpandm.clicked.connect(self.expandcollapsemem)
        self.pushButton_reloadfusetab.clicked.connect(self.refreshsummary)
        self.pushButton_genkey.clicked.connect(self.generateencryptionkey)
        self.pushButton_encrypt.clicked.connect(self.encryptflash)
        self.pushButton_zipfiles.clicked.connect(self.createpackage)
        # self.btnref.clicked.connect(self.refreshsummary2)
        self.btn1.clicked.connect(self.burnfirst)
        self.btn2.clicked.connect(self.burnsecond)
        self.btn3.clicked.connect(self.burnthird)
        self.btn4.clicked.connect(self.burnfourth)
        self.btn5.clicked.connect(self.burnfifth)
        self.btn6.clicked.connect(self.burnsixth)
        self.btn7.clicked.connect(self.burnseventh)
        self.btn8.clicked.connect(self.burneighth)
        self.btn9.clicked.connect(self.burnnineth)
        self.btn10.clicked.connect(self.burn10)
        self.btn11.clicked.connect(self.burn11)
        self.btn12.clicked.connect(self.burn12)
        self.btn13.clicked.connect(self.burn13)
        self.btn14.clicked.connect(self.burn14)
        self.btn15.clicked.connect(self.burn15)
        self.btn16.clicked.connect(self.burn16)
        self.btn17.clicked.connect(self.burn17)
        self.btn18.clicked.connect(self.burn18)
        self.btn19.clicked.connect(self.burn19)
        self.btn20.clicked.connect(self.burn20)
        self.btn21.clicked.connect(self.burn21)
        self.btn22.clicked.connect(self.burn22)
        self.btn23.clicked.connect(self.burn23)
        self.btn24.clicked.connect(self.burn24)
        self.btn25.clicked.connect(self.burn25)
        self.btn26.clicked.connect(self.burn26)
        self.btn27.clicked.connect(self.burn27)
        self.btn28.clicked.connect(self.burn28)
        self.btn29.clicked.connect(self.burn29)
        self.btn30.clicked.connect(self.burn30)
        self.btn31.clicked.connect(self.burn31)
        self.btn32.clicked.connect(self.burn32)
        self.pushButton_savesetting.clicked.connect(self.saveSettingstofilebutton)
        self.btnexport.clicked.connect(self.exportfuse)
        self.btnref.clicked.connect(self.refbuttonfunction)

    def expandcollapseopt(self):
        testwidth = self.plainTextEditadvanced.width()
        testheight = self.plainTextEditadvanced.height()
        if testheight == 511 and testwidth == 371:
            self.plainTextEditadvanced.setGeometry(QtCore.QRect(425, 10, 0, 0))
            self.groupBox.setGeometry(QtCore.QRect(30, 10, 720, 100))
            self.groupBox_2.setGeometry(QtCore.QRect(30, 140, 720, 161))
            self.groupBox_3.setGeometry(QtCore.QRect(30, 330, 720, 121))
            self.pushButton_verifyflash.setGeometry(QtCore.QRect(30, 20, 300, 25))
            self.lineEdit_verifyoffset.setGeometry(QtCore.QRect(390, 20, 300, 25))
            self.pushButton_loadram.setGeometry(QtCore.QRect(30, 55, 300, 25))
            self.pushButton_chipid.setGeometry(QtCore.QRect(390, 55, 300, 25))
            self.pushButton_flashcombined.setGeometry(QtCore.QRect(30, 30, 300, 25))
            self.pushButton_flashfirmware.setGeometry(QtCore.QRect(30, 70, 300, 25))
            self.pushButton_13.setGeometry(QtCore.QRect(30, 110, 300, 25))
            self.pushButton_flashAll.setGeometry(QtCore.QRect(390, 30, 300, 25))
            self.pushButton_eraseentireflash.setGeometry(QtCore.QRect(390, 70, 300, 25))
            self.pushButton_imageinfo.setGeometry(QtCore.QRect(390, 110, 300, 25))
            self.pushButton_clearop.setGeometry(QtCore.QRect(30, 30, 300, 25))
            self.pushButton_stop.setGeometry(QtCore.QRect(390, 30, 300, 25))
            self.progressBar.setGeometry(QtCore.QRect(30, 80, 660, 13))
            self.pushButtoncollapsexpand.setIcon(QIcon('icons/expandv.png'))
            self.pushButtoncollapsexpand.setIconSize(QSize(24, 15))
            self.pushButton_encrypt.setGeometry(QtCore.QRect(370, 265, 320, 25))
        if testheight == 0 and testwidth == 0:
            self.plainTextEditadvanced.setGeometry(QtCore.QRect(425, 10, 371, 511))
            self.groupBox.setGeometry(QtCore.QRect(30, 10, 381, 100))
            self.groupBox_2.setGeometry(QtCore.QRect(30, 140, 381, 161))
            self.groupBox_3.setGeometry(QtCore.QRect(30, 330, 381, 121))
            self.pushButton_verifyflash.setGeometry(QtCore.QRect(20, 20, 200, 25))
            self.lineEdit_verifyoffset.setGeometry(QtCore.QRect(250, 20, 111, 25))
            self.pushButton_loadram.setGeometry(QtCore.QRect(20, 55, 160, 25))
            self.pushButton_chipid.setGeometry(QtCore.QRect(200, 55, 160, 25))
            self.pushButton_flashcombined.setGeometry(QtCore.QRect(20, 30, 161, 25))
            self.pushButton_flashfirmware.setGeometry(QtCore.QRect(20, 70, 161, 25))
            self.pushButton_13.setGeometry(QtCore.QRect(20, 110, 161, 25))
            self.pushButton_flashAll.setGeometry(QtCore.QRect(200, 30, 161, 25))
            self.pushButton_eraseentireflash.setGeometry(QtCore.QRect(200, 70, 161, 25))
            self.pushButton_imageinfo.setGeometry(QtCore.QRect(200, 110, 161, 25))
            self.pushButton_clearop.setGeometry(QtCore.QRect(20, 30, 161, 25))
            self.pushButton_stop.setGeometry(QtCore.QRect(200, 30, 161, 25))
            self.progressBar.setGeometry(QtCore.QRect(20, 80, 340, 13))
            self.pushButtoncollapsexpand.setIcon(QIcon('icons/collapsev.png'))
            self.pushButtoncollapsexpand.setIconSize(QSize(24, 15))

    def expandcollapsemem(self):
        testwidth = self.plainTextEditadvancedmem.width()
        testheight = self.plainTextEditadvancedmem.height()
        if testheight == 511 and testwidth == 371:
            self.plainTextEditadvancedmem.setGeometry(QtCore.QRect(425, 10, 0, 0))
            self.groupBoxmemo.setGeometry(QtCore.QRect(30, 10, 720, 350))
            self.groupBox_2memo.setGeometry(QtCore.QRect(30, 370, 720, 100))
            self.pushButton_readmem.setGeometry(QtCore.QRect(30, 20, 320, 25))
            self.lineEditreadmemaddr.setGeometry(QtCore.QRect(370, 20, 320, 25))
            self.pushButton_writemem.setGeometry(QtCore.QRect(30, 55, 150, 25))
            self.lineEdit_writemem1.setGeometry(QtCore.QRect(200, 55, 150, 25))
            self.lineEdit_writemem2.setGeometry(QtCore.QRect(370, 55, 150, 25))
            self.lineEdit_writemem3.setGeometry(QtCore.QRect(540, 55, 150, 25))
            self.pushButton_eraseregion.setGeometry(QtCore.QRect(30, 90, 320, 25))
            self.lineEdit_eraseregion1.setGeometry(QtCore.QRect(370, 90, 150, 25))
            self.lineEdit_eraseregion2.setGeometry(QtCore.QRect(540, 90, 150, 25))
            self.pushButton_dumpmem.setGeometry(QtCore.QRect(30, 125, 320, 25))
            self.lineEdit_dumpmem1.setGeometry(QtCore.QRect(370, 125, 150, 25))
            self.lineEdit_dumpmem2.setGeometry(QtCore.QRect(540, 125, 150, 25))
            self.pushButton_readstatusreg.setGeometry(QtCore.QRect(30, 160, 320, 25))
            self.comboBox_readstatusreg.setGeometry(QtCore.QRect(370, 160, 320, 25))
            self.pushButton_writestatusreg.setGeometry(QtCore.QRect(30, 195, 320, 25))
            self.comboBox_writestatusreg.setGeometry(QtCore.QRect(370, 195, 320, 25))
            self.pushButton_readFlash.setGeometry(QtCore.QRect(30, 230, 320, 25))
            self.lineEdit_readFlash1.setGeometry(QtCore.QRect(370, 230, 150, 25))
            self.lineEdit_readFlash2.setGeometry(QtCore.QRect(540, 230, 150, 25))
            self.pushButton_Fusedump.setGeometry(QtCore.QRect(30, 265, 320, 25))
            self.pushButton_encrypt.setGeometry(QtCore.QRect(370, 265, 320, 25))
            self.pushButton_clearmemo.setGeometry(QtCore.QRect(30, 20, 320, 25))
            self.pushButton_stopmemo.setGeometry(QtCore.QRect(370, 20, 320, 25))
            self.progressBarmemo.setGeometry(QtCore.QRect(30, 60, 660, 13))
            self.pushButtoncollapsexpandm.setIcon(QIcon('icons/expandv.png'))
            self.pushButtoncollapsexpandm.setIconSize(QSize(24, 15))
        if testheight == 0 and testwidth == 0:
            self.plainTextEditadvancedmem.setGeometry(QtCore.QRect(425, 10, 371, 511))
            self.groupBoxmemo.setGeometry(QtCore.QRect(30, 10, 381, 400))
            self.groupBox_2memo.setGeometry(QtCore.QRect(30, 421, 381, 100))
            self.pushButton_readmem.setGeometry(QtCore.QRect(20, 20, 221, 25))
            self.lineEditreadmemaddr.setGeometry(QtCore.QRect(250, 20, 111, 25))
            self.pushButton_writemem.setGeometry(QtCore.QRect(20, 55, 101, 25))
            self.lineEdit_writemem1.setGeometry(QtCore.QRect(132, 55, 72, 25))
            self.lineEdit_writemem2.setGeometry(QtCore.QRect(212, 55, 70, 25))
            self.lineEdit_writemem3.setGeometry(QtCore.QRect(290, 55, 70, 25))
            self.pushButton_eraseregion.setGeometry(QtCore.QRect(20, 90, 101, 25))
            self.lineEdit_eraseregion1.setGeometry(QtCore.QRect(132, 90, 111, 25))
            self.lineEdit_eraseregion2.setGeometry(QtCore.QRect(250, 90, 111, 25))
            self.pushButton_dumpmem.setGeometry(QtCore.QRect(20, 125, 101, 25))
            self.lineEdit_dumpmem1.setGeometry(QtCore.QRect(132, 125, 111, 25))
            self.lineEdit_dumpmem2.setGeometry(QtCore.QRect(250, 125, 111, 25))
            self.pushButton_readstatusreg.setGeometry(QtCore.QRect(20, 160, 160, 25))
            self.comboBox_readstatusreg.setGeometry(QtCore.QRect(200, 160, 160, 25))
            self.pushButton_writestatusreg.setGeometry(QtCore.QRect(20, 195, 160, 25))
            self.comboBox_writestatusreg.setGeometry(QtCore.QRect(200, 195, 160, 25))
            self.pushButton_readFlash.setGeometry(QtCore.QRect(20, 230, 101, 25))
            self.lineEdit_readFlash1.setGeometry(QtCore.QRect(132, 230, 111, 25))
            self.lineEdit_readFlash2.setGeometry(QtCore.QRect(250, 230, 111, 25))
            self.pushButton_Fusedump.setGeometry(QtCore.QRect(20, 265, 101, 25))
            self.pushButton_clearmemo.setGeometry(QtCore.QRect(20, 20, 161, 25))
            self.pushButton_stopmemo.setGeometry(QtCore.QRect(200, 20, 161, 25))
            self.progressBarmemo.setGeometry(QtCore.QRect(20, 60, 340, 13))
            self.pushButtoncollapsexpandm.setIcon(QIcon('icons/collapsev.png'))
            self.pushButtoncollapsexpandm.setIconSize(QSize(24, 15))
            self.pushButton_encrypt.setGeometry(QtCore.QRect(132, 265, 101, 25))

    def pushbutton_handler(self):
        choice = QtWidgets.QMessageBox.question(self, ' Confirm Exit ', "Are You Sure You want To Exit Advanced Mode ?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            self.loginwin = OpmodeMain.ESPToolGUIApp()
            self.close_serial()
            self.savesettings()
            self.close()
            self.loginwin.show()
        else:
            self.savesettings()
            pass

    def setProgressValdump(self, val):
        self.progressBarmemo.setValue(val)

    def setProgressVal(self, val):
        self.progressBar.setValue(val)

    def tick(self):
        if self.ser.is_open == True:
            try:
                s = self.ser.read(512)
                if len(s) > 0:
                    self.plainTextEditadvanced.appendPlainText(s.decode('utf-8'))
            except:
                pass

    def savesettings(self):
        settings = QSettings()

        settings.setValue(SETTINGS_check1, self.checkBox_1.isChecked())
        settings.setValue(SETTINGS_check2, self.checkBox_2.isChecked())
        settings.setValue(SETTINGS_check3, self.checkBox_3.isChecked())
        settings.setValue(SETTINGS_TRAYbaud, self.comboBox_baud.currentIndex())
        settings.setValue(SETTINGS_TRAYchip, self.comboBox_chip.currentIndex())
        settings.setValue(SETTINGS_TRAYflashsize, self.comboBox_flashsize.currentIndex())
        settings.setValue(SETTINGS_TRAYflashmode, self.comboBox_flashmode.currentIndex())
        settings.setValue(SETTINGS_TRAYreadstatus, self.comboBox_readstatusreg.currentIndex())
        settings.setValue(SETTINGS_TRAYwritestatus, self.comboBox_writestatusreg.currentIndex())

        settings.setValue(SETTING_verifyFlash, self.lineEdit_verifyoffset.text())
        settings.setValue(SETTING_dumpmem1, self.lineEdit_dumpmem1.text())
        settings.setValue(SETTING_dumpmem2, self.lineEdit_dumpmem2.text())
        settings.setValue(SETTING_eraseregion1, self.lineEdit_eraseregion1.text())
        settings.setValue(SETTING_eraseregion2, self.lineEdit_eraseregion2.text())
        settings.setValue(SETTING_offset1, self.lineEdit_offset1.text())
        settings.setValue(SETTING_offset2, self.lineEdit_offset2.text())
        settings.setValue(SETTING_offset3, self.lineEdit_offset3.text())
        settings.setValue(SETTING_offsetcombined, self.lineEdit_offsetcombined.text())
        settings.setValue(SETTING_path1, self.lineEdit_path1.text())
        settings.setValue(SETTING_path2, self.lineEdit_path2.text())
        settings.setValue(SETTING_path3, self.lineEdit_path3.text())
        settings.setValue(SETTING_path4, self.lineEdit_combinedfile.text())
        settings.setValue(SETTING_path5, self.lineEdit_elffile.text())
        settings.setValue(SETTING_path6, self.lineEdit_keypath.text())
        settings.setValue(SETTING_readflash1, self.lineEdit_readFlash1.text())
        settings.setValue(SETTING_readflash2, self.lineEdit_readFlash2.text())
        settings.setValue(SETTING_writemem1, self.lineEdit_writemem1.text())
        settings.setValue(SETTING_writemem2, self.lineEdit_writemem2.text())
        settings.setValue(SETTING_writemem3, self.lineEdit_writemem3.text())
        settings.setValue(SETTING_readmemory, self.lineEditreadmemaddr.text())
        settings.setValue(SETTING_offsetcombined, self.lineEdit_offsetcombined.text())
        settings.setValue(SETTING_plainmem, self.plainTextEditadvancedmem.toPlainText())
        settings.setValue(SETTINGS_plainadv, self.plainTextEditadvanced.toPlainText())

        settings.sync()

    def initsettings(self):

        settings = QSettings()

        check_state1 = settings.value(SETTINGS_check1, False, type=bool)
        check_state2 = settings.value(SETTINGS_check2, False, type=bool)
        check_state3 = settings.value(SETTINGS_check3, False, type=bool)

        baud_combo = settings.value(SETTINGS_TRAYbaud, self.comboBox_baud.currentIndex(), type=int)
        chip_combo = settings.value(SETTINGS_TRAYchip, self.comboBox_chip.currentIndex(), type=int)
        flashsize_combo = settings.value(SETTINGS_TRAYflashsize, self.comboBox_flashsize.currentIndex(), type=int)
        flashmode_combo = settings.value(SETTINGS_TRAYflashmode, self.comboBox_flashmode.currentIndex(), type=int)
        readregstatus_combo = settings.value(SETTINGS_TRAYreadstatus, self.comboBox_readstatusreg.currentIndex(),
                                             type=int)
        writeregstatus_combo = settings.value(SETTINGS_TRAYwritestatus, self.comboBox_writestatusreg.currentIndex(),
                                              type=int)
        self.checkBox_1.setChecked(check_state1)
        self.checkBox_2.setChecked(check_state2)
        self.checkBox_3.setChecked(check_state3)
        self.comboBox_baud.setCurrentIndex(baud_combo)
        self.comboBox_chip.setCurrentIndex(chip_combo)
        self.comboBox_flashsize.setCurrentIndex(flashsize_combo)
        self.comboBox_flashmode.setCurrentIndex(flashmode_combo)
        self.comboBox_readstatusreg.setCurrentIndex(readregstatus_combo)
        self.comboBox_writestatusreg.setCurrentIndex(writeregstatus_combo)

        if settings.value(SETTING_verifyFlash) is not None:
            self.lineEdit_verifyoffset.setText(settings.value(SETTING_verifyFlash))
        if settings.value(SETTING_readmemory) is not None:
            self.lineEditreadmemaddr.setText(settings.value(SETTING_readmemory))
        if settings.value(SETTING_writemem1) is not None:
            self.lineEdit_writemem1.setText(settings.value(SETTING_writemem1))
        if settings.value(SETTING_writemem2) is not None:
            self.lineEdit_writemem2.setText(settings.value(SETTING_writemem2))
        if settings.value(SETTING_writemem3) is not None:
            self.lineEdit_writemem3.setText(settings.value(SETTING_writemem3))
        if settings.value(SETTING_readflash1) is not None:
            self.lineEdit_readFlash1.setText(settings.value(SETTING_readflash1))
        if settings.value(SETTING_readflash2) is not None:
            self.lineEdit_readFlash2.setText(settings.value(SETTING_readflash2))
        if settings.value(SETTING_dumpmem1) is not None:
            self.lineEdit_dumpmem1.setText(settings.value(SETTING_dumpmem1))
        if settings.value(SETTING_dumpmem2) is not None:
            self.lineEdit_dumpmem2.setText(settings.value(SETTING_dumpmem2))
        if settings.value(SETTING_eraseregion1) is not None:
            self.lineEdit_eraseregion1.setText(settings.value(SETTING_eraseregion1))
        if settings.value(SETTING_eraseregion2) is not None:
            self.lineEdit_eraseregion2.setText(settings.value(SETTING_eraseregion2))
        if settings.value(SETTING_offset1) is not None:
            self.lineEdit_offset1.setText(settings.value(SETTING_offset1))
        if settings.value(SETTING_offset2) is not None:
            self.lineEdit_offset2.setText(settings.value(SETTING_offset2))
        if settings.value(SETTING_offset3) is not None:
            self.lineEdit_offset3.setText(settings.value(SETTING_offset3))
        if settings.value(SETTING_path1) is not None:
            self.lineEdit_path1.setText(settings.value(SETTING_path1))
        if settings.value(SETTING_path2) is not None:
            self.lineEdit_path2.setText(settings.value(SETTING_path2))
        if settings.value(SETTING_path3) is not None:
            self.lineEdit_path3.setText(settings.value(SETTING_path3))
        if settings.value(SETTING_path4) is not None:
            self.lineEdit_combinedfile.setText(settings.value(SETTING_path4))
        if settings.value(SETTING_path5) is not None:
            self.lineEdit_elffile.setText(settings.value(SETTING_path5))
        if settings.value(SETTING_path6) is not None:
            self.lineEdit_keypath.setText(settings.value(SETTING_path6))
        if settings.value(SETTING_offsetcombined) is not None:
            self.lineEdit_offsetcombined.setText(settings.value(SETTING_offsetcombined))
        if settings.value(SETTING_plainmem) is not None:
            self.plainTextEditadvancedmem.setPlainText(settings.value(SETTING_plainmem))
        if settings.value(SETTINGS_plainadv) is not None:
            self.plainTextEditadvanced.setPlainText(settings.value(SETTINGS_plainadv))

    # *******************************1st_Tab****************************************************************************

    def baudSelect(self):
        self.baudRate = int(self.comboBox_baud.currentText())

    def portSelect(self):
        self.port = self.comboBox_serial.currentText()
        Com_port = self.comboBox_serial.currentText()

    def comPortClick(self):
        comPort = []
        try:
            for x in serial.tools.list_ports.comports():
                comPort.append(str(x.device))
        except IndexError:
            pass
        self.comboBox_serial.clear()
        self.comboBox_serial.addItems(comPort)

    def comPortSelect(self):
        self.port = self.comboBox_serial.currentText()
        settingsport = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        settingsport.setValue(comport, self.comboBox_serial.currentText())
        settingsport.sync()

    def open_serial(self):
        self.port = self.comboBox_serial.currentText()
        try:
            if self.ser.is_open == False:
                self.ser = serial.Serial(self.port, baudrate=self.comboBox_baud.currentText(), timeout=0,
                                         bytesize=serial.EIGHTBITS,
                                         parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, rtscts=False,
                                         dsrdtr=False)
            if self.ser.is_open == True:
                self.label_8.setText("Connection Established !")
                scene = QGraphicsScene()
                scene.addPixmap(QPixmap('icons/connected.png'))
                self.graphicsView.setScene(scene)
                self.label_8.setStyleSheet(" border-radius: 5px;  color: #039BE5;font-weight: bold;")
        except:
            self.label_8.setText("Error! Check COM Port !")
            scene = QGraphicsScene()
            scene.addPixmap(QPixmap('icons/wrongcom.png'))
            self.graphicsView.setScene(scene)
            self.label_8.setStyleSheet(" border-radius: 5px;  color: #e53935;font-weight: bold;")

    def close_serial(self):
        self.port = self.comboBox_serial.currentText()
        self.ser.close()
        self.label_8.setText("Serial Port Closed !")
        scene = QGraphicsScene()
        scene.addPixmap(QPixmap('icons/disconnected.png'))
        self.graphicsView.setScene(scene)
        self.label_8.setStyleSheet(" border-radius: 5px;  color: #039BE5;font-weight: bold;")

    # *******************************2nd_Tab****************************************************************************
    def verifyFlash(self):
        # settingsverify = QSettings("verif_ini.ini", QSettings.IniFormat)
        verifyoffset = self.lineEdit_verifyoffset.text()
        if (verifyoffset == "") or (verifyoffset == " "):
            QMessageBox.warning(self, 'Error', "Missing Argument: " + "Please insert an Offset @ First", QMessageBox.Ok,
                                QMessageBox.Ok)
        else:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getOpenFileName(self, "Image File To Check", filter='(*.bin)', options=options)
            self.port = self.comboBox_serial.currentText()
            if not (fileName == "") and not fileName == " ":
                if os.name == 'nt':
                    if self.chip == 'ESP32':
                        self.process.start(
                            'python ' + self.bundle_dir + '/esptool.py --chip esp32 verify_flash --diff yes ' + " " + verifyoffset + " " + fileName)

                    if self.chip == 'ESP8266':
                        self.process.start(
                            'python ' + self.bundle_dir + '/esptool.py --chip esp8266 verify_flash --diff yes ' + " " + verifyoffset + " " + fileName)
                else:
                    if self.chip == 'ESP32':
                        self.process.start(
                            'sudo python ' + self.bundle_dir + '/esptool.py --chip esp32 verify_flash --diff yes ' + " " + verifyoffset + " " + fileName)

                    else:
                        self.process.start(
                            'sudo python ' + self.bundle_dir + '/esptool.py --chip esp8266 verify_flash --diff yes ' + " " + verifyoffset + " " + fileName)

            else:
                self.plainTextEditadvanced.appendPlainText("Operation Verify Flash Aborted ")
                QMessageBox.warning(self, 'Operation Aborted', "Operation Verify Flash Aborted ", QMessageBox.Ok)
        # diff_state = settingsverify.value(verifconst, type=str)
        # QMessageBox.warning(self, 'Verify Result', diff_state, QMessageBox.Ok)

    def loadRam(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Program to load into RAM", filter='(*.bin)', options=options)
        if not (fileName == "") and not fileName == " ":
            self.port = self.comboBox_serial.currentText()
            if os.name == 'nt':
                if self.chip == 'ESP32':
                    self.process.start(
                        'python ' + self.bundle_dir + '/esptool.py  --no-stub load_ram ' + " " + fileName)
                if self.chip == 'ESP8266':
                    self.process.start(
                        'python' + self.bundle_dir + '/esptool.py  --no-stub load_ram ' + " " + fileName)
            else:
                if self.chip == 'ESP32':
                    self.process.start(
                        'sudo python ' + self.bundle_dir + '/esptool.py  --no-stub load_ram ' + " " + fileName)
                else:
                    self.process.start(
                        'sudo python ' + self.bundle_dir + '/esptool.py  --no-stub load_ram ' + " " + fileName)
        else:
            self.plainTextEditadvanced.appendPlainText("Operation Load RAM Aborted ")

    def getChipid(self):
        self.port = self.comboBox_serial.currentText()
        if os.name == 'nt':
            if self.chip == 'ESP32':
                self.process.start('python ' + self.bundle_dir + '/esptool.py --chip esp32 read_mac')
            if self.chip == 'ESP8266':
                self.process.start('python ' + self.bundle_dir + '/esptool.py --chip esp8266 chip_id')
        else:
            if self.chip == 'ESP32':
                self.process.start('sudo python ' + self.bundle_dir + '/esptool.py --chip esp32 read_mac')
            else:
                self.process.start('sudo python ' + self.bundle_dir + '/esptool.py --chip esp8266 chip_id')

    def chipId(self):
        self.port = self.comboBox_serial.currentText()
        if os.name == 'nt':
            if self.chip == 'ESP32':
                self.process.start('python ' + self.bundle_dir + '/esptool.py --chip esp32 chip_id ')
            if self.chip == 'ESP8266':
                self.process.start(
                    'python' + self.bundle_dir + '/esptool.py --chip esp8266 chip_id ')
        else:
            if self.chip == 'ESP32':
                self.process.start(
                    'sudo python ' + self.bundle_dir + '/esptool.py --chip esp32 chip_id ')
            else:
                self.process.start(
                    'sudo python ' + self.bundle_dir + '/esptool.py --chip esp8266 chip_id ')

    def flashcombined(self):
        offsetflashcomb = self.lineEdit_offsetcombined.text()
        self.port = self.comboBox_serial.currentText()
        if (self.lineEdit_combinedfile.text() == "") or (self.lineEdit_combinedfile.text() == " "):
            QMessageBox.warning(self, 'Error', "Missing Argument: " + "Firmware File is Missing", QMessageBox.Ok,
                                QMessageBox.Ok)
        elif offsetflashcomb == "" or offsetflashcomb == " ":
            QMessageBox.warning(self, 'Error', "Missing Argument: " + "Please Verify Offset Address", QMessageBox.Ok,
                                QMessageBox.Ok)
        else:
            self.ser.close()
            self.thread = MyprogressbarThread()
            self.thread.change_value.connect(self.setProgressVal)
            self.thread.start()
            if os.name == 'nt':
                if self.chip == 'ESP32':

                    self.process.start('python ' + self.bundle_dir + '/esptool.py --chip esp32 --port {0} --baud {1}\
                                                       --before default_reset --after hard_reset write_flash\
                                                       -z --flash_freq 80m --flash_mod dio --flash_size {2} \
                                                       {3} {4}'.format(self.port, self.baudRate, self.flasSize,
                                                                       offsetflashcomb
                                                                       , self.lineEdit_combinedfile.text()))
                else:
                    self.process.start('python' + self.bundle_dir + '/esptool.py --chip esp8266 --port {0} --baud {1}\
                                                       --before default_reset --after hard_reset write_flash --flash_size={2}\
                                                        {3} {4}'.format(self.port, self.baudRate, self.flasSize,
                                                                        offsetflashcomb
                                                                        , self.lineEdit_combinedfile.text()))
            else:
                if self.chip == 'ESP32':
                    self.process.start('sudo python ' + self.bundle_dir + '/esptool.py --chip esp32 --port {0} --baud {1}\
                                                   --before default_reset --after hard_reset write_flash\
                                                   -z --flash_freq 80m --flash_mod dio --flash_size {2} \
                                                   {3} {4}'.format(self.port, self.baudRate, self.flasSize,
                                                                   offsetflashcomb
                                                                   , self.lineEdit_combinedfile.text()))
                else:
                    self.process.start('sudo python ' + self.bundle_dir + '/esptool.py --chip esp8266 --port {0} --baud {1}\
                                                   --before default_reset --after hard_reset write_flash --flash_size={2}\
                                                    {3} {4}'.format(self.port, self.baudRate, self.flasSize,
                                                                    offsetflashcomb
                                                                    , self.lineEdit_combinedfile.text()))

    def flashfirmware(self):

        offsetflash = self.lineEdit_offset1.text()
        self.port = self.comboBox_serial.currentText()
        if (self.lineEdit_path1.text() == "") or (self.lineEdit_path1.text() == " "):
            QMessageBox.warning(self, 'Error', "Missing Argument: " + "Firmware File is Missing", QMessageBox.Ok,
                                QMessageBox.Ok)
        elif offsetflash == "" or offsetflash == " ":
            QMessageBox.warning(self, 'Error', "Missing Argument: " + "Please Verify Offset Address", QMessageBox.Ok,
                                QMessageBox.Ok)
        else:
            self.ser.close()
            self.thread = MyprogressbarThread()
            self.thread.change_value.connect(self.setProgressVal)
            self.thread.start()
            if os.name == 'nt':
                if self.chip == 'ESP32':
                    self.process.start('python ' + self.bundle_dir + '/esptool.py --chip esp32 --port {0} --baud {1}\
                                                --before default_reset --after hard_reset write_flash\
                                                -z --flash_freq 80m --flash_mod dio --flash_size {2} \
                                                {3} {4}'.format(self.port, self.baudRate, self.flasSize, offsetflash
                                                                , self.lineEdit_path1.text()))

                else:
                    self.process.start('python ' + self.bundle_dir + '/esptool.py --chip esp8266 --port {0} --baud {1}\
                                                --before default_reset --after hard_reset write_flash --flash_size={2}\
                                                 {3} {4}'.format(self.port, self.baudRate, self.flasSize, offsetflash
                                                                 , self.lineEdit_path1.text()))
            else:
                if self.chip == 'ESP32':
                    self.process.start('sudo python ' + self.bundle_dir + '/esptool.py --chip esp32 --port {0} --baud {1}\
                                            --before default_reset --after hard_reset write_flash\
                                            -z --flash_freq 80m --flash_mod dio --flash_size {2} \
                                            {3} {4}'.format(self.port, self.baudRate, self.flasSize, offsetflash
                                                            , self.lineEdit_path1.text()))
                else:
                    self.process.start('sudo python ' + self.bundle_dir + '/esptool.py --chip esp8266 --port {0} --baud {1}\
                                            --before default_reset --after hard_reset write_flash --flash_size={2}\
                                             {3} {4}'.format(self.port, self.baudRate, self.flasSize, offsetflash
                                                             , self.lineEdit_path1.text()))

    def flash_boot(self):
        offsetboot = self.lineEdit_offset2.text()
        offsetpart = self.lineEdit_offset3.text()
        if not os.path.isfile(self.lineEdit_path2.text()):
            QMessageBox.warning(self, 'Error', "Error: " + "invalid bootloader file.", QMessageBox.Ok, QMessageBox.Ok)
            return
        elif not os.path.isfile(self.lineEdit_path3.text()):
            QMessageBox.warning(self, 'Error', "Error: " + "invalid partition file.", QMessageBox.Ok, QMessageBox.Ok)
            return
        elif offsetboot == "" or offsetboot == " ":
            QMessageBox.warning(self, 'Error', "Missing Argument: " + "Please Verify Bootloader Offset Address",
                                QMessageBox.Ok, QMessageBox.Ok)
        elif offsetpart == "" or offsetpart == " ":
            QMessageBox.warning(self, 'Error', "Missing Argument: " + "Please Verify Partition Offset Address",
                                QMessageBox.Ok, QMessageBox.Ok)
        else:
            self.port = self.comboBox_serial.currentText()
            self.ser.close()
            self.thread = MyprogressbarThread()
            self.thread.change_value.connect(self.setProgressVal)
            self.thread.start()
            if os.name == 'nt':
                if self.chip == 'ESP32':
                    self.process.start('python ' + self.bundle_dir + '/esptool.py --chip esp32 --port {0} --baud {1}\
                                        --before default_reset --after hard_reset write_flash\
                                        -z --flash_freq 80m --flash_mod dio --flash_size {2} \
                                      {3} {4} {5} {6}'.format(self.port, self.baudRate, self.flasSize, offsetboot,
                                                              self.lineEdit_path2.text(), offsetpart,
                                                              self.lineEdit_path3.text()))
            else:
                if self.chip == 'ESP32':
                    self.process.start('sudo python ' + self.bundle_dir + '/esptool.py --chip esp32 --port {0} --baud {1}\
                                    --before default_reset --after hard_reset write_flash\
                                    -z --flash_freq 80m --flash_mod dio --flash_size {2} \
                                   {3} {4} {5} {6}'.format(self.port, self.baudRate, self.flasSize, offsetboot,
                                                           self.lineEdit_path2.text(), offsetpart,
                                                           self.lineEdit_path3.text()))

    def flash_all(self):
        offsetboot = self.lineEdit_offset2.text()
        offsetpart = self.lineEdit_offset3.text()
        offsetfirm = self.lineEdit_offset1.text()
        self.port = self.comboBox_serial.currentText()
        self.ser.close()

        if not os.path.isfile(self.lineEdit_path1.text()):
            QMessageBox.warning(self, 'Error', "Error: " + "invalid Firmware file.", QMessageBox.Ok, QMessageBox.Ok)
            return
        if not os.path.isfile(self.lineEdit_path2.text()):
            QMessageBox.warning(self, 'Error', "Error: " + "invalid bootloader file.", QMessageBox.Ok, QMessageBox.Ok)
            return
        elif not os.path.isfile(self.lineEdit_path3.text()):
            QMessageBox.warning(self, 'Error', "Error: " + "invalid partition file.", QMessageBox.Ok, QMessageBox.Ok)
            return
        elif offsetboot == "" or offsetboot == " ":
            QMessageBox.warning(self, 'Error', "Missing Argument: " + "Please Verify Bootloader Offset Address",
                                QMessageBox.Ok, QMessageBox.Ok)
        elif offsetpart == "" or offsetpart == " ":
            QMessageBox.warning(self, 'Error', "Missing Argument: " + "Please Verify Partition Offset Address",
                                QMessageBox.Ok, QMessageBox.Ok)
        elif offsetfirm == "" or offsetfirm == " ":
            QMessageBox.warning(self, 'Error', "Missing Argument: " + "Please Verify Firmware Offset Address",
                                QMessageBox.Ok, QMessageBox.Ok)
        else:
            self.thread = MyprogressbarThreadflashall()
            self.thread.change_valueall.connect(self.setProgressVal)
            self.thread.start()
            if os.name == 'nt':
                if self.chip == 'ESP32':
                    self.process.start('python ' + self.bundle_dir + '/esptool.py --chip esp32 --port {0} --baud {1}\
                                        --before default_reset --after hard_reset write_flash\
                                        -z --flash_freq 80m --flash_mod dio --flash_size {2} \
                                         {3} {4} {5} {6} {7} {8}'.format(self.port, self.baudRate, self.flasSize,
                                                                         offsetboot,
                                                                         self.lineEdit_path2.text(), offsetpart,
                                                                         self.lineEdit_path3.text(), offsetfirm,
                                                                         self.lineEdit_path1.text()))
                else:
                    self.process.start('python ' + self.bundle_dir + '/esptool.py --chip esp8266 --port {0} --baud {1}\
                                        --before default_reset --after hard_reset write_flash --flash_size={2}\
                                        {3}{4}{5}{6}{7}{8}'.format(self.port, self.baudRate, self.flasSize, offsetboot,
                                                                   self.lineEdit_path2.text(), offsetpart,
                                                                   self.lineEdit_path3.text(), offsetfirm,
                                                                   self.lineEdit_path1.text()))
            else:
                if self.chip == 'ESP32':
                    self.process.start('sudo python ' + self.bundle_dir + '/esptool.py --chip esp32 --port {0} --baud {1}\
                                    --before default_reset --after hard_reset write_flash\
                                    -z --flash_freq 80m --flash_mod dio --flash_size {2} \
                                 {3}{4}{5}{6}{7}{8}'.format(self.port, self.baudRate, self.flasSize, offsetboot,
                                                            self.lineEdit_path2.text(), offsetpart,
                                                            self.lineEdit_path3.text(), offsetfirm,
                                                            self.lineEdit_path1.text()))
                else:
                    self.process.start('sudo python ' + self.bundle_dir + '/esptool.py --chip esp8266 --port {0} --baud {1}\
                                    --before default_reset --after hard_reset write_flash --flash_size={2}\
                                   {3}{4}{5}{6}{7}{8}'.format(self.port, self.baudRate, self.flasSize, offsetboot,
                                                              self.lineEdit_path2.text(), offsetpart,
                                                              self.lineEdit_path3.text(), offsetfirm,
                                                              self.lineEdit_path1.text()))

    def erase(self):
        self.port = self.comboBox_serial.currentText()
        if os.name == 'nt':
            if self.chip == 'ESP32':
                self.process.start(
                    'python ' + self.bundle_dir + '/esptool.py --chip esp32 --port {0} --baud {1} erase_flash'.format(
                        self.port,
                        self.baudRate))
            if self.chip == 'ESP8266':
                self.process.start(
                    'python ' + self.bundle_dir + '/esptool.py --chip esp8266 --port {0} --baud {1} erase_flash'.format(
                        self.port,
                        self.baudRate))
        else:
            if self.chip == 'ESP32':
                self.process.start(
                    'sudo python ' + self.bundle_dir + '/esptool.py --chip esp32 --port {0} --baud {1} erase_flash'.format(
                        self.port, self.baudRate))
            else:
                self.process.start(
                    'sudo python ' + self.bundle_dir + '/esptool.py --chip esp8266 --port {0} --baud {1} erase_flash'.format(
                        self.port, self.baudRate))

    def imageInfo(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Image File To Check", filter='(*.bin)', options=options)
        if not (fileName == "") and not fileName == " ":
            self.port = self.comboBox_serial.currentText()
            if os.name == 'nt':
                if self.chip == 'ESP32':
                    self.process.start(
                        'python ' + self.bundle_dir + '/esptool.py  --chip esp32 image_info' + " " + fileName)
                if self.chip == 'ESP8266':
                    self.process.start(
                        'python ' + self.bundle_dir + '/esptool.py  --chip esp8266 image_info ' + " " + fileName)
            else:
                if self.chip == 'ESP32':
                    self.process.start(
                        'sudo python ' + self.bundle_dir + '/esptool.py  --chip esp32 image_info ' + " " + fileName)
                else:
                    self.process.start(
                        'sudo python ' + self.bundle_dir + '/esptool.py  --chip esp8266 image_info ' + " " + fileName)
        else:
            self.plainTextEditadvanced.appendPlainText("Operation Image Information Aborted ")

    def clear_log(self):
        self.plainTextEditadvanced.clear()
        self.lineEdit_eraseregion1.clear()
        self.lineEdit_eraseregion2.clear()
        self.lineEdit_writemem1.clear()
        self.lineEdit_writemem2.clear()
        self.lineEditreadmemaddr.clear()

    def onStopbutton(self):
        self.pushButton_stop.clicked.connect(self.process.kill)
        # Just to prevent accidentally running multiple times
        # Disable the button when process starts, and enable it when it finishes
        self.process.started.connect(lambda: self.pushButton_dumpmem.setEnabled(False))
        self.process.finished.connect(lambda: self.pushButton_dumpmem.setEnabled(True))
        self.process.started.connect(lambda: self.pushButton_flashfirmware.setEnabled(False))
        self.process.finished.connect(lambda: self.pushButton_flashfirmware.setEnabled(True))

    def onStopbuttonmemo(self):
        self.pushButton_stopmemo.clicked.connect(self.processmem.kill)
        # Just to prevent accidentally running multiple times
        # Disable the button when process starts, and enable it when it finishes
        self.process.started.connect(lambda: self.pushButton_dumpmem.setEnabled(False))
        self.process.finished.connect(lambda: self.pushButton_dumpmem.setEnabled(True))
        self.process.started.connect(lambda: self.pushButton_flashfirmware.setEnabled(False))
        self.process.finished.connect(lambda: self.pushButton_flashfirmware.setEnabled(True))

    def eraseregion(self):
        startingaddress = self.lineEdit_eraseregion1.text()
        length = self.lineEdit_eraseregion2.text()
        self.port = self.comboBox_serial.currentText()
        if (startingaddress == "") or (startingaddress == " "):
            QMessageBox.warning(self, 'Error', "Missing Argument: " + "Please insert a Starting address First",
                                QMessageBox.Ok, QMessageBox.Ok)
        elif (length == "") or (length == " "):
            QMessageBox.warning(self, 'Error',
                                "Missing Argument: " + "Please insert size of the memory segment to erase",
                                QMessageBox.Ok, QMessageBox.Ok)
        else:
            if os.name == 'nt':
                if self.chip == 'ESP32':
                    self.processmem.start(
                        'python ' + self.bundle_dir + '/esptool.py --chip esp32 erase_region ' + startingaddress + " " + length)
                if self.chip == 'ESP8266':
                    self.processmem.start(
                        'python ' + self.bundle_dir + '/esptool.py --chip esp8266 erase_region ' + startingaddress + " " + length)
            else:
                if self.chip == 'ESP32':
                    self.processmem.start(
                        'sudo python ' + self.bundle_dir + '/esptool.py --chip esp32 erase_region ' + startingaddress + " " + length)
                else:
                    self.processmem.start(
                        'sudo python ' + self.bundle_dir + '/esptool.py --chip esp8266 erase_region ' + startingaddress + " " + length)

    def clear_mem(self):
        self.plainTextEditadvancedmem.clear()
        self.lineEdit_dumpmem2.clear()
        self.lineEdit_dumpmem1.clear()
        self.lineEdit_eraseregion2.clear()
        self.lineEdit_eraseregion1.clear()
        self.lineEditreadmemaddr.clear()
        self.lineEdit_writemem2.clear()
        self.lineEdit_writemem1.clear()

    def fusesummary(self):
        self.port = self.comboBox_serial.currentText()
        if os.name == 'nt':
            if self.chip == 'ESP32':
                self.processmem.start(
                    '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' summary')
            if self.chip == 'ESP8266':
                self.processmem.start(
                    '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' summary')
        else:
            if self.chip == 'ESP32':
                self.processmem.start(
                    'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' summary')
            else:
                self.processmem.start(
                    'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' summary')

    def fusedump(self):
        self.port = self.comboBox_serial.currentText()
        if os.name == 'nt':
            if self.chip == 'ESP32':
                self.processmem.start(
                    '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' dump')
            if self.chip == 'ESP8266':
                self.processmem.start(
                    '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' dump')
        else:
            if self.chip == 'ESP32':
                self.processmem.start(
                    'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' dump')
            else:
                self.processmem.start(
                    'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' dump')

    # *********************************3rd_Tab**************************************************************************
    def readmemory(self):
        memoryaddr = self.lineEditreadmemaddr.text()
        self.port = self.comboBox_serial.currentText()
        if (memoryaddr == "") or (memoryaddr == " "):
            QMessageBox.warning(self, 'Error', "Missing Argument: " + "Please insert an address First", QMessageBox.Ok,
                                QMessageBox.Ok)
        else:
            if os.name == 'nt':
                if self.chip == 'ESP32':
                    self.processmem.start(
                        'python ' + self.bundle_dir + '/esptool.py --chip esp32 read_mem ' + memoryaddr)
                if self.chip == 'ESP8266':
                    self.processmem.start(
                        'python ' + self.bundle_dir + '/esptool.py --chip esp8266 read_mem ' + memoryaddr)
            else:
                if self.chip == 'ESP32':
                    self.processmem.start(
                        'sudo python ' + self.bundle_dir + '/esptool.py --chip esp32 read_mem ' + memoryaddr)
                else:
                    self.processmem.start(
                        'sudo python ' + self.bundle_dir + '/esptool.py --chip esp8266 read_mem ' + memoryaddr)

    def readstatusreg(self):
        RDSR = self.comboBox_readstatusreg.currentText()
        self.port = self.comboBox_serial.currentText()
        if os.name == 'nt':
            if self.chip == 'ESP32':
                self.processmem.start(
                    'python ' + self.bundle_dir + '/esptool.py --chip esp32 read_flash_status --bytes  ' + " " + RDSR)
            if self.chip == 'ESP8266':
                self.processmem.start(
                    'python ' + self.bundle_dir + '/esptool.py --chip esp8266 read_flash_status --bytes  ' + " " + RDSR)
        else:
            if self.chip == 'ESP32':
                self.processmem.start(
                    'sudo python ' + self.bundle_dir + '/esptool.py --chip esp32 read_flash_status --bytes  ' + " " + RDSR)
            else:
                self.processmem.start(
                    'sudo python ' + self.bundle_dir + '/esptool.py --chip esp8266 read_flash_status --bytes  ' + " " + RDSR)

    def writestatusreg(self):
        WRSR = self.comboBox_writestatusreg.currentText()
        self.port = self.comboBox_serial.currentText()
        if os.name == 'nt':
            if self.chip == 'ESP32':
                self.processmem.start(
                    'python ' + self.bundle_dir + '/esptool.py --chip esp32 write_flash_status  --bytes  ' + " " + WRSR + " " + '--non-volatile 0')
            if self.chip == 'ESP8266':
                self.processmem.start(
                    'python ' + self.bundle_dir + '/esptool.py --chip esp8266 write_flash_status  --bytes  ' + " " + WRSR + " " + '--non-volatile 0')
        else:
            if self.chip == 'ESP32':
                self.processmem.start(
                    'sudo python ' + self.bundle_dir + '/esptool.py --chip esp32 write_flash_status  --bytes  ' + " " + WRSR + " " + '--non-volatile 0')
            else:
                self.processmem.start(
                    'sudo python ' + self.bundle_dir + '/esptool.py --chip esp8266 write_flash_status  --bytes  ' + " " + WRSR + " " + '--non-volatile 0')

    def writememory(self):
        memoryaddr1 = self.lineEdit_writemem1.text()
        memoryaddr2 = self.lineEdit_writemem2.text()
        mask = self.lineEdit_writemem3.text()
        self.port = self.comboBox_serial.currentText()
        if (memoryaddr1 == "") or (memoryaddr1 == " "):
            QMessageBox.warning(self, 'Error', "Missing Argument: " + "Please insert an address First", QMessageBox.Ok,
                                QMessageBox.Ok)
        elif (memoryaddr2 == "") or (memoryaddr2 == " "):
            QMessageBox.warning(self, 'Error', "Missing Argument: " + "Please insert an address First", QMessageBox.Ok,
                                QMessageBox.Ok)
        elif (mask == "") or (mask == " "):
            QMessageBox.warning(self, 'Error', "Missing Argument: " + "Mask Value is Missing ", QMessageBox.Ok,
                                QMessageBox.Ok)
        else:
            if os.name == 'nt':
                if self.chip == 'ESP32':
                    self.processmem.start(
                        'python ' + self.bundle_dir + '/esptool.py --chip esp32 write_mem ' + " " + memoryaddr1 + " " + memoryaddr2 + " " + mask)
                if self.chip == 'ESP8266':
                    self.processmem.start(
                        'python ' + self.bundle_dir + '/esptool.py --chip esp8266 write_mem ' + " " + memoryaddr1 + " " + memoryaddr2 + " " + mask)
            else:
                if self.chip == 'ESP32':
                    self.processmem.start(
                        'sudo python ' + self.bundle_dir + '/esptool.py --chip esp32 write_mem ' + " " + memoryaddr1 + " " + memoryaddr2 + " " + mask)
                else:
                    self.processmem.start(
                        'sudo python ' + self.bundle_dir + '/esptool.py --chip esp8266 write_mem ' + " " + memoryaddr1 + " " + memoryaddr2 + " " + mask)

    def dumpmemory(self):
        dumpline1 = self.lineEdit_dumpmem1.text()
        dumpline2 = self.lineEdit_dumpmem2.text()
        self.port = self.comboBox_serial.currentText()
        if (dumpline1 == "") or (dumpline1 == " "):
            QMessageBox.warning(self, 'Error',
                                "Missing Argument: " + "Please Enter the region from the chip's memory to dump",
                                QMessageBox.Ok, QMessageBox.Ok)
        elif (dumpline2 == "") or (dumpline2 == " "):
            QMessageBox.warning(self, 'Error', "Missing Argument: " + "Please Enter the size", QMessageBox.Ok,
                                QMessageBox.Ok)
        else:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getSaveFileName(self, "Dump Memory", "", "All Files (*);;Bin Files (*.bin)",
                                                      options=options)
            self.thread = MyprogressbarThreaddump()
            self.thread.change_valuedump.connect(self.setProgressValdump)
            self.thread.start()
            if os.name == 'nt':
                if self.chip == 'ESP32':
                    self.processmem.start(
                        'python ' + self.bundle_dir + '/esptool.py --chip esp32 dump_mem ' + dumpline1 + " " + dumpline2 + " " + fileName)
                if self.chip == 'ESP8266':
                    self.processmem.start(
                        'python ' + self.bundle_dir + '/esptool.py --chip esp8266 dump_mem ' + dumpline1 + " " + dumpline2 + " " + fileName)
            else:
                if self.chip == 'ESP32':
                    self.processmem.start(
                        'sudo python ' + self.bundle_dir + '/esptool.py --chip esp32 dump_mem ' + dumpline1 + " " + dumpline2 + " " + fileName)
                else:
                    self.processmem.start(
                        'sudo python ' + self.bundle_dir + '/esptool.py --chip esp8266 dump_mem ' + dumpline1 + " " + dumpline2 + " " + fileName)

    def readFlashfunc(self):
        readflashline1 = self.lineEdit_readFlash1.text()
        readflashline2 = self.lineEdit_readFlash2.text()
        self.port = self.comboBox_serial.currentText()
        if (readflashline1 == "") or (readflashline1 == " "):
            QMessageBox.warning(self, 'Error', "Missing Argument: " + "Address is missing", QMessageBox.Ok,
                                QMessageBox.Ok)
        elif (readflashline2 == "") or (readflashline2 == " "):
            QMessageBox.warning(self, 'Error', "Missing Argument: " + "Please Enter the size", QMessageBox.Ok,
                                QMessageBox.Ok)
        else:
            self.thread = MyprogressbarThreadreadflash()
            self.thread.change_valuereadflash.connect(self.setProgressValdump)
            self.thread.start()
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getSaveFileName(self, "Flash Memory Read", "", "Bin Files (*.bin)",
                                                      options=options)
            if os.name == 'nt':
                if self.chip == 'ESP32':
                    self.processmem.start(
                        'python ' + self.bundle_dir + '/esptool.py  -p ' + " " + self.port + " " + ' -b' + " " + self.comboBox_baud.currentText() + " " + ' read_flash ' + " " + readflashline1 + " " + readflashline2 + " " + fileName)
                if self.chip == 'ESP8266':
                    self.processmem.start(
                        'python ' + self.bundle_dir + '/esptool.py  -p ' + " " + self.port + " " + ' -b' + " " + self.comboBox_baud.currentText() + " " + ' read_flash ' + " " + readflashline1 + " " + readflashline2 + " " + fileName)
            else:
                if self.chip == 'ESP32':
                    self.processmem.start(
                        'sudo python ' + self.bundle_dir + '/esptool.py -p ' + " " + self.port + " " + ' -b' + " " + self.comboBox_baud.currentText() + " " + ' read_flash ' + " " + readflashline1 + " " + readflashline2 + " " + fileName)
                else:
                    self.processmem.start(
                        'sudo python ' + self.bundle_dir + '/esptool.py -p ' + " " + self.port + " " + ' -b' + " " + self.comboBox_baud.currentText() + " " + ' read_flash ' + " " + readflashline1 + " " + readflashline2 + " " + fileName)

    def encryptflash(self):
        self.port = self.comboBox_serial.currentText()
        if (self.lineEdit_keypath.text() == "") or (self.lineEdit_keypath.text() == " "):
            QMessageBox.warning(self, 'Error', "Missing Argument: " + "Flash Encryption Key is Missing", QMessageBox.Ok,
                                QMessageBox.Ok)
        else:
            # head, keyfile = os.path.split(self.lineEdit_keypath.text())
            if not self.lineEdit_keypath.text() == "" and not self.lineEdit_keypath.text() == " ":
                if os.name == 'nt':
                    if self.chip == 'ESP32':
                        self.processmem.start(
                            '  python ' + self.bundle_dir + '/espefuse.py --port {0} burn_key flash_encryption {1}'.format(
                                self.port, self.lineEdit_keypath.text()))
                    if self.chip == 'ESP8266':
                        self.processmem.start(
                            '  python ' + self.bundle_dir + '//espefuse.py --port {0} burn_key flash_encryption {1}'.format(
                                self.port, self.lineEdit_keypath.text()))
                else:
                    if self.chip == 'ESP32':
                        self.processmem.start(
                            'sudo python ' + self.bundle_dir + '/espefuse.py --port {0} burn_key flash_encryption {1}'.format(
                                self.port, self.lineEdit_keypath.text()))
                    else:
                        self.processmem.start(
                            'sudo python ' + self.bundle_dir + '/espefuse.py --port {0} burn_key flash_encryption {1}'.format(
                                self.port, self.lineEdit_keypath.text()))

    # *******************************4th_Tab****************************************************************************

    def onDefault(self):
        self.comboBox_baud.setCurrentIndex(5)
        self.comboBox_flashsize.setCurrentIndex(0)
        self.comboBox_chip.setCurrentIndex(0)
        self.comboBox_flashmode.setCurrentIndex(1)

    def clearData(self):
        self.checkBox_1.setChecked(False)
        self.checkBox_2.setChecked(False)
        self.checkBox_3.setChecked(False)
        self.lineEdit_path1.clear()
        self.lineEdit_path2.clear()
        self.lineEdit_path3.clear()
        self.lineEdit_elffile.clear()
        self.lineEdit_keypath.clear()
        self.lineEdit_offset1.clear()
        self.lineEdit_offset2.clear()
        self.lineEdit_offset3.clear()

    def selectall(self):
        if self.checkBox_1.isEnabled():
            self.checkBox_1.setChecked(True)
        else:
            pass
        if self.checkBox_2.isEnabled():
            self.checkBox_2.setChecked(True)
        else:
            pass
        if self.checkBox_3.isEnabled():
            self.checkBox_3.setChecked(True)
        else:
            pass

    def saveSettingstofilebutton(self):

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "Select path", filter='*.ini', options=options)
        if os.path.exists(fileName):
            os.remove(fileName)
        pre, ext = os.path.splitext(fileName)
        settings = QSettings(pre + ".ini", QSettings.IniFormat)
        settings.setValue('offset1', self.lineEdit_offset1.text())
        settings.setValue('offset2', self.lineEdit_offset2.text())
        settings.setValue('offset3', self.lineEdit_offset3.text())
        settings.setValue('baudrate', self.comboBox_baud.currentIndex())
        settings.setValue('flashsize', self.comboBox_flashsize.currentIndex())
        settings.setValue('flashmode', self.comboBox_flashmode.currentIndex())
        settings.setValue('verifyflash', self.lineEdit_verifyoffset.text())
        settings.setValue('readmem', self.lineEditreadmemaddr.text())
        settings.setValue('writemem1', self.lineEdit_writemem1.text())
        settings.setValue('writemem2', self.lineEdit_writemem2.text())
        settings.setValue('writemem3', self.lineEdit_writemem3.text())
        settings.setValue('eraseregion1', self.lineEdit_eraseregion1.text())
        settings.setValue('eraseregion2', self.lineEdit_eraseregion2.text())
        settings.setValue('readstatus', self.comboBox_readstatusreg.currentIndex())
        settings.setValue('writestatus', self.comboBox_writestatusreg.currentIndex())
        settings.setValue('readflash1', self.lineEdit_readFlash1.text())
        settings.setValue('readflash2', self.lineEdit_readFlash2.text())
        settings.setValue('combined_offset', self.lineEdit_offsetcombined.text())
        settings.setValue('memdump1', self.lineEdit_dumpmem1.text())
        settings.setValue('memdump2', self.lineEdit_dumpmem2.text())

        settings.sync()

    def loadsettingsbutton(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, 'Load Settings File', options=options)
        settingsfile_load = QSettings(fileName, QSettings.IniFormat)
        self.lineEdit_offset1.setText(settingsfile_load.value(offset1))
        self.lineEdit_offset2.setText(settingsfile_load.value(offset2))
        self.lineEdit_offset3.setText(settingsfile_load.value(offset3))
        self.comboBox_baud.setCurrentIndex(settingsfile_load.value(baudrate, type=int))
        self.comboBox_flashsize.setCurrentIndex(settingsfile_load.value(flashsize, type=int))
        self.comboBox_flashmode.setCurrentIndex(settingsfile_load.value(flashmode, type=int))
        self.comboBox_readstatusreg.setCurrentIndex(settingsfile_load.value(readstatus, type=int))
        self.comboBox_writestatusreg.setCurrentIndex(settingsfile_load.value(writestatus, type=int))
        self.lineEdit_verifyoffset.setText(settingsfile_load.value(verifyflash))
        self.lineEditreadmemaddr.setText(settingsfile_load.value(readmem))
        self.lineEdit_writemem1.setText(settingsfile_load.value(writemem1))
        self.lineEdit_writemem2.setText(settingsfile_load.value(writemem2))
        self.lineEdit_writemem3.setText(settingsfile_load.value(writemem3))
        self.lineEdit_eraseregion1.setText(settingsfile_load.value(eraseregion1))
        self.lineEdit_eraseregion2.setText(settingsfile_load.value(eraseregion2))
        self.lineEdit_readFlash1.setText(settingsfile_load.value(readflash1))
        self.lineEdit_readFlash2.setText(settingsfile_load.value(readflash2))
        self.lineEdit_offsetcombined.setText(settingsfile_load.value(combined_offset))
        self.lineEdit_dumpmem1.setText(settingsfile_load.value(memdump1))
        self.lineEdit_dumpmem2.setText(settingsfile_load.value(memdump2))

    def combine_bin(self):
        path1 = self.lineEdit_path1.text()
        path2 = self.lineEdit_path2.text()
        path3 = self.lineEdit_path3.text()
        if self.checkBox_1.isChecked():
            head1, tail1 = os.path.split(path1)
            offset1 = self.lineEdit_offset1.text()
        else:
            tail1 = ""
            offset1 = ""
        if self.checkBox_2.isChecked():
            head2, tail2 = os.path.split(path2)
            offset2 = self.lineEdit_offset2.text()
        else:
            tail2 = ""
            offset2 = ""
        if self.checkBox_3.isChecked():
            head3, tail3 = os.path.split(path3)
            offset3 = self.lineEdit_offset3.text()
        else:
            tail3 = ""
            offset3 = ""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Combine Binary File ", filter='(*.bin)', options=options)
        head5, tail5 = os.path.split(fileName)
        print(head5)
        self.port = self.comboBox_serial.currentText()
        if os.name == 'nt':
            if self.chip == 'ESP32':
                self.process.start(
                    'python ' + self.bundle_dir + '/esptool.py --chip esp32 make_image -f  {0} -a {1}  -f {2} -a {3} -f  {4} -a {5} {6}'.format(
                        path1, offset1, path2, offset2, path3, offset3, fileName))
            if self.chip == 'ESP8266':
                self.process.start(
                    'python ' + self.bundle_dir + '/esptool.py --chip esp8266 make_image -f  {0} -a {1}  -f {2} -a {3} -f  {4} -a {5} {6}'.format(
                        path1, offset1, path2, offset2, path3, offset3, fileName))
        else:
            if self.chip == 'ESP32':
                self.process.start(
                    'sudo python ' + self.bundle_dir + '/esptool.py --chip esp32 make_image -f  {0} -a {1}  -f {2} -a {3} -f  {4} -a {5} {6}'.format(
                        path1, offset1, path2, offset2, path3, offset3, fileName))
            else:
                self.process.start(
                    'sudo python ' + self.bundle_dir + '/esptool.py --chip esp8266 make_image -f  {0} -a {1}  -f {2} -a {3} -f  {4} -a {5} {6}'.format(
                        path1, offset1, path2, offset2, path3, offset3, fileName))

    def saveSettingstofilepackage(self):

        settings = QSettings("privatesettings.ini", QSettings.IniFormat)
        settings.setValue('offset1', self.lineEdit_offset1.text())
        settings.setValue('offset2', self.lineEdit_offset2.text())
        settings.setValue('offset3', self.lineEdit_offset3.text())
        settings.setValue('baudrate', self.comboBox_baud.currentIndex())
        settings.setValue('flashsize', self.comboBox_flashsize.currentIndex())
        settings.setValue('flashmode', self.comboBox_flashmode.currentText())
        # add pc info and date/time to display later on

        now = QDate.currentDate()
        settings.setValue('datenowsetting', now.toString(Qt.DefaultLocaleLongDate))
        time = QTime.currentTime()
        settings.setValue('timenowsetting', time.toString(Qt.DefaultLocaleLongDate))
        """Get all ip addresses from computer
           :rtype: list
           """
        ip_list = []

        for interface in QNetworkInterface().allInterfaces():
            flags = interface.flags()
            is_loopback = bool(flags & QNetworkInterface.IsLoopBack)
            is_p2p = bool(flags & QNetworkInterface.IsPointToPoint)
            is_running = bool(flags & QNetworkInterface.IsRunning)
            is_up = bool(flags & QNetworkInterface.IsUp)

            if not is_running:
                continue
            if not interface.isValid() or is_loopback or is_p2p:
                continue

            for addr in interface.allAddresses():
                if addr == QHostAddress.LocalHost:
                    continue
                if not addr.toIPv4Address():
                    continue
                ip = addr.toString()
                if ip == '':
                    continue

                if ip not in ip_list:
                    ip_list.append(ip)
        settings.setValue('ipaddresssetting', ip_list)
        settings.setValue('machinesettig', str((platform.uname())))
        settings.sync()

    def createpackage(self):
        self.saveSettingstofilepackage()
        path1 = self.lineEdit_path1.text()
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "Select Package path", options=options)
        head, tail = os.path.split(fileName)

        if not (fileName == " " or fileName == ""):
            secret_password = b'hello123456789'
            with pyzipper.AESZipFile(fileName, 'w', compression=pyzipper.ZIP_LZMA) as zf:
                zf.setpassword(secret_password)
                zf.setencryption(pyzipper.WZ_AES, nbits=256)
                if self.checkBox_1.isChecked() and not self.checkBox_2.isChecked() and not self.checkBox_3.isChecked():
                    if os.path.isfile(path1):
                        zf.write(self.lineEdit_path1.text())
                        zf.write("privatesettings.ini")
                    else:
                        QMessageBox.about(self, "No Device is Connected", "Please Connect a Device First")

                elif self.checkBox_2.isChecked() and not self.checkBox_1.isChecked() and not self.checkBox_3.isChecked():
                    zf.write(self.lineEdit_path2.text())
                    zf.write("privatesettings.ini")
                elif self.checkBox_3.isChecked() and not self.checkBox_2.isChecked() and not self.checkBox_1.isChecked():
                    zf.write(self.lineEdit_path3.text())
                    zf.write("privatesettings.ini")
                elif self.checkBox_1.isChecked() and self.checkBox_2.isChecked() and not self.checkBox_3.isChecked():
                    zf.write(self.lineEdit_path1.text())
                    zf.write(self.lineEdit_path2.text())
                    zf.write("privatesettings.ini")
                elif self.checkBox_1.isChecked() and self.checkBox_3.isChecked() and not self.checkBox_2.isChecked():
                    zf.write(self.lineEdit_path1.text())
                    zf.write(self.lineEdit_path3.text())
                    zf.write("privatesettings.ini")
                elif self.checkBox_2.isChecked() and self.checkBox_3.isChecked() and not self.checkBox_1.isChecked():
                    zf.write(self.lineEdit_path2.text())
                    zf.write(self.lineEdit_path3.text())
                    zf.write("privatesettings.ini")
                elif self.checkBox_1.isChecked() and self.checkBox_2.isChecked() and self.checkBox_3.isChecked():
                    zf.write(self.lineEdit_path1.text())
                    zf.write(self.lineEdit_path2.text())
                    zf.write(self.lineEdit_path3.text())
                    zf.write("privatesettings.ini")
                else:
                    pass
        else:
            pass
        base = os.path.splitext(fileName)[0]
        os.rename(fileName, base + '.mtool')

    def selectbinFile(self, name, obj):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, name, filter='(*.bin)', options=options)
        if (not fileName == "") or (not fileName == " "):
            obj.setText(fileName)
        else:
            pass

    def selectkeyFile(self, name, obj):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, name, filter='(*.bin)', options=options)
        if (not fileName == "") or (not fileName == " "):
            obj.setText(fileName)
        else:
            pass

    def selectelfFile(self, name, obj):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, name, filter='(*.elf)', options=options)
        if (not fileName == "") or (not fileName == " "):
            obj.setText(fileName)
        else:
            pass

    def convertELFtoBIN(self):
        elfpath = self.lineEdit_elffile.text()
        if (elfpath == "") or (elfpath == " "):
            QMessageBox.warning(self, 'Error', "Missing Argument: " + "ELF File Path Not Found ", QMessageBox.Ok,
                                QMessageBox.Ok)
        else:
            if os.name == 'nt':
                if self.chip == 'ESP32':
                    self.process.start(
                        'python ' + self.bundle_dir + '/esptool.py --chip esp32 elf2image ' + " " + elfpath)
                if self.chip == 'ESP8266':
                    self.process.start(
                        'python ' + self.bundle_dir + '/esptool.py --chip esp8266 elf2image ' + " " + elfpath)
            else:
                if self.chip == 'ESP32':
                    self.process.start(
                        'sudo python ' + self.bundle_dir + '/esptool.py --chip esp32 elf2image ' + " " + elfpath)
                else:
                    self.process.start(
                        'sudo python ' + self.bundle_dir + '/esptool.py --chip esp8266 elf2image ' + " " + elfpath)

    def generateencryptionkey(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "Generated Key File Path", filter='(*.bin)', options=options)
        if not fileName == " " and not fileName == "":
            self.lineEdit_keypath.setText(fileName)
            if os.name == 'nt':
                if self.chip == 'ESP32':
                    self.processmem.start(
                        '  python ' + self.bundle_dir + '/espsecure.py generate_flash_encryption_key' + " " + fileName)
                if self.chip == 'ESP8266':
                    self.processmem.start(
                        '  python ' + self.bundle_dir + '/espsecure.py generate_flash_encryption_key ' + " " + fileName)
            else:
                if self.chip == 'ESP32':
                    self.processmem.start(
                        'sudo python ' + self.bundle_dir + '/espsecure.py generate_flash_encryption_key ' + " " + fileName)
                else:
                    self.processmem.start(
                        'sudo python ' + self.bundle_dir + '/espsecure.py generate_flash_encryption_key ' + " " + fileName)

    # *******************************5th_Tab****************************************************************************

    def refbuttonfunction(self):

        self.workerThread.start()
        self.btnref.setDisabled(True)
        self.btnexport.setDisabled(True)
        self.status_txt = QtWidgets.QLabel()
        movie = QMovie("icons/GREY-GEAR-LOADING.gif")
        self.status_txt.setMovie(movie)
        self.status_txt.setAlignment(Qt.AlignCenter)
        movie.start()
        self.lay.addWidget(self.status_txt)

        QtTest.QTest.qWait(11000)
        movie.stop()
        self.status_txt.deleteLater()
        #
        self.conn = sqlite3.connect('samples.db')
        cur = self.conn.cursor()
        cur.execute("SELECT Field1 , Field2, Field3,Field4, Field5 from samples")
        rows = cur.fetchall()

        itr1 = 1
        itr2 = 0
        for record in rows:
            itr2 = 0
            for eachrecord in record:
                self.tableWidget.setItem(itr1, itr2, QTableWidgetItem(str(eachrecord)))
                itr2 = itr2 + 1
            itr1 = itr1 + 1
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.btnref.setDisabled(False)
        self.btnexport.setDisabled(False)

    def refreshsummary(self):
        self.workerThread.start()

        self.pushButton_reloadfusetab.deleteLater()
        self.fusetab.setLayout(self.lay)

        self.status_txt = QtWidgets.QLabel()
        movie = QMovie("icons/GREY-GEAR-LOADING.gif")
        self.status_txt.setMovie(movie)
        self.status_txt.setAlignment(Qt.AlignCenter)

        movie.start()
        self.lay.addWidget(self.status_txt)

        QtTest.QTest.qWait(10000)
        movie.stop()
        self.status_txt.deleteLater()

        self.conn = sqlite3.connect('samples.db')
        cur = self.conn.cursor()
        cur.execute("SELECT Field1 , Field2, Field3,Field4, Field5 from samples")
        rows = cur.fetchall()
        self.tableWidget.setRowCount(0)
        self.tableWidget.setRowCount(33)
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderItem(0, QTableWidgetItem("EFUSE NAME"))
        self.tableWidget.setHorizontalHeaderItem(1, QTableWidgetItem("Description "))
        self.tableWidget.setHorizontalHeaderItem(2, QTableWidgetItem("Meaningful Value"))
        self.tableWidget.setHorizontalHeaderItem(3, QTableWidgetItem("Readable/Writeable"))
        self.tableWidget.setHorizontalHeaderItem(4, QTableWidgetItem("Hex Value"))
        self.tableWidget.setHorizontalHeaderItem(5, QTableWidgetItem("Action"))
        self.tableWidget.setGeometry(QtCore.QRect(0, 0, 780, 545))
        self.lay.addWidget(self.tableWidget)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setColumnWidth(0, 200)
        self.tableWidget.setColumnWidth(1, 250)
        self.tableWidget.setColumnWidth(2, 130)
        self.tableWidget.setColumnWidth(3, 110)
        self.tableWidget.setColumnWidth(4, 70)
        self.tableWidget.setColumnWidth(5, 36)

        self.setuptablebuttons()

        itr1 = 1
        itr2 = 0
        for record in rows:
            itr2 = 0
            for eachrecord in record:
                self.tableWidget.setItem(itr1, itr2, QTableWidgetItem(str(eachrecord)))
                itr2 = itr2 + 1
            itr1 = itr1 + 1
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    def exportfuse(self):

        choice = QtWidgets.QMessageBox.question(self, ' Export efuse ',
                                                "Would you like to save a copy of efuse table ?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            path, _ = QFileDialog.getSaveFileName(self, "Select path", filter='*.xls', options=options)
            if not path == '':
                wbk = xlwt.Workbook()
                self.sheet = wbk.add_sheet("sheet", cell_overwrite_ok=True)
                row = 0
                col = 0
                for i in range(self.tableWidget.columnCount()):
                    for x in range(self.tableWidget.rowCount()):
                        try:
                            teext = str(self.tableWidget.item(row, col).text())
                            self.sheet.write(row, col, teext)
                            row += 1
                        except AttributeError:
                            row += 1
                    row = 0
                    col += 1
                pre, ext = os.path.splitext(path)
                wbk.save(pre + ".xls")

        else:
            pass

    def setuptablebuttons(self):
        self.tableWidget.setCellWidget(0, 0, self.btnexport)
        self.btnexport.setIcon(QIcon('icons/Excel.png'))
        self.btnexport.setStyleSheet("border: none;border-radius: 0px;")
        self.btnexport.setIconSize(QSize(20, 20))
        self.btnexport.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(0, 5, self.btnref)
        self.btnref.setIcon(QIcon('icons/refresh.png'))
        self.btnref.setStyleSheet("border: none;border-radius: 0px;")
        self.btnref.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(1, 5, self.btn1)
        self.btn1.setIcon(QIcon('icons/executefuse1.png'))
        self.btn1.setStyleSheet("border: none;border-radius: 0px;")
        self.btn1.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(2, 5, self.btn2)
        self.btn2.setIcon(QIcon('icons/executefuse1.png'))
        self.btn2.setStyleSheet("border: none;border-radius: 0px;")
        self.btn2.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(3, 5, self.btn3)
        self.btn3.setIcon(QIcon('icons/executefuse1.png'))
        self.btn3.setStyleSheet("border: none;border-radius: 0px;")
        self.btn3.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(4, 5, self.btn4)
        self.btn4.setIcon(QIcon('icons/executefuse1.png'))
        self.btn4.setStyleSheet("border: none;border-radius: 0px;")
        self.btn4.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(5, 5, self.btn5)
        self.btn5.setIcon(QIcon('icons/executefuse1.png'))
        self.btn5.setStyleSheet("border: none;border-radius: 0px;")
        self.btn5.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(6, 5, self.btn6)
        self.btn6.setIcon(QIcon('icons/executefuse1.png'))
        self.btn6.setStyleSheet("border: none;border-radius: 0px;")
        self.btn6.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(7, 5, self.btn7)
        self.btn7.setIcon(QIcon('icons/executefuse1.png'))
        self.btn7.setStyleSheet("border: none;border-radius: 0px;")
        self.btn7.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(8, 5, self.btn8)
        self.btn8.setIcon(QIcon('icons/executefuse1.png'))
        self.btn8.setStyleSheet("border: none;border-radius: 0px;")
        self.btn8.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(9, 5, self.btn9)
        self.btn9.setIcon(QIcon('icons/executefuse1.png'))
        self.btn9.setStyleSheet("border: none;border-radius: 0px;")
        self.btn9.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(10, 5, self.btn10)
        self.btn10.setIcon(QIcon('icons/executefuse1.png'))
        self.btn10.setStyleSheet("border: none;border-radius: 0px;")
        self.btn10.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(11, 5, self.btn11)
        self.btn11.setIcon(QIcon('icons/executefuse1.png'))
        self.btn11.setStyleSheet("border: none;border-radius: 0px;")
        self.btn11.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(12, 5, self.btn12)
        self.btn12.setIcon(QIcon('icons/executefuse1.png'))
        self.btn12.setStyleSheet("border: none;border-radius: 0px;")
        self.btn12.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(13, 5, self.btn13)
        self.btn13.setIcon(QIcon('icons/executefuse1.png'))
        self.btn13.setStyleSheet("border: none;border-radius: 0px;")
        self.btn13.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(14, 5, self.btn14)
        self.btn14.setIcon(QIcon('icons/executefuse1.png'))
        self.btn14.setStyleSheet("border: none;border-radius: 0px;")
        self.btn14.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(15, 5, self.btn15)
        self.btn15.setIcon(QIcon('icons/executefuse1.png'))
        self.btn15.setStyleSheet("border: none;border-radius: 0px;")
        self.btn15.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(16, 5, self.btn16)
        self.btn16.setIcon(QIcon('icons/executefuse1.png'))
        self.btn16.setStyleSheet("border: none;border-radius: 0px;")
        self.btn16.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(17, 5, self.btn17)
        self.btn17.setIcon(QIcon('icons/executefuse1.png'))
        self.btn17.setStyleSheet("border: none;border-radius: 0px;")
        self.btn17.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(18, 5, self.btn18)
        self.btn18.setIcon(QIcon('icons/executefuse1.png'))
        self.btn18.setStyleSheet("border: none;border-radius: 0px;")
        self.btn18.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(19, 5, self.btn19)
        self.btn19.setIcon(QIcon('icons/executefuse1.png'))
        self.btn19.setStyleSheet("border: none;border-radius: 0px;")
        self.btn19.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(20, 5, self.btn20)
        self.btn20.setIcon(QIcon('icons/executefuse1.png'))
        self.btn20.setStyleSheet("border: none;border-radius: 0px;")
        self.btn20.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(21, 5, self.btn21)
        self.btn21.setIcon(QIcon('icons/executefuse1.png'))
        self.btn21.setStyleSheet("border: none;border-radius: 0px;")
        self.btn21.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(22, 5, self.btn22)
        self.btn22.setIcon(QIcon('icons/executefuse1.png'))
        self.btn22.setStyleSheet("border: none;border-radius: 0px;")
        self.btn22.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(23, 5, self.btn23)
        self.btn23.setIcon(QIcon('icons/executefuse1.png'))
        self.btn23.setStyleSheet("border: none;border-radius: 0px;")
        self.btn23.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(24, 5, self.btn24)
        self.btn24.setIcon(QIcon('icons/executefuse1.png'))
        self.btn24.setStyleSheet("border: none;border-radius: 0px;")
        self.btn24.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(25, 5, self.btn25)
        self.btn25.setIcon(QIcon('icons/executefuse1.png'))
        self.btn25.setStyleSheet("border: none;border-radius: 0px;")
        self.btn25.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(26, 5, self.btn26)
        self.btn26.setIcon(QIcon('icons/executefuse1.png'))
        self.btn26.setStyleSheet("border: none;border-radius: 0px;")
        self.btn26.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(27, 5, self.btn27)
        self.btn27.setIcon(QIcon('icons/executefuse1.png'))
        self.btn27.setStyleSheet("border: none;border-radius: 0px;")
        self.btn27.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(28, 5, self.btn28)
        self.btn28.setIcon(QIcon('icons/executefuse1.png'))
        self.btn28.setStyleSheet("border: none;border-radius: 0px;")
        self.btn28.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(29, 5, self.btn29)
        self.btn29.setIcon(QIcon('icons/executefuse1.png'))
        self.btn29.setStyleSheet("border: none;border-radius: 0px;")
        self.btn29.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(30, 5, self.btn30)
        self.btn30.setIcon(QIcon('icons/executefuse1.png'))
        self.btn30.setStyleSheet("border: none;border-radius: 0px;")
        self.btn30.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(31, 5, self.btn31)
        self.btn31.setIcon(QIcon('icons/executefuse1.png'))
        self.btn31.setStyleSheet("border: none;border-radius: 0px;")
        self.btn31.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

        self.tableWidget.setCellWidget(32, 5, self.btn32)
        self.btn32.setIcon(QIcon('icons/executefuse1.png'))
        self.btn32.setStyleSheet("border: none;border-radius: 0px;")
        self.btn32.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

    def burnfirst(self):
        self.item = self.tableWidget.item(1, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burnsecond(self):

        self.item = self.tableWidget.item(2, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burnthird(self):

        self.item = self.tableWidget.item(3, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burnfourth(self):

        self.item = self.tableWidget.item(4, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burnfifth(self):

        self.item = self.tableWidget.item(5, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burnsixth(self):

        self.item = self.tableWidget.item(6, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burnseventh(self):

        self.item = self.tableWidget.item(7, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burneighth(self):

        self.item = self.tableWidget.item(8, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burnnineth(self):

        self.item = self.tableWidget.item(9, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burn10(self):

        self.item = self.tableWidget.item(10, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burn11(self):

        self.item = self.tableWidget.item(11, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burn12(self):

        self.item = self.tableWidget.item(12, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burn13(self):

        self.item = self.tableWidget.item(13, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burn14(self):

        self.item = self.tableWidget.item(14, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burn15(self):

        self.item = self.tableWidget.item(15, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burn16(self):

        self.item = self.tableWidget.item(16, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burn17(self):

        self.item = self.tableWidget.item(17, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burn18(self):

        self.item = self.tableWidget.item(18, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burn19(self):

        self.item = self.tableWidget.item(19, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burn20(self):

        self.item = self.tableWidget.item(20, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burn21(self):

        self.item = self.tableWidget.item(21, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burn22(self):

        self.item = self.tableWidget.item(22, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burn23(self):

        self.item = self.tableWidget.item(23, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burn24(self):

        self.item = self.tableWidget.item(24, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burn25(self):

        self.item = self.tableWidget.item(25, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burn26(self):

        self.item = self.tableWidget.item(26, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burn27(self):

        self.item = self.tableWidget.item(27, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burn28(self):

        self.item = self.tableWidget.item(28, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burn29(self):

        self.item = self.tableWidget.item(29, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burn30(self):

        self.item = self.tableWidget.item(30, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burn31(self):

        self.item = self.tableWidget.item(31, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    def burn32(self):

        self.item = self.tableWidget.item(32, 0)

        settings_burn = QSettings("settingsprogresswrite.ini", QSettings.IniFormat)
        new_value, okPressed = QInputDialog.getText(self, "Enter a New Value ", self.item.text() + " value :",
                                                    QLineEdit.Normal, "")
        if okPressed and new_value != '':
            choice = QtWidgets.QMessageBox.question(self, ' Confirm Efuse Burn ',
                                                    "Are You Sure You want To Burn " + self.item.text() + " ?",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if choice == QtWidgets.QMessageBox.Yes:
                settings_burn.setValue('confirm_burn', "BURN")
                if not self.item.text() == "" or not self.item.text() == " ":
                    self.port = self.comboBox_serial.currentText()
                    if os.name == 'nt':
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + '/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    # *******************************6th_Tab****************************************************************************

    def chipSelect(self):
        self.chip = self.comboBox_chip.currentText()
        if self.chip == 'ESP8266':
            self.comboBox_flashsize.clear()
            self.comboBox_flashsize.addItems(self.memoryESP8266)
            self.lineEdit_path1.setPlaceholderText("Firmware File")
            self.lineEdit_path2.setPlaceholderText("Firmware File")
            self.lineEdit_path3.setPlaceholderText("Firmware File")
            self.pushButton_13.setDisabled(True)
            self.pushButton_genkey.setDisabled(True)
            self.pushButton_Fusedump.setDisabled(True)
            self.pushButton_encrypt.setDisabled(True)
            self.lineEdit_keypath.setDisabled(True)
            self.pushButton_pathkey.setDisabled(True)
            self.fusetab.setDisabled(True)
        else:
            self.comboBox_flashsize.clear()
            self.comboBox_flashsize.addItems(self.memoryESP32)
            self.lineEdit_path1.setPlaceholderText("Firmware File")
            self.lineEdit_path2.setPlaceholderText("Bootloader File")
            self.lineEdit_path3.setPlaceholderText("Partition File")
            self.pushButton_13.setDisabled(False)
            self.pushButton_genkey.setDisabled(False)
            self.pushButton_Fusedump.setDisabled(False)
            self.pushButton_encrypt.setDisabled(False)
            self.lineEdit_keypath.setDisabled(False)
            self.pushButton_pathkey.setDisabled(False)

    def flashSizeSelect(self):
        self.flasSize = self.comboBox_flashsize.currentText()

    def memorySelect(self):
        self.flasSize = self.comboBox_flashsize.currentText()


class PlainTextEdit(QPlainTextEdit):
    commandSignal = pyqtSignal(str)
    commandZPressed = pyqtSignal(str)

    def __init__(self, parent=None, movable=False):
        super(PlainTextEdit, self).__init__()

        self.installEventFilter(self)
        self.setAcceptDrops(True)
        QApplication.setCursorFlashTime(1000)
        self.process = QProcess()
        self.process.readyReadStandardError.connect(self.onReadyReadStandardError)
        self.process.readyReadStandardOutput.connect(self.onReadyReadStandardOutput)

        self.name = (str(getpass.getuser()) + "@" + str(socket.gethostname())
                     + ":" + str(os.getcwd()) + "$ ")
        self.appendPlainText(self.name)
        self.commands = []  # This is a list to track what commands the user has used so we could display them when
        # up arrow key is pressed
        self.tracker = 0
        self.setStyleSheet("QPlainTextEdit{background-color: #212121; color: #f3f3f3; padding: 8;}")
        self.verticalScrollBar().setStyleSheet("background-color: #212121;")
        self.text = None
        self.setFont(QFont("Noto Sans Mono", 8))
        self.previousCommandLength = 0

    def eventFilter(self, source, event):
        if event.type() == QEvent.DragEnter:
            event.accept()
            print('DragEnter')
            return True
        elif event.type() == QEvent.Drop:
            print('Drop')
            self.setDropEvent(event)
            return True
        else:
            return False  ### super(QPlainTextEdit).eventFilter(event)

    def setDropEvent(self, event):
        if event.mimeData().hasUrls():
            f = str(event.mimeData().urls()[0].toLocalFile())
            self.insertPlainText(f)
            event.accept()
        elif event.mimeData().hasText():
            ft = event.mimeData().text()
            print("text:", ft)
            self.insertPlainText(ft)
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, e):
        cursor = self.textCursor()

        if e.modifiers() == Qt.ControlModifier and e.key() == Qt.Key_A:
            return

        if e.modifiers() == Qt.ControlModifier and e.key() == Qt.Key_Z:
            self.commandZPressed.emit("True")
            return

        if e.modifiers() == Qt.ControlModifier and e.key() == Qt.Key_C:
            self.process.kill()
            self.name = (str(getpass.getuser()) + "@" + str(socket.gethostname())
                         + ":" + str(os.getcwd()) + "$ ")
            self.appendPlainText("process cancelled")
            self.appendPlainText(self.name)
            self.textCursor().movePosition(QTextCursor.End)
            return

        if e.key() == Qt.Key_Return:  ### 16777220:  # This is the ENTER key
            text = self.textCursor().block().text()

            if text == self.name + text.replace(self.name, "") and text.replace(self.name,
                                                                                "") != "":  # This is to prevent adding in commands that were not meant to be added in
                self.commands.append(text.replace(self.name, ""))
            #                print(self.commands)
            self.handle(text)
            self.commandSignal.emit(text)
            self.appendPlainText(self.name)

            return

        if e.key() == Qt.Key_Up:
            try:
                if self.tracker != 0:
                    cursor.select(QTextCursor.BlockUnderCursor)
                    cursor.removeSelectedText()
                    self.appendPlainText(self.name)

                self.insertPlainText(self.commands[self.tracker])
                self.tracker -= 1

            except IndexError:
                self.tracker = 0

            return

        if e.key() == Qt.Key_Down:
            try:
                cursor.select(QTextCursor.BlockUnderCursor)
                cursor.removeSelectedText()
                self.appendPlainText(self.name)

                self.insertPlainText(self.commands[self.tracker])
                self.tracker += 1

            except IndexError:
                self.tracker = 0

        if e.key() == Qt.Key_Backspace:  ### 16777219:
            if cursor.positionInBlock() <= len(self.name):
                return

            else:
                cursor.deleteChar()

        super().keyPressEvent(e)
        cursor = self.textCursor()
        e.accept()

    def ispressed(self):
        return self.pressed

    def onReadyReadStandardError(self):
        self.error = self.process.readAllStandardError().data().decode()
        self.appendPlainText(self.error.strip('\n'))

    def onReadyReadStandardOutput(self):
        self.result = self.process.readAllStandardOutput().data().decode()
        self.appendPlainText(self.result.strip('\n'))
        self.state = self.process.state()

    #        print(self.result)

    def run(self, command):
        """Executes a system command."""
        if self.process.state() != 2:
            self.process.start(command)
            self.process.waitForFinished()
            self.textCursor().movePosition(QTextCursor.End)

    def handle(self, command):
        #        print("begin handle")
        """Split a command into list so command echo hi would appear as ['echo', 'hi']"""
        real_command = command.replace(self.name, "")

        if command == "True":
            if self.process.state() == 2:
                self.process.kill()
                self.appendPlainText("Program execution killed, press enter")

        if real_command.startswith("python"):
            pass

        if real_command != "":
            command_list = real_command.split()
        else:
            command_list = None
        """Now we start implementing some commands"""
        if real_command == "clear":
            self.clear()

        elif command_list is not None and command_list[0] == "echo":
            self.appendPlainText(" ".join(command_list[1:]))

        elif real_command == "exit":
            quit()

        elif command_list is not None and command_list[0] == "cd" and len(command_list) > 1:
            try:
                os.chdir(" ".join(command_list[1:]))
                self.name = (str(getpass.getuser()) + "@" + str(socket.gethostname())
                             + ":" + str(os.getcwd()) + "$ ")
                self.textCursor().movePosition(QTextCursor.End)

            except FileNotFoundError as E:
                self.appendPlainText(str(E))

        elif command_list is not None and len(command_list) == 1 and command_list[0] == "cd":
            os.chdir(str(Path.home()))
            self.name = (str(getpass.getuser()) + "@" + str(socket.gethostname())
                         + ":" + str(os.getcwd()) + "$ ")
            self.textCursor().movePosition(QTextCursor.End)

        elif self.process.state() == 2:
            self.process.write(real_command.encode())
            self.process.closeWriteChannel()

        elif command == self.name + real_command:
            self.run(real_command)
        else:
            pass
