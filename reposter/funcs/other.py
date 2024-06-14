from reposter.core import common
import reposter.funcs.parse_conf
import reposter.core.config
import reposter.tg.save_file
import pyrogram.client
import types
import os


async def init():
    reposter.funcs.parse_conf.read_env()
    reposter.funcs.parse_conf.read_config()
    get_client()
    await common.tg.client.start()


def get_client() -> None:
    session_name = 'tg_bot'
    session_path = common.path.data_dir / f'{session_name}.session'
    if not session_path.exists() and not reposter.core.config.json.tg_session:
        if not reposter.core.config.json.api_id or not reposter.core.config.json.api_hash:
            common.log(
                f'[red]\\[error][/] you should set api_id and api_hash in {common.path.config_json}'
            )
    common.tg.client = pyrogram.client.Client(
        name=session_name,
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

