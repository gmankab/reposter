from app.init import config_load, cwd, yml
from app.libs.dateutil.relativedelta import relativedelta
from app.libs import pyrogram
from app.libs import rich
from app import func as f
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path
import os


config = config_load()
filters = pyrogram.filters
cache = []


bot = pyrogram.Client(
    name = 'bot',
    bot_token = config['bot_token'],
    api_id = config['api_id'],
    api_hash = config['api_hash'],
    workdir = cwd,
)

chats_blacklist = []
ban_list_path = f'{cwd}/ban_list.yml'

if Path(ban_list_path).exists() and os.stat(ban_list_path).st_size != 0:
    ban_list =  yml.load(open(ban_list_path, 'r'))
else:
    ban_list =  []

console = rich.console.Console()
log = console.log


def get_first_button(msg):
    return InlKb([[msg.reply_markup.inline_keyboard[0][0]]])


def callback_filter(*got_callback):
    async def func(
        __,
        _,
        target_callback
    ):
        for i in got_callback:
            if i in target_callback.data:
                return True
        # return target_callback.data in got_callback
        return False

    return filters.create(
        func = func,
        data = got_callback,
    )


async def dump_ban_list(
    data
):
    yml.dump(
        data,
        open(
            ban_list_path,
            'w',
        ),
    )
    if 'database_log_chat' in config and config['database_log_chat']:
        return await bot.send_document(
            chat_id = config['database_log_chat'],
            document = ban_list_path,
        )


async def is_banned(
    user_id,
):
    now = datetime.now().replace(
        microsecond = 0,
    )
    updated = False
    for item in ban_list.copy():
        if item['time'] != 'forever':
            if datetime.fromisoformat(item['time']) <  now:
                ban_list.remove(item)
                updated = True
                if item['user'] == user_id:
                    await dump_ban_list(ban_list)
                    return False
        if updated:
            await dump_ban_list(ban_list)
        if item['user'] == user_id:
            if item['time'] == 'forever':
                return 'forever'
            return datetime.fromisoformat(
                item['time']
            ) - now
    if updated:
        await dump_ban_list(ban_list)
    return False


async def forward(
    msg,
    target,
):
    if msg.media_group_id:
        now = datetime.now().replace(
        microsecond = 0
    )
        deadline = now - timedelta(
            seconds = 3
        )
        if cache:
            for item in cache:
                cached_id, time = item
                if cached_id == msg.media_group_id:
                    return
                if time < deadline:
                    cache.remove(item)
        cache.append((msg.media_group_id, now))
        return (
            await bot.copy_media_group(
                chat_id = target,
                from_chat_id = msg.chat.id,
                message_id = msg.message_id,
                captions = msg.caption,
            )
        )[0]
    else:
        return await msg.copy(
            target,
        )


@dataclass
class Bot:
    help_message = '''\
Я - бот для предложки, как в вк. Пришли сообщение, чтобы предложить его в @example_gmanka_channel

Автор бота - @gmanka. Делаю ботов, 4000 рублей или 50 баксов/евро за бота. Оплата в рублях, долларах, евро и крипте. Писать только по деловым предложениям. Резюме - github.com/gmankab

Исходники - github.com/gmankab/suggest
О багах в боте сообщать в @suggest_chat
'''


@dataclass
class Buttons:
    suggest = InlKb(
        [
            [
                Button(
                    text = '✅проверил, отправить',
                    callback_data = 'suggest',
                ),
            ],
        ],
    )
    open_ban_menu = Button(
        text = '💀забанить',
        callback_data = 'open_ban_menu',
    )
    unban = Button(
        text = '❤️разбанить',
        callback_data = 'unban',
    )

    @staticmethod
    def publish(
        notify,
        ban_button,
    ):
        return InlKb(
            [
                [
                    ban_button,
                    Button(
                        text = '⛔отклонить',
                        callback_data = f'cancel {notify}',
                    ),
                    Button(
                        text = '✅опубликовать',
                        callback_data = f'publish {notify}',
                    ),
                ],
            ],
        )

    ban_menu = InlKb(
        [
            [
                Button(
                    text = '✅скрыть меню',
                    callback_data = 'close_ban_menu',
                )
            ], [
                Button(
                    text = 'забанить навсегда',
                    callback_data = 'ban forever',
                )
            ], [
                Button(
                    text = 'забанить на год',
                    callback_data = 'ban year',
                )
            ], [
                Button(
                    text = 'забанить на месяц',
                    callback_data = 'ban month',
                )
            ], [
                Button(
                    text = 'забанить на неделю',
                    callback_data = 'ban week',
                )
            ], [
                Button(
                    text = 'забанить на 2 минуты',
                    callback_data = 'ban 2_min',
                )
            ], [
                Button(
                    text = '✅скрыть меню',
                    callback_data = 'close_ban_menu',
                )
            ],
        ],
    )


@bot.on_message(
    filters.command(
        [
            'help',
            'start',
            'h',
            's'
        ]
    )
)
async def start_command(
    _,
    msg
):
    await msg.reply(
        Bot.help_message
    )


@bot.on_message()
async def on_message(
    app,
    msg
):
    chat = msg.chat.id
    if chat in chats_blacklist:
        return

    forwarded = await forward(
        msg,
        chat,
    )

    if forwarded:
        await forwarded.reply(
            text = 'Проверь этот пост, потому что его нельзя будет отредактировать или удалить',
            quote = True,
            reply_markup = Buttons.suggest
        )


@bot.on_callback_query(
    callback_filter(
        'empty'
    )
)
def answer_empty(
    _,
    cb,
):
    cb.answer()


@bot.on_callback_query(
    callback_filter(
        'cancel'
    )
)
async def cancel(
    _,
    cb,
):
    await cb.message.edit(
        text = f'{f.get_text(cb.message)}\n⛔Админ {cb.from_user.mention()} отклонил пост, юзер получил уведомление.',
        reply_markup = get_first_button(cb.message),
    )

    chat, msg = cb.data.split(' ', 1)[-1].split('/', 1)
    await bot.send_message(
        text = '⛔Твой пост отклонен',
        chat_id = int(chat),
        reply_to_message_id = int(msg),
    )


@bot.on_callback_query(
    callback_filter(
        'publish'
    )
)
async def publish(
    _,
    cb,
):
    await cb.message.edit(
        text = f'{f.get_text(cb.message)}\n✅Админ {cb.from_user.mention()} опубликовал пост, юзер получил уведомление.',
        reply_markup = get_first_button(cb.message),
    )
    link = (
        await forward(
            msg = cb.message.reply_to_message,
            target = config['main_chat'],
        )
    ).link.replace(
        'https://',
        ''
    )
    chat, msg = cb.data.split(' ', 1)[-1].split('/', 1)
    await bot.send_message(
        text = f'✅Твой пост опубликован - {link}',
        chat_id = int(chat),
        reply_to_message_id = int(msg),
    )


@bot.on_callback_query(
    callback_filter(
        'open_ban_menu'
    )
)
async def open_ban_menu(
    _,
    cb,
):
    await cb.answer()
    await cb.message.reply(
        text = f'Админ {cb.from_user.mention()} открыл меню для бана.',
        reply_markup = Buttons.ban_menu
    )


@bot.on_callback_query(
    callback_filter(
        'unban'
    )
)
async def unban(
    _,
    cb,
):
    if len(cb.message.reply_markup.inline_keyboard[0]) == 1:
        reply_markup = InlKb([[Buttons.open_ban_menu]])
    else:
        reply_markup = Buttons.publish(
            notify = f.get_notify(cb.message),
            ban_button = Buttons.open_ban_menu,
        )
    await cb.message.edit(
        text = f'{f.get_text(cb.message)}\n❤️Админ {cb.from_user.mention()} разбанил юзера, юзер получил уведомление.',
        reply_markup = reply_markup
    )
    user = f.get_user(cb.message)
    await bot.send_message(
        text = '❤️Хорошие новости, ты разбанен',
        chat_id = user,
    )
    now = datetime.now().replace(
        microsecond = 0,
    )
    for item in ban_list.copy():
        if item['user'] == user:
            ban_list.remove(item)
        elif item['time'] != 'forever':
            if datetime.fromisoformat(item['time']) <  now:
                ban_list.remove(item)
    await dump_ban_list(ban_list)


@bot.on_callback_query(
    callback_filter(
        'ban '  # do not remove whitespace after "ban"
    )
)
async def ban(
    _,
    cb,
):
    await cb.message.delete()
    ban_time = cb.data.split(' ', 1)[-1]
    time = None
    now = datetime.now().replace(
        microsecond = 0,
    )
    match ban_time:
        case 'forever':
            str_time = 'навсегда'
        case 'year':
            str_time = 'на год'
            time = now + relativedelta(
                years = 1
            )
        case 'month':
            str_time = 'на месяц'
            time = now + relativedelta(
                months = 1
            )
        case 'week':
            str_time = 'на неделю'
            time = now + relativedelta(
                weeks = 1
            )
        case '2_min':
            str_time = 'на 2 минуты'
            time = now + relativedelta(
                minutes = 2
            )
    if len(cb.message.reply_to_message.reply_markup.inline_keyboard[0]) == 1:
        reply_markup = InlKb([[Buttons.unban]])
    else:
        reply_markup = Buttons.publish(
            notify = f.get_notify(cb.message.reply_to_message),
            ban_button = Buttons.unban,
        )
    await cb.message.reply_to_message.edit(
        text = f'{f.get_text(cb.message.reply_to_message)}\n💀Админ {cb.from_user.mention()} выдал юзеру бан {str_time}, юзер получил уведомление.',
        reply_markup = reply_markup,
    )
    if time:
        time = time.isoformat(' ', 'minutes')
    else:
        time = 'forever'
    user = f.get_user(cb.message.reply_to_message)
    await bot.send_message(
        text = f'💀К сожалению, ты забанен {str_time}',
        chat_id = user,
    )
    for i in ban_list:
        if i['user'] == user:
            i['time'] = time
            await dump_ban_list(ban_list)
            return
    ban_list.append(
        {
            'user': user,
            'time': time,
        }
    )
    await dump_ban_list(ban_list)


@bot.on_callback_query(
    callback_filter(
        'close_ban_menu'
    )
)
async def close_ban_menu(
    _,
    cb,
):
    await cb.message.delete()


@bot.on_callback_query(
    callback_filter(
        'suggest'
    )
)
async def suggest(
    _,
    cb,
):
    msg = cb.message
    await msg.edit(
        'отправляю пост...'
    )
    time = await is_banned(cb.from_user.id)
    if time:
        if time == 'forever':
            text = '💀К сожалению, ты забанен навсегда'
        else:
            text = '💀К сожалению, ты сейчас забанен. Разбан через'
            days = time.days
            hours = time.seconds // 3600
            minutes = (time.seconds // 60) % 60
            seconds = time.seconds % 60
            if days:
                text += f' {days} дней'
            if hours:
                text += f' {hours} часов'
            if minutes:
                text += f' {minutes} минут'
            if seconds:
                text += f' {seconds} секунд'
        await msg.edit(
            text = text
        )
        return

    await msg.edit(
        text = '⌛Пост отправлен. Я пришлю тебе уведомление, когда его опубликуют, или отклонят'
    )
    notify = f'{cb.message.chat.id}/{cb.message.reply_to_message.message_id}'
    text = f'⌛️Юзер {cb.from_user.id}'
    if cb.from_user.username:
        text += f' @{cb.from_user.username}'
    await (
        await forward(
        msg = cb.message.reply_to_message,
        target = config['confirming_chat'],
        )
    ).reply(
        text = f'{text} отправил этот пост в предложку.',
        quote = True,
        reply_markup = Buttons.publish(
            notify = notify,
            ban_button = Buttons.open_ban_menu,
        )
)


def main():
    global chats_blacklist
    bot.start()
    console.log(bot.get_me())
    chats_blacklist = list(
        bot.get_chat(
            id
        ).id for id in (
            config['confirming_chat'],
            # config['main_chat']
        )
    )
    pyrogram.idle()
