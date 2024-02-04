import math
from asyncio import Semaphore
from json import dump, loads
from typing import Dict

from app.logic.fetcher import fetch_json, multi_fetch_json
from app.schemes import NormalizedProduct


class scraper:
    @staticmethod
    async def getAllProducts(url: str, city_id: str) -> list[Dict[str, any]]:
        items = []
        try:
            with open("items.json", "r") as file:
                content = file.read()
                if not content:
                    raise ValueError("File is empty")
                items = loads(content)
        except (FileNotFoundError, ValueError):
            print("File is empty or not found, so downloading")
            response = await fetch_json(
                url,
                {
                    "categoryId": 1000000007,
                    "cityId": city_id,
                    "cityDistrict": None,
                    "pageNumber": 1,
                    "filters": [],
                },
            )
            total_pages = math.ceil(response["data"]["count"] / 24)
            for page in range(1, total_pages + 1):
                print(f"Trying to get page {page}")
                response = await fetch_json(
                    url,
                    {
                        "categoryId": 1000000007,
                        "cityId": city_id,
                        "cityDistrict": None,
                        "pageNumber": page,
                        "filters": [],
                    },
                )
                items.extend(response["data"]["products"])

            with open("items.json", "w") as write_file:
                dump(items, write_file)

        try:
            with open("products.json", "r") as file:
                content = file.read()
                if not content:
                    raise ValueError("File is empty")
                products = loads(content)
        except (FileNotFoundError, ValueError):
            semaphore = Semaphore(500)
            fetched = await multi_fetch_json(
                "https://goldapple.ru/front/api/catalog/product-card", items, semaphore
            )
            products = [response["data"] for response in fetched]
            with open("products.json", "w") as write_file:
                dump(products, write_file)

        return products

    @staticmethod
    async def getProductsInfo(products: list) -> list[NormalizedProduct]:
        items = []
        for product in products:
            link = product["url"]
            name = product["name"]
            price = product["variants"][0]["price"]["regular"]
            user_rating = (
                None  # because in goldapple there is no user ratings, so it none
            )
            description = product["productDescription"][0]["content"]
            if len(product["productDescription"]) == 3:
                instructions = product["productDescription"][1]["content"]
                country_of_origin = product["productDescription"][2]["content"]
            else:
                instructions = None
                country_of_origin = product["productDescription"][1]["content"]
            items.append(
                NormalizedProduct(
                    link,
                    name,
                    price,
                    user_rating,
                    description,
                    instructions,
                    country_of_origin,
                )
            )
        return items

    @staticmethod
    async def scrape_all_data() -> str:
        raw_products = await scraper.getAllProducts(
            "https://goldapple.ru/front/api/catalog/products",
            "dd8caeab-c685-4f2a-bf5f-550aca1bbc48",
        )
        products = [
            product.get_csv() for product in await scraper.getProductsInfo(raw_products)
        ]
        products.insert(
            0,
            "link,name,price,user_rating,description,instructions,country_of_origin\n",
        )
        return "".join(products)
