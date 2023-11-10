build-pgvector-local:
	docker-compose -f docker-compose-postgres.yml build

run-pgvector-local:
	docker-compose -f docker-compose-postgres.yml up

build-bot-local:
	docker-compose -f docker-compose.yml build nc-bot

run-bot-local:
	docker-compose -f docker-compose.yml up nc-bot

build-and-push:
	./scripts/build_and_push_docker.sh
