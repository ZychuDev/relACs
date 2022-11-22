from PyQt6.QtCore import QObject, pyqtSlot, QLocale
from PyQt6.QtWidgets import QInputDialog, QMessageBox, QWidget
from models import CompoundItemsCollectionModel

class CompoundItemsCollectionController(QObject):
    def __init__(self, model:CompoundItemsCollectionModel):
        super().__init__()
        self._model: CompoundItemsCollectionModel = model

    @pyqtSlot()
    def add_compound(self):

        name, ok = QInputDialog.getText(QWidget(), 'Creating new compund', 'Enter name of compound:')

        if len(name) == 0:
            msg: QMessageBox = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Compound's name must consist of at least one character !")
            msg.setWindowTitle("Compound creation cancelation")
            msg.exec()
            return
        if ok:
            if self._model.check_name(name):
                msg: QMessageBox = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setText(f'Compound "{name}" already exists. Choose different name or delete old compound!')
                msg.setWindowTitle("Compound creation cancelation")
                msg.exec()

                return
            dialog: QInputDialog = QInputDialog()
            dialog.setInputMode(QInputDialog.InputMode.DoubleInput)
            dialog.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
            dialog.setLabelText('Enter molar mass in g/mol:')
            dialog.setDoubleMinimum(0.0)
            dialog.setDoubleMaximum(1000000.0)
            dialog.setDoubleDecimals(6)
            dialog.setWindowTitle('Compound Creation')
            status: bool = dialog.exec()

            if status:
                molar_mass: float = dialog.doubleValue()
                self._model.append_new_compound(name, molar_mass)
