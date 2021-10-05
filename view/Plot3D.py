from math import inf, isclose
from PyQt5.QtCore import QLocale, Qt
from PyQt5.QtWidgets import QTableWidgetItem, QApplication, QDialog, QComboBox, QHBoxLayout, QPushButton

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
from enum import IntEnum
import matplotlib.colors as mcolors
from .Fit_models import *
import copy 

import configparser

class X_dimension(IntEnum):
    TEMP = 1
    FIELD = 2

class Plot3D(FigureCanvasQTAgg): 
    def __init__(self):
        config = configparser.RawConfigParser()
        config.optionxform = str
        config.read('view/default_settings.ini')

        self.picker_radius = int(config['Plot']['picker_radius'])
        self.fig = plt.figure(figsize=(1,1), dpi = int(config['Plot']['dpi']), constrained_layout=True)
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
        nr_of_steps = 60
        x = np.linspace(min(self.tau_item.temp.min(), self.tau_item.hidden_temp.min() if len(self.tau_item.hidden_temp) > 0 else self.tau_item.temp.min()),
         max(self.tau_item.temp.max(), self.tau_item.hidden_temp.max() if len(self.tau_item.hidden_temp) else self.tau_item.temp.max()), nr_of_steps)
        y = np.linspace(min(self.tau_item.field.min(), self.tau_item.hidden_field.min() if len(self.tau_item.hidden_field) > 0 else self.tau_item.field.min()),
         max(self.tau_item.field.max(), self.tau_item.hidden_field.max() if len(self.tau_item.hidden_field) > 0 else self.tau_item.field.max()), nr_of_steps)
        X, Y = np.meshgrid(x,y)

        a = list(self.tau_item.current.values())
        p = list(self.tau_item.previous.values())
        Z = -np.log(model(X,Y,*a))
        P = -np.log(model(X,Y,*p))

        x = [1/t for t in x]
        X, Y = np.meshgrid(x,y)
        self.axes.plot_wireframe(X, Y, P, rstride=1, cstride=1, color='k', label='saved')
        self.axes.plot_wireframe(X, Y, Z, rstride=1, cstride=1, label='current', linestyles=':', color=mcolors.TABLEAU_COLORS["tab:green"])
        
        t_invert = [1/t for t in self.tau_item.temp]
        hidden_t_invert = [1/t for t in self.tau_item.hidden_temp]
        value_3d = np.log(self.tau_item.tau.tolist())
        hidden_value_3d = np.log(self.tau_item.hidden_tau.tolist())
        self.axes.scatter(t_invert, self.tau_item.field, value_3d , marker='o', color=mcolors.TABLEAU_COLORS["tab:blue"], label='points from fits')


        self.axes.scatter(hidden_t_invert, self.tau_item.hidden_field, hidden_value_3d , marker='o', label='hidden points from fits',
         color=mcolors.TABLEAU_COLORS["tab:orange"])


        #xs = np.linspace(min(np.amin(Z), min(value_3d)), min(np.amax(Z), max(value_3d) ), 25)
        #zs = np.linspace(min(np.amin(Z), min(value_3d)), max(np.amax(Z), max(value_3d) ), 25)

        if self.tau_item.ui.slice.x_dimension == X_dimension.TEMP:
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

        saved_values = list(self.tau_item.previous.values())
        parameters = list(self.tau_item.previous.keys())
        plusminus = u'\u00b1'
        length = len(self.tau_item.current_error)
        for i in range(length):
            self.tau_item.ui.tableWidget_error_3d.setItem(1, i,
                QTableWidgetItem(str(self.tau_item.current_error[i])))

            if parameters[i] not in self.tau_item.parent().parent().log_params:
                self.tau_item.ui.tableWidget_error_3d.setItem(0, i,
                    QTableWidgetItem(f"{saved_values[i]:.4f} {plusminus} {self.tau_item.error[i]:.4e}"))
            else:
                self.tau_item.ui.tableWidget_error_3d.setItem(0, i,
                    QTableWidgetItem(f"{np.log10(saved_values[i]):.4f} {plusminus} {self.tau_item.error[i]:.4e}"))

        self.tau_item.ui.tableWidget_error_3d.setItem(1, length,
            QTableWidgetItem(f"{self.tau_item.current_residual_error:.4e}"))

        self.tau_item.ui.tableWidget_error_3d.setItem(0, length,
            QTableWidgetItem(f"{self.tau_item.residual_error:.5e}"))

    def my_power(self, b, x):
        result = np.ndarray((len(b), len(b[0])))
        for i in range(len(b)):
            for j in range(len(b[i])):
                if b[i][j] <= 0.1:
                    result[i][j] = np.power(1, x)
                else:
                    result[i][j] = np.power(b[i][j], x)
        
            return result

    def cost_function(self, p, slice=False):
        if slice:
            slice = self.tau_item.ui.slice
            a = pd.Series(slice.x_ax)
            b = pd.Series(np.ones(len(a)) * slice.const)
            tau = pd.Series(np.exp(slice.y_ax))
            if slice.x_dimension == X_dimension.FIELD:
                a,b = b,a

            return np.power(np.log(model(a, b,*p)) - np.log((1/tau)), 2)

        return np.power(np.log(model(self.tau_item.temp, self.tau_item.field, *p)) - np.log((1/self.tau_item.tau)), 2)

    def make_auto_fit(self, slice_flag=False):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        QApplication.processEvents()
        np.seterr(divide = 'ignore') 
        compound = self.tau_item.parent().parent()
        r = compound.ranges
        ui = self.tau_item.ui
        params = ui.slider3D.keys() 

        lower_bound = []
        upper_bound = []
        for p in self.tau_item.current:
            if p in compound.log_params:
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
                if key in compound.log_params:
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

            for i in range(len(self.tau_item.current_error)):
                self.tau_item.current_error[i] = perr[i]
            self.tau_item.current_residual_error = res.cost

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




    def value_edited(self, k, auto=False, show_after=True):
        sliders = self.tau_item.ui.slider3D
        edits = self.tau_item.ui.edit3D
        self.edit_to_slider(sliders[k], edits[k], k)

        if not auto:
            for i in range(len(self.tau_item.current_error)):
                self.tau_item.current_error[i] = 0.0
            self.tau_item.current_residual_error = 0.0
        if show_after:
            self.tau_item.show()

    def edit_to_slider(self, slider, edit, name):
        v = str(edit.text())
        if v == '':
            v = self.tau_item.current[name]
        self.tau_item.current[name] = float(v)
        slider.blockSignals(True)
        slider.setValue(self.map_value_reverse(slider, edit , name))
        slider.blockSignals(False)

        compound = self.tau_item.parent().parent()
        if name in compound.log_params:
            self.tau_item.current[name] = np.power(10, self.tau_item.current[name])

    def slider_to_edit(self, slider, edit, name):
        self.tau_item.current[name] = self.map_value(slider, name)
        edit.blockSignals(True)
        edit.setText(str(self.tau_item.current[name]))
        edit.blockSignals(False)
        compound = self.tau_item.parent().parent()
        if name in compound.log_params:
            self.tau_item.current[name] = np.power(10, self.tau_item.current[name])

    def map_value_reverse(self, slider, edit, name=""):
        compound = self.tau_item.parent().parent()
        r = compound.ranges
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
        compound = self.tau_item.parent().parent()
        max = compound.ranges[name][1]
        min = compound.ranges[name][0]
        leftSpan = slider.maximum() - slider.minimum()
        rightSpan = max - min
        valueScaled = float(slider.value() - slider.minimum()) / float(leftSpan)
        return round(min + (valueScaled * rightSpan),2)

    def change(self, item):
        self.tau_item = item
        self.name = item.name
        self.tau_item.ui.actualFit3DLabel.setText(self.name)

        for k in item.ui.edit3D:
            item.ui.edit3D[k].setValidator(Validator(item, k,item.ui.edit3D[k]))

        if self.nr_of_connections == 1:
            for k in item.ui.slider3D:
                item.ui.slider3D[k].valueChanged.disconnect()

            item.ui.pushButton_fit3d.clicked.disconnect()
            item.ui.pushButton_save3d.clicked.disconnect()
            item.ui.pushButton_copyParameters3D.disconnect()
            item.ui.pushButton_range.disconnect()
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
        item.ui.pushButton_range.clicked.connect(partial(self.tau_item.parent().parent().change_ranges, self.tau_item.change))
        item.ui.pushButton_copyParameters3D.clicked.connect(self.copy_parameters)

        for k in item.ui.edit3D:
            f = partial (self.value_edited, k)
            item.ui.edit3D[k].editingFinished.connect(f)

        item.ui.comboBox_slice2.clear()
        item.ui.comboBox_slice2.currentIndexChanged.connect(item.ui.slice.change_const)
        item.ui.pushButton_set_current_3d.clicked.connect(self.tau_item.set_current_as_saved)
        item.ui.pushButton_fitSlice.clicked.connect(partial(self.make_auto_fit, slice_flag=True))
        compound = self.tau_item.parent().parent()
        print("3D change!!!!!!")
        for key in self.tau_item.ui.edit3D:
            print(f"Current {key}:{self.tau_item.current[key]}")
            self.tau_item.current[key]
            if key in compound.log_params:
                print(f"Do edita: {round(np.log10(self.tau_item.current[key]), 9)}")
                self.tau_item.ui.edit3D[key].setText(str(round(np.log10(self.tau_item.current[key]), 9)))

            else:
                print(f"Bez loga: {round(self.tau_item.current[key], 9)}")
                self.tau_item.ui.edit3D[key].setText(str(round(self.tau_item.current[key], 9)))

        for k in self.tau_item.ui.edit3D:
            self.value_edited(k, True, False)

        #self.refresh()
        self.tau_item.show()

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
        self.tau_item.residual_error = self.tau_item.current_residual_error
        self.tau_item.show()

    def copy_parameters(self):
        dlg = QDialog()
        dlg.setWindowTitle("Choose fit item to copy from")
        layout = QHBoxLayout()
        button = QPushButton("Copy")
        combo_box = QComboBox()
        layout.addWidget(combo_box)
        layout.addWidget(button)
        dlg.setLayout(layout)

        parent = self.tau_item.parent()
        i = 0
        while(parent.child(i) is not None):
            combo_box.addItem(parent.child(i).name)
            i += 1
        
        button.clicked.connect(partial(self.copy_parameters_from, combo_box, dlg))
        dlg.exec_()


    def copy_parameters_from(self, combo_box, dlg):
        source = self.tau_item.parent().child(combo_box.currentIndex())
        if  source is not None:
            self.tau_item.current = source.current.copy()
            self.current_error = [0] * len(self.tau_item.error)
            self.current_residual_error = 0.0
            self.tau_item.change()
            dlg.accept()
  

class Slice(FigureCanvasQTAgg):
    def __init__(self):
        config = configparser.RawConfigParser()
        config.optionxform = str
        config.read('view/default_settings.ini')

        self.picker_radius = int(config['Plot']['picker_radius'])
        self.fig, self.ax = plt.subplots(figsize=(1,1), dpi=int(config['Plot']['dpi']))
        self.fig.patch.set_facecolor("#f0f0f0")
        
        super().__init__(self.fig)
        self.x_dimension = X_dimension.TEMP
        self.unit = "K"
        self.x_ax = []
        self.y_ax = []
        self.const_ax = []
        self.const = 0
        self.tau_item = None
        self.intervals = set()
        self.nr_of_connections = 0

    def set_slice_x_ax(self, x=X_dimension.TEMP):
        self.x_ax = []
        self.y_ax = []
        
        self.hidden_x_ax = []
        self.hidden_y_ax = []
        if x == X_dimension.TEMP:
            for p in self.tau_item.points:

                if p[2] == self.const:
                    self.x_ax.append(p[1])
                    self.y_ax.append(np.log(p[0]))
            #self.x_ax =  [1/x for x in self.tau_item.temp]

            for p in self.tau_item.hidden_points:
                if p[2] == self.const:
                    self.hidden_x_ax.append(p[1])
                    self.hidden_y_ax.append(np.log(p[0]))

        if x == X_dimension.FIELD:
            for p in self.tau_item.points:

                if p[1] == self.const:
                    self.x_ax.append(p[2])
                    self.y_ax.append(np.log(p[0]))
            #self.x_ax = self.tau_item.field

            for p in self.tau_item.hidden_points:
                if p[1] == self.const:
                    self.hidden_x_ax.append(p[2])
                    self.hidden_y_ax.append(np.log(p[0]))


        if len(self.x_ax) == 0:
            self.x_ax = [0.1]
            self.y_ax = [0.1]
        self.x_dimension = x
    
    def change_slice_x_ax(self):
        if self.x_dimension != X_dimension.TEMP:
            self.set_slice_x_ax(X_dimension.TEMP)
            
            self.const_ax = self.tau_item.field
            self.unit = "Oe"
            
        else:
            self.set_slice_x_ax(X_dimension.FIELD)
            
            self.const_ax = self.tau_item.temp
            self.unit = "K"
            
    
    def change_const(self, i):
        list_intervals = list(self.intervals)
        list_intervals.sort()

        self.const = list_intervals[i]
        self.set_slice_x_ax(self.x_dimension)
        self.refresh()
        self.tau_item.ui.plot3d.refresh()

    def change(self, item):
        self.tau_item = item
        self.set_slice_x_ax(X_dimension.TEMP)
        
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
        self.fig.canvas.mpl_connect('pick_event', self.on_click)

        x_label = r"$\frac{K}{T}$"
        if self.x_dimension == X_dimension.FIELD:
            x_label = r"$\frac{H}{Oe}$"
        self.ax.set(xlabel=x_label, ylabel=r"$\ln{\frac{\tau}{s}}$",
         title=r"$\tau^{-1}=A_{dir}TH^{N_{dir}} + \frac{B_1(1+B_3H^2)}{1+B_2H^2} + C_{Raman}T^{N_{Raman}}+\tau_0^{-1}\exp{\frac{-\Delta E}{T}}$")
        self.ax.grid()

        nr_of_steps = 50
        a = np.linspace(min(min(self.x_ax), min(self.hidden_x_ax) if len(self.hidden_x_ax) > 0 else min(self.x_ax) ),
         max(max(self.x_ax), max(self.hidden_x_ax) if len(self.hidden_x_ax) > 0 else max(self.x_ax)),
         nr_of_steps)

        b = np.ones(len(a)) * self.const

        if self.x_dimension == X_dimension.FIELD:
            a,b = b,a

        r1 = Direct(a, b, self.tau_item.current['Adir'], self.tau_item.current['Ndir'])
        direct_y = -np.log(r1)
        if np.isinf(sum(direct_y)):
            direct_y = np.zeros(len(direct_y))
        try:
            len(direct_y)
        except TypeError:
            
            direct_y = np.ones(len(a)) * direct_y
        

        r2 = QTM(a, b, self.tau_item.current['B1'], self.tau_item.current['B2'], self.tau_item.current['B3'])
        QTM_y = -np.log(r2)
        try:
            len(QTM_y)
        except TypeError:
            
            QTM_y = np.ones(len(a)) * QTM_y

        r3 = Raman(a, b, self.tau_item.current['CRaman'], self.tau_item.current['NRaman'])
        Raman_y = -np.log(r3)
        try:
            len(Raman_y )
        except TypeError:
            
            Raman_y  = np.ones(len(a)) * Raman_y 

        r4 = Orbach(a, b, self.tau_item.current['Tau0'], self.tau_item.current['DeltaE'])
        Orbach_y = -np.log(r4)
        try:
            len(Orbach_y )
        except TypeError:
            Orbach_y  = np.ones(len(a)) * Orbach_y 

        c = list(self.tau_item.current.values())
        yy_current = -np.log(model(pd.Series(a), pd.Series(b),*c))
        yy_saved = -np.log(model(pd.Series(a), pd.Series(b),**self.tau_item.previous))

        if self.x_dimension == X_dimension.FIELD:
            a,b = b,a


        xx = self.x_ax
        hidden_xx = self.hidden_x_ax
        if self.x_dimension == X_dimension.TEMP:
            xx = [1/x for x in self.x_ax]
            hidden_xx = [1/x for x in self.hidden_x_ax]

        self.ax.plot(xx, self.y_ax, 'o', picker=self.picker_radius)
        self.ax.plot(hidden_xx, self.hidden_y_ax, 'o', picker=self.picker_radius, label='hidden points')

        
        if self.x_dimension == X_dimension.TEMP:
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
        
        self.ax.set_ylim(min(min(self.y_ax), min(self.hidden_y_ax) if len(self.hidden_y_ax) > 0 else min(self.y_ax)) - 1,
         3 + max(max(self.y_ax), max(self.hidden_y_ax) if len(self.hidden_y_ax) > 0 else max(self.y_ax) ))

        leg = self.ax.legend()
        
        if leg:
            leg.set_draggable(True)

        self.draw()

    def on_click(self, event):
        xdata = event.artist.get_xdata()
        ydata = event.artist.get_ydata()
        mouse = event.mouseevent
        ind = event.ind
        if mouse.button == mouse.button.LEFT:
            self.hide_point(xdata[ind], ydata[ind])

        if mouse.button == mouse.button.RIGHT:
            self.delete_point(xdata[ind],ydata[ind])
        
        self.refresh()
        self.tau_item.ui.plot3d.refresh()
        
    def hide_point(self, x, y):

        if len(x) > 0:
            tau_item = self.tau_item
            points = tau_item.points
            hidden_points =tau_item.hidden_points
            found = False
            if len(self.x_ax) > 1:
                for point in points:
                    if isclose(point[0], np.exp(y[0]), rel_tol=1e-12):
                        if self.x_dimension == X_dimension.TEMP:
                            if 1/point[1] == x[0]:
                                found = True
                                tau_item.delete_point(point)
                                tau_item.add_hidden_point(point)
                        if self.x_dimension == X_dimension.FIELD:
                            if point[2] == x[0] and point[0] == np.exp(y[0]):
                                found = True
                                tau_item.delete_point(point)
                                tau_item.add_hidden_point(point)

            if not found:
                for point in hidden_points:
                    if isclose(point[0], np.exp(y[0]), rel_tol=1e-12):
                        if self.x_dimension == X_dimension.TEMP:
                            if 1/point[1] == x[0] and point[0] == np.exp(y[0]):
                                print(f"match on {point}")
                                found = True
                                tau_item.delete_hidden_point(point)
                                tau_item.add_point(point)
                                
                        if self.x_dimension == X_dimension.FIELD:
                            if point[2] == x[0] and point[0] == np.exp(y[0]):
                                print(f"match on {point}")
                                found = True
                                tau_item.delete_hidden_point(point)
                                tau_item.add_point(point)
        self.set_slice_x_ax(self.x_dimension)

    def delete_point(self, x, y):
        if len(self.x_ax) == 1:
            return

        tau_item = self.tau_item
        for point in tau_item.points:
            if isclose(point[0], np.exp(y[0]), rel_tol=1e-12):
                if self.x_dimension == X_dimension.TEMP:
                    
                    if 1/point[1] == x[0]:
                        print(f"delete on {point}")
                        tau_item.delete_point(point)

                if self.x_dimension == X_dimension.FIELD:
                    if point[2] == x[0]:
                        print(f"delete on {point}")
                        tau_item.delete_point(point)

        for point in tau_item.hidden_points:
            if isclose(point[0], np.exp(y[0]), rel_tol=1e-12):
                if self.x_dimension == X_dimension.TEMP:
                    if 1/point[1] == x[0]:
                        print(f"delete on {point}")
                        tau_item.delete_hidden_point(point)

                if self.x_dimension == X_dimension.FIELD:
                    if point[2] == x[0]:
                        print(f"delete on {point}")
                        tau_item.delete_hidden_point(point)

        self.set_slice_x_ax(self.x_dimension)





