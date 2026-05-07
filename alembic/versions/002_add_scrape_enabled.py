"""Add scrape_enabled to leagues

Revision ID: 002
Revises: 001
Create Date: 2026-05-07
"""

from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "leagues",
        sa.Column("scrape_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )


def downgrade() -> None:
    op.drop_column("leagues", "scrape_enabled")
