"""
    The relACs is a analysis tool for magnetic data for SMM systems using
    various models for ac magnetic characteristics and the further reliable
    determination of diverse relaxation processes.

    Copyright (C) 2021  Wiktor Zychowicz & Mikolaj Zychowicz

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
""" 

from .Plots import *

from .MainPageUI2 import *
#from .Fit2D import Fit2D

from .DataItems import *
from .TauItems import *
from .FrequencyItems import *
from .CompoundItems import *
from .PlotsFit import *
from .Plot3D import *

from PyQt5.QtGui import QStandardItemModel, QIntValidator
from PyQt5.QtWidgets import QHeaderView, QTableView, QLabel

from webbrowser import open as wb_open

class SvgImageLabel(QLabel):
    """A TextEdit widget derived from QTextEdit and implementing its
       own paintEvent"""



class MainPage(Ui_MainWindow):

    def __init__ (self, window):
        super().__init__()
        self.setupUi(window)
        self.whole = RootItem(self, 'relACs')
        
        self.window = window
        self.window.setWindowTitle("relACs")
        """Main Page implementation"""
        self.WorkingSpace.setCurrentWidget(self.homePage)
        self.LeftTextTableWidget.item(7,1).setForeground(QBrush(QColor(0, 0, 255)))
        self.LeftTextTableWidget.itemClicked.connect(self.open_link)

        """Tree implementation"""
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

        self.comboBox_slice.currentIndexChanged.connect(self.slice_change_const)
        self.slider3D = {'Adir': self.horizontalSlider_Adir,
        'Ndir': self.horizontalSlider_Ndir,
        'B1': self.horizontalSlider_B1,
        'B2': self.horizontalSlider_B2,
        'B3': self.horizontalSlider_B3,
        'CRaman': self.horizontalSlider_Craman,
        'NRaman': self.horizontalSlider_Nraman,
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

        self.checkFit2D = { "alpha": self.checkBox_Alpha,
         "beta": self.checkBox_Beta,
         "tau" : self.checkBox_Tau,
         "chiT" : self.checkBox_ChiT,
         "chiS" : self.checkBox_ChiS
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

        self.inspectPlots.addWidget(self.pointPlotChi1, 0, 1)
        self.inspectPlots.addWidget(self.pointPlotChi2, 0 ,0)
        self.inspectPlots.addWidget(self.pointPlotChi, 1, 0)
        self.inspectPlots.addWidget(self.table, 1, 1)

        self.inspectPlots.setRowStretch(0,1)
        self.inspectPlots.setRowStretch(1,1)
        self.inspectPlots.setColumnStretch(0,1)
        self.inspectPlots.setColumnStretch(1,1)


        self.menuSettings.addAction("Default Settings", self.edit_default_settings)
        self.WorkingSpace.setCurrentWidget(self.homePage)

    def open_link(self, item):
        if item.text()[:3] == 'www':
            wb_open(item.text())

    def edit_default_settings(self):
        dlg = QDialog()
        dlg.setWindowTitle("Default Settings")

        config = configparser.RawConfigParser()
        config.optionxform = str
        config.read('settings/default_settings.ini')

        r = config['Ranges']
        ranges = {}
        for p in r:
            ranges[p] = [float(s) for s in config['Ranges'][p].split(',')]

        layout = QVBoxLayout()
        ranges_edit = {}
        for p in ranges:
            l = QHBoxLayout()
            low = QLineEdit()
            low.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

            v = QDoubleValidator()
            loc = QLocale(QLocale.c())
            loc.setNumberOptions(QLocale.RejectGroupSeparator)
            v.setLocale(loc)

            low.setValidator(v)
            low.setText(str(ranges[p][0]))

            up = QLineEdit()
            up.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))


            up.setValidator(v)
            up.setText(str(ranges[p][1]))

            ranges_edit[p] = [low, up]
            l.addWidget(low)
            label_txt = p if p != 'chiT' else 'chiT-chiS'
            label = QLabel(label_txt)
            label.setMinimumSize(QSize(65, 0))
            label.setAlignment(Qt.AlignCenter)
            l.addWidget(label)
            l.addWidget(up)
            layout.addLayout(l)

        headers_edit = {}
        headers = dict(config['Headers']).items()
        for key, val in headers:
            l = QHBoxLayout()
            label = QLabel(key)
            label.setMinimumSize(QSize(150, 0))
            label.setAlignment(Qt.AlignLeft)

            edit = QLineEdit()
            edit.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
            edit.setText(val)

            l.addWidget(label)
            l.addWidget(edit)
            headers_edit[key] = edit
            layout.addLayout(l)
        
        epsilons_edit = {}
        print(dict(config['Epsilons']))
        epsilons = dict(config['Epsilons'])
        for key, val in epsilons.items():
            l = QHBoxLayout()
            label = QLabel(key)
            label.setMinimumSize(QSize(150, 0))
            label.setAlignment(Qt.AlignLeft)

            edit = QLineEdit()
            edit.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
            v = QDoubleValidator()
            v.setBottom(0)
            loc = QLocale(QLocale.c())
            loc.setNumberOptions(QLocale.RejectGroupSeparator)
            v.setLocale(loc)
            edit.setValidator(v)
            edit.setText(val)
            l.addWidget(label)
            l.addWidget(edit)
            epsilons_edit[key] = edit
            layout.addLayout(l)

        plot_edit = {}
        plot_settings = dict(config['Plot'])
        for key , val in plot_settings.items():
            l = QHBoxLayout()
            label = QLabel(key)
            label.setMinimumSize(QSize(150, 0))
            label.setAlignment(Qt.AlignLeft)
            edit = QLineEdit()
            edit.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
            v = QIntValidator()
            v.setRange(0,1000)
            loc = QLocale(QLocale.c())
            loc.setNumberOptions(QLocale.RejectGroupSeparator)
            v.setLocale(loc)
            edit.setValidator(v)
            edit.setText(val)
            l.addWidget(label)
            l.addWidget(edit)
            plot_edit[key] = edit
            layout.addLayout(l)

        button = QPushButton("Apply new default settigs")
        button.clicked.connect(partial(self.write_default_settings, ranges_edit, headers_edit, epsilons_edit, plot_edit, dlg))
        layout.addWidget(button)
        dlg.setLayout(layout)
        dlg.exec_()

    def write_default_settings(self, ranges_edit, headers_edit, epsilons_edit, plot_edit, dlg):
        config = configparser.RawConfigParser()
        config.optionxform = str

        config['Ranges'] = {key:f"{edit[0].text()}, {edit[1].text()}" for key, edit in ranges_edit.items()}
        config['Headers'] = {key:header.text() for key, header in headers_edit.items()}
        config['Epsilons'] = {key:epsilon.text() for key, epsilon in epsilons_edit.items()}
        config['Plot'] = {key:value.text() for key, value in plot_edit.items()}

        with open('settings/default_settings.ini', 'w') as f:
            config.write(f)

        dlg.accept()

    def double_click(self, val):
        self.treeModel.itemFromIndex(val).double_click()
    
    def click(self, val):
        self.treeModel.itemFromIndex(val).click()

    def showMenu(self, position):
        index = self.TModel.indexAt(position)
        try:
            self.treeModel.itemFromIndex(index).showMenu(position)
        except AttributeError:
            pass
            #print("Non object clicked!")

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

    def slice_change_const(self):
        
        text = self.comboBox_slice.currentText()
        if text == "Field":
            self.label_slice_const.setText("Temp:")
        else:
            self.label_slice_const.setText("Field:")
            self.comboBox_slice.setCurrentText("Temperature")
        
        self.slice.change_slice_x_ax()

        if self.slice is not None:
            self.comboBox_slice2.blockSignals(True)
            self.comboBox_slice2.clear()
            self.slice.intervals = set()
            for value in self.slice.const_ax.sort_values():
                if value not in self.slice.intervals:
                    self.slice.intervals.add(value)
                    self.comboBox_slice2.addItem(f"{value} {self.slice.unit}")
            self.comboBox_slice2.setCurrentIndex(-1)
            self.comboBox_slice2.blockSignals(False)
            
            
            self.comboBox_slice2.setCurrentIndex(0)
        self.plot3d.refresh()
            
            


        

    # def resize_model(self):
    #     self.TModel.resizeColumnToContents(0)
















