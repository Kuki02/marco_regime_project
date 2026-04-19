from datetime import datetime

CURRENT_YEAR = datetime.now().year

TREASURY_PAGES = {
    "nominal": f"https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value={CURRENT_YEAR}",
    "tips": f"https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_real_yield_curve&field_tdr_date_value={CURRENT_YEAR}",
}

TARGET_COLUMNS = {
    "nominal": [
        "Date",
        "1 Mo",
        "3 Mo",
        "6 Mo",
        "1 Yr",
        "2 Yr",
        "3 Yr",
        "5 Yr",
        "7 Yr",
        "10 Yr",
        "20 Yr",
        "30 Yr",
    ],
    "tips": [
        "Date",
        "5 YR",
        "7 YR",
        "10 YR",
        "20 YR",
        "30 YR",
    ],
}