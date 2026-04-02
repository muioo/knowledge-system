from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `users` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `email` VARCHAR(100) NOT NULL UNIQUE,
    `hashed_password` VARCHAR(255) NOT NULL,
    `role` VARCHAR(10) NOT NULL  DEFAULT 'user',
    `is_active` BOOL NOT NULL  DEFAULT 1,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `articles` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `title` VARCHAR(255) NOT NULL,
    `original_filename` VARCHAR(255),
    `source_url` VARCHAR(1000),
    `summary` LONGTEXT,
    `keywords` VARCHAR(500),
    `view_count` INT NOT NULL  DEFAULT 0,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `html_path` VARCHAR(500),
    `processing_status` VARCHAR(20) NOT NULL  DEFAULT 'pending',
    `original_html_url` VARCHAR(1000),
    `author_id` INT NOT NULL,
    CONSTRAINT `fk_articles_users_3b493172` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `tags` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(50) NOT NULL UNIQUE,
    `color` VARCHAR(7) NOT NULL  DEFAULT '#3498db',
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `reading_goals` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `goal_type` VARCHAR(20) NOT NULL  COMMENT '目标类型：daily/weekly/monthly',
    `target_duration` INT NOT NULL  COMMENT '目标阅读时长（分钟）',
    `target_articles` INT NOT NULL  COMMENT '目标阅读文章数' DEFAULT 0,
    `is_active` BOOL NOT NULL  COMMENT '是否激活' DEFAULT 1,
    `start_date` DATE NOT NULL  COMMENT '目标开始日期',
    `end_date` DATE   COMMENT '目标结束日期',
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `user_id` INT NOT NULL,
    CONSTRAINT `fk_reading__users_0bc5bbe2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    KEY `idx_reading_goa_user_id_c76634` (`user_id`, `is_active`, `start_date`)
) CHARACTER SET utf8mb4 COMMENT='阅读目标表';
CREATE TABLE IF NOT EXISTS `reading_history` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `started_at` DATETIME(6) NOT NULL  COMMENT '开始阅读时间',
    `ended_at` DATETIME(6)   COMMENT '结束阅读时间',
    `reading_duration` INT NOT NULL  COMMENT '阅读时长（秒）' DEFAULT 0,
    `reading_progress` INT NOT NULL  COMMENT '阅读进度（0-100）' DEFAULT 0,
    `scroll_position` INT NOT NULL  COMMENT '滚动位置（像素）' DEFAULT 0,
    `total_content_length` INT NOT NULL  COMMENT '总内容长度（像素）' DEFAULT 0,
    `actual_progress` INT NOT NULL  COMMENT '实际阅读进度（基于滚动位置计算）' DEFAULT 0,
    `session_id` VARCHAR(100)   COMMENT '阅读会话ID，用于关联同一次阅读的多次暂停/继续',
    `is_completed` BOOL NOT NULL  COMMENT '是否已完成阅读（进度>=100%）' DEFAULT 0,
    `device_type` VARCHAR(50)   COMMENT '设备类型（desktop/mobile/tablet）',
    `ip_address` VARCHAR(50)   COMMENT 'IP地址',
    `created_at` DATETIME(6) NOT NULL  COMMENT '记录创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `article_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    CONSTRAINT `fk_reading__articles_79504fd1` FOREIGN KEY (`article_id`) REFERENCES `articles` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_reading__users_4b68aef9` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    KEY `idx_reading_his_user_id_2c4563` (`user_id`, `started_at`),
    KEY `idx_reading_his_user_id_9d0e56` (`user_id`, `article_id`),
    KEY `idx_reading_his_user_id_a8491b` (`user_id`, `article_id`, `started_at`),
    KEY `idx_reading_his_session_21785c` (`session_id`)
) CHARACTER SET utf8mb4 COMMENT='阅读历史记录表';
CREATE TABLE IF NOT EXISTS `reading_notes` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `content` LONGTEXT NOT NULL  COMMENT '笔记内容',
    `note_type` VARCHAR(20) NOT NULL  COMMENT '笔记类型：text/code/quote' DEFAULT 'text',
    `chapter_title` VARCHAR(200)   COMMENT '章节标题',
    `section_index` INT   COMMENT '章节索引',
    `reading_progress` INT   COMMENT '添加笔记时的阅读进度（0-100）',
    `color` VARCHAR(20) NOT NULL  COMMENT '笔记颜色：yellow/blue/green/pink' DEFAULT 'yellow',
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `article_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    CONSTRAINT `fk_reading__articles_5cb68475` FOREIGN KEY (`article_id`) REFERENCES `articles` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_reading__users_82df4220` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    KEY `idx_reading_not_user_id_c8a00c` (`user_id`, `article_id`),
    KEY `idx_reading_not_user_id_136a09` (`user_id`, `created_at`),
    KEY `idx_reading_not_article_dda356` (`article_id`, `created_at`)
) CHARACTER SET utf8mb4 COMMENT='阅读笔记表';
CREATE TABLE IF NOT EXISTS `reading_stats` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `total_views` INT NOT NULL  COMMENT '总阅读次数' DEFAULT 1,
    `completed_reads` INT NOT NULL  COMMENT '完成阅读次数（进度>=100%）' DEFAULT 0,
    `total_duration` INT NOT NULL  COMMENT '总阅读时长（秒）' DEFAULT 0,
    `avg_duration` INT NOT NULL  COMMENT '平均每次阅读时长（秒）' DEFAULT 0,
    `last_reading_progress` INT NOT NULL  COMMENT '最后阅读进度（0-100）' DEFAULT 0,
    `max_reading_progress` INT NOT NULL  COMMENT '最高阅读进度（0-100）' DEFAULT 0,
    `first_read_at` DATETIME(6)   COMMENT '首次阅读时间',
    `last_read_at` DATETIME(6) NOT NULL  COMMENT '最后阅读时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `article_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    UNIQUE KEY `uid_reading_sta_user_id_823df3` (`user_id`, `article_id`),
    CONSTRAINT `fk_reading__articles_75268596` FOREIGN KEY (`article_id`) REFERENCES `articles` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_reading__users_afdd0e9e` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    KEY `idx_reading_sta_user_id_d78b8b` (`user_id`, `last_read_at`),
    KEY `idx_reading_sta_user_id_5e2dac` (`user_id`, `total_views`),
    KEY `idx_reading_sta_user_id_b95026` (`user_id`, `total_duration`)
) CHARACTER SET utf8mb4 COMMENT='阅读统计表';
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `article_tags` (
    `tag_id` INT NOT NULL,
    `article_id` INT NOT NULL,
    FOREIGN KEY (`tag_id`) REFERENCES `articles` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`article_id`) REFERENCES `tags` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
