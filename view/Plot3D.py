from math import inf
from PyQt5.QtCore import QLocale, Qt
from PyQt5.QtWidgets import QTableWidgetItem, QApplication

import numpy as np
import matplotlib.pyplot as plt
from numpy.core.records import get_remaining_size
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from .Validator import Validator

from numba import jit
from scipy.optimize._lsq.least_squares import least_squares
from scipy.interpolate import interp1d
from scipy import linalg

from functools import partial

class Plot3D(FigureCanvasQTAgg): 
    def __init__(self):
        self.fig = plt.figure(figsize=(1,1), dpi = 100, constrained_layout=True)
        self.fig.patch.set_facecolor("#f0f0f0")
        super().__init__(self.fig) # creating FigureCanvas
        self.axes = self.fig.gca(projection='3d') # generates 3D Axes object
        self.axes.set_facecolor("#f0f0f0")
        self.setWindowTitle("Main") # sets Window title

        self.nr_of_connections = 0

        # self.fig.constrained_layout(True)
        # self.fig.subplots_adjust(left=-0.11)

    def refresh(self): # Fun for Graph plotting
        self.axes.clear()
        # self.axes.plot_surface(x, y, z) # plots the 3D surface plot
        x = np.linspace(self.tau_item.temp.min(), self.tau_item.temp.max(), 60)
        y = np.linspace(self.tau_item.field.min(), self.tau_item.field.max(), 60)
        X, Y = np.meshgrid(x,y)

        a = list(self.tau_item.current.values())
        p = list(self.tau_item.previous.values())
        Z = -np.log(self.model(X,Y,a[0],a[1],a[2],a[3],a[4],a[5],a[6],a[7],a[8]))
        P = -np.log(self.model(X,Y,p[0],p[1],p[2],p[3],p[4],p[5],p[6],p[7],p[8]))

        x = [1/t for t in x]
        X, Y = np.meshgrid(x,y)
        self.axes.plot_wireframe(X, Y, P, rstride=1, cstride=1, label='saved')
        self.axes.plot_wireframe(X, Y, Z, rstride=1, cstride=1, label='current', linestyles=':', color='g')
        
        t_invert = [1/t for t in self.tau_item.temp]
        value_3d = np.log(self.tau_item.tau.tolist())
        self.axes.scatter(t_invert, self.tau_item.field, value_3d , marker='o', color='r', label='points from fits')

        #xs = np.linspace(min(np.amin(Z), min(value_3d)), min(np.amax(Z), max(value_3d) ), 25)
        #zs = np.linspace(min(np.amin(Z), min(value_3d)), max(np.amax(Z), max(value_3d) ), 25)

        if self.tau_item.ui.slice.xStr =='temp':
            xx, zz = np.meshgrid(self.axes.get_xlim(), self.axes.get_zlim())
            yy = np.ones(xx.shape) * self.tau_item.ui.slice.const
            surf = self.axes.plot_surface(xx, yy, zz, color='y', alpha=0.2, label='slice')
            surf._facecolors2d = surf._facecolor3d
            surf._edgecolors2d=surf._edgecolor3d
        else:
            yy, zz = np.meshgrid(self.axes.get_ylim(), self.axes.get_zlim())
            xx = np.ones(yy.shape) * 1/self.tau_item.ui.slice.const
            surf = self.axes.plot_surface(xx, yy, zz, color='y', alpha=0.2, label='slice')
            surf._facecolors2d = surf._facecolor3d
            surf._edgecolors2d=surf._edgecolor3d

        self.axes.set_xlabel(r'$\frac{1}{T}$', rotation = 0, fontsize=15)
        self.axes.set_ylabel(r'$\frac{H}{Oe}$', rotation = 0, fontsize=15)
        self.axes.set_zlabel(r'$\ln{\frac{\tau}{s}}$', rotation = 0, fontsize=15)

        self.axes.xaxis.set_rotate_label(False) 
        self.axes.yaxis.set_rotate_label(False) 
        self.axes.zaxis.set_rotate_label(False) 
        self.axes.legend()
        self.draw()

        for i in range(len(self.tau_item.current_error)):
            self.tau_item.ui.tableWidget_error_3d.setItem(1, i,
                QTableWidgetItem(str(self.tau_item.current_error[i])))

            self.tau_item.ui.tableWidget_error_3d.setItem(0, i,
                QTableWidgetItem(str(self.tau_item.error[i])))

    def my_power(self, b, x):
        result = np.ndarray((len(b), len(b[0])))
        for i in range(len(b)):
            for j in range(len(b[i])):
                if b[i][j] <= 0.1:
                    result[i][j] = np.power(1, x)
                else:
                    result[i][j] = np.power(b[i][j], x)
        
            return result

            

    def model(self, temp, field, Adir, Ndir, B1, B2, B3, CRaman, NRaman, Tau0, DeltaE):

        return Adir*temp*(field**Ndir) \
        + B1*(1+B3*field*field)/(1+B2*field*field) \
        + CRaman * np.power(temp, NRaman) \
        + Tau0 *np.exp(-DeltaE/(temp))

    def cost_function(self, p, slice=False):
        if slice:
            slice = self.tau_item.ui.slice
            a = pd.Series(slice.x_ax)
            b = pd.Series(np.ones(len(a)) * slice.const)
            tau = pd.Series(np.exp(slice.y_ax))
            if slice.xStr == 'field':
                a,b = b,a

            return np.power(self.model(a, b,
                p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8]) - (1/tau), 2)

        return np.power(self.model(self.tau_item.temp, self.tau_item.field,
            p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8]) - (1/self.tau_item.tau), 2)

    def make_auto_fit(self, slice_flag=False):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        QApplication.processEvents()
        np.seterr(divide = 'ignore') 
        r = AppState.ranges
        ui = self.tau_item.ui
        params = ui.slider3D.keys() 

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
        

        
        i = 0
        for k in self.tau_item.ui.check3D:
            if self.tau_item.ui.check3D[k].isChecked():
                if self.tau_item.current[k] == 0:
                    continue
                fraction =  1e16
                b[0][i] = max(self.tau_item.current[k] - self.tau_item.current[k]/fraction, b[0][i])
                b[1][i] = min(self.tau_item.current[k] + self.tau_item.current[k]/fraction, b[1][i])
                self.tau_item.current[k] = b[1][i] - self.tau_item.current[k]/fraction
            i += 1

        i = 0
        for k in self.tau_item.ui.check3D_2:
            if self.tau_item.ui.check3D_2[k].isChecked():
                self.tau_item.current[k] = 1e-65
                b[0][i] = 0
                b[1][i] = 1e-64
            i += 1

        
        cost_f = partial(self.cost_function, slice=slice_flag)
 
    try:
        res = least_squares(cost_f, tuple(self.tau_item.current.values()), bounds = b)
        J = res.jac
        i = 0
        for key in self.tau_item.current:
            self.tau_item.current[key] = res.x[i]
            i += 1

        for key in ui.edit3D:
            if key in AppState.log_params:
                ui.edit3D[key].setText(str(round(np.log10(self.tau_item.current[key]), 9)))

            else:
                ui.edit3D[key].setText(str(round(self.tau_item.current[key], 9)))

        U, s, Vh = linalg.svd(res.jac, full_matrices=False)
        tol = np.finfo(float).eps*s[0]*max(res.jac.shape)
        w = s > tol
        cov = (Vh[w].T/s[w]**2) @ Vh[w]  # robust covariance matrix

        chi2dof = np.sum(res.fun**2)/(res.fun.size - res.x.size)
        cov *= chi2dof
        
        perr = np.sqrt(np.diag(cov))

        print(perr)

        for i in range(len(self.tau_item.current_error)-1):
            self.tau_item.current_error[i] = perr[i]
        self.tau_item.current_error[-1] = res.cost

        for k in ui.edit3D:
            # if ui.blockedOnZero[k].isChecked() == False:
            self.value_edited(k, True)

        print("bounds", b)
        print("current:",list(self.tau_item.current.values()))
    except Exception as e:
        print(e)
        self.tau_item.set_current_as_saved()
        print("bounds", b)
        print("current:",list(self.tau_item.current.values()))

        QApplication.restoreOverrideCursor()
        QApplication.processEvents()




    def value_edited(self, k, auto=False):
        sliders = self.tau_item.ui.slider3D
        edits = self.tau_item.ui.edit3D
        self.edit_to_slider(sliders[k], edits[k], k)

        if not auto:
            for i in range(len(self.tau_item.current_error)):
                self.tau_item.current_error[i] = 0

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
            item.ui.pushButton_save3d.clicked.disconnect()
            item.ui.comboBox_slice2.currentIndexChanged.disconnect()
            item.ui.pushButton_set_current_3d.clicked.disconnect()
            item.ui.pushButton_fitSlice.clicked.disconnect()
            
            

            for k in item.ui.edit3D:
                item.ui.edit3D[k].editingFinished.disconnect()
            self.nr_of_connections = 0

        self.nr_of_connections += 1
        for k in item.ui.slider3D:
            f = partial (self.value_changed, k)
            item.ui.slider3D[k].valueChanged.connect(f)

        item.ui.pushButton_fit3d.clicked.connect(self.make_auto_fit)
        item.ui.pushButton_save3d.clicked.connect(self.save_fit)

        for k in item.ui.edit3D:
            f = partial (self.value_edited, k)
            item.ui.edit3D[k].editingFinished.connect(f)

        item.ui.comboBox_slice2.clear()
        item.ui.comboBox_slice2.currentIndexChanged.connect(item.ui.slice.change_const)
        item.ui.pushButton_set_current_3d.clicked.connect(self.tau_item.set_current_as_saved)
        item.ui.pushButton_fitSlice.clicked.connect(partial(self.make_auto_fit, slice_flag=True))
        self.refresh()

    def value_changed(self, k):
        self.slider_to_edit(self.tau_item.ui.slider3D[k], self.tau_item.ui.edit3D[k], k)

        for i in range(len(self.tau_item.current_error)):
            self.tau_item.current_error[i] = 0

        self.tau_item.show()

    def save_fit(self):
        for param in self.tau_item.current:
            self.tau_item.previous[param] = self.tau_item.current[param]

        for i in range(len(self.tau_item.current_error)):
            self.tau_item.error[i] = self.tau_item.current_error[i]
        self.tau_item.show()

    


class Slice(FigureCanvasQTAgg):
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(1,1), dpi=100)
        self.fig.patch.set_facecolor("#f0f0f0")
        super().__init__(self.fig)
        self.xStr = "temp"
        self.unit = "K"
        self.x_ax = []
        self.y_ax = []
        self.const_ax = []
        self.const = 0
        self.tau_item = None
        self.intervals = set()
        self.nr_of_connections = 0
        

    def set_slice_x_ax(self, x='temp'):
        self.x_ax = []
        self.y_ax = []
        
        if x == 'temp':
            for p in self.tau_item.points:

                if p[2] == self.const:
                    self.x_ax.append(p[1])
                    self.y_ax.append(np.log(p[0]))
            #self.x_ax =  [1/x for x in self.tau_item.temp]

        if x == 'field':
            for p in self.tau_item.points:

                if p[1] == self.const:
                    self.x_ax.append(p[2])
                    self.y_ax.append(np.log(p[0]))
            #self.x_ax = self.tau_item.field
        if len(self.x_ax) == 0:
            self.x_ax = [0.1]
            self.y_ax = [0.1]
        self.xStr = x
    
    def change_slice_x_ax(self):
        if self.xStr != 'temp':
            self.set_slice_x_ax('temp')
            
            self.const_ax = self.tau_item.field
            self.unit = "Oe"
            
        else:
            self.set_slice_x_ax('field')
            
            self.const_ax = self.tau_item.temp
            self.unit = "K"
            
    
    def change_const(self, i):
        list_intervals = list(self.intervals)
        list_intervals.sort()

        self.const = list_intervals[i]
        self.set_slice_x_ax(self.xStr)
        self.refresh()
        self.tau_item.ui.plot3d.refresh()

    def change(self, item):
        self.tau_item = item
        self.set_slice_x_ax('temp')
        
        self.const_ax = self.tau_item.field
        self.unit = "Oz"
        
        if len(self.intervals) != 0:
            list_intervals = list(self.intervals)
            list_intervals.sort()
            self.const = list_intervals[0]
  

        self.tau_item.show()

    def refresh(self):
        np.seterr(divide = 'ignore') 
        if self.tau_item == None:
            return

        self.ax.cla()
        x_label = r"$\frac{K}{T}$"
        if self.xStr == "field":
            x_label = r"$\frac{H}{Oe}$"
        self.ax.set(xlabel=x_label, ylabel=r"$\ln{\frac{\tau}{s}}$",
         title=r"$\tau^{-1}=A_{dir}TH^{N_{dir}} + \frac{B_1(1+B_3H^2)}{1+B_2H^2} + C_{Raman}T^{N_{Raman}}+\tau_0^{-1}\exp{\frac{-\Delta E}{T}}$")
        self.ax.grid()

       
        a = np.linspace(min(self.x_ax), max(self.x_ax), 45)

        b = np.ones(len(a)) * self.const

        if self.xStr == 'field':
            a,b = b,a

        r1 = self.direct(a, b, self.tau_item.current['Adir'], self.tau_item.current['Ndir'])
        direct_y = -np.log(r1)
        if np.isinf(sum(direct_y)):
            direct_y = np.zeros(len(direct_y))
        try:
            len(direct_y)
        except TypeError:
            
            direct_y = np.ones(len(a)) * direct_y
        

        r2 = self.QTM(a, b, self.tau_item.current['B1'], self.tau_item.current['B2'], self.tau_item.current['B3'])
        QTM_y = -np.log(r2)
        try:
            len(QTM_y)
        except TypeError:
            
            QTM_y = np.ones(len(a)) * QTM_y

        r3 = self.Raman(a, b, self.tau_item.current['CRaman'], self.tau_item.current['NRaman'])
        Raman_y = -np.log(r3)
        try:
            len(Raman_y )
        except TypeError:
            
            Raman_y  = np.ones(len(a)) * Raman_y 

        r4 = self.Orbach(a, b, self.tau_item.current['Tau0'], self.tau_item.current['DeltaE'])
        Orbach_y = -np.log(r4)
        try:
            len(Orbach_y )
        except TypeError:
            Orbach_y  = np.ones(len(a)) * Orbach_y 

        c = list(self.tau_item.current.values())
        yy_current = -np.log(self.model(pd.Series(a), pd.Series(b),*c))
        yy_saved = -np.log(self.model(pd.Series(a), pd.Series(b),**self.tau_item.previous))

        if self.xStr == 'field':
            a,b = b,a


        xx = self.x_ax

        if self.xStr == 'temp':
            xx = [1/x for x in self.x_ax]


        self.ax.plot(xx, self.y_ax, 'o')

        
        if self.xStr == "temp":
            a = 1/a
        self.ax.plot(a, yy_saved, 'k-', label='saved sum')
        self.ax.plot(a, yy_current, 'b-', label='current sum')

        if self.tau_item.ui.checkBox_Adir_2.isChecked() == False:
            self.ax.plot(a, direct_y, 'y--', label ='Direct process')

        if self.tau_item.ui.checkBox_B1_2.isChecked() == False:
            self.ax.plot(a, QTM_y, 'g--', label='QTM')

        if self.tau_item.ui.checkBox_Craman_2.isChecked() == False:
            self.ax.plot(a, Raman_y, 'r--', label='Raman')

        if self.tau_item.ui.checkBox_Tau0_2.isChecked() == False:
            self.ax.plot(a, Orbach_y, 'm--', label='Orbach')
        
        self.ax.set_ylim(min(self.y_ax) - 1, 3 + max(self.y_ax))

        leg = self.ax.legend()
        
        if leg:
            leg.set_draggable(True)

        self.draw()


    def direct(self, temp, field, Adir, Ndir):
        return Adir*temp*np.power(field ,Ndir)

    def QTM(self, temp, field, B1, B2, B3):
        return B1*(1+B3*field*field)/(1+B2*field*field)

    def Raman(self, temp, field, CRaman, Nraman):
        return CRaman* np.power(temp, Nraman)

    def Orbach(self, temp, field, Tau0, DeltaE):
        return Tau0 *np.exp(-DeltaE/temp)

    def model(self, temp, field, Adir, Ndir, B1, B2, B3, CRaman, NRaman, Tau0, DeltaE):

        return Adir*temp*(field**Ndir) \
        + B1*(1+B3*field*field)/(1+B2*field*field) \
        + CRaman * np.power(temp, NRaman) \
        + Tau0 *np.exp(-DeltaE/(temp))


