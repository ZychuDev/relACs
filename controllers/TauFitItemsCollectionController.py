from PyQt6.QtCore import QObject, pyqtSlot
from PyQt6.QtWidgets import QFileDialog, QWidget, QMessageBox, QInputDialog
from models import TauFitItemsCollectionModel, TauFit
from pandas import concat, DataFrame #type: ignore
from os import path

class TauFitItemsCollectionController(QObject):
    def __init__(self, model:TauFitItemsCollectionModel):
        super().__init__()
        self._model: TauFitItemsCollectionModel = model

    @pyqtSlot()
    def save_all_to_file(self):
        """Save results from all TauFits in collection to .csv file.
        """
        df = DataFrame()
        for fit in  self._model._tau_fits:
            df = concat([df, fit.get_result()], axis=1)

        name = QFileDialog.getSaveFileName(QWidget(), 'Save file')
        try:
            with  open(name[0] + (".csv" if name[0][-4:] != ".csv" else ""), 'w') as f:
                df.to_csv(f.name, index=False, sep= ";")
        except Exception as e:
            print(e)
            return
        
    @pyqtSlot()
    def load_points(self):
        """Loads taut measurements from dat file
        """

        name, ok = QInputDialog.getText(QWidget(), 'Creating new Tau fit', 'Enter name of Tau fit:')

        if not ok:
            return
        
        if len(name) == 0:
            msg: QMessageBox = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Tau fit's name must consist of at least one character!")
            msg.setWindowTitle("Tau fit creation cancelation")
            msg.exec()
            return
        
        dlg: QFileDialog = QFileDialog()
        dlg.setFileMode(QFileDialog.FileMode.ExistingFile)

        if dlg.exec():
           filenames = dlg.selectedFiles()
        else:
           return

        if len(filenames) != 1 :
            return 
        
        filepath = filenames[0]  
        if not path.isfile(filepath):
            print("File path {} does not exist. Exiting...".format(filepath))
            return
        
        points: list[tuple(float, float, float)] = []
        with open(filepath, "r") as f:
            next(f)  # Skip [Data] tag
            next(f)  # Skip header line: T,H,tau
            for line in f:
                T_str, H_str, tau_str = line.strip().split(",")
                T = float(T_str)
                H = float(H_str)
                tau = float(tau_str)
                points.append((tau, T, H))


        new_fit: TauFit = TauFit(name, self._model._compound, self._model)
        for p in points:
            new_fit.append_point(*p)
        self._model.append_tau_fit(new_fit, display=True)    