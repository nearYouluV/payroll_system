# Generated by Django 5.1.2 on 2024-12-01 19:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0005_alter_payouthistory_unique_together'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PayoutHistory',
        ),
    ]