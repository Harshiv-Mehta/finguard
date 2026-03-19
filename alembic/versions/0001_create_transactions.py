"""create transactions table"""

from alembic import op
import sqlalchemy as sa


revision = "0001_create_transactions"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("balance_before", sa.Float(), nullable=False),
        sa.Column("expense_amount", sa.Float(), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("expense_type", sa.String(length=20), nullable=False),
        sa.Column("monthly_needs", sa.Float(), nullable=False),
        sa.Column("savings_goal", sa.Float(), nullable=False),
        sa.Column("remaining_balance", sa.Float(), nullable=False),
        sa.Column("recent_expense_count", sa.Integer(), nullable=False),
        sa.Column("risk_score", sa.Integer(), nullable=False),
        sa.Column("risk_level", sa.String(length=20), nullable=False),
        sa.Column("is_risky", sa.Integer(), nullable=False),
        sa.Column("message", sa.String(length=255), nullable=False),
    )
    op.create_index("ix_transactions_created_at", "transactions", ["created_at"])
    op.create_index("ix_transactions_category", "transactions", ["category"])
    op.create_index("ix_transactions_risk_level", "transactions", ["risk_level"])


def downgrade() -> None:
    op.drop_index("ix_transactions_risk_level", table_name="transactions")
    op.drop_index("ix_transactions_category", table_name="transactions")
    op.drop_index("ix_transactions_created_at", table_name="transactions")
    op.drop_table("transactions")
