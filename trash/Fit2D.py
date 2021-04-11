from .Fit2DUI import Ui_Fit2D
from .Plot import Plot

from PyQt5.QtWidgets import QPushButton, QWidget

class Fit2D(Ui_Fit2D):
    def __init__(self, parent):
        super(self.__class__, self).__init__()
        
        self.setupUi(self)
        
        self.UpperPlots.insertWidget(0, Plot(caption='Pierwszy'))
        self.UpperPlots.insertWidget(1, Plot(caption='Drugi'))
        self.UpperPlots.insertWidget(2, Plot(caption='Trzeci'))


        buttonPrevious = QPushButton('Previous')
        buttonPrevious.clicked.connect(parent.previousWidget)

        buttonNext = QPushButton('Next')
        buttonNext.clicked.connect(parent.nextWidget)

        self.BottomPanel.addWidget(buttonNext)
        self.BottomPanel.addWidget(buttonPrevious)


