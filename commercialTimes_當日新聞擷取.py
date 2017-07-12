#-*-coding: utf-8-*-
import requests
from bs4 import BeautifulSoup as bs
import time

news = ["http://news.cnyes.com/news/cat/tw_stock_news"]

links = ["http://ctee.com.tw/News/ListCateNews.aspx?cateid=tg&page=1",
        "http://ctee.com.tw/News/ListCateNews.aspx?cateid=ggce&page=1",
        "http://ctee.com.tw/News/ListCateNews.aspx?cateid=vvgc&page=1",
        "http://ctee.com.tw/News/ListCateNews.aspx?cateid=cjzc&page=1"]

heading = "http://ctee.com.tw/News/"

today = time.strftime("%Y/%m/%d", time.localtime())

def soupify( urlLink ):
    req = requests.get(urlLink)
    sp = bs(req.content, "html.parser")
    return sp

newsList = {}

for link in links:
    for h in soupify(link).find("div", {"class":"NewsList"}).find_all("h3"):
        for each in h.find_all("a"):
            if each.get("href") != None:
                print ("*" * 20)
                print ("{}: {}{}".format(each.text, heading, each.get("href")))
                newsList[each.text] = heading + each.get("href")
                for ps in soupify(heading + each.get("href")).find_all("p"):
                    print (ps.text)
    

