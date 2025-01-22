import reposter.handlers.other
import reposter.funcs.handle
import reposter.core.common
import reposter.core.config
import reposter.core.types


class StreamNotify:
    def __init__(
        self,
        target_any: reposter.core.types.target,
    ) -> None:
        self.delay: int = 5
        self.repeat_count: int = 40
        self.target_any: reposter.core.types.target = target_any
        self.progress = reposter.core.common.app.progress
        self.text: str = ''
        assert isinstance(self.target_any, (str, int, list))
        assert isinstance(reposter.core.config.json.stream_notify_chats, list)

    async def notify_all(
        self,
    ):
        reposter.core.common.tg.stream_notificating_now = True
        task_id_big = self.progress.add_task(
            description='stream notifications',
            total=self.repeat_count,
        )
        task_id_little = self.progress.add_task(
            description=f'{self.delay} seconds delay',
        )
        for index in range(self.repeat_count):
            self.progress.update(
                task_id=task_id_big,
                completed=index,
            )
            self.text = f'stream notifications {index+1}/{self.repeat_count}'
            await reposter.handlers.other.parse_targets(
                target_any=reposter.core.config.json.stream_notify_chats,
                to_call=self.notify_one,
            )
            await reposter.funcs.handle.wait(
                seconds=self.delay,
                task_id=task_id_little,
                hide=False,
            )
            if not reposter.core.common.tg.stream_notificating_now:
                break
        for task in task_id_big, task_id_little:
            self.progress.update(
                task_id=task,
                visible=False,
            )
            self.progress.stop_task(
                task_id=task,
            )
        reposter.core.common.tg.stream_notificating_now = False

    async def notify_one(
        self,
        target: str | int,
    ):
        await reposter.funcs.handle.run_excepted(
            reposter.core.common.tg.client.send_message,
            chat_id=target,
            text=self.text,
            repeat=False,
            to_raise=False,
        )

