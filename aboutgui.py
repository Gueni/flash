from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(575, 410)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(170, 10, 231, 191))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap("icons/espLogo.png"))
        self.label_2.setObjectName("label_2")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(80, 230, 221, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(80, 260, 361, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(80, 290, 481, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(80, 320, 481, 16))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(80, 350, 111, 23))
        self.pushButton.setObjectName("pushButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "About "))
        self.label.setText(_translate("MainWindow", "Version : 1.0"))
        urlLink = " <a href=\"http://mdtunisie.com/\"> <font face=rmfamily   color=BLUE> Micro Device Tunisie</font> </a>"
        urlLinkesptool = " <a href=\"https://github.com/espressif/esptool/\"> <font face=rmfamily   color=BLUE> esptool</font> </a>"
        urlLinkgueni = " <a href=\"https://github.com/Gueni/\"> <font face=rmfamily   color=BLUE> Mohamed Gueni</font> </a>"
        # self.label_3.setText(_translate("MainWindow", "Copyright" + urlLink + " © 2019 "))
        self.label_3.setText(_translate("MainWindow",
                                        "This Software uses libraries from the " + urlLinkesptool + "project under the GPLv2 license"))
        self.label_4.setText(_translate("MainWindow", "Author :" + urlLinkgueni))
        self.pushButton.setText(_translate("MainWindow", "License"))
