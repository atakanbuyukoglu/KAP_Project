from src.DataFetch.KAP import KAP
from src.DataFetch.Helpers.DateHandler import DateHandler
from pathlib import Path
from datetime import date, timedelta

data_path = Path(__file__).parent / "Data/"

kap = KAP(data_path)
x = kap.get_share_count('SISE', online=False)
print(x)

#kap.save_financials('AKFK')