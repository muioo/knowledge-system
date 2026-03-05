from aerich.migrate import Migrate


class InitialSchema(Migrate):

    async def upgrade(self):
        upgrade_sql = """
        -- Create User table
        CREATE TABLE IF NOT EXISTS `users` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `username` VARCHAR(50) NOT NULL UNIQUE,
            `email` VARCHAR(100) NOT NULL UNIQUE,
            `hashed_password` VARCHAR(255) NOT NULL,
            `is_active` BOOL NOT NULL DEFAULT 1,
            `is_superuser` BOOL NOT NULL DEFAULT 0,
            `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
            `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
        );

        -- Create Tag table
        CREATE TABLE IF NOT EXISTS `tags` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `name` VARCHAR(50) NOT NULL UNIQUE,
            `color` VARCHAR(7) NOT NULL,
            `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
            `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
        );

        -- Create Article table
        CREATE TABLE IF NOT EXISTS `articles` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `title` VARCHAR(255) NOT NULL,
            `content` LONGTEXT NOT NULL,
            `original_filename` VARCHAR(255) NULL,
            `source_url` VARCHAR(1000) NULL,
            `summary` TEXT NULL,
            `keywords` VARCHAR(500) NULL,
            `author_id` INT NOT NULL,
            `view_count` INT NOT NULL DEFAULT 0,
            `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
            `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
            FOREIGN KEY (`author_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
        );

        -- Create article_tags relation table
        CREATE TABLE IF NOT EXISTS `article_tags` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `article_id` INT NOT NULL,
            `tag_id` INT NOT NULL,
            UNIQUE KEY `article_tag_unique` (`article_id`, `tag_id`),
            FOREIGN KEY (`article_id`) REFERENCES `articles`(`id`) ON DELETE CASCADE,
            FOREIGN KEY (`tag_id`) REFERENCES `tags`(`id`) ON DELETE CASCADE
        );

        -- Create ReadingHistory table
        CREATE TABLE IF NOT EXISTS `reading_history` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `user_id` INT NOT NULL,
            `article_id` INT NOT NULL,
            `read_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
            FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
            FOREIGN KEY (`article_id`) REFERENCES `articles`(`id`) ON DELETE CASCADE
        );

        -- Create ReadingStats table
        CREATE TABLE IF NOT EXISTS `reading_stats` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            `user_id` INT NOT NULL,
            `total_articles` INT NOT NULL DEFAULT 0,
            `total_reading_time` INT NOT NULL DEFAULT 0,
            `last_read_at` DATETIME(6) NULL,
            `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
            `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
            UNIQUE KEY `user_id` (`user_id`),
            FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
        );
        """
        await self.execute(upgrade_sql)

    async def downgrade(self):
        downgrade_sql = """
        DROP TABLE IF EXISTS `reading_stats`;
        DROP TABLE IF EXISTS `reading_history`;
        DROP TABLE IF EXISTS `article_tags`;
        DROP TABLE IF EXISTS `articles`;
        DROP TABLE IF EXISTS `tags`;
        DROP TABLE IF EXISTS `users`;
        """
        await self.execute(downgrade_sql)
