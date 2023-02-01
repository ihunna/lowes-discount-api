def build_proxies():

    temp_proxy_list = []
    with open("send_message/proxies.txt",'r') as data_file:
        for line in data_file:
            variables = line.split(":")
            ip = variables[0]
            port = variables[1]
            user = variables[2]
            pw = variables[3].strip()
            temp_proxy_list.append((f"http://{user}:{pw}@{ip}:{port}"))
    return temp_proxy_list