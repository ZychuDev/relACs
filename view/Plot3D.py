import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from mpl_toolkits.mplot3d import Axes3D

class Plot3D(FigureCanvasQTAgg): # Class for 3D window
    def __init__(self):
        self.fig = plt.figure(figsize=(1,1), dpi = 100 )
        super().__init__(self.fig) # creating FigureCanvas
        self.axes = self.fig.gca(projection='3d') # generates 3D Axes object
        self.setWindowTitle("Main") # sets Window title

    def DrawGraph(self, x, y, z): # Fun for Graph plotting
        self.axes.clear()
        self.axes.plot_surface(x, y, z) # plots the 3D surface plot
        self.draw()

    def change(self): # Invoked when the ComboBox index changes
        x = np.linspace(np.random.randint(-5,0), np.random.randint(5,10), 40) # X coordinates
        y = np.linspace(np.random.randint(-5,0), np.random.randint(5,10), 40) # Y coordinates


        X, Y = np.meshgrid(x, y) # Forming MeshGrid
        Z = self.f(X, Y)
        self.ThreeDWin.DrawGraph(X, Y, Z) # call Fun for Graph plot