import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QIcon
from pandas import DataFrame # type: ignore

from models import MainModel
from controllers import MainController
from views import MainView

class RelACs(QApplication):
    def __init__(self, sys_argv:list[str]):
        super(RelACs, self).__init__(sys_argv)
        self.main_model = MainModel()
        self.main_controller: MainController = MainController(self.main_model)
        self.main_view: MainView = MainView(self.main_model, self.main_controller)

        app_icon: QIcon = QIcon("./assets/img/relACs.ico")
        RelACs.setWindowIcon(app_icon) 
        self.main_view.showMaximized()

if __name__ == "__main__":
    app:QApplication = RelACs(sys.argv)
    # app.setStyle("Fusion")
    sys.exit(app.exec())