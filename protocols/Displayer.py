from typing import Protocol

class Displayer(Protocol):

    def display_home_page(self):
        """Display home page.
        """
        ...
    
    def display_measurement(self, measurement): 
        """Display measurement page.

        Args:
            measurement (Measurement): Model for measurement page.
        """
        ...

    def display_fit(self, fit):
        """Display fit page.

        Args:
            fit (Fit): Model for measurement page.
        """
        ...

    def display_tau_fit(self, tau_fit):
        """Display tau fit page.

        Args:
            tau_fit (TauFit): Model for tau fit page.
        """