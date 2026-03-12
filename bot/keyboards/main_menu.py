from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="چه خبر از ایران؟")],
        [KeyboardButton(text="آینده ایران چی میشه؟")]
    ],
    resize_keyboard=True
)
