from aiogram import types

from aiogram.dispatcher.router import Router

from countdown.chatbot import bot
from countdown.data import users

import datetime

from countdown.data.countdown import Countdown

router = Router()

@router.inline_query()
async def inline_query_handler(query: types.InlineQuery) -> None:
    query_str = query.query

    if query_str.count("%%") == 2:
        try:
            text_1, date_str, text_2 = query_str.split("%%")
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        except Exception as e:
            await query.answer(
                results=[
                    types.InlineQueryResultArticle(
                        id="invalid_format",
                        title="Error",
                        description=f"⚠️ Invalid date format",
                        input_message_content=types.InputTextMessageContent(
                            message_text="❌ <b>Error:</b> Invalid date format",
                        ),
                    ),
                ],
            )

            return


        await query.answer(
            results=[
                types.InlineQueryResultArticle(
                    id="date",
                    title="Countdown",
                    description=f"✅ Valid date format",
                    input_message_content=types.InputTextMessageContent(
                        message_text=f"⏳ Wait a second",

                    ),
                    reply_markup=types.InlineKeyboardMarkup(
                        inline_keyboard=[
                            [ types.InlineKeyboardButton(text="Loading...", switch_inline_query=f"{text_1}%%{date_str}%%{text_2}") ],
                        ],
                    )
                ),
            ],
        )

    else:
        await query.answer(
            results=[
                types.InlineQueryResultArticle(
                    id="empty",
                    title="Empty",
                    input_message_content=types.InputTextMessageContent(
                        message_text="Empty query",
                    ),
                ),
            ],
        )


@router.chosen_inline_result()
async def chosen_inline_result_handler(chosen_result: types.ChosenInlineResult) -> None:
    assert chosen_result.from_user is not None
    assert chosen_result.inline_message_id is not None

    try:
        user = await users.get_user(chosen_result.from_user.id)
    except ValueError:
        user = await users.register_user(chosen_result.from_user.id, chosen_result.from_user.username)

    query_str = chosen_result.query

    text_1, date_str, text_2 = query_str.split("%%")
    date = datetime.datetime.strptime(date_str, "%Y-%m-%d")

    new_countdown = Countdown(
        inline_message_id=chosen_result.inline_message_id,
        text=text_1.strip()+text_2.strip(),
        date=date
    )

    user.add_countdown(new_countdown)
    await users.save_user(user)

    await bot.edit_message_text(
        inline_message_id=chosen_result.inline_message_id,
        text=new_countdown.get_message_text(),
        reply_markup=new_countdown.get_message_markup()
    )
