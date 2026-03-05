"""
集成测试示例
"""
import pytest
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_health_check():
    """测试健康检查端点"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_api_endpoints_exist():
    """测试所有 API 端点是否可访问"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 测试认证端点
        response = await client.post("/api/v1/auth/register")
        assert response.status_code in [200, 422]  # 422 用于缺少参数的情况

        response = await client.post("/api/v1/auth/login")
        assert response.status_code in [200, 422]

        # 测试用户管理端点
        response = await client.get("/api/v1/users/")
        assert response.status_code in [200, 401]  # 401 用于未认证的情况

        # 测试文章管理端点
        response = await client.get("/api/v1/articles/")
        assert response.status_code in [200, 401]

        # 测试标签管理端点
        response = await client.get("/api/v1/tags/")
        assert response.status_code in [200, 401]

        # 测试搜索端点
        response = await client.get("/api/v1/search/articles")
        assert response.status_code in [200, 401]

        # 测试阅读记录端点
        response = await client.get("/api/v1/reading/history")
        assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_cors_middleware():
    """测试 CORS 中间件"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"}
        )
        assert "access-control-allow-origin" in response.headers


@pytest.mark.asyncio
async def test_logging_middleware():
    """测试日志中间件"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert "x-process-time" in response.headers
        assert float(response.headers["x-process-time"]) >= 0


@pytest.mark.asyncio
async def test_document_converters():
    """测试文档转换器"""
    from utils.converters import get_converter

    # 测试各种文件类型的转换器
    test_files = [
        ("test.docx", "WordConverter"),
        ("test.pdf", "PDFConverter"),
        ("test.pptx", "PPTConverter"),
        ("test.md", "MarkdownConverter"),
        ("test.html", "HTMLConverter"),
    ]

    for filename, expected_converter in test_files:
        converter = get_converter(filename)
        assert converter.__class__.__name__ == expected_converter


@pytest.mark.asyncio
async def test_unsupported_file_type():
    """测试不支持的文件类型"""
    from utils.converters import get_converter
    import pytest

    with pytest.raises(ValueError, match="不支持的文件类型"):
        get_converter("test.xyz")


@pytest.mark.asyncio
async def test_settings_configuration():
    """测试配置设置"""
    from settings.config import settings

    assert settings.app_name == "知识系统后端"
    assert settings.app_version == "1.0.0"
    assert isinstance(settings.cors_origins_list, list)
    assert "http://localhost:3000" in settings.cors_origins_list


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
