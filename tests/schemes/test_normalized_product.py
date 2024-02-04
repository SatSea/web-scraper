import unittest

from app.schemes.normalized_product import NormalizedProduct


class TestNormalizedProduct(unittest.TestCase):
    def setUp(self):
        self.product = NormalizedProduct(
            link="http://example.com/product",
            name="Test Product",
            price={"amount": 19.99, "currency": "USD"},
            user_rating=4.5,
            description="This is a test\nproduct.<br>Enjoy it!",
            instructions="Use with care.<Br/>Follow the manual.",
            country_of_origin="Made in Wonderland",
        )

    def test_initialization(self):
        self.assertEqual(self.product.link, "http://example.com/product")
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.price, {"amount": 19.99, "currency": "USD"})
        self.assertEqual(self.product.user_rating, 4.5)
        self.assertEqual(self.product.description, "This is a test product. Enjoy it!")
        self.assertEqual(self.product.instructions, "Use with care. Follow the manual.")
        self.assertEqual(self.product.country_of_origin, "Made in Wonderland")

    def test_normalize_text(self):
        self.assertIsNone(NormalizedProduct.normalize_text(None))
        self.assertEqual(
            NormalizedProduct.normalize_text("Test\nText<Br><br/><Br/>"), "Test Text   "
        )

    def test_get_csv(self):
        expected_csv = (
            '"http://example.com/product","Test Product","19.99USD","4.5",'
            '"This is a test product. Enjoy it!","Use with care. Follow the manual.",'
            '"Made in Wonderland"\r\n'
        )
        self.assertEqual(self.product.get_csv(), expected_csv)


if __name__ == "__main__":
    unittest.main()
