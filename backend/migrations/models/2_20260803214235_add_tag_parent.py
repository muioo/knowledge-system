from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `tags` ADD `parent_id` INT;
        ALTER TABLE `tags` ADD CONSTRAINT `fk_tags_tags_f8b39d4c` FOREIGN KEY (`parent_id`) REFERENCES `tags` (`id`) ON DELETE RESTRICT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `tags` DROP FOREIGN KEY `fk_tags_tags_f8b39d4c`;
        ALTER TABLE `tags` DROP COLUMN `parent_id`;"""
