.PHONY: install dev test lint format migrate revision up

PYTHON=python

install:
	$(PYTHON) -m pip install --upgrade pip
	@if [ -f pyproject.toml ]; then $(PYTHON) -m pip install .[dev]; else pip install -r requirements.txt; fi

revision:
	alembic revision --autogenerate -m "$$(date +'%Y%m%d_%H%M')"

migrate:
	alembic upgrade head

test:
	./scripts/test_with_migrate.sh

lint:
	ruff check src tests
	mypy src

format:
	ruff check --fix src tests

up:
	docker compose up -d

down:
	docker compose down
