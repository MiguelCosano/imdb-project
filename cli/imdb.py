import click
import requests
import os
from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent.parent
dotenv_path = BASE_DIR / ".env"

load_dotenv(dotenv_path)

server = os.getenv("API_URL", "http://localhost:8000")

def format_professions(professions: str | None) -> str:
    """
    Apply formatting to all possible professions in IMDb dataset
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
    
    prof_list = [p.strip() for p in professions.split(',')]
    formatted = [profession_format.get(p, p.replace('_', ' ')) for p in prof_list]
    
    if len(formatted) == 0:
        return "unknown profession"
    elif len(formatted) == 1:
        return formatted[0]
    elif len(formatted) == 2:
        return f"{formatted[0]} and {formatted[1]}"
    else:
        return f"{', '.join(formatted[:-1])}, and {formatted[-1]}"

def format_genres(genres: str| None) -> str:

    if not genres:
        return "Unknown genre"
    
    def add_article(genre: str) -> str:
        if (genre[0] == 'a'):
            return f"an {genre}"
        else:
            return f"a {genre}"
    
    genres_list = [g.strip() for g in genres.split(',')]
    formatted = [add_article(g) for g in genres_list]

    if len(formatted) == 0:
        return "unknown genre"
    elif len(formatted) == 1:
        return formatted[0]
    elif len(formatted) == 2:
        return f"{formatted[0]} and {formatted[1]}"
    else:
        return f"{', '.join(formatted[:-1])}, and {formatted[-1]}"

def deadOrAlive(isDead: bool) -> str:
    """Return 'is' or 'was' based on isDead boolean"""
    return "was" if isDead else "is"

API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")

@click.group()
def cli():
    """IMDb Data CLI Client - Query actors and films from IMDb dataset"""
    pass

@cli.command()
@click.argument('name')
def actor(name):
    """Get information about a person (actor, director, etc.)
    
    Example: imdb actor "Bruce Lee"
    """
    try:
        response = requests.get(f"{API_BASE_URL}/actors/search?name={name}", timeout=10)
        response.raise_for_status()
        data = response.json()
        click.echo(f"{data['primaryName']} was born in {data['birthYear']} and he {deadOrAlive(data['isDead'])} {format_professions(data['primaryProfession'])}")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            click.echo(f"Actor with name:'{title}' not found.", err=True)
        else:
            click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    except requests.exceptions.ConnectionError as e:
        click.echo(f"The connection with the API has failed. Please check if the service has been launched correctly. Error message: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        raise click.Abort()

@cli.command()
@click.argument('title')
def movie(title):
    """Get information about a film/documentary
    
    Example: imdb movie "Blacksmith Scene"
    """
    try:
        response = requests.get(f"{API_BASE_URL}/movies/search?title={title}", timeout=10)
        response.raise_for_status()
        data = response.json()
        click.echo(f"{data['primaryTitle']}, originally titled '{data['originalTitle']}', is {format_genres(data['genres'])}.")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            click.echo(f"Movie with title:'{title}' not found.", err=True)
        else:
            click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    except requests.exceptions.ConnectionError as e:
        click.echo(f"The connection with the API has failed. Please check if the service has been launched correctly. Error message: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    cli()