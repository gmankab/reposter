import reposter.core.types
import reposter.core.common
import pyrogram.types
import pyrogram
import typing


class ChunkGen:
    def __init__(
        self,
        msg: pyrogram.types.Message,
        media: reposter.core.types.media_file,
        remove_progress: bool = True,
    ):
        self.remove_progress: bool = remove_progress
        self.progress = reposter.core.common.app.progress
        self.total: int = media.file_size
        self.name: str = getattr(media, 'file_name', 'noname')
        self.msg: pyrogram.types.Message = msg
        self.return_next: bytes = b''
        self.max_chunk_size = 512 * 1024
        if msg.chat.username:
            self.description = f'big file {msg.chat.username}/{msg.id}'
        else:
            self.description = f'big file {msg.chat.full_name}/{msg.id}'
        assert self.total > 10 * 1024 * 1024

    def __aiter__(self):
        return self.stream_512()

    async def stream_512(
        self,
    ) -> typing.AsyncGenerator[bytes, None]:
        task_id = self.progress.add_task(
            description=self.description,
            total=self.total,
            transfer=True,
        )
        stream_1024 = reposter.core.common.tg.client.stream_media(self.msg)
        assert isinstance(stream_1024, typing.AsyncGenerator)
        completed: int = 0
        async for chunk_1024 in stream_1024:
            while len(chunk_1024) > self.max_chunk_size:
                completed += self.max_chunk_size
                self.progress.update(
                    task_id=task_id,
                    completed=completed,
                )
                yield chunk_1024[:self.max_chunk_size]
                chunk_1024 = chunk_1024[self.max_chunk_size:]
            completed += len(chunk_1024)
            self.progress.update(
                task_id=task_id,
                completed=completed,
            )
            yield chunk_1024
        self.progress.stop_task(
            task_id=task_id,
        )
        if self.remove_progress:
            self.progress.update(
                task_id=task_id,
                visible=False,
            )

