from reposter.core import common, config
import reposter.tg.save_file
import pyrogram.client
import types
import os


async def init():
    set_env()
    get_client()
    await common.tg.client.start()


def get_client() -> None:
    common.tg.client = pyrogram.client.Client(
        name='tg_bot',
        api_id=config.env.api_id,
        api_hash=config.env.api_hash,
        workdir=str(common.path.data),
        sleep_threshold=0,
    )
    common.tg.client.save_file = types.MethodType(
        reposter.tg.save_file.save_file_custom_wrapper,
        common.tg.client,
    )


def set_env() -> None:
    for key, value_type in config.env.__annotations__.items():
        value = os.getenv(key)
        if value:
            assert isinstance(value_type, type)
            assert isinstance(value, value_type)
            setattr(config.env, key, value)


def before_shutdown() -> None:
    common.log('exiting')
    common.app.progress.stop()
    common.app.console.show_cursor()


async def shutdown() -> None:
    before_shutdown()
    await common.tg.client.stop()
    os._exit(0)

