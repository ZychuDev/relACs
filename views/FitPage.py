from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import QAbstractTableModel, QSize, Qt
from PyQt6.QtGui import QFont
from models import Fit

from matplotlib.figure import Figure # type: ignore
from matplotlib.artist import Artist # type: ignore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width: int=10, height: int=5, dpi: int=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax1 = fig.add_subplot(221)
        self.ax1.grid()
        self.ax1.set(title=r"$\chi^{\prime}$", xlabel=r"$\log {\frac{v}{Hz}}$", ylabel=r"$\chi^{\prime} /cm^3*mol^{-1}$")
        self.ax2 = fig.add_subplot(222)
        self.ax2.grid()
        self.ax2.set(title=r"$\chi^{\prime \prime}$", xlabel=r"$\log {\frac{v}{Hz}}$", ylabel=r"$\chi^{\prime \prime} /cm^3*mol^{-1}$")
        self.ax3 = fig.add_subplot(2,2, (3,4))
        self.ax3.grid()
        self.ax3.set(title=r"Cole-Cole", xlabel=r"$\chi^{\prime} /cm^3*mol^{-1}$", ylabel=r"$\chi^{\prime \prime} / cm^3*mol^{-1}$")
        fig.subplots_adjust(left=0.06, right=0.99, top=0.9, bottom=0.15)
        super(MplCanvas, self).__init__(fig)

class FitPage(QWidget):
    def __init__(self):
        super().__init__()
        self.fit: Fit = None
        self.picker_radius: int = 5

        vertical_layout: QVBoxLayout = QVBoxLayout()

        self.title_label: QLabel = QLabel("Title")
        self.title_label.setMaximumSize(QSize(16777215, 45))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("{color: #C0BBFE}")
        font:QFont = QFont()
        font.setPointSize(22)
        font.setBold(True)
        font.setWeight(100)
        self.title_label.setFont(font)

        vertical_layout.addWidget(self.title_label, stretch=1)

        self.canvas: MplCanvas = MplCanvas(self, width=5, height=4, dpi=100)
        vertical_layout.addWidget(self.canvas)

        self.setLayout(vertical_layout)

    def set_fit(self, fit:Fit):
        if self.fit is not None:
            pass

        self.fit = fit
        self.fit.name_changed.connect(lambda new_name: self.title_label.setText(new_name))

        self.title_label.setText(fit.name)


        
