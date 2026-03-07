from aerich.migrate import Migrate


class ResetArticles(Migrate):
    """重置文章表，移除 content 字段"""

    async def upgrade(self):
        upgrade_sql = """
        -- 删除旧表
        DROP TABLE IF EXISTS `article_tags`;
        DROP TABLE IF EXISTS `articles`;

        -- 创建新表（不含 content 字段）
        CREATE TABLE `articles` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `title` VARCHAR(255) NOT NULL,
            `original_filename` VARCHAR(255) NULL,
            `source_url` VARCHAR(1000) NULL,
            `summary` TEXT NULL,
            `keywords` VARCHAR(500) NULL,
            `author_id` INT NOT NULL,
            `view_count` INT NOT NULL DEFAULT 0,
            `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
            `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
            `html_path` VARCHAR(500) NULL,
            `processing_status` VARCHAR(20) NOT NULL DEFAULT 'pending',
            `original_html_url` VARCHAR(1000) NULL,
            FOREIGN KEY (`author_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
        );

        -- 重建关联表
        CREATE TABLE IF NOT EXISTS `article_tags` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `article_id` INT NOT NULL,
            `tag_id` INT NOT NULL,
            UNIQUE KEY `article_tag_unique` (`article_id`, `tag_id`),
            FOREIGN KEY (`article_id`) REFERENCES `articles`(`id`) ON DELETE CASCADE,
            FOREIGN KEY (`tag_id`) REFERENCES `tags`(`id`) ON DELETE CASCADE
        );
        """
        await self.execute(upgrade_sql)

    async def downgrade(self):
        downgrade_sql = """
        DROP TABLE IF EXISTS `article_tags`;
        DROP TABLE IF EXISTS `articles`;
        """
        await self.execute(downgrade_sql)
