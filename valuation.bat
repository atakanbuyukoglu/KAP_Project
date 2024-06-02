call activate kap
set /p ticker=Degerlenecek hisse ismi?:
python valuation.py %ticker%

pause