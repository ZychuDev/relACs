from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableView, QHeaderView
from PyQt6.QtCore import QAbstractTableModel, QSize, Qt
from PyQt6.QtGui import QFont

from models import Measurement

from pandas import DataFrame, Series # type: ignore

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg # type: ignore
from matplotlib.figure import Figure # type: ignore
from matplotlib.artist import Artist # type: ignore
from matplotlib import use # type: ignore
use('Qt5Agg')

from time import time

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width: int=10, height: int=5, dpi: int=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax1 = fig.add_subplot(131)
        self.ax1.grid()
        self.ax1.set(title=r"$\chi^{\prime}$", xlabel=r"$\log {\frac{v}{Hz}}$", ylabel=r"$\chi^{\prime} /cm^3*mol^{-1}$")
        self.ax2 = fig.add_subplot(132)
        self.ax2.grid()
        self.ax2.set(title=r"$\chi^{\prime \prime}$", xlabel=r"$\log {\frac{v}{Hz}}$", ylabel=r"$\chi^{\prime \prime} /cm^3*mol^{-1}$")
        self.ax3 = fig.add_subplot(133)
        self.ax3.grid()
        self.ax3.set(title=r"Cole-Cole", xlabel=r"$\chi^{\prime} /cm^3*mol^{-1}$", ylabel=r"$\chi^{\prime \prime} / cm^3*mol^{-1}$")
        fig.subplots_adjust(left=0.06, right=0.99, top=0.9, bottom=0.15)
        super(MplCanvas, self).__init__(fig)

class TableModel(QAbstractTableModel):

    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            row, col = self._data.shape
            if index.column() != col-1:
                value = self._data.iloc[index.row(), index.column()]
                return str(value)
            else:
                value = self._data.iloc[index.row(), index.column()]
                if value == 0.0:
                    return "Visible"
                else:
                    return "Hidden"
        
        if (role == Qt.ItemDataRole.TextAlignmentRole):
             return Qt.AlignmentFlag.AlignCenter

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])
                

class DataExplorer(QWidget):
    def __init__(self):
        super().__init__()
        self.measurement:Measurement = None
        self.picker_radius: int = 5

        vertical_layout: QVBoxLayout = QVBoxLayout()

        self.title_label = QLabel("Title")
        self.title_label.setMaximumSize(QSize(16777215, 45))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font:QFont = QFont()
        font.setPointSize(22)
        font.setBold(True)
        font.setWeight(100)
        self.title_label.setFont(font)

        vertical_layout.addWidget(self.title_label, stretch=1)

        self.sc:MplCanvas = MplCanvas(self, width=5, height=4, dpi=100)
        self._chi_prime_plot = None
        self._chi_bis_plot = None
        self._cole_cole_plot = None
        self._chi_prime_plot_2 = None
        self._chi_bis_plot_2 = None
        self._cole_cole_plot_2 = None
        self.update_plots()

        vertical_layout.addWidget(self.sc, stretch=6)

        self.table: QTableView = QTableView()
        self.table.verticalHeader().setHidden(True)

        vertical_layout.addWidget(self.table, stretch=4)

        
        self.setLayout(vertical_layout)

        self.cid:int = self.sc.mpl_connect('pick_event', self.on_click)
        self._last_event_time:float = time()

    def set_measurement(self, measurement:Measurement):
        if self.measurement is not None:
            self.measurement.df_changed.disconnect()
            self.measurement.name_changed.disconnect()

        self.measurement = measurement
        self.measurement.df_changed.connect(self.update_plots)
        self.measurement.df_changed.connect(self.table.update)
        self.measurement.name_changed.connect(lambda new_name: self.title_label.setText(new_name))
        self.title_label.setText(measurement.name)

        self.table_model = TableModel(self.measurement._df)
        self.table.setModel(self.table_model)
        header = self.table.horizontalHeader() 
        font: QFont = header.font()
        font.setBold(True)
        font.setWeight(100)
        header.setFont(font)

        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        for i in range(1, self.measurement._df.shape[1]):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

        header.setStretchLastSection(True)

        
        # self.update_domains()
        self.update_plots()

    def update_plots(self):
        if self.measurement is None:
            return

        df:DataFrame = self.measurement._df
        hidden: DataFrame = df.loc[df["Hidden"] == True]
        visible: DataFrame = df.loc[df["Hidden"] == False]

        if self._chi_prime_plot is None or self._chi_bis_plot is None or self._cole_cole_plot is None:
            self._chi_prime_plot = self.sc.ax1.plot(visible["FrequencyLog"].values, visible["ChiPrimeMol"], "o", picker=self.picker_radius)[0]
            self._chi_prime_plot_2 = self.sc.ax1.plot(hidden["FrequencyLog"].values, hidden["ChiPrimeMol"], "o", picker=self.picker_radius)[0]
            self._chi_bis_plot = self.sc.ax2.plot(visible["FrequencyLog"].values, visible["ChiBisMol"], "o", picker=self.picker_radius )[0]
            self._chi_bis_plot_2 = self.sc.ax2.plot(hidden["FrequencyLog"].values, hidden["ChiBisMol"], "o", picker=self.picker_radius )[0]
            self._cole_cole_plot = self.sc.ax3.plot(visible["ChiPrimeMol"].values, visible["ChiBisMol"], "o", picker=self.picker_radius)[0]
            self._cole_cole_plot_2 = self.sc.ax3.plot(hidden["ChiPrimeMol"].values, hidden["ChiBisMol"], "o", picker=self.picker_radius)[0]
        else:
            self._chi_prime_plot.set_xdata(visible["FrequencyLog"])
            self._chi_prime_plot_2.set_xdata(hidden["FrequencyLog"])
            self._chi_bis_plot.set_xdata(visible["FrequencyLog"])
            self._chi_bis_plot_2.set_xdata(hidden["FrequencyLog"])
            self._cole_cole_plot.set_xdata(visible["ChiPrimeMol"])
            self._cole_cole_plot_2.set_xdata(hidden["ChiPrimeMol"])

            self._chi_prime_plot.set_ydata(visible["ChiPrimeMol"])
            self._chi_prime_plot_2.set_ydata(hidden["ChiPrimeMol"])
            self._chi_bis_plot.set_ydata(visible["ChiBisMol"])
            self._chi_bis_plot_2.set_ydata(hidden["ChiBisMol"])
            self._cole_cole_plot.set_ydata(visible["ChiBisMol"])
            self._cole_cole_plot_2.set_ydata(hidden["ChiBisMol"])

        self.update_domains()
        self.sc.draw()

    def update_domains(self):

        df: DataFrame = self.measurement._df
        span:float = df["FrequencyLog"].max() - df["FrequencyLog"].min()
        span_prime:float = df["ChiPrimeMol"].max() - df["ChiPrimeMol"].min()
        span_bis:float = df["ChiBisMol"].max() - df["ChiBisMol"].min()
        self.sc.ax1.set_xbound(df["FrequencyLog"].min()-span*0.05, df["FrequencyLog"].max()+span*0.05)
        self.sc.ax1.set_ybound(df["ChiPrimeMol"].min()-span_prime*0.05, df["ChiPrimeMol"].max()+span_prime*0.05)
        self.sc.ax2.set_xbound(df["FrequencyLog"].min()-span*0.05, df["FrequencyLog"].max()+span*0.05)
        self.sc.ax2.set_ybound(df["ChiBisMol"].min()-span_bis*0.05, df["ChiBisMol"].max()+span_bis*0.05)
        self.sc.ax3.set_xbound(df["ChiPrimeMol"].min()-span_prime*0.05, df["ChiPrimeMol"].max()+span_prime*0.05)
        self.sc.ax3.set_ybound(df["ChiBisMol"].min()-span_bis*0.05, df["ChiBisMol"].max()+span_bis*0.05)

    def on_click(self, event):
        mouse = event.mouseevent
        tmp_time:float = time()
        if tmp_time - self._last_event_time < 0.1:
            return
        
        i: int
        for i, ax in enumerate([self.sc.ax1, self.sc.ax2, self.sc.ax3]):
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
            self.measurement.hide_point(x_data[ind], x_str)

        if mouse.button == mouse.button.RIGHT:
            self.measurement.delete_point(x_data[ind], x_str)

        self._last_event_time = time()
        