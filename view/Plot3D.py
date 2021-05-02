from PyQt5.QtCore import QLocale
import numpy as np
import matplotlib.pyplot as plt
from numpy.core.records import get_remaining_size
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from mpl_toolkits.mplot3d import Axes3D

from .Validator import Validator

from numba import jit
from scipy.optimize._lsq.least_squares import least_squares
from scipy.interpolate import interp1d

from functools import partial

class Plot3D(FigureCanvasQTAgg): 

    nr_of_connections = 0

    def __init__(self):
        self.fig = plt.figure(figsize=(1,1), dpi = 100 )
        super().__init__(self.fig) # creating FigureCanvas
        self.axes = self.fig.gca(projection='3d') # generates 3D Axes object
        self.setWindowTitle("Main") # sets Window title

    def refresh(self): # Fun for Graph plotting
        self.axes.clear()
        # self.axes.plot_surface(x, y, z) # plots the 3D surface plot
        x = np.linspace(0,1,60)
        y = np.linspace(0,5000, 60)
        X, Y = np.meshgrid(x,y)

        a = list(self.tau_item.current.values())
        Z = -np.log10(self.model(X,Y,a[0],a[1],a[2],a[3],a[4],a[5],a[6],a[7],a[8],a[9]))
        self.axes.plot_wireframe(X, Y, Z, rstride=1, cstride=1)
        t_invert = [1/t for t in self.tau_item.temp]
        self.axes.scatter(t_invert, self.tau_item.field, self.tau_item.tau, marker='o')
        self.draw()

    def change(self, tau_item): # Invoked when the ComboBox index changes
        self.tau_item = tau_item
        self.refresh(tau_item.tau, tau_item.temp, tau_item.field) # call Fun for Graph plot

    @jit()
    def model(self, temp, field, Adir, Ndir, B1, B2, B3, CRaman, Nraman, NHraman, Tau0, DeltaE):
        return Adir*(1/temp)*np.power(field,Ndir) \
        + B1*(1+B3*field*field)/(1+B2*field*field) \
        + CRaman*np.power(field, NHraman) * np.power((1/temp), Nraman) \
        + 1/Tau0 *np.exp(-DeltaE/(1/temp))

    def cost_function(self, p):
        return np.abs(self.model(self.tau_item.temp, self.tau_item.field,
        p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9]) - self.tau_item.tau)

    def make_auto_fit(self):
        r = AppState.ranges
        ui = self.tau_item.ui
        params = ui.slider3D.keys() 
        lower_bound = []
        upper_bound = []
        for p in params:
            lower_bound.append(r[p][0])
            upper_bound.append(r[p][1])
        b = (lower_bound, upper_bound)
        eps = 0.000000000001   


        res = least_squares(self.cost_function, tuple(self.tau_item.current.values()), bounds=b)
        i = 0
        for key in self.tau_item.current:
            self.tau_item.current[key] = res.x[i]
            i += 1

        for key in ui.edit3D:
            ui.edit3D[key].setText(str(round(self.tau_item.current[key], 6)))

        self.value_edited()

    def value_edited(self, k):
        print('Edited')
        print(k)
        sliders = self.tau_item.ui.slider3D
        edits = self.tau_item.ui.edit3D
        self.edit_to_slider(sliders[k], edits[k], k)

        self.tau_item.show()

    def edit_to_slider(self, slider, edit, name):
        v = str(edit.text())
        if v == '':
            v = self.tau_item.current[name]
        self.tau_item.current[name] = float(v)
        slider.blockSignals(True)
        slider.setValue(self.map_value_reverse(slider, edit , name))
        slider.blockSignals(False)

        if name in ('Adir', 'B1', 'B2', 'B3', 'Tau0'):
            self.tau_item.current[name] = np.power(10, self.tau_item.current[name])

    def slider_to_edit(self, slider, edit, name):
        self.tau_item.current[name] = self.map_value(slider, name)
        edit.blockSignals(True)
        edit.setText(str(self.tau_item.current[name]))
        edit.blockSignals(False)

        if name in ('Adir', 'B1', 'B2', 'B3', 'Tau0'):
            self.tau_item.current[name] = np.power(10, self.tau_item.current[name])

    def map_value_reverse(self, slider, edit, name=""):
        r = AppState.ranges
        m = interp1d([r[name][0], r[name][1]], [slider.minimum(), slider.maximum()])
        v = str(edit.text())
        if v == '':
            v = self.tau_item.current[name]
        v = float(v)
        v = float(m(v))
        return round(v)

    def map_value(self, slider, name=""):
        max = AppState.ranges[name][1]
        min = AppState.ranges[name][0]
        leftSpan = slider.maximum() - slider.minimum()
        rightSpan = max - min
        valueScaled = float(slider.value() - slider.minimum()) / float(leftSpan)
        return round(min + (valueScaled * rightSpan),2)

    def change(self, item):
        self.tau_item = item
        self.name = item.name

        for k in item.ui.edit3D:
            item.ui.edit3D[k].setValidator(Validator(item, k,item.ui.edit3D[k]))

        if Plot3D.nr_of_connections == 1:
            for k in item.ui.slider3D:
                item.ui.slider3D[k].valueChanged.disconnect()

            #item.ui.pushButtonFit3D.clicked.disconnect()

            for k in item.ui.edit3D:
                item.ui.edit3D[k].editingFinished.disconnect()
            Plot3D.nr_of_connections = 0

        Plot3D.nr_of_connections += 1
        for k in item.ui.slider3D:
            f = partial (self.value_changed, k)
            item.ui.slider3D[k].valueChanged.connect(f)

        #item.ui.pushButtonFit3D.clicked.connect(self.make_auto_fit)

        for k in item.ui.edit3D:
            f = partial (self.value_edited, k)
            item.ui.edit3D[k].editingFinished.connect(f)

        self.refresh()

    def value_changed(self, k):
        self.slider_to_edit(self.tau_item.ui.slider3D[k], self.tau_item.ui.edit3D[k], k)
        self.tau_item.show()
        print('Value changed:')
        print(k)

        

        


