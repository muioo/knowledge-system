from tortoise import fields
from tortoise.models import Model


class Tag(Model):
    """支持任意层级父子关系的文章标签。"""

    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True)
    color = fields.CharField(max_length=7, default="#3498db")
    parent = fields.ForeignKeyField(
        "models.Tag",
        related_name="children",
        null=True,
        on_delete=fields.RESTRICT,
    )
    created_at = fields.DatetimeField(auto_now_add=True)

    # 反向文章关系由 Article.tags 的 related_name 提供。
    articles: fields.ManyToManyRelation["Article"]

    class Meta:
        table = "tags"

    def __str__(self):
        """返回用于日志和调试的标签名称。"""
        return self.name
