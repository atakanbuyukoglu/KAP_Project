call activate kap
set /p ticker=Guncellenecek hisse ismi?:
python update_ticker_record.py %ticker%

pause