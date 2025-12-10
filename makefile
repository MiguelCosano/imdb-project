help:
	@echo "IMDb Data System"
	@echo ""
	@echo "make up     - Start postgres → ingest → API"
	@echo "make down   - Stop services"
	@echo "make logs   - View logs"
	@echo "make status - Service status"
	@echo "make test   - Test API"
	@echo "make clean  - Clean everything"
	@echo "make reload - Reload data into the database if there are changes"

up:
	docker-compose build
	@echo "Starting PostgreSQL..."
	docker-compose up -d db
	
	@echo "Starting INGESTION..."
	docker-compose run --rm ingest
	
	@echo "Starting API..."
	docker-compose up -d api
	
	@echo ""
	@echo "SYSTEM READY!"

reload:
	@echo "Reloading data..."
	docker-compose run --rm ingest
	@echo "Data reloaded!"

down:
	docker-compose down

logs:
	docker-compose logs -f

status:
	docker-compose ps

test:
	curl -s $(API_URL)/health || echo "Health OK"

clean:
	docker-compose down -v
