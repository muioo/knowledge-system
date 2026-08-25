"""标签层级纯函数与请求模型测试。"""

from datetime import datetime

import pytest

from backend.schemas.tag import TagCreate, TagResponse
from backend.utils.tag_hierarchy import collect_descendant_tag_ids


def test_collect_descendant_tag_ids_includes_all_levels():
    """父标签筛选范围必须包含自身和任意深度的子标签。"""
    tag_pairs = [(1, None), (2, 1), (3, 2), (4, 1), (5, None)]

    assert collect_descendant_tag_ids(1, tag_pairs) == {1, 2, 3, 4}


def test_collect_descendant_tag_ids_ignores_cycles():
    """异常循环数据不能导致后代遍历无限循环。"""
    tag_pairs = [(1, 3), (2, 1), (3, 2)]

    assert collect_descendant_tag_ids(1, tag_pairs) == {1, 2, 3}


def test_tag_create_and_response_expose_parent_id():
    """标签创建和读取模型必须包含可选父标签 ID。"""
    payload = TagCreate(name="后端", parent_id=7)
    response = TagResponse(
        id=8,
        name="FastAPI",
        color="#3498db",
        parent_id=7,
        created_at=datetime.now(),
    )

    assert payload.parent_id == 7
    assert response.parent_id == 7


class _FakeTagQuery:
    """提供标签 ID/父级对的最小查询模拟对象。"""

    def __init__(self, tag_pairs):
        """保存测试所需的平铺标签关系。"""
        self.tag_pairs = tag_pairs

    async def values_list(self, *fields):
        """返回控制器查询的 ID 和父级 ID。"""
        assert fields == ("id", "parent_id")
        return self.tag_pairs


class _FakeTagModel:
    """为控制器提供标签查询入口的模拟模型。"""

    query = None

    @classmethod
    def all(cls):
        """返回预设的标签查询对象。"""
        return cls.query


async def _empty_article_result():
    """返回空文章列表，以观察查询链不受响响。"""
    return []


class _FakeArticleQuery:
    """记录 list_articles 构建的标签筛选条件。"""

    def __init__(self):
        """初始化筛选、去重和分页记录。"""
        self.filters = []
        self.distinct_called = False
        self.prefetched_relations = ()
        self.offset_value = None
        self.limit_value = None

    def filter(self, **conditions):
        """记录过滤条件并继续链式调用。"""
        self.filters.append(conditions)
        return self

    def distinct(self):
        """记录为多标签文章执行去重。"""
        self.distinct_called = True
        return self

    async def count(self):
        """返回空结果集的总数。"""
        return 0

    def prefetch_related(self, *relations):
        """记录文章查询的预加载关系。"""
        self.prefetched_relations = relations
        return self

    def offset(self, value):
        """记录分页起始位置。"""
        self.offset_value = value
        return self

    def limit(self, value):
        """记录分页大小。"""
        self.limit_value = value
        return self

    def __await__(self):
        """使模拟对象兼容 Tortoise 查询集的 await 行为。"""
        return _empty_article_result().__await__()


class _FakeArticleModel:
    """为控制器提供可观察查询链的模拟文章模型。"""

    query = None

    @classmethod
    def all(cls):
        """返回预设的文章查询对象。"""
        return cls.query


@pytest.mark.asyncio
async def test_list_articles_filters_with_parent_and_descendant_tags(monkeypatch):
    """文章列表按父标签筛选时必须传入其全部后代 ID。"""
    from backend.controllers import article_controller

    tag_query = _FakeTagQuery([(10, None), (11, 10), (12, 11), (20, None)])
    article_query = _FakeArticleQuery()
    _FakeTagModel.query = tag_query
    _FakeArticleModel.query = article_query
    monkeypatch.setattr(article_controller, "Tag", _FakeTagModel)
    monkeypatch.setattr(article_controller, "Article", _FakeArticleModel)

    articles, total = await article_controller.list_articles(page=2, size=5, tag_id=10)

    assert articles == []
    assert total == 0
    assert article_query.filters == [{"tags__id__in": {10, 11, 12}}]
    assert article_query.distinct_called is True
    assert article_query.prefetched_relations == ("tags",)
    assert article_query.offset_value == 5
    assert article_query.limit_value == 5
