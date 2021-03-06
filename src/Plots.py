"""
    The relACs is a analysis tool for magnetic data for SMM systems using
    various models for ac magnetic characteristics and the further reliable
    determination of diverse relaxation processes.

    Copyright (C) 2021  Wiktor Zychowicz & Mikolaj Zychowicz

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
""" 

import numpy as np
import configparser
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

class Plot(FigureCanvasQTAgg):
    def __init__(self, caption):
        config = configparser.RawConfigParser()
        config.optionxform = str
        config.read('settings/default_settings.ini')

        fig, self.ax = plt.subplots(figsize=(5,4), dpi=int(config['Plot']['dpi']))
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
        config = configparser.RawConfigParser()
        config.optionxform = str
        config.read('settings/default_settings.ini')
        
        self.fig, self.ax = plt.subplots(figsize=(1,1), dpi=int(config['Plot']['dpi']))
        self.fig.patch.set_facecolor("#f0f0f0")
        super().__init__(self.fig)
        self.xStr = "ChiPrimeMol"
        self.picker_radius = int(config['Plot']['picker_radius'])
        
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
        self.ax.set(title=r"Cole-Cole", xlabel=r"$\chi^{\prime} /cm^3*mol^{-1}$", ylabel=r"$\chi^{\prime \prime} / cm^3*mol^{-1}$")
        selected = df.loc[df["Selected"] == True]
        rest = df.loc[df["Selected"] == False]
        self.ax.plot(rest["ChiPrimeMol"].values, rest["ChiBisMol"], "o", picker=self.picker_radius )
        self.ax.plot(selected["ChiPrimeMol"].values, selected["ChiBisMol"], "o", picker=self.picker_radius)
        
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
        
        self.ax.set(title=r"$\chi^{\prime}$", xlabel=r"$\log {\frac{v}{Hz}}$", ylabel=r"$\chi^{\prime} /cm^3*mol^{-1}$")
        selected = df.loc[df["Selected"] == True]
        rest = df.loc[df["Selected"] == False]
        self.ax.plot(rest["FrequencyLog"].values, rest["ChiPrimeMol"], "o", picker=self.picker_radius )
        self.ax.plot(selected["FrequencyLog"].values, selected["ChiPrimeMol"], "o", picker=self.picker_radius )
        

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
        self.ax.set(title=r"$\chi^{\prime \prime}$", xlabel=r"$\log {\frac{v}{Hz}}$", ylabel=r"$\chi^{\prime \prime} /cm^3*mol^{-1}$")
        selected = df.loc[df["Selected"] == True]
        rest = df.loc[df["Selected"] == False]
        self.ax.plot(rest["FrequencyLog"].values, rest["ChiBisMol"], "o", picker=self.picker_radius )
        self.ax.plot(selected["FrequencyLog"].values, selected["ChiBisMol"], "o", picker=self.picker_radius )

        
        self.draw()




        



