"""Add duration_seconds to games and create game_multi_kills table

Revision ID: 003
Revises: 002
Create Date: 2026-05-09
"""

from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("games", sa.Column("duration_seconds", sa.Integer(), nullable=True))

    op.create_table(
        "game_multi_kills",
        sa.Column("game_id", sa.String(), sa.ForeignKey("games.id", ondelete="CASCADE"),
                  nullable=False),
        sa.Column("participant_id", sa.Integer(), nullable=False),
        sa.Column("kill_number", sa.Integer(), nullable=False),
        sa.Column("kill_type", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("game_id", "participant_id", "kill_number"),
    )

    # Wipe incorrectly-ordered dragon data; the analysis job will repopulate correctly.
    op.execute("DELETE FROM game_dragons")


def downgrade() -> None:
    op.drop_table("game_multi_kills")
    op.drop_column("games", "duration_seconds")
