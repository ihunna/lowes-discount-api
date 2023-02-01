import requests
import random
import string

def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

def build_proxies():
    temp_proxy_list = []
    with open("api/proxies.txt",'r') as data_file:
        for line in data_file:
            variables = line.split(":")
            ip = variables[0]
            port = variables[1]
            user = variables[2]
            pw = variables[3].strip()
            tmp_proxy = f"{user}:{pw}@{ip}:{port}"
            temp_proxy_list.append({"http":f"http://{tmp_proxy}"})
    return temp_proxy_list

def get_proxies():
    proxies = []
    with open("api/proxies.txt","r") as f:
        for proxy in f.readlines():
            proxy = proxy.replace("\n","").split(":")
            ip = proxy[0]
            port = proxy[1]
            username = proxy[2]
            password = proxy[3]
            proxy = {
                "http": f'http://{username}:{password}@{ip}:{port}',
                "https": f'http://{username}:{password}@{ip}:{port}'
            }
            proxies.append(proxy)

    return proxies



def get_token(type="new",token="",proxy=""):
    headers = {}
    if type == "new":
        headers = {
            'Host': 'api-prod.lowes.com',
            'accept': '*/*',
            'user-agent': 'lowesMobileApp/23.1.3 (iPhone; iOS 16.2.0)',
            'accept-language': 'en-US,en;q=0.9',
        }
    elif type == "refresh":
        headers = {
            'Host': 'api-prod.lowes.com',
            'accept': '*/*',
            'content-type': 'application/x-www-form-urlencoded',
            'authorization': f'Bearer {token}',
            'x-lowes-uuid': f'd4a0a30d-d44f-4754-983c-{generate_sensor_data(type="random_string")}',
            'accept-language': 'en-US,en;q=0.9',
            'user-agent': 'lowesMobileApp/23.1.3 (iPhone; iOS 16.2.0)',
        }

    data = {
        'client_id': 'pGAW7y8NJVlZvoWijVia21K4HzOqskRU',
        'client_secret': 'zbwMYDyPp4XQS00E',
        'grant_type': 'client_credentials',
    }

    response = requests.post('https://api-prod.lowes.com/oauth2/accesstoken', headers=headers, data=data,proxies=proxy)

    data = response.json()

    token = data['access_token']

    return token


def generate_sensor_data(type="sensor_data"):
    if type == "sensor_data":
        return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    elif type == "client_id":
        return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

    elif type == "client_secret":
        return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

    elif type == "random_string":
        return  ''.join(random.choices( string.hexdigits[:6] + string.digits, k=10))
