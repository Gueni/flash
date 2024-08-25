import os
import os.path
import sqlite3
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QMessageBox
import OpmodeMain
import advancedmode
import changepasshandler
import logingui

SETTINGS_style = 'style'


class Loghandler(QtWidgets.QMainWindow, logingui.Ui_MainWindow):
    switch_window2 = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(Loghandler, self).__init__(parent)
        if getattr(sys, 'frozen', False):
            self.frozen = 'ever so'
            self.bundle_dir = sys._MEIPASS
        else:
            self.bundle_dir = os.path.dirname(os.path.abspath(__file__))
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(self.bundle_dir + '/icons/espLogo.png'))
        self.setStyleSheet(open("Theme/qssthemes/LightBlue/stylesheet.qss", "r").read())
        self.pushButton.clicked.connect(self.log_sig)
        self.pushButton_2.clicked.connect(self.changepass)
        self.pushButton_cancel.clicked.connect(self.cancellog)
        self.settingstyle = QSettings("settingsstyle.ini", QSettings.IniFormat)
        self.setStyleSheet(self.styleSheet())
        self.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

    def log_sig(self):
        conn = sqlite3.connect('Userdatabase.db')
        c = conn.cursor()
        try:
            c.execute("SELECT * FROM USERTABLE ")
            data = c.fetchall()
            for row in data:
                conn.commit()
            c.close()
            conn.close()
        except Exception:
            QMessageBox.warning(QMessageBox(), 'Error', 'Could not connect to the database.')
        if self.lineEdit.text() == row[1]:
            self.advanced = advancedmode.AdvancedModeApp()
            self.close()
            self.advanced.show()
        else:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.setStyleSheet(open("qssthemes/Dark/darkstyle.qss", "r").read())
            error_dialog.showMessage('Password Incorrect !')
            error_dialog.exec_()

    def changepass(self):
        self.changep = changepasshandler.passhandler()
        self.close()
        self.changep.show()

    def cancellog(self):
        self.loginwin = OpmodeMain.ESPToolGUIApp()
        self.close()
        self.loginwin.show()
