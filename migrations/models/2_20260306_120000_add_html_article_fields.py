from aerich.migrate import Migrate


class AddHtmlArticleFields(Migrate):

    async def upgrade(self):
        upgrade_sql = """
        ALTER TABLE `articles` ADD COLUMN `html_path` VARCHAR(500) NULL;
        ALTER TABLE `articles` ADD COLUMN `processing_status` VARCHAR(20) NOT NULL DEFAULT 'pending';
        ALTER TABLE `articles` ADD COLUMN `original_html_url` VARCHAR(1000) NULL;
        """
        await self.execute(upgrade_sql)

    async def downgrade(self):
        downgrade_sql = """
        ALTER TABLE `articles` DROP COLUMN `html_path`;
        ALTER TABLE `articles` DROP COLUMN `processing_status`;
        ALTER TABLE `articles` DROP COLUMN `original_html_url`;
        """
        await self.execute(downgrade_sql)
