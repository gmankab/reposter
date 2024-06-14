import reposter.core.common
import reposter.core.types
import reposter.tg.chunk_gen
import pyrogram.client
import pyrogram.types
import rich.progress
import typing
import io


class Resender():
    def __init__(
        self,
        source_msg: pyrogram.types.Message,
        target_chat: int | str,
        remove_progress_bar: bool = True,
    ) -> None:
        self.msg: pyrogram.types.Message = source_msg
        self.progress = reposter.core.common.app.progress
        self.client: pyrogram.client.Client = reposter.core.common.tg.client
        self.task_id: rich.progress.TaskID
        self.remove_progress_bar: bool = remove_progress_bar
        self.big_file_size = 10 * 1024 * 1024
        self.target_chat: int | str = target_chat
        self.send_kwargs: dict[str, typing.Any] = {
            'chat_id': self.target_chat,
        }
        self.capiton_sep: str = ''
        if self.msg.chat.username:
            self.link = f'{self.msg.chat.username}/{self.msg.id}'
        else:
            self.link = f'{self.msg.chat.full_name}/{self.msg.id}'
        self.media_value: str = ''
        if self.msg.media:
            if isinstance(self.msg.media.value, str):
                self.media_value: str = self.msg.media.value
        self.send_method: typing.Callable
        self.media_file: reposter.core.types.media_file
        self.sent_msg: pyrogram.types.Message

    async def resend_anything(self) -> None:
        if self.msg.text:
            await self.client.send_message(
                chat_id=self.target_chat,
                text=self.msg.text.markdown
            )
            return
        self.set_caption()
        media = getattr(self.msg, self.media_value)
        if isinstance(media, reposter.core.types.media_file):
            self.media_file = media
            self.send_method = getattr(self.client, f'send_{self.media_value}')
            if self.media_file.file_size > self.big_file_size:
                await self.send_big_file()
            else:
                await self.send_small_file()
        if self.capiton_sep:
            assert self.sent_msg
            await self.sent_msg.reply_text(
                text=self.capiton_sep,
                quote=True,
            )

    def set_caption(self) -> None:
        if self.msg.caption:
            if len(self.msg.caption) > 1024:
                assert self.client.me
                if not self.client.me.is_premium:
                    self.capiton_sep = self.msg.caption
            if not self.capiton_sep:
                self.send_kwargs['caption'] = self.msg.caption.markdown

    async def send_small_file(self) -> None:
        self.start_progress(
            description=f'download {self.link}',
            total=self.media_file.file_size,
        )
        file = await self.msg.download(
            in_memory=True,
            block=True,
            progress=self.progress_update,
        )
        assert isinstance(file, io.BytesIO)
        self.send_kwargs[self.media_value] = file
        self.send_kwargs['progress'] = self.progress_update
        self.progress.update(
            task_id=self.task_id,
            description=f'upload {self.link}',
        )
        self.sent_msg: pyrogram.types.Message = await self.send_method(
            **self.send_kwargs,
        )
        self.end_progress()

    async def send_big_file(self) -> None:
        chunk_gen = reposter.tg.chunk_gen.ChunkGen(
            msg=self.msg,
            media=self.media_file,
        )
        self.send_kwargs[self.media_value] = chunk_gen
        self.sent_msg: pyrogram.types.Message = await self.send_method(
            **self.send_kwargs,
        )

    def progress_update(
        self,
        completed: int,
        _,
    ) -> None:
        self.progress.update(
            task_id=self.task_id,
            completed=completed
        )

    def start_progress(
        self,
        description: str,
        total: int,
    ) -> None:
        self.task_id = self.progress.add_task(
            description=description,
            total=total,
            transfer=True,
        )

    def end_progress(
        self,
    ) -> None:
        self.progress.stop_task(
            task_id=self.task_id,
        )
        if self.remove_progress_bar:
            self.progress.update(
                task_id=self.task_id,
                visible=False,
            )

    async def send_poll(self) -> None:
        options = []
        for option in self.msg.poll.options:
            options.append(
                option.text
            )
        await self.client.send_poll(
            chat_id = self.target_chat,
            question = self.msg.poll.question,
            options = options,
            allows_multiple_answers = self.msg.poll.allows_multiple_answers,
        )

