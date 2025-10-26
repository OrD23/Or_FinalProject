# app/integrations/shodan_async.py
import httpx
import asyncio
from config import SHODAN_API_KEY

API_BASE_URL = "https://api.shodan.io"


async def get_host_info_async(ip: str):
    if SHODAN_API_KEY == "your_shodan_api_key_here":
        raise ValueError("No valid Shodan API key provided. Please set your SHODAN_API_KEY in the .env file.")

    url = f"{API_BASE_URL}/shodan/host/{ip}?key={SHODAN_API_KEY}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


# Example usage of the async function
if __name__ == "__main__":
    ip_to_lookup = "8.8.8.8"
    host_info = asyncio.run(get_host_info_async(ip_to_lookup))
    print(host_info)
