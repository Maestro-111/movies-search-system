# Environment variables
LOCAL_COMPOSE := docker/local/docker-compose.yml
PROD_COMPOSE :=  docker/prod/docker-compose.yml
DC := docker compose --env-file .env

# Default environment
ENV_FILE := local

# Default target
.DEFAULT_GOAL := help

# Environment selection
.PHONY: local prod
local:
	$(eval COMPOSE_FILES := -f $(LOCAL_COMPOSE))
	@echo "🔧 Setting environment to local"

prod:
	$(eval COMPOSE_FILES := -f $(PROD_COMPOSE))
	@echo "🚀 Setting environment to production"

# Docker commands
.PHONY: build up down restart logs clean config ps
build:
	$(DC) $(COMPOSE_FILES) build

up:
	$(DC) $(COMPOSE_FILES) up -d
	@echo "🌐 Services are up"

down:
	$(DC) $(COMPOSE_FILES) down
	@echo "⏹️ Services stopped and removed"

restart:
	$(DC) $(COMPOSE_FILES) restart
	@echo "🔄 Services restarted"

logs:
	$(DC) $(COMPOSE_FILES) logs -f

ps:
	$(DC) $(COMPOSE_FILES) ps

config:
	$(DC) $(COMPOSE_FILES) config

clean:
	$(DC) $(COMPOSE_FILES) down -v --remove-orphans
	@echo "🧹 Cleaned up containers, volumes, and orphans"

# Django commands
.PHONY: migrations migrate shell static
migrations:
	$(DC) $(COMPOSE_FILES) exec web python manage.py makemigrations

migrate:
	$(DC) $(COMPOSE_FILES) exec web python manage.py migrate

shell:
	$(DC) $(COMPOSE_FILES) exec web python manage.py shell

static:
	$(DC) $(COMPOSE_FILES) exec web python manage.py collectstatic --noinput

# Development helpers
.PHONY: lint test coverage
lint:
	$(DC) $(COMPOSE_FILES) exec web flake8 .

test:
	$(DC) $(COMPOSE_FILES) exec web python manage.py test

coverage:
	$(DC) $(COMPOSE_FILES) exec web coverage run manage.py test
	$(DC) $(COMPOSE_FILES) exec web coverage report

# Help
.PHONY: help
help:
	@echo "🛠️  Available commands:"
	@echo "Environment:"
	@echo "  make local          💻 Set to local environment"
	@echo "  make prod           🚀 Set to production environment"
	@echo
	@echo "Docker Commands:"
	@echo "  make build          🏗️  Build the containers"
	@echo "  make up             🚀 Start the containers"
	@echo "  make down           ⏹️  Stop and remove containers"
	@echo "  make restart        🔄 Restart containers"
	@echo "  make logs           📝 View logs"
	@echo "  make ps             👀 List running containers"
	@echo "  make clean          🧹 Remove containers, volumes, and orphans"
	@echo
	@echo "Django Commands:"
	@echo "  make migrations     📝 Create new migrations"
	@echo "  make migrate        💾 Apply migrations"
	@echo "  make shell          🐚 Django shell"
	@echo "  make static         📦 Collect static files"
	@echo
	@echo "Development:"
	@echo "  make lint           🔍 Run linter"
	@echo "  make test           🧪 Run tests"
	@echo "  make coverage       📊 Run tests with coverage"