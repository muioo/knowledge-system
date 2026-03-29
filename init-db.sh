#!/bin/bash
# 在服务器上运行此脚本初始化数据库

echo "=== 初始化 MySQL 数据库 ==="

# 连接到 MySQL 容器并创建数据库和用户
docker exec -i mysql mysql -uroot -proot123456 <<EOF
-- 创建数据库
CREATE DATABASE IF NOT EXISTS knowledge_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户（如果不存在）
CREATE USER IF NOT EXISTS 'knowledge_user'@'%' IDENTIFIED BY 'Knowledge@123';

-- 授予权限
GRANT ALL PRIVILEGES ON knowledge_system.* TO 'knowledge_user'@'%';
FLUSH PRIVILEGES;

-- 显示结果
SHOW DATABASES;
SELECT User, Host FROM mysql.user WHERE User='knowledge_user';
EOF

echo "=== 数据库初始化完成 ==="
