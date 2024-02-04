import unittest
from unittest.mock import patch, mock_open, MagicMock
import asyncio
from app.logic.scraper import scraper  
from app.schemes import NormalizedProduct

class TestScraper(unittest.IsolatedAsyncioTestCase):
    async def test_getAllProducts_with_existing_file(self):
        
        mock_content = '[{"id": 1, "name": "Product 1"}]'
        with patch("builtins.open", mock_open(read_data=mock_content)), \
             patch("json.loads", return_value=[{"id": 1, "name": "Product 1"}]):
            products = await scraper.getAllProducts("dummy_url", "dummy_city_id")
            self.assertEqual(len(products), 1)
            self.assertEqual(products[0]["name"], "Product 1")

    async def test_getAllProducts_fetch_and_save(self):
        
        with patch("app.logic.fetcher.fetch_json", side_effect=[
            asyncio.Future(),  
            asyncio.Future(),  
        ]) as mock_fetch, patch("builtins.open", mock_open()) as mocked_file:
            
            mock_fetch.side_effect[0].set_result({"data": {"count": 24}})  
            mock_fetch.side_effect[1].set_result({"data": {"products": [{"id": 2, "name": "Product 2"}]}})  

            products = await scraper.getAllProducts("dummy_url", "dummy_city_id")
            self.assertEqual(len(products), 1)
            self.assertEqual(products[0]["name"], "Product 2")
            mocked_file.assert_called_with("items.json", "w")  

    async def test_getProductsInfo(self):
        products = [
            {
                "url": "http://example.com/product",
                "name": "Test Product",
                "variants": [{"price": {"regular": {"amount": 100, "currency": "USD"}}}],
                "productDescription": [{"content": "Description"}, {"content": "Instructions"}, {"content": "Country"}]
            }
        ]
        normalized_products = await scraper.getProductsInfo(products)
        self.assertEqual(len(normalized_products), 1)
        self.assertIsInstance(normalized_products[0], NormalizedProduct)
        self.assertEqual(normalized_products[0].name, "Test Product")

    async def test_scrape_all_data_integration(self):
        
        with patch("app.logic.scraper.scraper.getAllProducts", return_value=asyncio.Future()) as mock_getAllProducts, \
             patch("app.logic.scraper.scraper.getProductsInfo", return_value=asyncio.Future()) as mock_getProductsInfo:
            mock_getAllProducts.return_value.set_result([{"url": "http://example.com/product", "name": "Product"}])
            mock_getProductsInfo.return_value.set_result([NormalizedProduct(
                "http://example.com/product",
                "Product",
                {"amount": 100, "currency": "USD"},
                None,
                "Description",
                "Instructions",
                "Country"
            )])

            csv_output = await scraper.scrape_all_data()
            expected_header = "link,name,price,user_rating,description,instructions,country_of_origin\n"
            expected_data = '"http://example.com/product","Product","100USD",,"Description","Instructions","Country"\n'
            self.assertIn(expected_header, csv_output)
            self.assertIn(expected_data, csv_output)

if __name__ == "__main__":
    unittest.main()
