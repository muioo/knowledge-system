"""
文章存储工具函数单元测试
"""
import pytest
import os
import shutil
from pathlib import Path
from backend.utils.article_storage import (
    get_article_dir,
    get_html_path,
    get_relative_html_path,
    ensure_article_dir,
    save_html_content,
    read_html_content,
    delete_article_files
)
from backend.settings.config import settings


@pytest.fixture
def temp_upload_dir(tmp_path):
    """临时上传目录"""
    original_upload_dir = settings.upload_dir
    settings.upload_dir = str(tmp_path)
    yield tmp_path
    settings.upload_dir = original_upload_dir


@pytest.mark.asyncio
async def test_get_article_dir(temp_upload_dir):
    """测试获取文章目录路径"""
    article_id = 123
    result = get_article_dir(article_id)
    expected = os.path.join(temp_upload_dir, "articles", "123")
    assert result == expected


@pytest.mark.asyncio
async def test_get_html_path(temp_upload_dir):
    """测试获取 HTML 文件路径"""
    article_id = 456
    result = get_html_path(article_id)
    expected = os.path.join(temp_upload_dir, "articles", "456", "index.html")
    assert result == expected


@pytest.mark.asyncio
async def test_get_relative_html_path():
    """测试获取相对路径"""
    article_id = 789
    result = get_relative_html_path(article_id)
    expected = "articles/789/index.html"
    assert result == expected


@pytest.mark.asyncio
async def test_ensure_article_dir(temp_upload_dir):
    """测试确保文章目录存在"""
    article_id = 100
    article_dir = await ensure_article_dir(article_id)

    # 检查目录是否创建
    assert os.path.exists(article_dir)
    assert article_dir == os.path.join(temp_upload_dir, "articles", "100")

    # 再次调用应该不会报错
    await ensure_article_dir(article_id)
    assert os.path.exists(article_dir)


@pytest.mark.asyncio
async def test_save_html_content(temp_upload_dir):
    """测试保存 HTML 内容"""
    article_id = 200
    html_content = "<html><body>Test Content</body></html>"

    relative_path = await save_html_content(article_id, html_content)

    # 验证返回的相对路径
    assert relative_path == "articles/200/index.html"

    # 验证文件是否创建
    html_path = get_html_path(article_id)
    assert os.path.exists(html_path)

    # 验证文件内容
    async with await __import__('aiofiles').open(html_path, 'r', encoding='utf-8') as f:
        content = await f.read()
    assert content == html_content


@pytest.mark.asyncio
async def test_read_html_content(temp_upload_dir):
    """测试读取 HTML 内容"""
    article_id = 300
    html_content = "<html><body>Read Test</body></html>"

    # 先保存内容
    await save_html_content(article_id, html_content)

    # 读取内容
    read_content = await read_html_content(article_id)
    assert read_content == html_content


@pytest.mark.asyncio
async def test_read_html_content_not_found(temp_upload_dir):
    """测试读取不存在的文件"""
    article_id = 999

    with pytest.raises(FileNotFoundError, match="文章内容文件不存在"):
        await read_html_content(article_id)


@pytest.mark.asyncio
async def test_delete_article_files(temp_upload_dir):
    """测试删除文章文件"""
    article_id = 400
    html_content = "<html><body>Delete Test</body></html>"

    # 创建文件
    await save_html_content(article_id, html_content)
    article_dir = get_article_dir(article_id)
    assert os.path.exists(article_dir)

    # 删除文件
    await delete_article_files(article_id)
    assert not os.path.exists(article_dir)


@pytest.mark.asyncio
async def test_delete_article_files_nonexistent(temp_upload_dir):
    """测试删除不存在的文章目录（不应该报错）"""
    article_id = 888

    # 删除不存在的目录不应该报错
    await delete_article_files(article_id)
    # 顺利通过即可


@pytest.mark.asyncio
async def test_save_html_content_unicode(temp_upload_dir):
    """测试保存包含 Unicode 字符的 HTML 内容"""
    article_id = 500
    html_content = "<html><body>中文测试 🎉 Test & Special < > \" '</body></html>"

    relative_path = await save_html_content(article_id, html_content)
    assert relative_path == "articles/500/index.html"

    # 读取并验证
    read_content = await read_html_content(article_id)
    assert read_content == html_content


@pytest.mark.asyncio
async def test_overwrite_html_content(temp_upload_dir):
    """测试覆盖已存在的 HTML 内容"""
    article_id = 600
    html_content_1 = "<html><body>Version 1</body></html>"
    html_content_2 = "<html><body>Version 2</body></html>"

    # 保存第一个版本
    await save_html_content(article_id, html_content_1)
    content = await read_html_content(article_id)
    assert content == html_content_1

    # 保存第二个版本（覆盖）
    await save_html_content(article_id, html_content_2)
    content = await read_html_content(article_id)
    assert content == html_content_2


@pytest.mark.asyncio
async def test_multiple_articles_isolation(temp_upload_dir):
    """测试多个文章之间的隔离性"""
    article_id_1 = 701
    article_id_2 = 702

    html_content_1 = "<html><body>Article 1</body></html>"
    html_content_2 = "<html><body>Article 2</body></html>"

    # 保存两个不同文章
    await save_html_content(article_id_1, html_content_1)
    await save_html_content(article_id_2, html_content_2)

    # 验证各自的内容
    content_1 = await read_html_content(article_id_1)
    content_2 = await read_html_content(article_id_2)

    assert content_1 == html_content_1
    assert content_2 == html_content_2
    assert content_1 != content_2

    # 验证目录隔离
    dir_1 = get_article_dir(article_id_1)
    dir_2 = get_article_dir(article_id_2)
    assert dir_1 != dir_2
    assert os.path.exists(dir_1)
    assert os.path.exists(dir_2)


@pytest.mark.asyncio
async def test_empty_html_content(temp_upload_dir):
    """测试保存空 HTML 内容"""
    article_id = 800
    html_content = ""

    relative_path = await save_html_content(article_id, html_content)
    assert relative_path == "articles/800/index.html"

    # 读取并验证
    read_content = await read_html_content(article_id)
    assert read_content == ""


@pytest.mark.asyncio
async def test_large_html_content(temp_upload_dir):
    """测试保存大型 HTML 内容"""
    article_id = 900
    # 创建一个较大的 HTML 内容
    html_content = "<html><body>" + "<p>Test paragraph</p>" * 1000 + "</body></html>"

    relative_path = await save_html_content(article_id, html_content)
    assert relative_path == "articles/900/index.html"

    # 读取并验证
    read_content = await read_html_content(article_id)
    assert read_content == html_content
    assert len(read_content) > 10000  # 验证文件大小
