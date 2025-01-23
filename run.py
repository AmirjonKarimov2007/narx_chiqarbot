import win32com.client

# Word ilovasini ishga tushurish
word = win32com.client.Dispatch("Word.Application")
word.Visible = False  # Word ilovasini foydalanuvchiga ko'rsatmaslik

# Word faylini to'g'ri yo'l bilan ochish
doc_path = r"C:\Users\user\Documents\narx_chiqarbot-main\bot\aaa.docx"  # Faylning to'liq yo'li
doc = word.Documents.Open(doc_path)

# Sahifa o'lchamlarini o'zgartirish (40mm x 30mm)
doc.PageSetup.PageWidth = 40  # 40mm
doc.PageSetup.PageHeight = 30  # 30mm

# Faylni chop etish
doc.PrintOut()

# Word ilovasini yopish
doc.Close()
word.Quit()
