import asyncio

from app.logic.scraper import scraper


async def main():
    with open("scraped_data.csv", "w") as file:
        file.write(await scraper.scrape_all_data())


if __name__ == "__main__":
    asyncio.run(main())
