from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout,
 QStackedWidget, QPushButton, QCheckBox, QTableView, QTableWidget, QAbstractScrollArea,
 QAbstractItemView, QTableWidgetItem, QTabWidget)
from PyQt6.QtCore import QAbstractTableModel, QSize, Qt
from PyQt6.QtGui import QFont, QPalette, QBrush, QColor

from models import Fit, PARAMETER_NAME, Relaxation
from typing import get_args

from .ParameterSlider import ParameterSlider

from pandas import DataFrame, Series # type: ignore

from matplotlib.figure import Figure # type: ignore
from matplotlib.artist import Artist # type: ignore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg # type: ignore
from matplotlib.colors import CSS4_COLORS # type: ignore
from matplotlib.ticker import LinearLocator # type: ignore
from matplotlib import use # type: ignore

from numpy import ndarray, pi, power, add
from scipy.optimize import least_squares

use('Qt5Agg')

from time import time

def model(logFrequency: ndarray, alpha: float, beta: float, tau: float, chi_t: float, chi_s: float) -> ndarray:
    return chi_s + (chi_t - chi_s)/((1 + (10**logFrequency*2*pi * power(10, tau) * 1j )**(1- alpha))**beta)




class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width: int=10, height: int=5, dpi: int=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax1 = fig.add_subplot(222)
        self.ax1.grid(True, linestyle='--', linewidth=1, color=CSS4_COLORS["silver"])
        self.ax1.xaxis.set_major_locator(LinearLocator(10))
        self.ax1.yaxis.set_major_locator(LinearLocator(8))
        self.ax1.set(title=r"$\chi^{\prime}$", xlabel=r"$\log {\frac{v}{Hz}}$", ylabel=r"$\chi^{\prime} /cm^3*mol^{-1}$")
        self.ax2 = fig.add_subplot(2,2, (3,4))
        self.ax2.grid(True, linestyle='--', linewidth=1, color=CSS4_COLORS["silver"])
        self.ax2.xaxis.set_major_locator(LinearLocator(10))
        self.ax2.yaxis.set_major_locator(LinearLocator(8))
        self.ax2.set(title=r"$\chi^{\prime \prime}$", xlabel=r"$\log {\frac{v}{Hz}}$", ylabel=r"$\chi^{\prime \prime} /cm^3*mol^{-1}$")
        self.ax3 = fig.add_subplot(221)
        self.ax3.grid(True, linestyle='--', linewidth=1, color=CSS4_COLORS["silver"])
        self.ax3.xaxis.set_major_locator(LinearLocator(10))
        self.ax3.yaxis.set_major_locator(LinearLocator(8))
        self.ax3.set(title=r"Cole-Cole", xlabel=r"$\chi^{\prime} /cm^3*mol^{-1}$", ylabel=r"$\chi^{\prime \prime} / cm^3*mol^{-1}$")
        fig.subplots_adjust(left=0.06, right=0.99, top=0.9, bottom=0.15)
        super(MplCanvas, self).__init__(fig)

class RelaxationTab(QWidget):
    def __init__(self):
        super().__init__()
        self.sliders: list[ParameterSlider] = []

        tab_layout: QVBoxLayout = QVBoxLayout()
        for parameter in get_args(PARAMETER_NAME):
            ps: ParameterSlider = ParameterSlider()
            self.sliders.append(ps)
            tab_layout.addWidget(ps)
        
        palette: QPalette = QPalette()
        brush = QBrush(QColor(255, 244, 244))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush)
        brush = QBrush(QColor(255, 244, 244))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush)
        brush = QBrush(QColor(240, 240, 240))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush)
        fit_error: QTableWidget = QTableWidget()
        fit_error.setPalette(palette)
        fit_error.setAutoFillBackground(True)
        fit_error.setMinimumSize(QSize(255, 100))
        fit_error.setMaximumSize(QSize(16777215, 100))
        fit_error.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        fit_error.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        fit_error.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        fit_error.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        fit_error.setDragEnabled(False)
        fit_error.setAlternatingRowColors(False)
        fit_error.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        fit_error.setColumnCount(6)
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
        param: PARAMETER_NAME
        for i, param in enumerate(get_args(PARAMETER_NAME)):
            item: QTableWidgetItem = QTableWidgetItem()
            
            item.setText(str(param))
            fit_error.setHorizontalHeaderItem(i, item)
        fit_error.setHorizontalHeaderItem(i+1, QTableWidgetItem("residual"))

        tab_layout.addWidget(fit_error)
        self.setLayout(tab_layout)

    def set_relaxation(self, relaxation: Relaxation):
        for i, s in enumerate(self.sliders):
            s.set_parameter(relaxation.parameters[i])

class ParametersControl(QTabWidget):
    def __init__(self):
        super().__init__()
        self.fit: Fit = None
        self.relaxations: list[RelaxationTab] = []
        relaxation: int
        for relaxation in range(1,3):
            tab = RelaxationTab()
            self.relaxations.append(tab)
            self.addTab(tab, f"Relaxation nr {relaxation}")
            self.setTabEnabled(relaxation, False)

    def set_fit(self, fit: Fit):
        for i, r in enumerate(self.relaxations):
            if len(fit.relaxations) == i:
                self.setTabEnabled(i, False)
                continue
            r.set_relaxation(fit.relaxations[i])
            self.setTabEnabled(i, True)

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
        self._chi_prime_m = None
        self._chi_bis_m = None
        self._cole_cole_m = None

        self._chi_prime_m_h = None
        self._chi_bis_m_h = None
        self._cole_cole_m_h = None

        self._chi_prime_c: list = []
        self._chi_bis_c: list = []
        self._cole_cole_c: list = []

        self._chi_prime_s: list = []
        self._chi_bis_s: list = []
        self._cole_cole_s: list = []

        self._chi_prime_total = None
        self._chi_bis_total = None
        self._cole_cole_total = None

        self._chi_prime_total_s = None
        self._chi_bis_total_s = None
        self._cole_cole_total_s = None

        self.cid: int = self.canvas.mpl_connect('pick_event', self.on_click)
        self._last_event_time:float = time()
        
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

        self.fit_button.clicked.connect(self.make_auto_fit)

    def set_fit(self, fit:Fit):
        if self.fit is not None:
            self.fit.df_changed.disconnect()
            self.fit.df_point_deleted.disconnect()
            self.fit.name_changed.disconnect()
            for r in self.fit.relaxations:
                for p in r.parameters:
                    p.value_changed.disconnect()

        self.fit = fit
        self.fit.df_changed.connect(self._update_measurements_plots)
        self.fit.df_point_deleted.connect(self.on_point_deleted)
        self.fit.name_changed.connect(lambda new_name: self.title_label.setText(new_name))

        for i, r in enumerate(self.fit.relaxations):
            for p in r.parameters:
                p.value_changed.connect(lambda: self._update_fit_plot_for_one_relax(i, True))

        self.title_label.setText(fit.name)

        self.left_side.set_fit(fit)


        self._update_domains()
        self._update_fit_plots()
        self._update_measurements_plots()



    def _update_measurements_plots(self):
        if self.fit is None:
            return

        df: DataFrame = self.fit._df
        hidden: DataFrame = df.loc[df["Hidden"] == True]
        visible: DataFrame = df.loc[df["Hidden"] == False]

        if self._chi_prime_m is None or self._chi_bis_m is None or self._cole_cole_m is None:
            self._chi_prime_m = self.canvas.ax1.plot(visible["FrequencyLog"].values, visible["ChiPrimeMol"], "bo", picker=self.picker_radius)[0]
            self._chi_prime_m_h = self.canvas.ax1.plot(hidden["FrequencyLog"].values, hidden["ChiPrimeMol"], "yo", picker=self.picker_radius)[0]
            self._chi_bis_m = self.canvas.ax2.plot(visible["FrequencyLog"].values, visible["ChiBisMol"], "bo", picker=self.picker_radius )[0]
            self._chi_bis_m_h = self.canvas.ax2.plot(hidden["FrequencyLog"].values, hidden["ChiBisMol"], "yo", picker=self.picker_radius )[0]
            self._cole_cole_m = self.canvas.ax3.plot(visible["ChiPrimeMol"].values, visible["ChiBisMol"], "bo", picker=self.picker_radius)[0]
            self._cole_cole_m_h = self.canvas.ax3.plot(hidden["ChiPrimeMol"].values, hidden["ChiBisMol"], "yo", picker=self.picker_radius)[0]
        else:
            self._chi_prime_m.set_xdata(visible["FrequencyLog"])
            self._chi_prime_m.set_ydata(visible["ChiPrimeMol"])

            self._chi_prime_m_h.set_xdata(hidden["FrequencyLog"])
            self._chi_prime_m_h.set_ydata(hidden["ChiPrimeMol"])

            self._chi_bis_m.set_xdata(visible["FrequencyLog"])
            self._chi_bis_m.set_ydata(visible["ChiBisMol"])

            self._chi_bis_m_h.set_xdata(hidden["FrequencyLog"])
            self._chi_bis_m_h.set_ydata(hidden["ChiBisMol"])

            self._cole_cole_m.set_xdata(visible["ChiPrimeMol"])
            self._cole_cole_m.set_ydata(visible["ChiBisMol"])

            self._cole_cole_m_h.set_xdata(hidden["ChiPrimeMol"])
            self._cole_cole_m_h.set_ydata(hidden["ChiBisMol"])
            
        print("Hidden", len(hidden["FrequencyLog"]), len(hidden["ChiPrimeMol"]), len(hidden["ChiBisMol"]))
        print("visible", len(visible["FrequencyLog"]), len(visible["ChiPrimeMol"]), len(visible["ChiBisMol"]))
        self.canvas.draw()

    def _update_fit_plots(self):
        print("fit_plots")
        if self.fit is None:
            return
        relax_nr: int = len(self.fit.relaxations)
        if len(self._chi_prime_c) != relax_nr or len(self._chi_bis_c) != relax_nr or len(self._cole_cole_c) != relax_nr:
            self._recreate_fit_plot()
        else:
            for r in range(relax_nr):
                self._update_fit_plot_for_one_relax(r)

    def _recreate_fit_plot(self):
        print("reacreate_fit_plots")
        self._chi_prime_c = []
        self._chi_bis_c = []
        self._cole_cole_c = []

        self._chi_prime_s = []
        self._chi_bis_s = []
        self._cole_cole_s = []

        df: DataFrame = self.fit._df
        relax_nr: int = len(self.fit.relaxations)
        frequency_log: ndarray = df["FrequencyLog"].values

        total = []
        total_s = []
        for r in range(relax_nr):
            result: ndarray = model(frequency_log, *self.fit.relaxations[r].get_parameters_values())
            result_s: ndarray = model(frequency_log, *self.fit.relaxations[r].get_saved_parameters_values())
            print(result)

            self._chi_prime_c.append(self.canvas.ax1.plot(frequency_log, result.real, "--")[0])
            self._chi_bis_c.append(self.canvas.ax2.plot(frequency_log, result.imag, "--")[0])
            self._cole_cole_c.append(self.canvas.ax3.plot(result.real, result.imag, "--")[0])

            self._chi_prime_s.append(self.canvas.ax1.plot(frequency_log, result_s.real, "-")[0])
            self._chi_bis_s.append(self.canvas.ax2.plot(frequency_log, result_s.imag, "-")[0])
            self._cole_cole_s.append(self.canvas.ax3.plot(result_s.real, result_s.imag, "-")[0])

            if len(total) == 0:
                total = result
            else:
                add(total, result, total)

            if len(total_s) == 0:
                total_s = result_s
            else:
                add(total_s, result_s, total_s)

            self._chi_prime_total = self.canvas.ax1.plot(frequency_log, total.real, "--")[0]
            self._chi_bis_total = self.canvas.ax2.plot(frequency_log, total.imag, "--")[0]
            self._cole_cole_total = self.canvas.ax3.plot(total.real, total.imag, "--")[0]

            self._chi_prime_total_s = self.canvas.ax1.plot(frequency_log, total_s.real, "-")[0]
            self._chi_bis_total_s = self.canvas.ax2.plot(frequency_log, total_s.imag, "-")[0]
            self._cole_cole_total_s = self.canvas.ax3.plot(total_s.real, total_s.imag, "-")[0]
           

    def _update_fit_plot_for_one_relax(self, r: int, redraw: bool=False):  
        print("update_fit_plots")
        df: DataFrame = self.fit._df
        frequency_log: ndarray = df["FrequencyLog"].values
        result: ndarray = model(frequency_log, *self.fit.relaxations[r].get_parameters_values())
        self._cole_cole_c[r].set_xdata(result.real)
        self._cole_cole_c[r].set_ydata(result.imag)
        self._chi_prime_c[r].set_ydata(result.real)
        self._chi_bis_c[r].set_ydata(result.imag)
        
        total = result
        for other in range(len(self.fit.relaxations)):
            if other != r:
                src = self._cole_cole_c[other]
                add(total, src.get_xdata().astype(complex), total)
                add(total, src.get_ydata().astype(complex), total)


        self._cole_cole_total.set_xdata(total.real)
        self._cole_cole_total.set_ydata(total.imag)
        self._chi_prime_total.set_ydata(total.real)
        self._chi_bis_total.set_ydata(total.imag)

        if redraw:
            self._update_domains(result=result)
            self.canvas.draw()


    def _update_fit_plot_for_one_saved_relax(self, r: int, redraw: bool = False):  
        df: DataFrame = self.fit._df
        frequency_log: ndarray = df["FrequencyLog"].values
        result: ndarray = model(frequency_log, *self.fit.relaxations[r].get_saved_parameters_values())
        self._cole_cole_c[r].set_xdata(result.real)
        self._cole_cole_c[r].set_ydata(result.imag)
        self._chi_prime_c[r].set_ydata(result.real)
        self._chi_bis_c[r].set_ydata(result.imag)
        
        total = result
        for other in range(len(self.fit.relaxations)):
            if other != r:
                src = self._cole_cole_s[other]
                add(total, src.get_xdata().astype(complex), total)
                add(total, src.get_ydata().astype(complex), total)

        self._cole_cole_total_s.set_xdata(total.real)
        self._cole_cole_total_s.set_ydata(total.imag)
        self._chi_prime_total_s.set_ydata(total.real)
        self._chi_bis_total_s.set_ydata(total.imag)

        if redraw:
            self.canvas.draw()

    def _update_domains(self, result=None):
        df: DataFrame = self.fit._df
        span:float = df["FrequencyLog"].max() - df["FrequencyLog"].min()
        span_prime:float = df["ChiPrimeMol"].max() - df["ChiPrimeMol"].min()
        span_bis:float = df["ChiBisMol"].max() - df["ChiBisMol"].min()
        self.canvas.ax1.set_xbound(df["FrequencyLog"].min()-span*0.05, df["FrequencyLog"].max()+span*0.05)
        self.canvas.ax1.set_ybound(df["ChiPrimeMol"].min()-span_prime*0.05, df["ChiPrimeMol"].max()+span_prime*0.05)
        self.canvas.ax2.set_xbound(df["FrequencyLog"].min()-span*0.05, df["FrequencyLog"].max()+span*0.05)
        self.canvas.ax2.set_ybound(df["ChiBisMol"].min()-span_bis*0.05, df["ChiBisMol"].max()+span_bis*0.05)
        self.canvas.ax3.set_xbound(df["ChiPrimeMol"].min()-span_prime*0.05, df["ChiPrimeMol"].max()+span_prime*0.05)
        self.canvas.ax3.set_ybound(df["ChiBisMol"].min()-span_bis*0.05, df["ChiBisMol"].max()+span_bis*0.05)

        if result is not None:
            self.canvas.ax1.set_ybound(result.real.min()-span_prime*0.05, result.real.max()+span_prime*0.05)
            self.canvas.ax2.set_ybound(result.imag.min()-span_bis*0.05, result.imag.max()+span_bis*0.05)
            self.canvas.ax3.set_ybound(result.imag.min()-span_bis*0.05, result.imag.max()+span_bis*0.05)

    def on_point_deleted(self):
        self._update_domains()
        self._recreate_fit_plot()
        self._update_fit_plots()
        self._update_measurements_plots()

    def on_click(self, event):
        mouse = event.mouseevent

        tmp_time:float = time()
        if tmp_time - self._last_event_time < 0.1:
            return
        
        i: int
        for i, ax in enumerate([self.canvas.ax1, self.canvas.ax2, self.canvas.ax3]):
            if ax == mouse.inaxes:
                break

        x_str: str = "FrequencyLog"
        if i == 2:
            x_str = "ChiPrimeMol"

        try:
            x_data = event.artist.get_xdata().values.tolist()
        except AttributeError:
            x_data = event.artist.get_xdata().tolist()
            
        ind = event.ind[0]

        if mouse.button == mouse.button.LEFT:
            self.fit.hide_point(x_data[ind], x_str)

        if mouse.button == mouse.button.RIGHT:
            self.fit.delete_point(x_data[ind], x_str)

        self._last_event_time = time()

    def costF(self, p):
        rest = self.fit._df

        sum_real = 0
        sum_img = 0
        i = 0
        while i < len(self.fit.relaxations):
            r = model(rest["FrequencyLog"].values, p[0+i*5], p[1+i*5], p[2+i*5], p[3+i*5], p[4+i*5])
            sum_real += r.real
            sum_img += -r.imag

            i += 1

        dif_real = power(sum_real - rest['ChiPrimeMol'], 2)
        dif_img = power(sum_img - rest['ChiBisMol'], 2)


        return  dif_real + dif_img

    def make_auto_fit(self, auto: bool = False):
        p = []
        min = []
        max = []
        for r in range(len(self.fit.relaxations)):
            relaxation = self.fit.relaxations[r]
            p = p + list(relaxation.get_parameters_values())
            min = min + relaxation.get_parameters_min_bounds()
            max = max + relaxation.get_parameters_max_bounds()

        res = least_squares(self.costF, tuple(p), bounds=(min, max))

        

        for i, r in enumerate(self.fit.relaxations):
            for j, p in enumerate(r.parameters):
                p.set_value(res.x[j + i*len(r.parameters)])
