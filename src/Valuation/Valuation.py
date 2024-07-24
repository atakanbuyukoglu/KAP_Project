from .Metrics import Company

# Returns specific metrics per share for valuation purposes
class Valuation:

    def __init__(self, ticker, data_path) -> None:
        self.company = Company(ticker, data_path, update=False)
        self.share_count = self.company.get_share_count()

    def get_ebitda(self, quarter=False):
        return self.company.get_ebitda(control_adjusted=True, quarter=quarter) / self.share_count
    
    def get_net_assets(self):
        return self.company.get_net_assets_for_ev(control_adjusted=True) / self.share_count
    
    def get_book_value(self):
        return self.company.get_equity() / self.share_count
    
    def get_net_profit(self):
        return self.company.get_net_profit(quarter=False) / self.share_count
    
