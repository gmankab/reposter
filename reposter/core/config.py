import reposter.core.common


class tests:
    source: str = '@autotests_source'
    target: str = '@autotests_target'
    min_id: int = 107
    max_id: int = 121


class env:
    XDG_CONFIG_HOME: str
    XDG_DATA_HOME: str
    session_name: str
    reposter_data_dir: str
    reposter_conf: str
    tg_session: str
    big_tests: str
    tests: str


class json:
    app_version: str
    api_id: int
    api_hash: str
    tg_session: str
    drop_author: bool
    logs_chat: str | int
    stream_notify_chats: list
    edit_timeout_seconds: int
    repost_delay_seconds: int
    online_status_every_seconds: int
    chats: dict


default = {
    'app_version': reposter.core.common.app.version,
    'api_id': 0,
    'api_hash': '',
    'tg_session': '',
    'drop_author': True,
    'logs_chat': 'me',
    'stream_notify_chats': [],
    'edit_timeout_seconds': 0,
    'repost_delay_seconds': 0,
    'online_status_every_seconds': 0,
    'chats': {
        tests.source: tests.target,
    }
}

