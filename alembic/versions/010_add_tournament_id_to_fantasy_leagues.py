"""add_tournament_id_to_fantasy_leagues

Revision ID: 010
Revises: 009
Create Date: 2026-07-25

"""

from alembic import op
import sqlalchemy as sa

revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "fantasy_leagues",
        sa.Column(
            "tournament_id",
            sa.String(),
            sa.ForeignKey("tournaments.id", ondelete="RESTRICT"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("fantasy_leagues", "tournament_id")
