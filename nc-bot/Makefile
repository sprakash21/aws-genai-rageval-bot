build-pgvector-local:
	docker-compose -f docker-compose.yml build postgres

run-pgvector-local:
	docker-compose -f docker-compose.yml up postgres

build-bot-local:
	docker-compose -f docker-compose.yml build nc-bot

run-bot-local:
	docker-compose -f docker-compose.yml up nc-bot

build-and-push:
	./scripts/build_and_push_docker.sh
