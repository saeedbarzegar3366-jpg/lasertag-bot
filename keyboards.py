from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup
)

phone_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="📱 ارسال شماره",
                request_contact=True
            )
        ]
    ],
    resize_keyboard=True
)

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📖 آموزش رزرو")
        ],
        [
            KeyboardButton(text="📆 رزرو"),
            KeyboardButton(text="❌ لغو رزرو")
        ],
        [
            KeyboardButton(text="📋 رزروهای من")
        ],
        [
            KeyboardButton(text="🖼 تصاویر باشگاه"),
            KeyboardButton(text="🎯 لیزرتگ چیست")
        ],
        [
            KeyboardButton(text="🎁 کد تخفیف"),
            KeyboardButton(text="📜 قوانین باشگاه")
        ],
        [
            KeyboardButton(text="📍 اطلاعات باشگاه"),
            KeyboardButton(text="📞 ارتباط با ادمین")
        ],
    ],
    resize_keyboard=True
)


confirm_reservation_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="✅ رزرو کن")
        ],
        [
            KeyboardButton(text="🔙 تغییر ساعت")
        ],
        [
            KeyboardButton(text="🏠 منوی اصلی")
        ]
    ],
    resize_keyboard=True
)


admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📅 رزروهای امروز")
        ],
        [
            KeyboardButton(text="👥 تعداد کاربران")
        ],
        [
            KeyboardButton(text="📋 مدیریت رزروها")
        ],
        [
            KeyboardButton(text="⏳ رزروهای تایید نشده")
        ],
        [
            KeyboardButton(text="📢 ارسال پیام همگانی")
        ],
        [
            KeyboardButton(text="🎟 ساخت کد تخفیف همگانی")
        ],
        [
            KeyboardButton(text="🖼 مدیریت تصاویر")
        ],
        [
            KeyboardButton(text="🏠 منوی اصلی")
        ]
    ],
    resize_keyboard=True
)


admin_main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📆 رزرو")
        ],
        [
            KeyboardButton(text="📋 رزروهای من")
        ],
        [
            KeyboardButton(text="❌ لغو رزرو")
        ],
        [
            KeyboardButton(text="🖼 تصاویر باشگاه")
        ],
        [
            KeyboardButton(text="🎯 لیزرتگ چیست")
        ],
        [
            KeyboardButton(text="🎁 کد تخفیف")
        ],
        [
            KeyboardButton(text="👨‍💼 پنل مدیریت")
        ]
    ],
    resize_keyboard=True
)


discount_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="🔗 لینک دعوت من"
            )
        ],
        [
            KeyboardButton(
                text="🎟 ساخت کد تخفیف"
            )
        ],
        [
            KeyboardButton(
                text="🔙 بازگشت"
            )
        ]
    ],
    resize_keyboard=True
)



discount_create_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="10٪ تخفیف (5 امتیاز)")],
        [KeyboardButton(text="20٪ تخفیف (10 امتیاز)")],
        [KeyboardButton(text="30٪ تخفیف (15 امتیاز)")],
        [KeyboardButton(text="40٪ تخفیف (20 امتیاز)")],
        [KeyboardButton(text="50٪ تخفیف (25 امتیاز)")],
        [KeyboardButton(text="🔙 بازگشت")]
    ],
    resize_keyboard=True
)



discount_choice_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="🎟 کد تخفیف دارم"
            )
        ],
        [
            KeyboardButton(
                text="➡️ ادامه بدون تخفیف"
            )
        ],
        [
            KeyboardButton(
                text="🔙 بازگشت"
            )
        ]
    ],
    resize_keyboard=True
)


from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

cancel_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔙 بازگشت")]
    ],
    resize_keyboard=True
)



photos_admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="➕ افزودن عکس"
            )
        ],
        [
            KeyboardButton(
                text="🗑 حذف عکس"
            )
        ],
        [
            KeyboardButton(
                text="👀 مشاهده عکس‌ها"
            )
        ],
        [
            KeyboardButton(
                text="🔙 بازگشت"
            )
        ]
    ],
    resize_keyboard=True
)