from tortoise import Tortoise
from models.user import User
from models.article import Article
from models.tag import Tag
from models.reading import ReadingHistory, ReadingStats

TORTOISE_ORM = {
    "connections": {"default": "mysql://root:123456@localhost:3306/knowledge-system"},
    "apps": {
        "models": {
            "models": ["models.user", "models.article", "models.tag", "models.reading"],
            "default_connection": "default",
        }
    },
}

__all__ = ["User", "Article", "Tag", "ReadingHistory", "ReadingStats", "TORTOISE_ORM"]
