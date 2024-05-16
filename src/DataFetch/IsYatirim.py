# Request related imports
from .Helpers.RequestWrapper import Request

# Miscellaneous imports
from pathlib import Path

SLEEP_TIME = 2.01

class IsYatirim:

    def __init__(self, data_path) -> None:
        self.companies_path = Path(data_path)
        self.r = Request(sleep_time=SLEEP_TIME)

        self.company_info = None