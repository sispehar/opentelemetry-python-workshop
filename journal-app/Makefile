.PHONY: build run reload logs down

# Build all Docker containers
build:
	@echo "Building Docker containers..."
	docker compose build

# Run the application (foreground)
run:
	@echo "Starting application..."
	docker compose up -d

# Reload the application by stopping containers, rebuilding, and starting up
reload:
	@echo "Reloading application (down, build, and up)..."
	docker compose down && docker-compose up --build -d

# Follow container logs
logs:
	@echo "Tailing container logs..."
	docker compose logs -f

# Stop all running containers
down:
	@echo "Stopping application..."
	docker compose down