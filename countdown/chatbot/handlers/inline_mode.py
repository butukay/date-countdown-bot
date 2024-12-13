from aiogram import types

from aiogram.dispatcher.router import Router

from countdown.chatbot import bot
from countdown.data import users

import datetime

from countdown.data.countdown import DefaultCountdown, FormattedCountdown
from countdown.locale import Locale, __

router = Router()

@router.inline_query()
async def inline_query_handler(query: types.InlineQuery) -> None:
    assert query.from_user is not None

    _ = lambda locale_str: __(Locale(query.from_user.language_code), locale_str)

    query_str = query.query

    # if not query_str:
    #     await query.answer(
    #         results=[
    #             types.InlineQueryResultArticle(
    #                 id="empty",
    #                 title="Empty",
    #                 input_message_content=types.InputTextMessageContent(
    #                     message_text="Empty query",
    #                 ),
    #             ),
    #         ],
    #     )

    try:
        if query_str.count("%%") == 2:
            text_1, date_str, text_2 = query_str.split("%%")

            try:
                datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M")
            except ValueError:
                datetime.datetime.strptime(date_str, "%Y-%m-%d")

        elif query_str.count("[[") == query_str.count("]]") >= 1:
            values = query_str.replace("[[", "$*").replace("]]", "*$").split("$")

            for val in values:
                if val.startswith("*") and val.endswith("*"):
                    try:
                        datetime.datetime.strptime(val.strip("*"), "%Y-%m-%d %H:%M")
                    except ValueError:
                        datetime.datetime.strptime(val.strip("*"), "%Y-%m-%d")
                else:
                    pass
        else:
            raise ValueError

    except ValueError:
        await query.answer(
            results=[
                types.InlineQueryResultArticle(
                    id="invalid_format",
                    title=_("countdown.create.invalid_title"),
                    description=_("countdown.create.invalid_desc"),
                    input_message_content=types.InputTextMessageContent(
                        message_text=_("countdown.create.invalid_message"),
                    ),
                ),
            ],
        )

        return

    await query.answer(
        results=[
            types.InlineQueryResultArticle(
                id="new_coundown",
                title=_("countdown.create.valid_title"),
                description=_("countdown.create.valid_desc"),
                input_message_content=types.InputTextMessageContent(
                    message_text=_("countdown.create.valid_wait"),

                ),
                reply_markup=types.InlineKeyboardMarkup(
                    inline_keyboard=[
                        [ types.InlineKeyboardButton(text=_("countdown.create.valid_loading"), switch_inline_query=query_str) ],
                    ],
                )
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

    if "%%" in query_str:
        text_1, date_str, text_2 = query_str.split("%%")

        show_time = False

        try:
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M")
            show_time = True
        except ValueError:
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d")

        new_countdown = DefaultCountdown(
            inline_message_id=chosen_result.inline_message_id,
            text=(text_1.strip() + " " + text_2.strip()).strip(),
            date=date,
        )

        new_countdown.settings.show_time = show_time

    elif "[[" in query_str and "]]" in query_str:
        values = [ val for val in query_str.replace("[[", "$*").replace("]]", "*$").split("$") ]

        new_countdown = FormattedCountdown(
            inline_message_id=chosen_result.inline_message_id,
            values=values
        )

    else:
        raise NotImplementedError

    new_countdown.settings.locale = Locale(chosen_result.from_user.language_code)

    user.add_countdown(new_countdown)
    await users.save_user(user)

    await bot.edit_message_text(
        inline_message_id=chosen_result.inline_message_id,
        text=new_countdown.get_message_text(),
        reply_markup=new_countdown.get_message_markup()
    )
