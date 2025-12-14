"""Formatting utilities for IMDb data presentation."""


def format_professions(professions: str | None) -> str:
    """
    Apply formatting to all possible professions in IMDb dataset actors
    Example: "actor,producer,director" -> "an actor, a producer, and a director"
    """
    if not professions:
        return "unknown profession"

    profession_format = {
        "actor": "an actor",
        "actress": "an actress",
        "producer": "a producer",
        "director": "a director",
        "writer": "a writer",
        "composer": "a composer",
        "cinematographer": "a cinematographer",
        "editor": "an editor",
        "animation_department": "in the animation department",
        "art_department": "in the art department",
        "art_director": "an art director",
        "assistant": "an assistant",
        "assistant_director": "an assistant director",
        "camera_department": "in the camera department",
        "casting_department": "in the casting department",
        "casting_director": "a casting director",
        "choreographer": "a choreographer",
        "costume_department": "in the costume department",
        "costume_designer": "a costume designer",
        "editorial_department": "in the editorial department",
        "electrical_department": "in the electrical department",
        "executive": "an executive",
        "legal": "in legal",
        "location_management": "in location management",
        "make_up_department": "in the make-up department",
        "manager": "a manager",
        "miscellaneous": "in miscellaneous roles",
        "music_artist": "a music artist",
        "music_department": "in the music department",
        "podcaster": "a podcaster",
        "production_department": "in the production department",
        "production_designer": "a production designer",
        "production_manager": "a production manager",
        "publicist": "a publicist",
        "script_department": "in the script department",
        "set_decorator": "a set decorator",
        "sound_department": "in the sound department",
        "soundtrack": "in soundtracks",
        "special_effects": "in special effects",
        "stunts": "a stunt performer",
        "talent_agent": "a talent agent",
        "transportation_department": "in the transportation department",
        "visual_effects": "in visual effects",
        "archive_footage": "in archive footage",
        "archive_sound": "in archive sound",
        "accountant": "an accountant",
    }

    prof_list = [p.strip() for p in professions.split(",")]
    formatted = [profession_format.get(p, p.replace("_", " ")) for p in prof_list]

    if len(formatted) == 0:
        return "unknown profession"
    elif len(formatted) == 1:
        return formatted[0]
    elif len(formatted) == 2:
        return f"{formatted[0]} and {formatted[1]}"
    else:
        return f"{', '.join(formatted[:-1])}, and {formatted[-1]}"


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
    return "was" if is_dead else "is"


def plural_s(amount: int) -> str:
    """Returns 's' for plural, '' for singular."""
    return "s" if abs(amount) != 1 else ""
