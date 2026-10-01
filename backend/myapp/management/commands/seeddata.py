import os
from pathlib import Path

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.storage import storages
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Load example seed data into the database and file storages."

    def handle(self, *args, **options):
        call_command("loaddata", "seeddata")
        self._set_passwords()
        self._load_storage_files("default")
        self._load_storage_files("objectstore")

    def _set_passwords(self):
        """Replace dummy fixture password hashes with real usable passwords."""
        admin_password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "admin")
        accounts = {
            "admin":      admin_password,
            "staff1":     "staff123",
            "spectator1": "spectator123",
        }
        for username, password in accounts.items():
            try:
                u = User.objects.get(username=username)
                u.set_password(password)
                u.save(update_fields=["password"])
                self.stdout.write(f"  Password set for '{username}'.")
            except User.DoesNotExist:
                pass

    def _load_storage_files(self, storage_name: str):
        # Load file using Django Storage API (FileSystemStorage, S3Storage, etc)
        storage = storages[storage_name]
        source_dir = Path(__file__).resolve().parent.parent.parent / "fixtures" / "storages" / storage_name
        count = 0
        for file_path in source_dir.rglob("*"):
            if not file_path.is_file() or file_path.name == '.gitkeep':
                continue
            relative = file_path.relative_to(source_dir)
            storage_path = relative.as_posix()
            if storage.exists(storage_path):
                storage.delete(storage_path)
            storage.save(storage_path, ContentFile(file_path.read_bytes()))
            count += 1
        self.stdout.write(f"Loaded {count} files into storage '{storage_name}'.")
