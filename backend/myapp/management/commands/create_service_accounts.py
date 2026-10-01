import os

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.db import transaction
from rest_framework.authtoken.models import Token

SERVICE_ACCOUNTS = [
    ('SERVICE_API_TOKEN', 'api-service-bot', ['system-service-accounts']),
]


class Command(BaseCommand):
    help = (
        "Create internal API service-account users from"
        "environment variables (e.g. secrets loaded from Kubernetes). "
    )

    def handle(self, *args, **options):
        for env_var, username, group_names in SERVICE_ACCOUNTS:
            token_key = os.environ.get(env_var)
            if not token_key:
                self.stdout.write(f"${env_var} not set — skipping {username}")
                continue

            with transaction.atomic():
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={'is_active': True},
                )
                if created:
                    user.set_unusable_password()
                    user.save()

                for group_name in group_names:
                    group, _ = Group.objects.get_or_create(name=group_name)
                    user.groups.add(group)

                try:
                    token = Token.objects.get(user=user)
                except Token.DoesNotExist:
                    token = Token(user=user)
                token.key = token_key
                token.save()

            self.stdout.write(self.style.SUCCESS(
                f"{username} {group_names}: token configured from ${env_var}"
            ))
