import builtins
"""Container class for all data"""
class AppStateBase:
    def __init__(self):

        self.resolution = 125
        self.sample_mass = 0.01
        self.separator = ';'


builtins.AppState = AppStateBase()