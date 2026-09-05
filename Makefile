.PHONY: install scan dashboard api test lint docker

install:
	pip install -r requirements.txt

scan:
	python scanner.py

dashboard:
	python dashboard/app.py

api:
	python api_server.py

dev:
	@echo "Starting dashboard :8000 + api :8001 + scanner in parallel..."
	@python dashboard/app.py &
	@python api_server.py &
	@python scanner.py

test:
	python -m compileall -q .
	python test_all_modules.py
	python test_improved.py

lint:
	python -m compileall -q .
	@echo "lint ok"

docker:
	docker-compose up --build -d
	@echo "Dashboard http://localhost:8000  API http://localhost:8001"

clean:
	rm -rf output/*.xls output/logs/*.jsonl __pycache__ fetchers/__pycache__
