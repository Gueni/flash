
#?---------------------------------------------------------------------------------------------------------------------------
import os
import os.path
import platform
import sqlite3
import sys
import pyzipper
import serial.tools.list_ports
import xlwt
from PyQt5 import QtCore, QtGui, QtWidgets, QtTest
from PyQt5.QtCore import QSize, QRegExp, QCoreApplication 
from PyQt5.QtCore import  QSettings, QThread, pyqtSignal, Qt
from PyQt5.QtCore import  QDate, QTime
from PyQt5.QtGui import QPixmap, QRegExpValidator, QKeySequence, QIcon, QMovie
from PyQt5.QtNetwork import QHostAddress, QNetworkInterface
from PyQt5.QtWidgets import QFileDialog, QGraphicsScene, QShortcut
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QTableWidget,QVBoxLayout
from PyQt5.QtWidgets import QInputDialog, QLineEdit
import aboutmain
import advancedgui
import time
from PyQt5.QtCore import Qt, QSize, QSettings, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QFileDialog, QSplashScreen, QProgressBar, QInputDialog, QLineEdit
from PyQt5.QtCore import QPoint
#?---------------------------------------------------------------------------------------------------------------------------
machinesettig                   = 'machinesettig'
ipaddresssetting                = 'ipaddresssetting'
timenowsetting                  = 'timenowsetting'
datenowsetting                  = 'datenowsetting'
ORGANIZATION_NAME               = 'flash Softwares'
ORGANIZATION_DOMAIN             = 'https://github.com/Gueni/flash'
APPLICATION_NAME                = 'Flash'
SETTINGS_TRAYbaud               = 'SETTINGS_TRAYbaud'
SETTINGS_TRAYchip               = 'SETTINGS_TRAYchip'
SETTINGS_TRAYflashsize          = 'SETTINGS_TRAYflashsize'
SETTINGS_TRAYflashmode          = 'SETTINGS_TRAYflashmode'
SETTINGS_TRAYreadstatus         = 'SETTINGS_TRAYreadstatus'
SETTINGS_TRAYwritestatus        = 'SETTINGS_TRAYwritestatus'
SETTINGS_plainadv               = 'SETTINGS_plainadv'
SETTING_verifyFlash             = 'SETTING_verifyFlash'
SETTING_readmemory              = 'SETTING_readmemory'
SETTING_writemem1               = 'SETTING_writemem1'
SETTING_writemem2               = 'SETTING_writemem2'
SETTING_writemem3               = 'SETTING_writemem3'
SETTING_eraseregion1            = 'SETTING_eraseregion1'
SETTING_eraseregion2            = 'SETTING_eraseregion2'
SETTING_dumpmem1                = 'SETTING_dumpmem1'
SETTING_dumpmem2                = 'SETTING_dumpmem2'
SETTING_readflash1              = 'SETTING_readflash1'
SETTING_readflash2              = 'SETTING_readflash2'
SETTING_plainmem                = 'SETTING_plainmem'
SETTING_offset1                 = 'SETTING_offset1'
SETTING_offset2                 = 'SETTING_offset2'
SETTING_offset3                 = 'SETTING_offset3'
SETTING_offsetcombined          = 'SETTING_offsetcombined'
SETTING_path1                   = 'SETTING_path1'
SETTING_path2                   = 'SETTING_path2'
SETTING_path3                   = 'SETTING_path3'
SETTING_path4                   = 'SETTING_path4'
SETTING_path5                   = 'SETTING_path5'
SETTING_path6                   = 'SETTING_path6'
SETTINGS_check1                 = 'SETTINGS_check1'
SETTINGS_check2                 = 'SETTINGS_check2'
SETTINGS_check3                 = 'SETTINGS_check3'
SETTINGS_style                  = 'Theme/stylesheet.qss'
offset1                         = 'offset1'
offset2                         = 'offset2'
offset3                         = 'offset3'
baudrate                        = 'baudrate'
flashsize                       = 'flashsize'
flashmode                       = 'flashmode'
verifyflash                     = 'verifyflash'
readmem                         = 'readmem'
writemem1                       = 'writemem1'
writemem2                       = 'writemem2'
writemem3                       = 'writemem3'
eraseregion1                    = 'eraseregion1'
eraseregion2                    = 'eraseregion2'
readstatus                      = 'readstatus'
writestatus                     = 'writestatus'
readflash1                      = 'readflash1'
readflash2                      = 'readflash2'
combined_offset                 = 'combined_offset'
memdump1                        = 'memdump1'
memdump2                        = 'memdump2'
progressnum                     = 'progressnum'
verifconst                      = 'veriftest'
dump_progress                   = 'dump_progress'
read_flash_progress             = 'read_flash_progress'
comport                         = 'comport'
QSS_style                       = "Theme/stylesheet.qss"
settingsprogresswrite           = "Dependecies/Dependecies/settingsprogresswrite.ini"
settingsstyle                   = "Dependecies/settingsstyle.ini"
expand_png                      = 'Theme/icons/expand.png'
collapse_png                    = 'Theme/icons/collapse.png'
espLogo_png                     = 'Theme/icons/espLogo.png'
splash_screen_png               = 'Theme/icons/logo-color.png'
#?---------------------------------------------------------------------------------------------------------------------------

class MyprogressbarThread(QThread):
    
    change_value = pyqtSignal(int)

    def run(self):

        cnt                         = 0
        while cnt < 100:
            settingsprogresswrite   = QSettings("Dependecies/settingsprogresswrite.ini", QSettings.IniFormat)
            cnt                     = settingsprogresswrite.value(progressnum, type=int)
            self.change_value.emit(cnt)
            QtTest.QTest.qWait(500)
        if cnt == 100:
            print("done")
            self.change_value.emit(0)

class MyprogressbarThreadreadflash(QThread):
    
    change_valuereadflash = pyqtSignal(int)

    def run(self):

        cnt                         = 0
        while cnt < 100:
            settingsread_flash      = QSettings("Dependecies/settingsprogresswrite.ini", QSettings.IniFormat)
            cnt                     = settingsread_flash.value(read_flash_progress, type=int)
            self.change_valuereadflash.emit(cnt)
            QtTest.QTest.qWait(500)

class MyprogressbarThreaddump(QThread):
    
    change_valuedump = pyqtSignal(int)

    def run(self):

        cnt                         = 0
        while cnt < 100:
            settingsprogresdump     = QSettings("Dependecies/settingsprogresswrite.ini", QSettings.IniFormat)
            cnt                     = settingsprogresdump.value(dump_progress, type=int)
            self.change_valuedump.emit(cnt)
            QtTest.QTest.qWait(500)
        if cnt == 100:
            print("done")
            self.change_valuedump.emit(0)

class MyprogressbarThreadflashall(QThread):
    
    change_valueall                 = pyqtSignal(int)

    def run(self):
        cnt                         = 0
        while cnt <= 100:
            settingsprogresswrite   = QSettings("Dependecies/settingsprogresswrite.ini", QSettings.IniFormat)
            cnt                     = settingsprogresswrite.value(progressnum, type=int)
            self.change_valueall.emit(cnt)
            QtTest.QTest.qWait(500)

class WorkerThread(QThread):

    def __init__(self, parent=None):

        super(WorkerThread, self).__init__(parent)
        self.bundle_dir     = os.path.dirname(os.path.abspath(__file__))
        self.settingsport   = QSettings("Dependecies/settingsprogresswrite.ini", QSettings.IniFormat)

    def run(self):

        Com_port            = self.settingsport.value(comport, type=str)
        os.system('python ' + self.bundle_dir + 'Dependecies/espefuse.py --port ' + " " + Com_port + " " + ' summary')

class AdvancedModeApp(QtWidgets.QMainWindow, advancedgui.Ui_MainWindowadvanced):

    updatePb = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):

        super(AdvancedModeApp, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.old_pos = None  # To store the last mouse position
        if getattr(sys, 'frozen', False):
            self.frozen         = 'ever so'
            self.bundle_dir     = sys._MEIPASS
        else:
            self.bundle_dir     = os.path.dirname(os.path.abspath(__file__))
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(self.bundle_dir + 'Theme/icons/espLogo.png'))

        self.lay                = QVBoxLayout()

        self.settingstyle       = QSettings("Dependencies/settingsstyle.ini", QSettings.IniFormat)
        self.setStyleSheet(open('Theme/stylesheet.qss', "r").read())
        self.workerThread       = WorkerThread()
        self.memoryESP8266      = ['detect', '512KB', '256KB', '1MB', '2MB', '4MB', '2MB-c1', '4MB-c1', '4MB-c2']
        self.memoryESP32        = ['detect', '1MB', '2MB', '4MB', '8MB', '16MB']
        self.ser                = serial.Serial()
        self.timer              = QtCore.QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(50)
        self.initButtons()
        QCoreApplication.setApplicationName(ORGANIZATION_NAME)
        QCoreApplication.setOrganizationDomain(ORGANIZATION_DOMAIN)
        QCoreApplication.setApplicationName(APPLICATION_NAME)
        self.initProcess()
        self.initProcessmem()
        self.baudRate           = 115200
        self.setAcceptDrops(True)
        self.port               = ''
        self.flasSize           = self.comboBox_flashsize.currentText()
        self.frozen             = 'not'
        self.chip               = 'ESP32'
        self.statusbar.showMessage('Version 2.0')
        validator               = QRegExpValidator(QRegExp("0x[0-9A-Fa-f][0-9A-Fa-f]{1,8}"))
        validator2              = QRegExpValidator(QRegExp("[0-9]{1,8}"))
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
        iconConnection          = QtGui.QIcon(u'Theme/icons/connection.png')
        icondata                = QtGui.QIcon(u'Theme/icons/settings.ico')
        iconoperation           = QtGui.QIcon(u'Theme/icons/chip.png')
        iconsetting             = QtGui.QIcon(u'Theme/icons/setting.png')
        iconmemo                = QtGui.QIcon(u'Theme/icons/debug.png')
        iconfuse                = QtGui.QIcon(u'Theme/icons/fuse.png')
        icon_terminal           = QtGui.QIcon(u'Theme/icons/terminal.png')
        iconhelp                = QtGui.QIcon(u'Theme/icons/Info-icon.png')
        self.tabWidget.setTabIcon(0, iconConnection)
        self.tabWidget.setTabIcon(1, iconoperation)
        self.tabWidget.setTabIcon(2, iconmemo)
        self.tabWidget.setTabIcon(3, icondata)
        self.tabWidget.setTabIcon(4, iconfuse)
        self.tabWidget.setTabIcon(5, iconsetting)
        self.tabWidget.setTabIcon(6, icon_terminal)
        self.tabWidget.setTabIcon(7, iconhelp)
        self.tabWidget.setIconSize(QSize(57, 57))
        scene                   = QGraphicsScene()
        pixmap                  = QPixmap('Theme/icons/disconnected.png')
        pixmapbig               = pixmap.scaled(100, 100, QtCore.Qt.KeepAspectRatio)
        scene.addPixmap(pixmapbig)
        self.graphicsView.setScene(scene)
        self.label_8.setText("Serial Port Closed !")
        self.label_8.setStyleSheet(" border-radius: 5px;  color: #039BE5;font-weight: bold;")
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
        self.tableWidget        = QTableWidget()
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)

    def initui(self):

        self.plainTextEditadvancedmem.setGeometry(QtCore.QRect(510, 10+50, 0, 0))
        self.groupBoxmemo.setGeometry(QtCore.QRect(100, 10+70, 720, 350))
        self.groupBox_2memo.setGeometry(QtCore.QRect(100, 370+70, 720, 100))
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
        self.pushButtoncollapsexpandm.setIcon(QIcon('Theme/icons/expandv.png'))
        self.pushButtoncollapsexpandm.setIconSize(QSize(24, 15))
       
        self.plainTextEditadvanced.setGeometry(QtCore.QRect(510, 10+50, 0, 0))
        self.groupBox.setGeometry(QtCore.QRect(100, 10+80, 720, 100))
        self.groupBox_2.setGeometry(QtCore.QRect(100, 140+80, 720, 161))
        self.groupBox_3.setGeometry(QtCore.QRect(100, 330+80, 720, 121))
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
        self.pushButtoncollapsexpand.setIcon(QIcon('Theme/icons/expandv.png'))
        self.pushButtoncollapsexpand.setIconSize(QSize(24, 15))
        self.pushButton_encrypt.setGeometry(QtCore.QRect(370, 265, 320, 25))
        self.pushButton_loadsetting.clicked.connect(self.loadsettingsbutton)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

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

    def disableButtons(self):
       
        for name in advancedgui.widget_names:
            getattr(self, name).setDisabled(True)

    def enableButtons(self):
     
        for name in advancedgui.widget_names:
            getattr(self, name).setDisabled(False)

    def close_application(self):

        choice = QtWidgets.QMessageBox.question(self, ' Confirm Exit ', "Are You Sure You want To Exit Flash ?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            self.close_serial()
            self.savesettings()

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
        self.baudRate       = int(self.comboBox_baud.currentText())
        self.comboBox_readstatusreg.addItems(['1', '2', '3'])
        self.comboBox_writestatusreg.addItems(['1', '2', '3'])
        self.comboBox_flashmode.addItems(["qio", "dio", "dout"])
        self.comboBox_flashmode.currentIndexChanged.connect(self.baudSelect)
        self.flashmode      = self.comboBox_flashmode.currentText()
        self.comboBox_chip.addItems(['ESP32', 'ESP8266'])
        self.comboBox_chip.currentIndexChanged.connect(self.chipSelect)
        comPort             = []
        try:
            for x in serial.tools.list_ports.comports():
                comPort.append(str(x.device))
        except IndexError:
            pass
        self.comboBox_serial.addItems(comPort)
        self.comboBox_serial.popupAboutToBeShown.connect(self.comPortClick)
        self.comboBox_serial.currentIndexChanged.connect(self.comPortSelect)
        self.port           = self.comboBox_serial.currentText()
        self.comboBox_flashsize.addItems(self.memoryESP32)
        self.comboBox_flashsize.currentIndexChanged.connect(self.memorySelect)
        self.flasSize       = self.comboBox_flashsize.currentText()
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
        self.connectshortcut    = QShortcut(QKeySequence("CTRL+C"), self)
        self.connectshortcut.activated.connect(self.open_serial)
        self.pushButtonconnect.setStatusTip('Open Serial Connection CTRL+C')
        self.disconnectshortcut = QShortcut(QKeySequence("CTRL+D"), self)
        self.disconnectshortcut.activated.connect(self.close_serial)
        self.pushButton_disconnect.setStatusTip('Close Serial Connection CTRL+D')
        self.flashBootShortcut  = QShortcut(QKeySequence("CTRL+B"), self)
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
        self.pushButtoncollapsexpand.clicked.connect(self.expandcollapseopt)
        self.pushButtoncollapsexpandm.clicked.connect(self.expandcollapsemem)
        self.pushButton_reloadfusetab.clicked.connect(self.refreshsummary)
        self.pushButton_genkey.clicked.connect(self.generateencryptionkey)
        self.pushButton_encrypt.clicked.connect(self.encryptflash)
        for i in range(32):
            getattr(self, f'btn{i+1}').clicked.connect(self.burn)
        self.pushButton_savesetting.clicked.connect(self.saveSettingstofilebutton)
        self.btnexport.clicked.connect(self.exportfuse)
        self.btnref.clicked.connect(self.refbuttonfunction)

    def expandcollapseopt(self):

        testwidth = self.plainTextEditadvanced.width()
        testheight = self.plainTextEditadvanced.height()
        if testheight == 500 and testwidth == 400:
            self.plainTextEditadvanced.setGeometry(QtCore.QRect(510, 10+50, 0, 0))
            self.groupBox.setGeometry(QtCore.QRect(100, 10+80, 720, 100))
            self.groupBox_2.setGeometry(QtCore.QRect(100, 140+80, 720, 161))
            self.groupBox_3.setGeometry(QtCore.QRect(100, 330+80, 720, 121))
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
            self.pushButtoncollapsexpand.setIcon(QIcon('Theme/icons/expandv.png'))
            self.pushButtoncollapsexpand.setIconSize(QSize(24, 15))
            self.pushButton_encrypt.setGeometry(QtCore.QRect(370, 265, 320, 25))
        if testheight == 0 and testwidth == 0:
            self.plainTextEditadvanced.setGeometry(QtCore.QRect(510, 10+50, 400, 500))
            self.groupBox.setGeometry(QtCore.QRect(30+50, 10+80, 381, 100))
            self.groupBox_2.setGeometry(QtCore.QRect(30+50, 140+80, 381, 161))
            self.groupBox_3.setGeometry(QtCore.QRect(30+50, 330+80, 381, 121))
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
            self.pushButtoncollapsexpand.setIcon(QIcon('Theme/icons/collapsev.png'))
            self.pushButtoncollapsexpand.setIconSize(QSize(24, 15))

    def expandcollapsemem(self):

        testwidth = self.plainTextEditadvancedmem.width()
        testheight = self.plainTextEditadvancedmem.height()
        if testheight == 500 and testwidth == 400:
            self.plainTextEditadvancedmem.setGeometry(QtCore.QRect(510, 10+50, 0, 0))
            self.groupBoxmemo.setGeometry(QtCore.QRect(100, 10+70, 720, 350))
            self.groupBox_2memo.setGeometry(QtCore.QRect(100, 370+70, 720, 100))
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
            self.pushButtoncollapsexpandm.setIcon(QIcon('Theme/icons/expandv.png'))
            self.pushButtoncollapsexpandm.setIconSize(QSize(24, 15))
        if testheight == 0 and testwidth == 0:
            self.plainTextEditadvancedmem.setGeometry(QtCore.QRect(510, 10+50, 400, 500))
            self.groupBoxmemo.setGeometry(QtCore.QRect(30+50, 10+50, 381, 400))
            self.groupBox_2memo.setGeometry(QtCore.QRect(30+50, 421+50, 381, 100))
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
            self.pushButtoncollapsexpandm.setIcon(QIcon('Theme/icons/collapsev.png'))
            self.pushButtoncollapsexpandm.setIconSize(QSize(24, 15))
            self.pushButton_encrypt.setGeometry(QtCore.QRect(132, 265, 101, 25))

    def pushbutton_handler(self):

        choice = QtWidgets.QMessageBox.question(self, ' Confirm Exit ', "Are You Sure You want To Exit Advanced Mode ?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            self.close_serial()
            self.savesettings()
            self.close()
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

    #! tabwidge 1 ------------------------------------------------------------------------------------------------------

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
        settingsport = QSettings("Dependecies/settingsprogresswrite.ini", QSettings.IniFormat)
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
                scene.addPixmap(QPixmap('Theme/icons/connected.png'))
                self.graphicsView.setScene(scene)
                self.label_8.setStyleSheet(" border-radius: 5px;  color: #039BE5;font-weight: bold;")
        except:
            self.label_8.setText("Error! Check COM Port !")
            scene = QGraphicsScene()
            scene.addPixmap(QPixmap('Theme/icons/wrongcom.png'))
            self.graphicsView.setScene(scene)
            self.label_8.setStyleSheet(" border-radius: 5px;  color: #e53935;font-weight: bold;")

    def close_serial(self):
        self.port = self.comboBox_serial.currentText()
        self.ser.close()
        self.label_8.setText("Serial Port Closed !")
        scene = QGraphicsScene()
        scene.addPixmap(QPixmap('Theme/icons/disconnected.png'))
        self.graphicsView.setScene(scene)
        self.label_8.setStyleSheet(" border-radius: 5px;  color: #039BE5;font-weight: bold;")

    #! tabwidge 2 ------------------------------------------------------------------------------------------------------

    def verifyFlash(self):
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
                            'python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 verify_flash --diff yes ' + " " + verifyoffset + " " + fileName)

                    if self.chip == 'ESP8266':
                        self.process.start(
                            'python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 verify_flash --diff yes ' + " " + verifyoffset + " " + fileName)
                else:
                    if self.chip == 'ESP32':
                        self.process.start(
                            'sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 verify_flash --diff yes ' + " " + verifyoffset + " " + fileName)

                    else:
                        self.process.start(
                            'sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 verify_flash --diff yes ' + " " + verifyoffset + " " + fileName)

            else:
                self.plainTextEditadvanced.appendPlainText("Operation Verify Flash Aborted ")
                QMessageBox.warning(self, 'Operation Aborted', "Operation Verify Flash Aborted ", QMessageBox.Ok)

    def loadRam(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Program to load into RAM", filter='(*.bin)', options=options)
        if not (fileName == "") and not fileName == " ":
            self.port = self.comboBox_serial.currentText()
            if os.name == 'nt':
                if self.chip == 'ESP32':
                    self.process.start(
                        'python ' + self.bundle_dir + 'Dependecies/esptool.py  --no-stub load_ram ' + " " + fileName)
                if self.chip == 'ESP8266':
                    self.process.start(
                        'python' + self.bundle_dir + 'Dependecies/esptool.py  --no-stub load_ram ' + " " + fileName)
            else:
                if self.chip == 'ESP32':
                    self.process.start(
                        'sudo python ' + self.bundle_dir + 'Dependecies/esptool.py  --no-stub load_ram ' + " " + fileName)
                else:
                    self.process.start(
                        'sudo python ' + self.bundle_dir + 'Dependecies/esptool.py  --no-stub load_ram ' + " " + fileName)
        else:
            self.plainTextEditadvanced.appendPlainText("Operation Load RAM Aborted ")

    def getChipid(self):
        self.port = self.comboBox_serial.currentText()
        if os.name == 'nt':
            if self.chip == 'ESP32':
                self.process.start('python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 read_mac')
            if self.chip == 'ESP8266':
                self.process.start('python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 chip_id')
        else:
            if self.chip == 'ESP32':
                self.process.start('sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 read_mac')
            else:
                self.process.start('sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 chip_id')

    def chipId(self):
        self.port = self.comboBox_serial.currentText()
        if os.name == 'nt':
            if self.chip == 'ESP32':
                self.process.start('python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 chip_id ')
            if self.chip == 'ESP8266':
                self.process.start(
                    'python' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 chip_id ')
        else:
            if self.chip == 'ESP32':
                self.process.start(
                    'sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 chip_id ')
            else:
                self.process.start(
                    'sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 chip_id ')

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

                    self.process.start('python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 --port {0} --baud {1}\
                                                       --before default_reset --after hard_reset write_flash\
                                                       -z --flash_freq 80m --flash_mod dio --flash_size {2} \
                                                       {3} {4}'.format(self.port, self.baudRate, self.flasSize,
                                                                       offsetflashcomb
                                                                       , self.lineEdit_combinedfile.text()))
                else:
                    self.process.start('python' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 --port {0} --baud {1}\
                                                       --before default_reset --after hard_reset write_flash --flash_size={2}\
                                                        {3} {4}'.format(self.port, self.baudRate, self.flasSize,
                                                                        offsetflashcomb
                                                                        , self.lineEdit_combinedfile.text()))
            else:
                if self.chip == 'ESP32':
                    self.process.start('sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 --port {0} --baud {1}\
                                                   --before default_reset --after hard_reset write_flash\
                                                   -z --flash_freq 80m --flash_mod dio --flash_size {2} \
                                                   {3} {4}'.format(self.port, self.baudRate, self.flasSize,
                                                                   offsetflashcomb
                                                                   , self.lineEdit_combinedfile.text()))
                else:
                    self.process.start('sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 --port {0} --baud {1}\
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
                    self.process.start('python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 --port {0} --baud {1}\
                                                --before default_reset --after hard_reset write_flash\
                                                -z --flash_freq 80m --flash_mod dio --flash_size {2} \
                                                {3} {4}'.format(self.port, self.baudRate, self.flasSize, offsetflash
                                                                , self.lineEdit_path1.text()))

                else:
                    self.process.start('python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 --port {0} --baud {1}\
                                                --before default_reset --after hard_reset write_flash --flash_size={2}\
                                                 {3} {4}'.format(self.port, self.baudRate, self.flasSize, offsetflash
                                                                 , self.lineEdit_path1.text()))
            else:
                if self.chip == 'ESP32':
                    self.process.start('sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 --port {0} --baud {1}\
                                            --before default_reset --after hard_reset write_flash\
                                            -z --flash_freq 80m --flash_mod dio --flash_size {2} \
                                            {3} {4}'.format(self.port, self.baudRate, self.flasSize, offsetflash
                                                            , self.lineEdit_path1.text()))
                else:
                    self.process.start('sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 --port {0} --baud {1}\
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
                    self.process.start('python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 --port {0} --baud {1}\
                                        --before default_reset --after hard_reset write_flash\
                                        -z --flash_freq 80m --flash_mod dio --flash_size {2} \
                                      {3} {4} {5} {6}'.format(self.port, self.baudRate, self.flasSize, offsetboot,
                                                              self.lineEdit_path2.text(), offsetpart,
                                                              self.lineEdit_path3.text()))
            else:
                if self.chip == 'ESP32':
                    self.process.start('sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 --port {0} --baud {1}\
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
                    self.process.start('python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 --port {0} --baud {1}\
                                        --before default_reset --after hard_reset write_flash\
                                        -z --flash_freq 80m --flash_mod dio --flash_size {2} \
                                         {3} {4} {5} {6} {7} {8}'.format(self.port, self.baudRate, self.flasSize,
                                                                         offsetboot,
                                                                         self.lineEdit_path2.text(), offsetpart,
                                                                         self.lineEdit_path3.text(), offsetfirm,
                                                                         self.lineEdit_path1.text()))
                else:
                    self.process.start('python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 --port {0} --baud {1}\
                                        --before default_reset --after hard_reset write_flash --flash_size={2}\
                                        {3}{4}{5}{6}{7}{8}'.format(self.port, self.baudRate, self.flasSize, offsetboot,
                                                                   self.lineEdit_path2.text(), offsetpart,
                                                                   self.lineEdit_path3.text(), offsetfirm,
                                                                   self.lineEdit_path1.text()))
            else:
                if self.chip == 'ESP32':
                    self.process.start('sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 --port {0} --baud {1}\
                                    --before default_reset --after hard_reset write_flash\
                                    -z --flash_freq 80m --flash_mod dio --flash_size {2} \
                                 {3}{4}{5}{6}{7}{8}'.format(self.port, self.baudRate, self.flasSize, offsetboot,
                                                            self.lineEdit_path2.text(), offsetpart,
                                                            self.lineEdit_path3.text(), offsetfirm,
                                                            self.lineEdit_path1.text()))
                else:
                    self.process.start('sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 --port {0} --baud {1}\
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
                    'python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 --port {0} --baud {1} erase_flash'.format(
                        self.port,
                        self.baudRate))
            if self.chip == 'ESP8266':
                self.process.start(
                    'python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 --port {0} --baud {1} erase_flash'.format(
                        self.port,
                        self.baudRate))
        else:
            if self.chip == 'ESP32':
                self.process.start(
                    'sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 --port {0} --baud {1} erase_flash'.format(
                        self.port, self.baudRate))
            else:
                self.process.start(
                    'sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 --port {0} --baud {1} erase_flash'.format(
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
                        'python ' + self.bundle_dir + 'Dependecies/esptool.py  --chip esp32 image_info' + " " + fileName)
                if self.chip == 'ESP8266':
                    self.process.start(
                        'python ' + self.bundle_dir + 'Dependecies/esptool.py  --chip esp8266 image_info ' + " " + fileName)
            else:
                if self.chip == 'ESP32':
                    self.process.start(
                        'sudo python ' + self.bundle_dir + 'Dependecies/esptool.py  --chip esp32 image_info ' + " " + fileName)
                else:
                    self.process.start(
                        'sudo python ' + self.bundle_dir + 'Dependecies/esptool.py  --chip esp8266 image_info ' + " " + fileName)
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
                        'python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 erase_region ' + startingaddress + " " + length)
                if self.chip == 'ESP8266':
                    self.processmem.start(
                        'python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 erase_region ' + startingaddress + " " + length)
            else:
                if self.chip == 'ESP32':
                    self.processmem.start(
                        'sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 erase_region ' + startingaddress + " " + length)
                else:
                    self.processmem.start(
                        'sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 erase_region ' + startingaddress + " " + length)

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
                    '  python ' + self.bundle_dir + 'Dependecies/espefuse.py --port ' + " " + self.port + " " + ' summary')
            if self.chip == 'ESP8266':
                self.processmem.start(
                    '  python ' + self.bundle_dir + 'Dependecies/espefuse.py --port ' + " " + self.port + " " + ' summary')
        else:
            if self.chip == 'ESP32':
                self.processmem.start(
                    'sudo python ' + self.bundle_dir + 'Dependecies/espefuse.py --port ' + " " + self.port + " " + ' summary')
            else:
                self.processmem.start(
                    'sudo python ' + self.bundle_dir + 'Dependecies/espefuse.py --port ' + " " + self.port + " " + ' summary')

    def fusedump(self):
        self.port = self.comboBox_serial.currentText()
        if os.name == 'nt':
            if self.chip == 'ESP32':
                self.processmem.start(
                    '  python ' + self.bundle_dir + 'Dependecies/espefuse.py --port ' + " " + self.port + " " + ' dump')
            if self.chip == 'ESP8266':
                self.processmem.start(
                    '  python ' + self.bundle_dir + 'Dependecies/espefuse.py --port ' + " " + self.port + " " + ' dump')
        else:
            if self.chip == 'ESP32':
                self.processmem.start(
                    'sudo python ' + self.bundle_dir + 'Dependecies/espefuse.py --port ' + " " + self.port + " " + ' dump')
            else:
                self.processmem.start(
                    'sudo python ' + self.bundle_dir + 'Dependecies/espefuse.py --port ' + " " + self.port + " " + ' dump')

    #! tabwidge 3 ------------------------------------------------------------------------------------------------------

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
                        'python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 read_mem ' + memoryaddr)
                if self.chip == 'ESP8266':
                    self.processmem.start(
                        'python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 read_mem ' + memoryaddr)
            else:
                if self.chip == 'ESP32':
                    self.processmem.start(
                        'sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 read_mem ' + memoryaddr)
                else:
                    self.processmem.start(
                        'sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 read_mem ' + memoryaddr)

    def readstatusreg(self):
        RDSR = self.comboBox_readstatusreg.currentText()
        self.port = self.comboBox_serial.currentText()
        if os.name == 'nt':
            if self.chip == 'ESP32':
                self.processmem.start(
                    'python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 read_flash_status --bytes  ' + " " + RDSR)
            if self.chip == 'ESP8266':
                self.processmem.start(
                    'python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 read_flash_status --bytes  ' + " " + RDSR)
        else:
            if self.chip == 'ESP32':
                self.processmem.start(
                    'sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 read_flash_status --bytes  ' + " " + RDSR)
            else:
                self.processmem.start(
                    'sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 read_flash_status --bytes  ' + " " + RDSR)

    def writestatusreg(self):
        WRSR = self.comboBox_writestatusreg.currentText()
        self.port = self.comboBox_serial.currentText()
        if os.name == 'nt':
            if self.chip == 'ESP32':
                self.processmem.start(
                    'python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 write_flash_status  --bytes  ' + " " + WRSR + " " + '--non-volatile 0')
            if self.chip == 'ESP8266':
                self.processmem.start(
                    'python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 write_flash_status  --bytes  ' + " " + WRSR + " " + '--non-volatile 0')
        else:
            if self.chip == 'ESP32':
                self.processmem.start(
                    'sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 write_flash_status  --bytes  ' + " " + WRSR + " " + '--non-volatile 0')
            else:
                self.processmem.start(
                    'sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 write_flash_status  --bytes  ' + " " + WRSR + " " + '--non-volatile 0')

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
                        'python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 write_mem ' + " " + memoryaddr1 + " " + memoryaddr2 + " " + mask)
                if self.chip == 'ESP8266':
                    self.processmem.start(
                        'python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 write_mem ' + " " + memoryaddr1 + " " + memoryaddr2 + " " + mask)
            else:
                if self.chip == 'ESP32':
                    self.processmem.start(
                        'sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 write_mem ' + " " + memoryaddr1 + " " + memoryaddr2 + " " + mask)
                else:
                    self.processmem.start(
                        'sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 write_mem ' + " " + memoryaddr1 + " " + memoryaddr2 + " " + mask)

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
                        'python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 dump_mem ' + dumpline1 + " " + dumpline2 + " " + fileName)
                if self.chip == 'ESP8266':
                    self.processmem.start(
                        'python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 dump_mem ' + dumpline1 + " " + dumpline2 + " " + fileName)
            else:
                if self.chip == 'ESP32':
                    self.processmem.start(
                        'sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 dump_mem ' + dumpline1 + " " + dumpline2 + " " + fileName)
                else:
                    self.processmem.start(
                        'sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 dump_mem ' + dumpline1 + " " + dumpline2 + " " + fileName)

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
                        'python ' + self.bundle_dir + 'Dependecies/esptool.py  -p ' + " " + self.port + " " + ' -b' + " " + self.comboBox_baud.currentText() + " " + ' read_flash ' + " " + readflashline1 + " " + readflashline2 + " " + fileName)
                if self.chip == 'ESP8266':
                    self.processmem.start(
                        'python ' + self.bundle_dir + 'Dependecies/esptool.py  -p ' + " " + self.port + " " + ' -b' + " " + self.comboBox_baud.currentText() + " " + ' read_flash ' + " " + readflashline1 + " " + readflashline2 + " " + fileName)
            else:
                if self.chip == 'ESP32':
                    self.processmem.start(
                        'sudo python ' + self.bundle_dir + 'Dependecies/esptool.py -p ' + " " + self.port + " " + ' -b' + " " + self.comboBox_baud.currentText() + " " + ' read_flash ' + " " + readflashline1 + " " + readflashline2 + " " + fileName)
                else:
                    self.processmem.start(
                        'sudo python ' + self.bundle_dir + 'Dependecies/esptool.py -p ' + " " + self.port + " " + ' -b' + " " + self.comboBox_baud.currentText() + " " + ' read_flash ' + " " + readflashline1 + " " + readflashline2 + " " + fileName)

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
                            '  python ' + self.bundle_dir + 'Dependecies/espefuse.py --port {0} burn_key flash_encryption {1}'.format(
                                self.port, self.lineEdit_keypath.text()))
                    if self.chip == 'ESP8266':
                        self.processmem.start(
                            '  python ' + self.bundle_dir + '//espefuse.py --port {0} burn_key flash_encryption {1}'.format(
                                self.port, self.lineEdit_keypath.text()))
                else:
                    if self.chip == 'ESP32':
                        self.processmem.start(
                            'sudo python ' + self.bundle_dir + 'Dependecies/espefuse.py --port {0} burn_key flash_encryption {1}'.format(
                                self.port, self.lineEdit_keypath.text()))
                    else:
                        self.processmem.start(
                            'sudo python ' + self.bundle_dir + 'Dependecies/espefuse.py --port {0} burn_key flash_encryption {1}'.format(
                                self.port, self.lineEdit_keypath.text()))

    #! tabwidge 4 ------------------------------------------------------------------------------------------------------

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
                    'python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 make_image -f  {0} -a {1}  -f {2} -a {3} -f  {4} -a {5} {6}'.format(
                        path1, offset1, path2, offset2, path3, offset3, fileName))
            if self.chip == 'ESP8266':
                self.process.start(
                    'python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 make_image -f  {0} -a {1}  -f {2} -a {3} -f  {4} -a {5} {6}'.format(
                        path1, offset1, path2, offset2, path3, offset3, fileName))
        else:
            if self.chip == 'ESP32':
                self.process.start(
                    'sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 make_image -f  {0} -a {1}  -f {2} -a {3} -f  {4} -a {5} {6}'.format(
                        path1, offset1, path2, offset2, path3, offset3, fileName))
            else:
                self.process.start(
                    'sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 make_image -f  {0} -a {1}  -f {2} -a {3} -f  {4} -a {5} {6}'.format(
                        path1, offset1, path2, offset2, path3, offset3, fileName))

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
                        'python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 elf2image ' + " " + elfpath)
                if self.chip == 'ESP8266':
                    self.process.start(
                        'python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 elf2image ' + " " + elfpath)
            else:
                if self.chip == 'ESP32':
                    self.process.start(
                        'sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp32 elf2image ' + " " + elfpath)
                else:
                    self.process.start(
                        'sudo python ' + self.bundle_dir + 'Dependecies/esptool.py --chip esp8266 elf2image ' + " " + elfpath)

    def generateencryptionkey(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "Generated Key File Path", filter='(*.bin)', options=options)
        if not fileName == " " and not fileName == "":
            self.lineEdit_keypath.setText(fileName)
            if os.name == 'nt':
                if self.chip == 'ESP32':
                    self.processmem.start(
                        '  python ' + self.bundle_dir + 'Dependecies/espsecure.py generate_flash_encryption_key' + " " + fileName)
                if self.chip == 'ESP8266':
                    self.processmem.start(
                        '  python ' + self.bundle_dir + 'Dependecies/espsecure.py generate_flash_encryption_key ' + " " + fileName)
            else:
                if self.chip == 'ESP32':
                    self.processmem.start(
                        'sudo python ' + self.bundle_dir + 'Dependecies/espsecure.py generate_flash_encryption_key ' + " " + fileName)
                else:
                    self.processmem.start(
                        'sudo python ' + self.bundle_dir + 'Dependecies/espsecure.py generate_flash_encryption_key ' + " " + fileName)

    #! tabwidge 5 ------------------------------------------------------------------------------------------------------

    def refbuttonfunction(self):

        self.workerThread.start()
        self.btnref.setDisabled(True)
        self.btnexport.setDisabled(True)
        self.status_txt = QtWidgets.QLabel()
        movie = QMovie("Theme/icons/GREY-GEAR-LOADING.gif")
        self.status_txt.setMovie(movie)
        self.status_txt.setAlignment(Qt.AlignCenter)
        movie.start()
        self.lay.addWidget(self.status_txt)

        QtTest.QTest.qWait(8000)
        movie.stop()
        self.status_txt.deleteLater()
        #
        self.conn = sqlite3.connect('Dependecies/samples.db')
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
        movie = QMovie("Theme/icons/GREY-GEAR-LOADING.gif")
        self.status_txt.setMovie(movie)
        self.status_txt.setAlignment(Qt.AlignCenter)

        movie.start()
        self.lay.addWidget(self.status_txt)

        QtTest.QTest.qWait(10000)
        movie.stop()
        self.status_txt.deleteLater()

        self.conn = sqlite3.connect('Dependecies/samples.db')
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
        self.tableWidget.setGeometry(QtCore.QRect(0, 0, 850, 650))
        self.lay.addWidget(self.tableWidget)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setColumnWidth(0, 200)
        self.tableWidget.setColumnWidth(1, 230)
        self.tableWidget.setColumnWidth(2, 200)
        self.tableWidget.setColumnWidth(3, 100)
        self.tableWidget.setColumnWidth(4, 100)
        self.tableWidget.setColumnWidth(5, 50)

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
        self.btnexport.setIcon(QIcon('Theme/icons/Excel.png'))
        self.btnexport.setStyleSheet("border: none;border-radius: 0px;")
        self.btnexport.setIconSize(QSize(20, 20))
        self.btnexport.setStyleSheet(open(SETTINGS_style, "r").read())

        self.tableWidget.setCellWidget(0, 5, self.btnref)
        self.btnref.setIcon(QIcon('Theme/icons/refresh.png'))
        self.btnref.setStyleSheet("border: none;border-radius: 0px;")
        self.btnref.setStyleSheet(open(SETTINGS_style, "r").read())

        for i in range(32):
            btn = getattr(self, f'btn{i+1}')
            btn.setIcon(QIcon('Theme/icons/executefuse1.png'))
            btn.setStyleSheet("border: none;border-radius: 0px;")
            btn.setStyleSheet(open(SETTINGS_style, "r").read())
            self.tableWidget.setCellWidget(i+1, 5, btn)  # Place the button in the i-th row, 0-th column

    def burn(self):
        self.item = self.tableWidget.item(1, 0)

        settings_burn = QSettings("Dependecies/settingsprogresswrite.ini", QSettings.IniFormat)
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
                                '  python ' + self.bundle_dir + 'Dependecies/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        if self.chip == 'ESP8266':
                            self.processmem.start(
                                '  python ' + self.bundle_dir + 'Dependecies/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                    else:
                        if self.chip == 'ESP32':
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + 'Dependecies/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                        else:
                            self.processmem.start(
                                'sudo python ' + self.bundle_dir + 'Dependecies/espefuse.py --port ' + " " + self.port + " " + ' burn_efuse' + " " + self.item.text() + " " + new_value)
                else:
                    pass

            else:
                settings_burn.setValue('confirm_burn', "no")
                pass

    #! tabwidge 6 ------------------------------------------------------------------------------------------------------

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
            # self.fusetab.setDisabled(True)
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
        self.flasSize   = self.comboBox_flashsize.currentText()
   
    def cleanUp(self):
        choice          = QtWidgets.QMessageBox.question(self, ' Confirm Exit ', "Are You Sure You want To Exit Flash ?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            self.close_serial()
            sys.exit()
        else:
            app         = QtWidgets.QApplication(sys.argv)
            window      = AdvancedModeApp()
            window.show()
            app.aboutToQuit.connect(window.cleanUp)
            sys.exit(app.exec_())

def main():
    app             = QtWidgets.QApplication(sys.argv)
    
    splash_pix      = QPixmap(splash_screen_png)
    splash          = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    
    progressBar     = QProgressBar(splash)
    progressBar.setGeometry(0, 470, 480, 10)
    
    splash.setMask(splash_pix.mask())
    
    progressBar.setTextVisible(False)
    progressBar.setStyleSheet(open(QSS_style, "r").read())
    
    splash.show()
    
    for i in range(0, 100):
        progressBar.setValue(i)
        t = time.time()
        while time.time() < t + 0.02:
            app.processEvents()
    splash.close()
    window          = AdvancedModeApp()
    window.setWindowFlags(Qt.FramelessWindowHint)
    window.show()
    app.aboutToQuit.connect(window.cleanUp)
    sys.exit(app.exec_())

#?---------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
#?---------------------------------------------------------------------------------------------------------------------------