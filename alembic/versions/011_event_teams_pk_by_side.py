"""event_teams primary key by (match_id, side)

The event_teams primary key was (match_id, team_code). team_code is not unique
within a match: undetermined upcoming matches return both teams as "TBD", which
collides on insert and crashes the schedule sync. It also let stale placeholder
rows accumulate (a "TBD" row plus the real team on the same side), which made
match_view emit duplicate match rows.

side (1/2) is the true per-match unique key and is already how match_view joins
the rows, so this migration de-duplicates existing rows and moves the primary key
to (match_id, side).

Revision ID: 011
Revises: 010
Create Date: 2026-09-19

"""

from alembic import op

revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Remove stale/duplicate rows so (match_id, side) is unique.
    #    Per (match_id, side) keep: a real team over a "TBD" placeholder, then a row
    #    that already has game data, then the physically-first row.
    op.execute(
        """
        DELETE FROM event_teams
        WHERE ctid IN (
            SELECT ctid FROM (
                SELECT
                    ctid,
                    ROW_NUMBER() OVER (
                        PARTITION BY match_id, side
                        ORDER BY
                            (CASE WHEN team_code = 'TBD' THEN 1 ELSE 0 END),
                            (CASE WHEN game_wins IS NULL THEN 1 ELSE 0 END),
                            ctid
                    ) AS rn
                FROM event_teams
            ) ranked
            WHERE rn > 1
        );
        """
    )

    # 2. Swap the primary key: (match_id, team_code) -> (match_id, side).
    op.drop_constraint("event_teams_pkey", "event_teams", type_="primary")
    op.create_primary_key("event_teams_pkey", "event_teams", ["match_id", "side"])


def downgrade() -> None:
    # NOTE: rows deleted during upgrade are not restored. This downgrade can fail if
    # any match still has two teams sharing a team_code (e.g. two "TBD" teams).
    op.drop_constraint("event_teams_pkey", "event_teams", type_="primary")
    op.create_primary_key("event_teams_pkey", "event_teams", ["match_id", "team_code"])
