from aiogram.fsm.state import State, StatesGroup


# Класс состояний
class UserState(StatesGroup):
    MAIN_MENU = State()     # Главное меню
    PROJECTS = State()      # Наши проекты
    NEWS = State()          # Новости спутника
    PRESENTATION = State()  # Получить последнюю презентацию
    INVEST = State()        # Хочу инвестировать
    STARTUP = State()       # Хочу открыть свой стартап