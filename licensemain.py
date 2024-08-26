import os
import os.path
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtWidgets import QDesktopWidget
import licensegui

SETTINGS_style = 'Theme/stylesheet.qss'

class licensehandel(QtWidgets.QMainWindow, licensegui.Ui_MainWindow):
    switch_window2 = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(licensehandel, self).__init__(parent)
        if getattr(sys, 'frozen', False):
            self.frozen = 'ever so'
            self.bundle_dir = sys._MEIPASS
        else:
            self.bundle_dir = os.path.dirname(os.path.abspath(__file__))
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(self.bundle_dir + 'Theme/icons/espLogo.png'))
        self.setStyleSheet(open("Theme/stylesheet.qss", "r").read())
        self.pushButton.clicked.connect(self.backtoabout)
        self.label.setOpenExternalLinks(True)
        self.textEdit.setReadOnly(True)
        self.setWindowFlags(self.windowFlags() | Qt.Popup | Qt.WindowStaysOnTopHint)
        self.center()


    def backtoabout(self):
        self.close()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
