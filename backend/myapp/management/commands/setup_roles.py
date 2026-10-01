from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
# Importing your models to assign specific permissions
from myapp.models import Result, Event

class Command(BaseCommand):
    help = 'Create initial groups and permissions for the Olympics site'

    def handle(self, *args, **kwargs):
        # 1. Create the Groups
        staff_group, _ = Group.objects.get_or_create(name='Staff')
        athlete_group, _ = Group.objects.get_or_create(name='Athlete')
        spectator_group, _ = Group.objects.get_or_create(name='Spectator')

        # 2. Assign Permissions to Staff
        # Staff should be able to add/change/delete Results and Events
        result_ct = ContentType.objects.get_for_model(Result)
        event_ct = ContentType.objects.get_for_model(Event)
        
        staff_perms = Permission.objects.filter(content_type__in=[result_ct, event_ct])
        staff_group.permissions.set(staff_perms)

        self.stdout.write(self.style.SUCCESS('Successfully configured Roles and Groups'))