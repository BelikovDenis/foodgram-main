import csv
import os
from pathlib import Path

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Загружает ингредиенты из CSV"

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            default=None,
            help="Путь к файлу данных"
        )

    def handle(self, *args, **options):
        file_path = self.get_file_path(options['path'])
        if not file_path:
            self.stderr.write(self.style.ERROR("Файл не найден!"))
            self.stderr.write("Проверьте следующие пути:")
            self.stderr.write("- /app/data/ingredients.csv (Docker)")
            base_dir = Path(__file__).resolve().parents[4]
            local_example = os.path.join(
                base_dir, "data", "ingredients.csv"
            )
            self.stderr.write(f"- {local_example} (локально)")
            return

        with open(file_path, encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)
            count = 0
            for row in reader:
                name, unit = row
                _, created = Ingredient.objects.get_or_create(
                    name=name.strip(),
                    measurement_unit=unit.strip()
                )
                count += int(created)
        self.stdout.write(
            self.style.SUCCESS(f"Загружено ингредиентов: {count}")
        )

    def get_file_path(self, user_path=None):
        """Определяет путь к файлу данных"""
        if user_path and os.path.exists(user_path):
            return user_path

        docker_paths = [
            "/app/data/ingredients.csv",
            "/app/recipes/data/ingredients.csv",
            "/usr/src/app/data/ingredients.csv"
        ]

        base_dir = Path(__file__).resolve().parents[4]
        local_paths = [
            os.path.join(base_dir, "data", "ingredients.csv"),
            os.path.join(base_dir, "recipes", "data", "ingredients.csv")
        ]

        for path in docker_paths + local_paths:
            if os.path.exists(path):
                return path

        return None
