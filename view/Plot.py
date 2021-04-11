import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

class Plot(FigureCanvasQTAgg):
    def __init__(self, caption):
        fig, self.ax = plt.subplots(figsize=(5,4), dpi=100)
        super().__init__(fig)
        #self.setParent(parent)

        """Matplotlib Script"""
        t = np.arange(0.0, 2.0, 0.01)
        s = 1 + np.cos(2 * np.pi * t)

        self.ax.plot(t, s)

        self.ax.set(xlabel='time (s)', ylabel='voltage (mV)',
            title=caption)
        self.ax.grid()

        

    def change(self, msg=''):
        self.ax.cla()
        self.ax.set(xlabel='Zmieniona wiadomość dziłaj pls', title="Changed"+msg)
        t = np.arange(0.0, 2.0, 0.01)
        s = -1 + np.sin(2 * np.pi * t)
        self.ax.plot(t, s)
        self.ax.grid()

    def plotFromData():
        pass
