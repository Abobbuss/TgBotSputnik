from aiogram.fsm.state import State, StatesGroup


# Класс состояний
class UserState(StatesGroup):
    MAIN_MENU = State()                  # Главное меню
    START_MENU = State()                 # Меню после /start
    SELECT_DIRECTION = State()           # В каком направлении вы работаете
    SHOW_RUDA_OPTIONS = State()          # После выбора "Руды"
    SHOW_UGOL_OPTIONS = State()          # После выбора "Уголь"
    SHOW_BOTH_OPTIONS = State()          # После выбора "Оба направления"

    AWAITING_CONTACT_INFO = State()      # для имени, email, компании и должности

    AWAITING_EMAIL_RUDA = State()
    AWAITING_EMAIL_UGOL = State()

    AWAITING_CONTACT_INFO_RUDA = State()
    AWAITING_CONTACT_INFO_UGOL = State()

    AWAITING_PHONE_RUDA = State()
    AWAITING_PHONE_UGOL = State()

    CONFIRM_PHONE_UGOL = State()
    CONFIRM_PHONE_RUDA = State()

    AWAITING_EMAIL_BOTH = State()         # Email для обоих направлений
    AWAITING_CONTACT_INFO_BOTH = State()  # Контактные данные для обоих направлений
    AWAITING_PHONE_BOTH = State()         # Телефон для обоих направлений
    CONFIRM_PHONE_BOTH = State()          # Подтверждение телефона (если уже указан)



    # Admins
    AWAITING_REFERRAL_NAME = State()