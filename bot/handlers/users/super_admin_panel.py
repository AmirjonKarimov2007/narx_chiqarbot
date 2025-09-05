import time
import datetime
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
#Dasturchi @Mrgayratov kanla @Kingsofpy
from filters import IsSuperAdmin
from keyboards.inline.main_menu_super_admin import main_menu_for_super_admin, back_to_main_menu
from loader import dp, db, bot
from states.admin_state import SuperAdminState
# ADMIN TAYORLASH VA CHIQARISH QISMI UCHUN
@dp.callback_query_handler(IsSuperAdmin(), text="add_admin", state="*")
async def add_admin(call: types.CallbackQuery):
    await call.answer(cache_time=1)
    await call.message.edit_text("Yangi adminni chat IDsini yuboring...\n"
                                 "🆔 Admin ID raqamini olish uchun @userinfobot ga /start bosishini ayting",
                                 reply_markup=back_to_main_menu)
    await SuperAdminState.SUPER_ADMIN_ADD_ADMIN.set()

@dp.message_handler(IsSuperAdmin(), state=SuperAdminState.SUPER_ADMIN_ADD_ADMIN)
async def add_admin_method(message: types.Message, state: FSMContext):
    adminid =message.text
    try:
        royxat = await db.select_admins()
        # Dasturchi @Mrgayratov kanla @Kingsofpy
        try:
            if adminid not in royxat:
                user = await db.select_user(user_id=int(adminid))
                fullname = user[0]['name']
                await db.add_admin(user_id=int(adminid), full_name=fullname)
                await bot.send_message(chat_id=adminid,text="tabriklaymiz siz botimizda adminlik huquqini qolgan kiritidingiz /start bosing.")
                await message.answer("✅ Yangi admin muvaffaqiyatli qo'shildi!", reply_markup=main_menu_for_super_admin)
                await state.finish()

        except Exception as e:
            print(e)
            await message.answer("Adminni qo'shishda muammo yuz berdi.Admin botga start bosganligi yoki botni bloklamganligiga ishonch hozil qiling.")
            await state.finish()

    except Exception as e:
        await message.answer("❌ Xatolik yuz berdi!", reply_markup=main_menu_for_super_admin)
        await state.finish()
    
#Dasturchi @Mrgayratov kanla @Kingsofpy
@dp.message_handler(IsSuperAdmin(), state=SuperAdminState.SUPER_ADMIN_ADD_FULLNAME)
async def add_admin_method(message: types.Message,state: FSMContext):
    try:
        royxat = await db.select_admins()
        full_name = message.text
        await state.update_data({"full_name": full_name})
        malumot = await state.get_data()
        # Dasturchi @Mrgayratov kanla @Kingsofpy
        adminid = malumot.get("admin_id")
        full_name = malumot.get("full_name")
        try:
            if adminid not in royxat:
                await db.add_admin(user_id=int(adminid), full_name=full_name)
                await bot.send_message(chat_id=adminid,text="tabriklaymiz siz botimizda adminlik huquqini qolgan kiritidingiz /start bosing.")
                await message.answer("✅ Yangi admin muvaffaqiyatli qo'shildi!", reply_markup=main_menu_for_super_admin)
                await state.finish()

        except Exception as e:
            await message.answer("Adminni qo'shishda muammo yuz berdi.Admin botga start bosganligi yoki botni bloklamganligiga ishonch hozil qiling.")
            await state.finish()

    except Exception as e:
        await message.answer("❌ Xatolik yuz berdi!", reply_markup=main_menu_for_super_admin)
        await state.finish()

@dp.callback_query_handler(IsSuperAdmin(), text="del_admin", state="*")
async def show_admins(call: types.CallbackQuery):

    await call.answer(cache_time=2)
    admins = await db.select_all_admins()
    buttons = InlineKeyboardMarkup(row_width=1)
    for admin in admins:
        buttons.insert(InlineKeyboardButton(text=f"{admin[2]}", callback_data=f"admin:{admin[1]}"))
    # Dasturchi @Mrgayratov kanla @Kingsofpy
    buttons.add(InlineKeyboardButton(text="➕ Admin qo'shish", callback_data="add_admin"))
    buttons.insert(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_main_menu"))
    await call.message.edit_text(text="👤 Adminlar", reply_markup=buttons)
    
#Dasturchi @Mrgayratov kanla @Kingsofpy
@dp.callback_query_handler(IsSuperAdmin(), text_contains="admin:", state="*")
async def del_admin_method(call: types.CallbackQuery):
    await call.answer(cache_time=1)
    data = call.data.rsplit(":")
    admin = await db.select_all_admin(user_id=int(data[1]))
    for data in admin:
        text = f"Sizning ma'lumotlaringiz\n\n"
        text += f"<i>👤 Admin ismi :</i> <b>{data[2]}\n</b>"
        text += f"<i>🆔 Admin ID raqami :</i> <b>{data[1]}</b>"
        buttons = InlineKeyboardMarkup(row_width=1)

        buttons.insert(InlineKeyboardButton(text="❌ Admindan bo'shatish", callback_data=f"deladm:{data[1]}"))
        buttons.insert(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admins"))

        await call.message.edit_text(text=text, reply_markup=buttons)

@dp.callback_query_handler(IsSuperAdmin(), text_contains="deladm:", state="*")
async def del_admin_method(call: types.CallbackQuery):
    await call.answer(cache_time=1)
    data = call.data.rsplit(":")
    delete_orders = await db.delete_admin(admin_id=int(data[1]))
    await bot.send_message(chat_id=data[1],
                           text="Sizdan adminlik huquqi olindi")

    await call.answer("🗑 Admin o'chirildi !",show_alert=True)
    await call.message.edit_text("✅ Admin muvaffaqiyatli o'chirildi!", reply_markup=main_menu_for_super_admin)


# ADMIN TAYORLASH VA CHIQARISH QISMI UCHUN

# MAJBURIY OBUNA SOZLASH UCHUN
@dp.callback_query_handler(text = "add_channel")
async def add_channel(call: types.CallbackQuery):
    await SuperAdminState.SUPER_ADMIN_ADD_CHANNEL.set()
    await call.message.edit_text(text="<i><b>📛 Kanal usernamesini yoki ID sini kiriting: </b></i>")
    await call.message.edit_reply_markup(reply_markup=back_to_main_menu)


@dp.message_handler(state=SuperAdminState.SUPER_ADMIN_ADD_CHANNEL)
async def add_channel(message: types.Message, state: FSMContext):
    matn = message.text
    if matn.isdigit() or matn.startswith("@") or matn.startswith("-"):
        try:
            if await db.check_channel(channel=message.text):
                await message.answer("<i>❌Bu kanal qo'shilgan! Boshqa kanal qo'shing!</i>", reply_markup=back_to_main_menu)
            else:
                try:
                    deeellll = await bot.send_message(chat_id=message.text, text=".")
                    await bot.delete_message(chat_id=message.text, message_id=deeellll.message_id)
                    try:
                        await db.add_channel(channel=message.text)
                    except:
                        pass
                    await message.answer("<i><b>Channel succesfully added ✅</b></i>")
                    await message.answer("<i>Siz admin panelidasiz. 🧑‍💻</i>", reply_markup=main_menu_for_super_admin)
                    await state.finish()
                except:
                    await message.reply("""<i><b>
Bu kanalda admin emasman!⚙️
Yoki siz kiritgan username ga ega kanal mavjud emas! ❌
Kanalga admin qilib qaytadan urinib ko'ring yoki to'g'ri username kiriting.🔁
                    </b></i>""", reply_markup=back_to_main_menu)
        except Exception as err:
            await message.answer(f"Xatolik ketdi: {err}")
            await state.finish()
    else:
        await message.answer("Xato kiritdingiz.", reply_markup=back_to_main_menu)

@dp.callback_query_handler(text="del_channel")
async def channel_list(call: types.CallbackQuery):
    royxat = await db.select_channels()
    text = "🔰 Kanallar ro'yxati:\n\n"
    son = 0
    for o in royxat:
        son +=1
        text += f"{son}. {o[1]}\n💠 Username: {o[1]}\n\n"
    await call.message.edit_text(text=text)
    admins =await db.select_all_channels()
    buttons = InlineKeyboardMarkup(row_width=2)
    for admin in admins:
        buttons.insert(InlineKeyboardButton(text=f"{admin[1]}", callback_data=f"delchanel:{admin[1]}"))

    buttons.add(InlineKeyboardButton(text="➕ Kanal qo'shish", callback_data="add_channel"))
    buttons.insert(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_main_menu"))
    await call.message.edit_text(text=text, reply_markup=buttons)

@dp.callback_query_handler(IsSuperAdmin(), text_contains="delchanel:", state="*")
async def del_admin_method(call: types.CallbackQuery):
    await call.answer(cache_time=1)
    data = call.data.rsplit(":")
    delete_orders = await db.delete_channel(channel=data[1])
    await call.answer("🗑 Channel o'chirildi !",show_alert=True)
    await call.message.edit_text("✅ Kanal muvaffaqiyatli o'chirildi!", reply_markup=main_menu_for_super_admin)

# ADMINLARNI KORISH
@dp.callback_query_handler(text="admins")
async def channel_list(call: types.CallbackQuery):
    royxat = await db.select_admins()
    text = "🔰 Adminlar ro'yxati:\n\n"
    son = 0
    for o in royxat:
        son +=1
        text += f"{son}. {o[2]}\nID : {o[1]}💠 Ismi: {o[2]}\n\n"
    await call.message.edit_text(text=text)

    buttons = InlineKeyboardMarkup(row_width=1)
    buttons.insert(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_main_menu"))
    await call.message.edit_text(text=text, reply_markup=buttons)
# ADMINLARNI KORISH

# STATISKA KORISH UCHUN
import pytz
import datetime

@dp.callback_query_handler(IsSuperAdmin(), text="statistics")
async def stat(call: types.CallbackQuery):
    uzbekistan_tz = pytz.timezone('Asia/Tashkent')
    datas = datetime.datetime.now(uzbekistan_tz)
    yil_oy_kun = datas.date()
    soat_minut_sekund = f"{datas.hour}:{datas.minute}:{datas.second}"

    daily_stat = await db.stat(timeframe="daily")
    weekly_stat = await db.stat(timeframe="weekly")
    monthly_stat = await db.stat(timeframe="monthly")
    all_users = await db.stat(timeframe="all_users")

    stat_message = f"<b>👥 Bot foydalanuvchilari soni:</b>\n"
    stat_message += f"<b>♻️ Jami obunachilar: {all_users} nafar</b>\n"
    stat_message += f"<b>📅 Kunlik: {daily_stat} nafar</b>\n"
    stat_message += f"<b>📆 Haftalik: {weekly_stat} nafar</b>\n"
    stat_message += f"<b>📅 Oylik: {monthly_stat} nafar</b>\n"
    stat_message += f"<b>⏰ Soat: {soat_minut_sekund}</b>\n"
    stat_message += f"<b>📆 Sana: {yil_oy_kun}</b>"

    inline_button = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("◀️ Orqaga", callback_data="back_to_main_menu")
    )

    await call.message.delete()
    await call.message.answer(stat_message, reply_markup=inline_button)

# ADMINGA SEND FUNC
@dp.callback_query_handler(IsSuperAdmin(), text="send_message_to_admins", state="*")
async def send_advertisement(call: types.CallbackQuery):
    await call.answer(cache_time=1)
    await call.message.edit_text("Adminlarga Reklamani yuboring...\n"
                                 "Yoki bekor qilish tugmasini bosing", reply_markup=back_to_main_menu)
    await SuperAdminState.SUPER_ADMIN_SEND_MESSAGE_TO_ADMINS.set()


@dp.message_handler(IsSuperAdmin(), state=SuperAdminState.SUPER_ADMIN_SEND_MESSAGE_TO_ADMINS,content_types=types.ContentTypes.ANY)
async def send_advertisement_to_user(message: types.Message, state: FSMContext):
    users = await db.stat()
    admin_list = await db.select_all_admins()
    
    black_list = 0
    white_list = 0
    seriy_list = 0
    datas = datetime.datetime.now()
    boshlanish_vaqti = f"{datas.hour}:{datas.minute}:{datas.second}"

    start_msg = await message.answer(f"📢 Reklama jo'natish boshlandi...\n"
                                      f"📊 Adminlar soni: {users} ta\n"
                                      f"🕒 Kuting...\n")

    semaphore = Semaphore(20)  # Har bir vaqtda 20 ta xabar yuborish bilan cheklov
    errors = []

    async def send_message(user_id):
        nonlocal black_list, white_list,seriy_list
        async with semaphore:
            try:
                await bot.copy_message(chat_id=user_id, from_chat_id=message.chat.id,
                                       message_id=message.message_id, reply_markup=message.reply_markup)
                white_list += 1
            except Exception as e:
                if "bot was blocked by the user" in str(e):
                    black_list += 1
                else:
                    seriy_list += 1
                errors.append((user_id, str(e)))

    # Foydalanuvchilarga parallel xabar yuborish
    tasks = [send_message(admin['user_id']) for admin in admin_list]

    await gather(*tasks)

    data = datetime.datetime.now()
    tugash_vaqti = f"{data.hour}:{data.minute}:{data.second}"
    
    text = (f'<b>✅ Reklama muvaffaqiyatli yuborildi!</b>\n\n'
            f'<b>⏰ Boshlangan vaqt: {boshlanish_vaqti}</b>\n'
            f'<b>👥 Yuborilgan adminlar soni: {white_list}</b>\n'
            f'<b>🚫 Botni Bloklagan adminlar soni: {black_list}</b>\n'
            f'<b>🔖 Reklama Yuborilmagan adminlar soni: {seriy_list}</b>\n'
            f'<b>🏁 Tugash vaqti: {tugash_vaqti}</b>\n')

    await bot.delete_message(chat_id=start_msg.chat.id, message_id=start_msg.message_id)
    await message.answer(text, reply_markup=main_menu_for_super_admin)
    await state.finish()


# ====================Foydalanuvchliar uchun SEND SUNC  ============================
@dp.callback_query_handler(IsSuperAdmin(), text="send_advertisement", state="*")
async def send_advertisement(call: types.CallbackQuery):
    await call.answer(cache_time=1)
    await call.message.edit_text("Reklamani yuboring...\n"
                                 "Yoki bekor qilish tugmasini bosing", reply_markup=back_to_main_menu)
    await SuperAdminState.SUPER_ADMIN_STATE_GET_ADVERTISEMENT.set()

from asyncio import Semaphore,gather
@dp.message_handler(IsSuperAdmin(), state=SuperAdminState.SUPER_ADMIN_STATE_GET_ADVERTISEMENT,
                    content_types=types.ContentTypes.ANY)
async def send_advertisement_to_user(message: types.Message, state: FSMContext):
    users = await db.stat()
    user_list = await db.select_all_users()
    
    black_list = 0
    white_list = 0
    seriy_list = 0
    datas = datetime.datetime.now()
    boshlanish_vaqti = f"{datas.hour}:{datas.minute}:{datas.second}"

    start_msg = await message.answer(f"📢 Reklama jo'natish boshlandi...\n"
                                      f"📊 Foydalanuvchilar soni: {users} ta\n"
                                      f"🕒 Kuting...\n")

    semaphore = Semaphore(20)  # Har bir vaqtda 20 ta xabar yuborish bilan cheklov
    errors = []

    async def send_message(user_id):
        nonlocal black_list, white_list,seriy_list
        async with semaphore:
            try:
                await bot.copy_message(chat_id=user_id, from_chat_id=message.chat.id,
                                       message_id=message.message_id, reply_markup=message.reply_markup)
                white_list += 1
            except Exception as e:
                if "bot was blocked by the user" in str(e):
                    black_list += 1
                else:
                    seriy_list += 1
                errors.append((user_id, str(e)))

    # Foydalanuvchilarga parallel xabar yuborish
    tasks = [send_message(user['user_id']) for user in user_list]
    await gather(*tasks)

    data = datetime.datetime.now()
    tugash_vaqti = f"{data.hour}:{data.minute}:{data.second}"
    
    text = (f'<b>✅ Reklama muvaffaqiyatli yuborildi!</b>\n\n'
            f'<b>⏰ Boshlangan vaqt: {boshlanish_vaqti}</b>\n'
            f'<b>👥 Yuborilgan foydalanuvchilar soni: {white_list}</b>\n'
            f'<b>🚫 Botni Bloklagan foydalanuvchilar soni: {black_list}</b>\n'
            f'<b>🔖 Reklama Yuborilmagan foydalanuvchilar soni: {seriy_list}</b>\n'
            f'<b>🏁 Tugash vaqti: {tugash_vaqti}</b>\n')

    await bot.delete_message(chat_id=start_msg.chat.id, message_id=start_msg.message_id)
    await message.answer(text, reply_markup=main_menu_for_super_admin)
    await state.finish()


# ==================== Foydalanuvchliar uchun SEND SUNC TUGADI ============================


#<><><><> ===================Post qo'shish=====================<><><><>
@dp.callback_query_handler(IsSuperAdmin(), text="add_post", state="*")
async def add_post(call: types.CallbackQuery):
    await call.answer(cache_time=1)
    await call.message.edit_text("rasm va textdan iborat post yuboring...\n"
                                 "Yoki Orqaga tugmasini bosing", reply_markup=back_to_main_menu)
    
    await SuperAdminState.SUPER_ADMIN_ADD_POST.set()

from typing import List, Union
# @dp.message_handler(IsSuperAdmin(),state=SuperAdminState.SUPER_ADMIN_ADD_POST,
#                     content_types=types.ContentTypes.ANY)
# @dp.message_handler(is_media_group=True, content_types=types.ContentType.ANY)
# async def add_post_to_social(message: types.Message,state: FSMContext):

#     file = message.content_type
#     niamdir = message.content_type
#     users =  await db.stat()
#     admin_id = message.from_user.id
#     caption = message.caption
    
#     caption_entities = message.caption_entities
#     urls = []

#     for caption_entry in caption_entities:
#         if caption_entry.type == 'text_link':
#             urls.append(caption_entry.url)
#     users = str(users)
#     for x in users:
#         user = await db.select_all_users()
#         for i in user:
#             user_id = i['user_id']
#             try:
#                 await bot.copy_message(
#                     chat_id=user_id,
#                     from_chat_id=message.from_user.id,
#                     message_id=message.message_id,
#                     reply_markup=message.reply_markup
#                 )

#                 time.sleep(0.5)
#             except Exception as e:
#                 await bot.send_message(admin_id, e)

#         # await message.answer("✅ Reklama muvaffaqiyatli yuborildi!", reply_markup=main_menu_for_super_admin)
    
#     channels = await db.channel_stat()
#     channels = str(channels)

#     for y in channels:

#         await message.answer(f"📢 Reklama jo'natish boshlandi...\n"
#                              f"📊 Foydalanuvchilar soni: {x} ta\n"
#                              f"📌 Kanallar soni: {y} ta\n"
#                              f"🕒 Kuting...\n")
#         channels = await db.select_all_channels()
#         for i in channels:
#             channel=i['channel']
#             channel_info = await bot.get_chat(channel)
#             channel = channel_info.id
#             try:
#                 await bot.copy_message(chat_id=channel, from_chat_id=admin_id,
#                                        message_id= message.message_id,reply_markup=message.reply_markup, parse_mode=types.ParseMode.HTML)
                
                
#                 time.sleep(0.5)
#             except Exception as e:
#                 await bot.send_message(admin_id,e)
#         await message.answer("✅ Reklama muvaffaqiyatli yuborildi!", reply_markup=main_menu_for_super_admin)
# # =================== ADD POST ON INSTAGRAM =================================
#         file_type = message.content_type
#         if file_type=='photo':
#             photo = message.photo[-1]
#             file_id = photo.file_id
#             caption = f"\n{message.caption}\n"
#             rasm = await upload_instagram(content_type=file_type,file_id=file_id,photo=photo,caption=caption)


#     await state.finish()


# # # # # # # # # # # # # # # # # # # # 
# # #TUGMA QO'SHISH UCHUN HANDLER # #  # # # # 
# # # # # # # # # # # # # # # # # # # 

@dp.callback_query_handler(IsSuperAdmin(),text_contains="add_keyboard")
async def add_keyboard(call: types.CallbackQuery):
    await call.answer(cache_time=1)
    try:
        await call.message.edit_text("Tugma qo'shish uchun tugmaning nomini  yuboring...\n"
                                 "Yoki bekor qilish tugmasini bosing", reply_markup=back_to_main_menu)
        await SuperAdminState.SUPER_ADMIN_UPDATE_GET_KEYBOARD_NAME.set()
    except:
        pass

@dp.message_handler(IsSuperAdmin(),content_types=types.ContentType.TEXT,state=SuperAdminState.SUPER_ADMIN_UPDATE_GET_KEYBOARD_NAME)
async def get_name(message: types.Message,state:FSMContext):
    keyboard_name = message.text
    try:
        await state.update_data({"keybaord_name":{keyboard_name}})
        await message.answer("Yaxshi endi tugma uchun link yuboring.")
        await SuperAdminState.SUPER_ADMIN_UPDATE_GET_KEYBOARD_URL.set()
    except:
        await message.answer(text="Tugma qo'shish bekor qilindi,qaytadan urining.")
        await state.finish()

import re

@dp.message_handler(IsSuperAdmin(),content_types=types.ContentType.TEXT,state=SuperAdminState.SUPER_ADMIN_UPDATE_GET_KEYBOARD_URL)
async def get_link(message: types.Message,state:FSMContext):
    link = message.text
    # Link validatsiyasi
    link_pattern = re.compile(
        r"^(https?://)?(www\.)?(t\.me|telegram\.me)/[a-zA-Z0-9_]+$"
    )
    try:
        if link_pattern.match(link):
            try:
                await state.update_data({"keyboard_link": link})
                await message.answer("Yaxshi yubormoqchi bo'lgan postingizni yuboring.")
                await SuperAdminState.SUPER_ADMIN_UPDATE_ADD_KEYBOARD.set()   
            except Exception as e:
                await message.answer(f"Tugma qo'shishda xatolik yuz berdi: {e}")
                await state.finish()
        else:
            await message.answer(
                "Noto'g'ri link format kiritildi. Qaytadan urinib ko'ring.\nMasalan: https://example.com yoki www.example.com"
            )
    except Exception as e:
        print(e)
        await state.finish()



@dp.message_handler(IsSuperAdmin(),content_types=types.ContentType.ANY,state=SuperAdminState.SUPER_ADMIN_UPDATE_ADD_KEYBOARD)
async def send_keyboard(message: types.Message,state:FSMContext):
    try:
        royxat = await db.select_channels()
        text = "🔰 Kanalni Tanlang:\n\n"
        son = 0
        data = await state.get_data()
        name = data.get("keybaord_name")
        name = list(name)[0]
        link = data.get("keyboard_link")
        for o in royxat:
            son +=1
            text += f"{son}. {o[1]}\n💠 Username: {o[1]}\n\n"
        channels =await db.select_all_channels()
        buttons = InlineKeyboardMarkup(row_width=1)
        for channel in channels:
            buttons.insert(InlineKeyboardButton(text=f"{channel[1]}", callback_data=f"channel_send:{channel[1]}:{message.message_id}:{name}"))

        buttons.insert(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_main_menu"))
        await message.answer(text=text, reply_markup=buttons)
        await SuperAdminState.SUPER_ADMIN_UPDATE_SEND_CHANNEL.set()   
    except Exception as e:
        await message.answer(f"Tugma qo'shishda xatolik yuz berdi: {e}")
        await state.finish()

    

@dp.callback_query_handler(IsSuperAdmin(),text_contains="channel_send:",state=SuperAdminState.SUPER_ADMIN_UPDATE_SEND_CHANNEL)
async def send_channel(call: types.CallbackQuery,state: FSMContext):
    await call.answer(cache_time=1)
    channel_username = call.data.rsplit(":")[1]
    message_id = call.data.rsplit(":")[2]
    info = await state.get_data()
    link = info.get("keyboard_link")
    name = call.data.rsplit(":")[3]
    markup =  InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(text=name,url=link))
    try:
        await bot.copy_message(chat_id=channel_username,
                           from_chat_id=call.from_user.id,message_id=message_id,reply_markup=markup)
        await call.message.edit_text(text="✅Kanalga post muvaffaqiyatli yuborildi.",reply_markup=main_menu_for_super_admin)
        await state.finish()
    except Exception as e:
        await call.message.answer(f"xatolik:{e}")





# Bosh menu
@dp.callback_query_handler(IsSuperAdmin(), text="back_to_main_menu", state="*")
async def back_to_main_menu_method(call: types.CallbackQuery,state: FSMContext):
    await call.answer(cache_time=1)
    await call.message.edit_text(text="👨‍💻 Bosh menyu", reply_markup=main_menu_for_super_admin)
    await state.finish()

