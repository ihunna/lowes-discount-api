import config as cfg
import random
import time
import traceback
from discord_webhook import DiscordWebhook, DiscordEmbed
from proxy_builder import *

proxy = {"http":"http://user-r4z:password1@all.smartproxy.com:10000"}
  
def ping(sale, original, discount, thumbnail, title, link, locations, zip,upc,qauntity,message):
    PING_UNF = 'https://discord.com/api/webhooks/1066368974671061142/WEWgGmFfCM_yJp9W6_5GOoapAzjjWyaNd8s_3UCLaCrfnyVZqY6EvbAwlFvPnNTx87Ef'
    
    webhook = DiscordWebhook(url=PING_UNF) 
    
    embed = DiscordEmbed(title = title, color="004990", url=link)
    embed.set_thumbnail(url=thumbnail)
    embed.add_embed_field(name='Discount', value=f"{discount}%", inline=False)
    embed.add_embed_field(name='Now', value=f"${sale}")
    embed.add_embed_field(name='Originally', value=f"${original}")
    embed.add_embed_field(name='Quantity', value=f"{qauntity}", inline = False)
    embed.add_embed_field(name='Message', value=f"{message}", inline = False)
    embed.add_embed_field(name='UPC', value=f"{upc}", inline = False)
    embed.add_embed_field(name='Link', value=f"[Buy Now]({link})", inline = False)
    embed.add_embed_field(name='Lowest Zip Code', value=zip, inline = False)
    
    embed.add_embed_field(name='Stores - Price, Zip, Location', value=locations, inline = False)
    embed.set_footer(text="Lowes - Alpha")
    embed.set_timestamp()
    
    webhook.add_embed(embed)
    
    # proxies = build_proxies()
    # proxy = {"https": random.choice(proxies)}
    webhook.set_proxies(proxy)
    response = webhook.execute()   
    print(response)
    print(response.json())
