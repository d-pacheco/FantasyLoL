"""expand_scoring_settings

Revision ID: 005
Revises: 004
Create Date: 2026-05-14

"""

from alembic import op
import sqlalchemy as sa

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "fantasy_league_scoring_settings",
        "creep_score",
        new_column_name="cspm",
    )
    op.execute("UPDATE fantasy_league_scoring_settings SET cspm = 1.0")

    for col, default in [
        ("double_kill", 1.0),
        ("triple_kill", 2.0),
        ("quadra_kill", 4.0),
        ("penta_kill", 10.0),
        ("match_win", 5.0),
        ("match_sweep", 5.0),
        ("dragon", 1.0),
        ("elder_dragon", 3.0),
        ("baron", 2.0),
        ("tower", 1.0),
        ("inhibitor", 1.0),
        ("soul", 4.0),
    ]:
        op.add_column(
            "fantasy_league_scoring_settings",
            sa.Column(col, sa.Float(), nullable=False, server_default=str(default)),
        )


def downgrade() -> None:
    for col in [
        "double_kill",
        "triple_kill",
        "quadra_kill",
        "penta_kill",
        "match_win",
        "match_sweep",
        "dragon",
        "elder_dragon",
        "baron",
        "tower",
        "inhibitor",
        "soul",
    ]:
        op.drop_column("fantasy_league_scoring_settings", col)

    op.alter_column(
        "fantasy_league_scoring_settings",
        "cspm",
        new_column_name="creep_score",
    )
