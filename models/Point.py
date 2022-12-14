class Point():
    def __init__(self, tau:float, temp:float, field: float):
        self.tau = tau
        self.temp = temp
        self.field = field

        self.is_hidden = False