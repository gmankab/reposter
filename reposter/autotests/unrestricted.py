from reposter.core import common
import reposter.tg.unrestricted
import reposter.core.types
import reposter.funcs.handle
import typing


async def get_msgs(
    description: str,
    from_chat: str,
    max_id: int,
    min_id: int,
) -> reposter.core.types.msg_gen:
    max_id +=1
    min_id -=1
    total = max_id - min_id - 1
    assert total > 0
    history_generator = common.tg.client.get_chat_history(
        chat_id=from_chat,
        offset_id=max_id,
        max_id=max_id,
        min_id=min_id,
    )
    assert isinstance(history_generator, typing.AsyncGenerator)
    task_id = common.app.progress.add_task(
        description=description,
        total=total,
    )
    async for msg in history_generator:
        common.app.progress.update(
            task_id=task_id,
            completed=max_id - msg.id,
        )
        yield msg
    common.app.progress.update(
        task_id=task_id,
        completed=total,
    )
    common.app.progress.stop_task(task_id)


async def unrestricted() -> str:
    async for msg in get_msgs(
        description='unrestricted',
        from_chat='@tgparse_chat',
        max_id=6,
        min_id=2,
    ):
        await reposter.funcs.handle.run_excepted(
            callable=reposter.tg.unrestricted.forward,
            source_msg=msg,
            target_chat='me',
        )
    return 'unrestricted repost test passed'

