### navigation

- [github repo](https://github.com/gmankab/reposter)
- [gitlab repo](https://gitlab.com/gmanka/reposter)
- [codeberg repo](https://codeberg.org/gmanka/reposter)
- [how to run](https://github.com/gmankab/reposter/blob/main/other/docs/run.md)
- [how to build](https://github.com/gmankab/reposter/blob/main/other/docs/build.md)
- [config](https://github.com/gmankab/reposter/blob/main/other/docs/config.md)
- [env](https://github.com/gmankab/reposter/blob/main/other/docs/env.md)
- [pypi](https://pypi.org/project/reposter)

### run via pip (recommended, any os)

```
python -m ensurepip
python -m pip install reposter
python -m reposter
```

### run on windows

download and run [reposter.bat](https://gitlab.com/gmanka/reposter/-/raw/main/other/launcher/reposter.bat?inline=false)

### run from sources

```shell
git clone https://github.com/gmankab/reposter
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

