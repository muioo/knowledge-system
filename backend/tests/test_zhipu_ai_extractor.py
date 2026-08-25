import pytest
from pydantic import ValidationError

from backend.schemas.article import ArticleFromHtmlUrlRequest
from backend.utils import ai_extractor


class FakeCompletions:
    """记录智谱请求参数，避免测试访问真实网络。"""

    def __init__(self, calls):
        self.calls = calls

    def create(self, **kwargs):
        self.calls.append(kwargs)
        message = type("Message", (), {"content": '{"title":"标题","summary":"摘要","keywords":"测试","content":"正文"}'})
        choice = type("Choice", (), {"message": message})
        return type("Response", (), {"choices": [choice]})


class FakeChat:
    """模拟 SDK 的 chat.completions 结构。"""

    def __init__(self, calls):
        self.completions = FakeCompletions(calls)


class FakeZhipuAiClient:
    """模拟智谱客户端，记录初始化时收到的 API Key。"""

    instances = []

    def __init__(self, api_key):
        self.api_key = api_key
        self.calls = []
        self.chat = FakeChat(self.calls)
        self.instances.append(self)


@pytest.mark.asyncio
async def test_extract_article_requires_environment_api_key(monkeypatch):
    """启用智谱提取时必须配置后端环境变量中的 API Key。"""
    monkeypatch.setattr(ai_extractor.settings, "zhipu_api_key", "", raising=False)

    with pytest.raises(ValueError, match="ZHIPU_API_KEY"):
        await ai_extractor.extract_article_from_url(
            url="https://example.com/article",
            html_content="<article>正文</article>",
        )


@pytest.mark.asyncio
async def test_extract_article_uses_environment_api_key_and_default_model(monkeypatch):
    """智谱客户端必须使用环境变量密钥，默认模型为 glm-4-flash。"""
    FakeZhipuAiClient.instances = []
    monkeypatch.setattr(ai_extractor, "ZhipuAiClient", FakeZhipuAiClient)
    monkeypatch.setattr(ai_extractor.settings, "zhipu_api_key", "environment-key", raising=False)

    result = await ai_extractor.extract_article_from_url(
        url="https://example.com/article",
        html_content="<article>正文</article>",
    )

    client = FakeZhipuAiClient.instances[0]
    assert client.api_key == "environment-key"
    assert client.calls[0]["model"] == "glm-4-flash"
    assert result["title"] == "标题"


@pytest.mark.asyncio
async def test_extract_article_passes_selected_zhipu_model(monkeypatch):
    """模型选择仍会透传到 SDK，但 API Key 不再来自请求。"""
    FakeZhipuAiClient.instances = []
    monkeypatch.setattr(ai_extractor, "ZhipuAiClient", FakeZhipuAiClient)
    monkeypatch.setattr(ai_extractor.settings, "zhipu_api_key", "environment-key", raising=False)

    await ai_extractor.extract_article_from_url(
        url="https://example.com/article",
        html_content="<article>正文</article>",
        model="glm-4-plus",
    )

    client = FakeZhipuAiClient.instances[0]
    assert client.calls[0]["model"] == "glm-4-plus"


def test_url_import_request_rejects_removed_api_key_field():
    """已删除的 api_key 请求字段必须明确拒绝，避免客户端误以为仍生效。"""
    with pytest.raises(ValidationError, match="api_key"):
        ArticleFromHtmlUrlRequest(url="https://example.com", api_key="frontend-key")
