import pytest
from tortoise import Tortoise
from models import User, Article, Tag, ReadingHistory, ReadingStats, TORTOISE_ORM


@pytest.fixture
async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest.mark.asyncio
async def test_create_user(init_db):
    user = await User.create(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed"
    )
    assert user.id is not None
    assert user.username == "testuser"


@pytest.mark.asyncio
async def test_user_role_default(init_db):
    user = await User.create(
        username="testuser2",
        email="test2@example.com",
        hashed_password="hashed"
    )
    assert user.role == "user"
