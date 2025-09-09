from aiogram.fsm.state import StatesGroup, State


class LinkStates(StatesGroup):
    waiting_for_link = State()