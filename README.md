
# IMDb ETL + API + CLI

A data engineering project that extracts IMDb datasets, processes them through an ETL pipeline, and stores the results in a PostgreSQL database.  
The system exposes a FastAPI-based REST API and a CLI tool built with Click for querying movie and actor data.

This project is organized into three main components: `ingest_module`, `server_module`, and `cli_module`.

## Overview

The architecture consists of the following modules:

- **ingest_module** – Handles the ETL process for downloading, transforming, and loading IMDb datasets into the database.  
- **PostgreSQL Database** – A Dockerized PostgreSQL database that stores the processed IMDb data, providing persistent and queryable storage.  
- **server_module** – A FastAPI-based REST API that exposes endpoints for accessing and querying movie and actor information.  
- **cli_module** – A command-line interface built with Click that allows users to interact with the API, execute predefined queries, and retrieve data directly from the terminal.

## Architecture diagram:
![System Architecture](docs/architecture.png)
