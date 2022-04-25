# makefile to install the package, document the API with lucidoc and build the documentation with mkdocs

doc_api:
	poetry install -v
	lucidoc cloudwatcher --parse rst --outfile docs/API_documentation.md

serve_docs: doc_api
	mkdocs serve

build_docs: doc_api
	mkdocs build

deploy_docs: doc_api
	mkdocs gh-deploy
