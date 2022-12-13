from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox, QFileDialog, QWidget

from .Relaxation import Relaxation
from models import Measurement 
from .Parameter import Parameter

from protocols import Collection, SettingsSource

from pandas import DataFrame, Series, concat # type: ignore
from numpy import ndarray, pi, power, finfo, diag, sum, sqrt, pi, power, logspace
from numpy import max as np_max
from scipy.optimize import least_squares # type: ignore
from scipy.linalg import svd #type: ignore
from math import nextafter

from typing import Self 

class Fit(QObject):
    name_changed = pyqtSignal(str)
    df_changed= pyqtSignal()
    df_point_deleted = pyqtSignal()
    parameter_changed = pyqtSignal()
    fit_changed = pyqtSignal()

    @staticmethod
    def model(logFrequency: ndarray, alpha: float, beta: float, tau: float, chi_t: float, chi_s: float) -> ndarray:
        return chi_s + (chi_t - chi_s)/((1 + (10**logFrequency*2*pi * power(10, tau) * 1j )**(1- alpha))**beta)

    @staticmethod
    def from_measurement(measurement: Measurement, compound:SettingsSource, nr_of_relaxations: int = 1):
        fit_name: str = measurement._name + "_Fit_Frequency"
        fit: Fit =  Fit(fit_name, measurement._df.copy(), measurement._tmp, measurement._field, compound, None)

        fit.relaxations = []
        i: int
        for i in range(nr_of_relaxations):
            fit.relaxations.append(Relaxation(compound))

        return fit
    def __init__(self, name: str, df: DataFrame, temp: float, field: float, compound:SettingsSource, collection: Collection|None):
        super().__init__()
        self._name: str = name
        self._df: DataFrame = df

        self._tmp: float = temp
        self._field: float = field

        self.relaxations: list[Relaxation]

        self._compound: SettingsSource = compound
        self._collection: Collection
        if collection is not None:
            self._collection = collection

        self.resolution = 50 # TO::DO 

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val:str):
        if len(val) < 1:
            raise ValueError("Compund name must be at least one character long")
        self._collection.update_names(self._name, val)
        self._name = val
        self.name_changed.emit(val)

    @property
    def molar_mass(self):
        return self._molar_mass

    @molar_mass.setter
    def molar_mass(self, val:float):
        if val <= 0:
            raise ValueError("Molar mass must be greater than 0")

        self._molar_mass = val

    def hide_point(self, x: float, x_str: str):
        actual: bool = bool(self._df.loc[self._df[x_str] == x]['Hidden'].values[0])
        self._df.loc[self._df[x_str] == x, "Hidden"] = not actual
        self.df_changed.emit()
        # self.dataChanged.emit() #type: ignore

    def delete_point(self, x: float, x_str: str):
        if self._df.shape[0] == 2:
            msg: QMessageBox = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Measurement must consist of at least 2 data points")
            msg.setWindowTitle("Data point removal error")
            msg.exec()
            return

        self._df.drop(self._df.loc[self._df[x_str] == x].index, inplace=True)
        self.df_point_deleted.emit()



    def cost_function(self, p):
        rest = self._df.loc[self._df["Hidden"] == False]

        sum_real = 0
        sum_img = 0
        i = 0
        while i < len(self.relaxations):
            r = Fit.model(rest["FrequencyLog"].values, p[0+i*5], p[1+i*5], p[2+i*5], p[3+i*5], p[4+i*5])
            sum_real += r.real
            sum_img += -r.imag

            i += 1

        dif_real = power(sum_real - rest['ChiPrimeMol'], 2)
        dif_img = power(sum_img - rest['ChiBisMol'], 2)


        return  dif_real + dif_img

    def make_auto_fit(self, auto: bool = False, next_fit: Self = None): # type: ignore
        params: tuple = ()
        min: list = []
        max: list = []
        for r_nr in range(len(self.relaxations)):
            relaxation = self.relaxations[r_nr]
            params = params + relaxation.get_parameters_values()
            min = min + relaxation.get_parameters_min_bounds()
            max = max + relaxation.get_parameters_max_bounds()

        
        r: Relaxation
        i: int
        for i, r in enumerate(self.relaxations):
            for j, p in enumerate(r.parameters):
                if p.is_blocked:
                    min[j + i*len(r.parameters)] = nextafter(p.value, min[j + i*len(r.parameters)])
                    max[j + i*len(r.parameters)] = nextafter(p.value, max[j + i*len(r.parameters)])

        bounds: tuple[list[float], list[float]] = (min, max)
        res = least_squares(self.cost_function, params, bounds=bounds)

        for i, r in enumerate(self.relaxations):
            for j, p in enumerate(r.parameters):
                p.set_value(res.x[j + i*len(r.parameters)])
        
        _, s, Vh = svd(res.jac, full_matrices=False)
        tol = finfo(float).eps * s[0] * np_max(res.jac.shape)
        w = s > tol
        cov = (Vh[w].T/s[w]**2) @ Vh[w] # robust covariance matrix

        chi2dof = sum(res.fun**2)/(res.fun.size - res.x.size)
        cov *= chi2dof

        perr = sqrt(diag(cov))
        for i, r in enumerate(self.relaxations):
            r.set_all_errors(res.cost, perr[i*5 : i*5+5])

        if auto:
            self.save_all_relaxations()
            if next_fit != None: #type: ignore
                self.copy_all_relxations(next_fit)

    def save_to_file(self):
        save_name, _ = QFileDialog.getSaveFileName(QWidget(), 'Save file')
        if save_name is not None:
            try:
                with open(save_name + ".csv", "w") as f:
                    self.get_result().to_csv(f.name, index=False, sep = ";")
            except Exception as e:
                print(e)
                return

    def get_result(self):
        df_param: DataFrame = DataFrame([['T', self._tmp, 0], ['H', self._field, 0]], columns=['Name', 'Value','Error'])
        df_model_final: DataFrame = DataFrame()
        for i, r in enumerate(self.relaxations):
            for p in r.saved_parameters:
                row = { "Name": f"{p.name}{i+1}", "Value": p.value, "Error": p.error}
                df_param = df_param.append(row, ignore_index = True)

            df_experimental: DataFrame = self._df[["Frequency", "ChiPrimeMol","ChiBisMol"]]
            columns_names: list[str] = [f"Frequency T={self._tmp} H={self._field}",
             f"ChiPrimeMol T={self._tmp} H={self._field}", f"ChiBisMol T={self._tmp} H={self._field}"]
            # df_experimental.columns = columns_names
            # df_experimental.reset_index(drop=True, inplace=True)

            df_model: DataFrame = DataFrame(columns = columns_names)
            displayed: DataFrame = self._df.loc[self._df["Hidden"] == False]

            xx = logspace(displayed["FrequencyLog"].min(), displayed["FrequencyLog"].max(), self.resolution)
            df_model[columns_names[0]] = Series(xx)

            yy = Fit.model(xx, *self.relaxations[i].get_saved_parameters_values())
            df_model[columns_names[1]] = Series(yy.real)
            df_model[columns_names[2]] = Series(-yy.imag)

            df_model_final = concat([df_model_final, df_model], axis=1)

        if i != 0:
            columns = list(df_model_final.columns)
            for j in range(0, len(columns), 3):
                rel_str:str = f"rel_nr={j//3 + 1}"
                columns[j] += rel_str
                columns[j+1] += rel_str
                columns[j+2] += rel_str
            df_model_final.columns = columns

        df: DataFrame = concat([df_param, df_experimental, df_model_final], axis=1)
        return df

    def save_all_relaxations(self):
        for r in self.relaxations:
            r.save()

    def copy_all_relxations(self, other: Self): #type: ignore
        for i, r in enumerate(other.relaxations): #type: ignore
                r.copy(self.relaxations[i])