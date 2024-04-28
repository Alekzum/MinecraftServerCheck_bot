from typing import Iterable, Literal
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, SwitchInlineQueryChosenChat


def make_button_url(text: str, url: str) -> InlineKeyboardMarkup:
    """Make a single button with text and callback data"""
    button = InlineKeyboardButton(text=text, url=url)
    result = InlineKeyboardMarkup(inline_keyboard=[[button]])
    return result

def make_button(text: str, callback: str) -> InlineKeyboardMarkup:
    """Make a single button with text and callback data"""
    button = InlineKeyboardButton(text=text, callback_data=callback)
    result = InlineKeyboardMarkup(inline_keyboard=[[button]])
    return result

def make_row(texts: Iterable[str], callbacks: Iterable[str]) -> InlineKeyboardMarkup:
    """Make a row with buttons"""
    buttons = [InlineKeyboardButton(text=texts[i], callback_data=callbacks[i]) for i in range(len(texts))]
    result = InlineKeyboardMarkup(inline_keyboard=[buttons])
    return result

def make_keyboard(texts: Iterable[Iterable[str]], callbacks: Iterable[Iterable[str]]) -> InlineKeyboardMarkup:
    """Make a whole keyboard"""
    keyboard = [[InlineKeyboardButton(text=texts[r][i], callback_data=callbacks[r][i]) for i in range(len(texts[r]))] for r in range(len(texts))]
    result = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return result

def make_row_things(texts: list[str], acts: list[dict[Literal['url', 'callback', 'switch_inline_query', 'switch_inline_query_chosen_chat', 'switch_inline_query_current_chat'], str]]):
    result = []
    for it, text in enumerate(texts):
        act_name, act_value = tuple(acts[it].items())[0]
        
        match act_name:
            case 'url': button = InlineKeyboardButton(text=text, url=act_value)
            case 'callback': button = InlineKeyboardButton(text=text, callback_data=act_value)
            case 'switch_inline_query': button = InlineKeyboardButton(text=text, switch_inline_query=act_value)
            case 'switch_inline_query_chosen_chat': button = InlineKeyboardButton(text=text, switch_inline_query_chosen_chat=SwitchInlineQueryChosenChat(query=act_value))
            case 'switch_inline_query_current_chat': button = InlineKeyboardButton(text=text, switch_inline_query_current_chat=act_value)
        result.append(button)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[result])
    return keyboard
if __name__ == "__main__":
    print(make_button("hello", "1"))
    print(make_row(("1", "2"), ("1", "2")))
    print(make_keyboard((("1", "2"), ("3", "4")), (("1", "2"), ("3", "4"))))