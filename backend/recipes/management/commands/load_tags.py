from django.core.management.base import BaseCommand
from recipes.models import Tag


class Command(BaseCommand):
    help = "Load tags into the database"

    def handle(self, *args, **options):
        try:
            self.create_tags()
            self.stdout.write(self.style.SUCCESS(
                'Теги успешно созданы и загружены'))
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'Произошла ошибка: {e}'))

    def create_tags(self):
        tags_to_create = [
            {'name': 'Завтрак', 'color': '#E26C2D', 'slug': 'breakfast'},
            {'name': 'Обед', 'color': '#008000', 'slug': 'lunch'},
            {'name': 'Ужин', 'color': '#8B00FF', 'slug': 'dinner'}]

        for tag_data in tags_to_create:
            Tag.objects.get_or_create(**tag_data)
