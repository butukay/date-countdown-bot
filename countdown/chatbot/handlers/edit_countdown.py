from aiogram import types

from aiogram.dispatcher.router import Router

from countdown.chatbot import bot
from countdown.data import users

import datetime

router = Router()

@router.callback_query(lambda c: c.data.startswith("edit:"))
async def edit_countdown(callback_query: types.CallbackQuery):
    assert callback_query.data is not None

    inline_message_id = callback_query.data.replace("edit:", "")

    try:
        user, countdown = await users.get_countdown(inline_message_id)

    except ValueError:
        await bot.answer_callback_query(callback_query.id, "⚠️ Database error")
        return

    await bot.edit_message_text(
        inline_message_id=inline_message_id,
        text=countdown.get_settings_text(),
        reply_markup=countdown.get_settings_markup()
    )

@router.callback_query(lambda c: c.data.startswith("back:"))
async def back_to_countdown(callback_query: types.CallbackQuery):
    assert callback_query.data is not None

    inline_message_id = callback_query.data.replace("back:", "")

    try:
        user, countdown = await users.get_countdown(inline_message_id)
    except ValueError:
        await bot.answer_callback_query(callback_query.id, "⚠️ Database error")
        return

    await bot.edit_message_text(
        inline_message_id=inline_message_id,
        text=countdown.get_message_text(),
        reply_markup=countdown.get_message_markup()
    )


@router.callback_query(lambda c: c.data.startswith("delete:"))
async def delete_countdown(callback_query: types.CallbackQuery):
    assert callback_query.data is not None
    assert callback_query.message is not None

    inline_message_id = callback_query.data.replace("back:", "")

    try:
        user, countdown = await users.get_countdown(inline_message_id)
    except ValueError:
        await bot.answer_callback_query(callback_query.id, "⚠️ Database error")
        return

    await callback_query.message.delete()

    user.countdowns.remove(countdown)
    await users.save_user(user)


@router.callback_query(lambda c: c.data.startswith("s:"))
async def change_settings_callback_handler(callback_query: types.CallbackQuery):
    assert callback_query.data is not None

    _, inline_message_id, key = callback_query.data.split(":")

    try:
        user, countdown = await users.get_countdown(inline_message_id)
    except ValueError:
        await bot.answer_callback_query(callback_query.id, "⚠️ Database error")
        return


    match key:
        case "show_time":
            countdown.settings.show_time = not countdown.settings.show_time
        case _:
            raise NotImplementedError

    await bot.edit_message_text(
        inline_message_id=inline_message_id,
        text=countdown.get_settings_text(),
        reply_markup=countdown.get_settings_markup()
    )

    await users.save_countdown(countdown)
