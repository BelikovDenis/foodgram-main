import json
import os

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Загрузка ингредиентов из JSON"

    def handle(self, *args, **options):
        base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
        )
        docker_path = "/app/data/ingredients.json"
        local_path = os.path.join(base_dir, "data", "ingredients.json")
        if os.path.exists(docker_path):
            file_path = docker_path
        elif os.path.exists(local_path):
            file_path = local_path
        else:
            self.stderr.write(self.style.ERROR("Файл не найден!"))
            return

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                Ingredient.objects.get_or_create(
                    name=item["name"],
                    measurement_unit=item["measurement_unit"],
                )

        self.stdout.write("Данные успешно загружены")
