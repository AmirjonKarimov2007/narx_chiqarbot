from data.config import ADMINS 
from filters.admins import IsAdmin,IsSuperAdmin
from loader import dp,db,bot
from aiogram import types
from aiogram.types import *
import requests
from requests.auth import HTTPBasicAuth
import json
import json
from aiogram import types
from loader import dp  
import re
from progress import print_barcode
from aiogram import types

import io
import json
import re
from PIL import Image
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton




async def get_product_by_barcode(user_input):
    try:
        with open('updated_data.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        return "Xatolik: updated_data.json fayli topilmadi!"
    except json.JSONDecodeError:
        return "Xatolik: JSON fayl noto‘g‘ri formatda!"

    found_products = []
    
    if user_input.isdigit():  
        for product in data["inventory"]:
            barcode = product.get("barcodes", "") or ""
            inventory_code = product.get("code", "") or ""  

            last_6_digits = barcode[-6:] if len(barcode) >= 6 else barcode
            inventory_digits = "".join(re.findall(r'\d+', inventory_code))

            if user_input in barcode or user_input == last_6_digits or user_input in inventory_digits:
                found_products.append(product)

    else:
        user_input_lower = user_input.lower()
        exact_match = []
        partial_match = []

        for product in data["inventory"]:
            article_code = (product.get("article_code", "") or "").lower()
            name = (product.get("name", "") or "").lower()

            if user_input_lower == article_code or user_input_lower == name:
                exact_match.append(product)
            elif user_input_lower in article_code or user_input_lower in name:
                partial_match.append(product)

        found_products.extend(exact_match)
        found_products.extend(partial_match)

    return found_products if found_products else None

# Matn orqali mahsulotni qidirish
@dp.message_handler(IsAdmin(), content_types=types.ContentType.TEXT, state='*')
async def get_text(message: types.Message):
    user_input = message.text.strip()
    tim = await message.answer(text="⏳")

    found_products = await get_product_by_barcode(user_input)

    if isinstance(found_products, str):  # Xatolik xabari bo'lsa
        await tim.delete()
        await message.answer(found_products)
        return

    if found_products:
        await tim.delete()
        response_text = "📌 Topilgan mahsulotlar:\n\n"
        for idx, product in enumerate(found_products, start=1):
            response_text += (
                f"🔹 <b>{idx}.</b>\n"
                f"🆔 Product ID: {product.get('product_id')}\n"
                f"🔢 Code: <code>{product.get('code')}</code>\n"
                f"📛 Name: {product.get('name')}\n"
                f"✏️ Short Name: <code>{product.get('short_name')}</code>\n"
                f"🛒 Article Code: {product.get('article_code') or 'Mavjud emas'}\n"
                f"📌 Barcodes: <code>{product.get('barcodes') or 'Mavjud emas'}</code>\n"
                f"💰 Narxlar:\n"
                f"📑 Sahifalar Soni:1\n"
                f"🇺🇿 UZS: {product.get('price_uzs', 'Noma’lum')}\n"
                f"🇺🇸 USD: {product.get('price_usd', 'Noma’lum')}\n\n"
            )

            barcode = str(product.get('barcodes'))
            price = product.get('price_uzs', 'Noma’lum')
            if isinstance(barcode, str) and '|' in barcode:
                barcode = barcode.split("|")[0]

            markup = InlineKeyboardMarkup(row_width=3)
            markup.insert(InlineKeyboardButton(text="➖", callback_data=f"remove_page"))
            markup.insert(InlineKeyboardButton(text="🖨Chiqarish✅", callback_data=f"narx_chiqar:{barcode}:narx"))
            markup.insert(InlineKeyboardButton(text="➕", callback_data=f"add_page"))
            markup.insert(InlineKeyboardButton(text="🏷Chiqarish✅", callback_data=f"narx_chiqar:{barcode}:barcode"))


            if price != "Noma'lum" and price is not None and price != "None":
                await message.answer(response_text,reply_markup=markup)
            
            response_text = ""
            if idx > 9:
                return

        if response_text:
            await message.answer(response_text, parse_mode="Markdown",reply_markup=markup)
    else:
        await message.answer("❌ Bunday mahsulot mavjud emas!")

from barcode_printer import print_barcode_barcode

@dp.callback_query_handler(IsAdmin(), text_contains='narx_chiqar:', state='*')
async def print_data(call: types.CallbackQuery):

    barcode = call.data.rsplit(":", 1)[1]
    type = call.data.rsplit(":")[2]
    caption = call.message.text
    # Kod
    code_match = re.search(r"🔢 Code: ([A-Za-z0-9\-/ ]+)", caption)
    code = code_match.group(1) if code_match else "Noma'lum"
    # Name
    name_match = re.search(r"📛 Name: (.+)", caption)
    name = name_match.group(1) if name_match else "Noma'lum"
    
    name_match = re.search(r"📛 Name: (.+)", caption)
    name = name_match.group(1) if name_match else "Noma'lum"
    # Barcodes
    barcode_match = re.search(r"📌 Barcodes: (\d+)", caption)
    barcode = barcode_match.group(1) if barcode_match else "Noma'lum"

    match = re.search(r"📑 Sahifalar Soni:(\d+)", caption)
    pages = match.group(1) 
    pages = int(pages)

    uzs_match = re.search(r"🇺🇿 UZS: (\d+)", caption)
    uzs_price = f"{int(uzs_match.group(1)):,}".replace(",", " ") if uzs_match else "Noma'lum"

    shortcode_match = re.search(r"🛒 Article Code: ([A-Za-z0-9\-]+)", caption)

    shortcode = shortcode_match.group(1) if shortcode_match else "Topilmadi"

    usd_match = re.search(r"🇺🇸 USD: ([\d.]+)", caption)
    usd_price = usd_match.group(1) if usd_match else "Noma'lum"
    try:
        if barcode=="Noma'lum":
            number = code.rsplit("/")
            barcode = number[1].rsplit(" ")[1]
    except:
        barcode="0000000000"
    if uzs_price == "Noma'lum" or uzs_price is None or uzs_price == "None":
        await call.answer("❌Mahsulot narxi nomalum.")

        return
    await call.answer("✅ Narx qog'ozi chiqarish muvaffiyatli boshlandi.")
    if type=='narx':
        a = await print_barcode(
            word_name=call.message.message_id,
            data_to_encode=barcode, 
            name=name, 
            price=uzs_price, 
            barcode_name=f'{call.id}.png', 
            usd_price=usd_price, 
            page=pages
        )
        if a:
            try:
                await call.answer("✅ Narx qog'ozi chiqarish muvaffiyatli boshlandi.")
            except:
                pass
        else:
            await call.answer("❌Narx chiqarib bo'lmadi.", show_alert=True)
    else:
        a = await print_barcode_barcode(
            word_name=call.message.message_id,
            data_to_encode=barcode, 
            name=shortcode, 
            barcode_name=f'{call.id}.png', 
            page=pages
        )
        if a:
            try:
                await call.answer("✅ Barcode qog'ozi chiqarish muvaffiyatli boshlandi.")
            except:
                pass
        else:
            await call.answer("❌Barcode chiqarib bo'lmadi.", show_alert=True)


    
        
@dp.callback_query_handler(IsAdmin(),text="add_page",state='*')
async def add_page(call: types.CallbackQuery):
    caption = call.message.text
    match = re.search(r"📑 Sahifalar Soni:(\d+)", caption)
    try:
        if match:
            pages = match.group(1) 
            pages = int(pages) + 2
            new_caption = re.sub(r"📑 Sahifalar Soni:\d+", f"📑 Sahifalar Soni:<b>{pages}</b>", caption)
            markup = call.message.reply_markup
            try:
                await call.answer("✅ Sahifalar soni qo'shildi")
            except:
                await call.answer("✅ Sahifalar soni 1taga yangilandi.")

            await call.message.edit_text(new_caption,reply_markup=markup)
        else:
            print("Sahifalar Soni topilmadi.")
    except Exception as e:
        print(e)
        pass

@dp.callback_query_handler(IsAdmin(),text="remove_page",state='*')
async def add_page(call: types.CallbackQuery):
    caption = call.message.text
    match = re.search(r"📑 Sahifalar Soni:(\d+)", caption)
    try:
        if match:
            pages = match.group(1) 
            if int(pages)>=1:
                pages = int(pages) - 1
                new_caption = re.sub(r"📑 Sahifalar Soni:\d+", f"📑 Sahifalar Soni:<b>{pages}</b>", caption)
                markup = call.message.reply_markup
                await call.answer("✅ Sahifalar soni 1taga olib tashlandi.")
                await call.message.edit_text(new_caption,reply_markup=markup)
            else:
                await call.answer("❌ Sahifalar soni olib tashlanmadi. maksimal kamayish miqdori 1ga teng")
        else:
            print("Sahifalar Soni topilmadi.")
    except Exception as e:
        return


from main import do_all
@dp.message_handler(IsAdmin(),commands='♻️yangilash',state='*')
async def new(message: types.Message):
    a = do_all()
    if a:
        await message.answer(text="✅Baza muvaffaqiyatli yangilandi")
    else:
        await message.answer(text="❌Baza yangilanmadi")

