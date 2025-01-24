import os
import win32com.client

def print_word_doc_multiple_copies(file_path, copies=1):
    if os.path.exists(file_path):
        try:
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            doc = word.Documents.Open(file_path)
            
            # Chop etiladigan nusxalar sonini belgilash
            doc.PrintOut(Copies=copies)
            
            doc.Close(False)
            word.Quit()
            print(f"Fayl {copies} nusxada chop etish uchun yuborildi.")
        except Exception as e:
            print(f"Chop etishda xatolik yuz berdi: {e}")
    else:
        print("Fayl topilmadi!")

# Fayl manzili va chop etiladigan nusxalar soni
file_path = r"C:\Users\user\Documents\narx_chiqarbot-main\bot\aaa.docx"
copies = 3  # Nechta nusxa chop etishni belgilaysiz
print_word_doc_multiple_copies(file_path, copies)
