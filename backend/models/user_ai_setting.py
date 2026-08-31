from tortoise import fields
from tortoise.models import Model


class UserAiSetting(Model):
    """用户级 AI 提取配置：每个用户可为每个供应商绑定一个常用模型。"""

    id = fields.IntField(pk=True)
    # 所属用户，删除用户时级联删除其配置
    user = fields.ForeignKeyField("models.User", on_delete=fields.CASCADE, related_name="ai_settings")
    # 供应商标识：zhipu / dashscope / custom
    provider = fields.CharField(max_length=20)
    # 用户录入的模型名称，例如 deepseek-v4-flash-0731
    model = fields.CharField(max_length=100)
    # 用户自行录入的 API Key 密文（encrypt_secret 产出）；为空表示未设置，走服务端环境变量
    api_key = fields.CharField(max_length=512, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "user_ai_settings"
        # 同一用户同一供应商只保留一条配置
        unique_together = (("user", "provider"),)

    def __str__(self):
        return f"{self.user_id}:{self.provider}={self.model}"
