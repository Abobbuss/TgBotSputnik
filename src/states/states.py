from aiogram.fsm.state import State, StatesGroup


# Класс состояний
class UserState(StatesGroup):
    MAIN_MENU = State()               # Главное меню
    PROJECTS = State()                # Наши проекты
    NEWS = State()                    # Новости спутника
    WAITING_TITLE = State()           # Ожидание заголовка
    WAITING_DESCRIPTION = State()     # Ожидание описания
    WAITING_IMAGE_DECISION = State()  # Ожидание ответа о загрузке фото
    WAITING_IMAGE = State()           # Ожидание фото (если нужно)