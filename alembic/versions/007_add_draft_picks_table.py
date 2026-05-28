"""add_draft_picks_table

Revision ID: 007
Revises: 006
Create Date: 2026-05-28

"""

from alembic import op
import sqlalchemy as sa

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "draft_picks",
        sa.Column("fantasy_league_id", sa.String(), nullable=False),
        sa.Column("pick_number", sa.Integer(), nullable=False),
        sa.Column("round_number", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("player_id", sa.String(), nullable=True),
        sa.Column("team_id", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("fantasy_league_id", "pick_number"),
    )


def downgrade() -> None:
    op.drop_table("draft_picks")
