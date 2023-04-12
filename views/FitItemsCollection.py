from PyQt6.QtCore import pyqtSlot, QPoint, QModelIndex, Qt
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtWidgets import QMenu, QFileDialog, QWidget, QInputDialog, QMessageBox

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
                    final_df = concat([final_df, DataFrame(child._model.get_result())], axis=1, ignore_index=True)
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