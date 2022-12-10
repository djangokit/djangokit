import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("djangokit_website", "0002_add_todo_item_model"),
    ]

    operations = [
        migrations.CreateModel(
            name="BlogPost",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("slug", models.SlugField(max_length=255)),
                (
                    "author",
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL,
                        on_delete=django.db.models.deletion.PROTECT,
                    ),
                ),
                ("lead", models.TextField(blank=True, null=True)),
                ("content", models.TextField()),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("published", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "db_table": "blog_post",
            },
        ),
    ]
