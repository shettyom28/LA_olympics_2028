from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_alter_event_start_time_message'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='random_number',
        ),
        migrations.AddField(
            model_name='message',
            name='bot_response',
            field=models.TextField(blank=True, null=True),
        ),
    ]
