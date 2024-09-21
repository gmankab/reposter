### navigation

- [github repo](https://github.com/gmankab/reposter)
- [gitlab repo](https://gitlab.com/gmanka/reposter)
- [codeberg repo](https://codeberg.org/gmanka/reposter)
- [how to run](https://github.com/gmankab/reposter/blob/main/other/docs/run.md)
- [how to build](https://github.com/gmankab/reposter/blob/main/other/docs/build.md)
- [config](https://github.com/gmankab/reposter/blob/main/other/docs/config.md)
- [env](https://github.com/gmankab/reposter/blob/main/other/docs/env.md)
- [pypi](https://pypi.org/project/reposter)


### build and upload to pypi

```shell
build_dir=/tmp/reposter
rm -rf $build_dir
git clone https://github.com/gmankab/reposter $build_dir
python -m ensurepip
python -m pip install -U uv
python -m uv venv $build_dir/.venv
python -m uv pip install -Ur $build_dir/pyproject.toml --extra=build --python=$build_dir/.venv/bin/python
$build_dir/.venv/bin/python -m build --installer=uv $build_dir
$build_dir/.venv/bin/twine upload $build_dir/dist/*
```

