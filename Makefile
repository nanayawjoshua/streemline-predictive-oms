.PHONY: all dev test build clean

all: build

# ── Development ──

dev:
	docker compose up --build

dev-prediction:
	cd prediction-engine && uv run uvicorn app.main:app --reload --port 8001

dev-connector:
	cd go-connector && go run . & disown

dev-dashboard:
	python3 -m http.server 8080 --directory dashboard &

# ── Testing ──

test:
	cd prediction-engine && python -m pytest tests/ -v

test-go:
	cd go-connector && go vet ./...

# ── Build ──

build:
	docker compose build

build-prediction:
	docker build -t streemline/predictive-oms:latest prediction-engine/

build-connector:
	docker build -t streemline/oms-connector:latest go-connector/

# ── Quality ──

lint:
	cd prediction-engine && pip install ruff && ruff check app/

typecheck:
	cd prediction-engine && pip install mypy && mypy app/

# ── Cleanup ──

clean:
	docker compose down -v
	rm -rf prediction-engine/__pycache__ prediction-engine/app/__pycache__
	rm -rf go-connector/connector
