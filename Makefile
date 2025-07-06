.PHONY: build test test-interactive clean down help

help:
	@echo "Available commands:"
	@echo "  make build          - Build Docker images"
	@echo "  make test           - Run tests in Docker"
	@echo "  make test-interactive - Run interactive test shell"
	@echo "  make clean          - Clean up containers and volumes"
	@echo "  make down           - Stop all containers"

build:
	docker-compose build

test: build
	docker-compose run --rm test

test-interactive: build
	docker-compose run --rm dev

clean:
	docker-compose down -v
	docker system prune -f

down:
	docker-compose down