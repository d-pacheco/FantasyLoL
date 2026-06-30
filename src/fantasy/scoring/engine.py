from src.common.schemas.fantasy_schemas import FantasyLeagueScoringSettings


def compute_player_score(
    game_stats: list[dict],
    game_durations: list[int],
    multi_kills: list[dict],
    weights: FantasyLeagueScoringSettings,
) -> dict:
    """Compute fantasy points for a player across games in a single match.

    Args:
        game_stats: List of stat dicts per game (kills, deaths, assists, creep_score,
                    wards_placed, wards_destroyed, kill_participation, champion_damage_share).
        game_durations: List of game durations in seconds (parallel to game_stats).
        multi_kills: List of multi-kill dicts with 'kill_type' and 'game_index'.
        weights: The league's scoring settings.

    Returns:
        Dict with 'total' (float) and 'breakdown' (dict of category → points).
        Stats are averaged per game. CSPM is computed per game then averaged.
    """
    num_games = len(game_stats)

    if num_games == 0:
        return {
            "total": 0.0,
            "breakdown": {
                "kills": 0.0,
                "deaths": 0.0,
                "assists": 0.0,
                "cspm": 0.0,
                "wards_placed": 0.0,
                "wards_destroyed": 0.0,
                "kill_participation": 0.0,
                "damage_percentage": 0.0,
                "double_kill": 0.0,
                "triple_kill": 0.0,
                "quadra_kill": 0.0,
                "penta_kill": 0.0,
            },
        }

    # Sum basic stats across games
    total_kills = sum(g.get("kills", 0) for g in game_stats)
    total_deaths = sum(g.get("deaths", 0) for g in game_stats)
    total_assists = sum(g.get("assists", 0) for g in game_stats)
    total_wards_placed = sum(g.get("wards_placed", 0) for g in game_stats)
    total_wards_destroyed = sum(g.get("wards_destroyed", 0) for g in game_stats)
    total_kill_participation = sum(g.get("kill_participation", 0) for g in game_stats)
    total_damage_share = sum(g.get("champion_damage_share", 0) for g in game_stats)

    # Average per game
    avg_kills = total_kills / num_games
    avg_deaths = total_deaths / num_games
    avg_assists = total_assists / num_games
    avg_wards_placed = total_wards_placed / num_games
    avg_wards_destroyed = total_wards_destroyed / num_games
    avg_kill_participation = total_kill_participation / num_games
    avg_damage_share = total_damage_share / num_games

    # CSPM: compute per game (creep_score / duration_minutes), then average
    cspm_values = []
    for i, g in enumerate(game_stats):
        duration = game_durations[i] if i < len(game_durations) else 0
        if duration > 0:
            duration_minutes = duration / 60
            cspm_values.append(g.get("creep_score", 0) / duration_minutes)
    avg_cspm = sum(cspm_values) / num_games if num_games > 0 else 0.0
    # If all games had 0 duration, cspm is 0
    if len(cspm_values) == 0:
        avg_cspm = 0.0

    # Multi-kills: count by type, then average per game
    multi_kill_counts = {"Double": 0, "Triple": 0, "Quadra": 0, "Penta": 0}
    for mk in multi_kills:
        kill_type = mk.get("kill_type", "")
        if kill_type in multi_kill_counts:
            multi_kill_counts[kill_type] += 1

    avg_double = multi_kill_counts["Double"] / num_games
    avg_triple = multi_kill_counts["Triple"] / num_games
    avg_quadra = multi_kill_counts["Quadra"] / num_games
    avg_penta = multi_kill_counts["Penta"] / num_games

    # Apply weights
    breakdown = {
        "kills": avg_kills * weights.kills,
        "deaths": avg_deaths * weights.deaths,
        "assists": avg_assists * weights.assists,
        "cspm": avg_cspm * weights.cspm,
        "wards_placed": avg_wards_placed * weights.wards_placed,
        "wards_destroyed": avg_wards_destroyed * weights.wards_destroyed,
        "kill_participation": avg_kill_participation * weights.kill_participation,
        "damage_percentage": avg_damage_share * weights.damage_percentage,
        "double_kill": avg_double * weights.double_kill,
        "triple_kill": avg_triple * weights.triple_kill,
        "quadra_kill": avg_quadra * weights.quadra_kill,
        "penta_kill": avg_penta * weights.penta_kill,
    }

    total = sum(breakdown.values())

    return {"total": total, "breakdown": breakdown}


def compute_team_score(
    game_stats: list[dict],
    dragons: list[dict],
    match_won: bool,
    match_swept: bool,
    weights: FantasyLeagueScoringSettings,
) -> dict:
    """Compute fantasy points for a rostered team across games in a single match.

    Args:
        game_stats: List of stat dicts per game (barons, towers, inhibitors).
        dragons: List of dragon dicts with 'dragon_type' and 'game_index'.
        match_won: Whether the team won the match.
        match_swept: Whether the team swept (won without dropping a game).
        weights: The league's scoring settings.

    Returns:
        Dict with 'total' (float) and 'breakdown' (dict of category → points).
        Team stats are averaged per game. Dragon Soul is summed (not averaged).
        Match bonuses are applied once per match and stack.
    """
    num_games = len(game_stats)

    if num_games == 0:
        return {
            "total": 0.0,
            "breakdown": {
                "dragon": 0.0,
                "elder_dragon": 0.0,
                "baron": 0.0,
                "tower": 0.0,
                "inhibitor": 0.0,
                "soul": 0.0,
                "match_win": 0.0,
                "match_sweep": 0.0,
            },
        }

    # Sum basic team stats across games
    total_barons = sum(g.get("barons", 0) for g in game_stats)
    total_towers = sum(g.get("towers", 0) for g in game_stats)
    total_inhibitors = sum(g.get("inhibitors", 0) for g in game_stats)

    # Average per game
    avg_barons = total_barons / num_games
    avg_towers = total_towers / num_games
    avg_inhibitors = total_inhibitors / num_games

    # Dragons: split by type, count per game for averaging
    regular_dragon_count = 0
    elder_dragon_count = 0
    # Track non-elder dragons per game for soul detection
    non_elder_per_game: dict[int, int] = {}

    for d in dragons:
        game_idx = d.get("game_index", 0)
        if d.get("dragon_type") == "elder":
            elder_dragon_count += 1
        else:
            regular_dragon_count += 1
            non_elder_per_game[game_idx] = non_elder_per_game.get(game_idx, 0) + 1

    avg_dragons = regular_dragon_count / num_games
    avg_elders = elder_dragon_count / num_games

    # Dragon Soul: ≥4 non-elder dragons in a single game, summed across games (not averaged)
    soul_count = sum(1 for count in non_elder_per_game.values() if count >= 4)

    # Match bonuses (applied once, not per game)
    win_bonus = 1.0 if match_won else 0.0
    sweep_bonus = 1.0 if match_swept else 0.0

    # Apply weights
    breakdown = {
        "dragon": avg_dragons * weights.dragon,
        "elder_dragon": avg_elders * weights.elder_dragon,
        "baron": avg_barons * weights.baron,
        "tower": avg_towers * weights.tower,
        "inhibitor": avg_inhibitors * weights.inhibitor,
        "soul": soul_count * weights.soul,
        "match_win": win_bonus * weights.match_win,
        "match_sweep": sweep_bonus * weights.match_sweep,
    }

    total = sum(breakdown.values())

    return {"total": total, "breakdown": breakdown}
