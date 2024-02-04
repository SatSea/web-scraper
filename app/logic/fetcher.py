from asyncio import Semaphore
from typing import Dict, List

from aiohttp import ClientSession

# cookie footprint from my browser, may not work later
headers = {
    "authority": "goldapple.ru",
    "accept": "application/json, text/plain, */*",
    "accept-language": "ru",
    "content-type": "application/json",
    "cookie": "PHPSESSID=2a10e403a62d8bbe4c7a19fa8a559630; ga-lang=ru; client-store-code=default; mage-cache-sessid=true; digi-analytics-sessionId=-m4KKGyBTeTyaJGStfqiD; advcake_track_id=92800eb5-6d29-8a4c-eb39-91949f89d5b1; advcake_session_id=03f76c6e-922b-d25c-9eff-bf3dd2bef475; mindboxDeviceUUID=0d57423a-109f-40a9-95a8-c2d24eaab013; directCrm-session=%7B%22deviceGuid%22%3A%220d57423a-109f-40a9-95a8-c2d24eaab013%22%7D; section_data_ids=%7B%22geolocation%22%3A1707025304%2C%22adult_goods%22%3A1707025305%2C%22cart%22%3A1707025306%7D",
    "origin": "https://goldapple.ru",
    "referer": "https://goldapple.ru/parfjumerija",
    "sec-ch-ua": '"Not A(Brand";v="99", "Microsoft Edge";v="121", "Chromium";v="121"',
    "traceparent": "00-46da821c9a8a705498894da3e8641266-219287fe6e078638-01",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
}


async def fetch_json(url: str, payload: Dict[str, str]) -> any:
    async with ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            return await response.json()


async def multi_fetch_json(
    url: str, items_page: List[Dict[str, str]], semaphore: Semaphore
) -> List[Dict]:
    result = []
    i = 0
    async with ClientSession() as session:
        for items_page in items_page:
            for item in items_page:
                id = i
                i += 1
                print(f"Starting getting item {id}")
                task_url = f"{url}?itemId={item['itemId']}&cityId=dd8caeab-c685-4f2a-bf5f-550aca1bbc48&customerGroupId=0"

                async with semaphore:
                    async with session.get(task_url, headers=headers) as response:
                        product = await response.json()
                        product["data"]["url"] = item["url"]
                        result.append(product)
                        print(
                            f"Got item {product['data']['name']} ({product['data']['type']}) with id {id} with status code {response.status}"
                        )
    return result
