# Generated by Django 4.1 on 2022-11-10 07:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="Company",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("isin", models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name="Industry",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Market",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Stock",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("symbol", models.CharField(max_length=15)),
                ("group", models.CharField(blank=True, default="", max_length=5)),
                ("face_value", models.DecimalField(decimal_places=4, max_digits=10)),
                ("sid", models.BigIntegerField(default=None, null=True)),
                ("object_id", models.PositiveIntegerField(default=None, null=True)),
                (
                    "content_type",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "market",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="stocks.market",
                        to_field="name",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Listing",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateTimeField()),
                ("open", models.DecimalField(decimal_places=5, max_digits=11)),
                ("high", models.DecimalField(decimal_places=5, max_digits=11)),
                ("low", models.DecimalField(decimal_places=5, max_digits=11)),
                ("close", models.DecimalField(decimal_places=5, max_digits=11)),
                ("traded", models.BigIntegerField(null=True)),
                ("trades", models.BigIntegerField(null=True)),
                ("deliverable", models.BigIntegerField(null=True)),
                (
                    "stock",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="stocks.stock"
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="company",
            index=models.Index(fields=["name"], name="company_idx"),
        ),
        migrations.AddIndex(
            model_name="company",
            index=models.Index(fields=["isin"], name="isin_idx"),
        ),
        migrations.AddIndex(
            model_name="stock",
            index=models.Index(fields=["symbol"], name="security_idx"),
        ),
        migrations.AddIndex(
            model_name="stock",
            index=models.Index(fields=["sid"], name="sid_idx"),
        ),
        migrations.AddIndex(
            model_name="stock",
            index=models.Index(
                fields=["content_type", "object_id"],
                name="stocks_stoc_content_a61c7c_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="listing",
            index=models.Index(fields=["date"], name="date_idx"),
        ),
    ]
