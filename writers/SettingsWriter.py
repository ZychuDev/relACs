from PyQt6.QtCore import QLocale, QSize, Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QPushButton, QGroupBox
from PyQt6.QtGui import QDoubleValidator, QIntValidator
from configparser import RawConfigParser 

from functools import partial
from models import Parameter

def edit_default_settings():
    """Display Dialog Window dor editing default settings
    """
    dlg = QDialog()
    dlg.setWindowTitle("Default Settings")

    config = RawConfigParser()
    config.optionxform = str
    config.read('default_settings.ini')

    r = config['Ranges']
    ranges = {}
    for p in r:
        ranges[p] = [float(s) for s in config['Ranges'][p].split(',')]

    layout:QVBoxLayout = QVBoxLayout()
    ranges_edit: dict = {}
    ranges_group:QGroupBox = QGroupBox("Parameters ranges")
    for p in ranges:
        l = QHBoxLayout()
        low = QLineEdit()
        low.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))

        v = QDoubleValidator()
        loc = QLocale(QLocale.c())
        loc.setNumberOptions(QLocale.NumberOption.RejectGroupSeparator)
        v.setLocale(loc)

        low.setValidator(v)
        low.setText(str(ranges[p][0]))

        up = QLineEdit()
        up.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))


        up.setValidator(v)
        up.setText(str(ranges[p][1]))

        ranges_edit[p] = [low, up]
        l.addWidget(low)
        label = QLabel(Parameter.name_to_symbol[p])
        label.setMinimumSize(QSize(65, 0))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(label)
        l.addWidget(up)
        layout.addLayout(l)
    ranges_group.setLayout(layout)

    layout = QVBoxLayout()
    headers_group:QGroupBox = QGroupBox("Headers")
    headers_edit:dict = {}
    headers = dict(config['Headers']).items()
    for key, val in headers:
        l = QHBoxLayout()
        label = QLabel(key)
        label.setMinimumSize(QSize(150, 0))
        label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        edit = QLineEdit()
        edit.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        edit.setText(val)

        l.addWidget(label)
        l.addWidget(edit)
        headers_edit[key] = edit
        layout.addLayout(l)
    headers_group.setLayout(layout)

    layout = QVBoxLayout()
    epsilons_group:QGroupBox = QGroupBox("Epsilons")
    epsilons_edit = {}
    epsilons = dict(config['Epsilons'])
    for key, val in epsilons.items():
        l = QHBoxLayout()
        label = QLabel(f'\u03B5<span style=\" vertical-align:sub;\">{key}</span>')
        label.setMinimumSize(QSize(150, 0))
        label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        edit = QLineEdit()
        edit.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        v = QDoubleValidator()
        v.setBottom(0)
        loc = QLocale(QLocale.c())
        loc.setNumberOptions(QLocale.NumberOption.RejectGroupSeparator)
        v.setLocale(loc)
        edit.setValidator(v)
        edit.setText(val)
        l.addWidget(label)
        l.addWidget(edit)
        epsilons_edit[key] = edit
        layout.addLayout(l)
    epsilons_group.setLayout(layout)

    layout = QVBoxLayout()
    plot_group:QGroupBox = QGroupBox("Plot")
    plot_edit = {}
    plot_settings = dict(config['Plot'])
    for key , val in plot_settings.items():
        l = QHBoxLayout()
        label = QLabel(key)
        label.setMinimumSize(QSize(150, 0))
        label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        edit = QLineEdit()
        edit.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        v = QIntValidator()
        v.setRange(0,1000)
        loc = QLocale(QLocale.c())
        loc.setNumberOptions(QLocale.NumberOption.RejectGroupSeparator)
        v.setLocale(loc)
        edit.setValidator(v)
        edit.setText(val)
        l.addWidget(label)
        l.addWidget(edit)
        plot_edit[key] = edit
        layout.addLayout(l)
    plot_group.setLayout(layout)

    layout = QVBoxLayout()
    tolerances_group:QGroupBox = QGroupBox("Fit tolerances")
    tolerance_edit = {}
    tolerance_settings = dict(config['Tolerance'])
    for key , val in tolerance_settings.items():
        l = QHBoxLayout()
        label = QLabel(key)
        label.setMinimumSize(QSize(150, 0))
        label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        edit = QLineEdit()
        edit.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        v = QDoubleValidator()
        v.setRange(0,1e-128)
        loc = QLocale(QLocale.c())
        loc.setNumberOptions(QLocale.NumberOption.RejectGroupSeparator)
        v.setLocale(loc)
        edit.setValidator(v)
        edit.setText(val)
        l.addWidget(label)
        l.addWidget(edit)
        tolerance_edit[key] = edit
        layout.addLayout(l)
    tolerances_group.setLayout(layout)
    
    layout_1:QHBoxLayout = QHBoxLayout()
    layout_2: QVBoxLayout = QVBoxLayout()
    layout_2.addWidget(headers_group)
    layout_2.addWidget(epsilons_group)
    layout_2.addWidget(plot_group)
    layout_2.addWidget(tolerances_group)

    layout_1.addWidget(ranges_group)
    layout_1.addLayout(layout_2)

    layout: QVBoxLayout = QVBoxLayout()
    layout.addLayout(layout_1)
    button = QPushButton("Apply new default settigs")
    button.clicked.connect(partial(write_default_settings, ranges_edit, headers_edit, epsilons_edit, plot_edit, tolerance_edit, dlg))
    layout.addWidget(button)

    reset_button = QPushButton("Reset settings")
    reset_button.clicked.connect(partial(reset_settings, dlg))
    layout.addWidget(reset_button)
    dlg.setLayout(layout)
    dlg.exec()

def write_default_settings(ranges_edit:dict, headers_edit:dict, epsilons_edit:dict, plot_edit:dict, tolerance_edit:dict ,dlg:QDialog):
    """Write new default settings.

    Args:
        ranges_edit (dict): Dictionary off all parameters ranges.
        headers_edit (dict): Dictionary of external headings.
        epsilons_edit (dict): Dictionary of epsilon(clusterization) values.
        plot_edit (dict): Dictionary of plots display settings.
        dlg (QDialog): Dialog Window. Source of new settings.
    """
    config = RawConfigParser()
    config.optionxform = str #type: ignore
    config['Ranges'] = {key:f"{edit[0].text()}, {edit[1].text()}" for key, edit in ranges_edit.items()}
    config['Headers'] = {key:header.text() for key, header in headers_edit.items()}
    config['Epsilons'] = {key:epsilon.text() for key, epsilon in epsilons_edit.items()}
    config['Plot'] = {key:value.text() for key, value in plot_edit.items()}
    config['Tolerance'] = {key:value.text() for key, value in tolerance_edit.items()}

    with open('default_settings.ini', 'w') as f:
        config.write(f)

    dlg.accept()

def reset_settings(dlg):
    config = RawConfigParser()
    config.optionxform = str #type: ignore
    config['Ranges'] = {
        "alpha":"0.0, 1.0",
        "beta":"0.0, 1.0",
        "log10_tau":"-10.0, 0.0",
        "chi_dif":"0.0, 20.0",
        "chi_s":"0.0, 20.0",
        "a_dir":"1e-15, 100.0",
        "n_dir":"0.0, 8.0",
        "b1":"1e-64, 1e+15",
        "b2":"1e-64, 10.0",
        "b3":"1e-64, 10.0",
        "c_raman_1":"0.0, 1.0",
        "n_raman_1":"0.0, 15.0",
        "c_raman_2":"0.0, 1.0",
        "n_raman_2":"0.0, 15.0",
        "m_2": "1.0, 5.0",
        "tau_0":"0.0, 1e+27",
        "delta_e ":"0.0, 3000.0",
    }

    config['Headers'] = {
        "Temperature" : "Temperature (K)",
        "MagneticField ": "Magnetic Field (Oe)",
        "ChiPrime" : "AC X' (emu/Oe)",
        "ChiBis" : "AC X'' (emu/Oe)",
        "Frequency" : "AC Frequency (Hz)",
    }

    config['Epsilons'] = {
        "Field" : "1",
        "Temp" : "0.05",
    }

    config['Plot'] = {
        "picker_radius" : "10",
        "dpi" : "100",
        "dpi_frequency_plots" : "100",
    }

    config['Tolerance'] = {
        "ftol" : "1e-8",
        "xtol" : "1e-8",
        "gtol" : "1e-8",
    }

    with open('default_settings.ini', 'w') as f:
        config.write(f)

    dlg.accept()