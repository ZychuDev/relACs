from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QCheckBox, QSlider
from PyQt6.QtCore import QSize, Qt

from models import Parameter

from scipy.interpolate import interp1d # type: ignore

class ParameterSlider(QWidget):
    def __init__(self):
        super().__init__()
        self.parameter: Parameter = None

        layout: QHBoxLayout = QHBoxLayout()
        self.label = QLabel("p_name")
        self.slider = QSlider()
        self.slider.setMinimumSize(QSize(50, 16))
        self.slider.setTracking(True)
        self.slider.setOrientation(Qt.Orientation.Horizontal)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setRange(0, 100)

        self.line_edit = QLineEdit()
        self.line_edit.setMinimumSize(QSize(0, 10))
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
        p = self.parameter
        self.label.setText(p.symbol)
        self.set_slider_value_silent(map(p.value))
        self.line_edit.set_edit_value_silent(p.value)

        self.slider.valueChanged.connect(lambda v: self.set_edit_value_silent(self.slider_to_param(v)))
        self.line_edit.textEdited.connect(lambda s: self.set_edit_value_silent(self.param_to_slider(float(s))))

    def set_slider_value_silent(self, v: float):
        self.slider.blockSignals(True)
        self.slider.setValue(self.parameter.value)
        self.slider.blockSignals(False)

    def set_edit_value_silent(self, v: float):
        self.slider.blockSignals(True)
        self.line_edit.setText(str(v))
        self.slider.blockSignals(False)

    def param_to_slider(self, v: float) -> int: 
        return int(interp1d([self.parameter.min, self.parameter.max], [self.slider.minimum(), self.slider.maximum()])(v))

    def slider_to_param(self) -> float:
        v: int = self.slider.value()
        return interp1d([self.slider.minimum(), self.slider.maximum()], [self.parameter.min, self.parameter.max])(v)



        

