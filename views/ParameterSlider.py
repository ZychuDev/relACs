from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QCheckBox, QSlider
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QFont

from models import Parameter

from scipy.interpolate import interp1d # type: ignore

class ParameterSlider(QWidget):
    def __init__(self):
        super().__init__()
        self.parameter: Parameter = None

        layout: QHBoxLayout = QHBoxLayout()
        self.label = QLabel("p_name")
        self.label.setMinimumSize(QSize(25,22))
        font: QFont = self.label.font()
        font.setPixelSize(16)
        font.setBold(True)
        self.label.setFont(font)
        self.slider = QSlider()
        self.slider.setMinimumSize(QSize(40, 22))
        self.slider.setTracking(True)
        self.slider.setOrientation(Qt.Orientation.Horizontal)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setRange(0, 100)

        self.line_edit = QLineEdit()
        self.line_edit.setMinimumSize(QSize(0, 8))
        self.line_edit.setMaximumSize(QSize(100, 16777215))

        self.blocked_check = QCheckBox("Blocked")
        self.blocked_check.setMinimumSize(QSize(85, 0))
        self.blocked_check.setMaximumSize(QSize(85, 16777215))

        
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.blocked_check)

        self.setLayout(layout)

    def set_parameter(self, parameter:Parameter):
        if self.parameter is not None:
            self.slider.disconnect()
            self.line_edit.disconnect()

        self.parameter: Parameter = parameter

        self.label.setText(self.parameter.symbol)
        self.set_edit_value_silent(self.parameter.value)
        self.set_slider_value_silent(self.edit_to_slider())


        self.slider.valueChanged.connect(lambda: self.set_edit_value_silent(self.slider_to_param()))
        self.line_edit.editingFinished.connect(lambda: self.set_slider_value_silent(self.edit_to_slider()))

    def set_slider_value_silent(self, v: int):
        self.slider.blockSignals(True)
        self.slider.setValue(v)
        self.slider.blockSignals(False)

    def set_edit_value_silent(self, v: float):
        self.slider.blockSignals(True)
        self.line_edit.setText(str(v))
        self.slider.blockSignals(False)

    def edit_to_slider(self) -> int: 
        v: float = float(self.line_edit.text())
        return int(interp1d([self.parameter.min, self.parameter.max], [self.slider.minimum(), self.slider.maximum()])(v))

    def slider_to_param(self) -> float:
        v: int = self.slider.value()
        result: float = float(interp1d([self.slider.minimum(), self.slider.maximum()], [self.parameter.min, self.parameter.max])(v))
        return round(result, 8)



        

