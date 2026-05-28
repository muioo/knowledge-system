import pytest

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
async def test_extract_article_requires_frontend_api_key():
    """启用智谱提取时必须由前端传入 API Key。"""
    with pytest.raises(ValueError, match="API Key"):
        await ai_extractor.extract_article_from_url(
            url="https://example.com/article",
            html_content="<article>正文</article>",
            api_key=None,
        )


@pytest.mark.asyncio
async def test_extract_article_uses_default_zhipu_model(monkeypatch):
    """未指定模型时默认使用 glm-4-flash。"""
    FakeZhipuAiClient.instances = []
    monkeypatch.setattr(ai_extractor, "ZhipuAiClient", FakeZhipuAiClient)

    result = await ai_extractor.extract_article_from_url(
        url="https://example.com/article",
        html_content="<article>正文</article>",
        api_key="frontend-key",
    )

    client = FakeZhipuAiClient.instances[0]
    assert client.api_key == "frontend-key"
    assert client.calls[0]["model"] == "glm-4-flash"
    assert result["title"] == "标题"


@pytest.mark.asyncio
async def test_extract_article_passes_selected_zhipu_model(monkeypatch):
    """前端选择的智谱模型会透传到 SDK 调用。"""
    FakeZhipuAiClient.instances = []
    monkeypatch.setattr(ai_extractor, "ZhipuAiClient", FakeZhipuAiClient)

    await ai_extractor.extract_article_from_url(
        url="https://example.com/article",
        html_content="<article>正文</article>",
        api_key="frontend-key",
        model="glm-4-plus",
    )

    client = FakeZhipuAiClient.instances[0]
    assert client.calls[0]["model"] == "glm-4-plus"
