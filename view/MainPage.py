from .Plots import *

from .MainPageUI2 import *
from .MainPageUI3 import *
#from .Fit2D import Fit2D

from .DataItems import *
from .TauItems import *
from .FrequencyItems import *
from .CompoundItems import *

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

        button = QPushButton("Whatever")
        button.clicked.connect(lambda x:self.WorkingSpace.setCurrentWidget(self.fit2Dpage))
        self.LeftPanel.insertWidget(0, button )

        self.RightPanel.insertWidget(0, Plot3D())
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
        width = self.window.frameGeometry().width() 
        height = self.window.frameGeometry().height()
        self.table.setMaximumHeight(height*0.75)
        self.table.setMaximumWidth(width*0.75)

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
        print(self.WorkingSpace.currentIndex())

    def previousWidget(self):
        self.WorkingSpace.setCurrentIndex((self.WorkingSpace.currentIndex() - 1) % 3)
        print(self.WorkingSpace.currentIndex())
    

    def refreshInspect(self):
        self.pointPlotChi1.refresh()
        self.pointPlotChi2.refresh()
        self.pointPlotChi.refresh()

        self.table.viewport().update()

    def refreshFitFr(self):
        self.plotFr.refresh()
        self.plotChi.refresh()
        self.plotMain.refresh()















