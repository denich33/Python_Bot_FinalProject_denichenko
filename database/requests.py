from database.models import async_session
from database.models import Ad, User
from sqlalchemy import select, update, or_


async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()


async def add_ad(tg_id, name, description, price, location, contact):
    async with async_session() as session:
        session.add(
            Ad(
                tg_id=tg_id,
                name=name,
                description=description,
                price=price,
                location=location,
                contact=contact)
        )
        await session.commit()


# показать все объявления пользователя
async def get_ads(tg_id):
    async with async_session() as session:
        ads = await session.scalars(
            select(Ad).where(Ad.tg_id == tg_id, Ad.moderated == True)
        )
        return ads


# Получение информации о обьявлении
async def get_ad_info(tg_id, ad_id):
    async with async_session() as session:
        ad = await session.scalar(
            select(Ad).where(Ad.tg_id == tg_id, Ad.id == ad_id)
        )
        return ad


# Удаление объявления пользователя
async def delete_ad(tg_id, ad_id):
    async with async_session() as session:
        ad = await session.scalar(
            select(Ad).where(Ad.tg_id == tg_id, Ad.id == ad_id)
        )
        if ad:
            await session.delete(ad)
            await session.commit()
            return True
        else:
            return False


# Изменение объявления пользователя
async def update_ad(tg_id, ad_id, column, edit_data):
    async with async_session() as session:
        ad = await session.scalar(
            select(Ad).where(Ad.tg_id == tg_id, Ad.id == ad_id)
        )
        if ad:
            if column == 'name':
                ad.name = edit_data
            elif column == 'description':
                ad.description = edit_data
            elif column == 'price':
                ad.price = edit_data
            elif column == 'location':
                ad.location = edit_data
            elif column == 'contact':
                ad.contact = edit_data
            else:
                return False
            await session.commit()
            return True
        else:
            return False


# Поиск по фильтру
async def search_ads(keyword, price, location):
    async with async_session() as session:
        ads = None
        if keyword is not None and price is None and location is None:
            ads = await session.scalars(
                select(Ad).where(or_(Ad.name.ilike(f'%{keyword}%'), Ad.description.ilike(f'%{keyword}%')),
                                 Ad.moderated == True)
            )
        elif keyword is not None and price is not None and location is None:
            ads = await session.scalars(
                select(Ad).where(or_(Ad.name.ilike(f'%{keyword}%'), Ad.description.ilike(f'%{keyword}%')),
                                 Ad.price == price, Ad.moderated == True)
            )
        elif keyword is None and price is not None and location is None:
            ads = await session.scalars(
                select(Ad).where(Ad.price == price, Ad.moderated == True)
            )
        elif keyword is None and price is None and location is not None:
            ads = await session.scalars(
                select(Ad).where(Ad.location == location, Ad.moderated == True)
            )
        elif keyword is not None and price is None and location is not None:
            ads = await session.scalars(
                select(Ad).where(or_(Ad.name.ilike(f'%{keyword}%'), Ad.description.ilike(f'%{keyword}%')),
                                 Ad.location == location, Ad.moderated == True)
            )
        elif keyword is not None and price is not None and location is not None:
            ads = await session.scalars()
        elif keyword and price and location:
            ads = await session.scalars(
                select(Ad).where(or_(Ad.name.ilike(f'%{keyword}%'), Ad.description.ilike(f'%{keyword}%')),
                                 Ad.price == price,
                                 Ad.location == location, Ad.moderated == True)
            )
        return ads


# Добавляет в базу данных о пользователе ключевые слова
async def add_search_history(tg_id, keyword):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            if user.search_history is not None:
                user.search_history += f'{str(keyword)} '
            else:
                user.search_history = f'{str(keyword)} '
            await session.commit()


# Получение списка ключевых слов пользователя
async def get_search_history(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            return user.search_history.split()
        else:
            return None


# Получение списка всех объявлений
async def get_all_ads():
    async with async_session() as session:
        ads = await session.scalars(select(Ad).where(Ad.moderated == True))
        return ads


# Получение списка всех  объявлений без модерации
async def get_all_ads_without_moderation():
    async with async_session() as session:
        ads = await session.scalars(select(Ad).where(Ad.moderated == False))
        return ads


# Получить всех пользователей, которых заинтересовало ключевое слово
async def get_users_by_keyword(keyword):
    async with (async_session() as session):
        keywords = keyword.split()
        users = []
        for keyword in keywords:
            data = await session.scalars(
                select(User).where(User.search_history.ilike(f'%{keyword}%'))
            )
            users.extend(data.all())
        return users


# Проверьте, был ли этот пользователь уже уведомлен об этом объявлении
async def is_user_notified(tg_id, ad_id):
    ad_id = str(ad_id)
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            notified_ads = user.notified_ads
            if notified_ads:
                notified_ads = notified_ads.split()
                if ad_id in notified_ads:
                    return True
                else:
                    return False
        else:
            return False


# mark_user_as_notified
async def mark_user_as_notified(tg_id, ad_id):
    async with async_session() as session:
        ad_id = str(ad_id)
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            notified_ads = user.notified_ads

            if notified_ads is not None:
                if ad_id not in notified_ads.split():
                    user.notified_ads += f'{ad_id} '
            else:
                user.notified_ads = f'{ad_id} '
            await session.commit()


# Принятие решения по модерации объявления
async def accept_moderation(ad_id, result):
    async with async_session() as session:
        ad = await session.scalar(select(Ad).where(Ad.id == ad_id))
        if ad:
            if result:
                ad.moderated = True
            else:
                await session.delete(ad)
            await session.commit()


# Оценка работы бота
async def rate_bot_for_user(tg_id, rating):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            user.rating_bot_job = rating
            await session.commit()
