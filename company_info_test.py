from src.DataFetch.KAP import KAP
from pathlib import Path

data_path = Path(__file__).parent / "Data/"
data_path.mkdir(parents=True, exist_ok=True)

kap = KAP(data_path=data_path)

print(kap.get_company_info())
