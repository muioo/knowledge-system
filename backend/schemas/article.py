from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List, Literal

class ArticleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    # 删除: content: str
    source_url: Optional[str] = None
    summary: Optional[str] = None
    keywords: Optional[str] = None

class ArticleCreate(ArticleBase):
    tag_ids: Optional[List[int]] = Field(default=None, description="标签ID列表")

    # Import type: "direct" (直接创建), "file" (文件上传), "html" (URL 导入)
    import_type: Literal["direct", "file", "html"] = "direct"

    # 新增：用于文件上传或 HTML 导入时的内容
    html_content: Optional[str] = None

class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    # 删除: content: Optional[str] = None
    source_url: Optional[str] = None
    summary: Optional[str] = None
    keywords: Optional[str] = None
    tag_ids: Optional[List[int]] = Field(default=None, description="标签ID列表")

class TagInfo(BaseModel):
    id: int
    name: str
    color: str

    class Config:
        from_attributes = True

class ArticleResponse(ArticleBase):
    id: int
    author_id: int
    original_filename: Optional[str] = None
    view_count: int
    created_at: datetime
    updated_at: datetime
    tags: List[TagInfo] = []

    # 新增字段（html_content 仅在 ArticleHtmlResponse 中包含）
    html_path: Optional[str] = None
    processing_status: Optional[str] = None
    original_html_url: Optional[str] = None

    class Config:
        from_attributes = True

class SearchQuery(BaseModel):
    q: Optional[str] = None
    tags: Optional[List[int]] = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)

class ArticleFromHtmlUrlRequest(BaseModel):
    """从 HTML URL 导入文章请求，不接受客户端提供密钥。"""

    model_config = ConfigDict(extra="forbid")
    url: str = Field(..., min_length=1, max_length=1000)
    tag_ids: Optional[List[int]] = Field(default=None, description="标签ID列表")
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="可选的自定义标题")
    use_ai: bool = Field(True, description="是否使用AI提取关键词和摘要，默认为True")
    summary: Optional[str] = Field(None, description="手动输入的摘要（不使用AI时）")
    keywords: Optional[str] = Field(None, description="手动输入的关键词（不使用AI时）")
    provider: Optional[str] = Field(None, description="AI 供应商标识（zhipu/dashscope/custom），缺省取用户绑定的供应商")
    model: Optional[str] = Field(None, description="AI 模型名称，缺省取用户绑定模型")

class ArticleFromHtmlUrlResponse(BaseModel):
    """从 HTML URL 导入文章响应"""
    article_id: int
    status: str
    message: str

class ArticleHtmlResponse(BaseModel):
    """包含 HTML 内容的文章响应"""
    id: int
    title: str
    source_url: Optional[str] = None
    summary: Optional[str] = None
    keywords: Optional[str] = None
    author_id: int
    original_filename: Optional[str] = None
    view_count: int
    created_at: datetime
    updated_at: datetime
    tags: List[TagInfo] = []
    html_content: Optional[str] = None
    html_path: Optional[str] = None
    processing_status: Optional[str] = None
    original_html_url: Optional[str] = None
