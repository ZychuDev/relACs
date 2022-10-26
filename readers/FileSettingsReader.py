from configparser import RawConfigParser   
   
class FileSettingsReader():
    def __init__(self):
        self.config: RawConfigParser = RawConfigParser()
        self.config.optionxform = str
        self.config.read('default_settings.ini')
        print(dict(self.config.items()))

    def get_external_headings(self) -> dict[str, str]:
        return dict(self.config['Headers'].items())