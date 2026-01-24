build:
	docker compose --file config/docker/docker-compose.yaml -p fatum_market build

dev:
	docker compose --file config/docker/docker-compose.yaml up

devbuild:
	docker compose --file config/docker/docker-compose.yaml -p fatum_market up --build

exec:
	docker compose --file config/docker/docker-compose.yaml exec webapp bash

shell:
	docker compose --file config/docker/docker-compose.yaml run --rm --entrypoint /bin/bash webapp

down:
	docker compose --file config/docker/docker-compose.yaml down

restart:
	docker compose --file config/docker/docker-compose.yaml restart

