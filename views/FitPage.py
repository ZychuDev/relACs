from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout,
 QPushButton, QCheckBox, QTableWidget, QAbstractScrollArea,
 QAbstractItemView, QTableWidgetItem, QTabWidget, QDialog, QComboBox)
from PyQt6.QtCore import QSize, QMetaObject, QObject, Qt
from PyQt6.QtGui import QFont, QPalette, QBrush, QColor

from models import Fit, PARAMETER_NAME, Relaxation
from typing import get_args

from .ParameterSlider import ParameterSlider

from pandas import DataFrame # type: ignore

from matplotlib.figure import Figure # type: ignore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg # type: ignore
from matplotlib.colors import CSS4_COLORS # type: ignore
from matplotlib.ticker import LinearLocator # type: ignore

from matplotlib import use # type: ignore
import matplotlib.colors as mcolors

from numpy import ndarray, add, append, linspace


from functools import partial
use('Qt5Agg')

from time import time




class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width: int=10, height: int=5, dpi: int=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        #Order is importnat for legend display
        self.ax1 = fig.add_subplot(222)
        self.ax1.grid(True, linestyle='--', linewidth=1, color=CSS4_COLORS["silver"])
        self.ax1.xaxis.set_major_locator(LinearLocator(10))
        self.ax1.yaxis.set_major_locator(LinearLocator(8))
        self.ax1.set(title=r"$\chi^{\prime}$", xlabel=r"$\log {\frac{v}{Hz}}$", ylabel=r"$\chi^{\prime} /cm^3*mol^{-1}$")
        
        self.ax3 = fig.add_subplot(221)
        self.ax3.grid(True, linestyle='--', linewidth=1, color=CSS4_COLORS["silver"])
        self.ax3.xaxis.set_major_locator(LinearLocator(10))
        self.ax3.yaxis.set_major_locator(LinearLocator(8))
        self.ax3.set(title=r"Cole-Cole", xlabel=r"$\chi^{\prime} /cm^3*mol^{-1}$", ylabel=r"$\chi^{\prime \prime} / cm^3*mol^{-1}$")

        self.ax2 = fig.add_subplot(2,2, (3,4))
        self.ax2.grid(True, linestyle='--', linewidth=1, color=CSS4_COLORS["silver"])
        self.ax2.xaxis.set_major_locator(LinearLocator(10))
        self.ax2.yaxis.set_major_locator(LinearLocator(8))
        self.ax2.set(title=r"$\chi^{\prime \prime}$", xlabel=r"$\log {\frac{v}{Hz}}$", ylabel=r"$\chi^{\prime \prime} /cm^3*mol^{-1}$")

        fig.subplots_adjust(left=0.06, right=0.99, top=0.9, bottom=0.15)
        super(MplCanvas, self).__init__(fig)

class RelaxationTab(QWidget):
    def __init__(self):
        super().__init__()
        self.sliders: list[ParameterSlider] = []
        self.relaxation: Relaxation = None

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
        self.fit_error = fit_error
        self.setLayout(tab_layout)

    def set_relaxation(self, relaxation: Relaxation):
        if self.relaxation is not None:
            QObject.disconnect(self.cid) 
            QObject.disconnect(self.cid_2)
            for i, p in enumerate(self.relaxation.parameters):
                QObject.disconnect(self.p_cid[i])

        for i, s in enumerate(self.sliders):
            s.set_parameter(relaxation.parameters[i])

        self.relaxation = relaxation
        self.cid: QMetaObject.Connection = relaxation.all_parameters_changed.connect(self.update_errors)
        self.cid_2: QMetaObject.Connection  = relaxation.parameters_saved.connect(self.update_saved_errors)
        self.p_cid: list[QMetaObject.Connection] = []
        for i, p in enumerate(self.relaxation.parameters):
            self.p_cid.append(p.value_changed.connect(self.update_errors))
            
        self.update_errors()
        self.update_saved_errors()

    def update_errors(self):
        i:int
        for i, p in enumerate(self.relaxation.parameters):
            self.fit_error.setItem(1, i, QTableWidgetItem(f"{round(p.value, 8)} += {str(round(p.error, 8))}"))
        self.fit_error.setItem(1, i+1, QTableWidgetItem(str(round(self.relaxation.residual_error, 8))))

    def update_saved_errors(self):
        for i, p in enumerate(self.relaxation.saved_parameters):
            self.fit_error.setItem(0, i, QTableWidgetItem(f"{round(p.value, 8)} += {str(round(p.error, 8))}"))
        self.fit_error.setItem(0, i+1, QTableWidgetItem(str(round(p.error, 8))))

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
        self.resolution: int = 100
        self.colors_names: list[str] = ["tab:green", "tab:red", "tab:purple", "tab:brown", "tab:pink"]

        p: QPalette = self.palette()
        p.setColor(self.backgroundRole(), Qt.GlobalColor.white)
        self.setPalette(p)
        self.setAutoFillBackground(True)

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
        self.save_button.clicked.connect(self.save_all_relaxations)
        self.reset_current_button.clicked.connect(self.reset_all_relaxations)
        self.copy_parameters_button.clicked.connect(self.copy_parameters)
        self.cycle_next.clicked.connect(self.on_cycle_next_clicked)
        self.cycle_previous.clicked.connect(self.on_cycle_previous_clicked)

    def make_auto_fit(self):
        self.fit.make_auto_fit()

    def on_cycle_next_clicked(self):
        c = self.fit._collection
        new_fit = c.get_item_model(c.get_next(self.fit.name))
        if self.remember_check_box.isChecked():
            for i, r in enumerate(new_fit.relaxations):
                r.copy(self.fit.relaxations[i])
        self.fit._collection.change_displayed_item(new_fit.name)

    def on_cycle_previous_clicked(self):
        c = self.fit._collection
        fit: Fit = c.get_item_model(c.get_previous(self.fit.name))
        if self.remember_check_box.isChecked():
            for i, r in enumerate(fit.relaxations):
                r.copy(self.fit.relaxations[i])
        self.fit._collection.change_displayed_item(fit.name)

    def save_all_relaxations(self):
        for r in self.fit.relaxations:
            r.save()

    def reset_all_relaxations(self):
        for r in self.fit.relaxations:
            r.reset()

    def copy_parameters(self):
        dlg: QDialog = QDialog()
        dlg.setWindowTitle("Choose fit item to copy from")
        layout = QHBoxLayout()
        button = QPushButton("Copy")
        combo_box: QComboBox = QComboBox()
        layout.addWidget(combo_box)
        layout.addWidget(button)
        dlg.setLayout(layout)

        for n in self.fit._collection.get_names():
            combo_box.addItem(n)

        button.clicked.connect(lambda: self.copy_all_relaxations(combo_box.currentText(), dlg))
        dlg.exec()

    def copy_all_relaxations(self, src_name: str, dlg: QDialog):
        if self.fit._collection is None:
            return
        other = self.fit._collection.get_item_model(src_name)
        for i, r in enumerate(self.fit.relaxations):
            r.copy(other.relaxations[i])
        dlg.close()

    def set_fit(self, fit:Fit):
        if self.fit is not None:
            self.fit.df_changed.disconnect()
            self.fit.df_point_deleted.disconnect()
            for r in self.fit.relaxations:
                r.parameters_saved.disconnect()
                r.all_parameters_changed.disconnect()
                for p in r.parameters:
                    p.value_changed.disconnect()
                    

        self.fit = fit
        self.fit.df_changed.connect(self._update_measurements_plots)
        self.fit.df_point_deleted.connect(self.on_point_deleted)
        self.fit.name_changed.connect(lambda new_name: self.title_label.setText(new_name))
        for i, r in enumerate(self.fit.relaxations):
            r.parameters_saved.connect(self._recreate_and_draw)
            r.all_parameters_changed.connect(self._recreate_fit_plot)
            for p in r.parameters:
                p.value_changed.connect(partial(self._update_fit_plot_for_one_relax, i, True))


        self.title_label.setText(fit.name)

        self.left_side.set_fit(fit)

        self._recreate_fit_plot()
        self._update_fit_plots()
        self._update_measurements_plots()
        self._update_domains()
        self.canvas.draw()



    def _update_measurements_plots(self):
        if self.fit is None:
            return

        df: DataFrame = self.fit._df
        hidden: DataFrame = df.loc[df["Hidden"] == True]
        visible: DataFrame = df.loc[df["Hidden"] == False]

        if self._chi_prime_m is None or self._chi_bis_m is None or self._cole_cole_m is None:
            self._chi_prime_m = self.canvas.ax1.plot(visible["FrequencyLog"].values, visible["ChiPrimeMol"], "o", c=mcolors.TABLEAU_COLORS["tab:blue"], picker=self.picker_radius)[0]
            self._chi_prime_m_h = self.canvas.ax1.plot(hidden["FrequencyLog"].values, hidden["ChiPrimeMol"], "o", c=mcolors.TABLEAU_COLORS["tab:orange"], picker=self.picker_radius)[0]
            self._chi_bis_m = self.canvas.ax2.plot(visible["FrequencyLog"].values, visible["ChiBisMol"], "o", c=mcolors.TABLEAU_COLORS["tab:blue"], label="Mesurement points", picker=self.picker_radius )[0]
            self._chi_bis_m_h = self.canvas.ax2.plot(hidden["FrequencyLog"].values, hidden["ChiBisMol"], "o", c=mcolors.TABLEAU_COLORS["tab:orange"], label="Hidden points", picker=self.picker_radius )[0]
            self._cole_cole_m = self.canvas.ax3.plot(visible["ChiPrimeMol"].values, visible["ChiBisMol"], "o", c=mcolors.TABLEAU_COLORS["tab:blue"], picker=self.picker_radius)[0]
            self._cole_cole_m_h = self.canvas.ax3.plot(hidden["ChiPrimeMol"].values, hidden["ChiBisMol"], "o", c=mcolors.TABLEAU_COLORS["tab:orange"], picker=self.picker_radius)[0]
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

        l = self.canvas.ax2.legend()
        l.set_draggable(True)
        l.set_zorder(1000)
        self.canvas.draw()
        

    def _update_fit_plots(self):
        if self.fit is None:
            return
        relax_nr: int = len(self.fit.relaxations)
        if len(self._chi_prime_c) != relax_nr or len(self._chi_bis_c) != relax_nr or len(self._cole_cole_c) != relax_nr:
            self._recreate_fit_plot()
        else:
            for r in range(relax_nr):
                self._update_fit_plot_for_one_relax(r)

    def _recreate_and_draw(self):
        self._recreate_fit_plot()
        self.canvas.draw()

    def _recreate_fit_plot(self):
        for l in self._chi_prime_c:
            l.remove()
        for l in self._chi_bis_c:
            l.remove()
        for l in self._cole_cole_c:
            l.remove()
        for l in self._chi_prime_s:
            l.remove()
        for l in self._chi_bis_s:
            l.remove()
        for l in self._cole_cole_s:
            l.remove()

        self._chi_prime_c = []
        self._chi_bis_c = []
        self._cole_cole_c = []

        self._chi_prime_s = []
        self._chi_bis_s = []
        self._cole_cole_s = []

        if self._chi_prime_total is not None:
            self._chi_prime_total.remove()
            self._chi_prime_total = None

        if self._chi_bis_total is not None:
            self._chi_bis_total.remove()
            self._chi_bis_total = None
        
        if self._cole_cole_total is not None:
            self._cole_cole_total.remove()
            self._cole_cole_total = None

        if self._chi_prime_total_s is not None:
            self._chi_prime_total_s.remove()
            self._chi_prime_total_s = None
        
        if self._chi_bis_total_s is not None:
            self._chi_bis_total_s.remove()
            self._chi_bis_total_s = None
        
        if self._cole_cole_total_s is not None:
            self._cole_cole_total_s.remove()
            self._cole_cole_total_s = None

        df: DataFrame = self.fit._df
        relax_nr: int = len(self.fit.relaxations)
        frequency_log: ndarray = df["FrequencyLog"].values
        frequency_log = linspace(frequency_log.min(), frequency_log.max(), self.resolution)

        total = None
        total_s = None
        for r in range(relax_nr):
            color = mcolors.TABLEAU_COLORS[self.colors_names[r]]
            result: ndarray = Fit.model(frequency_log, *self.fit.relaxations[r].get_parameters_values())
            result_s: ndarray = Fit.model(frequency_log, *self.fit.relaxations[r].get_saved_parameters_values())

            self._chi_prime_c.append(self.canvas.ax1.plot(frequency_log, result.real, "--", c=color)[0])
            self._chi_bis_c.append(self.canvas.ax2.plot(frequency_log, -result.imag, "--", c=color, label=f"Relaxation nr {r+1}")[0])
            self._cole_cole_c.append(self.canvas.ax3.plot(result.real, -result.imag, "--", c=color)[0])
            
            self._chi_prime_s.append(self.canvas.ax1.plot(frequency_log, result_s.real, "-", c=color)[0])
            self._chi_bis_s.append(self.canvas.ax2.plot(frequency_log, -result_s.imag, "-", label=f"Saved Relaxation nr {r+1}", c=color)[0])
            self._cole_cole_s.append(self.canvas.ax3.plot(result_s.real, -result_s.imag, "-", c=color)[0])

            if relax_nr > 1:
                if total is None:
                    total = result.copy()
                else:
                    add(total, result.copy(), total)

                if total_s is None:
                    total_s = result_s.copy()
                else:
                    add(total_s, result_s.copy(), total_s)
        
        if relax_nr > 1:
            color = mcolors.TABLEAU_COLORS[self.colors_names[relax_nr]]
            self._chi_prime_total = self.canvas.ax1.plot(frequency_log, total.real, "--", c=color)[0]
            self._chi_bis_total = self.canvas.ax2.plot(frequency_log, -total.imag, "--", label="Sum of relaxations", c=color)[0]
            self._cole_cole_total = self.canvas.ax3.plot(total.real, -total.imag, "--", c=color)[0]
            self._chi_prime_total_s = self.canvas.ax1.plot(frequency_log, total_s.real, "-", c=color)[0]
            self._chi_bis_total_s = self.canvas.ax2.plot(frequency_log, -total_s.imag, "-", label="Saved sum of relaxations", c=color)[0]
            self._cole_cole_total_s = self.canvas.ax3.plot(total_s.real, -total_s.imag, "-", c=color)[0]
 
    def _update_fit_plot_for_one_relax(self, r: int, redraw: bool=False): 
        df: DataFrame = self.fit._df
        frequency_log: ndarray = df["FrequencyLog"].values
        frequency_log = linspace(frequency_log.min(), frequency_log.max(), self.resolution)
        result: ndarray = Fit.model(frequency_log, *self.fit.relaxations[r].get_parameters_values())
        self._cole_cole_c[r].set_xdata(result.real)
        self._cole_cole_c[r].set_ydata(-result.imag)
        self._chi_prime_c[r].set_ydata(result.real)
        self._chi_bis_c[r].set_ydata(-result.imag)

        total = None
        if len(self.fit.relaxations) > 1:
            total = result.copy()
            for other in range(len(self.fit.relaxations)):
                if other != r:
                    src = self._cole_cole_c[other]
                    add(total, src.get_xdata().astype(complex).copy(), total)
                    add(total, -src.get_ydata().astype(complex)*1j, total)

            self._cole_cole_total.set_xdata(total.real)
            self._cole_cole_total.set_ydata(-total.imag)
            self._chi_prime_total.set_ydata(total.real)
            self._chi_bis_total.set_ydata(-total.imag)


        if redraw:
            self._update_domains()
            self.canvas.draw()


    def _update_domains(self, result=None, total=None):
        df: DataFrame = self.fit._df

        span:float = df["FrequencyLog"].max() - df["FrequencyLog"].min()
        self.canvas.ax1.set_xbound(df["FrequencyLog"].min()-span*0.05, df["FrequencyLog"].max()+span*0.05)
        self.canvas.ax2.set_xbound(df["FrequencyLog"].min()-span*0.05, df["FrequencyLog"].max()+span*0.05)

        if self._chi_bis_m is not None:
            lower_bis: float
            upper_bis: float

            values_bis = self._chi_bis_m.get_ydata()
            for l in self._chi_bis_c:
                values_bis = append(values_bis, l.get_ydata())
            for l in self._chi_bis_s:
                values_bis = append(values_bis, l.get_ydata())
            values_bis = append(values_bis, self._chi_bis_m_h.get_ydata())
            if len(self.fit.relaxations) > 1:
                values_bis = append(values_bis, self._chi_bis_total.get_ydata())
                values_bis = append(values_bis, self._chi_bis_total_s.get_ydata())
            lower_bis = min(values_bis)
            upper_bis = max(values_bis)

            values_prime = self._chi_prime_m.get_ydata()
            for l in self._chi_prime_c:
                values_prime = append(values_prime, l.get_ydata())
            for l in self._chi_prime_s:
                values_prime = append(values_prime, l.get_ydata())
            values_prime = append(values_prime, self._chi_prime_m_h.get_ydata())
            if len(self.fit.relaxations) > 1:
                values_prime = append(values_prime, self._chi_prime_total.get_ydata())
                values_prime = append(values_prime, self._chi_prime_total_s.get_ydata())
            lower_prime = min(values_prime)
            upper_prime = max(values_prime)
            
            span_bis = upper_bis - lower_bis
            self.canvas.ax2.set_ybound(lower_bis-span_bis*0.05, upper_bis+span_bis*0.05)
            self.canvas.ax3.set_ybound(lower_bis-span_bis*0.05, upper_bis+span_bis*0.05)
            
            span_prime = upper_prime - lower_prime
            self.canvas.ax1.set_ybound(lower_prime-span_prime*0.05, upper_prime+span_prime*0.05)
            self.canvas.ax3.set_xbound(lower_prime-span_prime*0.05, upper_prime+span_prime*0.05)


    def on_point_deleted(self):
        self._recreate_fit_plot()
        self._update_domains()

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



