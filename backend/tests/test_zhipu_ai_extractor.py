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


class FakeOpenAI:
    """模拟 OpenAI 兼容客户端，记录初始化参数与调用参数。"""

    instances = []

    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url
        self.calls = []
        FakeOpenAI.instances.append(self)
        # 复用智谱测试中的假响应结构
        self.chat = FakeChat(self.calls)


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
async def test_extract_article_rejects_unknown_provider(monkeypatch):
    """不支持的供应商标识必须直接拒绝。"""
    monkeypatch.setattr(ai_extractor.settings, "zhipu_api_key", "environment-key", raising=False)

    with pytest.raises(ValueError, match="不支持的 AI 供应商"):
        await ai_extractor.extract_article_from_url(
            url="https://example.com/article",
            html_content="<article>正文</article>",
            provider="unknown",
        )


@pytest.mark.asyncio
async def test_extract_article_dashscope_uses_openai_compatible_client(monkeypatch):
    """千问（百炼）必须走 OpenAI 兼容协议并按 workspace_id 拼接 base_url。"""
    FakeOpenAI.instances = []
    monkeypatch.setattr(ai_extractor, "OpenAI", FakeOpenAI)
    monkeypatch.setattr(ai_extractor.settings, "dashscope_api_key", "dash-key", raising=False)
    monkeypatch.setattr(ai_extractor.settings, "dashscope_workspace_id", "ws-123", raising=False)
    monkeypatch.setattr(ai_extractor.settings, "dashscope_default_model", "", raising=False)

    result = await ai_extractor.extract_article_from_url(
        url="https://example.com/article",
        html_content="<article>正文</article>",
        provider="dashscope",
        model="deepseek-v4-flash-0731",
    )

    client = FakeOpenAI.instances[0]
    assert client.api_key == "dash-key"
    assert client.base_url == "https://ws-123.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
    assert client.calls[0]["model"] == "deepseek-v4-flash-0731"
    assert result["title"] == "标题"


@pytest.mark.asyncio
async def test_extract_article_dashscope_requires_workspace(monkeypatch):
    """使用千问但未配置 workspace_id 时必须明确报错。"""
    monkeypatch.setattr(ai_extractor, "OpenAI", FakeOpenAI)
    monkeypatch.setattr(ai_extractor.settings, "dashscope_api_key", "dash-key", raising=False)
    monkeypatch.setattr(ai_extractor.settings, "dashscope_workspace_id", "", raising=False)

    with pytest.raises(ValueError, match="DASHSCOPE_WORKSPACE_ID"):
        await ai_extractor.extract_article_from_url(
            url="https://example.com/article",
            html_content="<article>正文</article>",
            provider="dashscope",
            model="deepseek-v4-flash-0731",
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
