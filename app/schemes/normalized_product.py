import csv
from io import StringIO


class NormalizedProduct:
    def __init__(
        self,
        link,
        name,
        price,
        user_rating,
        description,
        instructions,
        country_of_origin,
    ):
        self.link = link
        self.name = name
        self.price = price
        self.user_rating = user_rating
        self.description = self.normalize_text(description)
        self.instructions = self.normalize_text(instructions)
        self.country_of_origin = self.normalize_text(country_of_origin)

    @staticmethod
    def normalize_text(text):
        if text is None:
            return
        replacements = {
            "\n": " ",
            "\r": " ",
            "<br>": " ",
            "<Br>": " ",
            "<br/>": " ",
            "<Br/>": " ",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text

    def get_csv(self) -> str:
        output = StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_ALL)
        writer.writerow(
            [
                self.link,
                self.name,
                f"{self.price['amount']}{self.price['currency']}",
                self.user_rating,
                self.description,
                self.instructions,
                self.country_of_origin,
            ]
        )

        csv_string = output.getvalue()
        output.close()
        return csv_string
