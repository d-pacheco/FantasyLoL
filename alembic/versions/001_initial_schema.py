"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-06

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Enum types
matchstate = sa.Enum("completed", "inProgress", "unstarted", name="matchstate")
gamestate = sa.Enum("completed", "inProgress", "unstarted", "unneeded", name="gamestate")
playerrole = sa.Enum("top", "jungle", "mid", "bottom", "support", "none", name="playerrole")
fantasyleaguestatus = sa.Enum(
    "pre-draft", "draft", "active", "completed", "deleted", name="fantasyleaguestatus"
)
fantasyleaguemembershipstatus = sa.Enum(
    "pending", "accepted", "declined", "revoked", name="fantasyleaguemembershipstatus"
)
useraccountstatus = sa.Enum("active", "pendingVerification", "deleted", name="useraccountstatus")


def upgrade() -> None:
    # Riot data tables
    op.create_table(
        "leagues",
        sa.Column("id", sa.String(), primary_key=True, index=True),
        sa.Column("slug", sa.String()),
        sa.Column("name", sa.String()),
        sa.Column("region", sa.String()),
        sa.Column("image", sa.String()),
        sa.Column("priority", sa.Integer()),
        sa.Column("fantasy_available", sa.Boolean()),
    )

    op.create_table(
        "tournaments",
        sa.Column("id", sa.String(), primary_key=True, index=True),
        sa.Column("slug", sa.String()),
        sa.Column("start_date", sa.String()),
        sa.Column("end_date", sa.String()),
        sa.Column("league_id", sa.String(), sa.ForeignKey("leagues.id", ondelete="CASCADE")),
    )

    op.create_table(
        "professional_teams",
        sa.Column("id", sa.String(), primary_key=True, index=True),
        sa.Column("slug", sa.String()),
        sa.Column("name", sa.String()),
        sa.Column("code", sa.String()),
        sa.Column("image", sa.String()),
        sa.Column("alternative_image", sa.String(), nullable=True),
        sa.Column("background_image", sa.String(), nullable=True),
        sa.Column("status", sa.String()),
        sa.Column("home_league_name", sa.String(), nullable=True),
        sa.Column("home_league_region", sa.String(), nullable=True),
    )

    op.create_table(
        "matches",
        sa.Column("id", sa.String(), primary_key=True, index=True),
        sa.Column("start_time", sa.String()),
        sa.Column("block_name", sa.String()),
        sa.Column("league_slug", sa.String()),
        sa.Column(
            "league_id", sa.String(), sa.ForeignKey("leagues.id", ondelete="CASCADE"), nullable=True
        ),
        sa.Column("strategy_type", sa.String()),
        sa.Column("strategy_count", sa.Integer()),
        sa.Column(
            "tournament_id",
            sa.String(),
            sa.ForeignKey("tournaments.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("has_games", sa.Boolean(), default=True),
        sa.Column("state", matchstate, nullable=False),
    )

    op.create_table(
        "event_teams",
        sa.Column("match_id", sa.String(), sa.ForeignKey("matches.id", ondelete="CASCADE")),
        sa.Column(
            "team_id",
            sa.String(),
            sa.ForeignKey("professional_teams.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("side", sa.Integer(), nullable=False),
        sa.Column("team_code", sa.String(), nullable=False),
        sa.Column("team_name", sa.String(), nullable=True),
        sa.Column("team_image", sa.String(), nullable=True),
        sa.Column("game_wins", sa.Integer(), nullable=True),
        sa.Column("outcome", sa.String(), nullable=True),
        sa.Column("wins", sa.Integer(), nullable=True),
        sa.Column("losses", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("match_id", "team_code"),
    )

    op.create_table(
        "games",
        sa.Column("id", sa.String(), primary_key=True, index=True),
        sa.Column("state", gamestate, nullable=False),
        sa.Column("number", sa.Integer()),
        sa.Column("match_id", sa.String(), sa.ForeignKey("matches.id", ondelete="CASCADE")),
        sa.Column("frames_status", sa.String(), nullable=True),
        sa.Column("details_status", sa.String(), nullable=True),
    )

    op.create_table(
        "game_teams",
        sa.Column("game_id", sa.String(), sa.ForeignKey("games.id", ondelete="CASCADE")),
        sa.Column(
            "team_id", sa.String(), sa.ForeignKey("professional_teams.id", ondelete="CASCADE")
        ),
        sa.Column("side", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("game_id", "team_id"),
    )

    op.create_table(
        "game_metadata",
        sa.Column(
            "game_id", sa.String(), sa.ForeignKey("games.id", ondelete="CASCADE"), primary_key=True
        ),
        sa.Column("patch_version", sa.String()),
    )

    op.create_table(
        "game_participant_perks",
        sa.Column("game_id", sa.String(), sa.ForeignKey("games.id", ondelete="CASCADE")),
        sa.Column("participant_id", sa.Integer()),
        sa.Column("style_id", sa.Integer()),
        sa.Column("sub_style_id", sa.Integer()),
        sa.Column("perks", sa.JSON()),
        sa.PrimaryKeyConstraint("game_id", "participant_id"),
    )

    op.create_table(
        "game_dragons",
        sa.Column("game_id", sa.String(), sa.ForeignKey("games.id", ondelete="CASCADE")),
        sa.Column("dragon_number", sa.Integer()),
        sa.Column(
            "team_id",
            sa.String(),
            sa.ForeignKey("professional_teams.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("dragon_type", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("game_id", "dragon_number"),
    )

    op.create_table(
        "professional_players",
        sa.Column("id", sa.String()),
        sa.Column(
            "team_id", sa.String(), sa.ForeignKey("professional_teams.id", ondelete="CASCADE")
        ),
        sa.Column("summoner_name", sa.String()),
        sa.Column("first_name", sa.String(), default=""),
        sa.Column("last_name", sa.String(), default=""),
        sa.Column("image", sa.String()),
        sa.Column("role", playerrole, nullable=False),
        sa.PrimaryKeyConstraint("id", "team_id"),
    )

    op.create_table(
        "player_game_metadata",
        sa.Column("game_id", sa.String(), sa.ForeignKey("games.id", ondelete="CASCADE")),
        sa.Column("player_id", sa.String()),
        sa.Column("participant_id", sa.Integer()),
        sa.Column("champion_id", sa.String()),
        sa.Column("role", playerrole, nullable=False),
        sa.PrimaryKeyConstraint("game_id", "player_id"),
    )

    op.create_table(
        "player_game_stats",
        sa.Column("game_id", sa.String(), sa.ForeignKey("games.id", ondelete="CASCADE")),
        sa.Column("participant_id", sa.Integer()),
        sa.Column("kills", sa.Integer()),
        sa.Column("deaths", sa.Integer()),
        sa.Column("assists", sa.Integer()),
        sa.Column("total_gold", sa.Integer()),
        sa.Column("creep_score", sa.Integer()),
        sa.Column("kill_participation", sa.Integer()),
        sa.Column("champion_damage_share", sa.Integer()),
        sa.Column("wards_placed", sa.Integer()),
        sa.Column("wards_destroyed", sa.Integer()),
        sa.PrimaryKeyConstraint("game_id", "participant_id"),
    )

    op.create_table(
        "team_game_stats",
        sa.Column("game_id", sa.String(), sa.ForeignKey("games.id", ondelete="CASCADE")),
        sa.Column(
            "team_id", sa.String(), sa.ForeignKey("professional_teams.id", ondelete="CASCADE")
        ),
        sa.Column("total_gold", sa.Integer()),
        sa.Column("inhibitors", sa.Integer()),
        sa.Column("towers", sa.Integer()),
        sa.Column("barons", sa.Integer()),
        sa.Column("total_kills", sa.Integer()),
        sa.PrimaryKeyConstraint("game_id", "team_id"),
    )

    # Fantasy tables
    op.create_table(
        "users",
        sa.Column("id", sa.String(), primary_key=True, unique=True, nullable=False),
        sa.Column("username", sa.String(), unique=True, nullable=False),
        sa.Column("email", sa.String(), unique=True, nullable=False),
        sa.Column("password", sa.LargeBinary(), nullable=False),
        sa.Column("permissions", sa.String()),
        sa.Column("account_status", useraccountstatus, nullable=False),
        sa.Column("verified", sa.Boolean(), default=False),
        sa.Column("verification_token", sa.String()),
    )

    op.create_table(
        "fantasy_leagues",
        sa.Column("id", sa.String(), primary_key=True, unique=True, nullable=False),
        sa.Column("owner_id", sa.String(), nullable=False),
        sa.Column("status", fantasyleaguestatus, nullable=False),
        sa.Column("name", sa.String()),
        sa.Column("number_of_teams", sa.Integer()),
        sa.Column("current_week", sa.Integer(), nullable=True),
        sa.Column("current_draft_position", sa.Integer(), nullable=True),
        sa.Column("available_leagues", sa.JSON()),
    )

    op.create_table(
        "fantasy_league_memberships",
        sa.Column("league_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("status", fantasyleaguemembershipstatus, nullable=False),
        sa.PrimaryKeyConstraint("league_id", "user_id"),
    )

    op.create_table(
        "fantasy_league_scoring_settings",
        sa.Column("fantasy_league_id", sa.String(), primary_key=True, nullable=False),
        sa.Column("kills", sa.Integer(), nullable=False),
        sa.Column("deaths", sa.Integer(), nullable=False),
        sa.Column("assists", sa.Float(), nullable=False),
        sa.Column("creep_score", sa.Float(), nullable=False),
        sa.Column("wards_placed", sa.Float(), nullable=False),
        sa.Column("wards_destroyed", sa.Float(), nullable=False),
        sa.Column("kill_participation", sa.Integer(), nullable=False),
        sa.Column("damage_percentage", sa.Integer(), nullable=False),
    )

    op.create_table(
        "fantasy_league_draft_order",
        sa.Column("fantasy_league_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("fantasy_league_id", "user_id"),
    )

    op.create_table(
        "fantasy_teams",
        sa.Column("fantasy_league_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("week", sa.Integer(), nullable=False),
        sa.Column("top_player_id", sa.String(), nullable=True),
        sa.Column("jungle_player_id", sa.String(), nullable=True),
        sa.Column("mid_player_id", sa.String(), nullable=True),
        sa.Column("adc_player_id", sa.String(), nullable=True),
        sa.Column("support_player_id", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("fantasy_league_id", "user_id", "week"),
    )

    # Views (raw SQL)
    op.execute("""
        CREATE VIEW player_game_view AS
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

    op.execute("""
        CREATE VIEW match_view AS
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

    op.execute("""
        CREATE VIEW game_view AS
        SELECT
            g.id,
            g.state,
            g.number,
            red.team_id AS red_team,
            blue.team_id AS blue_team,
            g.match_id,
            COALESCE(g.details_status != 'unavailable', TRUE) AS has_game_data,
            COALESCE(g.details_status = 'needs_final_fetch', FALSE) AS last_stats_fetch
        FROM games g
        LEFT JOIN game_teams red ON g.id = red.game_id AND red.side = 'red'
        LEFT JOIN game_teams blue ON g.id = blue.game_id AND blue.side = 'blue'
    """)


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS game_view")
    op.execute("DROP VIEW IF EXISTS match_view")
    op.execute("DROP VIEW IF EXISTS player_game_view")

    op.drop_table("fantasy_teams")
    op.drop_table("fantasy_league_draft_order")
    op.drop_table("fantasy_league_scoring_settings")
    op.drop_table("fantasy_league_memberships")
    op.drop_table("fantasy_leagues")
    op.drop_table("users")
    op.drop_table("team_game_stats")
    op.drop_table("player_game_stats")
    op.drop_table("player_game_metadata")
    op.drop_table("professional_players")
    op.drop_table("game_dragons")
    op.drop_table("game_participant_perks")
    op.drop_table("game_metadata")
    op.drop_table("game_teams")
    op.drop_table("games")
    op.drop_table("event_teams")
    op.drop_table("matches")
    op.drop_table("professional_teams")
    op.drop_table("tournaments")
    op.drop_table("leagues")

    useraccountstatus.drop(op.get_bind(), checkfirst=True)
    fantasyleaguemembershipstatus.drop(op.get_bind(), checkfirst=True)
    fantasyleaguestatus.drop(op.get_bind(), checkfirst=True)
    playerrole.drop(op.get_bind(), checkfirst=True)
    gamestate.drop(op.get_bind(), checkfirst=True)
    matchstate.drop(op.get_bind(), checkfirst=True)
