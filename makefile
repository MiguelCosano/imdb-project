ifneq (,$(wildcard ./.env))
	include .env
	export $(shell sed 's/=.*//' .env)
endif

help:
	@echo "IMDb Data System ($(PROJECT_NAME))"
	@echo ""
	@echo "make up       - Start postgres -> ingest -> create search indexes -> API"
	@echo "make down     - Stop services"
	@echo "make status   - Service status"
	@echo "make clean    - Clean volumes"
	@echo "make reload   - Clean volumes and run again"
	@echo "make test-api - Check if the API is running"
	@echo "make db-index - Add search indexes"
	@echo "make db-clean - Delete database data"

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

down:
	docker-compose -p $(PROJECT_NAME) down

status:
	docker-compose -p $(PROJECT_NAME) ps

clean:
	docker-compose -p $(PROJECT_NAME) down -v

reload:
	$(MAKE) clean
	$(MAKE) up

test-api:
	@echo "Testing API health..."
	@curl -f -s "${API_URL}/health"

db-index:
	@echo "Adding tsvector columns..."
	@docker exec $(DB_CONTAINER_NAME) psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -c \
		"ALTER TABLE actors ADD COLUMN IF NOT EXISTS search_vector tsvector GENERATED ALWAYS AS (to_tsvector('english', coalesce(primary_name, ''))) STORED;"
	@docker exec $(DB_CONTAINER_NAME) psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -c \
		"ALTER TABLE movies ADD COLUMN IF NOT EXISTS search_vector tsvector GENERATED ALWAYS AS (to_tsvector('english', coalesce(primary_title, ''))) STORED;"
	@echo "Creating GIN indexes..."
	@docker exec $(DB_CONTAINER_NAME) psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -c \
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_actors_search ON actors USING GIN(search_vector);"
	@docker exec $(DB_CONTAINER_NAME) psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -c \
		"CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_movies_search ON movies USING GIN(search_vector);"
	@echo "Indexes ready!"

db-clean:
	@echo "Cleaning database tables..."
	@docker exec $(DB_CONTAINER_NAME) psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -c \
		"DROP TABLE IF EXISTS actors CASCADE; DROP TABLE IF EXISTS movies CASCADE;"
	@echo "Tables cleaned"
