from PyQt6.QtCore import QObject, pyqtSlot
from PyQt6.QtWidgets import QFileDialog, QWidget
from models import TauFitItemsCollectionModel
from pandas import concat, DataFrame #type: ignore

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
            with  open(name[0] + '.csv', 'w') as f:
                df.to_csv(f.name, index=False, sep= ";")
        except Exception as e:
            print(e)
            return