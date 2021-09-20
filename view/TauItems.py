from .StandardItem import StandardItem
from PyQt5.QtCore import  Qt

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMenu, QInputDialog
from PyQt5 import QtWidgets
from .Plot3D import *

import pandas as pd
import numpy as np

import functools
import json 
import os 

from .Fit_models import *

class FitTauItem(StandardItem):
    def __init__(self, mainPage, compound, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)
        self.ui = mainPage
        self.name = txt

        self.error = [0,0,0,0,0,0,0,0,0]
        self.residual_error = 0.0
        self.current_error = [0,0,0,0,0,0,0,0,0]
        self.current_residual_error = 0.0

        self.points = []
        self.hidden_points = []

        self.tau = pd.Series()
        self.temp = pd.Series()
        self.field = pd.Series()

        self.hidden_tau = pd.Series()
        self.hidden_temp = pd.Series()
        self.hidden_field = pd.Series()

        names = ['Adir', 'Ndir', 'B1', 'B2', 'B3', 'CRaman', 'NRaman', 'Tau0', 'DeltaE']
        self.previous = {}
        self.current = {}
    
        for p in names:
            if p in compound.log_params:
                self.current[p] = (10**compound.ranges[p][0] + 10**compound.ranges[p][1])/2
                self.previous[p] = (10**compound.ranges[p][0] + 10**compound.ranges[p][1])/2
            else:
                self.current[p] = (compound.ranges[p][0] + compound.ranges[p][1])/2
                self.previous[p] = (compound.ranges[p][0] + compound.ranges[p][1])/2


    def get_jsonable(self):
        jsonable = {'name': self.name, 'error': self.error, 'residual_error': self.residual_error, 
         'current_error': self.current_error, 'current_residual_error':self.current_residual_error,
         'points': self.points, 'hidden_points': self.hidden_points, 'tau': self.tau.to_json(),
         'temp': self.temp.to_json(), 'field':self.field.to_json(), 'hidden_tau': self.hidden_tau.to_json(),
         'hidden_temp': self.hidden_temp.to_json(), 'hidden_field': self.hidden_field.to_json(),
         'previous': self.previous, 'current': self.current}
        return jsonable

    def from_json(self, json):
        self.name = json['name']
        self.error = json['error']
        self.residual_error = json['residual_error']
        self.current_error = json['current_error']
        self.current_residual_error = json['current_residual_error']
        self.points = json['points']
        self.hidden_points = json['hidden_points']
        self.tau = pd.read_json(json['tau'], typ='series', orient='records')
        self.temp = pd.read_json(json['temp'], typ='series', orient='records')
        self.field = pd.read_json(json['field'], typ='series', orient='records')
        self.hidden_tau = pd.read_json(json['hidden_tau'], typ='series', orient='records')
        self.hidden_temp = pd.read_json(json['hidden_temp'], typ='series', orient='records')
        self.hidden_field = pd.read_json(json['hidden_field'], typ='series', orient='records')
        self.previous = json['previous']
        self.current = json['current']

    def save_to_json(self):
        jsonable = self.get_jsonable()
        name = QtWidgets.QFileDialog.getSaveFileName(self.ui.window, 'Save file')

        if name == "":
            return

        with  open(name[0] + '.json' if len(name[0].split('.')) == 1 else name[0][:-5] + '.json' , 'w') as f:
            json.dump(jsonable, f, indent=4)

    def show(self):
        self.ui.WorkingSpace.setCurrentWidget(self.ui.fit3Dpage)

        self.ui.plot3d.refresh()
        self.ui.slice.refresh()

    def change(self):
        self.ui.plot3d.change(self)
        self.ui.slice.change(self)
        self.ui.slice_change_const()

        self.ui.comboBox_slice.setCurrentIndex(0)
        self.ui.WorkingSpace.setCurrentWidget(self.ui.fit3Dpage)






    def set_current_as_saved(self):
        for param in self.current:
            self.current[param] = self.previous[param]

        for i in range(len(self.error)):
            self.current_error[i] = self.error[i]
        self.current_residual_error = self.residual_error


        compound = self.parent().parent()
        for key in self.ui.edit3D:
            if key in compound.log_params:
                self.ui.edit3D[key].setText(str(round(np.log10(self.current[key]), 9)))

            else:
                self.ui.edit3D[key].setText(str(round(self.current[key], 9)))

            self.ui.plot3d.value_edited(key, True)
        self.show()


    def delete_point(self, point):
        self.points.remove(point)
        self.regenerate_points()
    
    def add_point(self, point):
        self.points.append(point)
        self.regenerate_points()

    def delete_hidden_point(self, point):
        self.hidden_points.remove(point)
        self.regenerate_hidden_points()

    def add_hidden_point(self, point):
        self.hidden_points.append(point)
        self.regenerate_hidden_points()

    def regenerate_points(self):
        try:
            unzipped = pd.Series(list(zip(*self.points)))
            self.tau = pd.Series(list(unzipped[0]))
            self.temp = pd.Series(list(unzipped[1]))
            self.field = pd.Series(list(unzipped[2]))
        except KeyError:
            print("Not allowed, unzipped == 0")
            print(f"{unzipped}")

    def regenerate_hidden_points(self):
        try:
            unzipped = pd.Series(list(zip(*self.hidden_points)))
            self.hidden_tau = pd.Series(list(unzipped[0]))
            self.hidden_temp = pd.Series(list(unzipped[1]))
            self.hidden_field = pd.Series(list(unzipped[2]))
        except KeyError:
            print("Not allowed, unzipped == 0")
            print(f"{unzipped}")

    def rename(self):
        text, ok = QInputDialog.getText(self.ui.window, 'Renaming dataPoint', 'Enter new dataPoint name:')
        names = self.parent().container
        if ok:
            if text in names:
                print("Name already taken")
                return

            names.pop(self.name, None)

            self.name = str(text)
            names[self.name] = self
            self.setText(self.name)

    def remove(self):
        self.parent().container.pop(self.name, None)
        self.parent().removeRow(self.index().row())


    def showMenu(self, position):
        menu = QMenu()
        menu.addAction("Rename", self.rename)
        menu.addSeparator()
        menu.addAction("Remove", self.remove)
        menu.addSeparator()
        menu.addAction("Save to file", self.save_to_file)
        # menu.addAction("Save", self.save_to_json)
        



        menu.exec_(self.ui.window.mapToGlobal(position))

    def save_to_file(self):
        compound = self.parent().parent()
        name = QtWidgets.QFileDialog.getSaveFileName(self.ui.window, 'Save file')
        try:
            with  open(name[0] + '.csv', 'w') as f:
                self.result().to_csv(f.name, index=False, sep=AppState.separator)
        except Exception as e:
            print(e)
            return

    def result(self):
        df_param = pd.DataFrame(columns=['Name', 'Value','Error'])
        i = 0
        for p in self.current:
            row = {'Name': p, 'Value':self.current[p], 'Error':self.error[i]}
            i += 1
            df_param = df_param.append(row, ignore_index=True)

        a = pd.DataFrame(pd.Series(self.temp)).rename(columns={0:'T'})
        b = pd.DataFrame(pd.Series(self.field)).rename(columns={0:'H'})
        c = pd.DataFrame(pd.Series(self.tau)).rename(columns={0:'Tau'})
        df_experimental = pd.concat([a,b,c], axis=1)

        x = np.linspace(self.temp.min(),self.temp.max(), 50)
        y = np.linspace(self.field.min(),self.field.max(), 50)
        X, Y = np.meshgrid(x,y)

        a = list(self.current.values())
        Z = 1/model(X,Y,*a)

        temp = []
        for x in X:
            for t in x:
                temp.append(t)

        field = []
        for y in Y:
            for h in y:
                field.append(h)

        tau = []
        for z in Z:
            for v in z:
                tau.append(v)

        a=pd.DataFrame(temp).rename(columns={0:'TempModel'})
        b=pd.DataFrame(field).rename(columns={0:'FieldModel'})
        c=pd.DataFrame(tau).rename(columns={0:'TauModel'})
        df_model = pd.concat([a,b,c], axis=1)

        df_model_2 = self.partial_result(x,y)

        
        all_temp = set()
        for p in self.points:
            all_temp.add(p[1])
        print('Set of tmp: ', all_temp)

        final_series_tmp = [pd.Series()]*7
        for t in list(all_temp):
            field = np.linspace(self.field.min(), self.field.max(), 50)
            field = pd.Series(field)
            tmp = pd.Series([t] * 50)
            partial_result = self.partial_result(tmp, field , return_df=False)
            one_point_series = [tmp, field] + partial_result
            for s in range(len(final_series_tmp)):
               final_series_tmp[s] = final_series_tmp[s].append(one_point_series[s], ignore_index=True)
        
        t = pd.DataFrame(final_series_tmp[0]).rename(columns={0:'Temp'})
        f = pd.DataFrame(final_series_tmp[1]).rename(columns={0:'Field'})
        a = pd.DataFrame(final_series_tmp[2]).rename(columns={0:'Orbach'})
        b = pd.DataFrame(final_series_tmp[3]).rename(columns={0:'Raman'})
        c = pd.DataFrame(final_series_tmp[4]).rename(columns={0:'QTM'})
        d = pd.DataFrame(final_series_tmp[5]).rename(columns={0:'Direct'})
        e = pd.DataFrame(final_series_tmp[6]).rename(columns={0:'Tau'})

        df_tmp = pd.concat([t,f,a,b,c,d,e], axis=1)

        final_series_field = [pd.Series()]*7
        all_field = set()
        for p in self.points:
            all_field.add(p[2])

        for f in list(all_field):
            tmp = np.linspace(self.temp.min(), self.temp.max(), 50)
            tmp = pd.Series(tmp)
            field = pd.Series([f]*50)
            partial_result = self.partial_result(tmp, field, return_df=False)
            one_point_series = [tmp, field] + partial_result
            for s in range(len(final_series_field)):
                final_series_field[s] = final_series_field[s].append(one_point_series[s], ignore_index=True)

        t = pd.DataFrame(final_series_field[0]).rename(columns={0:'Temp'})
        f = pd.DataFrame(final_series_field[1]).rename(columns={0:'Field'})
        a = pd.DataFrame(final_series_field[2]).rename(columns={0:'Orbach'})
        b = pd.DataFrame(final_series_field[3]).rename(columns={0:'Raman'})
        c = pd.DataFrame(final_series_field[4]).rename(columns={0:'QTM'})
        d = pd.DataFrame(final_series_field[5]).rename(columns={0:'Direct'})
        e = pd.DataFrame(final_series_field[6]).rename(columns={0:'Tau'})
        
        df_field = pd.concat([f,t,a,b,c,d,e], axis=1)

        return pd.concat([df_param, df_experimental, df_model, df_model_2, df_tmp, df_field], axis=1)


    def partial_result(self, temp, field, return_df = True):
        orbach= 1/Orbach(temp, field, self.previous['Tau0'], self.previous['DeltaE'] )
        raman = 1/Raman(temp, field, self.previous['CRaman'], self.previous['NRaman'])
        qtm = 1/QTM(temp, field, self.previous['B1'], self.previous['B2'], self.previous['B3'])
        direct = 1/Direct(temp, field, self.previous['Adir'], self.previous['Ndir'])
        sum = 1/model(temp, field, **self.previous)

        if return_df:
            a = pd.DataFrame(orbach).rename(columns={0:'Orbach Tau'})
            b = pd.DataFrame(raman).rename(columns={0:'Raman Tau'})
            c = pd.DataFrame(qtm).rename(columns={0:'QTM Tau'})
            d = pd.DataFrame(direct).rename(columns={0:'Direct Tau'})
            e = pd.DataFrame(sum).rename(columns={0:'Tau'})
            return pd.concat([a,b,c,d,e], axis=1)
        else:
            return [orbach, raman, qtm, direct, sum]

    def double_click(self):
        self.change()

    def click(self):
        self.change()


class FitTauCollectionItem(StandardItem):
    def __init__(self, mainPage, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__(txt, font_size, set_bold, color)
        self.markColor = QColor(46,184,199)
        #self.setBackground(markColor)
        self.ui = mainPage
        self.container = {}


    def showMenu(self, position):
        menu = QMenu()
        menu.addAction("Save all to file", self.save_to_file)
        # menu.addSeparator()
        # menu.addAction("Load from save", self.load_from_json)
        menu.exec_(self.ui.window.mapToGlobal(position))

    def load_from_json(self):
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.ExistingFile) #TMP

        if dlg.exec_():
           filenames = dlg.selectedFiles()
        else:
           return

        if len(filenames) != 1 :
            return 

        filepath = filenames[0]  #TMP "C:/Users/wikto/Desktop/ACMA/ac_0_Oe.dat"  #
        if not os.path.isfile(filepath):
            print("File path {} does not exist. Exiting...".format(filepath))
            return

        with open(filepath, "r") as f:
            jsonable = json.load(f)

        tau_item = self.from_json(jsonable)

        tau_item.change()

    def create_from_json(self, jsonable):
        tau_item = FitTauItem(self.ui, self.parent())
        tau_item.from_json(jsonable)
        i = 2
        if tau_item.name in self.container:
            saved_name = tau_item.name
            tau_item.name = saved_name + f"_{i}"
        while(tau_item.name in self.container):
            i += 1
            tau_item.name = saved_name + f"_{i}"

        tau_item.setText(tau_item.name)
        return tau_item

    def get_jsonable(self):
        items_list = []
        i = 0
        while(self.child(i) != None):
            items_list.append(self.child(i).get_jsonable())
            i += 1
        jsonable = {'items_list':items_list}
        return jsonable

    def save_to_json(self):
        jsonable = self.get_jsonable()
        name = QtWidgets.QFileDialog.getSaveFileName(self.ui.window, 'Save file')

        if name == "":
            return

        with  open(name[0] + '.json' if len(name[0].split('.')) == 1 else name[0][:-5] + '.json', 'w') as f:
            json.dump(jsonable, f, indent=4)

    def from_json(self, json):
        for item in json['items_list']:
            tau_item = self.create_from_json(item)
            self.append(tau_item)

        
    def save_to_file(self):
        compound = self.parent().parent()
        df = pd.DataFrame()
        i = 0
        while(self.child(i) != None):
            df = pd.concat([df, self.child(i).result()], axis=1)
            i += 1
        name = QtWidgets.QFileDialog.getSaveFileName(self.ui.window, 'Save file')
        try:
            with  open(name[0] + '.csv', 'w') as f:
                df.to_csv(f.name, index=False, sep= AppState.separator)
        except Exception as e:
            print(e)
            return

    def make_new_fit(self, nr_of_relax=1):
        
        f_items = self.parent().child(nr_of_relax)
        
       
        for r in range(nr_of_relax):
            i = 0
            points = []
            while(f_items.child(i) != None):
                f_item = f_items.child(i) #frequency_item
                if f_item.checkState() == Qt.Checked:
                    params = f_item.relaxations[r].previous
                    tau = np.power(10, params['tau'])
                    temp = round((f_item.df["Temperature"].max() + f_item.df["Temperature"].min())/2, 1)
                    field = round((f_item.df["MagneticField"].max() + f_item.df["MagneticField"].min())/2, 0)
                    point = (tau,temp,field)
                    points.append(point)

                i += 1

            if len(points) == 0:
                return
            name, ok = QInputDialog.getText(self.ui.window, 'Creating tau fit', 'Enter name of fit:')
            if ok:
                if r == 0:
                    tau_item = FitTauItem(self.ui, self.parent(), txt= name +'_relax_1')
                else:
                    tau_item = FitTauItem(self.ui, self.parent(), txt= name+ '_relax_2')

                tau_item.points = points
                tau_item.regenerate_points()

                if self.append(tau_item) == True:
                    self.append(tau_item)
                tau_item.change()

            self.ui.WorkingSpace.setCurrentWidget(self.ui.fit3Dpage)

    # def show(self):
    #     self.ui.WorkingSpace.setCurrentWidget(self.ui.fit3Dpage)

    #     self.ui.plot3d.change(self)


    def append(self, item):
        if item.name in self.container:
            print("TauFiTItem already exists choose other name or delete old one!")
            return False #To DO throw exception

        self.appendRow(item)
        self.container[item.name] = item
    



