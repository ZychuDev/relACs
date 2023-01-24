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
    def load_dielectric_measurements_from_folder(self):
        """Load data from dielectric spectometer to relACs program.
        """
        dlg: QFileDialog = QFileDialog()
        dlg.setFileMode(QFileDialog.FileMode.Directory)
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
        directory:str = filenames[0]  #TMP "C:/Users/wikto/Desktop/ACMA/ac_0_Oe.dat"  #
        
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if not os.path.isfile(filepath):
                continue
            if filepath.split(".")[-1] != "txt":
                continue

            csv_filepath: str
            try:
                csv_filepath = self.dielectric_dat_to_csv(filepath)
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
                data: DataFrame = read_csv(csv_filepath, header=0)
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
            
            probe_mass: float = 1.0
            molar_mass: float = 1.0

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

    @pyqtSlot()
    def load_measurements_from_file(self):
        """Load data from magnetometr to relACs program.
        """
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

    def dielectric_dat_to_csv(self, filepath: str):
        """Create new file in in .csv format from .dat source file.

        Args:
            filepath (str): System path to source file.

        Raises:
            ValueError: Raise when filepath is incorrect.

        Returns:
            str: Filepath to created .csv file.
        """
        if not os.path.isfile(filepath):
            raise ValueError 

        with open(filepath, "r") as f:
            lines: list[str] = f.readlines()

            if filepath.find('.'):
                filepath = filepath[:filepath.rfind('.')]
            new_filepath = filepath + ".csv"

            with open(new_filepath, "w+") as f:
                temp:str 
                for i, line in enumerate(lines):
                    if i == 0:
                        continue
                    if i == 1:
                        try:
                            temp = line.split("[K] = ")[1].split(",")[0]
                        except Exception as e:
                            temp = line.split("[°C]=")[1].split(" ")[0]
                            temp = float(temp) - 273.15
                    if i == 2:
                        rows = line.split()
                        rows[0] = "AC Frequency (Hz),"
                        rows[2] = "AC X' (emu/Oe),"
                        rows[3] = "AC X'' (emu/Oe),"
                        f.write(rows[0] + rows[2] + rows[3] + "Temperature (K),Magnetic Field (Oe)\n")
                    if i > 2:
                        rows = line.split()
                        f.write(f"{rows[0]},{rows[1]},{rows[2]},{temp},{0.0}\n")

        return new_filepath

    def dat_to_csv(self, filepath:str) -> str:
        """Create new file in in .csv format from .dat source file.

        Args:
            filepath (str): System path to source file.

        Raises:
            ValueError: Raise when filepath is incorrect.

        Returns:
            str: Filepath to created .csv file.
        """
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
        """Perform clusterization of measurement data from magnetometr.

        Args:
            data (DataFrame): Measurement data from magnetometr
            by (Literal[&quot;MagneticField&quot;, &quot;Temperature&quot;]): Main dimention of clusterization.
            epsilon (float): If space between two subsequent measurement points is bigger than epsilon, all new points from this point onward will we added to next cluster. 
            reindex (bool, optional): Whether to reset index for DataFrames in result. Defaults to False.

        Returns:
            list[DataFrame]: List of DataFrames that each represent one cluster.
        """
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