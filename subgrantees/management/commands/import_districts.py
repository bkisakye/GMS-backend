import json
from django.core.management.base import BaseCommand
from django.conf import settings
from subgrantees.models import District, Region


class Command(BaseCommand):
    help = "Import districts from JSON file into the database"

    def handle(self, *args, **kwargs):
        json_file_path = settings.BASE_DIR / "districts.json"

        with open(json_file_path, "r") as file:
            data = json.load(file)

        districts_data = data[0]["districts"]
        for district_data in districts_data:
            region_name = district_data["region"]
            region, created = Region.objects.get_or_create(name=region_name)

            District.objects.update_or_create(
                name=district_data["name"],
                defaults={
                    "region": region,
                },
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully imported {district_data["name"]}')
            )
