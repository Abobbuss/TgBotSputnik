from aiogram.fsm.state import State, StatesGroup


# Класс состояний
class UserState(StatesGroup):
    MAIN_MENU = State()                  # Главное меню
    START_MENU = State()                 # Меню после /start
    SELECT_DIRECTION = State()          # В каком направлении вы работаете
    SHOW_RUDA_OPTIONS = State()         # После выбора "Руды"
    SHOW_UGOL_OPTIONS = State()         # После выбора "Уголь"
    SHOW_BOTH_OPTIONS = State()         # После выбора "Оба направления"
    AWAITING_EMAIL_FOR_DETAILS = State()
    AWAITING_EMAIL_FOR_DEMO = State()
    AWAITING_CONTACT_INFO = State()  # для имени, email, компании и должности
    AWAITING_EMAIL_RUDA = State()
    AWAITING_EMAIL_UGOL = State()
    AWAITING_CONTACT_INFO_RUDA = State()
    AWAITING_CONTACT_INFO_UGOL = State()
    AWAITING_SHARE_AFTER_CONTACT_RUDA = State()
    AWAITING_SHARE_AFTER_CONTACT_UGOL = State()

    PROJECTS = State()
    NEWS = State()
    WAITING_TITLE = State()
    WAITING_DESCRIPTION = State()
    WAITING_IMAGE_DECISION = State()
    WAITING_IMAGE = State()

    # Amins
    AWAITING_REFERRAL_NAME = State()