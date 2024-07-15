from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

main = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text='Посмотреть свои объявления', resize_keyboard=True)],
    [KeyboardButton(text='Добавить объявление', resize_keyboard=True)],
    [KeyboardButton(text='Поиск объявлений', resize_keyboard=True)],
    [KeyboardButton(text='Оценить бота', resize_keyboard=True)]
])


async def get_ads_keyboard(all_ads):
    keyboard = InlineKeyboardBuilder()
    for ad in all_ads:
        keyboard.add(InlineKeyboardButton(text=ad.name, callback_data=f"ad_{ad.id}"))
    return keyboard.adjust(2).as_markup()


async def cancel():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Отменить заполнение объявления", callback_data="quit"))
    return keyboard.adjust(2).as_markup()


async def cancel_edit():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Отменить изменение объявления", callback_data="cancel_edit"))
    return keyboard.adjust(2).as_markup()


async def edit_ad(ad):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Изменить объявление", callback_data=f"edit_ad{ad}"))
    keyboard.add(InlineKeyboardButton(text="Удалить объявление", callback_data=f"delete_ad{ad}"))
    return keyboard.adjust(2).as_markup()


async def edit_ad_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Изменить название", callback_data="update_ad_name"))
    keyboard.add(InlineKeyboardButton(text="Изменить описание", callback_data="update_ad_description"))
    keyboard.add(InlineKeyboardButton(text="Изменить цену", callback_data="update_ad_price"))
    keyboard.add(InlineKeyboardButton(text="Изменить локацию", callback_data="update_ad_location"))
    keyboard.add(InlineKeyboardButton(text="Изменить контакт", callback_data="update_ad_contact"))
    keyboard.add(InlineKeyboardButton(text="Отменить изменение объявления", callback_data="cancel_edit"))
    return keyboard.adjust(2).as_markup()


async def return_to_edit(ad):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Вернуться к выбору изменения", callback_data=f"edit_ad{ad}"))
    return keyboard.adjust(2).as_markup()


# Клавиатура для поиска по фильтрам
async def filter_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Поиск по ключевому слову", callback_data="search_by_keyword"))
    keyboard.add(InlineKeyboardButton(text="Поиск по цене", callback_data="search_by_price"))
    keyboard.add(InlineKeyboardButton(text="Поиск по локации", callback_data="search_by_location"))
    return keyboard.adjust(3).as_markup()


async def cancel_search():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Отменить поиск", callback_data="cancel_search"))
    return keyboard.adjust(2).as_markup()


async def start_search():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Отменить поиск", callback_data="cancel_search"))
    keyboard.add(InlineKeyboardButton(text="Начать поиск", callback_data="start_search"))
    keyboard.add(InlineKeyboardButton(text="Добавить фильтр", callback_data="add_filter"))
    return keyboard.adjust(2).as_markup()


async def start_moderation():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Начать модерацию объявлений", callback_data=f"start_moderation"))
    keyboard.add(InlineKeyboardButton(text="Отменить модерацию объявлений", callback_data=f"cancel_moderate_ad"))
    return keyboard.adjust(2).as_markup()


# moderate_keyboard
async def moderate_keyboard(ad):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Принять объявление", callback_data=f"accept_ad{ad.id}"))
    keyboard.add(InlineKeyboardButton(text="Отклонить объявление", callback_data=f"decline_ad{ad.id}"))
    keyboard.add(InlineKeyboardButton(text="Отменить модерацию объявлений", callback_data=f"cancel_moderate_ad"))
    return keyboard.adjust(2).as_markup()


async def rating_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="1", callback_data="1"))
    keyboard.add(InlineKeyboardButton(text="2", callback_data="2"))
    keyboard.add(InlineKeyboardButton(text="3", callback_data="3"))
    keyboard.add(InlineKeyboardButton(text="4", callback_data="4"))
    keyboard.add(InlineKeyboardButton(text="5", callback_data="5"))
    return keyboard.adjust(5).as_markup()
