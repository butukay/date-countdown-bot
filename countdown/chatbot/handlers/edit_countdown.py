from aiogram import types

from aiogram.dispatcher.router import Router

from countdown.chatbot import bot
from countdown.data import users

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


@router.callback_query(lambda c: c.data.startswith("s:"))
async def change_settings_callback_handler(callback_query: types.CallbackQuery):
    assert callback_query.data is not None

    _, inline_message_id, key, action = callback_query.data.split(":")

    try:
        user, countdown = await users.get_countdown(inline_message_id)
    except ValueError:
        await bot.answer_callback_query(callback_query.id, "⚠️ Database error")
        return

    match key:
        case "show_time":
            countdown.settings.show_time = not countdown.settings.show_time
        case "timezone":
            match action:
                case "+":
                    if countdown.settings.utc_offset < 12:
                        countdown.settings.utc_offset += 1
                    else:
                        countdown.settings.utc_offset = -12
                case "-":
                    if countdown.settings.utc_offset > -12:
                        countdown.settings.utc_offset -= 1
                    else:
                        countdown.settings.utc_offset = 12
                case _:
                    raise NotImplementedError
        case _:
            raise NotImplementedError

    await bot.edit_message_text(
        inline_message_id=inline_message_id,
        text=countdown.get_settings_text(),
        reply_markup=countdown.get_settings_markup()
    )

    await users.save_countdown(countdown)

