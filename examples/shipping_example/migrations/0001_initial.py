# Generated by Django 2.1.14 on 2019-11-26 21:06

from django.db import migrations, models
import django.db.models.deletion
import river.models.fields.state


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('river', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shipping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.CharField(blank=True, max_length=50, null=True)),
                ('customer', models.CharField(blank=True, max_length=50, null=True)),
                ('shipping_status', river.models.fields.state.StateField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='river.State')),
            ],
        ),
    ]
