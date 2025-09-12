import traceback

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot_operations.bot_support.base_router import commands_router
from bot_operations.bot_support.keyboards import user_links_actions_keyboard, back_to_links_actions_keyboard, \
    delete_all_links_keyboard
from bot_operations.bot_support.states import LinkStates
from bot_operations.bot_support.support_funcs import normalize_url, split_text_by_limit
from db_operations.all_models import UserModel, LinksModel
from db_operations.links_dao.links_dao import LinksDAO
from db_operations.user_dao.user_dao import UserDAO
from logger.logger import logger


@commands_router.callback_query(F.data == 'links_list_actions_for_user')
async def links_list_actions_for_user(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        'Выберите действие со списком ссылок',
        reply_markup=user_links_actions_keyboard
    )
    await state.clear()

@commands_router.callback_query(F.data == 'bad_links')
async def bad_links(callback: CallbackQuery):
    try:
        user_id = callback.from_user.id
        links: list[LinksModel]  = await LinksDAO.get_user_links(user_id)
        bad_links_list = []
        for link in links:
            if link.last_status != 200:
                bad_links_list.append(str(link.last_status))
        if bad_links_list:
            await callback.message.edit_text(
                'Список всех сломанных ссылок:\n' + '\n'.join(bad_links_list),
                reply_markup=back_to_links_actions_keyboard,
                disable_web_page_preview=True
            )
        else:
            await callback.message.edit_text(
                'Все отслеживаемые ссылки имеют текущий статус 200',
                reply_markup=back_to_links_actions_keyboard
            )
    except Exception:
        logger.warning(traceback.format_exc())

@commands_router.callback_query(F.data == 'add_link_to_list')
async def add_link_to_list(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        'Теперь отправьте мне ссылки, которые хотите добавить.\n\n'
        'Отправить можно как одну, так и сразу несколько, каждую с новой строки.',
        reply_markup=back_to_links_actions_keyboard
    )
    await state.set_state(LinkStates.waiting_for_link)


@commands_router.callback_query(F.data == 'show_all_links')
async def show_all_links(callback: CallbackQuery):
    user_id = callback.from_user.id
    links = await LinksDAO.get_user_links(user_id)
    text = 'Ваши сайты для проверки:'
    if not links:
        text += '\nНет ни одной ссылки.'
    else:
        for url in links:
            text += f'\n{url}'
    parts = split_text_by_limit(text=text)
    if len(parts) == 1:
        await callback.message.edit_text(
            parts[0],
            reply_markup=back_to_links_actions_keyboard,
            disable_web_page_preview=True
        )
    else:
        await callback.message.edit_text(parts.pop(0))
        reply_markup = None
        for i, part in enumerate(parts):
            if i+1 == len(parts):
                reply_markup = back_to_links_actions_keyboard
            await callback.message.answer(
                text=part,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )

@commands_router.callback_query(F.data == 'delete_all_links')
async def delete_all_links(callback: CallbackQuery):
    await callback.message.edit_text(
        'Вы уверены в том, что хотите УДАЛИТЬ ВСЕ добавленные ссылки?',
        reply_markup=delete_all_links_keyboard
    )


@commands_router.callback_query(F.data == 'shure_to_delete_all')
async def shure_to_delete_all(callback: CallbackQuery):
    user_id = callback.from_user.id
    user: UserModel = await UserDAO.find_by_id(user_id)
    links = list(user.links)
    await UserDAO.drop_all_links(user_id)
    await LinksDAO.cleanup_orphan_links()
    await callback.message.edit_text(
        'Все ваши ссылки удалены!',
        reply_markup=back_to_links_actions_keyboard
    )


@commands_router.message(LinkStates.waiting_for_link)
async def parse_links(message: Message, state: FSMContext):
    try:
        text = message.text
        splitted: list = text.split('\n')

        links = []
        bad_links = []
        for line in splitted:
            line = line.strip()
            if line:  # пропускаем пустые строки
                try:
                    links.append(normalize_url(line))
                except ValueError:
                    bad_links.append(line)  # можно логировать или пропускать неверные ссылки
        if not links:
            await message.answer(
                'Не удалось получить ни одной ссылки из Вашего сообщения.'
                '\nПопробуете ещё раз?',
                reply_markup=back_to_links_actions_keyboard
            )
            return
        await UserDAO.add_links_to_user(user_id=message.from_user.id, new_links=links)
        await state.clear()
        answer_text = (f'Ваше сообщение успешно прочитано!\nБыло отправлено строк: {len(splitted)}'
                       f'\nИз них прочитано успешно: {len(links)}')
        if bad_links:
            answer_text += '\nНеобработанные строки:'
            for bad_line in bad_links:
                answer_text += f"\n{bad_line}"
        await message.answer(
            text=answer_text,
            reply_markup=back_to_links_actions_keyboard
        )
    except Exception:
        await message.answer(
            'Непредвиденная ошибка!',
            reply_markup=back_to_links_actions_keyboard
        )