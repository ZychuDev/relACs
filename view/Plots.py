import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
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
        self.draw()

    def plotFromData():
        pass


class PlotChi(FigureCanvasQTAgg):
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(1,1), dpi=100)
        super().__init__(self.fig)
        self.xStr = "ChiPrime"

    def change(self, dataItem):
        self.dataItem= dataItem
        self.df = dataItem.df
        self.name = dataItem.name
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
        self.ax.plot(rest["ChiPrime"].values, rest["ChiBis"], "o", picker=15 )
        self.ax.plot(selected["ChiPrime"].values, selected["ChiBis"], "o", picker=15 )
        
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
        self.ax.plot(rest["FrequencyLog"].values, rest["ChiPrime"], "o", picker=15 )
        self.ax.plot(selected["FrequencyLog"].values, selected["ChiPrime"], "o", picker=15 )
        

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
        self.ax.plot(rest["FrequencyLog"].values, rest["ChiBis"], "o", picker=15 )
        self.ax.plot(selected["FrequencyLog"].values, selected["ChiBis"], "o", picker=15 )
        
        self.draw()

class plotFitChi(FigureCanvasQTAgg):
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(1,1), dpi=100)
        super().__init__(self.fig)
        self.xStr = "ChiPrime"

    def change(self, fitFrequecyItem):
        self.fitItem = fitFrequecyItem
        self.name = fitFrequecyItem.name
        self.df = fitFrequecyItem.df
        self.refresh()

    def refresh(self):
        self.ax.cla()
        df = self.df
        self.fig.canvas.mpl_connect('pick_event', self.onClick)

        self.ax.set(xlabel="log v", ylabel="Chi'", title="Ch'(log v)")
        self.ax.grid()
        print("###")
        print(df)
        shown = df.loc[df["Show"]== True]
        hiden = df.loc[df["Show"]== False]

        self.ax.plot( shown["ChiPrime"].values, shown["ChiBis"].values, "o", label = "Experimental data", picker=15)
        self.ax.plot( hiden["ChiPrime"].values, hiden["ChiBis"].values, "o", label = "Hiden Experimental data", picker=15)

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

class plotFitChi1(plotFitChi):
    def __init__(self):
        super().__init__()
        self.xStr = "FrequencyLog"

    def refresh(self):
        self.ax.cla()
        df = self.df
        self.fig.canvas.mpl_connect('pick_event', self.onClick)
        self.ax.grid()
        self.ax.set(title="Ch2 vs logarithm of frequency")
        shown = df.loc[df["Show"]== True]
        hiden = df.loc[df["Show"]== False]

        self.ax.plot( shown["FrequencyLog"].values, shown["ChiPrime"].values, "o", label = "Experimental data", picker=15)
        self.ax.plot( hiden["FrequencyLog"].values, hiden["ChiPrime"].values, "o", label = "Hiden Experimental data", picker=15)

        self.draw()

class plotFitChi2(plotFitChi):
    def __init__(self):
        super().__init__()
        self.xStr = "FrequencyLog"

    def refresh(self):
        self.ax.cla()
        df = self.df
        self.fig.canvas.mpl_connect('pick_event', self.onClick)
        self.ax.grid()
        self.ax.set(title="Ch2 vs logarithm of frequency")
        shown = df.loc[df["Show"]== True]
        hiden = df.loc[df["Show"]== False]

        self.ax.plot( shown["FrequencyLog"].values, shown["ChiBis"].values, "o", label = "Experimental data", picker=15)
        self.ax.plot( hiden["FrequencyLog"].values, hiden["ChiBis"].values, "o", label = "Hiden Experimental data", picker=15)

        self.draw()

        



