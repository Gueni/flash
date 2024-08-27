
#?---------------------------------------------------------------------------------------------------------------------------
import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
#?---------------------------------------------------------------------------------------------------------------------------

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores files there
        base_path = sys._MEIPASS
    except AttributeError:
        # Access the path directly if not running as a bundled executable
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(600, 500)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("background-color: #dfd6e0;")  # Slightly dirty white

        
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(200, 130, 250, 66))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap(resource_path("Theme/icons/small.png")))
        self.label_2.setObjectName("label_2")
        
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(100, 270, 400, 21))
        
        font = QtGui.QFont()
        font.setPointSize(11)
        
        self.label.setFont(font)
        self.label.setObjectName("label")
        
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(100, 290, 400, 21))
        
        font = QtGui.QFont()
        font.setPointSize(10)
        
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(100, 330, 400, 21))
        
        font = QtGui.QFont()
        font.setPointSize(10)
        
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(100, 360, 400, 21))
        
        font = QtGui.QFont()
        font.setPointSize(10)
        
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(100, 390, 400, 21))
        self.pushButton.setObjectName("pushButton")
        
        MainWindow.setCentralWidget(self.centralwidget)
        
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        
        MainWindow.setStatusBar(self.statusbar)
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        
        _translate      = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "About "))
        self.label.setText(_translate("MainWindow", "Version : 2.0"))
        urlLinkgueni    = " <a href=\"https://github.com/Gueni/\"> <font face=rmfamily   color=BLUE> Mohamed Gueni</font> </a>"
        self.label_4.setText(_translate("MainWindow", "Author :" + urlLinkgueni))
        self.pushButton.setText(_translate("MainWindow", "License"))
