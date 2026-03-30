from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `reading_goals` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `goal_type` VARCHAR(20) NOT NULL COMMENT '目标类型：daily/weekly/monthly',
    `target_duration` INT NOT NULL COMMENT '目标阅读时长（分钟）',
    `target_articles` INT NOT NULL COMMENT '目标阅读文章数' DEFAULT 0,
    `is_active` BOOL NOT NULL COMMENT '是否激活' DEFAULT 1,
    `start_date` DATE NOT NULL COMMENT '目标开始日期',
    `end_date` DATE COMMENT '目标结束日期',
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `user_id` INT NOT NULL,
    CONSTRAINT `fk_reading__users_0bc5bbe2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    KEY `idx_reading_goa_user_id_c76634` (`user_id`, `is_active`, `start_date`)
) CHARACTER SET utf8mb4 COMMENT='阅读目标表';

        ALTER TABLE `reading_history` ADD COLUMN `actual_progress` INT NOT NULL DEFAULT 0 COMMENT '实际阅读进度（基于滚动位置计算）';
        ALTER TABLE `reading_history` ADD COLUMN `device_type` VARCHAR(50) NULL COMMENT '设备类型（desktop/mobile/tablet）';
        ALTER TABLE `reading_history` ADD COLUMN `total_content_length` INT NOT NULL DEFAULT 0 COMMENT '总内容长度（像素）';
        ALTER TABLE `reading_history` ADD COLUMN `scroll_position` INT NOT NULL DEFAULT 0 COMMENT '滚动位置（像素）';
        ALTER TABLE `reading_history` ADD COLUMN `ip_address` VARCHAR(50) NULL COMMENT 'IP地址';
        ALTER TABLE `reading_history` ADD COLUMN `is_completed` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否已完成阅读（进度>=100%）';
        ALTER TABLE `reading_history` ADD COLUMN `session_id` VARCHAR(100) NULL COMMENT '阅读会话ID，用于关联同一次阅读的多次暂停/继续';
        ALTER TABLE `reading_history` ADD COLUMN `created_at` DATETIME NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间';

        CREATE TABLE IF NOT EXISTS `reading_notes` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `content` LONGTEXT NOT NULL COMMENT '笔记内容',
    `note_type` VARCHAR(20) NOT NULL DEFAULT 'text' COMMENT '笔记类型：text/code/quote',
    `chapter_title` VARCHAR(200) NULL COMMENT '章节标题',
    `section_index` INT NULL COMMENT '章节索引',
    `reading_progress` INT NULL COMMENT '添加笔记时的阅读进度（0-100）',
    `color` VARCHAR(20) NOT NULL DEFAULT 'yellow' COMMENT '笔记颜色：yellow/blue/green/pink',
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `article_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    CONSTRAINT `fk_reading__articles_5cb68475` FOREIGN KEY (`article_id`) REFERENCES `articles` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_reading__users_82df4220` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    KEY `idx_reading_not_user_id_c8a00c` (`user_id`, `article_id`),
    KEY `idx_reading_not_user_id_136a09` (`user_id`, `created_at`),
    KEY `idx_reading_not_article_dda356` (`article_id`, `created_at`)
) CHARACTER SET utf8mb4 COMMENT='阅读笔记表';

        ALTER TABLE `reading_stats` ADD COLUMN `max_reading_progress` INT NOT NULL DEFAULT 0 COMMENT '最高阅读进度（0-100）';
        ALTER TABLE `reading_stats` ADD COLUMN `avg_duration` INT NOT NULL DEFAULT 0 COMMENT '平均每次阅读时长（秒）';
        ALTER TABLE `reading_stats` ADD COLUMN `completed_reads` INT NOT NULL DEFAULT 0 COMMENT '完成阅读次数（进度>=100%）';
        ALTER TABLE `reading_stats` ADD COLUMN `first_read_at` DATETIME(6) NULL COMMENT '首次阅读时间';
        ALTER TABLE `reading_stats` ADD COLUMN `last_reading_progress` INT NOT NULL DEFAULT 0 COMMENT '最后阅读进度（0-100）';

        ALTER TABLE `reading_history` ADD INDEX `idx_reading_his_user_id_a8491b` (`user_id`, `article_id`, `started_at`);
        ALTER TABLE `reading_history` ADD INDEX `idx_reading_his_session_21785c` (`session_id`);
        ALTER TABLE `reading_history` ADD INDEX `idx_reading_his_user_id_2c4563` (`user_id`, `started_at`);
        ALTER TABLE `reading_history` ADD INDEX `idx_reading_his_user_id_9d0e56` (`user_id`, `article_id`);
        ALTER TABLE `reading_stats` ADD INDEX `idx_reading_sta_user_id_d78b8b` (`user_id`, `last_read_at`);
        ALTER TABLE `reading_stats` ADD INDEX `idx_reading_sta_user_id_b95026` (`user_id`, `total_duration`);
        ALTER TABLE `reading_stats` ADD INDEX `idx_reading_sta_user_id_5e2dac` (`user_id`, `total_views`);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `reading_history` DROP INDEX `idx_reading_his_user_id_9d0e56`;
        ALTER TABLE `reading_history` DROP INDEX `idx_reading_his_user_id_2c4563`;
        ALTER TABLE `reading_history` DROP INDEX `idx_reading_his_session_21785c`;
        ALTER TABLE `reading_history` DROP INDEX `idx_reading_his_user_id_a8491b`;
        ALTER TABLE `reading_stats` DROP INDEX `idx_reading_sta_user_id_5e2dac`;
        ALTER TABLE `reading_stats` DROP INDEX `idx_reading_sta_user_id_b95026`;
        ALTER TABLE `reading_stats` DROP INDEX `idx_reading_sta_user_id_d78b8b`;
        ALTER TABLE `reading_stats` DROP COLUMN `max_reading_progress`;
        ALTER TABLE `reading_stats` DROP COLUMN `avg_duration`;
        ALTER TABLE `reading_stats` DROP COLUMN `completed_reads`;
        ALTER TABLE `reading_stats` DROP COLUMN `first_read_at`;
        ALTER TABLE `reading_stats` DROP COLUMN `last_reading_progress`;
        ALTER TABLE `reading_stats` MODIFY COLUMN `total_duration` INT NOT NULL  DEFAULT 0;
        ALTER TABLE `reading_stats` MODIFY COLUMN `total_views` INT NOT NULL  DEFAULT 1;
        ALTER TABLE `reading_stats` MODIFY COLUMN `last_read_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6);
        ALTER TABLE `reading_history` DROP COLUMN `actual_progress`;
        ALTER TABLE `reading_history` DROP COLUMN `device_type`;
        ALTER TABLE `reading_history` DROP COLUMN `total_content_length`;
        ALTER TABLE `reading_history` DROP COLUMN `scroll_position`;
        ALTER TABLE `reading_history` DROP COLUMN `ip_address`;
        ALTER TABLE `reading_history` DROP COLUMN `is_completed`;
        ALTER TABLE `reading_history` DROP COLUMN `session_id`;
        ALTER TABLE `reading_history` DROP COLUMN `created_at`;
        ALTER TABLE `reading_history` MODIFY COLUMN `ended_at` DATETIME(6);
        ALTER TABLE `reading_history` MODIFY COLUMN `reading_duration` INT NOT NULL  DEFAULT 0;
        ALTER TABLE `reading_history` MODIFY COLUMN `started_at` DATETIME(6) NOT NULL;
        ALTER TABLE `reading_history` MODIFY COLUMN `reading_progress` INT NOT NULL  DEFAULT 0;
        DROP TABLE IF EXISTS `reading_goals`;
        DROP TABLE IF EXISTS `reading_notes`;"""
