from PyQt6.QtCore import QObject, pyqtSlot, QLocale
from PyQt6.QtWidgets import QInputDialog, QMessageBox, QFileDialog, QWidget
from models import CompoundItemsCollectionModel
from json import dump, load
from os import path
class CompoundItemsCollectionController(QObject):
    def __init__(self, model:CompoundItemsCollectionModel):
        super().__init__()
        self._model: CompoundItemsCollectionModel = model

    def display(self):
        self._model._displayer.display_home_page()

    @pyqtSlot()
    def add_compound(self):

        name, ok = QInputDialog.getText(QWidget(), 'Creating new compund', 'Enter name of compound:')

        if not ok:
            return

        if len(name) == 0:
            msg: QMessageBox = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Compound's name must consist of at least one character !")
            msg.setWindowTitle("Compound creation cancelation")
            msg.exec()
            return

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

        


