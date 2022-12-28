from PyQt6.QtCore import QLocale, QSize, Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QPushButton
from PyQt6.QtGui import QDoubleValidator, QIntValidator
from configparser import RawConfigParser 

from functools import partial

def edit_default_settings():
        dlg = QDialog()
        dlg.setWindowTitle("Default Settings")

        config = RawConfigParser()
        config.optionxform = str
        config.read('default_settings.ini')

        r = config['Ranges']
        ranges = {}
        for p in r:
            ranges[p] = [float(s) for s in config['Ranges'][p].split(',')]

        layout = QVBoxLayout()
        ranges_edit = {}
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
            label = QLabel(p)
            label.setMinimumSize(QSize(65, 0))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            l.addWidget(label)
            l.addWidget(up)
            layout.addLayout(l)

        headers_edit = {}
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
        
        epsilons_edit = {}
        epsilons = dict(config['Epsilons'])
        for key, val in epsilons.items():
            l = QHBoxLayout()
            label = QLabel(key)
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

        button = QPushButton("Apply new default settigs")
        button.clicked.connect(partial(write_default_settings, ranges_edit, headers_edit, epsilons_edit, plot_edit, dlg))
        layout.addWidget(button)
        dlg.setLayout(layout)
        dlg.exec()

def write_default_settings(ranges_edit, headers_edit, epsilons_edit, plot_edit, dlg):
        config = RawConfigParser()
        config.optionxform = str
        config['Ranges'] = {key:f"{edit[0].text()}, {edit[1].text()}" for key, edit in ranges_edit.items()}
        config['Headers'] = {key:header.text() for key, header in headers_edit.items()}
        config['Epsilons'] = {key:epsilon.text() for key, epsilon in epsilons_edit.items()}
        config['Plot'] = {key:value.text() for key, value in plot_edit.items()}

        with open('default_settings.ini', 'w') as f:
            config.write(f)

        dlg.accept()