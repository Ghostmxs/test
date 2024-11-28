# Запрашиваем имя или описание
@dp.callback_query(F.data.in_({"edit_name_simple", "edit_name_chat_channel", "edit_description"}))
async def ask_for_name(call, state: FSMContext, user_id=None, false_msg="", current_state=None):
    """

    :param false_msg:
    :param call:
    :param state:
    :param user_id:
    :return:
    """

    if user_id is None:
        user_id = call.from_user.id

    if current_state is None:
        if call.data == "edit_name_simple":
            await state.set_state(MyState.edit_name)
        elif call.data == "edit_name_chat_channel":
            await state.set_state(MyState.edit_name_chat_channel)
        elif call.data == "edit_description":
            await state.set_state(MyState.edit_description)
    else:
        await state.set_state(current_state)

    # Проверяем, какой коллбек был получен, и в зависимости от этого отправляем нужный текст
    if call.data == "edit_name_simple":
        text = ask_for_new_name  
    if call.data == "edit_name_chat_channel":
        text = ask_for_new_name
    elif call.data == "edit_description":
        text = "Пришли новое описание для бота (1-255 символов):"  # Новый текст для запроса описания



    keyboard = create_inline_keyboard([InlineKeyboardButton(text=cancel_text, callback_data="cancel")])
    sent_message = await bot.send_message(chat_id=user_id,
                                          text=false_msg + text,
                                          reply_markup=keyboard,
                                          parse_mode='html')
    await state.update_data(form_message=sent_message.message_id)
    await state.update_data(message_id=sent_message.message_id)

    data = await state.get_data()
    await start_action(user_id, data.get("main_message_id"), data.get("message_id"))



# Проверка и сохранение нового названия бота/чата/канала
@dp.message(StateFilter(MyState.edit_name_chat_channel, MyState.edit_name))
async def handle_name_input(message: types.Message, state: FSMContext):
    """

    :param message:
    :param state:
    :return:
    """
    chat_id = message.chat.id
    text = message.text.strip()
    data = await state.get_data()
    current_state = await state.get_state()

    if current_state == MyState.edit_name and not (1 <= len(text) <= 64):
        await bot.delete_message(chat_id, message.message_id)
        await bot.delete_message(chat_id, data.get("form_message"))
        await ask_for_name(None, state, chat_id, symbol_limit(64), current_state)
        return
    elif current_state == MyState.edit_name_chat_channel and not (1 <= len(text) <= 255):
        await bot.delete_message(chat_id, message.message_id)
        await bot.delete_message(chat_id, data.get("form_message"))
        await ask_for_name(None, state, chat_id, symbol_limit(255), current_state)  # ВОТ ТУТ ВЫЗЫВАЕМ ФУНКЦИЮ. и она не возвращает колбек соответсвенно
        return

    # Успешно! Дальше просим токен

    last_bot_msg = data.get("message_id")

    await bot.delete_message(chat_id, last_bot_msg)
    await bot.delete_message(chat_id, message.message_id)

    await state.update_data(name=text)

    # Запоминаем, для чего нам token
    if current_state == MyState.edit_name:
        await state.update_data(last_state='name')
        await ask_for_token(chat_id, state)
    elif current_state == MyState.edit_name_chat_channel:
        await state.update_data(last_state='chat_channel_name')
        await ask_for_chat_channel_id(chat_id, state)
