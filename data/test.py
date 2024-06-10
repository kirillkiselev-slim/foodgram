import json


with open('ingredients.json') as json_file:
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
