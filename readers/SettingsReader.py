from configparser import RawConfigParser   
   
class SettingsReader():
    def __init__(self):
        self.config: RawConfigParser = RawConfigParser()
        self.config.optionxform = str
        self.config.read('default_settings.ini')

    def get_headings_maping(self) -> dict[str, str]:
        return dict(self.config['Headers'].items())

    def get_epsilons(self) -> tuple[float, float]:
        return (self.config['Epsilons']['Field'], self.config['Epsilons']['Temp'])