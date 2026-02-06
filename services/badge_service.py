def calculate_badge(trust_score: float, contributions: int) -> dict:
    """
    Determine user badge based on trust score and contribution count.

    Returns:
        {
            "level": "Gold" | "Silver" | "Bronze" | "None",
            "icon": "🥇" | "🥈" | "🥉" | "",
            "color": "#hex"
        }
    """

    if trust_score >= 85 and contributions >= 25:
        return {
            "level": "Gold",
            "icon": "🥇",
            "color": "#FFD700"
        }

    elif trust_score >= 65 and contributions >= 12:
        return {
            "level": "Silver",
            "icon": "🥈",
            "color": "#C0C0C0"
        }

    elif trust_score >= 45 and contributions >= 5:
        return {
            "level": "Bronze",
            "icon": "🥉",
            "color": "#CD7F32"
        }

    return {
        "level": "None",
        "icon": "",
        "color": "#9CA3AF"  # gray
    }
