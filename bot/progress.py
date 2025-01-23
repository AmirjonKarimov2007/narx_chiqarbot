import os
import asyncio
import win32print
import win32api
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
import barcode
from barcode.writer import ImageWriter
import pyautogui

def generate_barcode(data, filename='barcode.png'):
    """ Shtrixkod yaratish va saqlash """
    barcode_class = barcode.get_barcode_class('code128')
    barcode_obj = barcode_class(data, writer=ImageWriter())
    return barcode_obj.save(filename, options={
        "module_height": 15.0,
        "font_size": 10,
        "dpi": 650,
        "text_distance": 5.0,
    })

async def update_document(template_path, new_file_path, name, price, usd_price, barcode_image_path):
    """ Hujjatni yangilash va saqlash """
    doc = await asyncio.to_thread(Document, template_path)
    for para in doc.paragraphs:
        if "Mahsulotnomi" in para.text:
            para.text = ""
            run = para.add_run(f"{name} / {usd_price}")
            run.font.size = Pt(7)
            run.bold = True
            para.paragraph_format.left_indent = Cm(0.10)
        if "50000" in para.text:
            para.text = ""
            run = para.add_run(f"   {price} сум")
            run.font.size = Pt(14)
            run.bold = True
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    if os.path.exists(barcode_image_path):
        paragraph = doc.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = paragraph.add_run()
        run.add_picture(barcode_image_path, width=Cm(3), height=Cm(1))
    
    os.makedirs("documents", exist_ok=True)
    save_path = os.path.join("documents", new_file_path)
    await asyncio.to_thread(doc.save, save_path)
    return save_path

import time
async def print_document(file_path, pages=1):
    printer_name = win32print.GetDefaultPrinter()
    for _ in range(pages):
        pyautogui.press('enter')
        await asyncio.to_thread(win32api.ShellExecute, 0, "print", file_path, f'/d:"{printer_name}"', ".", 0)
        time.sleep(3)
        pyautogui.press('enter')

async def print_barcode(word_name, data_to_encode, name, price, usd_price, barcode_name='barcode.png', page=1):
    try:
        new_file_path = f'{word_name}.docx'
        barcode_image_path = await asyncio.to_thread(generate_barcode, data_to_encode, barcode_name)
        saved_file_path = await update_document('aaa.docx', new_file_path, name, price, usd_price, barcode_image_path)
        
        await print_document(saved_file_path, page)
        time.sleep(1)  
        os.remove(f"{barcode_name}.png.png")
        return True
    except Exception as e:
        if os.path.exists(f"{barcode_name}.png"):
            os.remove(f"{barcode_name}.png")
        return False
