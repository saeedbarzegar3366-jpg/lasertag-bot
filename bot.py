import asyncio

from aiogram import Bot
from aiogram import Dispatcher
from aiogram import F
from aiogram.types import FSInputFile
from aiogram.filters import CommandStart

from aiogram.fsm.context import FSMContext


from datetime import datetime


from states import (
    RegisterState,
    ReservationState,
    AdminState
)

from keyboards import (
    phone_keyboard,
    main_menu,
    confirm_reservation_keyboard,
    admin_menu,
    admin_main_menu,
    discount_menu,
    discount_create_menu,
    discount_choice_keyboard,
    cancel_menu,
    photos_admin_menu,
)

import jdatetime

from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)


from database import (
    create_db,
    add_user,
    get_user,
    create_reservations_table,
    add_reservation,
    get_reservation,
    update_reservation_status,
    get_last_user_reservation,
    get_day_reservations,
    get_reservation_by_id,
    get_user_reservations,
    cancel_reservation,
    get_all_user_reservations,
    get_users_count,
    get_all_users,
    delete_user,
    get_today_reservations,
    get_today_reservations_with_users,
    get_all_user_ids,
    create_discount_codes_table,
    get_user_points,
    add_points,
    increase_invites,
    create_discount_code,
    remove_points,
    get_user_discount_codes,
    update_reservations_table,
    get_discount_code,
    use_discount_code,
    delete_expired_reservations,
    get_unpaid_reservation,
    mark_receipt_sent,
    get_user_reservations_count,
    create_global_discount,
    has_used_discount,
    save_discount_usage,
    update_discount_codes_table,
    create_discount_usage_table,
    get_all_reservations_with_users,
    delete_reservation_by_id,
    expire_old_reservations,
    create_club_photos_table,
    add_club_photo,
    get_club_photos,
    delete_club_photo,
    get_all_approved_reservations,
    mark_reminder_sent,
    get_pending_approvals,
    save_receipt_file
)


from config import (
    BOT_TOKEN,
    ADMIN_ID,
    DEPOSIT_AMOUNT,
    CARD_NUMBER,
    CARD_OWNER
)


bot = Bot(BOT_TOKEN)

from aiogram.fsm.storage.memory import MemoryStorage

dp = Dispatcher(storage=MemoryStorage())


from aiogram.filters import CommandObject


def get_menu(user_id):

    if user_id == ADMIN_ID:
        return admin_main_menu

    return main_menu

    
@dp.message(CommandStart())
async def start(
    message: Message,
    state: FSMContext,
    command: CommandObject
):

    referrer_id = None

    if command.args:

        try:
            referrer_id = int(
                command.args
            )
        except:
            pass

    if referrer_id:

        await state.update_data(
            invited_by=referrer_id
        )

    user = await get_user(
        message.from_user.id
    )

    if user:

        if message.from_user.id == ADMIN_ID:

            await message.answer(
                "خوش آمدید",
                reply_markup=admin_main_menu
            )

        else:

            await message.answer(
                "خوش آمدید",
                reply_markup=get_menu(
                    message.from_user.id
                )
            )

        return

    await message.answer(
        "لطفا شماره خود را ارسال کنید",
        reply_markup=phone_keyboard
    )

    await state.set_state(
        RegisterState.phone
    )



@dp.message(RegisterState.phone, F.contact)
async def get_phone(
    message: Message,
    state: FSMContext
):
    await state.update_data(
        phone=message.contact.phone_number
    )

    await message.answer(
        "نام و نام خانوادگی خود را وارد کنید"
    )

    await state.set_state(RegisterState.name)


@dp.message(RegisterState.phone)
async def get_phone_text(
    message: Message,
    state: FSMContext
):

    phone = message.text.strip()

    if not phone.isdigit():

        await message.answer(
            "❌ لطفاً شماره تماس معتبر وارد کنید."
        )
        return

    await state.update_data(
        phone=phone
    )

    await message.answer(
        "نام و نام خانوادگی خود را وارد کنید"
    )

    await state.set_state(
        RegisterState.name
    )


@dp.message(RegisterState.name)
async def get_name(
    message: Message,
    state: FSMContext
):

    if any(char.isdigit() for char in message.text):

        await message.answer(
            "❌ نام و نام خانوادگی نباید شامل عدد باشد."
        )
        return

    data = await state.get_data()

    phone = data["phone"]

    invited_by = data.get(
        "invited_by"
    )

    await add_user(
        message.from_user.id,
        phone,
        message.text,
        invited_by
    )

    if (
        invited_by
        and invited_by != message.from_user.id
    ):

        await add_points(
            invited_by,
            1
        )

        await increase_invites(
            invited_by
        )

        try:

            points = await get_user_points(
                invited_by
            )

            await bot.send_message(
                invited_by,
                f"""
    🎉 یک کاربر جدید با لینک دعوت شما ثبت‌نام کرد.

    👤 نام:
    {message.text}

    ⭐ 1 امتیاز به حساب شما اضافه شد.

    مجموع امتیاز شما:
    {points}
    """
            )

        except:
            pass

    await message.answer(
        "ثبت نام شما کامل شد ✅",
        reply_markup=get_menu(
            message.from_user.id
        )
    )

    await state.clear()




def create_days_keyboard():

    today = jdatetime.date.today()

    rows = []
    current_row = []

    for i in range(30):

        day = today + jdatetime.timedelta(days=i)

        current_row.append(
            KeyboardButton(
                text=day.strftime("%Y/%m/%d")
            )
        )

        if len(current_row) == 3:
            rows.append(current_row)
            current_row = []

    if current_row:
        rows.append(current_row)

    rows.append(
        [KeyboardButton(text="🔙 بازگشت")]
    )

    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True
    )


async def create_time_keyboard(
    reserve_date
):

    await delete_expired_reservations()

    reservations = await get_day_reservations(
        reserve_date
    )

    reserved = {}

    for item in reservations:

        reserved[item[0]] = item[1]

    rows = []
    current_row = []

    now = datetime.now()

    today_jalali = jdatetime.datetime.fromgregorian(
        datetime=now
    ).strftime("%Y/%m/%d")

    for hour in range(10, 24):

        time_text = f"{hour}:00"

        if reserve_date == today_jalali and hour <= now.hour:
            button_text = f"⏰ {time_text}"

            current_row.append(
                KeyboardButton(text=button_text)
            )

            if len(current_row) == 3:
                rows.append(current_row)
                current_row = []

            continue

        if time_text in reserved:

            if reserved[time_text] in ["pending", "waiting_admin"]:
                button_text = f"🔒 {time_text}"

            elif reserved[time_text] == "approved":
                button_text = f"❌ {time_text}"

            else:
                button_text = time_text

        else:
            button_text = time_text

        current_row.append(
            KeyboardButton(
                text=button_text
            )
        )

        if len(current_row) == 3:

            rows.append(current_row)

            current_row = []

    if current_row:
        rows.append(current_row)

    rows.append(
        [KeyboardButton(text="🔙 بازگشت")]
    )

    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True
    )




@dp.message(F.text == "📆 رزرو")
async def reserve(
    message: Message,
    state: FSMContext
):

    await delete_expired_reservations()

    reservation = await get_unpaid_reservation(
    message.from_user.id
    )

    if reservation:

        await message.answer(
            """
    ❌ شما یک رزرو ثبت کرده‌اید اما هنوز فیش پرداخت ارسال نکرده‌اید.

    ابتدا فیش رزرو قبلی را ارسال کنید.

    در غیر اینصورت باید 10 دقیقه صبر کنید تا رزرو منقضی شود.
    """
        )

        return



    await state.set_state(
        ReservationState.selected_date
    )

    await message.answer(
    """ℹ️ توجه:

    هر ساعت رزرو شامل ۲ سانس بازی می‌باشد (هر سانس ۱۵ دقیقه است و هر بازی شامل ۲ سانس می‌باشد).

    در صورتی که قصد دارید بیشتر از ۲ سانس بازی کنید، لطفاً دو یا چند ساعت متوالی را رزرو نمایید
    برای مثال، برای ۴ سانس بازی باید ۲ ساعت پشت سر هم رزرو کنید

    📅 حالا تاریخ مورد نظر خود را انتخاب کنید:""",
        reply_markup=create_days_keyboard()
    )


@dp.message(ReservationState.selected_date)
async def select_date(
    message: Message,
    state: FSMContext
):

    if message.text == "🔙 بازگشت":

        await state.clear()

        if message.from_user.id == ADMIN_ID:

            await message.answer(
                "منوی اصلی",
                reply_markup=admin_main_menu
            )

        else:

            await message.answer(
                "منوی اصلی",
                reply_markup=get_menu(
                    message.from_user.id
                )
            )

        return

    count = await get_user_reservations_count(
    message.from_user.id,
    message.text
    )

    if count >= 5:

        await message.answer(
            """
        ⛔ شما امروز به سقف مجاز رزرو رسیده‌اید.

        هر کاربر حداکثر می‌تواند در طول یک روز ۵ رزرو ثبت کند و شما امروز ۵ رزرو خود را انجام داده‌اید.

        لطفاً پس از شروع روز جدید (ساعت ۰۰:۰۰) دوباره برای ثبت رزرو اقدام کنید.
        """
        )

        return

    today = jdatetime.date.today()

    valid_dates = []

    for i in range(30):
        day = today + jdatetime.timedelta(days=i)

        valid_dates.append(
            day.strftime("%Y/%m/%d")
        )

    if message.text not in valid_dates:

        await message.answer(
            "❌ لطفاً فقط از دکمه‌های تاریخ استفاده کنید."
        )
        return


    await state.update_data(
        selected_date=message.text
    )

    await state.set_state(
        ReservationState.selected_time
    )

    await message.answer(
        f"تاریخ انتخاب شد: {message.text}\n\nساعت را انتخاب کنید",
        reply_markup=await create_time_keyboard(
            message.text
        )
    )


@dp.message(ReservationState.selected_time)
async def select_time(
    message: Message,
    state: FSMContext
):

    if message.text.startswith("⏰"):

        await message.answer(
            "⛔ این ساعت گذشته و قابل رزرو نیست."
        )

        return

    if message.text == "🔙 بازگشت":

        await state.set_state(
            ReservationState.selected_date
        )

        await message.answer(
            "تاریخ مورد نظر را انتخاب کنید",
            reply_markup=create_days_keyboard()
        )

        return

    valid_times = [
    f"{hour}:00"
    for hour in range(10, 24)
]

    clean_time = (
        message.text
        .replace("🔒 ", "")
        .replace("❌ ", "")
    )

    if clean_time not in valid_times:

        await message.answer(
            "❌ لطفاً فقط از دکمه‌های ساعت استفاده کنید."
        )
        return


    data = await state.get_data()

    reserve_date = data["selected_date"]
    reserve_time = message.text

    if reserve_time.startswith("🔒"):

        await message.answer(
            "این تایم در انتظار تایید ادمین است."
        )
        return

    if reserve_time.startswith("❌"):

        await message.answer(
            "این تایم قبلاً رزرو شده است."
        )
        return

    reservation = await get_reservation(
        reserve_date,
        reserve_time
    )

    if reservation:

        await message.answer(
            "❌ این ساعت قبلاً رزرو شده یا در انتظار تایید است."
        )
        return

    await state.update_data(
    selected_time=reserve_time
    )

    await state.set_state(
        ReservationState.confirm_reservation
    )

    await message.answer(
        f"""
    📅 تاریخ: {reserve_date}

    ⏰ ساعت: {reserve_time}

    آیا مایل به ثبت رزرو هستید؟
    """,
        reply_markup=confirm_reservation_keyboard
    )


    
@dp.message(F.text == "❌ لغو رزرو")
async def cancel(
    message: Message,
    state: FSMContext
):

    reservations = await get_user_reservations(
        message.from_user.id
    )

    if not reservations:

        await message.answer(
            "شما هیچ رزرو فعالی ندارید."
        )
        return

    text = "رزروهای فعال شما:\n\n"

    for reservation in reservations:

        text += (
            f"ID: {reservation[0]}\n"
            f"📅 {reservation[2]}\n"
            f"⏰ {reservation[3]}\n\n"
        )

    text += "شماره ID رزرو را ارسال کنید."

    await state.set_state(
        ReservationState.waiting_cancel_id
    )

    await message.answer(
    text,
    reply_markup=cancel_menu
    )



@dp.message(
    ReservationState.waiting_cancel_id,
    F.text == "🔙 بازگشت"
)
async def back_from_cancel(
    message: Message,
    state: FSMContext
):
    await state.clear()

    await message.answer(
        "منوی اصلی",
        reply_markup=get_menu(
            message.from_user.id
        )
    )

@dp.message(
    ReservationState.waiting_cancel_id
)
async def process_cancel_id(
    message: Message,
    state: FSMContext
):

    if not message.text.isdigit():

        await message.answer(
            "لطفاً فقط شماره ID را وارد کنید."
        )
        return

    reservation_id = int(
        message.text
    )

    reservation = await get_reservation_by_id(
        reservation_id
    )

    if not reservation:

        await message.answer(
            "رزروی با این ID پیدا نشد."
        )
        return

    if reservation[1] != message.from_user.id:

        await message.answer(
            "این رزرو متعلق به شما نیست."
        )
        return

    if reservation[4] == "cancelled":

        await message.answer(
            "این رزرو قبلاً لغو شده است."
        )
        return

    await cancel_reservation(
        reservation_id
    )

    await state.clear()

    await message.answer(
        "✅ رزرو با موفقیت لغو شد.",
        reply_markup=get_menu(
            message.from_user.id
        )
    )



@dp.message(F.text == "🖼 تصاویر باشگاه")
async def show_club_photos(
    message: Message
):

    photos = await get_club_photos()

    if not photos:

        await message.answer(
            "هنوز تصویری ثبت نشده است."
        )
        return

    for photo in photos:

        await bot.send_photo(
            chat_id=message.chat.id,
            photo=photo[1]
        )


@dp.message(F.text == "🎯 لیزرتگ چیست")
async def laser_info(message: Message):
    await message.answer(
        """
🎯 لیزرتگ چیست؟

لیزرتگ یک بازی گروهی هیجان‌انگیز و کاملاً ایمن است که در آن بازیکنان با استفاده از تجهیزات الکترونیکی مخصوص و بدون هیچ‌گونه گلوله یا درد فیزیکی با یکدیگر رقابت می‌کنند.

در این بازی هر بازیکن یک جلیقه و یک تفنگ لیزری دریافت می‌کند و باید با همکاری تیم خود، حریفان را هدف قرار داده و امتیاز کسب کند.

✅ بدون درد و کاملاً ایمن
✅ مناسب برای بانوان و آقایان
✅ مناسب برای کودکان، نوجوانان و بزرگسالان
✅ مناسب برای تولدها و دورهمی‌ها

🏆 هدف بازی:
کسب بیشترین امتیاز و شکست دادن تیم مقابل.

قبل از شروع بازی نیز آموزش کامل توسط مجموعه ارائه می‌شود.
"""
    )


@dp.message(
    ReservationState.confirm_reservation,
    F.text == "✅ رزرو کن"
)
async def confirm_reservation(
    message: Message,
    state: FSMContext
):

    await state.set_state(
        ReservationState.waiting_discount_choice
    )

    await message.answer(
        """
🎟 کد تخفیف دارید؟

در صورت داشتن کد، روی دکمه
«کد تخفیف دارم»
بزنید.
""",
        reply_markup=discount_choice_keyboard
    )




@dp.message(
    ReservationState.confirm_reservation,
    F.text == "❌ لغو"
)
async def cancel_confirm(
    message: Message,
    state: FSMContext
):

    await state.clear()

    await message.answer(
        "رزرو لغو شد.",
        reply_markup=get_menu(
            message.from_user.id
        )
    )





@dp.message(
    ReservationState.waiting_receipt,
    F.photo
)
async def receive_receipt(
    message: Message,
    state: FSMContext
):

    reservation = await get_last_user_reservation(
        message.from_user.id
    )

    if not reservation:

        await message.answer(
            "رزروی پیدا نشد."
        )
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ تایید رزرو",
                    callback_data=f"approve_{reservation[0]}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ رد رزرو",
                    callback_data=f"reject_{reservation[0]}"
                )
            ]
        ]
    )

    await bot.send_photo(
        chat_id=ADMIN_ID,
        photo=message.photo[-1].file_id,
        caption=
        f"""
📌 درخواست رزرو جدید

👤 نام:
{message.from_user.full_name}

🆔 آیدی:
{message.from_user.id}

📅 تاریخ:
{reservation[2]}

⏰ ساعت:
{reservation[3]}

🎁 تخفیف:
{reservation[6]}٪
""",
        reply_markup=keyboard
    )

    file_id = message.photo[-1].file_id

    await save_receipt_file(
        reservation[0],
        file_id
    )

    await message.answer(
        "✅ فیش دریافت شد و برای بررسی ارسال گردید."
    )

    await state.clear()



@dp.message(
    AdminState.waiting_club_photo,
    F.photo
)
async def receive_club_photo(
    message: Message,
    state: FSMContext
):
    print("PHOTO RECEIVED")

    file_id = message.photo[-1].file_id

    await add_club_photo(file_id)

    await state.clear()

    await message.answer(
        "✅ عکس ذخیره شد",
        reply_markup=photos_admin_menu
    )



@dp.message(
    F.photo,
    F.from_user.id != ADMIN_ID
)

async def receive_receipt_without_state(
    message: Message,
    state: FSMContext
):


    reservation = await get_unpaid_reservation(
        message.from_user.id
    )

    if not reservation:
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ تایید رزرو",
                    callback_data=f"approve_{reservation[0]}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ رد رزرو",
                    callback_data=f"reject_{reservation[0]}"
                )
            ]
        ]
    )

    await bot.send_photo(
        chat_id=ADMIN_ID,
        photo=message.photo[-1].file_id,
        caption=f"""
📌 درخواست رزرو جدید

👤 نام:
{message.from_user.full_name}

🆔 آیدی:
{message.from_user.id}

📅 تاریخ:
{reservation[2]}

⏰ ساعت:
{reservation[3]}

🎁 تخفیف:
{reservation[6]}٪
""",
        reply_markup=keyboard
    )

    await mark_receipt_sent(
        reservation[0]
    )

    await message.answer(
        "✅ فیش دریافت شد و برای بررسی ارسال گردید."
    )

    await state.clear()



@dp.callback_query(
    F.data.startswith("approve_")
)
async def approve_reservation(
    callback: CallbackQuery
):

    reservation_id = int(
        callback.data.split("_")[1]
    )

    await update_reservation_status(
        reservation_id,
        "approved"
    )

    reservation = await get_reservation_by_id(
        reservation_id
    )

    user_id = reservation[1]



    await add_points(
        user_id,
        2
    )

    points = await get_user_points(
        user_id
    )

    await bot.send_message(
        user_id,
        f"""
    ✅ رزرو شما تایید شد

    📅 تاریخ: {reservation[2]}
    ⏰ ساعت: {reservation[3]}

    ⭐ 2 امتیاز به حساب شما اضافه شد.

    🏆 مجموع امتیاز شما:
    {points}

    منتظر حضور شما هستیم.
    """
    )


    
    await callback.message.edit_reply_markup(
    reply_markup=None
    )

    user = await get_user(user_id)

    discount_percent = reservation[6] or 0

    discount_text = f"{discount_percent}٪"

    await callback.message.answer(
    f"""
    ✅ رزرو تایید شد

    👤 نام:
    {user[2]}

    🆔 آیدی:
    {user_id}

    📱 شماره تماس:
    {user[1]}

    📅 تاریخ:
    {reservation[2]}

    ⏰ ساعت:
    {reservation[3]}

    🎟 میزان تخفیف:
    {discount_text}
    """
    )


@dp.callback_query(
    F.data.startswith("reject_")
)
async def reject_reservation(
    callback: CallbackQuery
):

    reservation_id = int(
        callback.data.split("_")[1]
    )

    await update_reservation_status(
        reservation_id,
        "rejected"
    )

    reservation = await get_reservation_by_id(
        reservation_id
    )

    user_id = reservation[1]

    await bot.send_message(
        user_id,
        f"""
    ❌ رزرو شما رد شد

    📅 تاریخ: {reservation[2]}
    ⏰ ساعت: {reservation[3]}

    در صورت نیاز دوباره رزرو ثبت کنید.
    """
    )

    await callback.message.edit_caption(
        callback.message.caption +
        "\n\n❌ رزرو رد شد"
    )

    await callback.answer(
        "رزرو رد شد"
    )


@dp.message(F.text == "📋 رزروهای من")
async def my_reservations(
    message: Message
):

    await expire_old_reservations()
    
    reservations = await get_all_user_reservations(
        message.from_user.id
    )

    if not reservations:

        await message.answer(
            "شما هنوز رزروی ندارید."
        )
        return

    text = "📋 لیست رزروهای شما:\n\n"

    for reservation in reservations:

        status = reservation[4]

        if status == "pending":
             status_text = "🟠 در انتظار ارسال فیش"

        elif status == "waiting_admin":
            status_text = "🟡 در انتظار تایید ادمین"

        elif status == "approved":
            status_text = "🟢 تایید شده"

        elif status == "cancelled":
            status_text = "⚫ لغو شده"

        elif status == "rejected":
            status_text = "🔴 رد شده"

        elif status == "expired":
            status_text = "⏳ تاریخ این رزرو گذشته"

        else:
            status_text = status

        text += (
            f"ID: {reservation[0]}\n"
            f"📅 {reservation[2]}\n"
            f"⏰ {reservation[3]}\n"
            f"📌 وضعیت: {status_text}\n\n"
        )

    await message.answer(text)



@dp.message(
    ReservationState.confirm_reservation,
    F.text == "🔙 تغییر ساعت"
)
async def back_to_time(
    message: Message,
    state: FSMContext
):

    data = await state.get_data()

    await state.set_state(
        ReservationState.selected_time
    )

    await message.answer(
        "ساعت جدید را انتخاب کنید",
        reply_markup=await create_time_keyboard(
            data["selected_date"]
        )
    )


@dp.message(
    ReservationState.confirm_reservation,
    F.text == "🏠 منوی اصلی"
)
async def back_to_menu(
    message: Message,
    state: FSMContext
):

    await state.clear()

    await message.answer(
        "منوی اصلی",
        reply_markup=get_menu(
            message.from_user.id
        )
    )



@dp.message(
    F.text == "🏠 منوی اصلی"
)
async def main_menu_button(
    message: Message,
    state: FSMContext
):

    await state.clear()

    if message.from_user.id == ADMIN_ID:

        await message.answer(
            "منوی اصلی",
            reply_markup=admin_main_menu
        )

    else:

        await message.answer(
            "منوی اصلی",
            reply_markup=get_menu(
            message.from_user.id
        )
        )



@dp.message(F.text == "/admin")
async def admin_panel(
    message: Message
):

    if message.from_user.id != ADMIN_ID:

        await message.answer(
            "شما دسترسی ندارید."
        )
        return

    await message.answer(
        "👨‍💼 پنل مدیریت",
        reply_markup=admin_menu
    )



@dp.message(
    F.text == "👨‍💼 پنل مدیریت"
)
async def admin_panel_button(
    message: Message
):

    if message.from_user.id != ADMIN_ID:

        await message.answer(
            "شما دسترسی ندارید."
        )
        return

    await message.answer(
        "👨‍💼 پنل مدیریت",
        reply_markup=admin_menu
    )



@dp.message(
    F.text == "👥 تعداد کاربران"
)
async def users_count(
    message: Message,
    state: FSMContext
):

    if message.from_user.id != ADMIN_ID:
        return

    users = await get_all_users()

    text = f"👥 تعداد کاربران: {len(users)}\n\n"

    for user in users:

        text += (
            f"👤 {user[1]}\n"
            f"🆔 {user[0]}\n\n"
        )

    text += (
        "آیدی عددی کاربر را برای حذف ارسال کنید."
    )

    await state.set_state(
    AdminState.waiting_delete_user
    )
    

    await message.answer(text)
    



@dp.message(
    AdminState.waiting_delete_user,
    F.text == "🔙 بازگشت"
)

async def back_from_delete_user(
    message: Message,
    state: FSMContext
):
    await state.clear()

    await message.answer(
        "پنل مدیریت",
        reply_markup=admin_menu
    )

@dp.message(
    AdminState.waiting_delete_user
)
async def process_delete_user(
    message: Message,
    state: FSMContext
):

    if not message.text.isdigit():

        await message.answer(
            "فقط آیدی عددی کاربر را ارسال کنید."
        )
        return

    user_id = int(message.text)

    await delete_user(user_id)

    await state.clear()

    await message.answer(
        "✅ کاربر حذف شد."
    )



@dp.message(
    F.text == "📅 رزروهای امروز"
)
async def today_reservations(
    message: Message
):

    if message.from_user.id != ADMIN_ID:
        return

    today = jdatetime.date.today().strftime(
        "%Y/%m/%d"
    )

    reservations = await get_today_reservations_with_users(
        today
    )

    if not reservations:

        await message.answer(
            "امروز رزروی ثبت نشده است."
        )
        return

    text = f"📅 رزروهای امروز ({today})\n\n"

    for reservation in reservations:

        if reservation[4] == "pending":
            status = "🟡 در انتظار تایید"
        else:
            status = "🟢 تایید شده"

        text += (
            f"{status}\n"
            f"⏰ ساعت: {reservation[3]}\n"
            f"👤 نام: {reservation[1]}\n"
            f"📱 شماره: {reservation[2]}\n"
            f"🆔 آیدی: {reservation[5]}\n\n"
        )

    await message.answer(text)


@dp.message(
    F.text == "📢 ارسال پیام همگانی"
)
async def broadcast_start(
    message: Message,
    state: FSMContext
):


    if message.from_user.id != ADMIN_ID:
        return

    await state.set_state(
        AdminState.waiting_broadcast
    )

    await message.answer(
        """
پیام یا عکس موردنظر را ارسال کنید.

برای خروج:
🏠 منوی اصلی
"""
    )


@dp.message(
    AdminState.waiting_broadcast,
    F.text
)
async def receive_broadcast_text(
    message: Message,
    state: FSMContext
):

    if message.text == "🏠 منوی اصلی":

        await state.clear()

        await message.answer(
            "پنل مدیریت",
            reply_markup=admin_menu
        )
        return

    await state.update_data(
        broadcast_text=message.text,
        broadcast_type="text"
    )

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="✅ تایید ارسال"
                )
            ],
            [
                KeyboardButton(
                    text="❌ لغو ارسال"
                )
            ]
        ],
        resize_keyboard=True
    )

    await state.set_state(
        AdminState.confirm_broadcast
    )

    await message.answer(
        f"""
📋 پیش نمایش پیام:

{message.text}
""",
        reply_markup=keyboard
    )


@dp.message(
    AdminState.waiting_broadcast,
    F.photo
)
async def receive_broadcast_photo(
    message: Message,
    state: FSMContext
):


    caption = message.caption or ""

    await state.update_data(
        broadcast_type="photo",
        photo_id=message.photo[-1].file_id,
        caption=caption
    )

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="✅ تایید ارسال"
                )
            ],
            [
                KeyboardButton(
                    text="❌ لغو ارسال"
                )
            ]
        ],
        resize_keyboard=True
    )

    await state.set_state(
        AdminState.confirm_broadcast
    )

    await message.answer_photo(
        photo=message.photo[-1].file_id,
        caption=
        f"""
📋 پیش نمایش ارسال

{caption}
""",
        reply_markup=keyboard
    )


@dp.message(
    AdminState.confirm_broadcast,
    F.text == "❌ لغو ارسال"
)
async def cancel_broadcast(
    message: Message,
    state: FSMContext
):

    await state.clear()

    await message.answer(
        "ارسال لغو شد.",
        reply_markup=admin_menu
    )



@dp.message(
    AdminState.confirm_broadcast,
    F.text == "✅ تایید ارسال"
)
async def send_broadcast(
    message: Message,
    state: FSMContext
):

    data = await state.get_data()

    users = await get_all_user_ids()

    success = 0

    for user in users:

        try:

            if data["broadcast_type"] == "text":

                await bot.send_message(
                    user[0],
                    data["broadcast_text"]
                )

            else:

                await bot.send_photo(
                    chat_id=user[0],
                    photo=data["photo_id"],
                    caption=data["caption"]
                )

            success += 1

        except:
            pass

    await state.clear()

    await message.answer(
        f"""
✅ ارسال انجام شد

تعداد کاربران دریافت کننده:
{success}
""",
        reply_markup=admin_menu
    )


@dp.message(
    F.text == "🎟 ساخت کد تخفیف همگانی"
)
async def admin_discount_start(
    message: Message,
    state: FSMContext
):

    if message.from_user.id != ADMIN_ID:
        return

    await state.set_state(
        AdminState.waiting_discount_code
    )

    await message.answer(
        "کد تخفیف را وارد کنید"
    )



@dp.message(
    AdminState.waiting_discount_code
)
async def admin_discount_code(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        discount_code=message.text.strip().upper()
    )

    await state.set_state(
        AdminState.waiting_discount_percent
    )

    await message.answer(
        "درصد تخفیف را وارد کنید (مثلاً 20)"
    )



@dp.message(
    AdminState.waiting_discount_percent
)
async def admin_discount_percent(
    message: Message,
    state: FSMContext
):

    if not message.text.isdigit():

        await message.answer(
            "فقط عدد وارد کنید."
        )
        return

    await state.update_data(
        discount_percent=int(message.text)
    )

    await state.set_state(
        AdminState.waiting_discount_days
    )

    await message.answer(
        "چند روز اعتبار داشته باشد؟"
    )




@dp.message(
    F.text == "🔗 لینک دعوت من"
)
async def my_invite_link(
    message: Message
):

    bot_info = await bot.get_me()

    invite_link = (
        f"https://t.me/"
        f"{bot_info.username}"
        f"?start={message.from_user.id}"
    )

    points = await get_user_points(
        message.from_user.id
    )

    await message.answer(
        f"""
🔗 لینک دعوت شما:

{invite_link}

⭐ امتیاز فعلی:
{points}

برای هر کاربر جدید:
1 امتیاز دریافت می‌کنید.
"""
    )



@dp.message(F.text == "🎁 کد تخفیف")
async def discount_panel(
    message: Message,
    state: FSMContext
):

    points = await get_user_points(
        message.from_user.id
    )

    await state.set_state(
    ReservationState.waiting_discount_menu
    )

    await message.answer(
        f"""
🎁 باشگاه تخفیف

⭐ امتیاز شما: {points}

هر 5 امتیاز = 10٪ تخفیف
هر 10 امتیاز = 20٪ تخفیف
هر 15 امتیاز = 30٪ تخفیف
هر 20 امتیاز = 40٪ تخفیف
هر 25 امتیاز = 50٪ تخفیف
""",
        reply_markup=discount_menu
    )



@dp.message(
    ReservationState.waiting_discount_menu,
    F.text == "🔙 بازگشت"
)
async def back_from_discount_menu(
    message: Message,
    state: FSMContext
):
    await state.clear()

    await message.answer(
        "منوی اصلی",
        reply_markup=get_menu(
            message.from_user.id
        )
    )



@dp.message(
    ReservationState.waiting_discount_menu,
    F.text == "🎟 ساخت کد تخفیف"
)
async def create_discount_menu(
    message: Message,
    state: FSMContext
):

    await state.set_state(
        ReservationState.waiting_discount_create
    )

    await message.answer(
        "درصد تخفیف مورد نظر را انتخاب کنید:",
        reply_markup=discount_create_menu
    )



@dp.message(
    ReservationState.waiting_discount_create,
    F.text == "🔙 بازگشت"
)
async def back_from_discount_create(
    message: Message,
    state: FSMContext
):
    await state.set_state(
        ReservationState.waiting_discount_menu
    )

    points = await get_user_points(
        message.from_user.id
    )

    await message.answer(
        f"""
🎁 باشگاه تخفیف

⭐ امتیاز شما: {points}
""",
        reply_markup=discount_menu
    )




@dp.message(
    F.text.in_(
        [
            "10٪ تخفیف (5 امتیاز)",
            "20٪ تخفیف (10 امتیاز)",
            "30٪ تخفیف (15 امتیاز)",
            "40٪ تخفیف (20 امتیاز)",
            "50٪ تخفیف (25 امتیاز)"
        ]
    )
)
async def create_discount(
    message: Message
):

    discounts = {
        "10٪ تخفیف (5 امتیاز)": (10, 5),
        "20٪ تخفیف (10 امتیاز)": (20, 10),
        "30٪ تخفیف (15 امتیاز)": (30, 15),
        "40٪ تخفیف (20 امتیاز)": (40, 20),
        "50٪ تخفیف (25 امتیاز)": (50, 25),
    }

    percent, required_points = discounts[
        message.text
    ]

    points = await get_user_points(
        message.from_user.id
    )

    if points < required_points:

        await message.answer(
            f"""
❌ امتیاز شما کافی نیست.

⭐ امتیاز فعلی:
{points}

🔒 برای این تخفیف به
{required_points}
امتیاز نیاز دارید.
"""
        )
        return

    await remove_points(
        message.from_user.id,
        required_points
    )

    code = await create_discount_code(
        message.from_user.id,
        percent
    )

    points = await get_user_points(
        message.from_user.id
    )

    await message.answer(
        f"""
✅ کد تخفیف شما ساخته شد

🎟 کد تخفیف:

<code>{code}</code>
(روی کد کلیک کنید تا کد کپی شود)

📉 درصد تخفیف:
{percent}٪

⭐ امتیاز باقی‌مانده:
{points}
""",
        parse_mode="HTML"
    )



@dp.message(
    ReservationState.waiting_discount_choice,
    F.text == "➡️ ادامه بدون تخفیف"
)
async def continue_without_discount(
    message: Message,
    state: FSMContext
):

    data = await state.get_data()

    reserve_date = data["selected_date"]
    reserve_time = data["selected_time"]

    await add_reservation(
        message.from_user.id,
        reserve_date,
        reserve_time,
        "pending"
    )

    await state.set_state(
        ReservationState.waiting_receipt
    )

    await message.answer(
        f"""
✅ رزرو ثبت شد

📅 تاریخ: {reserve_date}

⏰ ساعت: {reserve_time}

💳 مبلغ بیعانه:
{DEPOSIT_AMOUNT:,} تومان

شماره کارت:

<code>{CARD_NUMBER}</code>

(برای کپی کردن شماره کارت , روی آن کلیک کنید)

به نام:

{CARD_OWNER}

⏳ توجه:

شما فقط 10 دقیقه فرصت دارید
فیش واریزی را ارسال کنید.

در غیر اینصورت رزرو به صورت خودکار لغو شده و تایم آزاد خواهد شد.

پس از واریز، عکس فیش را ارسال کنید.
""",
        parse_mode="HTML",
        reply_markup=get_menu(
            message.from_user.id
        )
    )



@dp.message(
    ReservationState.waiting_discount_choice,
    F.text == "🎟 کد تخفیف دارم"
)
async def ask_discount_code(
    message: Message,
    state: FSMContext
):

    back_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🔙 بازگشت"
                )
            ]
        ],
        resize_keyboard=True
    )

    await state.set_state(
        ReservationState.waiting_discount_code
    )

    await message.answer(
        """
🎟 لطفاً کد تخفیف خود را ارسال کنید.
""",
        reply_markup=back_keyboard
    )



@dp.message(
    ReservationState.waiting_discount_choice,
    F.text == "🔙 بازگشت"
)
async def back_from_discount_choice(
    message: Message,
    state: FSMContext
):

    await state.set_state(
        ReservationState.confirm_reservation
    )

    data = await state.get_data()

    await message.answer(
        f"""
📅 تاریخ: {data['selected_date']}

⏰ ساعت: {data['selected_time']}

آیا مایل به ثبت رزرو هستید؟
""",
        reply_markup=confirm_reservation_keyboard
    )



@dp.message(
    ReservationState.waiting_discount_code
)
async def check_discount_code(
    message: Message,
    state: FSMContext
):

    if not message.text:
        await message.answer(
            "لطفاً کد تخفیف را به صورت متنی وارد کنید."
        )
        return

    if message.text == "🔙 بازگشت":

        await state.set_state(
            ReservationState.waiting_discount_choice
        )

        await message.answer(
            "یکی از گزینه‌ها را انتخاب کنید:",
            reply_markup=discount_choice_keyboard
        )
        return

    discount = await get_discount_code(
        message.text.strip().upper()
    )
    
    code = message.text.strip().upper()

    used_before = await has_used_discount(
        message.from_user.id,
        code
    )

    if used_before:

        await message.answer(
            """
    ❌ شما قبلاً از این کد تخفیف استفاده کرده‌اید.
    """
        )

        return


    if not discount:

        await message.answer(
            """
❌ کد تخفیف معتبر نیست.

دوباره تلاش کنید.
"""
        )
        return

    percent = discount[3]

  
    data = await state.get_data()

    reserve_date = data["selected_date"]
    reserve_time = data["selected_time"]

    code = message.text.strip().upper()

    await add_reservation(
        message.from_user.id,
        reserve_date,
        reserve_time,
        "pending",
        code,
        percent
    )

    await save_discount_usage(
    message.from_user.id,
    code
    )

    discounted_amount = int(
        DEPOSIT_AMOUNT *
        (100 - percent) / 100
    )

    await state.set_state(
        ReservationState.waiting_receipt
    )

    await message.answer(
        f"""
✅ کد تخفیف اعمال شد

🎁 درصد تخفیف:
{percent}٪

💳 مبلغ بیعانه اصلی:
{DEPOSIT_AMOUNT:,} تومان

💰 مبلغ قابل پرداخت:
{discounted_amount:,} تومان

📅 تاریخ:
{reserve_date}

⏰ ساعت:
{reserve_time}

شماره کارت:

<code>{CARD_NUMBER}</code>

(برای کپی کردن شماره کارت , روی آن کلیک کنید)

به نام:

{CARD_OWNER}

⏳ توجه:

شما فقط 10 دقیقه فرصت دارید
فیش واریزی را ارسال کنید.

در غیر اینصورت رزرو به صورت خودکار لغو شده و تایم آزاد خواهد شد.

پس از واریز، عکس فیش را ارسال کنید.
""",
        parse_mode="HTML",
        reply_markup=get_menu(
            message.from_user.id
        )
    )




@dp.message(
    AdminState.waiting_discount_days
)
async def admin_discount_days(
    message: Message,
    state: FSMContext
):

    if not message.text.isdigit():

        await message.answer(
            "فقط عدد وارد کنید."
        )
        return

    data = await state.get_data()

    code = data["discount_code"]

    percent = data["discount_percent"]

    days = int(message.text)

    await state.update_data(
        discount_days=days
    )

    await state.set_state(
        AdminState.waiting_discount_message
    )

    await message.answer(
        "متن اطلاعیه را وارد کنید"
    )

    return



@dp.message(
    AdminState.waiting_discount_message
)
async def admin_discount_message(
    message: Message,
    state: FSMContext
):

    data = await state.get_data()

    code = data["discount_code"]
    percent = data["discount_percent"]
    days = data["discount_days"]

    text = message.text

    await create_global_discount(
        code,
        percent,
        days
    )

    users = await get_all_user_ids()

    for user in users:

        try:

            await bot.send_message(
                user[0],
                f"""
            🎉 اطلاعیه

            {text}

            🎟 کد تخفیف:

            <code>{code}</code>

            (برای کپی کردن کد روی آن کلیک کنید)

            📉 درصد تخفیف:
            {percent}٪

            ⏳ اعتبار:
            {days} روز
            """,
                parse_mode="HTML"
            )


        except:
            pass

    await state.clear()

    await message.answer(
        "✅ کد تخفیف برای همه کاربران ارسال شد.",
        reply_markup=admin_menu
    )



@dp.message(
    F.text == "➕ رزرو تلفنی"
)
async def manual_reservation_start(
    message: Message,
    state: FSMContext
):

    await state.set_state(
        ReservationState.waiting_manual_date
    )

    await message.answer(
        "📅 تاریخ مورد نظر را انتخاب کنید",
        reply_markup=create_days_keyboard()
    )



@dp.message(
    ReservationState.waiting_manual_date
)
async def manual_reservation_date(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        manual_date=message.text
    )

    await state.set_state(
        ReservationState.waiting_manual_time
    )

    await message.answer(
        "🕐 ساعت مورد نظر را انتخاب کنید",
        reply_markup=await create_time_keyboard(
            message.text
        )
    )



@dp.message(
    ReservationState.waiting_manual_time
)
async def manual_reservation_time(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        manual_time=message.text
    )

    await state.set_state(
        ReservationState.waiting_manual_info
    )

    await message.answer(
        """👤 اطلاعات مشتری را وارد کنید

مثال:
علی محمدی - 09123456789"""
    )



@dp.message(
    ReservationState.waiting_manual_info
)
async def manual_reservation_info(
    message: Message,
    state: FSMContext
):

    data = await state.get_data()

    await add_reservation(
        user_id=0,
        reserve_date=data["manual_date"],
        reserve_time=data["manual_time"],
        status="approved"
    )

    await state.clear()

    await message.answer(
        f"""
✅ رزرو تلفنی ثبت شد

📅 {data['manual_date']}
⏰ {data['manual_time']}
""",
        reply_markup=admin_menu
    )


    

@dp.message(
    F.text == "📋 مدیریت رزروها"
)
async def manage_reservations(
    message: Message,
    state: FSMContext
):

    await expire_old_reservations()
    reservations = await get_all_reservations_with_users()

    reservations = [
    r for r in reservations
    if r[6] == "approved"
    ]

    if not reservations:

        await message.answer(
            "هیچ رزروی ثبت نشده است."
        )
        return

    text = "📋 لیست رزروها\n\n"

    for reservation in reservations:

        text += (
            f"ID: {reservation[0]}\n"
            f"👤 {reservation[1]}\n"
            f"📞 {reservation[2]}\n"
            f"🆔 {reservation[3]}\n"
            f"📅 {reservation[4]}\n"
            f"⏰ {reservation[5]}\n"
            f"📌 {reservation[6]}\n\n"
            f"━━━━━━━━━━━━━━\n\n"
    )

    text += (
        "━━━━━━━━━━━━━━\n\n"
        "برای حذف رزرو:\n"
        "55\n\n"
        "یا\n\n"
        "55,56,57"
    )

    await state.set_state(
        AdminState.waiting_delete_reservation
    )

    await message.answer(
        text
    )



@dp.message(
    AdminState.waiting_delete_reservation,
    F.text == "🔙 بازگشت"
)
async def back_from_delete_reservation(
    message: Message,
    state: FSMContext
):

    await state.clear()

    await message.answer(
        "پنل مدیریت",
        reply_markup=admin_menu
    )




@dp.message(
    AdminState.waiting_delete_reservation
)
async def process_delete_reservation(
    message: Message,
    state: FSMContext
):

    ids_text = message.text.replace(" ", "")

    try:

        ids = [
            int(x)
            for x in ids_text.split(",")
        ]

    except ValueError:

        await message.answer(
            "❌ فقط ID رزرو وارد کنید.\n\nمثال:\n55\n\nیا\n55,56,57"
        )
        return

    deleted_count = 0

    for reservation_id in ids:

        await delete_reservation_by_id(
            reservation_id
        )

        deleted_count += 1

    await state.clear()

    await message.answer(
        f"✅ تعداد {deleted_count} رزرو حذف شد.",
        reply_markup=admin_menu
    )




@dp.message(F.text == "📍 اطلاعات باشگاه")
async def club_address(
    message: Message
):

    await message.answer(
        """
🏢 باشگاه لیزرتگ اسکواد

📍 آدرس:

تبریز - راه آهن به سمت تراکتورسازی
صد متر بالاتر از سه راهی کبریت سازی

🗺 لوکیشن مجموعه:

https://maps.app.goo.gl/kDDuCp6kfCUDhT159

📞 تلفن تماس:

+989145805676

📷 اینستاگرام:

https://instagram.com/lasertag.squad
"""
    )



@dp.message(
    F.text == "🖼 مدیریت تصاویر"
)
async def photos_admin(
    message: Message
):

    await message.answer(
        "مدیریت تصاویر باشگاه",
        reply_markup=photos_admin_menu
    )



@dp.message(
    F.text == "➕ افزودن عکس"
)
async def add_photo_start(
    message: Message,
    state: FSMContext
):

    await state.set_state(
        AdminState.waiting_club_photo
    )
    

    await message.answer(
        "عکس را ارسال کنید"
    )




@dp.message(
    F.text == "👀 مشاهده عکس‌ها"
)
async def admin_show_photos(
    message: Message
):

    photos = await get_club_photos()

    if not photos:

        await message.answer(
            "عکسی ثبت نشده است."
        )
        return

    for photo in photos:

        await message.answer_photo(
            photo=photo[1],
            caption=f"ID: {photo[0]}"
        )



@dp.message(
    F.text == "🗑 حذف عکس"
)
async def delete_photo_start(
    message: Message,
    state: FSMContext
):

    photos = await get_club_photos()

    if not photos:

        await message.answer(
            "عکسی وجود ندارد."
        )
        return

    text = "ID عکس را وارد کنید:\n\n"

    for photo in photos:

        text += f"{photo[0]}\n"

    await state.set_state(
        AdminState.waiting_delete_photo
    )

    await message.answer(text)



@dp.message(
    AdminState.waiting_delete_photo
)
async def delete_photo_process(
    message: Message,
    state: FSMContext
):

    if not message.text.isdigit():

        await message.answer(
            "فقط ID وارد کنید."
        )
        return

    await delete_club_photo(
        int(message.text)
    )

    await state.clear()

    await message.answer(
        "✅ عکس حذف شد",
        reply_markup=photos_admin_menu
    )




@dp.message(F.text == "🔙 بازگشت")
async def back_from_photos_menu(
    message: Message,
    state: FSMContext
):
    await state.clear()

    if message.from_user.id == ADMIN_ID:

        await message.answer(
            "پنل مدیریت",
            reply_markup=admin_menu
        )




@dp.message(
    F.text == "🖼 تصاویر باشگاه"
)
async def show_club_photos(
    message: Message
):

    photos = await get_club_photos()

    if not photos:

        await message.answer(
            "هنوز تصویری ثبت نشده است."
        )
        return

    for photo in photos:

        await message.answer_photo(
            photo=photo[1]
        )




@dp.message(AdminState.waiting_club_photo, F.photo)
async def receive_club_photo(message: Message, state: FSMContext):

    print("PHOTO RECEIVED")

    file_id = message.photo[-1].file_id

    await add_club_photo(file_id)

    await state.clear()

    await message.answer(
        "✅ عکس ذخیره شد",
        reply_markup=photos_admin_menu
    )



async def reminder_checker():

    while True:

        try:

            reservations = await get_all_approved_reservations()

            now = datetime.now()

            for reservation in reservations:

                reservation_id = reservation[0]
                user_id = reservation[1]

                reserve_date = reservation[2]
                reserve_time = reservation[3]

                reminder_24 = reservation[9]
                reminder_12 = reservation[10]
                reminder_6 = reservation[11]

                jalali_dt = jdatetime.datetime.strptime(
                    f"{reserve_date} {reserve_time}",
                    "%Y/%m/%d %H:%M"
                )

                reserve_datetime = jalali_dt.togregorian()

                remaining_hours = (
                    reserve_datetime - now
                ).total_seconds() / 3600

                if (
                    remaining_hours <= 24
                    and remaining_hours > 23
                    and reminder_24 == 0
                ):
                

                    await bot.send_message(
                        user_id,
                        f"""
⏰ یادآوری رزرو

📅 تاریخ:
{reserve_date}

⏰ ساعت:
{reserve_time}

تنها 24 ساعت تا زمان رزرو شما باقی مانده است.
"""
                    )

                    await mark_reminder_sent(
                        reservation_id,
                        24
                    )

                elif (
                    remaining_hours <= 12
                    and remaining_hours > 11
                    and reminder_12 == 0
                ):

                    await bot.send_message(
                        user_id,
                        f"""
⏰ یادآوری رزرو

📅 تاریخ:
{reserve_date}

⏰ ساعت:
{reserve_time}

تنها 12 ساعت تا زمان رزرو شما باقی مانده است.
"""
                    )

                    await mark_reminder_sent(
                        reservation_id,
                        12
                    )

                elif (
                    remaining_hours <= 6
                    and remaining_hours > 5
                    and reminder_6 == 0
                ):

                    await bot.send_message(
                        user_id,
                        f"""
⏰ یادآوری رزرو

📅 تاریخ:
{reserve_date}

⏰ ساعت:
{reserve_time}

تنها 6 ساعت تا زمان رزرو شما باقی مانده است.
"""
                    )

                    await mark_reminder_sent(
                        reservation_id,
                        6
                    )

        except Exception as e:

            print("REMINDER ERROR:", e)

        await asyncio.sleep(60)




@dp.message(F.text == "📖 آموزش رزرو")
async def reservation_guide(message: Message):

    await message.answer_photo(
        photo="AgACAgQAAxkBAAIM92okVMec5PHOF8AYvDTRB_ZX83A9AAKNDmsbJE4pUYoGPZRAoU0SAQADAgADeQADOwQ"
    )




@dp.message(F.text == "📞 ارتباط با ادمین")
async def contact_admin(message: Message):

    await message.answer(
        """
📞 ارتباط با ادمین

📱 شماره تماس:
+989145805676

💬 تلگرام:
https://t.me/saeed_xau
"""
    )




@dp.message(F.text == "📜 قوانین باشگاه")
async def club_rules(message: Message):
    await message.answer(
        """
📜 قوانین باشگاه لیزرتگ اسکواد

1️⃣ حداقل 10 دقیقه قبل از سانس در مجموعه حضور داشته باشید.

2️⃣ در صورت تأخیر، زمان از دست‌رفته از تایم بازی کسر خواهد شد.

3️⃣ هر سانس شامل 2 راند 15 دقیقه‌ای و مجموعاً 30 دقیقه بازی است.

4️⃣ دویدن خطرناک، حرکات آکروباتیک و درگیری فیزیکی ممنوع است.

5️⃣ حداقل سن مجاز برای بازی 10 سال می‌باشد.

6️⃣ افراد مست و بانوان باردار مجاز به شرکت در بازی نیستند.

7️⃣ رعایت احترام به بازیکنان و پرسنل الزامی است.

8️⃣ استفاده صحیح از تجهیزات الزامی است.

9️⃣ تصمیم مسئول مجموعه در مسائل ایمنی لازم‌الاجرا است.

🔟 ثبت رزرو به منزله پذیرش قوانین مجموعه می‌باشد.

🌟 آرزوی لحظاتی هیجان‌انگیز برای شما
"""
    )




@dp.message(F.text == "⏳ رزروهای تایید نشده")
async def show_pending_reservations(message: Message):

    reservations = await get_pending_approvals()

    if not reservations:
        await message.answer(
            "✅ رزرو تایید نشده‌ای وجود ندارد."
        )
        return

    for reservation in reservations:

        reservation_id = reservation[0]

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ تایید",
                        callback_data=f"approve_{reservation_id}"
                    ),
                    InlineKeyboardButton(
                        text="❌ رد",
                        callback_data=f"reject_{reservation_id}"
                    )
                ]
            ]
        )

        user = await get_user(reservation[1])

        file_id = reservation[12]

        await bot.send_photo(
            chat_id=message.chat.id,
            photo=file_id,
            caption=f"""
        📌 رزرو شماره {reservation_id}

        👤 نام:
        {user[2]}

        📞 شماره تماس:
        {user[1]}

        🎁 میزان تخفیف:
        {reservation[6]}٪

        📅 تاریخ:
        {reservation[2]}

        ⏰ ساعت:
        {reservation[3]}
        """,
            reply_markup=keyboard
        )





async def main():

    await create_db()

    await create_reservations_table()

    await create_discount_codes_table()

    await create_discount_usage_table()

    await update_discount_codes_table()

    await update_reservations_table()

    await expire_old_reservations()

    await create_club_photos_table()

    asyncio.create_task(
    reminder_checker()
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())