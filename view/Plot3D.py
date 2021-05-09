from math import inf
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
from scipy import linalg

from functools import partial

class Plot3D(FigureCanvasQTAgg): 
    def __init__(self):
        self.fig = plt.figure(figsize=(1,1), dpi = 100, constrained_layout=True )
        super().__init__(self.fig) # creating FigureCanvas
        self.axes = self.fig.gca(projection='3d') # generates 3D Axes object
        self.setWindowTitle("Main") # sets Window title

        self.nr_of_connections = 0

        # self.fig.constrained_layout(True)
        # self.fig.subplots_adjust(left=-0.11)

    def refresh(self): # Fun for Graph plotting
        self.axes.clear()
        # self.axes.plot_surface(x, y, z) # plots the 3D surface plot
        x = np.linspace(self.tau_item.temp.min(),self.tau_item.temp.max(),60)
        y = np.linspace(0,5000, 60)
        X, Y = np.meshgrid(x,y)

        a = list(self.tau_item.current.values())
        Z = -np.log10(self.model(X,Y,a[0],a[1],a[2],a[3],a[4],a[5],a[6],a[7],a[8],a[9]))

        x = [1/t for t in x]
        X, Y = np.meshgrid(x,y)
        self.axes.plot_wireframe(X, Y, Z, rstride=1, cstride=1)
        t_invert = [1/t for t in self.tau_item.temp]
        self.axes.scatter(t_invert, self.tau_item.field, np.log10(self.tau_item.tau.tolist()), marker='o')
        self.draw()


    def model(self, temp, field, Adir, Ndir, B1, B2, B3, CRaman, Nraman, NHraman, Tau0, DeltaE):
        return Adir*temp*(field**Ndir) \
        + B1*(1+B3*field*field)/(1+B2*field*field) \
        + CRaman*np.power(field if field.all() != 0 else 1, NHraman ) * np.power(temp, Nraman) \
        + Tau0 *np.exp(-DeltaE/(temp))

    def cost_function(self, p):
        return np.power(self.model(self.tau_item.temp, self.tau_item.field,
        p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9]) - (1/self.tau_item.tau), 2)

    def make_auto_fit(self):
        np.seterr(divide = 'ignore') 
        r = AppState.ranges
        ui = self.tau_item.ui
        params = ui.slider3D.keys() 
        # lower_bound = [0,0,0,0,0,0,0,0,0,0]
        # upper_bound = [1e-31,1e-31,1e-31,1e-31,1e-31,1e-31,1e-31,1e-31,1e-31,1e-31]
        lower_bound = []
        upper_bound = []
        for p in self.tau_item.current:
            if p in AppState.log_params:
                lower_bound.append(10**r[p][0])
                upper_bound.append(10**r[p][1])
            else:
                lower_bound.append(r[p][0])
                upper_bound.append(r[p][1])

        b = (lower_bound, upper_bound)

        i = 0
        for k in self.tau_item.ui.edit3D:
            if self.tau_item.current[k] < b[0][i]:
                self.tau_item.current[k] = b[0][i]
            if self.tau_item.current[k] > b[1][i]:
                self.tau_item.current[k] = b[1][i]
            i += 1
        
        print(self.tau_item.current[k])
        print(b)
        eps = 0.000000001   

        i = 0
        for k in self.tau_item.ui.check3D:
            if self.tau_item.ui.check3D[k].isChecked():
                b[0][i] = max(self.tau_item.current[k] - eps, b[0][i])
                b[1][i] = min(self.tau_item.current[k] + eps, b[1][i])
            i += 1

        i = 0
        for k in self.tau_item.ui.check3D_2:
            if self.tau_item.ui.check3D_2[k].isChecked():
                self.tau_item.current[k] = 0
                b[0][i] = 0
                b[1][i] = 1e-64
            i += 1

        

        res = least_squares(self.cost_function, tuple(self.tau_item.current.values()), bounds = b)
        J = res.jac
        i = 0
        for key in self.tau_item.current:
            self.tau_item.current[key] = res.x[i]
            i += 1

        for key in ui.edit3D:
            if key in AppState.log_params:
                ui.edit3D[key].setText(str(np.log10(self.tau_item.current[key])))
                print(np.log10(self.tau_item.current[key]))
                print(str(np.log10(self.tau_item.current[key])))
                print('***')
            else:
                ui.edit3D[key].setText(str(self.tau_item.current[key]))

        
        for k in ui.edit3D:
            # if ui.blockedOnZero[k].isChecked() == False:
            self.value_edited(k)

        U, s, Vh = linalg.svd(res.jac, full_matrices=False)
        tol = np.finfo(float).eps*s[0]*max(res.jac.shape)
        w = s > tol
        cov = (Vh[w].T/s[w]**2) @ Vh[w]  # robust covariance matrix

        chi2dof = np.sum(res.fun**2)/(res.fun.size - res.x.size)
        cov *= chi2dof
        
        perr = np.sqrt(np.diag(cov))
        self.tau_item.error = perr
        print(perr)


    def value_edited(self, k):
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

        if name in AppState.log_params:
            self.tau_item.current[name] = np.power(10, self.tau_item.current[name])

    def slider_to_edit(self, slider, edit, name):
        self.tau_item.current[name] = self.map_value(slider, name)
        edit.blockSignals(True)
        edit.setText(str(self.tau_item.current[name]))
        edit.blockSignals(False)

        if name in AppState.log_params:
            self.tau_item.current[name] = np.power(10, self.tau_item.current[name])

    def map_value_reverse(self, slider, edit, name=""):
        r = AppState.ranges
        m = interp1d([r[name][0], r[name][1]], [slider.minimum(), slider.maximum()])
        v = str(edit.text())
        if v == '':
            v = self.tau_item.current[name]
        v = float(v)
        
        try:
           v = float(m(v))
        except ValueError as e:
            print(e)
            v = 0

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

        if self.nr_of_connections == 1:
            for k in item.ui.slider3D:
                item.ui.slider3D[k].valueChanged.disconnect()

            item.ui.pushButton_fit3d.clicked.disconnect()

            for k in item.ui.edit3D:
                item.ui.edit3D[k].editingFinished.disconnect()
            self.nr_of_connections = 0

        self.nr_of_connections += 1
        for k in item.ui.slider3D:
            f = partial (self.value_changed, k)
            item.ui.slider3D[k].valueChanged.connect(f)

        item.ui.pushButton_fit3d.clicked.connect(self.make_auto_fit)

        for k in item.ui.edit3D:
            f = partial (self.value_edited, k)
            item.ui.edit3D[k].editingFinished.connect(f)

        self.refresh()

    def value_changed(self, k):
        self.slider_to_edit(self.tau_item.ui.slider3D[k], self.tau_item.ui.edit3D[k], k)
        self.tau_item.show()


class Slice(FigureCanvasQTAgg):
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(1,1), dpi=100)
        super().__init__(self.fig)
        self.xStr = "temp"
        self.x_ax = []
        self.tau_item = None
        self.nr_of_connections = 0

    def set_slice_x_ax(self, x='temp'):
        if x == 'temp':
            self.x_ax = self.tau_item.temp
            self.xStr = x
        if x == 'field':
            self.x_ax = self.tau_item.field
            self.xStr = x
    

    def change(self, item):
        self.tau_item = item
        self.x_ax = item.temp
        self.const = item.field[0] #0

        self.refresh()

    def refresh(self):
        np.seterr(divide = 'ignore') 
        if self.tau_item == None:
            return

        self.ax.cla()
        self.ax.set(xlabel=self.xStr, ylabel='Tau', title="TO DO:: LaTeX equation")
        self.ax.grid()

       
        a = np.linspace(min(self.x_ax), max(self.x_ax), 45)
        b = np.ones(len(a)) * self.const

        if self.xStr == 'field':
            a,b = b,a

        r1 = self.direct(a, b, self.tau_item.current['Adir'], self.tau_item.current['Ndir'])
        direct_y = -np.log10(r1)
        if np.isinf(sum(direct_y)):
            direct_y = np.zeros(len(direct_y))
        try:
            len(direct_y)
        except TypeError:
            direct_y = np.ones(len(a)) * direct_y
        

        r2 = self.QTM(a, b, self.tau_item.current['B1'], self.tau_item.current['B2'], self.tau_item.current['B3'])
        QTM_y = -np.log10(r2)
        try:
            len(QTM_y)
        except TypeError:
            QTM_y = np.ones(len(a)) * QTM_y

        r3 = self.Raman(a, b, self.tau_item.current['CRaman'], self.tau_item.current['NHRaman'], self.tau_item.current['NRaman'])
        Raman_y = -np.log10(r3)
        try:
            len(Raman_y )
        except TypeError:
            Raman_y  = np.ones(len(a)) * Raman_y 

        r4 = self.Orbach(a, b, self.tau_item.current['Tau0'], self.tau_item.current['DeltaE'])
        Orbach_y = -np.log10(r4)
        try:
            len(Orbach_y )
        except TypeError:
            Orbach_y  = np.ones(len(a)) * Orbach_y 

        if self.xStr == 'field':
            a,b = b,a

        yy = -np.log10(self.model(pd.Series(a), pd.Series(b),self.tau_item.current['Adir'], self.tau_item.current['Ndir'],
         self.tau_item.current['B1'], self.tau_item.current['B2'], self.tau_item.current['B3'],
         self.tau_item.current['CRaman'], self.tau_item.current['NRaman'], self.tau_item.current['NHRaman'],
         self.tau_item.current['Tau0'], self.tau_item.current['DeltaE']))

        xx = [1/x for x in self.x_ax]
        self.ax.plot(xx, np.log10(self.tau_item.tau), 'o')

        a = [1/t for t in a]
        if self.tau_item.ui.checkBox_Adir_2.isChecked() == False:
            self.ax.plot(a, direct_y, 'y--', label ='Direct process')

        if self.tau_item.ui.checkBox_B1_2.isChecked() == False:
            self.ax.plot(a, QTM_y, 'g--', label='QTM')

        if self.tau_item.ui.checkBox_Craman_2.isChecked() == False:
            self.ax.plot(a, Raman_y, 'r--', label='Raman')

        if self.tau_item.ui.checkBox_Tau0_2.isChecked() == False:
            self.ax.plot(a, Orbach_y, 'm--', label='Orbach')
        
        self.ax.plot(a, yy, 'b-', label='Sum')

        self.ax.legend()
        self.draw()

    def direct(self, temp, field, Adir, Ndir):
        return Adir*temp*np.power(field ,Ndir)

    def QTM(self, temp, field, B1, B2, B3):
        return B1*(1+B3*field*field)/(1+B2*field*field)

    def Raman(self, temp, field, CRaman, NHraman, Nraman):
        return CRaman*np.power(field if field.all() != 0 else 1, NHraman) * np.power(temp, Nraman)

    def Orbach(self, temp, field, Tau0, DeltaE):
        return Tau0 *np.exp(-DeltaE/temp)

    def model(self, temp, field, Adir, Ndir, B1, B2, B3, CRaman, Nraman, NHraman, Tau0, DeltaE):
        return Adir*temp*(field**Ndir) \
        + B1*(1+B3*field*field)/(1+B2*field*field) \
        + CRaman*np.power(field if field.all() != 0 else 1, NHraman ) * np.power(temp, Nraman) \
        + Tau0 *np.exp(-DeltaE/(temp))
