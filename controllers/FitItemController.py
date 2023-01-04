from PyQt6.QtCore import QObject, pyqtSlot
from PyQt6.QtWidgets import QInputDialog, QMessageBox, QWidget
from models import Fit

class FitItemController(QObject):
    def __init__(self, model:Fit):
        self._model: Fit = model

    def rename(self):
        new_name, ok = QInputDialog.getText(QWidget(), 'Renaming fit', 'Enter new name of the fit:')
        if ok:
            msg: QMessageBox = QMessageBox()
            if len(new_name) == 0:
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setText("Fit's name must consist of at least one character!")
                msg.setWindowTitle("Fit renaming cancelation")
                msg.exec()
                return
            if self._model._collection.check_name(new_name):
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setText(f'Fit "{new_name}" already exists. Choose different name or delete old fit!')
                msg.setWindowTitle("Fit renaming cancelation")
                msg.exec()
                return

            self._model.set_name(new_name)
