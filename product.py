import requests
import simplejson as json
from discord_hooks import Webhook
import datetime
import math
import random
import pytz

import traceback
import logging

header = {'User-Agent': 'Mozilla/5.0'}

proxyList = []

#Proxy set up
with open ('proxies.txt') as f:
    for line in f:
        info = line.rstrip('\n').split(':')
        ipAddr = info[0]
        port = info[1]
        user = info[2]
        password = info[3]
        proxy = '{}:{}@{}:{}'.format(user, password, ipAddr, port)
        proxyList.append(proxy)
#Proxy set up


class StockItem:

    proxyIndex = 0

    def __init__(self, SKU, country):
        self.SKU = SKU
        self.country = country.lower()
        urls = self.__buildUrls()
        self.stockURL = urls['stockUrl']
        self.infoUrl = urls['infoUrl']
        self.mainUrl = urls['mainUrl']
        info = self.__requestProductInfo()
        self.name = info['name']
        self.price = info['price']
        self.oldStock = []
        self.newStock = self.__getStock()
        

    def compareStock(self):
        return (self.oldStock != self.newStock)

    def updateItemInfo(self):
        info = self.__requestProductInfo()
        self.name = info['name']
        self.price = info['price']

    def __buildUrls(self):
        urls = dict.fromkeys(['stockUrl', 'infoUrl', 'mainUrl'])
        SKU = self.SKU
        if (self.country == "uk"):
            urls['stockUrl'] = 'https://www.adidas.co.uk/api/products/{}/availability'.format(
                SKU)
            urls['infoUrl'] = 'https://www.adidas.co.uk/api/products/{}'.format(
                SKU)
            urls['mainUrl'] = 'https://www.adidas.co.uk/{}.html'.format(SKU)
        elif (self.country == "us"):
            urls['stockUrl'] = 'https://www.adidas.com/api/products/{}/availability'.format(
                SKU)
            urls['infoUrl'] = 'https://www.adidas.com/api/products/{}'.format(
                SKU)
            urls['mainUrl'] = 'https://www.adidas.com/us/{}.html'.format(SKU)
        return urls

    def __requestProductInfo(self):
        info = dict.fromkeys(['name', 'price'])

        self.__processRequest(self.infoUrl)
        dataJson = self.__processRequest(self.infoUrl)
        if 'pricing_information' in dataJson:
            info['price'] = str(
                dataJson['pricing_information']['standard_price'])

        if 'name' in dataJson:
            info['name'] = dataJson['name']
        else:
            info['name'] = "Product Unavaiable"

        return info

    def __getStock(self):
        available = []
        dataJson = self.__processRequest(self.stockURL)
        if 'variation_list' in dataJson:
            data = dataJson['variation_list']
            for item in data:
                if (item['availability'] > 0):
                    available.append([item['size'], str(item['availability'])])
        return available

    def updateStock(self):
        self.oldStock = self.newStock
        self.newStock = self.__getStock()

    def __processRequest(self, url):
        #r = requests.get(url, headers=header)
        dataJson = []

        proxies = {
            'http': 'http://' + proxyList[StockItem.proxyIndex],
            'https': 'https://' + proxyList[StockItem.proxyIndex]
        }

        if StockItem.proxyIndex == len(proxyList)-1:
            StockItem.proxyIndex = 0
        else:
            StockItem.proxyIndex += 1

        r = dict.fromkeys(['text'])
        try:
            #r = requests.get(url, headers=header, timeout=1)
            r = requests.get(url, headers=header, proxies=proxies, timeout=1)
        except requests.exceptions.Timeout:
            print("Timeout")
            print(proxies['http'])
            return self.__processRequest(url)
        except requests.exceptions.ProxyError:
            print("Proxy Error")
            print(proxies['http'])
            return self.__processRequest(url)
        except requests.exceptions.SSLError:
            print("SSL Error")
            print(proxies['http'])
            return self.__processRequest(url)

        '''
        try:
            r = requests.get(url, headers=header, proxies=proxies)
        except requests.exceptions.RequestException as e:
            print(e)
        #except requests.exceptions.Timeout:
            # Maybe set up for a retry, or continue in a retry loop
        #except requests.exceptions.TooManyRedirects:
            # Tell the user their URL was bad and try a different one
        #except requests.exceptions.RequestException as e:
            # catastrophic error
            #print(e)
        '''

        try:
            dataJson = json.loads(r.text)
        except Exception as e:
            print(r.text)
            logging.error(traceback.format_exc())
        return dataJson

    def getItemImage(self):
        url = "https://www.adidas.com/api/products/{}".format(self.SKU)
        dataJson = self.__processRequest(url)
        imageUrl = dataJson['view_list'][0]['image_url']
        return imageUrl

    def sendUpdateMessage(self, url):
        embed = Webhook(url, title="{} ({})".format(self.name, self.SKU),
                        color=0xFFFFFF, title_url=self.mainUrl)

        try:
            imageUrl = self.getItemImage()
            embed.set_thumbnail(url=imageUrl)
        except:
            pass

        if (self.country == "us"):
            embed.add_field(name="Price",
                            value="${}".format(self.price))
        elif (self.country == "uk"):
            embed.add_field(name="Price",
                            value="£{}".format(self.price))

        stockMsg = "Out of Stock"
        stockList = self.newStock
        if (len(stockList) > 0):
            stockArray = []
            for stock in stockList:
                #stockArray.append(stock[0] + ":" + stock[1])
                stockArray.append("{} - {}".format(stock[0], stock[1]))
            stockMsg = "\n".join(stockArray)

        embed.add_field(name="Size(s)", value=stockMsg, inline=False)

        embed.set_footer(text="@ProjectImpactIO | Adidas | {0:%I:%M:%S %p} EST".format(datetime.datetime.now(tz=pytz.timezone(
            'US/Eastern'))), icon="brand_url")
        embed.post()
        print("Sent Update Message")


    def sendUpdateMessage2(self, url):
        embed = Webhook(url, title="{} ({})".format(self.name, self.SKU),
                        color=0x1132d8, title_url=self.mainUrl)
        try:
            imageUrl = self.getItemImage()
            embed.set_thumbnail(url=imageUrl)
        except:
            pass

        if (self.country == "us"):
            embed.add_field(name="Price",
                            value="${}".format(self.price))
        elif (self.country == "uk"):
            embed.add_field(name="Price",
                            value="£{}".format(self.price))

        stockMsg = "Out of Stock"
        stockList = self.newStock
        if (len(stockList) > 0):
            stockArray = []
            for stock in stockList:
                #stockArray.append(stock[0] + ":" + stock[1])
                stockArray.append("{} - {}".format(stock[0], stock[1]))
            stockMsg = "\n".join(stockArray)

        embed.add_field(name="Size(s)", value=stockMsg, inline=False)

        embed.set_footer(text="@GlobalAIO | Adidas | {0:%I:%M:%S %p} EST".format(datetime.datetime.now(tz=pytz.timezone(
            'US/Eastern'))), icon="brand_url")
        embed.post()
        print("Sent Update Message")


if __name__ == "__main__":
    item = StockItem("G28183", "uk")
    item.getItemImage()
    print(item)
