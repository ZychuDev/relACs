from PyQt6.QtCore import pyqtSlot, QPoint, QLocale, QSize, Qt
from PyQt6.QtGui import QColor, QBrush, QDoubleValidator
from PyQt6.QtWidgets import QMenu, QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QPushButton, QMessageBox

from models import Parameter

from models import (
    Compound, Fit, Relaxation, TauFit, MeasurementItemsCollectionModel,
    FitItemsCollectionModel, TauFitItemsCollectionModel)
from controllers import (
    CompoundItemController, MeasurementItemsCollectionController,
    FitItemsCollectionController, TauFitItemsCollectionController)

from .StandardItem import StandardItem
from .MeasurementItemsCollection import MeasurementItemsCollection
from .FitItemsCollection import FitItemsCollection
from .TauFitItemsCollection import TauFitItemsCollection

class CompoundItem(StandardItem):
    def __init__(self, model: Compound, ctrl: CompoundItemController):
        super().__init__(model._name, 14, False)
        self.setBackground(QBrush(QColor(255,255,255)))
        self.setCheckable(False)

        self._model: Compound = model
        self._ctrl: CompoundItemController = ctrl
        self.m_model = MeasurementItemsCollectionModel("Measurements", self._model)
        self.appendRow(MeasurementItemsCollection(self.m_model, MeasurementItemsCollectionController(self.m_model)))
        self.f1_model = FitItemsCollectionModel("Frequency Fits Single Relaxation", self._model)
        self.appendRow(FitItemsCollection(self.f1_model, FitItemsCollectionController(self.f1_model)))
        self.f2_model = FitItemsCollectionModel("Frequency Fits Double Relaxation", self._model)
        self.appendRow(FitItemsCollection(self.f2_model, FitItemsCollectionController(self.f2_model)))
        self.t_model = TauFitItemsCollectionModel("TauFits(3D)", self._model)
        self.appendRow(TauFitItemsCollection(self.t_model, TauFitItemsCollectionController(self.t_model)))
        self._model.name_changed.connect(self.on_name_changed)

        # self._model.change_ranges.connect(self.change_ranges)
        
    def on_name_changed(self, new_name:str):
        self.setText(new_name)

    def show_menu(self, menu_position: QPoint):
        menu = QMenu()
        menu.addAction("Rename", self._ctrl.rename)
        menu.addAction("Delete", lambda :  self._model._collection.remove(self._model.name, self.index()) if self._model._collection is not None else print("Item is not in collection") )
        menu.exec(menu_position)

    # def change_ranges(self):
    #     dlg:QDialog = QDialog()
    #     default_locale: QLocale = QLocale(QLocale.Language.English, QLocale.Country.UnitedStates)
    #     dlg.setLocale(default_locale)
    #     dlg.setWindowTitle("Set parameters ranges")
    #     layout: QVBoxLayout = QVBoxLayout()
    #     new_ranges: dict[str,tuple[QLineEdit, QLineEdit]] = {}
    #     p: str
    #     for p in self._model.get_parameters():
    #         l: QHBoxLayout = QHBoxLayout()

    #         v: QDoubleValidator = QDoubleValidator()
    #         loc: QLocale = QLocale(QLocale.c())
    #         loc.setNumberOptions(QLocale.NumberOption.RejectGroupSeparator)
    #         v.setLocale(loc)

    #         low: QLineEdit = QLineEdit()
    #         low.setLocale(default_locale)
    #         low.setValidator(v)
    #         low.setText(str(self._model.get_min(p)))

    #         up: QLineEdit = QLineEdit()
    #         up.setLocale(default_locale)
    #         up.setValidator(v)
    #         up.setText(str(self._model.get_max(p)))

    #         label:QLabel = QLabel(Parameter.name_to_symbol[p])
    #         label.setMinimumSize(QSize(65, 0))
    #         label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
    #         new_ranges[p] = (low, up)
    #         l.addWidget(low)
    #         l.addWidget(label)
    #         l.addWidget(up)

    #         layout.addLayout(l)

    #     buttons_layout: QHBoxLayout = QHBoxLayout()
    #     button: QPushButton = QPushButton("Apply")
    #     button.clicked.connect(lambda: self.set_new_ranges(new_ranges, False, dlg))

    #     force_button: QPushButton() = QPushButton("Force change")
    #     force_button.clicked.connect(lambda: self.set_new_ranges(new_ranges, True, dlg))

    #     buttons_layout.addWidget(button)
    #     buttons_layout.addWidget(force_button)
    #     layout.addLayout(buttons_layout)

    #     guess_button = QPushButton("Guess the magnetic susceptibility parameters")
    #     guess_button.clicked.connect(lambda: self.guess(new_ranges))
    #     layout.addWidget(guess_button)
    #     dlg.setLayout(layout)
    #     dlg.exec()
        
    # def guess(self, ranges: dict[str,tuple[QLineEdit, QLineEdit]]):
    #     max_chi_prime: float = -1e16
    #     max_chi_bis: float = -1e16
    #     for f in self.f1_model._fits:
    #         max_chi_prime = max(f._df["ChiPrimeMol"].max(), max_chi_prime)
    #         max_chi_bis = max(f._df["ChiBisMol"].max(), max_chi_bis)

    #     for f in self.f2_model._fits:
    #         max_chi_prime = max(f._df["ChiPrimeMol"].max(), max_chi_prime)
    #         max_chi_bis = max(f._df["ChiBisMol"].max(), max_chi_bis)

    #     ranges["chi_dif"][0].setText("0.0")
    #     ranges["chi_dif"][1].setText(f"{5.0*max_chi_bis}")
    #     ranges["chi_s"][0].setText("0.0")
    #     ranges["chi_s"][1].setText(f"{max_chi_prime}")


    # def set_new_ranges(self, edit_lines: dict[str,tuple[QLineEdit, QLineEdit]], force: bool, dlg:QDialog):
    #     pa: str
    #     message: str
    #     msg: QMessageBox
    #     for pa in edit_lines:
    #         if float(edit_lines[pa][0].text()) >=  float(edit_lines[pa][1].text()):
    #             message = f"Each upper bound must be strictly greater than lower bound\n Bounds for parameter: {p} are invalid"
    #             msg = QMessageBox()
    #             msg.setIcon(QMessageBox.Icon.Warning)
    #             msg.setText(message)
    #             msg.setWindowTitle("Incorrect bounds")
    #             msg.exec()
    #             return

    #     f: Fit
    #     r: Relaxation
    #     p: Parameter
    #     pp: Parameter
    #     t_f: TauFit

    #     lower: float
    #     upper: float
    #     value: float

    #     if not force:
    #         for f in self.f1_model._fits:
    #             for r in f.relaxations:
    #                 for p in r.saved_parameters:
    #                     lower = float(edit_lines[p.name][0].text())
    #                     upper = float(edit_lines[p.name][1].text())
    #                     value = p.get_value()
    #                     if value < lower or value > upper:
    #                         message = (f"Bounds for parameter: {p.name} are invalid\n"
    #                         +f"In {f.name} saved value of paramater is not in given range\n"
    #                         +f"Lower : {lower}\nUpper: {upper}\nActual: {value}\n" 
    #                         +"Force new ranges or change saved values of the parameters")
    #                         msg = QMessageBox()
    #                         msg.setIcon(QMessageBox.Icon.Warning)
    #                         msg.setText(message)
    #                         msg.setWindowTitle("Incorrect bounds")
    #                         msg.exec()
    #                         return

    #         for f in self.f2_model._fits:
    #             for r in f.relaxations:
    #                 for p in r.saved_parameters:
    #                     lower = float(edit_lines[p.name][0].text())
    #                     upper = float(edit_lines[p.name][1].text())
    #                     value = p.get_value()
    #                     if value < lower or value > upper:
    #                         message = (f"Bounds for parameter: {p.name} are invalid\n"
    #                         +f"In {f.name} saved value of paramater is not in given range\n"
    #                         +f"Lower : {lower}\nUpper: {upper}\nActual: {value}\n" 
    #                         +"Force new ranges or change saved values of the parameters")
    #                         msg = QMessageBox()
    #                         msg.setIcon(QMessageBox.Icon.Warning)
    #                         msg.setText(message)
    #                         msg.setWindowTitle("Incorrect bounds")
    #                         msg.exec()
    #                         return

    #         for t_f in self.t_model._tau_fits:
    #             for p in t_f.saved_parameters:
    #                 lower = float(edit_lines[p.name][0].text())
    #                 upper = float(edit_lines[p.name][1].text())
    #                 value = p.get_value()
    #                 if value < lower or value > upper:
    #                     message = (f"Bounds for parameter: {p.name} are invalid\n"
    #                     +f"In {t_f.name} saved value of paramater is not in given range\n"
    #                     +f"Lower : {lower}\nUpper: {upper}\nActual: {value}\n" 
    #                     +"Force new ranges or change saved values of the parameters")

    #                     msg = QMessageBox()
    #                     msg.setIcon(QMessageBox.Icon.Warning)
    #                     msg.setText(message)
    #                     msg.setWindowTitle("Incorrect bounds")
    #                     msg.exec()
    #                     return
        
    #     for i in range(len(self.f1_model._fits)):
    #         f = self.f1_model._fits[i]
    #         for j in range(len(f.relaxations)):
    #             r = f.relaxations[j]
    #             for k in range(len(r.saved_parameters)):
    #                 p = r.saved_parameters[k]
    #                 lower = float(edit_lines[p.name][0].text())
    #                 upper = float(edit_lines[p.name][1].text())
    #                 self._model.change_range(p.name, lower, upper)
    #                 value = p.get_value()
    #                 error = p.error
    #                 p.set_range(lower, upper)
    #                 if value < lower:
    #                     value = lower
    #                 if value > upper:
    #                     value = upper
    #                 p.set_value(value, new_error=error)
    #                 r.residual_error = 0.0
    #                 for m in range(len(r.parameters)):
    #                     pp = r.parameters[m]
    #                     if pp.name == p.name:
    #                         pp.set_range(lower, upper)
    #                         pp.set_value(value)
                    
                    

    #     for i in range(len(self.f2_model._fits)):
    #         f = self.f2_model._fits[i]
    #         for j in range(len(f.relaxations)):
    #             r = f.relaxations[j]
    #             for k in range(len(r.saved_parameters)):
    #                 p = r.saved_parameters[k]
    #                 lower = float(edit_lines[p.name][0].text())
    #                 upper = float(edit_lines[p.name][1].text())
    #                 self._model.change_range(p.name, lower, upper)
    #                 value = p.get_value()
    #                 error = p.error
    #                 p.set_range(lower, upper)
    #                 if value < lower:
    #                     value = lower
    #                 if value > upper:
    #                     value = upper
    #                 p.set_value(value, new_error=error)
    #                 r.residual_error = 0.0
    #                 for m in range(len(r.parameters)):
    #                     pp = r.parameters[m]
    #                     if pp.name == p.name:
    #                         pp.set_range(lower, upper)
    #                         pp.set_value(value)
                    

    #     for i in range(len(self.t_model._tau_fits)):
    #         t_f = self.t_model._tau_fits[i]
    #         for j in range(len(t_f.saved_parameters)):
    #             p = t_f.saved_parameters[j]
    #             lower = float(edit_lines[p.name][0].text())
    #             upper = float(edit_lines[p.name][1].text())
    #             self._model.change_range(p.name, lower, upper)
    #             value = p.get_value()
    #             error = p.error
    #             p.set_range(lower, upper)
    #             if value < lower:
    #                 value = lower
    #             if value > upper:
    #                 value = upper
    #             p.set_value(value, new_error=error)
    #             r.residual_error = 0.0
    #             for k in range(len(t_f.parameters)):
    #                 pp = t_f.parameters[k]
    #                 if pp.name == p.name:
    #                     pp.set_range(lower, upper)
    #                     pp.set_value(value)

    #     dlg.close()


        

