from reposter.core.common import app
import reposter.core.common
import reposter.core.types
import pyrogram.types
import typing


async def get_msgs(
    from_chat: str | int,
    start: int,
    stop: int,
) -> reposter.core.types.msg_gen:
    assert reposter.core.common.tg.client.me
    if reposter.core.common.tg.client.me.is_bot:
        async for msg in get_msgs_bot(
            from_chat=from_chat,
            start=start,
            stop=stop,
        ):
            yield msg
    else:
        if start < stop:
            gen = get_msgs_userbot(
                from_chat=from_chat,
                max_id=stop,
                min_id=start,
            )
            async for msg in get_msgs_userbot_reversed(
                gen=gen,
                from_chat=from_chat,
            ):
                yield msg
            return
        gen = get_msgs_userbot(
            from_chat=from_chat,
            max_id=start,
            min_id=stop,
        )
        if start > stop:
            async for msg in gen:
                yield msg
            return
        else:
            async for msg in gen:
                yield msg


async def get_msgs_userbot_reversed(
    gen: reposter.core.types.msg_gen,
    from_chat: str | int,
) -> reposter.core.types.msg_gen:
    cache: list[pyrogram.types.Message] = []
    async for msg in gen:
        cache.insert(0, msg)
    task_id = app.progress.add_task(
        description=f'msgs in {from_chat}',
        total=len(cache),
    )
    for msg in cache:
        app.progress.update(
            task_id=task_id,
            advance=1,
        )
        yield msg
    app.progress.update(
        task_id=task_id,
        completed=len(cache),
    )
    app.progress.stop_task(task_id)
    app.progress.update(
        task_id=task_id,
        visible=False,
    )


async def get_msgs_userbot(
    from_chat: str | int,
    max_id: int,
    min_id: int,
) -> reposter.core.types.msg_gen:
    max_id +=1
    min_id -=1
    total = max_id - min_id - 1
    print(f'{max_id}, {min_id}, {total}')
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
        if not msg.empty:
            yield msg
    app.progress.update(
        task_id=task_id,
        completed=total,
    )
    app.progress.stop_task(task_id)
    app.progress.update(
        task_id=task_id,
        visible=False,
    )


async def get_msgs_bot(
    from_chat: str | int,
    start: int,
    stop: int,
) -> reposter.core.types.msg_gen:
    id_200: list[int] = []
    if start < stop:
        step = 1
        total = stop - start
    elif start > stop:
        step = -1
        total = start - stop
    else:
        msg = await reposter.core.common.tg.client.get_messages(
            chat_id=from_chat,
            message_ids=start,
        )
        assert isinstance(msg, pyrogram.types.Message)
        yield msg
        return
    task_id = app.progress.add_task(
        description=f'msgs in {from_chat}',
        total=total,
    )
    completed = 0
    for num in range(start, stop + step, step):
        if len(id_200) < 200:
            id_200.append(num)
        else:
            async for msg in parse_id_200(
                id_200=id_200,
                from_chat=from_chat,
            ):
                app.progress.update(
                    task_id=task_id,
                    advance=1,
                )
                yield msg
            completed += 200
            app.progress.update(
                task_id=task_id,
                completed=completed,
            )
            id_200 = [num]
    async for msg in parse_id_200(
        id_200=id_200,
        from_chat=from_chat,
    ):
        yield msg
    app.progress.update(
        task_id=task_id,
        completed=total,
    )
    app.progress.stop_task(task_id)
    app.progress.update(
        task_id=task_id,
        visible=False,
    )


async def parse_id_200(
    from_chat: str | int,
    id_200: list[int],
) -> reposter.core.types.msg_gen:
    msgs = await reposter.core.common.tg.client.get_messages(
        chat_id=from_chat,
        message_ids=id_200,
    )
    if isinstance(msgs, list):
        for msg in msgs:
            if not msg.empty:
                yield msg
    else:
        if not msgs.empty:
            yield msgs

