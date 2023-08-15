from openpyxl import Workbook, worksheet

# Auto fit the columns of a worksheet to its data
def auto_fit_columns(sheet: worksheet):
    for column_cells in sheet.columns:
        max_length = 0
        column = column_cells[0].column_letter  # Get the column name
        for cell in column_cells:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        sheet.column_dimensions[column].width = max_length

def standardize_ticker(ticker):
    # Accept only upper characters
    ticker = ticker.upper()
    # Some tickers have multiple keys separated by comma
    ticker = ticker.split(', ')
    # Take the longest ticker only
    ticker = max(ticker, key=len)
    return ticker
