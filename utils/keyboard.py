from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, SwitchInlineQueryChosenChat
from typing import Sequence, Literal


INPUT_FIELDS = dict[Literal['url', 'callback', 'switch_inline_query', 'switch_inline_query_chosen_chat', 'switch_inline_query_current_chat'], str]


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

def make_row(texts: Sequence[str], callbacks: Sequence[str]) -> InlineKeyboardMarkup:
    """Make a row with buttons"""
    buttons = [InlineKeyboardButton(text=texts[i], callback_data=callbacks[i]) for i in range(len(texts))]
    result = InlineKeyboardMarkup(inline_keyboard=[buttons])
    return result

def make_keyboard(texts: Sequence[Sequence[str]], acts: Sequence[Sequence[INPUT_FIELDS]]) -> InlineKeyboardMarkup:
    """Make a whole keyboard"""
    result = []
    for index_row, row_texts in enumerate(texts):
        temp = []
        for index_column, text in enumerate(row_texts):
            act_name, act_value = tuple(acts[index_row][index_column].items())[0]
        
            match act_name:
                case 'url': button = InlineKeyboardButton(text=text, url=act_value)
                case 'callback': button = InlineKeyboardButton(text=text, callback_data=act_value)
                case 'switch_inline_query': button = InlineKeyboardButton(text=text, switch_inline_query=act_value)
                case 'switch_inline_query_chosen_chat': button = InlineKeyboardButton(text=text, switch_inline_query_chosen_chat=SwitchInlineQueryChosenChat(query=act_value))
                case 'switch_inline_query_current_chat': button = InlineKeyboardButton(text=text, switch_inline_query_current_chat=act_value)
            temp.append(button)
        result.append(temp)
    keyboard = InlineKeyboardMarkup(inline_keyboard=result)
    return keyboard

def make_row_things(texts: list[str], acts: Sequence[INPUT_FIELDS]):
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

EMPTY_BUTTON = make_button("Тут ничего нет", "ты думал тут что-то будет???")
