from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QCheckBox, QSlider
from PyQt6.QtCore import QSize, QLocale, Qt
from PyQt6.QtGui import QFont, QDoubleValidator

from models import Parameter

from scipy.interpolate import interp1d # type: ignore
from numpy import log10

# from time import time
class ParameterSlider(QWidget):
    def __init__(self):
        super().__init__()
        self.parameter: Parameter = None

        layout: QHBoxLayout = QHBoxLayout()
        self.label = QLabel("p_name")
        self.label.setMinimumSize(QSize(70,22))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font: QFont = self.label.font()
        font.setPixelSize(14)
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

        self.blocked_on_0 = QCheckBox("Blocked on 0")
        self.blocked_on_0.setMinimumSize(QSize(95, 0))
        self.blocked_on_0.setMaximumSize(QSize(85, 16777215))

        
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.blocked_check)
        layout.addWidget(self.blocked_on_0)

        self.setLayout(layout)

    def set_parameter(self, parameter:Parameter):
        if self.parameter is not None:
            self.slider.disconnect()
            self.line_edit.disconnect()
            self.blocked_check.disconnect()
            self.blocked_on_0.disconnect()

        self.parameter = parameter
        v_min: float
        v_max: float
        if self.parameter.is_log:
            self.blocked_on_0.setEnabled(True)
            v_min = log10(self.parameter.min)
            v_max= log10(self.parameter.max)
        else:
            self.blocked_on_0.setEnabled(False)
            v_min = self.parameter.min
            v_max= self.parameter.max

        validator: QDoubleValidator = QDoubleValidator(v_min, v_max, 8)
        l = QLocale(QLocale.c())
        l.setNumberOptions(QLocale.NumberOption.RejectGroupSeparator)
        validator.setLocale(l)
        validator.fixup = self.fixup_line_edit # type: ignore
        self.line_edit.setValidator(validator)
        log_str:str = f"<html><head/><body><p>log<span style=\" vertical-align:sub;\">10</span> {self.parameter.symbol}</html>"
        self.label.setText(self.parameter.symbol if not self.parameter.is_log else log_str)
        self.set_edit_value_silent(self.parameter.value)
        self.set_slider_value_silent(self.parameter.value)
        self.set_blocked_silent(self.parameter.is_blocked)
        self.set_blocked_0_silent(self.parameter.is_blocked_on_0)


        self.slider.valueChanged.connect(lambda: self.parameter.set_value(self.slider_to_param(), emit_reset_errors=True)) #lambda: self.set_edit_value_silent()
        self.line_edit.editingFinished.connect(lambda: self.parameter.set_value(round(float(self.line_edit.text()), 8) if not self.parameter.is_log else 10 ** round(float(self.line_edit.text()), 8)))
        self.blocked_check.stateChanged.connect(self.on_checkbox_clicked)
        self.blocked_on_0.stateChanged.connect(self.on_0_checkbox_clicked)

        self.parameter.value_changed.connect(self.set_slider_value_silent)
        self.parameter.value_changed.connect(self.set_edit_value_silent)
        self.parameter.block_state_changed.connect(self.set_blocked_silent)
        self.parameter.block_0_state_changed.connect(self.set_blocked_0_silent)
        self.parameter.range_changed.connect(self.on_range_change)
        
    def on_range_change(self):
        self.set_parameter(self.parameter)

    def on_checkbox_clicked(self):
        self.parameter.set_blocked(self.blocked_check.isChecked())

    def on_0_checkbox_clicked(self):
        self.parameter.set_blocked_0(self.blocked_on_0.isChecked())
        if self.parameter.is_blocked_on_0:
            self.parameter.set_value(0.0) 
            self.set_disabled(True)
        else:
            self.set_disabled(False)

    def set_blocked_silent(self, v: bool):
        self.blocked_check.blockSignals(True)
        self.blocked_check.setChecked(v)
        self.blocked_check.blockSignals(False)

    def set_blocked_0_silent(self, v: bool):
        self.blocked_on_0.blockSignals(True)
        self.blocked_on_0.setChecked(v)
        self.blocked_on_0.blockSignals(False)

    def set_slider_value_silent(self, v: float):
        self.slider.blockSignals(True)
        if(v < self.parameter.min):
            self.slider.setEnabled(False)
            return
        self.slider.setEnabled(True)
        if self.parameter.is_log:
            self.slider.setValue(int(interp1d([log10(self.parameter.min), log10(self.parameter.max)], [self.slider.minimum(), self.slider.maximum()])(log10(v))))
        else:
            self.slider.setValue(int(interp1d([self.parameter.min, self.parameter.max], [self.slider.minimum(), self.slider.maximum()])(v)))
        self.slider.blockSignals(False)

    def set_edit_value_silent(self, v: float):
        self.slider.blockSignals(True)
        if self.parameter.is_log:
            self.line_edit.setText(str(round(log10(v), 8)))
        else:
            self.line_edit.setText(str(round(v, 8)))
        self.slider.blockSignals(False)
        # print(time())

    def slider_to_param(self) -> float:
        v: int = self.slider.value()
        result: float
        if self.parameter.is_log:
            result = float(interp1d([self.slider.minimum(), self.slider.maximum()], [log10(self.parameter.min), log10(self.parameter.max)])(v))
            return 10**result
        else:
            result = float(interp1d([self.slider.minimum(), self.slider.maximum()], [self.parameter.min, self.parameter.max])(v))
        return round(result, 8)
    
    def fixup_line_edit(self, v: str):
        print("fixup")
        self.set_edit_value_silent(round(self.parameter.value, 8))

    def set_disabled(self, flag:bool):
        self.slider.setDisabled(flag)
        self.line_edit.setDisabled(flag)





        

