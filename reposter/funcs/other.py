import reposter.funcs.parse_conf
import reposter.core.config
import reposter.core.common
import pyrogram.client
import reposter.tg.save_file
import reposter.db.init
import hashlib
import types
import sys
import io
import os


async def init():
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    reposter.funcs.parse_conf.read_env()
    reposter.funcs.parse_conf.check_env()
    reposter.funcs.parse_conf.read_config()
    reposter.funcs.parse_conf.check_config()
    await reposter.db.init.init()
    get_client()
    await reposter.core.common.tg.client.start()
    await start_log()


async def start_log():
    try:
        reposter.core.config.json.logs_chat = int(reposter.core.config.json.logs_chat)
    except Exception:
        pass
    logs_chat = await reposter.core.common.tg.client.get_chat(reposter.core.config.json.logs_chat)
    assert isinstance(logs_chat, pyrogram.types.Chat)
    reposter.core.common.tg.logs_chat = logs_chat
    assert reposter.core.common.tg.client.me
    if reposter.core.common.tg.client.me.id == reposter.core.common.tg.logs_chat.id:
        if reposter.core.common.tg.client.me.is_bot:
            return
    await reposter.core.common.tg.client.send_message(
        chat_id=reposter.core.common.tg.logs_chat.id,
        text=f'started {reposter.core.common.app.name} {reposter.core.common.app.version}',
    )


def get_client() -> None:
    reposter.core.common.tg.client = pyrogram.client.Client(
        name=reposter.core.config.env.session_name,
        api_id=reposter.core.config.json.api_id,
        api_hash=reposter.core.config.json.api_hash,
        session_string=reposter.core.config.json.tg_session,
        workdir=str(reposter.core.common.path.data_dir),
        sleep_threshold=0,
    )
    reposter.core.common.tg.client.save_file = types.MethodType(
        reposter.tg.save_file.save_file_custom_wrapper,
        reposter.core.common.tg.client,
    )


def before_shutdown() -> None:
    reposter.core.common.log('[green]\\[exiting]')
    reposter.core.common.app.progress.stop()
    reposter.core.common.app.console.show_cursor()


async def shutdown() -> None:
    before_shutdown()
    await reposter.core.common.tg.client.stop()
    os._exit(reposter.core.common.app.exit_code)


def single_link(
    msg: pyrogram.types.Message,
) -> str:
    if msg.chat.username:
        return f'{msg.chat.username}/{msg.id}'
    else:
        return f'{msg.chat.full_name}/{msg.id}'


def double_links(
    src_msg: pyrogram.types.Message,
    target_msg: pyrogram.types.Message,
) -> str:
    return f'[blue]{single_link(src_msg)}[/] -> [yellow]{single_link(target_msg)}[/]'


def get_hash(
    msg: pyrogram.types.Message,
) -> str:
    hash = hashlib.new('sha256')
    if msg.text:
        to_hash = msg.text.markdown.encode()
    elif msg.caption:
        to_hash = msg.caption.markdown.encode()
    else:
        return ''
    hash.update(to_hash)
    return hash.hexdigest()

