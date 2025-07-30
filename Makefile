# Triad Model - Westminster Parliamentary AI System
# Makefile for development and deployment

.PHONY: help install dev-install test lint format check run clean docker-build docker-run constitutional-check

# Default target
help:
	@echo "Triad Model - Westminster Parliamentary AI System"
	@echo ""
	@echo "Available targets:"
	@echo "  install           Install production dependencies"
	@echo "  dev-install       Install development dependencies"
	@echo "  test              Run test suite"
	@echo "  lint              Run linting checks"
	@echo "  format            Format code"
	@echo "  check             Run all checks (lint, test, constitutional)"
	@echo "  run               Start development server"
	@echo "  constitutional-check  Check constitutional compliance"
	@echo "  clean             Clean build artifacts"
	@echo "  docker-build      Build Docker image"
	@echo "  docker-run        Run Docker container"

# Installation
install:
	pip install -e .

dev-install:
	pip install -e ".[dev]"
	pre-commit install

# Development
run:
	python scripts/start.py --environment development

run-prod:
	python scripts/start.py --environment production

# Configuration checks
check-config:
	python scripts/start.py --check-config

constitutional-check:
	python scripts/start.py --constitutional-check

# Testing
test:
	pytest tests/ -v --cov=triad --cov-report=html --cov-report=term

test-constitutional:
	pytest tests/ -v -m constitutional

test-parliamentary:
	pytest tests/ -v -m parliamentary

test-integration:
	pytest tests/ -v -m integration

# Code quality
lint:
	ruff check triad/ tests/
	mypy triad/

format:
	black triad/ tests/
	ruff check --fix triad/ tests/

# Comprehensive checks
check: lint test constitutional-check
	@echo "✅ All checks passed"

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Docker
docker-build:
	docker build -t triad-model:latest .

docker-run:
	docker run -p 8000:8000 --env-file .env triad-model:latest

# Database operations (Prisma)
db-setup:
	python scripts/setup_prisma.py

db-generate:
	prisma generate

db-push:
	prisma db push

db-reset:
	prisma db reset --force

db-migrate:
	prisma migrate dev

db-studio:
	prisma studio

# Development utilities
deps-update:
	pip-compile --upgrade requirements.in
	pip-compile --upgrade requirements-dev.in

security-check:
	bandit -r triad/
	safety check

# Parliamentary procedures (for testing)
start-session:
	curl -X POST "http://localhost:8000/api/v1/parliamentary/session/start" \
	     -H "Content-Type: application/json" \
	     -d '{"session_type": "regular"}'

question-period:
	curl -X POST "http://localhost:8000/api/v1/parliamentary/question-period/start" \
	     -H "Content-Type: application/json" \
	     -d '{"session_id": "test_session", "time_limit_minutes": 30}'

# API testing
test-api:
	curl -X GET "http://localhost:8000/api/v1/health/"
	curl -X GET "http://localhost:8000/api/v1/parliamentary/constitutional-status"

# Documentation
docs-serve:
	mkdocs serve

docs-build:
	mkdocs build

# Production deployment helpers
deploy-check: check constitutional-check
	@echo "✅ Deployment checks passed"

deploy-prod: deploy-check
	@echo "🚀 Ready for production deployment"
	@echo "   Remember to:"
	@echo "   1. Set production environment variables"
	@echo "   2. Configure database connections"
	@echo "   3. Enable authentication and security"
	@echo "   4. Set up monitoring and logging"