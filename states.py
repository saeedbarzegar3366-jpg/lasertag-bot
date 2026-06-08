from aiogram.fsm.state import State, StatesGroup


class RegisterState(StatesGroup):
    phone = State()
    name = State()


class ReservationState(StatesGroup):
    selected_date = State()
    selected_time = State()

    confirm_reservation = State()

    waiting_discount_choice = State()
    waiting_discount_code = State()

    waiting_discount_menu = State()
    waiting_discount_create = State()

    waiting_receipt = State()

    waiting_cancel_id = State()
    waiting_delete_user = State()



class AdminState(StatesGroup):
    waiting_broadcast = State()
    confirm_broadcast = State()

    waiting_discount_code = State()
    waiting_discount_percent = State()
    waiting_discount_days = State()
    waiting_discount_message = State()

    waiting_delete_user = State()

    waiting_delete_reservation = State()

    waiting_club_photo = State()
    waiting_delete_photo = State()