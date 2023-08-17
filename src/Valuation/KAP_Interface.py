from ..DataFetch.KAP import KAP

class KAPParser():
    
    def __init__(self, data_path) -> None:
        self.kap = KAP(data_path)

    def get_financials(self, ticker: str):
        return self.kap.get_company_financials(ticker)