from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from countdown.chatbot import bot, bot_event_loop

from countdown.data import users

import asyncio
import datetime

async def get_all_countdowns():
    all_countdowns = []

    async for user in users.get_users_async_iterable():
        for countdown in user.countdowns:
            all_countdowns.append(countdown)

    return all_countdowns

def update_messages():
    all_countdowns = asyncio.run(get_all_countdowns())

    for countdown in all_countdowns:
        try:
            asyncio.run_coroutine_threadsafe(
                bot.edit_message_text(
                    inline_message_id=countdown.inline_message_id,
                    text=f"""
    Until <b>{countdown.date.strftime("%d.%m.%Y")}</b> left: <b>{(countdown.date - datetime.datetime.now()).days + 1}</b> days

    {countdown.text}
    """,
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [ InlineKeyboardButton(text="Edit", callback_data=f"edit:{countdown.inline_message_id}") ],
                    ])
                ), bot_event_loop
            )
        except Exception as e:
            print(e)
            continue
