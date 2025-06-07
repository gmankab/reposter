### navigation

- [github repo](https://github.com/gmankab/reposter)
- [gitlab repo](https://gitlab.com/gmanka/reposter)
- [codeberg repo](https://codeberg.org/gmanka/reposter)
- [how to run](https://github.com/gmankab/reposter/blob/main/other/docs/run.md)
- [how to build](https://github.com/gmankab/reposter/blob/main/other/docs/build.md)
- [config](https://github.com/gmankab/reposter/blob/main/other/docs/config.md)
- [env](https://github.com/gmankab/reposter/blob/main/other/docs/env.md)
- [pypi](https://pypi.org/project/reposter)


### default config

```json
{
    "api_id": 0,
    "api_hash": "",
    "tg_session": "",
    "drop_author": true,
    "logs_chat": "me",
    "stream_notify_chats": [],
    "online_status_every_seconds": 0,
    "edit_timeout_seconds": 0,
    "chats": {
        "@autotests_source": "@autotests_target"
    }

}
```

### sessions

- in order to start using reposter you should open https://my.telegram.org and get your `api_id` and `api_hash`, then paste it to `config.json`
- if you have pyrogram/pyrofork session file, you can rename it to `tg_bot.session` and put near `config.json`
- if you have pyrogram/pyrofork session string, you can put it in `config.json` as `tg_session` parameter
- if you already have session file or session string, you can skip putting api_id and api_hash in config

### chats

- `logs_chat` - bot will send logs to this chat, it's recommended to change it from `me` to something else
- `@autotests_source` - chat to take posts from
- `@autotests_target` - chat to send posts to
- `stream_notify_chats` - list of chats to get notifications if source channel starts video chat, notifications can be stopped by writing `/stop` or `/s` in logs chat
- you may want to replace this values with other ones

### chats formats

you can use following formats:
- `"@username"`
- `"t.me/+abcd1234"` (ivite link)
- `"-100123456789"` (id)
- all ids should be strings, not integers
- supergroups and channels ids should start with `-100`

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

### online_status_every_seconds

- set 0 to disable, any other integer to enable
- allows your account to stay online, sometimes it solves issue when some messages not being reposted


### edit_timeout_seconds

- set 0 to disable, any other integer to enable
- if disabled, all edited posts are synced
- if set to 3600, all edited posts older than 1 hour will not be synced

