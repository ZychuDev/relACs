from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout,
 QStackedWidget, QPushButton, QCheckBox, QTableView, QTableWidget, QAbstractScrollArea,
 QAbstractItemView, QTableWidgetItem, QTabWidget, QDialog, QComboBox, QSplitter)
from PyQt6.QtCore import QAbstractTableModel, QSize, QMetaObject, QObject, Qt
from PyQt6.QtGui import QFont, QPalette, QBrush, QColor

from models import TauFit, TAU_PARAMETER_NAME, Point
from .ParameterSlider import ParameterSlider

from matplotlib.figure import Figure # type: ignore
from matplotlib.pyplot import figure, Axes # type: ignore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg # type: ignore
from matplotlib.colors import CSS4_COLORS # type: ignore
from matplotlib.ticker import LinearLocator # type: ignore
import matplotlib.colors as mcolors # type: ignore

from typing import get_args, cast, Literal

from time import time

from numpy import log, meshgrid, ones

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width: int=10, height: int=5, dpi: int=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(fig)
        self.ax: Axes = fig.add_subplot()
        self.ax.grid(True, linestyle='--', linewidth=1, color=CSS4_COLORS["silver"])
        self.ax.xaxis.set_major_locator(LinearLocator(10))
        self.ax.yaxis.set_major_locator(LinearLocator(8))
        self.temp_label = r"$\frac{K}{T}$"
        self.field_label = r"$\frac{H}{Oe}$"
        title = r"$\tau^{-1}=A_{dir}TH^{N_{dir}} + \frac{B_1(1+B_3H^2)}{1+B_2H^2} + C_{Raman}T^{N_{Raman}}+\tau_0^{-1}\exp{\frac{-\Delta E}{T}}$"
        self.ax.set(xlabel=self.temp_label, ylabel=r"$\ln{\frac{\tau}{s}}$",
         title=title)


class MplCanvas3D(FigureCanvasQTAgg):
    def __init__(self, parent=None, width: int=10, height: int=5, dpi: int=100):
        self.fig: Figure = figure(figsize=(1,1), dpi = int(100), constrained_layout=True)
        self.fig.patch.set_facecolor("#ffffff")
        super().__init__(self.fig)
        self.axes: Axes = self.fig.add_subplot(projection='3d')
        self.axes.set_facecolor("#ffffff")

        self.axes.set_xlabel(r'$\frac{1}{T}$', rotation = 0, fontsize=15)
        self.axes.set_ylabel(r'$\frac{H}{Oe}$', rotation = 0, fontsize=15)
        self.axes.set_zlabel(r'$\ln{\frac{\tau}{s}}$', rotation = 0, fontsize=15)

        self.axes.xaxis.set_rotate_label(False) 
        self.axes.yaxis.set_rotate_label(False) 
        self.axes.zaxis.set_rotate_label(False) 


class TauFitPage(QWidget):
    def __init__(self):
        super().__init__()
        self.tau_fit: TauFit = None
        self.sliders: list[ParameterSlider] = []

        horizontal_layout: QHBoxLayout = QHBoxLayout()
        horizontal_spliter: QSplitter = QSplitter()

        left_layout: QVBoxLayout = QVBoxLayout()

        self.title_label: QLabel = QLabel("Title")
        self.title_label.setMaximumSize(QSize(16777215, 45))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font:QFont = QFont()
        font.setPointSize(22)
        font.setBold(True)
        font.setWeight(100)
        self.title_label.setFont(font)
        left_layout.addWidget(self.title_label, stretch=1)

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

        self._hidden_m = None
        self._m = None
        self._surface = None
        self._current = None
        self._saved = None
        right_layout: QVBoxLayout = QVBoxLayout()
        self.canvas_3d: MplCanvas3D = MplCanvas3D(self, width=5, height=4, dpi=100)
        right_layout.addWidget(self.canvas_3d)

        self.picker_radius = 25
        self._slice_m = None
        self._slice_hidden_m = None
        self._direct = None
        self._orbach = None
        self._raman = None
        self._qtm = None
        self._sum = None
        self._saved_sum = None
        self.canvas_slice: MplCanvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.canvas_slice.mpl_connect('pick_event', self.on_click)
        self._last_event_time:float = time()
        right_layout.addWidget(self.canvas_slice)

        left: QWidget() = QWidget()
        left.setLayout(left_layout)
        horizontal_spliter.addWidget(left)
        right: QWidget = QWidget()
        right.setLayout(right_layout)
        horizontal_spliter.addWidget(right)
        horizontal_spliter.setStretchFactor(0,1)
        horizontal_spliter.setStretchFactor(1,3)

        horizontal_layout.addWidget(horizontal_spliter)
        self.setLayout(horizontal_layout)

        self.varying_slice_combo_box.currentTextChanged.connect(self.set_model_varying)
        self.constant_value_slice.currentTextChanged.connect(self.set_model_constant)

    def on_click(self, event):
        mouse = event.mouseevent

        tmp_time:float = time()
        if tmp_time - self._last_event_time < 0.1:
            return
        try:
            x_data = event.artist.get_xdata().values.tolist()
            y_data = event.artist.get_ydata().values.tolist()
        except AttributeError:
            x_data = event.artist.get_xdata()
            y_data = event.artist.get_ydata()

        ind = event.ind[0]
        if mouse.button == mouse.button.LEFT:
            self.tau_fit.hide_point(x_data[ind], y_data[ind])

        if mouse.button == mouse.button.RIGHT:
            self.tau_fit.delete_point(x_data[ind], y_data[ind])

        self._last_event_time = time()


    def on_constant_value_changed(self):
        self._update_plot_varying()
        self._update_measurements_plots()
        self.canvas_3d.draw()
        self.canvas_slice.draw()

    def set_model_varying(self, s: str):
        if s == "Field" or s == "Temperature":
            self.tau_fit.set_varying(cast(Literal['Field', 'Temperature'], s))

    def set_model_constant(self, s:str):
        if len(s.split()) == 2:
            self.tau_fit.set_constant(float(s.split()[0]))
        else:
            ...
            # print("Error")
            # print("S: ", s)

    def set_tau_fit(self, tau_fit:TauFit):
        if self.tau_fit is not None:
            for cid in self.cids:
                QObject.disconnect(cid)


        self.tau_fit = tau_fit
        

        i: int
        for i, p in enumerate(self.tau_fit.parameters):
            self.sliders[i].set_parameter(p)

        self.cids: list[QMetaObject.Connection] = []

        self.cids.append(self.tau_fit.name_changed.connect(lambda new_name: self.title_label.setText(new_name)))
        self.cids.append(self.tau_fit.varying_changed.connect(self._update_slice_varying))
        self.cids.append(self.tau_fit.constant_changed.connect(self.on_constant_value_changed))
        self.cids.append(self.tau_fit.points_changed.connect(self.on_points_changed))
        
        # for p in self.tau_fit.parameters:
        #     self.p_cid.append(p.value_changed.connect())

        self.title_label.setText(tau_fit.name)

        self._update_errors()
        self._update_saved_errors()

        self._update_measurements_plots()
        self._update_slice_varying()
        self.canvas_3d.draw()
        self.canvas_slice.draw()

    def on_points_changed(self):
        self._update_measurements_plots()
        self.canvas_3d.draw()
        self.canvas_slice.draw()

    def _update_slice_varying(self):
        j: int
        for j in range(self.varying_slice_combo_box.count()):
            if self.varying_slice_combo_box.itemText(j) == self.tau_fit.varying:
                self.varying_slice_combo_box.setCurrentIndex(j)

        self.constant_slice_label.setText("Field:" if self.tau_fit.varying == "Temperature" else "Temperature:")

        self.constant_value_slice.clear()
        _, temp, field = self.tau_fit.get_visible()

        tmp: list[float] = temp if self.tau_fit.varying == "Field" else field
        tmp = list(set(tmp))
        tmp.sort()
        unit: str = "K" if self.tau_fit.varying == "Field" else "Oe"
        unique_strs: list[str] = [f"{v} {unit}" for v in tmp]
        self.constant_value_slice.addItems(unique_strs)

        self._update_measurements_plots()
        self._update_plot_varying()
        self.canvas_3d.draw()
        self.canvas_slice.draw()

    def _update_plot_varying(self):
        c3: MplCanvas = self.canvas_3d
        if self._surface is not None:
            self._surface.remove()

        const: float = self.tau_fit.constant
        if self.tau_fit.varying == "Temperature":
            xx, zz = meshgrid(c3.axes.get_xlim(), c3.axes.get_zlim())
            yy = ones(xx.shape) * const
        else:
            yy, zz = meshgrid(c3.axes.get_ylim(), c3.axes.get_zlim())
            if const == 0:
                xx = ones(yy.shape) * 0
            else:
                xx = ones(yy.shape) * 1/const

        self._surface = c3.axes.plot_surface(xx, yy, zz, color="y", alpha=0.2, label='slice')

        c: MplCanvas = self.canvas_slice
        c.ax.set_xlabel(c.field_label if self.tau_fit.varying == "Field" else c.temp_label)

    def _update_measurements_plots(self):
        if self.tau_fit is None:
            return

        hidden_tau, hidden_temp, hidden_field = self.tau_fit.get_hidden()
        tau, temp, field = self.tau_fit.get_visible()
        temp_invert = [1/t for t in temp]
        hidden_temp_invert = [1/t for t in hidden_temp]

        if not(self._hidden_m is None or self._m is None):
            self._hidden_m.remove()
            self._m.remove()

        self._hidden_m = self.canvas_3d.axes.scatter(hidden_temp_invert, hidden_field, log(hidden_tau), "o",
             label='hidden points from fits', color=mcolors.TABLEAU_COLORS["tab:orange"])

        self._m = self.canvas_3d.axes.scatter(temp_invert, field, log(tau), "o", color=mcolors.TABLEAU_COLORS["tab:blue"], label='points from fits')

        if self._slice_m is None or self._slice_hidden_m is None:
            xx: list[float]
            zz, temp, field = self.tau_fit.get_visible_s()
            if self.tau_fit.varying == "Field":
                xx = field
            else:
                xx = [1/t for t in temp]
            self._slice_m = self.canvas_slice.ax.plot(xx, log(zz), "o", c=mcolors.TABLEAU_COLORS["tab:blue"], picker=self.picker_radius)[0]

            zz, temp, field = self.tau_fit.get_hidden_s()
            if self.tau_fit.varying == "Field":
                xx = field
            else:
                xx = [1/t for t in temp]
            self._slice_hidden_m = self.canvas_slice.ax.plot(xx, log(zz), "o", c=mcolors.TABLEAU_COLORS["tab:orange"], picker=self.picker_radius)[0]
        else:
            zz, temp, field = self.tau_fit.get_visible_s()
            zz_h, temp_h, field_h = self.tau_fit.get_hidden_s()
            if self.tau_fit.varying == "Field":
                xx = field
                xx_h = field_h
            else:
                xx = [1/t for t in temp]
                xx_h = [1/t for t in temp_h]

            zz = log(zz)
            zz_h = log(zz_h)
            self._slice_m.set_xdata(xx)
            self._slice_m.set_ydata(zz)
            
            self._slice_hidden_m.set_xdata(xx_h)
            self._slice_hidden_m.set_ydata(zz_h)

            min_x:float = None
            max_x:float = None
            if len(xx) != 0:
                min_x = min(xx)
                max_x = max(xx)
            if len(xx_h) != 0:
                if min_x is not None:
                    min_x = min(min_x, min(xx_h))
                    max_x = max(max_x, max(xx_h))
            if min_x is not None and max_x is not None:
                span_x: float = max_x - min_x
                self.canvas_slice.ax.set_xbound(min_x - span_x*0.05 , max_x + span_x*0.05)

            min_z:float = None
            max_z:float = None
            if len(zz) != 0:
                min_z = min(zz)
                max_z = max(zz)
            if len(zz_h) != 0:
                if min_z is not None:
                    min_z = min(min_z, min(zz_h))
                    max_z = max(max_z, max(zz_h))
            if min_z is not None and max_z is not None:
                span_z: float = max_z - min_z
                self.canvas_slice.ax.set_ybound(min_z - span_z*0.05, max_z + span_z*0.05)
       
    def _update_errors(self):
        i:int
        for i, p in enumerate(self.tau_fit.parameters):
            self.fit_error.setItem(1, i, QTableWidgetItem(f"{round(p.value, 8)} += {str(round(p.error, 8))}"))
        self.fit_error.setItem(1, i+1, QTableWidgetItem(str(round(self.tau_fit.residual_error, 8))))
    
    def _update_saved_errors(self):
        i:int
        for i, p in enumerate(self.tau_fit.saved_parameters):
            self.fit_error.setItem(0, i, QTableWidgetItem(f"{round(p.value, 8)} += {str(round(p.error, 8))}"))
        self.fit_error.setItem(0, i+1, QTableWidgetItem(str(round(self.tau_fit.saved_residual_erro, 8))))

    