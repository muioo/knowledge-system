from tortoise import fields
from tortoise.models import Model


class Article(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    original_filename = fields.CharField(max_length=255, null=True)
    source_url = fields.CharField(max_length=1000, null=True)
    summary = fields.TextField(null=True)
    keywords = fields.CharField(max_length=500, null=True)
    author = fields.ForeignKeyField("models.User", related_name="articles", on_delete=fields.CASCADE)
    view_count = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    html_path = fields.CharField(max_length=500, null=True)
    processing_status = fields.CharField(max_length=20, default="pending")  # pending/processing/completed/failed
    original_html_url = fields.CharField(max_length=1000, null=True)

    tags: fields.ManyToManyRelation["Tag"] = fields.ManyToManyField(
        "models.Tag", related_name="articles", through="article_tags"
    )

    class Meta:
        table = "articles"

    def __str__(self):
        return self.title
