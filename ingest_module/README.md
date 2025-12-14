
## INGEST_MODULE

A Python-based ETL pipeline that extracts data from the [IMDb datasource](https://datasets.imdbws.com/
), transforms and cleans it, and loads it into a PostgreSQL database. The module is designed with a layered architecture that clearly separates concerns across the extraction, transformation, and loading stages. The primary objective of this ETL is to be production-ready, with performance optimized to avoid unnecessary resource consumption.

## Features

The ETL pipeline implements a modular architecture with clear separation of concerns:

- **Extract** (`extract/`): Downloads and reads raw data from IMDb datasets without storing it in chunks if it has changed
- **Transform** (`transform/`): Cleans, validates, and transforms data to insert it into the database
- **Load** (`load/`): Efficiently inserts processed data into PostgreSQL
- **Utils** (`utils/`): Shared utilities for database connections, configuration, and metadata management

## Project Structure

```
ingest_module/
├── main.py                 # ETL pipeline orchestration
├── extract/
│   ├── __init__.py
│   └── imdb_extractor.py   # Streaming extraction from IMDb
├── transform/
│   ├── __init__.py
│   └── imdb_transformer.py # Data cleaning and transformation
├── load/
│   ├── __init__.py
│   └── imdb_loader.py      # PostgreSQL bulk loading
├── utils/
│   ├── __init__.py
│   ├── constants.py        # Configuration constants (URLs, chunk sizes)
│   ├── database.py         # Database connection and setup
│   ├── datasets.py         # Dataset configurations
│   └── metadata.py         # ETag tracking for update detection
├── data/
│   └── metadata.json       # ETag storage for files
├── test/
│   ├── __init__.py
│   └── __pycache__/
├── Dockerfile              # Container configuration
├── pyproject.toml          # Dependencies and metadata
└── README.md               # This file
```

## Technical decisions

The module evolved through performance optimization:

#### First optimization

1. **Initial Approach**: Sequential processing with basic pandas `to_sql()`

![System Architecture](../docs/before_copy.png)

2. **Optimized Approach**: Chunk-based streaming with PostgreSQL `COPY` command - significantly faster

![System Architecture](../docs/after_copy.png)


The optimization uses PostgreSQL's native `COPY FROM` command via the `psql_insert_copy` function, which is recommended by both PostgreSQL and pandas documentation for bulk inserts. This approach:
- Streams data in chunks to reduce memory overhead
- Uses PostgreSQL's efficient binary copy protocol
- Processes millions of rows efficiently
- Clears the data that was previouly stored (is intended since after it it will need to create again the colum for improve search)

[Copy method in pandas documentation](https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#sql-queries)


#### Second optimization

At first, using a sequential approach, the file was saved inside the ETL process and kept in the Docker image so it could be checked to see if it had changed and decide whether to run the ETL again. After thinking about it more, this was not a good approach because the file is too large.

Because of this, the strategy was changed to store the file’s `ETag` in a JSON file instead. The `ETag` identifies the file, and when it changes, we know the file has changed too. This allows us to detect updates in a much lighter way, without downloading the entire dataset.

[ETag header documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/ETag)


#### Third optimization

The initial version executed each step sequentially: **Download → Transformation → Load**. This approach worked, but I came across several articles that discussed the use of Python generators:

* [Writing memory efficient data pipelines in Python](https://www.startdataengineering.com/post/writing-memory-efficient-dps-in-python/)
* [Python Generators: Boosting Performance and Simplifying Code](https://www.datacamp.com/tutorial/python-generators)

This aligned well with the goal of avoiding file downloads, especially since Pandas allows reading files directly from a URL. Based on this, the pipeline flow was redesigned to return data chunks using `yield`. In this approach, each chunk that is read is immediately sent for transformation and then loaded into the database.

As a result, the entire pipeline starts executing from the beginning without overloading memory, optimizing resource usage as much as possible. Additionally, this approach helped simplify the code and made it more readable and easier to understand.


## Data cleaning 

To clean the data, only the columns that are actually used were selected, and rows containing `NULL` values in relevant fields were filtered out. Additionally, in the case of actors, the `deathYear` column was transformed into an `is_dead` field to correctly indicate the actor’s status when retrieving their data.

Based on IMDb documentation, the `\N` values were mapped to `NULL` during data extraction. Finally, the columns were renamed to follow the database naming conventions before being inserted into the database.



## Installation

### Prerequisites

- Python 3.11 or higher
- PostgreSQL database running
- Environment variables configured (see Configuration section)

### Option 1: Setup with uv (Recommended)

uv is a fast, modern Python package manager:

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

#### Step 3: Install Ingest Module

```bash
uv pip install -e ./ingest_module/
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

#### Step 2: Install Ingest Module

```bash
python -m pip install -e ./ingest_module/
```

## Configuration

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/imdb
```

### Dataset Configuration

Datasets are configured in [utils/datasets.py](utils/datasets.py):

- **Actors**: `name.basics.tsv.gz` → `actors` table
- **Movies**: `title.basics.tsv.gz` → `movies` table

Each configuration specifies:
- Source filename from IMDb
- Target table name
- Columns to extract
- Data types for parsing
- Mapping to change columns names

## Usage

### Run the Complete Pipeline

```bash
python main.py
```

This will:
1. Check for updates to all datasets using ETags
2. Download only changed files
3. Extract raw data in chunks
4. Transform and validate each chunk
5. Load data into PostgreSQL with progress tracking

## Testing

Unit tests are provided in the `test/` directory using pytest:

### Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest test/test_extractor.py
pytest test/test_transformer.py
pytest test/test_loader.py
pytest test/test_metadata.py
```

### Test Files Overview

#### Extractor Tests (`test_extractor.py`)
- `TestReadChunks.test_read_chunks_yields_dataframes` - Tests that read_chunks yields pandas DataFrames
- `TestReadChunks.test_read_chunks_calls_save_metadata` - Tests metadata is saved after streaming
- `TestReadChunks.test_read_chunks_handles_exception` - Tests exception handling in streaming
- `TestGetFileMetadata.test_get_file_metadata_returns_etag` - Tests ETag retrieval from response
- `TestGetFileMetadata.test_get_file_metadata_timeout` - Tests timeout error handling
- `TestGetFileMetadata.test_get_file_metadata_http_error` - Tests HTTP error handling

#### Transformer Tests (`test_transformer.py`)
- `TestTransformChunksMovies.test_transform_chunks_filters_critical_nulls_actors` - Tests filtering of null values in actor data
- `TestTransformChunksMovies.test_transform_chunks_filters_critical_nulls_movies` - Tests filtering of null values in movie data
- `TestTransformChunksMovies.test_transform_chunks_renames_columns_correctly_actors` - Tests column renaming for actors
- `TestTransformChunksMovies.test_transform_chunks_renames_columns_correctly_movies` - Tests column renaming for movies
- `TestTransformChunksMovies.test_transform_chunks_adds_is_dead_and_drops_death_year` - Tests computed is_dead field
- `TestTransformChunksMovies.test_transform_chunks_skips_empty_chunks` - Tests that empty chunks are skipped
- `TestFilterCriticalNulls.test_filter_critical_nulls_actors` - Tests null filtering for actors
- `TestFilterCriticalNulls.test_filter_critical_nulls_movies` - Tests null filtering for movies

#### Loader Tests (`test_loader.py`)
- `TestLoadChunks.test_load_chunks_single_chunk` - Tests loading single data chunk to database
- `TestLoadChunks.test_load_chunks_multiple_chunks` - Tests loading multiple chunks
- `TestLoadChunks.test_load_chunks_subsequent_chunks_append_mode` - Tests replace mode for first chunk and append for subsequent
- `TestLoadChunks.test_load_chunks_uses_psql_insert_copy` - Tests PostgreSQL COPY optimization usage
- `TestLoadChunks.test_load_chunks_correct_table_name` - Tests correct table name is used
- `TestLoadChunks.test_load_chunks_empty_iterator` - Tests handling of empty data iterator
- `TestLoadChunks.test_load_chunks_handles_exception` - Tests exception handling during load
- `TestLoadChunks.test_load_chunks_with_movies_config` - Tests loading with movies configuration

#### Metadata Tests (`test_metadata.py`)
- `test_save_and_load_metadata` - Tests saving and loading metadata from JSON
- `test_should_reload_etag_match` - Tests ETag matching (no reload needed)
- `test_should_reload_etag_mismatch` - Tests ETag mismatch detection (reload needed)
- `test_should_reload_no_metadata` - Tests reload when no metadata exists
- `test_save_metadata_creates_directory` - Tests directory creation if not exists
- `test_should_reload_request_exception` - Tests handling of request exceptions
- `test_load_metadata_file_not_exists` - Tests loading when metadata file doesn't exist
- `test_save_metadata_overwrites_existing` - Tests overwriting existing metadata entries

## Dependencies

- `pandas>=2.2.0` - Data manipulation and CSV parsing
- `sqlalchemy>=2.0.0` - Database ORM and connection management
- `psycopg2-binary>=2.9.0` - PostgreSQL adapter
- `requests>=2.32.0` - HTTP requests for ETags
- `python-dotenv>=1.0.0` - Environment variable management
- `alive-progress>=3.3.0` - Progress indicators
- `pytest>=9.0.2` - Testing framework

## Database Schema

The pipeline creates two main tables (the search_vector column will be added later):

### actors
- `nconst` (TEXT, PRIMARY KEY) - IMDb person ID
- `primary_name` (TEXT) - Actor/director name
- `birth_year` (SMALLINT) - Birth year
- `death_year` (SMALLINT) - Death year (nullable)
- `primary_profession` (TEXT) - Professions

### movies
- `tconst` (TEXT, PRIMARY KEY) - IMDb title ID
- `primary_title` (TEXT) - Movie title
- `original_title` (TEXT) - Original language title
- `genres` (TEXT) - Comma-separated genres

## Docker

A Dockerfile is included for containerized execution:

```bash
docker build -t imdb-ingest .
docker run imdb-ingest
```

## Troubleshooting

- **Connection Error**: Verify `DATABASE_URL` environment variable and PostgreSQL is running
- **Download Fails**: Check internet connection and IMDb URL accessibility
- **Permission Denied**: Ensure PostgreSQL user has table creation permissions