from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from django.conf import settings
from bot.models import TgUser, Admin
from aiogram.dispatcher.filters import BoundFilter

bot = Bot(token=settings.API_TOKEN)
dp = Dispatcher(bot)

# Foydalanuvchining adminligini  tekshirish uchun maxsus filtr
class IsAdminFilter(BoundFilter):
    key = 'admin'

    def __init__(self, admin: bool):
        self.admin = admin

    async def check(self, message: types.Message):
        try:
            # Yuboruvchi malumotlar bazasida administrator ekanligini tekshirish
            await Admin.objects.aget(user_id=message.from_user.id)
            return True  # topildi foydalanuvchi admin
        except Admin.DoesNotExist:
            return False  # admin emas

# Administrator filtrini ro'yxatdan o'tkazish
dp.filters_factory.bind(IsAdminFilter)

#  mavjud adminlani olish
async def get_available_admin():
    try:
        return await Admin.objects.filter(status='online').afirst()
    except Admin.DoesNotExist:
        return None

# Admin holatini yangilash
async def set_admin_status(admin_id, status):
    try:
        admin_status = await Admin.objects.aget(user_id=admin_id)
        admin_status.status = status
        await admin_status.asave()
    except Admin.DoesNotExist:
        await Admin.objects.acreate(user_id=admin_id, status=status)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    try:
        user = await TgUser.objects.aget(user_id=message.from_user.id)
        # Agar user oldingi suhbatni tugatgan bolsa holatni "kutish" holatiga qaytarish
        if user.status == 'completed':
            user.status = 'waiting'
            await user.asave()
    except TgUser.DoesNotExist:
        user = await TgUser.objects.acreate(user_id=message.from_user.id, name=message.from_user.full_name, status='waiting')
        if await Admin.objects.filter(user_id=message.from_user.id).afirst():
            user.status = 'admin'
            await user.asave()
    await message.reply(f"Salom {user.name}")

# Admin suhbatni tugatish uchun /stop buyrug'idan foydalanadi
@dp.message_handler(commands=['stop'], admin=True)
async def admin_stop(message: types.Message):
    admin = await Admin.objects.prefetch_related('current_user').aget(user_id=message.from_user.id)

    if admin.current_user:
        user = admin.current_user

        # Administrator mavjudligini yangilang  joriy foydalanuvchini tozalash yani adminni bo'sh qilish
        admin.status = 'online'
        admin.current_user = None
        await admin.asave()

        # Foydalanuvchi holatini yangilash suxbat tugagandan keyingi message
        if user:
            user.status = 'completed'
            await user.asave()
            await bot.send_message(user.user_id, "Suhbat yakunlandi. Rahmat!")

        waiting_user = await TgUser.objects.filter(status='waiting').afirst()
        if waiting_user:
            admin.status = 'busy'
            admin.current_user = waiting_user
            await admin.asave()

            waiting_user.status = 'connected'
            await waiting_user.asave()

            await bot.send_message(admin.user_id, f"Yangi xabar {waiting_user.name} dan: {waiting_user.last_message}")
            await bot.send_message(waiting_user.user_id, "Sizning xabaringiz adminlarga yuborildi!")

        await bot.send_message(message.from_user.id, "Suhbat uchun rahmat, admin!")

    else:
        await message.reply("Hozirda hech qanday foydalanuvchi bilan bog'lanmadingiz.")

# /online komanda
@dp.message_handler(commands=['online'], admin=True)
async def set_online(message: types.Message):
    await set_admin_status(message.from_user.id, 'online')
    await message.reply("Siz online holatdasiz!")

    admin = await Admin.objects.aget(user_id=message.from_user.id)

    waiting_user = await TgUser.objects.filter(status='waiting').afirst()
    if waiting_user:
        admin.status = 'busy'
        admin.current_user = waiting_user
        await admin.asave()

        waiting_user.status = 'connected'
        await waiting_user.asave()

        await bot.send_message(admin.user_id, f"Yangi xabar {waiting_user.name} dan: {waiting_user.last_message}")
        await bot.send_message(waiting_user.user_id, "Sizning xabaringiz adminlarga yuborildi!")

# /offline komanda
@dp.message_handler(commands=['offline'], admin=True)
async def set_offline(message: types.Message):
    await set_admin_status(message.from_user.id, 'offline')
    await message.reply("Siz offline holatdasiz!")

@dp.callback_query_handler(lambda c: c.data in ["done", "not_done"], admin=True)
async def process_callback(callback_query: types.CallbackQuery):
    admin_id = callback_query.from_user.id
    outcome = "bajarildi" if callback_query.data == "done" else "bajarilmadi"

    # Administrator mavjudligini yangilang  joriy foydalanuvchini tozalash yani adminni bo'sh qilish
    admin = await Admin.objects.prefetch_related('current_user').aget(user_id=admin_id)
    user = admin.current_user

    admin.status = False
    admin.current_user = None
    await admin.asave()

    # Foydalanuvchi holatini yangilash suxbat tugagandan keyingi message
    if user:
        user.status = 'completed'
        await user.asave()
        await bot.send_message(user.user_id, "Suhbat yakunlandi. Rahmat!")

    waiting_user = await TgUser.objects.filter(status='waiting').afirst()
    if waiting_user:
        admin.status = True
        admin.current_user = waiting_user
        await admin.asave()

        waiting_user.status = 'connected'
        await waiting_user.asave()

        await bot.send_message(admin.user_id, f"Yangi xabar {waiting_user.name} dan: {waiting_user.last_message}")
        await bot.send_message(waiting_user.user_id, "Sizning xabaringiz adminlarga yuborildi!")

    await callback_query.message.edit_text(f"Siz {outcome} tanladingiz", reply_markup=None)
    # TODO: qanaqa tanlanganini bazaga yozib borish
    await callback_query.answer("Natija qayd qilindi!")

# Admin oziga tayinlangan foydalanuvchiga xabar yuboradi: admindan foydalanuvchiga message boradi
@dp.message_handler(content_types=types.ContentType.TEXT, admin=True)
async def admin_message_to_user(message: types.Message):
    admin = await Admin.objects.prefetch_related('current_user').aget(user_id=message.from_user.id)
    user = admin.current_user

    if user:
        await bot.send_message(user.user_id, message.text)
    else:
        await message.reply("Siz hozirda hech qanday foydalanuvchi bilan bog'lanmadingiz.")

# Foydalanuvchi xabarlarini boshqarish
@dp.message_handler(lambda message: not message.text.startswith('/'))
async def handle_user_message(message: types.Message):
    user = await TgUser.objects.aget(user_id=message.from_user.id)

    # Foydalanuvchi allaqachon administrator bilan suhbatda yoki yo'qligini tekshirish
    try:
        admin = await Admin.objects.prefetch_related('current_user').aget(current_user=user)
        await bot.send_message(admin.user_id, f"{user.name or user.user_id} dan xabar: {message.text}")
    except Admin.DoesNotExist:
        available_admin = await get_available_admin()

        if available_admin:
            # Foydalanuvchini adminga boglab, adminni band deb belgilash
            available_admin.status = True
            available_admin.current_user = user
            await available_admin.asave()

            user.status = 'connected'
            await user.asave()

            await bot.send_message(available_admin.user_id, f"Yangi xabar {user.name} dan: {message.text}")
            await message.reply("Sizning xabaringiz adminlarga yuborildi!")
        else:
            await message.reply("Hozirda bo'sh admin yo'q. Iltimos, kutib turing.")
            user.last_message = message.text
            user.status = 'waiting'
            await user.asave()

def start_bot():
    executor.start_polling(dp, skip_updates=True)

if __name__ == '__main__':
    start_bot()