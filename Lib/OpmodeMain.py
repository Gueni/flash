import os
import os.path
import shutil
import sys
import time

import pyzipper
import serial.tools.list_ports
from PyQt5 import QtCore, QtGui, QtWidgets, QtTest
from PyQt5.QtCore import Qt, QSize, QSettings, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QFileDialog, QSplashScreen, QProgressBar, QInputDialog, QLineEdit

import aboutmain
import Lib.getfilesubnamemodule as getfilesubnamemodule
import loghandel
import opmodeui

SETTINGS_style = 'style'
progressnum = 'progressnum'

machinesettig = 'machinesettig'
ipaddresssetting = 'ipaddresssetting'
timenowsetting = 'timenowsetting'
datenowsetting = 'datenowsetting'


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


class ESPToolGUIApp(QtWidgets.QMainWindow, opmodeui.Ui_MainWindow):
    switch_window2 = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(ESPToolGUIApp, self).__init__(parent)
        if getattr(sys, 'frozen', False):
            self.frozen = 'ever so'
            self.bundle_dir = sys._MEIPASS
        else:
            self.bundle_dir = os.path.dirname(os.path.abspath(__file__))
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(self.bundle_dir + '/icons/espLogo.png'))
        self.plainTextEditStatus.setReadOnly(True)
        self.memoryESP8266 = ['detect', '512KB', '256KB', '1MB', '2MB', '4MB', '2MB-c1', '4MB-c1', '4MB-c2']
        self.memoryESP32 = ['detect', '1MB', '2MB', '4MB', '8MB', '16MB']
        self.ser = serial.Serial()
        self._active = False
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(50)
        self.progressBaroverall.setMinimum(1)
        self.progressBaroverall.setMaximum(100)
        self.initButtons()
        self.initProcess()
        self.baudRate = 921600
        self.port = ''
        self.flasSize = self.comboBoxMemory.currentText()
        self.frozen = 'not'
        self.chip = 'ESP32'
        self.statusbar.showMessage('V 0.1')
        self.actionExit_2.setShortcut('Ctrl+Q')
        self.actionExit_2.triggered.connect(self.close_application)
        self.actionExit_2.setStatusTip('Exit ')
        self.actionAdvanced_Mode_2.setShortcut('Ctrl+A')
        self.actionAdvanced_Mode_2.setStatusTip('Switch to Advanced Mode')
        self.actionDark.triggered.connect(self.setDark)
        self.actionLight_Blue.triggered.connect(self.setactionLight_Blue)
        self.pushButtoncollapsexpand.setIcon(QIcon('icons/collapse.png'))
        self.pushButtoncollapsexpand.setIconSize(QSize(24, 15))
        self.actionAbout_2.triggered.connect(self.showAbout)
        self.settingstyle = QSettings("settingsstyle.ini", QSettings.IniFormat)
        self.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

    def setDark(self):
        self.settingstyle.setValue(SETTINGS_style, "qssthemes/Dark/darkstyle.qss")
        self.settingstyle.sync()
        self.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.label.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.label_2.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.label_3.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.label_4.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.label_5.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.labelfirmware.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButtonOpen.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButtonFlashAll.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButtonApplication.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButtonClear.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButtonClose.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButtoncollapsexpand.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButtonErase.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.plainTextEditStatus.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.comboBoxMemory.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.comboBoxBaudSelect.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.comboBoxChipSelect.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.comboBoxCOMPort.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.progressBaroverall.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

    def setactionLight_Blue(self):
        self.setStyleSheet(self.styleSheet())
        self.settingstyle = QSettings("settingsstyle.ini", QSettings.IniFormat)
        self.setStyleSheet(open("qssthemes/LightBlue/stylesheet.qss", "r").read())
        self.settingstyle.setValue(SETTINGS_style, "qssthemes/LightBlue/stylesheet.qss")
        self.settingstyle.sync()
        self.label.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.label_2.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.label_3.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.label_4.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.label_5.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.labelfirmware.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButtonOpen.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButtonFlashAll.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButtonApplication.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButtonClear.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButtonClose.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButtoncollapsexpand.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.pushButtonErase.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.plainTextEditStatus.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.comboBoxMemory.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.comboBoxBaudSelect.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.comboBoxChipSelect.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.comboBoxCOMPort.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())
        self.progressBaroverall.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

    def pushbutton_handler(self):
        self.switch_window.emit()

    def showAbout(self):
        self.window = aboutmain.abouthandel()
        self.window.show()

    def close_application(self):
        choice = QtWidgets.QMessageBox.question(self, ' Confirm Exit ', "Are You Sure You want To Exit MicroTool ?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            self.close_serial()
            if os.path.exists(os.path.join('temp')) and os.path.isdir(os.path.join('temp')):
                shutil.rmtree(os.path.join('temp'))
            sys.exit()
        else:
            pass

    def selectFile(self, name, obj):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        # , filter="Bin files (*.bin);; zip files (*.µdt)"
        fileName, _ = QFileDialog.getOpenFileName(self, name, options=options)
        obj.setText(fileName)

    def baudSelect(self):
        self.baudRate = int(self.comboBoxBaudSelect.currentText())

    def portSelect(self):
        self.port = self.lineEditCOMPort.text()

    def flashSizeSelect(self):
        self.flasSize = self.comboBoxMemory.currentText()

    def dataReady(self):
        self.plainTextEditStatus.appendPlainText(bytearray(self.process.readAllStandardOutput()).decode('utf-8'))

    def initProcess(self):
        self.process = QtCore.QProcess(self)
        self.process.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self.process.readyRead.connect(self.dataReady)
        self.process.started.connect(self.disableButtons)
        self.process.finished.connect(self.enableButtons)

    def disableButtons(self):
        self.pushButtonFlashAll.setDisabled(True)
        self.pushButtonApplication.setDisabled(True)
        self.comboBoxMemory.setDisabled(True)
        self.comboBoxCOMPort.setDisabled(True)
        self.comboBoxChipSelect.setDisabled(True)
        self.comboBoxBaudSelect.setDisabled(True)
        self.pushButtonOpen.setDisabled(True)
        self.pushButtonClose.setDisabled(True)
        self.pushButtonErase.setDisabled(True)

    def enableButtons(self):
        if self.chip == 'ESP32':
            self.pushButtonFlashAll.setDisabled(False)
            self.pushButtonApplication.setDisabled(False)
            self.comboBoxMemory.setDisabled(False)
            self.comboBoxCOMPort.setDisabled(False)
            self.comboBoxBaudSelect.setDisabled(False)
            self.pushButtonOpen.setDisabled(False)
            self.pushButtonErase.setDisabled(False)
            self.comboBoxChipSelect.setDisabled(False)
            self.pushButtonClose.setDisabled(False)
            if os.path.exists(os.path.join('temp')) and os.path.isdir(os.path.join('temp')):
                shutil.rmtree(os.path.join('temp'))

        else:
            self.pushButtonErase.setDisabled(False)
            self.comboBoxMemory.setDisabled(False)
            self.comboBoxCOMPort.setDisabled(False)
            self.comboBoxBaudSelect.setDisabled(False)
            self.pushButtonFlashAll.setDisabled(False)

    def expandcollaps(self):
        testwidth = self.plainTextEditStatus.width()
        testheight = self.plainTextEditStatus.height()
        if testheight == 296 and testwidth == 781:
            self.plainTextEditStatus.setGeometry(QtCore.QRect(10, 225, 0, 0))
            self.setFixedSize(806, 280)
            self.pushButtoncollapsexpand.setIcon(QIcon('icons/expand.png'))
            self.pushButtoncollapsexpand.setIconSize(QSize(24, 15))
        if testheight == 0 and testwidth == 0:
            self.plainTextEditStatus.setGeometry(QtCore.QRect(10, 225, 781, 296))
            self.setFixedSize(806, 567)
            self.pushButtoncollapsexpand.setIcon(QIcon('icons/collapse.png'))
            self.pushButtoncollapsexpand.setIconSize(QSize(24, 15))

    def initButtons(self):
        self.pushButtonApplication.clicked.connect(
            lambda: self.selectFile('Select Application File', self.labelfirmware))
        self.pushButtonErase.clicked.connect(self.erase)
        self.pushButtonFlashAll.clicked.connect(self.flashProcess)
        self.pushButtonOpen.clicked.connect(self.open_serial)
        self.pushButtonClose.clicked.connect(self.close_serial)
        self.pushButtonClear.clicked.connect(self.clear_log)
        self.comboBoxBaudSelect.addItems(['1500000', '921600', '512000', '256000', '230400', '115200', '74880', '9600'])
        self.comboBoxBaudSelect.currentIndexChanged.connect(self.baudSelect)
        self.baudRate = int(self.comboBoxBaudSelect.currentText())
        self.comboBoxChipSelect.addItems(['ESP32', 'ESP8266'])
        self.comboBoxChipSelect.currentIndexChanged.connect(self.chipSelect)
        comPort = []
        try:
            for x in serial.tools.list_ports.comports():
                comPort.append(str(x.device))
        except IndexError:
            pass
        self.comboBoxCOMPort.addItems(comPort)
        self.comboBoxCOMPort.popupAboutToBeShown.connect(self.comPortClick)
        self.comboBoxCOMPort.currentIndexChanged.connect(self.comPortSelect)
        self.port = self.comboBoxCOMPort.currentText()
        self.comboBoxMemory.addItems(self.memoryESP32)
        self.comboBoxMemory.currentIndexChanged.connect(self.memorySelect)
        self.flasSize = self.comboBoxMemory.currentText()
        self.actionAdvanced_Mode_2.triggered.connect(self.login2)
        self.pushButtoncollapsexpand.clicked.connect(self.expandcollaps)

    def login2(self):
        self.loginwin = loghandel.Loghandler()
        self.close_serial()
        self.close()
        self.loginwin.show()

    def memorySelect(self):
        self.flasSize = self.comboBoxMemory.currentText()

    def comPortClick(self):
        comPort = []
        try:
            for x in serial.tools.list_ports.comports():
                comPort.append(str(x.device))
        except IndexError:
            pass
        self.comboBoxCOMPort.clear()
        self.comboBoxCOMPort.addItems(comPort)

    def comPortSelect(self):
        self.port = self.comboBoxCOMPort.currentText()

    def chipSelect(self):
        self.chip = self.comboBoxChipSelect.currentText()
        if self.chip == 'ESP8266':
            self.comboBoxMemory.clear()
            self.comboBoxMemory.addItems(self.memoryESP8266)
        else:
            self.comboBoxMemory.clear()
            self.comboBoxMemory.addItems(self.memoryESP32)

    def open_serial(self):
        self.port = self.comboBoxCOMPort.currentText()
        try:
            if self.ser.is_open == False:
                self.ser = serial.Serial(self.port, baudrate=115200, timeout=0, bytesize=serial.EIGHTBITS,
                                         parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, rtscts=False,
                                         dsrdtr=False)
            if self.ser.is_open == True:
                self.plainTextEditStatus.appendPlainText("Connection Established !")
        except:
            self.plainTextEditStatus.appendPlainText("Error! Check COM Port")

    def close_serial(self):
        self.port = self.comboBoxCOMPort.currentText()
        self.ser.close()
        self.plainTextEditStatus.appendPlainText("Serial Port Closed !")

    def tick(self):
        if self.ser.is_open == True:
            try:
                s = self.ser.read(512)
                if len(s) > 0:
                    self.plainTextEditStatus.appendPlainText(s.decode('utf-8'))
            except:
                pass

    def clear_log(self):
        self.port = self.comboBoxCOMPort.currentText()
        self.plainTextEditStatus.clear()

    def cleanUp(self):
        choice = QtWidgets.QMessageBox.question(self, ' Confirm Exit ', "Are You Sure You want To Exit MicroTool ?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            self.close_serial()
            sys.exit()
        else:
            app = QtWidgets.QApplication(sys.argv)
            window = ESPToolGUIApp()
            window.show()
            app.aboutToQuit.connect(window.cleanUp)
            sys.exit(app.exec_())

    def erase(self):
        self.port = self.comboBoxCOMPort.currentText()
        if os.name == 'nt':
            if self.chip == 'ESP32':
                self.process.start(
                    'python ' +self.bundle_dir + '/esptool.py --chip esp32 --port {0} --baud {1} erase_flash'.format(self.port,
                                                                                                           self.baudRate))
            if self.chip == 'ESP8266':
                self.process.start(
                    'python ' +self.bundle_dir + '/esptool.py --chip esp8266 --port {0} --baud {1} erase_flash'.format(self.port,
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

    def setProgressVal(self, val):
        self.progressBaroverall.setValue(val)

    def flashProcess(self):

        self.port = self.comboBoxCOMPort.currentText()
        if self.labelfirmware.text() == "" or self.labelfirmware.text() == " ":
            self.plainTextEditStatus.appendPlainText("Error: Firmware is missing.")
            QtWidgets.QMessageBox.question(self, ' Error: Firmware is missing. ',
                                           "Select a firmware file (.bin) Or an mtool package (.mtool).",
                                           QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Yes)
            return
        self.ser.close()
        self.thread = MyprogressbarThread()
        self.thread.change_value.connect(self.setProgressVal)
        self.thread.start()
        filepath = self.labelfirmware.text()
        head, tail = os.path.split(filepath)

        if tail.lower().endswith(('.bin', '.Bin')):
            text, okPressed = QInputDialog.getText(self, "Get Offset", "Enter Offset:", QLineEdit.Normal, "")
            if okPressed and text != '':
                if os.name == 'nt':
                    if self.chip == 'ESP32':
                        self.process.start('python ' + self.bundle_dir + '/esptool.py --chip esp32 --port {0} --baud {1}\
                                                      --before default_reset --after hard_reset write_flash\
                                                      -z --flash_freq 80m --flash_mod dio --flash_size {2} {3} {4}'.format(
                            self.port,
                            self.comboBoxBaudSelect.currentText(), self.comboBoxMemory.currentText(), text, filepath))
                    else:
                        self.process.start('python ' + self.bundle_dir + '/esptool.py --chip esp8266 --port {0} --baud {1}\
                                                      --before default_reset --after hard_reset write_flash\
                                                      -z --flash_freq 80m --flash_mod dio --flash_size {3} {4} {5}'.format(
                            self.port,
                            self.comboBoxBaudSelect.currentText(), self.comboBoxMemory.currentText(), text,
                            self.labelfirmware.text()))
                else:
                    if self.chip == 'ESP32':
                        self.process.start('sudo python ' + self.bundle_dir + '/esptool.py --chip esp32 --port {0} --baud {1}\
                                                      --before default_reset --after hard_reset write_flash\
                                                      -z --flash_freq 80m --flash_mod dio --flash_size {3} {4} {5}'.format(
                            self.port,
                            self.baudRate, self.flasSize, text, self.labelfirmware.text()))
                    else:
                        self.process.start('sudo python ' + self.bundle_dir + '/esptool.py --chip esp8266 --port {0} --baud {1}\
                                                      --before default_reset --after hard_reset write_flash\
                                                      -z --flash_freq 80m --flash_mod dio --flash_size {3} {4} {5}'.format(
                            self.port,
                            self.baudRate, self.flasSize, text, self.labelfirmware.text()))
        elif tail.lower().endswith('.mtool'):
            secret_password = b'hello123456789'
            with pyzipper.AESZipFile(filepath) as zf:
                zf.extractall(os.path.join('temp'), pwd=secret_password)
            # For the given path, get the List of all files in the directory tree
            dirName = os.path.join('temp')
            if os.path.exists(dirName) and os.path.isdir(dirName):
                # Get the list of all files in directory tree at given path
                listOfFiles = getfilesubnamemodule.getListOfFiles(dirName)
                settings = QSettings(listOfFiles[0], QSettings.IniFormat)
                settings_offset1 = settings.value('offset1', type=str)
                settings_offset2 = settings.value('offset2', type=str)
                settings_offset3 = settings.value('offset3', type=str)
                settings_baudrate = settings.value('baudrate', type=int)
                settings_flashsize = settings.value('flashsize', type=int)
                settings_flashmode = settings.value('flashmode', type=str)

                datenowsetting = settings.value('datenowsetting')
                timenowsetting = settings.value('timenowsetting')
                ipaddresssetting = settings.value('ipaddresssetting')
                machinesettig = settings.value('machinesettig')
                self.comboBoxBaudSelect.setCurrentIndex(settings_baudrate)
                self.comboBoxMemory.setCurrentIndex(settings_flashsize)
                offsetboot = settings_offset2
                offsetpart = settings_offset3
                offsetfirm = settings_offset1
                self.ser.close()
                self.ser.close()
                self.thread = MyprogressbarThreadflashall()
                self.thread.change_valueall.connect(self.setProgressVal)
                self.thread.start()
                self.plainTextEditStatus.appendPlainText(
                    "********************************************************************")
                self.plainTextEditStatus.appendPlainText(
                    "********************************************************************")
                self.plainTextEditStatus.appendPlainText("INFORMATION ABOUT  " + str(tail))
                self.plainTextEditStatus.appendPlainText(
                    "********************************************************************")
                self.plainTextEditStatus.appendPlainText("Date Created : " + str(datenowsetting))
                self.plainTextEditStatus.appendPlainText("Time Created : " + str(timenowsetting))
                self.plainTextEditStatus.appendPlainText("Computer Created With : ")
                self.plainTextEditStatus.appendPlainText(str(ipaddresssetting))
                self.plainTextEditStatus.appendPlainText(str(machinesettig))
                self.plainTextEditStatus.appendPlainText(
                    "********************************************************************")
                self.plainTextEditStatus.appendPlainText(
                    "********************************************************************")
                if os.name == 'nt':
                    if self.chip == 'ESP32':
                        self.process.start('python ' + self.bundle_dir + '/esptool.py --chip esp32 --port {0} --baud {1}\
                                            --before default_reset --after hard_reset write_flash\
                                            -z --flash_freq 80m --flash_mod {2} --flash_size {3} \
                                             {4} {5} {6} {7} {8} {9}'.format(self.port,
                                                                             self.comboBoxBaudSelect.currentText(),
                                                                             settings_flashmode,
                                                                             self.comboBoxMemory.currentText(),
                                                                             offsetboot,
                                                                             listOfFiles[2], offsetpart,
                                                                             listOfFiles[3], offsetfirm,
                                                                             listOfFiles[1]))


                else:
                    if self.chip == 'ESP32':
                        self.process.start('sudo python ' + self.bundle_dir + '/esptool.py --chip esp32 --port {0} --baud {1}\
                                            --before default_reset --after hard_reset write_flash\
                                            -z --flash_freq 80m --flash_mod {2} --flash_size {3} \
                                             {4} {5} {6} {7} {8} {9}'.format(self.port, settings_baudrate,
                                                                             settings_flashmode, settings_flashsize,
                                                                             offsetboot,
                                                                             listOfFiles[2], offsetpart,
                                                                             listOfFiles[3], offsetfirm,
                                                                             listOfFiles[1]))




def main():
    app = QtWidgets.QApplication(sys.argv)
    splash_pix = QPixmap('icons/loadsplash.jpg')
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    progressBar = QProgressBar(splash)
    progressBar.setGeometry(0, 337, 429, 10)
    splash.setMask(splash_pix.mask())
    progressBar.setTextVisible(False)
    progressBar.setStyleSheet(open("qssthemes/Dark/darkstyle.qss", "r").read())
    splash.show()
    for i in range(0, 100):
        progressBar.setValue(i)
        t = time.time()
        while time.time() < t + 0.02:
            app.processEvents()
    time.sleep(0.01)
    splash.close()
    window = ESPToolGUIApp()
    window.show()
    app.aboutToQuit.connect(window.cleanUp)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
