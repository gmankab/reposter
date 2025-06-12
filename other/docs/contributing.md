### navigation

- [github repo](https://github.com/gmankab/reposter)
- [gitlab repo](https://gitlab.com/gmanka/reposter)
- [codeberg repo](https://codeberg.org/gmanka/reposter)
- [how to run](https://github.com/gmankab/reposter/blob/main/other/docs/run.md)
- [contributing](https://github.com/gmankab/reposter/blob/main/other/docs/contributing.md)
- [config](https://github.com/gmankab/reposter/blob/main/other/docs/config.md)
- [env](https://github.com/gmankab/reposter/blob/main/other/docs/env.md)
- [pypi](https://pypi.org/project/reposter)

### run code from sources

```sh
git clone https://github.com/gmankab/reposter
cd reposter
python -m ensurepip
python -m pip install uv
python -m uv venv
python -m uv pip install -r pyproject.toml --python=.venv/bin/python
.venv/bin/python reposter
```

### guidelines

- use ruff and pyright as linters
- run tests before any commit

### run small tests

```sh
python -m uv pip install -r pyproject.toml --extra=tests --python=.venv/bin/python
tests=true .venv/bin/python reposter
```

### run big tests

```sh
python -m uv pip install -r pyproject.toml --extra=tests --python=.venv/bin/python
big_tests=true .venv/bin/python reposter
```

### build and upload to pypi

```shell
export build_dir=/tmp/reposter
rm -rf $build_dir
git clone https://github.com/gmankab/reposter $build_dir
python -m ensurepip
python -m pip install -U uv
python -m uv venv $build_dir/.venv
python -m uv pip install -Ur $build_dir/pyproject.toml --extra=build --python=$build_dir/.venv/bin/python
$build_dir/.venv/bin/python -m build --installer=uv $build_dir
$build_dir/.venv/bin/twine upload $build_dir/dist/*
```

