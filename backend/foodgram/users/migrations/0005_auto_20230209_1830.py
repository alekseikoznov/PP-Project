# Generated by Django 2.2.19 on 2023-02-09 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20230208_2240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='favorite',
            field=models.ManyToManyField(blank=True, related_name='user_favorite', to='recipes.Recipe'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='shopping_cart',
            field=models.ManyToManyField(blank=True, related_name='user_shopping_cart', to='recipes.Recipe'),
        ),
    ]