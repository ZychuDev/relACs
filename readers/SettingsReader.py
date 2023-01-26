from configparser import RawConfigParser   
   
class SettingsReader():
    def __init__(self):
        self.config: RawConfigParser = RawConfigParser()
        self.config.optionxform = str
        self.config.read('default_settings.ini')

    def get_headings_maping(self) -> dict[str, str]:
        return dict(self.config['Headers'].items())

    def get_epsilons(self) -> tuple[float, float]:
        return (float(self.config['Epsilons']['Field']), float(self.config['Epsilons']['Temp']))

    def get_ranges(self) -> dict[str, tuple[float, float]]:
        tmp: dict[str, str] = dict(self.config["Ranges"])
        result: dict[str, tuple[float, float]] = dict()
        for key, val in tmp.items():
            s: list[str] = val.split(',')
            result[key] = float(s[0]), float(s[1])

        return result

    def get_tolerances(self) -> dict[str, float]:
        return {
            "f_tol" : float(self.config['Tolerance']['ftol']),
            "x_tol" : float(self.config['Tolerance']['xtol']),
            "g_tol" : float(self.config['Tolerance']['gtol']),
        }