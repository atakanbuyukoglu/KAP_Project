from ..DataFetch.KAP import KAP

class KAPParser():
    
    def __init__(self, data_path) -> None:
        self.kap = KAP(data_path)

    def get_financials(self, ticker: str, update=True):
        return self.kap.get_company_financials(ticker, update=update)
    
    def get_share_count(self, ticker: str):
        return self.kap.get_share_count(ticker)
    
    def get_info(self, ticker: str):
        company_info = self.kap.get_company_info()
        return company_info.loc[ticker]