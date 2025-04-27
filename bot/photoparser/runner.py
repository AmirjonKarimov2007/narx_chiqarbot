from playwright.sync_api import sync_playwright
import pandas as pd
import os
import requests
from tqdm import tqdm
import json
from datetime import datetime
import ssl
from typing import List, Dict, Tuple, Optional
import time
import urllib3 
ssl_context = ssl.create_default_context()
ssl_context.options |= ssl.OP_NO_SSLv3
ssl_context.options |= ssl.OP_NO_SSLv2
ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  

class SyncImageDownloader:
    def __init__(self, excel_path: str):
        
        self.excel_path = excel_path
        self.results: List[Dict] = []
        self.processed_ids: set = set()
        
        self.config = {
            "results_file": "results.json",
            "max_retries": 3,
            "concurrent_tasks": 5,
            "login_url": "https://smartup.online/login.html",
            "base_url": "https://smartup.online",
            "browser_path": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "user_data_dir": "user_dataa",
            "credentials": {
                "login": "Jamshidbek@falcon",
                "password": "571++632"
            }
        }
        
        self.load_existing_results()

    def load_existing_results(self):
        if os.path.exists(self.config["results_file"]):
            try:
                with open(self.config["results_file"], 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.results = data if isinstance(data, list) else [data]
                self.processed_ids = {r['id'] for r in self.results if r.get('status') == 'success'}
            except (json.JSONDecodeError, KeyError):
                self.results = []

    def save_results(self):
        with open(self.config["results_file"], 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

    def get_ids_to_process(self) -> List[Tuple[str, str]]:
        df = pd.read_excel(self.excel_path)
        ids = df.iloc[:, 1].dropna().astype(str).tolist() 
        rasm_ids = df.iloc[:, 3].dropna().astype(str).tolist()  
        
        return [(id, rasm_id) for id, rasm_id in zip(ids, rasm_ids) 
                if id not in self.processed_ids]

    def download_image(self, url: str) -> Optional[bytes]:
        for attempt in range(self.config["max_retries"]):
            try:
                response = requests.get(url, verify=False)
                if response.status_code == 200:
                    return response.content
                if attempt < self.config["max_retries"] - 1:
                    time.sleep(1 * (attempt + 1))
            except Exception as e:
                if attempt == self.config["max_retries"] - 1:
                    print(f"❌ Download failed after {self.config['max_retries']} attempts ({url}): {e}")
        return None

    def login(self, page):
        try:
            page.goto(self.config["login_url"], wait_until="networkidle")
            page.fill('#login', self.config["credentials"]["login"])
            page.fill('#password', self.config["credentials"]["password"])
            page.click('#sign_in')
            page.wait_for_load_state("networkidle")
            print("✅ Login successful")
            return True
        except Exception as e:
            print(f"⚠️ Login error: {e}")
            return False

    def process_image(self, context, id: str, rasm_id: str, pbar: tqdm):
        result = {
            'id': id,
            'rasm_id': rasm_id,
            'url': None,
            'status': 'failed',
            'timestamp': datetime.now().isoformat(),
            'attempts': 0
        }

        for attempt in range(self.config["max_retries"]):
            result['attempts'] = attempt + 1
            page = None
            try:
                page = context.new_page()
                main_url = f"{self.config['base_url']}/b/biruni/m:load_image_v2?_v=1&sha={rasm_id}"
                
                page.goto(main_url, wait_until="domcontentloaded")
                
                try:
                    page.wait_for_selector("img", timeout=10000)
                    img = page.query_selector("img")
                    
                    if not img:
                        raise Exception("Image element not found")
                        
                    src = img.get_attribute("src")
                    if not src:
                        raise Exception("Image source not found")
                        
                    if not src.startswith("http"):
                        src = f"{self.config['base_url']}{src}"
                    
                    image_data = self.download_image(src)
                    if image_data:
                        result.update({
                            'url': src,
                            'status': 'success'
                        })
                        self.processed_ids.add(id)
                        print(f"✅ Success (ID: {id}, Attempt: {attempt + 1})")
                        break
                    else:
                        raise Exception("Image download failed")
                        
                except Exception as e:
                    if attempt == self.config["max_retries"] - 1:
                        result['status'] = f'error: {str(e)[:100]}'
                        print(f"❌ Failed after {self.config['max_retries']} attempts (ID: {id}): {e}")
                    else:
                        time.sleep(1 * (attempt + 1))
            except Exception as e:
                if attempt == self.config["max_retries"] - 1:
                    result['status'] = f'fatal_error: {str(e)[:100]}'
                    print(f"❌ Fatal error (ID: {id}): {e}")
            finally:
                if page:
                    page.close()

        self.results.append(result)
        self.save_results()
        pbar.update(1)

    def run(self):
        with sync_playwright() as playwright:
            context = playwright.chromium.launch_persistent_context(
                self.config["user_data_dir"],
                headless=True,
                executable_path=self.config["browser_path"],
            )

            page = context.pages[0] if context.pages else context.new_page()
            if not self.login(page):
                print("⚠️ Proceeding without login - may fail for protected content")
            
            ids_to_process = self.get_ids_to_process()
            
            if not ids_to_process:
                print("✅ All images have been successfully processed!")
                context.close()
                return

            print(f"ℹ️ Processing {len(ids_to_process)} images...")

            with tqdm(total=len(ids_to_process), desc="Processing images") as pbar:
                for id, rasm_id in ids_to_process:
                    self.process_image(context, id, rasm_id, pbar)

            context.close()

def download_images_sync(excel_path: str):
    """Main synchronous function to download all images"""
    downloader = SyncImageDownloader(excel_path)
    downloader.run()