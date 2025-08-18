import os
import csv
import json
from pathlib import Path
from django.core.management.base import BaseCommand
from recipes.models import Tag

class Command(BaseCommand):
    help = "Загружает теги из CSV или JSON файла"

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            type=str,
            choices=['csv', 'json', 'auto'],
            default='auto',
            help="Формат файла (csv, json). По умолчанию auto - определение по расширению"
        )
        parser.add_argument(
            '--path',
            type=str,
            default=None,
            help="Путь к файлу данных (если не указан, будет использован стандартный путь)"
        )

    def handle(self, *args, **options):
        file_path = self.get_file_path(options['path'])
        if not file_path:
            self.stderr.write(self.style.ERROR("Файл не найден!"))
            self.stderr.write("Проверьте следующие пути:")
            self.stderr.write("- /app/data/tags.csv (Docker)")
            self.stderr.write("- /app/data/tags.json (Docker)")
            self.stderr.write(f"- {os.path.join(Path(__file__).resolve().parent.parent.parent.parent.parent, 'data', 'tags.csv')} (локально)")
            self.stderr.write(f"- {os.path.join(Path(__file__).resolve().parent.parent.parent.parent.parent, 'data', 'tags.json')} (локально)")
            return

        file_format = options['format']
        if file_format == 'auto':
            if file_path.endswith('.csv'):
                file_format = 'csv'
            elif file_path.endswith('.json'):
                file_format = 'json'
            else:
                self.stderr.write(self.style.ERROR(
                    f"Не удалось определить формат файла: {file_path}. "
                    "Укажите явно с помощью --format csv/json"
                ))
                return
        try:
            if file_format == 'csv':
                self.load_csv(file_path)
            elif file_format == 'json':
                self.load_json(file_path)
            self.stdout.write(self.style.SUCCESS("Теги успешно загружены"))
        except Exception as e:
            self.stderr.write(self.style.ERROR
                              (f"Ошибка при загрузке данных: {str(e)}"))

    def get_file_path(self, user_path=None):
        """Определяет путь к файлу данных"""
        if user_path and os.path.exists(user_path):
            return user_path

        docker_paths = [
            "/app/data/tags.csv",
            "/app/data/tags.json",
            "/usr/src/app/data/tags.csv",
            "/usr/src/app/data/tags.json"
        ]

        base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
        local_paths = [
            os.path.join(base_dir, "data", "tags.csv"),
            os.path.join(base_dir, "data", "tags.json"),
            os.path.join(base_dir, "data", "ingredients", "tags.csv"),
            os.path.join(base_dir, "data", "ingredients", "tags.json")
        ]

        for path in docker_paths + local_paths:
            if os.path.exists(path):
                return path

        return None

    def load_csv(self, file_path):
        """Загрузка данных из CSV файла"""
        created_count = 0
        skipped_count = 0

        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for i, row in enumerate(reader):

                if not row or all(not cell.strip() for cell in row):
                    skipped_count += 1
                    continue

                if len(row) < 2:
                    self.stderr.write(self.style.WARNING(
                        f"Строка {i+1}: не хватает данных (требуется 2 колонки)"
                    ))
                    skipped_count += 1
                    continue
                name, slug = row[0].strip(), row[1].strip()

                if not name or not slug:
                    self.stderr.write(self.style.WARNING(
                        f"Строка {i+1}: пропущено имя или slug"
                    ))
                    skipped_count += 1
                    continue
                _, created = Tag.objects.update_or_create(
                    name=name,
                    defaults={'slug': slug}
                )

                if created:
                    created_count += 1
        self.stdout.write(self.style.SUCCESS(
            f"Обработано строк: {i+1}\n"
            f"Создано тегов: {created_count}\n"
            f"Пропущено: {skipped_count}"
        ))

    def load_json(self, file_path):
        """Загрузка данных из JSON файла"""
        created_count = 0
        skipped_count = 0

        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Ошибка формата JSON: {str(e)}")
            if not isinstance(data, list):
                raise ValueError("JSON должен содержать массив объектов")
            for i, item in enumerate(data):
                if not isinstance(item, dict):
                    self.stderr.write(self.style.WARNING(
                        f"Элемент {i+1}: должен быть объектом, получен {type(item)}"
                    ))
                    skipped_count += 1
                    continue
                name = item.get('name', '').strip()
                slug = item.get('slug', '').strip()
                if not name or not slug:
                    self.stderr.write(self.style.WARNING(
                        f"Элемент {i+1}: пропущено имя или slug"
                    ))
                    skipped_count += 1
                    continue
                _, created = Tag.objects.update_or_create(
                    name=name,
                    defaults={'slug': slug}
                )

                if created:
                    created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Обработано элементов: {len(data)}\n"
            f"Создано тегов: {created_count}\n"
            f"Пропущено: {skipped_count}"
        ))
