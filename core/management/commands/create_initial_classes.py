# core/management/commands/create_initial_classes.py
from django.core.management.base import BaseCommand
from core.models import ClassRoom
from datetime import datetime

class Command(BaseCommand):
    help = 'Creates initial classes for the school'

    def handle(self, *args, **kwargs):
        current_year = datetime.now().year
        academic_year = f"{current_year}-{current_year + 1}"
        
        # List of classes to create
        classes = [
            {'name': 'Grade 0', 'section': 'A'},
            {'name': 'Grade 0', 'section': 'B'},
            {'name': 'Grade 1', 'section': 'A'},
            {'name': 'Grade 1', 'section': 'B'},
            {'name': 'Grade 2', 'section': 'A'},
            {'name': 'Grade 2', 'section': 'B'},
            {'name': 'Grade 3', 'section': 'A'},
            {'name': 'Grade 3', 'section': 'B'},
            {'name': 'Grade 4', 'section': 'A'},
            {'name': 'Grade 4', 'section': 'B'},
        ]
        
        for class_info in classes:
            ClassRoom.objects.get_or_create(
                name=class_info['name'],
                section=class_info['section'],
                academic_year=academic_year
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created class {class_info["name"]} - {class_info["section"]}'
                )
            )