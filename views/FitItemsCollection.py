from PyQt6.QtCore import pyqtSlot, QPoint, QModelIndex, Qt, QLocale, QSize
from PyQt6.QtGui import QColor, QBrush, QDoubleValidator
from PyQt6.QtWidgets import QMenu, QFileDialog, QWidget, QInputDialog, QMessageBox,  QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QPushButton, QComboBox

from models import FitItemsCollectionModel, Fit, TauFit
from controllers import FitItemsCollectionController, FitItemController
from .StandardItem import StandardItem
from .FitItem import FitItem

from typing import Literal, cast
from functools import partial

from pandas import DataFrame, concat # type: ignore

class FitItemsCollection(StandardItem):
    def __init__(self, model: FitItemsCollectionModel, ctrl: FitItemsCollectionController):
        super().__init__(model._name, 14, False)
        self.setBackground(QBrush(QColor(255,201,183)))
        self._model: FitItemsCollectionModel = model
        self._ctrl: FitItemsCollectionController = ctrl

        self._model.fit_added.connect(self.on_fit_added)
        self._model.fit_removed.connect(self.on_fit_removed)
        self._model.displayed_item_changed.connect(self.on_displayed_item_changed)

    def show_menu(self, menu_position: QPoint):
        menu = QMenu()

        submenu = menu.addMenu("Sort")
        submenu.addAction("Sort by temperature", partial(self.sort, "temp"))
        submenu.addAction("Sort by field", partial(self.sort, "field"))
        menu.addSeparator()

        menu.addAction("Check all", self.check_all)
        menu.addAction("Uncheck all", self.uncheck_all)
        menu.addSeparator()

        menu.addAction("Make Tau fits from checked data", self.make_tau_fits_checked)
        menu.addSeparator()
        
        menu.addAction("Adjust ranges for all checked", self.adjust_range_selected)
        menu.addSeparator()

        menu.addAction("Make auto fit for all checked", self.make_fit_selected)
        menu.addAction("Save all checked to file", self.save_to_file_selected)
        menu.addSeparator()
        
        menu.addAction("Remove checked", self.remove_selected)
        menu.exec(menu_position)

    def on_fit_added(self, new:Fit):
        self.appendRow(FitItem(new, FitItemController(new)))
        self._model.tree.expandAll()

    def on_displayed_item_changed(self, fit:Fit):
        self._model._compound._displayer.display_fit(fit)

    def on_fit_removed(self, index:QModelIndex):
        self.removeRow(index.row())

    def check_all(self):
        i: int
        for i in range(self.rowCount()):
            self.child(i).setCheckState(Qt.CheckState.Checked)

    def uncheck_all(self):
        i: int
        for i in range(self.rowCount()):
            self.child(i).setCheckState(Qt.CheckState.Unchecked)

    def sort(self, sort_by: Literal["temp", "field"]):
        self.sort_mode = sort_by

        i: int = 0
        while self.child(i) is not None:
            self.child(i).sort_mode = self.sort_mode # type: ignore
            i += 1

        self.sortChildren(0)

    def save_to_file_selected(self):
        save_name, _ = QFileDialog.getSaveFileName(QWidget(), 'Save file')
        if save_name is not None:
            final_df: DataFrame() = DataFrame()
            i: int = 0
            nr_of_rows: int = self.rowCount()
            while i < nr_of_rows:
                child = self.child(i)
                if child.checkState() == Qt.CheckState.Checked:
                    final_df = concat([final_df, DataFrame(child._model.get_result())], axis=1)
                i += 1
            with open(save_name + (".csv" if save_name[-4:] != ".csv" else ""), "w") as f:
                final_df.to_csv(f.name, index=False, sep = ";")

    def make_fit_selected(self):
        i: int = 0
        nr_of_rows: int = self.rowCount()
        while i < nr_of_rows:
            child = self.child(i)
            if child.checkState() == Qt.CheckState.Checked:
                child._model.make_auto_fit(auto = True, next_fit=self.child(i+1)._model if i != nr_of_rows-1 else None)
            i += 1

    def adjust_range_selected(self):
        nr_of_rows: int = self.rowCount()
        child = self.child(0)

        if nr_of_rows == 0:
            msg: QMessageBox = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("There is no Fit in collection")
            msg.setWindowTitle("Collection is empty!")
            msg.exec()
            return
        
        dlg:QDialog = QDialog()
        default_locale: QLocale = QLocale(QLocale.Language.English, QLocale.Country.UnitedStates)
        dlg.setLocale(default_locale)
        dlg.setWindowTitle(f"Set parameters ranges for all fits")
        layout: QVBoxLayout = QVBoxLayout()

        lh: QHBoxLayout = QHBoxLayout()

        inf_l:QLabel = QLabel("Relaxation nr")
        inf_l.setMinimumSize(QSize(64, 0))
        inf_l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        cb:QComboBox = QComboBox()
        cb.addItem("1")
        cb.addItem("2")
    
        lh.addWidget(inf_l)
        lh.addWidget(cb)
        layout.addLayout(lh)

        new_ranges: dict[str,tuple[QLineEdit, QLineEdit]] = {}
        p: str

        for p in child._model.relaxations[0].parameters:
            l: QHBoxLayout = QHBoxLayout()

            v: QDoubleValidator = QDoubleValidator()
            loc: QLocale = QLocale(QLocale.c())
            loc.setNumberOptions(QLocale.NumberOption.RejectGroupSeparator)
            v.setLocale(loc)

            low: QLineEdit = QLineEdit()
            low.setLocale(default_locale)
            low.setValidator(v)
            low.setText(str(p.min))

            up: QLineEdit = QLineEdit()
            up.setLocale(default_locale)
            up.setValidator(v)
            up.setText(str(p.max))

            label:QLabel = QLabel(p.symbol)
            label.setMinimumSize(QSize(65, 0))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            new_ranges[p.name] = (low, up)
            l.addWidget(low)
            l.addWidget(label)
            l.addWidget(up)

            layout.addLayout(l)

        buttons_layout: QHBoxLayout = QHBoxLayout()
        button: QPushButton = QPushButton("Apply")
        button.clicked.connect(lambda: self.set_new_ranges(new_ranges, False, dlg, cb))

        force_button: QPushButton() = QPushButton("Force change")
        force_button.clicked.connect(lambda: self.set_new_ranges(new_ranges, True, dlg, cb))

        buttons_layout.addWidget(button)
        buttons_layout.addWidget(force_button)
        layout.addLayout(buttons_layout)

        dlg.setLayout(layout)
        dlg.exec()

    def remove_selected(self):
        i: int = 0
        nr_of_rows: int = self.rowCount()
        while i < nr_of_rows:
            child = self.child(i)
            if child.checkState() == Qt.CheckState.Checked:
                self._model.remove(child._model._name, child.index())
                nr_of_rows -= 1
                i -= 1
            i += 1

    def set_new_ranges(self, new_ranges, force, dlg, cb):
        i: int = 0
        nr_of_rows: int = self.rowCount()
        while i < nr_of_rows:
            print(i)
            child = self.child(i)
            if child.checkState() == Qt.CheckState.Checked:
                child._model.set_new_ranges(new_ranges, force, dlg, cb.currentIndex(), False)
            i += 1

        dlg.close()

    def make_tau_fits_checked(self):
        i : int
        points: list[tuple(float, float, float)] = []
        for i in range(self.rowCount()):
            item: FitItem = cast(FitItem, self.child(i))
            if item.checkState() == Qt.CheckState.Checked:
                for r in item._model.relaxations:
                    df: DataFrame = item._model._df
                    temp = round((df["Temperature"].max() + df["Temperature"].min())/2, 1)
                    field = round((df["MagneticField"].max() + df["MagneticField"].min())/2, 0)
                    points.append((r.get_tau(), temp, field))

        if len(points) < 2:
            return 
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

        new_fit: TauFit = TauFit(name, self._model._compound, self._model)
        for p in points:
            new_fit.append_point(*p)
        self.parent().child(3)._model.append_tau_fit(new_fit, display=True)