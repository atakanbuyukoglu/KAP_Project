from src.DataFetch.KAP import KAP
from src.Valuation.Records import Records
from pathlib import Path

data_path = Path(__file__).parent / "Data/"
data_path.mkdir(parents=True, exist_ok=True)

records_path = Path(__file__).parent / "Data" / 'Valuation'
records_path.mkdir(parents=True, exist_ok=True)

kap = KAP(data_path=data_path)
company_info = kap.get_company_info()
companies = list(company_info.index)

record_file = Records(records_path / 'Valuation_all.xlsx', initial_tickers=companies, add_tickers=False, online=True)

record_file.update_intrinsic_values()
