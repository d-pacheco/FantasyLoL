"""Recreate match_view with team images

Revision ID: 004
Revises: 003
Create Date: 2026-05-09
"""

from alembic import op

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP VIEW IF EXISTS match_view CASCADE")
    op.execute("""
        CREATE OR REPLACE VIEW match_view AS
        SELECT
            m.id,
            m.start_time,
            m.block_name,
            m.league_slug,
            m.strategy_type,
            m.strategy_count,
            m.tournament_id,
            t1.team_name AS team_1_name,
            t2.team_name AS team_2_name,
            m.has_games,
            m.state,
            t1.game_wins AS team_1_wins,
            t2.game_wins AS team_2_wins,
            CASE
                WHEN t1.outcome = 'win' THEN t1.team_name
                WHEN t2.outcome = 'win' THEN t2.team_name
                ELSE NULL
            END AS winning_team,
            t1.team_image AS team_1_image,
            t2.team_image AS team_2_image
        FROM matches m
        LEFT JOIN event_teams t1 ON m.id = t1.match_id AND t1.side = 1
        LEFT JOIN event_teams t2 ON m.id = t2.match_id AND t2.side = 2
    """)


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS match_view CASCADE")
    op.execute("""
        CREATE OR REPLACE VIEW match_view AS
        SELECT
            m.id,
            m.start_time,
            m.block_name,
            m.league_slug,
            m.strategy_type,
            m.strategy_count,
            m.tournament_id,
            t1.team_name AS team_1_name,
            t2.team_name AS team_2_name,
            m.has_games,
            m.state,
            t1.game_wins AS team_1_wins,
            t2.game_wins AS team_2_wins,
            CASE
                WHEN t1.outcome = 'win' THEN t1.team_name
                WHEN t2.outcome = 'win' THEN t2.team_name
                ELSE NULL
            END AS winning_team
        FROM matches m
        LEFT JOIN event_teams t1 ON m.id = t1.match_id AND t1.side = 1
        LEFT JOIN event_teams t2 ON m.id = t2.match_id AND t2.side = 2
    """)
