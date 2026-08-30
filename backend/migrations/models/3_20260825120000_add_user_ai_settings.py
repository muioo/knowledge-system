from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE `user_ai_settings` (
            `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
            `user_id` INT NOT NULL,
            `provider` VARCHAR(20) NOT NULL,
            `model` VARCHAR(100) NOT NULL,
            `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
            `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
            CONSTRAINT `fk_user_ai_settings_user_id_1a2b3c4d` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
        ) CHARACTER SET utf8mb4;
        CREATE UNIQUE INDEX `uid_user_ai_settings_user_provider` ON `user_ai_settings` (`user_id`, `provider`);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `user_ai_settings`;"""
