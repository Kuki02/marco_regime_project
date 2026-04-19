from pathlib import Path
import io
import requests
import pandas as pd
import yfinance as yf

WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; research-bot/1.0)"}
START_DATE = "2020-01-01"
OUTPUT_DIR = Path("data/raw/sp500")
INDEX_OUTPUT = OUTPUT_DIR / "sp500_index_daily.csv"
TICKERS_OUTPUT = OUTPUT_DIR / "sp500_tickers_daily.csv"
EXCEL_OUTPUT = OUTPUT_DIR / "sp500_data.xlsx"

SECTOR_ETFS = {
    "XLB":  "Materials",
    "XLC":  "Communication Services",
    "XLE":  "Energy",
    "XLF":  "Financials",
    "XLI":  "Industrials",
    "XLK":  "Information Technology",
    "XLP":  "Consumer Staples",
    "XLRE": "Real Estate",
    "XLU":  "Utilities",
    "XLV":  "Health Care",
    "XLY":  "Consumer Discretionary",
}


def fetch_sp500_constituents() -> pd.DataFrame:
    response = requests.get(WIKIPEDIA_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    tables = pd.read_html(io.StringIO(response.text))
    df = tables[0][["Symbol", "Security", "GICS Sector", "GICS Sub-Industry"]].copy()
    df["Symbol"] = df["Symbol"].str.replace(".", "-", regex=False)
    df.columns = ["Ticker", "Company", "Sector", "Sub-Industry"]
    return df


def fetch_index() -> pd.DataFrame:
    df = yf.download("^GSPC", start=START_DATE, auto_adjust=True, progress=False)
    close = df["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close.name = "sp500"
    close.index.name = "Date"
    return close.reset_index()


def fetch_sector_etfs() -> pd.DataFrame:
    etf_tickers = list(SECTOR_ETFS.keys())
    df = yf.download(etf_tickers, start=START_DATE, auto_adjust=True, progress=False)
    close = df["Close"][etf_tickers].copy()
    close.columns = [SECTOR_ETFS[t] for t in etf_tickers]
    close.index.name = "Date"
    return close.reset_index()


def fetch_all_tickers(tickers: list[str]) -> pd.DataFrame:
    df = yf.download(tickers, start=START_DATE, auto_adjust=True, progress=True)
    close = df["Close"].copy()
    close.index.name = "Date"
    return close.reset_index()


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Fetching S&P 500 constituent list from Wikipedia...")
    constituents = fetch_sp500_constituents()
    tickers = constituents["Ticker"].tolist()
    print(f"Found {len(tickers)} tickers")

    print("Downloading S&P 500 index (^GSPC)...")
    index_df = fetch_index()
    index_df.to_csv(INDEX_OUTPUT, index=False)
    print(f"Saved index: {len(index_df)} rows to {INDEX_OUTPUT}")

    print(f"Downloading daily close prices for all {len(tickers)} tickers from {START_DATE}...")
    tickers_df = fetch_all_tickers(tickers)
    tickers_df.to_csv(TICKERS_OUTPUT, index=False)
    print(f"Saved tickers: {tickers_df.shape[0]} rows x {tickers_df.shape[1] - 1} tickers to {TICKERS_OUTPUT}")
    print(f"Date range: {tickers_df['Date'].min().date()} to {tickers_df['Date'].max().date()}")

    print("Downloading SPDR sector ETF daily prices...")
    sectors_df = fetch_sector_etfs()
    print(f"Sector ETFs: {sectors_df.shape[0]} rows x {sectors_df.shape[1] - 1} sectors")

    prices_df = tickers_df.merge(index_df.rename(columns={"sp500": "^GSPC"}), on="Date", how="left")

    print(f"Writing Excel workbook with 3 sheets to {EXCEL_OUTPUT}...")
    with pd.ExcelWriter(EXCEL_OUTPUT, engine="openpyxl") as writer:
        prices_df.to_excel(writer, sheet_name="Prices", index=False)
        sectors_df.to_excel(writer, sheet_name="Sectors", index=False)
        constituents.to_excel(writer, sheet_name="sectors_mapping", index=False)
    print(f"Done. Sheets: 'Prices', 'Sectors' ({len(SECTOR_ETFS)} ETFs), "
          f"'sectors_mapping' ({len(constituents)} tickers)")


if __name__ == "__main__":
    main()
