from countdown.chatbot import bot, bot_event_loop

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from countdown.data import users

import asyncio

import logging
log = logging.getLogger(__name__)


async def update_messages_a(only_with_time: bool = False):
    async for user in users.get_users_async_iterable():
        if user.countdowns:
            log.info(f"Updating {len(user.countdowns)} countdowns for {user.user_id}")

        to_remove = []
        for countdown in user.countdowns:
            if only_with_time:
                if not countdown.settings.show_time:
                    continue

            try:
                await bot.edit_message_text(
                    inline_message_id=countdown.inline_message_id,
                    text=countdown.get_message_text(),
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [ InlineKeyboardButton(text="Edit", callback_data=f"edit:{countdown.inline_message_id}") ],
                    ])
                )

                log.info(f" - Updated message {countdown.inline_message_id}")

            except Exception as e:
                if "message is not modified" in str(e):
                    log.info(f" - Message {countdown.inline_message_id} is not modified")
                elif "MESSAGE_ID_INVALID" in str(e):
                    log.info(f" - Message {countdown.inline_message_id} is invalid, removing...")
                    to_remove.append(countdown)
                else:
                    log.exception(f"Error while updating message {countdown.inline_message_id}: {e}")

        for countdown in to_remove:
            user.countdowns.remove(countdown)

        await users.save_user(user)


def update_messages(only_with_time: bool = False):
    asyncio.run_coroutine_threadsafe(
        update_messages_a(only_with_time=only_with_time),
        bot_event_loop
    )
