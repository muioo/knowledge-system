from tortoise import fields
from tortoise.models import Model


class ReadingHistory(Model):
    """
    阅读历史记录表
    记录用户每次阅读文章的详细信息
    """
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="reading_histories", on_delete=fields.CASCADE)
    article = fields.ForeignKeyField("models.Article", related_name="reading_histories", on_delete=fields.CASCADE)

    # 阅读时间信息
    started_at = fields.DatetimeField(description="开始阅读时间")
    ended_at = fields.DatetimeField(null=True, description="结束阅读时间")
    reading_duration = fields.IntField(default=0, description="阅读时长（秒）")
    reading_progress = fields.IntField(default=0, description="阅读进度（0-100）")

    # 阅读会话信息（支持暂停/继续功能）
    session_id = fields.CharField(max_length=100, null=True, description="阅读会话ID，用于关联同一次阅读的多次暂停/继续")
    is_completed = fields.BooleanField(default=False, description="是否已完成阅读（进度>=100%）")

    # 设备信息
    device_type = fields.CharField(max_length=50, null=True, description="设备类型（desktop/mobile/tablet）")
    ip_address = fields.CharField(max_length=50, null=True, description="IP地址")

    # 创建时间
    created_at = fields.DatetimeField(auto_now_add=True, description="记录创建时间")

    class Meta:
        table = "reading_history"
        # 添加索引以优化查询性能
        indexes = [
            ("user_id", "started_at"),  # 查询用户的阅读历史（按时间排序）
            ("user_id", "article_id"),  # 查询用户对某篇文章的阅读记录
            ("user_id", "article_id", "started_at"),  # 组合索引
            ("session_id",),  # 查询同一会话的所有记录
        ]

    def __str__(self):
        return f"{self.user_id} - {self.article_id} at {self.started_at}"


class ReadingStats(Model):
    """
    阅读统计表
    聚合每个用户对每篇文章的阅读统计
    """
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="reading_stats", on_delete=fields.CASCADE)
    article = fields.ForeignKeyField("models.Article", related_name="reading_stats", on_delete=fields.CASCADE)

    # 阅读次数统计
    total_views = fields.IntField(default=1, description="总阅读次数")
    completed_reads = fields.IntField(default=0, description="完成阅读次数（进度>=100%）")

    # 阅读时长统计
    total_duration = fields.IntField(default=0, description="总阅读时长（秒）")
    avg_duration = fields.IntField(default=0, description="平均每次阅读时长（秒）")

    # 阅读进度
    last_reading_progress = fields.IntField(default=0, description="最后阅读进度（0-100）")
    max_reading_progress = fields.IntField(default=0, description="最高阅读进度（0-100）")

    # 时间信息
    first_read_at = fields.DatetimeField(null=True, description="首次阅读时间")
    last_read_at = fields.DatetimeField(auto_now=True, description="最后阅读时间")

    class Meta:
        table = "reading_stats"
        unique_together = (("user", "article"),)  # 确保每个用户对每篇文章只有一条统计记录
        indexes = [
            ("user_id", "last_read_at"),  # 查询用户最近阅读的文章
            ("user_id", "total_views"),  # 按阅读次数排序
            ("user_id", "total_duration"),  # 按阅读时长排序
        ]

    def __str__(self):
        return f"{self.user_id} - {self.article_id} stats"


class ReadingGoal(Model):
    """
    阅读目标表
    设置用户的阅读目标
    """
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="reading_goals", on_delete=fields.CASCADE)

    # 目标类型
    goal_type = fields.CharField(max_length=20, description="目标类型：daily/weekly/monthly")

    # 目标数值
    target_duration = fields.IntField(description="目标阅读时长（分钟）")
    target_articles = fields.IntField(default=0, description="目标阅读文章数")

    # 目标状态
    is_active = fields.BooleanField(default=True, description="是否激活")
    start_date = fields.DateField(description="目标开始日期")
    end_date = fields.DateField(null=True, description="目标结束日期")

    # 时间戳
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "reading_goals"
        indexes = [
            ("user_id", "is_active", "start_date"),  # 查询用户的当前目标
        ]

    def __str__(self):
        return f"{self.user_id} - {self.goal_type} goal"


class ReadingNote(Model):
    """
    阅读笔记表
    用户在阅读时添加的笔记
    """
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="reading_notes", on_delete=fields.CASCADE)
    article = fields.ForeignKeyField("models.Article", related_name="reading_notes", on_delete=fields.CASCADE)

    # 笔记内容
    content = fields.TextField(description="笔记内容")
    note_type = fields.CharField(max_length=20, default="text", description="笔记类型：text/code/quote")

    # 位置信息
    chapter_title = fields.CharField(max_length=200, null=True, description="章节标题")
    section_index = fields.IntField(null=True, description="章节索引")
    reading_progress = fields.IntField(null=True, description="添加笔记时的阅读进度（0-100）")

    # 颜色标记
    color = fields.CharField(max_length=20, default="yellow", description="笔记颜色：yellow/blue/green/pink")

    # 时间戳
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "reading_notes"
        indexes = [
            ("user_id", "article_id"),  # 查询用户对某篇文章的所有笔记
            ("user_id", "created_at"),  # 按创建时间查询
            ("article_id", "created_at"),  # 查询某篇文章的所有笔记
        ]

    def __str__(self):
        return f"{self.user_id} - {self.article_id} note"
