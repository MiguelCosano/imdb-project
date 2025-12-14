"""Formatting utilities for IMDb data presentation."""


def format_professions(professions: str | None) -> str:
    """
    Apply formatting to all possible professions in IMDb dataset actors
    Example: "actor,producer,director" -> "an actor, a producer, and a director"
    """
    if not professions:
        return "profession: unknown profession"

    prof_list = [p.strip() for p in professions.split(",")]
    formatted = [p.replace("_", " ") for p in prof_list]

    if len(formatted) == 0:
        return "profession: unknown profession"
    elif len(formatted) == 1:
        return f"profession: {formatted[0]}"
    elif len(formatted) == 2:
        return f"professions: {formatted[0]} and {formatted[1]}"
    else:
        return f"professions: {', '.join(formatted[:-1])}, and {formatted[-1]}"


def format_genres(genres: str | None) -> str:
    """
    Apply formatting to all possible genres in IMDb dataset movies
    Example: "Documentary,Short" -> "a Documentary and a Short"
    """
    if not genres:
        return "an unknown genre"

    def add_article(genre: str) -> str:
        vowels = ("a", "e", "i", "o", "u")
        if genre[0].lower() in vowels:
            return f"an {genre}"
        return f"a {genre}"

    genres_list = [g.strip() for g in genres.split(",")]
    formatted = [add_article(g) for g in genres_list]

    if len(formatted) == 0:
        return "an unknown genre"
    elif len(formatted) == 1:
        return formatted[0]
    elif len(formatted) == 2:
        return f"{formatted[0]} and {formatted[1]}"
    else:
        return f"{', '.join(formatted[:-1])}, and {formatted[-1]}"


def is_dead_or_alive(is_dead: bool) -> str:
    """Return 'is' or 'was' based on is_dead boolean"""
    return "had" if is_dead else "has"


def plural_s(amount: int) -> str:
    """Returns 's' for plural, '' for singular."""
    return "s" if abs(amount) != 1 else ""
