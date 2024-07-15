from database.requests import get_all_ads, get_users_by_keyword, is_user_notified, mark_user_as_notified


async def notify_users(context):
    print("Начало отправки уведомлений")
    # Получите все активные объявления из вашей базы данных
    ads = await get_all_ads()
    for ad in ads:
        # Получить всех пользователей, которых заинтересовала категория и размер этого объявления
        interested_users = await get_users_by_keyword(ad.name)
        for user in interested_users:
            # Проверьте, был ли этот пользователь уже уведомлен об этом объявлении
            if not await is_user_notified(user.tg_id, ad.id):
                # Отправить уведомление этому пользователю о новом объявлении
                await context.send_message(chat_id=user.tg_id,
                                           text=f"Найдено новое объявление по вашему запросу:\n{ad.name}")
                # Отметьте этого пользователя как уведомленного об этом объявлении в вашей базе данных
                await mark_user_as_notified(user.tg_id, ad.id)
    print("Завершена отправка уведомлений")
