from abc import abstractmethod
from typing import Literal

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import pydantic
import datetime

from countdown.locale import Locale, __

class CountdownSettings(pydantic.BaseModel):
    show_time: bool = False

    utc_offset: int = pydantic.Field(lt=13, gt=-13, default=0)
    locale: Locale = Locale.ENGLISH

    @property
    def timezone(self):
        return datetime.timezone(datetime.timedelta(hours=self.utc_offset))

class Countdown(pydantic.BaseModel):
    inline_message_id: str

    settings: CountdownSettings = pydantic.Field(default_factory=CountdownSettings)

    @abstractmethod
    def get_message_text(self) -> str:
        return NotImplemented

    def get_message_markup(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
            [ InlineKeyboardButton(text=__(self.settings.locale, 'countdown.settings_button'), callback_data=f"edit:{self.inline_message_id}") ],
        ])

    def get_settings_text(self) -> str:
        return f"⚙️<b>{__(self.settings.locale, 'countdown.settings_title')}</b>\n\n{self.get_message_text()}"

    def get_settings_markup(self) -> InlineKeyboardMarkup:
        onoff = lambda v: "✅" if v else "❌"

        _ = lambda locale_str: __(self.settings.locale, locale_str)

        return InlineKeyboardMarkup(inline_keyboard=[
            [ InlineKeyboardButton(text=f"{_('countdown.settings.show_time')}: {onoff(self.settings.show_time)}", callback_data=f"s:{self.inline_message_id}:show_time:*") ],
            [
                InlineKeyboardButton(text="<", callback_data=f"s:{self.inline_message_id}:locale:-"),
                InlineKeyboardButton(text=f"{_('countdown.settings.locale')}: {self.settings.locale.get_name_flag()}", callback_data="null"),
                InlineKeyboardButton(text=">", callback_data=f"s:{self.inline_message_id}:locale:+")
            ],
            [
                InlineKeyboardButton(text="<", callback_data=f"s:{self.inline_message_id}:timezone:-"),
                InlineKeyboardButton(text=str(self.settings.timezone), callback_data="null"),
                InlineKeyboardButton(text=">", callback_data=f"s:{self.inline_message_id}:timezone:+")
            ],
            [ InlineKeyboardButton(text=_('countdown.settings.back'), callback_data=f"back:{self.inline_message_id}") ],
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

        match self.settings.locale:
            case Locale.ENGLISH:
                if self.settings.show_time:
                    text += f"Until <b>{self.date.strftime('%d.%m.%Y %H:%M')}</b> left: <b>{d.days}</b> days, <b>{d.seconds // 3600}</b> hours, <b>{(d.seconds // 60) % 60}</b> minutes"
                else:
                    text += f"Until <b>{self.date.strftime('%d.%m.%Y')}</b> left: <b>{d.days + 1}</b> days"

            case Locale.RUSSIAN:
                if self.settings.show_time:
                    minutes = ((d.seconds // 60) % 60)
                    hours = d.seconds // 3600
                    days = d.days

                    if days % 100 in [11, 12, 13, 14, 15, 16, 17, 18, 19] or days % 10 in [0, 5, 6, 7, 8, 9]:
                        d_str = f"осталось <b>{days}</b> дней"
                    elif days % 10 == 1:
                        d_str = f"остался <b>{days}</b> день"
                    else:
                        d_str = f"осталось <b>{days}</b> дня"

                    if hours % 100 in [11, 12, 13, 14, 15, 16, 17, 18, 19] or hours % 10 in [0, 5, 6, 7, 8, 9]:
                        h_str = f"<b>{hours}</b> часов"
                    elif hours % 10 == 1:
                        h_str = f"<b>{hours}</b> час"
                    else:
                        h_str = f"<b>{hours}</b> часа"

                    if minutes % 100 in [11, 12, 13, 14, 15, 16, 17, 18, 19] or minutes % 10 in [0, 5, 6, 7, 8, 9]:
                        m_str = f"<b>{minutes}</b> минут"
                    elif minutes % 10 == 1:
                        m_str = f"<b>{minutes}</b> минутa"
                    else:
                        m_str = f"<b>{minutes}</b> минуты"

                    text += f"До <b>{self.date.strftime('%d.%m.%Y %H:%M')}</b> {' '.join([d_str, h_str, m_str])}"

                else:
                    days = d.days + 1

                    if days % 100 in [11, 12, 13, 14, 15, 16, 17, 18, 19] or days % 10 in [0, 5, 6, 7, 8, 9]:
                        text += f"До <b>{self.date.strftime('%d.%m.%Y')}</b> осталось <b>{days}</b> дней"
                    elif days % 10 == 1:
                        text += f"До <b>{self.date.strftime('%d.%m.%Y')}</b> остался <b>{days}</b> день"
                    else:
                        text += f"До <b>{self.date.strftime('%d.%m.%Y')}</b> осталось <b>{days}</b> дня"

        text += "\n\n" + self.text.strip()

        return text.strip()


class FormattedCountdown(Countdown):
    mode: Literal["formatted"] = "formatted"

    values: list[str]

    def get_message_text(self) -> str:
        msg = ""

        for val in self.values:
            if val.startswith("*") and val.endswith("*"):
                dt_show_time = False
                try:
                    dt = datetime.datetime.strptime(val.strip("*"), "%Y-%m-%d %H:%M")
                    dt_show_time = True
                except ValueError:
                    dt = datetime.datetime.strptime(val.strip("*"), "%Y-%m-%d")

                d = dt.replace(tzinfo=self.settings.timezone) - datetime.datetime.now(datetime.timezone.utc)

                match self.settings.locale:
                    case Locale.ENGLISH:
                        if self.settings.show_time and dt_show_time:
                            msg += f"<b>{d.days} days {d.seconds // 3600} hours {(d.seconds // 60) % 60} minutes</b>"
                        else:
                            msg += f"<b>{d.days + 1} days</b>"

                    case Locale.RUSSIAN:
                        if self.settings.show_time and dt_show_time:
                            minutes = ((d.seconds // 60) % 60)
                            hours = d.seconds // 3600
                            days = d.days

                            if days % 100 in [11, 12, 13, 14, 15, 16, 17, 18, 19] or days % 10 in [0, 5, 6, 7, 8, 9]:
                                d_str = f"{days} дней"
                            elif days % 10 == 1:
                                d_str = f"{days} день"
                            else:
                                d_str = f"{days} дня"

                            if hours % 100 in [11, 12, 13, 14, 15, 16, 17, 18, 19] or hours % 10 in [0, 5, 6, 7, 8, 9]:
                                h_str = f"{hours} часов"
                            elif hours % 10 == 1:
                                h_str = f"{hours} час"
                            else:
                                h_str = f"{hours} часа"

                            if minutes % 100 in [11, 12, 13, 14, 15, 16, 17, 18, 19] or minutes % 10 in [0, 5, 6, 7, 8, 9]:
                                m_str = f"{minutes} минут"
                            elif minutes % 10 == 1:
                                m_str = f"{minutes} минутa"
                            else:
                                m_str = f"{minutes} минуты"

                            msg += f"<b>{' '.join([d_str, h_str, m_str])}</b>"

                        else:
                            days = d.days + 1

                            if days % 100 in [11, 12, 13, 14, 15, 16, 17, 18, 19] or days % 10 in [0, 5, 6, 7, 8, 9]:
                                msg += f"<b>{days} дней</b>"
                            elif days % 10 == 1:
                                msg += f"<b>{days} день</b>"
                            else:
                                msg += f"<b>{days} дня</b>"

            else:
                msg += val

        return msg.strip()
