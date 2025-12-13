import click
import requests
import os
from pathlib import Path
from dotenv import load_dotenv
from imdb_cli.models import MovieResponse, ActorResponse
from imdb_cli.formatters import (
    format_professions,
    format_genres,
    is_dead_or_alive,
    plural_s,
)

BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / ".env"
load_dotenv(dotenv_path)

server = os.getenv("API_URL", "http://localhost:8000")


@click.group()
def cli():
    """IMDb Data CLI - Query actors and movies from the IMDb dataset.

    This CLI connects to the IMDb API to search for actors and movies.
    Ensure the API is running at the configured URL (default: http://localhost:8000).

    \b
    Examples
    --------
    Search for an actor:
        $ imdb actor "Tom Hanks"

    Search for a movie with limit:
        $ imdb movie "Shrek" --limit 5

    Get help:
        $ imdb --help
    """
    pass


@cli.command()
@click.argument("name")
@click.option(
    "--limit",
    type=int,
    default=1,
    help="Number of actors to display (default: 1)",
)
def actor(name, limit):
    """Search for actors, directors, and other people in the IMDb dataset.

    Searches by name and returns matching results ordered by relevance.

    \b
    Examples
    --------
    Search for an actor and show first result:
        $ imdb actor "Bruce Lee"

    Show top 5 results for a common name:
        $ imdb actor "Tom Hanks" --limit 5
        $ imdb actor --limit 5 "Tom Hanks"
    """
    try:
        response = requests.get(f"{server}/actors/search?name={name}", timeout=10)
        response.raise_for_status()

        data = response.json()

        actor_data = ActorResponse.model_validate({"actors": data})
        number_of_actors = len(actor_data.actors)

        if number_of_actors == 0:
            click.echo(f"Actor named '{name}' not found.", err=True)
            return

        if number_of_actors < 1:
            click.echo("Error: Result number must be at least 1.", err=True)
            return

        shown = min(limit, number_of_actors)
        click.echo(
            f"Found {number_of_actors} actor{plural_s(number_of_actors)}.\n"
            f"Showing {shown} actor{plural_s(shown)}."
        )
        for i, actor in enumerate(actor_data.actors[:limit], 1):
            click.echo(
                f"{i}. {actor.primary_name} was born in {actor.birth_year} and"
                f" he {is_dead_or_alive(actor.is_dead)} {format_professions(actor.primary_profession)}."
            )

    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            click.echo(f"Actor named {name} not found", err=True)
        else:
            click.echo(
                f"HTTP Error {e.response.status_code if e.response else ''}: {e}",
                err=True,
            )
        raise click.Abort()

    except requests.exceptions.ConnectionError as e:
        click.echo(f"Connection error: {e}", err=True)
        raise click.Abort()

    except requests.exceptions.Timeout as e:
        click.echo(f"Request timed out: {e}", err=True)
        raise click.Abort()

    except requests.exceptions.RequestException as e:
        click.echo(f"Request error: {e}", err=True)
        raise click.Abort()

    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)


@cli.command()
@click.argument("title")
@click.option(
    "--limit",
    type=int,
    default=1,
    help="Number of movies to display (default: 1)",
)
def movie(title, limit):
    """Search for movies and films in the IMDb dataset.

    Searches by title and returns matching results ordered by exact match,
    completeness, and relevance.

    \b
    Examples:
      imdb movie "Shrek"
      imdb movie "Matrix" --limit 10
      imdb movie --limit 10 "Matrix"
    """
    try:
        response = requests.get(
            f"{server}/movies/search", params={"title": title}, timeout=10
        )
        response.raise_for_status()

        data = response.json()
        movie_data = MovieResponse.model_validate({"movies": data})
        number_of_movies = len(movie_data.movies)

        if number_of_movies == 0:
            click.echo(f"Movie titled '{title}' not found.", err=True)
            return

        if limit < 1:
            click.echo("Error: Result number must be at least 1.", err=True)
            return

        shown = min(limit, number_of_movies)
        click.echo(
            f"Found {number_of_movies} movie{plural_s(number_of_movies)}.\n"
            f"Showing {shown} movie{plural_s(shown)}."
        )

        for i, movie in enumerate(movie_data.movies[:limit], 1):
            click.echo(
                f"{i}. {movie.primary_title}, originally titled '{movie.original_title}', "
                f"is {format_genres(movie.genres)}."
            )

    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            click.echo(f"Movie titled {title} not found", err=True)
        else:
            click.echo(
                f"HTTP Error {e.response.status_code if e.response else ''}: {e}",
                err=True,
            )
        raise click.Abort()

    except requests.exceptions.ConnectionError as e:
        click.echo(f"Connection error: {e}", err=True)
        raise click.Abort()

    except requests.exceptions.Timeout as e:
        click.echo(f"Request timed out: {e}", err=True)
        raise click.Abort()

    except requests.exceptions.RequestException as e:
        click.echo(f"Request error: {e}", err=True)
        raise click.Abort()

    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)


if __name__ == "__main__":
    cli()
