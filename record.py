from src.Valuation.Records import Records
from pathlib import Path

records_path = data_path = Path(__file__).parent / "Data" / 'Valuation'
records_path.mkdir(parents=True, exist_ok=True)

record_file = Records(records_path / 'Valuation.xlsx')

record_file.update()
