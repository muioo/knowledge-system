"""HTML 文章导入功能测试"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_import_html_article_success(client: AsyncClient, auth_headers):
    """测试成功导入 HTML 文章"""
    # 使用测试 URL
    response = await client.post(
        "/api/v1/articles/from-url-html",
        json={"url": "https://example.com/article"},
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["article_id"] > 0
    assert data["data"]["status"] == "pending"


@pytest.mark.asyncio
async def test_import_html_article_duplicate_url(client: AsyncClient, auth_headers):
    """测试重复 URL 导入"""
    url = "https://example.com/test-unique"

    # 第一次导入
    response1 = await client.post(
        "/api/v1/articles/from-url-html",
        json={"url": url},
        headers=auth_headers
    )
    assert response1.status_code == 200

    # 第二次导入相同 URL
    response2 = await client.post(
        "/api/v1/articles/from-url-html",
        json={"url": url},
        headers=auth_headers
    )
    assert response2.status_code == 409


@pytest.mark.asyncio
async def test_import_html_article_invalid_url(client: AsyncClient, auth_headers):
    """测试无效 URL"""
    response = await client.post(
        "/api/v1/articles/from-url-html",
        json={"url": "https://this-domain-does-not-exist-12345.com"},
        headers=auth_headers
    )

    assert response.status_code == 400
