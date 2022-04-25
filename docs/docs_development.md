# Documentation development

The documentation is built from the makrdown files in the `/docs` directory with static site generator [MkDocs](https://mkdocs.org/).

## With `make`

!!! info "Makefile"

    The following commands are encoded in a Makefie in this repository: [`makefile`](./makefile).


### Serve

To serve the documentation locally, you can the `serve_docs` target:

```console
make serve_docs
```

The documentation is served on [http://localhost:8000/](http://localhost:8000/).

### Build

To build the documentation, you can the `build_docs` target:

```console
make build_docs
```

The documentation is built in the `/site` directory.

### Deploy

To deploy the documentation to GitHub Pages, you can the `deploy_docs` target:

```console
make deploy_docs
```

The documentation is deployed to GitHub Pages.

## By hand

In order to serve the documentation by hand follow the steps below.

!!! info "Note"

    The commands need to be run from the root of the repository, unless stated otherwise.

1. Install the documentation-related dependancies and the Python package itself with [Poetry](https://poetry.org/)

    ```console
    poetry install
    ```

2. Document the API of the package

    ```console
    lucidoc cloudwatcher --parse rst --outfile docs/API_documentation.md
    ```

3. Run the following command in the project root

    ```
    mkdocs serve
    ```

## Deploying the documentation

In order to deploy the documentation run the following command:

```
mkdocs gh-deploy
```
