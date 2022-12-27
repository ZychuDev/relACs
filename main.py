import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from views import MainView

class RelACs(QApplication):
    def __init__(self, sys_argv:list[str]):
        super(RelACs, self).__init__(sys_argv)
        self.main_view: MainView = MainView()
        app_icon: QIcon = QIcon("./assets/img/relACs.ico")
        RelACs.setWindowIcon(app_icon) 
        self.main_view.showMaximized()

if __name__ == "__main__":
    app:QApplication = RelACs(sys.argv)
    # app.setStyle("Fusion")
    sys.exit(app.exec())