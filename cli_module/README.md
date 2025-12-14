## IMDB CLI
A command-line interface built with Click for querying movies and actors from the IMDb Data API. Simple, fast, and beautifully formatted.

## Features

- **Fast searches** - Queries the IMDb API with optimized endpoints
- **Flexible limits** - Display a custom number of results
- **Error handling** - Clear error messages for connection issues, timeouts, and API errors
- **Beautiful formatting** - Human-readable output with contextual information

## Project Structure

```
cli_module/
├── README.md               # This file
├── imdb_cli/
│   ├── __init__.py
│   ├── formatters.py       # Output formatting utilities
│   ├── main.py             # CLI entry point and commands
│   ├── models.py           # Pydantic models for API responses
│   └── __pycache__/
├── test/
│   ├── __init__.py
│   ├── test_cli_actor.py   # Actor command unit tests
│   ├── test_cli_movie.py   # Movie command unit tests
│   ├── test_formatter.py   # Formatter utility tests
│   └── __pycache__/
├── pyproject.toml          # Dependencies and metadata
├── uv.lock                 # Dependency lock file
└── __pycache__/
```

## Installation

### Prerequisites

- Python 3.11 or higher
- The other modules should have been launched. Check main README for more info.

### Option 1: Setup with uv (Recommended)

uv is a fast, modern Python package manager.

#### Step 1: Install uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via Homebrew (macOS)
brew install uv
```

Verify: `uv --version`

#### Step 2: Create Virtual Environment

```bash
cd /path/to/imdb-project
uv venv .venv
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate.bat  # Windows
```

#### Step 3: Install CLI Module

```bash
uv pip install -e ./cli_module/
```

#### Step 4: Verify Installation

```bash
imdb --help
```

### Option 2: Setup with Python (Standard)

If you prefer standard pip:

#### Step 1: Create Virtual Environment

```bash
cd /path/to/imdb-project
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate.bat  # Windows
```

#### Step 2: Install CLI Module

```bash
python -m pip install -e ./cli_module/
```

#### Step 3: Verify Installation

```bash
imdb --help
```


### Configuration

You need to have the `.env` file properly configured in the root of the project as specified in the main README.md

## Usage

The CLI provides two main commands for searching the IMDb dataset:

### Search for Actors

```bash
imdb actor "Tom Hanks"
```

**Options:**
- `--limit` (optional): Number of results to display (default: 1)

**Examples:**
```bash
# Show first matching actor
imdb actor "Bruce Lee"
# Response
Found 1 actor.
Showing 1 actor.
1. Bruce Lee was born in 1940 and had the following professions: actor, writer, and miscellaneous.

# Show top 5 results
imdb actor "Robert" --limit 5
# Response
Found 4610 actors.
Showing 5 actors.
1. Robert P. was born in 1982 and has the following profession: actor.
2. Robert An was born in 2003 and has the following profession: actor.
3. Robert Ray was born in 1978 and had the following profession: archive footage.
4. Robert Joy was born in 1951 and has the following professions: actor, writer, and composer.
5. Robert Lee was born in 1957 and has the following professions: miscellaneous, actor, and archive footage.
```

**Output includes:**
- Actor name
- Birth year
- Life status with tense: "has" (alive) or had (deceased) 
- Primary professions

### Search for Movies

```bash
imdb movie "Shrek"
```

**Options:**
- `--limit` (optional): Number of results to display (default: 1)

**Examples:**
```bash
# Show first matching movie
imdb movie "Iron Man"
# Response
Found 553 movies.
Showing 1 movie.
1. Iron Man, originally titled 'Iron Man', is an Action, a Crime, and a Drama.

# Show top 10 results
imdb movie "Blacksmith Scene" --limit 10
imdb movie --limit 10 "Blacksmith Scene"
Found 3 movies.
Showing 3 movies.
1. Blacksmith Scene, originally titled 'Blacksmith Scene', is a Short.
2. Blacksmith Scene, originally titled 'Les forgerons', is a Documentary and a Short.
3. Blacksmith Rates 9 Forging Scenes from Movies and TV, originally titled 'Blacksmith Rates 9 Forging Scenes from Movies and TV', is a Documentary and a Short.
```

**Output includes:**
- Movie title
- Original title
- Genres

### Get Help

```bash
imdb --help
imdb actor --help
imdb movie --help
```

## Requirements

The CLI requires the following Python packages (automatically installed with pip):

- `click>=8.3.1` - Command-line interface creation
- `pydantic>=2.12.5` - Data validation
- `python-dotenv>=1.0` - Environment variable management
- `requests>=2.32.5` - HTTP requests
- `pytest>=9.0.2` - Testing framework

## Testing

Unit tests are provided in the `test/` directory using pytest:

### Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest test/test_cli_actor.py
pytest test/test_cli_movie.py
pytest test/test_formatter.py
```

### Actor Command Tests
- `test_invalid_limit_validation` - Validates invalid limit values (0, -1, -500)
- `test_no_actors_found` - Handles empty API response
- `test_single_actor_success` - Successful single actor query
- `test_multiple_actors_with_limit` - Multiple actors with limit parameter
- `test_http_404_error` - HTTP 404 error handling
- `test_http_500_error` - HTTP 500 error handling
- `test_connection_error` - Connection error handling
- `test_timeout_error` - Timeout error handling
- `test_generic_request_exception` - Generic request exception handling
- `test_generic_exception` - Generic exception handling

### Movie Command Tests
- `test_invalid_movie_limit` - Validates invalid limit values (0, -1, -500)
- `test_no_movies_found` - Handles empty movie response
- `test_single_movie_success` - Successful single movie query
- `test_multiple_movies_with_limit` - Multiple movies with limit parameter
- `test_http_404_error` - HTTP 404 error handling
- `test_http_500_error` - HTTP 500 error handling
- `test_connection_error` - Connection error handling
- `test_timeout_error` - Timeout error handling
- `test_generic_request_exception` - Generic request exception handling
- `test_generic_exception` - Generic exception handling

### Format Professions Tests
- `test_format_professions_single_actor` - Formats single profession
- `test_format_professions_multiple` - Formats multiple professions
- `test_format_professions_none_or_empty` - Handles None and empty values

### Format Genres Tests
- `test_format_genres_single` - Formats single genre
- `test_format_genres_multiple` - Formats multiple genres
- `test_format_genres_none_or_empty` - Handles None and empty values

### Is Dead or Alive Tests
- `test_is_dead` - Returns 'had' for deceased persons
- `test_is_alive` - Returns 'has' for alive persons
- `test_is_dead_none` - Handles None value

### Plural S Tests
- `test_plural_s_singular` - Returns empty string for count of 1
- `test_plural_s_plural_or_zero` - Returns 's' for counts values (0, 2, 100)

## Troubleshooting

- **Connection error**: Ensure the IMDb API server is running at the configured URL
- **Module not found**: Reinstall the package with `pip3 install -e ./cli_module/`
