from sqlalchemy import text

from src.common.schemas.riot_data_schemas import (
    RiotGameID,
    PlayerGameData,
    PlayerGameStats,
    PlayerMatchHistoryEntry,
    ProPlayerID,
)
from src.db.models import PlayerGameStatsModel
from src.db.views import PlayerGameView


def put_player_stats(session, player_stats: PlayerGameStats) -> None:
    db_player_stats = PlayerGameStatsModel(**player_stats.model_dump())
    session.merge(db_player_stats)
    session.commit()


def get_player_stats(session, game_id: RiotGameID, participant_id: int) -> PlayerGameStats | None:
    db_player_game_stats: PlayerGameStatsModel | None = (
        session.query(PlayerGameStatsModel)
        .filter(
            PlayerGameStatsModel.game_id == game_id,
            PlayerGameStatsModel.participant_id == participant_id,
        )
        .first()
    )
    if db_player_game_stats is None:
        return None
    else:
        return PlayerGameStats.model_validate(db_player_game_stats)


def get_game_ids_to_fetch_player_stats_for(session) -> list[RiotGameID]:
    sql_query = """
        SELECT games.id as game_id
        FROM games
        JOIN matches ON games.match_id = matches.id
        JOIN leagues ON matches.league_id = leagues.id
        LEFT JOIN player_game_stats ON games.id = player_game_stats.game_id
        WHERE ((games.state = 'completed'
                AND (SELECT COUNT(*) FROM player_game_stats WHERE game_id = games.id) < 10)
                OR games.state = 'inProgress')
            AND (games.details_status IS NULL OR games.details_status != 'unavailable')
            AND leagues.scrape_enabled = true
        GROUP BY games.id
    """
    result = session.execute(text(sql_query))
    rows = result.fetchall()
    game_ids = [RiotGameID(row[0]) for row in rows]
    return game_ids


def get_player_game_stats(session, filters: list | None = None) -> list[PlayerGameData]:
    if filters:
        query = session.query(PlayerGameView).filter(*filters)
    else:
        query = session.query(PlayerGameView)

    db_player_game_stat: list[PlayerGameView] = query.all()
    player_game_data = [
        PlayerGameData.model_validate(db_player_game_stat)
        for db_player_game_stat in db_player_game_stat
    ]
    return player_game_data


# SQL for a player's enriched match history. The player's side, opponent and
# match-level result are resolved from the player's actual team membership
# (professional_players.team_id) matched against the game's teams (game_teams),
# NOT from the participant id -> side convention which is unreliable in the data
# (blue/red is not consistently ordered the same way as participant ids).
_MATCH_HISTORY_SQL = text("""
    SELECT
        pgv.game_id, pgv.player_id, pgv.participant_id, pgv.champion_id, pgv.role,
        pgv.kills, pgv.deaths, pgv.assists, pgv.total_gold, pgv.creep_score,
        pgv.kill_participation, pgv.champion_damage_share, pgv.wards_placed, pgv.wards_destroyed,
        pgv.match_id, pgv.duration_seconds, pgv.start_time, pgv.block_name, pgv.league_slug,
        pgv.patch_version,
        gt_self.side AS side,
        opp.code AS opponent_code,
        opp.name AS opponent_name,
        et.outcome AS outcome
    FROM player_game_view pgv
    LEFT JOIN game_teams gt_self
        ON gt_self.game_id = pgv.game_id
        AND gt_self.team_id IN (SELECT team_id FROM professional_players WHERE id = pgv.player_id)
    LEFT JOIN game_teams gt_opp
        ON gt_opp.game_id = pgv.game_id AND gt_opp.team_id <> gt_self.team_id
    LEFT JOIN professional_teams opp ON opp.id = gt_opp.team_id
    LEFT JOIN event_teams et ON et.match_id = pgv.match_id AND et.team_id = gt_self.team_id
    WHERE pgv.player_id = :player_id
    ORDER BY pgv.start_time DESC NULLS LAST, pgv.game_id DESC
""")

_MULTI_KILLS_FOR_PLAYER_SQL = text("""
    SELECT mk.game_id, mk.kill_type
    FROM game_multi_kills mk
    JOIN player_game_metadata pm
        ON pm.game_id = mk.game_id AND pm.participant_id = mk.participant_id
    WHERE pm.player_id = :player_id
""")


def _per_min(value: int | None, duration_seconds: int | None) -> float | None:
    if not value or not duration_seconds:
        return None
    return round(value / (duration_seconds / 60), 2)


def get_player_match_history(session, player_id: ProPlayerID) -> list[PlayerMatchHistoryEntry]:
    """Return a player's games (newest first) enriched with opponent, match-level
    result, per-minute stats and multi-kill tags."""
    rows = session.execute(_MATCH_HISTORY_SQL, {"player_id": player_id}).mappings().all()

    # Group multi-kills by game for this player (one extra query, avoids N+1).
    multi_kills_by_game: dict[str, list[str]] = {}
    mk_rows = (
        session.execute(_MULTI_KILLS_FOR_PLAYER_SQL, {"player_id": player_id}).mappings().all()
    )
    for mk in mk_rows:
        multi_kills_by_game.setdefault(mk["game_id"], []).append(mk["kill_type"])

    history: list[PlayerMatchHistoryEntry] = []
    for row in rows:
        outcome = row["outcome"]
        win = None if outcome is None else outcome == "win"
        duration = row["duration_seconds"]
        history.append(
            PlayerMatchHistoryEntry(
                game_id=row["game_id"],
                player_id=row["player_id"],
                match_id=row["match_id"],
                participant_id=row["participant_id"],
                champion_id=row["champion_id"],
                role=row["role"],
                kills=row["kills"] or 0,
                deaths=row["deaths"] or 0,
                assists=row["assists"] or 0,
                total_gold=row["total_gold"] or 0,
                creep_score=row["creep_score"] or 0,
                kill_participation=row["kill_participation"] or 0,
                champion_damage_share=row["champion_damage_share"] or 0,
                wards_placed=row["wards_placed"] or 0,
                wards_destroyed=row["wards_destroyed"] or 0,
                start_time=row["start_time"],
                block_name=row["block_name"],
                league_slug=row["league_slug"],
                patch_version=row["patch_version"],
                duration_seconds=duration,
                side=row["side"],
                opponent_code=row["opponent_code"],
                opponent_name=row["opponent_name"],
                win=win,
                multi_kills=multi_kills_by_game.get(row["game_id"], []),
                cs_per_min=_per_min(row["creep_score"], duration),
                gold_per_min=_per_min(row["total_gold"], duration),
            )
        )
    return history
