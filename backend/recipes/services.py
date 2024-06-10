import csv
import json
import uuid

from django.http import HttpResponse


def is_valid_uuid(value):
    """Check if uuid is valid in url."""
    try:
        uuid.UUID(str(value))
        return value
    except ValueError:
        return False


def write_ingredients_to_csv(ingredients):
    """Write ingredients to scv when downloading."""
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition":
                     'attachment; filename="my-shopping-cart.csv"'},
    )
    headers = ['Ингредиенты', 'Единица измерения', 'Кол-во']
    writer_headers = csv.writer(response)
    writer_headers.writerow(headers)
    writer = csv.DictWriter(response, fieldnames=ingredients[0].keys())
    writer.writerows(ingredients)
    return response


def load_json_ingredients(json_data_file):
    """Load json data."""
    with open(json_data_file) as json_file:

        file = json.load(json_file)
        data = [
            {'model': 'recipes.ingredient', 'pk': pk + 1,
             'fields': {
                 'name': instance.get('name'),
                 'measurement_unit': instance.get('measurement_unit')}
             }
            for pk, instance in enumerate(file)
        ]
        output_json = open('ingredients_test_1.json', 'w', encoding='utf-8')
        json.dump(data, output_json, ensure_ascii=False, indent=4)
