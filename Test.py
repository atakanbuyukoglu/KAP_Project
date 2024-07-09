from src.DataFetch.KAP import KAP
from src.DataFetch.IsYatirim import IsYatirim
from pathlib import Path
from datetime import date, timedelta

data_path = Path(__file__).parent / "Data/"

isyat = IsYatirim()
x = isyat.get_sector('flap')
print(x)

#kap.save_financials('AKFK')