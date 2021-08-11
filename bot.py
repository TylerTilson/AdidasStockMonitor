import product
import simplejson as json
import time
from discord_hooks import Webhook
import os


UK_web_hooks = ["url1","url2"]

US_web_hooks = ["url1","url2"]

def buildMonitorList():
    script_path = os.path.abspath(__file__)
    script_dir = os.path.split(script_path)[0]
    rel_path = "items.json"
    abs_file_path = os.path.join(script_dir, rel_path)
    data = json.load(open(abs_file_path))

    monitorList = []
    items = data["stock"]
    for item in items:
        monitorItem = product.StockItem(item['sku'], item['country'])
        monitorList.append(monitorItem)
        time.sleep(.5)
    return monitorList


def buildMonitorMessage(monitorList):
    monitorNames = []
    monitorMessage = "Monitoring the following items: "
    for stock in monitorList:
        #monitorNames.append(stock.name + "-" + stock.SKU)
        monitorNames.append("{} ({})".format(stock.name, stock.SKU))

    #monitorMessage += ', '.join(monitorNames)
    monitorMessage = "{} {}".format(monitorMessage, '\n'.join(monitorNames))

    return monitorMessage


def sendDiscordMessage(monitorMessage):

    for hookUrl in UK_web_hooks:
        embed = Webhook(hookUrl, color=0xf5a623, desc=monitorMessage)
        embed.set_author(name="Adidas Monitor",
                        icon="brand_icon_url")
        embed.set_footer(text="@UNTITLEDiscord",
                        icon="brand_icon_url")
        embed.post()

    for hookUrl in US_web_hooks:
        embed = Webhook(hookUrl, color=0xf5a623, desc=monitorMessage)
        embed.set_author(name="Adidas Monitor",
                        icon="brand_icon_url")
        embed.set_footer(text="@UNTITLEDiscord",
                        icon="brand_icon_url")
        embed.post()


def sendMonitorMessage(monitorList):
    monitorMessage = buildMonitorMessage(monitorList)
    sendDiscordMessage(monitorMessage)


def main():
    monitorList = buildMonitorList()

    #sendMonitorMessage(validItems)

    while(True):
        for monitor in monitorList:
            monitor.updateStock()
            if monitor.name != "Product Unavaiable":
                if monitor.compareStock():
                    if monitor.country == "uk":
                        for hookUrl in UK_web_hooks:
                            monitor.sendUpdateMessage(hookUrl)
                    elif monitor.country == "us":
                        for hookUrl in US_web_hooks:
                            monitor.sendUpdateMessage(hookUrl)
            else:
                monitor.updateItemInfo()
            time.sleep(1)

if __name__ == "__main__":           
    main()
