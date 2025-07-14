import os
from alembic.config import Config
from alembic import command


def migrate():
    try:
        print("Running Alembic migrations...")
        os.makedirs("database", exist_ok=True)

        cfg = Config("alembic.ini")

        command.upgrade(cfg, "head")
        print("Migrations applied successfully")

    except Exception as e:
        print(f"Migration error: {e}")
        raise e
