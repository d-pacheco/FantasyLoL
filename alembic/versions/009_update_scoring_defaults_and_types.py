"""update_scoring_defaults_and_types

Revision ID: 009
Revises: 008
Create Date: 2026-06-30

"""

from alembic import op
import sqlalchemy as sa

revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "fantasy_league_scoring_settings",
        "kill_participation",
        type_=sa.Float(),
        existing_type=sa.Integer(),
        existing_nullable=False,
    )
    op.alter_column(
        "fantasy_league_scoring_settings",
        "damage_percentage",
        type_=sa.Float(),
        existing_type=sa.Integer(),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "fantasy_league_scoring_settings",
        "kill_participation",
        type_=sa.Integer(),
        existing_type=sa.Float(),
        existing_nullable=False,
    )
    op.alter_column(
        "fantasy_league_scoring_settings",
        "damage_percentage",
        type_=sa.Integer(),
        existing_type=sa.Float(),
        existing_nullable=False,
    )
