import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import os
import aiohttp
from tqdm import tqdm

df = pd.read_excel(r"C:\Users\alfatech.uz\Documents\narx_chiqarbot\bot\photoparser\downloads\ТМЦ.xlsx")
ids = df.iloc[:, 0].dropna().astype(str).tolist()
rasm_ids = df.iloc[:, 1].dropna().astype(str).tolist()

os.makedirs("rasmlar", exist_ok=True)

async def download_image(session, url, file_path):
    try:
        async with session.get(url) as resp:
            if resp.status == 200:
                with open(file_path, 'wb') as f:
                    f.write(await resp.read())
                return True
            return False
    except Exception as e:
        print(f"❌ Yuklab olishda xatolik ({url}): {e}")
        return False

async def process_image(context, session, id, rasm_id, pbar):
    try:
        page = await context.new_page()
        file_path = f"rasmlar/{id}.jpg"
        if os.path.exists(file_path):
            await page.close()
            pbar.update(1)
            return
            
        main_url = f"https://smartup.online/b/biruni/m:load_image_v2?_v=1&sha={rasm_id}"
        await page.goto(main_url, wait_until="domcontentloaded", timeout=30000)
        
        try:
            await page.wait_for_selector("img", timeout=10000)
            img = await page.query_selector("img")
            if not img:
                print(f"❌ Rasm topilmadi, qayta urinilmoqda: {rasm_id}")
                await page.goto(main_url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_selector("img", timeout=10000)
                img = await page.query_selector("img")
                if not img:
                    print(f"❌ Ikkinchi urinishda ham rasm topilmadi: {rasm_id}")
                    await page.close()
                    pbar.update(1)
                    return
            src = await img.get_attribute("src")
            if not src:
                print(f"❌ Rasm src topilmadi: {rasm_id}")
                await page.close()
                pbar.update(1)
                return
            if not src.startswith("http"):
                src = f"https://smartup.online{src}"
            success = await download_image(session, src, file_path)
            if success:
                print(f"✅ Saqlandi: {file_path}")
            else:
                print(f"❌ Yuklab bo'lmadi: {src}")
        except Exception as e:
            print(f"❌ Rasm yuklashda xatolik ({rasm_id}): {str(e)[:100]}...")
            try:
                await page.goto(main_url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_selector("img", timeout=10000)
                img = await page.query_selector("img")
                if img:
                    src = await img.get_attribute("src")
                    if src:
                        if not src.startswith("http"):
                            src = f"https://smartup.online{src}"
                        success = await download_image(session, src, file_path)
                        if success:
                            print(f"✅ (Qayta urinish) Saqlandi: {file_path}")
            except Exception as e2:
                print(f"❌ Qayta urinishda ham xatolik ({rasm_id}): {str(e2)[:100]}...")
    except Exception as e:
        print(f"❌ Umumiy xatolik ({rasm_id}): {str(e)[:100]}...")
    finally:
        await page.close()
        pbar.update(1)
async def run(playwright):  
    browser_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    user_data_dir = "user_dataa"

    context = await playwright.chromium.launch_persistent_context(
        user_data_dir,
        headless=False,
        executable_path=browser_path,
    )
    page = context.pages[0] if context.pages else await context.new_page()
    try:
        await page.goto("https://smartup.online/login.html", wait_until="domcontentloaded")
        await page.fill('#login', 'Jamshidbek@falcon')
        await page.fill('#password', '571++632')
        await page.click('#sign_in')
        await page.wait_for_load_state("networkidle", timeout=30000)
    except Exception as e:
        print(f"⚠️ Login jarayonida xatolik: {e}")

    connector = aiohttp.TCPConnector(limit_per_host=10)
    timeout = aiohttp.ClientTimeout(total=60)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        with tqdm(total=len(ids), desc="Yuklanmoqda") as pbar:
            tasks = []
            for id, rasm_id in zip(ids, rasm_ids):
                task = asyncio.create_task(process_image(context, session, id, rasm_id, pbar))
                tasks.append(task)
                if len(tasks) >= 5:
                    await asyncio.gather(*tasks)
                    tasks = []
            
            if tasks:
                await asyncio.gather(*tasks)

    await context.close()

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

