
from PyQt5 import QtCore, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setStyleSheet(open("qssthemes/Dark/darkstyle.qss", "r").read())
        Dialog.setFixedSize(378, 335)
        self.lineEditcurrentpass = QtWidgets.QLineEdit(Dialog)
        self.lineEditcurrentpass.setGeometry(QtCore.QRect(50, 60, 281, 31))
        self.lineEditcurrentpass.setObjectName("lineEditcurrentpass")
        self.lineEditnewpass = QtWidgets.QLineEdit(Dialog)
        self.lineEditnewpass.setGeometry(QtCore.QRect(50, 120, 281, 31))
        self.lineEditnewpass.setObjectName("lineEditnewpass")
        self.lineEdit_confirmpass = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_confirmpass.setGeometry(QtCore.QRect(50, 180, 281, 31))
        self.lineEdit_confirmpass.setObjectName("lineEdit_confirmpass")
        self.statuslabel = QtWidgets.QLabel(Dialog)
        self.statuslabel.setGeometry(QtCore.QRect(50, 220, 281, 21))
        self.statuslabel.setText("")
        self.statuslabel.setObjectName("statuslabel")
        self.pushButtonchangepass = QtWidgets.QPushButton(Dialog)
        self.pushButtonchangepass.setGeometry(QtCore.QRect(50, 250, 121, 41))
        self.pushButtonchangepass.setObjectName("pushButtonchangepass")
        self.pushButtoncancelpass = QtWidgets.QPushButton(Dialog)
        self.pushButtoncancelpass.setGeometry(QtCore.QRect(210, 250, 121, 41))
        self.pushButtoncancelpass.setObjectName("pushButtoncancelpass")
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Change Password"))
        self.pushButtonchangepass.setText(_translate("Dialog", "Change"))
        self.pushButtoncancelpass.setText(_translate("Dialog", "Cancel"))
        self.lineEditcurrentpass.setPlaceholderText(_translate("Dialog", "Current Password"))
        self.lineEditnewpass.setPlaceholderText(_translate("Dialog", "New Password"))
        self.lineEdit_confirmpass.setPlaceholderText(_translate("Dialog", "Confirm Password"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())