### navigation

- [repo](https://github.com/gmankab/reposter)
- [how to run](https://github.com/gmankab/reposter/blob/main/docs/run.md)
- [how to build](https://github.com/gmankab/reposter/blob/main/docs/build.md)
- [config and env](https://github.com/gmankab/reposter/blob/main/docs/config.md)
- [pypi](https://pypi.org/project/reposter)


### default config

```json
{
    "api_id": 0,
    "api_hash": "",
    "tg_session": "",
    "drop_author": true,
    "logs_chat": "me",
    "chats": {
        "@autotests_source": "@autotests_target"
    }
}
```

### sessions

- in order to start using reposter you should open (my.telegram.org)[https://my.telegram.org], get your `api_id` and `api_hash`, and paste it to `config.json`
- if you have pyrogram/pyrofork session file, you can rename it to `tg_bot.session` and put near `config.json`
- if you have pyrogram/pyrofork session string, you can put it in `config.json` as `tg_session` parameter
- there is not need to set api_id or api_hash if you already have session file or session string

### chats

- `logs_chat` - bot will send logs to this chat, it's recommended to change it from `me` to something else
- `@autotests_source` - chat to take posts from
- `@autotests_target` - chat to send posts to
- you may want to replace this values with other ones

### chats formats

you can use following formats:
- `@usrname`
- id, all ids should be strings, supergroups and channels ids should start with `-100`, for example `-100123456789`
- `t.me/+abcd1234` ivite links

```json
{
    "chats": {
        "@autotests_source": "@autotests_target",
        "-100123456789": "t.me/+abcd1234"
    }
}
```

also you can repost messages from one chat to multiple:

```json
{
    "chats": {
        "@source1": [
            "@target1",
            "@target2",
            "@target3",
            "-100123456789",
            "t.me/+abcd1234"
        ],
        "@source2": [
            "@target4",
            "@target5"
        ]
    }
}
```

### env variables: reposter_data_dir

- `reposter_data_dir` - directory to store reposter config and session
- if there is no `reposter_data_dir` variable, program looks for `XDG_DATA_HOME` variable
- if there is no `XDG_DATA_HOME` variable, program works in portable way and creates `data` directory near `reposter` dir which contains code

### env variables: reposter_conf

- `reposter_conf` - path to `config.json` file
- if there is no `reposter_data_dir` variable, program looks for `XDG_CONFIG_HOME` variable
- if there is no `XDG_CONFIG_HOME` variable, program creates config in `data` directory

### env variables: session_name

- `session_name` - name of tg session, defatults to `tg_bot`, so session file would be `tg_bot.session`
- if you set it to something like `my_session`, session file would be `my_session.session`

### env variables: tests

- `tests` - if set to `true`, autotests are started
- `big_tests` - if set to `true`, autotests with additional tests for big 10mb+ files are started
- big tests takes more time then regular tests

