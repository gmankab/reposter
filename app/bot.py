from app import func as f
from app.init import config_load, data_dir, downloads, c
from libs.rich import pretty
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
        self.target = target
        self.runned = False
        self.latest_id = 0
        self.callback_message = None
        self.downloads = f'{downloads}/{self.target}/'
        if forward_way == 'save_on_disk':
            backup = self.save_on_disk
        else:
            backup = self.forward
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
        text = loaded * 100 // total
        c.log(text)
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
            bot.copy_media_group(
                chat_id = self.target,
                from_chat_id = msg.chat.id,
                message_id = msg.message_id,
            )
        else:
            msg.copy(
                self.target,
            )

    def save_on_disk(
        self,
        _,
        msg,
    ):
        log(msg)
        if msg.edit_date:
            return
        while self.runned:
            time.sleep(1)
        self.runned = True
        f.rmtree(downloads)
        log(msg)

        def download(msg, index = None):
            print()
            id = msg.message_id
            log(f'latest = {self.latest_id}')
            log(f'id = {id}')
            if id <= self.latest_id:
                log('aborted')
                return 'aborted'
            self.latest_id = id
            log(f'now latest is {self.latest_id}')
            print()

            media_type = msg.media
            file_id = msg[media_type].file_id
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
                        file_name = self.downloads,  # path to save file
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
                    msg.chat.id, msg.message_id
                )
            ):
                downloaded = download(sub_msg, index)
                if downloaded != 'aborted':
                    path, caption = downloaded
                    files.append(
                        getattr(
                            pyrogram.types,
                            f'InputMedia{sub_msg.media.title()}'
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
                chat_id = self.target,
                media = files,
            )
            log('done.')
        elif msg.media:
            downloaded = download(msg)
            if downloaded != 'aborted':
                path, caption = downloaded
                log(
                    f'sending {msg.media} {path}'
                )
                self.callback_message = None
                if caption:
                    getattr(
                        bot,
                        f'send_{msg.media}',
                    )(
                        self.target,
                        path,
                        caption = caption,
                        progress = self.progress_callback,
                    )
                else:
                    getattr(
                        bot,
                        f'send_{msg.media}',
                    )(
                        self.target,
                        path,
                    progress = self.progress_callback,
                    )
                self.callback_message = None
        elif msg.text:
            log(f'sending text "{msg.text}"')
            send_msg(
                chat_id = self.target,
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
                    parse_mode = parse_mode,
                    entities = entities,
                    disable_web_page_preview = disable_web_page_preview,
                    disable_notification = disable_notification,
                    reply_to_message_id = reply_to_message_id,
                    schedule_date = schedule_date,
                    protect_content = protect_content,
                    reply_markup = reply_markup,
                )
            except:
                log(
                    text = f'error sending {text} to {chat_id}\n\n{format_exc()}',
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
    text,
    chat = 'log_chat',
    pin = False,
    check_if_in_config = False,
):
    c.log(text)

    if chat == 'log_chat':
        check_if_in_config = True

    if check_if_in_config:
        if chat not in config:
            return
        chat = config[chat]

    if chat:
        send_msg(
            chat_id = chat,
            text = text,
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
                    text = format_exc(),
                    chat = 'bugreport_chat',
                    pin = True,
                    check_if_in_config = True,
                )
                log('restart in 5 seconds')
                time.sleep(5)
            except:
                pass
