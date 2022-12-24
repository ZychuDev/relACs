class Point():
    def __init__(self, tau:float, temp:float, field: float, is_hidden=False):
        self.tau = tau
        self.temp = temp
        self.field = field

        self.is_hidden = is_hidden

    def get_jsonable(self) -> dict:
        jsoable: dict = {
            "tau": self.tau,
            "temp": self.temp,
            "field": self.field,
            "is_hidden": self.is_hidden
        }
        return jsoable