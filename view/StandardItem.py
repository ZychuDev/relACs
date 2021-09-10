from PyQt5.QtGui import QColor, QStandardItem, QFont


class StandardItem(QStandardItem):
    def __init__(self, txt='', font_size=12, set_bold=False, color=QColor(0,0,0)):
        super().__init__()
        fnt = QFont('Open Sans', font_size)
        fnt.setBold(set_bold)

        self.setEditable(False)
        self.setForeground(color)
        self.setFont(fnt)
        self.setText(txt)
        #self.setIcon(jakasTam.png)
    def double_click(self):
        print("No provided action for this item")

    def click(self):
        print("No provided action for single click")

