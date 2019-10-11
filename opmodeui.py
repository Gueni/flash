from PyQt5 import QtCore, QtWidgets

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8


    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)


class ComboBoxCOMPORT(QtWidgets.QComboBox):
    popupAboutToBeShown = QtCore.pyqtSignal()

    def showPopup(self):
        self.popupAboutToBeShown.emit()
        super(ComboBoxCOMPORT, self).showPopup()


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(806, 567)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        # MainWindow.setStyleSheet(open("qssthemes/Dark/darkstyle.qss", "r").read())
        self.plainTextEditStatus = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.plainTextEditStatus.setGeometry(QtCore.QRect(10, 225, 781, 296))
        self.plainTextEditStatus.setObjectName("plainTextEditStatus")
        self.pushButtoncollapsexpand = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtoncollapsexpand.setGeometry(QtCore.QRect(10, 210, 781, 15))
        self.pushButtoncollapsexpand.setObjectName("pushButtoncollapsexpand")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 20, 51, 21))
        self.label.setObjectName("label")
        self.comboBoxCOMPort = ComboBoxCOMPORT(self.centralwidget)
        self.comboBoxCOMPort.setGeometry(QtCore.QRect(120, 20, 261, 22))
        self.comboBoxCOMPort.setCurrentText("")
        self.comboBoxCOMPort.setObjectName("comboBoxCOMPort")
        self.comboBoxBaudSelect = QtWidgets.QComboBox(self.centralwidget)
        self.comboBoxBaudSelect.setGeometry(QtCore.QRect(120, 60, 261, 22))
        self.comboBoxBaudSelect.setObjectName("comboBoxBaudSelect")
        self.comboBoxMemory = QtWidgets.QComboBox(self.centralwidget)
        self.comboBoxMemory.setGeometry(QtCore.QRect(120, 140, 261, 22))
        self.comboBoxMemory.setObjectName("comboBoxMemory")
        self.comboBoxChipSelect = QtWidgets.QComboBox(self.centralwidget)
        self.comboBoxChipSelect.setGeometry(QtCore.QRect(120, 100, 261, 22))
        self.comboBoxChipSelect.setObjectName("comboBoxChipSelect")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(10, 60, 61, 21))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(10, 100, 61, 21))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(10, 140, 61, 21))
        self.label_4.setObjectName("label_4")
        self.pushButtonApplication = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonApplication.setGeometry(QtCore.QRect(310, 180, 71, 23))
        self.pushButtonApplication.setObjectName("pushButtonFirmware")
        self.pushButtonOpen = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonOpen.setGeometry(QtCore.QRect(410, 30, 111, 31))
        self.pushButtonOpen.setObjectName("pushButtonOpen")
        self.pushButtonClose = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonClose.setGeometry(QtCore.QRect(550, 30, 111, 31))
        self.pushButtonClose.setObjectName("pushButtonClose")
        self.pushButtonClear = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonClear.setGeometry(QtCore.QRect(680, 30, 111, 31))
        self.pushButtonClear.setObjectName("pushButtonClear")
        self.pushButtonErase = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonErase.setGeometry(QtCore.QRect(410, 110, 381, 31))
        self.pushButtonErase.setObjectName("pushButtonErase")
        self.pushButtonFlashAll = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonFlashAll.setGeometry(QtCore.QRect(410, 70, 381, 31))
        self.pushButtonFlashAll.setObjectName("pushButtonFlashALL")
        self.labelfirmware = QtWidgets.QLineEdit(self.centralwidget)
        self.labelfirmware.setGeometry(QtCore.QRect(10, 180, 291, 20))
        self.labelfirmware.setObjectName("labelfirmware")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(410, 180, 81, 16))
        self.label_5.setObjectName("label_5")
        self.progressBaroverall = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBaroverall.setGeometry(QtCore.QRect(510, 180, 281, 16))
        self.progressBaroverall.setProperty("value", 24)
        self.progressBaroverall.setObjectName("progressBaroverall")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 806, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menuTools = QtWidgets.QMenu(self.menubar)
        self.menuTools.setObjectName("menuTools")
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionExit_2 = QtWidgets.QAction(MainWindow)
        self.actionExit_2.setObjectName("actionExit_2")
        self.actionAdvanced_Mode_2 = QtWidgets.QAction(MainWindow)
        self.actionAdvanced_Mode_2.setObjectName("actionAdvanced_Mode_2")
        self.actionAbout_2 = QtWidgets.QAction(MainWindow)
        self.actionAbout_2.setObjectName("actionAbout_2")
        self.actionDark = QtWidgets.QAction(MainWindow)
        self.actionDark.setObjectName("Dark")

        self.actionLight_Blue = QtWidgets.QAction(MainWindow)
        self.actionLight_Blue.setObjectName("Light Blue")

        self.menuFile.addAction(self.actionExit_2)
        self.menuHelp.addAction(self.actionAbout_2)
        self.menuTools.addAction(self.actionAdvanced_Mode_2)
        self.menuView.addAction(self.actionDark)

        self.menuView.addAction(self.actionLight_Blue)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MicroTool 1.0"))
        self.label.setText(_translate("MainWindow", "Serial Port"))
        self.label_2.setText(_translate("MainWindow", "Baud Rate"))
        self.label_3.setText(_translate("MainWindow", "Device"))
        self.label_4.setText(_translate("MainWindow", "Flash Size"))
        self.pushButtonApplication.setText(_translate("MainWindow", "Browse"))
        self.pushButtonOpen.setText(_translate("MainWindow", "Open COM"))
        self.pushButtonClose.setText(_translate("MainWindow", "Close COM"))
        self.pushButtonClear.setText(_translate("MainWindow", "Clear Log"))
        self.pushButtonErase.setText(_translate("MainWindow", "Erase"))
        self.pushButtonFlashAll.setText(_translate("MainWindow", "Flash"))
        self.labelfirmware.setPlaceholderText(_translate("MainWindow", "Firmware File"))
        self.label_5.setText(_translate("MainWindow", "Overall Progress"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.menuTools.setTitle(_translate("MainWindow", "Tools"))
        self.menuView.setTitle(_translate("MainWindow", "View"))
        self.actionExit_2.setText(_translate("MainWindow", "Exit"))
        self.actionAdvanced_Mode_2.setText(_translate("MainWindow", "Advanced Mode"))
        self.actionAbout_2.setText(_translate("MainWindow", "About"))
        self.actionDark.setText(_translate("MainWindow", "Dark"))

        self.actionLight_Blue.setText(_translate("MainWindow", "Light Blue"))


