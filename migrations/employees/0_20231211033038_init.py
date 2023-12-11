from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "employees" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "first_name" VARCHAR(50) NOT NULL,
    "last_name" VARCHAR(50) NOT NULL,
    "father_name" VARCHAR(50),
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "phone" VARCHAR(70),
    "address" VARCHAR(255),
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "position" VARCHAR(150)
);
COMMENT ON TABLE "employees" IS 'Модель сотрудника для базы данных';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "tasks" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "deadline" TIMESTAMPTZ,
    "status" VARCHAR(50) NOT NULL  DEFAULT 'new',
    "parent_task_id" INT REFERENCES "tasks" ("id") ON DELETE CASCADE,
    "performer_id" INT REFERENCES "employees" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "password" VARCHAR(255) NOT NULL,
    "first_name" VARCHAR(50),
    "last_name" VARCHAR(50),
    "last_login" TIMESTAMPTZ,
    "registration_date" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "is_active" BOOL NOT NULL  DEFAULT True,
    "is_staff" BOOL NOT NULL  DEFAULT False,
    "is_superuser" BOOL NOT NULL  DEFAULT False
);
COMMENT ON TABLE "users" IS 'Модель пользователя для базы данных';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
