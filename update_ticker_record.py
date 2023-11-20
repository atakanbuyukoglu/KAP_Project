from src.Valuation.Records import Records
from pathlib import Path

records_path = Path(__file__).parent / "Data" / 'Valuation'
records_path.mkdir(parents=True, exist_ok=True)

record_file = Records(records_path / 'Valuation_all.xlsx', online=True)

record_file.update_ticker('ınveo')
