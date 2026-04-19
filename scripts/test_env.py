import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("FRED_API_KEY")

if api_key:
    print("API key loaded:", api_key[:5] + "...")
else:
    print("API key NOT found")