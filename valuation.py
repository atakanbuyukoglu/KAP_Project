from src.Valuation.Metrics import Company
from pathlib import Path

data_path = Path(__file__).parent / "Data/"
data_path.mkdir(parents=True, exist_ok=True)

kchol = Company('kchol', data_path)

print(kchol.get_cash_flow_statement())
