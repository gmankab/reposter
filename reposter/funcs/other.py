from reposter.core import common, config
import reposter.funcs.parse_conf
import reposter.core.config
import reposter.tg.save_file
import pyrogram.client
import types
import os


async def init():
    reposter.funcs.parse_conf.read_env()
    reposter.funcs.parse_conf.check_env()
    reposter.funcs.parse_conf.read_config()
    reposter.funcs.parse_conf.check_config()
    get_client()
    await common.tg.client.start()
    await start_log()


async def start_log():
    try:
        reposter.core.config.json.logs_chat = int(reposter.core.config.json.logs_chat)
    except Exception:
        pass
    await common.tg.client.send_message(
        chat_id=config.json.logs_chat,
        text=f'started {common.app.name} {common.app.version}',
    )


def get_client() -> None:
    common.tg.client = pyrogram.client.Client(
        name=config.env.session_name,
        api_id=reposter.core.config.json.api_id,
        api_hash=reposter.core.config.json.api_hash,
        session_string=reposter.core.config.json.tg_session,
        workdir=str(common.path.data_dir),
        sleep_threshold=0,
    )
    common.tg.client.save_file = types.MethodType(
        reposter.tg.save_file.save_file_custom_wrapper,
        common.tg.client,
    )


def before_shutdown() -> None:
    common.log('[green]\\[exiting]')
    common.app.progress.stop()
    common.app.console.show_cursor()


async def shutdown() -> None:
    before_shutdown()
    await common.tg.client.stop()
    os._exit(common.app.exit_code)


def single_link(
    msg: pyrogram.types.Message,
) -> str:
    if msg.chat.username:
        return f'{msg.chat.username}/{msg.id}'
    else:
        return f'{msg.chat.full_name}/{msg.id}'


def double_links(
    source_msg: pyrogram.types.Message,
    target_msg: pyrogram.types.Message,
) -> str:
    return f'[blue]{single_link(source_msg)}[/] -> [yellow]{single_link(target_msg)}[/]'

