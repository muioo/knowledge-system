# knowledge-system
1. 初始化项目
backend
创建数据库（mysql）

添加.env文件到backend

# 应用配置
APP_NAME=知识系统后端
APP_VERSION=1.0.0
DEBUG=True
# JWT令牌签名和严重 需生成
SECRET_KEY=随机生成

# 数据库配置
DB_HOST=localhost
DB_PORT=端口
DB_USER=数据库用户名
DB_PASSWORD=数据库密码
DB_NAME=数据库名称

# JWT 配置
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256

# 文件上传配置
MAX_FILE_SIZE=10485760
# UPLOAD_DIR 由代码自动设置为绝对路径

# CORS 配置
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000","http://localhost:3001"]

# 火山引擎 AI 配置
ARK_API_KEY=your-api-key
# SSL验证（某些网络环境下需要禁用）
VERIFY_SSL=False
数据库映射
# 初始化Aerich配置
aerich init -t backend.settings.config.TORTOISE_ORM

# 初始化数据库（创建所有表）
aerich init-db

# 创建迁移文件(初始化或者更新schemas)
aerich migrate

aerich update
frontend
创建.env文件
VITE_API_BASE_URL=http://ip:port/api/v1
初始化前端
# 开发环境
npm run dev