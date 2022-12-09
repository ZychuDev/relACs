from PyQt6.QtCore import QObject, pyqtSlot, QLocale
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QInputDialog

from typing import Literal

from models import MeasurementItemsCollectionModel, Measurement
from readers import SettingsReader

from pandas import DataFrame, Series, read_csv # type: ignore
from numpy import pi, log10
import os 

class MeasurementItemsCollectionController(QObject):
    def __init__(self, model:MeasurementItemsCollectionModel):
        super().__init__()
        self._model: MeasurementItemsCollectionModel = model

    @pyqtSlot()
    def load_measurements_from_file(self):
        dlg: QFileDialog = QFileDialog()
        dlg.setFileMode(QFileDialog.FileMode.ExistingFile)

        if dlg.exec():
            filenames: list[str] = dlg.selectedFiles()
        else:
            return

        if len(filenames) != 1:
            return

        settings: SettingsReader = SettingsReader()
        internal_to_external: dict[str, str] = settings.get_headings_maping()
        field_epsilon: float
        tmp_epsilon: float
        field_epsilon, tmp_epsilon = settings.get_epsilons()
        filepath:str = filenames[0]  #TMP "C:/Users/wikto/Desktop/ACMA/ac_0_Oe.dat"  #
        
        csv_filepath: str
        try:
            csv_filepath = self.dat_to_csv(filepath)
        except ValueError:
            msg: QMessageBox = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText(
            "Error when converting file from .dat  to .csv fromat.\n"
            + f"Loading measurements form file {filepath} skipped.")
            msg.setWindowTitle("Wrong file format")
            msg.exec()
            return
        try:
            data: DataFrame = read_csv(csv_filepath, header=1)
            data = data.sort_values(internal_to_external['Temperature'])

            external_to_internal: dict[str, str] = {value:key for key, value in internal_to_external.items()}
            data = data.rename(columns=external_to_internal)
            data = data[Measurement.columns_headers]
        except:
            msg: QMessageBox = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText(
            "Headers in file does not match with ones setted in Default Settings.\n"
            + "Navigate to Settings -> Default Settings and make adjustment or edit headers in source file.\n"
            + f"Loading measurements form file {filepath} skipped.")
            msg.setWindowTitle("Wrong headers")
            msg.exec()
            return
        
        dialog:QInputDialog = QInputDialog()
        dialog.setInputMode(QInputDialog.InputMode.DoubleInput)
        dialog.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        dialog.setLabelText('Enter sample mass in grams:')
        dialog.setDoubleMinimum(0.0)
        dialog.setDoubleMaximum(1000000.0)
        dialog.setDoubleDecimals(8)
        dialog.setWindowTitle('Loading data')
        status: bool = dialog.exec()
        if not status:
            return

        probe_mass: float = dialog.doubleValue()
        molar_mass: float = self._model._compound.molar_mass

        data["ChiPrimeMol"] = data["ChiPrime"] * molar_mass/probe_mass
        data["ChiBisMol"] = data["ChiBis"] * molar_mass/probe_mass
        data["Omega"] = 2 * data["Frequency"] * pi
        data["OmegaLog"] = log10(data["Omega"])
        data["FrequencyLog"] = log10(data["Frequency"])

        data = data.sort_values("Temperature")
        fields: list[DataFrame] = self.cluster(data, "MagneticField", field_epsilon)
        i: int
        for i in list(range(0, len(fields))):
            fields[i] = self.cluster(fields[i], "Temperature", tmp_epsilon)

        filename: str = filepath.split('/')[-1][:-4]
        x: DataFrame
        first: bool = True
        for x in fields:
            for y in x:
                if first:
                    self._model.append_measurement(Measurement.from_data_frame(y, filename, self._model._compound, self._model), display=True)
                    first = False
                else:
                    self._model.append_measurement(Measurement.from_data_frame(y, filename, self._model._compound, self._model))
        self._model._compound._tree.resizeColumnToContents(0)

    def dat_to_csv(self, filepath:str) -> str:
        if not os.path.isfile(filepath):
            raise ValueError 

        with open(filepath, "r") as f:
            lines: list[str] = f.readlines()

            if filepath.find('.'):
                filepath = filepath[:filepath.rfind('.')]
            new_filepath = filepath + ".csv"

            with open(new_filepath, "w+") as f:
                header: bool = True
                for line in lines:
                    if line.strip("\n") == "[Data]":
                        header = False
                    if not header:
                        f.write(line + "\n")

        return new_filepath

    def cluster(self, data: DataFrame, by:Literal["MagneticField", "Temperature"], epsilon:float, reindex: bool=False) -> list[DataFrame]:
        sorted_data: DataFrame = data.sort_values(by=by).copy()
        min_value: float = sorted_data[by].min()

        results: list[DataFrame] = []
        df: DataFrame = DataFrame(columns=data.columns)

        row: Series
        for _, row in sorted_data.iterrows():
            if row[by] <= min_value + epsilon:
                df.loc[-1] = row
                df.index = df.index + 1
            else:
                results.append(df)
                df = DataFrame(columns=data.columns)
                min_value = row[by]
                df.loc[-1] = row
                df.index = df.index +1
        
        results.append(df)

        if reindex:
            i:int
            for i in range(0, len(results)):
                results[i] = results[i].sort_values(by, ascending=False).reset_index(drop=True)

        # i: int
        for i in range(0, len(results)):
                results[i] = results[i].sort_values("Omega")
    
        return results

    def get_next(self, name: str):
        pass

    def get_previous(self, name: str):
        pass

    def get_item_model(self, name: str):
        pass

    def get_names(self) -> list[str]: 
        pass