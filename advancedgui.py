
#?---------------------------------------------------------------------------------------------------------------------------
from PyQt5 import QtCore, QtWidgets
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
#?---------------------------------------------------------------------------------------------------------------------------

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
        
        self.tabWidget                  = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 40, 1000, 650))
        self.tabWidget.setObjectName("tabWidget")
        self.tabbar                     = TabBar(self)
        self.tabWidget.setTabBar(self.tabbar)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.West)
        self.tabWidget.setTabsClosable(False)

        # **************first tabwidget ******************/
        self.info                       = QtWidgets.QWidget()
        self.info.setObjectName("Home")
        
        self.pushButton_disconnect      = QtWidgets.QPushButton(self.info)
        self.pushButton_disconnect.setGeometry(QtCore.QRect((324+112), 430, 131, 41))
        self.pushButton_disconnect.setObjectName("pushButton_disconnect")
        
        self.pushButton_logout          = QtWidgets.QPushButton(self.info)
        self.pushButton_logout.setGeometry(QtCore.QRect(int(488+112), 430, 131, 41))
        self.pushButton_logout.setObjectName("pushButton_logout")
        
        self.pushButtonconnect          = QtWidgets.QPushButton(self.info)
        self.pushButtonconnect.setGeometry(QtCore.QRect(int(160+112), 430, 131, 41))
        self.pushButtonconnect.setObjectName("pushButtonconnect")
        
        self.comboBox_serial            = ComboBoxCOMPORT(self.info)
        self.comboBox_serial.setGeometry(QtCore.QRect(250+112, 330, 365, 22))
        self.comboBox_serial.setObjectName("comboBox_serial")
        
        self.label_7                    = QtWidgets.QLabel(self.info)
        self.label_7.setGeometry(QtCore.QRect(162+112, 367, 61, 21))
        self.label_7.setObjectName("label_7")
        
        self.comboBox_baud              = QtWidgets.QComboBox(self.info)
        self.comboBox_baud.setGeometry(QtCore.QRect(250+112, 367, 365, 22))
        self.comboBox_baud.setObjectName("comboBox_baud")
        
        self.label_6                    = QtWidgets.QLabel(self.info)
        self.label_6.setGeometry(QtCore.QRect(160+112, 330, 61, 21))
        self.label_6.setObjectName("label_6")
        
        self.label_8                    = QtWidgets.QLabel(self.info)
        self.label_8.setGeometry(QtCore.QRect(320+112, 250, 451, 21))
        self.label_8.setObjectName("label_8")
        
        self.graphicsView               = QtWidgets.QGraphicsView(self.info)
        self.graphicsView.setGeometry(QtCore.QRect(160+112, 20, 456, 231))
        self.graphicsView.setObjectName("graphicsView")
        self.graphicsView.setStyleSheet("border: 0px")
        
        self.tabWidget.addTab(self.info, "")

        # ******************second tab widget***********************
        self.optab                      = QtWidgets.QWidget()
        self.optab.setObjectName("optab")
        
        self.plainTextEditadvanced      = QtWidgets.QPlainTextEdit(self.optab)
        self.plainTextEditadvanced.setGeometry(QtCore.QRect(425, 10, 371, 511))
        self.plainTextEditadvanced.setObjectName("plainTextEditadvanced")
        
        self.pushButtoncollapsexpand    = QtWidgets.QPushButton(self.optab)
        self.pushButtoncollapsexpand.setGeometry(QtCore.QRect(797, 10, 12, 511))
        self.pushButtoncollapsexpand.setObjectName("pushButtoncollapsexpand")
        
        self.groupBox                   = QtWidgets.QGroupBox(self.optab)
        self.groupBox.setGeometry(QtCore.QRect(30, 10, 381, 100))
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
        self.groupBox_2.setGeometry(QtCore.QRect(30, 140, 381, 161))
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
        self.groupBox_3.setGeometry(QtCore.QRect(30, 330, 381, 121))
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

        # ********** third tabwidget*******************************
        self.Memo = QtWidgets.QWidget()
        self.Memo.setObjectName("Home")
        
        self.plainTextEditadvancedmem   = QtWidgets.QPlainTextEdit(self.Memo)
        self.plainTextEditadvancedmem.setGeometry(QtCore.QRect(425, 10, 371, 511))
        self.plainTextEditadvancedmem.setObjectName("plainTextEditadvanced")
        
        self.pushButtoncollapsexpandm   = QtWidgets.QPushButton(self.Memo)
        self.pushButtoncollapsexpandm.setGeometry(QtCore.QRect(797, 10, 12, 511))
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
        
        # ****************fourth tabwidget******************************
        
        self.datatab = QtWidgets.QWidget()
        self.datatab.setObjectName("datatab")
        
        self.groupBox_data = QtWidgets.QGroupBox(self.datatab)
        self.groupBox_data.setGeometry(QtCore.QRect(40, 350, 705, 100))
        self.groupBox_data.setTitle("")
        self.groupBox_data.setObjectName("groupBox_data")
        
        self.pushButton_selectall = QtWidgets.QPushButton(self.groupBox_data)
        self.pushButton_selectall.setGeometry(QtCore.QRect(10, 30, 120, 40))
        self.pushButton_selectall.setObjectName("pushButton_selectall")
        
        self.pushButton_cleardata = QtWidgets.QPushButton(self.groupBox_data)
        self.pushButton_cleardata.setGeometry(QtCore.QRect(150, 30, 120, 40))
        self.pushButton_cleardata.setObjectName("pushButton_cleardata")
        
        self.pushButton_combine = QtWidgets.QPushButton(self.groupBox_data)
        self.pushButton_combine.setGeometry(QtCore.QRect(290, 30, 120, 40))
        self.pushButton_combine.setObjectName("pushButton_combine")
        
        self.pushButton_generatebinfromelf = QtWidgets.QPushButton(self.groupBox_data)
        self.pushButton_generatebinfromelf.setGeometry(QtCore.QRect(430, 30, 120, 40))
        self.pushButton_generatebinfromelf.setObjectName("pushButton_generatebinfromelf")
        
        self.pushButton_zipfiles = QtWidgets.QPushButton(self.groupBox_data)
        self.pushButton_zipfiles.setGeometry(QtCore.QRect(570, 30, 120, 40))
        self.pushButton_zipfiles.setObjectName("pushButton_zipfiles")
        
        self.lineEdit_offset3 = QtWidgets.QLineEdit(self.datatab)
        self.lineEdit_offset3.setGeometry(QtCore.QRect(625, 90, 101, 20))
        self.lineEdit_offset3.setObjectName("lineEdit_offset3")
        
        self.lineEdit_offset2 = QtWidgets.QLineEdit(self.datatab)
        self.lineEdit_offset2.setGeometry(QtCore.QRect(625, 60, 101, 20))
        self.lineEdit_offset2.setObjectName("lineEdit_offset2")
        
        self.lineEdit_offset1 = QtWidgets.QLineEdit(self.datatab)
        self.lineEdit_offset1.setGeometry(QtCore.QRect(625, 30, 101, 20))
        self.lineEdit_offset1.setObjectName("lineEdit_offset1")
        
        self.lineEdit_path1 = QtWidgets.QLineEdit(self.datatab)
        self.lineEdit_path1.setGeometry(QtCore.QRect(80, 30, 500, 20))
        self.lineEdit_path1.setObjectName("lineEdit_path1")
        
        self.lineEdit_path2 = QtWidgets.QLineEdit(self.datatab)
        self.lineEdit_path2.setGeometry(QtCore.QRect(80, 60, 500, 20))
        self.lineEdit_path2.setObjectName("lineEdit_path2")
        
        self.lineEdit_path3 = QtWidgets.QLineEdit(self.datatab)
        self.lineEdit_path3.setGeometry(QtCore.QRect(80, 90, 500, 20))
        self.lineEdit_path3.setObjectName("lineEdit_path3")
        
        self.lineEdit_keypath = QtWidgets.QLineEdit(self.datatab)
        self.lineEdit_keypath.setGeometry(QtCore.QRect(80, 180, 500, 20))
        self.lineEdit_keypath.setObjectName("lineEdit_keypath")
        
        self.lineEdit_combinedfile = QtWidgets.QLineEdit(self.datatab)
        self.lineEdit_combinedfile.setGeometry(QtCore.QRect(80, 120, 500, 20))
        self.lineEdit_combinedfile.setObjectName("lineEdit_combinedfile")
        
        self.checkBox_3 = QtWidgets.QCheckBox(self.datatab)
        self.checkBox_3.setGeometry(QtCore.QRect(735, 90, 31, 21))
        self.checkBox_3.setText("")
        self.checkBox_3.setObjectName("checkBox_3")
        
        self.checkBox_2 = QtWidgets.QCheckBox(self.datatab)
        self.checkBox_2.setGeometry(QtCore.QRect(735, 60, 31, 21))
        self.checkBox_2.setText("")
        self.checkBox_2.setObjectName("checkBox_2")
        
        self.checkBox_1 = QtWidgets.QCheckBox(self.datatab)
        self.checkBox_1.setGeometry(QtCore.QRect(735, 30, 31, 21))
        self.checkBox_1.setText("")
        self.checkBox_1.setObjectName("checkBox_1")
        
        self.pushButton_path1 = QtWidgets.QPushButton(self.datatab)
        self.pushButton_path1.setGeometry(QtCore.QRect(40, 31, 31, 20))
        self.pushButton_path1.setObjectName("pushButton_path1")
        
        self.pushButton_path2 = QtWidgets.QPushButton(self.datatab)
        self.pushButton_path2.setGeometry(QtCore.QRect(40, 60, 31, 20))
        self.pushButton_path2.setObjectName("pushButton_path2")
        
        self.pushButton_path3 = QtWidgets.QPushButton(self.datatab)
        self.pushButton_path3.setGeometry(QtCore.QRect(40, 91, 31, 20))
        self.pushButton_path3.setObjectName("pushButton_path3")
        
        self.pushButton_pathkey = QtWidgets.QPushButton(self.datatab)
        self.pushButton_pathkey.setGeometry(QtCore.QRect(40, 180, 31, 20))
        self.pushButton_pathkey.setObjectName("pushButton_pathkey")
        
        self.lineEdit_elffile = QtWidgets.QLineEdit(self.datatab)
        self.lineEdit_elffile.setGeometry(QtCore.QRect(80, 150, 500, 20))
        self.lineEdit_elffile.setObjectName("lineEdit_elffile")
        
        self.pushButton_elffile = QtWidgets.QPushButton(self.datatab)
        self.pushButton_elffile.setGeometry(QtCore.QRect(40, 150, 31, 20))
        self.pushButton_elffile.setObjectName("pushButton_elffile")
        
        self.pushButton_browsecombined = QtWidgets.QPushButton(self.datatab)
        self.pushButton_browsecombined.setGeometry(QtCore.QRect(40, 120, 31, 20))
        self.pushButton_browsecombined.setObjectName("pushButton_browsecombined")
        
        self.lineEdit_offsetcombined = QtWidgets.QLineEdit(self.datatab)
        self.lineEdit_offsetcombined.setGeometry(QtCore.QRect(625, 120, 101, 20))
        self.lineEdit_offsetcombined.setObjectName("lineEdit_offsetcombined")
        
        self.pushButton_genkey = QtWidgets.QPushButton(self.datatab)
        self.pushButton_genkey.setGeometry(QtCore.QRect(625, 180, 101, 22))
        self.pushButton_genkey.setObjectName("pushButton_selectall")
        
        self.tabWidget.addTab(self.datatab, "")
        
        # ********************fifth tabwidget**********************************
        self.fusetab = QtWidgets.QWidget()
        self.fusetab.setObjectName("fusetab")

        self.pushButton_reloadfusetab = QtWidgets.QPushButton(self.fusetab)
        self.pushButton_reloadfusetab.setGeometry(QtCore.QRect(320+70, 200+50, 128, 128))
        self.pushButton_reloadfusetab.setObjectName("pushButton_reloadfusetab")
        self.pushButton_reloadfusetab.setStyleSheet("background-image: url('Theme/icons/sync.png'); border: none;background-color :none")

        self.btnref = QtWidgets.QPushButton()
        for i in range(32):
            setattr(self, f'btn{i+1}', QtWidgets.QPushButton())
        self.btnexport = QtWidgets.QPushButton()

        self.tabWidget.addTab(self.fusetab, "")

        # ***************sixth tabwidget********************************
        self.settingtab = QtWidgets.QWidget()
        self.settingtab.setObjectName("settingtab")
        
        self.comboBox_flashmode = QtWidgets.QComboBox(self.settingtab)
        self.comboBox_flashmode.setGeometry(QtCore.QRect(160+50, 160+50, 311, 22))
        self.comboBox_flashmode.setObjectName("comboBox_flashmode")
        
        self.comboBox_flashsize = QtWidgets.QComboBox(self.settingtab)
        self.comboBox_flashsize.setGeometry(QtCore.QRect(160+50, 120+50, 311, 22))
        self.comboBox_flashsize.setObjectName("comboBox_flashsize")
        
        self.label_5 = QtWidgets.QLabel(self.settingtab)
        self.label_5.setGeometry(QtCore.QRect(50+50, 80+50, 71, 21))
        self.label_5.setObjectName("label_5")
        
        self.label_2 = QtWidgets.QLabel(self.settingtab)
        self.label_2.setGeometry(QtCore.QRect(50+50, 120+50, 81, 21))
        self.label_2.setObjectName("label_2")
        
        self.comboBox_chip = QtWidgets.QComboBox(self.settingtab)
        self.comboBox_chip.setGeometry(QtCore.QRect(160+50, 80+50, 311, 22))
        self.comboBox_chip.setObjectName("comboBox_chip")
        
        self.label = QtWidgets.QLabel(self.settingtab)
        self.label.setGeometry(QtCore.QRect(50+50, 160+50, 81, 21))
        self.label.setObjectName("label")
        
        self.pushButton_default = QtWidgets.QPushButton(self.settingtab)
        self.pushButton_default.setGeometry(QtCore.QRect(580+50, 80+50, 131, 41))
        self.pushButton_default.setObjectName("pushButton_default")
        
        self.pushButton_savesetting = QtWidgets.QPushButton(self.settingtab)
        self.pushButton_savesetting.setGeometry(QtCore.QRect(580+50, 140+50, 131, 41))
        self.pushButton_savesetting.setObjectName("pushButton_savesetting")
        
        self.pushButton_loadsetting = QtWidgets.QPushButton(self.settingtab)
        self.pushButton_loadsetting.setGeometry(QtCore.QRect(580+50, 200+50, 131, 41))
        self.pushButton_loadsetting.setObjectName("pushButton_loadsetting")
        
        self.tabWidget.addTab(self.settingtab, "")
       
        # ***************************************************************
        MainWindow.setCentralWidget(self.centralwidget)
        
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 900, 21))
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

       
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow",    "Flash 2.0"))
        self.menuFile.setTitle(_translate("MainWindow",    "File"))
        self.menuHelp.setTitle(_translate("MainWindow",    "Help"))

        set_text_elements = [
            (self.pushButton_disconnect,     "Disconnect"),
            (self.pushButton_logout,         "Log out"),
            (self.pushButtonconnect,         "Connect"),
            (self.label_6,                   "Serial Port"),
            (self.label_8,                   ""),
            (self.pushButton_chipid,         "chip ID"),
            (self.pushButton_zipfiles,       "Package"),
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
