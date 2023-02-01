import requests
import sys
import random
from utils import *
import json
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor
from itertools import chain
from ping import ping

def get_details(store,product_id,token,proxy=""):
    time.sleep(random.randrange(1,10))
    try:
        choice = random.choice([False,False,True])
        if choice:
            token = get_token(type="new",proxy=proxy)
            if not token:
                print(token)

        params = {
            'enableSameDayDelivery': 'false',
            'role': '',
            'showAtc': 'true',
            'storeNumber': store["id"],
            'carouselBadge': 'false',
            'customerType': 'REGULAR',
            'enableLiftOffRecs': 'true',
            'supportBuyAgain': 'true',
            # 'purchaseFromCatalog': 'false',
            'enableFulfillmentV2': 'true',
            'enableNewBadges': 'true',
            'organizationId': '',
            'promotionId': '',
            'associations': 'pd',
            'promoType': 'unknown',
        }
        
        headers = {
            'Host': 'api-prod.lowes.com',
            'accept-language': 'en-US,en;q=0.9',
            'accept': '*/*',
            f'authorization': f'Bearer {token}',
            'x-lowes-originating-server-hostname': 'LowesiOSConsumer',
            'device-idiom': 'phone',
            'os': 'ios',
            'isguestuser': 'true',
            'x-api-version': 'v3',
            'pagecontext': 'shop',
            'x-lowes-uuid': f'0f7ce92d-8170-4df4-9e83-{generate_sensor_data(type="random_string")}',
            'user-agent': 'lowesMobileApp/23.1.3 (iPhone; iOS 16.2.0)',
            'x-acf-sensor-data': generate_sensor_data(type="sensor_data"),

        }
        
        response = requests.get(
            f'https://api-prod.lowes.com/v1/mobile-experience/product-detail/product/{product_id}',
            params=params,
            headers=headers,
            proxies=proxy
        )

        data = response.json()
        return True,data
    except Exception as error:
        print(f"{error} from here second")
        return False,error


def check_prices(stores,product_id,token,proxy):
    now = str(datetime.now()).split(" ")[0]
    prices = []
    for store in stores:
        try:
            data = get_details(store,product_id,token,proxy=proxy)
            data = data[1] if data[0] else data[0]
            if not data:
                continue
            price = data["product"]["productPrice"]
            total = data["product"]["itemInventory"]["totalQty"] if "totalQty" in data["product"]["itemInventory"].keys() else 0
            status = data["product"]["itemInventory"]["inventoryDescription"]
            inventory = {"total":total,"status":status}
            prices.append({
                            "store_name":store["store_name"],
                            "store_id":store["id"],
                            "prices":[
                                {
                                    "date": now,
                                    "price":price,
                                    "inventory":inventory
                                },
                            ]
                            })
            print(f"{price} from store {store['id']} | item {product_id}")
        except Exception as error:
            print(error)
    return prices


def get_products(cat):
    proxy = {"http":"http://user-r4z:password1@all.smartproxy.com:10000"}
    try:
        stores = []
        with open("./store_ids.json","r",encoding="utf-8") as stores_data:
            stores += json.load(stores_data)["data"]
        store_lists = list(divide_chunks(stores,10))
        
        counter = 0
        items = {}
        while counter < cat["productCount"]:
            try:
                token = get_token(type="new",proxy=proxy)
                store = random.choice(stores)
                with open("api/results_master.json","r+",encoding="utf-8") as file:
                    file_data = json.load(file)
                    now = str(datetime.now()).split(" ")[0]

                    headers = {
                    'Host': 'api-prod.lowes.com',
                    'accept': '*/*',
                    'authorization': f'Bearer {token}',
                    'x-lowes-originating-server-hostname': 'LowesiOSConsumer',
                    'device-idiom': 'phone',
                    'os': 'ios',
                    'isguestuser': 'true',
                    'x-lowes-uuid': f'9d253f2c-9dda-4e3b-8120-{generate_sensor_data(type="random_string")}',
                    'x-api-version': 'v5',
                    'user-agent': 'lowesMobileApp/23.1.3 (iPhone; iOS 16.2.0)',
                    'accept-language': 'en-US,en;q=0.9',
                    }
                    
                    offset = 0
                    adjustedNextOffset = 0

                    if counter == 1:
                        adjustedNextOffset = 28
                        offset += 30
                    elif counter == 0:
                        pass
                    else:
                        adjustedNextOffset+=30
                        offset += 30   
                    counter+=1 

                    params = {
                        'freeDelivery': 'false',
                        'allowATCforPCR': 'true',
                        'freeDeliveryEnabled': 'true',
                        'isServerLoad': 'true',
                        'nValue': cat["nValue"],
                        'enableNewBadges': 'false',
                        'searchType': 'nValue',
                        'maxResults': '30',
                        'showIntSwatches': 'true',
                        'contractIds': '',
                        'offset': f'{offset}',
                        'showAtc': 'true',
                        'includeCollection': 'true',
                        'supportBuyAgain': 'false',
                        'adjustedNextOffset': f'{adjustedNextOffset}',
                        'inStock': 'false',
                        'rollUpVariants': 'true',
                        'channelType': 'IPHONE',
                        'customerType': 'REGULAR',
                    }
                    
                    response = requests.get(
                        'https://api-prod.lowes.com/v1/mobile-experience/search/items',
                        params=params,
                        headers=headers,
                        proxies=proxy
                    )

                    data = response.json()
                    print(data)
                    data = data['itemList']# array

                    for item in data:
                        try:
                            data = get_details(store,item["itemId"],token,proxy=proxy)
                            data = data[1] if data[0] else data[0]
                            assert data is not False
                            
                            barcode = data["product"]["barcode"]
                            price = data["product"]["productPrice"]
                            
                            total = data["product"]["itemInventory"]["totalQty"] if "totalQty" in data["product"]["itemInventory"].keys() else 0
                            status = data["product"]["itemInventory"]["inventoryDescription"]
                            inventory = {"total":total,"status":status}

                            excape = False
                            for result in file_data["data"]:
                                if result["itemId"] == item["itemId"]:
                                    old_price = result["product_price"]["displayPrice"]
                                    excape = True
                                    lowest_price = result["product_price"]["displayPrice"]
                                
                                    tokens = [token for _ in range(len(store_lists))]
                                    ids = [item["itemId"] for _ in range(len(store_lists))]
                                    proxies =[proxy for _ in range(len(store_lists))]
                                    locations = []
                                    with ThreadPoolExecutor(len(store_lists)) as executor:
                                        prices = executor.map(check_prices,store_lists,ids,tokens,proxies)
                                        for price in prices:
                                            for m_price in price:
                                                print(m_price)
                                                this_price = m_price["prices"][0]["price"]["displayPrice"]
                                                if this_price < lowest_price:
                                                    print(f"lowest_price: {lowest_price} | new_lowest: {this_price}")
                                                    lowest_price = this_price
                                                    result["product_price"] = m_price["prices"][0]["price"]
                                                    result["inventory"] = m_price["prices"][0]["inventory"]
                                                    locations.append(m_price)
                                    
                                            
                                                new_store = False
                                                for history in result["price_history"]:
                                                    if history["store_name"] == m_price["store_name"]:
                                                        history["prices"].append(m_price["prices"][0])
                                                        new_store = False
                                                        break
                                                    new_store = True
                                                if new_store:
                                                    continue
                                                result["price_history"].append(m_price)

                                        if lowest_price < old_price:
                                            locations = [s["store_id"] for s in locations if lowest_price == s["prices"][0]["price"]["displayPrice"]]
                                            title = f'{result["itemInfo"]["brand"]} | {result["itemInfo"]["description"]}'
                                            sale = lowest_price
                                            original = result["product_price"]["wasPrice"] if "wasPrice" in result["product_price"] else old_price
                                            discount = result["product_price"]["savings"] if "savings" in m_price["prices"][0]["price"] else int(((original - sale) * 100) / original)
                                            thumbnail = result["imageUrl"]
                                            link = f'https://www.lowes.com{result["shareableLink"]}'
                                            upc = result["barcode"] 
                                            qauntity = result["inventory"]["total"]
                                            message = "Out of stock" if qauntity < 1 else "In stock"
                                            zip = locations[0]
                                            locations = str(locations).replace("[","").replace("]","").replace("'","") if len(locations) < 10 else "Global"
                                            sale = str(sale)
                                            original = str(original)
                                            discount = str(discount).replace("%","")
                                            thumbnail = str(thumbnail)
                                            qauntity = str(qauntity)
                                            ping(sale, original, discount, thumbnail, title, link, locations,zip,upc,qauntity,message)
                                                
                                    break

                            if excape:
                                continue

                            item["barcode"] = barcode
                            item["product_price"] = price


                            item["inventory"] = inventory
                            item["price_history"] = [
                                {
                                    "store_name":store["store_name"],
                                    "store_id":store["id"],
                                    "prices":[
                                        {
                                            "date": now,
                                            "price":price,
                                            "inventory":inventory
                                        },
                                    ]
                                }
                            ]
                            old_price = item["product_price"]["displayPrice"]
                            lowest_price = float(item["product_price"]["displayPrice"]) * 2
                        
                            tokens = [token for _ in range(len(store_lists))]
                            ids = [item["itemId"] for _ in range(len(store_lists))]
                            proxies =[proxy for _ in range(len(store_lists))]
                            locations = []
                            with ThreadPoolExecutor(len(store_lists)) as executor:
                                prices = executor.map(check_prices,store_lists,ids,tokens,proxies)
                                for price in prices:
                                    for m_price in price:
                                        print(m_price)
                                        this_price = m_price["prices"][0]["price"]["displayPrice"]
                                        if this_price < lowest_price:
                                            print(f"lowest_price: {lowest_price} | new_lowest: {this_price}")
                                            lowest_price = this_price
                                            item["product_price"] = m_price["prices"][0]["price"]
                                            item["inventory"] = m_price["prices"][0]["inventory"]
                                            locations.append(m_price)
                                        result["price_history"].append(m_price)
                                        if this_price >= old_price:
                                            old_price = this_price
                                if lowest_price < old_price:
                                    locations = [s["store_id"] for s in locations if lowest_price == s["prices"][0]["price"]["displayPrice"]]
                                    title = f'{item["itemInfo"]["brand"]} | {item["itemInfo"]["description"]}'
                                    sale = lowest_price
                                    original = item["product_price"]["wasPrice"] if "wasPrice" in item["product_price"] else old_price
                                    discount = item["product_price"]["savings"] if "savings" in m_price["prices"][0]["price"] else int(((original - sale) * 100) / original)
                                    thumbnail = item["imageUrl"]
                                    link = f'https://www.lowes.com{item["shareableLink"]}'
                                    upc = item["barcode"] 
                                    qauntity = item["inventory"]["total"]
                                    message = "Out of stock" if qauntity < 1 else "In stock"
                                    zip = locations[0]
                                    locations = str(locations).replace("[","").replace("]","").replace("'","") if len(locations) < 10 else "Global"
                                    sale = str(sale)
                                    original = str(original)
                                    discount = str(discount).replace("%","")
                                    thumbnail = str(thumbnail)
                                    qauntity = str(qauntity)
                                    ping(sale, original, discount, thumbnail, title, link, locations,zip,upc,qauntity,message)
                                                
                            file_data["data"].append(item)
                        except Exception as error:
                            print(error)

                    time.sleep(5)
                    file.seek(0)
                    json.dump(file_data, file, ensure_ascii=False, indent=4, default=str)
            except Exception as error:
                print(error)
    except Exception as error:
        print(error)

with open("./categories.json","r",encoding="utf-8") as cats:
    cats = json.load(cats)["categories"][0]["subCategories"]
    get_products(cats[20])