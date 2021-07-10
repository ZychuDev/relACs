from numba.core.types.scalars import Float, Integer
from view.AppStateBase import *
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from numba import jit
from scipy.optimize import least_squares
from scipy.interpolate import interp1d
from scipy import linalg

from .Validator import Validator

class plotFitChi(FigureCanvasQTAgg):
    yy = []
    real = []
    img = []
    domain = []

    nr_of_connections = 0
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(1,1), dpi=100)
        super().__init__(self.fig)
        self.xStr = "ChiPrimeMol"

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
        print("Nr of connections" + str(plotFitChi.nr_of_connections))
        if plotFitChi.nr_of_connections == 3:
            try:
                self.fitItem.ui.horizontalSlider_Alpha.valueChanged.disconnect()
                self.fitItem.ui.horizontalSlider_Beta.valueChanged.disconnect()
                self.fitItem.ui.horizontalSlider_Tau.valueChanged.disconnect()
                self.fitItem.ui.horizontalSlider_ChiS.valueChanged.disconnect()
                self.fitItem.ui.horizontalSlider_ChiT.valueChanged.disconnect()
                self.fitItem.ui.pushButtonFit.clicked.disconnect()
                self.fitItem.ui.pushButtonSave.clicked.disconnect()
                self.fitItem.ui.pushButtonNext.clicked.disconnect()
                self.fitItem.ui.pushButtonPrevious.clicked.disconnect()

                self.fitItem.ui.lineEdit_Alpha.editingFinished.disconnect()
                self.fitItem.ui.lineEdit_Beta.editingFinished.disconnect()
                self.fitItem.ui.lineEdit_Tau.editingFinished.disconnect()
                self.fitItem.ui.lineEdit_ChiT.editingFinished.disconnect()
                self.fitItem.ui.lineEdit_ChiS.editingFinished.disconnect()
                plotFitChi.nr_of_connections = 0
            except Exception: pass

        plotFitChi.nr_of_connections = plotFitChi.nr_of_connections + 1
        self.fitItem.ui.horizontalSlider_Alpha.valueChanged.connect(self.value_changed_alpha)
        self.fitItem.ui.horizontalSlider_Beta.valueChanged.connect(self.value_changed_beta)
        self.fitItem.ui.horizontalSlider_Tau.valueChanged.connect(self.value_changed_tau)
        self.fitItem.ui.horizontalSlider_ChiS.valueChanged.connect(self.value_changed_chiS)
        self.fitItem.ui.horizontalSlider_ChiT.valueChanged.connect(self.value_changed_chiT)
        self.fitItem.ui.pushButtonFit.clicked.connect(self.makeAutoFit)
        self.fitItem.ui.pushButtonSave.clicked.connect(self.saveFit)
        self.fitItem.ui.pushButtonNext.clicked.connect(self.next)
        self.fitItem.ui.pushButtonPrevious.clicked.connect(self.previous)
        self.fitItem.ui.lineEdit_Alpha.editingFinished.connect(self.value_edited)
        self.fitItem.ui.lineEdit_Beta.editingFinished.connect(self.value_edited)
        self.fitItem.ui.lineEdit_Tau.editingFinished.connect(self.value_edited)
        self.fitItem.ui.lineEdit_ChiT.editingFinished.connect(self.value_edited)
        self.fitItem.ui.lineEdit_ChiS.editingFinished.connect(self.value_edited)



    def refresh(self):
        self.ax.cla()
        df = self.df
        self.fig.canvas.mpl_connect('pick_event', self.onClick)

        self.ax.set(xlabel="Chi '", ylabel="Chi''", title="Ch'(log v)")
        self.ax.grid()
        shown = df.loc[df["Show"]== True]
        hiden = df.loc[df["Show"]== False]

        self.ax.plot( shown["ChiPrimeMol"].values, shown["ChiBisMol"].values, "o", label = "Experimental data", picker=15)
        self.ax.plot( hiden["ChiPrimeMol"].values, hiden["ChiBisMol"].values, "o", label = "Hiden Experimental data", picker=15)

        step = (df['FrequencyLog'].max() - df['FrequencyLog'].min())/50
        min = df['FrequencyLog'].min()
        plotFitChi.domain = []
        while min <= (df['FrequencyLog'].max() + step):
            plotFitChi.domain.append(min)
            min += step

        plotFitChi.yy = []
        
        plotFitChi.yySaved = []
        for x in plotFitChi.domain:
            plotFitChi.yy.append(self.model(x, alpha = self.fitItem.current["alpha"]
                , beta = self.fitItem.current["beta"]
                , tau = self.fitItem.current["tau"]
                , chiT = self.fitItem.current["chiT"]
                , chiS = self.fitItem.current["chiS"] ))

            plotFitChi.yySaved.append(self.model(x, alpha = self.fitItem.previous["alpha"]
                , beta = self.fitItem.previous["beta"]
                , tau = self.fitItem.previous["tau"]
                , chiT = self.fitItem.previous["chiT"]
                , chiS = self.fitItem.previous["chiS"] ))

        plotFitChi.real = []
        plotFitChi.img = []
        for c in plotFitChi.yy:
            plotFitChi.real.append(c.real)
            plotFitChi.img.append(-c.imag)

        plotFitChi.realSaved = []
        plotFitChi.imgSaved = []
        for c in plotFitChi.yySaved:
            plotFitChi.realSaved.append(c.real)
            plotFitChi.imgSaved.append(-c.imag)

        
        self.ax.plot(plotFitChi.real, plotFitChi.img, "-", color="blue")
        if self.fitItem.wasSaved: 
            self.ax.plot(plotFitChi.realSaved, plotFitChi.imgSaved, "-", color="red" )

        self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1),fancybox=True, shadow=True, ncol=3)
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
            v = self.fitItem.current[name]
        v = float(v)
        v = float(m(v))
        return round(v)

    def value_changed_alpha(self):
        self.slider_to_edit(self.fitItem.ui.horizontalSlider_Alpha, self.fitItem.ui.lineEdit_Alpha, 'alpha')
        self.fitItem.show()

    def value_changed_beta(self):
        self.slider_to_edit(self.fitItem.ui.horizontalSlider_Beta, self.fitItem.ui.lineEdit_Beta, 'beta')
        self.fitItem.show()

    def value_changed_tau(self):
        self.slider_to_edit(self.fitItem.ui.horizontalSlider_Tau, self.fitItem.ui.lineEdit_Tau, 'tau')
        self.fitItem.show()

    def value_changed_chiT(self):
        self.slider_to_edit(self.fitItem.ui.horizontalSlider_ChiT, self.fitItem.ui.lineEdit_ChiT, 'chiT')
        self.fitItem.show()

    def value_changed_chiS(self):
        self.slider_to_edit(self.fitItem.ui.horizontalSlider_ChiS, self.fitItem.ui.lineEdit_ChiS, 'chiS')
        self.fitItem.show()
    
        
        
        

    def value_edited(self): 
        self.edit_to_slider(self.fitItem.ui.horizontalSlider_Alpha, self.fitItem.ui.lineEdit_Alpha, 'alpha')
        self.edit_to_slider(self.fitItem.ui.horizontalSlider_Beta, self.fitItem.ui.lineEdit_Beta, 'beta')
        self.edit_to_slider(self.fitItem.ui.horizontalSlider_Tau, self.fitItem.ui.lineEdit_Tau, 'tau')
        self.edit_to_slider(self.fitItem.ui.horizontalSlider_ChiT, self.fitItem.ui.lineEdit_ChiT, 'chiT')
        self.edit_to_slider(self.fitItem.ui.horizontalSlider_ChiS, self.fitItem.ui.lineEdit_ChiS, 'chiS')

        self.fitItem.show()

    def edit_to_slider(self, slider, edit, name):
        v = str(edit.text())
        if v == '':
            v = self.fitItem.current[name]
        self.fitItem.current[name] = float(v)
        slider.blockSignals(True)
        slider.setValue(self.map_value_reverse(slider,edit , name))
        slider.blockSignals(False)

    def slider_to_edit(self, slider, edit, name):
        self.fitItem.current[name] = self.map_value(slider, name)
        edit.blockSignals(True)
        edit.setText(str(self.fitItem.current[name]))
        edit.blockSignals(False)


    @jit()
    def model(self, logFrequency, alpha, beta, tau, chiT, chiS):
        return chiS + (chiT)/((1 + (10**logFrequency * 2 * np.pi * np.power(10, tau) * 1j )**(1- alpha))**beta)
        #return chiS + (chiT - chiS)/np.power((1 + np.power(2*np.pi, np.power(10, logFrequency)*tau*1j), 1 - alpha), beta)



    def costF(self, p):
        rest = self.df.loc[self.df['Show']==True]
        dif1 = np.power(self.model(rest["FrequencyLog"].values, p[0], p[1], p[2], p[3], p[4]).real - rest['ChiPrimeMol'], 2)
        dif2 = np.power(-self.model(rest["FrequencyLog"].values, p[0], p[1], p[2], p[3], p[4]).imag - rest['ChiBisMol'], 2)
        return  dif1 + dif2


    def makeAutoFit(self):
        r = AppState.ranges 
        b = ([r['alpha'][0], r['beta'][0], r['tau'][0], r['chiT'][0], r['chiS'][0]], [r['alpha'][1], r['beta'][1], r['tau'][1], r['chiT'][1], r['chiS'][1]])
        eps = 0.000000000001
        ui = self.fitItem.ui

        if ui.checkBox_ChiS.isChecked():
            b[0][4] = max(self.fitItem.current["chiS"] - eps, b[0][4])
            b[1][4] = min(self.fitItem.current["chiS"] + eps, b[1][4])
        if ui.checkBox_ChiT.isChecked():
            b[0][3] = max(self.fitItem.current["chiT"] - eps, b[0][3])
            b[1][3] = min(self.fitItem.current["chiT"] + eps, b[1][3])
        if ui.checkBox_Tau.isChecked():
            b[0][2] = max(self.fitItem.current["tau"] - eps, b[0][2])
            b[1][2] = min(self.fitItem.current["tau"] + eps, b[1][2])
        if ui.checkBox_Beta.isChecked():
            b[0][1] = max(self.fitItem.current["beta"] - eps, b[0][1])
            b[1][1] = min(self.fitItem.current["beta"] + eps, b[1][1])
        if ui.checkBox_Alpha.isChecked():
            b[0][0] = max(self.fitItem.current["alpha"] - eps, b[0][0])
            b[1][0] = min(self.fitItem.current["alpha"] + eps, b[1][0])

        res = least_squares(self.costF, tuple(self.fitItem.current.values()), bounds=b)

        i = 0
        for key in self.fitItem.current.keys():
            self.fitItem.current[key] = res.x[i]
            i = i + 1

        ui.lineEdit_Alpha.setText(str(round(self.fitItem.current["alpha"],6)))
        ui.lineEdit_Beta.setText(str(round(self.fitItem.current["beta"],6)))
        ui.lineEdit_Tau.setText(str(round(self.fitItem.current["tau"],6)))
        ui.lineEdit_ChiT.setText(str(round(self.fitItem.current["chiT"],6)))
        ui.lineEdit_ChiS.setText(str(round(self.fitItem.current["chiS"],6)))

        self.value_edited()
        U, s, Vh = linalg.svd(res.jac, full_matrices=False)
        tol = np.finfo(float).eps*s[0]*max(res.jac.shape)
        w = s > tol
        cov = (Vh[w].T/s[w]**2) @ Vh[w]  # robust covariance matrix

        chi2dof = np.sum(res.fun**2)/(res.fun.size - res.x.size)
        cov *= chi2dof

        perr = np.sqrt(np.diag(cov))     # 1sigma uncertainty on fitted parameters

        self.fitItem.error = perr

    def saveFit(self):
        self.fitItem.wasSaved = True
        for key in self.fitItem.ui.editFit2D:
            self.fitItem.previous[key] = self.fitItem.current[key]

        self.fitItem.show()

    def next(self):
        p = self.fitItem.parent()
        p.child((self.fitItem.row() + 1) % p.rowCount(), 0).changePage()

    def previous(self):
        p = self.fitItem.parent()
        p.child((self.fitItem.row() - 1) % p.rowCount(), 0).changePage()










class plotFitChi1(plotFitChi):
    def __init__(self):
        super().__init__()
        self.xStr = "FrequencyLog"

    def refresh(self):
        print('rChi1')
        self.ax.cla()
        df = self.df
        self.fig.canvas.mpl_connect('pick_event', self.onClick)
        self.ax.grid()
        self.ax.set(title="PlotFitChi1")
        shown = df.loc[df["Show"]== True]
        hiden = df.loc[df["Show"]== False]

        self.ax.plot( shown["FrequencyLog"].values, shown["ChiPrimeMol"].values, "o", label = "Experimental data", picker=15)
        self.ax.plot( hiden["FrequencyLog"].values, hiden["ChiPrimeMol"].values, "o", label = "Hiden Experimental data", picker=15)
        self.ax.plot(plotFitChi.domain, plotFitChi.real, '-', color="blue")
        if self.fitItem.wasSaved: 
            self.ax.plot(plotFitChi.domain, plotFitChi.realSaved, '-', color="red")
        self.draw()
    
    def valueChanged(self):
        return
        #return super().valueChanged()

    def value_edited(self):
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
        self.ax.grid()
        self.ax.set(title="plotFitChi2")
        shown = df.loc[df["Show"]== True]
        hiden = df.loc[df["Show"]== False]

        self.ax.plot( shown["FrequencyLog"].values, shown["ChiBisMol"].values, "o", label = "Experimental data", picker=15)
        self.ax.plot( hiden["FrequencyLog"].values, hiden["ChiBisMol"].values, "o", label = "Hiden Experimental data", picker=15)
        self.ax.plot(plotFitChi.domain, plotFitChi.img, '-', color="blue")
        if self.fitItem.wasSaved: 
            self.ax.plot(plotFitChi.domain, plotFitChi.imgSaved, '-', color="red")
        self.draw()

    def valueChanged(self):
        return
        #return super().valueChanged()

    def value_edited(self):
        return
        #return super().value_edited()

    def makeAutoFit(self):
        return
        #return super().makeAutoFit()