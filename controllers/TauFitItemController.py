from PyQt6.QtCore import QObject, pyqtSlot
from PyQt6.QtWidgets import QInputDialog, QMessageBox, QWidget
from models import TauFit

class TauFitItemController(QObject):
    def __init__(self, model:TauFit):
        self._model = model
    
    def rename(self):
        new_name, ok = QInputDialog.getText(QWidget(), 'Renaming Tau Fit', 'Enter new name of the Tau Fit:')
        if ok:
            msg: QMessageBox = QMessageBox()
            if len(new_name) == 0:
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setText("Tau Fits's name must consist of at least one character!")
                msg.setWindowTitle("Tau Fit renaming cancelation")
                msg.exec()
                return
            if self._model._collection.check_name(new_name):
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setText(f'Tau Fit "{new_name}" already exists. Choose different name or delete old Tau Fit!')
                msg.setWindowTitle("Tau Fit renaming cancelation")
                msg.exec()
                return

            self._model.name = new_name