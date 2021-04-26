# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'view/MainPage3.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow3(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920, 1080)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(2, 2))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setGeometry(QtCore.QRect(10, 10, 1851, 1011))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.Model = QtWidgets.QTreeView(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Model.sizePolicy().hasHeightForWidth())
        self.Model.setSizePolicy(sizePolicy)
        self.Model.setMinimumSize(QtCore.QSize(400, 0))
        self.Model.setMaximumSize(QtCore.QSize(400, 16777215))
        self.Model.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.Model.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.Model.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.Model.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.Model.setTextElideMode(QtCore.Qt.ElideNone)
        self.Model.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerItem)
        self.Model.setAutoExpandDelay(-1)
        self.Model.setIndentation(10)
        self.Model.setSortingEnabled(False)
        self.Model.setAllColumnsShowFocus(False)
        self.Model.setWordWrap(False)
        self.Model.setHeaderHidden(True)
        self.Model.setObjectName("Model")
        self.Model.header().setVisible(False)
        self.Model.header().setDefaultSectionSize(250)
        self.Model.header().setMinimumSectionSize(50)
        self.Model.header().setStretchLastSection(True)
        self.WorkingSpace = QtWidgets.QStackedWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.WorkingSpace.sizePolicy().hasHeightForWidth())
        self.WorkingSpace.setSizePolicy(sizePolicy)
        self.WorkingSpace.setObjectName("WorkingSpace")
        self.fit2Dpage = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.fit2Dpage.sizePolicy().hasHeightForWidth())
        self.fit2Dpage.setSizePolicy(sizePolicy)
        self.fit2Dpage.setObjectName("fit2Dpage")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.fit2Dpage)
        self.verticalLayout.setObjectName("verticalLayout")
        self.UpperPlots = QtWidgets.QHBoxLayout()
        self.UpperPlots.setObjectName("UpperPlots")
        self.verticalLayout.addLayout(self.UpperPlots)
        spacerItem = QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem)
        self.MainPlot = QtWidgets.QHBoxLayout()
        self.MainPlot.setObjectName("MainPlot")
        self.verticalLayout.addLayout(self.MainPlot)
        spacerItem1 = QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem1)
        self.BottomPanel = QtWidgets.QHBoxLayout()
        self.BottomPanel.setObjectName("BottomPanel")
        self.verticalLayout.addLayout(self.BottomPanel)
        self.WorkingSpace.addWidget(self.fit2Dpage)
        self.fit3Dpage = QtWidgets.QWidget()
        self.fit3Dpage.setObjectName("fit3Dpage")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.fit3Dpage)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.PanelContainer = QtWidgets.QHBoxLayout()
        self.PanelContainer.setObjectName("PanelContainer")
        self.LeftPanel = QtWidgets.QVBoxLayout()
        self.LeftPanel.setObjectName("LeftPanel")
        self.PanelContainer.addLayout(self.LeftPanel)
        self.RightPanel = QtWidgets.QVBoxLayout()
        self.RightPanel.setObjectName("RightPanel")
        self.PanelContainer.addLayout(self.RightPanel)
        self.horizontalLayout_5.addLayout(self.PanelContainer)
        self.WorkingSpace.addWidget(self.fit3Dpage)
        self.dataInspect = QtWidgets.QWidget()
        self.dataInspect.setObjectName("dataInspect")
        self.WorkingSpace.addWidget(self.dataInspect)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1920, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuSettings = QtWidgets.QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionLoad = QtWidgets.QAction(MainWindow)
        self.actionLoad.setObjectName("actionLoad")
        self.actionImport = QtWidgets.QAction(MainWindow)
        self.actionImport.setObjectName("actionImport")
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionLoad)
        self.menuFile.addAction(self.actionImport)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())

        self.retranslateUi(MainWindow)
        self.WorkingSpace.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuSettings.setTitle(_translate("MainWindow", "Settings"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionLoad.setText(_translate("MainWindow", "Load"))
        self.actionImport.setText(_translate("MainWindow", "Import"))
