import builtins
"""Container class for all data"""
class AppStateBase:
    def __init__(self):
        self.columnsHeadersExternal = ["Temperature (K)","Magnetic Field (Oe)","AC X' (emu/Oe)","AC X'' (emu/Oe)","AC Frequency (Hz)"]
        self.epsTemp = 0.05
        self.epsField = 1
        self.ranges ={'alpha':(0,1), 'beta':(0,1), 'tau':(-10,0), 'chiT':(0,20), 'chiS':(0,20),
        'Adir': (-15,1),
        'Ndir': (0,8),
        'B1': (-2,11),
        'B2': (-9,1),
        'B3': (-9,1),
        'CRaman': (0,100),
        'NRaman': (0,15),
        'Tau0': (0,12),
        'DeltaE': (0,3000)
        }
        self.log_params = ('Adir', 'B1', 'B2', 'B3', 'Tau0')
        self.resolution = 125
        self.sample_mass = 0.01
        self.separator = ';'

        
    # def addModel(self, name):
    #     if name in self.models:
    #         print("Model already exists choose other name or delete old one!")
    #         return
    #     self.models[name] = ModelItem(self.ui, name)

builtins.AppState = AppStateBase()