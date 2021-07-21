from .Plots import *

from .MainPageUI2 import *
#from .Fit2D import Fit2D

from .DataItems import *
from .TauItems import *
from .FrequencyItems import *
from .CompoundItems import *
from .PlotsFit import *
from .Plot3D import *

from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QHeaderView
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
        self.WorkingSpace.setCurrentWidget(self.fit2Dpage)
        self.TModel.setRootIsDecorated(False)
        self.TModel.setAlternatingRowColors(True)
        self.TModel.setHeaderHidden(True)
        
        #self.TModel.setAnimated(True)

        self.TModel.doubleClicked.connect(self.double_click)
        self.TModel.clicked.connect(self.click)
        

        self.TModel.setContextMenuPolicy(Qt.CustomContextMenu)
        self.TModel.customContextMenuRequested.connect(self.showMenu)

    
        # self.TModel.activated.connect(self.resize_model)

        self.treeModel = QStandardItemModel()


        rootNode = self.treeModel.invisibleRootItem()

        # chlor = CompoundItem(self, "Chlor")
        # self.whole.compounds.append(chlor)

        
        rootNode.appendRow(self.whole)
        #rootNode.appendColumn([RootItem(self, '')])
        
        self.TModel.setModel(self.treeModel)
        self.TModel.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        
        
        
        
        self.TModel.expandAll()

        """Workspace implementation"""
        """fitTau"""
        self.plot3d = Plot3D()
        # self.plot3d.setMinimumSize(QtCore.QSize(AppState.screen_size[0]*0.45, AppState.screen_size[1]*0.45))
        self.plot3d.setObjectName("plot3d")
        self.RightPanel.insertWidget(0, self.plot3d)

        self.slice = Slice()
        # self.slice.setMinimumSize(QtCore.QSize(AppState.screen_size[0]*0.45, AppState.screen_size[1]*0.45))
        self.slice.setObjectName('slice')
        self.RightPanel.insertWidget(1, self.slice)

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

        self.check3D_2 = {'Adir': self.checkBox_Adir_2,
        'Ndir': self.checkBox_Ndir_2,
        'B1': self.checkBox_B1_2,
        'B2': self.checkBox_B2_2,
        'B3': self.checkBox_B3_2,
        'CRaman': self.checkBox_Craman_2,
        'NRaman': self.checkBox_Nraman_2,
        'NHRaman': self.checkBox_NHraman_2,
        'Tau0': self.checkBox_Tau0_2,
        'DeltaE': self.checkBox_DeltaE_2
        }

        """fit2dplot"""

        self.plotFr = plotFitChi()
        self.plotChi = plotFitChi1()
        self.plotMain = plotFitChi2()
        
        self.UpperPlots.insertWidget(0, self.plotFr)
        self.UpperPlots.insertWidget(1, self.plotChi)
        self.MainPlot.insertWidget(0, self.plotMain)

        self.editFit2D = { "alpha": self.lineEdit_Alpha,
         "beta": self.lineEdit_Beta,
         "tau" : self.lineEdit_Tau,
         "chiT" : self.lineEdit_ChiT,
         "chiS" : self.lineEdit_ChiS
        }

        self.sliderFit2D = {"alpha": self.horizontalSlider_Alpha,
         "beta": self.horizontalSlider_Beta,
         "tau" : self.horizontalSlider_Tau,
         "chiT" : self.horizontalSlider_ChiT,
         "chiS" : self.horizontalSlider_ChiS
        }

        """dataInspect"""
        self.pointPlotChi1 = PlotChi1()
        self.pointPlotChi2 = PlotChi2()
        self.pointPlotChi = PlotChi()
        self.table = QTableView()

        #self.table.setSelectionMode(QAbstractItemView.SelectionMode.ContiguousSelection)

        # width = self.window.frameGeometry().width() 
        # height = self.window.frameGeometry().height()
        # print(width)
        # print(height)
        # self.table.setMaximumWidth(AppState.screen_size[0]*0.4)
        # self.table.setMaximumHeight(AppState.screen_size[1]*0.5)

        self.inspectPlots.addWidget(self.pointPlotChi1, 0, 0)
        self.inspectPlots.addWidget(self.pointPlotChi2, 1 ,0)
        self.inspectPlots.addWidget(self.pointPlotChi, 0, 1)
        self.inspectPlots.addWidget(self.table, 1, 1)

        self.inspectPlots.setRowStretch(0,1)
        self.inspectPlots.setRowStretch(1,1)
        self.inspectPlots.setColumnStretch(0,1)
        self.inspectPlots.setColumnStretch(1,1)


    def double_click(self, val):
        self.treeModel.itemFromIndex(val).double_click()
    
    def click(self, val):
        self.treeModel.itemFromIndex(val).click()

    def showMenu(self, position):
        index = self.TModel.indexAt(position)
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

    # def resize_model(self):
    #     self.TModel.resizeColumnToContents(0)
















