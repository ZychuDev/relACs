from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout,
 QStackedWidget, QPushButton, QCheckBox, QTableView, QTableWidget, QAbstractScrollArea,
 QAbstractItemView, QTableWidgetItem, QTabWidget, QDialog, QComboBox)
from PyQt6.QtCore import QAbstractTableModel, QSize, QMetaObject, QObject, Qt
from PyQt6.QtGui import QFont, QPalette, QBrush, QColor

from models import TauFit, TAU_PARAMETER_NAME, Point
from .ParameterSlider import ParameterSlider

from matplotlib.figure import Figure # type: ignore
from matplotlib.pyplot import figure # type: ignore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg # type: ignore

from typing import get_args

from time import time

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width: int=10, height: int=5, dpi: int=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(fig)

class MplCanvas3D(FigureCanvasQTAgg):
    def __init__(self, parent=None, width: int=10, height: int=5, dpi: int=100):
        self.fig: Figure = figure(figsize=(1,1), dpi = int(100), constrained_layout=True)
        self.fig.patch.set_facecolor("#f0f0f0")
        super().__init__(self.fig)
        self.axes = self.fig.add_subplot(projection='3d')
        self.axes.set_facecolor("#f0f0f0")


class TauFitPage(QWidget):
    def __init__(self):
        super().__init__()
        self.tau_fit: TauFit = None
        self.sliders: list[ParameterSlider] = []

        horizontal_layout: QHBoxLayout = QHBoxLayout()

        left_layout: QVBoxLayout = QVBoxLayout()

        self.title_label: QLabel = QLabel("Title")
        self.title_label.setMaximumSize(QSize(16777215, 45))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font:QFont = QFont()
        font.setPointSize(22)
        font.setBold(True)
        font.setWeight(100)
        self.title_label.setFont(font)
        left_layout.addWidget(self.title_label, stretch=2)

        for parameter in get_args(TAU_PARAMETER_NAME):
            ps: ParameterSlider = ParameterSlider()
            self.sliders.append(ps)
            left_layout.addWidget(ps)

        control_layout: QHBoxLayout = QHBoxLayout()

        col_1: QVBoxLayout = QVBoxLayout()
        self.adjust_range_button: QPushButton = QPushButton("Adjust ranges")
        self.copy_parameters_button: QPushButton = QPushButton("Copy parameters")
        col_1.addWidget(self.adjust_range_button)
        col_1.addWidget(self.copy_parameters_button)
        control_layout.addLayout(col_1, stretch=1)

        col_2: QVBoxLayout = QVBoxLayout()
        self.fit_button: QPushButton = QPushButton("Fit for all")
        self.save_button: QPushButton = QPushButton("Save")
        self.reset_button: QPushButton = QPushButton("Reset parameters")
        col_2.addWidget(self.fit_button)
        col_2.addWidget(self.save_button)
        col_2.addWidget(self.reset_button)
        control_layout.addLayout(col_2, stretch=1)

        col_3: QVBoxLayout = QVBoxLayout()
        self.fit_for_slice_button: QPushButton = QPushButton("Fit for slice")
        self.varying_slice_combo_box: QComboBox = QComboBox()
        self.varying_slice_combo_box.addItems(["Field", "Temperature"])
        self.constant_slice_label: QLabel = QLabel("Temperature")
        self.constant_value_slice: QComboBox = QComboBox()
        constant_slice_layout: QHBoxLayout = QHBoxLayout()
        constant_slice_layout.addWidget(self.constant_slice_label)
        constant_slice_layout.addWidget(self.constant_value_slice)
        col_3.addWidget(self.fit_for_slice_button)
        col_3.addWidget(self.varying_slice_combo_box)
        col_3.addLayout(constant_slice_layout)
        control_layout.addLayout(col_3, stretch=1)

        left_layout.addLayout(control_layout)

        fit_error: QTableWidget = QTableWidget()
        fit_error.setMinimumSize(QSize(255, 100))
        fit_error.setMaximumSize(QSize(16777215, 100))
        fit_error.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        fit_error.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        fit_error.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        fit_error.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        fit_error.setDragEnabled(False)
        fit_error.setAlternatingRowColors(False)
        fit_error.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        fit_error.setColumnCount(len(get_args(TAU_PARAMETER_NAME))+1)
        fit_error.setRowCount(2)

        fit_error.setVerticalHeaderItem(0, QTableWidgetItem("Saved: "))
        fit_error.setVerticalHeaderItem(1, QTableWidgetItem("Current: "))

        header = fit_error.verticalHeader()
        header.setVisible(True)
        header.setDefaultSectionSize(50)

        header = fit_error.horizontalHeader()
        header.setCascadingSectionResizes(True)
        header.setDefaultSectionSize(210)
        header.setStretchLastSection(True)
        header = fit_error.verticalHeader()
        header.setVisible(True)
        header.setDefaultSectionSize(25)
        header.setMinimumSectionSize(25)
        header.setStretchLastSection(True)

        i: int
        param: TAU_PARAMETER_NAME
        for i, param in enumerate(get_args(TAU_PARAMETER_NAME)):
            item: QTableWidgetItem = QTableWidgetItem()
            
            item.setText(str(param))
            fit_error.setHorizontalHeaderItem(i, item)
        fit_error.setHorizontalHeaderItem(i+1, QTableWidgetItem("Residual"))

        left_layout.addWidget(fit_error)
        self.fit_error = fit_error

        right_layout: QVBoxLayout = QVBoxLayout()
        self.canvas_3d: MplCanvas3D = MplCanvas3D(self, width=5, height=4, dpi=100)
        right_layout.addWidget(self.canvas_3d)

        self.canvas_slice: MplCanvas = MplCanvas(self, width=5, height=4, dpi=100)
        self._last_event_time:float = time()
        right_layout.addWidget(self.canvas_slice)

        horizontal_layout.addLayout(left_layout)
        horizontal_layout.addLayout(right_layout)
        self.setLayout(horizontal_layout)

    def set_tau_fit(self, tau_fit:TauFit):
        if self.tau_fit is not None:
            pass

        self.tau_fit = tau_fit
        self.tau_fit.name_changed.connect(lambda new_name: self.title_label.setText(new_name))

        self.title_label.setText(tau_fit.name)