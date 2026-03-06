import os
from volcenginesdkarkruntime import Ark

# 从环境变量中获取您的API KEY，配置方法见：https://www.volcengine.com/docs/82379/1399008

client = Ark(
    base_url='https://ark.cn-beijing.volces.com/api/v3',
    api_key="e78d20dd-ee6b-48dc-9dab-453b1b0fb77b",
)

tools = [{
    "type": "web_search",
    "max_keyword": 2,
}]

# 创建一个对话请求
response = client.responses.create(
    model="ep-20260302234602-pz4hc",
    input=[{"role": "user", "content": "https://blog.zestp.com/archives/14138，请你根据我的这个链接的页面内容，提取这个页面的关键词"}],
    tools=tools,
)

print(response)