"""智谱 SDK 调用示例：请通过环境变量提供 API Key。"""
import os

from zai import ZhipuAiClient


def main():
    """使用智谱默认模型发送一次简单对话请求。"""
    api_key = os.getenv("ZHIPU_API_KEY")
    model = os.getenv("ZHIPU_MODEL", "glm-4-flash")
    if not api_key:
        raise RuntimeError("请先设置环境变量 ZHIPU_API_KEY")

    client = ZhipuAiClient(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个有用的 AI 助手。"},
            {"role": "user", "content": "你好，请介绍一下自己。"},
        ],
        temperature=0.6,
    )
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
