from pathlib import Path
import time
import pandas as pd
import requests

FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=FEDFUNDS"
OUTPUT_PATH = Path("data/raw/fed_rates/fed_funds_rate.csv")
TIMEOUT = 30
MAX_RETRIES = 3


def fetch_fed_funds_rate() -> pd.DataFrame:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(FRED_URL, timeout=TIMEOUT)
            response.raise_for_status()
            break
        except Exception as e:
            if attempt == MAX_RETRIES:
                raise RuntimeError(f"Failed to fetch FRED data after {MAX_RETRIES} attempts: {e}") from e
            print(f"Attempt {attempt} failed: {e}. Retrying...")
            time.sleep(2 ** attempt)

    from io import StringIO
    df = pd.read_csv(StringIO(response.text))
    df.columns = ["Date", "fed_funds_rate"]
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["fed_funds_rate"] = pd.to_numeric(df["fed_funds_rate"], errors="coerce")
    df = df.dropna()
    df = df.sort_values("Date").reset_index(drop=True)
    return df


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    print("Downloading Fed Funds Rate from FRED...")
    df = fetch_fed_funds_rate()

    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(df)} rows to {OUTPUT_PATH}")
    print(f"Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")


if __name__ == "__main__":
    main()
