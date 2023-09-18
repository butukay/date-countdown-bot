from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from countdown.chatbot import bot, bot_event_loop

from countdown.data import users

import asyncio

import logging

async def get_all_countdowns():
    all_countdowns = []

    async for user in users.get_users_async_iterable():
        for countdown in user.countdowns:
            all_countdowns.append(countdown)

    return all_countdowns

def update_messages(only_with_time: bool = False):
    all_countdowns = asyncio.run(get_all_countdowns())

    for countdown in all_countdowns:
        if only_with_time:
            if not countdown.settings.show_time:
                continue

        try:
            asyncio.run_coroutine_threadsafe(
                bot.edit_message_text(
                    inline_message_id=countdown.inline_message_id,
                    text=countdown.get_message_text(),
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [ InlineKeyboardButton(text="Edit", callback_data=f"edit:{countdown.inline_message_id}") ],
                    ])
                ), bot_event_loop
            )
        except Exception as e:
            logging.error(f"Error while updating message {countdown.inline_message_id}: {e}")
            continue

