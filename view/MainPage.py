from .Plots import *

from .MainPageUI2 import *
from .MainPageUI3 import *
#from .Fit2D import Fit2D

from .DataItems import *
from .TauItems import *
from .FrequencyItems import *
from .CompoundItems import *
from .PlotsFit import *
from .Plot3D import *

from PyQt5.QtGui import QStandardItemModel
from model.dataFrameModel import pandasModel
import sys
import os

import pandas as pd
import numpy as np


class MainPage(Ui_MainWindow):

    def __init__ (self, window):
        super().__init__()
        self.setupUi(window)
        self.whole = RootItem(self, 'Main')

        
        self.window = window
        #self.window.showMaximized()

        self.plot3d = Plot3D()
        self.plot3d.setMinimumSize(QtCore.QSize(AppState.screen_size[0]*0.4, 16777215))
        self.plot3d.setObjectName("plot3d")
        self.slider3D = {'Adir': self.horizontalSlider_Adir,
        'Ndir': self.horizontalSlider_Ndir,
        'B1': self.horizontalSlider_B1,
        'B2': self.horizontalSlider_B2,
        'B3': self.horizontalSlider_B3,
        'CRaman': self.horizontalSlider_Craman,
        'NRaman': self.horizontalSlider_Nraman,
        'NHRaman': self.horizontalSlider_NHraman,
        'Tau0': self.horizontalSlider_Tau0,
        'DeltaE': self.horizontalSlider_DeltaE
        }

        self.edit3D = {'Adir': self.lineEdit_Adir,
        'Ndir': self.lineEdit_Ndir,
        'B1': self.lineEdit_B1,
        'B2': self.lineEdit_B2,
        'B3': self.lineEdit_B3,
        'CRaman': self.lineEdit_Craman,
        'NRaman': self.lineEdit_Nraman,
        'NHRaman': self.lineEdit_NHraman,
        'Tau0': self.lineEdit_Tau0,
        'DeltaE': self.lineEdit_DeltaE
        }

        self.check3D = {'Adir': self.checkBox_Adir,
        'Ndir': self.checkBox_Ndir,
        'B1': self.checkBox_B1,
        'B2': self.checkBox_B2,
        'B3': self.checkBox_B3,
        'CRaman': self.checkBox_Craman,
        'NRaman': self.checkBox_Nraman,
        'NHRaman': self.checkBox_NHraman,
        'Tau0': self.checkBox_Tau0,
        'DeltaE': self.checkBox_DeltaE
        }


        self.RightPanel.insertWidget(0, self.plot3d)
        self.WorkingSpace.setCurrentWidget(self.fit2Dpage)
        self.Model.setRootIsDecorated(False)
        self.Model.setAlternatingRowColors(True)
        self.Model.setHeaderHidden(True)
        

        self.Model.doubleClicked.connect(self.getValue)
        

        self.Model.setContextMenuPolicy(Qt.CustomContextMenu)
        self.Model.customContextMenuRequested.connect(self.showMenu)

        self.treeModel = QStandardItemModel()


        rootNode = self.treeModel.invisibleRootItem()

        chlor = CompoundItem(self, "Chlor")
        self.whole.compounds.append(chlor)

        
        rootNode.appendRow(self.whole)

        self.Model.setModel(self.treeModel)
        self.Model.expandAll()

        """Workspace implementation"""
        
        """fit2dplot"""
        self.plotFr = plotFitChi()
        self.plotChi = plotFitChi2()
        self.plotMain = plotFitChi1()
        
        self.UpperPlots.insertWidget(0, self.plotFr)
        self.UpperPlots.insertWidget(1, self.plotChi)
        self.MainPlot.insertWidget(0, self.plotMain)

        """dataInspect"""
        self.pointPlotChi1 = PlotChi1()
        self.pointPlotChi2 = PlotChi2()
        self.pointPlotChi = PlotChi()
        self.table = QTableView()
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ContiguousSelection)
        # width = self.window.frameGeometry().width() 
        # height = self.window.frameGeometry().height()
        # print(width)
        # print(height)
        self.table.setMaximumWidth(AppState.screen_size[0]*0.4)
        self.table.setMaximumHeight(AppState.screen_size[1]*0.5)

        self.inspectPlots.addWidget(self.pointPlotChi1, 0, 0)
        self.inspectPlots.addWidget(self.pointPlotChi2, 1 ,0)
        self.inspectPlots.addWidget(self.pointPlotChi, 0, 1)
        self.inspectPlots.addWidget(self.table, 1, 1)

        
        


    def getValue(self, val):
        self.treeModel.itemFromIndex(val).action()

    def showMenu(self, position):
        index = self.Model.indexAt(position)
        self.treeModel.itemFromIndex(index).showMenu(position)

    def nextWidget(self):
        self.WorkingSpace.setCurrentIndex((self.WorkingSpace.currentIndex() + 1) % 3)


    def previousWidget(self):
        self.WorkingSpace.setCurrentIndex((self.WorkingSpace.currentIndex() - 1) % 3)
    

    def refreshInspect(self):
        self.pointPlotChi1.refresh()
        self.pointPlotChi2.refresh()
        self.pointPlotChi.refresh()

        self.table.viewport().update()

    def refreshFitFr(self):
        self.plotFr.refresh()
        self.plotChi.refresh()
        self.plotMain.refresh()
















