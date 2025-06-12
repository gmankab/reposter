### navigation

- [github repo](https://github.com/gmankab/reposter)
- [gitlab repo](https://gitlab.com/gmanka/reposter)
- [codeberg repo](https://codeberg.org/gmanka/reposter)
- [how to run](https://github.com/gmankab/reposter/blob/main/other/docs/run.md)
- [contributing](https://github.com/gmankab/reposter/blob/main/other/docs/contributing.md)
- [config](https://github.com/gmankab/reposter/blob/main/other/docs/config.md)
- [env](https://github.com/gmankab/reposter/blob/main/other/docs/env.md)
- [pypi](https://pypi.org/project/reposter)

### run via pip (recommended, any os)

```sh
python -m ensurepip
python -m pip install reposter
python -m reposter
```

### run on windows

download and run [reposter.bat](https://gitlab.com/gmanka/reposter/-/raw/main/other/launcher/reposter.bat?inline=false)

### run container using podman and systemd

```sh
mkdir ~/.config/containers/systemd
cd ~/.config/containers/systemd
https://raw.githubusercontent.com/gmankab/reposter/refs/heads/main/other/container/reposter.container | tee ~/.config/containers/systemd/reposter.container
systemctl --user daemon-reload
systemctl --user start reposter
systemctl --user status reposter
```

### usage guide

- by default reposter waits for all new message in chat, and when new message arrives, it gets reposted
- for configuring guide see [config](https://github.com/gmankab/reposter/blob/main/other/docs/config.md) page
- also you can repost messages by their id range, if you set following environment variables

```sh
source=@source_chat target=@target_chat msg_start=1 msg_stop=10 python -m reposter
```

- `source` - chat to take posts from
- `target` - chat to send posts to
- `msg_start` - first message to be reposted
- `msg_stop` - last message to be reposted

you can use following formats:

- `source=@username` - username
- `source=t.me/+abcd1234` - ivite link
- `source=-100123456789` - id
- supergroups and channels ids should start with `-100`

