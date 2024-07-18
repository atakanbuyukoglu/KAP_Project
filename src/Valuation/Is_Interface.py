from ..DataFetch.IsYatirim import IsYatirim

class IsParser():
    
    def __init__(self, data_path) -> None:
        self.is_yat = IsYatirim()

    def get_sector(self, ticker: str):
        return self.is_yat.get_sector(ticker)
    