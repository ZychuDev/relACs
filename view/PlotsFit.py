from numba.core.types.scalars import Float, Integer
from view.AppStateBase import *
from PyQt5.QtWidgets import QTableWidgetItem
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.ticker import LinearLocator, AutoMinorLocator

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from numba import jit
from scipy.optimize import least_squares
from scipy.interpolate import interp1d
from scipy import linalg

from .Validator import Validator

from functools import partial

class Curve():
    def __init__(self):
        self.yy = []
        self.real = []
        self.img = []

        self.yy_saved = []
        self.real_saved = []
        self.img_saved = []

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)

    def __add__(self, other):
        "Adding to curves all fileds should be lists of the same length"
        result = Curve()
        result_vars = vars(result)
        other_vars = vars(other)

        for key, val in vars(self).items():
            #diffrent length allowed version
            # tmp = other_vars[key][:] #shallow copy
            # size_diff = len(val) - len(other_vars[key])
            # if size_diff != 0:
            
            #     zero_padding = [0] * abs(size_diff)
            #     if size_diff < 0:
            #         val = val + zero_padding
            #     else:
            #         tmp = other_vars[key] + zero_padding

            # result_vars[key] = [sum(x) for x in zip(val, tmp)]
            result_vars[key] = [sum(x) for x in zip(val, other_vars[key])]

        return result

class plotFitChi(FigureCanvasQTAgg):
    curves = [Curve()]
    domain = []
    curves_sum = []
    curves_sum_saved = []

    nr_of_connections = 0

    nr_of_relaxation = 0

    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(1,1), dpi=80)
        self.fig.patch.set_facecolor("#f0f0f0")
        super().__init__(self.fig)
        self.xStr = "ChiPrimeMol"

        self.colors_names = ["tab:green", "tab:red", "tab:purple", "tab:brown", "tab:pink"]

    def change(self, fitFrequecyItem):
        self.fitItem = fitFrequecyItem
        self.name = fitFrequecyItem.name
        self.df = fitFrequecyItem.df

        self.refresh()


        v = Validator(self.fitItem, 'alpha', self.fitItem.ui.lineEdit_Alpha)
        self.fitItem.ui.lineEdit_Alpha.setValidator(v)
        v = Validator(self.fitItem, 'beta', self.fitItem.ui.lineEdit_Beta)
        self.fitItem.ui.lineEdit_Beta.setValidator(v)
        v = Validator(self.fitItem, 'tau', self.fitItem.ui.lineEdit_Tau)
        self.fitItem.ui.lineEdit_Tau.setValidator(v)
        v = Validator(self.fitItem, 'chiT', self.fitItem.ui.lineEdit_ChiT)
        self.fitItem.ui.lineEdit_ChiT.setValidator(v)
        v = Validator(self.fitItem, 'chiS', self.fitItem.ui.lineEdit_ChiS)
        self.fitItem.ui.lineEdit_ChiS.setValidator(v)


        ui = self.fitItem.ui
        ui.spinBoxRelaxation.setRange(1, len(self.fitItem.relaxations))
        try:
            ui.spinBoxRelaxation.valueChanged.disconnect()
        except Exception: pass

        ui.spinBoxRelaxation.valueChanged.connect(self.change_relaxation)

        if plotFitChi.nr_of_connections == 3:
            try:

                ui.horizontalSlider_Alpha.valueChanged.disconnect()
                ui.horizontalSlider_Beta.valueChanged.disconnect()
                ui.horizontalSlider_Tau.valueChanged.disconnect()
                ui.horizontalSlider_ChiS.valueChanged.disconnect()
                ui.horizontalSlider_ChiT.valueChanged.disconnect()

                ui.pushButtonFit.clicked.disconnect()
                ui.pushButtonSave.clicked.disconnect()
                ui.pushButtonNext.clicked.disconnect()
                ui.pushButtonPrevious.clicked.disconnect()
                ui.pushButtonSetSavedAsCurrent.clicked.disconnect()

                

                ui.lineEdit_Alpha.editingFinished.disconnect()
                ui.lineEdit_Beta.editingFinished.disconnect()
                ui.lineEdit_Tau.editingFinished.disconnect()
                ui.lineEdit_ChiT.editingFinished.disconnect()
                ui.lineEdit_ChiS.editingFinished.disconnect()
                plotFitChi.nr_of_connections = 0
            except Exception: pass

        plotFitChi.nr_of_connections = plotFitChi.nr_of_connections + 1
        ui.horizontalSlider_Alpha.valueChanged.connect(partial(self.value_changed, 'alpha'))
        ui.horizontalSlider_Beta.valueChanged.connect(partial(self.value_changed, 'beta'))
        ui.horizontalSlider_Tau.valueChanged.connect(partial(self.value_changed, 'tau'))
        ui.horizontalSlider_ChiS.valueChanged.connect(partial(self.value_changed, 'chiS'))
        ui.horizontalSlider_ChiT.valueChanged.connect(partial(self.value_changed, 'chiT'))

        ui.pushButtonFit.clicked.connect(self.makeAutoFit)
        ui.pushButtonSave.clicked.connect(self.saveFit)
        ui.pushButtonNext.clicked.connect(self.next)
        ui.pushButtonPrevious.clicked.connect(self.previous)
        ui.pushButtonSetSavedAsCurrent.clicked.connect(self.set_saved_as_current)

        

        ui.lineEdit_Alpha.editingFinished.connect(partial(self.value_edited, 'alpha'))
        ui.lineEdit_Beta.editingFinished.connect(partial(self.value_edited, 'beta'))
        ui.lineEdit_Tau.editingFinished.connect(partial(self.value_edited, 'tau'))
        ui.lineEdit_ChiT.editingFinished.connect(partial(self.value_edited, 'chiS'))
        ui.lineEdit_ChiS.editingFinished.connect(partial(self.value_edited, 'chiT'))

    def change_relaxation(self):
        ui = self.fitItem.ui 
        
        plotFitChi.nr_of_relaxation = ui.spinBoxRelaxation.value() - 1

        current = self.fitItem.relaxations[plotFitChi.nr_of_relaxation].current
        for key, edit  in ui.editFit2D.items():
            edit.setText(str(round(current[key],9)))
            self.edit_to_slider(ui.sliderFit2D[key], edit, key)

        self.fitItem.ui.refreshFitFr()




    def refresh(self):
        print("Refresh")
        self.ax.cla()
        df = self.df
        self.fig.canvas.mpl_connect('pick_event', self.onClick)

        
        self.ax.set(title=r"Cole-Cole", xlabel=r"$\chi^{\prime \prime} /cm^3*mol^{-1}$", ylabel=r"$\chi^{\prime \prime} / cm^3*mol^{-1}$")
        
        self.ax.grid(True, linestyle='--', linewidth=1, color=mcolors.CSS4_COLORS["silver"])
        #self.ax.grid(True, which="minor", linestyle="--")
        
        self.ax.xaxis.set_major_locator(LinearLocator(10))
        # self.ax.xaxis.set_minor_locator(AutoMinorLocator(2))

        self.ax.yaxis.set_major_locator(LinearLocator(8))
        # self.ax.yaxis.set_minor_locator(AutoMinorLocator(2))

        shown = df.loc[df["Show"]== True]
        hiden = df.loc[df["Show"]== False]

        self.ax.plot( shown["ChiPrimeMol"].values, shown["ChiBisMol"].values, "o", label = "Experimental data", picker=15, c=mcolors.TABLEAU_COLORS["tab:blue"])
        self.ax.plot( hiden["ChiPrimeMol"].values, hiden["ChiBisMol"].values, "o", label = "Hiden Experimental data", picker=15, c=mcolors.TABLEAU_COLORS["tab:orange"])

        step = (df['FrequencyLog'].max() - df['FrequencyLog'].min())/50
        min = df['FrequencyLog'].min()
        plotFitChi.domain = []
        while min <= (df['FrequencyLog'].max() + step):
            plotFitChi.domain.append(min)
            min += step

        #plot curves
        plotFitChi.curves = []
        for r in self.fitItem.relaxations:
           plotFitChi.curves.append(Curve())

        i = 0
        while i < len(self.fitItem.relaxations):
            r = self.fitItem.relaxations[i]
            curve = plotFitChi.curves[i]

            for x in plotFitChi.domain:
                curve.yy.append(self.model(x, alpha = r.current["alpha"]
                    , beta = r.current["beta"]
                    , tau = r.current["tau"]
                    , chiT = r.current["chiT"]
                    , chiS = r.current["chiS"] ))

                curve.yy_saved.append(self.model(x, alpha = r.previous["alpha"]
                    , beta = r.previous["beta"]
                    , tau = r.previous["tau"]
                    , chiT = r.previous["chiT"]
                    , chiS = r.previous["chiS"] ))

            for c in curve.yy:
                curve.real.append(c.real)
                curve.img.append(-c.imag)

            for c in curve.yy_saved:
                curve.real_saved.append(c.real)
                curve.img_saved.append(-c.imag)
        
            i += 1

        color_nr = 0
        for c in plotFitChi.curves:
            self.ax.plot(c.real, c.img, "--", c=mcolors.TABLEAU_COLORS[self.colors_names[color_nr]])
            if self.fitItem.wasSaved: 
                self.ax.plot(c.real_saved, c.img_saved, "-", c=mcolors.TABLEAU_COLORS[self.colors_names[color_nr]])
            color_nr = (color_nr + 1) % len(self.colors_names)

        if len(plotFitChi.curves) > 1:
            plotFitChi.curves_sum = sum(plotFitChi.curves)
            self.ax.plot(plotFitChi.curves_sum.real, plotFitChi.curves_sum.img, '--', c=mcolors.TABLEAU_COLORS["tab:cyan"] )

            if self.fitItem.wasSaved:
                self.ax.plot(plotFitChi.curves_sum.real_saved, plotFitChi.curves_sum.img_saved, '-', c=mcolors.TABLEAU_COLORS["tab:cyan"])

        #self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1),fancybox=True, shadow=True)
        

        for i in range(5):
            self.fitItem.ui.tableWidget_error_frequency.setItem(1, i,
             QTableWidgetItem(str(self.fitItem.relaxations[plotFitChi.nr_of_relaxation].current_error[i])))

            self.fitItem.ui.tableWidget_error_frequency.setItem(0, i,
             QTableWidgetItem(str(self.fitItem.relaxations[plotFitChi.nr_of_relaxation].error[i])))

        self.draw()

    def onClick(self, event):
        xdata = event.artist.get_xdata()
        mouse = event.mouseevent
        ind = event.ind
        if mouse.button == mouse.button.LEFT:
            self.selectPoint(xdata[ind])

        if mouse.button == mouse.button.RIGHT:
            self.deletePoint(xdata[ind])
        
    def selectPoint(self, x):
        self.df.loc[self.df[self.xStr] == x[0], "Show"] = not bool(self.df.loc[self.df[self.xStr] == x[0]]["Show"].values[0])
        self.fitItem.ui.refreshFitFr()

    def deletePoint(self, x):
        self.df.drop(self.df.loc[self.df[self.xStr] == x[0]].index, inplace=True)
        self.fitItem.df.drop(self.df.loc[self.df[self.xStr] == x[0]].index, inplace=True)
        self.fitItem.ui.refreshFitFr()

    def map_value(self, slider, name=""):
        max = AppState.ranges[name][1]
        min = AppState.ranges[name][0]
        leftSpan = slider.maximum() - slider.minimum()
        rightSpan = max - min
        valueScaled = float(slider.value() - slider.minimum()) / float(leftSpan)
        return round(min + (valueScaled * rightSpan),2)

    def map_value_reverse(self, slider, edit, name=""):
        r = AppState.ranges
        m = interp1d([r[name][0], r[name][1]], [slider.minimum(), slider.maximum()])
        v = str(edit.text())
        if v == '':
            v = self.fitItem.relaxations[plotFitChi.nr_of_relaxation].current[name]
        v = float(v)
        v = float(m(v))
        return round(v)

    def value_changed(self, param):
        self.slider_to_edit(self.fitItem.ui.sliderFit2D[param], self.fitItem.ui.editFit2D[param], param)

        for r in self.fitItem.relaxations:
            for i in range(len(r.current_error)):
                r.current_error[i] = 0

        self.refresh()

    def value_edited(self, param): 
        self.edit_to_slider(self.fitItem.ui.sliderFit2D[param], self.fitItem.ui.editFit2D[param], param)

        for r in self.fitItem.relaxations:
            for i in range(len(r.current_error)):
                r.current_error[i] = 0

        self.fitItem.ui.refreshFitFr()

    def edit_to_slider(self, slider, edit, name):
        v = str(edit.text())
        if v == '':
            v = self.fitItem.relaxations[plotFitChi.nr_of_relaxation].current[name]
        self.fitItem.relaxations[plotFitChi.nr_of_relaxation].current[name] = float(v)
        slider.blockSignals(True)
        slider.setValue(self.map_value_reverse(slider,edit , name))
        slider.blockSignals(False)

    def slider_to_edit(self, slider, edit, name):
        self.fitItem.relaxations[plotFitChi.nr_of_relaxation].current[name] = self.map_value(slider, name)
        edit.blockSignals(True)
        edit.setText(str(self.fitItem.relaxations[plotFitChi.nr_of_relaxation].current[name]))
        edit.blockSignals(False)


    @jit()
    def model(self, logFrequency, alpha, beta, tau, chiT, chiS):
        return chiS + (chiT)/((1 + (10**logFrequency * np.power(10, tau) * 1j )**(1- alpha))**beta)
        #return chiS + (chiT - chiS)/np.power((1 + np.power(2*np.pi, np.power(10, logFrequency)*tau*1j), 1 - alpha), beta)



    def costF(self, p):
        rest = self.df.loc[self.df['Show']==True]


        sum_real = 0
        sum_img = 0
        i = 0
        while i < len(self.fitItem.relaxations):
            sum_real += self.model(rest["FrequencyLog"].values, p[0+i*5], p[1+i*5], p[2+i*5], p[3+i*5], p[4+i*5]).real
            sum_img += -self.model(rest["FrequencyLog"].values, p[0+i*5], p[1+i*5], p[2+i*5], p[3+i*5], p[4+i*5]).imag

            i += 1

        dif_real = np.power(sum_real - rest['ChiPrimeMol'], 2)
        dif_img = np.power(sum_img - rest['ChiBisMol'], 2)


        return  dif_real + dif_img


    def makeAutoFit(self):
        l = len(self.fitItem.relaxations)
        r = AppState.ranges 
        b = ([r['alpha'][0], r['beta'][0], r['tau'][0], r['chiT'][0], r['chiS'][0]], [r['alpha'][1], r['beta'][1], r['tau'][1], r['chiT'][1], r['chiS'][1]])
        tmp = (b[0]*l, b[1]*l)
        b  = tmp
        eps = 0.000000000001
        ui = self.fitItem.ui

        p = []
        i = 0
        while i < l:

            current = self.fitItem.relaxations[i].current

            if ui.checkBox_ChiS.isChecked():
                b[0][4+i*5] = max(current["chiS"] - eps, b[0][4+i*5])
                b[1][4+i*5] = min(current["chiS"] + eps, b[1][4+i*5])
            if ui.checkBox_ChiT.isChecked():
                b[0][3+i*5] = max(current["chiT"] - eps, b[0][3+i*5])
                b[1][3+i*5] = min(current["chiT"] + eps, b[1][3+i*5])
            if ui.checkBox_Tau.isChecked():
                b[0][2+i*5] = max(current["tau"] - eps, b[0][2+i*5])
                b[1][2+i*5] = min(current["tau"] + eps, b[1][2+i*5])
            if ui.checkBox_Beta.isChecked():
                b[0][1+i*5] = max(current["beta"] - eps, b[0][1+i*5])
                b[1][1+i*5] = min(current["beta"] + eps, b[1][1+i*5])
            if ui.checkBox_Alpha.isChecked():
                b[0][0+i*5] = max(current["alpha"] - eps, b[0][0+i*5])
                b[1][0+i*5] = min(current["alpha"] + eps, b[1][0+i*5])

            p = p + list(current.values())
            i += 1

        res = least_squares(self.costF, tuple(p), bounds=b)

        print("Fit results: ", res.x)
        i = 0
        while i < len(self.fitItem.relaxations):
            current = self.fitItem.relaxations[i].current
            j = 0 + i*5
            for key in current.keys():
                print(res.x[j])
                current[key] = res.x[j]
                j += 1
            i += 1

        current = self.fitItem.relaxations[self.nr_of_relaxation].current
        for key, edit  in ui.editFit2D.items():
            edit.setText(str(round(current[key],9)))
            self.edit_to_slider(ui.sliderFit2D[key], edit, key)

        


        U, s, Vh = linalg.svd(res.jac, full_matrices=False)
        tol = np.finfo(float).eps*s[0]*max(res.jac.shape)
        w = s > tol
        cov = (Vh[w].T/s[w]**2) @ Vh[w]  # robust covariance matrix

        chi2dof = np.sum(res.fun**2)/(res.fun.size - res.x.size)
        cov *= chi2dof

        perr = np.sqrt(np.diag(cov))     # 1sigma uncertainty on fitted parameters
        print(f"Error{perr}")
        for i in range(len(self.fitItem.relaxations)):
            print(perr[i*5:i*5+5])
            self.fitItem.relaxations[i].current_error = perr[i*5:i*5+5]


        self.fitItem.ui.refreshFitFr()

    def saveFit(self):
        self.fitItem.wasSaved = True
        for r in self.fitItem.relaxations:
            for key in self.fitItem.ui.editFit2D:
                r.previous[key] = r.current[key]
            for i in range(len(r.error)):
                r.error[i] = r.current_error[i]

        self.fitItem.ui.refreshFitFr()

    def next(self):
        p = self.fitItem.parent()
        p.child((self.fitItem.row() + 1) % p.rowCount(), 0).changePage(self.fitItem)

    def previous(self):
        p = self.fitItem.parent()
        p.child((self.fitItem.row() - 1) % p.rowCount(), 0).changePage(self.fitItem)

    def set_saved_as_current(self):
        for r in self.fitItem.relaxations:
            for key in r.current.keys():
                r.current[key] = r.previous[key]
            
            for i in range(len(r.error)):
                r.current_error[i] = r.error[i]
        self.refresh()


class plotFitChi1(plotFitChi):
    def __init__(self):
        super().__init__()
        self.xStr = "FrequencyLog"

    def refresh(self):
        print('rChi1')
        self.ax.cla()
        df = self.df

        self.fig.canvas.mpl_connect('pick_event', self.onClick)
        self.ax.set(title=r"$\chi^{\prime}$", xlabel=r"$\log (v / Hz)$", ylabel=r"$\chi^{\prime} /cm^3*mol^{-1}$")
        self.ax.grid(True, linestyle='--', linewidth=1, color=mcolors.CSS4_COLORS["silver"])
        #self.ax.grid(True, which="minor", linestyle="--")
        
        self.ax.xaxis.set_major_locator(LinearLocator(10))
        # self.ax.xaxis.set_minor_locator(AutoMinorLocator(2))

        self.ax.yaxis.set_major_locator(LinearLocator(8))
        # self.ax.yaxis.set_minor_locator(AutoMinorLocator(2))

        shown = df.loc[df["Show"]== True]
        hiden = df.loc[df["Show"]== False]

        
        self.ax.plot( shown["FrequencyLog"].values, shown["ChiPrimeMol"].values, "o", label = "Experimental data", picker=15, c=mcolors.TABLEAU_COLORS["tab:blue"])
        self.ax.plot( hiden["FrequencyLog"].values, hiden["ChiPrimeMol"].values, "o", label = "Hiden Experimental data", picker=15, c=mcolors.TABLEAU_COLORS["tab:orange"])
        color_nr = 0
        for c in plotFitChi.curves:
            self.ax.plot(plotFitChi.domain, c.real, '--', c=mcolors.TABLEAU_COLORS[self.colors_names[color_nr]])
            if self.fitItem.wasSaved: 
                self.ax.plot(plotFitChi.domain, c.real_saved, '-', c=mcolors.TABLEAU_COLORS[self.colors_names[color_nr]] )
            color_nr = (color_nr + 1) % len(self.colors_names)

        if len(plotFitChi.curves) > 1:
            self.ax.plot(plotFitChi.domain, plotFitChi.curves_sum.real, '--', c=mcolors.TABLEAU_COLORS["tab:cyan"] )

            if self.fitItem.wasSaved:
                self.ax.plot(plotFitChi.domain, plotFitChi.curves_sum.real_saved, '-', c=mcolors.TABLEAU_COLORS["tab:cyan"])

        self.draw()
    
    def valueChanged(self):
        return
        #return super().valueChanged()

    def value_edited(self, param):
        return
        #return super().value_edited()

    def makeAutoFit(self):
        return
       # return super().makeAutoFit()

class plotFitChi2(plotFitChi):
    def __init__(self):
        super().__init__()
        self.xStr = "FrequencyLog"

    def refresh(self):
        self.ax.cla()
        df = self.df

        self.fig.canvas.mpl_connect('pick_event', self.onClick)

        self.ax.set(title=r"$\chi^{\prime \prime}$", xlabel=r"$\log (v / Hz)$", ylabel=r"$\chi^{\prime \prime} /cm^3*mol^{-1}$")

        self.ax.grid(True, linestyle='--', linewidth=1, color=mcolors.CSS4_COLORS["silver"])
        #self.ax.grid(True, which="minor", linestyle="--")
        
        self.ax.xaxis.set_major_locator(LinearLocator(10))
        # self.ax.xaxis.set_minor_locator(AutoMinorLocator(2))

        self.ax.yaxis.set_major_locator(LinearLocator(8))
        # self.ax.yaxis.set_minor_locator(AutoMinorLocator(2))
        
        shown = df.loc[df["Show"]== True]
        hiden = df.loc[df["Show"]== False]

        self.ax.plot( shown["FrequencyLog"].values, shown["ChiBisMol"].values, "o", label = "Experimental data", picker=15, c=mcolors.TABLEAU_COLORS["tab:blue"])
        self.ax.plot( hiden["FrequencyLog"].values, hiden["ChiBisMol"].values, "o", label = "Hiden Experimental data", picker=15, c=mcolors.TABLEAU_COLORS["tab:orange"])

        color_nr = 0
        for c in plotFitChi.curves:
            self.ax.plot(plotFitChi.domain, c.img, '--', c=mcolors.TABLEAU_COLORS[self.colors_names[color_nr]], label=f"relaxation nr {color_nr+1}")
            if self.fitItem.wasSaved: 
                self.ax.plot(plotFitChi.domain, c.img_saved, '-', c=mcolors.TABLEAU_COLORS[self.colors_names[color_nr]], label=f"saved relaxation nr {color_nr+1}")
            color_nr = (color_nr + 1) % len(self.colors_names)

        if len(plotFitChi.curves) > 1:
            self.ax.plot(plotFitChi.domain, plotFitChi.curves_sum.img, '--', c=mcolors.TABLEAU_COLORS["tab:cyan"], label="sum of relaxations" )

            if self.fitItem.wasSaved:
                self.ax.plot(plotFitChi.domain, plotFitChi.curves_sum.img_saved, '-', c=mcolors.TABLEAU_COLORS["tab:cyan"], label="saved sum of relaxations")

        leg = self.ax.legend()
        if leg:
            leg.set_draggable(True)

        self.draw()

    def valueChanged(self):
        return
        #return super().valueChanged()

    def value_edited(self, param):
        return
        #return super().value_edited()

    def makeAutoFit(self):
        return
        #return super().makeAutoFit()