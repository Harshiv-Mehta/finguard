from __future__ import annotations

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from app.db.base import Base


def bootstrap_database(engine: Engine) -> None:
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    transaction_tables = set(inspector.get_table_names())
    if "transactions" not in transaction_tables:
        return

    transaction_columns = {column["name"] for column in inspector.get_columns("transactions")}
    with engine.begin() as connection:
        if "user_id" not in transaction_columns:
            connection.execute(text("ALTER TABLE transactions ADD COLUMN user_id INTEGER"))

        dialect_name = engine.dialect.name
        if dialect_name == "sqlite":
            connection.execute(
                text("CREATE INDEX IF NOT EXISTS ix_transactions_user_id ON transactions (user_id)")
            )
        else:
            connection.execute(
                text("CREATE INDEX IF NOT EXISTS ix_transactions_user_id ON transactions (user_id)")
            )
