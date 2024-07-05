.PHONY: install run clean

install:
	pip install -r requirements.txt

run:
	python main.py

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -r {} +
