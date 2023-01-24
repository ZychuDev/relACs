from PyQt6.QtWidgets import QMainWindow, QSplitter, QMenu, QMenuBar
from PyQt6.QtCore import QRect
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
        self.menubar = QMenuBar(self)
        
        self.menuSettings = QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")
        self.menuSettings.setTitle("Settings")

        self.menuSettings.addAction("Default Settings", edit_default_settings)
        self.menubar.addAction(self.menuSettings.menuAction())
        self.setMenuBar(self.menubar)

        self.splitter = QSplitter()
        
        self.working_space = WorkingSpace()
        self.control_tree: ControlTreeView = ControlTreeView(self.working_space)
        
        self.splitter.addWidget(self.control_tree)
        self.splitter.addWidget(self.working_space)
        self.splitter.setStretchFactor(0,6)
        self.splitter.setStretchFactor(1,9)
        self.setCentralWidget(self.splitter)

    