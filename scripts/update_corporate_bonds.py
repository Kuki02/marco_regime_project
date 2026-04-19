from pathlib import Path
import pandas as pd
import yfinance as yf

from config.corporate_bonds import FRED_SERIES, ETF_TICKERS


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "corporate_bonds"
OUTPUT_FILE = DATA_DIR / "corporate_bonds.xlsx"
SHEET_NAME = "daily"


def ensure_folder():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def download_single_fred_series(series_code, start="2000-01-01"):
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_code}"

    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.upper()

    if "DATE" in df.columns:
        date_col = "DATE"
    elif "OBSERVATION_DATE" in df.columns:
        date_col = "OBSERVATION_DATE"
    else:
        raise ValueError(
            f"No date column found for {series_code}. Columns: {list(df.columns)}"
        )

    series_col = series_code.upper()
    if series_col not in df.columns:
        raise ValueError(
            f"No {series_col} column found for {series_code}. Columns: {list(df.columns)}"
        )

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df[series_col] = pd.to_numeric(df[series_col], errors="coerce")

    df = df.rename(columns={date_col: "Date", series_col: series_code})
    df = df.dropna(subset=["Date"])
    df = df.set_index("Date")
    df = df[df.index >= pd.to_datetime(start)]

    return df[[series_code]]


def download_fred_series(start="2000-01-01"):
    frames = []

    for name, series_code in FRED_SERIES.items():
        s = download_single_fred_series(series_code, start=start)
        s = s.rename(columns={series_code: name})
        frames.append(s)

    if not frames:
        return pd.DataFrame()

    df = pd.concat(frames, axis=1)
    df.index = pd.to_datetime(df.index)
    return df


def download_etfs(start="2000-01-01"):
    data = yf.download(
        ETF_TICKERS,
        start=start,
        auto_adjust=False,
        progress=False,
        group_by="column",
    )

    if data.empty:
        return pd.DataFrame()

    if isinstance(data.columns, pd.MultiIndex):
        level0 = list(data.columns.get_level_values(0))

        if "Adj Close" in level0:
            etf = data["Adj Close"].copy()
        elif "Close" in level0:
            etf = data["Close"].copy()
        else:
            raise ValueError(
                f"Could not find 'Adj Close' or 'Close' in Yahoo output. Columns: {data.columns}"
            )
    else:
        if "Adj Close" in data.columns:
            etf = data[["Adj Close"]].copy()
            if len(ETF_TICKERS) == 1:
                etf.columns = ETF_TICKERS
            else:
                raise ValueError("Yahoo returned flat columns unexpectedly for multiple tickers.")
        elif "Close" in data.columns:
            etf = data[["Close"]].copy()
            if len(ETF_TICKERS) == 1:
                etf.columns = ETF_TICKERS
            else:
                raise ValueError("Yahoo returned flat columns unexpectedly for multiple tickers.")
        else:
            raise ValueError(
                f"Could not find 'Adj Close' or 'Close' in Yahoo output. Columns: {data.columns}"
            )

    etf.columns.name = None
    etf.index = pd.to_datetime(etf.index)

    for ticker in ETF_TICKERS:
        if ticker not in etf.columns:
            etf[ticker] = pd.NA

    etf = etf[ETF_TICKERS]
    return etf


def load_existing_data():
    if not OUTPUT_FILE.exists():
        return pd.DataFrame()

    try:
        df = pd.read_excel(OUTPUT_FILE, sheet_name=SHEET_NAME)

        if df.empty:
            return pd.DataFrame()

        if "Date" not in df.columns:
            raise ValueError("Existing Excel file does not contain a 'Date' column.")

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])
        df = df.set_index("Date")
        df = df.sort_index()
        return df

    except Exception as e:
        print(f"Warning: could not load existing data from {OUTPUT_FILE}: {e}")
        return pd.DataFrame()


def merge_new_and_existing(existing_df, new_df):
    combined = pd.concat([existing_df, new_df], axis=0)
    combined = combined[~combined.index.duplicated(keep="last")]
    combined = combined.sort_index()
    return combined


def main():
    ensure_folder()

    existing_df = load_existing_data()

    if not existing_df.empty:
        last_date = existing_df.index.max()
        start_date = (last_date - pd.Timedelta(days=10)).strftime("%Y-%m-%d")
    else:
        start_date = "2000-01-01"

    fred_df = download_fred_series(start=start_date)
    etf_df = download_etfs(start=start_date)

    new_df = fred_df.join(etf_df, how="outer")
    new_df.index.name = "Date"

    combined = merge_new_and_existing(existing_df, new_df)
    combined = combined.reset_index()

    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        combined.to_excel(writer, sheet_name=SHEET_NAME, index=False)

    print(f"Saved {len(combined)} rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()