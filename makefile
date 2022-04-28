# makefile to install the package, document the API with lucidoc and build the documentation with mkdocs

doc_api:
	poetry install -v
	lucidoc cloudwatcher --parse rst --outfile docs/API_documentation.md
	jupyter nbconvert docs/API_usage.ipynb  --to markdown --output API_usage.md

serve_docs: doc_api
	mkdocs serve

build_docs: doc_api
	mkdocs build

deploy_docs: doc_api
	mkdocs gh-deploy
