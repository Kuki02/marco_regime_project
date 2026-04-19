from pathlib import Path
import pandas as pd

FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=FEDFUNDS"
OUTPUT_PATH = Path("data/raw/fed_rates/fed_funds_rate.csv")


def fetch_fed_funds_rate() -> pd.DataFrame:
    df = pd.read_csv(FRED_URL)
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
