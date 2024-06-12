from src.DataFetch.KAP import KAP
from src.Valuation.Records import Records
from pathlib import Path
from wakepy import keep

data_path = Path(__file__).parent / "Data/"
data_path.mkdir(parents=True, exist_ok=True)

records_path = Path(__file__).parent / "Data" / 'Valuation'
records_path.mkdir(parents=True, exist_ok=True)

kap = KAP(data_path=data_path)
company_info = kap.get_company_info(online=True)
companies = list(company_info.companies.keys())

record_file = Records(records_path / 'Valuation_all.xlsx', initial_tickers=companies, add_tickers=False, online=True)

#record_file.update_share_counts(intrinsic_online=False)
#record_file.update()
with keep.presenting():
    record_file.update_prices()
    #record_file.update_intrinsic_values()
    #record_file.online = False
    #record_file.update_intrinsic_values(quarter=True)
    #record_file.update_revenue_change()
    #record_file.update_last_quarter()

