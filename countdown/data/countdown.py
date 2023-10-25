from typing import Literal

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import pydantic
import datetime

class CountdownSettings(pydantic.BaseModel):
    show_time: bool = False
    utc_offset: int = pydantic.Field(lt=13, gt=-13, default=0)

    @property
    def timezone(self):
        return datetime.timezone(datetime.timedelta(hours=self.utc_offset))

class Countdown(pydantic.BaseModel):
    inline_message_id: str

    settings: CountdownSettings = pydantic.Field(default_factory=CountdownSettings)

    def get_message_text(self):
        return NotImplemented

    def get_message_markup(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
            [ InlineKeyboardButton(text="Edit", callback_data=f"edit:{self.inline_message_id}") ],
        ])

    def get_settings_text(self) -> str:
        return "⚙️<b>Settings</b>\n\n" + self.get_message_text()

    def get_settings_markup(self) -> InlineKeyboardMarkup:
        onoff = lambda v: "✅" if v else "❌"

        return InlineKeyboardMarkup(inline_keyboard=[
            [ InlineKeyboardButton(text=f"Show time: {onoff(self.settings.show_time)}", callback_data=f"s:{self.inline_message_id}:show_time:*") ],
            [
                InlineKeyboardButton(text="<", callback_data=f"s:{self.inline_message_id}:timezone:-"),
                InlineKeyboardButton(text=str(self.settings.timezone), callback_data="null"),
                InlineKeyboardButton(text=">", callback_data=f"s:{self.inline_message_id}:timezone:+")
            ],
            [ InlineKeyboardButton(text="< Back", callback_data=f"back:{self.inline_message_id}") ],
        ])


### MODE:
# default: Until 03.02.2023 is left
# formatted: some text 03.02.2023 some text 01.33.2007 some text

class DefaultCountdown(Countdown):
    mode: Literal["default"] = "default"

    date: datetime.datetime
    text: str

    def get_message_text(self) -> str:
        text = ""

        d = self.date.replace(tzinfo=self.settings.timezone) - datetime.datetime.now(datetime.timezone.utc)
        if not self.settings.show_time:
            text += f"Until <b>{self.date.strftime('%d.%m.%Y')}</b> left: <b>{d.days + 1}</b> days"
        else:
            text += f"Until <b>{self.date.strftime('%d.%m.%Y %H:%M')}</b> left: <b>{d.days}</b> days, <b>{d.seconds // 3600}</b> hours, <b>{(d.seconds // 60) % 60}</b> minutes"

        text += "\n\n" + self.text.strip()

        return text.strip()


class FormattedCountdown(Countdown):
    mode: Literal["formatted"] = "formatted"

    values: list[str]

    def get_message_text(self) -> str:
        msg = ""

        for val in self.values:
            if val.startswith("*") and val.endswith("*"):
                try:
                    dt = datetime.datetime.strptime(val.strip("*"), "%Y-%m-%d %H:%M")
                except ValueError:
                    dt = datetime.datetime.strptime(val.strip("*"), "%Y-%m-%d")

                d = dt.replace(tzinfo=self.settings.timezone) - datetime.datetime.now(datetime.timezone.utc)

                if not self.settings.show_time:
                    msg += f"<b>{d.days + 1} days</b>"
                else:
                    msg += f"<b>{d.days} days, {d.seconds // 3600} hours, {(d.seconds // 60) % 60} minutes</b>"

            else:
                msg += val


        return msg.strip()
