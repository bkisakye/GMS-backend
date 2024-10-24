import json
from django.core.management.base import BaseCommand
from django.conf import settings
from subgrantees.models import Bank
from pathlib import Path


class Command(BaseCommand):
    help = "Import banks from JSON file into the database"

    def handle(self, *args, **kwargs):
        json_file_path = Path(settings.BASE_DIR) / "banks.json"

        try:
            with open(json_file_path, 'r') as file:
                data = json.load(file)
                banks_data = data.get('banks', [])

            # Check the structure of banks_data
            print(banks_data)  # For debugging

            for bank_data in banks_data:
                bank, created = Bank.objects.get_or_create(
                    name=bank_data['name'],
                    defaults={
                        'head_office': bank_data['head_office'],
                        'website': bank_data['website'],
                        'year_of_establishment': bank_data['year_of_establishment'],
                        'contact_info': bank_data['contact_info']
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(
                        f'Successfully imported {bank.name}'))
                else:
                    self.stdout.write(self.style.WARNING(
                        f'{bank.name} already exists in the database'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(
                f'File not found: {json_file_path}'))
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR(
                'Error decoding JSON from the file.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'An unexpected error occurred: {str(e)}'))
