"""
文章控制器集成测试
测试文章创建、读取、更新、删除等功能的端到端流程
"""
import pytest
from httpx import AsyncClient
from backend.models import Article, Tag
from backend.schemas.article import ArticleCreate, ArticleUpdate
from backend.controllers.article_controller import (
    create_article,
    get_article_by_id,
    update_article,
    delete_article,
    list_articles,
    search_articles
)


@pytest.fixture
async def clean_db():
    """清理测试数据"""
    yield
    # 清理测试创建的文章
    await Article.filter(title__startswith="TEST_").delete()


@pytest.mark.asyncio
async def test_create_article_direct(clean_db):
    """测试直接创建文章（不包含 HTML 内容）"""
    data = ArticleCreate(
        title="TEST_Direct Article",
        summary="Test summary",
        keywords="test,keywords",
        import_type="direct"
    )

    article = await create_article(data, author_id=1)

    assert article.id > 0
    assert article.title == "TEST_Direct Article"
    assert article.summary == "Test summary"
    assert article.keywords == "test,keywords"
    assert article.author_id == 1
    assert article.html_path is None


@pytest.mark.asyncio
async def test_create_article_with_html(clean_db):
    """测试创建包含 HTML 内容的文章"""
    html_content = "<html><body>Test HTML Content</body></html>"
    data = ArticleCreate(
        title="TEST_HTML Article",
        summary="Test summary",
        html_content=html_content,
        import_type="direct"
    )

    article = await create_article(data, author_id=1)

    assert article.id > 0
    assert article.title == "TEST_HTML Article"
    assert article.html_path == f"articles/{article.id}/index.html"

    # 验证文件已创建
    from backend.utils.article_storage import read_html_content
    saved_html = await read_html_content(article.id)
    assert saved_html == html_content


@pytest.mark.asyncio
async def test_create_article_with_tags(clean_db):
    """测试创建带标签的文章"""
    # 创建测试标签
    tag1 = await Tag.create(name="Python", color="#007bff")
    tag2 = await Tag.create(name="FastAPI", color="#28a745")

    data = ArticleCreate(
        title="TEST_Tagged Article",
        summary="Test article with tags",
        import_type="direct",
        tag_ids=[tag1.id, tag2.id]
    )

    article = await create_article(data, author_id=1)

    assert len(article.tags) == 2
    tag_names = {tag.name for tag in article.tags}
    assert "Python" in tag_names
    assert "FastAPI" in tag_names


@pytest.mark.asyncio
async def test_get_article_by_id(clean_db):
    """测试获取文章详情"""
    # 创建文章
    data = ArticleCreate(
        title="TEST_Get Article",
        html_content="<html><body>Content</body></html>",
        import_type="direct"
    )
    created = await create_article(data, author_id=1)

    # 获取文章
    article = await get_article_by_id(created.id)

    assert article.id == created.id
    assert article.title == "TEST_Get Article"
    assert article.html_content == "<html><body>Content</body></html>"
    assert article.view_count == 1  # 应该增加浏览次数


@pytest.mark.asyncio
async def test_get_article_by_id_not_found(clean_db):
    """测试获取不存在的文章"""
    with pytest.raises(ValueError, match="文章不存在"):
        await get_article_by_id(article_id=99999)


@pytest.mark.asyncio
async def test_update_article(clean_db):
    """测试更新文章"""
    # 创建文章
    data = ArticleCreate(
        title="TEST_Update Original",
        summary="Original summary",
        import_type="direct"
    )
    created = await create_article(data, author_id=1)

    # 更新文章
    update_data = ArticleUpdate(
        title="TEST_Update Modified",
        summary="Modified summary"
    )
    updated = await update_article(created.id, update_data, user_id=1)

    assert updated.id == created.id
    assert updated.title == "TEST_Update Modified"
    assert updated.summary == "Modified summary"


@pytest.mark.asyncio
async def test_update_article_unauthorized(clean_db):
    """测试更新无权限的文章"""
    # 创建文章
    data = ArticleCreate(
        title="TEST_Unauthorized Article",
        import_type="direct"
    )
    created = await create_article(data, author_id=1)

    # 尝试用其他用户更新
    update_data = ArticleUpdate(title="Modified Title")
    with pytest.raises(ValueError, match="无权编辑此文章"):
        await update_article(created.id, update_data, user_id=2, is_admin=False)


@pytest.mark.asyncio
async def test_update_article_tags(clean_db):
    """测试更新文章标签"""
    # 创建标签
    tag1 = await Tag.create(name="Tag1", color="#111")
    tag2 = await Tag.create(name="Tag2", color="#222")
    tag3 = await Tag.create(name="Tag3", color="#333")

    # 创建文章
    data = ArticleCreate(
        title="TEST_Tag Update",
        import_type="direct",
        tag_ids=[tag1.id, tag2.id]
    )
    created = await create_article(data, author_id=1)

    assert len(created.tags) == 2

    # 更新标签
    update_data = ArticleUpdate(tag_ids=[tag2.id, tag3.id])
    updated = await update_article(created.id, update_data, user_id=1)

    assert len(updated.tags) == 2
    tag_names = {tag.name for tag in updated.tags}
    assert "Tag1" not in tag_names
    assert "Tag2" in tag_names
    assert "Tag3" in tag_names


@pytest.mark.asyncio
async def test_delete_article(clean_db):
    """测试删除文章"""
    html_content = "<html><body>Delete Test</body></html>"
    data = ArticleCreate(
        title="TEST_Delete Article",
        html_content=html_content,
        import_type="direct"
    )
    created = await create_article(data, author_id=1)

    article_id = created.id

    # 验证文件存在
    from backend.utils.article_storage import read_html_content
    content = await read_html_content(article_id)
    assert content == html_content

    # 删除文章
    result = await delete_article(article_id, user_id=1)
    assert result is True

    # 验证数据库记录已删除
    article = await Article.get_or_none(id=article_id)
    assert article is None

    # 验证文件已删除
    with pytest.raises(FileNotFoundError):
        await read_html_content(article_id)


@pytest.mark.asyncio
async def test_delete_article_unauthorized(clean_db):
    """测试删除无权限的文章"""
    data = ArticleCreate(
        title="TEST_Unauthorized Delete",
        import_type="direct"
    )
    created = await create_article(data, author_id=1)

    # 尝试用其他用户删除
    with pytest.raises(ValueError, match="无权删除此文章"):
        await delete_article(created.id, user_id=2, is_admin=False)


@pytest.mark.asyncio
async def test_list_articles(clean_db):
    """测试列出文章"""
    # 创建多个文章
    for i in range(3):
        data = ArticleCreate(
            title=f"TEST_List Article {i}",
            import_type="direct"
        )
        await create_article(data, author_id=1)

    # 获取文章列表
    articles, total = await list_articles(page=1, size=10)

    assert total >= 3
    assert len(articles) >= 3


@pytest.mark.asyncio
async def test_list_articles_pagination(clean_db):
    """测试文章列表分页"""
    # 创建 5 个文章
    for i in range(5):
        data = ArticleCreate(
            title=f"TEST_Page Article {i}",
            import_type="direct"
        )
        await create_article(data, author_id=1)

    # 第一页
    articles1, total1 = await list_articles(page=1, size=2)
    assert len(articles1) == 2
    assert total1 >= 5

    # 第二页
    articles2, total2 = await list_articles(page=2, size=2)
    assert len(articles2) == 2
    assert total2 == total1


@pytest.mark.asyncio
async def test_list_articles_by_tag(clean_db):
    """测试按标签筛选文章"""
    # 创建标签
    tag1 = await Tag.create(name="FilterTag1", color="#111")
    tag2 = await Tag.create(name="FilterTag2", color="#222")

    # 创建带标签的文章
    data1 = ArticleCreate(
        title="TEST_Filter Article 1",
        import_type="direct",
        tag_ids=[tag1.id]
    )
    await create_article(data1, author_id=1)

    data2 = ArticleCreate(
        title="TEST_Filter Article 2",
        import_type="direct",
        tag_ids=[tag2.id]
    )
    await create_article(data2, author_id=1)

    # 按标签1筛选
    articles, total = await list_articles(page=1, size=10, tag_id=tag1.id)
    assert total >= 1
    assert all(article.tags for article in articles)


@pytest.mark.asyncio
async def test_search_articles_by_keyword(clean_db):
    """测试按关键词搜索文章"""
    # 创建文章
    data1 = ArticleCreate(
        title="TEST_Search Python Tutorial",
        summary="Learn Python programming",
        keywords="python,programming",
        import_type="direct"
    )
    await create_article(data1, author_id=1)

    data2 = ArticleCreate(
        title="TEST_Search Java Guide",
        summary="Java development guide",
        keywords="java,development",
        import_type="direct"
    )
    await create_article(data2, author_id=1)

    # 搜索 "Python"
    from backend.schemas.article import SearchQuery
    query = SearchQuery(q="Python", page=1, size=10)
    articles, total = await search_articles(query)

    assert total >= 1
    assert any("Python" in article.title or "Python" in article.summary for article in articles)


@pytest.mark.asyncio
async def test_search_articles_by_tags(clean_db):
    """测试按标签搜索文章"""
    # 创建标签
    tag1 = await Tag.create(name="SearchTag1", color="#111")
    tag2 = await Tag.create(name="SearchTag2", color="#222")

    # 创建文章
    data1 = ArticleCreate(
        title="TEST_Search Tag Article 1",
        import_type="direct",
        tag_ids=[tag1.id]
    )
    await create_article(data1, author_id=1)

    data2 = ArticleCreate(
        title="TEST_Search Tag Article 2",
        import_type="direct",
        tag_ids=[tag2.id]
    )
    await create_article(data2, author_id=1)

    # 按标签搜索
    from backend.schemas.article import SearchQuery
    query = SearchQuery(tags=[tag1.id], page=1, size=10)
    articles, total = await search_articles(query)

    assert total >= 1


@pytest.mark.asyncio
async def test_article_view_count_increment(clean_db):
    """测试浏览次数递增"""
    data = ArticleCreate(
        title="TEST_View Count",
        import_type="direct"
    )
    created = await create_article(data, author_id=1)

    initial_count = created.view_count

    # 第一次访问
    article1 = await get_article_by_id(created.id)
    assert article1.view_count == initial_count + 1

    # 第二次访问
    article2 = await get_article_by_id(created.id)
    assert article2.view_count == initial_count + 2


@pytest.mark.asyncio
async def test_article_with_missing_html_file(clean_db):
    """测试 HTML 文件丢失的情况"""
    # 创建文章（不保存 HTML）
    data = ArticleCreate(
        title="TEST_Missing HTML",
        import_type="direct"
    )
    created = await create_article(data, author_id=1)

    # 手动设置 html_path 但不创建文件
    await Article.filter(id=created.id).update(html_path="articles/9999/index.html")

    # 获取文章应该返回 html_content=None
    article = await get_article_by_id(created.id)
    assert article.html_content is None
    assert article.html_path == "articles/9999/index.html"


@pytest.mark.asyncio
async def test_create_article_file_rollback_on_error(clean_db):
    """测试创建文章失败时的回滚"""
    # 使用无效的 HTML 内容（可能导致错误）
    # 这个测试验证当保存文件失败时，数据库记录也会被删除
    original_upload_dir = await __import__('backend.utils.article_storage', fromlist=['settings']).settings.upload_dir

    # 设置一个无效的上传目录
    await __import__('backend.utils.article_storage', fromlist=['settings']).settings.update(
        upload_dir="/invalid/path/that/does/not/exist"
    )

    try:
        data = ArticleCreate(
            title="TEST_Rollback",
            html_content="<html><body>Test</body></html>",
            import_type="direct"
        )

        with pytest.raises(ValueError, match="文件保存失败"):
            await create_article(data, author_id=1)

        # 验证数据库中没有创建记录
        article = await Article.get_or_none(title="TEST_Rollback")
        assert article is None
    finally:
        # 恢复原始配置
        await __import__('backend.utils.article_storage', fromlist=['settings']).settings.update(
            upload_dir=original_upload_dir
        )


@pytest.mark.asyncio
async def test_update_article_preserves_html(clean_db):
    """测试更新文章时保留 HTML 内容"""
    html_content = "<html><body>Original Content</body></html>"
    data = ArticleCreate(
        title="TEST_Preserve HTML",
        html_content=html_content,
        import_type="direct"
    )
    created = await create_article(data, author_id=1)

    # 更新文章（不更新 HTML）
    update_data = ArticleUpdate(title="Updated Title")
    updated = await update_article(created.id, update_data, user_id=1)

    # 验证 HTML 内容仍然存在
    assert updated.html_content == html_content


@pytest.mark.asyncio
async def test_admin_can_update_any_article(clean_db):
    """测试管理员可以更新任何文章"""
    # 创建文章
    data = ArticleCreate(
        title="TEST_Admin Update",
        import_type="direct"
    )
    created = await create_article(data, author_id=1)

    # 管理员更新
    update_data = ArticleUpdate(title="Admin Modified")
    updated = await update_article(
        created.id,
        update_data,
        user_id=2,  # 不同的用户
        is_admin=True  # 但是是管理员
    )

    assert updated.title == "Admin Modified"


@pytest.mark.asyncio
async def test_admin_can_delete_any_article(clean_db):
    """测试管理员可以删除任何文章"""
    # 创建文章
    data = ArticleCreate(
        title="TEST_Admin Delete",
        import_type="direct"
    )
    created = await create_article(data, author_id=1)

    # 管理员删除
    result = await delete_article(
        created.id,
        user_id=2,  # 不同的用户
        is_admin=True  # 但是是管理员
    )

    assert result is True

    # 验证已删除
    article = await Article.get_or_none(id=created.id)
    assert article is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
