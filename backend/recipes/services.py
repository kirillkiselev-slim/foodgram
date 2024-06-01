import csv
import uuid

from django.http import HttpResponse


def is_valid_uuid(value):
    try:
        uuid.UUID(str(value))
        return value
    except ValueError:
        return


def write_ingredients_to_csv(ingredients):
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition":
                     'attachment; filename="my-shopping-cart.csv"'},
    )
    writer = csv.DictWriter(response, fieldnames=ingredients[0].keys())
    writer.writerows(ingredients)
    return response
