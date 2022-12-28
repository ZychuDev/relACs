class Point():
    """Point in three dimensional space

        Args:
            tau (float): Relaxation time.
            temp (float): Temperature.
            field (float): Filed strange.
            is_hidden (bool, optional): Determines wheter point is taken into account in fitting process. Defaults to False.
    """

    def __init__(self, tau:float, temp:float, field: float, is_hidden=False):
        self.tau = tau
        self.temp = temp
        self.field = field

        self.is_hidden = is_hidden

    def get_jsonable(self) -> dict:
        """Marshal Point to python dictionary.

        Returns:
            dict: Point marshaled into dictionary.
        """
        jsoable: dict = {
            "tau": self.tau,
            "temp": self.temp,
            "field": self.field,
            "is_hidden": self.is_hidden
        }
        return jsoable