import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("djangokit_website", "0003_add_blog_post_model"),
    ]

    operations = [
        migrations.CreateModel(
            name="BlogComment",
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
                ("email", models.EmailField(max_length=254)),
                ("name", models.CharField(max_length=255)),
                ("content", models.TextField()),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "post",
                    models.ForeignKey(
                        to="djangokit_website.blogpost",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="comments",
                    ),
                ),
            ],
            options={
                "db_table": "blog_comment",
            },
        ),
    ]
