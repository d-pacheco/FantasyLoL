import logging

from src.common.schemas.fantasy_schemas import (
    FantasyLeagueID,
    FantasyLeagueMembership,
    FantasyLeagueMembershipStatus,
    FantasyLeagueScoringSettings,
    FantasyLeagueStatus,
    FantasyTeam,
    UserID,
)
from src.common.schemas.riot_data_schemas import (
    Match,
    ProPlayerID,
    ProTeamID,
    RiotGameID,
    RiotLeagueID,
    RiotMatchID,
)
from src.db.database_service import DatabaseService
from src.fantasy.scoring.engine import compute_player_score, compute_team_score
from src.fantasy.util import FantasyLeagueUtil

logger = logging.getLogger("api.fantasy")

ROSTER_SLOTS = ["top", "jungle", "mid", "adc", "support", "team"]
PLAYER_SLOTS = ["top", "jungle", "mid", "adc", "support"]


class LeaderboardService:
    def __init__(self, database_service: DatabaseService):
        self.db = database_service
        self.fantasy_league_util = FantasyLeagueUtil(database_service)

    def get_leaderboard(
        self, league_id: FantasyLeagueID, user_id: UserID
    ) -> dict:
        """Get the leaderboard for a fantasy league.

        Returns ranked members with total points from start_week to current_week.
        Past week scores are read from fantasy_scores (lazy-written if missing).
        Current week scores are computed on-demand.
        """
        # Validate league exists and is in correct state
        fantasy_league = self.fantasy_league_util.validate_league(
            league_id, [FantasyLeagueStatus.ACTIVE, FantasyLeagueStatus.COMPLETED]
        )

        # Validate caller is a member
        self.fantasy_league_util.validate_membership(user_id, league_id)

        # Get all accepted members
        members = self.db.get_pending_and_accepted_members_for_league(league_id)
        accepted_members: list[FantasyLeagueMembership] = [
            m for m in members
            if m.status == FantasyLeagueMembershipStatus.ACCEPTED
        ]

        # Determine week range
        start_week: int = fantasy_league.start_week or 1
        riot_league_id: RiotLeagueID = fantasy_league.available_leagues[0]
        current_week_result: int | None = self.fantasy_league_util.get_leagues_current_week(
            riot_league_id
        )
        current_week: int = current_week_result if current_week_result is not None else start_week

        # Get scoring settings
        scoring_settings: FantasyLeagueScoringSettings | None = (
            self.db.get_fantasy_league_scoring_settings_by_id(league_id)
        )
        if scoring_settings is None:
            return {
                "fantasy_league_id": league_id,
                "current_week": current_week,
                "start_week": start_week,
                "members": [],
            }

        # Compute total points per member
        member_totals: dict[str, float] = {m.user_id: 0.0 for m in accepted_members}

        for week in range(start_week, current_week + 1):
            # Check for stored scores first
            stored_scores = self.db.get_fantasy_scores_for_week(league_id, week)
            if stored_scores:
                for score in stored_scores:
                    if score.user_id in member_totals:
                        member_totals[score.user_id] += score.points
                continue

            # Compute scores for this week
            week_scores: dict[str, list[dict]] = self._compute_week_scores(
                league_id, accepted_members, week, riot_league_id, scoring_settings
            )

            # Determine if we should store (no in-progress matches for this week)
            should_store: bool = not self._has_in_progress_matches(riot_league_id, week)

            for uid, slot_scores in week_scores.items():
                for slot_data in slot_scores:
                    member_totals[uid] += slot_data["points"]

                    if should_store:
                        self.db.put_fantasy_score({
                            "fantasy_league_id": league_id,
                            "user_id": uid,
                            "week": week,
                            "slot": slot_data["slot"],
                            "player_id": slot_data.get("player_id"),
                            "team_id": slot_data.get("team_id"),
                            "points": slot_data["points"],
                            "breakdown": slot_data["breakdown"],
                        })

        # Build ranked response
        ranked_members: list[dict] = []
        for member in accepted_members:
            user = self.db.get_user_by_id(member.user_id)
            username: str = user.username if user else member.user_id
            ranked_members.append({
                "user_id": member.user_id,
                "username": username,
                "total_points": round(member_totals[member.user_id], 2),
            })

        ranked_members.sort(key=lambda m: m["total_points"], reverse=True)
        for i, member_entry in enumerate(ranked_members):
            member_entry["position"] = i + 1

        return {
            "fantasy_league_id": league_id,
            "current_week": current_week,
            "start_week": start_week,
            "members": ranked_members,
        }

    def _compute_week_scores(
        self,
        league_id: FantasyLeagueID,
        members: list[FantasyLeagueMembership],
        week: int,
        riot_league_id: RiotLeagueID,
        scoring_settings: FantasyLeagueScoringSettings,
    ) -> dict[str, list[dict]]:
        """Compute scores for all members for a given week.

        Returns dict[user_id -> list of slot score dicts].
        """
        matches: list[Match] = self._get_matches_for_week(riot_league_id, week)

        result: dict[str, list[dict]] = {}

        for member in members:
            roster: FantasyTeam | None = self._get_member_roster(
                league_id, member.user_id, week
            )
            slot_scores: list[dict] = []

            for slot in PLAYER_SLOTS:
                player_id: ProPlayerID | None = self._get_roster_player_id(roster, slot)
                if player_id is None:
                    slot_scores.append({
                        "slot": slot, "player_id": None, "points": 0.0, "breakdown": {}
                    })
                    continue

                score: dict = self._compute_player_week_score(
                    player_id, matches, scoring_settings
                )
                slot_scores.append({
                    "slot": slot,
                    "player_id": player_id,
                    "points": score["total"],
                    "breakdown": score["breakdown"],
                })

            # Team slot
            team_id: ProTeamID | None = ProTeamID(roster.team_id) if roster and roster.team_id else None
            if team_id is None:
                slot_scores.append({
                    "slot": "team", "team_id": None, "points": 0.0, "breakdown": {}
                })
            else:
                score = self._compute_team_week_score(
                    team_id, matches, scoring_settings
                )
                slot_scores.append({
                    "slot": "team",
                    "team_id": team_id,
                    "points": score["total"],
                    "breakdown": score["breakdown"],
                })

            result[member.user_id] = slot_scores

        return result

    def _get_matches_for_week(self, riot_league_id: RiotLeagueID, week: int) -> list[Match]:
        """Get all completed matches for a given week in the league's active tournament."""
        all_matches: list[Match] = self.db.get_matches_for_league_with_active_tournament(
            riot_league_id
        )
        week_block: str = f"Week {week}"
        return [
            m for m in all_matches
            if m.block_name and m.block_name.lower() == week_block.lower()
            and m.state and m.state.value == "completed"
        ]

    def _has_in_progress_matches(self, riot_league_id: RiotLeagueID, week: int) -> bool:
        """Check if there are any in-progress matches for a given week."""
        all_matches: list[Match] = self.db.get_matches_for_league_with_active_tournament(
            riot_league_id
        )
        week_block: str = f"Week {week}"
        return any(
            m for m in all_matches
            if m.block_name and m.block_name.lower() == week_block.lower()
            and m.state and m.state.value == "inProgress"
        )

    def _get_member_roster(
        self, league_id: FantasyLeagueID, user_id: UserID, week: int
    ) -> FantasyTeam | None:
        """Get a member's roster for a specific week."""
        teams: list[FantasyTeam] = self.db.get_all_fantasy_teams_for_user(league_id, user_id)
        teams.sort(key=lambda t: t.week)
        roster: FantasyTeam | None = None
        for team in teams:
            if team.week <= week:
                roster = team
        return roster

    def _get_roster_player_id(self, roster: FantasyTeam | None, slot: str) -> ProPlayerID | None:
        """Get the player ID for a given slot from a roster."""
        if roster is None:
            return None
        slot_map: dict[str, ProPlayerID | None] = {
            "top": roster.top_player_id,
            "jungle": roster.jungle_player_id,
            "mid": roster.mid_player_id,
            "adc": roster.adc_player_id,
            "support": roster.support_player_id,
        }
        return slot_map.get(slot)

    def _compute_player_week_score(
        self,
        player_id: ProPlayerID,
        matches: list[Match],
        scoring_settings: FantasyLeagueScoringSettings,
    ) -> dict:
        """Compute a player's total score across all matches in a week."""
        all_game_stats: list[dict] = []
        all_durations: list[int] = []
        all_multi_kills: list[dict] = []

        for match in matches:
            games: list[dict] = self.db.get_games_for_match(match.id)
            game_stats_for_match: list[dict] = []
            durations_for_match: list[int] = []
            multi_kills_for_match: list[dict] = []

            for game in games:
                game_id: RiotGameID = RiotGameID(game["id"])
                stats: dict | None = self.db.get_player_stats_for_game(game_id, player_id)
                if stats is None:
                    continue
                game_stats_for_match.append(stats)
                durations_for_match.append(game.get("duration_seconds") or 0)

                mks: list[dict] = self.db.get_multi_kills_for_game_and_player(
                    game_id, player_id
                )
                game_idx: int = len(game_stats_for_match) - 1
                for mk in mks:
                    multi_kills_for_match.append({
                        "kill_type": mk["kill_type"],
                        "game_index": game_idx,
                    })

            if game_stats_for_match:
                all_game_stats.extend(game_stats_for_match)
                all_durations.extend(durations_for_match)
                all_multi_kills.extend(multi_kills_for_match)

        if not all_game_stats:
            return {"total": 0.0, "breakdown": {}}

        return compute_player_score(
            all_game_stats, all_durations, all_multi_kills, scoring_settings
        )

    def _compute_team_week_score(
        self,
        team_id: ProTeamID,
        matches: list[Match],
        scoring_settings: FantasyLeagueScoringSettings,
    ) -> dict:
        """Compute a team's total score across all matches in a week."""
        all_game_stats: list[dict] = []
        all_dragons: list[dict] = []
        total_match_wins: int = 0
        total_match_sweeps: int = 0

        for match in matches:
            games: list[dict] = self.db.get_games_for_match(match.id)
            game_stats_for_match: list[dict] = []
            dragons_for_match: list[dict] = []

            for game in games:
                game_id: RiotGameID = RiotGameID(game["id"])
                stats: dict | None = self.db.get_team_stats_for_game(game_id, team_id)
                if stats is None:
                    continue
                game_stats_for_match.append(stats)

                game_dragons: list[dict] = self.db.get_dragons_for_game_and_team(
                    game_id, team_id
                )
                game_idx: int = len(game_stats_for_match) - 1
                for d in game_dragons:
                    dragons_for_match.append({
                        "dragon_type": d["dragon_type"],
                        "game_index": game_idx,
                    })

            if game_stats_for_match:
                # Determine match outcome
                match_won: bool = False
                match_swept: bool = False
                if hasattr(match, "winning_team") and match.winning_team:
                    team = self.db.get_team_by_id(team_id)
                    if team and team.name == match.winning_team:
                        match_won = True
                        total_games: int = len(games)
                        team_games_played: int = len(game_stats_for_match)
                        opponent_wins: int = total_games - team_games_played
                        if opponent_wins == 0 and total_games > 1:
                            match_swept = True

                match_score: dict = compute_team_score(
                    game_stats_for_match, dragons_for_match,
                    match_won, match_swept, scoring_settings
                )

                all_game_stats.extend(game_stats_for_match)
                all_dragons.extend(dragons_for_match)
                total_match_wins += (1 if match_won else 0)
                total_match_sweeps += (1 if match_swept else 0)

        if not all_game_stats:
            return {"total": 0.0, "breakdown": {}}

        # Compute base score with all games across the week (per-game averaged)
        # but without match bonuses (those are per-match, not per-game)
        base_score: dict = compute_team_score(
            all_game_stats, all_dragons, False, False, scoring_settings
        )
        # Override match bonuses with accumulated per-match values
        base_score["breakdown"]["match_win"] = total_match_wins * scoring_settings.match_win
        base_score["breakdown"]["match_sweep"] = (
            total_match_sweeps * scoring_settings.match_sweep
        )
        base_score["total"] = sum(base_score["breakdown"].values())

        return base_score

    def get_week_scores(
        self, league_id: FantasyLeagueID, user_id: UserID, week: int
    ) -> dict:
        """Get detailed scoring breakdown for a specific week.

        Returns per-member roster detail with points and per-category breakdown.
        Past weeks are read from fantasy_scores (lazy-written if missing).
        Current week is computed on-demand.
        """
        # Validate league exists and is in correct state
        fantasy_league = self.fantasy_league_util.validate_league(
            league_id, [FantasyLeagueStatus.ACTIVE, FantasyLeagueStatus.COMPLETED]
        )

        # Validate caller is a member
        self.fantasy_league_util.validate_membership(user_id, league_id)

        # Determine week range
        start_week: int = fantasy_league.start_week or 1
        riot_league_id: RiotLeagueID = fantasy_league.available_leagues[0]
        current_week_result: int | None = self.fantasy_league_util.get_leagues_current_week(
            riot_league_id
        )
        current_week: int = current_week_result if current_week_result is not None else start_week

        # Validate requested week is in range
        if week < start_week or week > current_week:
            from fastapi import HTTPException
            from http import HTTPStatus
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f"Week {week} is out of range. Valid range: {start_week} to {current_week}.",
            )

        # Get all accepted members
        members = self.db.get_pending_and_accepted_members_for_league(league_id)
        accepted_members: list[FantasyLeagueMembership] = [
            m for m in members
            if m.status == FantasyLeagueMembershipStatus.ACCEPTED
        ]

        # Get scoring settings
        scoring_settings: FantasyLeagueScoringSettings | None = (
            self.db.get_fantasy_league_scoring_settings_by_id(league_id)
        )
        if scoring_settings is None:
            return {
                "fantasy_league_id": league_id,
                "week": week,
                "members": [],
            }

        is_current_week: bool = (week == current_week)

        # Try to read stored scores
        stored_scores = self.db.get_fantasy_scores_for_week(league_id, week)
        if stored_scores:
            return self._build_week_response_from_stored(
                league_id, week, accepted_members, stored_scores
            )

        # Compute scores
        week_scores: dict[str, list[dict]] = self._compute_week_scores(
            league_id, accepted_members, week, riot_league_id, scoring_settings
        )

        # Store if no in-progress matches for this week
        should_store: bool = not self._has_in_progress_matches(riot_league_id, week)
        if should_store:
            for uid, slot_scores in week_scores.items():
                for slot_data in slot_scores:
                    self.db.put_fantasy_score({
                        "fantasy_league_id": league_id,
                        "user_id": uid,
                        "week": week,
                        "slot": slot_data["slot"],
                        "player_id": slot_data.get("player_id"),
                        "team_id": slot_data.get("team_id"),
                        "points": slot_data["points"],
                        "breakdown": slot_data["breakdown"],
                    })

        return self._build_week_response_from_computed(
            league_id, week, accepted_members, week_scores
        )

    def _build_week_response_from_stored(
        self,
        league_id: FantasyLeagueID,
        week: int,
        members: list[FantasyLeagueMembership],
        stored_scores: list,
    ) -> dict:
        """Build the week scores response from stored fantasy_scores rows."""
        # Group scores by user
        scores_by_user: dict[str, list] = {}
        for score in stored_scores:
            if score.user_id not in scores_by_user:
                scores_by_user[score.user_id] = []
            scores_by_user[score.user_id].append(score)

        member_entries: list[dict] = []
        for member in members:
            user = self.db.get_user_by_id(member.user_id)
            username: str = user.username if user else member.user_id
            user_scores = scores_by_user.get(member.user_id, [])

            roster: dict = {}
            total_points: float = 0.0
            for score in user_scores:
                slot_entry: dict = {
                    "points": score.points,
                    "breakdown": score.breakdown,
                }
                if score.slot == "team":
                    slot_entry["team_id"] = score.team_id
                    slot_entry["team_name"] = self._resolve_team_name(score.team_id)
                else:
                    slot_entry["player_id"] = score.player_id
                    slot_entry["summoner_name"] = self._resolve_player_name(score.player_id)
                roster[score.slot] = slot_entry
                total_points += score.points

            member_entries.append({
                "user_id": member.user_id,
                "username": username,
                "total_points": round(total_points, 2),
                "roster": roster,
            })

        return {
            "fantasy_league_id": league_id,
            "week": week,
            "members": member_entries,
        }

    def _build_week_response_from_computed(
        self,
        league_id: FantasyLeagueID,
        week: int,
        members: list[FantasyLeagueMembership],
        week_scores: dict[str, list[dict]],
    ) -> dict:
        """Build the week scores response from freshly computed scores."""
        member_entries: list[dict] = []
        for member in members:
            user = self.db.get_user_by_id(member.user_id)
            username: str = user.username if user else member.user_id
            slot_scores = week_scores.get(member.user_id, [])

            roster: dict = {}
            total_points: float = 0.0
            for slot_data in slot_scores:
                slot: str = slot_data["slot"]
                slot_entry: dict = {
                    "points": slot_data["points"],
                    "breakdown": slot_data["breakdown"],
                }
                if slot == "team":
                    slot_entry["team_id"] = slot_data.get("team_id")
                    slot_entry["team_name"] = self._resolve_team_name(slot_data.get("team_id"))
                else:
                    slot_entry["player_id"] = slot_data.get("player_id")
                    slot_entry["summoner_name"] = self._resolve_player_name(
                        slot_data.get("player_id")
                    )
                roster[slot] = slot_entry
                total_points += slot_data["points"]

            member_entries.append({
                "user_id": member.user_id,
                "username": username,
                "total_points": round(total_points, 2),
                "roster": roster,
            })

        return {
            "fantasy_league_id": league_id,
            "week": week,
            "members": member_entries,
        }

    def _resolve_player_name(self, player_id: str | None) -> str | None:
        """Resolve a player ID to their summoner name."""
        if player_id is None:
            return None
        player = self.db.get_player_by_id(ProPlayerID(player_id))
        return player.summoner_name if player else None

    def _resolve_team_name(self, team_id: str | None) -> str | None:
        """Resolve a team ID to their name."""
        if team_id is None:
            return None
        team = self.db.get_team_by_id(ProTeamID(team_id))
        return team.name if team else None
