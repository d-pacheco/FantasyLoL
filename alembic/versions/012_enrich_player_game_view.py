"""Enrich player_game_view with match context, duration, patch and side

Adds start_time, block_name, league_slug (from matches), match_id and
duration_seconds (from games), patch_version (from game_metadata), and a
derived side column (participants 1-5 => blue, 6-10 => red) to power the
player detail / match-history screen. View-only change (no table alterations).

Revision ID: 012
Revises: 011
Create Date: 2026-09-19
"""

from alembic import op

revision = "012"
down_revision = "011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP VIEW IF EXISTS player_game_view CASCADE")
    op.execute("""
        CREATE OR REPLACE VIEW player_game_view AS
        SELECT
            m.game_id,
            m.player_id,
            m.participant_id,
            m.champion_id,
            m.role,
            s.kills,
            s.deaths,
            s.assists,
            s.total_gold,
            s.creep_score,
            s.kill_participation,
            s.champion_damage_share,
            s.wards_placed,
            s.wards_destroyed,
            g.match_id,
            g.duration_seconds,
            mt.start_time,
            mt.block_name,
            mt.league_slug,
            gm.patch_version,
            CASE WHEN m.participant_id BETWEEN 1 AND 5 THEN 'blue' ELSE 'red' END AS side
        FROM
            player_game_metadata m
        JOIN
            player_game_stats s ON m.game_id = s.game_id AND m.participant_id = s.participant_id
        LEFT JOIN games g ON m.game_id = g.id
        LEFT JOIN matches mt ON g.match_id = mt.id
        LEFT JOIN game_metadata gm ON m.game_id = gm.game_id
    """)


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS player_game_view CASCADE")
    op.execute("""
        CREATE OR REPLACE VIEW player_game_view AS
        SELECT
            m.game_id,
            m.player_id,
            m.participant_id,
            m.champion_id,
            m.role,
            s.kills,
            s.deaths,
            s.assists,
            s.total_gold,
            s.creep_score,
            s.kill_participation,
            s.champion_damage_share,
            s.wards_placed,
            s.wards_destroyed
        FROM
            player_game_metadata m
        JOIN
            player_game_stats s ON m.game_id = s.game_id AND m.participant_id = s.participant_id
    """)
