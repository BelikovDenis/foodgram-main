import csv
import os

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Загружает ингредиенты из CSV"

    def handle(self, *args, **options):
        base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
        )
        docker_path = "/app/data/ingredients.csv"
        local_path = os.path.join(base_dir, "data", "ingredients.csv")
        if os.path.exists(docker_path):
            file_path = docker_path
        elif os.path.exists(local_path):
            file_path = local_path
        else:
            self.stderr.write(self.style.ERROR("Файл не найден!"))
            return

        with open(file_path, encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)
            count = 0
            for row in reader:
                name, unit = row
                _, created = Ingredient.objects.get_or_create(
                    name=name.strip(), measurement_unit=unit.strip()
                )
                count += int(created)
        self.stdout.write(
            self.style.SUCCESS(f"Загружено ингредиентов: {count}")
        )
