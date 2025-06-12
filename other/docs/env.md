### navigation

- [github repo](https://github.com/gmankab/reposter)
- [gitlab repo](https://gitlab.com/gmanka/reposter)
- [codeberg repo](https://codeberg.org/gmanka/reposter)
- [how to run](https://github.com/gmankab/reposter/blob/main/other/docs/run.md)
- [contributing](https://github.com/gmankab/reposter/blob/main/other/docs/contributing.md)
- [config](https://github.com/gmankab/reposter/blob/main/other/docs/config.md)
- [env](https://github.com/gmankab/reposter/blob/main/other/docs/env.md)
- [pypi](https://pypi.org/project/reposter)

### available environment variables

- `XDG_CONFIG_HOME`
- `XDG_DATA_HOME`
- `session_name`
- `reposter_data_dir`
- `reposter_conf`
- `tg_session`
- `big_tests`
- `tests`
- `source`
- `target`
- `msg_start`
- `msg_stop`

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

### repost messages by their id range

- `source` - chat to take posts from
- `target` - chat to send posts to
- `msg_start` - first message to be reposted
- `msg_stop` - last message to be reposted

you can use following formats:

- `source=@username` - username
- `source=t.me/+abcd1234` - ivite link
- `source=-100123456789` - id
- supergroups and channels ids should start with `-100`

