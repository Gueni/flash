import os
import os.path
import sqlite3
import sys
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QMessageBox, QLineEdit
import changepasswordgui
import loghandel
SETTINGS_style = 'style'


class passhandler(QtWidgets.QMainWindow, changepasswordgui.Ui_Dialog):

    def __init__(self, parent=None):
        super(passhandler, self).__init__(parent)
        if getattr(sys, 'frozen', False):
            self.frozen = 'ever so'
            self.bundle_dir = sys._MEIPASS
        else:
            self.bundle_dir = os.path.dirname(os.path.abspath(__file__))
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(self.bundle_dir + '/icons/espLogo.png'))
        self.setStyleSheet(open("qssthemes/Dark/darkstyle.qss", "r").read())
        self.pushButtoncancelpass.clicked.connect(self.cancel)
        self.pushButtonchangepass.clicked.connect(self.onchangeclicked)
        self.lineEditcurrentpass.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        self.lineEditnewpass.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        self.lineEdit_confirmpass.setEchoMode(QLineEdit.PasswordEchoOnEdit)
        self.settingstyle = QSettings("settingsstyle.ini", QSettings.IniFormat)
        self.setStyleSheet(self.styleSheet())
        self.setStyleSheet(open(self.settingstyle.value(SETTINGS_style, type=str), "r").read())

    def cancel(self):
        self.loginwin = loghandel.Loghandler()
        self.close()
        self.loginwin.show()

    def onchangeclicked(self):
        global row
        conn = sqlite3.connect('Userdatabase.db')
        c = conn.cursor()
        try:
            c.execute('SELECT * FROM USERTABLE ')
            data = c.fetchall()
            for row in data:
                conn.commit()
        except Exception:
            QMessageBox.warning(QMessageBox(), 'Error', 'Could not connect to the database.')
        if len(self.lineEditcurrentpass.text()) >= 8 or len(self.lineEditnewpass.text()) >= 8 or len(self.lineEdit_confirmpass.text()) >= 8:
            if self.lineEditcurrentpass.text() == row[1]:
                if self.lineEditnewpass.text() == self.lineEdit_confirmpass.text():
                    c.execute("UPDATE USERTABLE SET pass=? WHERE id=?", (self.lineEdit_confirmpass.text(), 0))
                    conn.commit()
                    c.close()
                    conn.close()
                    self.cancel()
                else:
                    self.statuslabel.setText("Please Enter The Same Password")
                    color = "#F8BBD0"
                    self.lineEdit_confirmpass.setStyleSheet("QLineEdit {{ background-color: {} }}".format(color))
                    self.lineEditnewpass.setStyleSheet("QLineEdit {{ background-color: {} }}".format(color))
            else:
                self.statuslabel.setText("Current Password Doesn't Match")
                color = "#F8BBD0"
                self.lineEditcurrentpass.setStyleSheet("QLineEdit {{ background-color: {} }}".format(color))
        else:
            color = "#F8BBD0"
            self.lineEditcurrentpass.setStyleSheet("QLineEdit {{ background-color: {} }}".format(color))
            self.lineEditnewpass.setStyleSheet("QLineEdit {{ background-color: {} }}".format(color))
            self.lineEdit_confirmpass.setStyleSheet("QLineEdit {{ background-color: {} }}".format(color))
            self.statuslabel.setText("Password Should be at least 8 characters long")
