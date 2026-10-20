install:
	pip install .

uninstall:
	pip uninstall eoqrid

ruff:
	ruff check .

test:
	cd tests; pytest -s .

uml:
	cd docs/uml; plantuml -tsvg class.pu

api:
	cd docs; make html
