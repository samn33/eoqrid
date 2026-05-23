install:
	pip install .

uninstall:
	pip uninstall eoqrid

ruff:
	ruff check .

test:
	cd tests; pytest -s .

sample:
	cd samples; python sample_08.py
