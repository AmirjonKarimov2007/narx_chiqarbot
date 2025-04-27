import json
import json
import requests
from requests.auth import HTTPBasicAuth
def get_info_for_product():
    url = "https://smartup.online/b/anor/mxsx/mr/inventory$export"

    auth = HTTPBasicAuth('jamshidbek@falcon', '571++632')

    headers = {
        'filial_id': '5012602',
        'project_id': 'trade',
        'Content-Type': 'application/json'
    }

    data = {
        "code": "",
        "begin_created_on": "",
        "end_created_on": "",
        "begin_modified_on": "",
        "end_modified_on": ""
    }

    response = requests.get(url, json=data, auth=auth, headers=headers)

    if response.status_code == 200:
        print("So'rov muvaffaqiyatli amalga oshirildi.")
        
        # JSON ma'lumotlarini dekodlash
        response_dict = response.json()

        # Ma'lumotlarni tartibli JSON faylga yozish va Unicode belgilarni to'g'ri ko'rsatish
        with open('data.json', 'w', encoding='utf-8') as file:
            json.dump(response_dict, file, indent=4, ensure_ascii=False)
        return True
    else:
        print(f"So'rovda xatolik: {response.status_code}")
        return False
def get_price_for_product():
    url = "https://smartup.online/b/anor/mxs/mkf/product_price$export"

    auth = HTTPBasicAuth('jamshidbek@falcon', '571++632')

    headers = {
        'filial_id': '5012602',
        'project_code': 'trade',
    }

    data = {
        
    }

    response = requests.get(url, json=data, auth=auth, headers=headers)

    if response.status_code == 200:
        print("So'rov muvaffaqiyatli amalga oshirildi.")
        response_dict = response.json()
        with open('prices.json', 'w', encoding='utf-8') as file:
            json.dump(response_dict, file, indent=4, ensure_ascii=False)
        return True
    else:
        print(f"So'rovda xatolik: {response.status_code}")
        return False

def do_all():
    info = get_info_for_product()
    price = get_price_for_product()
    try:
        # 1. results.json faylini o'qib olamiz
        with open('results.json', 'r', encoding='utf-8') as results_file:
            results_data = json.load(results_file)
            print(f"results.json dan {len(results_data)} ta yozuv o'qildi")
        
        # URL larni id bo'yicha lug'atga joylash (yaxshiroq tekshiruv bilan)
        url_dict = {}
        missing_id_count = 0
        missing_url_count = 0
        empty_url_count = 0
        
        for item in results_data:
            # ID ni tekshiramiz
            if 'id' not in item:
                missing_id_count += 1
                continue
                
            # URL ni tekshiramiz
            if 'url' not in item:
                missing_url_count += 1
                continue
                
            url = item['url']
            if not url or url.lower() == 'null' or url.strip() == '':
                empty_url_count += 1
                continue
                
            # ID ni string formatiga keltiramiz
            url_dict[str(item['id'])] = url.strip()
        
        print(f"URL lug'atiga {len(url_dict)} ta element qo'shildi")
        print(f"ID si yo'q yozuvlar: {missing_id_count} ta")
        print(f"URL si yo'q yozuvlar: {missing_url_count} ta")
        print(f"Bo'sh URL lar: {empty_url_count} ta")
        
        # 2. Asosiy ma'lumotlarni o'qib olamiz
        with open('data.json', 'r', encoding='utf-8') as data_file:
            data = json.load(data_file)
            print(f"\ndata.json dan {len(data['inventory'])} ta mahsulot o'qildi")

        with open('prices.json', 'r', encoding='utf-8') as prices_file:
            prices = json.load(prices_file)
            print(f"prices.json dan {len(prices['inventory'])} ta narx o'qildi")

        # 3. Narxlarni tayyorlaymiz
        price_dict = {}
        for item in prices["inventory"]:
            price_uzs = item["price_type"][0]["price"] if len(item["price_type"]) > 0 else None
            price_usd = item["price_type"][1]["price"] if len(item["price_type"]) > 1 else None
            price_dict[item["inventory_code"]] = {
                "price_uzs": price_uzs,
                "price_usd": price_usd
            }

        # 4. Asosiy ma'lumotlarni yangilaymiz
        url_qoshildi = 0
        missing_product_id = 0
        
        for product in data["inventory"]:
            # product_id ni tekshiramiz
            product_id = str(product.get("product_id")) if "product_id" in product else None
            
            # Narxlarni qo'shamiz
            code = str(product.get("code", ""))
            if code in price_dict:
                product["price_uzs"] = price_dict[code]["price_uzs"]
                product["price_usd"] = price_dict[code]["price_usd"]
            else:
                product["price_uzs"] = None
                product["price_usd"] = None
            
            # URL ni qo'shamiz
            if product_id and product_id in url_dict:
                product["image_url"] = url_dict[product_id]
                url_qoshildi += 1
            else:
                product["image_url"] = None
                if not product_id:
                    missing_product_id += 1

        print(f"\nJami {url_qoshildi} ta mahsulotga URL qo'shildi")
        print(f"product_id si yo'q mahsulotlar: {missing_product_id} ta")
        
        # 5. Yangilangan ma'lumotlarni saqlaymiz
        with open('updated_data.json', 'w', encoding='utf-8') as updated_file:
            json.dump(data, updated_file, ensure_ascii=False, indent=4)
        
        print("\nMa'lumotlar muvaffaqiyatli yangilandi!")
        return True

    except FileNotFoundError as e:
        print(f"\nFayl topilmadi xatosi: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"\nJSON faylni o'qishda xatolik: {e}")
        return False
    except Exception as e:
        print(f"\nKutilmagan xatolik: {e}")
        return False

# Funktsiyani chaqiramiz
# do_all()