''#-*- coding: utf-8 -*-''
import csv, requests, os, sys, winsound
from time import strftime, gmtime, sleep, localtime
from bs4 import BeautifulSoup

head = {
    "Host" : "mops.twse.com.tw", 
    "User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
    "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language" : "en-US,en;q=0.5",
    "Accept-Encoding" : "gzip, deflate",
    "Referer" : "http://mops.twse.com.tw/mops/web/index",
    "Connection" : "keep-alive"
    }

def beeping():
    Freq = 2500 # Set Frequency To 2500 Hertz
    Dur = 100 # Set Duration To ms == 1 second
    winsound.Beep(Freq,Dur)

#抓網頁
def website_grab(link):
    r = requests.get(link, headers=head)
    soup = BeautifulSoup(r.content, "html.parser")
    return soup

def tickerlistparse(lst):
    ticker = []
    for each in lst.find_all("td")[1::4]:
        ticker.append(each.text.replace(" ",""))
    
#抓大台成分股號做成list
def taiex():
    urls = ["http://www.taifex.com.tw/cht/2/weightedPropertion",
    "http://www.taifex.com.tw/cht/2/tPEXPropertion"]
    ticker = []
    for url in urls:
        content = website_grab(url)
        for each in content.find_all("td")[1::4]:
            ticker.append(each.text.replace(" ",""))
    return ticker

#抓MSCI股號做成list
def msci_grab():
    msci_website = "https://app2.msci.com/eqb/custom_indexes/tw_performance.html"
    msci_ary, msci_list = [], []
    n = BeautifulSoup(requests.get(msci_website).content, "html.parser")
    for tds in n.find_all("td")[8:-52]:
        if len(msci_list) == 11:
            msci_list.append(tds.text)
            msci_ary.append(msci_list)
            msci_list = []
        else:
            msci_list.append(tds.text)
    for each in msci_ary:
        msci_list.append("{!s}".format(each[10][:4]))
    return msci_list

#Remove '\n' in a list
def clean_list(target):
    while True:
        try:
            target.remove("\n")
        except ValueError:
            break
    return target
    
#公開資訊觀測站抓歷史公告
def previous_day():
    previous_days = "http://mops.twse.com.tw/mops/web/t05st02"
    payload = {
    "encodeURIComponent" : "1",
    "step" : "1",
    "step00": "0",
    "firstin" : "1",
    "off" : "1",
    "TYPEK" : "all",
    "year" : int((strftime("%Y", gmtime())))-1911,
    "month" : (strftime("%m", gmtime())),
    "day" : int((strftime("%d", gmtime())))-1
            }
    history_list = []
    result_p, final_p = [], []
    req = requests.get(previous_days, params=payload, headers=head)
    soup = BeautifulSoup(req.content, "html.parser")
    for each in soup.find_all("td"):
        clean_word = each.text.replace("\r\n","")
        history_list.append(clean_word.strip("\xa0"))
    cleanList = clean_list(history_list)
    for a in range(38, len(cleanList)-1):
        if len(result_p) == 4:
            result_p.append(cleanList[a])
            final_p.append(result_p)
            result_p = []
        else:
            result_p.append(cleanList[a])
    return final_p

def remove_list_duplicate(list_here):
    new_list = [ item for pos,item in enumerate(list_here) if list_here.index(item)==pos ]
    return new_list

def filter_list( here):
    filter_words = ["子公司", "孫公司"]
    x = 0
    for each in here:
        for words in filter_words:
            if words in each[4]:
                x += 1
    while x != 0:
        for each in here:
            for words in filter_words:
                if words in each[4]:
                    here.remove(each)
                    x -= 1
    return here
        
    
#公開資訊觀測站抓公告
def announcement_grabber():
    today = "http://mops.twse.com.tw/mops/web/t05sr01_1"
    m = website_grab(today)
    display_array, result, addin = [], [], []
    for tds in m.find_all("table", {"class" : "hasBorder"}):
        for each in tds.find_all("td"):
            clean_word = each.text.replace("\r\n","")
            display_array.append(clean_word)
    #remove all '\n' in the list
    while True:
        try:
            display_array.remove("\n")
        except ValueError:
            break
    for x in display_array:
        if len(addin) ==4:
            addin.append(x)
            result.append(addin)
            addin = []
        else:
            addin.append(x)
    return ( result)

def yesterday_list_output(a):
    for each in a:
        print ("%s %s %s %s %s " % (each[0],each[1],each[2],each[3],each[4]))

def today_list_output(a):
    for each in a:
        print ("%s %s %s %s %s " % (each[2],each[3],each[0],each[1],each[4]))

def sorted_list_output( list_to_sort, which_list):
    fp = [x for x in list_to_sort if x[0] in which_list]
    return fp

#Load all lists here and clean up unwanted announcements
include_words = ["庫藏股", "除權","除息","配股","配息","配發","分派", "派發", "分配", "調整","基準","股利", "股息", "股東會", "法人", "增資" ]
msci_list = msci_grab()
taiex_list = taiex()
t_minus1 = filter_list(previous_day())
allAnnouncement = filter_list(announcement_grabber())
t_minus1Day_dup = [ ans for ans in t_minus1 for wds in include_words if wds in ans[4]]
tDay_dup = [ ann for ann in allAnnouncement for words in include_words if words in ann[4]]

t_minus1Day = remove_list_duplicate(t_minus1Day_dup)
tDay = remove_list_duplicate(tDay_dup)

print ("\n昨日摩台")
yesterday_list_output(sorted_list_output(t_minus1Day, msci_list))
print ("\n昨日大台")
yesterday_list_output(sorted_list_output(t_minus1Day, taiex_list))

'''
while True:
    print ("\n" + "*" * 50)
    print (strftime("%a, %d %b %Y %H:%M:%S", gmtime()))
    print ("今日摩台")
    today_list_output(sorted_list_output(tDay, msci_list))
    print ("\n今日大台")
    today_list_output(sorted_list_output(tDay, taiex_list))
    sleep(300)
'''
