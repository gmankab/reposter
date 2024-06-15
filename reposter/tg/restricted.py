import reposter.core.common
import reposter.core.config
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
    ) -> None:
        self.msg: pyrogram.types.Message = source_msg
        self.client: pyrogram.client.Client = reposter.core.common.tg.client
        self.task_id: rich.progress.TaskID
        self.target_chat: int | str = target_chat
        if self.msg.chat.username:
            self.link = f'{self.msg.chat.username}/{self.msg.id}'
        else:
            self.link = f'{self.msg.chat.full_name}/{self.msg.id}'
        if self.msg.media:
            self.media_value: str = str(self.msg.media.value)
        else:
            self.media_value: str = 'text'

    async def resend_anything(self) -> None:
        if self.msg.text:
            return await self.send_text()
        if self.msg.media:
            await self.resend_media()

    async def resend_media(self) -> None:
        assert isinstance(self.msg.media.value, str)
        media_any = getattr(self.msg, self.msg.media.value)
        if isinstance(media_any, reposter.core.types.media_file):
            send_media_file = SendMediaFile(
                msg=self.msg,
                media_file=media_any,
                target_chat=self.target_chat,
                link=self.link,
            )
            await send_media_file.send_file_any_size()

    async def send_text(self) -> None:
        await self.client.send_message(
            chat_id=self.target_chat,
            text=self.msg.text.markdown
        )


class SendMediaFile:
    def __init__(
        self,
        msg: pyrogram.types.Message,
        media_file: reposter.core.types.media_file,
        target_chat: str | int,
        link: str,
    ) -> None:
        self.msg: pyrogram.types.Message = msg
        self.media_file: reposter.core.types.media_file = media_file
        self.target_chat: str | int = target_chat
        self.link: str = link
        self.progress = reposter.core.common.app.progress
        self.client: pyrogram.client.Client = reposter.core.common.tg.client
        self.capiton_sep: str = ''
        self.media_value: str = str(self.msg.media.value)
        self.send_method: typing.Callable = getattr(self.client, f'send_{self.media_value}')
        self.send_kwargs: dict[str, typing.Any] = {
            'chat_id': self.target_chat,
        }

    async def send_file_any_size(self) -> None:
        _1mb: int = 1024 * 1024
        _5mb: int = _1mb * 5
        _10mb: int = _1mb * 10
        self.set_caption()
        if self.media_file.file_size > _5mb:
            if reposter.core.config.env.tests:
                if not reposter.core.config.env.big_tests:
                    raise reposter.core.types.SkipError()
        if self.media_file.file_size > _10mb:
            sent_msg = await self.send_file_big()
        else:
            sent_msg = await self.send_file_small()
        if self.capiton_sep:
            await sent_msg.reply_text(
                text=self.capiton_sep,
                quote=True,
            )

    async def download_file_small(self) -> io.BytesIO:
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
        return file

    async def send_file_small(self) -> pyrogram.types.Message:
        self.send_kwargs[self.media_value] = await self.download_file_small()
        self.send_kwargs['progress'] = self.progress_update
        self.progress.update(
            task_id=self.task_id,
            description=f'upload {self.link}',
        )
        sent_msg = await self.send_method(
            **self.send_kwargs,
        )
        self.stop_progress()
        return sent_msg

    async def send_file_big(self) -> pyrogram.types.Message:
        chunk_gen = reposter.tg.chunk_gen.ChunkGen(
            msg=self.msg,
            media=self.media_file,
        )
        self.send_kwargs[self.media_value] = chunk_gen
        return await self.send_method(
            **self.send_kwargs,
        )

    def set_caption(self) -> None:
        if self.msg.caption:
            if len(self.msg.caption) > 1024:
                assert self.client.me
                if not self.client.me.is_premium:
                    self.capiton_sep = self.msg.caption
            if not self.capiton_sep:
                self.send_kwargs['caption'] = self.msg.caption.markdown

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

    def stop_progress(
        self,
    ) -> None:
        self.progress.stop_task(
            task_id=self.task_id,
        )
        self.progress.update(
            task_id=self.task_id,
            visible=False,
        )

