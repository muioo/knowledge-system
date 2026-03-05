from tortoise import fields
from tortoise.models import Model


class ReadingHistory(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="reading_histories", on_delete=fields.CASCADE)
    article = fields.ForeignKeyField("models.Article", related_name="reading_histories", on_delete=fields.CASCADE)
    started_at = fields.DatetimeField()
    ended_at = fields.DatetimeField(null=True)
    reading_duration = fields.IntField(default=0)  # 秒
    reading_progress = fields.IntField(default=0)  # 0-100

    class Meta:
        table = "reading_history"

    def __str__(self):
        return f"{self.user_id} - {self.article_id}"


class ReadingStats(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="reading_stats", on_delete=fields.CASCADE)
    article = fields.ForeignKeyField("models.Article", related_name="reading_stats", on_delete=fields.CASCADE)
    total_views = fields.IntField(default=1)
    total_duration = fields.IntField(default=0)  # 秒
    last_read_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "reading_stats"
        unique_together = (("user", "article"),)

    def __str__(self):
        return f"{self.user_id} - {self.article_id} stats"
