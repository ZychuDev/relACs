import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from mpl_toolkits.mplot3d import Axes3D

from numba import jit

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
        self.draw()

    def plotFromData():
        pass

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

class PlotChi(FigureCanvasQTAgg):
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(1,1), dpi=100)
        super().__init__(self.fig)
        self.xStr = "ChiPrimeMol"

    def change(self, dataItem):
        self.dataItem= dataItem
        self.df = dataItem.df
        self.name = dataItem.name

        nodes = self.df["FrequencyLog"]
        self.refresh()

    def refresh(self):
        self.ax.cla()
        df = self.df
      
        self.fig.canvas.mpl_connect('pick_event', self.onClick)
        self.ax.set(xlabel="Chi'", ylabel='Chi''', title="Chi' against Chi''")
        self.ax.grid()
        self.ax.set(title="Ch1 vs logarithm of frequency")
        selected = df.loc[df["Selected"] == True]
        rest = df.loc[df["Selected"] == False]
        self.ax.plot(rest["ChiPrimeMol"].values, rest["ChiBisMol"], "o", picker=15 )
        self.ax.plot(selected["ChiPrimeMol"].values, selected["ChiBisMol"], "o", picker=15 )
        
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
        self.df.loc[self.df[self.xStr] == x[0], "Selected"] = not bool(self.df.loc[self.df[self.xStr] == x[0]]['Selected'].values[0])
        self.dataItem.ui.refreshInspect()

    def deletePoint(self, x):
        self.df.drop(self.df.loc[self.df[self.xStr] == x[0]].index, inplace=True)
        self.dataItem.df.drop(self.df.loc[self.df[self.xStr] == x[0]].index, inplace=True)
        self.dataItem.ui.refreshInspect()


class PlotChi1(PlotChi):
    def __init__(self):
        super().__init__()
        self.xStr = "FrequencyLog"

    def refresh(self):
        self.ax.cla()
        df = self.df
        self.fig.canvas.mpl_connect('pick_event', self.onClick)
        self.ax.grid()
        self.ax.set(title="Ch2 vs logarithm of frequency")
        selected = df.loc[df["Selected"] == True]
        rest = df.loc[df["Selected"] == False]
        self.ax.plot(rest["FrequencyLog"].values, rest["ChiPrimeMol"], "o", picker=15 )
        self.ax.plot(selected["FrequencyLog"].values, selected["ChiPrimeMol"], "o", picker=15 )
        

        self.draw()


class PlotChi2(PlotChi):
    
    def __init__(self):
        super().__init__()
        self.xStr = "FrequencyLog"

    def refresh(self):
        self.ax.cla()
        df = self.df
        self.fig.canvas.mpl_connect('pick_event', self.onClick)

        self.ax.grid()
        self.ax.set(title="Chi' against Chi''")
        selected = df.loc[df["Selected"] == True]
        rest = df.loc[df["Selected"] == False]
        self.ax.plot(rest["FrequencyLog"].values, rest["ChiBisMol"], "o", picker=15 )
        self.ax.plot(selected["FrequencyLog"].values, selected["ChiBisMol"], "o", picker=15 )

        
        self.draw()



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

        print(plotFitChi.nr_of_connections)
        if plotFitChi.nr_of_connections == 3:
            try:
                self.fitItem.ui.horizontalSlider_Alpha.valueChanged.disconnect()
                self.fitItem.ui.horizontalSlider_Beta.valueChanged.disconnect()
                self.fitItem.ui.horizontalSlider_Tau.valueChanged.disconnect()
                self.fitItem.ui.horizontalSlider_ChiS.valueChanged.disconnect()
                self.fitItem.ui.horizontalSlider_ChiT.valueChanged.disconnect()
                plotFitChi.nr_of_connections = 0
            except Exception: pass

        plotFitChi.nr_of_connections = plotFitChi.nr_of_connections + 1
        self.fitItem.ui.horizontalSlider_Alpha.valueChanged.connect(self.valueChanged)
        self.fitItem.ui.horizontalSlider_Beta.valueChanged.connect(self.valueChanged)
        self.fitItem.ui.horizontalSlider_Tau.valueChanged.connect(self.valueChanged)
        self.fitItem.ui.horizontalSlider_ChiS.valueChanged.connect(self.valueChanged)
        self.fitItem.ui.horizontalSlider_ChiT.valueChanged.connect(self.valueChanged)

        

        

    def refresh(self):
        self.ax.cla()
        df = self.df
        self.fig.canvas.mpl_connect('pick_event', self.onClick)

        self.ax.set(xlabel="log v", ylabel="Chi'", title="Ch'(log v)")
        self.ax.grid()
        print("rChi")
        shown = df.loc[df["Show"]== True]
        hiden = df.loc[df["Show"]== False]

        self.ax.plot( shown["ChiPrimeMol"].values, shown["ChiBisMol"].values, "o", label = "Experimental data", picker=15)
        self.ax.plot( hiden["ChiPrimeMol"].values, hiden["ChiBisMol"].values, "o", label = "Hiden Experimental data", picker=15)

        step = (df['FrequencyLog'].max() - df['FrequencyLog'].min())/50
        min = df['FrequencyLog'].min()
        plotFitChi.domain = []
        while min < df['FrequencyLog'].max():
            plotFitChi.domain.append(min)
            min += step

        plotFitChi.yy = []
        for x in plotFitChi.domain:
            plotFitChi.yy.append(self.model(x, alpha = self.fitItem.current["alpha"]
        , beta = self.fitItem.current["beta"]
        , tau = self.fitItem.current["tau"]
        , chiT = self.fitItem.current["chiT"]
        , chiS = self.fitItem.current["chiS"] ))

        plotFitChi.real = []
        plotFitChi.img = []
        for c in plotFitChi.yy:
            plotFitChi.real.append(c.real)
            plotFitChi.img.append(-c.imag)

        self.ax.plot(plotFitChi.real, plotFitChi.img, "-")
        # if str == "ChiPrimeMol":
        #     self.chi = self.sChi.get()
        #     self.tau = 10**self.sTau.get()
        #     self.diff = self.sDiff.get()
        #     self.alpha = self.sAlpha.get()
        # else:
        #     self.tau = 10**self.sTau.get()
        #     self.diff = self.sDiff.get()
        #     self.alpha = self.sAlpha.get()

        # if str == "ChiPrimeMol":
        #     yy = (self.models[str]([self.chi], [shown["Omega"], self.diff, self.alpha, self.tau]))
        # else:
        #     yy = (self.models[str]([self.diff,self.alpha,self.tau], [shown["Omega"]]))

        # self.ax.plot(shown["FrequencyLog"], yy,'-', label = "Fitted model", picker=0)

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
        #resolution = (slider.maximum() - slider.minimum())/slider.singleStep()
        #max = self.fitItem.ui.appState.ranges[name][1] #ranges -> tuple
        #min = self.fitItem.ui.appState.ranges[name][0] #ranges -> tuple
        ranges ={'alpha':(0,1), 'beta':(0,1), 'tau':(-10,0), 'chiT':(0,10), 'chiS':(0,10)}
        max = ranges[name][1]
        min = ranges[name][0]
        leftSpan = slider.maximum() - slider.minimum()
        rightSpan = max - min
        valueScaled = float(slider.value() - slider.minimum()) / float(leftSpan)
        return round(min + (valueScaled * rightSpan),2)

    def valueChanged(self):
        self.fitItem.current["alpha"] = self.map_value(self.fitItem.ui.horizontalSlider_Alpha, 'alpha')
        self.fitItem.current["beta"] = self.map_value(self.fitItem.ui.horizontalSlider_Beta, 'beta')
        self.fitItem.current["tau"] = self.map_value(self.fitItem.ui.horizontalSlider_Tau, 'tau')
        self.fitItem.current["chiT"] = self.map_value(self.fitItem.ui.horizontalSlider_ChiT, 'chiT')
        self.fitItem.current["chiS"] = self.map_value(self.fitItem.ui.horizontalSlider_ChiS, 'chiS')

        self.fitItem.ui.lineEdit_Alpha.setText(str(self.fitItem.current["alpha"]))
        self.fitItem.ui.lineEdit_Beta.setText(str(self.fitItem.current["beta"]))
        self.fitItem.ui.lineEdit_Tau.setText(str(self.fitItem.current["tau"]))
        self.fitItem.ui.lineEdit_ChiT.setText(str(self.fitItem.current["chiT"]))
        self.fitItem.ui.lineEdit_ChiS.setText(str(self.fitItem.current["chiS"]))

        self.refresh()
    @jit()
    def model(self, logFrequency, alpha, beta, tau, chiT, chiS):
        # alpha = self.fitItem.current["alpha"]
        # beta = self.fitItem.current["beta"]
        # tau = self.fitItem.current["tau"]
        # chiT = self.fitItem.current["chiT"]
        # chiS = self.fitItem.current["chiS"]
        return chiS + (chiT)/((1 + (10**logFrequency * 2 * np.pi * np.power(10, tau) * 1j )**(1- alpha))**beta)
        #return chiS + (chiT - chiS)/np.power((1 + np.power(2*np.pi, np.power(10, logFrequency)*tau*1j), 1 - alpha), beta)








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
        self.ax.plot(plotFitChi.domain, plotFitChi.real, '-')
        self.draw()

class plotFitChi2(plotFitChi):
    def __init__(self):
        super().__init__()
        self.xStr = "FrequencyLog"

    def refresh(self):
        print("rCHi2")
        self.ax.cla()
        df = self.df
        self.fig.canvas.mpl_connect('pick_event', self.onClick)
        self.ax.grid()
        self.ax.set(title="plotFitChi2")
        shown = df.loc[df["Show"]== True]
        hiden = df.loc[df["Show"]== False]

        self.ax.plot( shown["FrequencyLog"].values, shown["ChiBisMol"].values, "o", label = "Experimental data", picker=15)
        self.ax.plot( hiden["FrequencyLog"].values, hiden["ChiBisMol"].values, "o", label = "Hiden Experimental data", picker=15)
        self.ax.plot(plotFitChi.domain, plotFitChi.img, '-')
        self.draw()

        



