from django.core.management.base import BaseCommand

from recipes.models import Recipe


class Command(BaseCommand):
    help = 'Generate short links for existing recipes'

    def handle(self, *args, **options):
        for recipe in Recipe.objects.filter(short_link__isnull=True):
            recipe.save()
            self.stdout.write(
                f'Generated short link for {recipe.name}: {recipe.short_link}'
            )
