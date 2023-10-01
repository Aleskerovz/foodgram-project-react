import csv

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Load ingredients from CSV to DB"

    def handle(self, *args, **options):
        csv_file_path = f'{settings.BASE_DIR}/data/ingredients.csv'
        with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            ingredients_to_create = []
            for row in csv_reader:
                ingredient = Ingredient(
                    name=row['name'],
                    measurement_unit=row['measurement_unit'])
                ingredients_to_create.append(ingredient)

            if ingredients_to_create:
                Ingredient.objects.bulk_create(ingredients_to_create)
                self.stdout.write(self.style.SUCCESS(
                    'Ингредиенты успешно загружены'))
            else:
                self.stdout.write(self.style.SUCCESS(
                    'CSV файл не содержит данных для загрузки'))
