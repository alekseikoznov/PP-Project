# Generated by Django 2.2.19 on 2023-02-08 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_auto_20230205_2241'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(default=1, upload_to='recipe/images/'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(through='recipes.Ingredientrecipe', to='recipes.Ingredient'),
        ),
    ]
