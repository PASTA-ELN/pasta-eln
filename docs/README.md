## Editing, building, and publishing extension documentation


PASTA-ELN uses [Sphinx](https://www.sphinx-doc.org/en/master/index.html#) for document generation.

### Local testing

```
pip install -r requirements-devel.txt
```

Then build the documentation locally:

```
make -C docs html
```

Navigate to `docs/build/` and open `index.html`.

### Remote building and testing

The documentation is automatically build by the GitHub Action  `.github/workflows/docbuild.yml` and will be published within that action.
