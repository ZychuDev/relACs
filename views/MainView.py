from PyQt6.QtWidgets import QMainWindow, QSplitter
from .WorkingSpace import WorkingSpace
from .ControlTreeView import ControlTreeView

class MainView(QMainWindow):
    """
        Implements relACs user interface.
    """
    def __init__(self):
        super().__init__()

        self.setObjectName("MainWindow")
        # self.resize(930, 86)
        self.splitter = QSplitter()
        
        self.working_space = WorkingSpace()
        self.control_tree: ControlTreeView = ControlTreeView(self.working_space)
        
        self.splitter.addWidget(self.control_tree)
        self.splitter.addWidget(self.working_space)
        self.splitter.setStretchFactor(0,2)
        self.splitter.setStretchFactor(1,9)
        self.setCentralWidget(self.splitter)
