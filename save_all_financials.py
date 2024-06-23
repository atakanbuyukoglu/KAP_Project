from src.DataFetch.KAP import KAP
from pathlib import Path
from wakepy import keep

data_path = Path(__file__).parent / "Data/"
data_path.mkdir(parents=True, exist_ok=True)

kap = KAP(data_path=data_path)

companies = kap.get_company_info(online=True)

with keep.presenting():
    for ticker in companies.companies.keys():
        print(ticker, 'start')
        kap.get_company_financials(ticker)
        print(ticker, 'end')

