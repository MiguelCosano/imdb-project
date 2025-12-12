ifneq (,$(wildcard ./.env))
    include .env
    export $(shell sed 's/=.*//' .env)
endif

help:
	@echo "IMDb Data System ($(PROJECT_NAME))"
	@echo ""
	@echo "make up       - Start postgres -> ingest -> API"
	@echo "make down     - Stop services"
	@echo "make status   - Service status"
	@echo "make clean    - Clean volumes"
	@echo "make reload   - Reload data"
	@echo "make db-index - Add search indexes"

up:
	docker-compose -p $(PROJECT_NAME) build
	@echo "Starting PostgreSQL database..."
	docker-compose -p $(PROJECT_NAME) up -d db
	@echo "Running ingestion..."
	docker-compose -p $(PROJECT_NAME) run --rm ingest
	@echo "Adding search indexes..."
	$(MAKE) db-index
	@echo "Starting API..."
	docker-compose -p $(PROJECT_NAME) up -d api
	@echo ""
	@echo "SYSTEM READY! API: $(API_URL)"
	@echo "IF YOU WANT TO ISNTALL THE CLI PACKAGE AUTOMATICALLY EXECUTE "

down:
	docker-compose -p $(PROJECT_NAME) down

clean:
	docker-compose -p $(PROJECT_NAME) down -v

status:
	docker-compose -p $(PROJECT_NAME) ps

test:
	curl -s "http://localhost:8000/health"

reload:
	docker-compose -p $(PROJECT_NAME) run --rm ingest
	@echo "Data reloaded!"

db-index:
	@echo "Adding tsvector columns..."
	@docker exec -it $(DB_CONTAINER_NAME) psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -c \
		"ALTER TABLE actors ADD COLUMN IF NOT EXISTS search_vector tsvector GENERATED ALWAYS AS (to_tsvector('english', coalesce(primary_name, ''))) STORED;"
	@docker exec -it $(DB_CONTAINER_NAME) psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -c \
		"ALTER TABLE movies ADD COLUMN IF NOT EXISTS search_vector tsvector GENERATED ALWAYS AS (to_tsvector('english', coalesce(primary_title, ''))) STORED;"
	@echo "Creating GIN indexes..."
	@docker exec -it $(DB_CONTAINER_NAME) psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -c \
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_actors_search ON actors USING GIN(search_vector);"
	@docker exec -it $(DB_CONTAINER_NAME) psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -c \
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_movies_search ON movies USING GIN(search_vector);"
	@echo "Indexes ready!"

db-clean:
	@echo "Cleaning database tables..."
	@docker exec -it $(DB_CONTAINER_NAME) psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -c \
		"DROP TABLE IF EXISTS actors CASCADE; DROP TABLE IF EXISTS movies CASCADE;"
	@echo "Tables cleaned"
