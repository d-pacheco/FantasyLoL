"""add_start_week_and_fantasy_scores

Revision ID: 008
Revises: 007
Create Date: 2026-06-29

"""

from alembic import op
import sqlalchemy as sa

revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "fantasy_leagues",
        sa.Column("start_week", sa.Integer(), nullable=True),
    )

    op.create_table(
        "fantasy_scores",
        sa.Column("fantasy_league_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("week", sa.Integer(), nullable=False),
        sa.Column("slot", sa.String(), nullable=False),
        sa.Column("player_id", sa.String(), nullable=True),
        sa.Column("team_id", sa.String(), nullable=True),
        sa.Column("points", sa.Float(), nullable=False),
        sa.Column("breakdown", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("fantasy_league_id", "user_id", "week", "slot"),
        sa.ForeignKeyConstraint(["fantasy_league_id"], ["fantasy_leagues.id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    op.drop_table("fantasy_scores")
    op.drop_column("fantasy_leagues", "start_week")
