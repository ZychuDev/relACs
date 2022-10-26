from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QSpinBox, QLabel, QPushButton
from PyQt6.QtCore import pyqtSlot

from models.MainModel import MainModel
from controllers.MainController import MainController
from views.mvc_app_rc import Ui_MainWindow



class MainView(QMainWindow):
    def __init__(self, model:MainModel, main_controller: MainController):
        super().__init__()
        self._ui = QWidget()
        self._ui.centralwidget = QWidget(self)
        self._ui.centralwidget.setObjectName("centralwidget")
        self._ui.vboxlayout = QVBoxLayout(self._ui.centralwidget)
        self._ui.vboxlayout.setObjectName("vboxlayout")
        self._ui.spinBox_amount = QSpinBox(self._ui.centralwidget)
        self._ui.spinBox_amount.setObjectName("spinBox_amount")
        self._ui.vboxlayout.addWidget(self._ui.spinBox_amount)
        self._ui.label_even_odd = QLabel(self._ui.centralwidget)
        self._ui.label_even_odd.setObjectName("label_even_odd")
        self._ui.vboxlayout.addWidget(self._ui.label_even_odd)
        self._ui.pushButton_reset = QPushButton(self._ui.centralwidget)
        self._ui.pushButton_reset.setEnabled(False)
        self._ui.pushButton_reset.setObjectName("pushButton_reset")
        self._ui.vboxlayout.addWidget(self._ui.pushButton_reset)
        self.setObjectName("MainWindow")
        self.resize(93, 86)

        self.setCentralWidget(self._ui.centralwidget)

        self._model = model
        self._main_controller = main_controller


        # connect widgets to controller
        self._ui.spinBox_amount.valueChanged.connect(lambda v: self._main_controller.change_amount(v))
        self._ui.pushButton_reset.clicked.connect(lambda: self._main_controller.change_amount(0))

        # listen for model event signals
        self._model.amount_changed.connect(self.on_amount_changed)
        self._model.even_odd_changed.connect(self.on_even_odd_changed)
        self._model.enable_reset_changed.connect(self.on_enable_reset_changed)

        # set a default value
        self._main_controller.change_amount(42)

    @pyqtSlot(int)
    def on_amount_changed(self, value):
        self._ui.spinBox_amount.setValue(value)

    @pyqtSlot(str)
    def on_even_odd_changed(self, value):
        self._ui.label_even_odd.setText(value)

    @pyqtSlot(bool)
    def on_enable_reset_changed(self, value):
        self._ui.pushButton_reset.setEnabled(value)