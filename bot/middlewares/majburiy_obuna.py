from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from data.tekshirish import tekshir
from loader import bot, db
from filters import IsUser, IsSuperAdmin, IsGuest
from filters.admins import IsAdmin
import asyncpg
from data.config import ADMINS
import re
import html

async def kanallar():
    royxat = []
    ights = await db.select_channels()

    for x in ights:
        royxat.append(x[1])
    return royxat


class Asosiy(BaseMiddleware):
    async def on_pre_process_update(self, xabar: types.Update, data: dict):
        if xabar.message:
            if xabar.message.text:
                cleaned_text = re.sub(r"<[^>]*>", "", xabar.message.text)
                xabar.message.text = html.escape(cleaned_text.strip())
            user_id = xabar.message.from_user.id
            username = xabar.message.from_user.username
            first_name = xabar.message.from_user.first_name
            if str(xabar.message.chat.id).startswith('-'):
                return
            
        elif xabar.callback_query:
            user_id = xabar.callback_query.from_user.id
            username = xabar.callback_query.from_user.username
            first_name = xabar.callback_query.from_user.first_name

            if str(xabar.callback_query.message.chat.id).startswith('-'):
                return
        else:
            return
        try:
            await db.add_user(user_id=user_id,username=username, name=first_name)
        except asyncpg.exceptions.UniqueViolationError:
            await db.select_user(user_id=user_id)
        if str(user_id) in ADMINS:
            return
        matn = "<b>🤖 Botdan Foydalanish uchun kanallarga a'zo bo'lib. \n\n\"✅ Tekshirish\" tugmasini bosing!</b>"
        royxat = []
        dastlabki = True

        for k in await kanallar():
            holat = await tekshir(user_id=user_id, kanal_id=k)
            dastlabki *= holat
            kanals = await bot.get_chat(k)
            if not holat:
                link = await kanals.export_invite_link()
                button = [InlineKeyboardButton(text=f"{kanals.title}", url=f"{link}")]
                royxat.append(button)
        royxat.append([InlineKeyboardButton(text="✅ Tekshirish", callback_data="start")])
        if not dastlabki:
            if xabar.callback_query:
                data = xabar.callback_query.data
                if data=='start':
                    await xabar.callback_query.message.delete()
            try:
                await bot.send_message(chat_id=user_id, text=matn, disable_web_page_preview=True,
                                        reply_markup=InlineKeyboardMarkup(inline_keyboard=royxat))
            except:
                pass
            raise CancelHandler()
