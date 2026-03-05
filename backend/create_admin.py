import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tortoise import Tortoise
from backend.models import User, TORTOISE_ORM
from backend.utils.password import hash_password


async def create_admin_user():
    """创建超级管理员账号"""
    await Tortoise.init(config=TORTOISE_ORM)

    # 检查 admin 用户是否已存在
    existing = await User.get_or_none(username="admin")
    if existing:
        print("管理员账号已存在，正在更新...")
        existing.hashed_password = hash_password("123456")
        existing.role = "admin"
        existing.is_active = True
        await existing.save()
        print("管理员账号已更新：username=admin, password=123456, role=admin")
    else:
        # 创建新的管理员账号
        hashed = hash_password("123456")
        admin = await User.create(
            username="admin",
            email="admin@knowledge-system.com",
            hashed_password=hashed,
            role="admin",
            is_active=True
        )
        print("管理员账号创建成功！")
        print("  用户名: admin")
        print("  密码: 123456")
        print("  角色: admin")
        print("  邮箱: admin@knowledge-system.com")

    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(create_admin_user())
