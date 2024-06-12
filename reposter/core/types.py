import rich.progress
import pyrogram.types
import typing


cor_str = typing.Coroutine[typing.Any, typing.Any, str]
msg_gen = typing.AsyncGenerator[pyrogram.types.Message, None]
bytes_gen = typing.AsyncGenerator[bytes, None]
media_file = typing.Union[
    pyrogram.types.Audio,
    pyrogram.types.Photo,
    pyrogram.types.Video,
    pyrogram.types.Voice,
    pyrogram.types.Sticker,
    pyrogram.types.Document,
    pyrogram.types.Animation,
    pyrogram.types.VideoNote,
]
media_other = typing.Union[
    pyrogram.types.Location,
    pyrogram.types.Story,
    pyrogram.types.Venue,
    pyrogram.types.Poll,
]


class Progress(rich.progress.Progress):
    def get_renderables(self):
        for task in self.tasks:
            if task.fields.get('percents'):
                self.columns = (
                    '➜',
                    rich.progress.BarColumn(),
                    rich.progress.TimeElapsedColumn(),
                    rich.progress.TaskProgressColumn(),
                    rich.progress.TextColumn("[progress.description]{task.description}"),
                )
            elif task.fields.get('transfer'):
                self.columns = (
                    '➜',
                    rich.progress.BarColumn(),
                    rich.progress.TimeElapsedColumn(),
                    rich.progress.TransferSpeedColumn(),
                    rich.progress.FileSizeColumn(),
                    '/',
                    rich.progress.TotalFileSizeColumn(),
                    rich.progress.TextColumn("[progress.description]{task.description}"),
                )
            else:
                self.columns = (
                    '➜',
                    rich.progress.BarColumn(),
                    rich.progress.TimeElapsedColumn(),
                    rich.progress.MofNCompleteColumn(),
                    rich.progress.TextColumn("[progress.description]{task.description}"),
                )
            yield self.make_tasks_table([task])


class NotPassed(Exception):
    def __init__(
        self,
        msg: str = '',
    ):
        self.msg = msg

