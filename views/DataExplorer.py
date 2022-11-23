from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class DataExplorer(QWidget):
    def __init__(self):
        super().__init__()
        vertical_layout: QVBoxLayout = QVBoxLayout()
        vertical_layout.addWidget(QLabel("Data Explorer"))
        self.setLayout(vertical_layout)