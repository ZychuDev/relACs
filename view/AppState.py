"""Container class for all data"""
class AppState:
    columnsHeadersExternal = ["Temperature (K)","Magnetic Field (Oe)","AC X' (emu/Oe)","AC X'' (emu/Oe)","AC Frequency (Hz)"]
    epsTemp = 0.05
    epsField = 1
 
    # def addModel(self, name):
    #     if name in self.models:
    #         print("Model already exists choose other name or delete old one!")
    #         return
    #     self.models[name] = ModelItem(self.ui, name)