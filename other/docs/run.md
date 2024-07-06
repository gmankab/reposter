### navigation

- [repo](https://github.com/gmankab/reposter)
- [how to run](https://github.com/gmankab/reposter/blob/main/docs/run.md)
- [how to build](https://github.com/gmankab/reposter/blob/main/docs/build.md)
- [config and env](https://github.com/gmankab/reposter/blob/main/docs/config.md)
- [pypi](https://pypi.org/project/reposter)

### run via pip (recommended)

```
python -m ensurepip
python -m pip install reposter
python -m reposter
```

### run from sources

```shell
git clone https://gitlab.com/gmanka/reposter
cd reposter
python -m ensurepip
python -m pip install uv
python -m uv venv
python -m uv pip install -r pyproject.toml --python=.venv/bin/python
.venv/bin/python reposter
```

### run tests from sources

```shell
python -m uv pip install -r pyproject.toml --extra=tests --python=.venv/bin/python
tests=true .venv/bin/python reposter
```

### run big tests from sources

```shell
python -m uv pip install -r pyproject.toml --extra=tests --python=.venv/bin/python
big_tests=true .venv/bin/python reposter
```

