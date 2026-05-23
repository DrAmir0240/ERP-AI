COMPOSE=docker compose
DEV_COMPOSE=$(COMPOSE) -f docker-compose.yml -f docker-compose.dev.yml

.PHONY: build up down logs migrate shell backend-shell frontend-shell celery test

build:
	$(DEV_COMPOSE) build

up:
	$(DEV_COMPOSE) up

down:
	$(DEV_COMPOSE) down

logs:
	$(DEV_COMPOSE) logs -f

migrate:
	$(DEV_COMPOSE) run --rm backend python manage.py migrate

shell:
	$(DEV_COMPOSE) run --rm backend python manage.py shell

backend-shell:
	$(DEV_COMPOSE) run --rm backend sh

frontend-shell:
	$(DEV_COMPOSE) run --rm frontend sh

celery:
	$(DEV_COMPOSE) logs -f celery celery-beat

test:
	$(DEV_COMPOSE) run --rm backend python manage.py test
