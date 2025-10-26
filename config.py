# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch API keys with default placeholders.
SHODAN_API_KEY = os.getenv("SHODAN_API_KEY", "your_shodan_api_key_here")
DNSDUMPSTER_API_KEY = os.getenv("DNSDUMPSTER_API_KEY", "your_dnsdumpster_api_key_here")
ONYPHE_API_KEY = os.getenv("ONYPHE_API_KEY", "your_onyphe_api_key_here")
NVD_API_KEY = os.getenv("NVD_API_KEY", "your_nvd_api_key_here")
# For demonstration, print which keys have been set (you might want to log this differently in production)
# print(f"Shodan API Key: {SHODAN_API_KEY}")
# print(f"DNSDumpster API Key: {DNSDUMPSTER_API_KEY}")
# print(f"Onyphe API Key: {ONYPHE_API_KEY}")
# print(f"NVD API Key: {NVD_API_KEY}")
