from reposter.core.common import app
import reposter.core.common
import reposter.core.types
import pyrogram.types
import typing


async def get_msgs(
    from_chat: str,
    max_id: int,
    min_id: int,
    remove_progress: bool = True,
) -> reposter.core.types.msg_gen:
    max_id +=1
    min_id -=1
    total = max_id - min_id - 1
    assert total > 0
    history_generator = reposter.core.common.tg.client.get_chat_history(
        chat_id=from_chat,
        offset_id=max_id,
        max_id=max_id,
        min_id=min_id,
    )
    assert isinstance(history_generator, typing.AsyncGenerator)
    task_id = app.progress.add_task(
        description=f'msgs in {from_chat}',
        total=total,
    )
    async for msg in history_generator:
        assert isinstance(msg, pyrogram.types.Message)
        if msg.empty:
            continue
        app.progress.update(
            task_id=task_id,
            completed=max_id - msg.id,
        )
        yield msg
    app.progress.update(
        task_id=task_id,
        completed=total,
    )
    app.progress.stop_task(task_id)
    if remove_progress:
        app.progress.update(
            task_id=task_id,
            visible=False,
        )

