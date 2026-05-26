up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f --tail=200

migrate:
	docker compose exec backend sh -lc 'psql "$$DATABASE_URL" -f /app/migrations/sql/001_init.sql && psql "$$DATABASE_URL" -f /app/migrations/sql/002_shots_expand.sql && psql "$$DATABASE_URL" -f /app/migrations/sql/003_generation_task_fields.sql'


test-backend:
	docker compose exec backend pytest -q
