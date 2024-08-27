
#?---------------------------------------------------------------------------------------------------------------------------
from PyQt5 import QtCore, QtWidgets
import os
from PyQt5.QtCore import QSize  # Import QSize from QtCore
import sys
from PyQt5 import QtWidgets, QtGui
#?---------------------------------------------------------------------------------------------------------------------------
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
widget_names = [
            'pushButton_eraseentireflash', 'pushButton_disconnect', 'pushButton_combine',
            'pushButton_selectall', 'pushButton_loadsetting', 'pushButton_flashAll',
            'pushButton_loadram', 'pushButton_13', 'pushButton_writestatusreg',
            'pushButton_savesetting', 'pushButton_default', 'pushButtonconnect',
            'pushButton_chipid', 'pushButton_dumpmem', 'pushButton_eraseregion',
            'pushButton_flashcombined', 'pushButton_flashfirmware', 'pushButton_generatebinfromelf',
            'pushButton_imageinfo', 'pushButton_logout', 'pushButton_readmem',
            'pushButton_readstatusreg', 'pushButton_verifyflash', 'pushButton_writemem',
            'lineEditreadmemaddr', 'lineEdit_combinedfile', 'lineEdit_offsetcombined',
            'lineEdit_path2', 'lineEdit_path1', 'lineEdit_path3',
            'lineEdit_offset1', 'lineEdit_elffile', 'lineEdit_offset2',
            'lineEdit_offset3', 'lineEdit_verifyoffset', 'lineEdit_writemem2',
            'lineEdit_keypath', 'lineEdit_eraseregion2', 'lineEdit_eraseregion1',
            'lineEdit_dumpmem1', 'lineEdit_dumpmem2', 'lineEdit_writemem1',
            'lineEdit_writemem3', 'comboBox_readstatusreg', 'comboBox_writestatusreg',
            'comboBox_serial', 'pushButton_clearop', 'pushButton_cleardata',
            'pushButton_clearmemo', 'pushButton_readFlash', 'pushButton_Fusedump',
            'pushButton_encrypt', 'lineEdit_readFlash1', 'lineEdit_readFlash2',
            'pushButton_path1', 'pushButton_path2', 'pushButton_path3',
            'pushButton_pathkey', 'pushButton_browsecombined', 'pushButton_elffile',
            'checkBox_1', 'checkBox_2', 'checkBox_3',
            'pushButton_genkey', 'comboBox_serial', 'comboBox_chip',
            'comboBox_flashmode', 'comboBox_flashsize'
        ]
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

class ComboBoxCOMPORT(QtWidgets.QComboBox):
    popupAboutToBeShown = QtCore.pyqtSignal()

    def showPopup(self):
        self.popupAboutToBeShown.emit()
        super(ComboBoxCOMPORT, self).showPopup()

class Ui_MainWindowadvanced(object):

    def setupUi(self, MainWindow):

        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(1080, 720)
       
        self.centralwidget              = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        #!---------------------------------------
        # Create custom title bar
        self.custom_title_bar = QtWidgets.QWidget()
        self.custom_title_bar.setFixedHeight(30)  # Set the height of the title bar
        self.custom_title_bar.setStyleSheet("background-color: #a50658;")  # Title bar background color
        # Create title bar buttons
        self.minimize_button = QtWidgets.QPushButton('-')
        self.close_button = QtWidgets.QPushButton('x')
        # Style buttons
        self.minimize_button.setGeometry(QtCore.QRect(1060, 0, 20, 20))
        self.close_button.setGeometry(QtCore.QRect(1030, 0, 20, 20))
        self.minimize_button.setStyleSheet("background-color: #a50658; color: white; font-weight: bold ;border: none;")
        self.close_button.setStyleSheet("background-color: #a50658; color: white; font-weight: bold; border: none;")
        # Connect buttons to their slots
        self.minimize_button.clicked.connect(self.minimize)
        self.close_button.clicked.connect(self.close)
        # Create a layout for the custom title bar
        title_bar_layout = QtWidgets.QHBoxLayout()
        
        title_bar_layout.addWidget(self.minimize_button)
        title_bar_layout.addWidget(self.close_button)
        title_bar_layout.setContentsMargins(1010, 0, 20, 0)
        # title_bar_layout.setSpacing(0)
        self.custom_title_bar.setLayout(title_bar_layout)

        # Set the custom title bar as the window's title bar
        MainWindow.setMenuWidget(self.custom_title_bar)

        # Handle mouse events for dragging the window
        self.custom_title_bar.mousePressEvent = self.startMove
        self.custom_title_bar.mouseMoveEvent = self.doMove
        #!---------------------------------------
        self.tabWidget                  = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 40, 1000, 650))
        self.tabWidget.setObjectName("tabWidget")
        self.tabbar                     = TabBar(self)
        self.tabWidget.setTabBar(self.tabbar)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.West)
        self.tabWidget.setTabsClosable(False)
        #! tabwidge 1 ------------------------------------------------------------------------------------------------------
        self.info                       = QtWidgets.QWidget()
        self.info.setObjectName("Home")
        
        self.pushButton_disconnect      = QtWidgets.QPushButton(self.info)
        self.pushButton_disconnect.setGeometry(QtCore.QRect((324+112), 430, 140, 25))
        self.pushButton_disconnect.setObjectName("pushButton_disconnect")
        
        self.pushButton_logout          = QtWidgets.QPushButton(self.info)
        self.pushButton_logout.setGeometry(QtCore.QRect(int(488+112), 430, 140, 25))
        
        self.pushButtonconnect          = QtWidgets.QPushButton(self.info)
        self.pushButtonconnect.setGeometry(QtCore.QRect(int(160+112), 430, 140, 25))
        self.pushButtonconnect.setObjectName("pushButtonconnect")
        
        self.comboBox_serial            = ComboBoxCOMPORT(self.info)
        self.comboBox_serial.setGeometry(QtCore.QRect(250+112+10, 330, 365, 22))
        self.comboBox_serial.setObjectName("comboBox_serial")
        
        self.label_8                    = QtWidgets.QLabel(self.info)
        self.label_8.setGeometry(QtCore.QRect(320+112, 250, 451, 21))
        self.label_8.setObjectName("label_8")

        self.label_6                    = QtWidgets.QLabel(self.info)
        self.label_6.setGeometry(QtCore.QRect(160+112, 330, 61, 21))
        self.label_6.setObjectName("label_6")

        self.label_7                    = QtWidgets.QLabel(self.info)
        self.label_7.setGeometry(QtCore.QRect(160+112, 367, 61, 21))
        self.label_7.setObjectName("label_7")
        
        self.comboBox_baud              = QtWidgets.QComboBox(self.info)
        self.comboBox_baud.setGeometry(QtCore.QRect(250+112+10, 367, 365, 22))
        self.comboBox_baud.setObjectName("comboBox_baud")
        
        self.graphicsView               = QtWidgets.QGraphicsView(self.info)
        self.graphicsView.setGeometry(QtCore.QRect(160+112, 20, 456, 231))
        self.graphicsView.setObjectName("graphicsView")
        self.graphicsView.setStyleSheet("border: 0px")
        
        self.tabWidget.addTab(self.info, "")

        #! tabwidge 2 ------------------------------------------------------------------------------------------------------
        self.optab                      = QtWidgets.QWidget()
        self.optab.setObjectName("optab")
        
        self.plainTextEditadvanced      = QtWidgets.QPlainTextEdit(self.optab)
        self.plainTextEditadvanced.setGeometry(QtCore.QRect(510, 10+50, 0, 0))
        self.plainTextEditadvanced.setObjectName("plainTextEditadvanced")
        
        self.pushButtoncollapsexpand    = QtWidgets.QPushButton(self.optab)
        self.pushButtoncollapsexpand.setGeometry(QtCore.QRect(910, 10+50, 12, 500))
        self.pushButtoncollapsexpand.setObjectName("pushButtoncollapsexpand")
        
        self.groupBox                   = QtWidgets.QGroupBox(self.optab)
        self.groupBox.setGeometry(QtCore.QRect(100, 10+50, 381, 100))
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        
        self.pushButton_verifyflash     = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_verifyflash.setGeometry(QtCore.QRect(20, 10, 200, 25))
        self.pushButton_verifyflash.setObjectName("pushButton_verifyflash")
        
        self.lineEdit_verifyoffset      = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_verifyoffset.setGeometry(QtCore.QRect(250, 10, 111, 25))
        self.lineEdit_verifyoffset.setObjectName("lineEditreadmemaddr")
        
        self.pushButton_loadram         = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_loadram.setGeometry(QtCore.QRect(20, 45, 160, 25))
        self.pushButton_loadram.setObjectName("pushButton_loadram")
        
        self.pushButton_chipid          = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_chipid.setGeometry(QtCore.QRect(200, 45, 160, 25))
        self.pushButton_chipid.setObjectName("pushButton_chipid")
        
        self.groupBox_2                 = QtWidgets.QGroupBox(self.optab)
        self.groupBox_2.setGeometry(QtCore.QRect(100, 140+50, 381, 161))
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        
        self.pushButton_imageinfo       = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_imageinfo.setGeometry(QtCore.QRect(200, 100, 161, 25))
        self.pushButton_imageinfo.setObjectName("pushButton_imageinfo")
        
        self.pushButton_flashcombined   = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_flashcombined.setGeometry(QtCore.QRect(20, 20, 161, 25))
        self.pushButton_flashcombined.setObjectName("pushButton_flashcombined")
        
        self.pushButton_13              = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_13.setGeometry(QtCore.QRect(20, 100, 161, 25))
        self.pushButton_13.setObjectName("pushButton_13")
        
        self.pushButton_flashAll        = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_flashAll.setGeometry(QtCore.QRect(200, 20, 161, 25))
        self.pushButton_flashAll.setObjectName("pushButton_flashAll")
        
        self.pushButton_flashfirmware   = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_flashfirmware.setGeometry(QtCore.QRect(20, 60, 161, 25))
        self.pushButton_flashfirmware.setObjectName("pushButton_flashfirmware")
        
        self.pushButton_eraseentireflash = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_eraseentireflash.setGeometry(QtCore.QRect(200, 60, 161, 25))
        self.pushButton_eraseentireflash.setObjectName("pushButton_eraseentireflash")
        
        self.groupBox_3                 = QtWidgets.QGroupBox(self.optab)
        self.groupBox_3.setGeometry(QtCore.QRect(100, 330+50, 381, 121))
        self.groupBox_3.setTitle("")
        self.groupBox_3.setObjectName("groupBox_3")
        
        self.pushButton_clearop         = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_clearop.setGeometry(QtCore.QRect(20, 20, 161, 25))
        self.pushButton_clearop.setObjectName("pushButton_clearop")
        
        self.pushButton_stop            = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton_stop.setGeometry(QtCore.QRect(200, 20, 161, 25))
        self.pushButton_stop.setObjectName("pushButton_stop")
        
        self.progressBar                = QtWidgets.QProgressBar(self.groupBox_3)
        self.progressBar.setGeometry(QtCore.QRect(20, 80, 340, 13))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        
        self.tabWidget.addTab(self.optab, "")

        #! tabwidge 3 ------------------------------------------------------------------------------------------------------
        self.Memo = QtWidgets.QWidget()
        self.Memo.setObjectName("Home")
        
        self.plainTextEditadvancedmem   = QtWidgets.QPlainTextEdit(self.Memo)
        self.plainTextEditadvancedmem.setGeometry(QtCore.QRect(510, 10+50, 0, 0))
        self.plainTextEditadvancedmem.setObjectName("plainTextEditadvanced")
        
        self.pushButtoncollapsexpandm   = QtWidgets.QPushButton(self.Memo)
        self.pushButtoncollapsexpandm.setGeometry(QtCore.QRect(910, 10+50, 12, 500))
        self.pushButtoncollapsexpandm.setObjectName("pushButtoncollapsexpandm")
        
        self.line                       = QtWidgets.QFrame(self.Memo)
        self.line.setGeometry(QtCore.QRect(420, 10, 10, 510))
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        
        self.groupBoxmemo = QtWidgets.QGroupBox(self.Memo)
        self.groupBoxmemo.setGeometry(QtCore.QRect(30, 10, 381, 400))
        self.groupBoxmemo.setTitle("")
        self.groupBoxmemo.setObjectName("groupBox")
        
        self.pushButton_eraseregion = QtWidgets.QPushButton(self.groupBoxmemo)
        self.pushButton_eraseregion.setGeometry(QtCore.QRect(20, 110, 101, 25))
        self.pushButton_eraseregion.setObjectName("pushButton_eraseregion")
        
        self.lineEditreadmemaddr = QtWidgets.QLineEdit(self.groupBoxmemo)
        self.lineEditreadmemaddr.setGeometry(QtCore.QRect(250, 20, 111, 25))
        self.lineEditreadmemaddr.setObjectName("lineEditreadmemaddr")
        
        self.pushButton_readmem = QtWidgets.QPushButton(self.groupBoxmemo)
        self.pushButton_readmem.setGeometry(QtCore.QRect(20, 20, 221, 25))
        self.pushButton_readmem.setObjectName("pushButton_readmem")
        
        self.lineEdit_writemem1 = QtWidgets.QLineEdit(self.groupBoxmemo)
        self.lineEdit_writemem1.setGeometry(QtCore.QRect(132, 70, 72, 25))
        self.lineEdit_writemem1.setObjectName("lineEdit_writemem1")
        
        self.lineEdit_writemem2 = QtWidgets.QLineEdit(self.groupBoxmemo)
        self.lineEdit_writemem2.setGeometry(QtCore.QRect(212, 70, 70, 25))
        self.lineEdit_writemem2.setObjectName("lineEdit_writemem2")
        
        self.lineEdit_writemem3 = QtWidgets.QLineEdit(self.groupBoxmemo)
        self.lineEdit_writemem3.setGeometry(QtCore.QRect(290, 70, 70, 25))
        self.lineEdit_writemem3.setObjectName("lineEdit_writemem3")
        
        self.lineEdit_eraseregion2 = QtWidgets.QLineEdit(self.groupBoxmemo)
        self.lineEdit_eraseregion2.setGeometry(QtCore.QRect(250, 111, 111, 25))
        self.lineEdit_eraseregion2.setObjectName("lineEdit_eraseregion2")
        
        self.lineEdit_eraseregion1 = QtWidgets.QLineEdit(self.groupBoxmemo)
        self.lineEdit_eraseregion1.setGeometry(QtCore.QRect(132, 111, 111, 25))
        self.lineEdit_eraseregion1.setObjectName("lineEdit_eraseregion1")
        
        self.pushButton_writemem = QtWidgets.QPushButton(self.groupBoxmemo)
        self.pushButton_writemem.setGeometry(QtCore.QRect(20, 69, 101, 25))
        self.pushButton_writemem.setObjectName("pushButton_writemem")
        
        self.pushButton_dumpmem = QtWidgets.QPushButton(self.groupBoxmemo)
        self.pushButton_dumpmem.setGeometry(QtCore.QRect(20, 150, 101, 25))
        self.pushButton_dumpmem.setObjectName("pushButton_dumpmem")
        
        self.lineEdit_dumpmem1 = QtWidgets.QLineEdit(self.groupBoxmemo)
        self.lineEdit_dumpmem1.setGeometry(QtCore.QRect(132, 150, 111, 25))
        self.lineEdit_dumpmem1.setObjectName("lineEdit_eraseregion2")
        
        self.lineEdit_dumpmem2 = QtWidgets.QLineEdit(self.groupBoxmemo)
        self.lineEdit_dumpmem2.setGeometry(QtCore.QRect(250, 150, 111, 25))
        self.lineEdit_dumpmem2.setObjectName("lineEdit_eraseregion1")
        
        self.pushButton_readFlash = QtWidgets.QPushButton(self.groupBoxmemo)
        self.pushButton_readFlash.setGeometry(QtCore.QRect(20, 270, 101, 25))
        self.pushButton_readFlash.setObjectName("pushButton_readFlash")
        
        self.pushButton_Fusedump = QtWidgets.QPushButton(self.groupBoxmemo)
        self.pushButton_Fusedump.setGeometry(QtCore.QRect(20, 310, 101, 25))
        self.pushButton_Fusedump.setObjectName("pushButton_Fusedump")
        
        self.pushButton_encrypt = QtWidgets.QPushButton(self.groupBoxmemo)
        self.pushButton_encrypt.setGeometry(QtCore.QRect(132, 310, 101, 25))
        self.pushButton_encrypt.setObjectName("pushButton_encrypt")
        
        self.lineEdit_readFlash1 = QtWidgets.QLineEdit(self.groupBoxmemo)
        self.lineEdit_readFlash1.setGeometry(QtCore.QRect(132, 270, 111, 25))
        self.lineEdit_readFlash1.setObjectName("lineEdit_readFlash1")
        
        self.lineEdit_readFlash2 = QtWidgets.QLineEdit(self.groupBoxmemo)
        self.lineEdit_readFlash2.setGeometry(QtCore.QRect(250, 270, 111, 25))
        self.lineEdit_readFlash2.setObjectName("lineEdit_readFlash2")
        
        self.pushButton_readstatusreg = QtWidgets.QPushButton(self.groupBoxmemo)
        self.pushButton_readstatusreg.setGeometry(QtCore.QRect(20, 190, 160, 25))
        self.pushButton_readstatusreg.setObjectName("pushButton_readstatusreg")
        
        self.comboBox_readstatusreg = QtWidgets.QComboBox(self.groupBoxmemo)
        self.comboBox_readstatusreg.setGeometry(QtCore.QRect(200, 190, 160, 25))
        self.comboBox_readstatusreg.setObjectName("comboBox_flashmode")
        
        self.pushButton_writestatusreg = QtWidgets.QPushButton(self.groupBoxmemo)
        self.pushButton_writestatusreg.setGeometry(QtCore.QRect(20, 230, 160, 25))
        self.pushButton_writestatusreg.setObjectName("pushButton_readstatusreg")
        
        self.comboBox_writestatusreg = QtWidgets.QComboBox(self.groupBoxmemo)
        self.comboBox_writestatusreg.setGeometry(QtCore.QRect(200, 230, 160, 25))
        self.comboBox_writestatusreg.setObjectName("comboBox_flashmode")
        
        self.groupBox_2memo = QtWidgets.QGroupBox(self.Memo)
        self.groupBox_2memo.setGeometry(QtCore.QRect(30, 421, 381, 100))
        self.groupBox_2memo.setTitle("")
        self.groupBox_2memo.setObjectName("groupBox_3")
        
        self.pushButton_clearmemo = QtWidgets.QPushButton(self.groupBox_2memo)
        self.pushButton_clearmemo.setGeometry(QtCore.QRect(20, 20, 161, 25))
        self.pushButton_clearmemo.setObjectName("pushButton_clearop")
        
        self.pushButton_stopmemo = QtWidgets.QPushButton(self.groupBox_2memo)
        self.pushButton_stopmemo.setGeometry(QtCore.QRect(200, 20, 161, 25))
        self.pushButton_stopmemo.setObjectName("pushButton_stop")
        
        self.progressBarmemo = QtWidgets.QProgressBar(self.groupBox_2memo)
        self.progressBarmemo.setGeometry(QtCore.QRect(20, 70, 340, 13))
        self.progressBarmemo.setProperty("value", 24)
        self.progressBarmemo.setObjectName("progressBar")
        
        self.tabWidget.addTab(self.Memo, "")
        
        #! tabwidge 4 ------------------------------------------------------------------------------------------------------
        
        self.datatab = QtWidgets.QWidget()
        self.datatab.setObjectName("datatab")
        
        self.groupBox_data = QtWidgets.QGroupBox(self.datatab)
        self.groupBox_data.setGeometry(QtCore.QRect(40+85, 350+50, 705, 100))
        self.groupBox_data.setTitle("")
        self.groupBox_data.setObjectName("groupBox_data")
        
        self.pushButton_selectall = QtWidgets.QPushButton(self.groupBox_data)
        self.pushButton_selectall.setGeometry(QtCore.QRect(10+15, 30, 120+30, 30))
        self.pushButton_selectall.setObjectName("pushButton_selectall")
        
        self.pushButton_cleardata = QtWidgets.QPushButton(self.groupBox_data)
        self.pushButton_cleardata.setGeometry(QtCore.QRect(150+30+15, 30, 120+30, 30))
        self.pushButton_cleardata.setObjectName("pushButton_cleardata")
        
        self.pushButton_combine = QtWidgets.QPushButton(self.groupBox_data)
        self.pushButton_combine.setGeometry(QtCore.QRect(290+30+30+15, 30, 120+30, 30))
        self.pushButton_combine.setObjectName("pushButton_combine")
        
        self.pushButton_generatebinfromelf = QtWidgets.QPushButton(self.groupBox_data)
        self.pushButton_generatebinfromelf.setGeometry(QtCore.QRect(430+30+60+15, 30, 120+30, 30))
        self.pushButton_generatebinfromelf.setObjectName("pushButton_generatebinfromelf")
        
        # ***************# ***************# ***************# ***************
        self.lineEdit_offset3 = QtWidgets.QLineEdit(self.datatab)
        self.lineEdit_offset3.setGeometry(QtCore.QRect(625+85, 90+50, 101, 20))
        self.lineEdit_offset3.setObjectName("lineEdit_offset3")
        
        self.lineEdit_offset2 = QtWidgets.QLineEdit(self.datatab)
        self.lineEdit_offset2.setGeometry(QtCore.QRect(625+85, 60+50, 101, 20))
        self.lineEdit_offset2.setObjectName("lineEdit_offset2")
        
        self.lineEdit_offset1 = QtWidgets.QLineEdit(self.datatab)
        self.lineEdit_offset1.setGeometry(QtCore.QRect(625+85, 30+50, 101, 20))
        self.lineEdit_offset1.setObjectName("lineEdit_offset1")
        
        self.lineEdit_path1 = QtWidgets.QLineEdit(self.datatab)
        self.lineEdit_path1.setGeometry(QtCore.QRect(80+85, 30+50, 500, 20))
        self.lineEdit_path1.setObjectName("lineEdit_path1")
        
        self.lineEdit_path2 = QtWidgets.QLineEdit(self.datatab)
        self.lineEdit_path2.setGeometry(QtCore.QRect(80+85, 60+50, 500, 20))
        self.lineEdit_path2.setObjectName("lineEdit_path2")
        
        self.lineEdit_path3 = QtWidgets.QLineEdit(self.datatab)
        self.lineEdit_path3.setGeometry(QtCore.QRect(80+85, 90+50, 500, 20))
        self.lineEdit_path3.setObjectName("lineEdit_path3")
        
        self.lineEdit_keypath = QtWidgets.QLineEdit(self.datatab)
        self.lineEdit_keypath.setGeometry(QtCore.QRect(80+85, 180+50, 500, 20))
        self.lineEdit_keypath.setObjectName("lineEdit_keypath")
        
        self.lineEdit_combinedfile = QtWidgets.QLineEdit(self.datatab)
        self.lineEdit_combinedfile.setGeometry(QtCore.QRect(80+85, 120+50, 500, 20))
        self.lineEdit_combinedfile.setObjectName("lineEdit_combinedfile")
        
        self.checkBox_3 = QtWidgets.QCheckBox(self.datatab)
        self.checkBox_3.setGeometry(QtCore.QRect(735+85, 90+50, 31, 21))
        self.checkBox_3.setText("")
        self.checkBox_3.setObjectName("checkBox_3")
        
        self.checkBox_2 = QtWidgets.QCheckBox(self.datatab)
        self.checkBox_2.setGeometry(QtCore.QRect(735+85, 60+50, 31, 21))
        self.checkBox_2.setText("")
        self.checkBox_2.setObjectName("checkBox_2")
        
        self.checkBox_1 = QtWidgets.QCheckBox(self.datatab)
        self.checkBox_1.setGeometry(QtCore.QRect(735+85, 30+50, 31, 21))
        self.checkBox_1.setText("")
        self.checkBox_1.setObjectName("checkBox_1")
        
        self.pushButton_path1 = QtWidgets.QPushButton(self.datatab)
        self.pushButton_path1.setGeometry(QtCore.QRect(40+85, 31+50, 31, 20))
        self.pushButton_path1.setObjectName("pushButton_path1")
        
        self.pushButton_path2 = QtWidgets.QPushButton(self.datatab)
        self.pushButton_path2.setGeometry(QtCore.QRect(40+85, 60+50, 31, 20))
        self.pushButton_path2.setObjectName("pushButton_path2")
        
        self.pushButton_path3 = QtWidgets.QPushButton(self.datatab)
        self.pushButton_path3.setGeometry(QtCore.QRect(40+85, 91+50, 31, 20))
        self.pushButton_path3.setObjectName("pushButton_path3")
        
        self.pushButton_pathkey = QtWidgets.QPushButton(self.datatab)
        self.pushButton_pathkey.setGeometry(QtCore.QRect(40+85, 180+50, 31, 20))
        self.pushButton_pathkey.setObjectName("pushButton_pathkey")
        
        self.lineEdit_elffile = QtWidgets.QLineEdit(self.datatab)
        self.lineEdit_elffile.setGeometry(QtCore.QRect(80+85, 150+50, 500, 20))
        self.lineEdit_elffile.setObjectName("lineEdit_elffile")
        
        self.pushButton_elffile = QtWidgets.QPushButton(self.datatab)
        self.pushButton_elffile.setGeometry(QtCore.QRect(40+85, 150+50, 31, 20))
        self.pushButton_elffile.setObjectName("pushButton_elffile")
        
        self.pushButton_browsecombined = QtWidgets.QPushButton(self.datatab)
        self.pushButton_browsecombined.setGeometry(QtCore.QRect(40+85, 120+50, 31, 20))
        self.pushButton_browsecombined.setObjectName("pushButton_browsecombined")
        
        self.lineEdit_offsetcombined = QtWidgets.QLineEdit(self.datatab)
        self.lineEdit_offsetcombined.setGeometry(QtCore.QRect(625+85, 120+50, 101, 20))
        self.lineEdit_offsetcombined.setObjectName("lineEdit_offsetcombined")
        
        self.pushButton_genkey = QtWidgets.QPushButton(self.datatab)
        self.pushButton_genkey.setGeometry(QtCore.QRect(625+85, 180+50, 101, 22))
        self.pushButton_genkey.setObjectName("pushButton_selectall")
        
        self.tabWidget.addTab(self.datatab, "")
        
        #! tabwidge 5 ------------------------------------------------------------------------------------------------------
        self.fusetab = QtWidgets.QWidget()
        self.fusetab.setObjectName("fusetab")

        self.pushButton_reloadfusetab = QtWidgets.QPushButton(self.fusetab)
        self.pushButton_reloadfusetab.setGeometry(QtCore.QRect(320+85, 200+50, 100, 100))
        self.pushButton_reloadfusetab.setObjectName("pushButton_reloadfusetab")
        # icon_path = resource_path('Theme/icons/sync.png')
        # self.pushButton_reloadfusetab.setStyleSheet(f"background-image: url({icon_path}); border: none;background-color :none")
        # Get the path to the resource file
        icon_path = resource_path('Theme/icons/sync.png')

        # Set the icon directly
        icon = QtGui.QIcon(icon_path)
        self.pushButton_reloadfusetab.setIcon(icon)

        # Optionally, set the icon size
        self.pushButton_reloadfusetab.setIconSize(QSize(100, 100))
        self.pushButton_reloadfusetab.setStyleSheet("background: transparent; border: none;")


        self.btnref = QtWidgets.QPushButton()
        for i in range(32):
            setattr(self, f'btn{i+1}', QtWidgets.QPushButton())
        self.btnexport = QtWidgets.QPushButton()

        self.tabWidget.addTab(self.fusetab, "")

        #! tabwidge 6 ------------------------------------------------------------------------------------------------------
        self.settingtab = QtWidgets.QWidget()
        self.settingtab.setObjectName("settingtab")
        
        self.comboBox_flashmode = QtWidgets.QComboBox(self.settingtab)
        self.comboBox_flashmode.setGeometry(QtCore.QRect(160+50, 200+50, 311, 25))
        self.comboBox_flashmode.setObjectName("comboBox_flashmode")
        
        self.comboBox_flashsize = QtWidgets.QComboBox(self.settingtab)
        self.comboBox_flashsize.setGeometry(QtCore.QRect(160+50, 140+50, 311, 25))
        self.comboBox_flashsize.setObjectName("comboBox_flashsize")
        
        self.label_5 = QtWidgets.QLabel(self.settingtab)
        self.label_5.setGeometry(QtCore.QRect(50+50, 80+50, 71, 21))
        self.label_5.setObjectName("label_5")
        
        self.label_2 = QtWidgets.QLabel(self.settingtab)
        self.label_2.setGeometry(QtCore.QRect(50+50, 120+50, 81, 21))
        self.label_2.setObjectName("label_2")
        
        self.comboBox_chip = QtWidgets.QComboBox(self.settingtab)
        self.comboBox_chip.setGeometry(QtCore.QRect(160+50, 80+50, 311, 25))
        self.comboBox_chip.setObjectName("comboBox_chip")
        
        self.label = QtWidgets.QLabel(self.settingtab)
        self.label.setGeometry(QtCore.QRect(50+50, 160+50, 81, 21))
        self.label.setObjectName("label")
        
        self.pushButton_default = QtWidgets.QPushButton(self.settingtab)
        self.pushButton_default.setGeometry(QtCore.QRect(580+50, 80+50,  160, 25))
        self.pushButton_default.setObjectName("pushButton_default")
        
        self.pushButton_savesetting = QtWidgets.QPushButton(self.settingtab)
        self.pushButton_savesetting.setGeometry(QtCore.QRect(580+50, 140+50, 160, 25))
        self.pushButton_savesetting.setObjectName("pushButton_savesetting")
        
        self.pushButton_loadsetting = QtWidgets.QPushButton(self.settingtab)
        self.pushButton_loadsetting.setGeometry(QtCore.QRect(580+50, 200+50, 160, 25))
        self.pushButton_loadsetting.setObjectName("pushButton_loadsetting")
        
        self.tabWidget.addTab(self.settingtab, "")
       
        #!----------------------------------------------------------------------------------------------------------------
        MainWindow.setCentralWidget(self.centralwidget)
        
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 20, 900, 21))
        self.menubar.setObjectName("menubar")
        
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
       
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        
        self.menuView = QtWidgets.QMenu(self.menubar)
       
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        
        MainWindow.setStatusBar(self.statusbar)

        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
   
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        
        self.menuFile.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionAbout)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        
        self.retranslateUi(MainWindow)
        
        self.tabWidget.setCurrentIndex(0)
        
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        #!----------------------------------------------------------------------------------------------------------------

    def startMove(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.old_pos = event.globalPos()
            self.setCursor(QtCore.Qt.ClosedHandCursor)

    def doMove(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def minimize(self):
        self.showMinimized()

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def close(self):
        self.close()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow",    "flash 2.1"))
        self.menuFile.setTitle(_translate("MainWindow",    "File"))
        self.menuHelp.setTitle(_translate("MainWindow",    "Help"))

        set_text_elements = [
            (self.pushButton_disconnect,     "Disconnect"),
            (self.pushButton_logout,         "Log out"),
            (self.pushButtonconnect,         "Connect"),
            (self.label_6,                   "Serial Port"),
            (self.label_7,                   "Baud Rate"),
            (self.label_8,                   ""),
            (self.pushButton_chipid,         "chip ID"),
            (self.pushButton_reloadfusetab,  ""),
            (self.pushButton_eraseregion,    "Erase Region"),
            (self.pushButton_readmem,        "Read Memory"),
            (self.pushButton_writemem,       "Write Memory"),
            (self.pushButton_dumpmem,        "Dump Memory"),
            (self.pushButton_readFlash,      "Read Flash"),
            (self.pushButton_readstatusreg,  "Read Status Reg"),
            (self.pushButton_imageinfo,      "Image Info"),
            (self.pushButton_verifyflash,    "Verify Flash"),
            (self.pushButton_flashcombined,  "Flash Combined"),
            (self.pushButton_13,             "Flash Bootloader"),
            (self.pushButton_flashfirmware,  "Flash firmware"),
            (self.pushButton_eraseentireflash, "Erase Entire Flash"),
            (self.pushButton_clearop,        "Clear"),
            (self.pushButton_stop,           "Stop"),
            (self.pushButton_selectall,      "Select All"),
            (self.pushButton_browsecombined, "..."),
            (self.pushButton_cleardata,      "Clear"),
            (self.pushButton_combine,        "Combine"),
            (self.pushButton_path1,          "..."),
            (self.pushButton_path2,          "..."),
            (self.pushButton_path3,          "..."),
            (self.pushButton_flashAll,       "Flash All"),
            (self.pushButton_Fusedump,       "efuse dump"),
            (self.pushButton_pathkey,        "..."),
            (self.pushButton_elffile,        "..."),
            (self.pushButton_generatebinfromelf, "Elf to Bin"),
            (self.pushButton_default,        "Default"),
            (self.pushButton_savesetting,    "Save Setting"),
            (self.pushButton_loadsetting,    "Load Setting"),
            (self.pushButton_clearmemo,      "Clear"),
            (self.pushButton_stopmemo,       "Stop"),
            (self.pushButton_writestatusreg, "Write Status Reg"),
            (self.pushButton_encrypt,        "Encrypt Flash"),
            (self.pushButton_loadram,        "Load RAM"),
            (self.pushButton_genkey,         "Generate Key"),
            (self.actionAbout,               "About"),
            (self.actionExit,                "Exit")
        ]

        # Widgets that use setPlaceholderText
        set_placeholder_elements = [
            (self.lineEditreadmemaddr, "0x00000000 "),
            (self.lineEdit_writemem2, "0x00000000"),
            (self.lineEdit_writemem1, "0x00000000 "),
            (self.lineEdit_eraseregion2, "0x00000000"),
            (self.lineEdit_eraseregion1, "0x00000000 "),
            (self.lineEdit_dumpmem1, "0x00000000 "),
            (self.lineEdit_dumpmem2, "00000  "),
            (self.lineEdit_readFlash1, "@ "),
            (self.lineEdit_readFlash2, "size  "),
            (self.lineEdit_offset3, "@"),
            (self.lineEdit_offset1, "@"),
            (self.lineEdit_offset2, "@"),
            (self.lineEdit_offsetcombined, "@"),
            (self.lineEdit_combinedfile, "Combined File"),
            (self.lineEdit_path1, "Firmware File"),
            (self.lineEdit_path2, "Bootloader File"),
            (self.lineEdit_path3, "Partition File"),
            (self.lineEdit_keypath, "Device Master Key Folder Path"),
            (self.lineEdit_elffile, "Browse elf File"),
            (self.lineEdit_writemem3, "0x00000000"),
            (self.lineEdit_verifyoffset, "0x00000000")
        ]
        
        # Tabs that use setTabText
        set_tab_text_elements = [
            (self.tabWidget.indexOf(self.info), ""),
            (self.tabWidget.indexOf(self.Memo), ""),
            (self.tabWidget.indexOf(self.optab), ""),
            (self.tabWidget.indexOf(self.datatab), ""),
            (self.tabWidget.indexOf(self.settingtab), "")
        ]

        # Apply setText
        for widget, text in set_text_elements:
            widget.setText(_translate("MainWindow", text))
        # Apply setPlaceholderText
        for widget, text in set_placeholder_elements:
            widget.setPlaceholderText(_translate("MainWindow", text))
        # Apply setTabText
        for index, text in set_tab_text_elements:
            self.tabWidget.setTabText(index, _translate("MainWindow", text))


class TabBar(QtWidgets.QTabBar):

    def tabSizeHint(self, index):
        s = QtWidgets.QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s

    def paintEvent(self, event):
        painter = QtWidgets.QStylePainter(self)
        opt = QtWidgets.QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QtWidgets.QStyle.CE_TabBarTabShape, opt)
            painter.save()
            s = opt.rect.size()
            s.transpose()
            r = QtCore.QRect(QtCore.QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r
            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QtWidgets.QStyle.CE_TabBarTabLabel, opt)
            painter.restore()
