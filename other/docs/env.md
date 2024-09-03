## env variables guide

### navigation

- [repo](https://github.com/gmankab/reposter)
- [how to run](https://github.com/gmankab/reposter/blob/main/other/docs/run.md)
- [how to build](https://github.com/gmankab/reposter/blob/main/other/docs/build.md)
- [config](https://github.com/gmankab/reposter/blob/main/other/docs/config.md)
- [env](https://github.com/gmankab/reposter/blob/main/other/docs/env.md)
- [pypi](https://pypi.org/project/reposter)

### reposter_data_dir

- `reposter_data_dir` - directory to store reposter config and session
- if there is no `reposter_data_dir` variable, program looks for `XDG_DATA_HOME` variable
- if there is no `XDG_DATA_HOME` variable, program works in portable way and creates `data` directory near `reposter` dir which contains code

### reposter_conf

- `reposter_conf` - path to `config.json` file
- if there is no `reposter_data_dir` variable, program looks for `XDG_CONFIG_HOME` variable
- if there is no `XDG_CONFIG_HOME` variable, program creates config in `data` directory

### session_name

- `session_name` - name of tg session, defatults to `tg_bot`, so session file would be `tg_bot.session`
- if you set it to something like `my_session`, session file would be `my_session.session`

### tests

- `tests` - if set to `true`, autotests are started
- `big_tests` - if set to `true`, autotests with additional tests for big 10mb+ files are started
- big tests takes more time then regular tests

