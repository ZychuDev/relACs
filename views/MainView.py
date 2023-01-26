from PyQt6.QtWidgets import QMainWindow, QSplitter, QMenu, QMenuBar
from PyQt6.QtGui import QKeySequence
from .WorkingSpace import WorkingSpace
from .ControlTreeView import ControlTreeView
from writers.SettingsWriter import edit_default_settings
class MainView(QMainWindow):
    """
        Implements relACs user interface.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RelACs")
        self.setObjectName("MainWindow")

        
        self.splitter = QSplitter()
        
        self.working_space = WorkingSpace()
        self.control_tree: ControlTreeView = ControlTreeView(self.working_space)
        
        self.splitter.addWidget(self.control_tree)
        self.splitter.addWidget(self.working_space)
        self.splitter.setStretchFactor(0,6)
        self.splitter.setStretchFactor(1,9)

        self.menubar = QMenuBar(self)
        
        self.menuSettings = QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")
        self.menuSettings.setTitle("Settings")
        self.menuSettings.addAction("Default Settings", edit_default_settings)
        self.menubar.addAction(self.menuSettings.menuAction())

        self.menuSettings = QMenu(self.menubar)
        self.menuSettings.setTitle("File")
        self.menuSettings.addAction("Save", self.control_tree.compounds.save)
        self.menuSettings.addAction("Save as ...", self.control_tree.compounds.save_to_json)
        self.menubar.addAction(self.menuSettings.menuAction())
        self.setMenuBar(self.menubar)


        self.menuSettings = QMenu(self.menubar)
        self.menuSettings.setTitle("Undo/Redo")
        self.menuSettings.addAction("Undo | Ctrl+Z", self.try_undo)
        self.menuSettings.addAction("Redo | Ctrl+Y", self.try_redo)
        self.menubar.addAction(self.menuSettings.menuAction())
        self.setMenuBar(self.menubar)

        self.setCentralWidget(self.splitter)

    def try_redo(self):
        try:
            self.working_space.currentWidget().on_redo() 
        except Exception as e:
            pass

    def try_undo(self):
        try:
            self.working_space.currentWidget().on_undo() 
        except Exception as e:
            pass

    