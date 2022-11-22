from PyQt6.QtWidgets import QMainWindow, QWidget, QSplitter, QVBoxLayout, QSpinBox, QLabel, QPushButton, QTreeView
from PyQt6.QtCore import pyqtSlot, Qt, QPoint, QModelIndex
from PyQt6.QtGui import QStandardItemModel, QStandardItem

from models.MainModel import MainModel
from controllers.MainController import MainController
from views.mvc_app_rc import Ui_MainWindow

from .HomePageView import HomePageView
from .ControlTreeView import ControlTreeView
from .RootItem import RootItem

from controllers import CompoundItemsCollectionController
from models import CompoundItemsCollectionModel
from .CompundItemsCollection import CompoundItemsCollection

class MainUi(QWidget):
    def __init__(self):
        super().__init__()
        # self.centralwidget = QWidget(self)
        # self.centralwidget.setObjectName("centralwidget")
        # self.vboxlayout = QVBoxLayout(self.centralwidget)
        # self.vboxlayout.setObjectName("vboxlayout")
        # self.spinBox_amount = QSpinBox(self.centralwidget)
        # self.spinBox_amount.setObjectName("spinBox_amount")
        # self.vboxlayout.addWidget(self.spinBox_amount)
        # self.label_even_odd = QLabel(self.centralwidget)
        # self.label_even_odd.setObjectName("label_even_odd")
        # self.vboxlayout.addWidget(self.label_even_odd)
        # self.pushButton_reset = QPushButton(self.centralwidget)
        # self.pushButton_reset.setEnabled(False)
        # self.pushButton_reset.setObjectName("pushButton_reset")
        # self.vboxlayout.addWidget(self.pushButton_reset)

        # self.vboxlayout.addWidget(HomePageView())
        # self.setLayout(self.vboxlayout)

class MainView(QMainWindow):
    def __init__(self, model:MainModel, main_controller: MainController):
        super().__init__()
        self._ui = MainUi()
        
        self.setObjectName("MainWindow")
        # self.resize(930, 86)
        self.splitter = QSplitter()
        tree_model = CompoundItemsCollectionModel("relACs")
        self.compounds = CompoundItemsCollection(tree_model, CompoundItemsCollectionController(tree_model))
        self.control_tree: ControlTreeView = ControlTreeView()
 # type: ignore 
        self.splitter.addWidget(self.control_tree)
        rootNode:QStandardItem  = self.control_tree.model().invisibleRootItem() # type: ignore 
        rootNode.appendRow(self.compounds)
        self.splitter.addWidget(HomePageView())
        self.setCentralWidget(self.splitter)
        self.setStyleSheet("background-color: white;")

        self._model = model
        self._main_controller = main_controller


        # connect widgets to controller
        # self._ui.spinBox_amount.valueChanged.connect(lambda v: self._main_controller.change_amount(v))
        # self._ui.pushButton_reset.clicked.connect(lambda: self._main_controller.change_amount(0))

        # listen for model event signals
        # self._model.amount_changed.connect(self.on_amount_changed)
        # self._model.even_odd_changed.connect(self.on_even_odd_changed)
        # self._model.enable_reset_changed.connect(self.on_enable_reset_changed)

        # set a default value
        # self._main_controller.change_amount(model.amount)

    # @pyqtSlot(int)
    # def on_amount_changed(self, value):
    #     self._ui.spinBox_amount.setValue(value)

    # @pyqtSlot(str)
    # def on_even_odd_changed(self, value):
    #     self._ui.label_even_odd.setText(value)

    # @pyqtSlot(bool)
    # def on_enable_reset_changed(self, value):
    #     self._ui.pushButton_reset.setEnabled(value)