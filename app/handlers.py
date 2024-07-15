from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import StatesGroup, State
from database.requests import set_user, add_ad, get_ads, get_ad_info, delete_ad, update_ad, search_ads, \
    add_search_history, get_all_ads_without_moderation, accept_moderation, rate_bot_for_user
from keyboards import get_ads_keyboard, main, cancel, edit_ad, edit_ad_keyboard, cancel_edit, \
    return_to_edit, filter_keyboard, cancel_search, start_search, moderate_keyboard, start_moderation, rating_keyboard
from config import ADMIN
router = Router()




# Определяем состояние для машины состояний
class AdState(StatesGroup):
    name = State()
    description = State()
    price = State()
    location = State()
    contact = State()


class EditAdState(StatesGroup):
    id = State()
    name_column = State()


class SearchAdState(StatesGroup):
    filter = State()
    keyword = State()
    location = State()
    price = State()


class ModerateAdState(StatesGroup):
    action = State()


class RateAdState(StatesGroup):
    action = State()


# Обработчик команды /start
@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await set_user(message.from_user.id)
    await message.reply(
        "Привет! Я бот для размещения объявлений об аренде товаров. Чтобы разместить объявление, введите команду нажмите на кнопку ниже:Добавить объявление",
        reply_markup=main)


# Обработчик команды Добавить объявление
@router.message(F.text == 'Добавить объявление')
async def cmd_new_ad(message: types.Message, state: FSMContext):
    await state.set_state(AdState.name)
    await message.answer("Введите название товара:", reply_markup=await cancel())


# Обработчик ввода названия товара
@router.message(AdState.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AdState.description)
    await message.answer("Введите описание товара:", reply_markup=await cancel())


# Обработчик ввода описание товара
@router.message(AdState.description)
async def process_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AdState.price)
    await message.answer("Введите стоимость аренды:", reply_markup=await cancel())


# Обработчик ввода стоимости аренды
@router.message(AdState.price)
async def process_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(AdState.location)
    await message.answer("Введите местонахождение товара:", reply_markup=await cancel())


# Обработчик ввода местонахождения товара
@router.message(AdState.location)
async def process_location(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    await state.set_state(AdState.contact)
    await message.answer("Введите контактную информацию владельца:", reply_markup=await cancel())


# Обработчик ввода контактной информации владельца
@router.message(AdState.contact)
async def process_contact(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    data = await state.get_data()
    user_id = message.from_user.id
    await add_ad(user_id, data['name'], data['description'], data['price'], data['location'], data['contact'])
    await message.answer(
        f"Ваше объявление отправлено на модерацию:\nНазвание:{data['name']}\nОписание:{data['description']}\nСтоимость:{data['price']}\nМестонахождение:{data['location']}\nКонтактная информация:{data['contact']}\n")
    await state.clear()


# Показать все объявления пользователя
@router.message(F.text == 'Посмотреть свои объявления')
async def show_ads(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    ads = await get_ads(user_id)
    ads = ads.all()
    if not ads:
        await message.delete()
        await message.answer("У вас нет размещенных объявлений, прошедших модерацию.")
    else:
        await message.answer("Ваши объявления:", reply_markup=await get_ads_keyboard(ads))


# Подробная информация о объявлении пользователя
@router.callback_query(F.data.startswith('ad_'))
async def show_ad(call: types.CallbackQuery, state: FSMContext):
    data = await get_ad_info(call.from_user.id, call.data.split('_')[1])
    if not data:
        await call.answer("У вас нет такого объявления")
    else:
        await call.answer('')
        await call.message.edit_text(
            f'Название:{data.name}\nОписание:{data.description}\nСтоимость:{data.price}\nМестонахождение:{data.location}\nКонтактная информация:{data.contact}\n',
            reply_markup=await edit_ad(call.data.split('_')[1]))


# Удаление обявления пользователя
@router.callback_query(F.data.startswith('delete_ad'))
async def delete_ad_user(call: types.CallbackQuery, state: FSMContext):
    await delete_ad(call.from_user.id, call.data.split('_ad')[1])
    await call.answer('Объявление удалено')
    await call.message.edit_text("Ваши объявления:",
                                 reply_markup=await get_ads_keyboard(
                                     await get_ads(call.from_user.id)))  # TODO: может и не нужно


# Выбор изменения обявления пользователя
@router.callback_query(F.data.startswith('edit_ad'))
async def edit_ad_user(call: types.CallbackQuery, state: FSMContext):
    data = await get_ad_info(call.from_user.id, call.data.split('_ad')[1])
    await state.update_data(id=call.data.split('_ad')[1])
    await state.set_state(EditAdState.id)
    await call.message.edit_text(
        f'Название:{data.name}\nОписание:{data.description}\nСтоимость:{data.price}\nМестонахождение:{data.location}\nКонтактная информация:{data.contact}\n\n\nВыберите, что нужно изменить',
        reply_markup=await edit_ad_keyboard())
    # await call.message.answer("Что хотите изменить?", reply_markup=await edit_ad_keyboard())
    await call.answer('')


# Обработчик ввода изменных данных об объявлении
@router.callback_query(EditAdState.id, F.data.startswith("update_ad"))
async def process_update_ad_user(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(name_column=call.data.split('_ad_')[1])
    await state.set_state(EditAdState.name_column)
    await call.message.edit_text("Отправьте измененные данные", reply_markup=await cancel_edit())


# Изменение обявления пользователя
@router.message(EditAdState.name_column)
async def updating(message: types.Message, state: FSMContext):
    data = await state.get_data()
    result = await update_ad(message.from_user.id, data['id'], data['name_column'], message.text)
    if result:
        await message.answer("Объявление изменено", reply_markup=await return_to_edit(data['id']))
    else:
        await message.answer("Объявление не изменено")
    await state.set_state(EditAdState.id)


# Поиск объявлений
@router.message(F.text == 'Поиск объявлений')
async def cmd_search(message: types.Message, state: FSMContext):
    await message.answer("Выберите фильтр для поиска", reply_markup=await filter_keyboard())
    await state.set_state(SearchAdState.filter)


@router.callback_query(F.data.startswith('search_by'))
async def choose_filter(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(filter=None, keyword=None, location=None, price=None)
    await state.update_data(filter=call.data.split('_by_')[1])
    await call.answer('')
    if call.data.split('_by_')[1] == 'keyword':
        await call.message.edit_text("Введите ключевое слово для поиска:", reply_markup=await cancel_search())
        await state.set_state(SearchAdState.keyword)
    elif call.data.split('_by_')[1] == 'price':
        await call.message.edit_text("Введите цену товара:", reply_markup=await cancel_search())
        await state.set_state(SearchAdState.price)
    elif call.data.split('_by_')[1] == 'location':
        await call.message.edit_text("Введите местоположение товара:", reply_markup=await cancel_search())
        await state.set_state(SearchAdState.location)


@router.message(SearchAdState.keyword)
async def process_search_keyword(message: types.Message, state: FSMContext):
    await state.update_data(keyword=message.text)
    await message.answer("Филтр успешно применен", reply_markup=await start_search())


@router.message(SearchAdState.price)
async def process_search_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer("Филтр успешно применен", reply_markup=await start_search())


@router.message(SearchAdState.location)
async def process_search_location(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    await message.answer("Филтр успешно применен", reply_markup=await start_search())


@router.callback_query(F.data == 'start_search')
async def process_search_ads(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await add_search_history(call.from_user.id, data['keyword'])
    ads = await search_ads(data['keyword'], data['price'], data['location'])
    ads = ads.all()
    if not ads:
        await call.message.edit_text("Объявления не найдены.")
    else:
        await call.message.edit_text("Найденные объявления:")
        for ad in ads:
            await call.message.answer(
                f"Название:{ad.name}\nОписание:{ad.description}\nСтоимость:{ad.price}\nМестонахождение:{ad.location}\nКонтактная информация:{ad.contact}\n", )
    await state.clear()


@router.callback_query(F.data == 'add_filter')
async def add_filter(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Выберите фильтр для поиска", reply_markup=await filter_keyboard())
    await state.set_state(SearchAdState.filter)


# Модерация обявлений
@router.message(Command('moderate'), F.from_user.id == ADMIN)
async def moderate_ads(message: types.Message, state: FSMContext):
    await state.set_state(ModerateAdState.action)
    ads = await get_all_ads_without_moderation()
    ads = ads.all()
    await message.answer(f'{len(ads)} объявлений ждут модерации', reply_markup=await start_moderation())


@router.callback_query(ModerateAdState.action, F.data.startswith('start_moderation'))
async def process_moderate_ads(call: types.CallbackQuery, state: FSMContext):
    await call.answer('')
    ads = await get_all_ads_without_moderation()
    ads = ads.all()
    if not ads:
        await call.message.answer("Объявления к модерации не найдены")
        await state.clear()
    else:
        ad = ads[0]
        await call.message.edit_text(
            f"Название:{ad.name}\nОписание:{ad.description}\nСтоимость:{ad.price}\nМестонахождение:{ad.location}\nКонтактная информация:{ad.contact}\n",
            reply_markup=await moderate_keyboard(ad))


# Принять объявление на модерации
@router.callback_query(ModerateAdState.action, F.data.startswith('accept_ad'))
async def accept_ad(call: types.CallbackQuery, state: FSMContext):
    await call.answer('Объявление принято')
    ad_id = call.data.split('_ad')[1]
    await accept_moderation(ad_id, True)
    ads = await get_all_ads_without_moderation()
    ads = ads.all()
    if not ads:
        await call.message.edit_text("Объявления к модерации не найдены")
        await state.clear()
    else:
        ad = ads[0]
        await call.message.edit_text(
            f"Название:{ad.name}\nОписание:{ad.description}\nСтоимость:{ad.price}\nМестонахождение:{ad.location}\nКонтактная информация:{ad.contact}\n",
            reply_markup=await moderate_keyboard(ad))


# Отклонить объявление на модерации
@router.callback_query(ModerateAdState.action, F.data.startswith('decline_ad'))
async def decline_ad(call: types.CallbackQuery, state: FSMContext):
    await call.answer('Объявление отклонено')
    ad_id = call.data.split('_ad')[1]
    await accept_moderation(ad_id, False)
    ads = await get_all_ads_without_moderation()
    ads = ads.all()
    if not ads:
        await call.message.edit_text("Объявления к модерации не найдены")
        await state.clear()
    else:
        ad = ads[0]
        await call.message.edit_text(
            f"Название:{ad.name}\nОписание:{ad.description}\nСтоимость:{ad.price}\nМестонахождение:{ad.location}\nКонтактная информация:{ad.contact}\n",
            reply_markup=await moderate_keyboard(ad))


@router.message(F.text == 'Оценить бота')
async def rate_bot(message: types.Message, state: FSMContext):
    await state.set_state(RateAdState.action)
    await message.answer("Выберите оценку", reply_markup=await rating_keyboard())


@router.callback_query(RateAdState.action)
async def process_rate_bot(call: types.CallbackQuery, state: FSMContext):
    await call.answer('')
    await rate_bot_for_user(call.from_user.id, call.data)
    await call.message.edit_text("Спасибо за оценку нашего бота")
    await state.clear()


# Вспомогательные роутеры
# Отмена заполнения обявления
@router.callback_query(F.data == 'quit')
async def cancel_fill_ad(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text('❌Заполнение объявления отменено')


# Отмена поиска обявления
@router.callback_query(F.data == 'cancel_search')
async def cancel_fill_ad(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text('❌Поиск объявления отменен')


# Отмена изменения обявления
@router.callback_query(F.data == 'cancel_edit')
async def cancel_edit_user(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text('❌Изменение объявления отменено')


# Возврат назад к объявлениям пользователя
@router.callback_query(F.data == 'back')
async def return_back(call: types.CallbackQuery, state: FSMContext):
    await call.answer('')
    await call.message.answer("Ваши объявления:", reply_markup=await get_ads_keyboard(await get_ads(call.from_user.id)))


# Отмена модерации объявления
@router.callback_query(F.data == 'cancel_moderate_ad')
async def cancel_moderation_ad(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text('❌Модерация объявления отменена')
