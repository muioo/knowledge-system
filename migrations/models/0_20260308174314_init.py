from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `users` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `email` VARCHAR(100) NOT NULL UNIQUE,
    `hashed_password` VARCHAR(255) NOT NULL,
    `role` VARCHAR(10) NOT NULL DEFAULT 'user',
    `is_active` BOOL NOT NULL DEFAULT 1,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `articles` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `title` VARCHAR(255) NOT NULL,
    `original_filename` VARCHAR(255),
    `source_url` VARCHAR(1000),
    `summary` LONGTEXT,
    `keywords` VARCHAR(500),
    `view_count` INT NOT NULL DEFAULT 0,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `html_path` VARCHAR(500),
    `processing_status` VARCHAR(20) NOT NULL DEFAULT 'pending',
    `original_html_url` VARCHAR(1000),
    `author_id` INT NOT NULL,
    CONSTRAINT `fk_articles_users_3b493172` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `tags` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(50) NOT NULL UNIQUE,
    `color` VARCHAR(7) NOT NULL DEFAULT '#3498db',
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `reading_history` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `started_at` DATETIME(6) NOT NULL,
    `ended_at` DATETIME(6),
    `reading_duration` INT NOT NULL DEFAULT 0,
    `reading_progress` INT NOT NULL DEFAULT 0,
    `article_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    CONSTRAINT `fk_reading__articles_79504fd1` FOREIGN KEY (`article_id`) REFERENCES `articles` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_reading__users_4b68aef9` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `reading_stats` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `total_views` INT NOT NULL DEFAULT 1,
    `total_duration` INT NOT NULL DEFAULT 0,
    `last_read_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `article_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    UNIQUE KEY `uid_reading_sta_user_id_823df3` (`user_id`, `article_id`),
    CONSTRAINT `fk_reading__articles_75268596` FOREIGN KEY (`article_id`) REFERENCES `articles` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_reading__users_afdd0e9e` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
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
    FOREIGN KEY (`article_id`) REFERENCES `tags` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `uidx_article_tag_tag_id_ea80eb` (`tag_id`, `article_id`)
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "eJztm29P2zgYwL8K6r1h0m6CDgZ37wqUA23QCbq7adMUmcakEYmd2c6gmvrdz3bjJE6ckJ"
    "SWNm3eIHjsJ7F/fmw/f8Lvjo9t6NF3Xygknb93fncQ8CH/RZO/3emAIEikQsDAnSc7hryH"
    "lIA7yggYMS68Bx6FXGRDOiJuwFyMuBSFnieEeMQ7ushJRCFyf4bQYtiBbCwH8v0HF7vIhk"
    "+Qqj+DB+vehZ6tjdO1xbul3GKTQMouETuXHcXb7qwR9kIfJZ2DCRtjFPd2ERNSByJIAIPi"
    "8YyEYvhidNE01YxmI026zIaY0rHhPQg9lppuRQYjjAQ/PhoqJ+iIt/zZ3T84Ojh+/+HgmH"
    "eRI4klR9PZ9JK5zxQlgethZyrbAQOzHhJjwk0sm/w9R+90DIgZX1onA5EPPQtRIVspRR88"
    "WR5EDhvzPw/3SpD927s5vejd7B7uvREzwdyUZwZ+HbV0ZZOgmlCEPnC9OghjhSby29+rAp"
    "D3KiQo23SEY0DH0LYCQOkjJobdXAzToLoYrEqQcE1OtGWA7R4eVgDLexWClW06WIK9Wrtb"
    "9X89hPJA6SzOOisZZ4ltZgm61OL3mfvLgPEEc1oAFVwzab0MzjuuuCye8eafi2YJvZPB4J"
    "MYtE/pT08KLocZjF+uTvocr6TLO7kMpu+hhOmIQDFrC7A81DPewlwfmqnqmhmsdqT6Tv2y"
    "ptuez8EeIG8SrVYJ8+HlVf922Lv6rIE/6w37oqUrpZOMdPdDxrrjh+z8dzm82BF/7nwbXP"
    "clQUyZQ+Qbk37Dbx0xJhAybCH8aAE7dasoqQKjLWwY2HMurK7ZLuxKF1YOXnjb9w8pv1EI"
    "7sDo4REQ29JaEgMAhLl8dNRwWEaa5x9voAck2vxCRwFHb/aU9VzlqTJdJU1WO3XvckvgD7"
    "HGLmWYuC8FcjN73IV82mQDuFAG2GKY3KonNYiI2Em4i4v2Vr7J7/pZCUDAkaMW7xZvyuwd"
    "Qxyf2lbFoXx6B7fRfJOieeayes5+rNAGTDFEflg7LgIefyZ/Uc3ciFF5LriR6W0WW4pDMo"
    "JWSGplS3StRtLc36uaNCnNmuRiUxr6Ppj5AzrNIXwqOC9TKg1BWeZF978ONQda4dq96n19"
    "oznRnwbX/6juKbynnwYnGagPcCISSQbvpNhG0zoNwZrNilZLi5blRXPm+cuFjxxSiAzRYO"
    "GFris9f7Ev6mbaW/XF3qZHNiyKbtMjG7qwuah2zHzPCgA/SWvcGZpSe2kolgHBI0ipShKE"
    "te5ho/Ir1jICiEROYmHljG4VwN1ivt0c3jhEkeZX0xU3KjfSdJflkfNTYoyJVSuFoem8ns"
    "Oz+mRGLsOc5ZiHeI4JdB30EU4ky0s+JoBGpjg78+3K+hEsyg5yMQGPcV5MNw8+QT4tOCus"
    "nfZuT3tn/c60Sma+zUi3GemlZaRTSUjgGCheATQZYvGz4rYdAmcegstO4ZbsWTlwK5Nxj6"
    "ZBhOlw791YJcNEIn6Ak1RTtN3jBYhaOd2ohY0JDp1xWkWhN54RXG7laE5LKwli8IYqQjSn"
    "4gqCGkdbPVi3C/dtSfWgbq67/QZQS9lgz+SuFOOLFV4xOvnj/cFfx/bdwqKTMoNTFI8KIR"
    "7lGLZpr03IjiQ3S8WvRxbmexR/fFLb/3jBFyjr5oOkppL1Q2JnTfdBEi8j63/o3slLfZDY"
    "8yx0QTJRhsEbycchxY6JHgJNWh+laT4K37VkvhtC12zmDdGQG0FNu7QSAjmledYxrbeAVV"
    "yvanbTFlGdp3ZI4sxIxUPNpLqVtV4FIiBYLI3Bd3mWYVp1KxnqXknVrLumtE1pd60iTWHN"
    "akVKY5ugldQq1D8wbX2lImUa5jqFYdMuAFwj/1sgy04/juqWeZb5QblW1SiOwOKqx/PxV1"
    "xqWWz09T3eicq2frQB2XIDMoYZ8CzxyV4dxyWj9XrXyP6qSWbJzeE55xW30ufzAGWWOFDm"
    "CCKzus1MB2xMwjhXkm/9+dafb/351fukrT+/Of789H9NTNNd"
)
