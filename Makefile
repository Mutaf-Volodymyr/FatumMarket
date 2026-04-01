COMPOSE = docker compose --file config/docker/docker-compose.yaml -p fatum_market

build:
	$(COMPOSE) build

dev:
	$(COMPOSE) up

devbuild:
	$(COMPOSE) up --build

exec:
	$(COMPOSE) exec fatum-web bash

shell:
	$(COMPOSE) run --rm --entrypoint /bin/bash fatum-web

down:
	$(COMPOSE) down

restart:
	$(COMPOSE) restart
