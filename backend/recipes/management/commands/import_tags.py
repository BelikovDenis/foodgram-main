import csv
import os

from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = "Загружаем тэги из csv."

    def handle(self, *args, **options):
        base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
        )
        docker_path = "/app/data/tags.csv"
        local_path = os.path.join(base_dir, "data", "tags.csv")
        if os.path.exists(docker_path):
            file_path = docker_path
        elif os.path.exists(local_path):
            file_path = local_path
        else:
            self.stderr.write(self.style.ERROR("Файл не найден!"))
            return

        with open(file_path, encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                name, slug = row
                Tag.objects.get_or_create(name=name.strip(), slug=slug.strip())
        self.stdout.write(self.style.SUCCESS("Теги загружены, мой господин."))
