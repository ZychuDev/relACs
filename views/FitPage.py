from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout,
 QStackedWidget, QPushButton, QCheckBox, QTableView, QTableWidget, QAbstractScrollArea,
 QAbstractItemView, QTableWidgetItem, QTabWidget)
from PyQt6.QtCore import QAbstractTableModel, QSize, Qt
from PyQt6.QtGui import QFont, QPalette, QBrush, QColor

from models import Fit, PARAMETER_NAME
from typing import get_args

from .ParameterSlider import ParameterSlider

from matplotlib.figure import Figure # type: ignore
from matplotlib.artist import Artist # type: ignore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg # type: ignore

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width: int=10, height: int=5, dpi: int=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax1 = fig.add_subplot(222)
        self.ax1.grid()
        self.ax1.set(title=r"$\chi^{\prime}$", xlabel=r"$\log {\frac{v}{Hz}}$", ylabel=r"$\chi^{\prime} /cm^3*mol^{-1}$")
        self.ax2 = fig.add_subplot(2,2, (3,4))
        self.ax2.grid()
        self.ax2.set(title=r"$\chi^{\prime \prime}$", xlabel=r"$\log {\frac{v}{Hz}}$", ylabel=r"$\chi^{\prime \prime} /cm^3*mol^{-1}$")
        self.ax3 = fig.add_subplot(221)
        self.ax3.grid()
        self.ax3.set(title=r"Cole-Cole", xlabel=r"$\chi^{\prime} /cm^3*mol^{-1}$", ylabel=r"$\chi^{\prime \prime} / cm^3*mol^{-1}$")
        fig.subplots_adjust(left=0.06, right=0.99, top=0.9, bottom=0.15)
        super(MplCanvas, self).__init__(fig)

class ParametersControl(QTabWidget):
    def __init__(self):
        super().__init__()
        self.fit: Fit = None

        relaxation: int
        for relaxation in range(1,3):

            palette: QPalette = QPalette()
            brush = QBrush(QColor(240, 240, 240))
            brush.setStyle(Qt.BrushStyle.SolidPattern)
            palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush)
            self.fit_error: QTableWidget = QTableWidget()
            self.fit_error.setMinimumSize(QSize(255, 100))
            self.fit_error.setMaximumSize(QSize(16777215, 100))
            self.fit_error.setPalette(palette)
            self.fit_error.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.fit_error.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.fit_error.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
            self.fit_error.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self.fit_error.setDragEnabled(False)
            self.fit_error.setAlternatingRowColors(False)
            self.fit_error.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
            self.fit_error.setColumnCount(6)
            self.fit_error.setRowCount(2)

            self.fit_error.setVerticalHeaderItem(0, QTableWidgetItem("Saved: "))
            self.fit_error.setVerticalHeaderItem(1, QTableWidgetItem("Current: "))

            header = self.fit_error.verticalHeader()
            header.setVisible(True)
            header.setDefaultSectionSize(50)
            
            header = self.fit_error.horizontalHeader()
            header.setCascadingSectionResizes(True)
            header.setDefaultSectionSize(210)
            header.setStretchLastSection(True)
            header = self.fit_error.verticalHeader()
            header.setVisible(True)
            header.setDefaultSectionSize(25)
            header.setMinimumSectionSize(25)
            header.setStretchLastSection(True)

            self.addTab(self.fit_error, f"Relaxation nr {relaxation}")

            i: int
            param: PARAMETER_NAME
            for i, param in enumerate(get_args(PARAMETER_NAME)):
                item: QTableWidgetItem = QTableWidgetItem()
                item.setText(str(param))
                self.fit_error.setHorizontalHeaderItem(i, item)
            self.fit_error.setHorizontalHeaderItem(i+1, QTableWidgetItem("residual"))

    def on_fit_changed(fit: Fit):
        pass

class FitPage(QWidget):
    def __init__(self):
        super().__init__()
        self.fit: Fit = None
        self.picker_radius: int = 5

        vertical_layout: QVBoxLayout = QVBoxLayout()

        self.title_label: QLabel = QLabel("Title")
        self.title_label.setMaximumSize(QSize(16777215, 45))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font:QFont = QFont()
        font.setPointSize(22)
        font.setBold(True)
        font.setWeight(100)
        self.title_label.setFont(font)

        vertical_layout.addWidget(self.title_label, stretch=1)

        self.canvas: MplCanvas = MplCanvas(self, width=5, height=4, dpi=100)
        
        lower_panel: QHBoxLayout = QHBoxLayout()
        right_side: QVBoxLayout = QVBoxLayout()

        self.fit_button: QPushButton = QPushButton("Fit")
        self.fit_button.setMinimumSize(QSize(205, 0))
        self.fit_button.setMaximumSize(QSize(205, 16777215))
        self.adjust_range_button: QPushButton = QPushButton("Adjust Range")
        self.adjust_range_button.setMinimumSize(QSize(205, 0))
        self.adjust_range_button.setMaximumSize(QSize(205, 16777215))
        self.save_button: QPushButton = QPushButton("Save")
        self.save_button.setMinimumSize(QSize(205, 0))
        self.save_button.setMaximumSize(QSize(205, 16777215))
        self.reset_current_button: QPushButton = QPushButton("Reset current parameters")
        self.reset_current_button.setMinimumSize(QSize(205, 0))
        self.reset_current_button.setMaximumSize(QSize(205, 16777215))
        self.copy_parameters_button: QPushButton = QPushButton("Copy parameters")
        self.copy_parameters_button.setMinimumSize(QSize(205, 0))
        self.copy_parameters_button.setMaximumSize(QSize(205, 16777215))
        self.remember_check_box: QCheckBox = QCheckBox("Remember paraneters")
        self.remember_check_box.setMinimumSize(QSize(205, 0))
        self.remember_check_box.setMaximumSize(QSize(205, 16777215))
        self.cycle_buttons: QVBoxLayout = QHBoxLayout()
        self.cycle_previous: QPushButton = QPushButton("<")
        self.cycle_previous.setMinimumSize(QSize(100, 0))
        self.cycle_previous.setMaximumSize(QSize(100, 16777215))
        self.cycle_next: QPushButton = QPushButton(">")
        self.cycle_next.setMinimumSize(QSize(100, 0))
        self.cycle_next.setMaximumSize(QSize(100, 16777215))
        
        right_side.addWidget(self.fit_button)
        right_side.addWidget(self.adjust_range_button)
        right_side.addWidget(self.save_button)
        right_side.addWidget(self.reset_current_button)
        right_side.addWidget(self.copy_parameters_button)
        right_side.addWidget(self.remember_check_box)

        self.cycle_buttons.addWidget(self.cycle_previous, stretch=1)
        self.cycle_buttons.addWidget(self.cycle_next, stretch=1)
        right_side.addLayout(self.cycle_buttons)

        self.left_side = ParametersControl()

        lower_panel.addWidget(self.left_side, stretch=5)
        lower_panel.addLayout(right_side, stretch=1)

        vertical_layout.addWidget(self.canvas, stretch=3)
        vertical_layout.addLayout(lower_panel, stretch=1)
        self.setLayout(vertical_layout)

    def set_fit(self, fit:Fit):
        if self.fit is not None:
            pass

        self.fit = fit
        self.fit.name_changed.connect(lambda new_name: self.title_label.setText(new_name))

        self.title_label.setText(fit.name)


        
