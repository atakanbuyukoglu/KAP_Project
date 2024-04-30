from src.Valuation.Records import Records
from src.Valuation.Metrics import Company
from pathlib import Path

company_name = 'megap'

records_path = Path(__file__).parent / "Data" / 'Valuation'
data_path = records_path.parent
records_path.mkdir(parents=True, exist_ok=True)

company = Company(company_name, data_path, update=False)

record_file = Records(records_path / 'Valuation_all.xlsx', online=True)

company.get_share_count(online=True)
record_file.update_ticker(company_name)
