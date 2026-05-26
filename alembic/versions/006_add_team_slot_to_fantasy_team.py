"""add_team_slot_to_fantasy_team

Revision ID: 006
Revises: 005
Create Date: 2026-05-26

"""

from alembic import op
import sqlalchemy as sa

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "fantasy_teams",
        sa.Column(
            "team_id",
            sa.String(),
            sa.ForeignKey("professional_teams.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("fantasy_teams", "team_id")
