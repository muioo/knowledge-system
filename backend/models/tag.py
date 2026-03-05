from tortoise import fields
from tortoise.models import Model


class Tag(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True)
    color = fields.CharField(max_length=7, default="#3498db")
    created_at = fields.DatetimeField(auto_now_add=True)

    # 反向关系 - 只需要类型注解，不需要定义字段
    articles: fields.ManyToManyRelation["Article"]

    class Meta:
        table = "tags"

    def __str__(self):
        return self.name
