# 阅读记录数据库设计文档

## 概述

本文档描述了阅读记录相关的数据库表设计，确保每个用户拥有独立的阅读数据。

## 数据隔离原则

**所有阅读相关表都通过 `user_id` 外键实现用户隔离：**
- `reading_history.user_id` - 阅读历史
- `reading_stats.user_id` - 阅读统计
- `reading_goals.user_id` - 阅读目标
- `reading_notes.user_id` - 阅读笔记

## 数据表结构

### 1. reading_history (阅读历史表)

记录用户每次阅读文章的详细信息。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT (PK) | 主键 |
| user_id | INT (FK) | 用户ID |
| article_id | INT (FK) | 文章ID |
| started_at | DATETIME | 开始阅读时间 |
| ended_at | DATETIME | 结束阅读时间（可为空） |
| reading_duration | INT | 阅读时长（秒） |
| reading_progress | INT | 阅读进度（0-100） |
| session_id | VARCHAR(100) | 阅读会话ID（支持暂停/继续） |
| is_completed | BOOLEAN | 是否完成阅读 |
| device_type | VARCHAR(50) | 设备类型 |
| ip_address | VARCHAR(50) | IP地址 |
| created_at | DATETIME | 记录创建时间 |

**索引：**
- `idx_user_started`: (user_id, started_at) - 查询用户阅读历史
- `idx_user_article`: (user_id, article_id) - 查询用户对某文章的记录
- `idx_user_article_started`: (user_id, article_id, started_at) - 组合查询
- `idx_session`: (session_id) - 查询同一会话记录

### 2. reading_stats (阅读统计表)

聚合每个用户对每篇文章的阅读统计。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT (PK) | 主键 |
| user_id | INT (FK) | 用户ID |
| article_id | INT (FK) | 文章ID |
| total_views | INT | 总阅读次数 |
| completed_reads | INT | 完成阅读次数 |
| total_duration | INT | 总阅读时长（秒） |
| avg_duration | INT | 平均阅读时长（秒） |
| last_reading_progress | INT | 最后阅读进度 |
| max_reading_progress | INT | 最高阅读进度 |
| first_read_at | DATETIME | 首次阅读时间 |
| last_read_at | DATETIME | 最后阅读时间 |

**约束：**
- `UNIQUE(user_id, article_id)` - 每个用户对每篇文章只有一条统计记录

**索引：**
- `idx_user_last_read`: (user_id, last_read_at) - 最近阅读
- `idx_user_total_views`: (user_id, total_views) - 按次数排序
- `idx_user_total_duration`: (user_id, total_duration) - 按时长排序

### 3. reading_goals (阅读目标表)

设置用户的阅读目标。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT (PK) | 主键 |
| user_id | INT (FK) | 用户ID |
| goal_type | VARCHAR(20) | 目标类型（daily/weekly/monthly） |
| target_duration | INT | 目标阅读时长（分钟） |
| target_articles | INT | 目标阅读文章数 |
| is_active | BOOLEAN | 是否激活 |
| start_date | DATE | 目标开始日期 |
| end_date | DATE | 目标结束日期 |

**索引：**
- `idx_user_active_start`: (user_id, is_active, start_date) - 查询当前目标

### 4. reading_notes (阅读笔记表)

用户在阅读时添加的笔记。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT (PK) | 主键 |
| user_id | INT (FK) | 用户ID |
| article_id | INT (FK) | 文章ID |
| content | TEXT | 笔记内容 |
| note_type | VARCHAR(20) | 笔记类型（text/code/quote） |
| chapter_title | VARCHAR(200) | 章节标题 |
| section_index | INT | 章节索引 |
| reading_progress | INT | 添加笔记时的阅读进度 |
| color | VARCHAR(20) | 笔记颜色 |

**索引：**
- `idx_user_article`: (user_id, article_id) - 查询用户对某文章的笔记
- `idx_user_created`: (user_id, created_at) - 按时间查询
- `idx_article_created`: (article_id, created_at) - 查询某文章的笔记

## 数据关系图

```
users (用户表)
  │
  ├─ 1:N → reading_history (阅读历史)
  │
  ├─ 1:N → reading_stats (阅读统计)
  │       └─ UNIQUE(user_id, article_id)
  │
  ├─ 1:N → reading_goals (阅读目标)
  │
  └─ 1:N → reading_notes (阅读笔记)

articles (文章表)
  │
  ├─ 1:N → reading_history
  │
  ├─ 1:N → reading_stats
  │
  └─ 1:N → reading_notes
```

## 使用示例

### 查询用户的阅读历史
```sql
SELECT * FROM reading_history
WHERE user_id = ?
ORDER BY started_at DESC;
```

### 查询用户对某篇文章的所有阅读记录
```sql
SELECT * FROM reading_history
WHERE user_id = ? AND article_id = ?
ORDER BY started_at DESC;
```

### 查询用户的阅读统计
```sql
SELECT * FROM reading_stats
WHERE user_id = ?
ORDER BY last_read_at DESC;
```

### 查询用户的总阅读时长
```sql
SELECT SUM(total_duration) as total_seconds
FROM reading_stats
WHERE user_id = ?;
```

## 迁移说明

运行迁移脚本：
```bash
cd backend
python migrate_reading_enhancements.py
```

**迁移内容：**
1. 为 `reading_history` 添加新字段和索引
2. 为 `reading_stats` 添加新字段和索引
3. 创建 `reading_goals` 表
4. 创建 `reading_notes` 表

**注意：** 迁移脚本会自动检查字段/索引是否已存在，避免重复创建。

## 性能优化

1. **索引优化**：所有常用查询路径都已添加索引
2. **查询优化**：使用组合索引减少回表查询
3. **数据隔离**：通过 user_id 过滤确保数据安全

## 安全考虑

1. **用户隔离**：所有查询必须包含 `user_id` 条件
2. **外键约束**：确保数据引用完整性
3. **级联删除**：用户删除时自动清理相关数据
