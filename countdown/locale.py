from functools import lru_cache

from enum import Enum

class Locale(str, Enum):
    ENGLISH = "en"
    RUSSIAN = "ru"

    @classmethod
    def _missing_(cls, value):
        return cls.ENGLISH

    def get_flag(self) -> str:
        return {
            Locale.ENGLISH: "🇬🇧",
            Locale.RUSSIAN: "🇷🇺"
        }[self]

    def get_name(self) -> str:
        return {
            Locale.ENGLISH: "English",
            Locale.RUSSIAN: "Русский"
        }[self]

    def get_name_flag(self) -> str:
        return f"{self.get_flag()} {self.get_name()}"

@lru_cache(None)
def parse_locale_file(locale: Locale) -> dict:
    with open(f"locale/{locale.value}.lang", 'r', encoding='utf-8') as file:
        lines = file.readlines()

    result = {}

    key = None
    value = ""
    is_multiline = False

    for line in lines:
        line = line.strip()

        if is_multiline:
            if line.endswith('"""'):
                value += '\n' + line[:-3]
                result[key] = value.strip()

                key = None
                value = ""
                is_multiline = False
            else:
                value += '\n' + line

            continue

        if not line or line.startswith('#'):
            continue

        if '=' in line:
            key, val = line.split('=', 1)
            key = key.strip()
            val = val.strip()

            if val.startswith('"""'):
                is_multiline = True
                value = val[3:]
                if value.endswith('"""'):
                    result[key] = value[:-3].strip()

                    key = None
                    value = ""
                    is_multiline = False
            else:
                result[key] = val

    return result

def __(locale: Locale, locale_str: str) -> str:
    return parse_locale_file(locale).get(locale_str, locale_str)

def _(locale_str: str) -> str:
    return __(Locale.ENGLISH, locale_str)

def get_next_locale(locale: Locale) -> Locale:
    return {
        Locale.ENGLISH: Locale.RUSSIAN,
        Locale.RUSSIAN: Locale.ENGLISH
    }[locale]

def get_prev_locale(locale: Locale) -> Locale:
    return {
        Locale.ENGLISH: Locale.RUSSIAN,
        Locale.RUSSIAN: Locale.ENGLISH
    }[locale]

__all__ = [
    "Locale",
    "__",
    "_",

    "get_next_locale",
    "get_prev_locale"
]
