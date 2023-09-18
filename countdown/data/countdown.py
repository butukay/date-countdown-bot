import pydantic
import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class CountdownSettings(pydantic.BaseModel):
    show_time: bool = False

class Countdown(pydantic.BaseModel):
    inline_message_id: str

    date: datetime.datetime
    text: str

    settings: CountdownSettings = pydantic.Field(default_factory=CountdownSettings)

    def get_message_text(self):
        text = ""

        d = self.date - datetime.datetime.now()
        if not self.settings.show_time:
            text += f"Until <b>{self.date.strftime('%d.%m.%Y')}</b> left: <b>{d.days + 1}</b> days"
        else:
            text += f"Until <b>{self.date.strftime('%d.%m.%Y %H:%M')}</b> left: <b>{d.days}</b> days, <b>{d.seconds // 3600}</b> hours, <b>{(d.seconds // 60) % 60}</b> minutes"

        text += "\n\n" + self.text.strip()

        return text

    def get_message_markup(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
            [ InlineKeyboardButton(text="Edit", callback_data=f"edit:{self.inline_message_id}") ],
        ])

    def get_settings_text(self) -> str:
        return "⚙️<b>Settings</b>\n\n" + self.get_message_text()

    def get_settings_markup(self) -> InlineKeyboardMarkup:
        onoff = lambda v: "✅" if v else "❌"

        return InlineKeyboardMarkup(inline_keyboard=[
            [ InlineKeyboardButton(text=f"Show time: {onoff(self.settings.show_time)}", callback_data=f"s:{self.inline_message_id}:show_time") ],
            [ InlineKeyboardButton(text="< Back", callback_data=f"back:{self.inline_message_id}") ],
        ])


