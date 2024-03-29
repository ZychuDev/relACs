from PyQt6.QtCore import QObject, pyqtSlot
from PyQt6.QtWidgets import QInputDialog, QMessageBox, QWidget
from models import Measurement

class MeasurementItemController(QObject):
    def __init__(self, model:Measurement):
        self._model: Measurement = model
        
    @pyqtSlot()
    def rename(self):
        """Change model name."""
        new_name, ok = QInputDialog.getText(QWidget(), 'Renaming compund', 'Enter new name of the compound:')
        if ok:
            msg: QMessageBox = QMessageBox()
            if len(new_name) == 0:
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setText("Compound's name must consist of at least one character !")
                msg.setWindowTitle("Compound renaming cancelation")
                msg.exec()
                return
            if self._model._collection.check_name(new_name):
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setText(f'Compound "{new_name}" already exists. Choose different name or delete old compound!')
                msg.setWindowTitle("Compound renaming cancelation")
                msg.exec()
                return

            self._model.set_name(new_name)