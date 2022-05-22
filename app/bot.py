from app import func as f
from app.init import config_load, data_dir, downloads, c
from libs.rich import pretty  # type: ignore
from traceback import format_exc
from pathlib import Path
import pyrogram  # type: ignore
from pyrogram import errors, filters  # type: ignore
import time
import os


config = config_load()
pretty.install()
cache = []
bot = None


class Handler:
    def __init__(
        self,
        source,
        target,
        forward_way,
    ):
        self.source = source
        self.runned = False
        self.latest_id = 0
        self.callback_message = None

        if forward_way == 'save_on_disk':
            backup = self.save_on_disk
        else:
            backup = self.forward

        if isinstance(target, str):
            self.targets = [target]
        else:
            self.targets = target

        bot.add_handler(
            pyrogram.handlers.MessageHandler(
                backup,
                filters = (
                    filters.chat(
                        source
                    )
                )
            )
        )

    def progress_callback(self, loaded, total):
        text = f'{loaded * 100 // total}% {loaded}/{total}'
        c.log(text)
        if 'log_chat' in config and config['log_chat']:
            if self.callback_message:
                self.callback_message.edit(
                    text = text
                )
            else:
                bot.send_message(
                    chat_id = config['log_chat'],
                    text = text,
                )

    def forward(
        self,
        _,
        msg,
    ):
        if msg.edit_date:
            return
        log(msg)
        if msg.media_group_id:
            if msg.media_group_id > self.latest_id:
                self.latest_id = msg.media_group_id
            else:
                return
        for target in self.targets:
            if msg.media_group_id:
                bot.copy_media_group(
                    chat_id = target,
                    from_chat_id = msg.chat.id,
                    message_id = msg.id,
                )
            else:
                msg.copy(
                    target,
                )

    def save_on_disk(
        self,
        _,
        msg,
    ):
        while self.runned:
            time.sleep(1)
        self.runned = True
        print()
        if msg.media_group_id:
            id = msg.media_group_id
            log(f'latest = {self.latest_id}')
            log(f'id = {id}')
            if id <= self.latest_id:
                log('aborted')
                self.runned = False
                return 'aborted'
            self.latest_id = id
            log(f'now latest is {self.latest_id}')
            print()
        log(msg)
        if msg.edit_date:
            self.runned = False
            return
        for target in self.targets:
            local_downloads = f'{downloads}/{target}/'
            f.rmtree(local_downloads)
            log(msg)

            def download(msg, index = None):
                media_type = msg.media.value
                file_id = getattr(
                    msg,
                    media_type,
                ).file_id
                log('downloading file:')
                log(f'file_id = {file_id}')
                caption = msg.caption
                log(f'caption = {caption}')
                log(f'media_type = {media_type}')
                self.callback_message = None
                path = Path(
                    f.clean_path(
                        bot.download_media(
                            msg,
                            file_name = local_downloads,  # path to save file
                            progress = self.progress_callback
                        )
                    )
                )
                self.callback_message = None
                if index is not None:
                    new_path = f'{path.parent}/{index}{path.suffix}'
                    os.rename(
                        path,
                        new_path,
                    )
                    path = new_path

                log(f'downloaded {path}')
                return (path, caption)

            if msg.media_group_id:
                log(f'found media group: {msg.media_group_id}')
                files = []
                for index, sub_msg in enumerate(
                    bot.get_media_group(
                        msg.chat.id, msg.id
                    )
                ):
                    downloaded = download(sub_msg, index)
                    if downloaded != 'aborted':
                        path, caption = downloaded
                        files.append(
                            getattr(
                                pyrogram.types,
                                f'InputMedia{sub_msg.media.value.title()}'
                            )(
                                media = path,
                                caption = caption,
                            )
                        )
                if files:
                    log(
                        'sending files',
                        files,
                    )
                    bot.send_media_group(
                        chat_id = target,
                        media = files,
                    )
                    log('done.')
            elif msg.media:
                c.log(msg.media.value)
                downloaded = download(msg)
                if downloaded != 'aborted':
                    path, caption = downloaded
                    log(
                        f'sending {msg.media.value} {path}'
                    )
                    self.callback_message = None
                    getattr(
                        bot,
                        f'send_{msg.media.value}',
                    )(
                        target,
                        path,
                        caption = caption,
                        progress = self.progress_callback,
                    )
                    self.callback_message = None
            elif msg.text:
                log(f'sending text "{msg.text}"')
                send_msg(
                    chat_id = target,
                    text = msg.text,
                )
        self.runned = False


def send_msg(
    text: str,
    chat_id = None,
    quote = None,
    entities = None,
    disable_web_page_preview = None,
    disable_notification = None,
    reply_to_message_id = None,
    schedule_date = None,
    protect_content = None,
    reply_markup = None,
    mono = False,
    pin = False,
    msg_r = None,
    parse_mode = None,
    **kwargs,
):
    if parse_mode:
        kwargs['parse_mode'] = parse_mode
    sended_message = None
    for chunk in f.text_wrap(text):
        if mono:
            chunk = '```' + chunk + '```'
        if chat_id:
            try:
                sended_message = bot.send_message(
                    chat_id = chat_id,
                    text = chunk,
                    entities = entities,
                    disable_web_page_preview = disable_web_page_preview,
                    disable_notification = disable_notification,
                    reply_to_message_id = reply_to_message_id,
                    schedule_date = schedule_date,
                    protect_content = protect_content,
                    reply_markup = reply_markup,
                    **kwargs
                )
            except:
                log(
                    f'error sending {text} to {chat_id}\n\n{format_exc()}',
                    chat = 'bugreport_chat',
                    check_if_in_config = True,
                )
        elif msg_r:
            sended_message = msg_r.reply(
                text = chunk,
                quote = quote,
                parse_mode = parse_mode,
                entities = entities,
                disable_web_page_preview = disable_web_page_preview,
                disable_notification = disable_notification,
                reply_to_message_id = reply_to_message_id,
                reply_markup = reply_markup,
                **kwargs
            )
        else:
            raise AttributeError(
                'Please specify "chat_id"'
            )
        if pin:
            sended_message.pin(
                both_sides = True
            )
            pin = False
    return sended_message


def log(
    *args,
    chat = 'log_chat',
    pin = False,
    check_if_in_config = False,
):
    c.log(*args)

    if chat in ('log_chat', 'bugreport_chat'):
        check_if_in_config = True

    if check_if_in_config:
        if chat not in config:
            return
        chat = config[chat]

    for i in args:
        if chat:
            send_msg(
                chat_id = chat,
                text = i,
                pin = pin,
            )


def start_bot(
    start_message = 'bot started'
):
    global bot

    phone_number = str(config['phone_number'])
    if phone_number[0] != '+':
        phone_number = '+' + phone_number

    bot = pyrogram.Client(
        name = 'bot',
        api_id = config['api_id'],
        api_hash = config['api_hash'],
        phone_number = phone_number,
        workdir = data_dir,
    )

    handlers = []

    for chat in config['chats']:
        handlers.append(
            Handler(
                source = chat['source'],
                target = chat['target'],
                forward_way = chat['forward_way'],
            )
        )

    try:
        bot.start()
    except:
        pass
    log(start_message)
    pyrogram.idle()


def main(
    start_message = 'bot started'
):
    while True:
        try:
            start_bot(start_message)
        except (
            errors.exceptions.flood_420.FloodWait,
        ):
            pass
        except:
            try:
                log(
                    format_exc(),
                    chat = 'bugreport_chat',
                    pin = True,
                    check_if_in_config = True,
                )
                log('restart in 5 seconds')
                time.sleep(5)
            except:
                pass
